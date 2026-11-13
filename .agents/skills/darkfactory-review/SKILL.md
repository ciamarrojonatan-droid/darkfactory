---
name: darkfactory-review
description: >-
  Runs a comprehensive multi-layer quality gate for DarkFactory: automated pytest
  suite, audio compliance (-14 LUFS / -1.0 dBTP), video pacing QA, quarantine inspection,
  and security audit. Use when running /review.
---

# DarkFactory Comprehensive Quality Review (`/review`)

Comando integrado de auditoria de qualidade, engenharia acústica, conformidade de streaming e testes do repositório DarkFactory.

## 🧭 O que este comando executa

1. **Gate Automatizado de Testes (Pytest)**:
   Executa toda a suíte de testes unitários e de integração:
   ```powershell
   .\venv\Scripts\python.exe -m pytest -q
   ```
   *Critério de aprovação*: **100% dos testes passando sem falhas (253+ testes)**.

2. **Auditoria de Conformidade Acústica (Loudness & True Peak)**:
   - Verifica se os masters de áudio em `data/audio/` cumprem rigorosamente os padrões de streaming:
     - **Integrated Loudness**: `-14.0 LUFS` (tolerância ±0.5 LUFS).
     - **Maximum True Peak**: `<= -1.0 dBTP` (evita distorção inter-sample na compressão AAC/Opus).
     - **Faixa de Diálogo**: Frequências vocais limpas entre 80Hz e 8kHz sem mascaramento pela trilha.

3. **Auditoria de Vídeo & Pacing Cinematográfico**:
   - Valida ritmo de corte (ASL - Average Shot Length) entre 2.5s e 4.5s para thrillers históricos.
   - Inspeciona relatórios em `data/quarantine/` para identificar anomalias visuais ou distorções de IA.
   - Checa conformidade com o formato Dual-Shot (Shot A Drama + Shot B Macro).

4. **Auditoria de Segurança & Credenciais**:
   - Confirma que `.env` está estritamente listado no `.gitignore`.
   - Varre arquivos modificados em busca de API keys (`GEMINI_API_KEY`, tokens RunningHub) expostas.

5. **Relatório Consolidado**:
   Gera um relatório objetivo com veredicto final: `PASS (Aprovado para Produção / YouTube)` ou `FAIL (Correções Requeridas)`.
