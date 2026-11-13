---
name: darkfactory-deploy
description: >-
  Pre-flight validation, test gate, and startup of the DarkFactory Cinema Dashboard
  FastAPI Web SPA on port 8502 with health checks and process management. Use when running /deploy.
---

# DarkFactory Cinema Dashboard Deploy & Launch (`/deploy`)

Workflow para validação de integridade pré-deploy e inicialização do servidor Cinema Dashboard do DarkFactory na porta 8502.

## 🧭 Etapas do Procedimento

### Passo 1: Gate de Testes Automatizados
Antes de subir qualquer processo, a esteira executa os testes para garantir estabilidade:
```powershell
.\venv\Scripts\python.exe -m pytest tests/test_dashboard_api.py -q
```
Se algum teste de API falhar, o deploy é abortado imediatamente com diagnóstico do erro.

### Passo 2: Verificação de Ambiente & Porta
- Checa a presença do arquivo `.env`.
- Valida se as chaves necessárias (`GEMINI_API_KEY`, etc.) estão configuradas.
- Verifica se a porta `8502` está livre para bind (ou encerra processos zumbis).

### Passo 3: Inicialização do Servidor FastAPI
O servidor é iniciado via script dedicado ou comando Uvicorn:
```powershell
.\run_dashboard.bat
```
Ou diretamente via Uvicorn:
```powershell
.\venv\Scripts\python.exe -m uvicorn src.dashboard.app:app --host 0.0.0.0 --port 8502 --reload
```

### Passo 4: Health-Check HTTP
O assistente realiza uma requisição de health check no endpoint local:
```powershell
Invoke-WebRequest -Uri "http://localhost:8502" -UseBasicParsing -TimeoutSec 5
```
Se retornar `StatusCode: 200`, o Cinema Dashboard é considerado operacional.

### Passo 5: Confirmação Operacional
Apresenta o painel com:
- URL de acesso: `http://localhost:8502`
- Status dos pipelines de renderização e áudio em tempo real
- Visualizador de roteiros Nolan, timeline de beats e reprodutor de áudio masterizado
