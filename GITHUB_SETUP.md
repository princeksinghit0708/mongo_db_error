# GitHub Setup Instructions

## Step 1: Create Repository on GitHub

1. Go to https://github.com/new
2. Repository name: `mongodb_error_predictive_analysis`
3. Description: "MongoDB Error Predictive Analytics with ML and LLM"
4. Choose Public or Private
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## Step 2: Push to GitHub

### Option A: Using the provided script

```bash
cd "/Users/princekumarsingh/Mongodb_error_predictive analysis"
./push_to_github.sh <your-github-username>
```

### Option B: Manual commands

Replace `<your-github-username>` with your actual GitHub username:

```bash
cd "/Users/princekumarsingh/Mongodb_error_predictive analysis"

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/mongodb_error_predictive_analysis.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Option C: Using SSH (if you have SSH keys set up)

```bash
cd "/Users/princekumarsingh/Mongodb_error_predictive analysis"

# Add remote with SSH
git remote add origin git@github.com:YOUR_USERNAME/mongodb_error_predictive_analysis.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 3: Verify

After pushing, visit:
```
https://github.com/YOUR_USERNAME/mongodb_error_predictive_analysis
```

You should see all your files there!

## Troubleshooting

### Authentication Issues

If you get authentication errors:

1. **Use Personal Access Token**:
   - Go to GitHub Settings → Developer settings → Personal access tokens
   - Generate a new token with `repo` permissions
   - Use token as password when pushing

2. **Or use GitHub CLI**:
   ```bash
   gh auth login
   gh repo create mongodb_error_predictive_analysis --public --source=. --remote=origin --push
   ```

### Remote Already Exists

If you get "remote origin already exists":
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/mongodb_error_predictive_analysis.git
```
