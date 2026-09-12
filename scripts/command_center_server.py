#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import threading
import time
import uuid
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
STATE = DATA / "runtime-action-jobs.json"
LOCK = threading.RLock()
CODEX_CACHE = {"path": None, "checked": 0.0}
ACTIVE = {"queued", "running"}
FINAL_RE = re.compile(r"^PCC_STATUS:\s*(DONE|NEEDS_USER|BLOCKED|FAILED)\s*$", re.I | re.M)
ACTION_RE = re.compile(r"^PCC_USER_ACTION:\s*(.+?)\s*$", re.I | re.M)
SUMMARY_RE = re.compile(r"^PCC_SUMMARY:\s*(.+?)\s*$", re.I | re.M)


def now():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def read_json(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


def write_state(payload):
    tmp = STATE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp, STATE)


def state():
    value = read_json(STATE, {"schemaVersion": 1, "jobs": []})
    if not isinstance(value, dict):
        value = {"schemaVersion": 1, "jobs": []}
    value.setdefault("schemaVersion", 1)
    value.setdefault("jobs", [])
    value["jobs"] = value["jobs"][-200:]
    return value


def patch_job(job_id, **changes):
    with LOCK:
        value = state()
        for job in value["jobs"]:
            if job.get("id") == job_id:
                job.update(changes)
                write_state(value)
                return dict(job)
    return None


def projects():
    source = DATA / "runtime-projects.json"
    if not source.exists():
        source = DATA / "projects.json"
    base = read_json(source, {}).get("projects", [])
    extra = read_json(DATA / "knowledge-extraction-projects.json", {}).get("projects", [])
    return [p for p in [*base, *extra] if isinstance(p, dict)]


def project(project_id):
    return next((p for p in projects() if p.get("id") == project_id), None)


def sources():
    items = read_json(DATA / "status-sources.json", {}).get("sources", [])
    return {
        str(item["projectId"]): item
        for item in items
        if isinstance(item, dict) and item.get("projectId") and item.get("enabled", True)
    }


def source_for(item):
    by_id = {p.get("id"): p for p in projects()}
    by_source = sources()
    current = item
    seen = set()
    while current:
        pid = str(current.get("id", ""))
        if not pid or pid in seen:
            break
        seen.add(pid)
        if pid in by_source:
            return by_source[pid]
        current = by_id.get(current.get("parentId"))
    return None


def workspace_for(item):
    src = source_for(item)
    if not src:
        return None, None
    repo = str(src.get("repository", "")).rsplit("/", 1)[-1]
    if not repo:
        return None, src
    root = Path(os.environ.get("PCC_PROJECTS_DIR", "~/Projects")).expanduser()
    return root / repo, src


def resolve_codex():
    t = time.time()
    if t - CODEX_CACHE["checked"] < 30:
        return CODEX_CACHE["path"]

    found = None
    explicit = os.environ.get("PCC_CODEX_BIN")
    if explicit:
        candidate = Path(explicit).expanduser()
        if candidate.is_file() and os.access(candidate, os.X_OK):
            found = str(candidate)
    if not found:
        found = shutil.which("codex")
    if not found:
        try:
            probe = subprocess.run(
                ["/bin/zsh", "-lc", "command -v codex"],
                capture_output=True, text=True, timeout=5, check=False
            )
            candidate = probe.stdout.strip().splitlines()[0] if probe.stdout.strip() else ""
            if candidate and Path(candidate).is_file():
                found = candidate
        except (OSError, subprocess.SubprocessError):
            pass

    CODEX_CACHE.update(path=found, checked=t)
    return found


def notify(message, subtitle="Ação necessária"):
    if os.environ.get("PCC_NOTIFICATIONS", "1").lower() in {"0", "false", "no"}:
        return
    script = (
        "on run argv\n"
        "display notification (item 2 of argv) with title (item 1 of argv) subtitle (item 3 of argv)\n"
        "end run"
    )
    try:
        subprocess.run(
            ["/usr/bin/osascript", "-e", script, "Project Command Center", message[:220], subtitle],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5, check=False
        )
    except (OSError, subprocess.SubprocessError):
        pass


def parse_agent_result(text, return_code):
    sm = FINAL_RE.search(text or "")
    am = ACTION_RE.search(text or "")
    mm = SUMMARY_RE.search(text or "")
    status = {
        "DONE": "done",
        "NEEDS_USER": "needs_user",
        "BLOCKED": "blocked",
        "FAILED": "failed",
    }.get(sm.group(1).upper() if sm else "", "done" if return_code == 0 else "failed")
    summary = mm.group(1).strip() if mm else " ".join((text or "").strip().split())[-320:]
    if not summary:
        summary = "Tarefa concluída." if status == "done" else "Execução encerrada sem resumo."
    action = am.group(1).strip() if am else ""
    if action.upper() == "NONE":
        action = ""
    if status in {"needs_user", "blocked", "failed"} and not action:
        action = summary
    return status, summary[:600], action[:600]


def build_prompt(item, src):
    source_hint = src.get("path", "não informada") if src else "não informada"
    return f"""Você está executando uma tarefa disparada pelo Project Command Center em modo não interativo.

Projeto: {item.get('name', item.get('id', ''))}
Fase atual: {item.get('current', '')}
Próximo marco: {item.get('next', '')}
Ação selecionada: {item.get('action', '')}
Fonte de status canônica: {source_hint}

Avance este projeto o máximo possível agora dentro do repositório atual. Inspecione primeiro código, documentação, testes e git status.

Regras:
- Faça trabalho reversível e local claramente implícito na ação: código, documentação, testes, validações e status factual.
- Preserve trabalho não relacionado já existente.
- Não faça push, deploy, publicação, pagamento, flash de hardware, alteração externa irreversível ou uso de segredo.
- Não pare para atualizações de progresso. Faça tudo o que puder antes de escalar.
- Se depender de hardware, browser autenticado, credencial, decisão de produto, permissão do sistema ou ação humana, prepare tudo que puder e marque NEEDS_USER.
- Se houver bloqueio técnico independente do usuário, marque BLOCKED.
- Rode as validações pertinentes antes de concluir.

A resposta final DEVE terminar com exatamente estas três linhas:
PCC_STATUS: DONE|NEEDS_USER|BLOCKED|FAILED
PCC_USER_ACTION: <uma linha objetiva ou NONE>
PCC_SUMMARY: <uma linha objetiva com o que foi feito>
"""


def active_job(project_id, workspace):
    for job in reversed(state()["jobs"]):
        if job.get("status") not in ACTIVE:
            continue
        if job.get("projectId") == project_id or (workspace and job.get("workspace") == workspace):
            return job
    return None


def create_job(item, workspace, src):
    job = {
        "id": uuid.uuid4().hex[:12],
        "projectId": item.get("id"),
        "projectName": item.get("name"),
        "actionSnapshot": item.get("action", ""),
        "nextSnapshot": item.get("next", ""),
        "status": "queued",
        "startedAt": now(),
        "finishedAt": None,
        "workspace": str(workspace) if workspace else None,
        "repository": src.get("repository") if src else None,
        "summary": "Tarefa enfileirada.",
        "userAction": "",
    }
    value = state()
    value["jobs"].append(job)
    write_state(value)
    return job


def run_job(job_id, item, workspace, src, codex):
    logs = Path(os.environ.get("PCC_JOB_LOG_DIR", "/tmp/project-command-center-jobs")).expanduser()
    logs.mkdir(parents=True, exist_ok=True)
    log = logs / f"{job_id}.log"
    result = logs / f"{job_id}.result.txt"
    patch_job(job_id, status="running", summary="Codex executando a próxima ação.", logPath=str(log))

    command = [
        codex, "--ask-for-approval", "never", "exec",
        "--sandbox", "workspace-write", "--color", "never",
        "-C", str(workspace), "-o", str(result), build_prompt(item, src)
    ]
    rc = 1
    try:
        with log.open("w", encoding="utf-8") as handle:
            proc = subprocess.run(
                command, cwd=workspace, stdout=handle, stderr=subprocess.STDOUT,
                text=True, timeout=int(os.environ.get("PCC_JOB_TIMEOUT_SECONDS", "7200")), check=False
            )
            rc = proc.returncode
        text = result.read_text(encoding="utf-8", errors="replace") if result.exists() else ""
        if not text and log.exists():
            text = log.read_text(encoding="utf-8", errors="replace")[-12000:]
        status, summary, user_action = parse_agent_result(text, rc)
    except subprocess.TimeoutExpired:
        status, summary = "failed", "A execução excedeu o limite de tempo configurado."
        user_action = "Revise o log e dispare a tarefa novamente se necessário."
    except Exception as exc:
        status, summary = "failed", f"Falha ao executar o agente: {type(exc).__name__}: {exc}"
        user_action = "Verifique Codex, autenticação e workspace local."

    patch_job(
        job_id, status=status, finishedAt=now(), summary=summary,
        userAction=user_action, returnCode=rc
    )
    if status in {"needs_user", "blocked", "failed"}:
        notify(user_action or summary, "Ação sua necessária" if status == "needs_user" else "Tarefa bloqueada")
    elif status == "done" and os.environ.get("PCC_NOTIFY_DONE", "0").lower() in {"1", "true", "yes"}:
        notify(summary, "Tarefa concluída")


def start_action(project_id):
    item = project(project_id)
    if not item:
        return HTTPStatus.NOT_FOUND, {"error": "Projeto não encontrado."}
    action = str(item.get("action", "")).strip()
    if not action:
        return HTTPStatus.BAD_REQUEST, {"error": "Projeto sem ação configurada."}

    workspace, src = workspace_for(item)
    workspace_key = str(workspace.resolve()) if workspace and workspace.exists() else str(workspace or "")
    with LOCK:
        running = active_job(project_id, workspace_key)
        if running:
            return HTTPStatus.CONFLICT, {"error": "Já existe uma tarefa ativa neste projeto/workspace.", "job": running}
        job = create_job(item, workspace, src)

    if not src or not workspace:
        current = patch_job(
            job["id"], status="needs_user", finishedAt=now(),
            summary="Projeto sem repositório automatizável.",
            userAction=action
        )
        notify(action)
        return HTTPStatus.ACCEPTED, {"job": current}

    workspace = workspace.expanduser()
    if not workspace.is_dir():
        user_action = f"Disponibilize {src.get('repository')} em {workspace}."
        current = patch_job(
            job["id"], status="needs_user", finishedAt=now(),
            summary=f"Workspace local não encontrado: {workspace}", userAction=user_action
        )
        notify(user_action)
        return HTTPStatus.ACCEPTED, {"job": current}

    codex = resolve_codex()
    if not codex:
        user_action = "Instale/autentique o Codex CLI ou defina PCC_CODEX_BIN e reinicie o serviço."
        current = patch_job(
            job["id"], status="needs_user", finishedAt=now(),
            summary="Codex CLI não encontrado pelo serviço local.", userAction=user_action
        )
        notify(user_action)
        return HTTPStatus.ACCEPTED, {"job": current}

    threading.Thread(
        target=run_job, args=(job["id"], item, workspace, src, codex),
        name=f"pcc-{job['id']}", daemon=True
    ).start()
    return HTTPStatus.ACCEPTED, {"job": job}


def recover_jobs():
    with LOCK:
        value = state()
        changed = False
        for job in value["jobs"]:
            if job.get("status") in ACTIVE:
                job.update(
                    status="failed", finishedAt=now(),
                    summary="Execução interrompida pelo reinício do Project Command Center.",
                    userAction="Revise o workspace e dispare a tarefa novamente se necessário."
                )
                changed = True
        if changed:
            write_state(value)


def snapshot():
    value = state()
    latest = {}
    for job in value["jobs"]:
        if job.get("projectId"):
            latest[str(job["projectId"])] = job
    return {
        "jobs": value["jobs"],
        "latestByProject": latest,
        "capabilities": {
            "codexAvailable": bool(resolve_codex()),
            "projectsDir": str(Path(os.environ.get("PCC_PROJECTS_DIR", "~/Projects")).expanduser()),
            "notifications": os.environ.get("PCC_NOTIFICATIONS", "1").lower() not in {"0", "false", "no"},
        },
    }


class Handler(SimpleHTTPRequestHandler):
    server_version = "ProjectCommandCenter/4.7"

    def send_json(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def serve_index(self):
        try:
            html = (ROOT / "index.html").read_text(encoding="utf-8")
            marker = '<script src="/scripts/action-runner-ui.js"></script>'
            if marker not in html:
                html = html.replace("</body>", marker + "</body>")
            body = html.encode()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/actions":
            self.send_json(HTTPStatus.OK, snapshot())
        elif path in {"/", "/index.html"}:
            self.serve_index()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/api/actions/start":
            self.send_json(HTTPStatus.NOT_FOUND, {"error": "Endpoint não encontrado."})
            return
        try:
            if self.headers.get_content_type() != "application/json":
                raise ValueError("Content-Type deve ser application/json.")
            length = int(self.headers.get("Content-Length", "0") or 0)
            if length <= 0 or length > 65536:
                raise ValueError("Payload inválido.")
            payload = json.loads(self.rfile.read(length).decode())
            project_id = str(payload.get("projectId", "")).strip()
            if not project_id:
                raise ValueError("projectId é obrigatório.")
            status, result = start_action(project_id)
            self.send_json(status, result)
        except (ValueError, json.JSONDecodeError) as exc:
            self.send_json(HTTPStatus.BAD_REQUEST, {"error": str(exc)})

    def log_message(self, fmt, *args):
        print(f"[pcc] {self.address_string()} - {fmt % args}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=int(os.environ.get("PCC_PORT", "8787")))
    parser.add_argument("--bind", default=os.environ.get("PCC_BIND", "127.0.0.1"))
    args = parser.parse_args()

    os.chdir(ROOT)
    recover_jobs()
    server = ThreadingHTTPServer((args.bind, args.port), Handler)
    print(f"Project Command Center em http://{args.bind}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
