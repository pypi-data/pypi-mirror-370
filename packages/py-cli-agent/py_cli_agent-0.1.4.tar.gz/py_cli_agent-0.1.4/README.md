# py-cli-agent

[![PyPI version](https://img.shields.io/pypi/v/py-cli-agent.svg)](https://pypi.org/project/py-cli-agent/)

A simple Python CLI agent powered by **Google’s Gemini API**.  
Interact with Gemini models directly from your terminal.

---

## ⚠️ Requirements

- Python
- A valid **`GEMINI_API_KEY`**

Either set your `GEMINI_API_KEY` by using:

**Linux / macOS:**

```bash
export GEMINI_API_KEY="your_api_key_here"
```

**Windows (PowerShell):**

```powershell
$env:GEMINI_API_KEY="your_api_key_here"
```

Or pass it on the command line:

```bash
$ python -m cli_agent.main
Enter your Gemini API key: <your_api_key_here>
✅ API key saved to C:\Users\andro\.cli_agent_config.json
Using API key: <your_api_key_here>****
>>

```

---

## 📦 Installation

```bash
pip install py-cli-agent
```

---

## 🚀 Usage

Run from the terminal:

```bash
andro-cli
```

If no API key is found in your environment, the tool will prompt for it
and save it in your home directory: `~/.cli_agent_config.json`.

---
## 🛠️ Features

- Interact with Gemini AI models directly from your terminal
- Easy API key management
- Rich output formatting

## 📄 License

MIT License. See [LICENSE](./LICENSE) for details.
