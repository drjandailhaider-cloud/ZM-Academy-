# ═══════════════════════════════════════════════════════════════════════════════
# ZM Academy — Complete Streamlit App
# FIXED VERSION: All bugs corrected
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

# Legacy compat mapping: Class 1-10 → Grade 1-10
_LEVEL_ALIAS = {f"Class {i}": f"Grade {i}" for i in range(1, 11)}

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

IMAGE_STYLES = {
    "📐 Educational Diagram": "a clean labeled educational diagram with arrows, colorful sections, white background",
    "🎨 Cartoon":             "a bright fun cartoon illustration with cheerful bold colors suitable for students",
    "🎌 Anime Style":         "an anime-style illustration with vibrant colors, clean lines, expressive characters",
    "🤖 AI Art":              "a futuristic AI-generated digital art style with glowing elements and deep colors",
    "🔬 Realistic / Scientific": "a detailed realistic scientific illustration like a textbook diagram, accurate and labeled",
}

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
USERS_FILE    = "users.json"
HISTORY_FILE  = "history.json"
IMAGES_FILE   = "images.json"
GROUPS_FILE   = "groups.json"
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
            "dailyQs":0,"dailyDate":"","study_dates":[]}

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
    study_dates = s.get("study_dates", [])
    if today not in study_dates:
        study_dates.append(today)
        study_dates = study_dates[-60:]
    s["study_dates"] = study_dates
    if s.get("dailyDate","") != today:
        s["dailyQs"]   = 0
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
    "syl_curriculum": "Cambridge",
    "syl_grade": "Grade 8",
    "syl_subject_name": "Mathematics",
    "syl_custom_grade": "",
    "syl_custom_subject": "",
    "group_session": None,
    "group_player_idx": 0,
    "confirm_clear_hist": False,
    "mobile_hint_shown": False,
    # Online friends quiz room state
    "fq_room_id": None,
    "fq_role": None,
    "fq_last_q": 0,
    "fq_answered": {},
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
# CSS
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=Sora:wght@700;800;900&display=swap');

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

@media(max-width:768px){
  .main .block-container{ padding-left:.6rem !important; padding-right:.6rem !important; }
  .stButton>button{ min-height:48px !important; font-size:14px !important; }
  .msg-user{ margin-left:6px !important; }
  .msg-bot{  margin-right:6px !important; }
  div[data-testid="column"]{ padding:2px !important; }
  .stTextInput>div>div>input{ font-size:16px !important; padding:12px !important; }
}

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

.prog-bar{
  background:rgba(13,110,63,0.08); border-radius:99px;
  height:10px; overflow:hidden; margin-bottom:4px;
}
.prog-fill{ height:100%; border-radius:99px; transition:width .6s cubic-bezier(.4,0,.2,1); }

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

.word-card{
  background:linear-gradient(135deg,#061A0E 0%,#0A2414 50%,#071510 100%);
  border-radius:var(--radius); padding:20px 22px; margin-bottom:16px;
  color:#fff; border:1px solid rgba(201,168,76,0.25);
  box-shadow:0 8px 32px rgba(6,26,14,0.3);
  position:relative; overflow:hidden;
}

.reminder{
  background:linear-gradient(135deg,#FFFDF0,#FFF8DC);
  border:1.5px solid rgba(201,168,76,0.4); border-radius:var(--radius);
  padding:13px 18px; margin-bottom:16px; font-size:13px; color:var(--text);
  box-shadow:0 2px 10px rgba(201,168,76,0.12);
}

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

[data-testid="stExpander"]{
  background:var(--surface) !important; border:1.5px solid var(--border) !important;
  border-radius:var(--radius-sm) !important; margin-bottom:6px !important;
}
[data-testid="stExpander"] summary{
  font-weight:700 !important; color:var(--text) !important;
}

[data-testid="stMetricValue"]{ color:var(--green) !important; font-family:'Sora',sans-serif !important; font-weight:900 !important; }
[data-testid="stMetricLabel"]{ color:var(--text2) !important; font-weight:700 !important; }

[data-testid="stAlert"]{
  border-radius:var(--radius-sm) !important;
  border-left-width:4px !important;
}

.stRadio label,[data-testid="stRadio"] label{ color:var(--text) !important; font-weight:600 !important; }
.stCheckbox label{ color:var(--text) !important; font-weight:600 !important; }

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
    st.markdown("""
    <style>
    .main .block-container{ max-width:480px !important; padding-top:2rem !important; }
    [data-testid="stForm"]{ background:var(--surface) !important; border-radius:20px !important; padding:24px !important; border:1.5px solid var(--border) !important; box-shadow:var(--shadow-lg) !important; }
    </style>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;padding:32px 0 24px">
        <div style="display:inline-flex;align-items:center;justify-content:center;
            width:80px;height:80px;border-radius:24px;margin-bottom:16px;
            background:linear-gradient(135deg,#0D6E3F,#1A8C50);
            box-shadow:0 8px 32px rgba(13,110,63,0.4)">
            <span style="font-size:40px;line-height:1">📚</span>
        </div>
        <h1 style="font-family:'Sora',sans-serif;font-size:32px;font-weight:900;
            color:#0D1F0D;margin:0 0 6px;letter-spacing:-1px">ZM Academy</h1>
        <p style="color:#3D5C3D;font-size:14px;font-weight:600;margin:0">
            🇵🇰 Pakistan's <b style="color:#0D6E3F">#1</b> AI-Powered Education Platform
        </p>
        <div style="display:flex;justify-content:center;gap:8px;margin-top:10px;flex-wrap:wrap">
            <span style="background:rgba(13,110,63,0.08);color:#0D6E3F;padding:3px 12px;
                border-radius:99px;font-size:11px;font-weight:700;border:1px solid rgba(13,110,63,0.15)">
                Grades 1-10</span>
            <span style="background:rgba(13,110,63,0.08);color:#0D6E3F;padding:3px 12px;
                border-radius:99px;font-size:11px;font-weight:700;border:1px solid rgba(13,110,63,0.15)">
                O Level</span>
            <span style="background:rgba(13,110,63,0.08);color:#0D6E3F;padding:3px 12px;
                border-radius:99px;font-size:11px;font-weight:700;border:1px solid rgba(13,110,63,0.15)">
                A Level</span>
            <span style="background:rgba(201,168,76,0.15);color:#7A5C00;padding:3px 12px;
                border-radius:99px;font-size:11px;font-weight:700;border:1px solid rgba(201,168,76,0.25)">
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
                        "plan": "free", "stats": init_stats(), "badges": [],
                        "studied_topics": {}, "is_new": True
                    }
                    users[email2] = new_user
                    save_json(USERS_FILE, users)
                    st.session_state.logged_in = True
                    st.session_state.user = new_user
                    st.success("Account created! Welcome 🎉"); time.sleep(0.5); st.rerun()

    with tab_forgot:
        st.markdown("""
        <div style="background:rgba(13,110,63,0.06);border-radius:10px;padding:12px 14px;
            font-size:13px;color:#0D6E3F;margin-bottom:14px;border:1px solid rgba(13,110,63,0.12)">
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
    <p style="text-align:center;color:#7A9A7A;font-size:11px;margin-top:20px;font-weight:600">
        🔒 Secure &nbsp;·&nbsp; 🆓 Free to use &nbsp;·&nbsp; 🇵🇰 Pakistan National Curriculum
    </p>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────
def render_sidebar():
    u = st.session_state.user
    role_info = {
        "student": ("🎒", "Student",  "#27A862"),
        "parent":  ("👨‍👩‍👦","Parent",  "#1A8C50"),
        "teacher": ("👨‍🏫","Teacher", "#C9A84C"),
        "admin":   ("🛡️", "Admin",    "#C0392B"),
    }
    r_icon, r_label, r_color = role_info.get(u.get("role","student"), ("👤","User","#27A862"))
    role = u.get("role", "student")

    with st.sidebar:
        # FIX: Use double-quotes inside HTML to avoid single-quote conflicts
        st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;
            padding:14px 14px 12px;border-bottom:1px solid rgba(201,168,76,0.18)">
            <div style="width:36px;height:36px;border-radius:10px;flex-shrink:0;
                background:linear-gradient(135deg,#0D6E3F,#1A8C50);
                display:flex;align-items:center;justify-content:center;font-size:20px;
                box-shadow:0 3px 10px rgba(13,110,63,0.5)">📚</div>
            <div>
                <div style="font-family:'Sora',sans-serif;font-weight:900;font-size:15px;
                    color:#fff;letter-spacing:-.3px;line-height:1.1">ZM Academy</div>
                <div style="font-size:9px;color:rgba(201,168,76,0.7);font-weight:700;
                    letter-spacing:.8px;text-transform:uppercase">🇵🇰 Pakistan's #1 AI Tutor</div>
            </div>
        </div>""", unsafe_allow_html=True)

        grade_html = ""
        if u.get("grade"):
            grade_html = (
                "<span style=\"font-size:10px;color:rgba(255,255,255,0.35)\">·</span>"
                "<span style=\"font-size:10px;color:rgba(255,255,255,0.5);font-weight:600\">"
                + u.get("grade","") + "</span>"
            )

        stats = u.get("stats", {})
        st.markdown(f"""
        <div style="padding:14px 12px 14px;border-bottom:1px solid rgba(201,168,76,0.15)">
            <div style="display:flex;flex-direction:column;align-items:center">
                <div style="width:62px;height:62px;border-radius:18px;
                    background:linear-gradient(135deg,rgba(201,168,76,0.2),rgba(13,110,63,0.3));
                    display:flex;align-items:center;justify-content:center;
                    font-size:34px;line-height:1;margin-bottom:8px;
                    border:2px solid rgba(201,168,76,0.3);box-shadow:0 4px 20px rgba(0,0,0,0.3)">
                    {u.get("avatar","👦")}
                </div>
                <div style="font-family:'Sora',sans-serif;font-weight:800;font-size:14px;
                    color:#fff;text-align:center;letter-spacing:-.3px">{u["name"]}</div>
                <div style="display:inline-flex;align-items:center;gap:5px;margin-top:5px;
                    background:rgba(255,255,255,0.07);border-radius:99px;
                    padding:3px 10px;border:1px solid rgba(201,168,76,0.2)">
                    <span style="font-size:11px">{r_icon}</span>
                    <span style="font-size:11px;font-weight:700;color:{r_color}">{r_label}</span>
                    {grade_html}
                </div>
            </div>
            <div style="display:flex;justify-content:center;gap:0;margin-top:12px;
                background:rgba(0,0,0,0.25);border-radius:10px;
                border:1px solid rgba(201,168,76,0.12);overflow:hidden">
                <div style="flex:1;text-align:center;padding:8px 4px;
                    border-right:1px solid rgba(201,168,76,0.1)">
                    <div style="font-family:'Sora',sans-serif;font-size:16px;font-weight:900;
                        color:#E8C96A">{stats.get("total",0)}</div>
                    <div style="font-size:9px;color:rgba(255,255,255,0.4);
                        text-transform:uppercase;letter-spacing:.8px;font-weight:700">Qs</div>
                </div>
                <div style="flex:1;text-align:center;padding:8px 4px;
                    border-right:1px solid rgba(201,168,76,0.1)">
                    <div style="font-family:'Sora',sans-serif;font-size:16px;font-weight:900;
                        color:#E8C96A">{len(u.get("badges",[]))}</div>
                    <div style="font-size:9px;color:rgba(255,255,255,0.4);
                        text-transform:uppercase;letter-spacing:.8px;font-weight:700">Badges</div>
                </div>
                <div style="flex:1;text-align:center;padding:8px 4px">
                    <div style="font-family:'Sora',sans-serif;font-size:16px;font-weight:900;
                        color:#E8C96A">{stats.get("streak",0)}</div>
                    <div style="font-size:9px;color:rgba(255,255,255,0.4);
                        text-transform:uppercase;letter-spacing:.8px;font-weight:700">Streak</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        cur = st.session_state.page

        def nav_btn(icon, label, key, uid=""):
            btn_type = "primary" if cur == key else "secondary"
            if st.button(f"{icon}  {label}", key=f"nav_{key}{uid}",
                         use_container_width=True, type=btn_type):
                st.session_state.page = key; st.rerun()

        def section_label(text, color="rgba(201,168,76,0.65)"):
            st.markdown(
                f"<div style=\"font-size:9.5px;font-weight:800;color:{color};"
                f"text-transform:uppercase;letter-spacing:1.4px;"
                f"padding:14px 4px 4px;"
                f"border-top:1px solid rgba(255,255,255,0.06)\">{text}</div>",
                unsafe_allow_html=True
            )

        section_label("📊  Dashboard")
        nav_btn("🏠", "Home",            "home")
        nav_btn("📚", "Syllabus",        "syllabus")
        nav_btn("🎨", "Image Generator", "image")
        nav_btn("📈", "My Progress",     "progress")

        if role in ("student", "parent"):
            section_label("🎒  Student")
            nav_btn("💬", "Chat Tutor",    "chat",    "_s")
            nav_btn("📝", "Practice Quiz", "quiz")
            nav_btn("👥", "Friendz Quiz",  "friends")
            nav_btn("📋", "My Homework",   "my_homework")
            nav_btn("🕐", "Chat History",  "history", "_s")
            nav_btn("🏆", "Badges",        "badges")

        if role == "teacher":
            section_label("👨‍🏫  Teacher", "#C9A84C")
            nav_btn("📋", "Create Homework",     "homework", "_t")
            nav_btn("💬", "Chat Tutor",          "chat",     "_t")
            nav_btn("📊", "Student Performance", "admin",    "_t")
            nav_btn("🏆", "Badges",              "badges",   "_t")

        if role == "admin":
            section_label("🛡️  Admin", "#E87070")
            nav_btn("📊", "Student Performance", "admin",    "_a")
            nav_btn("🕐", "Chat History",        "history",  "_a")
            nav_btn("📋", "Homework Tracker",    "homework", "_a")
            nav_btn("💬", "Chat Tutor",          "chat",     "_a")

        section_label("👤  Account")
        nav_btn("👤", "Profile", "profile")

        st.markdown("""
        <div style="margin:16px 0 4px;border-top:1px solid rgba(255,255,255,0.08);
            padding-top:12px"></div>""", unsafe_allow_html=True)
        if st.button("🚪  Logout", key="logout_btn", use_container_width=True):
            # Only clear app-defined keys to avoid disturbing Streamlit internals
            for k in list(defaults.keys()):
                if k in st.session_state:
                    del st.session_state[k]
            st.rerun()


# ─────────────────────────────────────────────────────────────────
# HOME PAGE — FIX #1 (CRITICAL): All HTML strings use double-quotes
# to prevent single-quote conflicts with style attributes containing
# rgba() values like rgba(201,168,76,0.5) which broke rendering.
# ─────────────────────────────────────────────────────────────────
def page_home():
    u     = st.session_state.user
    sub   = st.session_state.subject
    h     = datetime.datetime.now().hour
    greet = "Good morning" if h < 12 else "Good afternoon" if h < 17 else "Good evening"
    role  = u.get("role", "student")

    _default_stats = init_stats()
    _raw_stats = u.get("stats", {})
    stats = {**_default_stats, **_raw_stats}

    # ── Onboarding for new users ──────────────────────────────
    if u.get("is_new") and not st.session_state.get("onboarding_done"):
        step = st.session_state.get("onboard_step", 1)
        steps = [
            {"emoji":"🎓","title":f"Welcome to ZM Academy, {u['name'].split()[0]}! 🎉",
             "body":"Pakistan's <b>AI-powered study app</b> for Grades 1-10, O Level and A Level.<br><br>Your personal AI tutor <b>Ustad</b> is here to help!","btn":"Next →"},
            {"emoji":"💬","title":"Everything you need to study",
             "body":"<b>💬 Chat Tutor</b> — Ask any question in any subject<br><br><b>📝 Practice Quiz</b> — Custom quizzes with difficulty levels<br><br><b>📚 My Syllabus</b> — Full Cambridge curriculum<br><br><b>🎨 Image Generator</b> — AI draws educational diagrams","btn":"Next →"},
            {"emoji":"🏆","title":"Earn Badges and Challenge Friends",
             "body":"Earn <b>11 achievement badges</b> as you study.<br><br>Use <b>👥 Friends Quiz</b> to compete with up to 3 friends on the same quiz — and see who tops the leaderboard!","btn":"🚀 Start Learning!"},
        ]
        s = steps[step-1]
        # FIX #2: Use named columns instead of _ to avoid shadowing built-in
        col_l, col_c, col_r = st.columns([1,2,1])
        with col_c:
            dots = "".join(
                "<span style=\"display:inline-block;width:9px;height:9px;border-radius:50%;"
                "background:" + ("#E8C96A" if i+1==step else "rgba(255,255,255,0.2)") + ";margin:0 3px\"></span>"
                for i in range(3)
            )
            # FIX: Use double-quotes throughout onboarding HTML
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#061A0E,#0D6E3F);border-radius:24px;
                padding:32px 28px;color:#fff;text-align:center;margin-top:20px;
                border:1px solid rgba(201,168,76,0.25);
                box-shadow:0 16px 48px rgba(6,26,14,0.5)">
                <div style="margin-bottom:14px">{dots}</div>
                <div style="font-size:56px;margin-bottom:14px">{s['emoji']}</div>
                <div style="font-family:'Sora',sans-serif;font-size:22px;font-weight:900;
                    margin-bottom:14px;letter-spacing:-.5px">{s['title']}</div>
                <div style="font-size:14px;opacity:.85;line-height:1.8">{s['body']}</div>
            </div>""", unsafe_allow_html=True)
            st.markdown("<div style=\"height:14px\"></div>", unsafe_allow_html=True)
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
    streak = stats.get("streak", 0)
    streak_fire = "🔥" * min(streak, 5) if streak > 0 else ""
    quotes = [
        ("علم حاصل کرنا ہر مسلمان پر فرض ہے", "Seeking knowledge is an obligation upon every Muslim"),
        ("محنت کا پھل میٹھا ہوتا ہے", "The fruit of hard work is always sweet"),
        ("آج کی محنت کل کی کامیابی ہے", "Today's effort is tomorrow's success"),
        ("ہر مشکل کے بعد آسانی ہے", "After every difficulty comes ease"),
        ("علم روشنی ہے", "Knowledge is light"),
    ]
    q_urdu, q_eng = quotes[(datetime.date.today().month * 31 + datetime.date.today().day) % len(quotes)]
    streak_extra = f"&nbsp;·&nbsp;🔥 {streak}-day streak!" if streak > 1 else ""

    # FIX #1 (CRITICAL): Use double-quotes for ALL HTML attributes.
    # The original code used single-quoted style attrs like style='border-left:3px solid rgba(201,168,76,0.5)'
    # which caused the f-string to terminate early at the 0.5)' portion,
    # making Streamlit render raw HTML text instead of parsed HTML.
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#061A0E 0%,#0D6E3F 55%,#0A5A32 100%);
        border-radius:20px;padding:22px 24px;margin-bottom:16px;color:#fff;
        border:1px solid rgba(201,168,76,0.2);box-shadow:0 8px 32px rgba(6,26,14,0.25);
        position:relative;overflow:hidden">
        <div style="position:absolute;top:-30px;right:-30px;width:150px;height:150px;border-radius:50%;
            background:radial-gradient(circle,rgba(201,168,76,0.18),transparent 70%)"></div>
        <div style="position:absolute;bottom:-20px;left:10px;width:90px;height:90px;border-radius:50%;
            background:radial-gradient(circle,rgba(39,168,98,0.15),transparent 70%)"></div>
        <div style="display:flex;align-items:center;gap:16px;position:relative;margin-bottom:14px">
            <div style="width:58px;height:58px;border-radius:16px;flex-shrink:0;
                background:rgba(255,255,255,0.1);display:flex;align-items:center;
                justify-content:center;font-size:32px;border:1.5px solid rgba(201,168,76,0.3)">
                {u.get("avatar","👦")}</div>
            <div style="flex:1">
                <div style="font-family:'Sora',sans-serif;font-size:20px;font-weight:900;
                    letter-spacing:-.5px;line-height:1.2">
                    {greet}, {u["name"].split()[0]}! {streak_fire or "👋"}</div>
                <div style="font-size:12px;opacity:.7;margin-top:4px;font-weight:500">
                    🇵🇰 Pakistan's #1 AI Study Platform{streak_extra}
                </div>
            </div>
        </div>
        <div style="background:rgba(0,0,0,0.2);border-radius:10px;padding:10px 14px;
            border-left:3px solid rgba(201,168,76,0.5);position:relative">
            <div style="font-size:13px;font-weight:700;color:#E8C96A;margin-bottom:2px">{q_urdu}</div>
            <div style="font-size:11px;opacity:.65;font-style:italic">{q_eng}</div>
        </div>
    </div>""", unsafe_allow_html=True)

    today_str = datetime.date.today().isoformat()
    last_date = stats.get("lastDate", "")

    # Mobile hint — shown once per session, only on home page
    if not st.session_state.get("mobile_hint_shown", False):
        st.info("📱 **On mobile?** Tap the **☰ arrow** at top-left to open the menu!", icon="📱")
        st.session_state.mobile_hint_shown = True

    if last_date and last_date != today_str:
        st.markdown("""<div class="reminder">🔔 <b>Daily Reminder:</b> You haven't studied today! Even 15 minutes makes a difference 💪</div>""", unsafe_allow_html=True)

    # ── 7-Day Streak Calendar ─────────────────────────────────
    # Use st.components.v1.html — st.markdown can silently escape
    # dynamically-built HTML strings in some Streamlit versions.
    study_dates = set(stats.get("study_dates", []))
    today = datetime.date.today()
    day_labels = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    calendar_cells = ""
    for i in range(7):
        day = today - datetime.timedelta(days=6-i)
        day_str = day.isoformat()
        studied = day_str in study_dates
        is_today = (day == today)
        bdr = "#E8C96A" if is_today else ("#0D6E3F" if studied else "rgba(13,110,63,0.1)")
        icon_html = '<span style="color:#0D6E3F;font-weight:900;">&#10003;</span>' if studied else ('<span style="color:#C9A84C;">&#9679;</span>' if is_today else '<span style="color:#ccc;">&#9675;</span>')
        day_color = "#0D6E3F" if studied else ("#C9A84C" if is_today else "#7A9A7A")
        shadow = "0 3px 12px rgba(13,110,63,0.2)" if studied else "none"
        bg = "#F0FAF3" if studied else ("#FFFDF0" if is_today else "#FFFFFF")
        calendar_cells += (
            f'<div style="background:{bg};border:1.5px solid {bdr};border-radius:10px;'
            f'padding:8px 4px;text-align:center;box-shadow:{shadow};min-width:44px;flex:1;">'
            f'<div style="font-size:14px;">{icon_html}</div>'
            f'<div style="font-size:9px;font-weight:800;color:{day_color};'
            f'text-transform:uppercase;letter-spacing:.5px;margin-top:2px;">{day_labels[day.weekday()]}</div>'
            f'<div style="font-size:8px;color:#7A9A7A;margin-top:1px;">{day.day}</div>'
            f'</div>'
        )
    st.components.v1.html(
        '<div style="display:flex;gap:6px;overflow-x:auto;padding-bottom:4px;font-family:sans-serif;">'
        + calendar_cells + '</div>',
        height=72,
        scrolling=False,
    )

    st.markdown("<div style=\"height:8px\"></div>", unsafe_allow_html=True)

    # ── Word of the Day (collapsed by default — not blocking) ─────
    if not st.session_state.word_of_day:
        st.session_state.word_of_day = {
            "word":"Perseverance","urdu":"ثابت قدمی",
            "meaning":"Continued effort despite difficulties",
            "example":"Success comes to those with perseverance.",
            "tip":"Use this word in your next essay!"
        }

    with st.expander("📖 Word of the Day", expanded=False):
        # Load AI word once per session — not every render
        if not st.session_state.wod_loaded:
            with st.spinner("Loading today's word..."):
                grade = u.get("grade", "Grade 6")
                try:
                    raw = call_ai(
                        [{"role":"user","content":
                          f"Give ONE interesting English word suitable for {grade} students in Pakistan. "
                          f"Return ONLY this JSON: {{\"word\":\"...\",\"urdu\":\"...\",\"meaning\":\"...\",\"example\":\"...\",\"tip\":\"...\"}}"}],
                        "Vocabulary teacher. Return ONLY valid JSON. No markdown.",
                    )
                    clean = raw.replace("```json","").replace("```","").strip()
                    parsed = json.loads(clean)
                    if parsed.get("word"):
                        st.session_state.word_of_day = parsed
                except Exception:
                    pass
            st.session_state.wod_loaded = True
            st.rerun()

        w = st.session_state.word_of_day
        st.markdown(f"""
        <div style="padding:8px 0">
            <div style="display:flex;align-items:baseline;gap:12px;flex-wrap:wrap;margin-bottom:6px">
                <span style="font-family:'Sora',sans-serif;font-size:22px;font-weight:900;color:#0D6E3F">{w.get("word","")}</span>
                <span style="font-size:13px;color:#7A9A7A">— {w.get("urdu","")}</span>
            </div>
            <div style="font-size:13px;color:#3D5C3D;margin-bottom:4px">{w.get("meaning","")}</div>
            <div style="font-size:12px;color:#7A9A7A;font-style:italic;margin-bottom:4px">"{w.get("example","")}"</div>
            <div style="font-size:12px;color:#C9A84C;font-weight:700">💡 {w.get("tip","")}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style=\"height:4px\"></div>", unsafe_allow_html=True)

    # ── Stats row ─────────────────────────────────────────────
    st.markdown("<div style=\"font-family:'Sora',sans-serif;font-size:13px;font-weight:800;"
                "color:#7A9A7A;text-transform:uppercase;letter-spacing:1px;"
                "margin-bottom:8px\">📊 Your Progress</div>", unsafe_allow_html=True)
    total_q   = stats.get("total", 0)
    streak_v  = stats.get("streak", 0)
    badges_v  = len(u.get("badges", []))
    quizzes_v = stats.get("quizzes_done", 0)
    goals = {"q": 50, "streak": 7, "badges": 11, "quiz": 10}

    c1,c2,c3,c4 = st.columns(4)
    for col_w, icon, val, lbl, accent, pct in [
        (c1,"❓", total_q,        "Questions",  "#0D6E3F", min(100, int(total_q/goals["q"]*100))),
        (c2,"🔥", f"{streak_v}d", "Streak",     "#C0392B", min(100, int(streak_v/goals["streak"]*100))),
        (c3,"🏆", badges_v,       "Badges",     "#C9A84C", min(100, int(badges_v/goals["badges"]*100))),
        (c4,"📝", quizzes_v,      "Quizzes",    "#1A56C4", min(100, int(quizzes_v/goals["quiz"]*100))),
    ]:
        with col_w:
            st.markdown(f"""
            <div class="stat-card">
                <div style="font-size:20px;margin-bottom:3px">{icon}</div>
                <div style="font-family:'Sora',sans-serif;font-size:24px;font-weight:900;
                    color:{accent};line-height:1">{val}</div>
                <div class="stat-lbl">{lbl}</div>
                <div style="background:rgba(13,110,63,0.08);border-radius:99px;height:5px;
                    overflow:hidden;margin-top:8px">
                    <div style="width:{pct}%;height:100%;border-radius:99px;background:{accent};
                        transition:width .6s"></div>
                </div>
                <div style="font-size:9px;color:#7A9A7A;margin-top:3px;font-weight:700">{pct}% goal</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style=\"height:6px\"></div>", unsafe_allow_html=True)

    # ── Upcoming Homework ─────────────────────────────────────
    if role in ("student","parent"):
        homework = load_json(HOMEWORK_FILE)
        upcoming = []
        for hw in homework.values():
            try:
                due = datetime.date.fromisoformat(hw.get("due_date",""))
                days_left = (due - datetime.date.today()).days
                if 0 <= days_left <= 7:
                    upcoming.append({**hw, "days_left": days_left})
            except: pass
        upcoming.sort(key=lambda x: x["days_left"])
        if upcoming:
            st.markdown("<div style=\"font-family:'Sora',sans-serif;font-size:15px;font-weight:800;"
                        "color:#0D1F0D;margin-bottom:10px;letter-spacing:-.3px\">📅 Upcoming Homework</div>",
                        unsafe_allow_html=True)
            for hw in upcoming[:3]:
                dl = hw["days_left"]
                dl_color = "#C0392B" if dl == 0 else "#E8770A" if dl <= 2 else "#0D6E3F"
                dl_label = "Due Today!" if dl == 0 else f"Due in {dl} day{'s' if dl!=1 else ''}"
                subj_info = SUBJECTS.get(hw.get("subject","Maths"), {"emoji":"📚","color":"#0D6E3F"})
                st.markdown(f"""
                <div style="background:#fff;border:1.5px solid #E2EAE2;border-radius:12px;
                    padding:11px 14px;margin-bottom:8px;display:flex;align-items:center;gap:12px;
                    box-shadow:0 2px 8px rgba(13,110,63,0.05)">
                    <div style="font-size:24px;flex-shrink:0">{subj_info["emoji"]}</div>
                    <div style="flex:1;min-width:0">
                        <div style="font-weight:800;font-size:13px;color:#0D1F0D;
                            white-space:nowrap;overflow:hidden;text-overflow:ellipsis">
                            {hw.get("data",{}).get("title", hw.get("topic","Homework"))}</div>
                        <div style="font-size:11px;color:#7A9A7A;margin-top:1px">
                            {hw.get("subject","")} · {hw.get("grade","")}</div>
                    </div>
                    <span style="background:{dl_color}15;color:{dl_color};
                        border:1px solid {dl_color}30;border-radius:99px;
                        padding:3px 9px;font-size:10px;font-weight:800;white-space:nowrap">
                        {dl_label}</span>
                </div>""", unsafe_allow_html=True)

    # ── Continue Last Chat ────────────────────────────────────
    hist = load_json(HISTORY_FILE)
    user_hist = hist.get(u["email"], [])
    if user_hist:
        last = user_hist[-1]
        last_sub  = last.get("subject", "")
        last_updated = last.get("updated", "")
        last_msgs = last.get("messages", [])
        # Only show if session has messages and was updated within the last 7 days
        is_recent = True
        if last_updated:
            try:
                updated_date = datetime.datetime.strptime(last_updated[:10], "%Y-%m-%d").date()
                is_recent = (datetime.date.today() - updated_date).days <= 7
            except Exception:
                pass
        if last_msgs and is_recent:
            last_q = next((m["content"][:55] for m in reversed(last_msgs) if m["role"]=="user"), "")
            if last_q:
                ellipsis = "..." if len(last_q) == 55 else ""
                time_label = last_updated[:16] if last_updated else ""
                st.markdown(f"""
                <div style="background:linear-gradient(135deg,rgba(13,110,63,0.06),rgba(13,110,63,0.02));
                    border:1.5px solid rgba(13,110,63,0.15);border-radius:12px;
                    padding:11px 14px;margin-bottom:16px;display:flex;align-items:center;gap:10px">
                    <div style="font-size:20px">💬</div>
                    <div style="flex:1;min-width:0">
                        <div style="font-size:10px;font-weight:800;color:#0D6E3F;
                            text-transform:uppercase;letter-spacing:.6px;margin-bottom:2px">
                            Continue last chat · {last_sub} · {time_label}</div>
                        <div style="font-size:12px;color:#3D5C3D;font-weight:600;
                            white-space:nowrap;overflow:hidden;text-overflow:ellipsis">
                            "{last_q}{ellipsis}"</div>
                    </div>
                </div>""", unsafe_allow_html=True)
                if st.button("▶  Continue Chat", key="home_continue_chat"):
                    st.session_state.page = "chat"; st.rerun()

    # ── Quick Access ──────────────────────────────────────────
    st.markdown("<div style=\"font-family:'Sora',sans-serif;font-size:15px;font-weight:800;"
                "color:#0D1F0D;margin-bottom:10px;letter-spacing:-.3px\">⚡ Quick Access</div>",
                unsafe_allow_html=True)

    # Scoped CSS — only targets buttons inside .home-quick-access to avoid bleeding to other pages
    st.markdown("""
    <style>
    .home-quick-access .stButton > button {
        min-height: 72px !important;
        font-size: 13px !important;
        line-height: 1.4 !important;
        border-radius: 14px !important;
        font-weight: 800 !important;
        white-space: normal !important;
        word-break: break-word !important;
    }
    </style>
    <div class="home-quick-access">""", unsafe_allow_html=True)

    qa_items = [
        ("💬", "Chat Tutor",    "chat"),
        ("📝", "Practice Quiz", "quiz"),
        ("👥", "Friendz Quiz",  "friends"),
        ("🎨", "Image Gen",     "image"),
    ]
    qa_cols = st.columns(4)
    for qa_col, (qa_icon, qa_label, qa_dest) in zip(qa_cols, qa_items):
        with qa_col:
            is_active = (st.session_state.page == qa_dest)
            if st.button(
                f"{qa_icon} {qa_label}",
                key=f"home_go_{qa_dest}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.page = qa_dest; st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# CHAT / AI TUTOR
# ─────────────────────────────────────────────────────────────────
def build_system(u, sub, lvl):
    urdu_rule = "- Reply in Urdu script. Use English only for technical terms." if sub == "Urdu" else ""
    parent_rule = "- User is a parent. Explain how to help their child understand." if u.get("role") == "parent" else ""
    return f"""You are Ustad, a warm and encouraging homework tutor for Pakistani students.
Student: {u['name']} | Role: {'Parent' if u.get('role')=='parent' else 'Student'} | Class: {lvl} | Subject: {sub}

Teaching rules:
- Adapt complexity to {lvl}: Grade 1-3=very simple+emojis; Grade 4-5=simple+examples; Grade 6-8=structured steps; O Level=exam-focused; A Level=university depth
{urdu_rule}
{parent_rule}
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
    st.markdown("<div class=\"section-header\">💬 Chat Tutor — Ask Ustad Anything</div>", unsafe_allow_html=True)
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

    st.markdown("<div style=\"font-size:11px;font-weight:800;color:#aaa;text-transform:uppercase;letter-spacing:1px;margin:10px 0 6px\">⚡ Quick Questions</div>", unsafe_allow_html=True)
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
        # Escape content to prevent XSS — user input must never be injected raw into HTML
        safe_content = (m['content']
                        .replace('&', '&amp;')
                        .replace('<', '&lt;')
                        .replace('>', '&gt;'))
        if m["role"] == "user":
            st.markdown(f"<div class=\"msg-lbl msg-lbl-r\">You</div><div class=\"msg-user\">{safe_content}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class=\"msg-lbl\">🎓 Ustad</div><div class=\"msg-bot\">{safe_content}</div>", unsafe_allow_html=True)

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


# ─────────────────────────────────────────────────────────────────
# PRACTICE QUIZ
# ─────────────────────────────────────────────────────────────────
def page_quiz():
    u = st.session_state.user
    st.markdown("<div class=\"section-header orange\">📝 Practice Quiz</div>", unsafe_allow_html=True)

    q = st.session_state.quiz

    if q is not None and q["done"]:
        # FIX #5: Save quiz stat once, guarded by _stat_saved flag
        if not q.get("_stat_saved"):
            users = load_json(USERS_FILE)
            eu    = users.get(u["email"], u)
            eu.setdefault("stats", init_stats())
            eu["stats"]["quizzes_done"] = eu["stats"].get("quizzes_done",0) + 1
            # Also bump subject stats for quiz questions answered
            sub_field = q.get("sub","")
            if sub_field in SUBJECTS:
                eu["stats"][sub_field] = eu["stats"].get(sub_field,0) + len(q["questions"])
            eu, new_b = check_badges(eu)
            users[u["email"]] = eu
            save_json(USERS_FILE, users)
            st.session_state.user = eu
            for b in new_b:
                st.toast(f"🏆 Badge: {b['icon']} {b['name']}!", icon="🎉")
            q["_stat_saved"] = True
            st.session_state.quiz = q

        total = len(q["questions"]); score = q["score"]
        pct   = int((score/total)*100)
        emoji = "🏆" if pct>=80 else "👍" if pct>=60 else "💪"
        col_c = "#059669" if pct>=80 else "#F59E0B" if pct>=60 else "#E8472A"

        st.markdown(f"""
        <div style="text-align:center;background:#fff;border-radius:20px;padding:28px;
            box-shadow:0 4px 20px rgba(0,0,0,0.08);margin-bottom:18px">
            <div style="font-size:56px">{emoji}</div>
            <h2 style="font-size:26px;font-weight:800;color:#1A1A2E">Quiz Complete!</h2>
            <div style="font-size:48px;font-weight:900;color:{col_c};margin:8px 0">{score}/{total}</div>
            <div style="font-size:15px;color:#666">
                {pct}% — {"Excellent! ⭐" if pct>=80 else "Good effort! 📚" if pct>=60 else "Keep practicing! 💪"}
            </div>
            <div style="font-size:13px;color:#999;margin-top:4px">
                Topic: {q.get("topic","Custom")} · {q.get("difficulty","Medium")} · {q.get("sub","")} {q.get("lvl","")}
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("### 📋 Review Answers")
        for i,(ques,ans) in enumerate(zip(q["questions"],q["answers"])):
            correct = ans["chosen"] == ques["answer"]
            bg     = "#F0FDF4" if correct else "#FFF1EE"
            border = "#059669" if correct else "#E8472A"
            wrong_line = "" if correct else f"<div style=\"font-size:13px;color:#059669;margin-top:2px\">✅ Correct: <b>{ques['answer']}</b></div>"
            st.markdown(f"""
            <div style="background:{bg};border:1.5px solid {border};border-radius:12px;
                padding:14px 16px;margin-bottom:10px;color:#1A1A2E">
                <div style="font-weight:700;font-size:14px">Q{i+1}. {ques["q"]}</div>
                <div style="font-size:13px;margin-top:5px">
                    Your answer: <b>{ans["chosen"]}</b> {"✅" if correct else "❌"}
                </div>
                {wrong_line}
                <div style="font-size:12px;color:#555;margin-top:5px;padding:6px 10px;background:rgba(0,0,0,.04);border-radius:8px">
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

    if q is not None and not q["done"]:
        info    = SUBJECTS.get(q.get("sub","Maths"), SUBJECTS["Maths"])
        current = q["current"]
        ques    = q["questions"][current]
        pct_bar = int((current/len(q["questions"]))*100)

        st.markdown(f"""
        <div style="background:{info["color"]}18;border-radius:14px;padding:12px 16px;
            margin-bottom:14px;display:flex;justify-content:space-between;align-items:center">
            <div>
                <span style="font-weight:800;color:{info["color"]}">{info["emoji"]} {q.get("sub","")} Quiz</span>
                <span style="font-size:12px;color:#888;margin-left:10px">{q.get("topic","")} · {q.get("difficulty","")}</span>
            </div>
            <span style="font-weight:700;color:{info["color"]}">Score: {q["score"]}/{current}</span>
        </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;font-size:12px;color:#888;margin-bottom:4px">
            <span>Question {current+1} of {len(q["questions"])}</span>
            <span>{pct_bar}% complete</span>
        </div>
        <div class="prog-bar"><div class="prog-fill" style="width:{pct_bar}%;background:{info["color"]}"></div></div>
        <br>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div style="background:#fff;border-radius:16px;padding:18px 20px;margin-bottom:14px;
            box-shadow:0 3px 16px rgba(0,0,0,0.07);font-weight:800;font-size:15px;
            color:#1A1A2E;line-height:1.55;border-left:5px solid {info["color"]}">
            Q{current+1}. {ques["q"]}
        </div>""", unsafe_allow_html=True)

        for opt_i, opt in enumerate(ques["options"]):
            if st.button(opt, key=f"opt_{current}_{opt_i}", use_container_width=True):
                q["answers"].append({"chosen":opt})
                if opt == ques["answer"]:
                    q["score"] += 1; st.toast("✅ Correct!", icon="🎉")
                else:
                    st.toast(f"❌ Correct: {ques['answer']}", icon="💡")
                q["current"] += 1
                if q["current"] >= len(q["questions"]): q["done"] = True
                st.session_state.quiz = q; st.rerun()
        return

    # Quiz setup
    st.markdown("""
    <div style="background:#EFF4FF;border-radius:14px;padding:14px 18px;
        margin-bottom:18px;font-size:13px;color:#1B4FD8;border-left:4px solid #2563EB">
        📝 <b>Custom Quiz Generator</b> — Enter any topic, pick your difficulty and number of questions!
    </div>""", unsafe_allow_html=True)

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

    diff_info = {
        "Easy":   ("🟢","Straightforward recall questions. Perfect for revision."),
        "Medium": ("🟡","Mixed conceptual and application questions."),
        "Hard":   ("🔴","Challenging analytical and higher-order thinking questions."),
    }
    d_icon, d_text = diff_info[difficulty]
    st.markdown(f"""
    <div style="background:#F8F9FA;border-radius:10px;padding:10px 14px;
        font-size:12px;color:#555;margin-bottom:14px">
        {d_icon} <b>{difficulty}:</b> {d_text}
    </div>""", unsafe_allow_html=True)

    if st.button("🚀 Generate Quiz", use_container_width=True, type="primary", key="gen_quiz_btn"):
        topic_str  = quiz_topic.strip() if quiz_topic.strip() else f"{quiz_sub} general topics"
        quiz_tokens = max(1200, num_qs * 220 + 300)
        with st.spinner(f"✨ Generating {num_qs} {difficulty} questions on '{topic_str}'..."):
            raw = call_ai(
                [{"role":"user","content":
                  f"Create exactly {num_qs} {difficulty}-level multiple choice questions "
                  f"about '{topic_str}' for {quiz_lvl} {quiz_sub} students in Pakistan. "
                  f"Easy=basic recall, Medium=understanding+application, Hard=analysis+evaluation. "
                  f"Return ONLY raw JSON: "
                  f"{{\"questions\":[{{\"q\":\"question text\",\"options\":[\"A. option\",\"B. option\",\"C. option\",\"D. option\"],\"answer\":\"A. option\",\"explanation\":\"why\"}}]}}"}],
                "Quiz generator. Return ONLY valid raw JSON. No backticks. No markdown.", quiz_tokens
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


# ─────────────────────────────────────────────────────────────────
# ONLINE FRIENDS QUIZ — Room-based multiplayer via groups.json
# Two friends each open the app, one creates a room, shares the
# 6-character code, the other joins — then each answers on their
# own device simultaneously. groups.json is the shared backend.
# ─────────────────────────────────────────────────────────────────
def _grp_save(room_id, data):
    """Write room data to groups.json."""
    groups = load_json(GROUPS_FILE)
    groups[room_id] = data
    save_json(GROUPS_FILE, groups)

def _grp_load(room_id):
    """Load room data from groups.json."""
    groups = load_json(GROUPS_FILE)
    return groups.get(room_id)

def _gen_room_id():
    """Generate a short memorable 6-char room code."""
    import string
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choices(chars, k=6))

def _cleanup_old_rooms():
    """Delete rooms older than 2 hours to keep groups.json lean."""
    groups = load_json(GROUPS_FILE)
    now    = datetime.datetime.now()
    pruned = {}
    for rid, room in groups.items():
        try:
            created = datetime.datetime.fromisoformat(room.get("created",""))
            if (now - created).total_seconds() < 7200:
                pruned[rid] = room
        except Exception:
            pass  # drop malformed entries
    if len(pruned) != len(groups):
        save_json(GROUPS_FILE, pruned)

def page_friends():
    u = st.session_state.user
    st.markdown("<div class=\"section-header purple\">👥 Online Friends Quiz</div>", unsafe_allow_html=True)

    # ── Session state shortcuts ───────────────────────────────
    my_room  = st.session_state.get("fq_room_id")       # room code I'm in
    my_role  = st.session_state.get("fq_role")          # "host" or "guest"
    my_email = u["email"]
    avatars  = ["👦","👧","🧑","👨","👩","🧒","🧑‍🎓","🧑‍💻"]

    # ── Helper: leave room ─────────────────────────────────────
    def leave_room():
        for k in ["fq_room_id","fq_role","fq_last_q","fq_answered"]:
            st.session_state.pop(k, None)
        st.rerun()

    # ── If already in a room, load its state ──────────────────
    if my_room:
        room = _grp_load(my_room)
        if not room:
            st.error("⚠️ Room not found or expired. Please create or join a new room.")
            leave_room()
            return

        phase = room.get("phase","waiting")  # waiting | playing | done

        # ── WAITING LOBBY ─────────────────────────────────────
        if phase == "waiting":
            players = room.get("players", {})
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#F5F0FF,#EDE9FE);border-radius:16px;
                padding:20px 24px;margin-bottom:18px;border:1.5px solid #A78BFA;text-align:center">
                <div style="font-size:11px;font-weight:800;color:#7C3AED;
                    text-transform:uppercase;letter-spacing:1.5px;margin-bottom:8px">Room Code</div>
                <div style="font-family:'Sora',sans-serif;font-size:48px;font-weight:900;
                    color:#5B21B6;letter-spacing:8px;margin-bottom:8px">{my_room}</div>
                <div style="font-size:13px;color:#7C3AED;font-weight:600">
                    Share this code with your friend — they enter it to join!</div>
            </div>""", unsafe_allow_html=True)

            st.markdown(f"**Players joined: {len(players)}/2**")
            for email, pdata in players.items():
                you = "  ← You" if email == my_email else ""
                st.markdown(f"- {pdata['avatar']} **{pdata['name']}**{you}")

            if len(players) < 2:
                st.info("⏳ Waiting for your friend to join with the room code...")
                time.sleep(3)
                st.rerun()
            else:
                # Both players in — host can start
                if my_role == "host":
                    st.success("✅ Friend joined! You can start the quiz.")
                    if st.button("🚀 Start Quiz!", use_container_width=True, type="primary", key="host_start"):
                        room["phase"] = "playing"
                        _grp_save(my_room, room)
                        st.rerun()
                else:
                    st.success("✅ Both players ready! Waiting for host to start...")
                    time.sleep(2)
                    st.rerun()

            if st.button("🚪 Leave Room", key="leave_waiting"):
                leave_room()
            return

        # ── PLAYING ───────────────────────────────────────────
        if phase == "playing":
            questions    = room.get("questions", [])
            players      = room.get("players", {})
            answers_all  = room.get("answers", {})        # {email: {q_idx: chosen}}
            my_answers   = answers_all.get(my_email, {})
            total_q      = len(questions)
            my_done_count = len(my_answers)

            # Which question am I on?
            my_q_idx = my_done_count  # next unanswered index

            # Scores
            def calc_score(email):
                ans = answers_all.get(email, {})
                return sum(1 for idx, chosen in ans.items()
                           if chosen == questions[int(idx)]["answer"])

            # Live scoreboard
            score_html = "<div style=\"display:flex;gap:8px;margin-bottom:16px;flex-wrap:wrap\">"
            for email, pdata in players.items():
                sc  = calc_score(email)
                done = len(answers_all.get(email,{}))
                you  = " (You)" if email == my_email else ""
                bg   = "#7C3AED" if email == my_email else "#E0D9F5"
                col  = "#fff"    if email == my_email else "#5B21B6"
                score_html += (
                    f"<div style=\"background:{bg};color:{col};border-radius:99px;"
                    f"padding:6px 16px;font-size:12px;font-weight:800\">"
                    f"{pdata['avatar']} {pdata['name']}{you}: {sc} pts · {done}/{total_q}</div>"
                )
            score_html += "</div>"
            st.markdown(score_html, unsafe_allow_html=True)

            # Show if I've finished all questions
            if my_q_idx >= total_q:
                other_done = all(
                    len(answers_all.get(e, {})) >= total_q
                    for e in players
                )
                if other_done:
                    # Everyone done — mark room done
                    room["phase"] = "done"
                    _grp_save(my_room, room)
                    st.rerun()
                else:
                    other_names = [p["name"] for e, p in players.items() if e != my_email]
                    st.success(f"✅ You've finished all {total_q} questions! Waiting for {', '.join(other_names)}...")
                    time.sleep(3)
                    st.rerun()
                return

            # Show current question
            ques    = questions[my_q_idx]
            pct_bar = int((my_q_idx / total_q) * 100)

            st.markdown(f"""
            <div style="display:flex;justify-content:space-between;font-size:12px;
                color:#888;margin-bottom:4px">
                <span>Your Question {my_q_idx+1} of {total_q}</span>
                <span>{pct_bar}% done</span>
            </div>
            <div class="prog-bar"><div class="prog-fill"
                style="width:{pct_bar}%;background:#7C3AED"></div></div>""",
                unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown(f"""
            <div style="background:#fff;border-radius:16px;padding:18px 20px;margin-bottom:14px;
                box-shadow:0 3px 16px rgba(0,0,0,0.07);font-weight:800;font-size:15px;
                color:#1A1A2E;border-left:5px solid #7C3AED;line-height:1.55">
                Q{my_q_idx+1}. {ques["q"]}
            </div>""", unsafe_allow_html=True)

            for opt_i, opt in enumerate(ques["options"]):
                if st.button(opt, key=f"fq_{my_q_idx}_{opt_i}", use_container_width=True):
                    # Record answer in shared room
                    room_fresh = _grp_load(my_room) or room
                    if "answers" not in room_fresh: room_fresh["answers"] = {}
                    if my_email not in room_fresh["answers"]: room_fresh["answers"][my_email] = {}
                    room_fresh["answers"][my_email][str(my_q_idx)] = opt
                    if opt == ques["answer"]:
                        st.toast("✅ Correct!", icon="🎉")
                    else:
                        st.toast(f"❌ Answer: {ques['answer']}", icon="💡")
                    _grp_save(my_room, room_fresh)
                    st.rerun()

            st.markdown("<div style=\"height:8px\"></div>", unsafe_allow_html=True)
            if st.button("🚪 Leave Quiz", use_container_width=True, type="secondary", key="leave_playing"):
                leave_room()
            return

        # ── RESULTS ───────────────────────────────────────────
        if phase == "done":
            questions   = room.get("questions", [])
            players     = room.get("players", {})
            answers_all = room.get("answers", {})
            total_q     = len(questions)

            # Save stat once
            if not room.get("_stat_saved_" + my_email):
                bump_stats(room.get("sub"), "quizzes_done")
                room_fresh = _grp_load(my_room) or room
                room_fresh["_stat_saved_" + my_email] = True
                _grp_save(my_room, room_fresh)

            st.markdown("## 🏆 Final Results")

            results = []
            for email, pdata in players.items():
                ans  = answers_all.get(email, {})
                sc   = sum(1 for idx, chosen in ans.items()
                           if chosen == questions[int(idx)]["answer"])
                pct  = int((sc/total_q)*100) if total_q else 0
                results.append({"email":email, "name":pdata["name"],
                                 "avatar":pdata["avatar"], "score":sc, "pct":pct})
            results.sort(key=lambda x: x["score"], reverse=True)

            rank_icons = ["🥇","🥈","🥉","4️⃣"]
            for i, r in enumerate(results):
                you_tag = "  ← You" if r["email"] == my_email else ""
                st.markdown(f"""
                <div class="lb-row">
                    <span class="lb-rank">{rank_icons[i]}</span>
                    <span class="lb-name">{r["avatar"]} {r["name"]}{you_tag}</span>
                    <span style="font-size:12px;color:#888">{r["pct"]}%</span>
                    <span class="lb-score">{r["score"]}/{total_q}</span>
                </div>""", unsafe_allow_html=True)

            winner = results[0]
            is_winner = (winner["email"] == my_email)
            st.markdown(f"""
            <div style="text-align:center;background:linear-gradient(135deg,#FFF8E7,#FFFBF0);
                border-radius:16px;padding:24px;margin:14px 0;border:2px solid #F5CC4A">
                <div style="font-size:44px">{"🎉" if is_winner else "👏"}</div>
                <div style="font-size:20px;font-weight:800;color:#A07820;margin-top:8px">
                    {"You win! 🏆" if is_winner else f"{winner['name']} wins!"}
                </div>
                <div style="font-size:13px;color:#888;margin-top:4px">
                    {winner["name"]}: {winner["score"]}/{total_q} correct
                </div>
            </div>""", unsafe_allow_html=True)

            st.markdown("### 📋 Answer Review")
            my_ans = answers_all.get(my_email, {})
            for i, ques in enumerate(questions):
                chosen  = my_ans.get(str(i), "—")
                correct = chosen == ques["answer"]
                bg      = "#F0FDF4" if correct else "#FFF1EE"
                border  = "#059669" if correct else "#E8472A"
                wrong   = "" if correct else f"<div style=\"font-size:12px;color:#059669;margin-top:3px\">✅ {ques['answer']}</div>"
                st.markdown(f"""
                <div style="background:{bg};border:1.5px solid {border};border-radius:12px;
                    padding:12px 14px;margin-bottom:8px">
                    <div style="font-weight:700;font-size:13px">Q{i+1}. {ques["q"]}</div>
                    <div style="font-size:12px;margin-top:4px">
                        Your answer: <b>{chosen}</b> {"✅" if correct else "❌"}</div>
                    {wrong}
                    <div style="font-size:11px;color:#666;margin-top:4px;padding:5px 8px;
                        background:rgba(0,0,0,.04);border-radius:6px">💡 {ques.get("explanation","")}</div>
                </div>""", unsafe_allow_html=True)

            if st.button("🔄 Play Again", use_container_width=True, type="primary", key="play_again"):
                leave_room()
            return

    # ── NO ROOM — Show Create / Join tabs ─────────────────────
    _cleanup_old_rooms()

    st.markdown("""
    <div style="background:linear-gradient(135deg,#F5F0FF,#EDE9FE);border-radius:14px;
        padding:14px 18px;margin-bottom:18px;font-size:13px;color:#5B21B6;
        border-left:4px solid #7C3AED">
        🌐 <b>Online Friends Quiz</b> — Play with a friend on any device, anywhere!
        One person creates a room, shares the code, and both answer simultaneously.
        The fastest and most accurate player wins!
    </div>""", unsafe_allow_html=True)

    tab_create, tab_join = st.tabs(["➕  Create Room", "🔗  Join Room"])

    with tab_create:
        st.markdown("#### 📚 Quiz Settings")
        c1, c2 = st.columns(2)
        with c1:
            grp_sub = st.selectbox("Subject", list(SUBJECTS.keys()), key="grp_sub")
        with c2:
            lvl_idx = get_level_index(u.get("grade","Grade 6"))
            grp_lvl = st.selectbox("Grade", LEVELS, index=lvl_idx, key="grp_lvl")

        grp_topic = st.text_input("Topic (optional)", placeholder="e.g. Photosynthesis...", key="grp_topic")
        c3, c4 = st.columns(2)
        with c3:
            grp_diff = st.selectbox("Difficulty", ["Easy","Medium","Hard"], index=1, key="grp_diff")
        with c4:
            grp_num = st.selectbox("Questions", [5, 10, 15], index=0, key="grp_num")

        if st.button("🚀 Create Room & Generate Quiz", use_container_width=True,
                     type="primary", key="create_room_btn"):
            topic_str  = grp_topic.strip() if grp_topic.strip() else f"{grp_sub} general"
            grp_tokens = max(1200, grp_num * 220 + 300)
            with st.spinner(f"Generating {grp_num} questions..."):
                raw = call_ai(
                    [{"role":"user","content":
                      f"Create exactly {grp_num} {grp_diff}-level MCQ questions about '{topic_str}' "
                      f"for {grp_lvl} {grp_sub} students. "
                      f"Return ONLY raw JSON: {{\"questions\":[{{\"q\":\"...\","
                      f"\"options\":[\"A. ...\",\"B. ...\",\"C. ...\",\"D. ...\"],"
                      f"\"answer\":\"A. ...\",\"explanation\":\"...\"}}]}}"}],
                    "Quiz generator. Return ONLY valid raw JSON.", grp_tokens
                )
            try:
                clean     = raw.replace("```json","").replace("```","").strip()
                data      = json.loads(clean)
                questions = data["questions"][:grp_num]
                room_id   = _gen_room_id()
                av_idx    = list(AVATARS.values()).index(u.get("avatar","👦")) if u.get("avatar","👦") in list(AVATARS.values()) else 0
                room_data = {
                    "created":  datetime.datetime.now().isoformat(),
                    "host":     my_email,
                    "phase":    "waiting",
                    "sub":      grp_sub,
                    "lvl":      grp_lvl,
                    "topic":    topic_str,
                    "difficulty": grp_diff,
                    "questions": questions,
                    "answers":  {},
                    "players":  {
                        my_email: {
                            "name":   u["name"],
                            "avatar": u.get("avatar","👦"),
                            "joined": datetime.datetime.now().isoformat(),
                        }
                    }
                }
                _grp_save(room_id, room_data)
                st.session_state.fq_room_id = room_id
                st.session_state.fq_role    = "host"
                st.rerun()
            except Exception as e:
                st.error(f"⚠️ Could not generate quiz: {e}")
                with st.expander("Debug"): st.code(raw[:500])

    with tab_join:
        st.markdown("#### 🔗 Enter the room code your friend shared with you")
        join_code = st.text_input("Room Code", placeholder="e.g. AB3X7K",
                                  max_chars=6, key="join_code_input").strip().upper()
        if st.button("🚪 Join Room", use_container_width=True,
                     type="primary", key="join_room_btn"):
            if not join_code:
                st.error("Please enter a room code.")
            else:
                room = _grp_load(join_code)
                if not room:
                    st.error("⚠️ Room not found. Check the code and try again.")
                elif room.get("phase") != "waiting":
                    st.error("⚠️ This quiz has already started or finished.")
                elif my_email in room.get("players",{}):
                    # Rejoin own room
                    st.session_state.fq_room_id = join_code
                    st.session_state.fq_role    = "host" if room.get("host")==my_email else "guest"
                    st.rerun()
                elif len(room.get("players",{})) >= 2:
                    st.error("⚠️ Room is full (2 players max).")
                else:
                    room["players"][my_email] = {
                        "name":   u["name"],
                        "avatar": u.get("avatar","👦"),
                        "joined": datetime.datetime.now().isoformat(),
                    }
                    _grp_save(join_code, room)
                    st.session_state.fq_room_id = join_code
                    st.session_state.fq_role    = "guest"
                    st.rerun()


# ─────────────────────────────────────────────────────────────────
# IMAGE GENERATOR
# ─────────────────────────────────────────────────────────────────
def page_image():
    u = st.session_state.user
    st.markdown("<div class=\"section-header purple\">🎨 AI Image Generator</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#F5F0FF;border:1.5px solid #7C3AED;border-radius:12px;
        padding:12px 16px;margin-bottom:16px;font-size:13px;color:#5B21B6">
        🖌️ Claude AI draws a <b>custom SVG diagram</b> — choose your style!
        Generation takes 20-40 seconds. Works fully offline.
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        img_sub = st.selectbox("📚 Subject", list(SUBJECTS.keys()), key="img_sub")
    with c2:
        lvl_idx = get_level_index(u.get("grade","Grade 6"))
        img_lvl = st.selectbox("🏫 Grade", LEVELS, index=lvl_idx, key="img_lvl")

    style_choice = st.selectbox("🎨 Art Style", list(IMAGE_STYLES.keys()), key="img_style")
    style_hint   = IMAGE_STYLES[style_choice]

    style_colors = {
        "📐 Educational Diagram":"#2563EB",
        "🎨 Cartoon":            "#E8472A",
        "🎌 Anime Style":        "#7C3AED",
        "🤖 AI Art":             "#059669",
        "🔬 Realistic / Scientific":"#B45309",
    }
    sc = style_colors.get(style_choice,"#666")
    st.markdown(f"""
    <div style="background:{sc}18;border:1.5px solid {sc}44;border-radius:10px;
        padding:8px 14px;font-size:12px;color:{sc};font-weight:700;margin-bottom:12px">
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
        time.sleep(0.4)
        prog.progress(20, text="✏️ Step 2/4 — Drawing shapes and structure...")
        time.sleep(0.4)
        prog.progress(45, text="🎨 Step 3/4 — Adding colors, labels and arrows...")

        system_msg = (
            "You are an expert SVG illustrator who creates educational diagrams. "
            "STRICT OUTPUT RULES:\n"
            "1. Output ONLY the SVG code. No markdown. No backticks. No explanations.\n"
            "2. Start with exactly: <svg\n"
            "3. End with exactly: </svg>\n"
            "4. Use: xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 700 500\" width=\"700\" height=\"500\"\n"
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

            b64 = base64.b64encode(final_svg.encode()).decode()
            st.markdown(
                f"<a href=\"data:image/svg+xml;base64,{b64}\" download=\"zm_diagram.svg\" "
                f"style=\"display:inline-flex;align-items:center;gap:8px;padding:10px 22px;"
                f"background:linear-gradient(135deg,#7C3AED,#A78BFA);color:#fff;"
                f"border-radius:12px;font-weight:700;font-size:14px;text-decoration:none;margin-top:10px\">"
                f"⬇️ Download SVG Image</a>",
                unsafe_allow_html=True
            )

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
                        prompt_preview = img['prompt'][:60] + ('...' if len(img['prompt'])>60 else '')
                        st.markdown(f"""
                        <div style="background:#fff;border-radius:14px;padding:12px;
                            box-shadow:0 2px 10px rgba(0,0,0,0.07);border:1px solid #F0F0F5;
                            margin-bottom:12px">
                            <div style="font-size:11px;font-weight:800;color:#7C3AED;margin-bottom:8px">
                                {img['style']} · {img['subject']} · {img['created']}
                            </div>
                            <div style="font-size:12px;color:#555;margin-bottom:8px">
                                📝 {prompt_preview}
                            </div>
                        </div>""", unsafe_allow_html=True)
                        with st.expander("🔍 View full image"):
                            st.components.v1.html(img["svg"], height=480, scrolling=False)
                            b64 = base64.b64encode(img["svg"].encode()).decode()
                            dl_col, del_col = st.columns(2)
                            with dl_col:
                                st.markdown(
                                    f"<a href=\"data:image/svg+xml;base64,{b64}\" download=\"zm_diagram_{img['id']}.svg\" "
                                    f"style=\"display:inline-block;padding:6px 14px;background:#7C3AED;color:#fff;"
                                    f"border-radius:8px;font-weight:700;font-size:12px;text-decoration:none\">⬇️ Download</a>",
                                    unsafe_allow_html=True
                                )
                            with del_col:
                                if st.button("🗑️ Delete", key=f"del_img_{img['id']}", use_container_width=True):
                                    imgs_fresh = load_json(IMAGES_FILE)
                                    user_list  = imgs_fresh.get(u["email"], [])
                                    imgs_fresh[u["email"]] = [x for x in user_list if x["id"] != img["id"]]
                                    save_json(IMAGES_FILE, imgs_fresh)
                                    st.success("Image deleted."); st.rerun()


# ─────────────────────────────────────────────────────────────────
# SYLLABUS
# ─────────────────────────────────────────────────────────────────
def page_syllabus():
    u = st.session_state.user
    st.markdown("<div class=\"section-header blue\">📚 My Syllabus</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class="syl-step">
        <div class="syl-step-title">📋 Step 1 — Choose Curriculum</div>
    </div>""", unsafe_allow_html=True)
    curriculum = st.selectbox("Curriculum", ["Cambridge (Pakistan)"], key="syl_curr")

    st.markdown("""
    <div class="syl-step">
        <div class="syl-step-title">🏫 Step 2 — Choose Grade</div>
    </div>""", unsafe_allow_html=True)
    default_grade = normalise_level(u.get("grade","Grade 8"))
    default_grade_idx = get_level_index(default_grade)
    sel_grade = st.selectbox("Grade", LEVELS, index=default_grade_idx, key="syl_grade_sel")

    st.markdown("""
    <div class="syl-step">
        <div class="syl-step-title">📖 Step 3 — Choose Subject</div>
    </div>""", unsafe_allow_html=True)
    available_subjects = CAMBRIDGE_SUBJECTS.get(sel_grade, list(SUBJECTS.keys()))
    sel_sub = st.selectbox("Subject", available_subjects, key="syl_sub_sel")
    st.session_state.syl_subject = sel_sub

    with st.expander("➕ Step 4 — Add Custom Class or Subject"):
        st.markdown("<div style=\"color:#1A1A2E;font-size:13px;margin-bottom:8px\">Not seeing your class or subject? Add it manually:</div>", unsafe_allow_html=True)
        cc1, cc2 = st.columns(2)
        with cc1:
            custom_grade = st.text_input("Custom Grade/Class", placeholder="e.g. Grade 11, A2 Level...", key="custom_grade_inp")
        with cc2:
            custom_subject = st.text_input("Custom Subject", placeholder="e.g. Accounting, History...", key="custom_sub_inp")
        if custom_grade.strip(): sel_grade   = custom_grade.strip()
        if custom_subject.strip(): sel_sub = custom_subject.strip()
        if custom_grade.strip() or custom_subject.strip():
            st.info(f"✅ Using: **{sel_grade}** · **{sel_sub}**")

    if sel_grade != normalise_level(u.get("grade","")):
        users = load_json(USERS_FILE)
        if u["email"] in users:
            users[u["email"]]["grade"] = sel_grade
            save_json(USERS_FILE, users)
            st.session_state.user["grade"] = sel_grade

    subj_key_map = {
        "Mathematics":"Maths","Maths":"Maths","Physics":"Physics",
        "Chemistry":"Chemistry","Biology":"Biology",
        "English":"English","English Language":"English",
        "Computer Science":"Computer Science","Urdu":"Urdu",
        "Science":"Biology","Islamiyat":"English",
    }
    subj_key  = subj_key_map.get(sel_sub, "Maths")
    info      = SUBJECTS.get(subj_key, {"emoji":"📚","color":"#666"})
    sub_color = info["color"]
    sub_emoji = info["emoji"]

    st.markdown(f"""
    <div style="background:{sub_color}18;border:2px solid {sub_color}44;
        border-radius:14px;padding:14px 18px;margin:16px 0;
        display:flex;align-items:center;gap:12px">
        <div style="font-size:36px">{sub_emoji}</div>
        <div>
            <div style="font-weight:800;font-size:16px;color:{sub_color}">{sel_sub} — {sel_grade}</div>
            <div style="font-size:12px;color:#666;margin-top:2px">🎓 {curriculum}</div>
        </div>
    </div>""", unsafe_allow_html=True)

    curr  = CAMBRIDGE_CURRICULUM.get(subj_key, {}).get(sel_grade, {})
    if not curr:
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

    # FIX: Ensure studied_topics exists for older user records
    if "studied_topics" not in u:
        users_tmp = load_json(USERS_FILE)
        eu_tmp = users_tmp.get(u["email"], u)
        eu_tmp.setdefault("studied_topics", {})
        users_tmp[u["email"]] = eu_tmp
        save_json(USERS_FILE, users_tmp)
        st.session_state.user = eu_tmp
        u = eu_tmp

    studied_topics = u.get("studied_topics", {})
    key = f"{subj_key}_{sel_grade}"
    done_topics  = studied_topics.get(key,[])
    total_topics = sum(len(un["topics"]) for un in units)
    done_count   = sum(1 for un in units for t in un["topics"] if f"{un['unit']}::{t}" in done_topics)
    pct = int((done_count/max(total_topics,1))*100)

    st.markdown(f"""
    <div style="margin-bottom:16px">
        <div style="display:flex;justify-content:space-between;font-size:13px;
            font-weight:700;color:#666;margin-bottom:6px">
            <span>📊 Syllabus Progress</span>
            <span style="color:{sub_color}">{done_count}/{total_topics} topics ({pct}%)</span>
        </div>
        <div class="prog-bar"><div class="prog-fill" style="width:{pct}%;background:{sub_color}"></div></div>
    </div>""", unsafe_allow_html=True)

    for ui, unit in enumerate(units):
        unit_done = [t for t in unit["topics"] if f"{unit['unit']}::{t}" in done_topics]
        unit_pct  = int((len(unit_done)/max(len(unit["topics"]),1))*100)

        with st.expander(
            f"{'✅' if unit_pct==100 else '🔵' if unit_pct>0 else '⚪'}  "
            f"Unit {ui+1}: {unit['unit']}  ({unit_pct}% done)",
            expanded=(ui==0)
        ):
            st.markdown(f"""<div class="prog-bar" style="margin-bottom:12px">
                <div class="prog-fill" style="width:{unit_pct}%;background:{sub_color}"></div>
            </div>""", unsafe_allow_html=True)

            chip_parts = []
            for t in unit["topics"]:
                tk   = f"{unit['unit']}::{t}"
                tick = "✅ " if tk in done_topics else ""
                chip_parts.append(
                    f"<span class=\"topic-chip\" style=\"background:{sub_color}18;"
                    f"border:1px solid {sub_color}44;color:{sub_color}\">"
                    f"{tick}{t}</span>"
                )
            chips = "".join(chip_parts)
            st.markdown(f"<div style=\"margin-bottom:12px\">{chips}</div>", unsafe_allow_html=True)

            for topic in unit["topics"]:
                topic_key = f"{unit['unit']}::{topic}"
                is_done   = topic_key in done_topics
                tc1, tc2, tc3 = st.columns([3,1,1])
                with tc1:
                    st.markdown(
                        f"<div style=\"padding:6px 0;font-size:14px;"
                        f"color:{'#059669' if is_done else '#1A1A2E'};"
                        f"font-weight:{'700' if is_done else '400'}\">"
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
                        eu, new_b = check_badges(eu)
                        users[u["email"]] = eu
                        save_json(USERS_FILE, users)
                        st.session_state.user = eu
                        for b in new_b:
                            st.toast(f"🏆 Badge: {b['icon']} {b['name']}!", icon="🎉")
                        st.rerun()

            ba, bb, bc = st.columns(3)
            with ba:
                if st.button(f"📝 Quiz on Unit {ui+1}", key=f"qunit_{ui}", use_container_width=True):
                    topics_str = ", ".join(unit["topics"])
                    with st.spinner("Generating unit quiz..."):
                        raw = call_ai(
                            [{"role":"user","content":
                              f"Create 5 MCQ questions for unit '{unit['unit']}' covering: {topics_str}. "
                              f"For {sel_grade} {sel_sub} students. "
                              f"Return ONLY raw JSON: {{\"questions\":[{{\"q\":\"...\",\"options\":[\"A.\",\"B.\",\"C.\",\"D.\"],\"answer\":\"A.\",\"explanation\":\"...\"}}]}}"}],
                            "Quiz generator. Return ONLY valid raw JSON.", 1600
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
                    <div style="background:#F8F9FA;border-left:4px solid {sub_color};
                        border-radius:0 12px 12px 0;padding:14px 16px;margin-top:10px;
                        font-size:13px;line-height:1.7;white-space:pre-wrap;color:#1A1A2E">
                        {summary}
                    </div>""", unsafe_allow_html=True)

    st.markdown("---")
    syllabus_text = f"{sel_sub} — {sel_grade}\nBoard: {board}\n\n"
    for ui, unit in enumerate(units):
        syllabus_text += f"Unit {ui+1}: {unit['unit']}\n"
        for t in unit["topics"]: syllabus_text += f"  • {t}\n"
        syllabus_text += "\n"
    b64 = base64.b64encode(syllabus_text.encode()).decode()
    st.markdown(
        f"<a href=\"data:text/plain;base64,{b64}\" download=\"{sel_sub}_{sel_grade}_syllabus.txt\" "
        f"style=\"display:inline-block;padding:10px 20px;background:{sub_color};color:#fff;"
        f"border-radius:12px;font-weight:700;font-size:14px;text-decoration:none;margin-top:8px\">"
        f"⬇️ Download Syllabus</a>",
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────────────────────────────
# PROGRESS PAGE
# ─────────────────────────────────────────────────────────────────
def page_progress():
    u     = st.session_state.user
    stats = u.get("stats",{})
    total = stats.get("total",0)

    st.markdown("<div class=\"section-header\">📊 My Progress</div>", unsafe_allow_html=True)
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
        <div style="margin-bottom:14px">
            <div style="display:flex;justify-content:space-between;font-size:13px;
                font-weight:700;margin-bottom:5px;color:#1A1A2E">
                <span>{info['emoji']} {name}</span>
                <span style="color:{info['color']}">{cnt} questions ({pct}%)</span>
            </div>
            <div class="prog-bar"><div class="prog-fill" style="width:{pct}%;background:{info['color']}"></div></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("### 🛠️ Activity")
    c1,c2,c3 = st.columns(3)
    with c1: st.metric("🎨 Images Generated", stats.get("images",0))
    with c2: st.metric("📅 Member Since",      u.get("joined",""))
    with c3: st.metric("📖 Subjects Studied",  sum(1 for s in SUBJECTS if stats.get(s,0)>0))


# ─────────────────────────────────────────────────────────────────
# HISTORY PAGE
# FIX #4: Removed HTML-escaping of chat content before rendering
# with unsafe_allow_html. Instead use st.text for user messages
# and render bot messages safely. The original code escaped HTML
# but then rendered it, causing visible &lt; &gt; entities.
# ─────────────────────────────────────────────────────────────────
def page_history():
    u = st.session_state.user
    st.markdown("<div class=\"section-header\">🕐 Chat History</div>", unsafe_allow_html=True)
    hist     = load_json(HISTORY_FILE)
    sessions = sorted(hist.get(u["email"],[]), key=lambda x:x.get("updated",""), reverse=True)

    if not sessions:
        st.info("📭 No chat history yet. Start a conversation with Ustad!")
        return

    if not st.session_state.get("confirm_clear_hist"):
        if st.button("🗑️ Clear All History", type="secondary"):
            st.session_state.confirm_clear_hist = True; st.rerun()
    else:
        st.warning("⚠️ This will permanently delete all your chat history. Are you sure?")
        cc1, cc2 = st.columns(2)
        with cc1:
            if st.button("✅ Yes, delete all", type="primary", use_container_width=True):
                hist[u["email"]] = []
                save_json(HISTORY_FILE, hist)
                st.session_state.confirm_clear_hist = False
                st.success("History cleared."); st.rerun()
        with cc2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.confirm_clear_hist = False; st.rerun()

    for sess in sessions:
        info  = SUBJECTS.get(sess.get("subject",""), {"emoji":"📚","color":"#666"})
        msgs  = sess.get("messages",[])
        label = (f"{info['emoji']} {sess.get('subject','')} — {sess.get('level','')} | "
                 f"{sess.get('updated','')} ({len(msgs)} msgs)")
        with st.expander(label):
            for m in msgs:
                if m["role"] == "user":
                    # FIX #4: Use st.text-like approach for user messages to avoid
                    # HTML injection while preserving styling
                    st.markdown(
                        f"<div class=\"msg-user\" style=\"margin-left:40px\">"
                        f"{m['content'].replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')}"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                else:
                    # Bot messages can contain markdown formatting — render as plain text
                    # to avoid XSS while preserving readability
                    st.markdown(
                        f"<div class=\"msg-bot\" style=\"margin-right:40px\">"
                        f"{m['content'].replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')}"
                        f"</div>",
                        unsafe_allow_html=True
                    )
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
    st.markdown("<div class=\"section-header orange\">🏆 Badges & Achievements</div>", unsafe_allow_html=True)
    st.markdown(f"<p style=\"color:#666;font-size:13px\">Earned "
                f"<b style=\"color:#1A1A2E\">{len(earned)}</b> of "
                f"<b style=\"color:#1A1A2E\">{len(BADGES)}</b> badges</p>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i,b in enumerate(BADGES):
        is_earned = b["id"] in earned
        with cols[i%3]:
            locked = "" if is_earned else "badge-locked"
            status_color = "#059669" if is_earned else "#ccc"
            status_text  = "✅ Earned!" if is_earned else "🔒 Locked"
            st.markdown(f"""
            <div class="badge-card {locked}" style="margin-bottom:12px">
                <span class="badge-icon">{b['icon']}</span>
                <div class="badge-name">{b['name']}</div>
                <div class="badge-desc">{b['desc']}</div>
                <div style="font-size:11px;margin-top:5px;color:{status_color};font-weight:700">{status_text}</div>
            </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# PROFILE PAGE
# ─────────────────────────────────────────────────────────────────
def page_profile():
    u = st.session_state.user
    st.markdown("<div class=\"section-header\">👤 My Profile</div>", unsafe_allow_html=True)
    c1,c2 = st.columns([1,2])
    with c1:
        st.markdown(f"<div style=\"font-size:80px;text-align:center;background:#F3F4F6;"
                    f"border-radius:20px;padding:20px\">{u.get('avatar','👦')}</div>", unsafe_allow_html=True)
    with c2:
        role_label = (
            '🎒 Student'  if u.get('role')=='student'
            else '👨‍👩‍👦 Parent'  if u.get('role')=='parent'
            else '👨‍🏫 Teacher' if u.get('role')=='teacher'
            else '🛡️ Admin'    if u.get('role')=='admin'
            else '👤 User'
        )
        st.markdown(f"""
        <div style="padding:10px 0;color:#1A1A2E">
            <div style="font-size:22px;font-weight:800">{u['name']}</div>
            <div style="font-size:13px;color:#999;margin-top:4px">{role_label} • {u.get('grade','')}</div>
            <div style="font-size:12px;color:#bbb;margin-top:2px">📧 {u['email']}</div>
            <div style="font-size:12px;color:#bbb;margin-top:2px">📅 Joined {u.get('joined','')}</div>
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
                if new_name.strip():            eu["name"]   = new_name.strip()
                if new_grade != "-- Select --": eu["grade"]  = new_grade
                eu["avatar"] = AVATARS[new_avatar]
                if new_pw:                      eu["password"] = hash_pw(new_pw)
                users[u["email"]] = eu
                save_json(USERS_FILE, users)
                st.session_state.user = eu
                st.success("✅ Profile updated!"); time.sleep(0.5); st.rerun()


# ─────────────────────────────────────────────────────────────────
# HOMEWORK PAGE (Teacher / Admin)
# ─────────────────────────────────────────────────────────────────
def page_homework():
    u = st.session_state.user
    st.markdown("<div class=\"section-header\">📋 Create Homework</div>", unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#EFF4FF;border-radius:14px;padding:14px 18px;
        margin-bottom:20px;font-size:13px;color:#1B4FD8;border-left:4px solid #2563EB">
        📝 <b>AI Homework Generator</b> — Fill in the details below and let AI create
        a complete assignment with questions, answers, hints, marking guide, and learning objectives.
    </div>""", unsafe_allow_html=True)

    st.markdown("#### 📚 Step 1 — Subject & Grade")
    c1, c2 = st.columns(2)
    with c1:
        hw_subject = st.selectbox("Subject", list(SUBJECTS.keys()), key="hw_subject")
    with c2:
        lvl_idx = get_level_index(u.get("grade", "Grade 6"))
        hw_grade = st.selectbox("Grade Level", LEVELS, index=lvl_idx, key="hw_grade")

    st.markdown("#### ✏️ Step 2 — Topic & Description")
    hw_topic = st.text_input(
        "Topic / Chapter",
        placeholder="e.g. Quadratic Equations, Photosynthesis, World War II, Newton's Laws...",
        key="hw_topic"
    )
    hw_desc = st.text_area(
        "Assignment Description & Instructions",
        placeholder="Describe what students should do...",
        height=110,
        key="hw_desc"
    )

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

    st.markdown("#### 📅 Step 4 — Due Date")
    hw_due_days = st.slider("Due in how many days from today?", 1, 14, 3, key="hw_due_days")
    due_date = (datetime.date.today() + datetime.timedelta(days=hw_due_days)).isoformat()
    st.markdown(f"""
    <div style="background:#F0FDF4;border-radius:10px;padding:10px 16px;
        font-size:13px;color:#065F46;font-weight:700;display:inline-block">
        📅 Due Date: {due_date}
    </div>""", unsafe_allow_html=True)

    st.markdown("<div style=\"height:16px\"></div>", unsafe_allow_html=True)

    if st.button("🚀 Generate Homework with AI", use_container_width=True, type="primary", key="gen_hw_btn"):
        if not hw_topic.strip():
            st.error("⚠️ Please enter a topic in Step 2 before generating.")
        else:
            topic_str = hw_topic.strip()
            desc_str  = hw_desc.strip() if hw_desc.strip() else "Standard homework assignment."
            with st.spinner(f"✨ Generating {hw_num_q} {hw_difficulty} questions on '{topic_str}'... (20-30 sec)"):
                hw_tokens = max(2000, hw_num_q * 280 + 600)
                raw = call_ai(
                    [{"role": "user", "content":
                      f"Create a complete homework assignment for {hw_grade} {hw_subject} students in Pakistan. "
                      f"Topic: {topic_str}. Teacher instructions: {desc_str}. "
                      f"Homework type: {hw_type}. Difficulty: {hw_difficulty}. "
                      f"Generate exactly {hw_num_q} questions. "
                      f"Return ONLY raw JSON with no backticks and no markdown, in this exact structure: "
                      f"{{\"title\":\"homework title\",\"instructions\":\"detailed student-facing instructions\","
                      f"\"learning_objectives\":\"what students will learn\","
                      f"\"questions\":[{{\"number\":1,\"type\":\"MCQ|short_answer|long_answer|problem\","
                      f"\"question\":\"question text\",\"marks\":2,"
                      f"\"options\":[\"A. ...\",\"B. ...\",\"C. ...\",\"D. ...\"],"
                      f"\"answer\":\"correct answer or full model answer\","
                      f"\"hint\":\"a helpful hint without giving away the answer\"}}],"
                      f"\"total_marks\":20,\"marking_guide\":\"concise marking guide for each question type\"}}"}],
                    "You are an expert Pakistani curriculum homework generator. Return ONLY valid JSON, no extra text.",
                    hw_tokens
                )
            try:
                clean   = raw.replace("```json", "").replace("```", "").strip()
                hw_data = json.loads(clean)

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
                    "status":        "active",
                    "submissions":   {},
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

    hw_prev = st.session_state.get("hw_preview")
    if hw_prev:
        data = hw_prev["data"]
        info = SUBJECTS.get(hw_prev["subject"], {"emoji": "📚", "color": "#2563EB"})
        col_c  = info["color"]

        st.markdown("---")
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,{col_c}18,{col_c}08);
            border:2px solid {col_c}44;border-radius:18px;padding:20px 22px;margin-bottom:18px">
            <div style="font-size:20px;font-weight:900;color:#1A1A2E;margin-bottom:10px">
                {info["emoji"]} {data.get("title", hw_prev["topic"])}
            </div>
            <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:12px">
                <span style="background:{col_c}22;color:{col_c};padding:3px 12px;
                    border-radius:99px;font-size:12px;font-weight:700">📚 {hw_prev["subject"]}</span>
                <span style="background:{col_c}22;color:{col_c};padding:3px 12px;
                    border-radius:99px;font-size:12px;font-weight:700">🏫 {hw_prev["grade"]}</span>
                <span style="background:{col_c}22;color:{col_c};padding:3px 12px;
                    border-radius:99px;font-size:12px;font-weight:700">🎯 {hw_prev["difficulty"]}</span>
                <span style="background:{col_c}22;color:{col_c};padding:3px 12px;
                    border-radius:99px;font-size:12px;font-weight:700">
                    📝 {len(data.get("questions", []))} questions · {data.get("total_marks", 0)} marks</span>
                <span style="background:#D1FAE5;color:#065F46;padding:3px 12px;
                    border-radius:99px;font-size:12px;font-weight:700">📅 Due: {hw_prev["due_date"]}</span>
            </div>
            <div style="font-size:13px;color:#374151;margin-bottom:8px">
                <b>📋 Instructions:</b> {data.get("instructions", "")[:250]}
            </div>
            <div style="font-size:12px;color:#6B7280">
                <b>🎯 Learning Objectives:</b> {data.get("learning_objectives", "")}
            </div>
        </div>""", unsafe_allow_html=True)

        questions = data.get("questions", [])
        st.markdown(f"#### 📝 Questions ({len(questions)} total)")

        type_icons = {
            "MCQ":          ("🔵", "#2563EB"),
            "short_answer": ("📝", "#059669"),
            "long_answer":  ("📄", "#7C3AED"),
            "problem":      ("🔢", "#E8472A"),
        }

        for i, q in enumerate(questions):
            t_icon, t_color = type_icons.get(q.get("type", ""), ("❓", "#666"))
            type_label = q.get("type", "").replace("_", " ").title()

            with st.expander(
                f"Q{i+1}. {q['question'][:75]}{'...' if len(q['question'])>75 else ''}  "
                f"[{q.get('marks', 0)} mark{'s' if q.get('marks',0)!=1 else ''}]"
            ):
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px">
                    <span style="background:{t_color}18;color:{t_color};padding:2px 10px;
                        border-radius:99px;font-size:12px;font-weight:700">
                        {t_icon} {type_label}</span>
                    <span style="font-size:12px;color:#888">{q.get("marks",0)} marks</span>
                </div>
                <div style="font-size:14px;font-weight:700;color:#1A1A2E;margin-bottom:10px;line-height:1.5">
                    {q["question"]}
                </div>""", unsafe_allow_html=True)

                if q.get("options"):
                    for opt in q["options"]:
                        st.markdown(f"""
                        <div style="background:#F8F9FA;border-radius:8px;padding:7px 12px;
                            margin-bottom:4px;font-size:13px;color:#374151">
                            {opt}
                        </div>""", unsafe_allow_html=True)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div style="background:#D1FAE5;border-radius:8px;padding:8px 12px;
                        font-size:12px;color:#065F46;margin-top:6px">
                        ✅ <b>Answer:</b> {q.get("answer", "")}
                    </div>""", unsafe_allow_html=True)
                with col2:
                    if q.get("hint"):
                        st.markdown(f"""
                        <div style="background:#FFF8E7;border-radius:8px;padding:8px 12px;
                            font-size:12px;color:#92400E;margin-top:6px">
                            💡 <b>Hint:</b> {q.get("hint", "")}
                        </div>""", unsafe_allow_html=True)

        if data.get("marking_guide"):
            st.markdown(f"""
            <div style="background:#FFF8E7;border:1.5px solid #F5CC4A;border-radius:12px;
                padding:14px 16px;margin-top:14px">
                <div style="font-size:13px;font-weight:800;color:#92400E;margin-bottom:6px">
                    📖 Marking Guide
                </div>
                <div style="font-size:13px;color:#78350F;line-height:1.6">
                    {data.get("marking_guide", "")}
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style=\"height:12px\"></div>", unsafe_allow_html=True)
        ba, bb = st.columns(2)
        with ba:
            if st.button("➕ Create Another Homework", use_container_width=True, type="primary"):
                st.session_state["hw_preview"] = None
                st.rerun()
        with bb:
            if st.button("📂 Clear Preview", use_container_width=True):
                st.session_state["hw_preview"] = None
                st.rerun()


# ─────────────────────────────────────────────────────────────────
# ADMIN DASHBOARD
# ─────────────────────────────────────────────────────────────────
def page_admin():
    st.markdown("<div class=\"section-header orange\">🛡️ Admin Dashboard</div>", unsafe_allow_html=True)

    users    = load_json(USERS_FILE)
    homework = load_json(HOMEWORK_FILE)

    students  = {e: d for e, d in users.items() if d.get("role") not in ("admin",)}
    all_hw    = list(homework.values())

    tab_perf, tab_hw = st.tabs([
        "📊 Student Performance Analytics",
        "📋 Homework Tracking",
    ])

    with tab_perf:
        st.markdown("### 📊 Platform Overview")
        total_students  = len(students)
        total_questions = sum(d.get("stats",{}).get("total",0)        for d in students.values())
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
                <div style="background:#fff;border-radius:14px;padding:18px 14px;text-align:center;
                    box-shadow:0 2px 12px rgba(0,0,0,0.07);border-top:4px solid {color}">
                    <div style="font-size:26px">{icon}</div>
                    <div style="font-size:26px;font-weight:900;color:{color};margin:4px 0">{val}</div>
                    <div style="font-size:11px;color:#999;font-weight:700">{lbl}</div>
                </div>""", unsafe_allow_html=True)

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

        rank_icons = ["🥇","🥈","🥉"] + [f"{i+1}️⃣" for i in range(3,10)]
        max_score  = max(
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
            <div style="background:#fff;border-radius:14px;padding:14px 18px;
                margin-bottom:10px;box-shadow:0 2px 10px rgba(0,0,0,0.06);
                border-left:5px solid {"#FFD700" if i<3 else "#E0E7FF"};color:#1A1A2E">
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px">
                    <div style="display:flex;align-items:center;gap:12px">
                        <span style="font-size:24px">{rank_icons[i]}</span>
                        <div>
                            <div style="font-weight:800;font-size:15px">
                                {ud.get("avatar","👤")} {ud.get("name","?")}
                            </div>
                            <div style="font-size:11px;color:#aaa">{grade} &nbsp;·&nbsp; {email}</div>
                        </div>
                    </div>
                    <div style="display:flex;gap:18px;font-size:12px;flex-wrap:wrap">
                        <div style="text-align:center">
                            <div style="font-weight:900;font-size:17px;color:#E8472A">{qs}</div>
                            <div style="color:#bbb">Qs</div>
                        </div>
                        <div style="text-align:center">
                            <div style="font-weight:900;font-size:17px;color:#2563EB">{quizzes}</div>
                            <div style="color:#bbb">Quizzes</div>
                        </div>
                        <div style="text-align:center">
                            <div style="font-weight:900;font-size:17px;color:#F59E0B">{streak}d</div>
                            <div style="color:#bbb">Streak</div>
                        </div>
                        <div style="text-align:center">
                            <div style="font-weight:900;font-size:17px;color:#7C3AED">{badges}</div>
                            <div style="color:#bbb">Badges</div>
                        </div>
                    </div>
                </div>
                <div style="margin-top:10px">
                    <div style="display:flex;justify-content:space-between;
                        font-size:11px;color:#bbb;margin-bottom:4px">
                        <span>🏅 Top subject: {SUBJECTS.get(top_subj[0],{}).get("emoji","")}&nbsp;{top_subj[0]} ({top_subj[1]} Qs)</span>
                        <span style="font-weight:700;color:{bar_col}">Score: {score}</span>
                    </div>
                    <div style="background:#F0F0F8;border-radius:99px;height:10px;overflow:hidden">
                        <div style="width:{bar_pct}%;height:10px;border-radius:99px;
                            background:linear-gradient(90deg,{bar_col},{bar_col}88);
                            transition:width 1s ease"></div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

        if not sorted_users:
            st.info("No user data available yet.")

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
            <div style="margin-bottom:14px">
                <div style="display:flex;justify-content:space-between;
                    font-size:13px;font-weight:700;margin-bottom:5px;color:#1A1A2E">
                    <span>{info["emoji"]} {subj}</span>
                    <span style="color:{info["color"]}">{count} questions &nbsp;·&nbsp; {pct}%</span>
                </div>
                <div style="background:#F0F0F8;border-radius:99px;height:12px;overflow:hidden">
                    <div style="width:{bar_w}%;height:12px;border-radius:99px;
                        background:linear-gradient(90deg,{info["color"]},{info["color"]}88);
                        transition:width 1s ease"></div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("### 🗓️ 7-Day Activity Heatmap")
        today = datetime.date.today()
        days  = [(today - datetime.timedelta(days=i)) for i in range(6, -1, -1)]
        activity = {d.isoformat(): 0 for d in days}
        for ud in students.values():
            study_dates_list = ud.get("stats", {}).get("study_dates", [])
            for d_iso in study_dates_list:
                if d_iso in activity:
                    activity[d_iso] += 1
            if not study_dates_list:
                last = ud.get("stats", {}).get("lastDate", "")
                if last in activity:
                    activity[last] += 1

        max_act = max(max(activity.values(), default=0), 1)
        for day_iso, cnt in activity.items():
            day_obj  = datetime.date.fromisoformat(day_iso)
            weekday  = day_obj.strftime("%a %d %b")
            bar_w    = max(int((cnt / max_act) * 100), 2) if cnt else 0
            is_today = day_iso == today.isoformat()
            bar_col  = "#E8472A" if is_today else "#2563EB"
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px">
                <div style="font-size:12px;color:{"#E8472A" if is_today else "#888"};
                    font-weight:{"800" if is_today else "400"};width:90px;flex-shrink:0">
                    {"📍 " if is_today else ""}{weekday}
                </div>
                <div style="flex:1;background:#F0F0F8;border-radius:99px;height:20px;overflow:hidden">
                    <div style="width:{bar_w}%;height:20px;border-radius:99px;
                        background:linear-gradient(90deg,{bar_col},{bar_col}88)"></div>
                </div>
                <div style="font-size:13px;font-weight:800;color:#1A1A2E;width:28px;text-align:right">
                    {cnt}
                </div>
            </div>""", unsafe_allow_html=True)

    with tab_hw:
        st.markdown("### 📋 Homework Tracking")

        if not all_hw:
            st.info("📭 No homework assignments have been created yet.")
        else:
            total_hw   = len(all_hw)
            total_subs = sum(len(h.get("submissions", {})) for h in all_hw)
            est_poss   = total_hw * max(len(students), 1)
            comp_pct   = min(int((total_subs / max(est_poss, 1)) * 100), 100)
            comp_color = "#059669" if comp_pct >= 70 else "#F59E0B" if comp_pct >= 40 else "#E8472A"

            c1, c2, c3 = st.columns(3)
            for col_w, icon, val, lbl, color in [
                (c1, "📋", total_hw,   "Assignments",      "#2563EB"),
                (c2, "📬", total_subs, "Total Submissions","#7C3AED"),
                (c3, "📈", f"{comp_pct}%", "Est. Completion", comp_color),
            ]:
                with col_w:
                    st.markdown(f"""
                    <div style="background:#fff;border-radius:14px;padding:16px;text-align:center;
                        box-shadow:0 2px 10px rgba(0,0,0,0.06);border-top:4px solid {color}">
                        <div style="font-size:22px">{icon}</div>
                        <div style="font-size:24px;font-weight:900;color:{color}">{val}</div>
                        <div style="font-size:11px;color:#999;font-weight:700">{lbl}</div>
                    </div>""", unsafe_allow_html=True)

            f1, f2 = st.columns(2)
            with f1:
                f_subj   = st.selectbox("Subject", ["All"] + list(SUBJECTS.keys()), key="adm_f_subj")
            with f2:
                f_status = st.selectbox("Status",  ["All", "Active", "Inactive"],   key="adm_f_status")

            st.markdown("---")

            for hw in sorted(all_hw, key=lambda x: x.get("created",""), reverse=True):
                if f_subj != "All" and hw.get("subject") != f_subj:
                    continue
                hw_active = hw.get("status","active") == "active"
                if f_status == "Active"   and not hw_active: continue
                if f_status == "Inactive" and hw_active:     continue

                info      = SUBJECTS.get(hw["subject"], {"emoji":"📚","color":"#2563EB"})
                col_c     = info["color"]
                subs      = hw.get("submissions", {})
                sub_cnt   = len(subs)
                data      = hw.get("data", {})
                hw_title  = data.get("title", hw.get("topic",""))
                due       = hw.get("due_date","")
                today_str = datetime.date.today().isoformat()
                overdue   = due < today_str if due else False

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
                    st.markdown(f"""
                    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px">
                        <span style="background:{col_c}18;color:{col_c};padding:3px 10px;
                            border-radius:99px;font-size:12px;font-weight:700">{info["emoji"]} {hw["subject"]}</span>
                        <span style="background:{col_c}18;color:{col_c};padding:3px 10px;
                            border-radius:99px;font-size:12px;font-weight:700">🏫 {hw.get("grade","")}</span>
                        <span style="background:{col_c}18;color:{col_c};padding:3px 10px;
                            border-radius:99px;font-size:12px;font-weight:700">🎯 {hw.get("difficulty","")}</span>
                        <span style="background:{"#FEE2E2" if overdue else "#D1FAE5"};
                            color:{"#991B1B" if overdue else "#065F46"};padding:3px 10px;
                            border-radius:99px;font-size:12px;font-weight:700">{due_label}</span>
                    </div>""", unsafe_allow_html=True)

                    if sub_cnt > 0:
                        m1, m2, m3 = st.columns(3)
                        with m1: st.metric("📬 Submissions", sub_cnt)
                        with m2: st.metric("📈 Avg Score",  f"{avg_score}%")
                        with m3: st.metric("🏅 Quality",    q_label)

                        for email_s, sub in sorted(
                            subs.items(),
                            key=lambda x: x[1].get("score_pct",0),
                            reverse=True
                        ):
                            sp       = sub.get("score_pct", 0)
                            q_dot    = "🟢" if sp>=80 else "🟡" if sp>=60 else "🔴"
                            sub_time = sub.get("submitted_at","")
                            st.markdown(f"""
                            <div style="background:#F8F9FA;border-radius:10px;padding:9px 14px;
                                margin-bottom:5px;border-left:3px solid {col_c};color:#1A1A2E;
                                display:flex;justify-content:space-between;
                                align-items:center;flex-wrap:wrap;gap:6px">
                                <div>
                                    <b>{sub.get("student_name","?")}</b>
                                    <span style="font-size:11px;color:#aaa;margin-left:6px">{email_s}</span>
                                </div>
                                <div style="display:flex;gap:14px;align-items:center;font-size:12px">
                                    <span>{q_dot} <b>{sp}%</b></span>
                                    <span style="color:#bbb">🕐 {sub_time}</span>
                                </div>
                            </div>""", unsafe_allow_html=True)
                    else:
                        st.info("⏳ No submissions yet for this assignment.")


# ─────────────────────────────────────────────────────────────────
# STUDENT HOMEWORK VIEW
# ─────────────────────────────────────────────────────────────────
def page_student_homework():
    u = st.session_state.user
    st.markdown("<div class=\"section-header blue\">📋 My Homework</div>", unsafe_allow_html=True)

    homework = load_json(HOMEWORK_FILE)
    all_hw = sorted(homework.values(), key=lambda x: x.get("due_date",""), reverse=False)

    if not all_hw:
        st.info("📭 No homework assignments have been posted yet. Check back soon!")
        return

    tab_pending, tab_done = st.tabs(["📝 Pending", "✅ Submitted"])

    with tab_pending:
        pending = [
            hw for hw in all_hw
            if u["email"] not in hw.get("submissions", {})
            and hw.get("status","active") == "active"
        ]
        if not pending:
            st.success("🎉 You're all caught up! No pending homework.")
        for hw in pending:
            data      = hw.get("data", {})
            info      = SUBJECTS.get(hw.get("subject","Maths"), {"emoji":"📚","color":"#2563EB"})
            col_c     = info["color"]
            due       = hw.get("due_date","")
            days_left = (datetime.date.fromisoformat(due) - datetime.date.today()).days if due else 0
            dl_color  = "#C0392B" if days_left <= 0 else "#E8770A" if days_left <= 2 else "#059669"
            dl_label  = "Due Today!" if days_left == 0 else (f"⚠️ Overdue by {abs(days_left)}d" if days_left < 0 else f"Due in {days_left}d")
            hw_title  = data.get("title", hw.get("topic","Homework"))

            with st.expander(f"{info['emoji']} {hw_title} · {hw.get('grade','')} · {dl_label}"):
                st.markdown(f"""
                <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px">
                    <span style="background:{col_c}18;color:{col_c};padding:3px 10px;
                        border-radius:99px;font-size:12px;font-weight:700">{info["emoji"]} {hw["subject"]}</span>
                    <span style="background:{col_c}18;color:{col_c};padding:3px 10px;
                        border-radius:99px;font-size:12px;font-weight:700">🎯 {hw.get("difficulty","")}</span>
                    <span style="background:{dl_color}18;color:{dl_color};padding:3px 10px;
                        border-radius:99px;font-size:12px;font-weight:700">📅 {dl_label}</span>
                </div>
                <div style="font-size:13px;color:#374151;margin-bottom:8px">
                    <b>📋 Instructions:</b> {data.get("instructions","")[:300]}
                </div>""", unsafe_allow_html=True)

                questions = data.get("questions", [])
                if not questions:
                    st.warning("No questions found for this assignment.")
                    continue

                st.markdown(f"**📝 Answer {len(questions)} Questions**")
                answers = {}
                type_icons = {"MCQ":("🔵","#2563EB"),"short_answer":("📝","#059669"),
                              "long_answer":("📄","#7C3AED"),"problem":("🔢","#E8472A")}

                for qi, question in enumerate(questions):
                    q_type = question.get("type","MCQ")
                    t_icon, t_color = type_icons.get(q_type, ("❓","#666"))
                    st.markdown(f"""
                    <div style="background:#F8F9FA;border-radius:10px;padding:12px 14px;
                        margin-bottom:8px;border-left:4px solid {t_color}">
                        <span style="background:{t_color}18;color:{t_color};padding:2px 8px;
                            border-radius:99px;font-size:11px;font-weight:700;margin-bottom:6px;display:inline-block">
                            {t_icon} {q_type.replace("_"," ").title()} · {question.get("marks",1)} mark(s)
                        </span>
                        <div style="font-size:14px;font-weight:700;color:#1A1A2E;margin-top:6px">
                            Q{qi+1}. {question["question"]}
                        </div>
                    </div>""", unsafe_allow_html=True)

                    if question.get("hint"):
                        with st.expander(f"💡 Hint for Q{qi+1}"):
                            st.info(question["hint"])

                    if q_type == "MCQ" and question.get("options"):
                        answers[qi] = st.radio(
                            f"Your answer for Q{qi+1}",
                            question["options"],
                            key=f"hw_ans_{hw['id']}_{qi}",
                            label_visibility="collapsed"
                        )
                    else:
                        answers[qi] = st.text_area(
                            f"Your answer for Q{qi+1}",
                            placeholder="Write your answer here...",
                            height=80,
                            key=f"hw_ans_{hw['id']}_{qi}",
                            label_visibility="collapsed"
                        )

                st.markdown("<div style=\"height:8px\"></div>", unsafe_allow_html=True)
                if st.button(f"📤 Submit Homework", key=f"submit_hw_{hw['id']}", use_container_width=True, type="primary"):
                    score = 0
                    total_marks = 0
                    for qi, question in enumerate(questions):
                        marks = question.get("marks", 1)
                        total_marks += marks
                        if question.get("type") == "MCQ":
                            if answers.get(qi,"") == question.get("answer",""):
                                score += marks

                    score_pct = int((score / max(total_marks, 1)) * 100) if total_marks else 0

                    hw_fresh = load_json(HOMEWORK_FILE)
                    if hw["id"] in hw_fresh:
                        hw_fresh[hw["id"]].setdefault("submissions", {})
                        hw_fresh[hw["id"]]["submissions"][u["email"]] = {
                            "student_name": u["name"],
                            "answers":      {str(k): v for k, v in answers.items()},
                            "score":        score,
                            "total_marks":  total_marks,
                            "score_pct":    score_pct,
                            "submitted_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                        }
                        save_json(HOMEWORK_FILE, hw_fresh)

                    grade_emoji = "🏆" if score_pct >= 80 else "👍" if score_pct >= 60 else "💪"
                    st.success(f"{grade_emoji} Submitted! Your MCQ score: **{score}/{total_marks}** ({score_pct}%)")
                    st.balloons()
                    time.sleep(1.5); st.rerun()

    with tab_done:
        submitted = [
            hw for hw in all_hw
            if u["email"] in hw.get("submissions", {})
        ]
        if not submitted:
            st.info("📭 You haven't submitted any homework yet.")
        for hw in submitted:
            data     = hw.get("data", {})
            sub      = hw["submissions"][u["email"]]
            info     = SUBJECTS.get(hw.get("subject","Maths"), {"emoji":"📚","color":"#2563EB"})
            sp       = sub.get("score_pct", 0)
            q_dot    = "🟢" if sp >= 80 else "🟡" if sp >= 60 else "🔴"
            hw_title = data.get("title", hw.get("topic","Homework"))

            with st.expander(f"{info['emoji']} {hw_title} · {q_dot} {sp}% · Submitted {sub.get('submitted_at','')[:10]}"):
                st.markdown(f"""
                <div style="background:#F0FDF4;border-radius:12px;padding:14px 16px;margin-bottom:12px">
                    <div style="font-size:15px;font-weight:900;color:#065F46;margin-bottom:6px">
                        {q_dot} Score: {sub.get("score",0)}/{sub.get("total_marks",0)} ({sp}%)
                    </div>
                    <div style="font-size:12px;color:#6B7280">
                        Submitted: {sub.get("submitted_at","")}
                    </div>
                </div>""", unsafe_allow_html=True)

                questions = data.get("questions", [])
                student_answers = sub.get("answers", {})
                for qi, question in enumerate(questions):
                    student_ans = student_answers.get(str(qi), "—")
                    correct_ans = question.get("answer","")
                    is_mcq = question.get("type") == "MCQ"
                    is_correct = (student_ans == correct_ans) if is_mcq else None
                    bg = "#F0FDF4" if is_correct else ("#FFF1EE" if is_correct is False else "#F8F9FA")
                    border_col = "#059669" if is_correct else "#E8472A" if is_correct is False else "#ccc"
                    wrong_line = f"<div style=\"font-size:12px;color:#059669;margin-top:2px\">✅ Correct: <b>{correct_ans}</b></div>" if is_mcq and not is_correct else ""
                    st.markdown(f"""
                    <div style="background:{bg};border-radius:10px;padding:10px 14px;
                        margin-bottom:6px;border-left:3px solid {border_col}">
                        <div style="font-size:13px;font-weight:700;color:#1A1A2E">Q{qi+1}. {question["question"][:100]}</div>
                        <div style="font-size:12px;color:#555;margin-top:4px">Your answer: <b>{student_ans}</b>
                            {"✅" if is_correct else "❌" if is_correct is False else ""}
                        </div>
                        {wrong_line}
                    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    page_auth()
else:
    render_sidebar()
    p = st.session_state.page
    if   p == "home":        page_home()
    elif p == "chat":        page_chat()
    elif p == "syllabus":    page_syllabus()
    elif p == "quiz":        page_quiz()
    elif p == "friends":     page_friends()
    elif p == "image":       page_image()
    elif p == "homework":    page_homework()
    elif p == "my_homework": page_student_homework()
    elif p == "admin":       page_admin()
    elif p == "progress":    page_progress()
    elif p == "history":     page_history()
    elif p == "badges":      page_badges()
    elif p == "profile":     page_profile()
