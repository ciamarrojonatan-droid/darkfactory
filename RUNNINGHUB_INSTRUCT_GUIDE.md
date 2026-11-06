# DarkFactory — Guia de Execução CosyVoice 3 Instruct 2

> **Workflow RunningHub**: [CosyVoice 3 Instruct 2 (Workflow ID: 2118531898170486785)](https://www.runninghub.ai/pt-br/workflow/2118531898170486785)  
> **Botão de Execução**: Sempre **Lite/Plus** (Botão do meio / Cor amarela-ouro). Nunca usar *Standard*.  
> **Meta**: Finalizar narração de cinema para o documentário *"The 1983 Soviet Glitch That Almost Ended Humanity"*.

---

## 🎯 Cenas & Prompts Prontos para Copiar e Colar

### 📍 Cena 1: O Alarme Toca (Hook / Tensão Imediata)
- **Arquivo de saída**: Salvar como `scene_1.wav` (ou `.mp3`)
- **Campo `instruct_text` (Comando de atuação)**:
  ```text
  Speak with controlled urgency and mounting dread, deep authoritative baritone documentary tone, crisp articulation, ominous cadence.
  ```
- **Campo `tts_text` (Texto da narração)**:
  ```text
  At 12:15 AM on September 26, 1983, a red siren illuminated a top-secret Soviet bunker outside Moscow. The radar screens confirmed what every officer dreaded: five American nuclear warheads were already in the air.
  ```

---

### 📍 Cena 2: As Vidas em Risco (Escalação Existencial)
- **Arquivo de saída**: Salvar como `scene_2.wav` (ou `.mp3`)
- **Campo `instruct_text` (Comando de atuação)**:
  ```text
  Slow down pace, speak in a grim, somber, heavy baritone, emphasizing the tragic existential weight of three hundred million lives.
  ```
- **Campo `tts_text` (Texto da narração)**:
  ```text
  Soviet protocol gave Lieutenant Colonel Stanislav Petrov exactly twenty minutes to authorize a retaliatory strike that would wipe three hundred million people off the face of the Earth.
  ```

---

### 📍 Cena 3: O Dilemma de Petrov (Suspense / Cliffhanger)
- **Arquivo de saída**: Salvar como `scene_3.wav` (ou `.mp3`)
- **Campo `instruct_text` (Comando de atuação)**:
  ```text
  Intense cinematic suspense, hushed dramatic delivery, deliberate pause after orders, delivering the cliffhanger with chilling mystery.
  ```
- **Campo `tts_text` (Texto da narração)**:
  ```text
  He had a direct line to the Kremlin. His finger hovered over the confirmation switch. But instead of following orders... Petrov decided to trust a hunch.
  ```

---

## 🚀 Opção Rápida: Narração Contínua Completa (1 take só)
Se quiser renderizar o áudio inteiro de uma só vez no RunningHub em vez de cena a cena:
- **Arquivo de saída**: Salvar como `pilot_intro_full.wav`
- **Campo `instruct_text`**:
  ```text
  Authoritative Netflix documentary narrator, deep baritone, slow and suspenseful cadence, deliberate dramatic pauses between sentences, high cinematic tension.
  ```
- **Campo `tts_text`**:
  ```text
  At 12:15 AM on September 26, 1983, a red siren illuminated a top-secret Soviet bunker outside Moscow. The radar screens confirmed what every officer dreaded: five American nuclear warheads were already in the air. Soviet protocol gave Lieutenant Colonel Stanislav Petrov exactly twenty minutes to authorize a retaliatory strike that would wipe three hundred million people off the face of the Earth. He had a direct line to the Kremlin. His finger hovered over the confirmation switch. But instead of following orders... Petrov decided to trust a hunch.
  ```

---

## 📥 Onde colocar os áudios gerados
Coloque os arquivos baixados na pasta:
`darkfactory/data/audio/raw/` (ex: `scene_1.wav`, `scene_2.wav`, `scene_3.wav` ou `pilot_intro_full.wav`).

Depois execute o script mestre de masterização e montagem:
```bash
python run_pilot_pipeline.py --step master-audio
```
O script cuidará da equalização broadcast, compressão, sub-graves de cinema e sincronia de legendas SRT automaticamente!
