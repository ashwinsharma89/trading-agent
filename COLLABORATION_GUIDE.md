# Git Collaboration Guide

## ✅ Repository Setup Complete

Your enterprise trading framework is now ready for collaboration! Here's what has been configured:

### 🔒 Security Features
- **`.env` file excluded** - Your API keys and credentials are protected
- **Sensitive data ignored** - Database files, logs, and cache excluded
- **`.env.example` included** - Template for collaborators to set up their own credentials

### 📦 What's Committed
- All source code (Python scripts, shell scripts)
- Documentation (README, guides, reports)
- Configuration files (docker-compose.yml, requirements.txt)
- Database schema
- Directory structure (with .gitkeep files)

### 🚫 What's Excluded
- `.env` (contains your API keys)
- `__pycache__/` and Python bytecode
- `logs/` directory contents
- `data/` directory contents (CSV, JSON files)
- `models/` directory contents (trained models)
- Virtual environments

---

## 🚀 Next Steps: Push to Remote Repository

### Option 1: GitHub (Recommended)

1. **Create a new repository on GitHub:**
   - Go to https://github.com/new
   - Name it: `enterprise-trading-framework`
   - Choose **Private** (recommended for trading systems)
   - Don't initialize with README (you already have one)

2. **Connect and push:**
   ```bash
   cd /Users/ashwin/Library/Containers/com.microsoft.Excel/Data/Documents/enterprise_trading_framework
   
   # Add remote (replace YOUR_USERNAME with your GitHub username)
   git remote add origin https://github.com/YOUR_USERNAME/enterprise-trading-framework.git
   
   # Push to GitHub
   git branch -M main
   git push -u origin main
   ```

### Option 2: GitLab

1. **Create a new project on GitLab:**
   - Go to https://gitlab.com/projects/new
   - Name it: `enterprise-trading-framework`
   - Set visibility to **Private**

2. **Connect and push:**
   ```bash
   cd /Users/ashwin/Library/Containers/com.microsoft.Excel/Data/Documents/enterprise_trading_framework
   
   # Add remote
   git remote add origin https://gitlab.com/YOUR_USERNAME/enterprise-trading-framework.git
   
   # Push to GitLab
   git branch -M main
   git push -u origin main
   ```

### Option 3: Bitbucket

1. **Create a new repository on Bitbucket:**
   - Go to https://bitbucket.org/repo/create
   - Name it: `enterprise-trading-framework`
   - Set to **Private**

2. **Connect and push:**
   ```bash
   cd /Users/ashwin/Library/Containers/com.microsoft.Excel/Data/Documents/enterprise_trading_framework
   
   # Add remote
   git remote add origin https://YOUR_USERNAME@bitbucket.org/YOUR_USERNAME/enterprise-trading-framework.git
   
   # Push to Bitbucket
   git branch -M main
   git push -u origin main
   ```

---

## 👥 Collaborator Setup Instructions

Share these steps with your team members:

### 1. Clone the Repository
```bash
git clone <REPOSITORY_URL>
cd enterprise-trading-framework
```

### 2. Set Up Environment
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your own credentials
nano .env  # or use your preferred editor
```

**Important:** Each collaborator must add their own:
- OpenAI API key
- Anthropic/Claude API key
- TradingView credentials
- Database credentials (if different)

### 3. Install Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 4. Set Up Database
```bash
# Start Docker services
docker-compose up -d

# Initialize database
python setup_database.py
```

---

## 🔄 Daily Workflow

### Before Starting Work
```bash
# Get latest changes
git pull origin main

# Create a feature branch
git checkout -b feature/your-feature-name
```

### Making Changes
```bash
# Check what changed
git status

# Stage your changes
git add .

# Commit with descriptive message
git commit -m "Add portfolio management system"

# Push to remote
git push origin feature/your-feature-name
```

### Merging Changes
1. Create a Pull Request (PR) on GitHub/GitLab/Bitbucket
2. Request code review from team members
3. After approval, merge to main branch
4. Delete the feature branch

---

## 🌿 Branching Strategy

### Main Branches
- **`main`** - Production-ready code
- **`develop`** - Integration branch for features

### Feature Branches
- **`feature/portfolio-management`** - New features
- **`bugfix/fix-data-pipeline`** - Bug fixes
- **`hotfix/critical-security-fix`** - Urgent fixes

### Example Workflow
```bash
# Create feature branch from main
git checkout main
git pull origin main
git checkout -b feature/portfolio-management

# Work on your feature...
git add .
git commit -m "Implement portfolio tracking"

# Push feature branch
git push origin feature/portfolio-management

# Create PR to merge into main
```

---

## 🔐 Security Best Practices

### ⚠️ NEVER Commit These:
- API keys or tokens
- Passwords or credentials
- Private keys (.pem, .key files)
- Database connection strings with passwords
- Personal trading data

### ✅ Always:
- Use `.env` for sensitive data
- Review changes before committing: `git diff`
- Use `.env.example` as a template
- Keep `.gitignore` updated
- Use private repositories for trading systems

### 🚨 If You Accidentally Commit Secrets:
```bash
# Remove file from Git history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .env" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (be careful!)
git push origin --force --all

# Rotate all exposed credentials immediately!
```

---

## 📝 Commit Message Guidelines

### Format
```
<type>: <subject>

<body>

<footer>
```

### Types
- **feat:** New feature
- **fix:** Bug fix
- **docs:** Documentation changes
- **style:** Code formatting
- **refactor:** Code restructuring
- **test:** Adding tests
- **chore:** Maintenance tasks

### Examples
```bash
git commit -m "feat: Add portfolio management system with P&L tracking"
git commit -m "fix: Resolve data pipeline memory leak"
git commit -m "docs: Update README with installation instructions"
```

---

## 🤝 Code Review Checklist

Before submitting a PR, ensure:
- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] Documentation is updated
- [ ] No sensitive data committed
- [ ] Commit messages are clear
- [ ] Feature branch is up to date with main

---

## 🆘 Common Git Commands

### Undo Changes
```bash
# Discard local changes
git checkout -- <file>

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1
```

### Sync with Remote
```bash
# Fetch changes without merging
git fetch origin

# Pull and rebase
git pull --rebase origin main

# Force pull (discard local changes)
git fetch origin
git reset --hard origin/main
```

### Stash Changes
```bash
# Save work in progress
git stash

# List stashes
git stash list

# Apply latest stash
git stash pop

# Apply specific stash
git stash apply stash@{0}
```

---

## 📊 Repository Statistics

```bash
# View commit history
git log --oneline --graph --all

# View contributors
git shortlog -sn

# View file changes
git diff --stat

# View branch list
git branch -a
```

---

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Clone repo | `git clone <url>` |
| Check status | `git status` |
| Create branch | `git checkout -b <branch>` |
| Switch branch | `git checkout <branch>` |
| Stage changes | `git add .` |
| Commit | `git commit -m "message"` |
| Push | `git push origin <branch>` |
| Pull | `git pull origin <branch>` |
| Merge | `git merge <branch>` |
| View log | `git log --oneline` |

---

## 📞 Support

For Git-related questions:
- Git Documentation: https://git-scm.com/doc
- GitHub Guides: https://guides.github.com/
- Git Cheat Sheet: https://education.github.com/git-cheat-sheet-education.pdf

For project-specific questions, refer to:
- `README.md` - Project overview
- `QUICK_START.md` - Getting started guide
- `SETUP_GUIDE.md` - Detailed setup instructions

---

**Happy Collaborating! 🚀**
