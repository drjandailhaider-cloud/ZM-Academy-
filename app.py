# ═══════════════════════════════════════════════════════════════════════════════
# ZM Academy — Futuristic AI Edition 🤖✨
# UI: Neon Cosmos Dark Theme with AI Mascot Characters
# ═══════════════════════════════════════════════════════════════════════════════
import streamlit as st
import json, hashlib, datetime, time, os, base64, random
from anthropic import Anthropic
from curriculum import CAMBRIDGE_CURRICULUM

st.set_page_config(
    page_title="ZM Academy 🤖",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

SUBJECTS = {
    "Maths":           {"emoji": "🔢", "color": "#00FFD1"},
    "Physics":         {"emoji": "⚡", "color": "#60A5FA"},
    "Chemistry":       {"emoji": "🧪", "color": "#A78BFA"},
    "Biology":         {"emoji": "🌱", "color": "#34D399"},
    "English":         {"emoji": "📖", "color": "#F472B6"},
    "Computer Science":{"emoji": "💻", "color": "#818CF8"},
    "Urdu":            {"emoji": "🖊️", "color": "#FBBF24"},
}

LEVELS = [
    "Grade 1","Grade 2","Grade 3","Grade 4","Grade 5",
    "Grade 6","Grade 7","Grade 8","Grade 9","Grade 10",
    "O Level","A Level"
]

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
    "🤖 Robot":"🤖","🚀 Astronaut":"🚀","🧑‍🔬 Scientist":"🧑‍🔬",
    "🧝 Elf":"🧝","🦸 Superhero":"🦸","🧙 Wizard":"🧙",
    "👦 Boy":"👦","👧 Girl":"👧","👨 Dad":"👨","👩 Mom":"👩",
    "👨‍🏫 Teacher":"👨‍🏫","🧑‍🎨 Artist":"🧑‍🎨"
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

# ── AI Mascot SVG Characters ──────────────────────────────────────
# USTAD: Friendly robot tutor with glowing cyan eyes
MASCOT_USTAD_SVG = """
<svg width="90" height="90" viewBox="0 0 90 90" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="ustadBodyGrad" cx="50%" cy="40%" r="55%">
      <stop offset="0%" stop-color="#1A3A6A"/>
      <stop offset="100%" stop-color="#0A1628"/>
    </radialGradient>
    <filter id="ustadGlow"><feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  <line x1="45" y1="8" x2="45" y2="18" stroke="#00FFD1" stroke-width="2"/>
  <circle cx="45" cy="6" r="3" fill="#00FFD1" filter="url(#ustadGlow)"/>
  <rect x="20" y="18" width="50" height="40" rx="12" fill="url(#ustadBodyGrad)" stroke="#00FFD1" stroke-width="1.5"/>
  <ellipse cx="33" cy="34" rx="7" ry="7" fill="#000D1A"/>
  <ellipse cx="57" cy="34" rx="7" ry="7" fill="#000D1A"/>
  <ellipse cx="33" cy="34" rx="4.5" ry="4.5" fill="#00FFD1" filter="url(#ustadGlow)"/>
  <ellipse cx="57" cy="34" rx="4.5" ry="4.5" fill="#00FFD1" filter="url(#ustadGlow)"/>
  <circle cx="34" cy="33" r="1.5" fill="white"/>
  <circle cx="58" cy="33" r="1.5" fill="white"/>
  <rect x="30" y="46" width="30" height="6" rx="3" fill="#000D1A"/>
  <rect x="32" y="47" width="6" height="4" rx="2" fill="#00FFD1" opacity="0.8"/>
  <rect x="40" y="47" width="6" height="4" rx="2" fill="#00FFD1" opacity="0.6"/>
  <rect x="48" y="47" width="6" height="4" rx="2" fill="#00FFD1" opacity="0.4"/>
  <rect x="25" y="60" width="40" height="22" rx="8" fill="url(#ustadBodyGrad)" stroke="#00FFD1" stroke-width="1"/>
  <rect x="33" y="64" width="24" height="12" rx="4" fill="#000D1A"/>
  <circle cx="40" cy="70" r="3" fill="#8B5CF6" filter="url(#ustadGlow)"/>
  <circle cx="50" cy="70" r="3" fill="#00FFD1" filter="url(#ustadGlow)"/>
  <rect x="18" y="16" width="54" height="5" rx="2" fill="#8B5CF6"/>
  <rect x="40" y="11" width="10" height="6" rx="1" fill="#8B5CF6"/>
  <line x1="60" y1="18" x2="65" y2="25" stroke="#FFD700" stroke-width="2"/>
  <circle cx="66" cy="26" r="2" fill="#FFD700"/>
</svg>
"""

# ZARA: Anime-style girl mascot (for younger grades)
MASCOT_ZARA_SVG = """
<svg width="80" height="80" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="zaraSkinGrad" cx="50%" cy="40%" r="55%">
      <stop offset="0%" stop-color="#FFD9B0"/>
      <stop offset="100%" stop-color="#FFBE85"/>
    </radialGradient>
    <filter id="zaraGlow"><feGaussianBlur stdDeviation="1.5" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  <ellipse cx="40" cy="22" rx="20" ry="16" fill="#2D1B69"/>
  <ellipse cx="40" cy="32" rx="18" ry="16" fill="url(#zaraSkinGrad)"/>
  <ellipse cx="22" cy="30" rx="6" ry="12" fill="#2D1B69"/>
  <ellipse cx="58" cy="30" rx="6" ry="12" fill="#2D1B69"/>
  <polygon points="40,8 42,14 48,14 43,18 45,24 40,20 35,24 37,18 32,14 38,14" fill="#FFD700" filter="url(#zaraGlow)"/>
  <ellipse cx="32" cy="32" rx="6" ry="7" fill="#1A0A4A"/>
  <ellipse cx="48" cy="32" rx="6" ry="7" fill="#1A0A4A"/>
  <ellipse cx="32" cy="32" rx="4" ry="5" fill="#8B5CF6"/>
  <ellipse cx="48" cy="32" rx="4" ry="5" fill="#8B5CF6"/>
  <ellipse cx="32" cy="32" rx="2" ry="3" fill="#000"/>
  <ellipse cx="48" cy="32" rx="2" ry="3" fill="#000"/>
  <circle cx="34" cy="30" r="1.5" fill="white"/>
  <circle cx="50" cy="30" r="1.5" fill="white"/>
  <ellipse cx="25" cy="37" rx="5" ry="3" fill="#FF9BB0" opacity="0.4"/>
  <ellipse cx="55" cy="37" rx="5" ry="3" fill="#FF9BB0" opacity="0.4"/>
  <path d="M34 40 Q40 45 46 40" stroke="#CC6B7A" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  <rect x="24" y="50" width="32" height="25" rx="8" fill="#2D1B69"/>
  <path d="M32 50 L40 58 L48 50" fill="#8B5CF6"/>
  <circle cx="35" cy="62" r="2" fill="#FFD700" filter="url(#zaraGlow)"/>
  <circle cx="45" cy="62" r="2" fill="#00FFD1" filter="url(#zaraGlow)"/>
</svg>
"""

# NOVA: Space explorer/astronaut (cool for older students)
MASCOT_NOVA_SVG = """
<svg width="80" height="80" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <radialGradient id="novaHelmetGrad" cx="50%" cy="35%" r="60%">
      <stop offset="0%" stop-color="#1E3A5F"/>
      <stop offset="100%" stop-color="#0A1628"/>
    </radialGradient>
    <filter id="novaGlow"><feGaussianBlur stdDeviation="2" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>
  <circle cx="40" cy="28" r="22" fill="url(#novaHelmetGrad)" stroke="#60A5FA" stroke-width="1.5"/>
  <ellipse cx="40" cy="28" rx="14" ry="12" fill="#000D2A"/>
  <ellipse cx="40" cy="28" rx="14" ry="12" fill="none" stroke="#60A5FA" stroke-width="1" opacity="0.5"/>
  <ellipse cx="36" cy="26" rx="3" ry="3.5" fill="#00FFD1" filter="url(#novaGlow)"/>
  <ellipse cx="44" cy="26" rx="3" ry="3.5" fill="#00FFD1" filter="url(#novaGlow)"/>
  <path d="M35 33 Q40 37 45 33" stroke="#60A5FA" stroke-width="1.5" fill="none" stroke-linecap="round"/>
  <path d="M28 20 Q35 16 42 18" stroke="white" stroke-width="1" fill="none" opacity="0.3"/>
  <rect x="22" y="48" width="36" height="26" rx="10" fill="#0E2A4A" stroke="#60A5FA" stroke-width="1"/>
  <rect x="30" y="53" width="20" height="12" rx="4" fill="#000D1A"/>
  <circle cx="37" cy="59" r="2.5" fill="#FF2D78" filter="url(#novaGlow)"/>
  <circle cx="43" cy="59" r="2.5" fill="#00FFD1" filter="url(#novaGlow)"/>
  <circle cx="24" cy="52" r="3" fill="#FFD700" filter="url(#novaGlow)"/>
  <circle cx="56" cy="52" r="3" fill="#FFD700" filter="url(#novaGlow)"/>
  <rect x="28" y="55" width="8" height="5" rx="1" fill="#01411C"/>
  <circle cx="31" cy="57" r="1.5" fill="white" opacity="0.8"/>
</svg>
"""


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
    study_dates = s.get("study_dates", [])
    if today not in study_dates:
        study_dates.append(today)
        study_dates = study_dates[-60:]
    s["study_dates"] = study_dates
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
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

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
# CSS — ZM Academy FUTURISTIC AI THEME 🤖🌌
# Neon Cosmos Dark + Holographic UI + AI Mascot Characters
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;800;900&family=Exo+2:ital,wght@0,300;0,400;0,600;0,700;0,800;1,400&family=Rajdhani:wght@400;500;600;700&display=swap');
/* ── FONT FACES LOADED ABOVE ─────────────────────────────────── */


html,body,[class*="css"]{
  font-family:'Exo 2',sans-serif !important;
  background:#03040A !important; color:#E0F4FF !important;
}
.main .block-container{
  padding-top:1rem !important; padding-bottom:4rem !important;
  max-width:980px !important;
  padding-left:1.4rem !important; padding-right:1.4rem !important;
  background:transparent !important;
}
#MainMenu,footer,header{visibility:hidden;}
.main::before{
  content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
  background:
    radial-gradient(ellipse at 20% 50%,rgba(139,92,246,0.07) 0%,transparent 50%),
    radial-gradient(ellipse at 80% 20%,rgba(0,255,209,0.05) 0%,transparent 40%),
    radial-gradient(ellipse at 60% 80%,rgba(255,45,120,0.04) 0%,transparent 35%),
    url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Ccircle cx='50' cy='80' r='1' fill='white' opacity='0.5'/%3E%3Ccircle cx='150' cy='30' r='0.5' fill='white' opacity='0.7'/%3E%3Ccircle cx='250' cy='120' r='1' fill='%2300FFD1' opacity='0.35'/%3E%3Ccircle cx='80' cy='200' r='1' fill='%238B5CF6' opacity='0.4'/%3E%3Ccircle cx='220' cy='260' r='0.8' fill='white' opacity='0.5'/%3E%3Ccircle cx='180' cy='150' r='1.2' fill='%2300FFD1' opacity='0.25'/%3E%3Ccircle cx='290' cy='80' r='0.7' fill='%23FFD700' opacity='0.35'/%3E%3C/svg%3E");
}
@keyframes scan{0%{transform:translateY(-100vh)}100%{transform:translateY(100vh)}}
.main::after{
  content:'';position:fixed;left:0;right:0;height:2px;pointer-events:none;z-index:1;
  background:linear-gradient(90deg,transparent,rgba(0,255,209,0.25),transparent);
  animation:scan 10s linear infinite;
}
@media(max-width:768px){
  .main .block-container{padding-left:.6rem !important;padding-right:.6rem !important;}
  .stButton>button{min-height:48px !important;font-size:13px !important;}
  div[data-testid="column"]{padding:2px !important;}
  .stTextInput>div>div>input{font-size:16px !important;padding:12px !important;}
}
@keyframes borderGlow{
  0%,100%{box-shadow:0 0 8px rgba(0,255,209,0.25),inset 0 0 8px rgba(0,255,209,0.04)}
  50%{box-shadow:0 0 18px rgba(0,255,209,0.45),inset 0 0 14px rgba(0,255,209,0.07)}
}
.stButton>button{
  background:linear-gradient(135deg,rgba(10,22,40,0.9),rgba(13,30,54,0.95)) !important;
  border:1px solid rgba(0,255,209,0.25) !important;
  color:#00FFD1 !important;
  font-family:'Rajdhani',sans-serif !important;
  font-weight:700 !important; font-size:13.5px !important; letter-spacing:.6px !important;
  border-radius:12px !important; padding:10px 20px !important;
  transition:all .25s cubic-bezier(.4,0,.2,1) !important;
  box-shadow:0 0 10px rgba(0,255,209,0.1) !important;
  text-transform:uppercase !important; overflow:hidden !important;
}
.stButton>button:hover{
  border-color:#00FFD1 !important; color:#ffffff !important;
  box-shadow:0 0 20px rgba(0,255,209,0.4),0 0 40px rgba(0,255,209,0.15) !important;
  transform:translateY(-2px) scale(1.02) !important;
  background:linear-gradient(135deg,rgba(0,255,209,0.1),rgba(10,22,40,0.95)) !important;
}
.stButton>button[kind="primary"]{
  background:linear-gradient(135deg,rgba(0,255,209,0.12) 0%,rgba(0,180,165,0.16) 100%) !important;
  border:1px solid #00FFD1 !important; color:#00FFD1 !important;
  box-shadow:0 0 20px rgba(0,255,209,0.4),inset 0 0 20px rgba(0,255,209,0.04) !important;
  font-weight:800 !important;
  animation:borderGlow 3s ease-in-out infinite !important;
}
.stButton>button[kind="primary"]:hover{
  background:linear-gradient(135deg,rgba(0,255,209,0.22),rgba(0,200,180,0.25)) !important;
  color:#fff !important;
  box-shadow:0 0 30px rgba(0,255,209,0.6),0 0 60px rgba(0,255,209,0.2) !important;
  transform:translateY(-3px) scale(1.03) !important;
}
[data-testid="stSidebar"]{
  background:linear-gradient(180deg,#020510 0%,#04091A 40%,#060B20 100%) !important;
  border-right:1px solid rgba(0,255,209,0.1) !important;
}
[data-testid="stSidebar"] *{color:#E0F4FF !important;}
[data-testid="stSidebar"] p,[data-testid="stSidebar"] span,
[data-testid="stSidebar"] div,[data-testid="stSidebar"] label,
[data-testid="stSidebar"] small{color:#E0F4FF !important;}
[data-testid="stSidebar"] .stButton>button{
  background:rgba(0,255,209,0.03) !important;
  border:1px solid rgba(0,255,209,0.08) !important;
  color:#94B4CC !important; font-weight:600 !important;
  font-size:13px !important; text-align:left !important;
  padding:10px 14px !important; border-radius:10px !important;
  margin-bottom:3px !important; width:100% !important;
  text-transform:none !important; letter-spacing:0 !important;
  animation:none !important; box-shadow:none !important;
}
[data-testid="stSidebar"] .stButton>button:hover{
  background:rgba(0,255,209,0.07) !important;
  border-color:rgba(0,255,209,0.3) !important;
  color:#00FFD1 !important;
  transform:translateX(4px) !important;
  box-shadow:3px 0 14px rgba(0,255,209,0.12) !important;
}
[data-testid="stSidebar"] .stButton>button[kind="primary"]{
  background:linear-gradient(135deg,rgba(0,255,209,0.1),rgba(0,180,165,0.07)) !important;
  border:1px solid rgba(0,255,209,0.35) !important;
  color:#00FFD1 !important; font-weight:800 !important;
  box-shadow:0 0 12px rgba(0,255,209,0.18) !important;
  animation:borderGlow 3s ease-in-out infinite !important;
}
@keyframes cardPulse{0%,100%{border-color:rgba(0,255,209,0.12)}50%{border-color:rgba(0,255,209,0.25)}}
.stat-card{
  background:linear-gradient(135deg,rgba(10,22,40,0.96),rgba(6,11,24,0.99));
  border-radius:18px;padding:18px 14px;text-align:center;
  box-shadow:0 8px 32px rgba(0,0,0,0.6);border:1px solid rgba(0,255,209,0.15);
  transition:all .3s cubic-bezier(.4,0,.2,1);position:relative;overflow:hidden;
  animation:cardPulse 4s ease-in-out infinite;
}
.stat-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,#00FFD1,transparent);}
.stat-card:hover{box-shadow:0 0 20px rgba(0,255,209,0.4),0 8px 32px rgba(0,0,0,0.6);transform:translateY(-4px);border-color:rgba(0,255,209,0.4);}
.stat-num{font-size:30px;font-weight:900;color:#00FFD1;font-family:'Orbitron',monospace;text-shadow:0 0 20px rgba(0,255,209,0.4);}
.stat-lbl{font-size:10px;color:#4A6A80;margin-top:4px;font-weight:700;text-transform:uppercase;letter-spacing:1.5px;font-family:'Rajdhani',sans-serif;}
.feature-card{
  background:linear-gradient(135deg,rgba(10,22,40,0.96),rgba(6,11,24,0.99));
  border-radius:18px;padding:18px 20px;border-left:3px solid #00FFD1;
  box-shadow:0 8px 32px rgba(0,0,0,0.6);margin-bottom:10px;color:#E0F4FF;transition:all .25s ease;
}
.feature-card:hover{box-shadow:0 0 20px rgba(0,255,209,0.4),0 8px 32px rgba(0,0,0,0.6);transform:translateY(-2px) translateX(2px);}
.hist-card{
  background:linear-gradient(135deg,rgba(10,22,40,0.9),rgba(6,11,24,0.96));
  border-radius:18px;padding:14px 16px;box-shadow:0 8px 32px rgba(0,0,0,0.6);
  border:1px solid rgba(0,255,209,0.15);margin-bottom:10px;
}
.section-header{
  background:linear-gradient(135deg,rgba(0,255,209,0.07) 0%,rgba(10,22,40,0.97) 40%,rgba(0,100,80,0.05) 100%);
  color:#00FFD1;border-radius:18px;padding:16px 22px;margin-bottom:20px;
  font-family:'Orbitron',monospace;font-size:17px;font-weight:800;
  border:1px solid rgba(0,255,209,0.25);
  box-shadow:0 0 20px rgba(0,255,209,0.4),inset 0 0 40px rgba(0,255,209,0.02);
  letter-spacing:1.5px;position:relative;overflow:hidden;text-transform:uppercase;
}
.section-header::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,#00FFD1,transparent);}
.section-header::after{content:'';position:absolute;bottom:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(0,255,209,0.3),transparent);}
.section-header.orange{background:linear-gradient(135deg,rgba(255,45,120,0.07),rgba(10,22,40,0.97));color:#FF2D78;border-color:rgba(255,45,120,0.25);box-shadow:0 0 20px rgba(255,45,120,0.4);}
.section-header.orange::before{background:linear-gradient(90deg,transparent,#FF2D78,transparent);}
.section-header.gold{background:linear-gradient(135deg,rgba(255,215,0,0.07),rgba(10,22,40,0.97));color:#FFD700;border-color:rgba(255,215,0,0.25);box-shadow:0 0 20px rgba(255,215,0,0.25);}
.section-header.blue{background:linear-gradient(135deg,rgba(59,130,246,0.07),rgba(10,22,40,0.97));color:#60A5FA;border-color:rgba(59,130,246,0.25);box-shadow:0 0 20px rgba(59,130,246,0.25);}
.section-header.blue::before{background:linear-gradient(90deg,transparent,#60A5FA,transparent);}
.section-header.purple{background:linear-gradient(135deg,rgba(139,92,246,0.07),rgba(10,22,40,0.97));color:#A78BFA;border-color:rgba(139,92,246,0.25);box-shadow:0 0 20px rgba(139,92,246,0.4);}
.section-header.purple::before{background:linear-gradient(90deg,transparent,#A78BFA,transparent);}
.msg-user{
  background:linear-gradient(135deg,rgba(0,255,209,0.1),rgba(0,180,165,0.07));
  color:#E0F4FF;border-radius:18px 18px 4px 18px;padding:13px 18px;
  margin:5px 0 5px 50px;font-size:14px;line-height:1.7;
  border:1px solid rgba(0,255,209,0.2);box-shadow:0 0 15px rgba(0,255,209,0.08);
}
.msg-bot{
  background:linear-gradient(135deg,rgba(10,22,40,0.96),rgba(6,11,24,0.99));
  color:#E0F4FF;border-radius:18px 18px 18px 4px;padding:13px 18px;
  margin:5px 50px 5px 0;font-size:14px;line-height:1.75;
  box-shadow:0 8px 32px rgba(0,0,0,0.6);border:1px solid rgba(139,92,246,0.18);
}
.msg-lbl{font-size:10px;color:#4A6A80;margin-bottom:3px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;font-family:'Rajdhani',sans-serif;}
.msg-lbl-r{text-align:right;}
@keyframes energyFlow{0%{background-position:0 0}100%{background-position:40px 0}}
.prog-bar{background:rgba(0,255,209,0.04);border-radius:99px;height:10px;overflow:hidden;margin-bottom:4px;border:1px solid rgba(0,255,209,0.07);}
.prog-fill{height:100%;border-radius:99px;background:linear-gradient(90deg,#00FFD1,#A78BFA,#00FFD1);background-size:40px 100%;animation:energyFlow 2s linear infinite;box-shadow:0 0 8px rgba(0,255,209,0.4);}
.badge-card{
  background:linear-gradient(135deg,rgba(10,22,40,0.96),rgba(6,11,24,0.99));
  border:1px solid rgba(255,215,0,0.2);border-radius:18px;
  padding:14px 10px;text-align:center;
  box-shadow:0 0 15px rgba(255,215,0,0.08),0 8px 32px rgba(0,0,0,0.6);transition:all .3s ease;
}
.badge-card:hover{transform:translateY(-4px) scale(1.02);box-shadow:0 0 25px rgba(255,215,0,0.28),0 8px 32px rgba(0,0,0,0.6);border-color:rgba(255,215,0,0.45);}
.badge-locked{opacity:0.18;filter:grayscale(1);}
.badge-icon{font-size:30px;display:block;}
.badge-name{font-size:10.5px;font-weight:800;color:#FFD700;margin-top:6px;font-family:'Orbitron',monospace;letter-spacing:.5px;}
.badge-desc{font-size:10px;color:#4A6A80;margin-top:3px;}
.word-card{
  background:linear-gradient(135deg,#020510 0%,#04091A 50%,#060B20 100%);
  border-radius:18px;padding:20px 22px;margin-bottom:16px;
  color:#E0F4FF;border:1px solid rgba(0,255,209,0.18);
  box-shadow:0 0 20px rgba(0,255,209,0.4),0 8px 32px rgba(0,0,0,0.6);position:relative;overflow:hidden;
}
.word-card::before{content:'';position:absolute;top:-30px;right:-30px;width:120px;height:120px;border-radius:50%;background:radial-gradient(circle,rgba(0,255,209,0.12),transparent 70%);}
.reminder{
  background:linear-gradient(135deg,rgba(255,215,0,0.05),rgba(10,22,40,0.96));
  border:1px solid rgba(255,215,0,0.2);border-radius:18px;
  padding:13px 18px;margin-bottom:16px;font-size:13px;color:#E0F4FF;
  box-shadow:0 0 15px rgba(255,215,0,0.07);
}
.lb-row{
  display:flex;align-items:center;gap:12px;padding:13px 18px;
  background:linear-gradient(135deg,rgba(10,22,40,0.96),rgba(6,11,24,0.99));
  border-radius:14px;margin-bottom:8px;
  box-shadow:0 8px 32px rgba(0,0,0,0.6);border:1px solid rgba(0,255,209,0.15);color:#E0F4FF;transition:all .2s ease;
}
.lb-row:hover{box-shadow:0 0 20px rgba(0,255,209,0.4),0 8px 32px rgba(0,0,0,0.6);transform:translateX(4px);border-color:rgba(0,255,209,0.28);}
.lb-rank{font-size:22px;font-weight:900;width:32px;text-align:center;}
.lb-name{flex:1;font-weight:700;font-size:14px;}
.lb-score{font-weight:900;font-size:18px;color:#00FFD1;font-family:'Orbitron',monospace;text-shadow:0 0 20px rgba(0,255,209,0.4);}
.syl-step{background:linear-gradient(135deg,rgba(0,255,209,0.03),rgba(10,22,40,0.96));border-radius:18px;padding:14px 18px;margin-bottom:14px;border:1px solid rgba(0,255,209,0.1);color:#E0F4FF;}
.syl-step-title{font-size:10px;font-weight:800;color:#00FFD1;text-transform:uppercase;letter-spacing:2px;margin-bottom:8px;font-family:'Orbitron',monospace;}
.topic-chip{display:inline-block;border-radius:6px;padding:3px 10px;font-size:11px;font-weight:700;margin:3px 3px 3px 0;}
[data-testid="stSelectbox"]>div>div{background:rgba(10,22,40,0.96) !important;border:1px solid rgba(0,255,209,0.22) !important;border-radius:12px !important;color:#E0F4FF !important;box-shadow:0 0 10px rgba(0,255,209,0.04) !important;}
[data-testid="stSelectbox"]>div>div>div{color:#E0F4FF !important;font-weight:600 !important;}
[data-testid="stSelectbox"] svg{color:#00FFD1 !important;fill:#00FFD1 !important;}
[data-baseweb="popover"],[data-baseweb="menu"],[role="listbox"]{background:rgba(6,11,24,0.99) !important;border:1px solid rgba(0,255,209,0.18) !important;border-radius:14px !important;box-shadow:0 0 20px rgba(0,255,209,0.4),0 20px 60px rgba(0,0,0,0.85) !important;}
[role="option"]{color:#E0F4FF !important;background:transparent !important;font-size:14px !important;padding:10px 14px !important;}
[role="option"]:hover,[role="option"][aria-selected="true"]{background:rgba(0,255,209,0.07) !important;color:#00FFD1 !important;font-weight:700 !important;}
.stTextInput>div>div>input,.stTextArea>div>div>textarea{
  border-radius:12px !important;border:1px solid rgba(0,255,209,0.18) !important;
  color:#E0F4FF !important;background:rgba(10,22,40,0.96) !important;
  font-family:'Exo 2',sans-serif !important;box-shadow:0 0 10px rgba(0,255,209,0.04) !important;
}
.stTextInput>div>div>input:focus,.stTextArea>div>div>textarea:focus{border-color:#00FFD1 !important;box-shadow:0 0 20px rgba(0,255,209,0.4) !important;}
.stTextInput>div>div>input::placeholder,.stTextArea>div>div>textarea::placeholder{color:#4A6A80 !important;}
[data-testid="stNumberInput"] input{color:#E0F4FF !important;background:rgba(10,22,40,0.96) !important;border:1px solid rgba(0,255,209,0.18) !important;border-radius:12px !important;}
[data-testid="stNumberInput"] button{background:rgba(0,255,209,0.06) !important;border-color:rgba(0,255,209,0.18) !important;color:#00FFD1 !important;}
[data-testid="stSlider"] [role="slider"]{background:#00FFD1 !important;border:2px solid #00FFD1 !important;box-shadow:0 0 10px rgba(0,255,209,0.6) !important;}
[data-testid="stSlider"] [data-testid="stThumbValue"]{background:#00FFD1 !important;color:#03040A !important;font-weight:800 !important;border-radius:6px !important;font-family:'Orbitron',monospace !important;}
[data-testid="stSlider"] > div > div > div > div{background:linear-gradient(90deg,#00FFD1,#8B5CF6) !important;}
[data-testid="stSlider"] > div > div > div{background:rgba(0,255,209,0.1) !important;}
[data-testid="stSlider"] p{color:#00FFD1 !important;font-weight:700 !important;font-family:'Orbitron',monospace !important;}
label,[data-testid="stLabel"]>label{color:#00FFD1 !important;font-weight:700 !important;font-size:11.5px !important;letter-spacing:1.2px !important;text-transform:uppercase !important;font-family:'Rajdhani',sans-serif !important;}
[data-testid="stSidebar"] label{color:#E0F4FF !important;}
.stRadio label,[data-testid="stRadio"] label{color:#E0F4FF !important;font-weight:600 !important;}
.stRadio [role="radio"]{border-color:rgba(0,255,209,0.4) !important;}
.stRadio [aria-checked="true"] [role="radio"]{background:#00FFD1 !important;border-color:#00FFD1 !important;}
.stCheckbox label{color:#E0F4FF !important;font-weight:600 !important;}
[data-testid="stCheckbox"] p{color:#E0F4FF !important;}
[data-testid="stCheckbox"] [aria-checked="true"]{background:#00FFD1 !important;border-color:#00FFD1 !important;}
[data-testid="stMultiSelect"]>div>div{background:rgba(10,22,40,0.96) !important;border:1px solid rgba(0,255,209,0.22) !important;border-radius:12px !important;color:#E0F4FF !important;}
[data-testid="stMultiSelect"] span{color:#E0F4FF !important;}
[data-baseweb="tag"]{background:rgba(0,255,209,0.12) !important;color:#00FFD1 !important;border:1px solid rgba(0,255,209,0.3) !important;}
[data-baseweb="tag"] span{color:#00FFD1 !important;}
.stTabs [data-baseweb="tab-list"]{background:rgba(10,22,40,0.8) !important;border-radius:12px !important;padding:4px !important;border:1px solid rgba(0,255,209,0.1) !important;gap:4px !important;}
.stTabs [data-baseweb="tab"]{background:transparent !important;color:#4A6A80 !important;font-weight:700 !important;font-size:12.5px !important;border-radius:8px !important;padding:8px 16px !important;border:none !important;letter-spacing:.8px !important;text-transform:uppercase !important;font-family:'Rajdhani',sans-serif !important;}
.stTabs [aria-selected="true"]{background:linear-gradient(135deg,rgba(0,255,209,0.1),rgba(0,180,165,0.07)) !important;color:#00FFD1 !important;box-shadow:0 0 20px rgba(0,255,209,0.4) !important;border:1px solid rgba(0,255,209,0.28) !important;}
[data-testid="stExpander"]{background:rgba(10,22,40,0.8) !important;border:1px solid rgba(0,255,209,0.1) !important;border-radius:12px !important;margin-bottom:6px !important;}
[data-testid="stExpander"] summary{font-weight:700 !important;color:#E0F4FF !important;}
[data-testid="stExpander"] summary p{color:#E0F4FF !important;}
[data-testid="stExpander"] summary svg{color:#00FFD1 !important;fill:#00FFD1 !important;}
[data-testid="stMetricValue"]{color:#00FFD1 !important;font-family:'Orbitron',monospace !important;font-weight:900 !important;text-shadow:0 0 20px rgba(0,255,209,0.4) !important;}
[data-testid="stMetricLabel"]{color:#94B4CC !important;font-weight:700 !important;}
[data-testid="stMetricDelta"]{color:#34D399 !important;}
[data-testid="stAlert"]{background:rgba(10,22,40,0.9) !important;border-radius:12px !important;border-left-width:3px !important;color:#E0F4FF !important;}
[data-testid="stAlert"] p{color:#E0F4FF !important;}
[data-testid="stSpinner"] p{color:#00FFD1 !important;}
::-webkit-scrollbar{width:4px;height:4px;}
::-webkit-scrollbar-track{background:#03040A;}
::-webkit-scrollbar-thumb{background:rgba(0,255,209,0.25);border-radius:99px;}
::-webkit-scrollbar-thumb:hover{background:rgba(0,255,209,0.5);}
@keyframes float{0%,100%{transform:translateY(0) rotate(-1deg)}50%{transform:translateY(-8px) rotate(1deg)}}
@keyframes glowPulse{0%,100%{filter:drop-shadow(0 0 6px rgba(0,255,209,0.5))}50%{filter:drop-shadow(0 0 16px rgba(0,255,209,0.9))}}
.mascot-float{animation:float 4s ease-in-out infinite,glowPulse 3s ease-in-out infinite;display:inline-block;cursor:pointer;}
[data-testid="stForm"] *{color:#E0F4FF;}
[data-testid="stForm"] label{color:#00FFD1 !important;}
[data-testid="stForm"] input{color:#E0F4FF !important;background:rgba(10,22,40,0.96) !important;}
p,div,span,h1,h2,h3,h4,h5,h6,li{color:#E0F4FF;}
strong,b{color:#ffffff;}

</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# AUTH PAGE — Futuristic Login Terminal
# ─────────────────────────────────────────────────────────────────
def page_auth():
    st.markdown("""
    <style>
    .main .block-container{max-width:500px !important;padding-top:1.5rem !important;}
    [data-testid="stForm"]{background:rgba(10,22,40,0.95) !important;border-radius:20px !important;padding:24px !important;border:1px solid rgba(0,255,209,0.2) !important;box-shadow:0 0 40px rgba(0,255,209,0.08),0 20px 60px rgba(0,0,0,0.6) !important;}
    </style>""", unsafe_allow_html=True)

    # Hero with mascot
    st.markdown(f"""
    <div style='text-align:center;padding:24px 0 20px'>
        <div style='display:flex;justify-content:center;align-items:flex-end;gap:16px;margin-bottom:16px'>
            <div class='mascot-float'>{MASCOT_ZARA_SVG}</div>
            <div style='display:inline-flex;align-items:center;justify-content:center;
                width:80px;height:80px;border-radius:22px;
                background:linear-gradient(135deg,rgba(0,255,209,0.1),rgba(10,22,40,0.9));
                box-shadow:0 0 30px rgba(0,255,209,0.3),0 0 60px rgba(0,255,209,0.1);
                border:1px solid rgba(0,255,209,0.3)'>
                <span style='font-size:42px;line-height:1'>🤖</span>
            </div>
            <div class='mascot-float' style='animation-delay:.8s'>{MASCOT_NOVA_SVG}</div>
        </div>
        <h1 style='font-family:"Orbitron",monospace;font-size:28px;font-weight:900;
            color:#00FFD1;margin:0 0 4px;letter-spacing:2px;
            text-shadow:0 0 20px rgba(0,255,209,0.6)'>ZM ACADEMY</h1>
        <p style='color:#94B4CC;font-size:12px;font-weight:600;margin:0;letter-spacing:2px;text-transform:uppercase;font-family:"Rajdhani",sans-serif'>
            🇵🇰 Pakistan's AI-Powered Education System
        </p>
        <div style='display:flex;justify-content:center;gap:8px;margin-top:12px;flex-wrap:wrap'>
            <span style='background:rgba(0,255,209,0.08);color:#00FFD1;padding:3px 12px;
                border-radius:6px;font-size:10px;font-weight:700;border:1px solid rgba(0,255,209,0.2);
                font-family:"Rajdhani",sans-serif;letter-spacing:1px'>GRADES 1–10</span>
            <span style='background:rgba(0,255,209,0.08);color:#00FFD1;padding:3px 12px;
                border-radius:6px;font-size:10px;font-weight:700;border:1px solid rgba(0,255,209,0.2);
                font-family:"Rajdhani",sans-serif;letter-spacing:1px'>O LEVEL</span>
            <span style='background:rgba(0,255,209,0.08);color:#00FFD1;padding:3px 12px;
                border-radius:6px;font-size:10px;font-weight:700;border:1px solid rgba(0,255,209,0.2);
                font-family:"Rajdhani",sans-serif;letter-spacing:1px'>A LEVEL</span>
            <span style='background:rgba(139,92,246,0.12);color:#A78BFA;padding:3px 12px;
                border-radius:6px;font-size:10px;font-weight:700;border:1px solid rgba(139,92,246,0.25);
                font-family:"Rajdhani",sans-serif;letter-spacing:1px'>🤖 AI POWERED</span>
        </div>
    </div>""", unsafe_allow_html=True)

    tab_login, tab_signup, tab_forgot = st.tabs(["🔑  LOGIN","✨  SIGN UP","🔓  RESET"])

    with tab_login:
        with st.form("login_form"):
            email    = st.text_input("📧 Email", placeholder="you@example.com")
            password = st.text_input("🔒 Password", type="password")
            if st.form_submit_button("⚡ LOGIN TO ZM ACADEMY", use_container_width=True, type="primary"):
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
            avatar = st.selectbox("🎮 Choose Avatar", list(AVATARS.keys()))
            grade  = st.selectbox("🏫 Grade", ["-- Select --"]+LEVELS)
            pw     = st.text_input("🔒 Password", type="password", placeholder="Min 6 characters")
            pw2    = st.text_input("🔒 Confirm Password", type="password")
            if st.form_submit_button("🚀 CREATE ACCOUNT", use_container_width=True, type="primary"):
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
        <div style='background:rgba(0,255,209,0.04);border-radius:10px;padding:12px 14px;
            font-size:13px;color:#00FFD1;margin-bottom:14px;border:1px solid rgba(0,255,209,0.15)'>
            🔒 Enter your email and a new password to reset your account.
        </div>""", unsafe_allow_html=True)
        with st.form("forgot_form"):
            fp_email = st.text_input("📧 Your registered email")
            fp_new   = st.text_input("🔒 New Password", type="password")
            fp_new2  = st.text_input("🔒 Confirm New Password", type="password")
            if st.form_submit_button("🔓 RESET PASSWORD", use_container_width=True, type="primary"):
                users = load_json(USERS_FILE)
                if fp_email not in users:    st.error("⚠️ Email not found.")
                elif len(fp_new) < 6:        st.error("Min 6 characters.")
                elif fp_new != fp_new2:      st.error("Passwords don't match.")
                else:
                    users[fp_email]["password"] = hash_pw(fp_new)
                    save_json(USERS_FILE, users)
                    st.success("✅ Password reset! You can now login.")

    st.markdown("""
    <p style='text-align:center;color:#4A6A80;font-size:10px;margin-top:20px;font-weight:700;
        font-family:"Rajdhani",sans-serif;letter-spacing:1.5px'>
        🔒 SECURE &nbsp;·&nbsp; 🆓 FREE &nbsp;·&nbsp; 🇵🇰 PAKISTAN CURRICULUM
    </p>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# SIDEBAR — Holographic Command Center
# ─────────────────────────────────────────────────────────────────
def render_sidebar():
    u = st.session_state.user
    role_info = {
        "student": ("🎒", "Student",  "#00FFD1"),
        "parent":  ("👨‍👩‍👦","Parent",  "#34D399"),
        "teacher": ("👨‍🏫","Teacher", "#FFD700"),
        "admin":   ("🛡️", "Admin",    "#FF2D78"),
    }
    r_icon, r_label, r_color = role_info.get(u.get("role","student"), ("👤","User","#00FFD1"))
    role = u.get("role", "student")

    with st.sidebar:
        # App logo
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:10px;
            padding:14px 14px 12px;border-bottom:1px solid rgba(0,255,209,0.1)'>
            <div style='width:38px;height:38px;border-radius:11px;flex-shrink:0;
                background:linear-gradient(135deg,rgba(0,255,209,0.12),rgba(10,22,40,0.9));
                display:flex;align-items:center;justify-content:center;font-size:22px;
                border:1px solid rgba(0,255,209,0.3);
                box-shadow:0 0 16px rgba(0,255,209,0.25)'>🤖</div>
            <div>
                <div style='font-family:"Orbitron",monospace;font-weight:900;font-size:14px;
                    color:#00FFD1;letter-spacing:1.5px;
                    text-shadow:0 0 12px rgba(0,255,209,0.5)'>ZM ACADEMY</div>
                <div style='font-size:8.5px;color:rgba(0,255,209,0.45);font-weight:700;
                    letter-spacing:1.2px;text-transform:uppercase;font-family:"Rajdhani",sans-serif'>
                    🇵🇰 AI Education Platform</div>
            </div>
        </div>""", unsafe_allow_html=True)

        # Profile card with mascot
        stats = u.get("stats", {})
        mascot = MASCOT_USTAD_SVG if u.get("role","student") == "teacher" else (MASCOT_ZARA_SVG if u.get("avatar","🤖") in ["👧","🧝","🧙"] else MASCOT_NOVA_SVG)
        st.markdown(f"""
        <div style='padding:12px 10px 14px;border-bottom:1px solid rgba(0,255,209,0.1)'>
            <div style='display:flex;flex-direction:column;align-items:center'>
                <div style='display:flex;align-items:center;gap:8px;margin-bottom:8px'>
                    <div style='width:54px;height:54px;border-radius:16px;flex-shrink:0;
                        background:linear-gradient(135deg,rgba(0,255,209,0.1),rgba(10,22,40,0.9));
                        display:flex;align-items:center;justify-content:center;font-size:30px;
                        border:1px solid rgba(0,255,209,0.25);
                        box-shadow:0 0 16px rgba(0,255,209,0.15)'>{u.get("avatar","🤖")}</div>
                    <div style='flex:1'>
                        <div style='font-family:"Orbitron",monospace;font-weight:800;font-size:12px;
                            color:#E0F4FF;letter-spacing:.5px'>{u["name"]}</div>
                        <div style='display:inline-flex;align-items:center;gap:4px;margin-top:4px;
                            background:rgba(0,255,209,0.06);border-radius:6px;
                            padding:2px 8px;border:1px solid rgba(0,255,209,0.15)'>
                            <span style='font-size:10px'>{r_icon}</span>
                            <span style='font-size:10px;font-weight:700;color:{r_color};font-family:"Rajdhani",sans-serif;letter-spacing:.8px'>{r_label.upper()}</span>
                        </div>
                    </div>
                </div>
            </div>
            <div style='display:flex;justify-content:center;gap:0;
                background:rgba(0,0,0,0.3);border-radius:10px;
                border:1px solid rgba(0,255,209,0.08);overflow:hidden'>
                <div style='flex:1;text-align:center;padding:7px 4px;
                    border-right:1px solid rgba(0,255,209,0.07)'>
                    <div style='font-family:"Orbitron",monospace;font-size:15px;font-weight:900;
                        color:#00FFD1;text-shadow:0 0 8px rgba(0,255,209,0.5)'>{stats.get("total",0)}</div>
                    <div style='font-size:8px;color:rgba(0,255,209,0.3);
                        text-transform:uppercase;letter-spacing:1px;font-weight:700;font-family:"Rajdhani",sans-serif'>QS</div>
                </div>
                <div style='flex:1;text-align:center;padding:7px 4px;
                    border-right:1px solid rgba(0,255,209,0.07)'>
                    <div style='font-family:"Orbitron",monospace;font-size:15px;font-weight:900;
                        color:#FFD700;text-shadow:0 0 8px rgba(255,215,0,0.5)'>{len(u.get("badges",[]))}</div>
                    <div style='font-size:8px;color:rgba(255,215,0,0.3);
                        text-transform:uppercase;letter-spacing:1px;font-weight:700;font-family:"Rajdhani",sans-serif'>BDGS</div>
                </div>
                <div style='flex:1;text-align:center;padding:7px 4px'>
                    <div style='font-family:"Orbitron",monospace;font-size:15px;font-weight:900;
                        color:#FF2D78;text-shadow:0 0 8px rgba(255,45,120,0.5)'>{stats.get("streak",0)}</div>
                    <div style='font-size:8px;color:rgba(255,45,120,0.3);
                        text-transform:uppercase;letter-spacing:1px;font-weight:700;font-family:"Rajdhani",sans-serif'>STRK</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

        cur = st.session_state.page

        def nav_btn(icon, label, key, uid=""):
            btn_type = "primary" if cur == key else "secondary"
            if st.button(f"{icon}  {label}", key=f"nav_{key}{uid}",
                         use_container_width=True, type=btn_type):
                st.session_state.page = key; st.rerun()

        def section_label(text, color="rgba(0,255,209,0.5)"):
            st.markdown(
                f"<div style='font-size:9px;font-weight:800;color:{color};"
                f"text-transform:uppercase;letter-spacing:1.8px;"
                f"padding:14px 4px 4px;margin-top:2px;font-family:\"Rajdhani\",sans-serif;"
                f"border-top:1px solid rgba(0,255,209,0.06)'>{text}</div>",
                unsafe_allow_html=True
            )

        section_label("📊  Dashboard")
        nav_btn("🏠", "Home",            "home")
        nav_btn("📚", "Syllabus",        "syllabus")
        nav_btn("🎨", "Image Generator", "image")
        nav_btn("📈", "My Progress",     "progress")

        if role in ("student", "parent"):
            section_label("🎒  Student", "rgba(0,255,209,0.45)")
            nav_btn("💬", "Chat Tutor",    "chat",    "_s")
            nav_btn("📝", "Practice Quiz", "quiz")
            nav_btn("👥", "Friendz Quiz",  "friends")
            nav_btn("🕐", "Chat History",  "history", "_s")
            nav_btn("🏆", "Badges",        "badges")

        if role == "teacher":
            section_label("👨‍🏫  Teacher", "rgba(255,215,0,0.5)")
            nav_btn("📋", "Create Homework",     "homework", "_t")
            nav_btn("💬", "Chat Tutor",          "chat",     "_t")
            nav_btn("📊", "Student Performance", "admin",    "_t")
            nav_btn("🏆", "Badges",              "badges",   "_t")

        if role == "admin":
            section_label("🛡️  Admin", "rgba(255,45,120,0.5)")
            nav_btn("📊", "Student Performance", "admin",    "_a")
            nav_btn("🕐", "Chat History",        "history",  "_a")
            nav_btn("📋", "Homework Tracker",    "homework", "_a")
            nav_btn("💬", "Chat Tutor",          "chat",     "_a")

        section_label("👤  Account")
        nav_btn("👤", "Profile", "profile")

        st.markdown("""<div style='margin:16px 0 4px;border-top:1px solid rgba(0,255,209,0.06);padding-top:12px'></div>""", unsafe_allow_html=True)
        if st.button("🚪  Logout", key="logout_btn", use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()


# ─────────────────────────────────────────────────────────────────
# HOME PAGE — Futuristic Dashboard with Characters
# ─────────────────────────────────────────────────────────────────
def page_home():
    u     = st.session_state.user
    sub   = st.session_state.subject
    h     = datetime.datetime.now().hour
    greet = "GOOD MORNING" if h < 12 else "GOOD AFTERNOON" if h < 17 else "GOOD EVENING"
    role  = u.get("role", "student")
    stats = u.get("stats", {})

    # ── Onboarding for new users ──
    if u.get("is_new") and not st.session_state.get("onboarding_done"):
        step = st.session_state.get("onboard_step", 1)
        mascots = [MASCOT_ZARA_SVG, MASCOT_USTAD_SVG, MASCOT_NOVA_SVG]
        steps = [
            {"title":f"Welcome to ZM Academy, {u['name'].split()[0]}!",
             "body":"Pakistan's <b style='color:#00FFD1'>AI-powered study platform</b> for Grades 1–10, O Level & A Level.<br><br>Your AI tutor <b style='color:#A78BFA'>Ustad 🤖</b> is ready to help!","btn":"NEXT →"},
            {"title":"Your Learning Arsenal",
             "body":"<b style='color:#00FFD1'>💬 Chat Tutor</b> — Ask anything<br><br><b style='color:#A78BFA'>📝 Practice Quiz</b> — Custom difficulty quizzes<br><br><b style='color:#FFD700'>📚 My Syllabus</b> — Cambridge curriculum<br><br><b style='color:#FF2D78'>🎨 Image Gen</b> — AI draws diagrams","btn":"NEXT →"},
            {"title":"Earn Badges & Challenge Friends",
             "body":"Unlock <b style='color:#FFD700'>11 achievement badges</b> as you study.<br><br>Use <b style='color:#A78BFA'>👥 Friends Quiz</b> to compete with up to 3 friends on the same quiz!","btn":"🚀 START LEARNING!"},
        ]
        s = steps[step-1]
        _, c, _ = st.columns([1,2,1])
        with c:
            dots = "".join(
                f"<span style='display:inline-block;width:8px;height:8px;border-radius:50%;"
                f"background:{'#00FFD1' if i+1==step else 'rgba(0,255,209,0.15)'};margin:0 3px;"
                f"box-shadow:{'0 0 8px rgba(0,255,209,0.7)' if i+1==step else 'none'}'></span>"
                for i in range(3)
            )
            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#020510,#04091A,#060B20);
                border-radius:24px;padding:32px 28px;color:#E0F4FF;text-align:center;margin-top:20px;
                border:1px solid rgba(0,255,209,0.2);
                box-shadow:0 0 40px rgba(0,255,209,0.1),0 20px 60px rgba(0,0,0,0.7)'>
                <div style='margin-bottom:14px'>{dots}</div>
                <div class='mascot-float' style='display:flex;justify-content:center;margin-bottom:12px'>
                    {mascots[step-1]}
                </div>
                <div style='font-family:"Orbitron",monospace;font-size:20px;font-weight:900;
                    color:#00FFD1;margin-bottom:14px;letter-spacing:.5px;
                    text-shadow:0 0 16px rgba(0,255,209,0.5)'>{s['title']}</div>
                <div style='font-size:13px;opacity:.85;line-height:1.9'>{s['body']}</div>
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
            if step > 1 and st.button("← BACK", key=f"ob_back_{step}", use_container_width=True):
                st.session_state.onboard_step = step-1; st.rerun()
            if st.button("SKIP INTRO", key="skip_ob", use_container_width=True):
                users = load_json(USERS_FILE)
                if u["email"] in users:
                    users[u["email"]]["is_new"] = False
                    save_json(USERS_FILE, users)
                    st.session_state.user = users[u["email"]]
                st.session_state.onboarding_done = True; st.rerun()
        return

    # ── Hero Banner ──
    streak = stats.get("streak", 0)
    streak_fire = "🔥" * min(streak, 5) if streak > 0 else ""
    quotes = [
        ("علم حاصل کرنا ہر مسلمان پر فرض ہے", "Seeking knowledge is an obligation upon every Muslim"),
        ("محنت کا پھل میٹھا ہوتا ہے", "The fruit of hard work is always sweet"),
        ("آج کی محنت کل کی کامیابی ہے", "Today's effort is tomorrow's success"),
        ("ہر مشکل کے بعد آسانی ہے", "After every difficulty comes ease"),
        ("علم روشنی ہے", "Knowledge is light"),
    ]
    q_urdu, q_eng = quotes[datetime.date.today().toordinal() % len(quotes)]
    grade_num = u.get("grade","Grade 6")
    # Pick mascot by grade
    try:
        g_idx = get_level_index(grade_num)
        hero_mascot = MASCOT_ZARA_SVG if g_idx < 5 else (MASCOT_NOVA_SVG if g_idx >= 9 else MASCOT_USTAD_SVG)
    except:
        hero_mascot = MASCOT_USTAD_SVG

    st.markdown(f"""
    <div style='background:linear-gradient(135deg,#020510 0%,#04091A 50%,#060B20 100%);
        border-radius:20px;padding:20px 22px;margin-bottom:16px;color:#E0F4FF;
        border:1px solid rgba(0,255,209,0.18);
        box-shadow:0 0 30px rgba(0,255,209,0.08),0 12px 40px rgba(0,0,0,0.5);
        position:relative;overflow:hidden'>
        <div style='position:absolute;top:-20px;right:-20px;width:140px;height:140px;border-radius:50%;
            background:radial-gradient(circle,rgba(0,255,209,0.1),transparent 70%)'></div>
        <div style='position:absolute;bottom:-30px;left:20px;width:100px;height:100px;border-radius:50%;
            background:radial-gradient(circle,rgba(139,92,246,0.1),transparent 70%)'></div>
        <div style='display:flex;align-items:center;gap:14px;position:relative;margin-bottom:12px'>
            <div class='mascot-float' style='flex-shrink:0'>{hero_mascot}</div>
            <div style='flex:1'>
                <div style='font-family:"Rajdhani",sans-serif;font-size:10px;font-weight:700;
                    color:rgba(0,255,209,0.5);letter-spacing:2.5px;text-transform:uppercase;
                    margin-bottom:4px'>{greet}</div>
                <div style='font-family:"Orbitron",monospace;font-size:18px;font-weight:900;
                    letter-spacing:-.5px;line-height:1.2;color:#00FFD1;
                    text-shadow:0 0 16px rgba(0,255,209,0.4)'>
                    {u["name"].split()[0]}! {streak_fire or "👋"}</div>
                <div style='font-size:11px;color:#94B4CC;margin-top:4px;font-weight:500'>
                    🇵🇰 Pakistan's #1 AI Study Platform
                    {"&nbsp;&nbsp;<span style='color:#FF2D78;font-weight:800'>🔥 " + str(streak) + "-day streak!</span>" if streak > 1 else ""}
                </div>
            </div>
        </div>
        <div style='background:rgba(0,0,0,0.35);border-radius:10px;padding:10px 14px;
            border-left:2px solid rgba(0,255,209,0.4);position:relative'>
            <div style='font-size:13px;font-weight:700;color:#FFD700;margin-bottom:2px'>{q_urdu}</div>
            <div style='font-size:11px;color:#94B4CC;font-style:italic'>{q_eng}</div>
        </div>
    </div>""", unsafe_allow_html=True)

    today_str = datetime.date.today().isoformat()
    if stats.get("lastDate","") != today_str:
        st.markdown("""<div class='reminder'>⚡ <b style='color:#FFD700'>Daily Mission:</b> You haven't studied today! Even 15 minutes powers up your streak 💪</div>""", unsafe_allow_html=True)

    # ── 7-Day Streak Calendar ──
    study_dates = set(stats.get("study_dates", []))
    today = datetime.date.today()
    day_labels = ["MON","TUE","WED","THU","FRI","SAT","SUN"]
    cols_7 = st.columns(7)
    for i in range(7):
        day = today - datetime.timedelta(days=6-i)
        day_str = day.isoformat()
        studied = day_str in study_dates
        is_today = (day == today)
        bdr = "#FFD700" if is_today else ("#00FFD1" if studied else "rgba(0,255,209,0.08)")
        icon = "✅" if studied else ("📍" if is_today else "⬜")
        with cols_7[i]:
            st.markdown(f"""
            <div style='background:rgba(10,22,40,0.96);border:1px solid {bdr};
                border-radius:10px;padding:7px 4px;text-align:center;
                box-shadow:{"0 0 12px rgba(0,255,209,0.2)" if studied else ("0 0 12px rgba(255,215,0,0.2)" if is_today else "none")}'>
                <div style='font-size:14px'>{icon}</div>
                <div style='font-size:8px;font-weight:800;
                    color:{"#00FFD1" if studied else ("#FFD700" if is_today else "#4A6A80")};
                    text-transform:uppercase;letter-spacing:.5px;margin-top:2px;
                    font-family:"Rajdhani",sans-serif'>{day_labels[day.weekday()]}</div>
                <div style='font-size:8px;color:#4A6A80;margin-top:1px'>{day.day}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Word of the Day ──
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
        <div class='word-card' style='margin-bottom:16px'>
            <div style='font-size:9px;font-weight:800;color:rgba(0,255,209,0.4);text-transform:uppercase;
                letter-spacing:2px;margin-bottom:8px;font-family:"Rajdhani",sans-serif'>
                📖 WORD OF THE DAY</div>
            <div style='display:flex;align-items:baseline;gap:12px;flex-wrap:wrap'>
                <span style='font-family:"Orbitron",monospace;font-size:22px;font-weight:900;
                    color:#00FFD1;text-shadow:0 0 16px rgba(0,255,209,0.5)'>{w.get("word","")}</span>
                <span style='font-size:13px;color:#94B4CC'>— {w.get("urdu","")}</span>
            </div>
            <div style='font-size:13px;color:#E0F4FF;margin-top:6px;opacity:.8'>{w.get("meaning","")}</div>
            <div style='font-size:12px;color:#4A6A80;margin-top:4px;font-style:italic'>"{w.get("example","")}"</div>
            <div style='font-size:11px;color:#FFD700;margin-top:6px'>💡 {w.get("tip","")}</div>
        </div>""", unsafe_allow_html=True)

    # ── Stats ──
    total_q   = stats.get("total", 0)
    streak_v  = stats.get("streak", 0)
    badges_v  = len(u.get("badges", []))
    quizzes_v = stats.get("quizzes_done", 0)
    goals = {"q": 50, "streak": 7, "badges": 11, "quiz": 10}
    c1,c2,c3,c4 = st.columns(4)
    for col_w, icon, val, lbl, accent, pct in [
        (c1,"❓", total_q,             "Questions",  "#00FFD1", min(100, int(total_q/goals["q"]*100))),
        (c2,"🔥", f"{streak_v}d",      "Streak",     "#FF2D78", min(100, int(streak_v/goals["streak"]*100))),
        (c3,"🏆", badges_v,            "Badges",     "#FFD700", min(100, int(badges_v/goals["badges"]*100))),
        (c4,"📝", quizzes_v,           "Quizzes",    "#A78BFA", min(100, int(quizzes_v/goals["quiz"]*100))),
    ]:
        with col_w:
            st.markdown(f"""
            <div class='stat-card'>
                <div style='font-size:20px;margin-bottom:3px'>{icon}</div>
                <div class='stat-num'>{val}</div>
                <div class='stat-lbl'>{lbl}</div>
                <div style='background:rgba(0,0,0,0.4);border-radius:99px;height:5px;
                    overflow:hidden;margin-top:8px;border:1px solid rgba(0,255,209,0.06)'>
                    <div style='width:{pct}%;height:100%;border-radius:99px;background:{accent};
                        box-shadow:0 0 6px {accent}88;transition:width .6s'></div>
                </div>
                <div style='font-size:9px;color:#4A6A80;margin-top:3px;font-weight:700;
                    font-family:"Rajdhani",sans-serif;letter-spacing:.8px'>{pct}% GOAL</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    # ── Upcoming Homework ──
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
            st.markdown(f"""<div style='font-family:"Orbitron",monospace;font-size:13px;font-weight:800;
                color:#00FFD1;margin-bottom:10px;letter-spacing:1px'>📅 UPCOMING HOMEWORK</div>""",
                unsafe_allow_html=True)
            for hw in upcoming[:3]:
                dl = hw["days_left"]
                dl_color = "#FF2D78" if dl == 0 else "#FFD700" if dl <= 2 else "#00FFD1"
                dl_label = "DUE TODAY!" if dl == 0 else f"DUE IN {dl}D"
                subj_info = SUBJECTS.get(hw.get("subject","Maths"), {"emoji":"📚","color":"#00FFD1"})
                st.markdown(f"""
                <div style='background:rgba(10,22,40,0.96);border:1px solid rgba(0,255,209,0.12);
                    border-radius:12px;padding:11px 14px;margin-bottom:8px;
                    display:flex;align-items:center;gap:12px;
                    box-shadow:0 0 10px rgba(0,255,209,0.04)'>
                    <div style='font-size:22px;flex-shrink:0'>{subj_info["emoji"]}</div>
                    <div style='flex:1;min-width:0'>
                        <div style='font-weight:800;font-size:13px;color:#E0F4FF;
                            white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>
                            {hw.get("data",{}).get("title", hw.get("topic","Homework"))}</div>
                        <div style='font-size:11px;color:#4A6A80;margin-top:1px'>
                            {hw.get("subject","")} · {hw.get("grade","")}</div>
                    </div>
                    <span style='background:rgba(0,0,0,0.4);color:{dl_color};
                        border:1px solid {dl_color}44;border-radius:6px;
                        padding:3px 9px;font-size:10px;font-weight:800;white-space:nowrap;
                        font-family:"Rajdhani",sans-serif;letter-spacing:.8px'>{dl_label}</span>
                </div>""", unsafe_allow_html=True)

    # ── Continue Last Chat ──
    hist = load_json(HISTORY_FILE)
    user_hist = hist.get(u["email"], [])
    if user_hist:
        last = user_hist[-1]
        last_sub  = last.get("subject", "")
        last_msgs = last.get("messages", [])
        if last_msgs:
            last_q = next((m["content"][:55] for m in reversed(last_msgs) if m["role"]=="user"), "")
            if last_q:
                st.markdown(f"""
                <div style='background:linear-gradient(135deg,rgba(0,255,209,0.05),rgba(10,22,40,0.96));
                    border:1px solid rgba(0,255,209,0.12);border-radius:12px;
                    padding:11px 14px;margin-bottom:16px;display:flex;align-items:center;gap:10px'>
                    <div style='font-size:20px'>💬</div>
                    <div style='flex:1;min-width:0'>
                        <div style='font-size:9px;font-weight:800;color:#00FFD1;
                            text-transform:uppercase;letter-spacing:1.2px;margin-bottom:2px;
                            font-family:"Rajdhani",sans-serif'>CONTINUE LAST CHAT · {last_sub}</div>
                        <div style='font-size:12px;color:#94B4CC;font-weight:600;
                            white-space:nowrap;overflow:hidden;text-overflow:ellipsis'>
                            "{last_q}{"..." if len(last_q)==55 else ""}"</div>
                    </div>
                </div>""", unsafe_allow_html=True)
                if st.button("▶  CONTINUE CHAT", key="home_continue_chat"):
                    st.session_state.page = "chat"; st.rerun()
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── Quick Access ──
    st.markdown(f"""<div style='font-family:"Orbitron",monospace;font-size:13px;font-weight:800;
        color:#00FFD1;margin-bottom:10px;letter-spacing:1px;
        text-shadow:0 0 12px rgba(0,255,209,0.4)'>⚡ QUICK ACCESS</div>""", unsafe_allow_html=True)

    qa_items = [
        ("💬","Chat Tutor",    "chat"),
        ("📝","Practice Quiz", "quiz"),
        ("👥","Friendz Quiz",  "friends"),
        ("🎨","Image Gen",     "image"),
    ]
    qa_cols = st.columns(4)
    for col_w, (icon, label, page) in zip(qa_cols, qa_items):
        with col_w:
            is_active = (st.session_state.page == page)
            if st.button(f"{icon}\n{label}", key=f"home_go_{page}",
                         use_container_width=True,
                         type="primary" if is_active else "secondary"):
                st.session_state.page = page; st.rerun()

    st.markdown("""
    <style>
    div[data-testid="stHorizontalBlock"] .stButton > button {
        min-height: 80px !important;
        font-size: 12.5px !important;
        white-space: pre-line !important;
        line-height: 1.5 !important;
        border-radius: 14px !important;
        font-weight: 800 !important;
    }
    </style>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# CHAT / AI TUTOR — with Ustad mascot
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
    st.markdown("<div class='section-header'>💬 CHAT TUTOR — ASK USTAD ANYTHING</div>", unsafe_allow_html=True)

    # Ustad mascot header
    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:14px;
        background:linear-gradient(135deg,rgba(0,255,209,0.05),rgba(10,22,40,0.96));
        border:1px solid rgba(0,255,209,0.15);border-radius:14px;padding:12px 16px;margin-bottom:16px'>
        <div class='mascot-float'>{MASCOT_USTAD_SVG}</div>
        <div>
            <div style='font-family:"Orbitron",monospace;font-size:13px;font-weight:800;
                color:#00FFD1;text-shadow:0 0 10px rgba(0,255,209,0.4)'>USTAD AI 🤖</div>
            <div style='font-size:12px;color:#94B4CC;margin-top:3px'>
                Your personal AI tutor — ask me anything in any subject!</div>
        </div>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        sub = st.selectbox("📚 Subject", list(SUBJECTS.keys()),
                           index=list(SUBJECTS.keys()).index(st.session_state.subject))
    with c2:
        lvl_idx = get_level_index(u.get("grade","Grade 6"))
        lvl = st.selectbox("🏫 Grade", LEVELS, index=lvl_idx)
    st.session_state.subject = sub

    if st.button("🆕 NEW CHAT", type="secondary"):
        st.session_state.chat_messages = []
        st.session_state.session_id    = None
        st.rerun()

    st.markdown("<div style='font-size:9px;font-weight:800;color:rgba(0,255,209,0.4);text-transform:uppercase;letter-spacing:2px;margin:10px 0 6px;font-family:\"Rajdhani\",sans-serif'>⚡ QUICK QUESTIONS</div>", unsafe_allow_html=True)
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
        st.markdown(f"""
        <div style='background:rgba(10,22,40,0.8);border:1px solid rgba(0,255,209,0.12);
            border-radius:14px;padding:16px;text-align:center;color:#94B4CC;font-size:13px'>
            👋 Assalam-o-Alaikum <b style='color:#00FFD1'>{u['name'].split()[0]}</b>!
            I'm Ustad, your <b style='color:#A78BFA'>{sub}</b> tutor for {lvl}. Ask me anything!
        </div>""", unsafe_allow_html=True)

    for m in st.session_state.chat_messages:
        if m["role"] == "user":
            st.markdown(f"<div class='msg-lbl msg-lbl-r'>YOU</div><div class='msg-user'>{m['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='msg-lbl'>🤖 USTAD AI</div><div class='msg-bot'>{m['content']}</div>", unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=True):
        ph  = "یہاں سوال لکھیں..." if sub=="Urdu" else f"Ask your {sub} question here..."
        txt = st.text_area("Q", placeholder=ph, height=80, label_visibility="collapsed")
        c1f, c2f = st.columns([3,1])
        with c1f:
            send = st.form_submit_button("📤 SEND", use_container_width=True, type="primary")
        with c2f:
            clear = st.form_submit_button("🗑️ CLEAR", use_container_width=True)
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
# PRACTICE QUIZ
# ═════════════════════════════════════════════════════════════════
def page_quiz():
    u = st.session_state.user
    st.markdown("<div class='section-header orange'>📝 PRACTICE QUIZ</div>", unsafe_allow_html=True)
    q = st.session_state.quiz

    if q is not None and q["done"]:
        total = len(q["questions"]); score = q["score"]
        pct   = int((score/total)*100)
        emoji = "🏆" if pct>=80 else "👍" if pct>=60 else "💪"
        col   = "#00FFD1" if pct>=80 else "#FFD700" if pct>=60 else "#FF2D78"
        st.markdown(f"""
        <div style='text-align:center;background:linear-gradient(135deg,rgba(10,22,40,0.96),rgba(6,11,24,0.99));
            border-radius:20px;padding:28px;box-shadow:0 8px 32px rgba(0,0,0,0.6);margin-bottom:18px;
            border:1px solid rgba(0,255,209,0.15)'>
            <div style='font-size:56px'>{emoji}</div>
            <h2 style='font-family:"Orbitron",monospace;font-size:22px;font-weight:800;color:{col};
                text-shadow:0 0 16px {col}88'>QUIZ COMPLETE!</h2>
            <div style='font-size:48px;font-weight:900;color:{col};margin:8px 0;
                font-family:"Orbitron",monospace'>{score}/{total}</div>
            <div style='font-size:15px;color:#94B4CC'>
                {pct}% — {"Excellent! ⭐" if pct>=80 else "Good effort! 📚" if pct>=60 else "Keep going! 💪"}
            </div>
            <div style='font-size:12px;color:#4A6A80;margin-top:4px'>
                {q.get("topic","Custom")} · {q.get("difficulty","Medium")} · {q.get("sub","")} {q.get("lvl","")}
            </div>
        </div>""", unsafe_allow_html=True)

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
            bg  = "rgba(0,255,209,0.05)" if correct else "rgba(255,45,120,0.05)"
            bdr = "rgba(0,255,209,0.3)"  if correct else "rgba(255,45,120,0.3)"
            wrong_line = "" if correct else f'<div style="font-size:13px;color:#00FFD1;margin-top:2px">✅ Correct: <b>{ques["answer"]}</b></div>'
            st.markdown(f"""
            <div style='background:{bg};border:1px solid {bdr};border-radius:12px;
                padding:14px 16px;margin-bottom:10px;color:#E0F4FF'>
                <div style='font-weight:700;font-size:14px'>Q{i+1}. {ques["q"]}</div>
                <div style='font-size:13px;margin-top:5px'>Your answer: <b>{ans["chosen"]}</b> {"✅" if correct else "❌"}</div>
                {wrong_line}
                <div style='font-size:12px;color:#94B4CC;margin-top:5px;padding:6px 10px;background:rgba(0,0,0,0.3);border-radius:8px'>
                    💡 {ques.get("explanation","")}
                </div>
            </div>""", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 NEW QUIZ", use_container_width=True, type="primary"):
                st.session_state.quiz = None; st.rerun()
        with col2:
            if st.button("👥 CHALLENGE FRIENDS", use_container_width=True):
                st.session_state.page = "friends"; st.rerun()
        return

    if q is not None and not q["done"]:
        info    = SUBJECTS.get(q.get("sub","Maths"), SUBJECTS["Maths"])
        current = q["current"]
        ques    = q["questions"][current]
        pct_bar = int((current/len(q["questions"]))*100)
        st.markdown(f"""
        <div style='background:rgba(10,22,40,0.9);border-radius:14px;padding:12px 16px;
            margin-bottom:14px;display:flex;justify-content:space-between;align-items:center;
            border:1px solid rgba(0,255,209,0.1)'>
            <div>
                <span style='font-weight:800;color:{info["color"]}'>{info["emoji"]} {q.get("sub","")} QUIZ</span>
                <span style='font-size:12px;color:#4A6A80;margin-left:10px'>{q.get("topic","")} · {q.get("difficulty","")}</span>
            </div>
            <span style='font-family:"Orbitron",monospace;font-weight:700;color:{info["color"]}'>
                {q["score"]}/{current}</span>
        </div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class='prog-bar'><div class='prog-fill' style='width:{pct_bar}%'></div></div><br>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='background:rgba(10,22,40,0.96);border-radius:16px;padding:18px 20px;
            margin-bottom:14px;box-shadow:0 8px 32px rgba(0,0,0,0.6);font-weight:800;font-size:15px;
            color:#E0F4FF;line-height:1.55;border-left:3px solid {info["color"]}'>
            Q{current+1}. {ques["q"]}
        </div>""", unsafe_allow_html=True)
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

    st.markdown("""
    <div style='background:rgba(0,255,209,0.04);border-radius:14px;padding:14px 18px;
        margin-bottom:18px;font-size:13px;color:#00FFD1;border:1px solid rgba(0,255,209,0.15)'>
        📝 <b>Custom Quiz Generator</b> — Enter any topic, pick difficulty and number of questions!
    </div>""", unsafe_allow_html=True)

    st.markdown("#### ⚙️ QUIZ SETTINGS")
    c1, c2 = st.columns(2)
    with c1: quiz_sub = st.selectbox("📚 Subject", list(SUBJECTS.keys()), key="quiz_sub")
    with c2:
        lvl_idx  = get_level_index(u.get("grade","Grade 6"))
        quiz_lvl = st.selectbox("🏫 Grade", LEVELS, index=lvl_idx, key="quiz_lvl")
    quiz_topic = st.text_input("✏️ Topic (optional)", placeholder="e.g. Photosynthesis, Quadratic equations...", key="quiz_topic_input")
    c3, c4 = st.columns(2)
    with c3: difficulty = st.selectbox("🎯 Difficulty", ["Easy","Medium","Hard"], index=1, key="quiz_diff")
    with c4: num_qs = st.selectbox("🔢 Questions", [5,10,15,20], index=0, key="quiz_num")
    diff_colors = {"Easy":"#00FFD1","Medium":"#FFD700","Hard":"#FF2D78"}
    diff_info = {"Easy":("🟢","Basic recall — perfect for revision."),
                 "Medium":("🟡","Mixed conceptual + application."),
                 "Hard":("🔴","Analytical higher-order thinking.")}
    d_icon, d_text = diff_info[difficulty]
    st.markdown(f"""<div style='background:rgba(0,0,0,0.3);border-radius:10px;padding:10px 14px;
        font-size:12px;color:{diff_colors[difficulty]};margin-bottom:14px;
        border:1px solid {diff_colors[difficulty]}22'>{d_icon} <b>{difficulty}:</b> {d_text}</div>""",
        unsafe_allow_html=True)

    if st.button("🚀 GENERATE QUIZ", use_container_width=True, type="primary", key="gen_quiz_btn"):
        topic_str = quiz_topic.strip() if quiz_topic.strip() else f"{quiz_sub} general topics"
        with st.spinner(f"✨ Generating {num_qs} {difficulty} questions on '{topic_str}'..."):
            raw = call_ai(
                [{"role":"user","content":
                  f"Create exactly {num_qs} {difficulty}-level MCQ questions about '{topic_str}' "
                  f"for {quiz_lvl} {quiz_sub} students in Pakistan. "
                  f'Return ONLY raw JSON: {{"questions":[{{"q":"question text","options":["A. option","B. option","C. option","D. option"],"answer":"A. option","explanation":"why"}}]}}'}],
                "Quiz generator. Return ONLY valid raw JSON. No backticks.", 2000
            )
        try:
            clean = raw.replace("```json","").replace("```","").strip()
            data  = json.loads(clean)
            st.session_state.quiz = {
                "questions": data["questions"][:num_qs], "current":0, "score":0,
                "answers":[], "done":False, "sub":quiz_sub, "lvl":quiz_lvl,
                "topic":topic_str, "difficulty":difficulty
            }
            st.rerun()
        except:
            st.error("⚠️ Could not generate quiz. Try again with a different topic.")


# ═══════════════ FRIENDS QUIZ ════════════════════════════════════
def page_friends():
    u = st.session_state.user
    st.markdown("<div class='section-header purple'>👥 FRIENDS GROUP QUIZ</div>", unsafe_allow_html=True)
    grp = st.session_state.group_session

    if grp is not None and grp.get("done"):
        st.markdown("## 🏆 FINAL LEADERBOARD")
        players = sorted(grp["players"], key=lambda p: p["score"], reverse=True)
        rank_icons = ["🥇","🥈","🥉","4️⃣"]
        for i, p in enumerate(players):
            total = len(grp["questions"])
            pct   = int((p["score"]/total)*100)
            st.markdown(f"""<div class='lb-row'>
                <span class='lb-rank'>{rank_icons[i]}</span>
                <span class='lb-name'>{p['name']} {p['avatar']}</span>
                <span style='font-size:12px;color:#4A6A80'>{pct}%</span>
                <span class='lb-score'>{p['score']}/{total}</span>
            </div>""", unsafe_allow_html=True)
        winner = players[0]
        st.markdown(f"""
        <div style='text-align:center;background:linear-gradient(135deg,rgba(255,215,0,0.08),rgba(10,22,40,0.96));
            border-radius:16px;padding:20px;margin-top:14px;border:1px solid rgba(255,215,0,0.25);
            box-shadow:0 0 20px rgba(255,215,0,0.15)'>
            <div style='font-size:40px'>🎉</div>
            <div style='font-family:"Orbitron",monospace;font-size:18px;font-weight:800;color:#FFD700;
                text-shadow:0 0 16px rgba(255,215,0,0.5)'>
                {winner['name']} WINS {winner['score']}/{len(grp['questions'])}!</div>
        </div>""", unsafe_allow_html=True)
        if st.button("🔄 PLAY AGAIN", use_container_width=True, type="primary"):
            st.session_state.group_session = None; st.rerun()
        return

    if grp is not None and not grp.get("done"):
        pidx    = grp["current_player"]
        player  = grp["players"][pidx]
        qidx    = player.get("q_index", 0)
        total_q = len(grp["questions"])
        if qidx >= total_q:
            grp["current_player"] = pidx + 1
            if grp["current_player"] >= len(grp["players"]): grp["done"] = True
            st.session_state.group_session = grp; st.rerun()
            return
        ques = grp["questions"][qidx]
        for i, p in enumerate(grp["players"]):
            active = (i == pidx)
            bg   = "rgba(139,92,246,0.15)" if active else "rgba(10,22,40,0.8)"
            col  = "#A78BFA" if active else "#4A6A80"
            bdr  = "rgba(139,92,246,0.4)" if active else "rgba(0,255,209,0.08)"
            st.markdown(f"""
            <div style='display:inline-block;background:{bg};color:{col};border-radius:8px;
                padding:5px 14px;font-size:12px;font-weight:800;margin-right:6px;
                border:1px solid {bdr};font-family:"Rajdhani",sans-serif;letter-spacing:.5px'>
                {p['avatar']} {p['name']}: {p['score']}/{total_q} {"← NOW" if active else ""}
            </div>""", unsafe_allow_html=True)
        st.markdown(f"""<br><div style='background:rgba(139,92,246,0.07);border-radius:14px;
            padding:12px 16px;margin:10px 0;font-size:12px;color:#A78BFA;font-weight:700;
            border:1px solid rgba(139,92,246,0.2)'>
            🎮 {player['name']}'s turn — Q{qidx+1} of {total_q}</div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class='prog-bar'><div class='prog-fill' style='width:{int((qidx/total_q)*100)}%'></div></div><br>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='background:rgba(10,22,40,0.96);border-radius:16px;padding:18px 20px;
            margin-bottom:14px;box-shadow:0 8px 32px rgba(0,0,0,0.6);font-weight:800;font-size:15px;
            color:#E0F4FF;border-left:3px solid #A78BFA'>Q{qidx+1}. {ques["q"]}</div>""", unsafe_allow_html=True)
        for opt in ques["options"]:
            if st.button(opt, key=f"grp_{pidx}_{qidx}_{opt}", use_container_width=True):
                if opt == ques["answer"]:
                    grp["players"][pidx]["score"] += 1; st.toast("✅ Correct!", icon="🎉")
                else: st.toast(f"❌ Correct: {ques['answer']}", icon="💡")
                grp["players"][pidx]["q_index"] = qidx + 1
                st.session_state.group_session = grp; st.rerun()
        return

    st.markdown("""
    <div style='background:rgba(139,92,246,0.06);border-radius:14px;padding:14px 18px;
        margin-bottom:18px;font-size:13px;color:#A78BFA;border:1px solid rgba(139,92,246,0.18)'>
        👥 <b>Friends Group Quiz</b> — Take turns answering the same questions. Highest scorer wins!
    </div>""", unsafe_allow_html=True)

    num_friends = st.selectbox("👥 Players (including you)", [2,3,4], index=0)
    st.markdown("#### 🎮 PLAYER NAMES")
    player_names = [u["name"]]
    for i in range(1, num_friends):
        name = st.text_input(f"Player {i+1} name", placeholder=f"Friend {i}", key=f"friend_name_{i}")
        player_names.append(name.strip() if name.strip() else f"Player {i+1}")

    st.markdown("#### 📚 QUIZ SETTINGS")
    c1, c2 = st.columns(2)
    with c1: grp_sub  = st.selectbox("Subject", list(SUBJECTS.keys()), key="grp_sub")
    with c2:
        lvl_idx = get_level_index(u.get("grade","Grade 6"))
        grp_lvl = st.selectbox("Grade", LEVELS, index=lvl_idx, key="grp_lvl")
    grp_topic = st.text_input("Topic (optional)", placeholder="Any topic...", key="grp_topic")
    c3, c4 = st.columns(2)
    with c3: grp_diff = st.selectbox("Difficulty", ["Easy","Medium","Hard"], index=1, key="grp_diff")
    with c4: grp_num  = st.selectbox("Questions per player", [5,10], index=0, key="grp_num")

    if st.button("🚀 START GROUP QUIZ", use_container_width=True, type="primary"):
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
            avatars = ["🤖","🚀","🧙","🦸","🧝","🧑‍🔬"]
            players = [{"name":n,"avatar":avatars[i%len(avatars)],"score":0,"q_index":0}
                       for i,n in enumerate(player_names)]
            st.session_state.group_session = {
                "questions":data["questions"][:grp_num],"players":players,
                "current_player":0,"done":False,
                "topic":topic_str,"difficulty":grp_diff
            }
            st.rerun()
        except:
            st.error("⚠️ Could not generate quiz. Please try again.")


# ═══════════════ IMAGE GENERATOR ═════════════════════════════════
def page_image():
    u = st.session_state.user
    st.markdown("<div class='section-header purple'>🎨 AI IMAGE GENERATOR</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:rgba(139,92,246,0.06);border:1px solid rgba(139,92,246,0.2);border-radius:12px;
        padding:12px 16px;margin-bottom:16px;font-size:13px;color:#A78BFA'>
        🖌️ Claude AI draws a <b>custom SVG diagram</b> — choose your style! Takes 20–40 seconds.
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
        "📐 Educational Diagram":"#60A5FA",
        "🎨 Cartoon":            "#FF2D78",
        "🎌 Anime Style":        "#A78BFA",
        "🤖 AI Art":             "#00FFD1",
        "🔬 Realistic / Scientific":"#FFD700",
    }
    sc = style_colors.get(style_choice,"#00FFD1")
    st.markdown(f"""<div style='background:{sc}0F;border:1px solid {sc}33;border-radius:10px;
        padding:8px 14px;font-size:12px;color:{sc};font-weight:700;margin-bottom:12px'>
        {style_choice} — {style_hint[:60]}...</div>""", unsafe_allow_html=True)

    prompt = st.text_area("📝 Describe what you want to see",
        placeholder="e.g. Diagram showing how photosynthesis works\ne.g. Solar system with all 8 planets\ne.g. Water cycle diagram",
        height=100, key="img_prompt")

    if st.button("🎨 GENERATE IMAGE", use_container_width=True, type="primary"):
        if not prompt.strip():
            st.warning("Please enter a description first!")
            return
        prog = st.progress(0, text="🎨 Step 1/4 — Planning...")
        time.sleep(0.5); prog.progress(20, text="✏️ Step 2/4 — Drawing...")
        time.sleep(0.5); prog.progress(45, text="🎨 Step 3/4 — Adding colors...")

        system_msg = (
            "You are an expert SVG illustrator for educational content. "
            "STRICT OUTPUT RULES:\n"
            "1. Output ONLY the SVG code. No markdown. No backticks. No explanations.\n"
            "2. Start with exactly: <svg\n3. End with exactly: </svg>\n"
            f"4. Use: xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 700 500\" width=\"700\" height=\"500\"\n"
            "5. Include <defs> with at least 3 linearGradient definitions.\n"
            "6. Bold title at top (y=35, font-size=24, font-weight=bold, text-anchor=middle, x=350).\n"
            "7. BRIGHT colors — use gradient fills. Include 20+ visual elements.\n"
            f"8. Style: {style_hint}\n"
            "9. Every component must have a clear text label.\n"
            "10. Make it look like a professional educational poster.\n"
            "11. DO NOT use any xlink:href or external images."
        )
        user_msg = (
            f"Create a detailed colorful educational SVG: TOPIC: {prompt}\n"
            f"SUBJECT: {img_sub}\nLEVEL: {img_lvl}\nSTYLE: {style_hint}\n"
            f"Output ONLY the SVG. Start with <svg and end with </svg>."
        )
        raw = call_ai_svg([{"role":"user","content":user_msg}], system_msg)
        prog.progress(90, text="✨ Step 4/4 — Finishing..."); time.sleep(0.3)
        prog.progress(100, text="✅ Done!"); time.sleep(0.3); prog.empty()

        cleaned = raw
        for fence in ["```svg","```xml","```html","```"]: cleaned = cleaned.replace(fence,"")
        cleaned = cleaned.strip()
        svg_start = cleaned.find("<svg"); svg_end = cleaned.rfind("</svg>")

        if svg_start >= 0 and svg_end >= 0:
            final_svg = cleaned[svg_start:svg_end+6]
            st.success("✅ Image generated!")
            st.markdown("### 🖼️ Your Educational Image")
            st.components.v1.html(final_svg, height=520, scrolling=False)
            b64 = base64.b64encode(final_svg.encode()).decode()
            st.markdown(
                f'<a href="data:image/svg+xml;base64,{b64}" download="zm_diagram.svg" '
                f'style="display:inline-flex;align-items:center;gap:8px;padding:10px 22px;'
                f'background:linear-gradient(135deg,rgba(139,92,246,0.2),rgba(10,22,40,0.9));'
                f'color:#A78BFA;border-radius:12px;font-weight:700;font-size:14px;'
                f'text-decoration:none;border:1px solid rgba(139,92,246,0.3);margin-top:10px">⬇️ DOWNLOAD SVG</a>',
                unsafe_allow_html=True
            )
            imgs = load_json(IMAGES_FILE); email = u["email"]
            if email not in imgs: imgs[email] = []
            imgs[email].insert(0,{"id":str(int(time.time())),"svg":final_svg,"prompt":prompt,
                "subject":img_sub,"level":img_lvl,"style":style_choice,
                "created":datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
            save_json(IMAGES_FILE, imgs)
            users = load_json(USERS_FILE); eu = users.get(u["email"], u)
            eu.setdefault("stats", init_stats())
            eu["stats"]["images"] = eu["stats"].get("images",0)+1
            eu, new_b = check_badges(eu); users[u["email"]] = eu
            save_json(USERS_FILE, users); st.session_state.user = eu
            for b in new_b: st.toast(f"🏆 Badge: {b['icon']} {b['name']}!", icon="🎉")
        else:
            st.error("⚠️ Could not generate image. Try rephrasing your description.")

    imgs = load_json(IMAGES_FILE); user_imgs = imgs.get(u["email"], [])
    if user_imgs:
        st.markdown("---")
        st.markdown("### 🖼️ YOUR IMAGE GALLERY")
        for i in range(0, min(len(user_imgs), 8), 2):
            cols = st.columns(2)
            for j, c in enumerate(cols):
                if i+j < len(user_imgs):
                    img = user_imgs[i+j]
                    with c:
                        st.markdown(f"""
                        <div style='background:rgba(10,22,40,0.96);border-radius:14px;padding:12px;
                            box-shadow:0 8px 32px rgba(0,0,0,0.6);border:1px solid rgba(0,255,209,0.1);margin-bottom:12px'>
                            <div style='font-size:10px;font-weight:800;color:#A78BFA;margin-bottom:8px;
                                font-family:"Rajdhani",sans-serif;letter-spacing:1px'>
                                {img['style']} · {img['subject']} · {img['created']}</div>
                            <div style='font-size:12px;color:#94B4CC;margin-bottom:8px'>
                                📝 {img['prompt'][:60]}...</div>
                        </div>""", unsafe_allow_html=True)
                        with st.expander("🔍 View"):
                            st.components.v1.html(img["svg"], height=480, scrolling=False)


# ═══════════════ SYLLABUS ════════════════════════════════════════
def page_syllabus():
    u = st.session_state.user
    st.markdown("<div class='section-header blue'>📚 MY SYLLABUS</div>", unsafe_allow_html=True)
    st.markdown("""<div class='syl-step'><div class='syl-step-title'>📋 Step 1 — Choose Curriculum</div></div>""", unsafe_allow_html=True)
    curriculum = st.selectbox("Curriculum", ["Cambridge (Pakistan)"], key="syl_curr")
    st.markdown("""<div class='syl-step'><div class='syl-step-title'>🏫 Step 2 — Choose Grade</div></div>""", unsafe_allow_html=True)
    default_grade = normalise_level(u.get("grade","Grade 8"))
    sel_grade = st.selectbox("Grade", LEVELS, index=get_level_index(default_grade), key="syl_grade_sel")
    st.markdown("""<div class='syl-step'><div class='syl-step-title'>📖 Step 3 — Choose Subject</div></div>""", unsafe_allow_html=True)
    available_subjects = CAMBRIDGE_SUBJECTS.get(sel_grade, list(SUBJECTS.keys()))
    sel_sub = st.selectbox("Subject", available_subjects, key="syl_sub_sel")
    st.session_state.syl_subject = sel_sub

    with st.expander("➕ Step 4 — Add Custom Class or Subject"):
        cc1, cc2 = st.columns(2)
        with cc1: custom_grade = st.text_input("Custom Grade", placeholder="e.g. Grade 11...", key="custom_grade_inp")
        with cc2: custom_subject = st.text_input("Custom Subject", placeholder="e.g. Accounting...", key="custom_sub_inp")
        if custom_grade.strip(): sel_grade = custom_grade.strip()
        if custom_subject.strip(): sel_sub = custom_subject.strip()
        if custom_grade.strip() or custom_subject.strip():
            st.info(f"✅ Using: **{sel_grade}** · **{sel_sub}**")

    if sel_grade != normalise_level(u.get("grade","")):
        users = load_json(USERS_FILE)
        if u["email"] in users:
            users[u["email"]]["grade"] = sel_grade
            save_json(USERS_FILE, users)
            st.session_state.user["grade"] = sel_grade

    subj_key_map = {"Mathematics":"Maths","Maths":"Maths","Physics":"Physics","Chemistry":"Chemistry",
                    "Biology":"Biology","English":"English","English Language":"English",
                    "Computer Science":"Computer Science","Urdu":"Urdu","Science":"Biology","Islamiyat":"English"}
    subj_key  = subj_key_map.get(sel_sub, "Maths")
    info      = SUBJECTS.get(subj_key, {"emoji":"📚","color":"#00FFD1"})
    sub_color = info["color"]; sub_emoji = info["emoji"]

    st.markdown(f"""
    <div style='background:rgba(10,22,40,0.96);border:1px solid {sub_color}33;
        border-radius:14px;padding:14px 18px;margin:16px 0;
        display:flex;align-items:center;gap:12px;box-shadow:0 0 20px {sub_color}11'>
        <div style='font-size:36px'>{sub_emoji}</div>
        <div>
            <div style='font-weight:800;font-size:16px;color:{sub_color};
                font-family:"Orbitron",monospace;letter-spacing:.5px'>{sel_sub} — {sel_grade}</div>
            <div style='font-size:12px;color:#4A6A80;margin-top:2px'>🎓 {curriculum}</div>
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
        st.info(f"📋 No pre-loaded syllabus for {sel_sub} — {sel_grade}. Use the AI to explore!")
        if st.button(f"💬 ASK USTAD ABOUT {sel_sub} {sel_grade}", use_container_width=True, type="primary"):
            st.session_state.subject = subj_key
            st.session_state.chat_messages = [{"role":"user","content":
                f"Give me an overview of the {sel_sub} syllabus for {sel_grade} in Pakistan."}]
            st.session_state.page = "chat"; st.rerun()
        return

    studied_topics = u.get("studied_topics",{})
    key = f"{subj_key}_{sel_grade}"
    done_topics  = studied_topics.get(key,[])
    total_topics = sum(len(un["topics"]) for un in units)
    done_count   = sum(1 for un in units for t in un["topics"] if f"{un['unit']}::{t}" in done_topics)
    pct = int((done_count/max(total_topics,1))*100)

    st.markdown(f"""
    <div style='margin-bottom:16px'>
        <div style='display:flex;justify-content:space-between;font-size:12px;font-weight:700;
            color:#4A6A80;margin-bottom:6px;font-family:"Rajdhani",sans-serif;letter-spacing:.8px'>
            <span>📊 SYLLABUS PROGRESS</span>
            <span style='color:{sub_color}'>{done_count}/{total_topics} TOPICS ({pct}%)</span>
        </div>
        <div class='prog-bar'><div class='prog-fill' style='width:{pct}%'></div></div>
    </div>""", unsafe_allow_html=True)

    for ui, unit in enumerate(units):
        unit_done = [t for t in unit["topics"] if f"{unit['unit']}::{t}" in done_topics]
        unit_pct  = int((len(unit_done)/max(len(unit["topics"]),1))*100)
        with st.expander(
            f"{'✅' if unit_pct==100 else '🔵' if unit_pct>0 else '⬜'}  "
            f"Unit {ui+1}: {unit['unit']}  ({unit_pct}% done)", expanded=(ui==0)
        ):
            st.markdown(f"""<div class='prog-bar' style='margin-bottom:12px'>
                <div class='prog-fill' style='width:{unit_pct}%'></div></div>""", unsafe_allow_html=True)
            chip_parts = []
            for t in unit["topics"]:
                tk = f"{unit['unit']}::{t}"; tick = "✅ " if tk in done_topics else ""
                chip_parts.append(f"<span class='topic-chip' style='background:{sub_color}11;border:1px solid {sub_color}33;color:{sub_color}'>{tick}{t}</span>")
            st.markdown(f"<div style='margin-bottom:12px'>{''.join(chip_parts)}</div>", unsafe_allow_html=True)

            for topic in unit["topics"]:
                topic_key = f"{unit['unit']}::{topic}"
                is_done   = topic_key in done_topics
                tc1, tc2, tc3 = st.columns([3,1,1])
                with tc1:
                    st.markdown(f"<div style='padding:6px 0;font-size:14px;color:{'#00FFD1' if is_done else '#E0F4FF'};font-weight:{'700' if is_done else '400'}'>{'✅' if is_done else '📖'} {topic}</div>", unsafe_allow_html=True)
                with tc2:
                    if st.button("💬 Ask", key=f"ask_{ui}_{topic[:18]}", use_container_width=True):
                        st.session_state.subject = subj_key; st.session_state.level = sel_grade
                        st.session_state.chat_messages = [{"role":"user","content":f"Explain this topic: {topic}"}]
                        st.session_state.session_id = None; st.session_state.page = "chat"; st.rerun()
                with tc3:
                    if st.button("✅ Done" if is_done else "Mark ✓", key=f"done_{ui}_{topic[:18]}", use_container_width=True):
                        users = load_json(USERS_FILE); eu = users.get(u["email"],u)
                        st_map = eu.get("studied_topics",{}); tlist = st_map.get(key,[])
                        if topic_key in tlist: tlist.remove(topic_key)
                        else: tlist.append(topic_key)
                        st_map[key] = tlist; eu["studied_topics"] = st_map
                        users[u["email"]] = eu; save_json(USERS_FILE, users)
                        st.session_state.user = eu; st.rerun()

            ba, bb, bc = st.columns(3)
            with ba:
                if st.button(f"📝 Quiz Unit {ui+1}", key=f"qunit_{ui}", use_container_width=True):
                    topics_str = ", ".join(unit["topics"])
                    with st.spinner("Generating..."):
                        raw = call_ai([{"role":"user","content":
                            f"Create 5 MCQ for unit '{unit['unit']}' covering: {topics_str}. {sel_grade} {sel_sub}. "
                            f'Return ONLY raw JSON: {{"questions":[{{"q":"...","options":["A.","B.","C.","D."],"answer":"A.","explanation":"..."}}]}}'}],
                            "Quiz generator. Return ONLY valid raw JSON.", 1200)
                        try:
                            data = json.loads(raw.replace("```json","").replace("```","").strip())
                            st.session_state.quiz = {"questions":data["questions"],"current":0,"score":0,
                                "answers":[],"done":False,"sub":subj_key,"lvl":sel_grade,
                                "topic":unit["unit"],"difficulty":"Medium"}
                            st.session_state.page = "quiz"; st.rerun()
                        except: st.error("Could not generate quiz.")
            with bb:
                if st.button(f"🎨 Diagram", key=f"imgunit_{ui}", use_container_width=True):
                    st.session_state.page = "image"; st.rerun()
            with bc:
                if st.button(f"📖 Summary", key=f"sumunit_{ui}", use_container_width=True):
                    topics_str = ", ".join(unit["topics"])
                    with st.spinner("Generating summary..."):
                        summary = call_ai([{"role":"user","content":
                            f"Revision summary of '{unit['unit']}' for {sel_grade} {sel_sub}. "
                            f"Topics: {topics_str}. Bullet points, key formulas, max 300 words."}],
                            f"You are a {sel_sub} teacher.", 800)
                    st.markdown(f"""<div style='background:rgba(0,0,0,0.3);border-left:3px solid {sub_color};
                        border-radius:0 12px 12px 0;padding:14px 16px;margin-top:10px;
                        font-size:13px;line-height:1.7;color:#E0F4FF'>{summary}</div>""", unsafe_allow_html=True)

    st.markdown("---")
    syllabus_text = f"{sel_sub} — {sel_grade}\nBoard: {board}\n\n"
    for ui, unit in enumerate(units):
        syllabus_text += f"Unit {ui+1}: {unit['unit']}\n"
        for t in unit["topics"]: syllabus_text += f"  • {t}\n"
        syllabus_text += "\n"
    b64 = base64.b64encode(syllabus_text.encode()).decode()
    st.markdown(
        f'<a href="data:text/plain;base64,{b64}" download="{sel_sub}_{sel_grade}_syllabus.txt" '
        f'style="display:inline-block;padding:10px 20px;background:rgba(0,255,209,0.1);'
        f'color:#00FFD1;border-radius:12px;font-weight:700;font-size:14px;text-decoration:none;'
        f'border:1px solid rgba(0,255,209,0.25);margin-top:8px">⬇️ DOWNLOAD SYLLABUS</a>',
        unsafe_allow_html=True
    )


# ═══════════════ PROGRESS ════════════════════════════════════════
def page_progress():
    u     = st.session_state.user
    stats = u.get("stats",{})
    total = stats.get("total",0)
    st.markdown("<div class='section-header'>📊 MY PROGRESS</div>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("❓ Questions",  total)
    with c2: st.metric("🏆 Badges",     len(u.get("badges",[])))
    with c3: st.metric("🔥 Streak",     f"{stats.get('streak',0)} days")
    with c4: st.metric("🎯 Quizzes",    stats.get("quizzes_done",0))

    st.markdown("### 📚 QUESTIONS PER SUBJECT")
    for name, info in SUBJECTS.items():
        cnt = stats.get(name,0); pct = int((cnt/max(total,1))*100)
        st.markdown(f"""
        <div style='margin-bottom:14px'>
            <div style='display:flex;justify-content:space-between;font-size:13px;font-weight:700;
                margin-bottom:5px;color:#E0F4FF'>
                <span>{info['emoji']} {name}</span>
                <span style='color:{info["color"]}'>{cnt} questions ({pct}%)</span>
            </div>
            <div class='prog-bar'><div class='prog-fill' style='width:{pct}%;background:{info["color"]}'></div></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("### 🛠️ ACTIVITY")
    c1,c2,c3 = st.columns(3)
    with c1: st.metric("🎨 Images Generated", stats.get("images",0))
    with c2: st.metric("📅 Member Since",      u.get("joined",""))
    with c3: st.metric("📖 Subjects Studied",  sum(1 for s in SUBJECTS if stats.get(s,0)>0))

# ═══════════════ HISTORY ═════════════════════════════════════════
def page_history():
    u = st.session_state.user
    st.markdown("<div class='section-header'>🕐 CHAT HISTORY</div>", unsafe_allow_html=True)
    hist     = load_json(HISTORY_FILE)
    sessions = sorted(hist.get(u["email"],[]), key=lambda x:x.get("updated",""), reverse=True)
    if not sessions:
        st.info("📭 No chat history yet. Start a conversation with Ustad!")
        return
    if st.button("🗑️ CLEAR ALL HISTORY", type="secondary"):
        hist[u["email"]] = []; save_json(HISTORY_FILE, hist)
        st.success("History cleared."); st.rerun()
    for sess in sessions:
        info  = SUBJECTS.get(sess.get("subject",""), {"emoji":"📚","color":"#00FFD1"})
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
                st.session_state.chat_messages = msgs; st.session_state.session_id = sess["id"]
                st.session_state.subject = sess.get("subject","Maths")
                st.session_state.page = "chat"; st.rerun()

# ═══════════════ BADGES ══════════════════════════════════════════
def page_badges():
    u      = st.session_state.user
    earned = u.get("badges",[])
    st.markdown("<div class='section-header orange'>🏆 BADGES & ACHIEVEMENTS</div>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#94B4CC;font-size:13px'>Earned <b style='color:#00FFD1'>{len(earned)}</b> of <b style='color:#00FFD1'>{len(BADGES)}</b> badges</p>", unsafe_allow_html=True)
    cols = st.columns(3)
    for i,b in enumerate(BADGES):
        is_earned = b["id"] in earned
        with cols[i%3]:
            locked = "" if is_earned else "badge-locked"
            status_color = "#00FFD1" if is_earned else "#4A6A80"
            status_text  = "✅ EARNED" if is_earned else "🔒 LOCKED"
            st.markdown(f"""
            <div class='badge-card {locked}' style='margin-bottom:12px'>
                <span class='badge-icon'>{b['icon']}</span>
                <div class='badge-name'>{b['name']}</div>
                <div class='badge-desc'>{b['desc']}</div>
                <div style='font-size:10px;margin-top:5px;color:{status_color};font-weight:700;
                    font-family:"Rajdhani",sans-serif;letter-spacing:1px'>{status_text}</div>
            </div>""", unsafe_allow_html=True)

# ═══════════════ PROFILE ═════════════════════════════════════════
def page_profile():
    u = st.session_state.user
    st.markdown("<div class='section-header'>👤 MY PROFILE</div>", unsafe_allow_html=True)
    c1,c2 = st.columns([1,2])
    with c1:
        st.markdown(f"""<div style='font-size:80px;text-align:center;
            background:rgba(10,22,40,0.96);border-radius:20px;padding:20px;
            border:1px solid rgba(0,255,209,0.15);
            box-shadow:0 0 20px rgba(0,255,209,0.08)'>{u.get('avatar','🤖')}</div>""",
            unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div style='padding:10px 0;color:#E0F4FF'>
            <div style='font-family:"Orbitron",monospace;font-size:20px;font-weight:800;
                color:#00FFD1;text-shadow:0 0 12px rgba(0,255,209,0.4)'>{u['name']}</div>
            <div style='font-size:13px;color:#94B4CC;margin-top:6px'>
                {'🎒 Student' if u.get('role')=='student' else '👨‍👩‍👦 Parent' if u.get('role')=='parent'
                 else '👨‍🏫 Teacher' if u.get('role')=='teacher' else '🛡️ Admin'} · {u.get('grade','')}
            </div>
            <div style='font-size:12px;color:#4A6A80;margin-top:2px'>📧 {u['email']}</div>
            <div style='font-size:12px;color:#4A6A80;margin-top:2px'>📅 Joined {u.get('joined','')}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### ✏️ UPDATE PROFILE")
    with st.form("profile_form"):
        new_name  = st.text_input("Full Name", value=u.get("name",""))
        new_grade = st.selectbox("Default Grade", ["-- Select --"]+LEVELS,
                                 index=get_level_index(u.get("grade","Grade 6"))+1)
        cur_av_key = next((k for k,v in AVATARS.items() if v==u.get("avatar","🤖")), list(AVATARS.keys())[0])
        new_avatar = st.selectbox("Avatar", list(AVATARS.keys()),
                                  index=list(AVATARS.keys()).index(cur_av_key))
        st.markdown("#### 🔒 CHANGE PASSWORD")
        old_pw = st.text_input("Current Password", type="password")
        new_pw = st.text_input("New Password", type="password", placeholder="Leave blank to keep current")
        cnf_pw = st.text_input("Confirm New Password", type="password")
        if st.form_submit_button("💾 SAVE CHANGES", type="primary"):
            users = load_json(USERS_FILE); eu = users[u["email"]]
            if old_pw and eu["password"] != hash_pw(old_pw):
                st.error("Current password incorrect.")
            elif new_pw and new_pw != cnf_pw:
                st.error("New passwords don't match.")
            elif new_pw and len(new_pw) < 6:
                st.error("Min 6 characters.")
            else:
                if new_name.strip():           eu["name"]   = new_name.strip()
                if new_grade != "-- Select --": eu["grade"]  = new_grade
                eu["avatar"] = AVATARS[new_avatar]
                if new_pw:                     eu["password"] = hash_pw(new_pw)
                users[u["email"]] = eu; save_json(USERS_FILE, users)
                st.session_state.user = eu
                st.success("✅ Profile updated!"); time.sleep(0.5); st.rerun()


# ═══════════════ HOMEWORK ════════════════════════════════════════
def page_homework():
    u = st.session_state.user
    st.markdown("<div class='section-header'>📋 CREATE HOMEWORK</div>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background:rgba(0,255,209,0.04);border-radius:14px;padding:14px 18px;
        margin-bottom:20px;font-size:13px;color:#00FFD1;border:1px solid rgba(0,255,209,0.15)'>
        📝 <b>AI Homework Generator</b> — Fill details and let AI create a complete assignment
        with questions, answers, hints, marking guide, and learning objectives.
    </div>""", unsafe_allow_html=True)

    st.markdown("#### 📚 STEP 1 — SUBJECT & GRADE")
    c1, c2 = st.columns(2)
    with c1: hw_subject = st.selectbox("Subject", list(SUBJECTS.keys()), key="hw_subject")
    with c2:
        lvl_idx = get_level_index(u.get("grade", "Grade 6"))
        hw_grade = st.selectbox("Grade Level", LEVELS, index=lvl_idx, key="hw_grade")

    st.markdown("#### ✏️ STEP 2 — TOPIC & DESCRIPTION")
    hw_topic = st.text_input("Topic / Chapter", placeholder="e.g. Quadratic Equations, Photosynthesis...", key="hw_topic")
    hw_desc  = st.text_area("Description & Instructions", placeholder="Describe the assignment...", height=100, key="hw_desc")

    st.markdown("#### ⚙️ STEP 3 — SETTINGS")
    c3, c4, c5 = st.columns(3)
    with c3: hw_type = st.selectbox("Type", ["Mixed (MCQ + Short + Long)","MCQ Only","Short Answer","Long Answer / Essay","Problem Solving"], key="hw_type")
    with c4: hw_difficulty = st.selectbox("Difficulty", ["Easy","Medium","Hard","Mixed"], index=1, key="hw_diff")
    with c5: hw_num_q = st.selectbox("Questions", [5,8,10,12,15], index=1, key="hw_num_q")

    st.markdown("#### 📅 STEP 4 — DUE DATE")
    hw_due_days = st.slider("Due in how many days?", 1, 14, 3, key="hw_due_days")
    due_date = (datetime.date.today() + datetime.timedelta(days=hw_due_days)).isoformat()
    st.markdown(f"""<div style='background:rgba(0,255,209,0.06);border-radius:10px;padding:10px 16px;
        font-size:13px;color:#00FFD1;font-weight:700;display:inline-block;
        border:1px solid rgba(0,255,209,0.2);font-family:"Rajdhani",sans-serif;letter-spacing:.8px'>
        📅 DUE DATE: {due_date}</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    if st.button("🚀 GENERATE HOMEWORK WITH AI", use_container_width=True, type="primary", key="gen_hw_btn"):
        if not hw_topic.strip():
            st.error("⚠️ Please enter a topic in Step 2.")
        else:
            topic_str = hw_topic.strip(); desc_str = hw_desc.strip() if hw_desc.strip() else "Standard homework."
            with st.spinner(f"✨ Generating {hw_num_q} questions on '{topic_str}'..."):
                raw = call_ai(
                    [{"role":"user","content":
                      f"Create a complete homework for {hw_grade} {hw_subject} students in Pakistan. "
                      f"Topic: {topic_str}. Instructions: {desc_str}. Type: {hw_type}. "
                      f"Difficulty: {hw_difficulty}. Exactly {hw_num_q} questions. "
                      f'Return ONLY raw JSON: {{"title":"...","instructions":"...","learning_objectives":"...",'
                      f'"questions":[{{"number":1,"type":"MCQ","question":"...","marks":2,'
                      f'"options":["A.","B.","C.","D."],"answer":"...","hint":"..."}}],'
                      f'"total_marks":20,"marking_guide":"..."}}'}],
                    "Homework generator. Return ONLY valid JSON.", 3000
                )
            try:
                hw_data = json.loads(raw.replace("```json","").replace("```","").strip())
                homework = load_json(HOMEWORK_FILE)
                hw_id = f"hw_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{u['email'].split('@')[0]}"
                homework[hw_id] = {"id":hw_id,"created_by":u["email"],"creator_name":u["name"],
                    "subject":hw_subject,"grade":hw_grade,"topic":topic_str,"description":desc_str,
                    "type":hw_type,"difficulty":hw_difficulty,"due_date":due_date,
                    "created":datetime.date.today().isoformat(),"data":hw_data}
                save_json(HOMEWORK_FILE, homework)
                st.session_state["hw_preview"] = homework[hw_id]
                st.success("✅ Homework generated and saved!"); st.rerun()
            except Exception as e:
                st.error(f"⚠️ Could not parse AI response. ({e})")

    hw_prev = st.session_state.get("hw_preview")
    if hw_prev:
        data = hw_prev["data"]
        info = SUBJECTS.get(hw_prev["subject"], {"emoji":"📚","color":"#00FFD1"})
        col  = info["color"]
        st.markdown("---")
        st.markdown(f"""
        <div style='background:rgba(10,22,40,0.96);border:1px solid {col}33;
            border-radius:18px;padding:20px 22px;margin-bottom:18px'>
            <div style='font-size:20px;font-weight:900;color:{col};margin-bottom:10px;
                font-family:"Orbitron",monospace'>{info["emoji"]} {data.get("title",hw_prev["topic"])}</div>
            <div style='display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px'>
                <span style='background:{col}15;color:{col};padding:3px 10px;border-radius:6px;font-size:11px;font-weight:700;font-family:"Rajdhani",sans-serif'>{hw_prev["subject"]}</span>
                <span style='background:{col}15;color:{col};padding:3px 10px;border-radius:6px;font-size:11px;font-weight:700;font-family:"Rajdhani",sans-serif'>{hw_prev["grade"]}</span>
                <span style='background:{col}15;color:{col};padding:3px 10px;border-radius:6px;font-size:11px;font-weight:700;font-family:"Rajdhani",sans-serif'>{hw_prev["difficulty"]}</span>
                <span style='background:rgba(0,255,209,0.1);color:#00FFD1;padding:3px 10px;border-radius:6px;font-size:11px;font-weight:700;font-family:"Rajdhani",sans-serif'>📅 DUE: {hw_prev["due_date"]}</span>
            </div>
            <div style='font-size:13px;color:#94B4CC;margin-bottom:6px'><b style='color:#E0F4FF'>📋 Instructions:</b> {data.get("instructions","")[:250]}</div>
            <div style='font-size:12px;color:#4A6A80'><b style='color:#E0F4FF'>🎯 Objectives:</b> {data.get("learning_objectives","")}</div>
        </div>""", unsafe_allow_html=True)

        questions = data.get("questions",[])
        st.markdown(f"#### 📝 QUESTION PREVIEW ({min(5,len(questions))} of {len(questions)})")
        for i, q in enumerate(questions[:5]):
            with st.expander(f"Q{i+1}. {q['question'][:75]}... [{q.get('marks',0)} marks]"):
                if q.get("options"):
                    for opt in q["options"]:
                        st.markdown(f"""<div style='background:rgba(0,0,0,0.3);border-radius:8px;
                            padding:7px 12px;margin-bottom:4px;font-size:13px;color:#E0F4FF'>{opt}</div>""",
                            unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1: st.markdown(f"""<div style='background:rgba(0,255,209,0.06);border-radius:8px;
                    padding:8px 12px;font-size:12px;color:#00FFD1;margin-top:6px'>
                    ✅ <b>Answer:</b> {q.get("answer","")}</div>""", unsafe_allow_html=True)
                with col2:
                    if q.get("hint"): st.markdown(f"""<div style='background:rgba(255,215,0,0.06);
                        border-radius:8px;padding:8px 12px;font-size:12px;color:#FFD700;margin-top:6px'>
                        💡 <b>Hint:</b> {q.get("hint","")}</div>""", unsafe_allow_html=True)

        ba, bb = st.columns(2)
        with ba:
            if st.button("➕ CREATE ANOTHER", use_container_width=True, type="primary"):
                st.session_state["hw_preview"] = None; st.rerun()
        with bb:
            if st.button("📂 CLEAR PREVIEW", use_container_width=True):
                st.session_state["hw_preview"] = None; st.rerun()


# ═══════════════ ADMIN ═══════════════════════════════════════════
def page_admin():
    st.markdown("<div class='section-header orange'>🛡️ ADMIN DASHBOARD</div>", unsafe_allow_html=True)
    users    = load_json(USERS_FILE)
    homework = load_json(HOMEWORK_FILE)
    students = {e: d for e, d in users.items() if d.get("role") not in ("admin",)}
    all_hw   = list(homework.values())

    tab_perf, tab_hw = st.tabs(["📊 STUDENT ANALYTICS", "📋 HOMEWORK TRACKER"])

    with tab_perf:
        st.markdown("### 📊 PLATFORM OVERVIEW")
        total_students  = len(students)
        total_questions = sum(d.get("stats",{}).get("total",0) for d in students.values())
        total_quizzes   = sum(d.get("stats",{}).get("quizzes_done",0) for d in students.values())
        avg_streak      = sum(d.get("stats",{}).get("streak",0) for d in students.values()) / max(total_students,1)
        c1,c2,c3,c4 = st.columns(4)
        for col_w,icon,val,lbl,color in [
            (c1,"🎒",total_students,"Total Users","#60A5FA"),
            (c2,"❓",total_questions,"Questions","#FF2D78"),
            (c3,"📝",total_quizzes,"Quizzes","#A78BFA"),
            (c4,"🔥",f"{avg_streak:.1f}d","Avg Streak","#FFD700")]:
            with col_w:
                st.markdown(f"""
                <div style='background:rgba(10,22,40,0.96);border-radius:14px;padding:18px 14px;
                    text-align:center;box-shadow:0 8px 32px rgba(0,0,0,0.6);
                    border-top:3px solid {color};border:1px solid {color}22;'>
                    <div style='font-size:24px'>{icon}</div>
                    <div style='font-family:"Orbitron",monospace;font-size:24px;font-weight:900;
                        color:{color};text-shadow:0 0 12px {color}88'>{val}</div>
                    <div style='font-size:10px;color:#4A6A80;font-weight:700;font-family:"Rajdhani",sans-serif;letter-spacing:1px'>{lbl}</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("### 🏆 TOP 10 LEADERBOARD")
        sorted_users = sorted(students.items(),
            key=lambda x:(x[1].get("stats",{}).get("total",0)+x[1].get("stats",{}).get("quizzes_done",0)*3+x[1].get("stats",{}).get("streak",0)*2+len(x[1].get("badges",[]))*5),
            reverse=True)
        rank_icons = ["🥇","🥈","🥉"]+[f"{i+1}️⃣" for i in range(3,10)]
        max_score  = max((s.get("stats",{}).get("total",0)+s.get("stats",{}).get("quizzes_done",0)*3+s.get("stats",{}).get("streak",0)*2+len(s.get("badges",[]))*5 for _,s in sorted_users[:1]),default=1)

        for i,(email,ud) in enumerate(sorted_users[:10]):
            stats  = ud.get("stats",{}); qs=stats.get("total",0); quizzes=stats.get("quizzes_done",0)
            streak = stats.get("streak",0); badges = len(ud.get("badges",[]))
            score  = qs+quizzes*3+streak*2+badges*5
            bar_pct= min(int((score/max(max_score,1))*100),100)
            bar_col= "#FFD700" if i<3 else "#A78BFA"
            top_subj = max([(s,stats.get(s,0)) for s in SUBJECTS],key=lambda x:x[1],default=("—",0))
            st.markdown(f"""
            <div style='background:rgba(10,22,40,0.96);border-radius:14px;padding:14px 18px;
                margin-bottom:8px;box-shadow:0 8px 32px rgba(0,0,0,0.6);
                border-left:4px solid {"#FFD700" if i<3 else "rgba(0,255,209,0.12)"};color:#E0F4FF'>
                <div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px'>
                    <div style='display:flex;align-items:center;gap:12px'>
                        <span style='font-size:22px'>{rank_icons[i]}</span>
                        <div>
                            <div style='font-weight:800;font-size:14px'>{ud.get("avatar","🤖")} {ud.get("name","?")}</div>
                            <div style='font-size:11px;color:#4A6A80'>{ud.get("grade","")} · {email}</div>
                        </div>
                    </div>
                    <div style='display:flex;gap:16px;font-size:12px;flex-wrap:wrap'>
                        <div style='text-align:center'><div style='font-family:"Orbitron",monospace;font-size:15px;font-weight:900;color:#FF2D78'>{qs}</div><div style='color:#4A6A80'>Qs</div></div>
                        <div style='text-align:center'><div style='font-family:"Orbitron",monospace;font-size:15px;font-weight:900;color:#60A5FA'>{quizzes}</div><div style='color:#4A6A80'>Quiz</div></div>
                        <div style='text-align:center'><div style='font-family:"Orbitron",monospace;font-size:15px;font-weight:900;color:#FFD700'>{streak}d</div><div style='color:#4A6A80'>Strk</div></div>
                        <div style='text-align:center'><div style='font-family:"Orbitron",monospace;font-size:15px;font-weight:900;color:#A78BFA'>{badges}</div><div style='color:#4A6A80'>Bdg</div></div>
                    </div>
                </div>
                <div style='margin-top:10px'>
                    <div style='display:flex;justify-content:space-between;font-size:10px;color:#4A6A80;margin-bottom:4px;font-family:"Rajdhani",sans-serif;letter-spacing:.5px'>
                        <span>TOP: {SUBJECTS.get(top_subj[0],{}).get("emoji","")}&nbsp;{top_subj[0]} ({top_subj[1]})</span>
                        <span style='font-weight:800;color:{bar_col}'>SCORE: {score}</span>
                    </div>
                    <div style='background:rgba(0,0,0,0.4);border-radius:99px;height:8px;overflow:hidden'>
                        <div style='width:{bar_pct}%;height:8px;border-radius:99px;
                            background:linear-gradient(90deg,{bar_col},{bar_col}88);
                            box-shadow:0 0 8px {bar_col}88'></div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("### 📚 SUBJECT ENGAGEMENT")
        subject_totals = {s:sum(d.get("stats",{}).get(s,0) for d in students.values()) for s in SUBJECTS}
        grand_total = max(sum(subject_totals.values()),1)
        for subj,count in sorted(subject_totals.items(),key=lambda x:x[1],reverse=True):
            info=SUBJECTS[subj]; pct=int((count/grand_total)*100)
            st.markdown(f"""
            <div style='margin-bottom:12px'>
                <div style='display:flex;justify-content:space-between;font-size:13px;font-weight:700;margin-bottom:5px;color:#E0F4FF'>
                    <span>{info["emoji"]} {subj}</span>
                    <span style='color:{info["color"]}'>{count} · {pct}%</span>
                </div>
                <div style='background:rgba(0,0,0,0.4);border-radius:99px;height:10px;overflow:hidden'>
                    <div style='width:{max(pct,2)}%;height:10px;border-radius:99px;background:{info["color"]};box-shadow:0 0 8px {info["color"]}88'></div>
                </div>
            </div>""", unsafe_allow_html=True)

    with tab_hw:
        st.markdown("### 📋 HOMEWORK TRACKING")
        if not all_hw:
            st.info("📭 No homework assignments yet.")
        else:
            total_hw=len(all_hw); total_subs=sum(len(h.get("submissions",{})) for h in all_hw)
            c1,c2 = st.columns(2)
            with c1: st.metric("📋 Assignments", total_hw)
            with c2: st.metric("📬 Submissions", total_subs)
            st.markdown("---")
            for hw in sorted(all_hw,key=lambda x:x.get("created",""),reverse=True):
                info=SUBJECTS.get(hw["subject"],{"emoji":"📚","color":"#00FFD1"})
                col=info["color"]; subs=hw.get("submissions",{}); data=hw.get("data",{})
                hw_title=data.get("title",hw.get("topic",""))
                with st.expander(f"{info['emoji']} {hw_title[:45]} | {hw['subject']} {hw.get('grade','')} | {len(subs)} sub(s)"):
                    st.markdown(f"""
                    <div style='display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px'>
                        <span style='background:{col}15;color:{col};padding:3px 10px;border-radius:6px;font-size:11px;font-weight:700'>{hw["subject"]}</span>
                        <span style='background:{col}15;color:{col};padding:3px 10px;border-radius:6px;font-size:11px;font-weight:700'>{hw.get("grade","")}</span>
                        <span style='background:{col}15;color:{col};padding:3px 10px;border-radius:6px;font-size:11px;font-weight:700'>📅 {hw.get("due_date","")}</span>
                    </div>
                    <div style='font-size:12px;color:#94B4CC;margin-bottom:8px'>Topic: <b style='color:#E0F4FF'>{hw.get("topic","")}</b> · Created: {hw.get("created","")} · By: {hw.get("creator_name","?")}</div>""",
                    unsafe_allow_html=True)
                    if not subs: st.info("⏳ No submissions yet.")

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
