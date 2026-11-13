@echo off
chcp 65001 >nul
title تثبيت برنامج برومات - Promat Setup
cls
echo ========================================================
echo        مرحباً بك في برنامج تثبيت برومات (Promat Setup)
echo   المكتبة الذكية للبرومبتات وهندسة الذكاء الاصطناعي
echo ========================================================
echo.

set "INSTALL_DIR=%LOCALAPPDATA%\Promat"
set "SOURCE_DIR=%~dp0dist\Promat"

if not exist "%SOURCE_DIR%\Promat.exe" (
    set "SOURCE_DIR=%~dp0Promat"
)

if not exist "%SOURCE_DIR%\Promat.exe" (
    echo [خطأ] لم يتم العثور على ملفات البرنامج المصدرية!
    pause
    exit /b 1
)

echo [1/3] جاري نسخ وتثبيت ملفات البرنامج في: %INSTALL_DIR%
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
xcopy "%SOURCE_DIR%\*" "%INSTALL_DIR%\" /E /I /Y /Q >nul

echo [2/3] إنشاء اختصار البرنامج على سطح المكتب...
powershell -NoProfile -Command ^
  "$ws = New-Object -ComObject WScript.Shell; " ^
  "$s = $ws.CreateShortcut([Environment]::GetFolderPath('Desktop') + '\برومات Promat.lnk'); " ^
  "$s.TargetPath = '%INSTALL_DIR%\Promat.exe'; " ^
  "$s.WorkingDirectory = '%INSTALL_DIR%'; " ^
  "$s.IconLocation = '%INSTALL_DIR%\app_icon.ico, 0'; " ^
  "$s.Description = 'برومات - المكتبة الذكية للبرومبتات'; " ^
  "$s.Save()"

echo [3/3] إنشاء اختصار البرنامج في قائمة ابدأ (Start Menu)...
powershell -NoProfile -Command ^
  "$ws = New-Object -ComObject WScript.Shell; " ^
  "$programs = [Environment]::GetFolderPath('Programs'); " ^
  "$s = $ws.CreateShortcut($programs + '\برومات Promat.lnk'); " ^
  "$s.TargetPath = '%INSTALL_DIR%\Promat.exe'; " ^
  "$s.WorkingDirectory = '%INSTALL_DIR%'; " ^
  "$s.IconLocation = '%INSTALL_DIR%\app_icon.ico, 0'; " ^
  "$s.Description = 'برومات - المكتبة الذكية للبرومبتات'; " ^
  "$s.Save()"

echo.
echo ========================================================
echo   ✓ تم تثبيت برنامج برومات بنجاح على هذا الحاسوب!
echo   ✓ تم إنشاء أيقونة واختصار على سطح المكتب وفي قائمة ابدأ.
echo ========================================================
echo.
set /p launch="هل تريد تشغيل البرنامج الآن؟ (Y/N): "
if /i "%launch%"=="Y" (
    start "" "%INSTALL_DIR%\Promat.exe"
)
exit /b 0
