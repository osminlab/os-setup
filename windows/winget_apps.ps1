<#
Autor: Osmin Larreynaga
Fecha: 2021-10-15
Descripción: Instala aplicaciones con winget
#>


# Instalar winget
Write-Host "Instalando aplicaciones usando winget..."


# ------------------------------
# Utilidades/Productividad

# Insalar Git
Write-Host "Instalando Git..."
winget install -e --id Git.Git

# Instalar Github Desktop
Write-Host "Instalando Github Desktop..."
winget install -e --id GitHub.GitHubDesktop

# Instalar Gimp
Write-Host "Instalando Gimp..."
winget install -e --id GIMP.GIMP

# Instalar Google Chrome Dev
Write-Host "Instalando Google Chrome Dev..."
winget install -e --id Google.ChromeDev

# Instalar Windows Terminal
Write-Host "Instalando Windows Terminal..."
winget install -e --id Microsoft.WindowsTerminal

# Instalar 7zip
Write-Host "Instalando 7zip..."
winget install -e --id 7zip.7zip

# Instalar Arduino IDE
Write-Host "Instalando Arduino IDE..."
winget install -e --id Arduino.ArduinoIDE

# Instalar Visual Studio Code
Write-Host "Instalando Visual Studio Code..."
winget install -e --id Microsoft.VisualStudioCode

# Instalar Brave
Write-Host "Instalando Brave..."
winget install -e --id BraveSoftware.Brave-Browser

# Instalar PowerToys
Write-Host "Instalando PowerToys..."
winget install -e --id Microsoft.PowerToys

# Instalar Spotify
Write-Host "Instalando Spotify..."
winget install -e --id Spotify.Spotify
# ------------------------------

Write-Host "Instalación completa."
