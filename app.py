import streamlit as st
import json, hashlib, datetime, time, os, base64
from anthropic import Anthropic
from curriculum import CAMBRIDGE_CURRICULUM

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
            "streak":0,"lastDate":"","images":0,"essays":0}

# ─────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────
defaults = {
    "logged_in": False, "user": None, "page": "home",
    "subject": "Maths", "level": "Class 5",
    "chat_messages": [], "session_id": None,
    "quiz": None, "essay_result": "",
    "trans_result": "", "word_of_day": None, "wod_loaded": False,
    "syl_subject": "Maths", "syl_unit": None,
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

def call_ai_svg(messages, system):
    """Use a higher token limit for SVG generation"""
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
# CSS
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Baloo+2:wght@600;700;800&display=swap');
html,body,[class*="css"]{ font-family:'Nunito',sans-serif !important; }
.main .block-container{ padding-top:1rem; padding-bottom:2rem; max-width:900px; }
#MainMenu,footer,header{ visibility:hidden; }
.msg-user{ background:linear-gradient(135deg,#E8472A,#C1391F); color:#fff;
  border-radius:18px 18px 4px 18px; padding:12px 16px;
  margin:4px 0 4px 60px; font-size:14px; line-height:1.65; }
.msg-bot{ background:#fff; color:#1A1A2E;
  border-radius:18px 18px 18px 4px; padding:12px 16px;
  margin:4px 60px 4px 0; font-size:14px; line-height:1.7;
  box-shadow:0 2px 10px rgba(0,0,0,0.07); border:1px solid #F0F0F5; }
.msg-lbl{ font-size:11px; color:#bbb; margin-bottom:2px; }
.msg-lbl-r{ text-align:right; }
.stat-card{ background:#fff; border-radius:14px; padding:16px; text-align:center;
  box-shadow:0 2px 10px rgba(0,0,0,0.05); border:1px solid #F0F0F5; }
.stat-num{ font-size:28px; font-weight:900; color:#1A1A2E; }
.stat-lbl{ font-size:11px; color:#999; margin-top:3px; }
.badge-card{ background:linear-gradient(135deg,#FFF8E7,#FFFBF0);
  border:1.5px solid #F5CC4A; border-radius:12px; padding:12px 10px; text-align:center; }
.badge-locked{ opacity:0.35; filter:grayscale(1); }
.badge-icon{ font-size:28px; display:block; }
.badge-name{ font-size:12px; font-weight:800; color:#A07820; margin-top:4px; }
.badge-desc{ font-size:10px; color:#bbb; margin-top:2px; }
.prog-bar{ background:#F0F0F5; border-radius:99px; height:10px; overflow:hidden; margin-bottom:4px; }
.prog-fill{ height:100%; border-radius:99px; transition:width .4s; }
.word-card{ background:linear-gradient(135deg,#1A1A2E,#2D2D4A);
  border-radius:16px; padding:18px 20px; margin-bottom:14px; color:#fff; }
.reminder{ background:#FFFBF0; border:1.5px solid #F5CC4A;
  border-radius:12px; padding:12px 16px; margin-bottom:14px; font-size:13px; }
.hist-card{ background:#fff; border-radius:14px; padding:14px 16px;
  box-shadow:0 2px 10px rgba(0,0,0,0.05); border:1px solid #F0F0F5; margin-bottom:10px; }
[data-testid="stSidebar"]{ background:#0F0F1A !important; }
[data-testid="stSidebar"] *{ color:#fff !important; }
.stButton>button{ border-radius:12px !important;
  font-family:'Nunito',sans-serif !important; font-weight:700 !important; }
.stTextInput>div>div>input,
.stSelectbox>div>div>div,
.stTextArea>div>div>textarea{ border-radius:10px !important; font-family:'Nunito',sans-serif !important; }
div[data-testid="column"]{ padding:4px !important; }
</style>
""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════
# AUTH PAGE
# ═════════════════════════════════════════════════════════════════
def page_auth():
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown("""
        <div style='text-align:center;padding:24px 0 16px'>
            <div style='font-size:56px'>📚</div>
            <h1 style='font-family:"Baloo 2",cursive;font-size:28px;font-weight:800;
                color:#0F0F1A;margin:6px 0 2px'>HomeWork Helper</h1>
            <p style='color:#999;font-size:13px'>🇵🇰 Pakistan's Smart Study Companion</p>
            <p style='color:#bbb;font-size:12px'>Classes 1–8 • O Level • A Level</p>
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

        st.markdown("<p style='text-align:center;color:#ccc;font-size:11px;margin-top:14px'>"
                    "Free to use • Pakistan National Curriculum</p>", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════
# SIDEBAR
# ═════════════════════════════════════════════════════════════════
def render_sidebar():
    u = st.session_state.user
    with st.sidebar:
        st.markdown(f"""
        <div style='padding:14px 8px;border-bottom:1px solid rgba(255,255,255,.12);margin-bottom:14px'>
            <div style='font-size:48px;line-height:1;margin-bottom:8px'>{u.get('avatar','👦')}</div>
            <div style='font-weight:800;font-size:15px'>{u['name']}</div>
            <div style='font-size:11px;opacity:.55;margin-top:2px'>
                {'🎒 Student' if u.get('role')=='student' else '👨‍👩‍👦 Parent'} • {u.get('grade','')}
            </div>
            <div style='display:flex;gap:12px;margin-top:8px;flex-wrap:wrap'>
                <span style='font-size:11px;opacity:.6'>❓ <b style='color:#fff'>{u.get('stats',{}).get('total',0)}</b></span>
                <span style='font-size:11px;opacity:.6'>🏆 <b style='color:#fff'>{len(u.get('badges',[]))}</b></span>
                <span style='font-size:11px;opacity:.6'>🔥 <b style='color:#fff'>{u.get('stats',{}).get('streak',0)}d</b></span>
            </div>
        </div>""", unsafe_allow_html=True)

        nav = [
            ("🏠", "Home",            "home"),
            ("💬", "Chat Tutor",      "chat"),
            ("📚", "My Syllabus",     "syllabus"),
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
        st.markdown("<div class='reminder'>🔔 <b>Daily Reminder:</b> You haven't studied today! "
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

    # Stats row
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
    st.markdown("### 📚 Start Learning — Choose a Subject")
    c1, c2, c3, c4 = st.columns(4)
    for col_obj, (name, info) in zip([c1,c2,c3,c4], SUBJECTS.items()):
        cnt = stats.get(name, 0)
        with col_obj:
            st.markdown(f"""
            <div style='background:{info["color"]}18;border:2px solid {info["color"]};
                border-radius:14px;padding:16px 10px;text-align:center;margin-bottom:8px'>
                <div style='font-size:30px'>{info["emoji"]}</div>
                <div style='font-weight:800;font-size:14px;color:{info["color"]}'>{name}</div>
                <div style='font-size:10px;color:#aaa;margin-top:2px'>{cnt} questions</div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"Study {name}", key=f"home_{name}", use_container_width=True):
                st.session_state.subject = name
                st.session_state.page = "chat"
                st.session_state.chat_messages = []
                st.session_state.session_id = None
                st.rerun()

    # Syllabus progress teaser
    st.markdown("### 📚 Syllabus Progress")
    grade = u.get("grade","Class 5")
    studied_topics = u.get("studied_topics", {})
    sub_cols = st.columns(4)
    for col_obj, (sname, sinfo) in zip(sub_cols, SUBJECTS.items()):
        curr_data  = CAMBRIDGE_CURRICULUM.get(sname,{}).get(grade,{})
        units_data = curr_data.get("units",[])
        total_t    = sum(len(un["topics"]) for un in units_data)
        key        = f"{sname}_{grade}"
        done_t     = len(studied_topics.get(key,[]))
        pct        = int((done_t/max(total_t,1))*100)
        with col_obj:
            st.markdown(f"""
            <div style='background:{sinfo["color"]}12;border:2px solid {sinfo["color"]}55;
                border-radius:14px;padding:14px 10px;text-align:center;cursor:pointer'>
                <div style='font-size:26px'>{sinfo["emoji"]}</div>
                <div style='font-weight:800;font-size:13px;color:{sinfo["color"]}'>{sname}</div>
                <div class='prog-bar' style='margin:8px 0 4px'>
                    <div class='prog-fill' style='width:{pct}%;background:{sinfo["color"]}'></div>
                </div>
                <div style='font-size:10px;color:#aaa'>{done_t}/{total_t} topics</div>
            </div>""", unsafe_allow_html=True)
            if st.button("View", key=f"syl_home_{sname}", use_container_width=True):
                st.session_state.syl_subject = sname
                st.session_state.page = "syllabus"
                st.rerun()

    if u.get("badges"):
        st.markdown("### 🏆 Recent Badges")
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

    st.markdown("<div style='font-size:11px;font-weight:800;color:#aaa;"
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
# QUIZ
# ═════════════════════════════════════════════════════════════════
def page_quiz():
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
        <div style='text-align:center;background:#fff;border-radius:20px;padding:30px;
            box-shadow:0 2px 16px rgba(0,0,0,0.06);margin-bottom:16px'>
            <div style='font-size:56px'>{emoji}</div>
            <h2 style='font-family:"Baloo 2",cursive;font-size:26px;font-weight:800;color:#1A1A2E'>
                Quiz Complete!</h2>
            <div style='font-size:44px;font-weight:900;color:{info["color"]};margin:8px 0'>
                {score}/{total}</div>
            <div style='font-size:15px;color:#666'>
                {pct}% — {"Excellent! ⭐" if pct>=80 else "Good effort! 📚" if pct>=60 else "Keep practicing! 💪"}
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("### 📋 Review Answers")
        for i, (ques, ans) in enumerate(zip(q["questions"], q["answers"])):
            correct = ans["chosen"] == ques["answer"]
            bg     = "#F0FDF4" if correct else "#FFF1EE"
            border = "#059669" if correct else "#E8472A"
            wrong_line = "" if correct else f'<div style="font-size:13px;color:#059669;margin-top:2px">✅ Correct: <b>{ques["answer"]}</b></div>'
            st.markdown(f"""
            <div style='background:{bg};border:1.5px solid {border};border-radius:12px;
                padding:14px 16px;margin-bottom:10px'>
                <div style='font-weight:700;font-size:14px'>Q{i+1}. {ques["q"]}</div>
                <div style='font-size:13px;margin-top:5px'>
                    Your answer: <b>{ans["chosen"]}</b> {"✅" if correct else "❌"}
                </div>
                {wrong_line}
                <div style='font-size:12px;color:#666;margin-top:4px'>
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
        color:#666;margin-bottom:6px'>
        <span>Question {current+1} of {len(q["questions"])}</span>
        <span style='color:{info["color"]}'>Score: {q["score"]}/{current}</span>
    </div>
    <div class='prog-bar'>
        <div class='prog-fill' style='width:{pct_bar}%;background:{info["color"]}'></div>
    </div>
    <div style='background:#fff;border-radius:16px;padding:18px 20px;margin:12px 0;
        box-shadow:0 2px 16px rgba(0,0,0,0.06);font-weight:800;font-size:15px;
        color:#1A1A2E;line-height:1.5'>
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
# IMAGE GENERATOR  — SVG via Claude AI (no external URLs needed)
# ═════════════════════════════════════════════════════════════════
def page_image():
    u = st.session_state.user
    st.markdown("### 🎨 Educational Image Generator")
    st.markdown("""
    <div style='background:#F5F0FF;border:1.5px solid #7C3AED;border-radius:12px;
        padding:12px 16px;margin-bottom:16px;font-size:13px;color:#5B21B6'>
        🖌️ Claude AI draws a <b>custom SVG diagram</b> based on your description — works 100% offline, no external URLs needed!
    </div>""", unsafe_allow_html=True)

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
            "e.g.  Water cycle showing evaporation, clouds and rain\n"
            "e.g.  Human heart with blood flow direction"
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
                "STRICT OUTPUT RULES — follow every rule or the image will not display:\n"
                "1. Output ONLY the SVG code. No markdown. No backticks. No explanations. No text before <svg or after </svg>.\n"
                "2. Start your response with exactly: <svg\n"
                "3. End your response with exactly: </svg>\n"
                "4. Use: xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 700 500\" width=\"700\" height=\"500\"\n"
                "5. Include a <defs> block with at least 3 linearGradient definitions for colorful fills.\n"
                "6. Add a bold title at the top (y=35, font-size=24, font-weight=bold, text-anchor=middle, x=350).\n"
                "7. Use BRIGHT colors — never plain white shapes. Use gradient fills on all major shapes.\n"
                "8. Include at least 20 visual elements: shapes, labels, arrows, icons.\n"
                "9. Draw arrows using <line> with marker-end or <path> elements.\n"
                "10. Every component must have a clear text label.\n"
                "11. Make it look like a professional educational poster.\n"
                "12. DO NOT use any xlink:href or external images."
            )

            user_msg = (
                f"Create a detailed colorful educational SVG illustration:\n"
                f"TOPIC: {prompt}\n"
                f"SUBJECT: {img_sub}\n"
                f"LEVEL: {img_lvl}\n"
                f"STYLE: {style_hint}\n\n"
                f"Include: gradient background, bold title, labeled components, "
                f"arrows showing flow/relationships, color-coded sections.\n"
                f"Remember: output ONLY the SVG. Start with <svg and end with </svg>."
            )

            raw = call_ai_svg([{"role":"user","content":user_msg}], system_msg)

        # ── Extract SVG ──────────────────────────────────────────
        # Strip any markdown fences
        cleaned = raw
        for fence in ["```svg", "```xml", "```html", "```"]:
            cleaned = cleaned.replace(fence, "")
        cleaned = cleaned.strip()

        svg_start = cleaned.find("<svg")
        svg_end   = cleaned.rfind("</svg>")

        if svg_start >= 0 and svg_end >= 0:
            final_svg = cleaned[svg_start : svg_end + 6]

            # ── Display ──────────────────────────────────────────
            st.success("✅ Image generated successfully!")
            st.markdown("### 🖼️ Your Educational Diagram")
            st.components.v1.html(final_svg, height=520, scrolling=False)

            # ── Download button ──────────────────────────────────
            b64 = base64.b64encode(final_svg.encode()).decode()
            st.markdown(
                f'<a href="data:image/svg+xml;base64,{b64}" download="hw_diagram.svg" '
                f'style="display:inline-block;padding:10px 20px;background:#7C3AED;color:#fff;'
                f'border-radius:12px;font-weight:700;font-size:14px;text-decoration:none;margin-top:8px">'
                f'⬇️ Download SVG Image</a>',
                unsafe_allow_html=True
            )

            # ── Save to gallery ──────────────────────────────────
            imgs  = load_json(IMAGES_FILE)
            email = u["email"]
            if email not in imgs:
                imgs[email] = []
            imgs[email].insert(0, {
                "id":      str(int(time.time())),
                "svg":     final_svg,
                "prompt":  prompt,
                "subject": img_sub,
                "level":   img_lvl,
                "style":   style_choice,
                "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            save_json(IMAGES_FILE, imgs)

            # ── Update user stats ────────────────────────────────
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
            with st.expander("Show raw response (debug)"):
                st.code(raw[:800])

    # ── Gallery ──────────────────────────────────────────────────
    imgs      = load_json(IMAGES_FILE)
    user_imgs = imgs.get(u["email"], [])
    if user_imgs:
        st.markdown("---")
        st.markdown("### 🖼️ Your Image Gallery")
        for img in user_imgs[:8]:
            label = f"🎨 {img['subject']} — {img['prompt'][:55]}... | {img['created']}"
            with st.expander(label):
                st.components.v1.html(img["svg"], height=520, scrolling=False)
                b64 = base64.b64encode(img["svg"].encode()).decode()
                st.markdown(
                    f'<a href="data:image/svg+xml;base64,{b64}" download="hw_diagram.svg" '
                    f'style="display:inline-block;padding:7px 16px;background:#7C3AED;color:#fff;'
                    f'border-radius:10px;font-weight:700;font-size:12px;text-decoration:none">'
                    f'⬇️ Download</a>',
                    unsafe_allow_html=True
                )

# ═════════════════════════════════════════════════════════════════
# ESSAY HELPER
# ═════════════════════════════════════════════════════════════════
def page_essay():
    u = st.session_state.user
    st.markdown("### ✏️ Essay & Writing Helper")
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
        <div style='background:#fff;border-radius:16px;padding:20px 22px;
            box-shadow:0 2px 16px rgba(0,0,0,0.06);border-top:4px solid #059669;margin-top:12px'>
            <div style='font-weight:800;font-size:14px;color:#059669;margin-bottom:12px'>
                ✏️ {etype}: {topic}</div>
            <div style='font-size:14px;line-height:1.85;color:#1A1A2E;white-space:pre-wrap'>
                {st.session_state.essay_result}</div>
            <div style='margin-top:14px;padding:10px 12px;background:#EDFAF5;
                border-radius:10px;font-size:12px;color:#065F46'>
                💡 Use this as a learning example — try writing your own version!
            </div>
        </div>""", unsafe_allow_html=True)
        if st.button("📋 Copy Essay"):
            st.code(st.session_state.essay_result, language=None)

# ═════════════════════════════════════════════════════════════════
# STUDY TOOLS
# ═════════════════════════════════════════════════════════════════
def page_tools():
    st.markdown("### 🔧 Study Tools")
    t1, t2 = st.tabs(["🌐 Language Translator", "⏱️ Pomodoro Timer"])

    with t1:
        st.markdown("#### 🌐 Language Translator")
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
                          f"Also explain any difficult words.\n"
                          f"Format:\nTranslation:\n[translation here]\n\nWord Explanations:\n- word: meaning"}],
                        "Translation assistant for Pakistani school students. Be accurate and helpful."
                    )
                st.session_state.trans_result = result
        if st.session_state.trans_result:
            st.markdown(f"""
            <div style='background:#EFF4FF;border-radius:12px;padding:16px;
                font-size:14px;line-height:1.75;white-space:pre-wrap;margin-top:10px;color:#1A1A2E'>
                {st.session_state.trans_result}
            </div>""", unsafe_allow_html=True)

    with t2:
        st.markdown("#### ⏱️ Pomodoro Study Timer")
        st.markdown("""
        <div style='background:#F5F0FF;border-radius:12px;padding:14px 16px;
            font-size:13px;color:#5B21B6;margin-bottom:16px'>
            🍅 <b>Pomodoro Technique:</b> Study 25 min → 5 min break → repeat 4 times → 15 min long break.
            Proven to boost focus and memory!
        </div>""", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("📚 Study Session", "25 min")
        with c2: st.metric("☕ Short Break",    "5 min")
        with c3: st.metric("🌟 Long Break",     "15 min")
        st.info("⏱️ Set your phone timer and follow the schedule below:")
        st.markdown("**Your 4-Session Study Plan:**")
        for i in range(1, 5):
            brk = "☕ 5 min break" if i < 4 else "🌟 15 min long break — you deserve it!"
            st.markdown(f"- 🍅 **Session {i}:** 25 min study → {brk}")

# ═════════════════════════════════════════════════════════════════
# PROGRESS
# ═════════════════════════════════════════════════════════════════
def page_progress():
    u     = st.session_state.user
    stats = u.get("stats", {})
    total = stats.get("total", 0)

    st.markdown("### 📊 My Progress")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("❓ Questions",   total)
    with c2: st.metric("🏆 Badges",      len(u.get("badges",[])))
    with c3: st.metric("🔥 Streak",      f"{stats.get('streak',0)} days")
    with c4: st.metric("📅 Member Since", u.get("joined",""))

    st.markdown("### 📚 Questions Per Subject")
    for name, info in SUBJECTS.items():
        cnt = stats.get(name, 0)
        pct = int((cnt / max(total, 1)) * 100)
        st.markdown(f"""
        <div style='margin-bottom:14px'>
            <div style='display:flex;justify-content:space-between;font-size:13px;
                font-weight:700;margin-bottom:5px'>
                <span>{info['emoji']} {name}</span>
                <span style='color:{info["color"]}'>{cnt} questions ({pct}%)</span>
            </div>
            <div class='prog-bar'>
                <div class='prog-fill' style='width:{pct}%;background:{info["color"]}'></div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("### 🛠️ Activity Summary")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("🎨 Images Generated", stats.get("images", 0))
    with c2: st.metric("✏️ Essays Written",   stats.get("essays", 0))
    with c3: st.metric("📖 Subjects Studied",
                        sum(1 for s in ["Maths","Physics","English","Urdu"] if stats.get(s,0)>0))

# ═════════════════════════════════════════════════════════════════
# HISTORY
# ═════════════════════════════════════════════════════════════════
def page_history():
    u = st.session_state.user
    st.markdown("### 🕐 Chat History")
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
    u      = st.session_state.user
    earned = u.get("badges", [])
    st.markdown("### 🏆 Badges & Achievements")
    st.markdown(f"<p style='color:#999;font-size:13px'>Earned "
                f"<b style='color:#1A1A2E'>{len(earned)}</b> of "
                f"<b style='color:#1A1A2E'>{len(BADGES)}</b> badges</p>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i, b in enumerate(BADGES):
        is_earned = b["id"] in earned
        with cols[i % 3]:
            locked = "" if is_earned else "badge-locked"
            status_color = "#059669" if is_earned else "#ccc"
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
    u = st.session_state.user
    st.markdown("### 👤 My Profile")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f"<div style='font-size:80px;text-align:center;background:#F3F4F6;"
                    f"border-radius:20px;padding:20px'>{u.get('avatar','👦')}</div>",
                    unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style='padding:10px 0'>
            <div style='font-family:"Baloo 2",cursive;font-size:22px;font-weight:800;color:#1A1A2E'>
                {u['name']}</div>
            <div style='font-size:13px;color:#999;margin-top:4px'>
                {'🎒 Student' if u.get('role')=='student' else '👨‍👩‍👦 Parent'} • {u.get('grade','')}
            </div>
            <div style='font-size:12px;color:#bbb;margin-top:2px'>📧 {u['email']}</div>
            <div style='font-size:12px;color:#bbb;margin-top:2px'>📅 Joined {u.get('joined','')}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### ✏️ Update Profile")
    with st.form("profile_form"):
        new_name   = st.text_input("Full Name", value=u.get("name",""))
        new_grade  = st.selectbox("Default Class", ["-- Select --"] + LEVELS,
                                  index=LEVELS.index(u["grade"])+1 if u.get("grade","") in LEVELS else 0)
        cur_av_key = next((k for k,v in AVATARS.items() if v == u.get("avatar","👦")), list(AVATARS.keys())[0])
        new_avatar = st.selectbox("Avatar", list(AVATARS.keys()),
                                  index=list(AVATARS.keys()).index(cur_av_key))
        st.markdown("#### 🔒 Change Password")
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
    st.markdown("#### 🗑️ Danger Zone")
    if st.button("🗑️ Clear All My Chat History"):
        hist = load_json(HISTORY_FILE)
        hist[u["email"]] = []
        save_json(HISTORY_FILE, hist)
        st.success("Chat history cleared.")


# ═════════════════════════════════════════════════════════════════
# SYLLABUS PAGE
# ═════════════════════════════════════════════════════════════════
def page_syllabus():
    u     = st.session_state.user
    grade = u.get("grade","Class 5")

    st.markdown("### 📚 My Cambridge Syllabus")
    st.markdown(
        f"<p style='color:#666;font-size:13px;margin-bottom:16px'>"
        f"Showing the full syllabus for <b>{grade}</b> — aligned with Cambridge / Pakistan National Curriculum.</p>",
        unsafe_allow_html=True
    )

    # ── Class & Subject selectors ──────────────────────────────
    c1, c2 = st.columns(2)
    with c1:
        sel_grade = st.selectbox("🏫 Class", LEVELS,
            index=LEVELS.index(grade) if grade in LEVELS else 4,
            key="syl_grade")
    with c2:
        sel_sub = st.selectbox("📖 Subject", list(SUBJECTS.keys()),
            index=list(SUBJECTS.keys()).index(st.session_state.syl_subject),
            key="syl_sub_sel")
    st.session_state.syl_subject = sel_sub

    curr = CAMBRIDGE_CURRICULUM.get(sel_sub, {}).get(sel_grade, {})
    board = curr.get("board", "Pakistan National Curriculum")
    units = curr.get("units", [])

    # ── Board badge ────────────────────────────────────────────
    sub_color = SUBJECTS[sel_sub]["color"]
    sub_emoji = SUBJECTS[sel_sub]["emoji"]
    st.markdown(f"""
    <div style='background:{sub_color}18;border:2px solid {sub_color};
        border-radius:14px;padding:14px 18px;margin-bottom:18px;
        display:flex;align-items:center;gap:12px'>
        <div style='font-size:36px'>{sub_emoji}</div>
        <div>
            <div style='font-weight:800;font-size:16px;color:{sub_color}'>{sel_sub} — {sel_grade}</div>
            <div style='font-size:12px;color:#666;margin-top:2px'>🎓 {board}</div>
            <div style='font-size:12px;color:#999;margin-top:1px'>📋 {len(units)} Units</div>
        </div>
    </div>""", unsafe_allow_html=True)

    if not units:
        st.info("Curriculum data coming soon for this combination.")
        return

    # ── Progress tracker (which units studied) ─────────────────
    studied_topics = u.get("studied_topics", {})
    key = f"{sel_sub}_{sel_grade}"
    done_topics = studied_topics.get(key, [])
    total_topics = sum(len(un["topics"]) for un in units)
    done_count   = sum(1 for un in units for t in un["topics"] if f"{un['unit']}::{t}" in done_topics)
    pct = int((done_count / max(total_topics,1)) * 100)

    st.markdown(f"""
    <div style='margin-bottom:16px'>
        <div style='display:flex;justify-content:space-between;font-size:13px;
            font-weight:700;color:#666;margin-bottom:6px'>
            <span>📊 Syllabus Progress</span>
            <span style='color:{sub_color}'>{done_count}/{total_topics} topics studied ({pct}%)</span>
        </div>
        <div class='prog-bar'>
            <div class='prog-fill' style='width:{pct}%;background:{sub_color}'></div>
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Unit cards ─────────────────────────────────────────────
    for ui, unit in enumerate(units):
        unit_done = [t for t in unit["topics"] if f"{unit['unit']}::{t}" in done_topics]
        unit_pct  = int((len(unit_done)/len(unit["topics"]))*100)

        with st.expander(
            f"{'✅' if unit_pct==100 else '🔵' if unit_pct>0 else '⚪'}  "
            f"Unit {ui+1}: {unit['unit']}   ({unit_pct}% done)",
            expanded=(ui==0)
        ):
            # Mini progress bar
            st.markdown(f"""
            <div class='prog-bar' style='margin-bottom:12px'>
                <div class='prog-fill' style='width:{unit_pct}%;background:{sub_color}'></div>
            </div>""", unsafe_allow_html=True)

            for topic in unit["topics"]:
                topic_key = f"{unit['unit']}::{topic}"
                is_done   = topic_key in done_topics

                tc1, tc2, tc3 = st.columns([3, 1, 1])
                with tc1:
                    icon = "✅" if is_done else "📖"
                    st.markdown(
                        f"<div style='padding:6px 0;font-size:14px;color:{'#059669' if is_done else '#1A1A2E'};font-weight:{'700' if is_done else '400'}'>"
                        f"{icon} {topic}</div>",
                        unsafe_allow_html=True
                    )
                with tc2:
                    if st.button("💬 Ask", key=f"ask_{ui}_{topic[:20]}", use_container_width=True):
                        # Go to chat with this topic pre-loaded
                        st.session_state.subject       = sel_sub
                        st.session_state.level         = sel_grade
                        st.session_state.chat_messages = [{
                            "role": "user",
                            "content": f"Please explain this topic from my {sel_grade} {sel_sub} syllabus: {topic}"
                        }]
                        st.session_state.session_id = None
                        st.session_state.page       = "chat"
                        st.rerun()
                with tc3:
                    btn_label = "✅ Done" if is_done else "Mark ✓"
                    if st.button(btn_label, key=f"done_{ui}_{topic[:20]}", use_container_width=True):
                        users = load_json(USERS_FILE)
                        eu    = users.get(u["email"], u)
                        st_map = eu.get("studied_topics", {})
                        tlist  = st_map.get(key, [])
                        if topic_key in tlist:
                            tlist.remove(topic_key)
                        else:
                            tlist.append(topic_key)
                        st_map[key] = tlist
                        eu["studied_topics"] = st_map
                        users[u["email"]] = eu
                        save_json(USERS_FILE, users)
                        st.session_state.user = eu
                        st.rerun()

            # Quick action buttons
            st.markdown("<div style='margin-top:12px;display:flex;gap:8px;flex-wrap:wrap'>", unsafe_allow_html=True)
            ba, bb, bc = st.columns(3)
            with ba:
                if st.button(f"📝 Quiz on this unit", key=f"qunit_{ui}", use_container_width=True):
                    topics_str = ", ".join(unit["topics"])
                    with st.spinner("Generating unit quiz..."):
                        raw = call_ai(
                            [{"role":"user","content":
                              f"Create 5 MCQ questions specifically about this unit: '{unit['unit']}' "
                              f"covering these topics: {topics_str}. "
                              f"For {sel_grade} level {sel_sub} students ({board}). "
                              f"Return ONLY raw JSON: "
                              f'{{"questions":[{{"q":"...","options":["A. ...","B. ...","C. ...","D. ..."],"answer":"A. ...","explanation":"..."}}]}}'}],
                            "Quiz generator. Return ONLY valid raw JSON.", 1200
                        )
                        try:
                            clean = raw.replace("```json","").replace("```","").strip()
                            data  = json.loads(clean)
                            st.session_state.quiz = {
                                "questions": data["questions"],
                                "current":0,"score":0,"answers":[],"done":False,
                                "sub":sel_sub,"lvl":sel_grade
                            }
                            st.session_state.page = "quiz"
                            st.rerun()
                        except:
                            st.error("Could not generate quiz. Try again.")
            with bb:
                if st.button(f"🎨 Diagram", key=f"imgunit_{ui}", use_container_width=True):
                    st.session_state.page = "image"
                    st.rerun()
            with bc:
                if st.button(f"📖 Summary", key=f"sumunit_{ui}", use_container_width=True):
                    topics_str = ", ".join(unit["topics"])
                    with st.spinner("Generating summary..."):
                        summary = call_ai(
                            [{"role":"user","content":
                              f"Give a clear, concise revision summary of '{unit['unit']}' for a {sel_grade} "
                              f"{sel_sub} student ({board}). Cover these key topics: {topics_str}. "
                              f"Use bullet points, include key formulas or rules, and keep it under 300 words."}],
                            f"You are a {sel_sub} teacher. Give revision summaries in clear simple English.", 800
                        )
                    st.markdown(f"""
                    <div style='background:#F8F9FA;border-left:4px solid {sub_color};
                        border-radius:0 12px 12px 0;padding:14px 16px;margin-top:10px;
                        font-size:13px;line-height:1.7;white-space:pre-wrap;color:#1A1A2E'>
                        {summary}
                    </div>""", unsafe_allow_html=True)

    # ── Full syllabus overview ─────────────────────────────────
    st.markdown("---")
    st.markdown("### 📋 Full Syllabus Overview")
    for ui, unit in enumerate(units):
        topics_html = "".join(
            f"<span style='display:inline-block;background:{sub_color}18;border:1px solid {sub_color}44;"
            f"border-radius:20px;padding:3px 10px;font-size:11px;color:{sub_color};margin:3px 3px 3px 0;"
            f"font-weight:600'>{t}</span>"
            for t in unit["topics"]
        )
        st.markdown(f"""
        <div style='background:#fff;border-radius:14px;padding:14px 16px;
            margin-bottom:10px;box-shadow:0 2px 8px rgba(0,0,0,0.05);border:1px solid #F0F0F5'>
            <div style='font-weight:800;font-size:14px;color:#1A1A2E;margin-bottom:8px'>
                {ui+1}. {unit["unit"]}
            </div>
            <div>{topics_html}</div>
        </div>""", unsafe_allow_html=True)

    # ── Download syllabus ──────────────────────────────────────
    syllabus_text = f"{sel_sub} — {sel_grade}\nBoard: {board}\n\n"
    for ui, unit in enumerate(units):
        syllabus_text += f"Unit {ui+1}: {unit['unit']}\n"
        for t in unit["topics"]:
            syllabus_text += f"  • {t}\n"
        syllabus_text += "\n"
    b64 = base64.b64encode(syllabus_text.encode()).decode()
    st.markdown(
        f'<a href="data:text/plain;base64,{b64}" download="{sel_sub}_{sel_grade}_syllabus.txt" '
        f'style="display:inline-block;padding:10px 20px;background:{sub_color};color:#fff;'
        f'border-radius:12px;font-weight:700;font-size:14px;text-decoration:none;margin-top:8px">'
        f'⬇️ Download Syllabus as Text</a>',
        unsafe_allow_html=True
    )

# ═════════════════════════════════════════════════════════════════
# ROUTER
# ═════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    page_auth()
else:
    render_sidebar()
    p = st.session_state.page
    if   p == "home":     page_home()
    elif p == "chat":     page_chat()
    elif p == "syllabus": page_syllabus()
    elif p == "quiz":     page_quiz()
    elif p == "image":    page_image()
    elif p == "essay":    page_essay()
    elif p == "tools":    page_tools()
    elif p == "progress": page_progress()
    elif p == "history":  page_history()
    elif p == "badges":   page_badges()
    elif p == "profile":  page_profile()
