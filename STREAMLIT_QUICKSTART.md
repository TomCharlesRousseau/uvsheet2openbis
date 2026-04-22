# Streamlit UI - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies (First Time Only)

**Windows:**
```bash
# Double-click setup.bat
# OR run in Command Prompt:
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

### Step 2: Start the Application

**Windows:**
```bash
# Double-click run_streamlit.bat
# OR run in Command Prompt:
streamlit run streamlit_app.py
```

**Linux/Mac:**
```bash
streamlit run streamlit_app.py
```

### Step 3: Open in Browser

The app will automatically open at:
```
http://localhost:8501
```

If it doesn't, open this URL manually in your browser.

---

## 📋 First-Time Setup Checklist

- [ ] Install dependencies using `setup.bat` or `setup.sh`
- [ ] Prepare your Excel file (`UV-Sheets_protocol.xlsx`)
- [ ] Have your openBIS credentials ready
- [ ] Know your openBIS server URL
- [ ] Start the application with `run_streamlit.bat` or `streamlit run streamlit_app.py`

---

## 🔐 Understanding the Connection Flow

When you connect to openBIS, here's what happens:

1. **App tries to load saved PAT token from system keyring**
   - Fast (instant login)
   - No password needed

2. **If PAT not found, prompts for password** (appears in terminal)
   - Type your password and press Enter
   - Token is saved for next time

3. **Connection established**
   - Ready to use the parser
   - ✅ Status displayed in Connection tab

---

## 💡 Typical Usage Workflow

```
1. START APP
   ↓
2. CONNECT TO OPENBIS
   - Click "Connect to openBIS" button
   - Enter password when prompted in terminal
   - Wait for ✅ Connected message
   ↓
3. UPLOAD EXCEL FILE
   - Drag & drop your Excel file
   - Review the preview
   - Check "Already Uploaded" count
   ↓
4. CONFIGURE PARSER
   - Choose mode (Dry Run or Live)
   - Adjust batch size if needed
   - Review expected behavior
   ↓
5. RUN PARSER
   - Click "START PARSER"
   - Watch progress bar
   - Review detailed messages
   ↓
6. VIEW RESULTS
   - Check summary metrics
   - Review successful/failed counts
   - Download log if needed
   ↓
7. REPEAT OR VERIFY
   - Check newly created objects in openBIS
   - Excel file automatically updated
```

---

## 📁 File Locations

### Configuration Files
```
config/
├── __init__.py
└── settings.json          ← Edit with your openBIS details
```

### Log Files
```
parser.log                 ← Main parser log (see details there)
```

### Temporary Files
```
.temp/                     ← Uploaded Excel files go here
.cache/                    ← Local data cache (if enabled)
```

---

## 🆘 Troubleshooting

### Browser Won't Open
- The app is running in the terminal
- Manually open: `http://localhost:8501`

### Password Prompt Appears in Terminal (Not Browser)
- This is **normal**!
- Look for the prompt in the terminal window
- Type your password and press Enter

### "Not connected" Error
1. Check internet connection
2. Verify openBIS URL is correct
3. Verify username is correct
4. Check password
5. See Connection tab for detailed error

### Excel File Not Uploading
1. Ensure file is valid Excel (.xlsx or .xls)
2. Try opening in Excel first
3. Check file size (should be < 10 MB)
4. Look for error message in Results tab

### Parser Stuck/Slow
1. Check your internet connection
2. openBIS server might be slow
3. Try smaller batch size (default: 50)
4. Check parser.log for errors

---

## 📚 Available Documentation

- **[STREAMLIT_UI.md](STREAMLIT_UI.md)** - Full UI documentation
- **[README.md](README.md)** - Parser overview
- **[QUICKSTART.md](QUICKSTART.md)** - Command-line quick start
- **[CLAUDE.md](CLAUDE.md)** - Project architecture

---

## ⚙️ Advanced Configuration

### Custom Parser Settings

Edit `config/settings.json`:
```json
{
    "openbis": {
        "api_url": "https://your-server/api/v3",
        "space": "YOUR_SPACE",
        "project_name": "YOUR_PROJECT"
    }
}
```

### Debug Mode

```bash
streamlit run streamlit_app.py --logger.level=debug
```

---

## 📊 Typical Results

**Successful Example:**
```
Processing: EXP001 (1/10)
✅ Row 1 (EXP001): Created successfully with 3 child samples

Processing: EXP002 (2/10)
✅ Row 2 (EXP002): Created successfully with 2 child samples

...

Results:
✅ Successful: 8
⚠️ Skipped: 2  (already uploaded)
❌ Failed: 0

Total time: 12.3 seconds
```

---

## 🎯 Next Steps

Once you're comfortable with the basic workflow:

1. ✅ Understand dry-run mode for testing
2. ✅ Practice with a small Excel file first
3. ✅ Use live mode when confident
4. ✅ Set up automatic batch runs (future feature)
5. ✅ Monitor results and validate in openBIS

---

## 💬 Common Questions

**Q: Is it safe to run parser multiple times on same file?**
A: Yes! Rows already marked "Uploaded" → "Yes" are automatically skipped.

**Q: What if parser crashes mid-run?**
A: No problem! Your progress is saved. Re-run and it will continue from where it left off.

**Q: Can I edit the running parser?**
A: No, but you can use the Cancel button to stop it anytime.

**Q: Where do I verify if objects were created?**
A: Check openBIS directly by navigating to the collection.

**Q: Is dry-run mode accurate?**
A: Yes, it shows exactly what would be created in live mode.

---

## 📞 Support

For issues:
1. Check the parser log (downloads from Results tab)
2. Review error messages in the UI
3. Check openBIS server status
4. Consult full documentation in [STREAMLIT_UI.md](STREAMLIT_UI.md)

---

**Happy parsing! 🚀**
