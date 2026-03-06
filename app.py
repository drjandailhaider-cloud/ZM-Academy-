import streamlit as st
import json, hashlib, datetime, time, os, base64
from anthropic import Anthropic

# ─────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HomeWork Helper 📚",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────
SUBJECTS = {
    "Maths":   {"emoji": "🔢", "color": "#E8472A"},
    "Physics": {"emoji": "⚡", "color": "#2563EB"},
    "English": {"emoji": "📖", "color": "#059669"},
    "Urdu":    {"emoji": "🖊️", "color": "#7C3AED"},
}

LEVELS = [
    "Class 1","Class 2","Class 3","Class 4","Class 5",
    "Class 6","Class 7","Class 8","O Level","A Level"
]

AVATARS = {
    "👦 Boy":"👦", "👧 Girl":"👧", "👨 Dad":"👨", "👩 Mom":"👩",
    "👨‍🏫 Teacher":"👨‍🏫", "🧑‍🚀 Astronaut":"🧑‍🚀",
    "🧑‍🔬 Scientist":"🧑‍🔬", "🧑‍🎨 Artist":"🧑‍🎨"
}

ESSAY_TYPES = [
    "Descriptive Essay","Argumentative Essay","Narrative Story",
    "Letter Writing","Report Writing","Summary Writing"
]

IMAGE_STYLES = {
    "📐 Educational Diagram":
        "a clean labeled educational diagram with arrows showing relationships, colorful sections, white background",
    "🎨 Colorful Cartoon":
        "a bright fun cartoon illustration with cheerful colors suitable for children",
    "🔬 Scientific Illustration":
        "a detailed realistic scientific diagram like a textbook, accurate and clearly labeled",
    "🗺️ Mind Map":
        "a colorful mind map with a central topic, branches and sub-branches with connecting lines",
}

BADGES = [
    {"id":"first_q",  "icon":"🌟","name":"First Step",       "desc":"Asked first question",   "req": lambda s: s.get("total",0)>=1},
    {"id":"curious",  "icon":"🧠","name":"Curious Mind",     "desc":"Asked 5 questions",      "req": lambda s: s.get("total",0)>=5},
    {"id":"seeker",   "icon":"📚","name":"Knowledge Seeker", "desc":"Asked 20 questions",     "req": lambda s: s.get("total",0)>=20},
    {"id":"maths",    "icon":"🔢","name":"Maths Master",     "desc":"10 Maths questions",     "req": lambda s: s.get("Maths",0)>=10},
    {"id":"physics",  "icon":"⚡","name":"Physics Pro",      "desc":"10 Physics questions",   "req": lambda s: s.get("Physics",0)>=10},
    {"id":"english",  "icon":"📖","name":"English Expert",   "desc":"10 English questions",   "req": lambda s: s.get("English",0)>=10},
    {"id":"urdu",     "icon":"🖊️","name":"Urdu Ustad",       "desc":"10 Urdu questions",      "req": lambda s: s.get("Urdu",0)>=10},
    {"id":"allround", "icon":"🏆","name":"All-Rounder",      "desc":"Studied all 4 subjects", "req": lambda s: all(s.get(x,0)>0 for x in ["Maths","Physics","English","Urdu"])},
    {"id":"artist",   "icon":"🎨","name":"Visual Learner",   "desc":"Generated 3 images",     "req": lambda s: s.get("images",0)>=3},
    {"id":"writer",   "icon":"✏️","name":"Essay Writer",     "desc":"Used Essay Helper",      "req": lambda s: s.get("essays",0)>=1},
    {"id":"streak",   "icon":"🔥","name":"7-Day Streak",     "desc":"7 days in a row",        "req": lambda s: s.get("streak",0)>=7},
    {"id":"doc_reader","icon":"📄","name":"Doc Reader",      "desc":"Uploaded a document",    "req": lambda s: s.get("docs",0)>=1},
]

QUICK_PROMPTS = {
    "Maths":   ["Explain fractions with examples","Solve: 2x + 5 = 15","What is Pythagoras theorem?","How to calculate percentage?"],
    "Physics": ["What are Newton's 3 laws?","How does electricity work?","What is gravity?","Difference between speed and velocity"],
    "English": ["How to write a good essay?","Explain past and present tense","What are nouns and verbs?","How to improve vocabulary?"],
    "Urdu":    ["اردو گرامر کی بنیادی باتیں","نظم اور نثر میں کیا فرق ہے؟","اچھا مضمون کیسے لکھیں؟","محاورے کیا ہوتے ہیں؟"],
}

# ─────────────────────────────────────────────────────────────────
# DATA STORAGE (JSON files)
# ─────────────────────────────────────────────────────────────────
USERS_FILE   = "users.json"
HISTORY_FILE = "history.json"
IMAGES_FILE  = "images.json"

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_stats():
    return {"total":0,"Maths":0,"Physics":0,"English":0,"Urdu":0,
            "streak":0,"lastDate":"","images":0,"essays":0,"docs":0}

# ─────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────
defaults = {
    "logged_in": False, "user": None, "page": "home",
    "subject": "Maths", "level": "Class 5",
    "chat_messages": [], "session_id": None,
    "quiz": None, "essay_result": "",
    "trans_result": "", "word_of_day": None, "wod_loaded": False,
    "dark_mode": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────
# ANTHROPIC CLIENT
# ─────────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    key = st.secrets.get("ANTHROPIC_API_KEY", "") or os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        return None
    return Anthropic(api_key=key)

client = get_client()

def call_ai(messages, system, max_tokens=1200):
    if not client:
        return "⚠️ API key not configured. Add ANTHROPIC_API_KEY in Streamlit secrets."
    try:
        r = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=max_tokens,
            system=system,
            messages=messages
        )
        return r.content[0].text
    except Exception as e:
        return f"⚠️ Error: {e}"

def call_ai_with_doc(messages, system, doc_content, max_tokens=1500):
    """Call AI with document content included"""
    if not client:
        return "⚠️ API key not configured."
    try:
        augmented_system = system + f"\n\nThe student has uploaded a document. Here is its content:\n\n{doc_content[:8000]}"
        r = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=max_tokens,
            system=augmented_system,
            messages=messages
        )
        return r.content[0].text
    except Exception as e:
        return f"⚠️ Error: {e}"

def call_ai_svg(messages, system):
    if not client:
        return "⚠️ API key not configured."
    try:
        r = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4000,
            system=system,
            messages=messages
        )
        return r.content[0].text
    except Exception as e:
        return f"ERROR: {e}"

# ─────────────────────────────────────────────────────────────────
# BADGES & STATS
# ─────────────────────────────────────────────────────────────────
def check_badges(user):
    earned = user.get("badges", [])
    new_ones = []
    stats = user.get("stats", {})
    for b in BADGES:
        if b["id"] not in earned and b["req"](stats):
            earned.append(b["id"])
            new_ones.append(b)
    user["badges"] = earned
    return user, new_ones

def bump_stats(subject_field=None, extra_field=None):
    users = load_json(USERS_FILE)
    email = st.session_state.user["email"]
    u = users.get(email, st.session_state.user)
    s = u.get("stats", init_stats())
    s["total"] = s.get("total", 0) + 1
    if subject_field:
        s[subject_field] = s.get(subject_field, 0) + 1
    if extra_field:
        s[extra_field] = s.get(extra_field, 0) + 1
    today = datetime.date.today().isoformat()
    yest  = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    if s.get("lastDate", "") == today:
        pass
    elif s.get("lastDate", "") == yest:
        s["streak"] = s.get("streak", 0) + 1
    else:
        s["streak"] = 1
    s["lastDate"] = today
    u["stats"] = s
    u, new_badges = check_badges(u)
    users[email] = u
    save_json(USERS_FILE, users)
    st.session_state.user = u
    for b in new_badges:
        st.toast(f"🏆 Badge Earned: {b['icon']} {b['name']}!", icon="🎉")

# ─────────────────────────────────────────────────────────────────
# THEME COLORS
# ─────────────────────────────────────────────────────────────────
def get_theme():
    if st.session_state.dark_mode:
        return {
            "bg": "#0F0F1A",
            "card": "#1A1A2E",
            "card_border": "#2D2D4A",
            "text": "#FFFFFF",
            "text_muted": "#AAAACC",
            "sidebar_bg": "#070710",
            "sidebar_text": "#FFFFFF",
            "sidebar_active": "#E8472A",
            "input_bg": "#1A1A2E",
            "msg_bot_bg": "#1A1A2E",
            "msg_bot_text": "#FFFFFF",
            "msg_bot_border": "#2D2D4A",
            "page_bg": "#0F0F1A",
        }
    else:
        return {
            "bg": "#F8F9FC",
            "card": "#FFFFFF",
            "card_border": "#F0F0F5",
            "text": "#1A1A2E",
            "text_muted": "#666688",
            "sidebar_bg": "#1A1A2E",
            "sidebar_text": "#FFFFFF",
            "sidebar_active": "#E8472A",
            "input_bg": "#FFFFFF",
            "msg_bot_bg": "#FFFFFF",
            "msg_bot_text": "#1A1A2E",
            "msg_bot_border": "#F0F0F5",
            "page_bg": "#F8F9FC",
        }

# ─────────────────────────────────────────────────────────────────
# CSS — Dynamic based on theme
# ─────────────────────────────────────────────────────────────────
def inject_css():
    t = get_theme()
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Baloo+2:wght@600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Nunito', sans-serif !important;
    background-color: {t['page_bg']} !important;
    color: {t['text']} !important;
}}

/* ── Main background ── */
.stApp {{
    background-color: {t['page_bg']} !important;
}}
.main .block-container {{
    padding-top: 0.5rem;
    padding-bottom: 2rem;
    max-width: 950px;
    background-color: {t['page_bg']};
}}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header {{ visibility: hidden; }}

/* ── SIDEBAR — fully visible text ── */
[data-testid="stSidebar"] {{
    background-color: {t['sidebar_bg']} !important;
    border-right: 1px solid rgba(255,255,255,0.08);
    min-width: 220px !important;
}}
[data-testid="stSidebar"] * {{
    color: {t['sidebar_text']} !important;
}}
[data-testid="stSidebar"] .stButton > button {{
    background-color: rgba(255,255,255,0.07) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    padding: 8px 12px !important;
    margin-bottom: 3px !important;
    transition: all 0.2s ease;
    text-align: left !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background-color: rgba(232,71,42,0.35) !important;
    border-color: #E8472A !important;
    transform: translateX(2px);
}}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {{
    background: linear-gradient(135deg, #E8472A, #C1391F) !important;
    border-color: #E8472A !important;
    box-shadow: 0 3px 12px rgba(232,71,42,0.4) !important;
}}

/* ── Chat bubbles ── */
.msg-user {{
    background: linear-gradient(135deg, #E8472A, #C1391F);
    color: #fff;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 16px;
    margin: 4px 0 4px 60px;
    font-size: 14px;
    line-height: 1.65;
}}
.msg-bot {{
    background: {t['msg_bot_bg']};
    color: {t['msg_bot_text']};
    border-radius: 18px 18px 18px 4px;
    padding: 12px 16px;
    margin: 4px 60px 4px 0;
    font-size: 14px;
    line-height: 1.7;
    box-shadow: 0 2px 10px rgba(0,0,0,0.07);
    border: 1px solid {t['msg_bot_border']};
}}
.msg-lbl {{ font-size: 11px; color: #bbb; margin-bottom: 2px; }}
.msg-lbl-r {{ text-align: right; }}

/* ── Cards ── */
.stat-card {{
    background: {t['card']};
    border-radius: 14px;
    padding: 16px;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    border: 1px solid {t['card_border']};
}}
.stat-num {{ font-size: 28px; font-weight: 900; color: {t['text']}; }}
.stat-lbl {{ font-size: 11px; color: {t['text_muted']}; margin-top: 3px; }}

/* ── Badges ── */
.badge-card {{
    background: {'linear-gradient(135deg,#2A2A40,#1E1E35)' if st.session_state.dark_mode else 'linear-gradient(135deg,#FFF8E7,#FFFBF0)'};
    border: 1.5px solid {'#5B4A15' if st.session_state.dark_mode else '#F5CC4A'};
    border-radius: 12px;
    padding: 12px 10px;
    text-align: center;
}}
.badge-locked {{ opacity: 0.3; filter: grayscale(1); }}
.badge-icon {{ font-size: 28px; display: block; }}
.badge-name {{ font-size: 12px; font-weight: 800; color: {'#F5CC4A' if st.session_state.dark_mode else '#A07820'}; margin-top: 4px; }}
.badge-desc {{ font-size: 10px; color: {t['text_muted']}; margin-top: 2px; }}

/* ── Progress bar ── */
.prog-bar {{
    background: {'#2D2D4A' if st.session_state.dark_mode else '#F0F0F5'};
    border-radius: 99px;
    height: 10px;
    overflow: hidden;
    margin-bottom: 4px;
}}
.prog-fill {{ height: 100%; border-radius: 99px; transition: width .4s; }}

/* ── Word card ── */
.word-card {{
    background: linear-gradient(135deg, #1A1A2E, #2D2D4A);
    border-radius: 16px;
    padding: 18px 20px;
    margin-bottom: 14px;
    color: #fff;
}}

/* ── Reminder ── */
.reminder {{
    background: {'#2A2500' if st.session_state.dark_mode else '#FFFBF0'};
    border: 1.5px solid #F5CC4A;
    border-radius: 12px;
    padding: 12px 16px;
    margin-bottom: 14px;
    font-size: 13px;
    color: {t['text']};
}}

/* ── History card ── */
.hist-card {{
    background: {t['card']};
    border-radius: 14px;
    padding: 14px 16px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    border: 1px solid {t['card_border']};
    margin-bottom: 10px;
}}

/* ── Buttons ── */
.stButton > button {{
    border-radius: 12px !important;
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    transition: all 0.2s ease;
}}

/* ── Inputs ── */
.stTextInput > div > div > input,
.stSelectbox > div > div > div,
.stTextArea > div > div > textarea {{
    border-radius: 10px !important;
    font-family: 'Nunito', sans-serif !important;
    background-color: {t['input_bg']} !important;
    color: {t['text']} !important;
}}

/* ── File uploader ── */
[data-testid="stFileUploader"] {{
    background: {'#1A1A2E' if st.session_state.dark_mode else '#F8F9FC'} !important;
    border-radius: 12px !important;
    border: 2px dashed {'#4A4A6A' if st.session_state.dark_mode else '#D0D0E0'} !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    background: {'#1A1A2E' if st.session_state.dark_mode else '#F0F0F5'} !important;
    border-radius: 12px;
    padding: 4px;
}}
.stTabs [data-baseweb="tab"] {{
    color: {t['text']} !important;
    border-radius: 8px !important;
}}

/* ── Metric ── */
[data-testid="stMetricValue"] {{ color: {t['text']} !important; }}
[data-testid="stMetricLabel"] {{ color: {t['text_muted']} !important; }}

/* ── Expander ── */
.streamlit-expanderHeader {{
    background: {t['card']} !important;
    color: {t['text']} !important;
    border-radius: 10px !important;
}}
.streamlit-expanderContent {{
    background: {'#13132A' if st.session_state.dark_mode else '#FAFAFA'} !important;
}}

/* ── Selectbox options dropdown ── */
[data-baseweb="popover"] * {{
    background: {t['card']} !important;
    color: {t['text']} !important;
}}

/* ── Column padding ── */
div[data-testid="column"] {{ padding: 4px !important; }}

/* ── Mobile responsive ── */
@media (max-width: 768px) {{
    .main .block-container {{ padding: 0.5rem 0.8rem 2rem !important; max-width: 100% !important; }}
    .msg-user {{ margin-left: 10px !important; font-size: 13px; }}
    .msg-bot  {{ margin-right: 10px !important; font-size: 13px; }}
    [data-testid="stSidebar"] {{ min-width: 200px !important; }}
    .stat-num {{ font-size: 22px; }}
}}

/* ── Dark mode page bg override ── */
{'section[data-testid="stSidebar"] + div {background-color:' + t["page_bg"] + ' !important;}' if st.session_state.dark_mode else ''}

</style>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════
# AUTH PAGE
# ═════════════════════════════════════════════════════════════════
def page_auth():
    inject_css()
    t = get_theme()
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown(f"""
        <div style='text-align:center;padding:24px 0 16px'>
            <div style='font-size:56px'>📚</div>
            <h1 style='font-family:"Baloo 2",cursive;font-size:28px;font-weight:800;
                color:{t["text"]};margin:6px 0 2px'>HomeWork Helper</h1>
            <p style='color:{t["text_muted"]};font-size:13px'>🇵🇰 Pakistan's Smart Study Companion</p>
            <p style='color:{t["text_muted"]};font-size:12px'>Classes 1–8 • O Level • A Level</p>
        </div>""", unsafe_allow_html=True)

        tab_login, tab_signup = st.tabs(["🔑  Login", "✨  Sign Up"])

        with tab_login:
            with st.form("login_form"):
                email    = st.text_input("📧 Email", placeholder="you@example.com")
                password = st.text_input("🔒 Password", type="password")
                if st.form_submit_button("Login →", use_container_width=True, type="primary"):
                    users = load_json(USERS_FILE)
                    if email in users and users[email]["password"] == hash_pw(password):
                        users[email]["last_login"] = datetime.date.today().isoformat()
                        save_json(USERS_FILE, users)
                        st.session_state.logged_in = True
                        st.session_state.user = users[email]
                        st.success("Welcome back! 🎉")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("⚠️ Incorrect email or password.")

        with tab_signup:
            with st.form("signup_form"):
                name    = st.text_input("👤 Full Name", placeholder="Ahmed Khan")
                email2  = st.text_input("📧 Email", placeholder="you@example.com")
                role    = st.selectbox("👥 I am a", ["Student 🎒", "Parent 👨‍👩‍👦"])
                avatar  = st.selectbox("🧑 Choose Avatar", list(AVATARS.keys()))
                grade   = st.selectbox("🏫 Class", ["-- Select --"] + LEVELS)
                pw      = st.text_input("🔒 Password", type="password", placeholder="Min 6 characters")
                pw2     = st.text_input("🔒 Confirm Password", type="password")
                if st.form_submit_button("Create Account →", use_container_width=True, type="primary"):
                    users = load_json(USERS_FILE)
                    if not name or not email2 or not pw:
                        st.error("Please fill all required fields.")
                    elif len(pw) < 6:
                        st.error("Password must be at least 6 characters.")
                    elif pw != pw2:
                        st.error("Passwords don't match.")
                    elif email2 in users:
                        st.error("Email already registered.")
                    else:
                        new_user = {
                            "name": name.strip(), "email": email2.strip(),
                            "password": hash_pw(pw),
                            "role": "student" if "Student" in role else "parent",
                            "avatar": AVATARS[avatar],
                            "grade": grade if grade != "-- Select --" else "",
                            "joined": datetime.date.today().isoformat(),
                            "stats": init_stats(), "badges": []
                        }
                        users[email2] = new_user
                        save_json(USERS_FILE, users)
                        st.session_state.logged_in = True
                        st.session_state.user = new_user
                        st.success("Account created! Welcome aboard 🎉")
                        time.sleep(0.5)
                        st.rerun()

        st.markdown(f"<p style='text-align:center;color:{t['text_muted']};font-size:11px;margin-top:14px'>"
                    "Free to use • Pakistan National Curriculum</p>", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════════
def render_sidebar():
    u = st.session_state.user
    with st.sidebar:
        # ── Dark/Light toggle at top ──
        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.markdown(f"<div style='font-size:11px;font-weight:800;opacity:.6;padding-top:8px'>🌙 Dark Mode</div>",
                        unsafe_allow_html=True)
        with col_b:
            dark = st.toggle("", value=st.session_state.dark_mode, key="dark_toggle",
                             label_visibility="collapsed")
            if dark != st.session_state.dark_mode:
                st.session_state.dark_mode = dark
                st.rerun()

        st.markdown(f"""
        <div style='padding:14px 8px;border-bottom:1px solid rgba(255,255,255,.15);margin-bottom:14px'>
            <div style='font-size:48px;line-height:1;margin-bottom:8px'>{u.get('avatar','👦')}</div>
            <div style='font-weight:800;font-size:15px;color:#FFFFFF'>{u['name']}</div>
            <div style='font-size:11px;color:rgba(255,255,255,0.6);margin-top:2px'>
                {'🎒 Student' if u.get('role')=='student' else '👨‍👩‍👦 Parent'} • {u.get('grade','')}
            </div>
            <div style='display:flex;gap:12px;margin-top:8px;flex-wrap:wrap'>
                <span style='font-size:12px;color:rgba(255,255,255,0.6)'>❓ <b style='color:#FFD700'>{u.get('stats',{}).get('total',0)}</b></span>
                <span style='font-size:12px;color:rgba(255,255,255,0.6)'>🏆 <b style='color:#FFD700'>{len(u.get('badges',[]))}</b></span>
                <span style='font-size:12px;color:rgba(255,255,255,0.6)'>🔥 <b style='color:#FFD700'>{u.get('stats',{}).get('streak',0)}d</b></span>
            </div>
        </div>""", unsafe_allow_html=True)

        nav = [
            ("🏠", "Home",            "home"),
            ("💬", "Chat Tutor",      "chat"),
            ("📄", "Doc Q&A",         "docqa"),
            ("📝", "Practice Quiz",   "quiz"),
            ("🎨", "Image Generator", "image"),
            ("✏️", "Essay Helper",    "essay"),
            ("🔧", "Study Tools",     "tools"),
            ("📊", "My Progress",     "progress"),
            ("🕐", "Chat History",    "history"),
            ("🏆", "Badges",          "badges"),
            ("👤", "Profile",         "profile"),
        ]
        for icon, label, key in nav:
            active = st.session_state.page == key
            if st.button(f"{icon}  {label}", key=f"nav_{key}",
                         use_container_width=True,
                         type="primary" if active else "secondary"):
                st.session_state.page = key
                st.rerun()

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("🚪  Logout", use_container_width=True):
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.rerun()

# ═════════════════════════════════════════════════════════════════
# HOME
# ═════════════════════════════════════════════════════════════════
def page_home():
    t   = get_theme()
    u   = st.session_state.user
    sub = st.session_state.subject
    col = SUBJECTS[sub]["color"]
    h   = datetime.datetime.now().hour
    greet = "Good morning" if h < 12 else "Good afternoon" if h < 17 else "Good evening"

    st.markdown(f"""
    <div style='background:linear-gradient(135deg,{col}dd,{col}88);border-radius:18px;
        padding:20px 22px;margin-bottom:16px;color:#fff'>
        <div style='display:flex;align-items:center;gap:16px'>
            <div style='font-size:54px;line-height:1'>{u.get('avatar','👦')}</div>
            <div>
                <div style='font-family:"Baloo 2",cursive;font-size:22px;font-weight:800'>
                    {greet}, {u['name'].split()[0]}! 👋</div>
                <div style='font-size:13px;opacity:.9;margin-top:3px'>
                    Ready to learn something amazing today? 🚀</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    stats = u.get("stats", {})
    if stats.get("lastDate", "") != datetime.date.today().isoformat():
        st.markdown(f"<div class='reminder'>🔔 <b>Daily Reminder:</b> You haven't studied today! "
                    "Even 15 minutes makes a difference 💪</div>", unsafe_allow_html=True)

    # Word of the Day
    if not st.session_state.wod_loaded:
        with st.spinner("Loading Word of the Day..."):
            grade = u.get("grade", "Class 5")
            raw = call_ai(
                [{"role":"user","content":
                  f"Give ONE interesting English word suitable for {grade} students in Pakistan. "
                  f"Return ONLY this JSON with no extra text: "
                  f'{{\"word\":\"...\",\"urdu\":\"...\",\"meaning\":\"...\",\"example\":\"...\",\"tip\":\"...\"}}'}],
                "You are a vocabulary teacher. Return ONLY valid JSON. No markdown, no explanation."
            )
            try:
                clean = raw.replace("```json","").replace("```","").strip()
                st.session_state.word_of_day = json.loads(clean)
            except:
                st.session_state.word_of_day = {
                    "word": "Perseverance", "urdu": "ثابت قدمی",
                    "meaning": "Continued effort despite difficulties",
                    "example": "Success comes to those with perseverance.",
                    "tip": "Use this word in your next essay!"
                }
            st.session_state.wod_loaded = True

    if st.session_state.word_of_day:
        w = st.session_state.word_of_day
        st.markdown(f"""
        <div class='word-card'>
            <div style='font-size:11px;font-weight:800;opacity:.5;text-transform:uppercase;
                letter-spacing:1px;margin-bottom:8px'>📖 Word of the Day</div>
            <div style='display:flex;align-items:baseline;gap:12px;flex-wrap:wrap'>
                <span style='font-family:"Baloo 2",cursive;font-size:26px;font-weight:800;
                    color:#FFD700'>{w.get('word','')}</span>
                <span style='font-size:13px;opacity:.65'>— {w.get('urdu','')}</span>
            </div>
            <div style='font-size:13px;margin-top:6px;opacity:.9'>{w.get('meaning','')}</div>
            <div style='font-size:12px;margin-top:4px;opacity:.65;font-style:italic'>
                "{w.get('example','')}"</div>
            <div style='font-size:11px;margin-top:8px;background:rgba(255,255,255,.1);
                border-radius:8px;padding:6px 10px'>💡 {w.get('tip','')}</div>
        </div>""", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    for col_obj, ico, val, lbl in [
        (c1, "❓", stats.get("total",0),        "Questions"),
        (c2, "🏆", len(u.get("badges",[])),     "Badges"),
        (c3, "🔥", stats.get("streak",0),       "Day Streak"),
        (c4, "🎨", stats.get("images",0),       "Images Made"),
    ]:
        with col_obj:
            st.markdown(f"<div class='stat-card'><div class='stat-num'>{val}</div>"
                        f"<div class='stat-lbl'>{ico} {lbl}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:{t['text']}'>📚 Start Learning — Choose a Subject</h3>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    for col_obj, (name, info) in zip([c1,c2,c3,c4], SUBJECTS.items()):
        cnt = stats.get(name, 0)
        with col_obj:
            st.markdown(f"""
            <div style='background:{info["color"]}18;border:2px solid {info["color"]};
                border-radius:14px;padding:16px 10px;text-align:center;margin-bottom:8px'>
                <div style='font-size:30px'>{info["emoji"]}</div>
                <div style='font-weight:800;font-size:14px;color:{info["color"]}'>{name}</div>
                <div style='font-size:10px;color:{t["text_muted"]};margin-top:2px'>{cnt} questions</div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"Study {name}", key=f"home_{name}", use_container_width=True):
                st.session_state.subject = name
                st.session_state.page = "chat"
                st.session_state.chat_messages = []
                st.session_state.session_id = None
                st.rerun()

    if u.get("badges"):
        st.markdown(f"<h3 style='color:{t['text']}'>🏆 Recent Badges</h3>", unsafe_allow_html=True)
        cols = st.columns(min(5, len(u["badges"])))
        for i, bid in enumerate(u["badges"][-5:]):
            b = next((x for x in BADGES if x["id"] == bid), None)
            if b:
                with cols[i % 5]:
                    st.markdown(f"<div class='badge-card'><span class='badge-icon'>{b['icon']}</span>"
                                f"<div class='badge-name'>{b['name']}</div></div>", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════
# CHAT TUTOR
# ═════════════════════════════════════════════════════════════════
def build_system(u, sub, lvl):
    return f"""You are Ustad, a warm and encouraging homework tutor for Pakistani students.
Student: {u['name']} | Role: {'Parent' if u.get('role')=='parent' else 'Student'} | Class: {lvl} | Subject: {sub}

Teaching rules:
- Adapt complexity to {lvl}: Class 1-3=very simple+emojis; Class 4-5=simple+examples; Class 6-8=structured steps; O Level=exam-focused; A Level=university depth
{f'- Reply in Urdu script. Use English only for technical terms.' if sub=='Urdu' else ''}
{f'- User is a parent. Explain how to help their child understand the concept.' if u.get('role')=='parent' else ''}
- For Maths/Physics: ALWAYS show step-by-step working
- Use Pakistani curriculum context (FBISE, Cambridge Pakistan, local examples)
- Be warm, positive, and end with encouragement or a follow-up question"""

def save_chat_session(sub, lvl):
    hist  = load_json(HISTORY_FILE)
    email = st.session_state.user["email"]
    if email not in hist:
        hist[email] = []
    sid = st.session_state.session_id or datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.session_id = sid
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    ex = next((s for s in hist[email] if s["id"] == sid), None)
    if ex:
        ex["messages"] = st.session_state.chat_messages
        ex["updated"]  = now
    else:
        hist[email].append({
            "id": sid, "subject": sub, "level": lvl,
            "messages": st.session_state.chat_messages,
            "created": now, "updated": now
        })
    save_json(HISTORY_FILE, hist)

def page_chat():
    t = get_theme()
    u = st.session_state.user
    c1, c2 = st.columns(2)
    with c1:
        sub = st.selectbox("📚 Subject", list(SUBJECTS.keys()),
                           index=list(SUBJECTS.keys()).index(st.session_state.subject))
    with c2:
        lvl_idx = LEVELS.index(u.get("grade","Class 5")) if u.get("grade","") in LEVELS else 4
        lvl = st.selectbox("🏫 Class", LEVELS, index=lvl_idx)
    st.session_state.subject = sub

    if st.button("🆕 New Chat", type="secondary"):
        st.session_state.chat_messages = []
        st.session_state.session_id    = None
        st.rerun()

    st.markdown(f"<div style='font-size:11px;font-weight:800;color:{t['text_muted']};"
                "text-transform:uppercase;letter-spacing:1px;margin:10px 0 6px'>"
                "⚡ Quick Questions</div>", unsafe_allow_html=True)
    qc = st.columns(2)
    for i, p in enumerate(QUICK_PROMPTS.get(sub, [])):
        with qc[i % 2]:
            if st.button(p, key=f"qp{i}", use_container_width=True):
                st.session_state.chat_messages.append({"role":"user","content":p})
                with st.spinner("Ustad is thinking... 🤔"):
                    reply = call_ai(st.session_state.chat_messages, build_system(u, sub, lvl))
                st.session_state.chat_messages.append({"role":"assistant","content":reply})
                bump_stats(sub)
                save_chat_session(sub, lvl)
                st.rerun()

    if not st.session_state.chat_messages:
        st.info(f"👋 Assalam-o-Alaikum {u['name'].split()[0]}! I'm Ustad, your {sub} tutor for {lvl}. Ask me anything!")

    for m in st.session_state.chat_messages:
        if m["role"] == "user":
            st.markdown(f"<div class='msg-lbl msg-lbl-r'>You</div>"
                        f"<div class='msg-user'>{m['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='msg-lbl'>🎓 Ustad</div>"
                        f"<div class='msg-bot'>{m['content']}</div>", unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        ph  = "یہاں سوال لکھیں..." if sub == "Urdu" else f"Ask your {sub} question here..."
        txt = st.text_area("Q", placeholder=ph, height=80, label_visibility="collapsed")
        if st.form_submit_button("📤 Send", use_container_width=True, type="primary") and txt.strip():
            st.session_state.chat_messages.append({"role":"user","content":txt.strip()})
            with st.spinner("Ustad is thinking... 🤔"):
                reply = call_ai(st.session_state.chat_messages, build_system(u, sub, lvl))
            st.session_state.chat_messages.append({"role":"assistant","content":reply})
            bump_stats(sub)
            save_chat_session(sub, lvl)
            st.rerun()

# ═════════════════════════════════════════════════════════════════
# 📄 DOCUMENT Q&A  (NEW FEATURE)
# ═════════════════════════════════════════════════════════════════
def page_docqa():
    t = get_theme()
    u = st.session_state.user

    st.markdown(f"<h3 style='color:{t['text']}'>📄 Document Q&A</h3>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background:{"#1A2A1A" if st.session_state.dark_mode else "#F0FDF4"};
        border:1.5px solid #059669;border-radius:12px;
        padding:12px 16px;margin-bottom:16px;font-size:13px;
        color:{"#6EE7B7" if st.session_state.dark_mode else "#065F46"}'>
        📚 Upload your <b>notes, textbook pages, or past papers</b> and ask any question about them!
        Supports PDF and TXT files.
    </div>""", unsafe_allow_html=True)

    uploaded = st.file_uploader(
        "📎 Upload PDF or TXT file",
        type=["pdf", "txt"],
        help="Max 10MB. Supports PDF and plain text files."
    )

    doc_text = ""

    if uploaded:
        file_size_kb = len(uploaded.getvalue()) / 1024
        st.success(f"✅ File uploaded: **{uploaded.name}** ({file_size_kb:.1f} KB)")

        if uploaded.type == "text/plain":
            doc_text = uploaded.read().decode("utf-8", errors="ignore")
        elif uploaded.type == "application/pdf":
            try:
                import io
                pdf_bytes = uploaded.read()
                # Try to extract text using basic PDF parsing
                text_parts = []
                # Simple extraction: find text between stream markers
                content = pdf_bytes.decode("latin-1", errors="ignore")
                import re
                # Extract readable text portions
                text_chunks = re.findall(r'BT\s*(.*?)\s*ET', content, re.DOTALL)
                for chunk in text_chunks:
                    words = re.findall(r'\((.*?)\)', chunk)
                    if words:
                        text_parts.extend(words)
                doc_text = " ".join(text_parts)
                if len(doc_text.strip()) < 50:
                    # Fallback: extract all readable ASCII sequences
                    doc_text = " ".join(re.findall(r'[A-Za-z0-9\s\.,;:\!\?\'\"]{4,}', content))
                doc_text = doc_text[:12000]
            except Exception as e:
                st.warning(f"⚠️ Could not extract text from PDF: {e}. Try a text file instead.")
                doc_text = ""

        if doc_text.strip():
            st.markdown(f"""
            <div style='background:{t['card']};border:1px solid {t['card_border']};
                border-radius:10px;padding:10px 14px;margin:10px 0;
                font-size:12px;color:{t['text_muted']}'>
                📊 Extracted <b style='color:{t["text"]}'>{len(doc_text):,}</b> characters from document
            </div>""", unsafe_allow_html=True)

            with st.expander("👁️ Preview extracted text"):
                st.text(doc_text[:500] + ("..." if len(doc_text) > 500 else ""))

            # Action buttons
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("📋 Summarize Document", use_container_width=True, type="primary"):
                    with st.spinner("Reading document..."):
                        result = call_ai_with_doc(
                            [{"role":"user","content":"Please summarize this document clearly. List the main topics and key points."}],
                            build_system(u, "English", u.get("grade","Class 5")),
                            doc_text
                        )
                    st.session_state["doc_result"] = result
                    # update stats
                    users = load_json(USERS_FILE)
                    eu = users.get(u["email"], u)
                    eu.setdefault("stats", init_stats())
                    eu["stats"]["docs"] = eu["stats"].get("docs", 0) + 1
                    eu, new_b = check_badges(eu)
                    users[u["email"]] = eu
                    save_json(USERS_FILE, users)
                    st.session_state.user = eu
                    st.rerun()

            with c2:
                if st.button("❓ Generate Quiz from Doc", use_container_width=True):
                    with st.spinner("Creating quiz..."):
                        raw = call_ai_with_doc(
                            [{"role":"user","content":
                              'Create 5 multiple choice questions from this document. '
                              'Return ONLY this JSON: {"questions":[{"q":"...","options":["A. ...","B. ...","C. ...","D. ..."],"answer":"A. ...","explanation":"..."}]}'}],
                            "Quiz generator. Return ONLY valid JSON.",
                            doc_text, 1500
                        )
                        try:
                            clean = raw.replace("```json","").replace("```","").strip()
                            data = json.loads(clean)
                            st.session_state.quiz = {
                                "questions": data["questions"],
                                "current": 0, "score": 0,
                                "answers": [], "done": False,
                                "sub": "English", "lvl": u.get("grade","Class 5")
                            }
                            st.session_state.page = "quiz"
                            st.rerun()
                        except:
                            st.error("Could not generate quiz. Try again.")

            with c3:
                if st.button("🔑 Extract Key Points", use_container_width=True):
                    with st.spinner("Extracting..."):
                        result = call_ai_with_doc(
                            [{"role":"user","content":"List all the important key points, definitions, and formulas from this document. Use bullet points."}],
                            build_system(u, "English", u.get("grade","Class 5")),
                            doc_text
                        )
                    st.session_state["doc_result"] = result
                    st.rerun()

            # Custom Q&A
            st.markdown(f"<div style='margin-top:16px;font-weight:800;color:{t['text']}'>💬 Ask a Question About This Document</div>",
                        unsafe_allow_html=True)
            with st.form("doc_qa_form", clear_on_submit=True):
                doc_q = st.text_area("Your question", placeholder="e.g. What is the main topic? Explain the formula on page 2...",
                                     height=80, label_visibility="collapsed")
                if st.form_submit_button("🔍 Ask", use_container_width=True, type="primary") and doc_q.strip():
                    with st.spinner("Analyzing document..."):
                        result = call_ai_with_doc(
                            [{"role":"user","content":doc_q}],
                            build_system(u, "English", u.get("grade","Class 5")),
                            doc_text
                        )
                    st.session_state["doc_result"] = result
                    st.rerun()

        else:
            st.warning("⚠️ Could not extract readable text from this file. Please try a .txt file or a text-based PDF.")

    # Show result
    if st.session_state.get("doc_result"):
        st.markdown(f"""
        <div style='background:{t["card"]};border-radius:16px;padding:20px 22px;
            box-shadow:0 2px 16px rgba(0,0,0,0.06);
            border-left:4px solid #059669;margin-top:12px;color:{t["text"]}'>
            <div style='font-weight:800;font-size:13px;color:#059669;margin-bottom:10px'>🤖 Ustad's Answer</div>
            <div style='font-size:14px;line-height:1.8;white-space:pre-wrap'>{st.session_state["doc_result"]}</div>
        </div>""", unsafe_allow_html=True)
        if st.button("🗑️ Clear Answer"):
            st.session_state["doc_result"] = ""
            st.rerun()

    if not uploaded:
        st.markdown(f"""
        <div style='text-align:center;padding:40px 20px;color:{t["text_muted"]}'>
            <div style='font-size:48px'>📄</div>
            <div style='font-size:15px;font-weight:700;margin-top:12px'>Upload a Document to Get Started</div>
            <div style='font-size:13px;margin-top:8px'>Support for PDF and TXT files</div>
            <div style='font-size:12px;margin-top:16px;opacity:.6'>
                📌 Tips: Upload textbook chapters, notes, or past papers<br>
                Then summarize, quiz yourself, or ask questions!
            </div>
        </div>""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════
# QUIZ
# ═════════════════════════════════════════════════════════════════
def page_quiz():
    t = get_theme()
    u = st.session_state.user
    c1, c2 = st.columns(2)
    with c1:
        sub = st.selectbox("📚 Subject", list(SUBJECTS.keys()), key="quiz_sub")
    with c2:
        lvl_idx = LEVELS.index(u.get("grade","Class 5")) if u.get("grade","") in LEVELS else 4
        lvl = st.selectbox("🏫 Class", LEVELS, index=lvl_idx, key="quiz_lvl")

    q = st.session_state.quiz

    if q is None:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Generate 5-Question Quiz", use_container_width=True, type="primary"):
            with st.spinner("✨ Generating your quiz..."):
                raw = call_ai(
                    [{"role":"user","content":
                      f"Create exactly 5 multiple choice questions for {lvl} {sub} students in Pakistan. "
                      f"Return ONLY this raw JSON with no markdown: "
                      f'{{\"questions\":[{{\"q\":\"question text\",\"options\":[\"A. option\",\"B. option\",\"C. option\",\"D. option\"],\"answer\":\"A. option\",\"explanation\":\"why\"}}]}}'}],
                    "Quiz generator. Return ONLY valid raw JSON. No backticks. No markdown.", 1200
                )
                try:
                    clean = raw.replace("```json","").replace("```","").strip()
                    data = json.loads(clean)
                    st.session_state.quiz = {
                        "questions": data["questions"],
                        "current": 0, "score": 0,
                        "answers": [], "done": False,
                        "sub": sub, "lvl": lvl
                    }
                    st.rerun()
                except:
                    st.error("⚠️ Could not generate quiz. Please try again.")
        return

    info = SUBJECTS[q["sub"]]

    if q["done"]:
        total = len(q["questions"]); score = q["score"]
        pct   = int((score / total) * 100)
        emoji = "🏆" if pct >= 80 else "👍" if pct >= 60 else "💪"
        st.markdown(f"""
        <div style='text-align:center;background:{t["card"]};border-radius:20px;padding:30px;
            box-shadow:0 2px 16px rgba(0,0,0,0.06);margin-bottom:16px'>
            <div style='font-size:56px'>{emoji}</div>
            <h2 style='font-family:"Baloo 2",cursive;font-size:26px;font-weight:800;color:{t["text"]}'>
                Quiz Complete!</h2>
            <div style='font-size:44px;font-weight:900;color:{info["color"]};margin:8px 0'>
                {score}/{total}</div>
            <div style='font-size:15px;color:{t["text_muted"]}'>
                {pct}% — {"Excellent! ⭐" if pct>=80 else "Good effort! 📚" if pct>=60 else "Keep practicing! 💪"}
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"<h3 style='color:{t['text']}'>📋 Review Answers</h3>", unsafe_allow_html=True)
        for i, (ques, ans) in enumerate(zip(q["questions"], q["answers"])):
            correct = ans["chosen"] == ques["answer"]
            bg     = ("#0D2A0D" if st.session_state.dark_mode else "#F0FDF4") if correct else ("#2A0D0D" if st.session_state.dark_mode else "#FFF1EE")
            border = "#059669" if correct else "#E8472A"
            wrong_line = "" if correct else f'<div style="font-size:13px;color:#059669;margin-top:2px">✅ Correct: <b>{ques["answer"]}</b></div>'
            st.markdown(f"""
            <div style='background:{bg};border:1.5px solid {border};border-radius:12px;
                padding:14px 16px;margin-bottom:10px;color:{t["text"]}'>
                <div style='font-weight:700;font-size:14px'>Q{i+1}. {ques["q"]}</div>
                <div style='font-size:13px;margin-top:5px'>
                    Your answer: <b>{ans["chosen"]}</b> {"✅" if correct else "❌"}
                </div>
                {wrong_line}
                <div style='font-size:12px;color:{t["text_muted"]};margin-top:4px'>
                    💡 {ques.get("explanation","")}
                </div>
            </div>""", unsafe_allow_html=True)

        if st.button("🔄 Try Another Quiz", use_container_width=True, type="primary"):
            st.session_state.quiz = None
            st.rerun()
        return

    current = q["current"]
    ques    = q["questions"][current]
    pct_bar = int((current / len(q["questions"])) * 100)

    st.markdown(f"""
    <div style='display:flex;justify-content:space-between;font-size:13px;font-weight:700;
        color:{t["text_muted"]};margin-bottom:6px'>
        <span>Question {current+1} of {len(q["questions"])}</span>
        <span style='color:{info["color"]}'>Score: {q["score"]}/{current}</span>
    </div>
    <div class='prog-bar'>
        <div class='prog-fill' style='width:{pct_bar}%;background:{info["color"]}'></div>
    </div>
    <div style='background:{t["card"]};border-radius:16px;padding:18px 20px;margin:12px 0;
        box-shadow:0 2px 16px rgba(0,0,0,0.06);font-weight:800;font-size:15px;
        color:{t["text"]};line-height:1.5'>
        Q{current+1}. {ques["q"]}
    </div>""", unsafe_allow_html=True)

    for opt in ques["options"]:
        if st.button(opt, key=f"opt_{current}_{opt}", use_container_width=True):
            q["answers"].append({"chosen": opt})
            if opt == ques["answer"]:
                q["score"] += 1
                st.toast("✅ Correct!", icon="🎉")
            else:
                st.toast(f"❌ Correct answer: {ques['answer']}", icon="💡")
            q["current"] += 1
            if q["current"] >= len(q["questions"]):
                q["done"] = True
            st.session_state.quiz = q
            st.rerun()

# ═════════════════════════════════════════════════════════════════
# IMAGE GENERATOR
# ═════════════════════════════════════════════════════════════════
def page_image():
    t = get_theme()
    u = st.session_state.user
    st.markdown(f"<h3 style='color:{t['text']}'>🎨 Educational Image Generator</h3>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        img_sub = st.selectbox("📚 Subject", list(SUBJECTS.keys()), key="img_sub")
    with c2:
        lvl_idx = LEVELS.index(u.get("grade","Class 5")) if u.get("grade","") in LEVELS else 4
        img_lvl = st.selectbox("🏫 Class", LEVELS, index=lvl_idx, key="img_lvl")

    style_choice = st.selectbox("🎨 Diagram Style", list(IMAGE_STYLES.keys()))
    style_hint   = IMAGE_STYLES[style_choice]

    prompt = st.text_area(
        "📝 Describe what you want to see",
        placeholder=(
            "e.g.  Diagram showing how photosynthesis works with labeled parts\n"
            "e.g.  Solar system with all 8 planets in order\n"
            "e.g.  Water cycle showing evaporation, clouds and rain"
        ),
        height=110
    )

    if st.button("🎨  Generate Image", use_container_width=True, type="primary"):
        if not prompt.strip():
            st.warning("Please enter a description first!")
            return

        with st.spinner("🎨 Claude AI is creating your educational diagram... (20-30 seconds)"):
            system_msg = (
                "You are an expert SVG illustrator who creates educational diagrams for Pakistani school students. "
                "STRICT OUTPUT RULES:\n"
                "1. Output ONLY the SVG code. No markdown. No backticks. No explanations.\n"
                "2. Start your response with exactly: <svg\n"
                "3. End your response with exactly: </svg>\n"
                "4. Use: xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 700 500\" width=\"700\" height=\"500\"\n"
                "5. Include a <defs> block with at least 3 linearGradient definitions.\n"
                "6. Add a bold title at the top.\n"
                "7. Use BRIGHT colors and gradient fills.\n"
                "8. Include at least 20 visual elements.\n"
                "9. Every component must have a clear text label.\n"
                "10. DO NOT use any xlink:href or external images."
            )
            user_msg = (
                f"Create a detailed colorful educational SVG illustration:\n"
                f"TOPIC: {prompt}\nSUBJECT: {img_sub}\nLEVEL: {img_lvl}\nSTYLE: {style_hint}\n\n"
                f"Output ONLY the SVG. Start with <svg and end with </svg>."
            )
            raw = call_ai_svg([{"role":"user","content":user_msg}], system_msg)

        cleaned = raw
        for fence in ["```svg", "```xml", "```html", "```"]:
            cleaned = cleaned.replace(fence, "")
        cleaned = cleaned.strip()
        svg_start = cleaned.find("<svg")
        svg_end   = cleaned.rfind("</svg>")

        if svg_start >= 0 and svg_end >= 0:
            final_svg = cleaned[svg_start : svg_end + 6]
            st.success("✅ Image generated successfully!")
            st.components.v1.html(final_svg, height=520, scrolling=False)
            b64 = base64.b64encode(final_svg.encode()).decode()
            st.markdown(
                f'<a href="data:image/svg+xml;base64,{b64}" download="hw_diagram.svg" '
                f'style="display:inline-block;padding:10px 20px;background:#7C3AED;color:#fff;'
                f'border-radius:12px;font-weight:700;font-size:14px;text-decoration:none;margin-top:8px">'
                f'⬇️ Download SVG Image</a>',
                unsafe_allow_html=True
            )
            imgs  = load_json(IMAGES_FILE)
            email = u["email"]
            if email not in imgs:
                imgs[email] = []
            imgs[email].insert(0, {
                "id": str(int(time.time())), "svg": final_svg,
                "prompt": prompt, "subject": img_sub,
                "level": img_lvl, "style": style_choice,
                "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            save_json(IMAGES_FILE, imgs)
            users = load_json(USERS_FILE)
            eu    = users.get(u["email"], u)
            eu.setdefault("stats", init_stats())
            eu["stats"]["images"] = eu["stats"].get("images", 0) + 1
            eu, new_b = check_badges(eu)
            users[u["email"]] = eu
            save_json(USERS_FILE, users)
            st.session_state.user = eu
            for b in new_b:
                st.toast(f"🏆 Badge: {b['icon']} {b['name']}!", icon="🎉")
        else:
            st.error("⚠️ Could not generate image. Please rephrase your description and try again.")

    imgs      = load_json(IMAGES_FILE)
    user_imgs = imgs.get(u["email"], [])
    if user_imgs:
        st.markdown("---")
        st.markdown(f"<h3 style='color:{t['text']}'>🖼️ Your Image Gallery</h3>", unsafe_allow_html=True)
        for img in user_imgs[:8]:
            label = f"🎨 {img['subject']} — {img['prompt'][:55]}... | {img['created']}"
            with st.expander(label):
                st.components.v1.html(img["svg"], height=520, scrolling=False)
                b64 = base64.b64encode(img["svg"].encode()).decode()
                st.markdown(
                    f'<a href="data:image/svg+xml;base64,{b64}" download="hw_diagram.svg" '
                    f'style="display:inline-block;padding:7px 16px;background:#7C3AED;color:#fff;'
                    f'border-radius:10px;font-weight:700;font-size:12px;text-decoration:none">⬇️ Download</a>',
                    unsafe_allow_html=True
                )

# ═════════════════════════════════════════════════════════════════
# ESSAY HELPER
# ═════════════════════════════════════════════════════════════════
def page_essay():
    t = get_theme()
    u = st.session_state.user
    st.markdown(f"<h3 style='color:{t['text']}'>✏️ Essay & Writing Helper</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        etype = st.selectbox("📄 Writing Type", ESSAY_TYPES)
    with c2:
        lvl_idx = LEVELS.index(u.get("grade","Class 5")) if u.get("grade","") in LEVELS else 4
        lvl = st.selectbox("🏫 Class", LEVELS, index=lvl_idx, key="essay_lvl")

    topic = st.text_input("📝 Topic / Title", placeholder="e.g. My School, Climate Change, My Best Friend...")

    if st.button("✏️ Generate Essay", use_container_width=True, type="primary"):
        if not topic.strip():
            st.warning("Please enter a topic first!")
            return
        with st.spinner("✏️ Writing your essay..."):
            result = call_ai(
                [{"role":"user","content":
                  f"Write a complete {etype} about '{topic}' for a {lvl} student in Pakistan. "
                  f"Include proper structure: introduction, body paragraphs, and conclusion. "
                  f"Use simple age-appropriate language for {lvl}."}],
                "Expert writing teacher for Pakistani students. Write well-structured, complete essays.",
                1800
            )
        st.session_state.essay_result = result
        users = load_json(USERS_FILE)
        eu = users.get(u["email"], u)
        eu.setdefault("stats", init_stats())
        eu["stats"]["essays"] = eu["stats"].get("essays", 0) + 1
        eu, new_b = check_badges(eu)
        users[u["email"]] = eu
        save_json(USERS_FILE, users)
        st.session_state.user = eu
        for b in new_b:
            st.toast(f"🏆 Badge: {b['icon']} {b['name']}!", icon="🎉")

    if st.session_state.essay_result:
        st.markdown(f"""
        <div style='background:{t["card"]};border-radius:16px;padding:20px 22px;
            box-shadow:0 2px 16px rgba(0,0,0,0.06);border-top:4px solid #059669;margin-top:12px;color:{t["text"]}'>
            <div style='font-weight:800;font-size:14px;color:#059669;margin-bottom:12px'>
                ✏️ {etype}: {topic}</div>
            <div style='font-size:14px;line-height:1.85;white-space:pre-wrap'>
                {st.session_state.essay_result}</div>
            <div style='margin-top:14px;padding:10px 12px;background:{"#0D2A0D" if st.session_state.dark_mode else "#EDFAF5"};
                border-radius:10px;font-size:12px;color:{"#6EE7B7" if st.session_state.dark_mode else "#065F46"}'>
                💡 Use this as a learning example — try writing your own version!
            </div>
        </div>""", unsafe_allow_html=True)
        if st.button("📋 Copy Essay"):
            st.code(st.session_state.essay_result, language=None)

# ═════════════════════════════════════════════════════════════════
# STUDY TOOLS
# ═════════════════════════════════════════════════════════════════
def page_tools():
    t = get_theme()
    st.markdown(f"<h3 style='color:{t['text']}'>🔧 Study Tools</h3>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🌐 Language Translator", "⏱️ Pomodoro Timer"])

    with t1:
        st.markdown(f"<h4 style='color:{t['text']}'>🌐 Language Translator</h4>", unsafe_allow_html=True)
        lang = st.selectbox("Translate to", ["Urdu","English","Punjabi","Sindhi","Pashto"])
        text = st.text_area("Enter text to translate", height=100,
                            placeholder="Type English or Urdu text here...")
        if st.button("🌐 Translate", use_container_width=True, type="primary"):
            if not text.strip():
                st.warning("Enter some text first!")
            else:
                with st.spinner("Translating..."):
                    result = call_ai(
                        [{"role":"user","content":
                          f"Translate the following text to {lang}:\n\n{text}\n\n"
                          f"Also explain any difficult words."}],
                        "Translation assistant for Pakistani school students."
                    )
                st.session_state.trans_result = result
        if st.session_state.trans_result:
            st.markdown(f"""
            <div style='background:{t["card"]};border-radius:12px;padding:16px;
                font-size:14px;line-height:1.75;white-space:pre-wrap;margin-top:10px;color:{t["text"]}'>
                {st.session_state.trans_result}
            </div>""", unsafe_allow_html=True)

    with t2:
        st.markdown(f"<h4 style='color:{t['text']}'>⏱️ Pomodoro Study Timer</h4>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("📚 Study Session", "25 min")
        with c2: st.metric("☕ Short Break",    "5 min")
        with c3: st.metric("🌟 Long Break",     "15 min")
        st.info("⏱️ Set your phone timer and follow the schedule below:")
        for i in range(1, 5):
            brk = "☕ 5 min break" if i < 4 else "🌟 15 min long break — you deserve it!"
            st.markdown(f"- 🍅 **Session {i}:** 25 min study → {brk}")

# ═════════════════════════════════════════════════════════════════
# PROGRESS
# ═════════════════════════════════════════════════════════════════
def page_progress():
    t     = get_theme()
    u     = st.session_state.user
    stats = u.get("stats", {})
    total = stats.get("total", 0)

    st.markdown(f"<h3 style='color:{t['text']}'>📊 My Progress</h3>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("❓ Questions",   total)
    with c2: st.metric("🏆 Badges",      len(u.get("badges",[])))
    with c3: st.metric("🔥 Streak",      f"{stats.get('streak',0)} days")
    with c4: st.metric("📅 Member Since", u.get("joined",""))

    st.markdown(f"<h3 style='color:{t['text']}'>📚 Questions Per Subject</h3>", unsafe_allow_html=True)
    for name, info in SUBJECTS.items():
        cnt = stats.get(name, 0)
        pct = int((cnt / max(total, 1)) * 100)
        st.markdown(f"""
        <div style='margin-bottom:14px'>
            <div style='display:flex;justify-content:space-between;font-size:13px;
                font-weight:700;margin-bottom:5px;color:{t["text"]}'>
                <span>{info['emoji']} {name}</span>
                <span style='color:{info["color"]}'>{cnt} questions ({pct}%)</span>
            </div>
            <div class='prog-bar'>
                <div class='prog-fill' style='width:{pct}%;background:{info["color"]}'></div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown(f"<h3 style='color:{t['text']}'>🛠️ Activity Summary</h3>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("🎨 Images",  stats.get("images", 0))
    with c2: st.metric("✏️ Essays",  stats.get("essays", 0))
    with c3: st.metric("📄 Docs",    stats.get("docs", 0))
    with c4: st.metric("📖 Subjects", sum(1 for s in ["Maths","Physics","English","Urdu"] if stats.get(s,0)>0))

# ═════════════════════════════════════════════════════════════════
# HISTORY
# ═════════════════════════════════════════════════════════════════
def page_history():
    t = get_theme()
    u = st.session_state.user
    st.markdown(f"<h3 style='color:{t['text']}'>🕐 Chat History</h3>", unsafe_allow_html=True)
    hist     = load_json(HISTORY_FILE)
    sessions = sorted(hist.get(u["email"], []),
                      key=lambda x: x.get("updated",""), reverse=True)
    if not sessions:
        st.info("📭 No chat history yet. Start a conversation with Ustad!")
        return
    for sess in sessions:
        info   = SUBJECTS.get(sess.get("subject",""), {"emoji":"📚","color":"#666"})
        msgs   = sess.get("messages", [])
        label  = (f"{info['emoji']} {sess.get('subject','')} — {sess.get('level','')} | "
                  f"{sess.get('updated','')} ({len(msgs)} msgs)")
        with st.expander(label):
            for m in msgs:
                if m["role"] == "user":
                    st.markdown(f"<div class='msg-user' style='margin-left:40px'>{m['content']}</div>",
                                unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='msg-bot' style='margin-right:40px'>{m['content']}</div>",
                                unsafe_allow_html=True)
            if st.button("🔄 Continue this chat", key=f"cont_{sess['id']}"):
                st.session_state.chat_messages = msgs
                st.session_state.session_id    = sess["id"]
                st.session_state.subject       = sess.get("subject","Maths")
                st.session_state.page          = "chat"
                st.rerun()

# ═════════════════════════════════════════════════════════════════
# BADGES
# ═════════════════════════════════════════════════════════════════
def page_badges():
    t      = get_theme()
    u      = st.session_state.user
    earned = u.get("badges", [])
    st.markdown(f"<h3 style='color:{t['text']}'>🏆 Badges & Achievements</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:{t['text_muted']};font-size:13px'>Earned "
                f"<b style='color:{t['text']}'>{len(earned)}</b> of "
                f"<b style='color:{t['text']}'>{len(BADGES)}</b> badges</p>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i, b in enumerate(BADGES):
        is_earned = b["id"] in earned
        with cols[i % 3]:
            locked = "" if is_earned else "badge-locked"
            status_color = "#059669" if is_earned else "#aaa"
            status_text  = "✅ Earned!" if is_earned else "🔒 Locked"
            st.markdown(f"""
            <div class='badge-card {locked}' style='margin-bottom:12px'>
                <span class='badge-icon'>{b['icon']}</span>
                <div class='badge-name'>{b['name']}</div>
                <div class='badge-desc'>{b['desc']}</div>
                <div style='font-size:11px;margin-top:5px;color:{status_color};font-weight:700'>
                    {status_text}</div>
            </div>""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════
# PROFILE
# ═════════════════════════════════════════════════════════════════
def page_profile():
    t = get_theme()
    u = st.session_state.user
    st.markdown(f"<h3 style='color:{t['text']}'>👤 My Profile</h3>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f"<div style='font-size:80px;text-align:center;background:{t['card']};"
                    f"border-radius:20px;padding:20px'>{u.get('avatar','👦')}</div>",
                    unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style='padding:10px 0'>
            <div style='font-family:"Baloo 2",cursive;font-size:22px;font-weight:800;color:{t["text"]}'>
                {u['name']}</div>
            <div style='font-size:13px;color:{t["text_muted"]};margin-top:4px'>
                {'🎒 Student' if u.get('role')=='student' else '👨‍👩‍👦 Parent'} • {u.get('grade','')}
            </div>
            <div style='font-size:12px;color:{t["text_muted"]};margin-top:2px'>📧 {u['email']}</div>
            <div style='font-size:12px;color:{t["text_muted"]};margin-top:2px'>📅 Joined {u.get('joined','')}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(f"<h4 style='color:{t['text']}'>✏️ Update Profile</h4>", unsafe_allow_html=True)
    with st.form("profile_form"):
        new_name   = st.text_input("Full Name", value=u.get("name",""))
        new_grade  = st.selectbox("Default Class", ["-- Select --"] + LEVELS,
                                  index=LEVELS.index(u["grade"])+1 if u.get("grade","") in LEVELS else 0)
        cur_av_key = next((k for k,v in AVATARS.items() if v == u.get("avatar","👦")), list(AVATARS.keys())[0])
        new_avatar = st.selectbox("Avatar", list(AVATARS.keys()),
                                  index=list(AVATARS.keys()).index(cur_av_key))
        st.markdown(f"<h4 style='color:{t['text']}'>🔒 Change Password</h4>", unsafe_allow_html=True)
        old_pw = st.text_input("Current Password", type="password")
        new_pw = st.text_input("New Password", type="password", placeholder="Leave blank to keep current")
        cnf_pw = st.text_input("Confirm New Password", type="password")
        if st.form_submit_button("💾 Save Changes", type="primary"):
            users = load_json(USERS_FILE)
            eu    = users[u["email"]]
            if old_pw and eu["password"] != hash_pw(old_pw):
                st.error("Current password is incorrect.")
            elif new_pw and new_pw != cnf_pw:
                st.error("New passwords don't match.")
            elif new_pw and len(new_pw) < 6:
                st.error("New password must be at least 6 characters.")
            else:
                if new_name.strip():    eu["name"]   = new_name.strip()
                if new_grade != "-- Select --": eu["grade"] = new_grade
                eu["avatar"] = AVATARS[new_avatar]
                if new_pw:              eu["password"] = hash_pw(new_pw)
                users[u["email"]] = eu
                save_json(USERS_FILE, users)
                st.session_state.user = eu
                st.success("✅ Profile updated!")
                time.sleep(0.5)
                st.rerun()

    st.markdown("---")
    st.markdown(f"<h4 style='color:{t['text']}'>🗑️ Danger Zone</h4>", unsafe_allow_html=True)
    if st.button("🗑️ Clear All My Chat History"):
        hist = load_json(HISTORY_FILE)
        hist[u["email"]] = []
        save_json(HISTORY_FILE, hist)
        st.success("Chat history cleared.")

# ═════════════════════════════════════════════════════════════════
# ROUTER
# ═════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    page_auth()
else:
    inject_css()
    render_sidebar()
    p = st.session_state.page
    if   p == "home":     page_home()
    elif p == "chat":     page_chat()
    elif p == "docqa":    page_docqa()
    elif p == "quiz":     page_quiz()
    elif p == "image":    page_image()
    elif p == "essay":    page_essay()
    elif p == "tools":    page_tools()
    elif p == "progress": page_progress()
    elif p == "history":  page_history()
    elif p == "badges":   page_badges()
    elif p == "profile":  page_profile()
