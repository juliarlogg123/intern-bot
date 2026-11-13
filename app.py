"""
Intern Training Assistant
A simple chatbot that answers interns' questions using ONLY your firm's notes.

Run locally with:   streamlit run app.py
"""

from pathlib import Path

import anthropic
import streamlit as st

# ---------------------------------------------------------------------------
# 1. SETTINGS - change these to fit your firm
# ---------------------------------------------------------------------------
FIRM_NAME = "WBH Consulting"
SUPERVISOR = "Reagan"
MODEL = "claude-sonnet-5-5"             # the AI model to use
NOTES_FOLDER = Path(__file__).parent / "notes"

INSTRUCTIONS = f"""You are the training assistant for interns at {FIRM_NAME}, an accounting
firm that does QuickBooks bookkeeping, payroll, and tax returns (individual,
corporate, partnership, and trust).

Rules:
- Answer ONLY using the firm notes provided below. Do not use outside knowledge
  to fill in firm procedures.
- If the notes don't cover the question, say: "That isn't in our procedures yet -
  please ask {SUPERVISOR}." Do not guess.
- Never give tax advice about a specific client. Point the intern to {SUPERVISOR}.
- If an intern pastes client personal information (SSNs, account numbers, etc.),
  remind them not to share client data in this chat.
- Keep answers short and step-by-step. Use numbered steps for procedures.
- At the end of each answer, say which note or section it came from.
"""


# ---------------------------------------------------------------------------
# 2. LOAD THE NOTES - reads every .md, .txt, .docx and .pdf file in /notes
# ---------------------------------------------------------------------------
def read_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in (".md", ".txt"):
        return path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".docx":
        import docx  # from the python-docx package
        return "\n".join(p.text for p in docx.Document(path).paragraphs)
    if suffix == ".pdf":
        from pypdf import PdfReader
        return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)
    return ""


def notes_fingerprint() -> tuple:
    """Names + last-modified times of every note, so the cache refreshes
    automatically whenever a note is added, changed or removed."""
    return tuple(
        (str(p), p.stat().st_mtime)
        for p in sorted(NOTES_FOLDER.glob("**/*")) if p.is_file()
    )


@st.cache_data
def load_notes(fingerprint: tuple = ()) -> tuple[str, list[str]]:
    parts, names = [], []
    for path in sorted(NOTES_FOLDER.glob("**/*")):
        if path.is_file() and not path.name.startswith("."):
            text = read_file(path).strip()
            if text:
                parts.append(f"<note name=\"{path.name}\">\n{text}\n</note>")
                names.append(path.name)
    return "\n\n".join(parts), names


# ---------------------------------------------------------------------------
# 3. SIMPLE PASSWORD GATE - keeps the bot to your staff only
# ---------------------------------------------------------------------------
def check_password() -> bool:
    if st.session_state.get("authenticated"):
        return True
    if LOGO.exists():
        st.image(str(LOGO), width=220)
    st.title("Intern Training Assistant")
    pw = st.text_input("Staff password", type="password")
    if pw:
        if pw == st.secrets["APP_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    return False


# ---------------------------------------------------------------------------
# 4. THE CHAT PAGE
# ---------------------------------------------------------------------------
# Company logo: put your logo at assets/logo.png and it appears automatically
# (top-left corner and the browser tab). No file = no logo, nothing breaks.
LOGO = Path(__file__).parent / "assets" / "logo.png"

st.set_page_config(
    page_title="Intern Training Assistant",
    page_icon=str(LOGO) if LOGO.exists() else None,
)
if LOGO.exists():
    st.logo(str(LOGO), size="large")

if not check_password():
    st.stop()

notes_text, note_names = load_notes(fingerprint=notes_fingerprint())
client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

if LOGO.exists():
    st.image(str(LOGO), width=220)
st.title("Intern Training Assistant")
st.caption(f"{FIRM_NAME} · Answers come only from firm notes. "
           "Never paste client data here. A reviewer still checks your work.")

with st.sidebar:
    st.subheader("Notes loaded")
    if note_names:
        for name in note_names:
            st.write(f"- {name}")
    else:
        st.warning("No notes found. Add files to the 'notes' folder.")
    if st.button("Start a new chat"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Show the conversation so far
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle a new question
if question := st.chat_input("Ask a question about firm procedures..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    system = [
        {"type": "text", "text": INSTRUCTIONS},
        {
            "type": "text",
            "text": f"FIRM NOTES:\n\n{notes_text}",
            # Caching the notes makes repeat questions cheaper and faster
            "cache_control": {"type": "ephemeral"},
        },
    ]

    with st.chat_message("assistant"):
        try:
            with client.messages.stream(
                model=MODEL,
                max_tokens=1500,
                system=system,
                messages=st.session_state.messages,
            ) as stream:
                answer = st.write_stream(stream.text_stream)
        except anthropic.APIError as e:
            answer = f"Sorry, something went wrong talking to the AI service: {e}"
            st.error(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})
