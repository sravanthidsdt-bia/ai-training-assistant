$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Streamlit = Join-Path $ProjectRoot "venv\Scripts\streamlit.exe"

if (-not (Test-Path $Streamlit)) {
    Write-Error "Virtual environment not found. Run: python -m venv venv; venv\Scripts\pip install -r requirements.txt"
    exit 1
}

Get-ChildItem -Path (Join-Path $ProjectRoot "src") -Recurse -Filter __pycache__ -ErrorAction SilentlyContinue |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

& $Streamlit run (Join-Path $ProjectRoot "app.py")
