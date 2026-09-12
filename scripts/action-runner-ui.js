(() => {
  const TERMINAL = new Set(["done", "needs_user", "blocked", "failed"]);
  const ACTIVE = new Set(["queued", "running"]);
  let latestByProject = {};
  let refreshing = false;

  const labels = {
    queued: ["AGUARDANDO", "running"],
    running: ["CHATGPT/CODEX EM EXECUÇÃO", "running"],
    done: ["CONCLUÍDO", "done"],
    needs_user: ["PRECISA DE VOCÊ", "needs-user"],
    blocked: ["BLOQUEADO", "blocked"],
    failed: ["FALHOU", "failed"],
  };

  function injectStyles() {
    if (document.getElementById("pcc-action-runner-style")) return;
    const style = document.createElement("style");
    style.id = "pcc-action-runner-style";
    style.textContent = `
      .pcc-agent-state{margin-top:-5px;margin-left:25px;display:flex;align-items:center;gap:7px;font-size:11px;color:var(--muted);min-height:18px}
      .pcc-agent-pill{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--line);background:var(--panel2);padding:4px 7px;border-radius:999px;font-weight:800;letter-spacing:.035em}
      .pcc-agent-pill.running{color:var(--accent);border-color:color-mix(in srgb,var(--accent) 55%,var(--line))}
      .pcc-agent-pill.done{color:var(--ok);border-color:color-mix(in srgb,var(--ok) 55%,var(--line))}
      .pcc-agent-pill.needs-user{color:var(--warn);border-color:color-mix(in srgb,var(--warn) 55%,var(--line))}
      .pcc-agent-pill.blocked,.pcc-agent-pill.failed{color:var(--hot);border-color:color-mix(in srgb,var(--hot) 55%,var(--line))}
      .pcc-agent-detail{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:78ch}
      .action input:disabled{opacity:.65;cursor:wait}
    `;
    document.head.appendChild(style);
  }

  function dismissKey(job) {
    return `pcc:auto-dismiss:${job.id}`;
  }

  function actionTextFor(cb) {
    return (cb.closest(".action")?.querySelector("span")?.textContent || "").trim();
  }

  function currentJobFor(cb) {
    const job = latestByProject[cb.dataset.id];
    if (!job) return null;
    return job.actionSnapshot === actionTextFor(cb) ? job : null;
  }

  function stateNode(cb) {
    const label = cb.closest(".action");
    if (!label) return null;
    let node = label.nextElementSibling;
    if (!node || !node.classList.contains("pcc-agent-state")) {
      node = document.createElement("div");
      node.className = "pcc-agent-state";
      label.insertAdjacentElement("afterend", node);
    }
    return node;
  }

  function decorate() {
    injectStyles();
    const version = document.getElementById("version");
    if (version) version.textContent = "4.7";
    const footer = document.querySelector(".footer");
    if (footer && !footer.dataset.actionRunner) {
      footer.dataset.actionRunner = "1";
      footer.innerHTML += " • Checkboxes de ação agora disparam o Action Runner local; tarefas que exigem intervenção humana geram notificação no macOS.";
    }

    document.querySelectorAll("#grid input[data-id]").forEach((cb) => {
      const job = currentJobFor(cb);
      const node = stateNode(cb);
      if (!node) return;

      if (!job) {
        cb.checked = false;
        cb.disabled = false;
        cb.title = "Marque para iniciar automaticamente esta próxima ação.";
        node.innerHTML = `<span class="pcc-agent-pill">PRONTO PARA INICIAR</span><span class="pcc-agent-detail">Marque a caixa para delegar esta ação.</span>`;
        return;
      }

      const dismissed = localStorage.getItem(dismissKey(job)) === "1";
      cb.checked = !dismissed;
      cb.disabled = ACTIVE.has(job.status);
      cb.title = job.userAction || job.summary || "";
      const [text, css] = labels[job.status] || [String(job.status || "STATUS").toUpperCase(), ""];
      const detail = job.userAction || job.summary || "";
      node.innerHTML = `<span class="pcc-agent-pill ${css}">${text}</span><span class="pcc-agent-detail" title="${escapeAttr(detail)}">${escapeHtml(detail)}</span>`;
    });
  }

  function escapeHtml(value) {
    return String(value ?? "").replace(/[&<>"']/g, (char) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;"
    }[char]));
  }

  function escapeAttr(value) {
    return escapeHtml(value).replace(/`/g, "&#096;");
  }

  async function refresh() {
    if (refreshing) return;
    refreshing = true;
    try {
      const response = await fetch(`/api/actions?t=${Date.now()}`, {cache: "no-store"});
      if (response.ok) {
        const payload = await response.json();
        latestByProject = payload.latestByProject || {};
      }
    } catch (_) {
      // O dashboard estático continua utilizável se a API local estiver indisponível.
    } finally {
      refreshing = false;
      decorate();
    }
  }

  async function startAction(cb) {
    const projectId = cb.dataset.id;
    cb.disabled = true;
    const node = stateNode(cb);
    if (node) {
      node.innerHTML = `<span class="pcc-agent-pill running">INICIANDO</span><span class="pcc-agent-detail">Preparando o agente local…</span>`;
    }
    try {
      const response = await fetch("/api/actions/start", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({projectId}),
      });
      const payload = await response.json().catch(() => ({}));
      if (!response.ok && response.status !== 409) {
        throw new Error(payload.error || `HTTP ${response.status}`);
      }
      if (payload.job) {
        latestByProject[projectId] = payload.job;
        localStorage.removeItem(dismissKey(payload.job));
      }
    } catch (error) {
      cb.checked = false;
      if (node) {
        node.innerHTML = `<span class="pcc-agent-pill failed">ERRO</span><span class="pcc-agent-detail">${escapeHtml(error.message || error)}</span>`;
      }
    } finally {
      cb.disabled = false;
      await refresh();
    }
  }

  document.addEventListener("change", (event) => {
    const cb = event.target instanceof Element ? event.target.closest("#grid input[data-id]") : null;
    if (!cb) return;
    event.stopImmediatePropagation();

    const job = currentJobFor(cb);
    if (!cb.checked && job && TERMINAL.has(job.status)) {
      localStorage.setItem(dismissKey(job), "1");
      decorate();
      return;
    }
    if (cb.checked) {
      if (job) localStorage.removeItem(dismissKey(job));
      startAction(cb);
    }
  }, true);

  const originalRender = window.render;
  if (typeof originalRender === "function") {
    window.render = function(...args) {
      const result = originalRender.apply(this, args);
      queueMicrotask(decorate);
      return result;
    };
  }

  const observer = new MutationObserver(() => queueMicrotask(decorate));
  const grid = document.getElementById("grid");
  if (grid) observer.observe(grid, {childList: true});

  refresh();
  setInterval(refresh, 2500);
})();
