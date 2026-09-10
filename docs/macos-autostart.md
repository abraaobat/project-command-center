# Inicialização automática no macOS

O Project Command Center pode instalar dois LaunchAgents do usuário:

- `com.abraaobat.project-command-center` — mantém o dashboard em `http://localhost:8787` e o Auto Status Sync em execução;
- `com.abraaobat.studyos-local` — mantém o StudyOS Local Pilot em `http://localhost:8788`.

A instalação é feita a partir do clone local do Project Command Center:

```bash
cd ~/Projects/project-command-center
git pull --ff-only
/bin/zsh scripts/install-macos-autostart.sh
```

O instalador:

1. valida Python, NVM e os caminhos locais;
2. migra processos manuais conhecidos das portas 8787 e 8788;
3. grava os arquivos `.plist` em `~/Library/LaunchAgents`;
4. registra e inicia os jobs com `launchctl`;
5. verifica `http://127.0.0.1:8787/` e `http://127.0.0.1:8788/api/health`.

Os serviços iniciam automaticamente quando o usuário entra no macOS e são reiniciados pelo `launchd` caso o processo encerre.

## Logs

```text
~/Library/Logs/ProjectCommandCenter/project-command-center.out.log
~/Library/Logs/ProjectCommandCenter/project-command-center.err.log
~/Library/Logs/ProjectCommandCenter/studyos.out.log
~/Library/Logs/ProjectCommandCenter/studyos.err.log
/tmp/project-command-center-sync.log
/tmp/project-command-center-git.log
```

## Verificar status

```bash
launchctl print gui/$(id -u)/com.abraaobat.project-command-center | grep -E 'state =|pid ='
launchctl print gui/$(id -u)/com.abraaobat.studyos-local | grep -E 'state =|pid ='

curl -fsS http://127.0.0.1:8787/ >/dev/null && echo 'Command Center OK'
curl -fsS http://127.0.0.1:8788/api/health && echo
```

## Parar ou remover a inicialização automática

Para parar os jobs na sessão atual:

```bash
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.abraaobat.project-command-center.plist
launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.abraaobat.studyos-local.plist
```

Para remover a configuração depois de parar os jobs:

```bash
rm -f ~/Library/LaunchAgents/com.abraaobat.project-command-center.plist
rm -f ~/Library/LaunchAgents/com.abraaobat.studyos-local.plist
```

O script `Abrir Dashboard.command` continua funcionando como atalho. Quando o LaunchAgent estiver instalado, ele apenas solicita a ativação do serviço se necessário e abre o dashboard, evitando criar outro servidor e outro loop de sincronização.
