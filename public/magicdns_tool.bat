@echo off
set "MAGIC_BAT=%~f0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "$c=[IO.File]::ReadAllLines($env:MAGIC_BAT,[Text.Encoding]::UTF8)|Select-Object -Skip 5;Invoke-Expression ($c -join [char]10)"
exit /b
:: ============================================================================
# MagicDNS Assistant for Windows (Открытый скрипт настройки и диагностики сети)
# Вы можете открыть этот файл в Блокноте и проверить каждую команду.
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$Host.UI.RawUI.WindowTitle = 'MagicDNS Assistant for Windows'

$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin -and -not $env:MAGIC_TEST_NO_UAC) {
    Write-Host '======================================================================' -ForegroundColor Yellow
    Write-Host '               ТРЕБУЮТСЯ ПРАВА АДМИНИСТРАТОРА' -ForegroundColor Yellow
    Write-Host '======================================================================' -ForegroundColor Yellow
    Write-Host 'Перезапускаем помощник от имени Администратора...' -ForegroundColor Cyan
    if ($env:MAGIC_BAT -and (Test-Path -LiteralPath $env:MAGIC_BAT)) {
        $b64Path = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($env:MAGIC_BAT))
        $elevCmd = "`$p=[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String('$b64Path'));`$env:MAGIC_BAT=`$p;`$c=[IO.File]::ReadAllLines(`$p,[Text.Encoding]::UTF8)|Select-Object -Skip 5;Invoke-Expression (`$c -join [char]10)"
        Start-Process -FilePath 'powershell.exe' -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', $elevCmd) -Verb RunAs
    } else {
        $elevWeb = "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12;`$b=(New-Object System.Net.WebClient).DownloadData('https://magicdns.ru/fix.ps1');Invoke-Expression ([System.Text.Encoding]::UTF8.GetString(`$b))"
        Start-Process -FilePath 'powershell.exe' -ArgumentList @('-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', $elevWeb) -Verb RunAs
    }
    exit
}

function Show-Menu {
    if (-not $env:MAGIC_TEST_NO_UAC) { Clear-Host }
    Write-Host '======================================================================' -ForegroundColor Cyan
    Write-Host '          MagicDNS Assistant — Быстрая настройка и ремонт сети' -ForegroundColor Cyan
    Write-Host '                     Официальный сайт: magicdns.ru' -ForegroundColor DarkGray
    Write-Host '======================================================================' -ForegroundColor Cyan
    Write-Host ''
    Write-Host ' [1] Настроить MagicDNS (прямой доступ к ChatGPT, Claude, Gemini)' -ForegroundColor White
    Write-Host '     Пропишет DNS 217.144.190.216 и 109.120.187.249, очистит hosts и сбросит кэш' -ForegroundColor DarkGray
    Write-Host ''
    Write-Host ' [2] Очистить файл hosts и отключить системный прокси' -ForegroundColor White
    Write-Host '     Сохранит копию в hosts.bak и уберет старые блокировки от чужих VPN' -ForegroundColor DarkGray
    Write-Host ''
    Write-Host ' [3] Полный сброс сети и кэша DNS (flushdns, winsock reset)' -ForegroundColor White
    Write-Host '     Лечит бесконечную загрузку и ошибки сетевых сокетов Windows' -ForegroundColor DarkGray
    Write-Host ''
    Write-Host ' [4] Экспресс-проверка связи и резолва (пинг + проверка ИИ)' -ForegroundColor White
    Write-Host '     Проверит доступность узлов MagicDNS и резолв ChatGPT / Gemini / Claude' -ForegroundColor DarkGray
    Write-Host ''
    Write-Host ' [5] Вернуть стандартный DNS по умолчанию (DHCP от роутера)' -ForegroundColor White
    Write-Host '     Полный откат настроек адаптера к заводскому состоянию' -ForegroundColor DarkGray
    Write-Host ''
    Write-Host ' [0] Выход' -ForegroundColor DarkGray
    Write-Host ''
    Write-Host '======================================================================' -ForegroundColor Cyan
}

while ($true) {
    Show-Menu
    $choice = Read-Host 'Выберите номер действия (1-5, 0 — выход)'
    switch ($choice.Trim()) {
        '1' {
            Write-Host ''
            Write-Host 'Настраиваем MagicDNS на активных сетевых адаптерах...' -ForegroundColor Cyan
            $adapters = @(Get-NetAdapter | Where-Object { $_.Status -eq 'Up' -and $_.InterfaceDescription -notmatch 'VPN|TAP|TUN|WireGuard|Wintun|ZeroTier|Tailscale|Radmin|Hamachi' })
            if ($adapters.Count -eq 0) {
                $adapters = @(Get-NetAdapter | Where-Object { $_.Status -eq 'Up' })
            }
            foreach ($a in $adapters) {
                Write-Host " -> Адаптер: $($a.Name) ($($a.InterfaceDescription))" -ForegroundColor Gray
                Set-DnsClientServerAddress -InterfaceIndex $a.ifIndex -ServerAddresses @('217.144.190.216','109.120.187.249') -ErrorAction SilentlyContinue
            }
            Write-Host ''
            Write-Host 'Очищаем файл hosts от старых блокировок чужих VPN...' -ForegroundColor Cyan
            $hosts = "$env:SystemRoot\System32\drivers\etc\hosts"
            if (Test-Path $hosts) {
                Copy-Item $hosts "$hosts.bak" -Force -ErrorAction SilentlyContinue
                Write-Host " -> Резервная копия сохранена: $hosts.bak" -ForegroundColor Gray
            }
            Set-Content -Path $hosts -Value "# Default Windows hosts file (cleaned by MagicDNS Assistant)`r`n127.0.0.1 localhost`r`n::1 localhost" -Encoding Ascii -Force
            Set-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' -Name ProxyEnable -Value 0 -ErrorAction SilentlyContinue
            Clear-DnsClientCache -ErrorAction SilentlyContinue
            Write-Host ''
            Write-Host 'Готово! Адреса MagicDNS (217.144.190.216, 109.120.187.249) установлены, файл hosts очищен.' -ForegroundColor Green
            Write-Host 'Нажмите Enter для возврата в меню...' -ForegroundColor DarkGray
            [void](Read-Host)
        }
        '2' {
            Write-Host ''
            Write-Host 'Очищаем файл hosts и проверяем системный прокси...' -ForegroundColor Cyan
            $hosts = "$env:SystemRoot\System32\drivers\etc\hosts"
            if (Test-Path $hosts) {
                Copy-Item $hosts "$hosts.bak" -Force -ErrorAction SilentlyContinue
                Write-Host " -> Резервная копия сохранена: $hosts.bak" -ForegroundColor Gray
            }
            Set-Content -Path $hosts -Value "# Default Windows hosts file (cleaned by MagicDNS Assistant)`r`n127.0.0.1 localhost`r`n::1 localhost" -Encoding Ascii -Force
            Set-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' -Name ProxyEnable -Value 0 -ErrorAction SilentlyContinue
            Clear-DnsClientCache -ErrorAction SilentlyContinue
            Write-Host 'Готово! Файл hosts очищен, старый системный прокси выключен.' -ForegroundColor Green
            Write-Host 'Нажмите Enter для возврата в меню...' -ForegroundColor DarkGray
            [void](Read-Host)
        }
        '3' {
            Write-Host ''
            Write-Host 'Выполняем сброс сетевого стека Windows и кэша DNS...' -ForegroundColor Cyan
            ipconfig /flushdns | Out-Null
            netsh winsock reset | Out-Null
            netsh int ip reset | Out-Null
            Write-Host 'Готово! Сетевой стек и кэш DNS сброшены. Если интернет не появился сразу — перезагрузите ПК.' -ForegroundColor Green
            Write-Host 'Нажмите Enter для возврата в меню...' -ForegroundColor DarkGray
            [void](Read-Host)
        }
        '4' {
            Write-Host ''
            Write-Host 'Проверяем связь с серверами MagicDNS...' -ForegroundColor Cyan
            foreach ($srv in @(@{Name='Узел 1 (Германия)';IP='217.144.190.216'}, @{Name='Узел 2 (Финляндия)';IP='109.120.187.249'})) {
                $ping = Test-Connection -ComputerName $srv.IP -Count 2 -ErrorAction SilentlyContinue
                if ($ping) {
                    $avg = [math]::Round(($ping | Measure-Object -Property ResponseTime -Average).Average, 1)
                    Write-Host " [OK] $($srv.Name) ($($srv.IP)) — пинг $avg мс" -ForegroundColor Green
                } else {
                    Write-Host " [!] $($srv.Name) ($($srv.IP)) — нет ответа на пинг" -ForegroundColor Red
                }
            }
            Write-Host ''
            Write-Host 'Проверяем работу DNS на доменах ChatGPT, Gemini и Claude...' -ForegroundColor Cyan
            foreach ($dom in @('chatgpt.com', 'gemini.google.com', 'claude.ai')) {
                try {
                    $res = Resolve-DnsName $dom -Type A -ErrorAction Stop | Where-Object { $_.IPAddress } | Select-Object -First 1
                    if ($res.IPAddress -in @('217.144.190.216','109.120.187.249')) {
                        Write-Host " [OK] $dom -> $($res.IPAddress) (маршрут MagicDNS активен)" -ForegroundColor Green
                    } else {
                        Write-Host " [!] $dom -> $($res.IPAddress) (идет мимо MagicDNS, выберите пункт [1] или выключите VPN)" -ForegroundColor Yellow
                    }
                } catch {
                    Write-Host " [!] $dom -> ошибка разрешения имени" -ForegroundColor Red
                }
            }
            Write-Host ''
            Write-Host 'Нажмите Enter для возврата в меню...' -ForegroundColor DarkGray
            [void](Read-Host)
        }
        '5' {
            Write-Host ''
            Write-Host 'Возвращаем автоматическое получение DNS от роутера (DHCP)...' -ForegroundColor Cyan
            Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | ForEach-Object {
                Set-DnsClientServerAddress -InterfaceIndex $_.ifIndex -ResetServerAddresses -ErrorAction SilentlyContinue
            }
            Clear-DnsClientCache -ErrorAction SilentlyContinue
            Write-Host 'Готово! Настройки DNS возвращены в исходное состояние по умолчанию.' -ForegroundColor Green
            Write-Host 'Нажмите Enter для возврата в меню...' -ForegroundColor DarkGray
            [void](Read-Host)
        }
        '0' {
            exit
        }
    }
}
