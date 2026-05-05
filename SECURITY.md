# 🔐 Security Guidelines

## Credential Storage

### ✅ Safe Workflow

1. **Run setup in Binder** (no credentials needed)
   - Click the Binder badge in README
   - Run the notebook cells to install dependencies
   - No credentials are entered during this step

2. **Download repository locally**
   - After Binder validation, download/clone to your machine
   - Credentials are ONLY stored on your local machine

3. **Edit `config/settings.json` LOCALLY** (on your computer)
   - Copy `config/settings.json.example` to `config/settings.json`
   - Edit your local copy with your openBIS credentials
   - This file is in `.gitignore` and will NEVER be committed to GitHub

4. **Use secure credential storage**
   - On first launch, you'll be prompted for password
   - Credentials are stored in your system's secure keyring:
     - **Windows:** Credential Manager
     - **macOS:** Keychain
     - **Linux:** pass or similar
   - Credentials are NEVER stored in plain text

### ❌ NEVER Do These Things

❌ **Don't paste credentials into Binder**
- Binder is a public service
- Credentials would be visible in cell outputs
- Outputs might be logged

❌ **Don't commit `config/settings.json` to GitHub**
- You would expose your credentials publicly
- GitHub will scan for exposed secrets

❌ **Don't hardcode credentials in code**
```python
# ❌ WRONG
API_KEY = "sk_live_abc123..."
```

❌ **Don't share notebooks with credentials**
- Credentials persist in Jupyter cell outputs
- `.ipynb` files are JSON and readable

---

## Sensitive Data Handling

### Settings File Protection

**`config/settings.json` is protected by:**

1. **.gitignore:** Prevents accidental commits
2. **File permissions:** Should be readable only by your user
   ```bash
   # Linux/macOS - restrict permissions
   chmod 600 config/settings.json
   ```
3. **Keyring storage:** OS-level encryption for tokens

### Environment Variables (Optional Alternative)

Instead of `config/settings.json`, you can use environment variables:

```bash
# Windows PowerShell
$env:OPENBIS_URL = "https://openbis.example.com/api/v3"
$env:OPENBIS_USERNAME = "your_username"

# macOS/Linux
export OPENBIS_URL="https://openbis.example.com/api/v3"
export OPENBIS_USERNAME="your_username"
```

---

## If You Accidentally Leaked a Credential

### 🚨 IMMEDIATE ACTIONS (Do This NOW)

1. **Rotate the credential in openBIS**
   - Go to your openBIS settings
   - Generate a new PAT/API key
   - The old one is now useless

2. **Check git history**
   ```bash
   git log --all --full-history config/settings.json
   git log --all --source --grep="settings" --oneline
   ```

3. **If credential is in git history:** Clean it
   ```bash
   # Remove file from all history
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch config/settings.json' \
   --prune-empty --tag-name-filter cat -- --all
   
   # Force push to GitHub
   git push origin --force --all
   ```

4. **Check logs**
   - GitHub Actions logs might contain outputs
   - Check workflow runs and delete if needed

5. **Notify maintainers**
   - Email the project maintainer
   - Don't post publicly (it confirms the leak)

---

## GitHub Secret Scanning

This repository has GitHub secret scanning enabled.

**What happens:**
- ✅ GitHub automatically scans for exposed credentials
- ✅ You'll get an alert if a secret is detected
- ✅ You'll be forced to rotate the credential
- ✅ The secret is added to GitHub's blocklist

**If you see an alert:**
1. **You have:** ~1 hour before attackers exploit it
2. **Action:** Immediately rotate the credential
3. **Then:** Follow "If You Accidentally Leaked" steps above

---

## Best Practices Checklist

- [ ] I understand that `config/settings.json` is never committed
- [ ] I have `.gitignore` in my local repository
- [ ] I haven't pasted credentials into Binder
- [ ] I store credentials in `.env` or keyring, never in code
- [ ] I never hardcode API keys in notebooks
- [ ] I know how to rotate credentials if needed

---

## Reporting Security Issues

**If you find a security vulnerability in this code:**

**DO NOT:**
- ❌ Post it in GitHub Issues (public)
- ❌ Post it in Discussions
- ❌ Ask for help in a public forum

**DO:**
- ✅ Email: [security@example.com](mailto:security@example.com)
- ✅ Subject: "Security Issue in UV Sheet Parser"
- ✅ Include: Detailed description, steps to reproduce, impact
- ✅ Allow: 7 days for response before public disclosure

**Responsible Disclosure:**
We take security seriously. Report responsibly and help us keep users safe.

---

## References

- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [Python Keyring Library](https://keyring.readthedocs.io/)
- [OWASP: Secrets Management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [Git: Removing Sensitive Data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)

---

**Last Updated:** 2026-05-05  
**Version:** 1.0
