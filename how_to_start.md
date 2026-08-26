# Start CodeRoast Locally

Use this guide in **PowerShell** after restarting Windows. It starts Ollama, verifies the local Qwen model, and launches the Streamlit app.

## 1. Open the Project

```powershell
Set-Location D:\CodeRoast
```

## 2. Activate the Python Environment

CodeRoast uses the `venv_gpu` environment:

```powershell
& .\venv_gpu\Scripts\Activate.ps1
```

If PowerShell blocks the activation script, allow it for the current terminal session and try again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& .\venv_gpu\Scripts\Activate.ps1
```

## 3. Configure Ollama's Model Directory

The Qwen model is stored on the D: drive inside this project:

```powershell
$env:OLLAMA_MODELS = "D:\CodeRoast\ollama_models"
```

## 4. Start Ollama

Start Ollama only when it is not already running:

```powershell
if (-not (Get-Process -Name ollama -ErrorAction SilentlyContinue)) {
    Start-Process -FilePath "D:\Ollama\ollama.exe" `
        -ArgumentList "serve" -WindowStyle Hidden
}
```

> Do not run a second `ollama serve` if Ollama is already running. A port-in-use error means the existing Ollama process is already using port `11434`.

## 5. Verify Ollama

Check that the Ollama API is responding:

```powershell
Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get
```

List the installed models:

```powershell
& "D:\Ollama\ollama.exe" list
```

The output should include:

```text
qwen2.5-coder:1.5b
```

If the model is missing, download it once:

```powershell
& "D:\Ollama\ollama.exe" pull qwen2.5-coder:1.5b
```

The `OLLAMA_MODELS` environment variable from step 3 ensures the model is downloaded to the project directory.

## 6. Test Local Qwen Inference (Optional)

Run a quick request before starting the app:

```powershell
$body = @{
    model = "qwen2.5-coder:1.5b"
    prompt = "Reply with exactly: CodeRoast local Qwen is working."
    stream = $false
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:11434/api/generate" `
    -Method Post -ContentType "application/json" -Body $body
```

The response should contain:

```text
CodeRoast local Qwen is working.
```

## 7. Start the CodeRoast App

```powershell
& .\venv_gpu\Scripts\streamlit.exe run app.py
```

Open the app in your browser:

<http://localhost:8501>

In the app, enable **Dynamic AI Roast** to use the local Qwen model through Ollama. If it is disabled, CodeRoast uses its template-based roast generator instead.

## Stop the App

In the terminal running Streamlit, press `Ctrl+C`.

To stop Ollama as well:

```powershell
Stop-Process -Name ollama
```
