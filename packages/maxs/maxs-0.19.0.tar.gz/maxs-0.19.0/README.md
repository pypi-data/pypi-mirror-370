# maxs

minimalist ai agent that learns from your conversations

## quick start

```bash
pipx install maxs
maxs
```

## setup your ai provider

**option 1: local**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull qwen3:4b
maxs
```

**option 2: cloud providers**
```bash
# anthropic
export ANTHROPIC_API_KEY="your-key"
MODEL_PROVIDER=anthropic maxs

# openai
export OPENAI_API_KEY="your-key" 
MODEL_PROVIDER=openai maxs

# other providers: bedrock, github, litellm, llamaapi, mistral
```

## what makes maxs special

### 🧠 **remembers everything**
- sees your recent shell commands (bash/zsh history)
- remembers past conversations across sessions
- learns from your conversation patterns

### 🛠️ **powerful built-in tools**
- execute shell commands
- scrape websites and parse html
- run background tasks
- network communication
- nested ai workflows

### 🌐 **team awareness (optional)**
when configured with aws, multiple maxs instances can share context:
- local development + github actions + production servers
- team members see each other's work
- coordinated automation across environments

## basic usage

```bash
# ask questions
maxs "what files are in this directory?"

# execute shell commands  
maxs "!ls -la"
maxs "!git status"

# analyze and process
maxs "analyze the log file and find errors"
maxs "format all python files in this project"

# web tasks
maxs "scrape news from hacker news"

# automation
maxs "monitor the system logs in background"
```

## built-in tools

### default tools (always available)

| tool | what it does | example |
|------|-------------|---------|
| **bash** | run shell commands safely | `check disk space` |
| **environment** | manage settings | `show all environment variables` |
| **tcp** | network communication | `start a web server on port 8080` |
| **scraper** | get data from websites | `scrape product prices from amazon` |
| **use_agent** | use different ai models for specific tasks | `use gpt-4 to write documentation` |
| **tasks** | run things in background | `monitor logs continuously` |

### optional tools (enable when needed)

| tool | what it does | how to enable |
|------|-------------|---------------|
| **dialog** | create interactive forms | `STRANDS_TOOLS="bash,environment,tcp,scraper,use_agent,tasks,dialog" maxs` |
| **event_bridge** | share context with other maxs instances | `STRANDS_TOOLS="bash,environment,tcp,scraper,use_agent,tasks,event_bridge" maxs` |

## smart features

### conversation memory
maxs automatically remembers:
```bash
# session 1
maxs "i'm working on user authentication"

# session 2 (later)
maxs "how's the auth work going?"
# maxs remembers the previous conversation
```

### shell integration
```bash
# maxs sees your recent commands
$ git clone https://github.com/user/repo
$ cd repo
$ maxs "analyze this codebase"
# maxs knows you just cloned a repo and can analyze it
```

### multi-model workflows
```bash
maxs "use claude for creative writing and gpt-4 for code review"
# automatically switches between models for different tasks
```

## team collaboration (advanced)

**first, enable team features:**
```bash
# enable event_bridge tool
export STRANDS_TOOLS="bash,environment,tcp,scraper,use_agent,tasks,event_bridge"
maxs
```

when multiple people use maxs with shared aws setup:

```bash
# developer 1 (local)
maxs "implementing payment processing"

# developer 2 (sees context from dev 1)  
maxs "i see you're working on payments, let me test the api"

# ci/cd pipeline (sees both contexts)
maxs "payment feature tested successfully, deploying to staging"
```

**how to enable team mode:**
1. enable event_bridge tool (see above)
2. set up aws credentials (`aws configure`)
3. one person runs: `maxs "setup event bridge for team collaboration"`
4. team members use same aws account
5. everyone's maxs instances share context automatically

## configuration

### basic settings
```bash
# use different ai provider
MODEL_PROVIDER=anthropic maxs
MODEL_PROVIDER=openai maxs

# use specific model
STRANDS_MODEL_ID=claude-sonnet-4-20250514 maxs

# remember more/less history
MAXS_LAST_MESSAGE_COUNT=50 maxs  # default: 100

# enable all tools
STRANDS_TOOLS="ALL" maxs

# enable specific tools only
STRANDS_TOOLS="bash,scraper" maxs
```

### team settings (advanced)
```bash
# first enable event_bridge
export STRANDS_TOOLS="bash,environment,tcp,scraper,use_agent,tasks,event_bridge"

# aws region for team features
AWS_REGION=us-west-2

# custom team event bus name  
MAXS_EVENT_TOPIC=my-team-maxs

# how many team messages to include
MAXS_DISTRIBUTED_EVENT_COUNT=25
```

## custom tools

drop a python file in `./tools/` directory:

```python
# ./tools/calculator.py
from strands import tool

@tool
def calculate_tip(bill: float, tip_percent: float = 18.0) -> dict:
    tip = bill * (tip_percent / 100)
    total = bill + tip
    return {
        "status": "success", 
        "content": [{"text": f"Bill: ${bill:.2f}\nTip: ${tip:.2f}\nTotal: ${total:.2f}"}]
    }
```

then use it:
```bash
maxs "calculate tip for a $50 bill"
```

## examples

### development workflow
```bash
maxs "!git status"                    # check repo status
maxs "analyze code quality issues"     # review code
maxs "!pytest -v"                     # run tests  
maxs "format all python files"        # clean up code
maxs "!git add . && git commit -m 'refactor'"  # commit changes
```

### system administration  
```bash
maxs "check system health"             # disk, memory, processes
maxs "monitor nginx logs for errors"   # background log monitoring
maxs "!systemctl restart nginx"       # restart services
```

### content and research
```bash
maxs "scrape latest tech news"         # gather information
maxs "summarize the main trends"       # analyze content
```

### automation
```bash
maxs "backup important files to cloud"     # file management
maxs "monitor website uptime every 5 minutes"  # background monitoring
maxs "send alert if disk usage > 90%"     # conditional actions
```

## installation options

### standard installation
```bash
pipx install maxs
```

### development installation
```bash
git clone https://github.com/cagataycali/maxs
cd maxs
pip install -e .
```

### binary distribution
```bash
pip install maxs[binary]
pyinstaller --onefile --name maxs -m maxs.main
# creates standalone ./dist/maxs binary
```

## data and privacy

### local storage
- conversations saved in `/tmp/.maxs/` 
- shell history integration (read-only)
- no data sent to external services (except your chosen ai provider)

### team mode (optional)
- uses aws eventbridge for team communication
- only shares conversation summaries, not full messages
- you control the aws account and data
- requires explicit enablement of event_bridge tool

## troubleshooting

### common issues
```bash
# ollama not responding
ollama serve
maxs

# tool permissions
BYPASS_TOOL_CONSENT=true maxs

# reset conversation history
rm -rf /tmp/.maxs/
maxs

# enable all tools if something is missing
STRANDS_TOOLS="ALL" maxs
```

### getting help
```bash
maxs "show available tools"
maxs "help with configuration"  
maxs "explain how team mode works"
```

## license

mit - use it however you want
