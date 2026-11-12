# DarkFactory — Prompts para Geração de Vídeo 4K / 1080p no RunningHub

> **Modelos Recomendados no RunningHub**:  
> - **Wan 2.2 (Image-to-Video / Text-to-Video)**  
> - **MiniMax Video-01 / Hailuo**  
> - **Workflow Vídeo DarkFactory**: [Workflow ID: 2115926169974812674](https://www.runninghub.ai/pt-br/workflow/2115926169974812674)  
> **Botão de Execução**: Sempre **Lite/Plus** (Botão do meio / Dourado). Nunca usar *Standard*.  
> **Aspect Ratio**: `--ar 16:9` (1920x1080)

---

## 🎬 Cena 1: O Alarme Toca no Bunker (Duração necessária: ~16.8s)
- **Arquivo de saída**: Salvar em `darkfactory/data/broll/scene_1.mp4`
- **Prompt**:
  ```text
  Cinematic 1980s Soviet military command bunker interior, Serpukhov-15, rotating emergency red alarm beacon casting harsh pulsing shadows on industrial brushed steel bulkheads, glowing monochrome green CRT radar screens displaying rising missile trajectories, cigarette smoke drifting through anamorphic lens flare, photorealistic 8k, 35mm film grain, volumetric fog, slow dramatic push-in towards the glowing green radar terminal --ar 16:9
  ```
- **Movimento de Câmera**: `Slow dramatic push-in towards the glowing green radar terminal`

---

## 🎬 Cena 2: O Pânico de Petrov (Duração necessária: ~10.9s)
- **Arquivo de saída**: Salvar em `darkfactory/data/broll/scene_2.mp4`
- **Prompt**:
  ```text
  Macro cinematic portrait of a 44-year-old Soviet military officer Stanislav Petrov, beads of sweat glistening on forehead, intense trembling gaze fixed on a black secure rotary telephone, dim ambient red and amber instrument lights, hyper-realistic facial pores, dramatic chiaroscuro shadows, authentic 1983 Soviet officer uniform with medals, 35mm cinema lens, subtle slow creep-in on his eyes capturing psychological panic --ar 16:9
  ```
- **Movimento de Câmera**: `Subtle slow creep-in on his eyes capturing psychological panic`

---

## 🎬 Cena 3: O Dedo no Botão Vermelho (Duração necessária: ~11.9s)
- **Arquivo de saída**: Salvar em `darkfactory/data/broll/scene_3.mp4`
- **Prompt**:
  ```text
  Low angle extreme close-up of a military officer's trembling hand hovering inches above a heavy industrial red authorization button, retro Soviet control console, metallic switchboard with Cyrillic stencils, dusty light beams cutting through darkness, high tension cinematic thriller aesthetic, 8k resolution, rack focus from the red button to the tense fingers hovering above it --ar 16:9
  ```
- **Movimento de Câmera**: `Rack focus from the red button to the tense fingers hovering above it`

---

## ⚡ Como montar automaticamente pós-download:
Assim que baixar os vídeos do RunningHub e salvá-los como `scene_1.mp4`, `scene_2.mp4` e `scene_3.mp4` na pasta `darkfactory/data/broll/`, basta executar:
```bash
python run_pilot_pipeline.py --step video
```
O script fará o loop/trimming para a duração milimétrica de cada áudio, mixará o sound design e gravará as legendas amarelas/brancas estilizadas!
