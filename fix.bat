@echo off
setlocal
chcp 65001 >nul
title MagicDNS Assistant for Windows

:: Auto-Elevation: if not admin, ask for elevation via UAC
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [i] Запрашиваем права Администратора...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Process cmd -ArgumentList '/c `"`"%~f0`"`"' -Verb RunAs"
    exit /b
)

:MENU
cls
echo ======================================================================
echo                MagicDNS Assistant - Быстрая настройка сети
echo                         Сайт: https://magicdns.ru
echo ======================================================================
echo.
echo  [1] Настроить MagicDNS (доступ к ChatGPT, Claude, Gemini)
echo  [2] Очистить файл hosts и отключить чужие прокси
echo  [3] Полный сброс сети и кэша DNS (flushdns, winsock reset)
echo  [4] Проверить доступность шлюзов MagicDNS
echo  [5] Сброс на стандартный DNS (DHCP от роутера)
echo  [0] Выход
echo.
echo ======================================================================
set "CHOICE="
set /p CHOICE="Выберите пункт (1-5, 0 - выход): "

if "%CHOICE%"=="1" goto DO_SETUP
if "%CHOICE%"=="2" goto DO_HOSTS
if "%CHOICE%"=="3" goto DO_RESET
if "%CHOICE%"=="4" goto DO_TEST
if "%CHOICE%"=="5" goto DO_DHCP
if "%CHOICE%"=="0" exit /b
goto MENU

:DO_SETUP
cls
echo [1/2] Настройка MagicDNS на активном подключении...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | ForEach-Object { Set-DnsClientServerAddress -InterfaceIndex $_.ifIndex -ServerAddresses '109.120.177.170','45.88.163.92' }; Clear-DnsClientCache; Write-Host 'Успешно! MagicDNS установлен.' -ForegroundColor Green"
echo.
echo [2/2] Сброс кэша DNS...
ipconfig /flushdns
echo.
echo ======================================================================
echo  Готово! MagicDNS активен. Доступ к нейросетям открыт.
echo ======================================================================
echo.
pause
goto MENU

:DO_HOSTS
cls
echo [1/2] Очистка файла hosts...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Copy-Item $env:SystemRoot\System32\drivers\etc\hosts $env:SystemRoot\System32\drivers\etc\hosts.bak -Force -ErrorAction SilentlyContinue; Set-Content -Path $env:SystemRoot\System32\drivers\etc\hosts -Value '# Cleaned by MagicDNS`n127.0.0.1 localhost`n::1 localhost' -Encoding Ascii; Set-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' -Name ProxyEnable -Value 0 -ErrorAction SilentlyContinue; Clear-DnsClientCache; Write-Host 'Успешно! Бэкап сохранен в hosts.bak, файл hosts чист, прокси выключен.' -ForegroundColor Green"
echo.
echo ======================================================================
echo  Готово! Файл hosts очищен от сторонних блокировок.
echo ======================================================================
echo.
pause
goto MENU

:DO_RESET
cls
echo Выполняется полный сброс сетевого стека Windows...
echo.
ipconfig /flushdns
netsh winsock reset
netsh int ip reset
echo.
echo ======================================================================
echo  Сброс завершен! Рекомендуется перезагрузить компьютер.
echo ======================================================================
echo.
pause
goto MENU

:DO_TEST
cls
echo Проверка пинга до шлюзов MagicDNS...
echo.
echo [1/2] Франкфурт (109.120.177.170):
ping -n 3 109.120.177.170
echo.
echo [2/2] Второй узел (45.88.163.92):
ping -n 3 45.88.163.92
echo.
pause
goto MENU

:DO_DHCP
cls
echo Возврат сетевых настроек на авто-получение (DHCP)...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-NetAdapter | Where-Object { $_.Status -eq 'Up' } | ForEach-Object { Set-DnsClientServerAddress -InterfaceIndex $_.ifIndex -ResetServerAddresses }; Clear-DnsClientCache; Write-Host 'Успешно! Настройки возвращены на автоматические (DHCP).' -ForegroundColor Green"
echo.
echo ======================================================================
echo  Готово! DNS сброшен на стандартный от роутера.
echo ======================================================================
echo.
pause
goto MENU
