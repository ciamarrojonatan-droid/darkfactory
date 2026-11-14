# DarkFactory Pipeline State

> Sincronizado em **2026-11-14** com arquitetura integral de 5 Atos (40 Cenas / 13,9 Minutos), conformidade EBU R128 (-14 LUFS), **Gate Obrigatório de Pré-Autenticação Persistente (Google Flow & RunningHub)** e **Padrão de Vídeo Real Cinematográfico (Google Flow Veo 3.1 / Omni Flash + Fallback MiniMax H3 no RunningHub)**.

## 🔌 Status do Ecossistema & Escopo Ativo
- **Showrunner Cinematográfico**: Christopher Nolan (`nolan-director.md`, `src/nolan_multi_act.py` e skill `nolan-dark-history-director`).
- **Pre-Flight Authentication Gate (`src/auth_gate.py`)**:
  - Verificação prévia obrigatória antes de gerar qualquer asset (áudio, vídeo, foley, motion).
  - Sessão persistente via cookies/storage state para **Google Flow** (`flow.google.com`) e **RunningHub** (`runninghub.ai`, Contas 4, 5 e 7).
  - Janela headful Chromium automatizada para 1º login do operador e operação 100% headless subsequente.
- **Estrutura Master do Documentário**: 5 Atos completos (8 cenas por ato = 40 cenas cinematográficas contínuas, totalizando **833.81 segundos / 13.90 minutos**).
- **Esteira de Vídeo Real (Fim das Placas Procedurais Falsas)**:
  - **Padrão Primário**: Google Flow Bot RPA (`src/google_flow_bot.py`) com DeepMind Veo 3.1 e Gemini Omni Flash 1.2.
  - **Fallback Automático**: RunningHub MiniMax H3 Cinematic V2 Turbo (`src/video/minimax_h3_engine.py`, Workflow 2118560390471745537, Conta 7, nó #107 sem watermark).
  - **Hard Quarantine Gate**: Eliminação definitiva de imagens procedurais 2D fingindo ser filmagens em produção. Qualquer falha é arquivada em `data/quarantine/` com relatório de diagnóstico e aborta com erro explícito. Placas procedurais são estritamente limitadas a mocks de testes unitários (`--allow-procedural-fallback`).
  - Movimentos Anamórficos Ken-Burns e Overlays táticos (`TacticalGraphicsEngine`) aplicados sobre takes reais de vídeo.
  - Color Grading via 3D LUT Kodak 2383 / Bleach-Bypass (elimina aspecto artificial de IA).
  - Formato Theatrical Scope 2.39:1 (letterbox matte de 140px) com legendas gravadas na barra preta inferior.
- **Arquitetura Acústica (4 Stems)**:
  - *Stem 1*: Narração masterizada via curva Ableton Complex Pro EQ/Compressor (CosyVoice 3 / Kokoro-82M).
  - *Stem 2*: OST orquestral atmosférico Hans Zimmer (Google Flow Music / Lyria / MiniMax Music Conta 5).
  - *Stem 3*: Foley tático de bunker soviético (klaxons, pulsos de radar, relógios mecânicos 60/90 BPM e chave industrial).
  - *Stem 4*: Âncora sub-grave de 35Hz com impactos Braam em transições de atos.
  - *Master*: Conformidade EBU R128 estrita (**-14.0 LUFS ±0.5, True Peak <= -1.0 dBTP**) e Sidechain Dynamic Ducking (-16dB sob falas).
- **Cinema Dashboard**: FastAPI Web SPA na porta `8502` com telemetria, visualização de roteiros, audição de áudio e status do pipeline.
- **Conformidade YouTube & Proteção EDSA**: Relatório de Compliance com pontuação **97/100 (AUTO_REMEDIATED)**, Kit de Disputa Content ID e declaração de conteúdo sintético.

---

## 📊 Telemetria Atual do Pipeline

| Fase / Módulo | Status | Métricas Verificadas no Ambiente |
| :--- | :--- | :--- |
| **Pre-Flight Auth Gate** | `ok` | **100% Autenticado & Ativo**: Google Flow (`flow.google.com`) e RunningHub (`runninghub.ai`) verificados com sucesso via `src/auth_gate.py --check` |
| **Pesquisa & Fatos Históricos** | `ok` | Roteiro de 40 cenas arquivado em `data/scripts/nolan_soviet_glitch.json` (Incidente Soviético de 1983) |
| **Roteirização Não-Linear (Nolan)** | `ok` | 5 Atos estruturados com prompts Dual-Shot (Shot A Drama + Shot B Macro) e filas Google Flow (`omni_queue` e `veo3_queue`) |
| **Engenharia de Voz & Áudio** | `ok` | 40 stems individuais (`scene_1.mp3` a `scene_40.mp3`), `pilot_intro_full.mp3` e mix 4-stems `pilot_final_audio_mix.mp3` (-14 LUFS) |
| **Fábrica de Vídeo T2V Real** | `ok` | `google_flow_bot.py` integrado à esteira com failover para MiniMax H3. Placas procedurais antigas removidas de `data/broll/` |
| **Montagem Master Final** | `ready` | Aguardando novo disparo do pipeline para geração de vídeo real com Google Flow e overlays táticos |
| **Cinema Dashboard (:8502)** | `ok` | Testes de API aprovados com 100% de sucesso · Pronto para inicialização via `run_dashboard.bat` |
| **Qualidade & Testes (Pytest)** | `ok` | **265 passed, 2 skipped** (100% de cobertura nos módulos de Auth Gate, Failover e Quarentena de Vídeo) |
| **YouTube Compliance QC** | `ok` | Status `AUTO_REMEDIATED` (Score: 97/100) com Legal Dispute Kit e sem bloqueios |

---

## 🚀 Ciclo de Execução Padronizado (`run_pilot_pipeline.py`)
```text
Step 0:  auth_gate.py               (Verifica/loga sessões persistentes Google Flow & RunningHub)
Step 1:  nolan_director.py          (Estrutura roteiro de 5 Atos, prompts Dual-Shot e filas T2V)
Step 2:  research_engine.py         (Verificação de fatos e extração de fontes históricas)
Step 3:  google_flow_bot.py         (Geração de vídeo real no Google Flow com fallback MiniMax H3)
Step 4:  generate_pilot_audio.py    (Síntese vocal CosyVoice / Kokoro-82M)
Step 5:  cosyvoice_master.py        (Masterização de voz broadcast & geração de legendas SRT)
Step 6:  audio_mixer_master.py      (Mix 4-stems: voz + OST Zimmer + Foley + Braams a -14 LUFS)
Step 7:  render_pilot_video.py      (Montagem 1080p final com footage real, HUD, LUT 2383 e Scope)
Step 8:  shorts_generator.py        (Geração de cortes verticais 9:16 para YouTube Shorts)
Step 9:  youtube_compliance_qc.py   (Auditoria de conformidade com diretrizes do YouTube)
Step 10: youtube_algorithm_booster.py (Geração de tags, metadados de retenção e CTR)
```
