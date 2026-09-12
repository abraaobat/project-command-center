# NanoVNA Modern — Roadmap Master

Roadmap incremental. Nenhuma fase deve comprometer a precisão RF para entregar recursos visuais ou de conectividade.

## F0 — Hardware Fingerprint & Safety Baseline

**Objetivo:** identificar de forma reproduzível o hardware real do ZN401 4.7_ZK e garantir rota de recuperação.

- [x] Identificar modelo externo: ZeenKo ZN401 / HW 4.7_ZK.
- [x] Identificar firmware atual: NanoVNA-D 1.2.44 `[x401]`.
- [x] Identificar MCU reportado: STM32F303xC / Cortex-M4F.
- [x] Confirmar display 480x320 e microSD funcional.
- [ ] Confirmar enumeração USB normal com cabo/porta compatíveis.
- [ ] Confirmar modo DFU sem gravar firmware.
- [ ] Registrar VID/PID, interface USB e comandos de console disponíveis.
- [ ] Confirmar variante de sintetizador/mixer/LCD quando necessário.
- [ ] Documentar recovery procedure.

**Gate F0:** dispositivo reconhecido em USB/DFU e rota de recuperação testada/documentada.

## F1 — Upstream Reproducible Build

**Objetivo:** produzir firmware equivalente ao upstream sem alteração funcional.

- [ ] Criar/fixar fork do `DiSlord/NanoVNA-D`.
- [ ] Registrar commit/tag upstream usado como baseline.
- [ ] Build macOS para `TARGET=F303`.
- [ ] Gerar `H4.bin` reproduzível.
- [ ] Adicionar CI de build.
- [ ] Verificar tamanho de flash/RAM e headroom inicial.
- [ ] Definir política de sincronização com upstream.
- [ ] Testar flash/recovery somente após F0.

**Gate F1:** build limpa, CI verde e aparelho operando igual ao baseline.

## F2 — Modern UI Foundation

**Objetivo:** criar arquitetura de UI separada do motor de medição.

- [ ] `ui_theme` com paleta/tipografia/métricas.
- [ ] widgets básicos reutilizáveis.
- [ ] navegação por abas.
- [ ] layout 480x320.
- [ ] redraw por regiões.
- [ ] orçamento explícito de RAM/flash/CPU.
- [ ] modo Classic preservado como fallback.

**Gate F2:** nova shell de UI navegável sem regressão de sweep.

## F3 — Modular Dashboard & Presets

**Objetivo:** permitir que o usuário escolha exatamente quais informações aparecem.

- [ ] registry de widgets/overlays.
- [ ] enable/disable por item.
- [ ] slots automáticos de layout.
- [ ] Quick Metrics.
- [ ] presets `Minimal`, `Antenna`, `Filter`, `Cable`, `Lab`, `Studio`.
- [ ] persistência local e/ou SD.
- [ ] estado por perfil.

**Gate F3:** troca de preset e overlays sem reinicialização e sem perda de configuração.

## F4 — Enhanced Graphics

**Objetivo:** modernizar traces sem exigir framebuffer integral.

- [ ] nova grade cartesiana.
- [ ] Smith chart refinado.
- [ ] espessuras de trace selecionáveis.
- [ ] marker highlight.
- [ ] anti-aliasing leve quando couber.
- [ ] glow falso com 1–2 passes.
- [ ] persistência limitada de traces.
- [ ] modos `Classic`, `Enhanced`, `Studio`, `Diagnostic`.
- [ ] medição de impacto em FPS/sweep/CPU/RAM.

**Gate F4:** modo Enhanced utilizável em tempo real; Studio permanece opcional.

## F5 — microSD Extension Platform

**Objetivo:** transformar o SD em armazenamento de extensões e histórico, não em RAM.

- [ ] estrutura `/NANOVNA/` versionada.
- [ ] presets/layouts externos.
- [ ] temas.
- [ ] idiomas.
- [ ] scripts seguros.
- [ ] calibrações.
- [ ] S1P/S2P e screenshots.
- [ ] histórico de medições.
- [ ] comparação old/new.
- [ ] esquema de versão dos arquivos.
- [ ] comportamento seguro sem cartão.

**Gate F5:** aparelho opera sem SD; com SD, recursos são descobertos e validados sem corromper configuração interna.

## F6 — USB Protocol & NanoVNA Bridge

**Objetivo:** criar um bridge desktop estável entre NanoVNA e aplicações modernas.

- [ ] inventariar comandos USB/serial do firmware.
- [ ] definir protocolo interno normalizado.
- [ ] implementar discovery e reconnect.
- [ ] REST API para device/config/markers/calibration.
- [ ] WebSocket para sweep ao vivo.
- [ ] logging e diagnostics.
- [ ] macOS primeiro; Linux/Windows depois.

**Gate F6:** sweep S11/S21 chega continuamente ao navegador via bridge sem alterar o firmware RF.

## F7 — Web Dashboard / PWA

**Objetivo:** oferecer dashboard avançado no computador, tablet e celular.

- [ ] gráfico cartesiano interativo.
- [ ] Smith chart interativo.
- [ ] markers e cursores.
- [ ] cards configuráveis.
- [ ] presets compartilhados.
- [ ] histórico e comparação.
- [ ] Touchstone export/import.
- [ ] relatório de medição.
- [ ] layout responsivo.
- [ ] PWA e acesso LAN.

**Gate F7:** desktop e celular exibem a mesma sessão em tempo real pela LAN.

## F8 — Smart Analysis

**Objetivo:** entregar comportamento inteligente com matemática/DSP antes de ML.

- [ ] resonance finder.
- [ ] SWR min/max e target offset.
- [ ] bandwidth em thresholds configuráveis.
- [ ] Q estimado.
- [ ] insertion loss.
- [ ] peak/notch detection.
- [ ] comparação e drift.
- [ ] cable/TDR helpers.
- [ ] regras de diagnóstico com explicação rastreável.

**Gate F8:** cada diagnóstico apresenta dados de origem e não depende de modelo opaco.

## F9 — SmartLink ESP32-S3 Proof of Concept

**Objetivo:** substituir o computador como bridge para uso de campo.

- [ ] escolher ESP32-S3 com PSRAM (referência N16R8).
- [ ] USB Host CDC-ACM.
- [ ] alimentação/VBUS protegida.
- [ ] evitar backfeed.
- [ ] parser de protocolo NanoVNA.
- [ ] Wi‑Fi AP/STA.
- [ ] servidor HTTP/WebSocket mínimo.
- [ ] reconexão USB robusta.

**Gate F9:** celular conecta ao Wi‑Fi do SmartLink e recebe sweep ao vivo sem computador.

## F10 — Wireless Platform

**Objetivo:** amadurecer o SmartLink como acessório permanente.

- [ ] mDNS (`nanovna.local`).
- [ ] provisioning Wi‑Fi.
- [ ] BLE opcional.
- [ ] PSRAM ring buffers.
- [ ] microSD adicional opcional.
- [ ] cache/histórico local.
- [ ] OTA do ESP32.
- [ ] segurança básica e modo offline-first.
- [ ] enclosure/box.

**Gate F10:** operação portátil estável em AP e STA.

## F11 — Edge Intelligence / TinyML Experimental

**Objetivo:** investigar ML pequeno sem tornar o produto dependente dele.

- [ ] dataset versionado por features, não dados sensíveis.
- [ ] feature extraction.
- [ ] classificador de padrões simples.
- [ ] benchmark RAM/latência/acurácia.
- [ ] fallback determinístico.
- [ ] modelos carregáveis/versionados via SD do SmartLink.

**Gate F11:** TinyML só é promovido se superar regras determinísticas em caso de uso real.

## F12 — External AI Integration

**Objetivo:** permitir análises mais ricas fora do dispositivo.

- [ ] formato de resumo estruturado de medição.
- [ ] consentimento explícito para envio externo.
- [ ] integração opcional com serviço de IA.
- [ ] explicação textual de medições.
- [ ] comparação histórica.
- [ ] geração de relatório técnico.
- [ ] funcionamento local preservado sem cloud.

## F13 — Hardening & Validation

- [ ] testes de regressão RF.
- [ ] testes de calibração.
- [ ] soak test USB/Wi‑Fi.
- [ ] corrupção/remoção de SD durante uso.
- [ ] brownout/power-cycle.
- [ ] limites de memória.
- [ ] watchdog/fail-safe.
- [ ] compatibilidade com versões de hardware explicitamente suportadas.

## F14 — Packaging & Releases

- [ ] matriz de hardware suportado.
- [ ] releases assinadas/checksums.
- [ ] release notes.
- [ ] firmware + bridge + web + SmartLink versionados de forma compatível.
- [ ] guia de recovery.
- [ ] screenshots e documentação de uso.
- [ ] política de upstream sync.

## Prioridade imediata

1. Fechar F0: USB/DFU/hardware fingerprint.
2. Criar o repositório/fork e fechar F1 com build original.
3. Só então iniciar Modern UI.

Não fazer flash experimental, alterações no DSP ou integração ESP32 antes dos gates de recuperação e build reproduzível.
