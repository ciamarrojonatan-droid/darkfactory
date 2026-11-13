# DarkFactory — Master Project Context & Architecture

> **Single Source of Truth (SSOT)** para agentes autônomos, orquestradores (Antigravity & Claude Code) e engenharia de software do projeto DarkFactory.

---

## 1. Identidade & Propósito do Sistema

O **DarkFactory** é uma esteira autônoma industrial de produção de documentários históricos cinematográficos para canais dark no YouTube e plataformas de streaming (Netflix, History Channel, BBC).

Sob a direção estética e estrutural do showrunner autoral **Christopher Nolan** (`nolan-director.md`), o sistema converte fatos históricos reais desclassificados em thrillers psicológicos não-lineares com qualidade de produção IMAX 70mm, pressão acústica contínua Zimmer/Göransson e conformidade técnica para algoritmos de recomendação e monetização.

### As 5 Fases da Esteira Documental:
1. **Fase 1: Pesquisa Histórica & Verificação de Fatos** — Mineração de fontes de domínio público, relatórios desclassificados e arquivos desclassificados via `research_engine.py`.
2. **Fase 2: Roteirização Não-Linear & Storyboard Nolan** — Construção em 5 Atos com fios temporais entrelaçados (Crosscutting) e formulação de prompts Dual-Shot (Shot A Drama + Shot B Macro).
3. **Fase 3: Engenharia Vocal & Sound Design Zimmer** — Narração com cadência cinematográfica (CosyVoice 3 com fallback Kokoro-82M) e mixagem de pressão acústica (Ticking Clocks, Shepard Tones, sub-bass Braams) calibrada em **-14 LUFS (±0.5)** e **-1.0 dBTP**.
4. **Fase 4: Fábrica de Vídeo T2V Cinematográfica** — Geração de takes visuais no RunningHub ComfyUI / Wan 2.2 / MiniMax H3 com granulação Kodak Vision3 500T e quarentena automática de takes defeituosos em `data/quarantine/`.
5. **Fase 5: Montagem Final, Foley & Exportação** — Concatenação inteligente orientada a beats, sincronização de legendas dinâmicas SRT e exportação final em `data/final/`.
6. **Módulo Transversal: Cinema Dashboard Web SPA** — Servidor FastAPI (`http://localhost:8502`) para visualização de roteiros, audição de stems e monitoramento em tempo real da produção.

---

## 2. Mapa Detalhado do Pipeline de 5 Fases

```text
    [Fatos Históricos / Arquivos Desclassificados]
                         │
                         ▼
      [Fase 1: Pesquisa] ──────► data/scripts/research_*.json
                         │
                         ▼
      [Fase 2: Roteiro Nolan] ──► data/scripts/nolan_*.json (Dual-Shot Prompts)
                         │
                         ▼
      [Fase 3: Áudio & Voz] ───► data/audio/ (Narração + Zimmer Mix -14 LUFS)
                         │
                         ▼
      [Fase 4: Fábrica Vídeo] ─► data/final/ (Takes brutos) + data/quarantine/ (QC Failures)
                         │
                         ▼
      [Fase 5: Montagem Final] ─► data/final/pilot_master.mp4 + data/subtitles/*.srt
```

### Fase 1: Pesquisa Histórica Preditiva
- **Módulos Centrais**: `src/research/research_engine.py`, `src/research/public_domain_research_engine.py`.
- **Entradas**: Temas históricos, datas, palavras-chave de desclassificação militar/governamental.
- **Saídas**: Relatórios estruturados de fatos verificados arquivados em `data/scripts/`.

### Fase 2: Roteirização Não-Linear Nolan
- **Módulos Centrais**: `.agents/agents/nolan-director.md`, `src/story/story_validator.py`, `src/video/pacing_analyzer.py`.
- **Entradas**: Fatos históricos validados da Fase 1.
- **Saídas**: Roteiro em 5 Atos com marcação temporal, instruções vocais e prompts Dual-Shot (Shot A Drama + Shot B Macro).

### Fase 3: Engenharia Vocal & Sound Design
- **Módulos Centrais**: `src/audio/voice_router.py`, `src/audio/audio_mixer.py`, `src/audio/audio_warp_complex_pro.py`.
- **Entradas**: Roteiro e falas formatadas.
- **Saídas**: Narração com CosyVoice/Kokoro, camadas de Foley e mix final normalizado a -14 LUFS / -1.0 dBTP.

### Fase 4: Fábrica de Vídeo T2V
- **Módulos Centrais**: `src/video/darkfactory_t2v.py`, `src/video/runninghub_execution_mode.py`.
- **Entradas**: Fila de prompts Dual-Shot da Fase 2.
- **Saídas**: Clipes de vídeo em `data/final/` e relatórios de quarentena em `data/quarantine/`.

### Fase 5: Montagem Final & Sincronização
- **Módulos Centrais**: `src/video/cinematic_pipeline.py`, `run_pilot_pipeline.py`.
- **Entradas**: Takes de vídeo aprovados e mix de áudio masterizado.
- **Saídas**: Episódio documental completo renderizado com legendas sincronizadas.

---

## 3. Decisões Arquiteturais (ADRs)

### ADR-01: Blindagem de Encoding UTF-8 em Windows
- **Contexto**: Ambientes Windows operam por padrão em `cp1252`, gerando exceções em acentuações e caracteres especiais.
- **Decisão**: Todos os scripts de entrada forçam `sys.stdout` e `sys.stderr` para UTF-8. Arquivos são abertos estritamente com `encoding="utf-8"`.

### ADR-02: Normalização Acústica Estrita (-14 LUFS / -1.0 dBTP)
- **Contexto**: YouTube e plataformas de streaming aplicam penalidades de volume e distorção em áudios fora da janela de loudness padrão.
- **Decisão**: Todo áudio final passa por filtro two-pass de loudness normalizado a **-14.0 LUFS (±0.5)** com limite estrito de True Peak em **-1.0 dBTP**.

### ADR-03: Roteador de Voz com Fallback Silencioso
- **Contexto**: A síntese vocal via APIs externas (CosyVoice) pode sofrer latência ou indisponibilidade temporária.
- **Decisão**: O `voice_router.py` detecta anomalias imediatamente e comuta a geração para o modelo local `Kokoro-82M`, garantindo produção contínua sem quebra do fluxo.

### ADR-04: Quarentena Atômica de Takes Defeituosos
- **Contexto**: Vídeos com distorções de anatomia, jitter ou anomalias temporais não devem contaminar o corte final.
- **Decisão**: Falhas no Quality Control (QC) direcionam o take para `data/quarantine/vid_<id>/` acompanhado de `quarantine_report.json` para reprocessamento ou substituição.

### ADR-05: Prompts Dual-Shot Nolan (IMAX 70mm)
- **Contexto**: Modelos generativos tendem a produzir tomadas genéricas se instruídos com prompts simplificados.
- **Decisão**: Cada cena exige obrigatoriamente a dobradinha Shot A (visão dramática/chiaroscuro) + Shot B (macro tátil de alta fidelidade) com especificações de película Kodak Vision3 e lentes anamórficas.

### ADR-06: Hard Gate de Persistência Git na branch `main`
- **Contexto**: Encerramento de sessões com modificações locais não commitadas acarreta perda de trabalho e inconsistência entre ambientes.
- **Decisão**: O hook `stop_gate.py` bloqueia a saída do agente até que todos os arquivos estejam commitados e sincronizados com `origin/main`.

---

## 4. Matriz de Subagentes & Ferramentas

| Domínio de Tarefa | Arquivos Alvo | Subagente Especializado | Skills Relacionadas |
| :--- | :--- | :--- | :--- |
| **Showrunner & Roteiro Cinematográfico** | `.agents/agents/nolan-director.md`, `data/scripts/` | `nolan-director` | `darkfactory-nolan`, `nolan-dark-history-director` |
| **Pesquisa & Fatos Históricos** | `src/research/` | `architect` | `api-design`, `verification-loop` |
| **Engenharia de Áudio & Foley** | `src/audio/`, `data/audio/` | `python-reviewer` | `python-patterns`, `darkfactory-review` |
| **Fábrica de Vídeo & RPA RunningHub** | `src/video/`, `data/final/` | `e2e-runner` | `darkfactory-pipeline`, `error-handling` |
| **Cinema Dashboard Web SPA (:8502)** | `src/dashboard/` | `architect` | `darkfactory-deploy`, `api-design` |
| **Qualidade & Testes Automatizados** | `tests/` | `tdd-guide` | `python-testing`, `darkfactory-review` |
| **Orquestração Geral & Pipeline** | `run_pilot_pipeline.py`, `.agents/` | `planner` | `darkfactory-pipeline`, `orchestrator` |

---

## 5. Diretiva Fundamental de Autonomia Operacional

O assistente e seus subagentes operam sob **autonomia total**:
1. Executar as fases da esteira documental sem interrupções desnecessárias para decisões triviais.
2. Validar sempre as alterações via suíte completa de testes (`pytest`).
3. Manter o `state.md` permanentemente atualizado com a telemetria real.
4. Cumprir o mandato de commit e push na branch `main` antes de encerrar tarefas.
