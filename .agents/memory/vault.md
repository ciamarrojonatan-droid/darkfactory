# DarkFactory Persistent Memory Vault

> Memória durável e compartilhada entre sessões, modelos e agentes do DarkFactory.

---

## 🧠 Aprendizados Operacionais & Resoluções de Problemas

### 1. Windows Console Encoding & UTF-8
- **Problema**: O Windows usa `cp1252` por padrão no PowerShell e CMD, causando quebras de `UnicodeEncodeError` com descrições narrativas, prompts ricos e acentuação em português.
- **Resolução**: Em todos os pontos de entrada (`run_pilot_pipeline.py`, hooks, scripts de teste), forçar `sys.stdout.reconfigure(encoding="utf-8")` e `sys.stderr.reconfigure(encoding="utf-8")`. Nos scripts `.bat`, usar `chcp 65001`.

### 2. Ciclo de Vida dos Hooks (`hooks.json`)
- **Problema**: O working directory ao executar comandos definidos em `.agents/hooks.json` varia entre `.agents/` e a raiz do projeto.
- **Resolução**: Referenciar scripts como `python scripts/<script_name>.py` e manter resolução dinâmica de caminho subindo os diretórios até localizar a raiz do projeto. Todos os scripts de hook utilizam estritamente a stdlib do Python (`json`, `sys`, `os`, `socket`, `datetime`) para não depender do ambiente virtual.

### 3. Normalização Acústica e Masterização (-14 LUFS)
- **Problema**: Áudios com loudness inconsistente sofrem distorção ou atenuação algorítmica ao serem enviados para o YouTube.
- **Resolução**: Filtro two-pass de loudness normalizado a **-14.0 LUFS (±0.5)** com limite estrito de True Peak em **-1.0 dBTP** no `audio_mixer.py`.

### 4. Resiliência do Pipeline de Narração
- **Problema**: Latência ou quedas em serviços remotos de TTS (CosyVoice).
- **Resolução**: Implementação do `voice_router.py` com fallback automático e transparente para o motor neural local `Kokoro-82M`.

### 5. Isolamento QC e Quarentena de Vídeo
- **Problema**: Takes gerados com anomalias anatômicas ou distorções de movimento não devem contaminar a montagem final.
- **Resolução**: Desvio automático de takes reprovados no QC para `data/quarantine/vid_<id>/` acompanhados do relatório `quarantine_report.json`.

---

## 📌 Histórico de Decisões Arquiteturais (ADRs Resumidas)
- **Showrunner Christopher Nolan**: Roteirização em 5 Atos com crosscutting temporal e prompts Dual-Shot (Shot A Drama + Shot B Macro).
- **Cinema Dashboard Web SPA**: Servidor FastAPI na porta 8502 com timeline de beats e player de áudio masterizado.
- **Hard Gate Git**: O encerramento de qualquer sessão exige `git add .`, commit e `git push origin main`.
