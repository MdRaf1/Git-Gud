@echo off
REM Git sensei GIF Demo Script
REM This script contains the perfect sequence for recording a demo GIF

cls
echo 🎬 Git sensei Demo - Safe, Simple, Smart Git Assistant
echo ==================================================
timeout /t 2 /nobreak >nul

REM Create demo environment
set DEMO_DIR=%TEMP%\git_sensei_demo_%RANDOM%
mkdir "%DEMO_DIR%"
cd /d "%DEMO_DIR%"
git init >nul 2>&1
git config user.name "Demo User" >nul 2>&1
git config user.email "demo@example.com" >nul 2>&1

cls

REM Part 1: Git sensei is SAFE 🛡️
echo # Part 1: Git sensei is SAFE 🛡️
echo # Dangerous operations require confirmation
echo.
echo $ git-sensei -e "git reset --hard HEAD~1"
timeout /t 1 /nobreak >nul

echo ⚠️  WARNING: This command will permanently delete uncommitted changes
echo Dangerous patterns detected: reset --hard
echo Type 'yes' to proceed with this dangerous operation: no
echo ❌ Operation cancelled by user
timeout /t 3 /nobreak >nul

cls

REM Part 2: Git sensei is SIMPLE 🗣️
echo # Part 2: Git sensei is SIMPLE 🗣️
echo # Natural language interface - just describe what you want
echo.
echo $ git-sensei "show me the current status"
timeout /t 1 /nobreak >nul
echo git status
echo On branch main
echo.
echo No commits yet
echo.
echo nothing to commit (create/copy files and use "git add" to track)
timeout /t 2 /nobreak >nul

echo.
echo $ git-sensei "list all branches"
timeout /t 1 /nobreak >nul
echo git branch -a
echo * main
timeout /t 2 /nobreak >nul

cls

REM Part 3: Git sensei is SMART 🧠
echo # Part 3: Git sensei is SMART 🧠
echo # Context-aware AI understands your repository state
echo.
echo $ echo "Hello Hackathon!" ^> demo.txt
echo Hello Hackathon! > demo.txt
timeout /t 1 /nobreak >nul

echo.
echo $ git-sensei "commit my new work"
timeout /t 1 /nobreak >nul
echo git add demo.txt
echo 💡 AI detected untracked files and suggested adding them first!
timeout /t 2 /nobreak >nul

echo.
echo $ git-sensei -e "git add demo.txt"
timeout /t 1 /nobreak >nul
echo ✅ Command executed successfully
timeout /t 1 /nobreak >nul

echo.
echo $ git-sensei -e "git commit -m \"Add demo file\""
timeout /t 1 /nobreak >nul
echo [main (root-commit) abc1234] Add demo file
echo  1 file changed, 1 insertion(+)
echo  create mode 100644 demo.txt
timeout /t 2 /nobreak >nul

echo.
echo $ git-sensei "show me the commit history"
timeout /t 1 /nobreak >nul
echo git log --oneline
echo abc1234 Add demo file
timeout /t 2 /nobreak >nul

cls

REM Finale
echo 🎉 Git sensei Demo Complete!
echo =========================
echo.
echo ✅ SAFE: Prevents dangerous operations with smart warnings
echo ✅ SIMPLE: Natural language interface for intuitive Git usage
echo ✅ SMART: Context-aware AI that understands your repository
echo.
echo Ready to make Git safer and more accessible for everyone!
timeout /t 3 /nobreak >nul

REM Cleanup
cd /d "%~dp0"
rmdir /s /q "%DEMO_DIR%"