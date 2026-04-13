# 🧠 TerminalBrain — AI-Powered Watchdog

A terminal wrapper that monitors command execution and uses a local LLM to suggest instant fixes for errors.

## 🚀 The Concept: Hardware Watchdog
In hardware, a **Watchdog Timer** monitors system state and triggers a recovery handler if a fault occurs. 
This project is the software equivalent:
- **The Wrapper:** Acts as the watchdog, monitoring `stderr`.
- **The Interrupt:** Fired when a regex pattern matches a known error.
- **The Recovery Handler:** A local LLM (Ollama) that analyzes the error and suggests a fix without stopping the process.

## 🛠 Tech Stack
- **Language:** Python 3.11+
- **Concurrency:** `threading` (independent stdout/stderr capture)
- **AI Engine:** Ollama (Model: `qwen2.5:0.5b` optimized for speed)
- **IPC:** `subprocess` with Windows-specific `shell=True` and `utf-8` encoding.

## ✨ Key Features & Improvements
- ✅ **Advanced Error Detection:** Expanded regex patterns to catch Python Tracebacks, Shell errors, and common Windows faults.
- ✅ **Pattern Caching:** Implemented an `ERROR_CACHE` to prevent redundant LLM calls for repeated errors.
- ✅ **Optimized for Windows:** Handled `subprocess` deadlocks and character encoding issues specific to PowerShell/CMD.
- ✅ **Tuned Prompting:** Engineered a system prompt that forces the LLM to provide concise, one-sentence fixes.
- ✅ **Fast API Integration:** Switched from CLI-based Ollama calls to direct local API requests for 5x faster response times.

## 📦 Usage
1. Ensure Ollama is running: `ollama serve`
2. Pull the lightweight model: `ollama pull qwen2.5:0.5b`
3. Run any command through the brain:
   ```bash
   python main.py python -c "print(x)"
