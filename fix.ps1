# MagicDNS Assistant for Windows (PowerShell)
$Host.UI.RawUI.WindowTitle = 'MagicDNS Assistant for Windows'

# Check Admin
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host '======================================================================' -ForegroundColor Yellow
    Write-Host '               ТРЕБУЮТСЯ ПРАВА АДМИНИСТРАТОРА' -ForegroundColor Yellow
    Write-Host '======================================================================' -ForegroundColor Yellow
    Write-Host 'Перезапускаем скрипт с правами Администратора...' -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -Command `"irm https://magicdns.ru/fix.ps1 | iex`"" -Verb RunAs
    exit
}

function Show-Menu {
    Clear-Host
    Write-Host '======================================================================' -ForegroundColor Cyan
    Write-Host '               MagicDNS Assistant - Быстрая настройка сети' -ForegroundColor Cyan
    Write-Host '                        Официальный сайт: magicdns.ru' -ForegroundColor DarkGray
    Write-Host '======================================================================' -ForegroundColor Cyan
    Write-Host ''
    Write-Host ' [1] Настроить MagicDNS (доступ к ChatGPT, Claude, Gemini)' -ForegroundColor White
    Write-Host ' [2] Очистить файл hosts и выключить чужие прокси' -ForegroundColor White
    Write-Host ' [3] Полный сброс сети и кэша DNS (flushdns, winsock reset)' -ForegroundColor White
    Write-Host ' [4] Проверить пинг до серверов MagicDNS' -ForegroundColor White
    Write-Host ' [5] Сброс на стандартный DNS (DHCP от роутера)' -ForegroundColor White
    Write-Host ' [0] Выход' -ForegroundColor DarkGray
    Write-Host ''
    Write-Host '======================================================================' -ForegroundColor Cyan
}

while ($true) {
    Show-Menu
    $choice = Read-Host 'Выберите пункт (1-5, 0 - выход)'
    switch ($choice) {
        '1' {
            Write-Host 'Настройка MagicDNS на активном подключении...' -ForegroundColor Cyan
            Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | ForEach-Object {
                Set-DnsClientServerAddress -InterfaceIndex $_.ifIndex -ServerAddresses '109.120.177.170','45.88.163.92'
            }
            Clear-DnsClientCache
            Write-Host 'Успешно! MagicDNS установлен. Нейросети доступны напрямую.' -ForegroundColor Green
            pause
        }
        '2' {
            Write-Host 'Очистка файла hosts...' -ForegroundColor Cyan
            $hosts = "$env:SystemRoot\System32\drivers\etc\hosts"
            if (Test-Path $hosts) {
                Copy-Item $hosts "$hosts.bak" -Force -ErrorAction SilentlyContinue
                Write-Host 'Бэкап сохранен в hosts.bak' -ForegroundColor DarkGray
            }
            Set-Content -Path $hosts -Value "# Cleaned by MagicDNS Assistant`n127.0.0.1 localhost`n::1 localhost" -Encoding Ascii
            Set-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' -Name ProxyEnable -Value 0 -ErrorAction SilentlyContinue
            Clear-DnsClientCache
            Write-Host 'Успешно! Файл hosts чист, системный прокси отключен.' -ForegroundColor Green
            pause
        }
        '3' {
            Write-Host 'Выполняется сброс сетевого стека...' -ForegroundColor Cyan
            ipconfig /flushdns
            netsh winsock reset
            netsh int ip reset
            Write-Host 'Сброс выполнен! Рекомендуется перезагрузить ПК.' -ForegroundColor Yellow
            pause
        }
        '4' {
            Write-Host 'Проверка пинга до серверов MagicDNS...' -ForegroundColor Cyan
            Test-Connection 109.120.177.170 -Count 2
            Test-Connection 45.88.163.92 -Count 2
            pause
        }
        '5' {
            Write-Host 'Возврат к стандартным настройкам (DHCP)...' -ForegroundColor Cyan
            Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | ForEach-Object {
                Set-DnsClientServerAddress -InterfaceIndex $_.ifIndex -ResetServerAddresses
            }
            Clear-DnsClientCache
            Write-Host 'Успешно! Настройки возвращены на автоматические (DHCP).' -ForegroundColor Green
            pause
        }
        '0' {
            exit
        }
    }
}
