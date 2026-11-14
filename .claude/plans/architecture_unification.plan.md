# Plan: Unificação Arquitetural DarkFactory (Padrão Facade / Bridge)

**Status**: Aprovado para implementação na próxima sessão  
**Data**: 2026-11-14  
**Abordagem Selecionada**: Padrão Facade / Bridge (Preserva CLI e testes existentes, substituindo código legado pelos motores de `src/video/`)  
**Complexity**: Medium  

---

## 1. Summary
Este plano estabelece a modernização e unificação do pipeline do DarkFactory sem quebrar interfaces externas. A esteira principal (`run_pilot_pipeline.py`), o Cinema Dashboard SPA e os 265 testes automatizados continuarão executando os mesmos comandos, mas seus scripts de entrada (`src/*.py`) delegarão internamente para o ecossistema avançado de `src/video/` (`DarkFactoryAudioEngine`, `MasterVoiceRouter`, `ShortsRepurposerEngine`, `PublicDomainResearchEngine`). Além disso, o manifesto de 40 cenas (5 Atos) é blindado contra sobrescritas acidentais pelo modo teaser.

---

## 2. Patterns to Mirror

| Category | Source File | Pattern |
|---|---|---|
| Encoding | `src/auth_gate.py:27` | `sys.stdout.reconfigure(encoding="utf-8")` sob Windows (ADR-01) |
| Atomic Persistence | `src/nolan_director.py:533` | Gravação em `.tmp.<pid>` seguida de `replace()` atômico (ADR-02) |
| Audio Loudness | `src/audio_mixer_master.py:139` | EBU R128 estrito: `-14.0 LUFS (±0.5)` e True Peak `<= -1.0 dBTP` |
| Voice Consistency | `src/video/voice_router.py:48` | `NarratorLock` persistido em `data/audio/narrator_locks.json` |
| Video Safety Zones | `src/video/shorts_repurposer.py:27` | `PLATFORM_SAFE_ZONES` para 9:16 mobile retention sem cortes de UI |
| Test Coverage | `tests/test_voice_router.py` | Pytest com `tmp_path`, fixtures e zero chamadas externas de rede |

---

## 3. Files to Change

| File | Action | Why |
|---|---|---|
| `src/nolan_director.py` | UPDATE | Adicionar campo `mode` ao `NolanEpisodeManifest`; salvar teaser exclusivamente em `*_teaser.json` para blindar o master de 40 cenas. |
| `src/video/pacing_analyzer.py` | UPDATE | Substituir chamadas depreciadas `start_time.get_seconds()` por `start_time.seconds`, limpando os warnings do Pytest. |
| `src/generate_pilot_audio.py` | UPDATE | Integrar `MasterVoiceRouter` (Single-Narrator Lock), ajustar fallback Edge-TTS para `en-GB-RyanNeural` (sotaque britânico documental) e sinalizar masterização única. |
| `src/cosyvoice_master.py` | UPDATE | Evitar segundo ciclo destrutivo de pitch-down e compressão quando áudios já tiverem sido masterizados. |
| `src/audio_mixer_master.py` | UPDATE | Substituir rotinas manuais de PCM por chamadas ao `DarkFactoryAudioEngine` (`src/video/audio_engine.py`) com perfil `cold_war_espionage`. |
| `src/shorts_generator.py` | UPDATE | Delegar internamente ao `ShortsRepurposerEngine` (`src/video/shorts_repurposer.py`) com legendas cinéticas e safe-zones mobile. |
| `src/research_engine.py` | UPDATE | Integrar metadados do `PublicDomainResearchEngine` (`src/video/research_engine.py`) para Wikimedia Commons e NASA APIs. |
| `src/daemon_darkfactory.py` | UPDATE | Integrar `auth_gate.py` e reordenar a geração de áudio antes do mix 4-stems. |
| `run_pilot_pipeline.py` | UPDATE | Apontar flag `--teaser` para `nolan_soviet_glitch_teaser.json`. |
| `state.md` | UPDATE | Atualizar telemetria do projeto registrando o plano de unificação arquitetural aprovado. |

---

## 4. Implementation Tasks

### Task 1: Blindagem de Roteiro & Limpeza de Avisos
- **Action**:
  1. No `src/nolan_director.py`, adicionar campo `mode: str = "full"` no `NolanEpisodeManifest`.
  2. No `export_manifest()`, se `is_teaser`, exportar para `nolan_soviet_glitch_teaser.json`, `pilot_soviet_glitch_teaser.json`, `google_flow_omni_queue_teaser.json` e `google_flow_veo3_queue_teaser.json`.
  3. No `src/video/pacing_analyzer.py:137-138`, usar `start_time.seconds` e `end_time.seconds`.
- **Validate**:
  ```powershell
  .\venv\Scripts\python.exe -m pytest tests/test_nolan_director.py tests/test_sprint8_foley_and_reverse.py -q
  ```

### Task 2: Unificação Vocal & Single-Narrator Lock
- **Action**:
  1. Em `src/generate_pilot_audio.py`, integrar `MasterVoiceRouter` com persistência em `data/audio/narrator_locks.json`.
  2. Alterar a voz de fallback do Edge-TTS de `en-US-ChristopherNeural` para `en-GB-RyanNeural` (preservando o sotaque de `bm_george`).
  3. No `src/cosyvoice_master.py`, checar se o arquivo de entrada já possui loudness normalizado antes de aplicar rubberband / compressor em cascata.
- **Validate**:
  ```powershell
  .\venv\Scripts\python.exe -m pytest tests/test_voice_router.py tests/test_narration.py -q
  ```

### Task 3: Unificação Acústica Hans Zimmer
- **Action**:
  1. Em `src/audio_mixer_master.py`, importar `DarkFactoryAudioEngine` de `src.video.audio_engine`.
  2. Substituir geração manual de ondas senoidais pela chamada a `DarkFactoryAudioEngine.generate_soundbed()` com perfil `"cold_war_espionage"`.
- **Validate**:
  ```powershell
  .\venv\Scripts\python.exe -m pytest tests/test_audio_mixer.py tests/test_voice_and_audio_engines.py -q
  ```

### Task 4: Unificação do Repurposer de Shorts
- **Action**:
  1. Em `src/shorts_generator.py`, instanciar `ShortsRepurposerEngine` de `src.video.shorts_repurposer`.
  2. Processar recorte vertical 9:16 com enquadramento de retenção e legendas cinéticas `HyperFrames`.
- **Validate**:
  ```powershell
  .\venv\Scripts\python.exe -m pytest tests/test_shorts_generator.py tests/test_sprint10_shorts_and_captions.py -q
  ```

### Task 5: Unificação de Pesquisa & Dossiês
- **Action**:
  1. Em `src/research_engine.py`, conectar fallback para `PublicDomainResearchEngine` (`src/video/research_engine.py`).
- **Validate**:
  ```powershell
  .\venv\Scripts\python.exe -m pytest tests/test_research_engine.py tests/test_public_domain_research_engine.py -q
  ```

### Task 6: Alinhamento do Daemon 24/7 & Orquestrador
- **Action**:
  1. Em `src/daemon_darkfactory.py`, incluir chamada a `auth_gate.py` antes de disparar o ciclo.
  2. Garantir que a etapa de áudio rode antes da mixagem e do vídeo.
- **Validate**:
  ```powershell
  .\venv\Scripts\python.exe -m pytest tests/test_daemon_darkfactory.py -q
  ```

---

## 5. Validation Commands

```powershell
# 1. Suíte completa de testes (265 testes passando)
.\venv\Scripts\python.exe -m pytest -q

# 2. Verificação de integridade do Auth Gate
.\venv\Scripts\python.exe src/auth_gate.py --check

# 3. Teste de isolamento de Teaser vs Master de 40 Cenas
.\venv\Scripts\python.exe src/nolan_director.py --mode teaser
.\venv\Scripts\python.exe -c "import json; assert len(json.load(open('data/scripts/nolan_soviet_glitch.json', encoding='utf-8'))['scenes']) == 40"
.\venv\Scripts\python.exe -c "import json; assert len(json.load(open('data/scripts/nolan_soviet_glitch_teaser.json', encoding='utf-8'))['scenes']) == 3"
```

---

## 6. Risks & Mitigation

| Risk | Likelihood | Mitigation |
|---|---|---|
| Quebra de compatibilidade CLI | Baixa | O padrão Facade preserva rigorosamente todos os argumentos existentes (`--topic`, `--dry-run`, etc.). |
| Dependência de rede em testes | Nula | Todos os novos facades mantêm mocks e fixtures locais idênticos aos testes unitários aprovados. |
| Perda de qualidade acústica | Nula | A suíte de testes de loudness (`-14 LUFS`) valida qualquer alteração de masterização. |

---

## 7. Acceptance Criteria
- [ ] `data/scripts/nolan_soviet_glitch.json` blindado com 40 cenas (5 Atos).
- [ ] Teasers exportados exclusivamente para arquivos com sufixo `_teaser.json`.
- [ ] Padrão Facade ativo em `audio_mixer_master.py`, `shorts_generator.py`, `research_engine.py`.
- [ ] Single-Narrator Lock ativo com persistência em `data/audio/narrator_locks.json`.
- [ ] Suíte de 265 testes `pytest` 100% verde com 0 warnings de pacing.
- [ ] Repositório sincronizado e com push na branch `main`.
