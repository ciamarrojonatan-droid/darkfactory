# DarkFactory Pipeline State

> Sincronizado em **2026-11-13** com infraestrutura completa de agentes, skills e esteira documental Nolan.

## 🔌 Status do Ecossistema & Escopo Ativo
- **Showrunner Cinematográfico**: Christopher Nolan (`nolan-director.md` e skill `nolan-dark-history-director`).
- **Arquitetura Acústica**: Mixagem procedural Zimmer/Göransson com conformidade estrita de loudness (-14 LUFS ±0.5, True Peak <= -1.0 dBTP).
- **Motores de Voz**: Roteador vocal inteligente com CosyVoice e fallback Kokoro-82M.
- **Cinema Dashboard**: FastAPI Web SPA na porta 8502 com monitoramento em tempo real de timeline, roteiros e áudios.
- **Ecossistema ECC Universal**: 122 regras de engenharia, 69 subagentes universais, workflows e hooks automáticos ativos.

---

## 📊 Telemetria Atual do Pipeline

| Fase / Módulo | Status | Métricas Verificadas no Ambiente |
| :--- | :--- | :--- |
| **Pesquisa & Fatos Históricos** | `ok` | **8** roteiros e filas estruturadas em `data/scripts/` (incidente soviético 1983, etc.) |
| **Roteirização Não-Linear (Nolan)** | `ok` | Estrutura de 5 Atos com Crosscutting temporal e prompts Dual-Shot (IMAX 70mm) |
| **Engenharia de Voz & Áudio** | `ok` | **24** arquivos de áudio em `data/audio/` (narrações, stems, Foley e master -14 LUFS) |
| **Síntese de Vídeo & Renders** | `ok` | **8** renders em `data/final/` (6 cinemáticos + 2 overlays) · **6** relatórios de auditoria em `data/quarantine/` |
| **Cinema Dashboard (:8502)** | `idle` | Serviço configurado em `src.dashboard.app` · Porta `8502` pronta para inicialização |
| **Qualidade & Testes (Pytest)** | `ok` | **253 passed, 2 skipped** (100% de sucesso na bateria completa de testes) |
| **Hooks & Automação** | `ok` | Telemetria de sessão, injeção de estado, consultor WWYD e Hard Gate Git na branch `main` |

---

## 🚀 Próxima Ação Recomendada
- Esteira DarkFactory 100% operacional e integrada:
  1. Para rodar o pipeline completo do piloto: `python run_pilot_pipeline.py` (ou `/pipeline`)
  2. Para inicializar o Cinema Dashboard: `.\run_dashboard.bat` (ou `/deploy`)
  3. Para acionar o showrunner Christopher Nolan: `/nolan`
