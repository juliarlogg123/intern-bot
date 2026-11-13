# Intern Training Assistant: Setup Guide

A chatbot that answers interns' questions using **only your firm's notes**.
You'll run it on your own computer first, then put it online for your team.

**Time needed:** about 1–2 hours the first time.
**Cost:** free tools, plus pay-as-you-go AI usage (see "Costs" at the end).

---

## What's in this folder

| File | What it does |
|---|---|
| `app.py` | The whole chatbot: chat page, password, loading notes, talking to the AI |
| `notes/` | **Put your notes here** (.docx, .pdf, .md or .txt) |
| `requirements.txt` | List of add-ons Python needs to install |
| `.streamlit/secrets.toml.example` | Template for your API key and password |
| `.gitignore` | Stops your secrets from being uploaded to GitHub |

---

## Part 1: One-time setup on your computer

### Step 1. Install Python
- Go to **python.org/downloads** and install the latest version (3.11 or newer).
- **Windows:** on the first install screen, tick **"Add Python to PATH"**.
- Check it worked: open **Terminal** (Mac) or **Command Prompt** (Windows) and type
  `python --version` (on a Mac, `python3 --version`). You should see a version number.

### Step 2. Install a code editor (recommended)
- Download **VS Code** from code.visualstudio.com. It makes editing files and running
  commands easier: File → Open Folder → choose this `intern-bot` folder, then
  Terminal → New Terminal gives you a command line already in the right place.

### Step 3. Get an AI API key
1. Go to **console.anthropic.com** and create an account (use a firm email).
2. Add a payment method under **Billing**, and **set a monthly spending limit**
   (e.g. $20–$50 to start) so costs can never surprise you.
3. Go to **API Keys → Create Key**. Copy it. It starts with `sk-ant-`.
   Treat this like a password.

### Step 4. Add your secrets
1. In the `.streamlit` folder, make a copy of `secrets.toml.example`
   and name the copy exactly **`secrets.toml`**.
2. Open it and paste in your API key, and choose a staff password.

### Step 5. Add your notes
1. Put your notes files in the `notes` folder. Word docs and PDFs are fine.
3. Tips for better answers:
   - One topic per file (e.g. `payroll_deadlines.docx`, `1040_workflow.docx`).
   - Use clear headings and numbered steps.
   - **Remove all client names and client data.**

### Step 6. Customize the bot
Open `app.py`. Near the top, under **SETTINGS**, change:
- `FIRM_NAME` to your firm's name
- `SUPERVISOR` to who interns should ask when the notes don't cover something
- Optionally edit the `INSTRUCTIONS` text to change how the bot behaves.

### Step 7. Install and run it
In the terminal, inside the `intern-bot` folder, run these one at a time:

**Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Your browser opens to the chatbot (usually http://localhost:8501).
Enter your staff password and start asking questions.

To stop it, press **Ctrl + C** in the terminal. Next time, you only need
the `activate` line and `streamlit run app.py`.

---

## Part 2: Test it before interns use it

Ask it at least 15 questions, including:
- [ ] Normal questions your notes answer ("How do I reconcile a bank account?")
- [ ] Questions your notes **don't** cover. It should say to ask your supervisor, not guess.
- [ ] A client-specific tax question. It should decline and send them to a supervisor.
- [ ] Pasting a fake SSN. It should warn about sharing client data.
- [ ] Check that each answer names which note it came from.

Bad answers almost always mean the notes are unclear or missing something.
Fix the notes; the bot uses the updated notes on the next question.

---

## Part 3: Put it online for your team

The simplest option is **Streamlit Community Cloud** (free).

1. Create a free account at **github.com**.
2. Create a new repository and set it to **Private**.
3. Upload the `intern-bot` folder contents (drag and drop works on GitHub's website).
   **Do NOT upload `secrets.toml`.** The `.gitignore` file prevents this if you use
   Git; if uploading by hand, just leave it out.
4. Go to **share.streamlit.io**, sign in with GitHub, click **Create app**, and
   pick your repository and `app.py`.
5. Under **Advanced settings → Secrets**, paste the contents of your
   `secrets.toml` (the API key and password).
6. Click **Deploy**. You'll get a web link to send to your interns, along with the password.

## Part 4: Adding new notes anytime

1. Write or clean up the new note: one topic per file, clear headings, numbered steps, no client data.
2. **Online version:** on GitHub, open the `notes` folder → **Add file → Upload files** → drop the file in → **Commit changes**.
   To edit an existing note, click the file → pencil icon → edit → **Commit changes**.
3. Within a minute or two the site updates by itself. The new note appears in the sidebar list.
4. **On your Mac:** just save the file in the `notes` folder; the bot uses it on the next question.
5. Test it: ask a question the new note answers.

Tip: if an intern asks something the bot can't answer, that's your next note.

*Alternatives:* Render.com or Railway.app work too, if you outgrow Streamlit Cloud.

---

## Ground rules for interns (share these)
1. Never paste client SSNs, account numbers, or financial data into the bot.
2. The bot covers firm procedures only, not tax advice for a client.
3. A reviewer still checks your work.
4. If the bot can't answer something, ask, and tell us so we can add it to the notes.

---

## Costs
- You pay the AI provider per question, based on how much text is sent and received.
  Because your notes are sent with each question, bigger notes mean slightly higher
  cost per question. The app uses "prompt caching" to cut this down for repeat use.
- Check current prices at **anthropic.com/pricing**, and watch actual usage in the
  console for the first month. Your spending limit is your safety net.

## Troubleshooting
| Problem | Fix |
|---|---|
| `python` not found | Reinstall Python and tick "Add to PATH" (Windows), or use `python3` (Mac) |
| `KeyError: 'ANTHROPIC_API_KEY'` | `secrets.toml` is missing or misnamed. It must be in the `.streamlit` folder |
| "authentication_error" | API key is wrong or was deleted. Create a new one |
| "No notes found" | Files must be directly in the `notes` folder |
| Answers ignore a new note | Refresh the browser page and click "Start a new chat". Check the note is listed in the sidebar |
| Notes very large (hundreds of pages) | Split into topics. Ask a developer about "retrieval" (search before answering) |

## Ideas for later
- Add a 👍/👎 button and save unanswered questions so you know what to add to the notes.
- Separate sections for bookkeeping, payroll, and tax.
- Proper staff logins instead of one shared password.
