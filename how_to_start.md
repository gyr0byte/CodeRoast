# 🚀 How to Start CodeRoast

Follow these simple steps in **PowerShell** to start CodeRoast and all required services (Ollama local AI + Streamlit UI).

---

## ⚡ Quick Start (One-Liner in PowerShell)

Open PowerShell and paste this command to start everything in 1 step:

```powershell
Set-Location D:\CodeRoast; Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned; $env:OLLAMA_MODELS = "D:\CodeRoast\ollama_models"; if (-not (Get-Process -Name ollama -ErrorAction SilentlyContinue)) { Start-Process -FilePath "D:\Ollama\ollama.exe" -ArgumentList "serve" -WindowStyle Hidden }; & .\venv_gpu\Scripts\streamlit.exe run app.py
```

---

## 📖 Step-by-Step Instructions

### Step 1: Open the Project Directory

```powershell
Set-Location D:\CodeRoast
```

### Step 2: Activate the Virtual Environment

CodeRoast uses the GPU-enabled Python environment `venv_gpu`:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& .\venv_gpu\Scripts\Activate.ps1
```

### Step 3: Set Ollama Model Path & Start Ollama

Configure the local model storage path (D: drive) and start the Ollama server in the background:

```powershell
$env:OLLAMA_MODELS = "D:\CodeRoast\ollama_models"

if (-not (Get-Process -Name ollama -ErrorAction SilentlyContinue)) {
    Start-Process -FilePath "D:\Ollama\ollama.exe" -ArgumentList "serve" -WindowStyle Hidden
}
```

### Step 4: Verify Ollama & Qwen Model (Optional)

Check if Ollama is running and has the `qwen2.5-coder:1.5b` model ready:

```powershell
& "D:\Ollama\ollama.exe" list
```

*(If missing, pull it once: `& "D:\Ollama\ollama.exe" pull qwen2.5-coder:1.5b`)*

### Step 5: Launch the CodeRoast Web App

Run Streamlit to open the CodeRoast user interface:

```powershell
& .\venv_gpu\Scripts\streamlit.exe run app.py
```

Once started, open your web browser at:
👉 **[http://localhost:8501](http://localhost:8501)**

---

## 🧠 AI Model Routing Overview

| Roast Mode | AI Model Used | Source / Backend |
|---|---|---|
| 🇳🇵 **Romanized Nepali** | **Gemini Multi-Model Fallback** (`2.5-flash` → `flash-lite-latest` → `3.5-flash-lite` → `3.1-flash-lite`) | Google Gemini REST API (`GEMINI_API_KEY` in `.env`) |
| 🇬🇧 **English Roast** | **Qwen 2.5 Coder 1.5B** | Local GPU via Ollama (`http://localhost:11434`) |
| 🅰️ **Letter Grade & Reaction** | **Qwen 2.5 Coder 1.5B** | Local GPU via Ollama |

---

## 🛑 How to Stop Everything

### Stop Streamlit App
Press `Ctrl + C` in the PowerShell window running Streamlit.

### Stop Ollama & Python Processes (Complete Shutdown)
To completely stop Ollama server and any running background AI tasks:

```powershell
Stop-Process -Name ollama, python, streamlit -ErrorAction SilentlyContinue
```
