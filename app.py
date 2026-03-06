import streamlit as st
import json, hashlib, datetime, time, os, base64, re
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
    "👦 Boy":"👦","👧 Girl":"👧","👨 Dad":"👨","👩 Mom":"👩",
    "👨‍🏫 Teacher":"👨‍🏫","🧑‍🚀 Astronaut":"🧑‍🚀",
    "🧑‍🔬 Scientist":"🧑‍🔬","🧑‍🎨 Artist":"🧑‍🎨"
}

ESSAY_TYPES = [
    "Descriptive Essay","Argumentative Essay","Narrative Story",
    "Letter Writing","Report Writing","Summary Writing"
]

IMAGE_STYLES = {
    "📐 Educational Diagram": "a clean labeled educational diagram with arrows showing relationships, colorful sections, white background",
    "🎨 Colorful Cartoon":    "a bright fun cartoon illustration with cheerful colors suitable for children",
    "🔬 Scientific Illustration": "a detailed realistic scientific diagram like a textbook, accurately labeled",
    "🗺️ Mind Map":            "a colorful mind map with central topic, branches and sub-branches with connecting lines",
}

# ── XP LEVELS ──────────────────────────────────────────────────
XP_LEVELS = [
    {"name":"🌱 Beginner",   "min":0,    "color":"#6B7280"},
    {"name":"📖 Student",    "min":100,  "color":"#059669"},
    {"name":"🎓 Scholar",    "min":300,  "color":"#2563EB"},
    {"name":"🔬 Expert",     "min":700,  "color":"#7C3AED"},
    {"name":"🏆 Champion",   "min":1500, "color":"#E8472A"},
]

XP_REWARDS = {
    "question":   10,
    "quiz_q":     15,
    "quiz_done":  25,
    "essay":      30,
    "image":      20,
    "doc":        20,
    "flashcard":  10,
    "streak_7":   100,
    "daily_done": 50,
    "challenge":  40,
}

# ── DAILY CHALLENGES ───────────────────────────────────────────
DAILY_CHALLENGES = [
    {"id":"ask3",   "desc":"Ask 3 questions today",        "type":"questions","target":3,  "xp":40},
    {"id":"quiz1",  "desc":"Complete a full quiz",         "type":"quiz",     "target":1,  "xp":50},
    {"id":"essay1", "desc":"Write an essay",               "type":"essays",   "target":1,  "xp":60},
    {"id":"flash5", "desc":"Study 5 flashcards",           "type":"flashcard","target":5,  "xp":35},
    {"id":"multi",  "desc":"Study 2 different subjects",   "type":"subjects", "target":2,  "xp":45},
    {"id":"img1",   "desc":"Generate an educational image","type":"images",   "target":1,  "xp":30},
]

MOTIVATIONAL_QUOTES = [
    {"quote":"Education is the most powerful weapon you can use to change the world.", "author":"Nelson Mandela"},
    {"quote":"The beautiful thing about learning is that no one can take it away from you.", "author":"B.B. King"},
    {"quote":"Success is the sum of small efforts, repeated day in and day out.", "author":"Robert Collier"},
    {"quote":"The expert in anything was once a beginner.", "author":"Helen Hayes"},
    {"quote":"Believe you can and you're halfway there.", "author":"Theodore Roosevelt"},
    {"quote":"The more that you read, the more things you will know.", "author":"Dr. Seuss"},
    {"quote":"Study hard, for the well is deep, and our brains are shallow.", "author":"Richard Baxter"},
    {"quote":"Don't let what you cannot do interfere with what you can do.", "author":"John Wooden"},
    {"quote":"It does not matter how slowly you go as long as you do not stop.", "author":"Confucius"},
    {"quote":"Knowledge is power. Information is liberating.", "author":"Kofi Annan"},
]

BADGES = [
    {"id":"first_q",   "icon":"🌟","name":"First Step",       "desc":"Asked first question",    "req": lambda s: s.get("total",0)>=1},
    {"id":"curious",   "icon":"🧠","name":"Curious Mind",     "desc":"Asked 5 questions",       "req": lambda s: s.get("total",0)>=5},
    {"id":"seeker",    "icon":"📚","name":"Knowledge Seeker", "desc":"Asked 20 questions",      "req": lambda s: s.get("total",0)>=20},
    {"id":"maths",     "icon":"🔢","name":"Maths Master",     "desc":"10 Maths questions",      "req": lambda s: s.get("Maths",0)>=10},
    {"id":"physics",   "icon":"⚡","name":"Physics Pro",      "desc":"10 Physics questions",    "req": lambda s: s.get("Physics",0)>=10},
    {"id":"english",   "icon":"📖","name":"English Expert",   "desc":"10 English questions",    "req": lambda s: s.get("English",0)>=10},
    {"id":"urdu",      "icon":"🖊️","name":"Urdu Ustad",       "desc":"10 Urdu questions",       "req": lambda s: s.get("Urdu",0)>=10},
    {"id":"allround",  "icon":"🏅","name":"All-Rounder",      "desc":"Studied all 4 subjects",  "req": lambda s: all(s.get(x,0)>0 for x in ["Maths","Physics","English","Urdu"])},
    {"id":"artist",    "icon":"🎨","name":"Visual Learner",   "desc":"Generated 3 images",      "req": lambda s: s.get("images",0)>=3},
    {"id":"writer",    "icon":"✏️","name":"Essay Writer",     "desc":"Used Essay Helper",       "req": lambda s: s.get("essays",0)>=1},
    {"id":"streak7",   "icon":"🔥","name":"7-Day Streak",     "desc":"7 days in a row",         "req": lambda s: s.get("streak",0)>=7},
    {"id":"doc_read",  "icon":"📄","name":"Doc Reader",       "desc":"Uploaded a document",     "req": lambda s: s.get("docs",0)>=1},
    {"id":"flasher",   "icon":"🃏","name":"Flash Master",     "desc":"Used flashcards 5 times", "req": lambda s: s.get("flashcard",0)>=5},
    {"id":"champion",  "icon":"🏆","name":"Champion",         "desc":"Reached Champion level",  "req": lambda s: s.get("xp",0)>=1500},
    {"id":"planner",   "icon":"📅","name":"Organised",        "desc":"Added 3 homework tasks",  "req": lambda s: s.get("hw_tasks",0)>=3},
    {"id":"social",    "icon":"👥","name":"Team Player",      "desc":"Joined a study group",    "req": lambda s: s.get("groups",0)>=1},
]

QUICK_PROMPTS = {
    "Maths":   ["Explain fractions with examples","Solve: 2x + 5 = 15","What is Pythagoras theorem?","How to calculate percentage?"],
    "Physics": ["What are Newton's 3 laws?","How does electricity work?","What is gravity?","Difference between speed and velocity"],
    "English": ["How to write a good essay?","Explain past and present tense","What are nouns and verbs?","How to improve vocabulary?"],
    "Urdu":    ["اردو گرامر کی بنیادی باتیں","نظم اور نثر میں کیا فرق ہے؟","اچھا مضمون کیسے لکھیں؟","محاورے کیا ہوتے ہیں؟"],
}

# ─────────────────────────────────────────────────────────────────
# DATA FILES
# ─────────────────────────────────────────────────────────────────
USERS_FILE   = "users.json"
HISTORY_FILE = "history.json"
IMAGES_FILE  = "images.json"
GROUPS_FILE  = "groups.json"
HW_FILE      = "homework.json"

def load_json(fp):
    if os.path.exists(fp):
        with open(fp,"r",encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_json(fp, data):
    with open(fp,"w",encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()

def init_stats():
    return {"total":0,"Maths":0,"Physics":0,"English":0,"Urdu":0,
            "streak":0,"lastDate":"","images":0,"essays":0,"docs":0,
            "flashcard":0,"xp":0,"hw_tasks":0,"groups":0,
            "daily_questions":0,"daily_quiz":0,"daily_essays":0,
            "daily_flashcard":0,"daily_subjects":set(),"daily_images":0,
            "daily_date":"","challenges_done":[]}

# ─────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────
defaults = {
    "logged_in":False,"user":None,"page":"home",
    "subject":"Maths","level":"Class 5",
    "chat_messages":[],"session_id":None,
    "quiz":None,"essay_result":"",
    "trans_result":"","word_of_day":None,"wod_loaded":False,
    "dark_mode":False,"flashcards":[],"fc_index":0,"fc_flipped":False,
    "doc_result":"","quote_index":0,
}
for k,v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────────────────────────
# ANTHROPIC
# ─────────────────────────────────────────────────────────────────
@st.cache_resource
def get_client():
    key = st.secrets.get("ANTHROPIC_API_KEY","") or os.environ.get("ANTHROPIC_API_KEY","")
    return Anthropic(api_key=key) if key else None

client = get_client()

def call_ai(messages, system, max_tokens=1200):
    if not client: return "⚠️ API key not configured."
    try:
        r = client.messages.create(model="claude-haiku-4-5-20251001",max_tokens=max_tokens,system=system,messages=messages)
        return r.content[0].text
    except Exception as e: return f"⚠️ Error: {e}"

def call_ai_with_doc(messages, system, doc_content, max_tokens=1500):
    if not client: return "⚠️ API key not configured."
    try:
        aug = system + f"\n\nUploaded document:\n\n{doc_content[:8000]}"
        r = client.messages.create(model="claude-haiku-4-5-20251001",max_tokens=max_tokens,system=aug,messages=messages)
        return r.content[0].text
    except Exception as e: return f"⚠️ Error: {e}"

def call_ai_svg(messages, system):
    if not client: return "⚠️ API key not configured."
    try:
        r = client.messages.create(model="claude-haiku-4-5-20251001",max_tokens=4000,system=system,messages=messages)
        return r.content[0].text
    except Exception as e: return f"ERROR: {e}"

# ─────────────────────────────────────────────────────────────────
# XP & LEVELS
# ─────────────────────────────────────────────────────────────────
def get_level(xp):
    lvl = XP_LEVELS[0]
    for l in XP_LEVELS:
        if xp >= l["min"]: lvl = l
    return lvl

def get_next_level(xp):
    for i, l in enumerate(XP_LEVELS):
        if xp < l["min"]: return l, i
    return None, len(XP_LEVELS)

def add_xp(amount, reason=""):
    users = load_json(USERS_FILE)
    email = st.session_state.user["email"]
    u = users.get(email, st.session_state.user)
    s = u.get("stats", init_stats())
    old_xp = s.get("xp", 0)
    s["xp"] = old_xp + amount
    old_level = get_level(old_xp)["name"]
    new_level = get_level(s["xp"])["name"]
    u["stats"] = s
    users[email] = u
    save_json(USERS_FILE, users)
    st.session_state.user = u
    st.toast(f"⚡ +{amount} XP{' — ' + reason if reason else ''}!", icon="✨")
    if old_level != new_level:
        st.toast(f"🎉 LEVEL UP! You are now {new_level}!", icon="🏆")

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

def bump_stats(subject_field=None, extra_field=None, xp_key=None):
    users = load_json(USERS_FILE)
    email = st.session_state.user["email"]
    u = users.get(email, st.session_state.user)
    s = u.get("stats", init_stats())
    s["total"] = s.get("total",0) + 1
    if subject_field: s[subject_field] = s.get(subject_field,0) + 1
    if extra_field:   s[extra_field]   = s.get(extra_field,0) + 1
    today = datetime.date.today().isoformat()
    yest  = (datetime.date.today()-datetime.timedelta(days=1)).isoformat()
    if s.get("lastDate","") == today: pass
    elif s.get("lastDate","") == yest: s["streak"] = s.get("streak",0)+1
    else: s["streak"] = 1
    s["lastDate"] = today
    # daily tracking
    if s.get("daily_date","") != today:
        s["daily_date"] = today
        s["daily_questions"] = 0; s["daily_quiz"] = 0
        s["daily_essays"] = 0; s["daily_flashcard"] = 0
        s["daily_images"] = 0; s["daily_subjects"] = []
        s["challenges_done"] = []
    if subject_field in SUBJECTS:
        daily_subs = s.get("daily_subjects",[])
        if subject_field not in daily_subs:
            daily_subs.append(subject_field)
            s["daily_subjects"] = daily_subs
        s["daily_questions"] = s.get("daily_questions",0)+1
    if extra_field == "essays":   s["daily_essays"]   = s.get("daily_essays",0)+1
    if extra_field == "images":   s["daily_images"]   = s.get("daily_images",0)+1
    if extra_field == "flashcard":s["daily_flashcard"]= s.get("daily_flashcard",0)+1
    if extra_field == "docs":     s["daily_docs"]     = s.get("daily_docs",0)+1
    # streak bonus
    if s.get("streak",0) == 7 and "streak7_bonus" not in s:
        s["streak7_bonus"] = True
        s["xp"] = s.get("xp",0) + XP_REWARDS["streak_7"]
        st.toast("🔥 7-Day Streak Bonus! +100 XP!", icon="🎉")
    u["stats"] = s
    u, new_badges = check_badges(u)
    users[email] = u
    save_json(USERS_FILE, users)
    st.session_state.user = u
    for b in new_badges:
        st.toast(f"🏆 Badge: {b['icon']} {b['name']}!", icon="🎉")
    if xp_key and xp_key in XP_REWARDS:
        add_xp(XP_REWARDS[xp_key])

def check_daily_challenges():
    """Check and award completed daily challenges"""
    u = st.session_state.user
    s = u.get("stats", {})
    today = datetime.date.today().isoformat()
    if s.get("daily_date","") != today: return
    done = s.get("challenges_done",[])
    for ch in DAILY_CHALLENGES:
        if ch["id"] in done: continue
        completed = False
        if ch["type"] == "questions"  and s.get("daily_questions",0)  >= ch["target"]: completed = True
        if ch["type"] == "quiz"       and s.get("daily_quiz",0)        >= ch["target"]: completed = True
        if ch["type"] == "essays"     and s.get("daily_essays",0)      >= ch["target"]: completed = True
        if ch["type"] == "flashcard"  and s.get("daily_flashcard",0)   >= ch["target"]: completed = True
        if ch["type"] == "images"     and s.get("daily_images",0)      >= ch["target"]: completed = True
        if ch["type"] == "subjects"   and len(s.get("daily_subjects",[]))>= ch["target"]: completed = True
        if completed:
            done.append(ch["id"])
            users = load_json(USERS_FILE)
            eu = users.get(u["email"], u)
            eu["stats"]["challenges_done"] = done
            eu["stats"]["xp"] = eu["stats"].get("xp",0) + ch["xp"]
            users[u["email"]] = eu
            save_json(USERS_FILE, users)
            st.session_state.user = eu
            st.toast(f"🎯 Daily Challenge Done: {ch['desc']} +{ch['xp']} XP!", icon="🎉")

# ─────────────────────────────────────────────────────────────────
# THEME
# ─────────────────────────────────────────────────────────────────
def get_theme():
    if st.session_state.dark_mode:
        return {"bg":"#0F0F1A","card":"#1A1A2E","card_border":"#2D2D4A",
                "text":"#FFFFFF","text_muted":"#AAAACC","sidebar_bg":"#070710",
                "sidebar_text":"#FFFFFF","input_bg":"#1A1A2E",
                "msg_bot_bg":"#1A1A2E","msg_bot_text":"#FFFFFF","msg_bot_border":"#2D2D4A","page_bg":"#0F0F1A"}
    return {"bg":"#F8F9FC","card":"#FFFFFF","card_border":"#F0F0F5",
            "text":"#1A1A2E","text_muted":"#666688","sidebar_bg":"#1A1A2E",
            "sidebar_text":"#FFFFFF","input_bg":"#FFFFFF",
            "msg_bot_bg":"#FFFFFF","msg_bot_text":"#1A1A2E","msg_bot_border":"#F0F0F5","page_bg":"#F8F9FC"}

def inject_css():
    t = get_theme()
    dm = st.session_state.dark_mode
    st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Baloo+2:wght@600;700;800&display=swap');
html,body,[class*="css"]{{font-family:'Nunito',sans-serif!important;background-color:{t['page_bg']}!important;color:{t['text']}!important;}}
.stApp{{background-color:{t['page_bg']}!important;}}
.main .block-container{{padding-top:.5rem;padding-bottom:2rem;max-width:960px;background-color:{t['page_bg']};}}
#MainMenu,footer,header{{visibility:hidden;}}
[data-testid="stSidebar"]{{background-color:{t['sidebar_bg']}!important;border-right:1px solid rgba(255,255,255,.08);min-width:225px!important;}}
[data-testid="stSidebar"] *{{color:{t['sidebar_text']}!important;}}
[data-testid="stSidebar"] .stButton>button{{background-color:rgba(255,255,255,.07)!important;color:#FFF!important;border:1px solid rgba(255,255,255,.15)!important;border-radius:10px!important;font-weight:700!important;font-size:13px!important;padding:8px 12px!important;margin-bottom:3px!important;transition:all .2s;text-align:left!important;}}
[data-testid="stSidebar"] .stButton>button:hover{{background-color:rgba(232,71,42,.35)!important;border-color:#E8472A!important;transform:translateX(2px);}}
[data-testid="stSidebar"] .stButton>button[kind="primary"]{{background:linear-gradient(135deg,#E8472A,#C1391F)!important;border-color:#E8472A!important;box-shadow:0 3px 12px rgba(232,71,42,.4)!important;}}
.msg-user{{background:linear-gradient(135deg,#E8472A,#C1391F);color:#fff;border-radius:18px 18px 4px 18px;padding:12px 16px;margin:4px 0 4px 60px;font-size:14px;line-height:1.65;}}
.msg-bot{{background:{t['msg_bot_bg']};color:{t['msg_bot_text']};border-radius:18px 18px 18px 4px;padding:12px 16px;margin:4px 60px 4px 0;font-size:14px;line-height:1.7;box-shadow:0 2px 10px rgba(0,0,0,.07);border:1px solid {t['msg_bot_border']};}}
.msg-lbl{{font-size:11px;color:#bbb;margin-bottom:2px;}}
.msg-lbl-r{{text-align:right;}}
.stat-card{{background:{t['card']};border-radius:14px;padding:16px;text-align:center;box-shadow:0 2px 10px rgba(0,0,0,.05);border:1px solid {t['card_border']};}}
.stat-num{{font-size:28px;font-weight:900;color:{t['text']};}}
.stat-lbl{{font-size:11px;color:{t['text_muted']};margin-top:3px;}}
.badge-card{{background:{'linear-gradient(135deg,#2A2A40,#1E1E35)' if dm else 'linear-gradient(135deg,#FFF8E7,#FFFBF0)'};border:1.5px solid {'#5B4A15' if dm else '#F5CC4A'};border-radius:12px;padding:12px 10px;text-align:center;}}
.badge-locked{{opacity:.3;filter:grayscale(1);}}
.badge-icon{{font-size:28px;display:block;}}
.badge-name{{font-size:12px;font-weight:800;color:{'#F5CC4A' if dm else '#A07820'};margin-top:4px;}}
.badge-desc{{font-size:10px;color:{t['text_muted']};margin-top:2px;}}
.prog-bar{{background:{'#2D2D4A' if dm else '#F0F0F5'};border-radius:99px;height:10px;overflow:hidden;margin-bottom:4px;}}
.prog-fill{{height:100%;border-radius:99px;transition:width .4s;}}
.xp-bar{{background:{'#2D2D4A' if dm else '#E5E7EB'};border-radius:99px;height:14px;overflow:hidden;}}
.xp-fill{{height:100%;border-radius:99px;background:linear-gradient(90deg,#F59E0B,#EF4444);transition:width .4s;}}
.word-card{{background:linear-gradient(135deg,#1A1A2E,#2D2D4A);border-radius:16px;padding:18px 20px;margin-bottom:14px;color:#fff;}}
.reminder{{background:{'#2A2500' if dm else '#FFFBF0'};border:1.5px solid #F5CC4A;border-radius:12px;padding:12px 16px;margin-bottom:14px;font-size:13px;color:{t['text']};}}
.challenge-card{{background:{t['card']};border-radius:12px;padding:14px 16px;border:1.5px solid {t['card_border']};margin-bottom:8px;}}
.challenge-done{{border-color:#059669!important;background:{'#0D2A0D' if dm else '#F0FDF4'}!important;}}
.trophy-card{{background:linear-gradient(135deg,#1A1A2E,#2D2D4A);border-radius:16px;padding:20px;text-align:center;border:2px solid #F5CC4A;}}
.quote-card{{background:linear-gradient(135deg,#2563EB22,#7C3AED22);border:1px solid {'#3B5BDB' if dm else '#C3D0FF'};border-radius:14px;padding:16px 20px;margin-bottom:14px;}}
.fc-card{{background:{t['card']};border-radius:20px;padding:30px 24px;text-align:center;min-height:200px;display:flex;flex-direction:column;justify-content:center;box-shadow:0 4px 20px rgba(0,0,0,.1);border:2px solid {t['card_border']};cursor:pointer;transition:transform .2s;}}
.fc-card:hover{{transform:scale(1.01);}}
.hw-card{{background:{t['card']};border-radius:12px;padding:14px 16px;border-left:4px solid #E8472A;margin-bottom:8px;box-shadow:0 2px 8px rgba(0,0,0,.05);}}
.hw-done{{border-left-color:#059669!important;opacity:.6;}}
.group-card{{background:{t['card']};border-radius:14px;padding:16px;border:1px solid {t['card_border']};margin-bottom:10px;}}
.leaderboard-row{{background:{t['card']};border-radius:12px;padding:12px 16px;margin-bottom:6px;border:1px solid {t['card_border']};display:flex;align-items:center;gap:12px;}}
.countdown-card{{background:linear-gradient(135deg,#E8472A,#7C3AED);border-radius:18px;padding:20px;color:#fff;text-align:center;margin-bottom:12px;}}
[data-testid="stFileUploader"]{{background:{'#1A1A2E' if dm else '#F8F9FC'}!important;border-radius:12px!important;border:2px dashed {'#4A4A6A' if dm else '#D0D0E0'}!important;}}
.stButton>button{{border-radius:12px!important;font-family:'Nunito',sans-serif!important;font-weight:700!important;transition:all .2s;}}
.stTextInput>div>div>input,.stSelectbox>div>div>div,.stTextArea>div>div>textarea{{border-radius:10px!important;font-family:'Nunito',sans-serif!important;background-color:{t['input_bg']}!important;color:{t['text']}!important;}}
.stTabs [data-baseweb="tab-list"]{{background:{'#1A1A2E' if dm else '#F0F0F5'}!important;border-radius:12px;padding:4px;}}
.stTabs [data-baseweb="tab"]{{color:{t['text']}!important;border-radius:8px!important;}}
[data-testid="stMetricValue"]{{color:{t['text']}!important;}}
[data-testid="stMetricLabel"]{{color:{t['text_muted']}!important;}}
.streamlit-expanderHeader{{background:{t['card']}!important;color:{t['text']}!important;border-radius:10px!important;}}
div[data-testid="column"]{{padding:4px!important;}}
@media(max-width:768px){{.main .block-container{{padding:.5rem .8rem 2rem!important;max-width:100%!important;}}.msg-user{{margin-left:10px!important;}}.msg-bot{{margin-right:10px!important;}}}}
</style>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────────
def page_auth():
    inject_css()
    t = get_theme()
    _, col, _ = st.columns([1,2,1])
    with col:
        st.markdown(f"""
        <div style='text-align:center;padding:24px 0 16px'>
            <div style='font-size:56px'>📚</div>
            <h1 style='font-family:"Baloo 2",cursive;font-size:28px;font-weight:800;color:{t["text"]};margin:6px 0 2px'>HomeWork Helper</h1>
            <p style='color:{t["text_muted"]};font-size:13px'>🇵🇰 Pakistan's Smart Study Companion</p>
            <p style='color:{t["text_muted"]};font-size:12px'>Classes 1–8 • O Level • A Level</p>
        </div>""", unsafe_allow_html=True)
        tab_login, tab_signup = st.tabs(["🔑  Login","✨  Sign Up"])
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
                        st.success("Welcome back! 🎉"); time.sleep(.5); st.rerun()
                    else:
                        st.error("⚠️ Incorrect email or password.")
        with tab_signup:
            with st.form("signup_form"):
                name   = st.text_input("👤 Full Name", placeholder="Ahmed Khan")
                email2 = st.text_input("📧 Email", placeholder="you@example.com")
                role   = st.selectbox("👥 I am a", ["Student 🎒","Parent 👨‍👩‍👦"])
                avatar = st.selectbox("🧑 Choose Avatar", list(AVATARS.keys()))
                grade  = st.selectbox("🏫 Class", ["-- Select --"]+LEVELS)
                pw     = st.text_input("🔒 Password", type="password", placeholder="Min 6 chars")
                pw2    = st.text_input("🔒 Confirm Password", type="password")
                if st.form_submit_button("Create Account →", use_container_width=True, type="primary"):
                    users = load_json(USERS_FILE)
                    if not name or not email2 or not pw: st.error("Fill all fields.")
                    elif len(pw)<6: st.error("Password min 6 chars.")
                    elif pw!=pw2: st.error("Passwords don't match.")
                    elif email2 in users: st.error("Email already registered.")
                    else:
                        new_user = {"name":name.strip(),"email":email2.strip(),"password":hash_pw(pw),
                            "role":"student" if "Student" in role else "parent",
                            "avatar":AVATARS[avatar],"grade":grade if grade!="-- Select --" else "",
                            "joined":datetime.date.today().isoformat(),"stats":init_stats(),"badges":[]}
                        users[email2] = new_user
                        save_json(USERS_FILE, users)
                        st.session_state.logged_in = True
                        st.session_state.user = new_user
                        st.success("Welcome aboard! 🎉"); time.sleep(.5); st.rerun()

# ─────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────
def render_sidebar():
    u = st.session_state.user
    stats = u.get("stats",{})
    xp = stats.get("xp",0)
    lvl = get_level(xp)
    next_lvl, _ = get_next_level(xp)
    xp_pct = 0
    if next_lvl:
        span = next_lvl["min"] - lvl["min"]
        prog = xp - lvl["min"]
        xp_pct = min(int((prog/max(span,1))*100), 100)
    with st.sidebar:
        ca, cb = st.columns([3,1])
        with ca: st.markdown(f"<div style='font-size:11px;font-weight:800;opacity:.6;padding-top:8px'>🌙 Dark Mode</div>", unsafe_allow_html=True)
        with cb:
            dark = st.toggle("", value=st.session_state.dark_mode, key="dark_toggle", label_visibility="collapsed")
            if dark != st.session_state.dark_mode:
                st.session_state.dark_mode = dark; st.rerun()

        st.markdown(f"""
        <div style='padding:12px 8px;border-bottom:1px solid rgba(255,255,255,.15);margin-bottom:12px'>
            <div style='font-size:44px;line-height:1;margin-bottom:6px'>{u.get('avatar','👦')}</div>
            <div style='font-weight:800;font-size:15px;color:#FFF'>{u['name']}</div>
            <div style='font-size:11px;color:rgba(255,255,255,.55);margin-top:2px'>{'🎒 Student' if u.get('role')=='student' else '👨‍👩‍👦 Parent'} • {u.get('grade','')}</div>
            <div style='margin-top:8px;font-size:12px;font-weight:800;color:{lvl["color"]}'>{lvl["name"]}</div>
            <div style='font-size:11px;color:rgba(255,255,255,.5);margin-bottom:4px'>⚡ {xp} XP {f"→ {next_lvl['min']} for {next_lvl['name']}" if next_lvl else "MAX LEVEL"}</div>
            <div class='xp-bar'><div class='xp-fill' style='width:{xp_pct}%'></div></div>
            <div style='display:flex;gap:10px;margin-top:8px;flex-wrap:wrap'>
                <span style='font-size:11px;color:rgba(255,255,255,.55)'>❓ <b style='color:#FFD700'>{stats.get('total',0)}</b></span>
                <span style='font-size:11px;color:rgba(255,255,255,.55)'>🏆 <b style='color:#FFD700'>{len(u.get('badges',[]))}</b></span>
                <span style='font-size:11px;color:rgba(255,255,255,.55)'>🔥 <b style='color:#FFD700'>{stats.get('streak',0)}d</b></span>
            </div>
        </div>""", unsafe_allow_html=True)

        nav = [
            ("🏠","Home","home"),("💬","Chat Tutor","chat"),("📄","Doc Q&A","docqa"),
            ("📝","Practice Quiz","quiz"),("🃏","Flashcards","flashcards"),
            ("🎨","Image Generator","image"),("✏️","Essay Helper","essay"),
            ("🔧","Study Tools","tools"),("📅","Homework Planner","homework"),
            ("⏳","Exam Countdown","exams"),("🎯","Daily Challenges","challenges"),
            ("👥","Study Groups","groups"),("🏆","Leaderboard","leaderboard"),
            ("🏅","Trophy Cabinet","trophies"),("📊","My Progress","progress"),
            ("🕐","Chat History","history"),("🎖️","Badges","badges"),
            ("👤","Profile","profile"),
        ]
        if u.get("role") == "parent":
            nav.append(("👨‍👩‍👦","Parent Dashboard","parent"))

        for icon, label, key in nav:
            active = st.session_state.page == key
            if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True,
                         type="primary" if active else "secondary"):
                st.session_state.page = key; st.rerun()

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        if st.button("🚪  Logout", use_container_width=True):
            for k in list(st.session_state.keys()): del st.session_state[k]
            st.rerun()

# ─────────────────────────────────────────────────────────────────
# HOME
# ─────────────────────────────────────────────────────────────────
def page_home():
    t   = get_theme()
    u   = st.session_state.user
    stats = u.get("stats",{})
    sub = st.session_state.subject
    col_hex = SUBJECTS[sub]["color"]
    h   = datetime.datetime.now().hour
    greet = "Good morning" if h<12 else "Good afternoon" if h<17 else "Good evening"
    xp  = stats.get("xp",0)
    lvl = get_level(xp)

    # Motivational quote of the day
    q_idx = (datetime.date.today().toordinal()) % len(MOTIVATIONAL_QUOTES)
    quote = MOTIVATIONAL_QUOTES[q_idx]
    st.markdown(f"""
    <div class='quote-card'>
        <div style='font-size:11px;font-weight:800;opacity:.6;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px'>💭 Daily Motivation</div>
        <div style='font-size:14px;font-style:italic;line-height:1.6;color:{t["text"]}'>&ldquo;{quote["quote"]}&rdquo;</div>
        <div style='font-size:12px;color:{t["text_muted"]};margin-top:6px'>— {quote["author"]}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"""
    <div style='background:linear-gradient(135deg,{col_hex}dd,{col_hex}88);border-radius:18px;padding:18px 22px;margin-bottom:14px;color:#fff'>
        <div style='display:flex;align-items:center;gap:16px'>
            <div style='font-size:48px;line-height:1'>{u.get('avatar','👦')}</div>
            <div style='flex:1'>
                <div style='font-family:"Baloo 2",cursive;font-size:20px;font-weight:800'>{greet}, {u['name'].split()[0]}! 👋</div>
                <div style='font-size:12px;opacity:.9;margin-top:2px'>Ready to learn? 🚀</div>
                <div style='display:flex;align-items:center;gap:10px;margin-top:8px;flex-wrap:wrap'>
                    <span style='background:rgba(0,0,0,.2);border-radius:20px;padding:3px 10px;font-size:12px;font-weight:800'>{lvl["name"]}</span>
                    <span style='background:rgba(0,0,0,.2);border-radius:20px;padding:3px 10px;font-size:12px'>⚡ {xp} XP</span>
                    <span style='background:rgba(0,0,0,.2);border-radius:20px;padding:3px 10px;font-size:12px'>🔥 {stats.get('streak',0)} day streak</span>
                </div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    if stats.get("lastDate","") != datetime.date.today().isoformat():
        st.markdown("<div class='reminder'>🔔 <b>Daily Reminder:</b> You haven't studied today! Even 15 minutes makes a difference 💪</div>", unsafe_allow_html=True)

    # Word of the Day
    if not st.session_state.wod_loaded:
        with st.spinner("Loading Word of the Day..."):
            grade = u.get("grade","Class 5")
            raw = call_ai([{"role":"user","content":
                f"Give ONE interesting English word suitable for {grade} students in Pakistan. "
                f'Return ONLY JSON: {{"word":"...","urdu":"...","meaning":"...","example":"...","tip":"..."}}'}],
                "Vocabulary teacher. Return ONLY valid JSON. No markdown.")
            try:
                clean = raw.replace("```json","").replace("```","").strip()
                st.session_state.word_of_day = json.loads(clean)
            except:
                st.session_state.word_of_day = {"word":"Perseverance","urdu":"ثابت قدمی","meaning":"Continued effort despite difficulties","example":"Success comes to those with perseverance.","tip":"Use this word in your next essay!"}
            st.session_state.wod_loaded = True

    if st.session_state.word_of_day:
        w = st.session_state.word_of_day
        st.markdown(f"""
        <div class='word-card'>
            <div style='font-size:11px;font-weight:800;opacity:.5;text-transform:uppercase;letter-spacing:1px;margin-bottom:8px'>📖 Word of the Day</div>
            <div style='display:flex;align-items:baseline;gap:12px;flex-wrap:wrap'>
                <span style='font-family:"Baloo 2",cursive;font-size:26px;font-weight:800;color:#FFD700'>{w.get('word','')}</span>
                <span style='font-size:13px;opacity:.65'>— {w.get('urdu','')}</span>
            </div>
            <div style='font-size:13px;margin-top:6px;opacity:.9'>{w.get('meaning','')}</div>
            <div style='font-size:12px;margin-top:4px;opacity:.65;font-style:italic'>"{w.get('example','')}"</div>
            <div style='font-size:11px;margin-top:8px;background:rgba(255,255,255,.1);border-radius:8px;padding:6px 10px'>💡 {w.get('tip','')}</div>
        </div>""", unsafe_allow_html=True)

    # Stats row
    c1,c2,c3,c4,c5 = st.columns(5)
    for col_obj,ico,val,lbl in [
        (c1,"❓",stats.get("total",0),"Questions"),
        (c2,"⚡",xp,"XP Points"),
        (c3,"🏆",len(u.get("badges",[])),"Badges"),
        (c4,"🔥",stats.get("streak",0),"Streak"),
        (c5,"🎨",stats.get("images",0),"Images"),
    ]:
        with col_obj:
            st.markdown(f"<div class='stat-card'><div class='stat-num'>{val}</div><div class='stat-lbl'>{ico} {lbl}</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color:{t['text']}'>📚 Start Learning</h3>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    for col_obj,(name,info) in zip([c1,c2,c3,c4], SUBJECTS.items()):
        cnt = stats.get(name,0)
        with col_obj:
            st.markdown(f"""<div style='background:{info["color"]}18;border:2px solid {info["color"]};border-radius:14px;padding:14px 10px;text-align:center;margin-bottom:8px'>
                <div style='font-size:28px'>{info["emoji"]}</div>
                <div style='font-weight:800;font-size:13px;color:{info["color"]}'>{name}</div>
                <div style='font-size:10px;color:{t["text_muted"]};margin-top:2px'>{cnt} questions</div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"Study {name}", key=f"home_{name}", use_container_width=True):
                st.session_state.subject=name; st.session_state.page="chat"
                st.session_state.chat_messages=[]; st.session_state.session_id=None; st.rerun()

# ─────────────────────────────────────────────────────────────────
# CHAT TUTOR
# ─────────────────────────────────────────────────────────────────
def build_system(u, sub, lvl):
    return f"""You are Ustad, a warm and encouraging homework tutor for Pakistani students.
Student: {u['name']} | Role: {'Parent' if u.get('role')=='parent' else 'Student'} | Class: {lvl} | Subject: {sub}
- Adapt complexity to {lvl}: Class 1-3=very simple+emojis; Class 4-5=simple+examples; Class 6-8=structured; O Level=exam-focused; A Level=university depth
{f'- Reply in Urdu script. Use English only for technical terms.' if sub=='Urdu' else ''}
{f'- User is a parent. Explain how to help their child.' if u.get("role")=="parent" else ''}
- For Maths/Physics: ALWAYS show step-by-step working. Use Pakistani curriculum (FBISE, Cambridge Pakistan).
- Be warm, positive, end with encouragement or follow-up question."""

def save_chat_session(sub, lvl):
    hist  = load_json(HISTORY_FILE)
    email = st.session_state.user["email"]
    if email not in hist: hist[email] = []
    sid = st.session_state.session_id or datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    st.session_state.session_id = sid
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    ex = next((s for s in hist[email] if s["id"]==sid), None)
    if ex: ex["messages"]=st.session_state.chat_messages; ex["updated"]=now
    else: hist[email].append({"id":sid,"subject":sub,"level":lvl,"messages":st.session_state.chat_messages,"created":now,"updated":now})
    save_json(HISTORY_FILE, hist)

def page_chat():
    t = get_theme()
    u = st.session_state.user
    c1,c2 = st.columns(2)
    with c1: sub = st.selectbox("📚 Subject", list(SUBJECTS.keys()), index=list(SUBJECTS.keys()).index(st.session_state.subject))
    with c2:
        lvl_idx = LEVELS.index(u.get("grade","Class 5")) if u.get("grade","") in LEVELS else 4
        lvl = st.selectbox("🏫 Class", LEVELS, index=lvl_idx)
    st.session_state.subject = sub
    if st.button("🆕 New Chat", type="secondary"):
        st.session_state.chat_messages=[]; st.session_state.session_id=None; st.rerun()
    st.markdown(f"<div style='font-size:11px;font-weight:800;color:{t['text_muted']};text-transform:uppercase;letter-spacing:1px;margin:10px 0 6px'>⚡ Quick Questions</div>", unsafe_allow_html=True)
    qc = st.columns(2)
    for i,p in enumerate(QUICK_PROMPTS.get(sub,[])):
        with qc[i%2]:
            if st.button(p, key=f"qp{i}", use_container_width=True):
                st.session_state.chat_messages.append({"role":"user","content":p})
                with st.spinner("Ustad is thinking... 🤔"):
                    reply = call_ai(st.session_state.chat_messages, build_system(u,sub,lvl))
                st.session_state.chat_messages.append({"role":"assistant","content":reply})
                bump_stats(sub, xp_key="question"); save_chat_session(sub,lvl); check_daily_challenges(); st.rerun()
    if not st.session_state.chat_messages:
        st.info(f"👋 Assalam-o-Alaikum {u['name'].split()[0]}! I'm Ustad, your {sub} tutor. Ask me anything!")
    for m in st.session_state.chat_messages:
        if m["role"]=="user":
            st.markdown(f"<div class='msg-lbl msg-lbl-r'>You</div><div class='msg-user'>{m['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='msg-lbl'>🎓 Ustad</div><div class='msg-bot'>{m['content']}</div>", unsafe_allow_html=True)
    with st.form("chat_form", clear_on_submit=True):
        ph = "یہاں سوال لکھیں..." if sub=="Urdu" else f"Ask your {sub} question here..."
        txt = st.text_area("Q", placeholder=ph, height=80, label_visibility="collapsed")
        if st.form_submit_button("📤 Send", use_container_width=True, type="primary") and txt.strip():
            st.session_state.chat_messages.append({"role":"user","content":txt.strip()})
            with st.spinner("Ustad is thinking... 🤔"):
                reply = call_ai(st.session_state.chat_messages, build_system(u,sub,lvl))
            st.session_state.chat_messages.append({"role":"assistant","content":reply})
            bump_stats(sub, xp_key="question"); save_chat_session(sub,lvl); check_daily_challenges(); st.rerun()

# ─────────────────────────────────────────────────────────────────
# 🃏 FLASHCARDS
# ─────────────────────────────────────────────────────────────────
def page_flashcards():
    t = get_theme(); u = st.session_state.user
    st.markdown(f"<h3 style='color:{t['text']}'>🃏 AI Flashcards</h3>", unsafe_allow_html=True)
    st.markdown(f"""<div style='background:{"#1A2A1A" if st.session_state.dark_mode else "#F0FDF4"};border:1.5px solid #059669;border-radius:12px;padding:12px 16px;margin-bottom:16px;font-size:13px;color:{"#6EE7B7" if st.session_state.dark_mode else "#065F46"}'>
        🃏 Enter any topic and get <b>AI-generated flashcards</b> to flip through for quick revision!</div>""", unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1: sub = st.selectbox("📚 Subject", list(SUBJECTS.keys()), key="fc_sub")
    with c2:
        lvl_idx = LEVELS.index(u.get("grade","Class 5")) if u.get("grade","") in LEVELS else 4
        lvl = st.selectbox("🏫 Class", LEVELS, index=lvl_idx, key="fc_lvl")
    topic = st.text_input("📝 Topic", placeholder="e.g. Newton's Laws, Algebra, Parts of Speech...")
    if st.button("✨ Generate 10 Flashcards", use_container_width=True, type="primary"):
        if not topic.strip(): st.warning("Enter a topic first!"); return
        with st.spinner("Creating flashcards... 🃏"):
            raw = call_ai([{"role":"user","content":
                f"Create 10 flashcards for {lvl} students on the topic '{topic}' in {sub}. "
                f'Return ONLY JSON: {{"cards":[{{"front":"question or term","back":"answer or definition"}}]}}'}],
                "Flashcard generator. Return ONLY valid JSON.", 1200)
            try:
                clean = raw.replace("```json","").replace("```","").strip()
                data = json.loads(clean)
                st.session_state.flashcards = data["cards"]
                st.session_state.fc_index = 0
                st.session_state.fc_flipped = False
                bump_stats(extra_field="flashcard", xp_key="flashcard")
                check_daily_challenges()
                st.rerun()
            except: st.error("Could not generate flashcards. Try again.")

    cards = st.session_state.flashcards
    if cards:
        idx = st.session_state.fc_index
        flipped = st.session_state.fc_flipped
        card = cards[idx]
        color = SUBJECTS.get(sub, {"color":"#2563EB"})["color"]
        muted = t["text_muted"]
        st.markdown(f"<div style='text-align:right;font-size:12px;color:{muted};margin-bottom:8px'>Card {idx+1} of {len(cards)}</div>", unsafe_allow_html=True)
        side_label = "💡 Answer" if flipped else "❓ Question"
        side_content = card["back"] if flipped else card["front"]
        side_color = "#059669" if flipped else color
        st.markdown(f"""
        <div class='fc-card' style='border-color:{side_color}'>
            <div style='font-size:11px;font-weight:800;color:{side_color};text-transform:uppercase;letter-spacing:1px;margin-bottom:12px'>{side_label}</div>
            <div style='font-size:18px;font-weight:700;line-height:1.5;color:{t["text"]}'>{side_content}</div>
            <div style='font-size:12px;color:{t["text_muted"]};margin-top:16px'>👆 Click "Flip Card" to reveal {"question" if flipped else "answer"}</div>
        </div>""", unsafe_allow_html=True)

        c1,c2,c3 = st.columns([1,2,1])
        with c1:
            if idx > 0:
                if st.button("◀ Prev", use_container_width=True):
                    st.session_state.fc_index -= 1; st.session_state.fc_flipped = False; st.rerun()
        with c2:
            if st.button("🔄 Flip Card", use_container_width=True, type="primary"):
                st.session_state.fc_flipped = not flipped; st.rerun()
        with c3:
            if idx < len(cards)-1:
                if st.button("Next ▶", use_container_width=True):
                    st.session_state.fc_index += 1; st.session_state.fc_flipped = False; st.rerun()
            else:
                if st.button("🔁 Restart", use_container_width=True):
                    st.session_state.fc_index = 0; st.session_state.fc_flipped = False; st.rerun()

        # Progress dots
        cb = t["card_border"]
        def dot_color(i): return color if i == idx else cb
        dots = "".join([f"<span style='display:inline-block;width:8px;height:8px;border-radius:50%;margin:0 2px;background:{dot_color(i)}'></span>" for i in range(len(cards))])
        st.markdown(f"<div style='text-align:center;margin-top:10px'>{dots}</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# 📅 HOMEWORK PLANNER
# ─────────────────────────────────────────────────────────────────
def page_homework():
    t = get_theme(); u = st.session_state.user
    st.markdown(f"<h3 style='color:{t['text']}'>📅 Homework Planner</h3>", unsafe_allow_html=True)
    hw = load_json(HW_FILE)
    email = u["email"]
    if email not in hw: hw[email] = []
    tasks = hw[email]

    with st.expander("➕ Add New Task", expanded=len(tasks)==0):
        with st.form("hw_form", clear_on_submit=True):
            c1,c2 = st.columns(2)
            with c1: hw_sub = st.selectbox("📚 Subject", list(SUBJECTS.keys()), key="hw_sub_sel")
            with c2: due = st.date_input("📅 Due Date", min_value=datetime.date.today())
            hw_title = st.text_input("📝 Task Title", placeholder="e.g. Solve Exercise 3.4, Write essay on...")
            hw_prio  = st.select_slider("🎯 Priority", options=["Low","Medium","High","Urgent"], value="Medium")
            ai_help  = st.checkbox("🤖 Get AI help breaking this into steps")
            if st.form_submit_button("➕ Add Task", type="primary"):
                if hw_title.strip():
                    steps = ""
                    if ai_help:
                        with st.spinner("AI is planning your task..."):
                            steps = call_ai([{"role":"user","content":
                                f"Break down this homework task into 4-5 clear steps for a {u.get('grade','Class 5')} student: '{hw_title}' for {hw_sub}. Keep each step brief and actionable."}],
                                "Homework planner. Give concise numbered steps.", 400)
                    new_task = {"id":str(int(time.time())),"title":hw_title.strip(),"subject":hw_sub,
                        "due":due.isoformat(),"priority":hw_prio,"done":False,"steps":steps,
                        "created":datetime.date.today().isoformat()}
                    tasks.append(new_task)
                    hw[email] = tasks
                    save_json(HW_FILE, hw)
                    bump_stats(extra_field="hw_tasks")
                    check_daily_challenges()
                    st.success("✅ Task added!"); st.rerun()

    today_str = datetime.date.today().isoformat()
    pending = [t2 for t2 in tasks if not t2.get("done")]
    done_tasks = [t2 for t2 in tasks if t2.get("done")]

    prio_order = {"Urgent":0,"High":1,"Medium":2,"Low":3}
    pending.sort(key=lambda x: (x.get("due","9999"), prio_order.get(x.get("priority","Medium"),2)))

    if pending:
        st.markdown(f"<h4 style='color:{t['text']}'>📋 Pending Tasks ({len(pending)})</h4>", unsafe_allow_html=True)
        for task in pending:
            info = SUBJECTS.get(task["subject"], {"emoji":"📚","color":"#666"})
            due_date = task.get("due","")
            overdue = due_date < today_str
            days_left = (datetime.date.fromisoformat(due_date) - datetime.date.today()).days if due_date else 99
            prio_colors = {"Urgent":"#EF4444","High":"#F97316","Medium":"#EAB308","Low":"#22C55E"}
            prio_c = prio_colors.get(task.get("priority","Medium"),"#666")
            due_label = "⚠️ OVERDUE" if overdue else ("📅 Today!" if days_left==0 else f"📅 {days_left}d left")
            due_color = "#EF4444" if overdue else ("#F97316" if days_left<=1 else t["text_muted"])

            with st.expander(f"{info['emoji']} {task['title']} | {due_label}"):
                c1,c2,c3 = st.columns([3,1,1])
                with c1:
                    st.markdown(f"""<div style='color:{t["text"]}'>
                        <b>{task['title']}</b><br>
                        <span style='font-size:12px;color:{t["text_muted"]}'>{task['subject']} • Due: {due_date}</span><br>
                        <span style='font-size:11px;background:{prio_c}22;color:{prio_c};padding:2px 8px;border-radius:20px;font-weight:700'>{task.get('priority','Medium')}</span>
                    </div>""", unsafe_allow_html=True)
                    if task.get("steps"):
                        st.markdown(f"<div style='font-size:13px;color:{t['text_muted']};margin-top:8px;white-space:pre-wrap'>{task['steps']}</div>", unsafe_allow_html=True)
                with c2:
                    if st.button("✅ Done", key=f"hw_done_{task['id']}"):
                        for tk in hw[email]:
                            if tk["id"]==task["id"]: tk["done"]=True; break
                        save_json(HW_FILE, hw); add_xp(20,"Task completed!"); st.rerun()
                with c3:
                    if st.button("🗑️ Del", key=f"hw_del_{task['id']}"):
                        hw[email] = [tk for tk in hw[email] if tk["id"]!=task["id"]]
                        save_json(HW_FILE, hw); st.rerun()
    else:
        st.success("🎉 No pending tasks! You're all caught up.")

    if done_tasks:
        with st.expander(f"✅ Completed Tasks ({len(done_tasks)})"):
            for task in done_tasks[-5:]:
                tmuted = t["text_muted"]
                st.markdown(f"<div style='color:{tmuted};font-size:13px;text-decoration:line-through'>✅ {task['title']}</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# ⏳ EXAM COUNTDOWN
# ─────────────────────────────────────────────────────────────────
def page_exams():
    t = get_theme(); u = st.session_state.user
    st.markdown(f"<h3 style='color:{t['text']}'>⏳ Exam Countdown</h3>", unsafe_allow_html=True)
    exams_key = f"exams_{u['email']}"
    if exams_key not in st.session_state: st.session_state[exams_key] = []
    exams = st.session_state[exams_key]

    with st.expander("➕ Add Exam", expanded=len(exams)==0):
        with st.form("exam_form", clear_on_submit=True):
            c1,c2 = st.columns(2)
            with c1: ex_name = st.text_input("📝 Exam Name", placeholder="e.g. Maths Final, Physics Test")
            with c2: ex_sub  = st.selectbox("📚 Subject", list(SUBJECTS.keys()))
            ex_date = st.date_input("📅 Exam Date", min_value=datetime.date.today())
            ex_note = st.text_input("📌 Notes (optional)", placeholder="Chapters 1-5, Past papers...")
            if st.form_submit_button("➕ Add Exam", type="primary") and ex_name.strip():
                exams.append({"name":ex_name.strip(),"subject":ex_sub,"date":ex_date.isoformat(),"note":ex_note})
                st.session_state[exams_key] = exams; st.rerun()

    if exams:
        today = datetime.date.today()
        sorted_exams = sorted(exams, key=lambda x: x["date"])
        for i, exam in enumerate(sorted_exams):
            info = SUBJECTS.get(exam["subject"],{"emoji":"📚","color":"#666"})
            exam_date = datetime.date.fromisoformat(exam["date"])
            days_left = (exam_date - today).days
            if days_left < 0:
                label = "Exam passed"; bg = "rgba(107,114,128,.3)"
            elif days_left == 0:
                label = "🚨 TODAY!"; bg = "linear-gradient(135deg,#EF4444,#B91C1C)"
            elif days_left <= 3:
                label = f"🔥 {days_left} days left!"; bg = "linear-gradient(135deg,#F97316,#C2410C)"
            elif days_left <= 7:
                label = f"⚡ {days_left} days left"; bg = "linear-gradient(135deg,#EAB308,#A16207)"
            else:
                label = f"📅 {days_left} days left"; bg = f"linear-gradient(135deg,{info['color']},{info['color']}99)"

            st.markdown(f"""
            <div class='countdown-card' style='background:{bg}'>
                <div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px'>
                    <div>
                        <div style='font-size:11px;opacity:.7;text-transform:uppercase;letter-spacing:1px'>{info['emoji']} {exam['subject']}</div>
                        <div style='font-size:20px;font-weight:900;margin:4px 0'>{exam['name']}</div>
                        <div style='font-size:12px;opacity:.8'>{exam_date.strftime('%B %d, %Y')}{" — " + exam['note'] if exam.get('note') else ""}</div>
                    </div>
                    <div style='text-align:right'>
                        <div style='font-size:36px;font-weight:900;line-height:1'>{"0" if days_left<=0 else days_left}</div>
                        <div style='font-size:12px;opacity:.7'>days</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"🗑️ Remove {exam['name']}", key=f"rm_exam_{i}"):
                exams.pop(i); st.session_state[exams_key]=exams; st.rerun()
    else:
        st.info("📅 No exams added yet. Add your upcoming exams to start the countdown!")

# ─────────────────────────────────────────────────────────────────
# 🎯 DAILY CHALLENGES
# ─────────────────────────────────────────────────────────────────
def page_challenges():
    t = get_theme(); u = st.session_state.user
    stats = u.get("stats",{})
    today = datetime.date.today().isoformat()
    st.markdown(f"<h3 style='color:{t['text']}'>🎯 Daily Challenges</h3>", unsafe_allow_html=True)
    if stats.get("daily_date","") != today:
        st.info("📅 Complete tasks today to earn bonus XP!")
    done = stats.get("challenges_done",[]) if stats.get("daily_date","")==today else []
    total_xp = sum(ch["xp"] for ch in DAILY_CHALLENGES if ch["id"] in done)
    max_xp   = sum(ch["xp"] for ch in DAILY_CHALLENGES)

    st.markdown(f"""
    <div style='background:{t["card"]};border-radius:14px;padding:16px;border:1px solid {t["card_border"]};margin-bottom:16px'>
        <div style='display:flex;justify-content:space-between;font-weight:800;color:{t["text"]};margin-bottom:8px'>
            <span>🎯 Today's Progress</span><span style='color:#F59E0B'>{total_xp}/{max_xp} XP</span>
        </div>
        <div class='prog-bar'><div class='prog-fill' style='width:{int(total_xp/max(max_xp,1)*100)}%;background:linear-gradient(90deg,#F59E0B,#EF4444)'></div></div>
        <div style='font-size:12px;color:{t["text_muted"]};margin-top:6px'>{len(done)}/{len(DAILY_CHALLENGES)} challenges completed</div>
    </div>""", unsafe_allow_html=True)

    prog_map = {
        "questions": stats.get("daily_questions",0) if stats.get("daily_date","")==today else 0,
        "quiz":      stats.get("daily_quiz",0) if stats.get("daily_date","")==today else 0,
        "essays":    stats.get("daily_essays",0) if stats.get("daily_date","")==today else 0,
        "flashcard": stats.get("daily_flashcard",0) if stats.get("daily_date","")==today else 0,
        "images":    stats.get("daily_images",0) if stats.get("daily_date","")==today else 0,
        "subjects":  len(stats.get("daily_subjects",[])) if stats.get("daily_date","")==today else 0,
    }
    for ch in DAILY_CHALLENGES:
        is_done = ch["id"] in done
        prog = prog_map.get(ch["type"],0)
        pct  = min(int(prog/ch["target"]*100),100)
        cls  = "challenge-card challenge-done" if is_done else "challenge-card"
        status = f"✅ Completed! +{ch['xp']} XP" if is_done else f"{prog}/{ch['target']}"
        status_color = "#059669" if is_done else t["text_muted"]
        st.markdown(f"""
        <div class='{cls}'>
            <div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px'>
                <div>
                    <div style='font-weight:800;font-size:14px;color:{t["text"]}'>{ch['desc']}</div>
                    <div style='font-size:12px;color:{status_color};margin-top:3px'>{status}</div>
                </div>
                <div style='text-align:right'>
                    <div style='font-size:18px;font-weight:900;color:#F59E0B'>+{ch["xp"]}</div>
                    <div style='font-size:10px;color:{t["text_muted"]}'>XP</div>
                </div>
            </div>
            {"" if is_done else f"<div class='prog-bar' style='margin-top:8px'><div class='prog-fill' style='width:{pct}%;background:linear-gradient(90deg,#F59E0B,#EF4444)'></div></div>"}
        </div>""", unsafe_allow_html=True)

    if len(done) == len(DAILY_CHALLENGES):
        st.markdown(f"""<div style='background:linear-gradient(135deg,#059669,#047857);border-radius:16px;padding:20px;text-align:center;color:#fff;margin-top:12px'>
            <div style='font-size:40px'>🏆</div>
            <div style='font-size:18px;font-weight:800;margin-top:8px'>All Challenges Complete!</div>
            <div style='font-size:13px;opacity:.8;margin-top:4px'>Come back tomorrow for new challenges!</div>
        </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# 👥 STUDY GROUPS
# ─────────────────────────────────────────────────────────────────
def page_groups():
    t = get_theme(); u = st.session_state.user
    st.markdown(f"<h3 style='color:{t['text']}'>👥 Study Groups</h3>", unsafe_allow_html=True)
    groups = load_json(GROUPS_FILE)
    email = u["email"]

    tab1, tab2, tab3 = st.tabs(["🔍 Browse Groups","➕ Create Group","📢 Group Chat"])

    with tab1:
        if not groups:
            st.info("No study groups yet. Create one and invite friends!")
        else:
            for gid, g in groups.items():
                is_member = email in g.get("members",[])
                info = SUBJECTS.get(g.get("subject",""), {"emoji":"📚","color":"#666"})
                st.markdown(f"""
                <div class='group-card'>
                    <div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:8px'>
                        <div>
                            <div style='font-size:20px;display:inline'>{info['emoji']} </div>
                            <span style='font-weight:800;font-size:15px;color:{t["text"]}'>{g['name']}</span>
                            <span style='font-size:11px;background:{info["color"]}22;color:{info["color"]};padding:2px 8px;border-radius:20px;font-weight:700;margin-left:8px'>{g.get('subject','')}</span>
                            <div style='font-size:12px;color:{t["text_muted"]};margin-top:4px'>👥 {len(g.get("members",[]))} members • Created by {g.get("creator_name","?")}</div>
                            <div style='font-size:12px;color:{t["text_muted"]};margin-top:2px'>📝 {g.get("description","")}</div>
                        </div>
                        <div style='font-size:11px;color:{"#059669" if is_member else t["text_muted"]};font-weight:700'>{"✅ Joined" if is_member else ""}</div>
                    </div>
                </div>""", unsafe_allow_html=True)
                if not is_member:
                    if st.button(f"Join '{g['name']}'", key=f"join_{gid}"):
                        groups[gid]["members"].append(email)
                        save_json(GROUPS_FILE, groups)
                        bump_stats(extra_field="groups")
                        st.toast(f"Joined '{g['name']}'! 🎉"); st.rerun()
                else:
                    if st.button(f"💬 Open '{g['name']}'", key=f"open_{gid}"):
                        st.session_state["active_group"] = gid; st.session_state.page="groups"; st.rerun()

    with tab2:
        with st.form("create_group"):
            gname = st.text_input("👥 Group Name", placeholder="e.g. Maths Champions, O-Level Squad")
            gsub  = st.selectbox("📚 Subject Focus", list(SUBJECTS.keys()))
            gdesc = st.text_input("📝 Description", placeholder="What is this group for?")
            if st.form_submit_button("🚀 Create Group", type="primary"):
                if gname.strip():
                    gid = str(int(time.time()))
                    groups[gid] = {"name":gname.strip(),"subject":gsub,"description":gdesc,
                        "creator":email,"creator_name":u["name"],"members":[email],"messages":[],"created":datetime.date.today().isoformat()}
                    save_json(GROUPS_FILE, groups)
                    bump_stats(extra_field="groups")
                    st.success(f"Group '{gname}' created! Share it with friends."); st.rerun()

    with tab3:
        active_gid = st.session_state.get("active_group")
        my_groups = {gid:g for gid,g in groups.items() if email in g.get("members",[])}
        if not my_groups:
            st.info("Join a group first to chat!")
        else:
            sel = st.selectbox("Select Group", list(my_groups.keys()),
                format_func=lambda x: my_groups[x]["name"])
            g = groups[sel]
            msgs = g.get("messages",[])[-20:]
            for m in msgs:
                is_me = m["email"]==email
                align = "msg-user" if is_me else "msg-bot"
                name_label = "You" if is_me else m["name"]
                st.markdown(f"<div class='msg-lbl {'msg-lbl-r' if is_me else ''}'>{name_label}</div><div class='{align}'>{m['content']}</div>", unsafe_allow_html=True)
            with st.form("group_msg", clear_on_submit=True):
                msg_txt = st.text_input("💬 Message", placeholder="Type your message...", label_visibility="collapsed")
                if st.form_submit_button("📤 Send", type="primary") and msg_txt.strip():
                    groups[sel]["messages"].append({"email":email,"name":u["name"],"content":msg_txt.strip(),"time":datetime.datetime.now().strftime("%H:%M")})
                    save_json(GROUPS_FILE, groups); st.rerun()

# ─────────────────────────────────────────────────────────────────
# 🏆 LEADERBOARD
# ─────────────────────────────────────────────────────────────────
def page_leaderboard():
    t = get_theme()
    st.markdown(f"<h3 style='color:{t['text']}'>🏆 Leaderboard</h3>", unsafe_allow_html=True)
    users = load_json(USERS_FILE)
    board = []
    for em, usr in users.items():
        if usr.get("role") == "parent": continue
        s = usr.get("stats",{})
        board.append({"name":usr["name"],"avatar":usr.get("avatar","👦"),
            "grade":usr.get("grade",""),
            "xp":s.get("xp",0),"total":s.get("total",0),
            "badges":len(usr.get("badges",[])),
            "streak":s.get("streak",0),
            "level":get_level(s.get("xp",0))["name"],
            "is_me":em==st.session_state.user["email"]})
    board.sort(key=lambda x: x["xp"], reverse=True)

    tab1, tab2, tab3 = st.tabs(["⚡ By XP","❓ By Questions","🔥 By Streak"])

    def render_board(sorted_board):
        medals = ["🥇","🥈","🥉"]
        for i, entry in enumerate(sorted_board[:10]):
            medal = medals[i] if i < 3 else f"#{i+1}"
            me_style = f"border:2px solid #E8472A!important;" if entry["is_me"] else ""
            st.markdown(f"""
            <div class='leaderboard-row' style='{me_style}'>
                <div style='font-size:22px;min-width:36px;text-align:center'>{medal}</div>
                <div style='font-size:28px'>{entry["avatar"]}</div>
                <div style='flex:1'>
                    <div style='font-weight:800;font-size:14px;color:{t["text"]}'>{entry["name"]} {"⭐ (You)" if entry["is_me"] else ""}</div>
                    <div style='font-size:11px;color:{t["text_muted"]}'>{entry["level"]} • {entry["grade"]}</div>
                </div>
                <div style='text-align:right'>
                    <div style='font-size:16px;font-weight:900;color:#F59E0B'>⚡ {entry["xp"]}</div>
                    <div style='font-size:10px;color:{t["text_muted"]}'>❓{entry["total"]} 🏆{entry["badges"]}</div>
                </div>
            </div>""", unsafe_allow_html=True)

    with tab1: render_board(sorted(board, key=lambda x: x["xp"], reverse=True))
    with tab2: render_board(sorted(board, key=lambda x: x["total"], reverse=True))
    with tab3: render_board(sorted(board, key=lambda x: x["streak"], reverse=True))

    # User rank
    my_rank = next((i+1 for i,e in enumerate(board) if e["is_me"]), None)
    if my_rank:
        st.markdown(f"""<div style='background:linear-gradient(135deg,#E8472A22,#7C3AED22);border:1.5px solid #E8472A;border-radius:12px;padding:12px 16px;text-align:center;margin-top:12px;color:{t["text"]}'>
            🎯 Your Rank: <b style='font-size:18px;color:#E8472A'>#{my_rank}</b> out of {len(board)} students
        </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# 🏅 TROPHY CABINET
# ─────────────────────────────────────────────────────────────────
def page_trophies():
    t = get_theme(); u = st.session_state.user
    stats = u.get("stats",{}); xp = stats.get("xp",0)
    lvl = get_level(xp); next_lvl, _ = get_next_level(xp)
    st.markdown(f"<h3 style='color:{t['text']}'>🏅 Trophy Cabinet</h3>", unsafe_allow_html=True)

    # Level progress
    st.markdown(f"""
    <div class='trophy-card'>
        <div style='font-size:11px;opacity:.6;text-transform:uppercase;letter-spacing:1px'>Current Level</div>
        <div style='font-size:48px;margin:8px 0'>{lvl["name"]}</div>
        <div style='font-size:28px;font-weight:900;color:#F5CC4A'>⚡ {xp} XP</div>
        {f"<div style='font-size:13px;opacity:.7;margin-top:6px'>Next: {next_lvl['name']} at {next_lvl['min']} XP</div>" if next_lvl else "<div style='font-size:14px;color:#FFD700;margin-top:6px'>🏆 Maximum Level Achieved!</div>"}
    </div>""", unsafe_allow_html=True)

    # All levels path
    st.markdown(f"<h4 style='color:{t['text']};margin-top:16px'>🗺️ Level Journey</h4>", unsafe_allow_html=True)
    cols = st.columns(len(XP_LEVELS))
    for i, (col_obj, lv) in enumerate(zip(cols, XP_LEVELS)):
        with col_obj:
            achieved = xp >= lv["min"]
            opacity = "1" if achieved else "0.3"
            st.markdown(f"""
            <div style='text-align:center;opacity:{opacity};padding:10px 5px'>
                <div style='font-size:24px'>{"✅" if achieved else "🔒"}</div>
                <div style='font-size:11px;font-weight:800;color:{lv["color"]};margin-top:4px'>{lv["name"]}</div>
                <div style='font-size:10px;color:{t["text_muted"]}'>{lv["min"]} XP</div>
            </div>""", unsafe_allow_html=True)

    # XP breakdown
    st.markdown(f"<h4 style='color:{t['text']};margin-top:8px'>💡 How to Earn XP</h4>", unsafe_allow_html=True)
    xp_info = [
        ("❓ Ask a question","10 XP"),("📝 Answer quiz question","15 XP"),("🏁 Complete a quiz","25 XP"),
        ("✏️ Write an essay","30 XP"),("🃏 Use flashcards","10 XP"),("🎨 Generate image","20 XP"),
        ("📄 Upload document","20 XP"),("🔥 7-day streak","100 XP bonus"),("🎯 Daily challenge","30-60 XP"),
    ]
    c1, c2 = st.columns(2)
    for i, (action, reward) in enumerate(xp_info):
        with (c1 if i%2==0 else c2):
            st.markdown(f"""
            <div style='background:{t["card"]};border-radius:10px;padding:10px 14px;margin-bottom:8px;border:1px solid {t["card_border"]};display:flex;justify-content:space-between;align-items:center'>
                <span style='font-size:13px;color:{t["text"]}'>{action}</span>
                <span style='font-size:13px;font-weight:800;color:#F59E0B'>{reward}</span>
            </div>""", unsafe_allow_html=True)

    # Stats summary
    st.markdown(f"<h4 style='color:{t['text']};margin-top:8px'>📊 Your Achievements</h4>", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    with c1: st.metric("❓ Questions", stats.get("total",0))
    with c2: st.metric("🏆 Badges", len(u.get("badges",[])))
    with c3: st.metric("🔥 Best Streak", f"{stats.get('streak',0)}d")
    with c4: st.metric("🎯 Challenges", len(stats.get("challenges_done",[])))

# ─────────────────────────────────────────────────────────────────
# 👨‍👩‍👦 PARENT DASHBOARD
# ─────────────────────────────────────────────────────────────────
def page_parent():
    t = get_theme(); u = st.session_state.user
    st.markdown(f"<h3 style='color:{t['text']}'>👨‍👩‍👦 Parent Dashboard</h3>", unsafe_allow_html=True)

    if u.get("role") != "parent":
        st.warning("This page is for parent accounts only.")
        return

    all_users = load_json(USERS_FILE)
    children = [usr for em,usr in all_users.items() if usr.get("role")=="student"]

    if not children:
        st.info("No student accounts found yet.")
        return

    st.markdown(f"<p style='color:{t['text_muted']};font-size:13px'>Monitoring {len(children)} student(s) on this platform</p>", unsafe_allow_html=True)

    for child in children:
        s = child.get("stats",{}); xp = s.get("xp",0)
        lvl = get_level(xp)
        info_color = "#059669" if s.get("lastDate","") == datetime.date.today().isoformat() else "#E8472A"
        activity = "✅ Studied today" if s.get("lastDate","") == datetime.date.today().isoformat() else "⚠️ Not studied today"

        with st.expander(f"{child.get('avatar','👦')} {child['name']} — {child.get('grade','')} — {activity}"):
            c1,c2,c3,c4 = st.columns(4)
            with c1: st.metric("⚡ XP",   xp)
            with c2: st.metric("❓ Questions", s.get("total",0))
            with c3: st.metric("🔥 Streak", f"{s.get('streak',0)}d")
            with c4: st.metric("🏆 Badges", len(child.get("badges",[])))

            txt_col = t["text"]
            st.markdown(f"<div style='margin:10px 0 6px;font-weight:800;color:{txt_col}'>📚 Subject Activity</div>", unsafe_allow_html=True)
            for sub, info in SUBJECTS.items():
                cnt = s.get(sub,0); total = s.get("total",1)
                pct = int(cnt/max(total,1)*100)
                st.markdown(f"""
                <div style='margin-bottom:10px'>
                    <div style='display:flex;justify-content:space-between;font-size:12px;font-weight:700;color:{t["text"]};margin-bottom:3px'>
                        <span>{info['emoji']} {sub}</span><span style='color:{info["color"]}'>{cnt} questions</span>
                    </div>
                    <div class='prog-bar'><div class='prog-fill' style='width:{pct}%;background:{info["color"]}'></div></div>
                </div>""", unsafe_allow_html=True)

            today_chal = len(s.get("challenges_done",[])) if s.get("daily_date","")==datetime.date.today().isoformat() else 0
            st.markdown(f"""
            <div style='background:{t["card"]};border-radius:10px;padding:12px;border:1px solid {t["card_border"]};margin-top:8px;font-size:13px;color:{t["text"]}'>
                📊 <b>Today's Activity:</b> {s.get("daily_questions",0) if s.get("daily_date","")==datetime.date.today().isoformat() else 0} questions •
                {today_chal} challenges done •
                {s.get("daily_images",0) if s.get("daily_date","")==datetime.date.today().isoformat() else 0} images generated
                <br><span style='color:{info_color};font-weight:700;margin-top:4px;display:block'>{activity}</span>
            </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# DOC Q&A
# ─────────────────────────────────────────────────────────────────
def page_docqa():
    t = get_theme(); u = st.session_state.user
    st.markdown(f"<h3 style='color:{t['text']}'>📄 Document Q&A</h3>", unsafe_allow_html=True)
    uploaded = st.file_uploader("📎 Upload PDF or TXT file", type=["pdf","txt"])
    doc_text = ""
    if uploaded:
        st.success(f"✅ Uploaded: **{uploaded.name}**")
        if uploaded.type == "text/plain":
            doc_text = uploaded.read().decode("utf-8", errors="ignore")
        elif uploaded.type == "application/pdf":
            try:
                content = uploaded.read().decode("latin-1", errors="ignore")
                text_chunks = re.findall(r'BT\s*(.*?)\s*ET', content, re.DOTALL)
                text_parts = []
                for chunk in text_chunks:
                    words = re.findall(r'\((.*?)\)', chunk)
                    if words: text_parts.extend(words)
                doc_text = " ".join(text_parts)
                if len(doc_text.strip()) < 50:
                    doc_text = " ".join(re.findall(r'[A-Za-z0-9\s\.,;:\!\?\'\"]{4,}', content))
                doc_text = doc_text[:12000]
            except: st.warning("⚠️ Could not extract text. Try a .txt file.")

        if doc_text.strip():
            c1,c2,c3 = st.columns(3)
            with c1:
                if st.button("📋 Summarize", use_container_width=True, type="primary"):
                    with st.spinner("Reading..."):
                        st.session_state["doc_result"] = call_ai_with_doc([{"role":"user","content":"Summarize this document clearly with key points."}], build_system(u,"English",u.get("grade","Class 5")), doc_text)
                    bump_stats(extra_field="docs", xp_key="doc"); check_daily_challenges(); st.rerun()
            with c2:
                if st.button("🔑 Key Points", use_container_width=True):
                    with st.spinner("Extracting..."):
                        st.session_state["doc_result"] = call_ai_with_doc([{"role":"user","content":"List all important key points, definitions and formulas. Use bullet points."}], build_system(u,"English",u.get("grade","Class 5")), doc_text)
                    st.rerun()
            with c3:
                if st.button("❓ Make Quiz", use_container_width=True):
                    with st.spinner("Creating quiz..."):
                        raw = call_ai_with_doc([{"role":"user","content":'Create 5 MCQs from this document. Return ONLY JSON: {"questions":[{"q":"...","options":["A. ...","B. ...","C. ...","D. ..."],"answer":"A. ...","explanation":"..."}]}'}], "Quiz generator. Return ONLY valid JSON.", doc_text, 1500)
                        try:
                            clean = raw.replace("```json","").replace("```","").strip()
                            data = json.loads(clean)
                            st.session_state.quiz = {"questions":data["questions"],"current":0,"score":0,"answers":[],"done":False,"sub":"English","lvl":u.get("grade","Class 5")}
                            st.session_state.page = "quiz"; st.rerun()
                        except: st.error("Could not generate quiz.")

            with st.form("doc_qa_form", clear_on_submit=True):
                doc_q = st.text_area("💬 Ask about this document", placeholder="What is the main topic? Explain the formula...", height=80, label_visibility="collapsed")
                if st.form_submit_button("🔍 Ask", use_container_width=True, type="primary") and doc_q.strip():
                    with st.spinner("Analyzing..."):
                        st.session_state["doc_result"] = call_ai_with_doc([{"role":"user","content":doc_q}], build_system(u,"English",u.get("grade","Class 5")), doc_text)
                    st.rerun()

    if st.session_state.get("doc_result"):
        st.markdown(f"""<div style='background:{t["card"]};border-radius:16px;padding:20px;border-left:4px solid #059669;margin-top:12px;color:{t["text"]}'>
            <div style='font-weight:800;font-size:13px;color:#059669;margin-bottom:10px'>🤖 Ustad's Answer</div>
            <div style='font-size:14px;line-height:1.8;white-space:pre-wrap'>{st.session_state["doc_result"]}</div>
        </div>""", unsafe_allow_html=True)
        if st.button("🗑️ Clear"): st.session_state["doc_result"]=""; st.rerun()

# ─────────────────────────────────────────────────────────────────
# QUIZ
# ─────────────────────────────────────────────────────────────────
def page_quiz():
    t = get_theme(); u = st.session_state.user
    c1,c2 = st.columns(2)
    with c1: sub = st.selectbox("📚 Subject", list(SUBJECTS.keys()), key="quiz_sub")
    with c2:
        lvl_idx = LEVELS.index(u.get("grade","Class 5")) if u.get("grade","") in LEVELS else 4
        lvl = st.selectbox("🏫 Class", LEVELS, index=lvl_idx, key="quiz_lvl")
    q = st.session_state.quiz
    if q is None:
        st.markdown("<br>",unsafe_allow_html=True)
        if st.button("🚀 Generate 5-Question Quiz", use_container_width=True, type="primary"):
            with st.spinner("✨ Generating quiz..."):
                raw = call_ai([{"role":"user","content":
                    f"Create exactly 5 MCQs for {lvl} {sub} students in Pakistan. "
                    f'Return ONLY raw JSON: {{"questions":[{{"q":"...","options":["A. ...","B. ...","C. ...","D. ..."],"answer":"A. ...","explanation":"..."}}]}}'}],
                    "Quiz generator. ONLY valid raw JSON.", 1200)
                try:
                    clean = raw.replace("```json","").replace("```","").strip()
                    data = json.loads(clean)
                    st.session_state.quiz={"questions":data["questions"],"current":0,"score":0,"answers":[],"done":False,"sub":sub,"lvl":lvl}; st.rerun()
                except: st.error("⚠️ Could not generate quiz. Try again.")
        return
    info = SUBJECTS[q["sub"]]
    if q["done"]:
        total=len(q["questions"]); score=q["score"]; pct=int((score/total)*100)
        emoji="🏆" if pct>=80 else "👍" if pct>=60 else "💪"
        st.markdown(f"""<div style='text-align:center;background:{t["card"]};border-radius:20px;padding:30px;box-shadow:0 2px 16px rgba(0,0,0,.06);margin-bottom:16px'>
            <div style='font-size:56px'>{emoji}</div>
            <h2 style='font-family:"Baloo 2",cursive;font-size:26px;font-weight:800;color:{t["text"]}'>Quiz Complete!</h2>
            <div style='font-size:44px;font-weight:900;color:{info["color"]};margin:8px 0'>{score}/{total}</div>
            <div style='font-size:15px;color:{t["text_muted"]}'>{pct}% — {"Excellent! ⭐" if pct>=80 else "Good effort! 📚" if pct>=60 else "Keep practicing! 💪"}</div>
        </div>""", unsafe_allow_html=True)
        # Award XP
        xp_earned = score*XP_REWARDS["quiz_q"] + XP_REWARDS["quiz_done"]
        add_xp(xp_earned, f"Quiz: {score}/{total} correct")
        bump_stats(extra_field="daily_quiz")
        check_daily_challenges()
        for i,(ques,ans) in enumerate(zip(q["questions"],q["answers"])):
            correct = ans["chosen"]==ques["answer"]
            bg = ("#0D2A0D" if st.session_state.dark_mode else "#F0FDF4") if correct else ("#2A0D0D" if st.session_state.dark_mode else "#FFF1EE")
            border = "#059669" if correct else "#E8472A"
            wrong = "" if correct else f'<div style="font-size:13px;color:#059669;margin-top:2px">✅ {ques["answer"]}</div>'
            st.markdown(f"""<div style='background:{bg};border:1.5px solid {border};border-radius:12px;padding:14px;margin-bottom:10px;color:{t["text"]}'>
                <div style='font-weight:700;font-size:14px'>Q{i+1}. {ques["q"]}</div>
                <div style='font-size:13px;margin-top:5px'>{ans["chosen"]} {"✅" if correct else "❌"}</div>
                {wrong}
                <div style='font-size:12px;color:{t["text_muted"]};margin-top:4px'>💡 {ques.get("explanation","")}</div>
            </div>""", unsafe_allow_html=True)
        if st.button("🔄 Try Another Quiz", use_container_width=True, type="primary"):
            st.session_state.quiz=None; st.rerun()
        return
    current=q["current"]; ques=q["questions"][current]; pct_bar=int((current/len(q["questions"]))*100)
    st.markdown(f"""
    <div style='display:flex;justify-content:space-between;font-size:13px;font-weight:700;color:{t["text_muted"]};margin-bottom:6px'>
        <span>Question {current+1} of {len(q["questions"])}</span>
        <span style='color:{info["color"]}'>Score: {q["score"]}/{current}</span>
    </div>
    <div class='prog-bar'><div class='prog-fill' style='width:{pct_bar}%;background:{info["color"]}'></div></div>
    <div style='background:{t["card"]};border-radius:16px;padding:18px 20px;margin:12px 0;font-weight:800;font-size:15px;color:{t["text"]};line-height:1.5'>
        Q{current+1}. {ques["q"]}
    </div>""", unsafe_allow_html=True)
    for opt in ques["options"]:
        if st.button(opt, key=f"opt_{current}_{opt}", use_container_width=True):
            q["answers"].append({"chosen":opt})
            if opt==ques["answer"]: q["score"]+=1; st.toast("✅ Correct!",icon="🎉")
            else: st.toast(f"❌ Correct: {ques['answer']}",icon="💡")
            q["current"]+=1
            if q["current"]>=len(q["questions"]): q["done"]=True
            st.session_state.quiz=q; st.rerun()

# ─────────────────────────────────────────────────────────────────
# IMAGE GENERATOR
# ─────────────────────────────────────────────────────────────────
def page_image():
    t=get_theme(); u=st.session_state.user
    st.markdown(f"<h3 style='color:{t['text']}'>🎨 Educational Image Generator</h3>",unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1: img_sub=st.selectbox("📚 Subject",list(SUBJECTS.keys()),key="img_sub")
    with c2:
        lvl_idx=LEVELS.index(u.get("grade","Class 5")) if u.get("grade","") in LEVELS else 4
        img_lvl=st.selectbox("🏫 Class",LEVELS,index=lvl_idx,key="img_lvl")
    style_choice=st.selectbox("🎨 Style",list(IMAGE_STYLES.keys()))
    prompt=st.text_area("📝 Describe what you want",placeholder="e.g. Photosynthesis diagram, Solar system, Water cycle...",height=100)
    if st.button("🎨 Generate Image",use_container_width=True,type="primary"):
        if not prompt.strip(): st.warning("Enter a description first!"); return
        with st.spinner("🎨 Generating... (20-30 sec)"):
            sys_msg=("You are an expert SVG illustrator for Pakistani school students. "
                "Output ONLY SVG code. Start with <svg and end with </svg>. No markdown. "
                "Use xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 700 500\" width=\"700\" height=\"500\". "
                "Include gradients, bright colors, bold title, labeled components, arrows. "
                "Minimum 20 visual elements. No external images.")
            usr_msg=f"Create educational SVG: TOPIC: {prompt}\nSUBJECT: {img_sub}\nLEVEL: {img_lvl}\nSTYLE: {IMAGE_STYLES[style_choice]}\nStart with <svg end with </svg>."
            raw=call_ai_svg([{"role":"user","content":usr_msg}],sys_msg)
        cleaned=raw
        for f in ["```svg","```xml","```html","```"]: cleaned=cleaned.replace(f,"")
        cleaned=cleaned.strip()
        s=cleaned.find("<svg"); e=cleaned.rfind("</svg>")
        if s>=0 and e>=0:
            final_svg=cleaned[s:e+6]
            st.success("✅ Generated!")
            st.components.v1.html(final_svg,height=520,scrolling=False)
            b64=base64.b64encode(final_svg.encode()).decode()
            st.markdown(f'<a href="data:image/svg+xml;base64,{b64}" download="diagram.svg" style="display:inline-block;padding:10px 20px;background:#7C3AED;color:#fff;border-radius:12px;font-weight:700;font-size:14px;text-decoration:none;margin-top:8px">⬇️ Download SVG</a>',unsafe_allow_html=True)
            imgs=load_json(IMAGES_FILE); email=u["email"]
            if email not in imgs: imgs[email]=[]
            imgs[email].insert(0,{"id":str(int(time.time())),"svg":final_svg,"prompt":prompt,"subject":img_sub,"level":img_lvl,"style":style_choice,"created":datetime.datetime.now().strftime("%Y-%m-%d %H:%M")})
            save_json(IMAGES_FILE,imgs)
            bump_stats(extra_field="images",xp_key="image"); check_daily_challenges()
        else: st.error("⚠️ Could not generate. Rephrase and try again.")

# ─────────────────────────────────────────────────────────────────
# ESSAY HELPER
# ─────────────────────────────────────────────────────────────────
def page_essay():
    t=get_theme(); u=st.session_state.user
    st.markdown(f"<h3 style='color:{t['text']}'>✏️ Essay & Writing Helper</h3>",unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1: etype=st.selectbox("📄 Type",ESSAY_TYPES)
    with c2:
        lvl_idx=LEVELS.index(u.get("grade","Class 5")) if u.get("grade","") in LEVELS else 4
        lvl=st.selectbox("🏫 Class",LEVELS,index=lvl_idx,key="essay_lvl")
    topic=st.text_input("📝 Topic",placeholder="e.g. My School, Climate Change...")
    if st.button("✏️ Generate Essay",use_container_width=True,type="primary"):
        if not topic.strip(): st.warning("Enter a topic!"); return
        with st.spinner("✏️ Writing..."):
            result=call_ai([{"role":"user","content":f"Write a complete {etype} about '{topic}' for a {lvl} student in Pakistan. Include introduction, body and conclusion."}],"Expert writing teacher for Pakistani students.",1800)
        st.session_state.essay_result=result
        bump_stats(extra_field="essays",xp_key="essay"); check_daily_challenges()
    if st.session_state.essay_result:
        st.markdown(f"""<div style='background:{t["card"]};border-radius:16px;padding:20px;border-top:4px solid #059669;margin-top:12px;color:{t["text"]}'>
            <div style='font-weight:800;font-size:14px;color:#059669;margin-bottom:12px'>✏️ {etype}: {topic}</div>
            <div style='font-size:14px;line-height:1.85;white-space:pre-wrap'>{st.session_state.essay_result}</div>
        </div>""",unsafe_allow_html=True)
        if st.button("📋 Copy Essay"): st.code(st.session_state.essay_result,language=None)

# ─────────────────────────────────────────────────────────────────
# STUDY TOOLS
# ─────────────────────────────────────────────────────────────────
def page_tools():
    t=get_theme()
    st.markdown(f"<h3 style='color:{t['text']}'>🔧 Study Tools</h3>",unsafe_allow_html=True)
    t1,t2=st.tabs(["🌐 Translator","⏱️ Pomodoro Timer"])
    with t1:
        lang=st.selectbox("Translate to",["Urdu","English","Punjabi","Sindhi","Pashto"])
        text=st.text_area("Enter text",height=100,placeholder="Type text here...")
        if st.button("🌐 Translate",use_container_width=True,type="primary"):
            if not text.strip(): st.warning("Enter some text!")
            else:
                with st.spinner("Translating..."):
                    result=call_ai([{"role":"user","content":f"Translate to {lang}:\n\n{text}\n\nAlso explain difficult words."}],"Translation assistant for Pakistani students.")
                st.session_state.trans_result=result
        if st.session_state.trans_result:
            st.markdown(f"<div style='background:{t['card']};border-radius:12px;padding:16px;font-size:14px;line-height:1.75;white-space:pre-wrap;margin-top:10px;color:{t['text']}'>{st.session_state.trans_result}</div>",unsafe_allow_html=True)
    with t2:
        c1,c2,c3=st.columns(3)
        with c1: st.metric("📚 Study","25 min")
        with c2: st.metric("☕ Break","5 min")
        with c3: st.metric("🌟 Long Break","15 min")
        st.info("⏱️ Set your timer and follow the plan:")
        for i in range(1,5):
            brk="☕ 5 min break" if i<4 else "🌟 15 min long break!"
            st.markdown(f"- 🍅 **Session {i}:** 25 min → {brk}")

# ─────────────────────────────────────────────────────────────────
# PROGRESS
# ─────────────────────────────────────────────────────────────────
def page_progress():
    t=get_theme(); u=st.session_state.user; stats=u.get("stats",{}); total=stats.get("total",0)
    st.markdown(f"<h3 style='color:{t['text']}'>📊 My Progress</h3>",unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    with c1: st.metric("❓ Questions",total)
    with c2: st.metric("⚡ XP",stats.get("xp",0))
    with c3: st.metric("🔥 Streak",f"{stats.get('streak',0)}d")
    with c4: st.metric("🏆 Badges",len(u.get("badges",[])))
    st.markdown(f"<h3 style='color:{t['text']}'>📚 Subject Breakdown</h3>",unsafe_allow_html=True)
    for name,info in SUBJECTS.items():
        cnt=stats.get(name,0); pct=int((cnt/max(total,1))*100)
        st.markdown(f"""<div style='margin-bottom:14px'>
            <div style='display:flex;justify-content:space-between;font-size:13px;font-weight:700;margin-bottom:5px;color:{t["text"]}'>
                <span>{info['emoji']} {name}</span><span style='color:{info["color"]}'>{cnt} ({pct}%)</span>
            </div><div class='prog-bar'><div class='prog-fill' style='width:{pct}%;background:{info["color"]}'></div></div>
        </div>""",unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    with c1: st.metric("🎨 Images",stats.get("images",0))
    with c2: st.metric("✏️ Essays",stats.get("essays",0))
    with c3: st.metric("📄 Docs",stats.get("docs",0))
    with c4: st.metric("🃏 Flashcards",stats.get("flashcard",0))

# ─────────────────────────────────────────────────────────────────
# HISTORY
# ─────────────────────────────────────────────────────────────────
def page_history():
    t=get_theme(); u=st.session_state.user
    st.markdown(f"<h3 style='color:{t['text']}'>🕐 Chat History</h3>",unsafe_allow_html=True)
    hist=load_json(HISTORY_FILE)
    sessions=sorted(hist.get(u["email"],[]),key=lambda x:x.get("updated",""),reverse=True)
    if not sessions: st.info("📭 No chat history yet."); return
    for sess in sessions:
        info=SUBJECTS.get(sess.get("subject",""),{"emoji":"📚","color":"#666"})
        msgs=sess.get("messages",[])
        with st.expander(f"{info['emoji']} {sess.get('subject','')} — {sess.get('level','')} | {sess.get('updated','')} ({len(msgs)} msgs)"):
            for m in msgs:
                if m["role"]=="user": st.markdown(f"<div class='msg-user'>{m['content']}</div>",unsafe_allow_html=True)
                else: st.markdown(f"<div class='msg-bot'>{m['content']}</div>",unsafe_allow_html=True)
            if st.button("🔄 Continue", key=f"cont_{sess['id']}"):
                st.session_state.chat_messages=msgs; st.session_state.session_id=sess["id"]
                st.session_state.subject=sess.get("subject","Maths"); st.session_state.page="chat"; st.rerun()

# ─────────────────────────────────────────────────────────────────
# BADGES
# ─────────────────────────────────────────────────────────────────
def page_badges():
    t=get_theme(); u=st.session_state.user; earned=u.get("badges",[])
    st.markdown(f"<h3 style='color:{t['text']}'>🎖️ Badges</h3>",unsafe_allow_html=True)
    st.markdown(f"<p style='color:{t['text_muted']};font-size:13px'>Earned <b style='color:{t['text']}'>{len(earned)}</b> of <b>{len(BADGES)}</b> badges</p>",unsafe_allow_html=True)
    cols=st.columns(3)
    for i,b in enumerate(BADGES):
        is_earned=b["id"] in earned
        with cols[i%3]:
            locked="" if is_earned else "badge-locked"
            sc="#059669" if is_earned else "#aaa"
            st.markdown(f"""<div class='badge-card {locked}' style='margin-bottom:12px'>
                <span class='badge-icon'>{b['icon']}</span>
                <div class='badge-name'>{b['name']}</div>
                <div class='badge-desc'>{b['desc']}</div>
                <div style='font-size:11px;margin-top:5px;color:{sc};font-weight:700'>{'✅ Earned' if is_earned else '🔒 Locked'}</div>
            </div>""",unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# PROFILE
# ─────────────────────────────────────────────────────────────────
def page_profile():
    t=get_theme(); u=st.session_state.user
    st.markdown(f"<h3 style='color:{t['text']}'>👤 Profile</h3>",unsafe_allow_html=True)
    c1,c2=st.columns([1,2])
    with c1: st.markdown(f"<div style='font-size:80px;text-align:center;background:{t['card']};border-radius:20px;padding:20px'>{u.get('avatar','👦')}</div>",unsafe_allow_html=True)
    with c2: st.markdown(f"""<div style='padding:10px 0'>
        <div style='font-family:"Baloo 2",cursive;font-size:22px;font-weight:800;color:{t["text"]}'>{u['name']}</div>
        <div style='font-size:13px;color:{t["text_muted"]};margin-top:4px'>{'🎒 Student' if u.get('role')=='student' else '👨‍👩‍👦 Parent'} • {u.get('grade','')}</div>
        <div style='font-size:12px;color:{t["text_muted"]};margin-top:2px'>📧 {u['email']}</div>
        <div style='font-size:12px;color:{t["text_muted"]};margin-top:2px'>📅 Joined {u.get('joined','')}</div>
        <div style='font-size:13px;font-weight:800;color:{get_level(u.get("stats",{}).get("xp",0))["color"]};margin-top:6px'>{get_level(u.get("stats",{}).get("xp",0))["name"]} • ⚡{u.get("stats",{}).get("xp",0)} XP</div>
    </div>""",unsafe_allow_html=True)
    st.markdown("---")
    with st.form("profile_form"):
        new_name=st.text_input("Full Name",value=u.get("name",""))
        new_grade=st.selectbox("Default Class",["-- Select --"]+LEVELS,index=LEVELS.index(u["grade"])+1 if u.get("grade","") in LEVELS else 0)
        cur_av_key=next((k for k,v in AVATARS.items() if v==u.get("avatar","👦")),list(AVATARS.keys())[0])
        new_avatar=st.selectbox("Avatar",list(AVATARS.keys()),index=list(AVATARS.keys()).index(cur_av_key))
        old_pw=st.text_input("Current Password",type="password")
        new_pw=st.text_input("New Password",type="password",placeholder="Leave blank to keep")
        cnf_pw=st.text_input("Confirm Password",type="password")
        if st.form_submit_button("💾 Save",type="primary"):
            users=load_json(USERS_FILE); eu=users[u["email"]]
            if old_pw and eu["password"]!=hash_pw(old_pw): st.error("Wrong password.")
            elif new_pw and new_pw!=cnf_pw: st.error("Passwords don't match.")
            elif new_pw and len(new_pw)<6: st.error("Min 6 chars.")
            else:
                if new_name.strip(): eu["name"]=new_name.strip()
                if new_grade!="-- Select --": eu["grade"]=new_grade
                eu["avatar"]=AVATARS[new_avatar]
                if new_pw: eu["password"]=hash_pw(new_pw)
                users[u["email"]]=eu; save_json(USERS_FILE,users); st.session_state.user=eu
                st.success("✅ Saved!"); time.sleep(.5); st.rerun()
    if st.button("🗑️ Clear Chat History"):
        hist=load_json(HISTORY_FILE); hist[u["email"]]=[]; save_json(HISTORY_FILE,hist); st.success("Cleared.")

# ─────────────────────────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    page_auth()
else:
    inject_css()
    render_sidebar()
    p = st.session_state.page
    pages = {
        "home":page_home,"chat":page_chat,"docqa":page_docqa,
        "quiz":page_quiz,"flashcards":page_flashcards,"image":page_image,
        "essay":page_essay,"tools":page_tools,"homework":page_homework,
        "exams":page_exams,"challenges":page_challenges,"groups":page_groups,
        "leaderboard":page_leaderboard,"trophies":page_trophies,
        "progress":page_progress,"history":page_history,"badges":page_badges,
        "profile":page_profile,"parent":page_parent,
    }
    if p in pages: pages[p]()
    else: page_home()
