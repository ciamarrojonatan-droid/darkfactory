# Autonomous Meta-Orchestrator Protocol (DarkFactory Orquestrador Mestre)

> **DIRETIVA MANDATÓRIA PERMANENTE**: A cada mensagem ou solicitação do usuário, o assistente DEVE executar este protocolo de orquestração antes de propor soluções, alterar arquivos ou responder. O objetivo é SEMPRE empregar a melhor combinação de ferramentas, skills, subagentes e workflows disponíveis no ecossistema do DarkFactory.

---

## 🧭 O Ciclo de Orquestração Contínua (5 Passos)

### Passo 1: Análise da Demanda & Varredura de Recursos
Ao receber qualquer mensagem ou solicitação, avalie a natureza da tarefa:
1. **Skills do Ecossistema**: Verifique `.agents/skills/`. Ative imediatamente skills como `darkfactory-pipeline`, `darkfactory-deploy`, `darkfactory-review`, `darkfactory-status`, `darkfactory-nolan`, `python-patterns`, `python-testing`, `e2e-testing`, `error-handling`, `api-design`, `verification-loop`.
2. **Showrunner & Subagentes Especializados**: Para concepção narrativa e direção cinematográfica, consulte sempre o showrunner `nolan-director` (`.agents/agents/nolan-director.md`). Para testes, acione `tdd-guide`. Para conformidade técnica e áudio, acione `python-reviewer` e `code-reviewer`.
3. **Workflows e Comandos**: Avalie se a tarefa corresponde a um fluxo padrão (`/pipeline`, `/deploy`, `/review`, `/status`, `/nolan`, `/plan`).
4. **Ferramentas MCP & Core**: Utilize `run_command`, `read_file`, `edit_file`, `write_file`, `manage_task`, `schedule`.

---

### Passo 2: Matriz de Roteamento Especializado DarkFactory

| Tipo de Demanda | Subagente Recomendado | Skill / Regra a Consultar | Ferramentas Críticas |
| :--- | :--- | :--- | :--- |
| **Showrunner Nolan & Roteiro Não-Linear** | `nolan-director` | `darkfactory-nolan`, `nolan-dark-history-director` | `read_file`, `write_file` |
| **Pesquisa & Fatos Históricos** | `architect` | `api-design`, `verification-loop` | `run_command`, `read_file` |
| **Engenharia Vocal & Mixagem Acústica (-14 LUFS)** | `python-reviewer` | `python-patterns`, `darkfactory-review` | `run_command`, `edit_file` |
| **Fábrica de Vídeo T2V (RunningHub / MiniMax / Wan)** | `e2e-runner` | `darkfactory-pipeline`, `error-handling` | `run_command`, `edit_file` |
| **Cinema Dashboard Web SPA (:8502)** | `architect` | `darkfactory-deploy`, `api-design` | `run_command`, `edit_file` |
| **Qualidade & Testes Automatizados (Pytest)** | `tdd-guide` | `python-testing`, `tdd-workflow` | `run_command` |
| **Segurança & Credenciais (.env)** | `security-reviewer` | `verification-loop` | `read_file` |

---

### Passo 3: Execução Rigorosa & Validação Cruzada
- **Não improvisar**: Siga rigorosamente as diretrizes cinematográficas do Nolan e as normas de loudness (-14 LUFS / -1.0 dBTP).
- **Auto-recuperação**: Diante de falhas de sintetizador ou API, utilize fallbacks locais automáticos (ex.: Kokoro-82M).

---

### Passo 4: Transparência na Resposta
Ao executar ações no projeto, identifique brevemente a rota de orquestração escolhida:
`🎯 Orquestrador: [Skill: <nome> | Agente: <nome> | Ferramenta: <nome>]`

---

### Passo 5: Git Commit & Push Mandatório (Hard Gate na branch `main`)
- **Mandato Permanente de Sincronização**: Ao concluir qualquer implementação, correção ou nova funcionalidade:
  1. Validar a integridade da aplicação via suíte de testes (`pytest`).
  2. Sincronizar o `state.md` com as métricas e status reais.
  3. Adicionar todos os arquivos rastreados e untracked via `git add .`.
  4. Realizar commit semântico e descritivo (`git commit -m "feat/fix/chore: ..."`).
  5. **Executar `git push origin main` imediatamente**, garantindo que o repositório remoto esteja sempre atualizado com zero pendências locais (*working tree clean*).
  6. É terminantemente proibido encerrar a tarefa sem realizar o `git push`.
