# Script pour lancer l'API et l'interface Streamlit
$root = Resolve-Path "$PSScriptRoot\.."
Set-Location $root

# Lancer l'API FastAPI en arrière-plan
Start-Process -FilePath "$root\.venv\Scripts\python.exe" -ArgumentList "-m uvicorn api.main:app --host 127.0.0.1 --port 8000" -WindowStyle Hidden

# Attendre 2 secondes pour que l'API soit prête
Start-Sleep -Seconds 2

# Lancer Streamlit (ouvrira automatiquement le navigateur sur http://localhost:8501)
Start-Process -FilePath "$root\.venv\Scripts\python.exe" -ArgumentList "-m streamlit run ui/app.py"

