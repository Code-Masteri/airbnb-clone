```
████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗
╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║
   ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║
   ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║
   ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███████╗
   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝

██████╗ ███████╗███╗   ██╗ ██████╗██╗  ██╗
██╔══██╗██╔════╝████╗  ██║██╔════╝██║  ██║
██████╔╝█████╗  ██╔██╗ ██║██║     ███████║
██╔══██╗██╔══╝  ██║╚██╗██║██║     ██╔══██║
██████╔╝███████╗██║ ╚████║╚██████╗██║  ██║
╚═════╝ ╚══════╝╚═╝  ╚═══╝ ╚═════╝╚═╝  ╚═╝
```

# TerminalBench Tasks

> A curated collection of hard DevOps & SWE evaluation tasks for AI coding agents,
> built on the TerminalBench 2.0 / Harbor framework.

Each task is a **reproducible Docker environment** with intentional bugs, a golden solution,
and functional pytest verification — designed to push AI agents to their limits.

---

## Architecture

\`\`\`
┌─────────────────────────────────────────────────────────┐
│ Harbor Framework │
│ │
│ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│ │ task │ │ Docker │ │ AI Agent │ │
│ │ .toml │───▶│ Environment───▶│ (terminus-2) │ │
│ └──────────┘ │ (broken) │ │ │ │
│ └──────────┘ │ reads instruction│ │
│ ┌──────────┐ │ │ explores files │ │
│ │instruction │ │ runs commands │ │
│ │ .md │─────────┘ │ fixes bugs │ │
│ └──────────┘ └────────┬─────────┘ │
│ │ │
│ ┌──────────┐ ┌────────▼─────────┐ │
│ │ solution │ oracle │ Verifier │ │
│ │ solve.sh │───▶ agent ────────▶│ pytest tests │ │
│ └──────────┘ │ reward: 0 or 1 │ │
│ └──────────────────┘ │
└─────────────────────────────────────────────────────────┘
\`\`\`

---

## Tasks

| Task                    | Domain           | Bugs | Difficulty      |
| ----------------------- | ---------------- | ---- | --------------- |
| `distributed_job_queue` | Backend / DevOps | 6    | ████████░░ Hard |

---

## Usage

\`\`\`bash

# Run oracle (your solution vs your tests)

harbor run -p "./distributed_job_queue" -a oracle

# Run AI agent (10 attempts)

harbor run -p "./distributed_job_queue" \
 -a terminus-2 \
 --model groq/moonshotai/kimi-k2-instruct-0905 \
 -k 10 -n 1
\`\`\`

---

## Stack

- **Harbor** — task runner & evaluation harness
- **Docker** — isolated reproducible environments
- **pytest** — functional verification
- **Groq / Kimi K2** — LLM agent backend
- **Python 3.12**
