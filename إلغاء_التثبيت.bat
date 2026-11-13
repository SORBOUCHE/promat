@echo off
chcp 65001 >nul
title إلغاء تثبيت برنامج برومات - Promat Uninstall
cls
echo ========================================================
echo             إلغاء تثبيت برنامج برومات (Promat)
echo ========================================================
echo.
set /p confirm="هل أنت متأكد من رغبتك في إزالة برنامج برومات من جهازك؟ (Y/N): "
if /i not "%confirm%"=="Y" (
    echo تم إلغاء العملية.
    pause
    exit /b 0
)

set "INSTALL_DIR=%LOCALAPPDATA%\Promat"

echo جاري إغلاق أي نافذة مفتوحة للبرنامج...
taskkill /f /im Promat.exe >nul 2>&1

echo جاري حذف ملفات البرنامج...
if exist "%INSTALL_DIR%" (
    rmdir /s /q "%INSTALL_DIR%"
)

echo جاري حذف الاختصارات من سطح المكتب وقائمة ابدأ...
powershell -NoProfile -Command ^
  "Remove-Item -Path ([Environment]::GetFolderPath('Desktop') + '\برومات Promat.lnk') -ErrorAction SilentlyContinue; " ^
  "Remove-Item -Path ([Environment]::GetFolderPath('Programs') + '\برومات Promat.lnk') -ErrorAction SilentlyContinue;"

echo.
echo ========================================================
echo       ✓ تم إلغاء تثبيت برنامج برومات بنجاح.
echo ========================================================
pause
exit /b 0
