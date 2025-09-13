# ERISA Recovery - GitHub Pages Deployment Guide

## Pre-Deployment Checklist ✅

### 1. Project Structure Verification
- ✅ All files are properly organized in `database/`, `frontend/`, `backend/` folders
- ✅ `requirements.txt` contains all necessary dependencies
- ✅ `README.md` is comprehensive and up-to-date
- ✅ `.gitignore` file created to exclude unnecessary files
- ✅ Copyright footer added to all pages
- ✅ All templates extend `base.html` correctly

### 2. Code Quality Check
- ✅ No syntax errors in Python files
- ✅ All Django migrations applied
- ✅ Static files properly configured
- ✅ Templates render without errors
- ✅ JavaScript (Chart.js) loads correctly on report page
- ✅ CSS styling is consistent and responsive

### 3. Security Considerations
- ✅ `DEBUG = False` for production
- ✅ Secret key should be changed for production
- ✅ `ALLOWED_HOSTS` configured properly
- ✅ CSRF protection enabled

## GitHub Deployment Steps

### Step 1: Initialize Git Repository
```bash
# Navigate to your project directory
cd C:\Users\siric\Desktop\erisa_recovery

# Initialize git repository
git init

# Add all files to staging
git add .

# Create initial commit
git commit -m "Initial commit: ERISA Recovery Claims Management System"
```

### Step 2: Create GitHub Repository
1. Go to [GitHub.com](https://github.com)
2. Click "New repository" (green button)
3. Repository name: `erisa-recovery-claims-management`
4. Description: "Django-based healthcare claims management system with interactive analytics"
5. Set to **Public** (required for GitHub Pages)
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

### Step 3: Connect Local Repository to GitHub
```bash
# Add GitHub remote (replace with your actual repository URL)
git remote add origin https://github.com/YOUR_USERNAME/erisa-recovery-claims-management.git

# Push to GitHub
git push -u origin main
```

### Step 4: Configure GitHub Pages
1. Go to your repository on GitHub
2. Click "Settings" tab
3. Scroll down to "Pages" section in left sidebar
4. Under "Source", select "Deploy from a branch"
5. Select "main" branch and "/ (root)" folder
6. Click "Save"

### Step 5: Create GitHub Actions Workflow (Recommended)
Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout
      uses: actions/checkout@v3
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Run migrations
      run: |
        python manage.py migrate
        
    - name: Collect static files
      run: |
        python manage.py collectstatic --noinput
        
    - name: Deploy to GitHub Pages
      uses: peaceiris/actions-gh-pages@v3
      if: github.ref == 'refs/heads/main'
      with:
        github_token: ${{ secrets.GITHUB_TOKEN }}
        publish_dir: ./
```

### Step 6: Alternative - Manual Deployment
If you prefer manual deployment:

1. **Install GitHub CLI** (optional but recommended):
   ```bash
   # Download from https://cli.github.com/
   gh auth login
   ```

2. **Create a simple deployment script** (`deploy.py`):
   ```python
   import os
   import subprocess
   
   def deploy():
       # Run migrations
       subprocess.run(['python', 'manage.py', 'migrate'])
       
       # Collect static files
       subprocess.run(['python', 'manage.py', 'collectstatic', '--noinput'])
       
       # Commit and push changes
       subprocess.run(['git', 'add', '.'])
       subprocess.run(['git', 'commit', '-m', 'Deploy: Update application'])
       subprocess.run(['git', 'push', 'origin', 'main'])
   
   if __name__ == '__main__':
       deploy()
   ```

## Production Configuration

### Step 7: Update Settings for Production
1. **Change Secret Key** in `erisa_recovery/settings.py`:
   ```python
   SECRET_KEY = 'your-unique-secret-key-here-change-this'
   ```

2. **Update ALLOWED_HOSTS**:
   ```python
   ALLOWED_HOSTS = ['your-username.github.io', 'localhost', '127.0.0.1']
   ```

3. **Set DEBUG to False**:
   ```python
   DEBUG = False
   ```

### Step 8: Environment Variables (Optional)
Create `.env` file for sensitive data:
```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-username.github.io,localhost
```

## Testing Deployment

### Step 9: Test Locally
```bash
# Test with production settings
python manage.py runserver --settings=erisa_recovery.production_settings

# Or test with debug off
python manage.py runserver 0.0.0.0:8000
```

### Step 10: Verify GitHub Pages
1. Wait 5-10 minutes for GitHub Pages to build
2. Visit: `https://your-username.github.io/erisa-recovery-claims-management`
3. Test all functionality:
   - Dashboard loads correctly
   - Search and filters work
   - Report page displays charts
   - CSV upload works
   - All styling is applied

## Troubleshooting

### Common Issues:

1. **Static files not loading**:
   - Run `python manage.py collectstatic`
   - Check `STATIC_URL` and `STATIC_ROOT` settings

2. **Database errors**:
   - Run `python manage.py migrate`
   - Check database file permissions

3. **Template errors**:
   - Verify all templates extend `base.html`
   - Check template syntax

4. **JavaScript not working**:
   - Check browser console for errors
   - Verify Chart.js CDN is loading

### Getting Help:
- Check GitHub Actions logs if using CI/CD
- Review Django logs in browser console
- Test locally with production settings

## Final Checklist Before Deployment

- [ ] All files committed to git
- [ ] Repository is public
- [ ] GitHub Pages is enabled
- [ ] Secret key changed from default
- [ ] DEBUG = False
- [ ] ALLOWED_HOSTS includes your GitHub Pages domain
- [ ] Static files collected
- [ ] Database migrations applied
- [ ] All functionality tested locally
- [ ] README.md is complete and accurate

## Post-Deployment

1. **Update README.md** with live demo link
2. **Add screenshots** to repository
3. **Create a demo video** (optional)
4. **Share the project** on LinkedIn/portfolio

Your ERISA Recovery Claims Management System will be live at:
`https://your-username.github.io/erisa-recovery-claims-management`

Good luck with your deployment! 🚀
