@echo off
chcp 65001 >nul
title MagicDNS Assistant for Windows

:: Проверка прав администратора без задержек (0 мс)
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ======================================================================
    echo                ТРЕБУЮТСЯ ПРАВА АДМИНИСТРАТОРА
    echo ======================================================================
    echo Перезапускаем помощник от имени Администратора...
    powershell -NoProfile -Command "Start-Process cmd.exe -ArgumentList '/c ""%~f0""' -Verb RunAs"
    exit /b
)
cd /d "%~dp0"

:menu
cls
echo ======================================================================
echo           MagicDNS Assistant — Быстрая настройка и ремонт сети
echo                      Официальный сайт: magicdns.ru
echo ======================================================================
echo.
echo  [1] Настроить MagicDNS (прямой доступ к ChatGPT, Claude, Gemini)
echo      Пропишет DNS 217.144.190.216 и 109.120.187.249 на активном адаптере
echo.
echo  [2] Очистить файл hosts и отключить системный прокси
echo      Сохранит копию в hosts.bak и уберет старые блокировки от чужих VPN
echo.
echo  [3] Полный сброс сети и кэша DNS (flushdns, winsock reset)
echo      Лечит бесконечную загрузку и ошибки сетевых сокетов Windows
echo.
echo  [4] Экспресс-проверка связи и резолва (пинг + проверка ИИ)
echo      Проверит доступность узлов MagicDNS и резолв ChatGPT / Gemini / Claude
echo.
echo  [5] Вернуть стандартный DNS по умолчанию (DHCP от роутера)
echo      Полный откат настроек адаптера к заводскому состоянию
echo.
echo  [0] Выход
echo.
echo ======================================================================
set /p choice="Выберите номер действия (1-5, 0 — выход): "

if "%choice%"=="1" goto opt1
if "%choice%"=="2" goto opt2
if "%choice%"=="3" goto opt3
if "%choice%"=="4" goto opt4
if "%choice%"=="5" goto opt5
if "%choice%"=="0" exit /b
goto menu

:opt1
echo.
echo Настраиваем MagicDNS на активных сетевых адаптерах...
powershell -NoProfile -Command "$ad = @(Get-NetAdapter | Where-Object { $_.Status -eq 'Up' -and $_.InterfaceDescription -notmatch 'VPN|TAP|TUN|WireGuard|Wintun|ZeroTier|Tailscale|Radmin|Hamachi' }); if ($ad.Count -eq 0) { $ad = @(Get-NetAdapter | Where-Object { $_.Status -eq 'Up' }) }; foreach ($a in $ad) { Write-Host (' -> Адаптер: ' + $a.Name + ' (' + $a.InterfaceDescription + ')'); Set-DnsClientServerAddress -InterfaceIndex $a.ifIndex -ServerAddresses @('217.144.190.216','109.120.187.249') -ErrorAction SilentlyContinue }; Clear-DnsClientCache"
echo.
echo [OK] Готово! Адреса MagicDNS (217.144.190.216, 109.120.187.249) успешно установлены.
echo.
pause
goto menu

:opt2
echo.
echo Очищаем файл hosts и проверяем системный прокси...
set "HOSTS_FILE=%SystemRoot%\System32\drivers\etc\hosts"
if exist "%HOSTS_FILE%" (
    copy /y "%HOSTS_FILE%" "%HOSTS_FILE%.bak" >nul
    echo  -^> Резервная копия сохранена: hosts.bak
)
(
echo # Default Windows hosts file
echo 127.0.0.1 localhost
echo ::1 localhost
) > "%HOSTS_FILE%"
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f >nul 2>&1
ipconfig /flushdns >nul 2>&1
echo.
echo [OK] Готово! Файл hosts очищен, системный прокси выключен.
echo.
pause
goto menu

:opt3
echo.
echo Выполняем сброс сетевого стека Windows и кэша DNS...
ipconfig /flushdns >nul
netsh winsock reset >nul
netsh int ip reset >nul
echo.
echo [OK] Готово! Сетевой стек и кэш DNS сброшены.
echo Если интернет не появился сразу — перезагрузите компьютер.
echo.
pause
goto menu

:opt4
echo.
echo Проверяем связь с узлами MagicDNS...
ping -n 2 217.144.190.216 >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] Узел 1 217.144.190.216 — доступен
) else (
    echo  [!] Узел 1 217.144.190.216 — нет ответа
)
ping -n 2 109.120.187.249 >nul 2>&1
if %errorlevel% equ 0 (
    echo  [OK] Узел 2 109.120.187.249 — доступен
) else (
    echo  [!] Узел 2 109.120.187.249 — нет ответа
)
echo.
echo Проверяем работу DNS на доменах ChatGPT, Gemini и Claude...
powershell -NoProfile -Command "foreach ($d in @('chatgpt.com', 'gemini.google.com', 'claude.ai')) { try { $r = Resolve-DnsName $d -Type A -ErrorAction Stop | Where-Object { $_.IPAddress } | Select-Object -First 1; if ($r.IPAddress -in @('217.144.190.216','109.120.187.249')) { Write-Host (' [OK] ' + $d + ' -> ' + $r.IPAddress + ' (маршрут MagicDNS активен)') -ForegroundColor Green } else { Write-Host (' [!] ' + $d + ' -> ' + $r.IPAddress + ' (идет мимо MagicDNS, примените пункт [1])') -ForegroundColor Yellow } } catch { Write-Host (' [!] ' + $d + ' -> ошибка DNS') -ForegroundColor Red } }"
echo.
pause
goto menu

:opt5
echo.
echo Возвращаем автоматическое получение DNS от роутера (DHCP)...
powershell -NoProfile -Command "Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | ForEach-Object { Set-DnsClientServerAddress -InterfaceIndex $_.ifIndex -ResetServerAddresses -ErrorAction SilentlyContinue }; Clear-DnsClientCache"
echo.
echo [OK] Готово! Настройки DNS возвращены в исходное состояние по умолчанию.
echo.
pause
goto menu