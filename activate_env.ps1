# PowerShell script to activate the virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
& ".\virtualenv\Scripts\Activate.ps1"
Write-Host ""
Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host "To run the project: cd src && python main.py" -ForegroundColor Yellow
Write-Host "To deactivate: deactivate" -ForegroundColor Yellow
