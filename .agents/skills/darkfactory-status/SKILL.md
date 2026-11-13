---
name: darkfactory-status
description: >-
  Displays real-time pipeline status for DarkFactory across all modules:
  scripts, audio stems, video renders, quarantine alerts, Cinema Dashboard status,
  and synchronizes state.md automatically. Use when running /status.
---

# DarkFactory Status Command (`/status`)

Este comando audita o estado operacional ao vivo da esteira cinematográfica DarkFactory e sincroniza automaticamente o `state.md`.

## 🧭 Fluxo de Execução

1. **Auditoria de Serviços Ativos**:
   - Checa se o Cinema Dashboard está respondendo na porta `8502`:
     ```powershell
     Invoke-WebRequest -Uri "http://localhost:8502" -UseBasicParsing -TimeoutSec 2
     ```

2. **Inspeção dos Diretórios de Produção**:
   - `data/scripts/`: Contabiliza roteiros, filas de prompts e estruturas de episódios (`.json`, `.txt`).
   - `data/audio/`: Contabiliza arquivos de voz gerados (`gemini_tts_*`, `cosyvoice_*`), faixas de Foley e áudios masterizados (`pilot_final_audio_mix.mp3`).
   - `data/final/`: Contabiliza vídeos renderizados e montados prontos para distribuição.
   - `data/quarantine/`: Contabiliza ocorrências e relatórios de quarentena visual/acústica.

3. **Validação da Suíte de Testes**:
   - Verifica o status do último ciclo de testes via `pytest`.

4. **Sincronização do `state.md`**:
   - Atualiza a tabela de métricas reais no `state.md` com timestamp atual e recomendação da próxima ação imediata.

5. **Exibição do Relatório Operacional**:
   - Apresenta a visão consolidada ao operador com o status de cada componente e sugestão da próxima etapa de produção.
