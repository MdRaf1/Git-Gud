#!/bin/bash

# Git sensei GIF Demo Script
# This script contains the perfect sequence for recording a demo GIF
# Record with: asciinema rec git-sensei-demo.cast -c "./generate_gif.sh"

set -e

# Setup
clear
echo "🎬 Git sensei Demo - Safe, Simple, Smart Git Assistant"
echo "=================================================="
sleep 2

# Create demo environment
DEMO_DIR=$(mktemp -d)
cd "$DEMO_DIR"
git init > /dev/null 2>&1
git config user.name "Demo User" > /dev/null 2>&1
git config user.email "demo@example.com" > /dev/null 2>&1

clear

# Part 1: Git sensei is SAFE 🛡️
echo "# Part 1: Git sensei is SAFE 🛡️"
echo "# Dangerous operations require confirmation"
echo ""
echo "$ git-sensei -e \"git reset --hard HEAD~1\""
sleep 1

# Simulate the dangerous command (will show warning)
echo "⚠️  WARNING: This command will permanently delete uncommitted changes"
echo "Dangerous patterns detected: reset --hard"
echo "Type 'yes' to proceed with this dangerous operation: no"
echo "❌ Operation cancelled by user"
sleep 3

clear

# Part 2: Git sensei is SIMPLE 🗣️
echo "# Part 2: Git sensei is SIMPLE 🗣️"
echo "# Natural language interface - just describe what you want"
echo ""
echo "$ git-sensei \"show me the current status\""
sleep 1
echo "git status"
echo "On branch main"
echo ""
echo "No commits yet"
echo ""
echo "nothing to commit (create/copy files and use \"git add\" to track)"
sleep 2

echo ""
echo "$ git-sensei \"list all branches\""
sleep 1
echo "git branch -a"
echo "* main"
sleep 2

clear

# Part 3: Git sensei is SMART 🧠
echo "# Part 3: Git sensei is SMART 🧠"
echo "# Context-aware AI understands your repository state"
echo ""
echo "$ echo \"Hello Hackathon!\" > demo.txt"
echo "Hello Hackathon!" > demo.txt
sleep 1

echo ""
echo "$ git-sensei \"commit my new work\""
sleep 1
echo "git add demo.txt"
echo "💡 AI detected untracked files and suggested adding them first!"
sleep 2

echo ""
echo "$ git-sensei -e \"git add demo.txt\""
sleep 1
echo "✅ Command executed successfully"
sleep 1

echo ""
echo "$ git-sensei -e \"git commit -m 'Add demo file'\""
sleep 1
echo "[main (root-commit) abc1234] Add demo file"
echo " 1 file changed, 1 insertion(+)"
echo " create mode 100644 demo.txt"
sleep 2

echo ""
echo "$ git-sensei \"show me the commit history\""
sleep 1
echo "git log --oneline"
echo "abc1234 Add demo file"
sleep 2

clear

# Finale
echo "🎉 Git sensei Demo Complete!"
echo "========================="
echo ""
echo "✅ SAFE: Prevents dangerous operations with smart warnings"
echo "✅ SIMPLE: Natural language interface for intuitive Git usage"
echo "✅ SMART: Context-aware AI that understands your repository"
echo ""
echo "Ready to make Git safer and more accessible for everyone!"
sleep 3

# Cleanup
rm -rf "$DEMO_DIR"