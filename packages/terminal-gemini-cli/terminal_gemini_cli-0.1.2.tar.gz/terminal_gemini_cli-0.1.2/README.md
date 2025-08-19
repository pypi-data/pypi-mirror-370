# Terminal Gemini CLI

[![PyPI version](https://badge.fury.io/py/terminal-gemini-cli.svg)](https://pypi.org/project/terminal-gemini-cli/)  
A lightweight command-line tool to interact with **Google Gemini AI** directly from your terminal.

---

## 🚀 Features
- Chat with **Google Gemini AI** from your terminal  
- Minimal and fast  
- Works on Linux, macOS, and Windows  
- Easy installation via `pip`  

---

## 📦 Installation
```bash
pip install terminal-gemini-cli
````

---

## ⚡ Usage

Run the CLI after installation:

```bash
terminal-gemini "Hello Gemini!"
```

You can also start an interactive session:

```bash
terminal-gemini
```

Example:

```bash
> terminal-gemini "Summarize the book Atomic Habits"
```

---

## ⚙️ Configuration

The CLI needs your **Gemini API key**.
Set it as an environment variable:

```bash
export GEMINI_API_KEY="your_api_key_here"   # Linux/macOS
setx GEMINI_API_KEY "your_api_key_here"     # Windows (PowerShell)
```

---

## 📌 Development

Clone the repo and install in editable mode:

```bash
git clone https://github.com/yourusername/terminal-gemini.git
cd terminal-gemini
pip install -e .
```

Build and upload:

```bash
rm -rf dist/ build/ *.egg-info
python -m build
twine upload dist/*
```

---

## 🛠 Requirements

* Python 3.8+
* [google-generativeai](https://pypi.org/project/google-generativeai/)

---

## 📄 License

MIT License.
Feel free to fork and improve!

---

## 💡 Example

```bash
$ terminal-gemini "Write a haiku about the ocean"
🌊
Calm waves kiss the shore,  
Endless blue whispers softly,  
Sky and sea as one.
```

```
