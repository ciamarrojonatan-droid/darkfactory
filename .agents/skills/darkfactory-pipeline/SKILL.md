---
name: darkfactory-pipeline
description: >-
  Executes, monitors, and orchestrates the DarkFactory cinematic documentary
  pipeline end-to-end or phase-by-phase (Research, Nolan Storyboard, Voice/Narration,
  Foley/Soundtrack, Video Generation, Final Assembly). Use when running /pipeline.
---

# DarkFactory Cinematic Pipeline Orchestrator (`/pipeline`)

Orquestrador unificado para execução autônoma das fases de produção documental do DarkFactory.

## 🧭 Comportamento dos Parâmetros

| Comando | Ação |
| :--- | :--- |
| `/pipeline` | Detecta a próxima etapa pendente no fluxo de produção documental e executa |
| `/pipeline --phase research` | Fase 1: Mineração e validação de fatos históricos desclassificados via `research_engine.py` |
| `/pipeline --phase script` | Fase 2: Roteirização não-linear em 5 Atos com Showrunner Nolan (`nolan_director.py`) |
| `/pipeline --phase audio` | Fase 3: Síntese vocal (CosyVoice / Kokoro) + Design de som Zimmer (-14 LUFS, -1.0 dBTP) |
| `/pipeline --phase video` | Fase 4: Geração de vídeo T2V/I2V no RunningHub ComfyUI / Wan 2.2 / MiniMax H3 |
| `/pipeline --phase assembly` | Fase 5: Montagem final de cortes, sincronia de beat, legendas SRT e exportação |
| `/pipeline --all` | Executa o pipeline completo do episódio piloto (`run_pilot_pipeline.py`) com validação |

---

## 🔬 Protocolo de Execução por Fase

### Fase 1: Pesquisa Histórica & Verificação de Fatos
- **Módulo**: `src/research/research_engine.py` / `src/research/public_domain_research_engine.py`
- **Execução**:
  ```powershell
  .\venv\Scripts\python.exe -m src.research.research_engine --query "soviet glitch nuclear 1983"
  ```
- **Validação**: Verifica se os fatos históricos, datas e nomes foram arquivados em `data/scripts/`.

### Fase 2: Roteiro & Storyboard Nolan
- **Módulo**: `src/story/story_validator.py` / `src/video/pacing_analyzer.py`
- **Execução**:
  ```powershell
  .\venv\Scripts\python.exe run_pilot_pipeline.py --phase script
  ```
- **Validação**: Roteiro não-linear estruturado em 5 Atos com prompts Dual-Shot (Drama + Macro) prontos para T2V.

### Fase 3: Engenharia Vocal & Sound Design
- **Módulos**: `src/audio/voice_router.py`, `src/audio/audio_mixer.py`, `src/audio/audio_warp_complex_pro.py`
- **Execução**:
  ```powershell
  .\venv\Scripts\python.exe run_pilot_pipeline.py --phase audio
  ```
- **Validação**: Áudio masterizado gerado em `data/audio/` com loudness normalizado a **-14 LUFS (±0.5)** e True Peak **<= -1.0 dBTP**.

### Fase 4: Fábrica de Vídeo T2V Cinematográfica
- **Módulos**: `src/video/darkfactory_t2v.py`, `src/video/runninghub_execution_mode.py`
- **Execução**:
  ```powershell
  .\venv\Scripts\python.exe run_pilot_pipeline.py --phase video
  ```
- **Validação**: Verificação dos renders em `data/final/` e isolamento de falhas em `data/quarantine/`.

### Fase 5: Montagem, Foley & Final Concat
- **Módulos**: `src/video/cinematic_pipeline.py`, `src/video/sprint8_foley_and_reverse.py`
- **Execução**:
  ```powershell
  .\venv\Scripts\python.exe run_pilot_pipeline.py --phase render
  ```
- **Validação**: Arquivo `.mp4` final gerado com áudio mixado, legendas sincronizadas e conformidade com YouTube/Streaming.

---

## 🛡️ Gestão de Erros & Auto-Recuperação
1. Se o sintetizador de voz principal (CosyVoice) apresentar indisponibilidade, o `voice_router.py` aciona automaticamente o fallback local Kokoro-82M sem interromper a esteira.
2. Qualquer frame ou take com artefatos visuais ou desvio de prompt é direcionado atomicamente para `data/quarantine/` com emissão de `quarantine_report.json`.
3. Ao finalizar qualquer fase do pipeline, atualize obrigatoriamente o `state.md`.
