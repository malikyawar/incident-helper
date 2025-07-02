# 🛠️ Incident Helper CLI

## An AI-powered terminal assistant for SREs and DevOps engineers
Triage incidents, interpret logs, and debug systems, right from your terminal, powered by local LLMs like Mistral (via Ollama).


## 🚀 Features

- 🔍 Accepts natural-language incident reports
- 💬 Conversational CLI: ask → guide → suggest → fix
- 🧠 Remembers session context (alert, OS, answers)
- 📂 Helps with logs, system metrics, SSH access
- 🧩 AI model plug-in ready (Ollama, OpenAI, Claude)
- 🐍 Python CLI built with Typer
- 🔌 Extensible design with plugin-ready resolvers


## 📦 Prerequisites

- Python 3.8+
- [Ollama](https://ollama.com) installed and a model pulled (e.g. `ollama run mistral`)
- Git & pip


## ⚙️ Installation

```bash
git clone https://github.com/yourname/incident-helper.git
cd incident-helper
pip install -e .
````

## 💡 How It Works

* Users start the tool with `incident-helper start`
* The CLI prompts for incident context.
* The AI (via Ollama) processes inputs and suggests diagnostic steps.
* Maintains context across the full session.
* Guides log checks, SSH access, service status, etc.
* Suggests real commands and interprets output depending on your system. 


## 🧠 Key Features

* 💬 Conversational interface.
* 🧠 Session memory across turns.
* 🧩 Plugin support for local or remote AI models.  
* 🔌 Extensible architecture for adding new “resolvers” (logs, SSH, etc.)
* 🔮 More AI models (Claude, OpenAI, etc.) will be supported in future releases via the pluggable LLM engine.


## 🧠 Usage

```bash
$ incident-helper start

👋 Hi! Describe your incident.
> Getting 5xx on AWS ELB

🤖 What OS are you using?
> Amazon Linux 2

🤖 Can you access the logs? Where are they?
> /var/log/nginx/error.log

🤖 Great. Try: less /var/log/nginx/error.log
```

Type `exit` anytime to end the session.


## 📝 License

MIT
