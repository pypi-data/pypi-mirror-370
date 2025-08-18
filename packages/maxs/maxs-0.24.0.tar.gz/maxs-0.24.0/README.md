# maxs

**minimalist ai agent with maximum capabilities**

comprehensive ai development platform featuring:
- 🔥 **hot reload tool creation** - extend capabilities instantly
- 🎙️ **voice-powered workflows** - hands-free development with "max" trigger
- 📡 **p2p encrypted communication** - agent-to-agent mesh networking over bluetooth
- 🧠 **advanced memory systems** - sqlite + bedrock with full-text search
- 📊 **data analytics platform** - sql databases, graph dbs, visualizations  
- 🌐 **universal connectivity** - any api, database, or service integration
- ⚡ **parallel execution** - maximum speed with concurrent operations
- 👥 **distributed intelligence** - team collaboration across environments

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

### 📡 **p2p encrypted communication (bitchat)**
maxs instances can communicate directly with each other over bluetooth:
```bash
# start p2p networking
maxs "start bitchat and enable agent triggers"

# agents automatically respond to each other
# agent alice says: "max, analyze the server logs" 
# agent bob automatically processes and responds

# encrypted channels for teams
maxs "join secure team channel with password"
maxs "send project status to p2p network"
```

bitchat features:
- **end-to-end encryption** - noise protocol with forward secrecy
- **mesh networking** - bluetooth low energy, no internet required
- **agent triggers** - agents respond to each other automatically
- **secure channels** - password-protected team communication
- **peer discovery** - automatic detection of nearby agents
- **distributed workflows** - coordinate tasks across agent network

### 🧠 **remembers everything**
- sees your recent shell commands (bash/zsh history)
- remembers past conversations across sessions
- learns from your conversation patterns

### 🛠️ **powerful built-in tools (50+)**
- execute shell commands with real-time output
- scrape websites and parse html with beautiful soup
- run background tasks with persistence
- network communication (TCP servers/clients)
- nested ai workflows with multiple models
- voice interaction with speech recognition & synthesis
- data analysis with SQL, graph databases, visualizations
- github integration with GraphQL API
- memory systems with full-text search
- hot reload tool creation system

### 🎙️ **voice-powered workflows**
maxs supports hands-free voice interaction:
```bash
# start voice listening
maxs
> listen(action="start", trigger_keyword="max")

# then just speak
"max, what time is it?"        # automatic response
"max, create a backup script"  # builds tools via voice
"max, check my emails"         # integrates with services
```

voice features:
- **trigger keyword** - say "max" to activate responses automatically
- **realistic speech** - generates natural audio with emotions and sound effects
- **multiple tts engines** - bark, dia, aws polly, macos native
- **conversation context** - remembers what you said and its own responses
- **echo detection** - won't reply to its own voice

### 🔥 **hot reload tool creation**
create custom tools instantly - no restart needed:
```python
# save this to ./tools/weather.py
from strands import tool

@tool  
def weather(city: str) -> str:
    # your implementation
    return f"weather for {city}"
```

then immediately use:
```bash
maxs "get weather for san francisco"
# tool is automatically loaded and available
```

features:
- **instant availability** - save .py file → tool ready
- **live development** - modify tools while maxs runs
- **full documentation** - complete guide at `/docs/tool-creation.md`
- **any functionality** - create tools for apis, data processing, automation

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

# voice interaction (hands-free)
maxs  # start interactive mode
> listen(action="start", trigger_keyword="max")
# then just speak: "max, what time is it?"

# p2p agent communication (no internet required)
maxs "start bitchat and join team channel"
maxs "enable agent triggers with 'max' keyword" 
# agents on bluetooth mesh automatically respond to each other

# analyze and process
maxs "analyze the log file and find errors"
maxs "format all python files in this project"

# data analysis
maxs "query the database and create a chart"
maxs "analyze csv data and show correlations"

# web tasks
maxs "scrape news from hacker news"
maxs "fetch github issues and summarize"

# automation & memory
maxs "remember this: we're using postgresql for user data"
maxs "search my memory for database decisions"
maxs "monitor the system logs in background"

# tool creation (instant)
maxs "create a tool to check cryptocurrency prices"
# maxs creates ./tools/crypto_prices.py instantly
```

## built-in tools (50+ available)

### 🎯 core maxs tools

| tool | what it does | example |
|------|-------------|---------|
| **shell** | interactive shell with real-time output | `check disk space and monitor processes` |
| **environment** | manage environment variables | `show aws credentials and update settings` |
| **tcp** | network servers & clients | `start tcp server on port 8080` |
| **scraper** | advanced web scraping | `scrape product data from e-commerce sites` |
| **use_agent** | multi-model ai workflows | `use claude for writing, gpt-4 for code` |
| **tasks** | background processes | `monitor logs continuously in background` |
| **bitchat** | p2p encrypted mesh communication | `join secure channels, agent-to-agent networking` |

### 🎙️ voice & audio tools

| tool | what it does | example |
|------|-------------|---------|
| **listen** | speech-to-text with trigger keywords | say `"max, what time is it?"` hands-free |
| **speak** | text-to-speech (aws polly, macos say) | `convert text to high-quality speech` |
| **realistic_speak** | natural speech with emotions | `"[S1] hello! (laughs) how are you?"` |
| **speak_bark** | multilingual tts with sound effects | `generate speech with [music] and [sighs]` |

### 🧠 memory & knowledge systems

| tool | what it does | example |
|------|-------------|---------|
| **sqlite_memory** | advanced memory with full sql | `store and search with fts5 full-text search` |
| **memory** | aws bedrock knowledge base | `semantic search across stored documents` |
| **retrieve** | knowledge base search | `find relevant info from stored knowledge` |
| **store_in_kb** | async knowledge storage | `store conversations in background` |

### 📊 data & analytics tools

| tool | what it does | example |
|------|-------------|---------|
| **sql_tool** | universal sql client | `connect to postgresql, mysql, sqlite, oracle` |
| **graph_db_tool** | graph database client | `query neo4j and arangodb with cypher/aql` |
| **data_viz_tool** | charts & visualizations | `create bar, line, scatter plots with plotly` |
| **python_repl** | interactive python execution | `run data analysis scripts with pandas` |

### 🌐 integration & apis

| tool | what it does | example |
|------|-------------|---------|
| **http_request** | universal http client | `call any rest api with authentication` |
| **use_github** | github graphql api v4 | `create issues, prs, manage repositories` |
| **graphql** | any graphql endpoint | `query shopify, contentful, hasura apis` |
| **slack** | team communication | `send messages, get events, manage channels` |
| **use_aws** | aws service integration | `manage ec2, s3, lambda with boto3` |

### 🎨 content creation

| tool | what it does | example |
|------|-------------|---------|
| **diagram** | aws & uml diagrams | `create cloud architecture and flowcharts` |
| **generate_image** | ai image creation | `generate logos, illustrations, charts` |
| **editor** | advanced file editing | `modify code with syntax highlighting` |
| **journal** | note-taking & memory | `create daily logs and personal notes` |

### 🚀 development & automation

| tool | what it does | example |
|------|-------------|---------|
| **create_subagent** | distributed ai via github actions | `delegate tasks to specialized agents` |
| **load_tool** | dynamic tool loading | `load custom tools from python files` |
| **workflow** | complex task automation | `orchestrate multi-step processes` |
| **batch** | bulk processing operations | `process hundreds of files simultaneously` |
| **fetch_github_tool** | download tools from github | `install community tools dynamically` |

### 🔧 system & utilities

| tool | what it does | example |
|------|-------------|---------|
| **calculator** | mathematical calculations | `solve complex equations and conversions` |
| **current_time** | date & time information | `get timestamps in any timezone` |
| **file_read/write** | file operations | `read configs, write reports, manage files` |
| **image_reader** | image analysis & ocr | `extract text from screenshots and photos` |
| **cron** | task scheduling | `schedule recurring automated tasks` |

### 📋 optional integrations (require setup)

| tool | what it does | setup required |
|------|-------------|----------------|
| **dialog** | interactive ui forms | `pip install prompt-toolkit` |
| **event_bridge** | team context sharing | aws credentials + `MAXS_EVENT_TOPIC` |
| **use_computer** | screen interaction | platform-specific dependencies |
| **mcp_client** | external tool integration | `MCP_CONFIG` environment variable |

## smart features

## smart features

### 🧠 **advanced memory systems**
maxs has sophisticated context awareness:
```bash
# triple memory architecture
maxs "remember: we're using react for the frontend"  # stored in sqlite + bedrock
maxs "what frontend tech are we using?"              # recalls from memory
# searches across: sqlite full-text + aws bedrock + conversation history
```

memory features:
- **sqlite memory** - full-text search, sql queries, rich metadata
- **knowledge base** - aws bedrock semantic search and storage  
- **conversation context** - remembers 200+ recent messages
- **distributed memory** - shares context with team members

### 🎙️ **voice interaction**
hands-free operation with natural conversation:
```bash
# start voice mode
maxs
> listen(action="start", trigger_keyword="max")

# then just speak naturally
"max, analyze the database performance"     # creates reports
"max, deploy to staging"                    # runs deployment scripts
"max, create a monitoring dashboard"        # builds visualization tools
```

### 🔥 **hot reload development**
extend capabilities instantly without restart:
```bash
# session 1: create tool
maxs "create a weather tool for openweathermap"
# saves to ./tools/weather.py

# session 2: tool ready immediately  
maxs "get weather for tokyo"
# uses the newly created weather tool
```

### 🤝 **context-aware automation**
maxs understands your workflow and environment:
```bash
# maxs sees your recent git commands
$ git clone https://github.com/user/repo
$ cd repo
$ maxs "analyze this codebase and suggest improvements"
# automatically knows you're working with a fresh repo

# maxs remembers project context
maxs "we're using postgresql"           # stores in memory
# later...
maxs "create database migration script" # remembers postgresql context
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
MAXS_LAST_MESSAGE_COUNT=50 maxs  # default: 200

# enable all tools
STRANDS_TOOLS="ALL" maxs

# enable specific tools only
STRANDS_TOOLS="sql_tool,data_viz_tool,listen,sqlite_memory" maxs
```

### 🎙️ voice & audio settings
```bash
# voice interaction
maxs
> listen(action="start", trigger_keyword="max", model_name="base")

# text-to-speech configuration
maxs
> speak("hello world", mode="polly", voice_id="Joanna")
> realistic_speak("[S1] hello! (laughs) how are you?")
> speak_bark("hello [music] this is amazing!")
```

### 🧠 memory & knowledge base settings
```bash
# sqlite memory (local)
# automatically uses ~/.maxs/sqlite_memory.db

# aws bedrock knowledge base
STRANDS_KNOWLEDGE_BASE_ID=your-kb-id maxs

# memory with retrieval context
maxs "remember this important decision"  # stores in both systems
maxs "what decisions did we make?"       # searches across all memory
```

### 🔌 external integrations
```bash
# mcp (model context protocol) integration
MCP_CONFIG='{"command": "uvx", "args": ["strands-agents-mcp-server"]}' maxs

# github integration 
GITHUB_TOKEN=your-token maxs

# slack integration
SLACK_BOT_TOKEN=xoxb-your-bot-token maxs
SLACK_APP_TOKEN=xapp-your-app-token maxs

# aws services
AWS_REGION=us-west-2 maxs
```

### team settings (advanced)
```bash
# first enable event_bridge
export STRANDS_TOOLS="event_bridge,tcp,scraper,use_agent,tasks,sqlite_memory,sql_tool"

# aws region for team features
AWS_REGION=us-west-2

# custom team event bus name  
MAXS_EVENT_TOPIC=my-team-maxs

# how many team messages to include
MAXS_DISTRIBUTED_EVENT_COUNT=25

# shared knowledge base for team
STRANDS_KNOWLEDGE_BASE_ID=team-knowledge-base-id
```

## 🔥 hot reload tool creation

maxs has a revolutionary hot reload system - create tools instantly without restart:

### instant tool development
```python
# save this to ./tools/weather.py
from strands import tool
import requests

@tool
def weather(city: str, units: str = "metric") -> dict:
    """Get current weather for any city using OpenWeatherMap API."""
    api_key = os.getenv("OPENWEATHER_API_KEY", "demo-key")
    url = f"https://api.openweathermap.org/data/2.5/weather"
    
    response = requests.get(url, params={
        "q": city, "appid": api_key, "units": units
    })
    
    if response.status_code == 200:
        data = response.json()
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        return {
            "status": "success",
            "content": [{"text": f"🌡️ {city}: {temp}°{'C' if units=='metric' else 'F'}, {desc}"}]
        }
    else:
        return {
            "status": "error", 
            "content": [{"text": f"❌ Weather data not available for {city}"}]
        }
```

**immediately use it:**
```bash
maxs "get weather for tokyo"
# tool is automatically loaded and working!
```

### advanced tool patterns
```python
# ./tools/database_analyzer.py  
from strands import tool

@tool
def db_analyzer(action: str, connection_string: str = None, **kwargs) -> dict:
    """Advanced database analysis tool with multiple actions."""
    if action == "schema":
        return analyze_schema(connection_string)
    elif action == "performance":  
        return check_performance(connection_string)
    elif action == "backup":
        return create_backup(connection_string, **kwargs)
    # ... more actions
```

### tool categories you can create instantly
- **🌐 api integrations** - weather, finance, social media, any rest/graphql api
- **🔧 system utilities** - process monitors, file managers, system health checks  
- **📊 data processors** - csv analyzers, json transformers, report generators
- **🤖 automation tools** - schedulers, watchers, batch processors
- **🎨 creative tools** - image processors, content generators, formatters
- **🔐 security tools** - log analyzers, vulnerability scanners, audit tools

### development workflow
1. **save** python file to `./tools/filename.py`
2. **test** immediately - `maxs "use my new tool"`  
3. **iterate** - modify file and test changes instantly
4. **deploy** - tools persist across maxs sessions

## 📊 data analytics platform

maxs includes comprehensive data analysis capabilities:

### database connectivity
```bash
# connect to any sql database  
maxs "connect to my postgresql database and analyze user growth"
maxs "query mysql sales data and create monthly reports"
maxs "run complex sql analytics on sqlite database"

# graph databases
maxs "query neo4j for user relationship patterns"  
maxs "analyze social network data in arangodb"
```

### data visualization
```bash
# create charts from any data source
maxs "create bar chart of quarterly sales" 
maxs "generate scatter plot correlation analysis"
maxs "build interactive dashboard with plotly"
maxs "export visualization as png, svg, or html"
```

### advanced analytics workflows
```bash
# end-to-end data pipeline
maxs "extract data from api, store in database, create visualization"

# memory-driven analytics  
maxs "remember: customer churn analysis shows 15% monthly rate"
maxs "search my analytics memory for churn patterns"
maxs "update the churn model with latest data"

# sql with memory integration
maxs
> sqlite_memory(action="sql", sql_query="SELECT * FROM memories WHERE tags LIKE '%analytics%'")
```

### supported data sources
- **sql databases:** postgresql, mysql, sqlite, sql server, oracle, mariadb
- **graph databases:** neo4j (cypher), arangodb (aql)  
- **apis:** any rest/graphql endpoint with authentication
- **files:** csv, json, excel, parquet via pandas integration
- **cloud services:** aws s3, redshift via boto3 integration

## installation options
**documentation:** complete guide at `/docs/tool-creation.md`

## examples

### 🔊 voice-powered development
```bash
# hands-free coding workflow  
maxs
> listen(action="start", trigger_keyword="max")

# then just speak:
"max, analyze the current database schema"
"max, create a backup script for production"  
"max, check the server logs for errors"
"max, generate a performance report"
```

### 💻 development workflow
```bash
maxs "!git status"                    # check repo status
maxs "analyze code quality issues"     # review code with advanced tools
maxs "create unit tests for auth.py"  # generates test files  
maxs "!pytest -v"                     # run tests
maxs "create deployment automation"    # builds ci/cd tools
maxs "!git add . && git commit -m 'add tests and deploy'"
```

### 📊 data analysis & visualization  
```bash
maxs "connect to postgresql and analyze user signup trends"
maxs "create a graph database of user relationships"
maxs "query sales data and generate revenue charts"  
maxs "export customer data to csv and create dashboards"
maxs "analyze log files and create error rate visualizations"
```

### 🧠 advanced memory & knowledge
```bash
maxs "remember: we're migrating to microservices architecture"
maxs "store this api documentation in knowledge base"
maxs "search my memory for database migration decisions" 
maxs "what did we decide about the user authentication system?"
```

### 🤖 distributed ai & automation
```bash
maxs "create subagent to monitor production metrics"
maxs "delegate code review task to specialized agent" 
maxs "setup background task to sync data daily"
maxs "create github tool to automate release notes"
```

### 🌐 system administration  
```bash
maxs "check system health and create monitoring dashboard"
maxs "analyze nginx logs and setup alerting"  
maxs "!systemctl restart nginx"       # restart services
maxs "create automated backup system for databases"
```

### 🔗 api integration & web tasks
```bash
maxs "scrape latest tech news and summarize trends"
maxs "connect to stripe api and analyze payment data"
maxs "setup slack bot for team notifications" 
maxs "create webhook handler for github events"
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

### 🧠 local memory systems
- **conversation history** saved in `/tmp/.maxs/` with session persistence
- **sqlite memory** stored in `~/.maxs/sqlite_memory.db` with full-text search  
- **voice transcripts** saved in `./.listen/transcripts.jsonl` (when using listen tool)
- **shell history integration** (read-only) from bash/zsh history
- **tool creation** - custom tools in `./tools/` directory
- **generated content** - diagrams, visualizations, audio files in local directories

### 🔒 privacy controls  
- **no external data transmission** - except to your chosen ai provider and explicitly used services
- **local-first architecture** - core functionality works completely offline
- **explicit consent** - tool operations requiring external access ask for permission
- **opt-in integrations** - team features, knowledge bases, external apis require explicit setup

### ☁️ optional cloud integrations
when you choose to enable them:

- **aws bedrock knowledge base** - persistent memory with semantic search (requires aws setup)
- **team collaboration** - uses aws eventbridge for team context sharing (optional)  
- **github integration** - api access for repository management (requires github token)
- **slack integration** - team communication and notifications (requires slack tokens)
- **external apis** - weather, finance, etc. (requires api keys for specific tools)

### 🛡️ security features
- **environment variable protection** - sensitive values masked in logs
- **path traversal prevention** - file operations are sanitized  
- **sql injection protection** - parameterized queries in database tools
- **consent prompts** - destructive operations require confirmation (bypass with `BYPASS_TOOL_CONSENT=true`)
## 🚀 what makes maxs a development platform

### 🧠 **triple memory architecture**
- **sqlite memory** - local full-text search with sql capabilities
- **bedrock knowledge base** - cloud semantic search and long-term storage  
- **conversation context** - 200+ message history with distributed team sharing

### 🎙️ **voice-first development**
- **trigger keyword** - say "max, deploy to staging" for hands-free operation
- **context awareness** - voice commands understand current project state
- **realistic speech** - generates natural responses with emotions and sound effects  
- **echo detection** - won't get confused by hearing its own voice

### ⚡ **parallel execution engine**  
- **concurrent tool calls** - runs multiple operations simultaneously for maximum speed
- **background processing** - long tasks run without blocking conversation
- **distributed computation** - delegates work to subagents via github actions

### 🔗 **universal connectivity**
- **any database** - postgresql, mysql, neo4j, arangodb with native drivers
- **any api** - rest, graphql, webhooks with comprehensive authentication  
- **any service** - github, slack, aws, custom integrations via mcp protocol
- **any model** - switch between claude, gpt, local models for different tasks

### 🛠️ **live extensibility**
- **hot reload system** - create tools while maxs is running  
- **github tool marketplace** - download and install community tools
- **mcp integration** - connect to external tool ecosystems
- **dynamic loading** - extend capabilities without restart

## 🌟 advanced workflows

### 🎯 **end-to-end data pipelines**
```bash
# complete data analysis workflow
maxs "connect to postgresql, analyze user behavior, create visualizations, store insights in memory, generate executive report, and send summary to slack"
# maxs executes all steps in parallel where possible
```

### 📡 **decentralized agent networking**  
```bash
# p2p mesh communication without internet
maxs "start bitchat and connect to agent network"
maxs "join team channel with password for secure coordination"
maxs "enable agent triggers so agents respond to each other automatically"
# agents communicate directly over encrypted bluetooth mesh
```

### 🤖 **distributed ai orchestration**  
```bash
# delegate specialized tasks
maxs "create subagent for security audit on github actions"
maxs "create subagent for performance testing with detailed metrics"  
maxs "create subagent for documentation generation using claude opus"
# each runs independently with specialized models and tools
```

### 🎙️ **voice-driven automation**
```bash
# production monitoring via voice
"max, check production database health"
"max, analyze error rates and create incident report"  
"max, update team via slack about system status"
# hands-free operations management
```

### 🧠 **intelligent memory workflows**
```bash
# context-aware development
maxs "remember: we're using stripe for payments and postgresql for user data"
maxs "create payment processing tool that works with our architecture"  
# tool creation uses stored context about stripe + postgresql

# knowledge base management
maxs "store this api documentation in knowledge base"
maxs "search knowledge for similar integration patterns"
maxs "retrieve best practices for payment processing"
```

### 🔄 **hot reload development cycles**
```bash
# instant iteration workflow
maxs "create a kubernetes deployment tool"
# saves to ./tools/k8s_deploy.py

maxs "test the kubernetes tool with staging cluster"  
# tool works immediately

# modify ./tools/k8s_deploy.py in editor
maxs "test the updated kubernetes tool"
# changes active instantly, no restart needed
```

## troubleshooting
- **session isolation** - each maxs instance operates independently by default

## troubleshooting

### 🔧 common issues

**ai provider problems:**
```bash
# ollama not responding
ollama serve
maxs

# anthropic/openai api issues
MODEL_PROVIDER=ollama maxs  # fallback to local

# model not found
ollama pull qwen3:4b  # install local model
```

**🎙️ voice & audio issues:**
```bash  
# voice recognition not working
pip install openai-whisper sounddevice webrtcvad
maxs
> listen(action="list_devices")  # check available microphones

# speech synthesis problems
pip install torch torchaudio transformers  # for realistic speech
maxs
> speak("test", mode="fast")  # test basic tts
```

**🧠 memory & database issues:**
```bash
# sqlite memory problems  
rm ~/.maxs/sqlite_memory.db  # reset local memory
maxs
> sqlite_memory(action="stats")  # check status

# knowledge base connectivity
AWS_REGION=us-west-2 STRANDS_KNOWLEDGE_BASE_ID=your-kb-id maxs
```

**📊 data tool issues:**
```bash
# database connection problems
maxs
> sql_tool(action="connect", database_type="postgresql", host="localhost")

# visualization dependencies
pip install matplotlib plotly pandas numpy seaborn
```

**⚙️ general troubleshooting:**
```bash
# tool permissions
BYPASS_TOOL_CONSENT=true maxs

# reset conversation history
rm -rf /tmp/.maxs/
maxs

# enable all tools if something is missing
STRANDS_TOOLS="ALL" maxs

# check tool availability  
maxs
> environment(action="list", prefix="STRANDS")
```

### 🆘 getting help
```bash
maxs "show all available tools and their capabilities"
maxs "help with voice setup and configuration"  
maxs "explain how memory systems work"
maxs "troubleshoot database connection issues"
maxs "test the hot reload tool creation system"

# voice help (hands-free)
"max, help me troubleshoot voice recognition"
"max, test all the data analysis tools"  
"max, show me how to create custom tools"
```

### 📋 debug information
```bash  
# get detailed system info
maxs
> environment(action="list")           # all environment variables
> sqlite_memory(action="stats")        # memory system status
> listen(action="status")              # voice system status  
> sql_tool(action="connect", ...)      # database connectivity
```

## license

mit - use it however you want
