# CodeRoast: start the local app with Ollama and Qwen
# Run these commands in PowerShell after restarting Windows.

# 1. Go to the project folder
Set-Location D:\CodeRoast

# 2. Activate the project environment used by this app
& .\venv_gpu\Scripts\Activate.ps1

# If PowerShell blocks activation, run this once in the same terminal and
# then activate again:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned

# 3. Point Ollama at the model files stored in this project
$env:OLLAMA_MODELS = "D:\CodeRoast\ollama_models"

# 4. Start Ollama only if it is not already running
# Do not run a second `ollama serve` if the API is already listening.
if (-not (Get-Process -Name ollama -ErrorAction SilentlyContinue)) {
	Start-Process -FilePath "D:\Ollama\ollama.exe" `
		-ArgumentList "serve" -WindowStyle Hidden
}

# 5. Confirm that Ollama is responding
# If this fails immediately after starting Ollama, wait a few seconds and run
# the command again.
Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -Method Get

# 6. Confirm that the required local Qwen model is installed
& "D:\Ollama\ollama.exe" list

# The list must contain:
# qwen2.5-coder:1.5b

# If the model is missing, download it once. This uses the D-drive model store
# configured above and is not normally needed after the first setup.
# & "D:\Ollama\ollama.exe" pull qwen2.5-coder:1.5b

# 7. Optional: test local Qwen inference before opening the app
$body = @{
	model = "qwen2.5-coder:1.5b"
	prompt = "Reply with exactly: CodeRoast local Qwen is working."
	stream = $false
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:11434/api/generate" `
	-Method Post -ContentType "application/json" -Body $body

# 8. Start the Streamlit app
& .\venv_gpu\Scripts\streamlit.exe run app.py

# Open this address in your browser:
# http://localhost:8501

# In the app, enable "Dynamic AI Roast" to use local Qwen through Ollama.
# Without that option, CodeRoast uses its template roast generator.

# To stop the app, press Ctrl+C in the Streamlit terminal.
# To stop Ollama too, run this separately when you are finished:
# Stop-Process -Name ollama
