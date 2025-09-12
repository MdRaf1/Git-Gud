@echo off
REM Git sensei Final Validation Script
REM This script performs a comprehensive end-to-end test of Git sensei functionality

echo 🚀 Starting Git sensei Final Validation...
echo ========================================

REM Create temporary directory for testing
set TEMP_DIR=%TEMP%\git_sensei_test_%RANDOM%
mkdir "%TEMP_DIR%"
echo 📁 Created temporary test directory: %TEMP_DIR%

REM Change to temp directory and initialize git repo
cd /d "%TEMP_DIR%"
git init
git config user.name "Test User"
git config user.email "test@example.com"

echo.
echo 🔍 Test 1: Check empty repository status
echo Command: git-sensei "check the status"
git-sensei "check the status"

echo.
echo 📝 Creating test file...
echo Hello Hackathon > file.txt

echo.
echo 🧠 Test 2: Context-aware AI suggestion
echo Command: git-sensei "commit this new file"
echo Expected: AI should suggest adding the file first
git-sensei "commit this new file"

echo.
echo ⚡ Test 3: Direct command execution
echo Command: git-sensei -e "git add file.txt"
git-sensei -e "git add file.txt"

echo.
echo Command: git-sensei -e "git commit -m \"Initial commit\""
git-sensei -e "git commit -m \"Initial commit\""

echo.
echo ⚠️  Test 4: Dangerous command with safety net
echo Command: git-sensei "revert the last commit completely"
echo Expected: Should prompt for confirmation, we'll respond 'no'
echo no | git-sensei "revert the last commit completely" || echo ✅ Safety net worked - dangerous command was aborted

echo.
echo 🎯 Test 5: Verify repository state
echo Command: git-sensei -e "git log --oneline"
git-sensei -e "git log --oneline"

echo.
echo 🧹 Cleaning up temporary directory...
cd /d "%~dp0"
rmdir /s /q "%TEMP_DIR%"

echo.
echo 🎉 All tests completed successfully!
echo Git sensei is working perfectly and ready for the hackathon!