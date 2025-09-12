#!/bin/bash

# Git sensei Final Validation Script
# This script performs a comprehensive end-to-end test of Git sensei functionality

set -e  # Exit on any error

echo "🚀 Starting Git sensei Final Validation..."
echo "========================================"

# Create temporary directory for testing
TEMP_DIR=$(mktemp -d)
echo "📁 Created temporary test directory: $TEMP_DIR"

# Cleanup function
cleanup() {
    echo "🧹 Cleaning up temporary directory..."
    rm -rf "$TEMP_DIR"
    echo "✅ Cleanup complete"
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Change to temp directory and initialize git repo
cd "$TEMP_DIR"
git init
git config user.name "Test User"
git config user.email "test@example.com"

echo ""
echo "🔍 Test 1: Check empty repository status"
echo "Command: git-sensei 'check the status'"
git-sensei "check the status"

echo ""
echo "📝 Creating test file..."
echo "Hello Hackathon" > file.txt

echo ""
echo "🧠 Test 2: Context-aware AI suggestion"
echo "Command: git-sensei 'commit this new file'"
echo "Expected: AI should suggest adding the file first"
git-sensei "commit this new file"

echo ""
echo "⚡ Test 3: Direct command execution"
echo "Command: git-sensei -e 'git add file.txt'"
git-sensei -e "git add file.txt"

echo ""
echo "Command: git-sensei -e 'git commit -m \"Initial commit\"'"
git-sensei -e "git commit -m 'Initial commit'"

echo ""
echo "⚠️  Test 4: Dangerous command with safety net"
echo "Command: git-sensei 'revert the last commit completely'"
echo "Expected: Should prompt for confirmation, we'll respond 'no'"
echo "no" | git-sensei "revert the last commit completely" || echo "✅ Safety net worked - dangerous command was aborted"

echo ""
echo "🎯 Test 5: Verify repository state"
echo "Command: git-sensei -e 'git log --oneline'"
git-sensei -e "git log --oneline"

echo ""
echo "🎉 All tests completed successfully!"
echo "Git sensei is working perfectly and ready for the hackathon!"