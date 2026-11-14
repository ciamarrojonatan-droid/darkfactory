# DarkFactory Pipeline State

> Sincronizado em **2026-11-13** com arquitetura integral de 5 Atos (40 Cenas / 13,9 Minutos), conformidade EBU R128 (-14 LUFS) e Master Cinematográfico 1080p.

## 🔌 Status do Ecossistema & Escopo Ativo
- **Showrunner Cinematográfico**: Christopher Nolan (`nolan-director.md`, `src/nolan_multi_act.py` e skill `nolan-dark-history-director`).
- **Estrutura Master do Documentário**: 5 Atos completos (8 cenas por ato = 40 cenas cinematográficas contínuas, totalizando **833.81 segundos / 13.90 minutos**).
- **Arquitetura Acústica (4 Stems)**:
  - *Stem 1*: Narração masterizada via curva Ableton Complex Pro EQ/Compressor.
  - *Stem 2*: OST orquestral atmosférico Hans Zimmer (Google Flow Music / Lyria / Drone sintetizado).
  - *Stem 3*: Foley tático de bunker soviético (klaxons, pulsos de radar, relógios mecânicos 60/90 BPM e chave industrial).
  - *Stem 4*: Âncora sub-grave de 35Hz com impactos Braam em transições de atos.
  - *Master*: Conformidade EBU R128 estrita (**-14.0 LUFS ±0.5, True Peak <= -1.0 dBTP**) e Sidechain Dynamic Ducking (-16dB sob falas).
- **Esteira Visual & Motion Graphics**:
  - Geração de placas procedurais com dados táticos, coordenadas de satélite e ruído de monitor CRT.
  - Movimentos Anamórficos Ken-Burns (zoom-in suave e deriva lenta).
  - Composição de Overlays com canal alfa via `TacticalGraphicsEngine` (HUD de radar, carimbos militares de desclassificação e lower-thirds cinematográficos).
  - Color Grading via 3D LUT Kodak 2383 / Bleach-Bypass (elimina aspecto artificial de IA).
  - Formato Theatrical Scope 2.39:1 (letterbox matte de 140px) com legendas gravadas na barra preta inferior.
- **Cinema Dashboard**: FastAPI Web SPA na porta `8502` com telemetria, visualização de roteiros, audição de áudio e status do pipeline.
- **Conformidade YouTube & Proteção EDSA**: Relatório de Compliance com pontuação **97/100 (AUTO_REMEDIATED)**, Kit de Disputa Content ID e declaração de conteúdo sintético.

---

## 📊 Telemetria Atual do Pipeline

| Fase / Módulo | Status | Métricas Verificadas no Ambiente |
| :--- | :--- | :--- |
| **Pesquisa & Fatos Históricos** | `ok` | Roteiro de 40 cenas arquivado em `data/scripts/nolan_soviet_glitch.json` (Incidente Soviético de 1983) |
| **Roteirização Não-Linear (Nolan)** | `ok` | 5 Atos estruturados (The Hook, The Genesis, The Escalation, The Climax, The Silence) com prompts Dual-Shot (IMAX 70mm) |
| **Engenharia de Voz & Áudio** | `ok` | 40 stems individuais (`scene_1.mp3` a `scene_40.mp3`), `pilot_intro_full.mp3` e mix 4-stems `pilot_final_audio_mix.mp3` (-14 LUFS) |
| **Fábrica de Vídeo & Overlays** | `ok` | 40 clipes gerados com Ken-Burns e overlays gráficos (HUD, dossiês desclassificados e lower-thirds) |
| **Montagem Master Final** | `ok` | `data/output/the_1983_soviet_glitch_final_1080p.mp4` (**13.90 min / 833.81s**, 68.6 MB, 1080p 2.39:1 Scope) |
| **Cinema Dashboard (:8502)** | `ok` | Testes de API aprovados com 100% de sucesso · Pronto para inicialização via `run_dashboard.bat` |
| **Qualidade & Testes (Pytest)** | `ok` | **253 passed, 2 skipped** (100% de sucesso na bateria completa de testes de regressão) |
| **YouTube Compliance QC** | `ok` | Status `AUTO_REMEDIATED` (Score: 97/100) com Legal Dispute Kit e sem bloqueios |

---

## 🚀 Próxima Ação Recomendada
- Documentário de 13,9 minutos completamente renderizado e validado:
  1. Para iniciar o Cinema Dashboard Web SPA: `python -m uvicorn src.dashboard.app:app --host 127.0.0.1 --port 8502`
  2. Para inspecionar o vídeo master: `data/output/the_1983_soviet_glitch_final_1080p.mp4`
