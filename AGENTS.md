# DarkFactory — Autonomous Meta-Orchestrator Protocol (Orquestrador Mestre)

@[Contexto do Projeto](PROJECT_CONTEXT.md)

> **DIRETIVA MANDATÓRIA PERMANENTE**: O assistente opera em **AUTONOMIA TOTAL**. A cada solicitação, analise a demanda, selecione os melhores recursos do ecossistema, execute as etapas multi-step de ponta a ponta sem interrupções desnecessárias, valide os resultados via testes (`pytest`) e mantenha o `state.md` sincronizado.

---

## 🧭 O Ciclo de Orquestração Contínua (5 Passos)

### Passo 1: Análise da Demanda & Varredura de Recursos
Ao receber qualquer mensagem ou solicitação, avalie a natureza da tarefa:
1. **Contexto & Estado do Projeto**: Consulte sempre `PROJECT_CONTEXT.md` para diretrizes de arquitetura cinematográfica e `state.md` para o status atual da esteira.
2. **Skills do Ecossistema**: Verifique `.agents/skills/`. Ative imediatamente skills como `darkfactory-pipeline`, `darkfactory-deploy`, `darkfactory-review`, `darkfactory-status`, `darkfactory-nolan`, além das skills universais `python-patterns`, `python-testing`, `e2e-testing`, `error-handling`, `orchestrator`, `verification-loop`.
3. **Subagentes Especializados**: Quando a tarefa exigir direção autoral cinematográfica, acione o showrunner `nolan-director`. Para testes, utilize `tdd-guide`. Para revisão de código e conformidade de áudio, acione `python-reviewer` e `code-reviewer`.
4. **Resolução Inline Resiliente**: Caso qualquer API externa ou subagente atinja limite de quota, assuma a execução de forma direta e transparente, sem travar o usuário.

---

## 🎭 Matriz de Roteamento Especializado DarkFactory

| Tipo de Demanda | Subagente Recomendado | Skill / Regra a Consultar | Ferramentas Críticas |
| :--- | :--- | :--- | :--- |
| **Showrunner, Roteiro & Storyboard Não-Linear** | `nolan-director` | `darkfactory-nolan`, `nolan-dark-history-director` | `read_file`, `write_file` |
| **Pesquisa Histórica & Verificação de Fontes** | `architect` | `api-design`, `verification-loop` | `run_command`, `read_file` |
| **Engenharia Vocal & Mixagem Acústica (-14 LUFS)** | `python-reviewer` | `python-patterns`, `darkfactory-review` | `run_command`, `edit_file` |
| **Fábrica de Vídeo T2V (RunningHub / MiniMax / Wan)** | `e2e-runner` | `darkfactory-pipeline`, `error-handling` | `run_command`, `edit_file` |
| **Cinema Dashboard Web SPA (:8502)** | `architect` | `darkfactory-deploy`, `api-design` | `run_command`, `edit_file` |
| **Qualidade de Código & Suíte de Testes (Pytest)** | `tdd-guide` | `python-testing`, `tdd-workflow` | `run_command` |
| **Segurança & Credenciais (.env)** | `security-reviewer` | `verification-loop` | `read_file` |

---

### Passo 2: Execução Rigorosa & Auto-Recuperação
- **Autonomia em Execução**: Execute tarefas de forma proativa. Não peça confirmação para ler arquivos, rodar testes ou formatar código.
- **Auto-Correção Obrigatória**: Se um comando falhar com erro de teste quebrado, auto-diagnostique a causa raiz e aplique a correção antes de reportar.
- **Transparência Operacional**: Indique a rota de orquestração escolhida:
  `🎯 Orquestrador: [Skill: <nome> | Agente: <nome> | Ferramenta: <nome>]`

---

### Passo 3: Persistência & Manutenção de Estado
- Ao concluir alterações de fases ou refatorações, atualize o `state.md` para refletir o status real do pipeline.
- Mantenha a integridade dos arquivos de dados (`data/scripts/`, `data/audio/`, `data/final/`, `data/quarantine/`).

---

### Passo 4: Validação de Qualidade
- Execute a suíte de testes com zero tolerância a regressões:
  ```powershell
  .\venv\Scripts\python.exe -m pytest -q
  ```

---

### Passo 5: Git Commit & Push Mandatório (Hard Gate na branch `main`)
- **Mandato Permanente de Sincronização**: Ao concluir qualquer implementação, correção ou nova funcionalidade:
  1. Validar a integridade da aplicação via suíte de testes (`pytest`).
  2. Sincronizar o `state.md` com as métricas e status reais.
  3. Adicionar todos os arquivos modificados e untracked via `git add .`.
  4. Realizar commit semântico e descritivo (`git commit -m "feat/fix/chore: ..."`).
  5. **Executar `git push origin main` imediatamente**, garantindo que o repositório remoto esteja atualizado com zero pendências locais (*working tree clean*).
  6. É terminantemente proibido encerrar a tarefa sem realizar o `git push`.
