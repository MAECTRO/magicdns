@echo off
chcp 65001 >nul
title MagicDNS Assistant for Windows

powershell -NoProfile -ExecutionPolicy Bypass -Command "$b = (New-Object System.Net.WebClient).DownloadData('https://magicdns.ru/fix.ps1'); iex [System.Text.Encoding]::UTF8.GetString($b)"
if %errorlevel% neq 0 (
    echo.
    echo ======================================================================
    echo  Если скрипт закрылся, запустите его от имени Администратора:
    echo  Правая кнопка мыши по файлу -^> 'Запуск от имени администратора'.
    echo ======================================================================
    pause
)
