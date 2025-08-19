# py-cli-agent

[![PyPI version](https://img.shields.io/pypi/v/py-cli-agent.svg)](https://pypi.org/project/py-cli-agent/)

A simple Python CLI agent powered by **Google’s Gemini API**.  
Interact with Gemini models directly from your terminal.

---

## ⚠️ Requirements

- Python **3.9+**
- A valid **`GEMINI_API_KEY`**

Set your `GEMINI_API_KEY` before use:

**Linux / macOS:**

```bash
export GEMINI_API_KEY="your_api_key_here"
```

**Windows (PowerShell):**

```powershell
$env:GEMINI_API_KEY="your_api_key_here"
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
py-cli-agent
✅ Using API key from environment variable
Using API key: AIz*****
>> hi
Step: OUTPUT
✅ Output: Hello! How can I help you?
>>
```

If no API key is found in your environment, the tool will prompt for it
and save it in your home directory: `~/.cli_agent_config.json`.

---

## 🔥 Example

```bash
py-cli-agent
```

---

## 📄 License

MIT License. See [LICENSE](./LICENSE) for details.
