# ═══════════════════════════════════════════════════════════════════════════════
# ZM Academy — Complete Streamlit App
# Updated with: Enhanced Quiz, Friends Group, Improved Image Gen,
#               Redesigned Syllabus, Removed Essay/StudyTools
# ═══════════════════════════════════════════════════════════════════════════════
import streamlit as st
import json, hashlib, datetime, time, os, base64, random
from anthropic import Anthropic
from curriculum import CAMBRIDGE_CURRICULUM

# ─────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ZM Academy 📚",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────────────────────────
# CONSTANTS & LOOKUPS
# ─────────────────────────────────────────────────────────────────
SUBJECTS = {
    "Maths":           {"emoji": "🔢", "color": "#E8472A"},
    "Physics":         {"emoji": "⚡", "color": "#2563EB"},
    "Chemistry":       {"emoji": "🧪", "color": "#7C3AED"},
    "Biology":         {"emoji": "🌱", "color": "#059669"},
    "English":         {"emoji": "📖", "color": "#0891B2"},
    "Computer Science":{"emoji": "💻", "color": "#6D28D9"},
    "Urdu":            {"emoji": "🖊️", "color": "#B45309"},
}

LEVELS = [
    "Grade 1","Grade 2","Grade 3","Grade 4","Grade 5",
    "Grade 6","Grade 7","Grade 8","Grade 9","Grade 10",
    "O Level","A Level"
]

# Legacy compat mapping (old "Class X" keys → new "Grade X")
_LEVEL_ALIAS = {f"Class {i}": f"Grade {i}" for i in range(1,11)}
_LEVEL_ALIAS.update({"Class 5": "Grade 5"})

def normalise_level(grade):
    return _LEVEL_ALIAS.get(grade, grade)

def get_level_index(grade):
    grade = normalise_level(grade)
    try:
        return LEVELS.index(grade) if grade in LEVELS else 5
    except Exception:
        return 5

AVATARS = {
    "👦 Boy":"👦","👧 Girl":"👧","👨 Dad":"👨","👩 Mom":"👩",
    "👨‍🏫 Teacher":"👨‍🏫","🧑‍🚀 Astronaut":"🧑‍🚀",
    "🧑‍🔬 Scientist":"🧑‍🔬","🧑‍🎨 Artist":"🧑‍🎨"
}

# ── Image styles ─────────────────────────────────────────────────
IMAGE_STYLES = {
    "📐 Educational Diagram": "a clean labeled educational diagram with arrows, colorful sections, white background",
    "🎨 Cartoon":             "a bright fun cartoon illustration with cheerful bold colors suitable for students",
    "🎌 Anime Style":         "an anime-style illustration with vibrant colors, clean lines, expressive characters",
    "🤖 AI Art":              "a futuristic AI-generated digital art style with glowing elements and deep colors",
    "🔬 Realistic / Scientific": "a detailed realistic scientific illustration like a textbook diagram, accurate and labeled",
}

# ── Badge definitions ─────────────────────────────────────────────
BADGES = [
    {"id":"first_q",  "icon":"🌟","name":"First Step",        "desc":"Asked first question",    "req": lambda s: s.get("total",0)>=1},
    {"id":"curious",  "icon":"🧠","name":"Curious Mind",      "desc":"Asked 5 questions",       "req": lambda s: s.get("total",0)>=5},
    {"id":"seeker",   "icon":"📚","name":"Knowledge Seeker",  "desc":"Asked 20 questions",      "req": lambda s: s.get("total",0)>=20},
    {"id":"maths",    "icon":"🔢","name":"Maths Master",      "desc":"10 Maths questions",      "req": lambda s: s.get("Maths",0)>=10},
    {"id":"physics",  "icon":"⚡","name":"Physics Pro",       "desc":"10 Physics questions",    "req": lambda s: s.get("Physics",0)>=10},
    {"id":"english",  "icon":"📖","name":"English Expert",    "desc":"10 English questions",    "req": lambda s: s.get("English",0)>=10},
    {"id":"urdu",     "icon":"🖊️","name":"Urdu Ustad",        "desc":"10 Urdu questions",       "req": lambda s: s.get("Urdu",0)>=10},
    {"id":"allround", "icon":"🏆","name":"All-Rounder",       "desc":"Studied 4+ subjects",     "req": lambda s: sum(1 for x in ["Maths","Physics","English","Urdu"] if s.get(x,0)>0)>=4},
    {"id":"artist",   "icon":"🎨","name":"Visual Learner",    "desc":"Generated 3 images",      "req": lambda s: s.get("images",0)>=3},
    {"id":"quiz_hero","icon":"🥇","name":"Quiz Champion",     "desc":"Completed 5 quizzes",     "req": lambda s: s.get("quizzes_done",0)>=5},
    {"id":"streak",   "icon":"🔥","name":"7-Day Streak",      "desc":"7 days in a row",         "req": lambda s: s.get("streak",0)>=7},
]

QUICK_PROMPTS = {
    "Maths":           ["Explain fractions with examples","Solve: 2x + 5 = 15","What is Pythagoras theorem?","How to calculate percentage?"],
    "Physics":         ["What are Newton's 3 laws?","How does electricity work?","What is gravity?","Difference between speed and velocity"],
    "Chemistry":       ["What is the periodic table?","Explain atomic structure","What are chemical bonds?","How do acids and bases work?"],
    "Biology":         ["Explain photosynthesis","What is DNA?","How does the heart work?","What is cell division?"],
    "English":         ["How to write a good essay?","Explain past and present tense","What are nouns and verbs?","How to improve vocabulary?"],
    "Computer Science":["What is an algorithm?","Explain loops in programming","What is a database?","How does the internet work?"],
    "Urdu":            ["اردو گرامر کی بنیادی باتیں","نظم اور نثر میں کیا فرق ہے؟","اچھا مضمون کیسے لکھیں؟","محاورے کیا ہوتے ہیں؟"],
}

# ── Cambridge syllabus subjects per grade ────────────────────────
CAMBRIDGE_SUBJECTS = {
    "Grade 6":  ["Mathematics","Physics","Chemistry","Biology","English","Computer Science","Urdu"],
    "Grade 7":  ["Mathematics","Physics","Chemistry","Biology","English","Computer Science","Urdu"],
    "Grade 8":  ["Mathematics","Physics","Chemistry","Biology","English","Computer Science","Urdu"],
    "Grade 9":  ["Mathematics","Physics","Chemistry","Biology","English","Computer Science","Urdu"],
    "Grade 10": ["Mathematics","Physics","Chemistry","Biology","English","Computer Science","Urdu"],
    "O Level":  ["Mathematics","Physics","Chemistry","Biology","English Language","Computer Science","Urdu"],
    "A Level":  ["Mathematics","Physics","Chemistry","Biology","English Language","Computer Science"],
}
for g in ["Grade 1","Grade 2","Grade 3","Grade 4","Grade 5"]:
    CAMBRIDGE_SUBJECTS[g] = ["Mathematics","English","Urdu","Science","Islamiyat"]

# ─────────────────────────────────────────────────────────────────
# DATA STORAGE
# ─────────────────────────────────────────────────────────────────
USERS_FILE   = "users.json"
HISTORY_FILE = "history.json"
IMAGES_FILE  = "images.json"
GROUPS_FILE  = "groups.json"
HOMEWORK_FILE = "homework.json"

def load_json(filepath):
    cache_key = f"_cache_{filepath}"
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            st.session_state[cache_key] = data
            return data
    except Exception:
        pass
    return st.session_state.get(cache_key, {})

def save_json(filepath, data):
    cache_key = f"_cache_{filepath}"
    st.session_state[cache_key] = data
    tmp = filepath + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, filepath)
    except Exception:
        try: os.remove(tmp)
        except Exception: pass

def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ─────────────────────────────────────────────────────────────────
# STATS & BADGES
# ─────────────────────────────────────────────────────────────────
DAILY_LIMITS = {"free":10, "basic":50, "premium":9999}

def init_stats():
    return {"total":0,"Maths":0,"Physics":0,"Chemistry":0,"Biology":0,
            "English":0,"Computer Science":0,"Urdu":0,
            "streak":0,"lastDate":"","images":0,"quizzes_done":0,
            "dailyQs":0,"dailyDate":""}

def get_daily_used(user):
    stats = user.get("stats", {})
    today = datetime.date.today().isoformat()
    if stats.get("dailyDate","") != today: return 0
    return stats.get("dailyQs", 0)

def check_daily_limit(user):
    plan  = user.get("plan","free")
    limit = DAILY_LIMITS.get(plan, 10)
    used  = get_daily_used(user)
    return used < limit, used, limit

def check_badges(user):
    earned   = user.get("badges", [])
    new_ones = []
    stats    = user.get("stats", {})
    for b in BADGES:
        if b["id"] not in earned and b["req"](stats):
            earned.append(b["id"])
            new_ones.append(b)
    user["badges"] = earned
    return user, new_ones

def bump_stats(subject_field=None, extra_field=None):
    users = load_json(USERS_FILE)
    email = st.session_state.user["email"]
    u     = users.get(email, st.session_state.user)
    s     = u.get("stats", init_stats())
    s["total"] = s.get("total", 0) + 1
    if subject_field: s[subject_field] = s.get(subject_field, 0) + 1
    if extra_field:   s[extra_field]   = s.get(extra_field, 0) + 1
    today = datetime.date.today().isoformat()
    yest  = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    if   s.get("lastDate","") == today: pass
    elif s.get("lastDate","") == yest:  s["streak"] = s.get("streak",0)+1
    else:                               s["streak"] = 1
    s["lastDate"] = today
    # daily counter
    if s.get("dailyDate","") != today:
        s["dailyQs"]  = 0
        s["dailyDate"] = today
    s["dailyQs"] = s.get("dailyQs",0)+1
    u["stats"] = s
    u, new_badges = check_badges(u)
    users[email] = u
    save_json(USERS_FILE, users)
    st.session_state.user = u
    for b in new_badges:
        st.toast(f"🏆 Badge Earned: {b['icon']} {b['name']}!", icon="🎉")

# ─────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────
defaults = {
    "logged_in": False, "user": None, "page": "home",
    "subject": "Maths", "level": "Grade 6",
    "chat_messages": [], "session_id": None,
    "quiz": None,
    "word_of_day": None, "wod_loaded": False,
    "syl_subject": "Maths", "syl_unit": None,
    # Syllabus selections
    "syl_curriculum": "Cambridge",
    "syl_grade": "Grade 8",
    "syl_subject_name": "Mathematics",
    "syl_custom_grade": "",
    "syl_custom_subject": "",
    # Friends group
    "group_session": None,
    "group_player_idx": 0,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────
# ANTHROPIC CLIENT
# ─────────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    key = st.secrets.get("ANTHROPIC_API_KEY","") or os.environ.get("ANTHROPIC_API_KEY","")
    if not key: return None
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
# CSS — ZM Academy Premium UI  🇵🇰  Dark Luxury + Emerald Gold
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=Sora:wght@700;800;900&display=swap');

/* ══════════════════════════════════════════
   ROOT TOKENS
══════════════════════════════════════════ */
:root{
  --bg:        #F0F4F0;
  --surface:   #FFFFFF;
  --surface2:  #F7FAF7;
  --border:    #E2EAE2;
  --green:     #0D6E3F;
  --green-mid: #1A8C50;
  --green-lt:  #27A862;
  --gold:      #C9A84C;
  --gold-lt:   #E8C96A;
  --crimson:   #C0392B;
  --text:      #0D1F0D;
  --text2:     #3D5C3D;
  --text3:     #7A9A7A;
  --white:     #FFFFFF;
  --shadow-sm: 0 2px 8px rgba(13,110,63,0.08);
  --shadow-md: 0 6px 24px rgba(13,110,63,0.12);
  --shadow-lg: 0 16px 48px rgba(13,110,63,0.16);
  --radius:    16px;
  --radius-sm: 10px;
}

/* ══════════════════════════════════════════
   BASE
══════════════════════════════════════════ */
html,body,[class*="css"]{
  font-family:'Plus Jakarta Sans',sans-serif !important;
  background:var(--bg) !important;
  color:var(--text) !important;
}
.main .block-container{
  padding-top:1.2rem !important; padding-bottom:4rem !important;
  max-width:960px !important;
  padding-left:1.4rem !important; padding-right:1.4rem !important;
  background:var(--bg) !important;
}
#MainMenu,footer,header{ visibility:hidden; }

/* ── Animated grain overlay for depth ── */
.main::before{
  content:''; position:fixed; inset:0; pointer-events:none; z-index:0;
  background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.025'/%3E%3C/svg%3E");
  opacity:.4;
}

/* ══════════════════════════════════════════
   MOBILE
══════════════════════════════════════════ */
@media(max-width:768px){
  .main .block-container{ padding-left:.6rem !important; padding-right:.6rem !important; }
  .stButton>button{ min-height:48px !important; font-size:14px !important; }
  .msg-user{ margin-left:6px !important; }
  .msg-bot{  margin-right:6px !important; }
  div[data-testid="column"]{ padding:2px !important; }
  .stTextInput>div>div>input{ font-size:16px !important; padding:12px !important; }
}

/* ══════════════════════════════════════════
   MAIN BUTTONS
══════════════════════════════════════════ */
.stButton>button{
  background:var(--surface) !important;
  border:1.5px solid var(--border) !important;
  color:var(--text) !important;
  font-family:'Plus Jakarta Sans',sans-serif !important;
  font-weight:700 !important; font-size:13.5px !important;
  border-radius:var(--radius-sm) !important;
  padding:10px 18px !important;
  transition:all .2s cubic-bezier(.4,0,.2,1) !important;
  box-shadow:var(--shadow-sm) !important;
}
.stButton>button:hover{
  border-color:var(--green-mid) !important;
  color:var(--green) !important;
  box-shadow:var(--shadow-md) !important;
  transform:translateY(-1px) !important;
}
.stButton>button[kind="primary"]{
  background:linear-gradient(135deg,var(--green) 0%,var(--green-lt) 100%) !important;
  color:#fff !important; border:none !important;
  box-shadow:0 6px 20px rgba(13,110,63,0.35) !important;
  font-weight:800 !important;
}
.stButton>button[kind="primary"]:hover{
  box-shadow:0 8px 28px rgba(13,110,63,0.5) !important;
  transform:translateY(-2px) !important;
  color:#fff !important;
}

/* ══════════════════════════════════════════
   SIDEBAR — Deep Forest Dark
══════════════════════════════════════════ */
[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#061A0E 0%,#0A2414 40%,#071510 100%) !important;
  border-right:1px solid rgba(201,168,76,0.15) !important;
}
[data-testid="stSidebar"] *{ color:#fff !important; }
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] label{ color:#fff !important; }

[data-testid="stSidebar"] .stButton>button{
  background:rgba(255,255,255,0.05) !important;
  border:1px solid rgba(201,168,76,0.12) !important;
  color:#E8F5EE !important; font-weight:600 !important;
  font-size:13.5px !important; text-align:left !important;
  padding:11px 16px !important; border-radius:10px !important;
  margin-bottom:3px !important; width:100% !important;
  transition:all .18s ease !important;
  box-shadow:none !important; transform:none !important;
}
[data-testid="stSidebar"] .stButton>button:hover{
  background:rgba(201,168,76,0.12) !important;
  border-color:rgba(201,168,76,0.35) !important;
  color:#E8C96A !important;
  transform:translateX(3px) !important;
}
[data-testid="stSidebar"] .stButton>button[kind="primary"]{
  background:linear-gradient(135deg,#0D6E3F,#1A8C50) !important;
  border:1px solid rgba(201,168,76,0.4) !important;
  color:#FFD700 !important; font-weight:800 !important;
  box-shadow:0 4px 16px rgba(13,110,63,0.5),0 0 0 1px rgba(201,168,76,0.2) !important;
}

/* ══════════════════════════════════════════
   CARDS
══════════════════════════════════════════ */
.stat-card{
  background:var(--surface); border-radius:var(--radius);
  padding:18px 14px; text-align:center;
  box-shadow:var(--shadow-sm); border:1.5px solid var(--border);
  transition:box-shadow .2s, transform .2s;
  position:relative; overflow:hidden;
}
.stat-card::before{
  content:''; position:absolute; top:0; left:0; right:0; height:3px;
  background:linear-gradient(90deg,var(--green),var(--gold));
}
.stat-card:hover{ box-shadow:var(--shadow-md); transform:translateY(-2px); }
.stat-num{ font-size:30px; font-weight:900; color:var(--green); font-family:'Sora',sans-serif; }
.stat-lbl{ font-size:11px; color:var(--text3); margin-top:4px; font-weight:600; text-transform:uppercase; letter-spacing:.6px; }

.feature-card{
  background:var(--surface); border-radius:var(--radius);
  padding:18px 20px; border-left:4px solid var(--green);
  box-shadow:var(--shadow-sm); margin-bottom:10px; color:var(--text);
  transition:box-shadow .2s, transform .2s;
}
.feature-card:hover{ box-shadow:var(--shadow-md); transform:translateY(-1px); }

.hist-card{
  background:var(--surface); border-radius:var(--radius);
  padding:14px 16px; box-shadow:var(--shadow-sm);
  border:1.5px solid var(--border); margin-bottom:10px;
}

/* ══════════════════════════════════════════
   SECTION HEADERS
══════════════════════════════════════════ */
.section-header{
  background:linear-gradient(135deg,#0D6E3F 0%,#1A8C50 60%,#0A5A32 100%);
  color:#fff; border-radius:var(--radius); padding:16px 22px; margin-bottom:20px;
  font-family:'Sora',sans-serif; font-size:20px; font-weight:800;
  border:1px solid rgba(201,168,76,0.25);
  box-shadow:0 6px 24px rgba(13,110,63,0.25);
  letter-spacing:-.3px; position:relative; overflow:hidden;
}
.section-header::after{
  content:''; position:absolute; top:-40px; right:-30px;
  width:120px; height:120px; border-radius:50%;
  background:rgba(201,168,76,0.15);
}
.section-header.orange{
  background:linear-gradient(135deg,#8B1A0A 0%,#C0392B 60%,#E74C3C 100%);
  border-color:rgba(255,200,100,0.2);
  box-shadow:0 6px 24px rgba(192,57,43,0.3);
}
.section-header.gold{
  background:linear-gradient(135deg,#7A5C00 0%,#C9A84C 60%,#E8C96A 100%);
  border-color:rgba(255,255,255,0.2);
  box-shadow:0 6px 24px rgba(201,168,76,0.35);
}
.section-header.blue{
  background:linear-gradient(135deg,#0A2F6B 0%,#1A56C4 60%,#2E7DD1 100%);
  border-color:rgba(100,180,255,0.2);
}
.section-header.purple{
  background:linear-gradient(135deg,#3A0A6B 0%,#6B21A8 60%,#8B5CF6 100%);
  border-color:rgba(200,150,255,0.2);
}

/* ══════════════════════════════════════════
   CHAT BUBBLES
══════════════════════════════════════════ */
.msg-user{
  background:linear-gradient(135deg,#0D6E3F,#1A8C50);
  color:#fff; border-radius:18px 18px 4px 18px;
  padding:13px 18px; margin:5px 0 5px 50px;
  font-size:14px; line-height:1.7;
  box-shadow:0 4px 16px rgba(13,110,63,0.25);
}
.msg-bot{
  background:var(--surface); color:var(--text);
  border-radius:18px 18px 18px 4px; padding:13px 18px;
  margin:5px 50px 5px 0; font-size:14px; line-height:1.75;
  box-shadow:var(--shadow-sm); border:1.5px solid var(--border);
}
.msg-lbl{ font-size:11px; color:var(--text3); margin-bottom:3px; font-weight:600; }
.msg-lbl-r{ text-align:right; }

/* ══════════════════════════════════════════
   PROGRESS BARS
══════════════════════════════════════════ */
.prog-bar{
  background:rgba(13,110,63,0.08); border-radius:99px;
  height:10px; overflow:hidden; margin-bottom:4px;
}
.prog-fill{ height:100%; border-radius:99px; transition:width .6s cubic-bezier(.4,0,.2,1); }

/* ══════════════════════════════════════════
   BADGES
══════════════════════════════════════════ */
.badge-card{
  background:linear-gradient(135deg,#FFFDF0,#FFF8E0);
  border:1.5px solid rgba(201,168,76,0.45); border-radius:var(--radius);
  padding:14px 10px; text-align:center;
  box-shadow:0 2px 12px rgba(201,168,76,0.15);
  transition:transform .2s, box-shadow .2s;
}
.badge-card:hover{ transform:translateY(-3px); box-shadow:0 8px 24px rgba(201,168,76,0.3); }
.badge-locked{ opacity:0.3; filter:grayscale(1); }
.badge-icon{ font-size:30px; display:block; }
.badge-name{ font-size:12px; font-weight:800; color:#7A5C00; margin-top:6px; }
.badge-desc{ font-size:10px; color:var(--text3); margin-top:3px; }

/* ══════════════════════════════════════════
   WORD CARD
══════════════════════════════════════════ */
.word-card{
  background:linear-gradient(135deg,#061A0E 0%,#0A2414 50%,#071510 100%);
  border-radius:var(--radius); padding:20px 22px; margin-bottom:16px;
  color:#fff; border:1px solid rgba(201,168,76,0.25);
  box-shadow:0 8px 32px rgba(6,26,14,0.3);
  position:relative; overflow:hidden;
}
.word-card::before{
  content:''; position:absolute; top:-20px; right:-20px;
  width:100px; height:100px; border-radius:50%;
  background:radial-gradient(circle,rgba(201,168,76,0.2),transparent 70%);
}

/* ══════════════════════════════════════════
   MISC
══════════════════════════════════════════ */
.reminder{
  background:linear-gradient(135deg,#FFFDF0,#FFF8DC);
  border:1.5px solid rgba(201,168,76,0.4); border-radius:var(--radius);
  padding:13px 18px; margin-bottom:16px; font-size:13px; color:var(--text);
  box-shadow:0 2px 10px rgba(201,168,76,0.12);
}

/* ── Leaderboard ── */
.lb-row{
  display:flex; align-items:center; gap:12px; padding:13px 18px;
  background:var(--surface); border-radius:var(--radius); margin-bottom:8px;
  box-shadow:var(--shadow-sm); border:1.5px solid var(--border); color:var(--text);
  transition:box-shadow .2s, transform .2s;
}
.lb-row:hover{ box-shadow:var(--shadow-md); transform:translateX(3px); }
.lb-rank{ font-size:22px; font-weight:900; width:32px; text-align:center; }
.lb-name{ flex:1; font-weight:700; font-size:14px; }
.lb-score{ font-weight:900; font-size:18px; color:var(--green); font-family:'Sora',sans-serif; }

/* ── Syllabus ── */
.syl-step{
  background:linear-gradient(135deg,#F0FAF3,#F5FFF7);
  border-radius:var(--radius); padding:16px 18px; margin-bottom:14px;
  border:1.5px solid rgba(13,110,63,0.12); color:var(--text);
}
.syl-step-title{
  font-size:11px; font-weight:800; color:var(--green);
  text-transform:uppercase; letter-spacing:1.2px; margin-bottom:8px;
}
.topic-chip{
  display:inline-block; border-radius:20px; padding:4px 12px;
  font-size:11px; font-weight:700; margin:3px 3px 3px 0;
}

/* ══════════════════════════════════════════
   INPUTS & SELECTS
══════════════════════════════════════════ */
[data-testid="stSelectbox"]>div>div{
  background:var(--surface) !important; border:2px solid var(--border) !important;
  border-radius:var(--radius-sm) !important; color:var(--text) !important;
}
[data-testid="stSelectbox"]>div>div>div{ color:var(--text) !important; font-weight:600 !important; }
[data-baseweb="popover"],[data-baseweb="menu"],[role="listbox"]{
  background:var(--surface) !important; border:1.5px solid var(--border) !important;
  border-radius:var(--radius) !important;
  box-shadow:0 12px 40px rgba(13,110,63,0.15) !important;
}
[role="option"]{ color:var(--text) !important; background:var(--surface) !important; font-size:14px !important; padding:10px 14px !important; }
[role="option"]:hover,[role="option"][aria-selected="true"]{
  background:rgba(13,110,63,0.08) !important; color:var(--green) !important; font-weight:700 !important;
}
.stTextInput>div>div>input,
.stTextArea>div>div>textarea{
  border-radius:var(--radius-sm) !important; border:2px solid var(--border) !important;
  color:var(--text) !important; background:var(--surface) !important;
  font-family:'Plus Jakarta Sans',sans-serif !important;
}
.stTextInput>div>div>input:focus,
.stTextArea>div>div>textarea:focus{
  border-color:var(--green) !important;
  box-shadow:0 0 0 3px rgba(13,110,63,0.12) !important;
}
label,[data-testid="stLabel"]>label{ color:var(--text) !important; font-weight:700 !important; font-size:13px !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"]{
  background:var(--surface2) !important; border-radius:var(--radius-sm) !important;
  padding:4px !important; border:1.5px solid var(--border) !important;
  gap:4px !important;
}
.stTabs [data-baseweb="tab"]{
  background:transparent !important; color:var(--text2) !important;
  font-weight:700 !important; font-size:13px !important;
  border-radius:8px !important; padding:8px 16px !important;
  border:none !important;
}
.stTabs [aria-selected="true"]{
  background:linear-gradient(135deg,var(--green),var(--green-lt)) !important;
  color:#fff !important; box-shadow:0 3px 10px rgba(13,110,63,0.3) !important;
}

/* ── Expanders ── */
[data-testid="stExpander"]{
  background:var(--surface) !important; border:1.5px solid var(--border) !important;
  border-radius:var(--radius-sm) !important; margin-bottom:6px !important;
}
[data-testid="stExpander"] summary{
  font-weight:700 !important; color:var(--text) !important;
}

/* ── Metrics ── */
[data-testid="stMetricValue"]{ color:var(--green) !important; font-family:'Sora',sans-serif !important; font-weight:900 !important; }
[data-testid="stMetricLabel"]{ color:var(--text2) !important; font-weight:700 !important; }

/* ── st.info / success / error ── */
[data-testid="stAlert"]{
  border-radius:var(--radius-sm) !important;
  border-left-width:4px !important;
}

/* ── Radio/checkbox ── */
.stRadio label,[data-testid="stRadio"] label{ color:var(--text) !important; font-weight:600 !important; }
.stCheckbox label{ color:var(--text) !important; font-weight:600 !important; }

/* ── Slider ── */
[data-testid="stSlider"] [data-baseweb="slider"] [data-testid="stThumbValue"]{
  color:var(--green) !important; font-weight:800 !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar{ width:6px; height:6px; }
::-webkit-scrollbar-track{ background:var(--bg); }
::-webkit-scrollbar-thumb{ background:rgba(13,110,63,0.25); border-radius:99px; }
::-webkit-scrollbar-thumb:hover{ background:rgba(13,110,63,0.45); }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# AUTH PAGE
# ─────────────────────────────────────────────────────────────────
def page_auth():
    # Full-page premium background
    st.markdown("""
    <style>
    .main .block-container{ max-width:480px !important; padding-top:2rem !important; }
    [data-testid="stForm"]{ background:var(--surface) !important; border-radius:20px !important; padding:24px !important; border:1.5px solid var(--border) !important; box-shadow:var(--shadow-lg) !important; }
    </style>""", unsafe_allow_html=True)

    st.markdown("""
    <div style='text-align:center;padding:32px 0 24px'>
        <div style='display:inline-flex;align-items:center;justify-content:center;
            width:80px;height:80px;border-radius:24px;margin-bottom:16px;
            background:linear-gradient(135deg,#0D6E3F,#1A8C50);
            box-shadow:0 8px 32px rgba(13,110,63,0.4)'>
            <span style='font-size:40px;line-height:1'>📚</span>
        </div>
        <h1 style='font-family:"Sora",sans-serif;font-size:32px;font-weight:900;
            color:#0D1F0D;margin:0 0 6px;letter-spacing:-1px'>ZM Academy</h1>
        <p style='color:#3D5C3D;font-size:14px;font-weight:600;margin:0'>
            🇵🇰 Pakistan's <b style="color:#0D6E3F">#1</b> AI-Powered Education Platform
        </p>
        <div style='display:flex;justify-content:center;gap:8px;margin-top:10px;flex-wrap:wrap'>
            <span style='background:rgba(13,110,63,0.08);color:#0D6E3F;padding:3px 12px;
                border-radius:99px;font-size:11px;font-weight:700;border:1px solid rgba(13,110,63,0.15)'>
                Grades 1–10</span>
            <span style='background:rgba(13,110,63,0.08);color:#0D6E3F;padding:3px 12px;
                border-radius:99px;font-size:11px;font-weight:700;border:1px solid rgba(13,110,63,0.15)'>
                O Level</span>
            <span style='background:rgba(13,110,63,0.08);color:#0D6E3F;padding:3px 12px;
                border-radius:99px;font-size:11px;font-weight:700;border:1px solid rgba(13,110,63,0.15)'>
                A Level</span>
            <span style='background:rgba(201,168,76,0.15);color:#7A5C00;padding:3px 12px;
                border-radius:99px;font-size:11px;font-weight:700;border:1px solid rgba(201,168,76,0.25)'>
                🤖 AI Powered</span>
        </div>
    </div>""", unsafe_allow_html=True)

    tab_login, tab_signup, tab_forgot = st.tabs(["🔑  Login","✨  Sign Up","🔓  Reset"])

    with tab_login:
        with st.form("login_form"):
            email    = st.text_input("📧 Email", placeholder="you@example.com")
            password = st.text_input("🔒 Password", type="password")
            if st.form_submit_button("Login to ZM Academy →", use_container_width=True, type="primary"):
                users = load_json(USERS_FILE)
                if email in users and users[email]["password"] == hash_pw(password):
                    users[email]["last_login"] = datetime.date.today().isoformat()
                    if "plan" not in users[email]: users[email]["plan"] = "free"
                    save_json(USERS_FILE, users)
                    st.session_state.logged_in = True
                    st.session_state.user      = users[email]
                    st.success("Welcome back! 🎉"); time.sleep(0.5); st.rerun()
                else:
                    st.error("⚠️ Incorrect email or password.")

    with tab_signup:
        with st.form("signup_form"):
            name   = st.text_input("👤 Full Name", placeholder="Ahmed Khan")
            email2 = st.text_input("📧 Email", placeholder="you@example.com")
            role   = st.selectbox("👥 I am a", ["Student 🎒","Parent 👨‍👩‍👦","Teacher 👨‍🏫","Admin 🛡️"])
            avatar = st.selectbox("🧑 Choose Avatar", list(AVATARS.keys()))
            grade  = st.selectbox("🏫 Grade", ["-- Select --"]+LEVELS)
            pw     = st.text_input("🔒 Password", type="password", placeholder="Min 6 characters")
            pw2    = st.text_input("🔒 Confirm Password", type="password")
            if st.form_submit_button("Create My Account →", use_container_width=True, type="primary"):
                users = load_json(USERS_FILE)
                if not name or not email2 or not pw:   st.error("Please fill all required fields.")
                elif len(pw) < 6:                      st.error("Password must be at least 6 characters.")
                elif pw != pw2:                        st.error("Passwords don't match.")
                elif email2 in users:                  st.error("Email already registered.")
                else:
                    new_user = {
                        "name": name.strip(), "email": email2.strip(),
                        "password": hash_pw(pw),
                        "role": ("student"  if "Student" in role
                                 else "parent"  if "Parent"  in role
                                 else "teacher" if "Teacher" in role
                                 else "admin"),
                        "avatar": AVATARS[avatar],
                        "grade": grade if grade != "-- Select --" else "Grade 6",
                        "joined": datetime.date.today().isoformat(),
                        "plan": "free", "stats": init_stats(), "badges": [], "is_new": True
                    }
                    users[email2] = new_user
                    save_json(USERS_FILE, users)
                    st.session_state.logged_in = True
                    st.session_state.user = new_user
                    st.success("Account created! Welcome 🎉"); time.sleep(0.5); st.rerun()

    with tab_forgot:
        st.markdown("""
        <div style='background:rgba(13,110,63,0.06);border-radius:10px;padding:12px 14px;
            font-size:13px;color:#0D6E3F;margin-bottom:14px;border:1px solid rgba(13,110,63,0.12)'>
            🔒 Enter your email and a new password to reset your account.
        </div>""", unsafe_allow_html=True)
        with st.form("forgot_form"):
            fp_email = st.text_input("📧 Your registered email")
            fp_new   = st.text_input("🔒 New Password", type="password")
            fp_new2  = st.text_input("🔒 Confirm New Password", type="password")
            if st.form_submit_button("Reset Password →", use_container_width=True, type="primary"):
                users = load_json(USERS_FILE)
                if fp_email not in users:    st.error("⚠️ Email not found.")
                elif len(fp_new) < 6:        st.error("Min 6 characters.")
                elif fp_new != fp_new2:      st.error("Passwords don't match.")
                else:
                    users[fp_email]["password"] = hash_pw(fp_new)
                    save_json(USERS_FILE, users)
                    st.success("✅ Password reset! You can now login.")

    st.markdown("""
    <p style='text-align:center;color:#7A9A7A;font-size:11px;margin-top:20px;font-weight:600'>
        🔒 Secure &nbsp;·&nbsp; 🆓 Free to use &nbsp;·&nbsp; 🇵🇰 Pakistan National Curriculum
    </p>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────
def render_sidebar():
    u = st.session_state.user
    role_info = {
        "student": ("🎒","Student",     "#27A862"),
        "parent":  ("👨‍👩‍👦","Parent",    "#1A8C50"),
        "teacher": ("👨‍🏫","Teacher",    "#C9A84C"),
        "admin":   ("🛡️","Admin",       "#C0392B"),
    }
    r_icon, r_label, r_color = role_info.get(u.get("role","student"),("👤","User","#27A862"))

    with st.sidebar:
        # ── Profile card ──────────────────────────────
        st.markdown(f"""
        <div style='padding:20px 12px 16px;margin-bottom:4px;
            border-bottom:1px solid rgba(201,168,76,0.15)'>
            <div style='position:relative;display:flex;flex-direction:column;align-items:center'>
                <div style='width:68px;height:68px;border-radius:20px;
                    background:linear-gradient(135deg,rgba(201,168,76,0.2),rgba(13,110,63,0.3));
                    display:flex;align-items:center;justify-content:center;
                    font-size:38px;line-height:1;margin-bottom:10px;
                    border:2px solid rgba(201,168,76,0.3);
                    box-shadow:0 4px 20px rgba(0,0,0,0.3)'>
                    {u.get("avatar","👦")}
                </div>
                <div style='font-family:"Sora",sans-serif;font-weight:800;font-size:15px;
                    color:#fff;text-align:center;letter-spacing:-.3px'>{u["name"]}</div>
                <div style='display:inline-flex;align-items:center;gap:5px;margin-top:5px;
                    background:rgba(255,255,255,0.07);border-radius:99px;
                    padding:3px 10px;border:1px solid rgba(201,168,76,0.2)'>
                    <span style='font-size:12px'>{r_icon}</span>
                    <span style='font-size:11px;font-weight:700;color:{r_color}'>{r_label}</span>
                    {"<span style='font-size:10px;color:rgba(255,255,255,0.4)'>·</span><span style='font-size:11px;color:rgba(255,255,255,0.55);font-weight:600'>" + u.get("grade","") + "</span>" if u.get("grade") else ""}
                </div>
            </div>
            <div style='display:flex;justify-content:center;gap:0;margin-top:14px;
                background:rgba(0,0,0,0.25);border-radius:12px;
                border:1px solid rgba(201,168,76,0.12);overflow:hidden'>
                <div style='flex:1;text-align:center;padding:9px 6px;
                    border-right:1px solid rgba(201,168,76,0.1)'>
                    <div style='font-family:"Sora",sans-serif;font-size:17px;font-weight:900;
                        color:#E8C96A'>{u.get("stats",{}).get("total",0)}</div>
                    <div style='font-size:9px;color:rgba(255,255,255,0.4);
                        text-transform:uppercase;letter-spacing:.8px;font-weight:700'>Qs</div>
                </div>
                <div style='flex:1;text-align:center;padding:9px 6px;
                    border-right:1px solid rgba(201,168,76,0.1)'>
                    <div style='font-family:"Sora",sans-serif;font-size:17px;font-weight:900;
                        color:#E8C96A'>{len(u.get("badges",[]))}</div>
                    <div style='font-size:9px;color:rgba(255,255,255,0.4);
                        text-transform:uppercase;letter-spacing:.8px;font-weight:700'>Badges</div>
                </div>
                <div style='flex:1;text-align:center;padding:9px 6px'>
                    <div style='font-family:"Sora",sans-serif;font-size:17px;font-weight:900;
                        color:#E8C96A'>{u.get("stats",{}).get("streak",0)}</div>
                    <div style='font-size:9px;color:rgba(255,255,255,0.4);
                        text-transform:uppercase;letter-spacing:.8px;font-weight:700'>Streak</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        role = u.get("role", "student")
        cur  = st.session_state.page

        def nav_btn(icon, label, key, uid=""):
            """uid makes widget key unique when same page key appears in multiple role blocks."""
            btn_type = "primary" if cur == key else "secondary"
            if st.button(f"{icon}  {label}", key=f"nav_{key}{uid}",
                         use_container_width=True, type=btn_type):
                st.session_state.page = key; st.rerun()

        def section_label(text):
            st.markdown(
                f"<div style='font-size:10px;font-weight:800;"
                f"color:rgba(255,255,255,0.38);text-transform:uppercase;"
                f"letter-spacing:1.2px;padding:12px 4px 3px'>  {text}</div>",
                unsafe_allow_html=True
            )

        # ── DASHBOARD ────────────────────────────────────────────
        section_label("📊 Dashboard")
        nav_btn("🏠", "Home",            "home")
        nav_btn("📚", "Syllabus",        "syllabus")
        nav_btn("🎨", "Image Generator", "image")
        nav_btn("📈", "My Progress",     "progress")

        # ── STUDENT ───────────────────────────────────────────
        section_label("🎒 Student")
        nav_btn("💬", "Chat Tutor",    "chat",    "_s")
        nav_btn("📝", "Practice Quiz", "quiz")
        nav_btn("👥", "Friendz Quiz",  "friends")
        nav_btn("🕐", "Chat History",  "history", "_s")
        nav_btn("🏆", "Badges",        "badges")

        # ── TEACHER ───────────────────────────────────────────
        section_label("👨‍🏫 Teacher")
        nav_btn("📋", "Create Homework",     "homework", "_t")
        nav_btn("📊", "Student Performance", "admin",    "_t")
        nav_btn("💬", "Chat Tutor",          "chat",     "_t")

        # ── ADMIN ─────────────────────────────────────────────
        section_label("🛡️ Admin")
        nav_btn("📊", "Student Performance", "admin",    "_a")
        nav_btn("🕐", "Chat History",        "history",  "_a")
        nav_btn("📋", "Homework Tracker",    "homework", "_a")
        nav_btn("💬", "Chat Tutor",          "chat",     "_a")

        # ── ACCOUNT ───────────────────────────────────────────
        section_label("👤 Account")
        nav_btn("👤", "Profile", "profile")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("🚪  Logout", key="logout_btn", use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()


# ─────────────────────────────────────────────────────────────────
# HOME PAGE
# ─────────────────────────────────────────────────────────────────
def page_home():
    u   = st.session_state.user
    sub = st.session_state.subject
    col = SUBJECTS.get(sub, SUBJECTS["Maths"])["color"]
    h   = datetime.datetime.now().hour
    greet = "Good morning" if h < 12 else "Good afternoon" if h < 17 else "Good evening"

    # ── Onboarding for new users ──────────────────────────────
    if u.get("is_new") and not st.session_state.get("onboarding_done"):
        step = st.session_state.get("onboard_step", 1)
        steps = [
            {"emoji":"🎓","title":f"Welcome to ZM Academy, {u['name'].split()[0]}! 🎉",
             "body":"Pakistan's <b>AI-powered study app</b> for Grades 1–10, O Level & A Level.<br><br>Your personal AI tutor <b>Ustad</b> is here to help!","btn":"Next →"},
            {"emoji":"💬","title":"Everything you need to study",
             "body":"<b>💬 Chat Tutor</b> — Ask any question in any subject<br><br><b>📝 Practice Quiz</b> — Custom quizzes with difficulty levels<br><br><b>📚 My Syllabus</b> — Full Cambridge curriculum<br><br><b>🎨 Image Generator</b> — AI draws educational diagrams","btn":"Next →"},
            {"emoji":"🏆","title":"Earn Badges & Challenge Friends",
             "body":"Earn <b>11 achievement badges</b> as you study.<br><br>Use <b>👥 Friends Quiz</b> to compete with up to 3 friends on the same quiz — and see who tops the leaderboard!","btn":"🚀 Start Learning!"},
        ]
        s = steps[step-1]
        _, c, _ = st.columns([1,2,1])
        with c:
            dots = "".join(
                f"<span style='display:inline-block;width:9px;height:9px;border-radius:50%;"
                f"background:{'#E8C96A' if i+1==step else 'rgba(255,255,255,0.2)'};margin:0 3px'></span>"
                for i in range(3)
            )
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#061A0E,#0D6E3F);border-radius:24px;
                padding:32px 28px;color:#fff;text-align:center;margin-top:20px;
                border:1px solid rgba(201,168,76,0.25);
                box-shadow:0 16px 48px rgba(6,26,14,0.5)'>
                <div style='margin-bottom:14px'>{dots}</div>
                <div style='font-size:56px;margin-bottom:14px'>{s['emoji']}</div>
                <div style='font-family:"Sora",sans-serif;font-size:22px;font-weight:900;
                    margin-bottom:14px;letter-spacing:-.5px'>{s['title']}</div>
                <div style='font-size:14px;opacity:.85;line-height:1.8'>{s['body']}</div>
            </div>""", unsafe_allow_html=True)
            st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
            if st.button(s["btn"], use_container_width=True, type="primary", key=f"ob_{step}"):
                if step < 3:
                    st.session_state.onboard_step = step+1; st.rerun()
                else:
                    users = load_json(USERS_FILE)
                    if u["email"] in users:
                        users[u["email"]]["is_new"] = False
                        save_json(USERS_FILE, users)
                        st.session_state.user = users[u["email"]]
                    st.session_state.onboarding_done = True; st.rerun()
            if step > 1 and st.button("← Back", key=f"ob_back_{step}", use_container_width=True):
                st.session_state.onboard_step = step-1; st.rerun()
            if st.button("Skip intro", key="skip_ob", use_container_width=True):
                users = load_json(USERS_FILE)
                if u["email"] in users:
                    users[u["email"]]["is_new"] = False
                    save_json(USERS_FILE, users)
                    st.session_state.user = users[u["email"]]
                st.session_state.onboarding_done = True; st.rerun()
        return

    # ── Hero banner ───────────────────────────────────────────
    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#061A0E 0%,#0D6E3F 50%,#0A5A32 100%);
        border-radius:20px;padding:24px 26px;margin-bottom:20px;color:#fff;
        border:1px solid rgba(201,168,76,0.2);
        box-shadow:0 8px 32px rgba(6,26,14,0.25);position:relative;overflow:hidden'>
        <div style='position:absolute;top:-30px;right:-30px;width:160px;height:160px;
            border-radius:50%;background:radial-gradient(circle,rgba(201,168,76,0.15),transparent 70%)'></div>
        <div style='position:absolute;bottom:-20px;left:20px;width:100px;height:100px;
            border-radius:50%;background:radial-gradient(circle,rgba(39,168,98,0.15),transparent 70%)'></div>
        <div style='display:flex;align-items:center;gap:18px;position:relative'>
            <div style='width:64px;height:64px;border-radius:18px;
                background:rgba(255,255,255,0.1);display:flex;align-items:center;
                justify-content:center;font-size:36px;flex-shrink:0;
                border:1.5px solid rgba(201,168,76,0.3)'>
                {u.get('avatar','👦')}</div>
            <div>
                <div style='font-family:"Sora",sans-serif;font-size:22px;font-weight:900;
                    letter-spacing:-.5px;line-height:1.2'>
                    {greet}, {u['name'].split()[0]}! 👋</div>
                <div style='font-size:13px;opacity:.75;margin-top:5px;font-weight:500'>
                    🇵🇰 Pakistan's #1 AI Study Platform &nbsp;·&nbsp; Ready to learn today?</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    stats = u.get("stats", {})
    if stats.get("lastDate","") != datetime.date.today().isoformat():
        st.markdown("""<div class='reminder'>🔔 <b>Daily Reminder:</b> You haven't studied today! Even 15 minutes makes a difference 💪</div>""", unsafe_allow_html=True)

    # ── Stats row ─────────────────────────────────────────────
    c1,c2,c3,c4 = st.columns(4)
    for col_w, icon, val, lbl, accent in [
        (c1,"❓", stats.get("total",0),          "Questions", "#0D6E3F"),
        (c2,"🔥", f"{stats.get('streak',0)}d",   "Streak",    "#C0392B"),
        (c3,"🏆", len(u.get("badges",[])),        "Badges",    "#C9A84C"),
        (c4,"📝", stats.get("quizzes_done",0),    "Quizzes",   "#1A56C4"),
    ]:
        with col_w:
            st.markdown(f"""
            <div class='stat-card'>
                <div style='font-size:22px;margin-bottom:4px'>{icon}</div>
                <div style='font-family:"Sora",sans-serif;font-size:26px;font-weight:900;
                    color:{accent};line-height:1'>{val}</div>
                <div class='stat-lbl'>{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    # ── Quick access features ─────────────────────────────────
    st.markdown(f"""<div style='font-family:"Sora",sans-serif;font-size:16px;font-weight:800;
        color:#0D1F0D;margin-bottom:12px;letter-spacing:-.3px'>⚡ Quick Access</div>""",
        unsafe_allow_html=True)
    fa, fb, fc, fd = st.columns(4)
    for col_w, icon, label, page, g, accent in [
        (fa,"💬","Chat Tutor",    "chat",    "#0D6E3F","#27A862"),
        (fb,"📝","Practice Quiz", "quiz",    "#0A2F6B","#1A56C4"),
        (fc,"👥","Friendz Quiz",  "friends", "#4A0D6B","#7C3AED"),
        (fd,"🎨","Image Gen",     "image",   "#7A5C00","#C9A84C"),
    ]:
        with col_w:
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,{g}12,{g}06);
                border:1.5px solid {g}25;border-radius:16px;
                padding:16px 10px;text-align:center;
                transition:box-shadow .2s;'>
                <div style='font-size:26px;margin-bottom:6px'>{icon}</div>
                <div style='font-size:11px;font-weight:800;color:{accent};
                    text-transform:uppercase;letter-spacing:.5px'>{label}</div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"Open {label}", key=f"home_go_{page}", use_container_width=True):
                st.session_state.page = page; st.rerun()

    # ── Word of the Day ───────────────────────────────────────
    if not st.session_state.wod_loaded:
        with st.spinner("Loading Word of the Day..."):
            grade = u.get("grade","Grade 6")
            raw = call_ai(
                [{"role":"user","content":
                  f"Give ONE interesting English word suitable for {grade} students in Pakistan. "
                  f'Return ONLY this JSON: {{"word":"...","urdu":"...","meaning":"...","example":"...","tip":"..."}}'}],
                "Vocabulary teacher. Return ONLY valid JSON. No markdown.",
            )
            try:
                clean = raw.replace("```json","").replace("```","").strip()
                st.session_state.word_of_day = json.loads(clean)
            except:
                st.session_state.word_of_day = {
                    "word":"Perseverance","urdu":"ثابت قدمی",
                    "meaning":"Continued effort despite difficulties",
                    "example":"Success comes to those with perseverance.",
                    "tip":"Use this word in your next essay!"
                }
            st.session_state.wod_loaded = True

    if st.session_state.word_of_day:
        w = st.session_state.word_of_day
        st.markdown(f"""
        <div class='word-card'>
            <div style='font-size:11px;font-weight:800;opacity:.5;text-transform:uppercase;
                letter-spacing:1px;margin-bottom:8px'>📖 Word of the Day</div>
            <div style='display:flex;align-items:baseline;gap:12px;flex-wrap:wrap'>
                <span style='font-family:"Baloo 2",cursive;font-size:26px;font-weight:800;color:#FFD700'>{w.get('word','')}</span>
                <span style='font-size:13px;opacity:.65'>— {w.get('urdu','')}</span>
            </div>
            <div style='font-size:13px;opacity:.75;margin-top:6px'>{w.get('meaning','')}</div>
            <div style='font-size:12px;opacity:.55;margin-top:4px;font-style:italic'>"{w.get('example','')}"</div>
            <div style='font-size:11px;color:#FFD700;margin-top:6px'>💡 {w.get('tip','')}</div>
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# CHAT / AI TUTOR
# ─────────────────────────────────────────────────────────────────
def build_system(u, sub, lvl):
    return f"""You are Ustad, a warm and encouraging homework tutor for Pakistani students.
Student: {u['name']} | Role: {'Parent' if u.get('role')=='parent' else 'Student'} | Class: {lvl} | Subject: {sub}

Teaching rules:
- Adapt complexity to {lvl}: Grade 1-3=very simple+emojis; Grade 4-5=simple+examples; Grade 6-8=structured steps; O Level=exam-focused; A Level=university depth
{f'- Reply in Urdu script. Use English only for technical terms.' if sub=='Urdu' else ''}
{f'- User is a parent. Explain how to help their child understand.' if u.get('role')=='parent' else ''}
- For Maths/Physics/Chemistry: ALWAYS show step-by-step working
- Use Pakistani curriculum context (FBISE, Cambridge Pakistan, local examples)
- Be warm, positive, and end with encouragement or a follow-up question"""

def save_chat_session(sub, lvl):
    hist  = load_json(HISTORY_FILE)
    email = st.session_state.user["email"]
    if email not in hist: hist[email] = []
    sid = st.session_state.session_id or datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.session_id = sid
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    ex = next((s for s in hist[email] if s["id"]==sid), None)
    if ex:
        ex["messages"] = st.session_state.chat_messages
        ex["updated"]  = now
    else:
        hist[email].append({
            "id":sid,"subject":sub,"level":lvl,
            "messages":st.session_state.chat_messages,
            "created":now,"updated":now
        })
    save_json(HISTORY_FILE, hist)

def page_chat():
    u = st.session_state.user
    st.markdown("<div class='section-header'>💬 Chat Tutor — Ask Ustad Anything</div>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        sub = st.selectbox("📚 Subject", list(SUBJECTS.keys()),
                           index=list(SUBJECTS.keys()).index(st.session_state.subject))
    with c2:
        lvl_idx = get_level_index(u.get("grade","Grade 6"))
        lvl = st.selectbox("🏫 Grade", LEVELS, index=lvl_idx)
    st.session_state.subject = sub

    if st.button("🆕 New Chat", type="secondary"):
        st.session_state.chat_messages = []
        st.session_state.session_id    = None
        st.rerun()

    st.markdown("<div style='font-size:11px;font-weight:800;color:#aaa;text-transform:uppercase;letter-spacing:1px;margin:10px 0 6px'>⚡ Quick Questions</div>", unsafe_allow_html=True)
    qc = st.columns(2)
    for i, p in enumerate(QUICK_PROMPTS.get(sub, [])):
        with qc[i%2]:
            if st.button(p, key=f"qp{i}", use_container_width=True):
                st.session_state.chat_messages.append({"role":"user","content":p})
                with st.spinner("Ustad is thinking... 🤔"):
                    reply = call_ai(st.session_state.chat_messages, build_system(u, sub, lvl))
                st.session_state.chat_messages.append({"role":"assistant","content":reply})
                bump_stats(sub); save_chat_session(sub, lvl); st.rerun()

    if not st.session_state.chat_messages:
        st.info(f"👋 Assalam-o-Alaikum {u['name'].split()[0]}! I'm Ustad, your {sub} tutor for {lvl}. Ask me anything!")

    for m in st.session_state.chat_messages:
        if m["role"] == "user":
            st.markdown(f"<div class='msg-lbl msg-lbl-r'>You</div><div class='msg-user'>{m['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='msg-lbl'>🎓 Ustad</div><div class='msg-bot'>{m['content']}</div>", unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        ph  = "یہاں سوال لکھیں..." if sub=="Urdu" else f"Ask your {sub} question here..."
        txt = st.text_area("Q", placeholder=ph, height=80, label_visibility="collapsed")
        c1f, c2f = st.columns([3,1])
        with c1f:
            send = st.form_submit_button("📤 Send", use_container_width=True, type="primary")
        with c2f:
            clear = st.form_submit_button("🗑️ Clear", use_container_width=True)
        if clear:
            st.session_state.chat_messages = []
            st.session_state.session_id    = None
            st.rerun()
        if send and txt.strip():
            st.session_state.chat_messages.append({"role":"user","content":txt.strip()})
            with st.spinner("Ustad is thinking... 🤔"):
                reply = call_ai(st.session_state.chat_messages, build_system(u, sub, lvl))
            st.session_state.chat_messages.append({"role":"assistant","content":reply})
            bump_stats(sub); save_chat_session(sub, lvl); st.rerun()


# ═════════════════════════════════════════════════════════════════
# 1. PRACTICE QUIZ — Enhanced with topic, difficulty, num questions
# ═════════════════════════════════════════════════════════════════
def page_quiz():
    u = st.session_state.user
    st.markdown("<div class='section-header orange'>📝 Practice Quiz</div>", unsafe_allow_html=True)

    q = st.session_state.quiz

    # ── Results screen ────────────────────────────────────────
    if q is not None and q["done"]:
        total = len(q["questions"]); score = q["score"]
        pct   = int((score/total)*100)
        emoji = "🏆" if pct>=80 else "👍" if pct>=60 else "💪"
        col   = "#059669" if pct>=80 else "#F59E0B" if pct>=60 else "#E8472A"

        st.markdown(f"""
        <div style='text-align:center;background:#fff;border-radius:20px;padding:28px;
            box-shadow:0 4px 20px rgba(0,0,0,0.08);margin-bottom:18px'>
            <div style='font-size:56px'>{emoji}</div>
            <h2 style='font-family:"Baloo 2",cursive;font-size:26px;font-weight:800;color:#1A1A2E'>
                Quiz Complete!</h2>
            <div style='font-size:48px;font-weight:900;color:{col};margin:8px 0'>{score}/{total}</div>
            <div style='font-size:15px;color:#666'>
                {pct}% — {"Excellent! ⭐" if pct>=80 else "Good effort! 📚" if pct>=60 else "Keep practicing! 💪"}
            </div>
            <div style='font-size:13px;color:#999;margin-top:4px'>
                Topic: {q.get("topic","Custom")} · {q.get("difficulty","Medium")} · {q.get("sub","")} {q.get("lvl","")}
            </div>
        </div>""", unsafe_allow_html=True)

        # Update quiz count stat
        users = load_json(USERS_FILE)
        eu    = users.get(u["email"], u)
        eu.setdefault("stats", init_stats())
        eu["stats"]["quizzes_done"] = eu["stats"].get("quizzes_done",0) + 1
        eu, new_b = check_badges(eu)
        users[u["email"]] = eu
        save_json(USERS_FILE, users)
        st.session_state.user = eu
        for b in new_b:
            st.toast(f"🏆 Badge: {b['icon']} {b['name']}!", icon="🎉")

        st.markdown("### 📋 Review Answers")
        for i,(ques,ans) in enumerate(zip(q["questions"],q["answers"])):
            correct = ans["chosen"] == ques["answer"]
            bg     = "#F0FDF4" if correct else "#FFF1EE"
            border = "#059669" if correct else "#E8472A"
            wrong_line = "" if correct else f'<div style="font-size:13px;color:#059669;margin-top:2px">✅ Correct: <b>{ques["answer"]}</b></div>'
            st.markdown(f"""
            <div style='background:{bg};border:1.5px solid {border};border-radius:12px;
                padding:14px 16px;margin-bottom:10px;color:#1A1A2E'>
                <div style='font-weight:700;font-size:14px'>Q{i+1}. {ques["q"]}</div>
                <div style='font-size:13px;margin-top:5px'>
                    Your answer: <b>{ans["chosen"]}</b> {"✅" if correct else "❌"}
                </div>
                {wrong_line}
                <div style='font-size:12px;color:#555;margin-top:5px;padding:6px 10px;background:rgba(0,0,0,.04);border-radius:8px'>
                    💡 {ques.get("explanation","")}
                </div>
            </div>""", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 New Quiz", use_container_width=True, type="primary"):
                st.session_state.quiz = None; st.rerun()
        with col2:
            if st.button("👥 Challenge Friends", use_container_width=True):
                st.session_state.page = "friends"; st.rerun()
        return

    # ── Active quiz ───────────────────────────────────────────
    if q is not None and not q["done"]:
        info    = SUBJECTS.get(q.get("sub","Maths"), SUBJECTS["Maths"])
        current = q["current"]
        ques    = q["questions"][current]
        pct_bar = int((current/len(q["questions"]))*100)

        # Header strip
        st.markdown(f"""
        <div style='background:{info["color"]}18;border-radius:14px;padding:12px 16px;
            margin-bottom:14px;display:flex;justify-content:space-between;align-items:center'>
            <div>
                <span style='font-weight:800;color:{info["color"]}'>{info["emoji"]} {q.get("sub","")} Quiz</span>
                <span style='font-size:12px;color:#888;margin-left:10px'>{q.get("topic","")} · {q.get("difficulty","")}</span>
            </div>
            <span style='font-weight:700;color:{info["color"]}'>Score: {q["score"]}/{current}</span>
        </div>""", unsafe_allow_html=True)

        # Progress bar
        st.markdown(f"""
        <div style='display:flex;justify-content:space-between;font-size:12px;color:#888;margin-bottom:4px'>
            <span>Question {current+1} of {len(q["questions"])}</span>
            <span>{pct_bar}% complete</span>
        </div>
        <div class='prog-bar'><div class='prog-fill' style='width:{pct_bar}%;background:{info["color"]}'></div></div>
        <br>""", unsafe_allow_html=True)

        # Question
        st.markdown(f"""
        <div style='background:#fff;border-radius:16px;padding:18px 20px;margin-bottom:14px;
            box-shadow:0 3px 16px rgba(0,0,0,0.07);font-weight:800;font-size:15px;
            color:#1A1A2E;line-height:1.55;border-left:5px solid {info["color"]}'>
            Q{current+1}. {ques["q"]}
        </div>""", unsafe_allow_html=True)

        # Options as styled buttons
        for opt in ques["options"]:
            if st.button(opt, key=f"opt_{current}_{opt}", use_container_width=True):
                q["answers"].append({"chosen":opt})
                if opt == ques["answer"]:
                    q["score"] += 1; st.toast("✅ Correct!", icon="🎉")
                else:
                    st.toast(f"❌ Correct: {ques['answer']}", icon="💡")
                q["current"] += 1
                if q["current"] >= len(q["questions"]): q["done"] = True
                st.session_state.quiz = q; st.rerun()
        return

    # ── Quiz setup (no active quiz) ───────────────────────────
    st.markdown("""
    <div style='background:#EFF4FF;border-radius:14px;padding:14px 18px;
        margin-bottom:18px;font-size:13px;color:#1B4FD8;border-left:4px solid #2563EB'>
        📝 <b>Custom Quiz Generator</b> — Enter any topic, pick your difficulty and number of questions!
    </div>""", unsafe_allow_html=True)

    with st.container():
        st.markdown("#### 🔧 Quiz Settings")

        c1, c2 = st.columns(2)
        with c1:
            quiz_sub = st.selectbox("📚 Subject", list(SUBJECTS.keys()), key="quiz_sub")
        with c2:
            lvl_idx  = get_level_index(u.get("grade","Grade 6"))
            quiz_lvl = st.selectbox("🏫 Grade", LEVELS, index=lvl_idx, key="quiz_lvl")

        quiz_topic = st.text_input(
            "✏️ Topic (optional — leave blank for general quiz)",
            placeholder="e.g. Photosynthesis, Quadratic equations, World War II, Pythagoras...",
            key="quiz_topic_input"
        )

        c3, c4 = st.columns(2)
        with c3:
            difficulty = st.selectbox("🎯 Difficulty Level", ["Easy","Medium","Hard"], index=1, key="quiz_diff")
        with c4:
            num_qs = st.selectbox("🔢 Number of Questions", [5,10,15,20], index=0, key="quiz_num")

        # Difficulty description
        diff_info = {
            "Easy":   ("🟢","Straightforward recall questions. Perfect for revision."),
            "Medium": ("🟡","Mixed conceptual and application questions."),
            "Hard":   ("🔴","Challenging analytical and higher-order thinking questions."),
        }
        d_icon, d_text = diff_info[difficulty]
        st.markdown(f"""
        <div style='background:#F8F9FA;border-radius:10px;padding:10px 14px;
            font-size:12px;color:#555;margin-bottom:14px'>
            {d_icon} <b>{difficulty}:</b> {d_text}
        </div>""", unsafe_allow_html=True)

        if st.button("🚀 Generate Quiz", use_container_width=True, type="primary", key="gen_quiz_btn"):
            topic_str = quiz_topic.strip() if quiz_topic.strip() else f"{quiz_sub} general topics"
            with st.spinner(f"✨ Generating {num_qs} {difficulty} questions on '{topic_str}'..."):
                raw = call_ai(
                    [{"role":"user","content":
                      f"Create exactly {num_qs} {difficulty}-level multiple choice questions "
                      f"about '{topic_str}' for {quiz_lvl} {quiz_sub} students in Pakistan. "
                      f"Easy=basic recall, Medium=understanding+application, Hard=analysis+evaluation. "
                      f"Return ONLY raw JSON: "
                      f'{{"questions":[{{"q":"question text","options":["A. option","B. option","C. option","D. option"],"answer":"A. option","explanation":"why"}}]}}'}],
                    "Quiz generator. Return ONLY valid raw JSON. No backticks. No markdown.", 2000
                )
            try:
                clean = raw.replace("```json","").replace("```","").strip()
                data  = json.loads(clean)
                st.session_state.quiz = {
                    "questions": data["questions"][:num_qs],
                    "current":0, "score":0, "answers":[], "done":False,
                    "sub":quiz_sub, "lvl":quiz_lvl,
                    "topic":topic_str, "difficulty":difficulty
                }
                st.rerun()
            except:
                st.error("⚠️ Could not generate quiz. Please try again with a different topic.")
                with st.expander("Debug info"): st.code(raw[:500])


# ═════════════════════════════════════════════════════════════════
# 4. FRIENDS GROUP QUIZ — Session-based leaderboard
# ═════════════════════════════════════════════════════════════════
def page_friends():
    u = st.session_state.user
    st.markdown("<div class='section-header purple'>👥 Friends Group Quiz</div>", unsafe_allow_html=True)

    grp = st.session_state.group_session

    # ── Results / Leaderboard ─────────────────────────────────
    if grp is not None and grp.get("done"):
        st.markdown("## 🏆 Final Leaderboard")
        players = sorted(grp["players"], key=lambda p: p["score"], reverse=True)
        rank_icons = ["🥇","🥈","🥉","4️⃣"]
        for i, p in enumerate(players):
            total = len(grp["questions"])
            pct   = int((p["score"]/total)*100)
            st.markdown(f"""
            <div class='lb-row'>
                <span class='lb-rank'>{rank_icons[i]}</span>
                <span class='lb-name'>{p['name']} {p['avatar']}</span>
                <span style='font-size:12px;color:#888'>{pct}%</span>
                <span class='lb-score'>{p['score']}/{total}</span>
            </div>""", unsafe_allow_html=True)

        winner = players[0]
        st.markdown(f"""
        <div style='text-align:center;background:linear-gradient(135deg,#FFF8E7,#FFFBF0);
            border-radius:16px;padding:20px;margin-top:14px;border:2px solid #F5CC4A'>
            <div style='font-size:40px'>🎉</div>
            <div style='font-family:"Baloo 2",cursive;font-size:20px;font-weight:800;color:#A07820'>
                {winner['name']} wins with {winner['score']}/{len(grp['questions'])}!
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Play Again", use_container_width=True, type="primary"):
            st.session_state.group_session = None; st.rerun()
        return

    # ── Active group quiz — player turn ──────────────────────
    if grp is not None and not grp.get("done"):
        pidx    = grp["current_player"]
        player  = grp["players"][pidx]
        qidx    = player.get("q_index", 0)
        total_q = len(grp["questions"])

        # Check if this player is done
        if qidx >= total_q:
            # Move to next player
            grp["current_player"] = pidx + 1
            if grp["current_player"] >= len(grp["players"]):
                grp["done"] = True
            st.session_state.group_session = grp; st.rerun()
            return

        ques = grp["questions"][qidx]

        # Scoreboard strip
        st.markdown("<div style='display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap'>", unsafe_allow_html=True)
        for i, p in enumerate(grp["players"]):
            active = (i == pidx)
            bg     = "#E8472A" if active else "#F0F0F5"
            color  = "#fff"    if active else "#555"
            st.markdown(f"""
            <div style='background:{bg};color:{color};border-radius:99px;
                padding:6px 14px;font-size:12px;font-weight:800;display:inline-block'>
                {p['avatar']} {p['name']}: {p['score']}/{total_q} {"← NOW" if active else ""}
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#7C3AED18,#A78BFA18);border-radius:14px;
            padding:12px 16px;margin-bottom:10px;font-size:12px;color:#7C3AED;font-weight:700'>
            🎮 {player['name']}'s turn — Q{qidx+1} of {total_q}
        </div>""", unsafe_allow_html=True)

        pct_bar = int((qidx/total_q)*100)
        st.markdown(f"""<div class='prog-bar'><div class='prog-fill'
            style='width:{pct_bar}%;background:#7C3AED'></div></div><br>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div style='background:#fff;border-radius:16px;padding:18px 20px;margin-bottom:14px;
            box-shadow:0 3px 16px rgba(0,0,0,0.07);font-weight:800;font-size:15px;
            color:#1A1A2E;border-left:5px solid #7C3AED'>
            Q{qidx+1}. {ques["q"]}
        </div>""", unsafe_allow_html=True)

        for opt in ques["options"]:
            if st.button(opt, key=f"grp_{pidx}_{qidx}_{opt}", use_container_width=True):
                if opt == ques["answer"]:
                    grp["players"][pidx]["score"] += 1
                    st.toast("✅ Correct!", icon="🎉")
                else:
                    st.toast(f"❌ Correct: {ques['answer']}", icon="💡")
                grp["players"][pidx]["q_index"] = qidx + 1
                st.session_state.group_session = grp; st.rerun()
        return

    # ── Group setup ───────────────────────────────────────────
    st.markdown("""
    <div style='background:#F5F0FF;border-radius:14px;padding:14px 18px;
        margin-bottom:18px;font-size:13px;color:#5B21B6;border-left:4px solid #7C3AED'>
        👥 <b>Friends Group Quiz</b> — Take turns answering the same questions. Whoever scores highest wins!
    </div>""", unsafe_allow_html=True)

    num_friends = st.selectbox("👥 Number of players (including you)", [2,3,4], index=0)

    st.markdown("#### 🎮 Player Names")
    player_names = [u["name"]]  # first player is always the current user
    for i in range(1, num_friends):
        name = st.text_input(f"Player {i+1} name", placeholder=f"Friend {i}", key=f"friend_name_{i}")
        player_names.append(name.strip() if name.strip() else f"Player {i+1}")

    st.markdown("#### 📚 Quiz Settings")
    c1, c2 = st.columns(2)
    with c1:
        grp_sub  = st.selectbox("Subject", list(SUBJECTS.keys()), key="grp_sub")
    with c2:
        lvl_idx  = get_level_index(u.get("grade","Grade 6"))
        grp_lvl  = st.selectbox("Grade", LEVELS, index=lvl_idx, key="grp_lvl")

    grp_topic = st.text_input("Topic (optional)", placeholder="Any topic...", key="grp_topic")
    c3, c4 = st.columns(2)
    with c3:
        grp_diff = st.selectbox("Difficulty", ["Easy","Medium","Hard"], index=1, key="grp_diff")
    with c4:
        grp_num  = st.selectbox("Questions per player", [5,10], index=0, key="grp_num")

    if st.button("🚀 Start Group Quiz", use_container_width=True, type="primary"):
        topic_str = grp_topic.strip() if grp_topic.strip() else f"{grp_sub} general"
        with st.spinner(f"Generating {grp_num} questions..."):
            raw = call_ai(
                [{"role":"user","content":
                  f"Create exactly {grp_num} {grp_diff}-level MCQ questions about '{topic_str}' "
                  f"for {grp_lvl} {grp_sub} students. "
                  f'Return ONLY raw JSON: {{"questions":[{{"q":"...","options":["A. ...","B. ...","C. ...","D. ..."],"answer":"A. ...","explanation":"..."}}]}}'}],
                "Quiz generator. Return ONLY valid raw JSON.", 2000
            )
        try:
            clean = raw.replace("```json","").replace("```","").strip()
            data  = json.loads(clean)
            questions = data["questions"][:grp_num]
            avatars   = ["👦","👧","🧑","👨","👩","🧒"]
            players   = [
                {"name":n, "avatar":avatars[i%len(avatars)],
                 "score":0, "q_index":0}
                for i,n in enumerate(player_names)
            ]
            st.session_state.group_session = {
                "questions":questions, "players":players,
                "current_player":0, "done":False,
                "topic":topic_str, "difficulty":grp_diff
            }
            st.rerun()
        except:
            st.error("⚠️ Could not generate quiz. Please try again.")


# ═════════════════════════════════════════════════════════════════
# 5. IMAGE GENERATOR — Upgraded with styles, gallery grid, download
# ═════════════════════════════════════════════════════════════════
def page_image():
    u = st.session_state.user
    st.markdown("<div class='section-header purple'>🎨 AI Image Generator</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style='background:#F5F0FF;border:1.5px solid #7C3AED;border-radius:12px;
        padding:12px 16px;margin-bottom:16px;font-size:13px;color:#5B21B6'>
        🖌️ Claude AI draws a <b>custom SVG diagram</b> — choose your style!
        Generation takes 20–40 seconds. Works fully offline.
    </div>""", unsafe_allow_html=True)

    # ── Controls ──────────────────────────────────────────────
    c1, c2 = st.columns(2)
    with c1:
        img_sub = st.selectbox("📚 Subject", list(SUBJECTS.keys()), key="img_sub")
    with c2:
        lvl_idx = get_level_index(u.get("grade","Grade 6"))
        img_lvl = st.selectbox("🏫 Grade", LEVELS, index=lvl_idx, key="img_lvl")

    style_choice = st.selectbox("🎨 Art Style", list(IMAGE_STYLES.keys()), key="img_style")
    style_hint   = IMAGE_STYLES[style_choice]

    # Style preview chips
    style_colors = {
        "📐 Educational Diagram":"#2563EB",
        "🎨 Cartoon":            "#E8472A",
        "🎌 Anime Style":        "#7C3AED",
        "🤖 AI Art":             "#059669",
        "🔬 Realistic / Scientific":"#B45309",
    }
    sc = style_colors.get(style_choice,"#666")
    st.markdown(f"""
    <div style='background:{sc}18;border:1.5px solid {sc}44;border-radius:10px;
        padding:8px 14px;font-size:12px;color:{sc};font-weight:700;margin-bottom:12px'>
        {style_choice} — {style_hint[:60]}...
    </div>""", unsafe_allow_html=True)

    prompt = st.text_area(
        "📝 Describe what you want to see",
        placeholder=(
            "e.g. Diagram showing how photosynthesis works with labeled parts\n"
            "e.g. Solar system with all 8 planets in order\n"
            "e.g. Water cycle showing evaporation, clouds and rain\n"
            "e.g. Human heart with blood flow direction"
        ),
        height=100, key="img_prompt"
    )

    if st.button("🎨 Generate Image", use_container_width=True, type="primary"):
        if not prompt.strip():
            st.warning("Please enter a description first!")
            return

        prog = st.progress(0,  text="🎨 Step 1/4 — Planning your diagram...")
        time.sleep(0.5)
        prog.progress(20, text="✏️ Step 2/4 — Drawing shapes and structure...")
        time.sleep(0.5)
        prog.progress(45, text="🎨 Step 3/4 — Adding colors, labels and arrows...")

        system_msg = (
            "You are an expert SVG illustrator who creates educational diagrams. "
            "STRICT OUTPUT RULES:\n"
            "1. Output ONLY the SVG code. No markdown. No backticks. No explanations.\n"
            "2. Start with exactly: <svg\n"
            "3. End with exactly: </svg>\n"
            f"4. Use: xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 700 500\" width=\"700\" height=\"500\"\n"
            "5. Include <defs> with at least 3 linearGradient definitions.\n"
            "6. Bold title at top (y=35, font-size=24, font-weight=bold, text-anchor=middle, x=350).\n"
            "7. BRIGHT colors — use gradient fills on all major shapes.\n"
            "8. Include 20+ visual elements: shapes, labels, arrows.\n"
            f"9. Style: {style_hint}\n"
            "10. Every component must have a clear text label.\n"
            "11. Make it look like a professional educational poster.\n"
            "12. DO NOT use any xlink:href or external images."
        )
        user_msg = (
            f"Create a detailed colorful educational SVG illustration:\n"
            f"TOPIC: {prompt}\nSUBJECT: {img_sub}\nLEVEL: {img_lvl}\nSTYLE: {style_hint}\n\n"
            f"Include: gradient background, bold title, labeled components, arrows.\n"
            f"Output ONLY the SVG. Start with <svg and end with </svg>."
        )

        raw = call_ai_svg([{"role":"user","content":user_msg}], system_msg)
        prog.progress(90, text="✨ Step 4/4 — Finishing touches...")
        time.sleep(0.3)
        prog.progress(100, text="✅ Done!")
        time.sleep(0.3)
        prog.empty()

        cleaned = raw
        for fence in ["```svg","```xml","```html","```"]:
            cleaned = cleaned.replace(fence,"")
        cleaned = cleaned.strip()

        svg_start = cleaned.find("<svg")
        svg_end   = cleaned.rfind("</svg>")

        if svg_start >= 0 and svg_end >= 0:
            final_svg = cleaned[svg_start:svg_end+6]

            st.success("✅ Image generated!")
            st.markdown("### 🖼️ Your Educational Image")
            st.components.v1.html(final_svg, height=520, scrolling=False)

            # Download button
            b64 = base64.b64encode(final_svg.encode()).decode()
            st.markdown(
                f'<a href="data:image/svg+xml;base64,{b64}" download="zm_diagram.svg" '
                f'style="display:inline-flex;align-items:center;gap:8px;padding:10px 22px;'
                f'background:linear-gradient(135deg,#7C3AED,#A78BFA);color:#fff;'
                f'border-radius:12px;font-weight:700;font-size:14px;text-decoration:none;margin-top:10px">'
                f'⬇️ Download SVG Image</a>',
                unsafe_allow_html=True
            )

            # Save to gallery
            imgs  = load_json(IMAGES_FILE)
            email = u["email"]
            if email not in imgs: imgs[email] = []
            imgs[email].insert(0,{
                "id": str(int(time.time())), "svg": final_svg,
                "prompt":prompt, "subject":img_sub, "level":img_lvl,
                "style":style_choice,
                "created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            })
            save_json(IMAGES_FILE, imgs)

            # Update stats
            users = load_json(USERS_FILE)
            eu    = users.get(u["email"], u)
            eu.setdefault("stats", init_stats())
            eu["stats"]["images"] = eu["stats"].get("images",0)+1
            eu, new_b = check_badges(eu)
            users[u["email"]] = eu
            save_json(USERS_FILE, users)
            st.session_state.user = eu
            for b in new_b:
                st.toast(f"🏆 Badge: {b['icon']} {b['name']}!", icon="🎉")
        else:
            st.error("⚠️ Could not generate image. Try rephrasing your description.")
            with st.expander("Debug"): st.code(raw[:600])

    # ── Gallery grid ──────────────────────────────────────────
    imgs      = load_json(IMAGES_FILE)
    user_imgs = imgs.get(u["email"], [])
    if user_imgs:
        st.markdown("---")
        st.markdown("### 🖼️ Your Image Gallery")
        for i in range(0, min(len(user_imgs), 8), 2):
            cols = st.columns(2)
            for j, c in enumerate(cols):
                if i+j < len(user_imgs):
                    img = user_imgs[i+j]
                    with c:
                        st.markdown(f"""
                        <div style='background:#fff;border-radius:14px;padding:12px;
                            box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #F0F0F5;
                            margin-bottom:12px'>
                            <div style='font-size:11px;font-weight:800;color:#7C3AED;margin-bottom:8px'>
                                {img['style']} · {img['subject']} · {img['created']}
                            </div>
                            <div style='font-size:12px;color:#555;margin-bottom:8px'>
                                📝 {img['prompt'][:60]}...
                            </div>
                        </div>""", unsafe_allow_html=True)
                        with st.expander("🔍 View full image"):
                            st.components.v1.html(img["svg"], height=480, scrolling=False)
                            b64 = base64.b64encode(img["svg"].encode()).decode()
                            st.markdown(
                                f'<a href="data:image/svg+xml;base64,{b64}" download="zm_diagram.svg" '
                                f'style="display:inline-block;padding:6px 14px;background:#7C3AED;color:#fff;'
                                f'border-radius:8px;font-weight:700;font-size:12px;text-decoration:none">⬇️ Download</a>',
                                unsafe_allow_html=True
                            )


# ═════════════════════════════════════════════════════════════════
# 6. MY SYLLABUS — Redesigned with 4-step dropdown flow
# ═════════════════════════════════════════════════════════════════
def page_syllabus():
    u = st.session_state.user
    st.markdown("<div class='section-header blue'>📚 My Syllabus</div>", unsafe_allow_html=True)

    # ──────────────────────────────────────────────────────────
    # STEP 1: Curriculum
    # ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class='syl-step'>
        <div class='syl-step-title'>📋 Step 1 — Choose Curriculum</div>
    </div>""", unsafe_allow_html=True)
    curriculum = st.selectbox("Curriculum", ["Cambridge (Pakistan)"], key="syl_curr")

    # ──────────────────────────────────────────────────────────
    # STEP 2: Grade
    # ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class='syl-step'>
        <div class='syl-step-title'>🏫 Step 2 — Choose Grade</div>
    </div>""", unsafe_allow_html=True)
    default_grade = normalise_level(u.get("grade","Grade 8"))
    default_grade_idx = get_level_index(default_grade)
    sel_grade = st.selectbox("Grade", LEVELS, index=default_grade_idx, key="syl_grade_sel")

    # ──────────────────────────────────────────────────────────
    # STEP 3: Subject
    # ──────────────────────────────────────────────────────────
    st.markdown("""
    <div class='syl-step'>
        <div class='syl-step-title'>📖 Step 3 — Choose Subject</div>
    </div>""", unsafe_allow_html=True)
    available_subjects = CAMBRIDGE_SUBJECTS.get(sel_grade, list(SUBJECTS.keys()))
    sel_sub = st.selectbox("Subject", available_subjects, key="syl_sub_sel")
    st.session_state.syl_subject = sel_sub

    # ──────────────────────────────────────────────────────────
    # STEP 4: Custom override
    # ──────────────────────────────────────────────────────────
    with st.expander("➕ Step 4 — Add Custom Class or Subject"):
        st.markdown("<div style='color:#1A1A2E;font-size:13px;margin-bottom:8px'>Not seeing your class or subject? Add it manually:</div>", unsafe_allow_html=True)
        cc1, cc2 = st.columns(2)
        with cc1:
            custom_grade = st.text_input("Custom Grade/Class", placeholder="e.g. Grade 11, A2 Level...", key="custom_grade_inp")
        with cc2:
            custom_subject = st.text_input("Custom Subject", placeholder="e.g. Accounting, History...", key="custom_sub_inp")
        if custom_grade.strip(): sel_grade   = custom_grade.strip()
        if custom_subject.strip(): sel_sub = custom_subject.strip()
        if custom_grade.strip() or custom_subject.strip():
            st.info(f"✅ Using: **{sel_grade}** · **{sel_sub}**")

    # ── Update user's default grade ───────────────────────────
    if sel_grade != normalise_level(u.get("grade","")):
        users = load_json(USERS_FILE)
        if u["email"] in users:
            users[u["email"]]["grade"] = sel_grade
            save_json(USERS_FILE, users)
            st.session_state.user["grade"] = sel_grade

    # ── Map subject name to SUBJECTS key ─────────────────────
    subj_key_map = {
        "Mathematics":"Maths","Maths":"Maths","Physics":"Physics",
        "Chemistry":"Chemistry","Biology":"Biology",
        "English":"English","English Language":"English",
        "Computer Science":"Computer Science","Urdu":"Urdu",
        "Science":"Biology","Islamiyat":"English",  # fallback
    }
    subj_key  = subj_key_map.get(sel_sub, "Maths")
    info      = SUBJECTS.get(subj_key, {"emoji":"📚","color":"#666"})
    sub_color = info["color"]
    sub_emoji = info["emoji"]

    # ── Subject header ────────────────────────────────────────
    st.markdown(f"""
    <div style='background:{sub_color}18;border:2px solid {sub_color}44;
        border-radius:14px;padding:14px 18px;margin:16px 0;
        display:flex;align-items:center;gap:12px'>
        <div style='font-size:36px'>{sub_emoji}</div>
        <div>
            <div style='font-weight:800;font-size:16px;color:{sub_color}'>{sel_sub} — {sel_grade}</div>
            <div style='font-size:12px;color:#666;margin-top:2px'>🎓 {curriculum}</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # ── Curriculum data ───────────────────────────────────────
    curr  = CAMBRIDGE_CURRICULUM.get(subj_key, {}).get(sel_grade, {})
    if not curr:
        # Try Grade alias (old "Class X" format)
        for alias_old, alias_new in _LEVEL_ALIAS.items():
            if alias_new == sel_grade:
                curr = CAMBRIDGE_CURRICULUM.get(subj_key, {}).get(alias_old, {})
                if curr: break

    board = curr.get("board","Cambridge / Pakistan National Curriculum")
    units = curr.get("units",[])

    if not units:
        st.info(f"📋 No pre-loaded syllabus for {sel_sub} — {sel_grade}. Use the AI to explore topics!")
        if st.button(f"💬 Ask Ustad about {sel_sub} {sel_grade}", use_container_width=True, type="primary"):
            st.session_state.subject = subj_key
            st.session_state.chat_messages = [{
                "role":"user",
                "content":f"Give me an overview of the {sel_sub} syllabus for {sel_grade} in Pakistan. "
                          f"What are the main topics and units I need to study?"
            }]
            st.session_state.page = "chat"; st.rerun()
        return

    # ── Progress tracker ──────────────────────────────────────
    studied_topics = u.get("studied_topics",{})
    key = f"{subj_key}_{sel_grade}"
    done_topics  = studied_topics.get(key,[])
    total_topics = sum(len(un["topics"]) for un in units)
    done_count   = sum(1 for un in units for t in un["topics"] if f"{un['unit']}::{t}" in done_topics)
    pct = int((done_count/max(total_topics,1))*100)

    st.markdown(f"""
    <div style='margin-bottom:16px'>
        <div style='display:flex;justify-content:space-between;font-size:13px;
            font-weight:700;color:#666;margin-bottom:6px'>
            <span>📊 Syllabus Progress</span>
            <span style='color:{sub_color}'>{done_count}/{total_topics} topics ({pct}%)</span>
        </div>
        <div class='prog-bar'><div class='prog-fill' style='width:{pct}%;background:{sub_color}'></div></div>
    </div>""", unsafe_allow_html=True)

    # ── Unit cards ─────────────────────────────────────────────
    for ui, unit in enumerate(units):
        unit_done = [t for t in unit["topics"] if f"{unit['unit']}::{t}" in done_topics]
        unit_pct  = int((len(unit_done)/max(len(unit["topics"]),1))*100)

        with st.expander(
            f"{'✅' if unit_pct==100 else '🔵' if unit_pct>0 else '⚪'}  "
            f"Unit {ui+1}: {unit['unit']}  ({unit_pct}% done)",
            expanded=(ui==0)
        ):
            st.markdown(f"""<div class='prog-bar' style='margin-bottom:12px'>
                <div class='prog-fill' style='width:{unit_pct}%;background:{sub_color}'></div>
            </div>""", unsafe_allow_html=True)

            # Topic chips overview
            chip_parts = []
            for t in unit["topics"]:
                tk   = f"{unit['unit']}::{t}"
                tick = "✅ " if tk in done_topics else ""
                chip_parts.append(
                    f"<span class='topic-chip' style='background:{sub_color}18;"
                    f"border:1px solid {sub_color}44;color:{sub_color}'>"
                    f"{tick}{t}</span>"
                )
            chips = "".join(chip_parts)
            st.markdown(f"<div style='margin-bottom:12px'>{chips}</div>", unsafe_allow_html=True)

            # Per-topic actions
            for topic in unit["topics"]:
                topic_key = f"{unit['unit']}::{topic}"
                is_done   = topic_key in done_topics
                tc1, tc2, tc3 = st.columns([3,1,1])
                with tc1:
                    st.markdown(
                        f"<div style='padding:6px 0;font-size:14px;"
                        f"color:{'#059669' if is_done else '#1A1A2E'};"
                        f"font-weight:{'700' if is_done else '400'}'>"
                        f"{'✅' if is_done else '📖'} {topic}</div>",
                        unsafe_allow_html=True
                    )
                with tc2:
                    if st.button("💬 Ask", key=f"ask_{ui}_{topic[:18]}", use_container_width=True):
                        st.session_state.subject = subj_key
                        st.session_state.level   = sel_grade
                        st.session_state.chat_messages = [{
                            "role":"user",
                            "content":f"Explain this topic from my {sel_grade} {sel_sub} syllabus: {topic}"
                        }]
                        st.session_state.session_id = None
                        st.session_state.page = "chat"; st.rerun()
                with tc3:
                    btn_lbl = "✅ Done" if is_done else "Mark ✓"
                    if st.button(btn_lbl, key=f"done_{ui}_{topic[:18]}", use_container_width=True):
                        users = load_json(USERS_FILE)
                        eu    = users.get(u["email"],u)
                        st_map = eu.get("studied_topics",{})
                        tlist  = st_map.get(key,[])
                        if topic_key in tlist: tlist.remove(topic_key)
                        else: tlist.append(topic_key)
                        st_map[key] = tlist
                        eu["studied_topics"] = st_map
                        users[u["email"]] = eu
                        save_json(USERS_FILE, users)
                        st.session_state.user = eu; st.rerun()

            # Quick action buttons
            ba, bb, bc = st.columns(3)
            with ba:
                if st.button(f"📝 Quiz on Unit {ui+1}", key=f"qunit_{ui}", use_container_width=True):
                    topics_str = ", ".join(unit["topics"])
                    with st.spinner("Generating unit quiz..."):
                        raw = call_ai(
                            [{"role":"user","content":
                              f"Create 5 MCQ questions for unit '{unit['unit']}' covering: {topics_str}. "
                              f"For {sel_grade} {sel_sub} students. "
                              f'Return ONLY raw JSON: {{"questions":[{{"q":"...","options":["A.","B.","C.","D."],"answer":"A.","explanation":"..."}}]}}'}],
                            "Quiz generator. Return ONLY valid raw JSON.", 1200
                        )
                        try:
                            clean = raw.replace("```json","").replace("```","").strip()
                            data  = json.loads(clean)
                            st.session_state.quiz = {
                                "questions":data["questions"],"current":0,"score":0,
                                "answers":[],"done":False,"sub":subj_key,"lvl":sel_grade,
                                "topic":unit["unit"],"difficulty":"Medium"
                            }
                            st.session_state.page = "quiz"; st.rerun()
                        except: st.error("Could not generate quiz.")
            with bb:
                if st.button(f"🎨 Diagram", key=f"imgunit_{ui}", use_container_width=True):
                    st.session_state.page = "image"; st.rerun()
            with bc:
                if st.button(f"📖 Summary", key=f"sumunit_{ui}", use_container_width=True):
                    topics_str = ", ".join(unit["topics"])
                    with st.spinner("Generating summary..."):
                        summary = call_ai(
                            [{"role":"user","content":
                              f"Give a clear revision summary of '{unit['unit']}' for {sel_grade} {sel_sub} ({board}). "
                              f"Cover: {topics_str}. Use bullet points, include key formulas, max 300 words."}],
                            f"You are a {sel_sub} teacher. Clear revision summaries.", 800
                        )
                    st.markdown(f"""
                    <div style='background:#F8F9FA;border-left:4px solid {sub_color};
                        border-radius:0 12px 12px 0;padding:14px 16px;margin-top:10px;
                        font-size:13px;line-height:1.7;white-space:pre-wrap;color:#1A1A2E'>
                        {summary}
                    </div>""", unsafe_allow_html=True)

    # ── Download ──────────────────────────────────────────────
    st.markdown("---")
    syllabus_text = f"{sel_sub} — {sel_grade}\nBoard: {board}\n\n"
    for ui, unit in enumerate(units):
        syllabus_text += f"Unit {ui+1}: {unit['unit']}\n"
        for t in unit["topics"]: syllabus_text += f"  • {t}\n"
        syllabus_text += "\n"
    b64 = base64.b64encode(syllabus_text.encode()).decode()
    st.markdown(
        f'<a href="data:text/plain;base64,{b64}" download="{sel_sub}_{sel_grade}_syllabus.txt" '
        f'style="display:inline-block;padding:10px 20px;background:{sub_color};color:#fff;'
        f'border-radius:12px;font-weight:700;font-size:14px;text-decoration:none;margin-top:8px">'
        f'⬇️ Download Syllabus</a>',
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────────────────────────
# PROGRESS PAGE
# ─────────────────────────────────────────────────────────────────
def page_progress():
    u     = st.session_state.user
    stats = u.get("stats",{})
    total = stats.get("total",0)

    st.markdown("<div class='section-header green'>📊 My Progress</div>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("❓ Questions",  total)
    with c2: st.metric("🏆 Badges",     len(u.get("badges",[])))
    with c3: st.metric("🔥 Streak",     f"{stats.get('streak',0)} days")
    with c4: st.metric("🎯 Quizzes",    stats.get("quizzes_done",0))

    st.markdown("### 📚 Questions Per Subject")
    for name, info in SUBJECTS.items():
        cnt = stats.get(name,0)
        pct = int((cnt/max(total,1))*100)
        st.markdown(f"""
        <div style='margin-bottom:14px'>
            <div style='display:flex;justify-content:space-between;font-size:13px;
                font-weight:700;margin-bottom:5px;color:#1A1A2E'>
                <span>{info['emoji']} {name}</span>
                <span style='color:{info["color"]}'>{cnt} questions ({pct}%)</span>
            </div>
            <div class='prog-bar'><div class='prog-fill' style='width:{pct}%;background:{info["color"]}'></div></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("### 🛠️ Activity")
    c1,c2,c3 = st.columns(3)
    with c1: st.metric("🎨 Images Generated", stats.get("images",0))
    with c2: st.metric("📅 Member Since",      u.get("joined",""))
    with c3: st.metric("📖 Subjects Studied",  sum(1 for s in SUBJECTS if stats.get(s,0)>0))


# ─────────────────────────────────────────────────────────────────
# HISTORY PAGE
# ─────────────────────────────────────────────────────────────────
def page_history():
    u = st.session_state.user
    st.markdown("<div class='section-header'>🕐 Chat History</div>", unsafe_allow_html=True)
    hist     = load_json(HISTORY_FILE)
    sessions = sorted(hist.get(u["email"],[]), key=lambda x:x.get("updated",""), reverse=True)

    if not sessions:
        st.info("📭 No chat history yet. Start a conversation with Ustad!")
        return

    if st.button("🗑️ Clear All History", type="secondary"):
        hist[u["email"]] = []
        save_json(HISTORY_FILE, hist)
        st.success("History cleared."); st.rerun()

    for sess in sessions:
        info  = SUBJECTS.get(sess.get("subject",""), {"emoji":"📚","color":"#666"})
        msgs  = sess.get("messages",[])
        label = (f"{info['emoji']} {sess.get('subject','')} — {sess.get('level','')} | "
                 f"{sess.get('updated','')} ({len(msgs)} msgs)")
        with st.expander(label):
            for m in msgs:
                if m["role"]=="user":
                    st.markdown(f"<div class='msg-user' style='margin-left:40px'>{m['content']}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div class='msg-bot' style='margin-right:40px'>{m['content']}</div>", unsafe_allow_html=True)
            if st.button("🔄 Continue chat", key=f"cont_{sess['id']}"):
                st.session_state.chat_messages = msgs
                st.session_state.session_id    = sess["id"]
                st.session_state.subject       = sess.get("subject","Maths")
                st.session_state.page          = "chat"; st.rerun()


# ─────────────────────────────────────────────────────────────────
# BADGES PAGE
# ─────────────────────────────────────────────────────────────────
def page_badges():
    u      = st.session_state.user
    earned = u.get("badges",[])
    st.markdown("<div class='section-header orange'>🏆 Badges & Achievements</div>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#666;font-size:13px'>Earned "
                f"<b style='color:#1A1A2E'>{len(earned)}</b> of "
                f"<b style='color:#1A1A2E'>{len(BADGES)}</b> badges</p>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i,b in enumerate(BADGES):
        is_earned = b["id"] in earned
        with cols[i%3]:
            locked = "" if is_earned else "badge-locked"
            status_color = "#059669" if is_earned else "#ccc"
            status_text  = "✅ Earned!" if is_earned else "🔒 Locked"
            st.markdown(f"""
            <div class='badge-card {locked}' style='margin-bottom:12px'>
                <span class='badge-icon'>{b['icon']}</span>
                <div class='badge-name'>{b['name']}</div>
                <div class='badge-desc'>{b['desc']}</div>
                <div style='font-size:11px;margin-top:5px;color:{status_color};font-weight:700'>{status_text}</div>
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# PROFILE PAGE
# ─────────────────────────────────────────────────────────────────
def page_profile():
    u = st.session_state.user
    st.markdown("<div class='section-header'>👤 My Profile</div>", unsafe_allow_html=True)
    c1,c2 = st.columns([1,2])
    with c1:
        st.markdown(f"<div style='font-size:80px;text-align:center;background:#F3F4F6;"
                    f"border-radius:20px;padding:20px'>{u.get('avatar','👦')}</div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style='padding:10px 0;color:#1A1A2E'>
            <div style='font-family:"Baloo 2",cursive;font-size:22px;font-weight:800'>{u['name']}</div>
            <div style='font-size:13px;color:#999;margin-top:4px'>
                {'🎒 Student'  if u.get('role')=='student'
                 else '👨‍👩‍👦 Parent'  if u.get('role')=='parent'
                 else '👨‍🏫 Teacher' if u.get('role')=='teacher'
                 else '🛡️ Admin'    if u.get('role')=='admin'
                 else '👤 User'} • {u.get('grade','')}
            </div>
            <div style='font-size:12px;color:#bbb;margin-top:2px'>📧 {u['email']}</div>
            <div style='font-size:12px;color:#bbb;margin-top:2px'>📅 Joined {u.get('joined','')}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### ✏️ Update Profile")
    with st.form("profile_form"):
        new_name  = st.text_input("Full Name", value=u.get("name",""))
        new_grade = st.selectbox("Default Grade", ["-- Select --"]+LEVELS,
                                 index=get_level_index(u.get("grade","Grade 6"))+1)
        cur_av_key = next((k for k,v in AVATARS.items() if v==u.get("avatar","👦")), list(AVATARS.keys())[0])
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
                st.error("Min 6 characters.")
            else:
                if new_name.strip():           eu["name"]   = new_name.strip()
                if new_grade != "-- Select --": eu["grade"]  = new_grade
                eu["avatar"] = AVATARS[new_avatar]
                if new_pw:                     eu["password"] = hash_pw(new_pw)
                users[u["email"]] = eu
                save_json(USERS_FILE, users)
                st.session_state.user = eu
                st.success("✅ Profile updated!"); time.sleep(0.5); st.rerun()


# ═════════════════════════════════════════════════════════════════
# HOMEWORK PAGE
# ═════════════════════════════════════════════════════════════════
def page_homework():
    u = st.session_state.user
    st.markdown("<div class='section-header'>📋 Create Homework</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style='background:#EFF4FF;border-radius:14px;padding:14px 18px;
        margin-bottom:20px;font-size:13px;color:#1B4FD8;border-left:4px solid #2563EB'>
        📝 <b>AI Homework Generator</b> — Fill in the details below and let AI create
        a complete assignment with questions, answers, hints, marking guide, and learning objectives.
    </div>""", unsafe_allow_html=True)

    # ── Step 1: Subject & Grade ───────────────────────────────
    st.markdown("#### 📚 Step 1 — Subject & Grade")
    c1, c2 = st.columns(2)
    with c1:
        hw_subject = st.selectbox("Subject", list(SUBJECTS.keys()), key="hw_subject")
    with c2:
        lvl_idx = get_level_index(u.get("grade", "Grade 6"))
        hw_grade = st.selectbox("Grade Level", LEVELS, index=lvl_idx, key="hw_grade")

    # ── Step 2: Topic & Description ───────────────────────────
    st.markdown("#### ✏️ Step 2 — Topic & Description")
    hw_topic = st.text_input(
        "Topic / Chapter",
        placeholder="e.g. Quadratic Equations, Photosynthesis, World War II, Newton's Laws...",
        key="hw_topic"
    )
    hw_desc = st.text_area(
        "Assignment Description & Instructions",
        placeholder="Describe what students should do — any special instructions, learning objectives, or context for this homework...",
        height=110,
        key="hw_desc"
    )

    # ── Step 3: Homework Settings ─────────────────────────────
    st.markdown("#### ⚙️ Step 3 — Homework Settings")
    c3, c4, c5 = st.columns(3)
    with c3:
        hw_type = st.selectbox("Homework Type", [
            "Mixed (MCQ + Short + Long)",
            "MCQ Only",
            "Short Answer",
            "Long Answer / Essay",
            "Problem Solving",
            "Research & Summary",
        ], key="hw_type")
    with c4:
        hw_difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard", "Mixed"], index=1, key="hw_diff")
    with c5:
        hw_num_q = st.selectbox("Number of Questions", [5, 8, 10, 12, 15], index=1, key="hw_num_q")

    # ── Step 4: Due Date ──────────────────────────────────────
    st.markdown("#### 📅 Step 4 — Due Date")
    hw_due_days = st.slider("Due in how many days from today?", 1, 14, 3, key="hw_due_days")
    due_date = (datetime.date.today() + datetime.timedelta(days=hw_due_days)).isoformat()
    st.markdown(f"""
    <div style='background:#F0FDF4;border-radius:10px;padding:10px 16px;
        font-size:13px;color:#065F46;font-weight:700;display:inline-block'>
        📅 Due Date: {due_date}
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Generate Button ───────────────────────────────────────
    if st.button("🚀 Generate Homework with AI", use_container_width=True, type="primary", key="gen_hw_btn"):
        if not hw_topic.strip():
            st.error("⚠️ Please enter a topic in Step 2 before generating.")
        else:
            topic_str = hw_topic.strip()
            desc_str  = hw_desc.strip() if hw_desc.strip() else "Standard homework assignment."
            with st.spinner(f"✨ Generating {hw_num_q} {hw_difficulty} questions on '{topic_str}'... (20–30 sec)"):
                raw = call_ai(
                    [{"role": "user", "content":
                      f"Create a complete homework assignment for {hw_grade} {hw_subject} students in Pakistan. "
                      f"Topic: {topic_str}. Teacher instructions: {desc_str}. "
                      f"Homework type: {hw_type}. Difficulty: {hw_difficulty}. "
                      f"Generate exactly {hw_num_q} questions. "
                      f"Return ONLY raw JSON with no backticks and no markdown, in this exact structure: "
                      f'{{"title":"homework title","instructions":"detailed student-facing instructions",'
                      f'"learning_objectives":"what students will learn",'
                      f'"questions":[{{"number":1,"type":"MCQ|short_answer|long_answer|problem",'
                      f'"question":"question text","marks":2,'
                      f'"options":["A. ...","B. ...","C. ...","D. ..."],'
                      f'"answer":"correct answer or full model answer",'
                      f'"hint":"a helpful hint without giving away the answer"}}],'
                      f'"total_marks":20,"marking_guide":"concise marking guide for each question type"}}'}],
                    "You are an expert Pakistani curriculum homework generator. Return ONLY valid JSON, no extra text.",
                    3000
                )
            try:
                clean   = raw.replace("```json", "").replace("```", "").strip()
                hw_data = json.loads(clean)

                # Save to file
                homework = load_json(HOMEWORK_FILE)
                hw_id = (f"hw_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_"
                         f"{u['email'].split('@')[0]}")
                homework[hw_id] = {
                    "id":            hw_id,
                    "created_by":    u["email"],
                    "creator_name":  u["name"],
                    "subject":       hw_subject,
                    "grade":         hw_grade,
                    "topic":         topic_str,
                    "description":   desc_str,
                    "type":          hw_type,
                    "difficulty":    hw_difficulty,
                    "due_date":      due_date,
                    "created":       datetime.date.today().isoformat(),
                    "data":          hw_data,
                }
                save_json(HOMEWORK_FILE, homework)
                st.session_state["hw_preview"] = homework[hw_id]
                st.success("✅ Homework generated and saved successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"⚠️ Could not parse AI response. Please try again. ({e})")
                with st.expander("🔍 Debug info"):
                    st.code(raw[:800])

    # ── Preview Section ───────────────────────────────────────
    hw_prev = st.session_state.get("hw_preview")
    if hw_prev:
        data = hw_prev["data"]
        info = SUBJECTS.get(hw_prev["subject"], {"emoji": "📚", "color": "#2563EB"})
        col  = info["color"]

        st.markdown("---")
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,{col}18,{col}08);
            border:2px solid {col}44;border-radius:18px;padding:20px 22px;margin-bottom:18px'>
            <div style='font-size:20px;font-weight:900;color:#1A1A2E;margin-bottom:10px'>
                {info["emoji"]} {data.get("title", hw_prev["topic"])}
            </div>
            <div style='display:flex;gap:10px;flex-wrap:wrap;margin-bottom:12px'>
                <span style='background:{col}22;color:{col};padding:3px 12px;
                    border-radius:99px;font-size:12px;font-weight:700'>📚 {hw_prev["subject"]}</span>
                <span style='background:{col}22;color:{col};padding:3px 12px;
                    border-radius:99px;font-size:12px;font-weight:700'>🏫 {hw_prev["grade"]}</span>
                <span style='background:{col}22;color:{col};padding:3px 12px;
                    border-radius:99px;font-size:12px;font-weight:700'>🎯 {hw_prev["difficulty"]}</span>
                <span style='background:{col}22;color:{col};padding:3px 12px;
                    border-radius:99px;font-size:12px;font-weight:700'>
                    📝 {len(data.get("questions", []))} questions · {data.get("total_marks", 0)} marks</span>
                <span style='background:#D1FAE5;color:#065F46;padding:3px 12px;
                    border-radius:99px;font-size:12px;font-weight:700'>📅 Due: {hw_prev["due_date"]}</span>
            </div>
            <div style='font-size:13px;color:#374151;margin-bottom:8px'>
                <b>📋 Instructions:</b> {data.get("instructions", "")[:250]}
            </div>
            <div style='font-size:12px;color:#6B7280'>
                <b>🎯 Learning Objectives:</b> {data.get("learning_objectives", "")}
            </div>
        </div>""", unsafe_allow_html=True)

        # Preview first 5 questions
        questions = data.get("questions", [])
        st.markdown(f"#### 📝 Question Preview (showing {min(5, len(questions))} of {len(questions)})")

        type_icons = {
            "MCQ":          ("🔵", "#2563EB"),
            "short_answer": ("📝", "#059669"),
            "long_answer":  ("📄", "#7C3AED"),
            "problem":      ("🔢", "#E8472A"),
        }

        for i, q in enumerate(questions[:5]):
            t_icon, t_color = type_icons.get(q.get("type", ""), ("❓", "#666"))
            type_label = q.get("type", "").replace("_", " ").title()

            with st.expander(
                f"Q{i+1}. {q['question'][:75]}{'...' if len(q['question'])>75 else ''}  "
                f"[{q.get('marks', 0)} mark{'s' if q.get('marks',0)!=1 else ''}]"
            ):
                st.markdown(f"""
                <div style='display:flex;align-items:center;gap:8px;margin-bottom:10px'>
                    <span style='background:{t_color}18;color:{t_color};padding:2px 10px;
                        border-radius:99px;font-size:12px;font-weight:700'>
                        {t_icon} {type_label}</span>
                    <span style='font-size:12px;color:#888'>{q.get("marks",0)} marks</span>
                </div>
                <div style='font-size:14px;font-weight:700;color:#1A1A2E;margin-bottom:10px;line-height:1.5'>
                    {q["question"]}
                </div>""", unsafe_allow_html=True)

                if q.get("options"):
                    for opt in q["options"]:
                        st.markdown(f"""
                        <div style='background:#F8F9FA;border-radius:8px;padding:7px 12px;
                            margin-bottom:4px;font-size:13px;color:#374151'>
                            {opt}
                        </div>""", unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div style='background:#D1FAE5;border-radius:8px;padding:8px 12px;
                        font-size:12px;color:#065F46;margin-top:6px'>
                        ✅ <b>Answer:</b> {q.get("answer", "")}
                    </div>""", unsafe_allow_html=True)
                with col2:
                    if q.get("hint"):
                        st.markdown(f"""
                        <div style='background:#FFF8E7;border-radius:8px;padding:8px 12px;
                            font-size:12px;color:#92400E;margin-top:6px'>
                            💡 <b>Hint:</b> {q.get("hint", "")}
                        </div>""", unsafe_allow_html=True)

        if len(questions) > 5:
            st.markdown(f"""
            <div style='text-align:center;font-size:13px;color:#888;
                background:#F8F9FA;border-radius:10px;padding:12px;margin-top:8px'>
                📄 + {len(questions)-5} more questions saved in the assignment
            </div>""", unsafe_allow_html=True)

        # Marking Guide
        if data.get("marking_guide"):
            st.markdown(f"""
            <div style='background:#FFF8E7;border:1.5px solid #F5CC4A;border-radius:12px;
                padding:14px 16px;margin-top:14px'>
                <div style='font-size:13px;font-weight:800;color:#92400E;margin-bottom:6px'>
                    📖 Marking Guide
                </div>
                <div style='font-size:13px;color:#78350F;line-height:1.6'>
                    {data.get("marking_guide", "")}
                </div>
            </div>""", unsafe_allow_html=True)

        # Action buttons
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        ba, bb = st.columns(2)
        with ba:
            if st.button("➕ Create Another Homework", use_container_width=True, type="primary"):
                st.session_state["hw_preview"] = None
                st.rerun()
        with bb:
            if st.button("📂 Clear Preview", use_container_width=True):
                st.session_state["hw_preview"] = None
                st.rerun()


# ═════════════════════════════════════════════════════════════════
# ADMIN DASHBOARD
# ═════════════════════════════════════════════════════════════════
def page_admin():
    st.markdown("<div class='section-header orange'>🛡️ Admin Dashboard</div>", unsafe_allow_html=True)

    users    = load_json(USERS_FILE)
    homework = load_json(HOMEWORK_FILE)

    students  = {e: d for e, d in users.items() if d.get("role") not in ("admin",)}
    all_hw    = list(homework.values())

    tab_perf, tab_hw = st.tabs([
        "📊 Student Performance Analytics",
        "📋 Homework Tracking",
    ])

    # ═══════════════════════════════════════════════
    # TAB 1 — STUDENT PERFORMANCE ANALYTICS
    # ═══════════════════════════════════════════════
    with tab_perf:

        # ── Platform Overview Cards ────────────────
        st.markdown("### 📊 Platform Overview")
        total_students  = len(students)
        total_questions = sum(d.get("stats",{}).get("total",0)     for d in students.values())
        total_quizzes   = sum(d.get("stats",{}).get("quizzes_done",0) for d in students.values())
        avg_streak      = (sum(d.get("stats",{}).get("streak",0) for d in students.values())
                           / max(total_students, 1))

        c1, c2, c3, c4 = st.columns(4)
        for col_w, icon, val, lbl, color in [
            (c1, "🎒", total_students,       "Total Users",      "#2563EB"),
            (c2, "❓", total_questions,      "Questions Asked",  "#E8472A"),
            (c3, "📝", total_quizzes,        "Quizzes Done",     "#7C3AED"),
            (c4, "🔥", f"{avg_streak:.1f}d", "Avg Streak",       "#F59E0B"),
        ]:
            with col_w:
                st.markdown(f"""
                <div style='background:#fff;border-radius:14px;padding:18px 14px;text-align:center;
                    box-shadow:0 2px 12px rgba(0,0,0,0.07);border-top:4px solid {color}'>
                    <div style='font-size:26px'>{icon}</div>
                    <div style='font-size:26px;font-weight:900;color:{color};margin:4px 0'>{val}</div>
                    <div style='font-size:11px;color:#999;font-weight:700'>{lbl}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        # ── Top 10 Leaderboard ─────────────────────
        st.markdown("### 🏆 Top 10 Students — Engagement Leaderboard")

        sorted_users = sorted(
            students.items(),
            key=lambda x: (
                x[1].get("stats",{}).get("total",0)
                + x[1].get("stats",{}).get("quizzes_done",0) * 3
                + x[1].get("stats",{}).get("streak",0) * 2
                + len(x[1].get("badges",[])) * 5
            ),
            reverse=True
        )

        rank_icons  = ["🥇","🥈","🥉"] + [f"{i+1}️⃣" for i in range(3,10)]
        max_score   = max(
            (s.get("stats",{}).get("total",0)
             + s.get("stats",{}).get("quizzes_done",0)*3
             + s.get("stats",{}).get("streak",0)*2
             + len(s.get("badges",[]))*5
             for _,s in sorted_users[:1]),
            default=1
        )

        for i, (email, ud) in enumerate(sorted_users[:10]):
            stats   = ud.get("stats", {})
            qs      = stats.get("total", 0)
            quizzes = stats.get("quizzes_done", 0)
            streak  = stats.get("streak", 0)
            badges  = len(ud.get("badges", []))
            score   = qs + quizzes*3 + streak*2 + badges*5
            bar_pct = min(int((score / max(max_score, 1)) * 100), 100)
            bar_col = "#FFD700" if i < 3 else "#6366F1"
            top_subj = max(
                [(s, stats.get(s,0)) for s in SUBJECTS],
                key=lambda x: x[1], default=("—", 0)
            )
            grade = ud.get("grade","")

            st.markdown(f"""
            <div style='background:#fff;border-radius:14px;padding:14px 18px;
                margin-bottom:10px;box-shadow:0 2px 10px rgba(0,0,0,0.06);
                border-left:5px solid {"#FFD700" if i<3 else "#E0E7FF"};color:#1A1A2E'>
                <div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px'>
                    <div style='display:flex;align-items:center;gap:12px'>
                        <span style='font-size:24px'>{rank_icons[i]}</span>
                        <div>
                            <div style='font-weight:800;font-size:15px'>
                                {ud.get("avatar","👤")} {ud.get("name","?")}
                            </div>
                            <div style='font-size:11px;color:#aaa'>{grade} &nbsp;·&nbsp; {email}</div>
                        </div>
                    </div>
                    <div style='display:flex;gap:18px;font-size:12px;flex-wrap:wrap'>
                        <div style='text-align:center'>
                            <div style='font-weight:900;font-size:17px;color:#E8472A'>{qs}</div>
                            <div style='color:#bbb'>Qs</div>
                        </div>
                        <div style='text-align:center'>
                            <div style='font-weight:900;font-size:17px;color:#2563EB'>{quizzes}</div>
                            <div style='color:#bbb'>Quizzes</div>
                        </div>
                        <div style='text-align:center'>
                            <div style='font-weight:900;font-size:17px;color:#F59E0B'>{streak}d</div>
                            <div style='color:#bbb'>Streak</div>
                        </div>
                        <div style='text-align:center'>
                            <div style='font-weight:900;font-size:17px;color:#7C3AED'>{badges}</div>
                            <div style='color:#bbb'>Badges</div>
                        </div>
                    </div>
                </div>
                <div style='margin-top:10px'>
                    <div style='display:flex;justify-content:space-between;
                        font-size:11px;color:#bbb;margin-bottom:4px'>
                        <span>🏅 Top subject: {SUBJECTS.get(top_subj[0],{}).get("emoji","")}&nbsp;{top_subj[0]} ({top_subj[1]} Qs)</span>
                        <span style='font-weight:700;color:{bar_col}'>Score: {score}</span>
                    </div>
                    <div style='background:#F0F0F8;border-radius:99px;height:10px;overflow:hidden'>
                        <div style='width:{bar_pct}%;height:10px;border-radius:99px;
                            background:linear-gradient(90deg,{bar_col},{bar_col}88);
                            transition:width 1s ease'></div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

        if not sorted_users:
            st.info("No user data available yet.")

        # ── Subject Breakdown ──────────────────────
        st.markdown("### 📚 Platform-Wide Subject Engagement")
        subject_totals = {
            s: sum(d.get("stats",{}).get(s,0) for d in students.values())
            for s in SUBJECTS
        }
        grand_total = max(sum(subject_totals.values()), 1)

        for subj, count in sorted(subject_totals.items(), key=lambda x: x[1], reverse=True):
            info    = SUBJECTS[subj]
            pct     = int((count / grand_total) * 100)
            bar_w   = max(pct, 2)
            st.markdown(f"""
            <div style='margin-bottom:14px'>
                <div style='display:flex;justify-content:space-between;
                    font-size:13px;font-weight:700;margin-bottom:5px;color:#1A1A2E'>
                    <span>{info["emoji"]} {subj}</span>
                    <span style='color:{info["color"]}'>{count} questions &nbsp;·&nbsp; {pct}%</span>
                </div>
                <div style='background:#F0F0F8;border-radius:99px;height:12px;overflow:hidden'>
                    <div style='width:{bar_w}%;height:12px;border-radius:99px;
                        background:linear-gradient(90deg,{info["color"]},{info["color"]}88);
                        transition:width 1s ease'></div>
                </div>
            </div>""", unsafe_allow_html=True)

        # ── 7-Day Activity Heatmap ─────────────────
        st.markdown("### 🗓️ 7-Day Activity Heatmap")
        today = datetime.date.today()
        days  = [(today - datetime.timedelta(days=i)) for i in range(6, -1, -1)]
        activity = {d.isoformat(): 0 for d in days}
        for ud in students.values():
            last = ud.get("stats",{}).get("lastDate","")
            if last in activity:
                activity[last] += 1

        max_act = max(max(activity.values(), default=0), 1)
        st.markdown("<div style='display:flex;flex-direction:column;gap:6px;margin-top:10px'>",
                    unsafe_allow_html=True)
        for day_iso, cnt in activity.items():
            day_obj  = datetime.date.fromisoformat(day_iso)
            weekday  = day_obj.strftime("%a %d %b")
            bar_w    = max(int((cnt / max_act) * 100), 2) if cnt else 0
            is_today = day_iso == today.isoformat()
            bar_col  = "#E8472A" if is_today else "#2563EB"
            dot_col  = "#FFD700" if is_today else "#E5E7EB"
            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:10px'>
                <div style='font-size:12px;color:{"#E8472A" if is_today else "#888"};
                    font-weight:{"800" if is_today else "400"};width:90px;flex-shrink:0'>
                    {"📍 " if is_today else ""}{weekday}
                </div>
                <div style='flex:1;background:#F0F0F8;border-radius:99px;height:20px;overflow:hidden'>
                    <div style='width:{bar_w}%;height:20px;border-radius:99px;
                        background:linear-gradient(90deg,{bar_col},{bar_col}88)'></div>
                </div>
                <div style='font-size:13px;font-weight:800;color:#1A1A2E;width:28px;text-align:right'>
                    {cnt}
                </div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div><div style='font-size:11px;color:#bbb;margin-top:8px'>"
                    "Counts unique active users per day based on last activity date.</div>",
                    unsafe_allow_html=True)

    # ═══════════════════════════════════════════════
    # TAB 2 — HOMEWORK TRACKING
    # ═══════════════════════════════════════════════
    with tab_hw:
        st.markdown("### 📋 Homework Tracking")

        if not all_hw:
            st.info("📭 No homework assignments have been created yet.")
        else:
            # ── Summary row ────────────────────────
            total_hw   = len(all_hw)
            total_subs = sum(len(h.get("submissions", {})) for h in all_hw)
            est_poss   = total_hw * max(len(students), 1)
            comp_pct   = min(int((total_subs / max(est_poss, 1)) * 100), 100)
            comp_color = "#059669" if comp_pct >= 70 else "#F59E0B" if comp_pct >= 40 else "#E8472A"

            c1, c2, c3 = st.columns(3)
            for col_w, icon, val, lbl, color in [
                (c1, "📋", total_hw,   "Assignments",     "#2563EB"),
                (c2, "📬", total_subs, "Total Submissions","#7C3AED"),
                (c3, "📈", f"{comp_pct}%", "Est. Completion", comp_color),
            ]:
                with col_w:
                    st.markdown(f"""
                    <div style='background:#fff;border-radius:14px;padding:16px;text-align:center;
                        box-shadow:0 2px 10px rgba(0,0,0,0.06);border-top:4px solid {color}'>
                        <div style='font-size:22px'>{icon}</div>
                        <div style='font-size:24px;font-weight:900;color:{color}'>{val}</div>
                        <div style='font-size:11px;color:#999;font-weight:700'>{lbl}</div>
                    </div>""", unsafe_allow_html=True)

            # Platform completion bar
            st.markdown(f"""
            <div style='margin:18px 0 8px'>
                <div style='display:flex;justify-content:space-between;
                    font-size:13px;font-weight:700;color:#1A1A2E;margin-bottom:6px'>
                    <span>🎯 Platform-wide Homework Completion</span>
                    <span style='color:{comp_color}'>{comp_pct}%</span>
                </div>
                <div style='background:#F0F0F8;border-radius:99px;height:16px;overflow:hidden'>
                    <div style='width:{comp_pct}%;height:16px;border-radius:99px;
                        background:linear-gradient(90deg,{comp_color},{comp_color}88);
                        transition:width 1s ease'></div>
                </div>
                <div style='font-size:11px;color:#bbb;margin-top:5px'>
                    🟢 ≥70% complete &nbsp;·&nbsp; 🟡 40–69% &nbsp;·&nbsp; 🔴 &lt;40%
                </div>
            </div>""", unsafe_allow_html=True)

            st.markdown("---")

            # ── Filters ────────────────────────────
            st.markdown("#### 🔍 Filter Assignments")
            f1, f2 = st.columns(2)
            with f1:
                f_subj   = st.selectbox("Subject", ["All"] + list(SUBJECTS.keys()), key="adm_f_subj")
            with f2:
                f_status = st.selectbox("Status",  ["All", "Active", "Inactive"],   key="adm_f_status")

            st.markdown("---")

            for hw in sorted(all_hw, key=lambda x: x.get("created",""), reverse=True):

                # Apply filters
                if f_subj != "All" and hw.get("subject") != f_subj:
                    continue
                hw_active = hw.get("status","active") == "active"
                if f_status == "Active"   and not hw_active: continue
                if f_status == "Inactive" and hw_active:     continue

                info      = SUBJECTS.get(hw["subject"], {"emoji":"📚","color":"#2563EB"})
                col       = info["color"]
                subs      = hw.get("submissions", {})
                sub_cnt   = len(subs)
                data      = hw.get("data", {})
                hw_title  = data.get("title", hw.get("topic",""))
                due       = hw.get("due_date","")
                today_str = datetime.date.today().isoformat()
                overdue   = due < today_str if due else False

                # Compute quality stats
                if subs:
                    scores    = [s.get("score_pct",0) for s in subs.values()]
                    avg_score = int(sum(scores) / len(scores))
                    high_q    = sum(1 for s in scores if s >= 80)
                    mid_q     = sum(1 for s in scores if 60 <= s < 80)
                    low_q     = sum(1 for s in scores if s < 60)
                    q_label   = "🟢 High" if avg_score>=80 else "🟡 Medium" if avg_score>=60 else "🔴 Low"
                else:
                    avg_score = high_q = mid_q = low_q = 0
                    q_label   = "⚪ No data"

                status_badge = "🟢 Active" if hw_active else "🔴 Inactive"
                due_label    = (f"⚠️ Overdue ({due})" if overdue else f"📅 Due: {due}")

                with st.expander(
                    f"{info['emoji']} {hw_title[:45]}{'…' if len(hw_title)>45 else ''} "
                    f"| {hw.get('subject','')} {hw.get('grade','')} "
                    f"| {status_badge} | {sub_cnt} sub(s) | Avg: {avg_score}%"
                ):
                    # Tag row
                    st.markdown(f"""
                    <div style='display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px'>
                        <span style='background:{col}18;color:{col};padding:3px 10px;
                            border-radius:99px;font-size:12px;font-weight:700'>{info["emoji"]} {hw["subject"]}</span>
                        <span style='background:{col}18;color:{col};padding:3px 10px;
                            border-radius:99px;font-size:12px;font-weight:700'>🏫 {hw.get("grade","")}</span>
                        <span style='background:{col}18;color:{col};padding:3px 10px;
                            border-radius:99px;font-size:12px;font-weight:700'>🎯 {hw.get("difficulty","")}</span>
                        <span style='background:{"#FEE2E2" if overdue else "#D1FAE5"};
                            color:{"#991B1B" if overdue else "#065F46"};padding:3px 10px;
                            border-radius:99px;font-size:12px;font-weight:700'>{due_label}</span>
                    </div>
                    <div style='font-size:12px;color:#888;margin-bottom:10px'>
                        ✏️ Topic: <b style='color:#1A1A2E'>{hw.get("topic","")}</b>
                        &nbsp;·&nbsp; Created: {hw.get("created","")}
                        &nbsp;·&nbsp; By: {hw.get("creator_name", hw.get("teacher_name","?"))}
                    </div>""", unsafe_allow_html=True)

                    if sub_cnt > 0:
                        # Metric row
                        m1, m2, m3 = st.columns(3)
                        with m1: st.metric("📬 Submissions", sub_cnt)
                        with m2: st.metric("📈 Avg Score",  f"{avg_score}%")
                        with m3: st.metric("🏅 Quality",    q_label)

                        # Quality distribution bar
                        total_parts = max(high_q + mid_q + low_q, 1)
                        hw_pct  = int((high_q / total_parts) * 100)
                        mw_pct  = int((mid_q  / total_parts) * 100)
                        lw_pct  = 100 - hw_pct - mw_pct
                        st.markdown(f"""
                        <div style='margin:12px 0 16px'>
                            <div style='font-size:12px;font-weight:700;color:#1A1A2E;margin-bottom:6px'>
                                Quality Distribution
                            </div>
                            <div style='display:flex;height:22px;border-radius:10px;overflow:hidden;gap:2px'>
                                <div style='flex:{max(hw_pct,1)};background:#059669;
                                    display:flex;align-items:center;justify-content:center;
                                    font-size:10px;color:#fff;font-weight:700'>
                                    {"🟢 "+str(high_q) if hw_pct>12 else ""}
                                </div>
                                <div style='flex:{max(mw_pct,1)};background:#F59E0B;
                                    display:flex;align-items:center;justify-content:center;
                                    font-size:10px;color:#fff;font-weight:700'>
                                    {"🟡 "+str(mid_q) if mw_pct>12 else ""}
                                </div>
                                <div style='flex:{max(lw_pct,1)};background:#E8472A;
                                    display:flex;align-items:center;justify-content:center;
                                    font-size:10px;color:#fff;font-weight:700'>
                                    {"🔴 "+str(low_q) if lw_pct>12 else ""}
                                </div>
                            </div>
                            <div style='display:flex;gap:16px;font-size:11px;color:#666;margin-top:5px'>
                                <span>🟢 Excellent (≥80%): {high_q}</span>
                                <span>🟡 Good (60–79%): {mid_q}</span>
                                <span>🔴 Needs Work (&lt;60%): {low_q}</span>
                            </div>
                        </div>""", unsafe_allow_html=True)

                        # Individual submissions table
                        st.markdown("**📬 Individual Submissions**")
                        for email, sub in sorted(
                            subs.items(),
                            key=lambda x: x[1].get("score_pct",0),
                            reverse=True
                        ):
                            sp       = sub.get("score_pct", 0)
                            q_dot    = "🟢" if sp>=80 else "🟡" if sp>=60 else "🔴"
                            sub_time = sub.get("submitted_at","")
                            sub_day  = sub_time[:10] if sub_time else ""
                            on_time  = (sub_day <= due) if (sub_day and due) else True
                            time_tag = (
                                f"<span style='color:#059669;font-weight:700'>⏰ On time</span>"
                                if on_time else
                                f"<span style='color:#E8472A;font-weight:700'>⚠️ Late</span>"
                            )
                            st.markdown(f"""
                            <div style='background:#F8F9FA;border-radius:10px;padding:9px 14px;
                                margin-bottom:5px;border-left:3px solid {col};color:#1A1A2E;
                                display:flex;justify-content:space-between;
                                align-items:center;flex-wrap:wrap;gap:6px'>
                                <div>
                                    <b>{sub.get("student_name","?")}</b>
                                    <span style='font-size:11px;color:#aaa;margin-left:6px'>{email}</span>
                                </div>
                                <div style='display:flex;gap:14px;align-items:center;font-size:12px'>
                                    <span>{q_dot} <b>{sp}%</b></span>
                                    {time_tag}
                                    <span style='color:#bbb'>🕐 {sub_time}</span>
                                </div>
                            </div>""", unsafe_allow_html=True)
                    else:
                        st.info("⏳ No submissions yet for this assignment.")


# ═════════════════════════════════════════════════════════════════
# ROUTER
# ═════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    page_auth()
else:
    render_sidebar()
    if not st.session_state.get("mobile_hint_shown", False):
        st.info("📱 **On mobile?** Tap the **☰ arrow** at top-left to open the menu!", icon="📱")
        st.session_state.mobile_hint_shown = True

    p = st.session_state.page
    if   p == "home":     page_home()
    elif p == "chat":     page_chat()
    elif p == "syllabus": page_syllabus()
    elif p == "quiz":     page_quiz()
    elif p == "friends":  page_friends()
    elif p == "image":    page_image()
    elif p == "homework": page_homework()
    elif p == "admin":    page_admin()
    elif p == "progress": page_progress()
    elif p == "history":  page_history()
    elif p == "badges":   page_badges()
    elif p == "profile":  page_profile()
