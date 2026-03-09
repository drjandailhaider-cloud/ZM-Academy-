"""
ZM Academy 2026 — Galactic Learning Command
Streamlit App — Deploy to Streamlit Cloud

Instructions:
1. Save this file as: streamlit_app.py
2. Place it in your GitHub repo root
3. Deploy at: https://share.streamlit.io
4. No extra packages needed beyond streamlit
"""

import streamlit as st

st.set_page_config(
    page_title="ZM Academy 2026 — Galactic Learning Command",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit chrome for full immersive experience
st.markdown("""
<style>
#MainMenu{visibility:hidden;}
footer{visibility:hidden;}
header{visibility:hidden;}
.block-container{padding:0!important;max-width:100%!important;}
iframe{border:none;}
</style>
""", unsafe_allow_html=True)

HTML_APP = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ZM Academy 2026</title>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Exo+2:wght@300;400;600;700;800&display=swap" rel="stylesheet">
<style>
:root{--bg-void:#020818;--bg-panel:rgba(6,20,60,0.85);--neon-cyan:#00f5ff;--neon-blue:#0080ff;--neon-purple:#bf00ff;--neon-green:#00ff88;--neon-yellow:#ffe600;--neon-orange:#ff6600;--neon-pink:#ff0080;--neon-red:#ff2244;--text-main:#e0f4ff;--text-dim:#5588aa;--grid-line:rgba(0,245,255,0.07);--glow-c:0 0 20px rgba(0,245,255,.6),0 0 60px rgba(0,245,255,.2);--glow-p:0 0 20px rgba(191,0,255,.6),0 0 60px rgba(191,0,255,.2);--glow-g:0 0 20px rgba(0,255,136,.6),0 0 60px rgba(0,255,136,.2);}
*{margin:0;padding:0;box-sizing:border-box;}html{scroll-behavior:smooth;}
body{font-family:'Exo 2',sans-serif;background:var(--bg-void);color:var(--text-main);min-height:100vh;overflow-x:hidden;cursor:crosshair;}
#canvas-bg{position:fixed;inset:0;z-index:0;pointer-events:none;}
.grid-overlay{position:fixed;inset:0;z-index:1;background-image:linear-gradient(var(--grid-line) 1px,transparent 1px),linear-gradient(90deg,var(--grid-line) 1px,transparent 1px);background-size:60px 60px;pointer-events:none;animation:gp 6s ease-in-out infinite;}
@keyframes gp{0%,100%{opacity:.6}50%{opacity:1}}
.scanline{position:fixed;inset:0;z-index:2;background:repeating-linear-gradient(0deg,transparent,transparent 3px,rgba(0,245,255,.012) 3px,rgba(0,245,255,.012) 4px);pointer-events:none;}
.app-wrap{position:relative;z-index:10;max-width:1400px;margin:0 auto;padding:0 20px 60px;}
header{position:relative;z-index:20;text-align:center;padding:36px 20px 10px;}
.hud-top{display:flex;justify-content:space-between;align-items:center;font-family:'Orbitron',monospace;font-size:.62rem;color:var(--neon-cyan);letter-spacing:2px;margin-bottom:18px;opacity:.65;flex-wrap:wrap;gap:6px;}
.hud-dot{width:6px;height:6px;border-radius:50%;background:var(--neon-green);animation:blink 1.2s ease-in-out infinite;display:inline-block;margin-right:4px;}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.1}}
.logo-wrap{position:relative;display:inline-block;margin-bottom:10px;}
.logo-ring{position:absolute;inset:-16px;border:2px solid var(--neon-cyan);border-radius:50%;opacity:.25;animation:sr 8s linear infinite;}
.logo-ring2{position:absolute;inset:-30px;border:1px solid var(--neon-purple);border-radius:50%;opacity:.18;animation:sr 14s linear infinite reverse;}
@keyframes sr{from{transform:rotate(0)}to{transform:rotate(360deg)}}
.academy-title{font-family:'Orbitron',monospace;font-size:clamp(1.6rem,5vw,3.6rem);font-weight:900;letter-spacing:5px;background:linear-gradient(90deg,var(--neon-cyan),var(--neon-blue),var(--neon-purple),var(--neon-cyan));background-size:300% 100%;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:ts 4s linear infinite;line-height:1.1;}
@keyframes ts{0%{background-position:0%}100%{background-position:300%}}
.academy-sub{font-family:'Orbitron',monospace;font-size:clamp(.55rem,1.4vw,.8rem);letter-spacing:7px;color:var(--neon-cyan);opacity:.65;margin-top:4px;text-transform:uppercase;}
.level-selector{display:flex;justify-content:center;gap:10px;flex-wrap:wrap;margin:26px 0;}
.level-btn{font-family:'Orbitron',monospace;font-size:.62rem;font-weight:700;letter-spacing:2px;padding:10px 16px;border-radius:4px;border:1px solid;cursor:pointer;background:transparent;transition:all .25s;position:relative;overflow:hidden;}
.level-btn::before{content:'';position:absolute;inset:0;background:currentColor;opacity:0;transition:opacity .25s;}
.level-btn:hover::before,.level-btn.active::before{opacity:.14;}
.level-btn:hover,.level-btn.active{box-shadow:var(--glow-c);transform:translateY(-2px);}
.lvl-p{color:var(--neon-green);border-color:var(--neon-green);}.lvl-m{color:var(--neon-cyan);border-color:var(--neon-cyan);}.lvl-o{color:var(--neon-purple);border-color:var(--neon-purple);}.lvl-a{color:var(--neon-yellow);border-color:var(--neon-yellow);}
.char-stage{display:flex;justify-content:center;align-items:flex-end;gap:clamp(6px,2vw,18px);padding:20px 10px 0;flex-wrap:wrap;min-height:170px;}
.char-pod{display:flex;flex-direction:column;align-items:center;cursor:pointer;position:relative;transition:transform .3s cubic-bezier(.34,1.56,.64,1);}
.char-pod:hover{transform:scale(1.2) translateY(-14px);z-index:50;}
.char-holo{font-size:clamp(38px,5.5vw,68px);position:relative;z-index:2;}
.char-shadow{width:clamp(50px,7vw,80px);height:5px;border-radius:50%;background:currentColor;opacity:.35;filter:blur(5px);margin-top:-2px;}
.char-label{font-family:'Orbitron',monospace;font-size:.5rem;letter-spacing:2px;margin-top:5px;text-align:center;opacity:.8;}
.char-grade{font-size:.45rem;opacity:.5;letter-spacing:1px;}
.c1{color:var(--neon-green);}.c2{color:var(--neon-cyan);}.c3{color:var(--neon-purple);}.c4{color:var(--neon-yellow);}.c5{color:var(--neon-pink);}.c6{color:var(--neon-orange);}.c7{color:var(--neon-blue);}.c8{color:var(--neon-red);}.c9{color:#00ffdd;}.c10{color:var(--neon-yellow);}
.c1 .char-holo{filter:drop-shadow(0 0 14px var(--neon-green));}.c2 .char-holo{filter:drop-shadow(0 0 14px var(--neon-cyan));}.c3 .char-holo{filter:drop-shadow(0 0 14px var(--neon-purple));}.c4 .char-holo{filter:drop-shadow(0 0 14px var(--neon-yellow));}.c5 .char-holo{filter:drop-shadow(0 0 14px var(--neon-pink));}.c6 .char-holo{filter:drop-shadow(0 0 14px var(--neon-orange));}.c7 .char-holo{filter:drop-shadow(0 0 14px var(--neon-blue));}.c8 .char-holo{filter:drop-shadow(0 0 14px var(--neon-red));}.c9 .char-holo{filter:drop-shadow(0 0 14px #00ffdd);}.c10 .char-holo{filter:drop-shadow(0 0 14px var(--neon-yellow));}
.holo-float{animation:hf 3s ease-in-out infinite;}.holo-flicker{animation:hfl 5s ease-in-out infinite;}.holo-pulse{animation:hp 2.5s ease-in-out infinite;}.holo-scan{animation:hs 4s ease-in-out infinite;}.holo-spin{animation:hspin 6s linear infinite;}
@keyframes hf{0%,100%{transform:translateY(0)}50%{transform:translateY(-14px)}}@keyframes hfl{0%,95%,100%{opacity:1}96%{opacity:.3}97%{opacity:1}98%{opacity:.5}}@keyframes hp{0%,100%{transform:scale(1)}50%{transform:scale(1.1)}}@keyframes hs{0%,100%{filter:brightness(1)}50%{filter:brightness(1.5) hue-rotate(20deg)}}@keyframes hspin{from{transform:rotateY(0)}to{transform:rotateY(360deg)}}
.stat-pods{display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin:26px 0;}
.stat-pod{background:var(--bg-panel);border:1px solid;border-radius:6px;padding:12px 20px;text-align:center;font-family:'Orbitron',monospace;min-width:110px;position:relative;overflow:hidden;transition:all .3s;}
.stat-pod:hover{transform:translateY(-4px);}
.stat-pod::after{content:'';position:absolute;bottom:0;left:0;right:0;height:2px;background:currentColor;animation:sb 2s ease-in-out infinite;}
@keyframes sb{0%{transform:scaleX(0);transform-origin:left}50%{transform:scaleX(1);transform-origin:left}51%{transform:scaleX(1);transform-origin:right}100%{transform:scaleX(0);transform-origin:right}}
.stat-pod:nth-child(1){color:var(--neon-cyan);border-color:rgba(0,245,255,.3);}.stat-pod:nth-child(2){color:var(--neon-green);border-color:rgba(0,255,136,.3);}.stat-pod:nth-child(3){color:var(--neon-purple);border-color:rgba(191,0,255,.3);}.stat-pod:nth-child(4){color:var(--neon-yellow);border-color:rgba(255,230,0,.3);}
.stat-val{font-size:1.4rem;font-weight:900;}.stat-lbl{font-size:.52rem;letter-spacing:2px;opacity:.6;margin-top:2px;}
.section-hd{font-family:'Orbitron',monospace;font-size:clamp(.78rem,1.8vw,1rem);letter-spacing:6px;color:var(--neon-cyan);text-transform:uppercase;margin:36px 0 18px;display:flex;align-items:center;gap:14px;}
.section-hd::before,.section-hd::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,transparent,var(--neon-cyan),transparent);}
.ai-panel{background:linear-gradient(135deg,rgba(0,0,80,.9),rgba(40,0,80,.9));border:1px solid rgba(191,0,255,.4);border-radius:10px;padding:26px;margin-bottom:36px;display:flex;align-items:center;gap:22px;flex-wrap:wrap;position:relative;overflow:hidden;box-shadow:var(--glow-p);}
.ai-panel::before{content:'';position:absolute;inset:0;background:repeating-linear-gradient(45deg,transparent,transparent 40px,rgba(191,0,255,.02) 40px,rgba(191,0,255,.02) 80px);}
.ai-ava{font-size:4rem;animation:hf 3s ease-in-out infinite;filter:drop-shadow(0 0 20px var(--neon-purple));}
.ai-content{flex:1;min-width:200px;}
.ai-name{font-family:'Orbitron',monospace;font-size:1.1rem;color:var(--neon-purple);letter-spacing:4px;margin-bottom:6px;text-shadow:0 0 14px var(--neon-purple);}
.ai-tagline{color:var(--text-main);font-weight:600;font-size:.88rem;margin-bottom:10px;}
.ai-chips{display:flex;gap:7px;flex-wrap:wrap;}
.ai-chip{font-family:'Orbitron',monospace;font-size:.5rem;letter-spacing:2px;padding:4px 10px;border-radius:3px;background:rgba(191,0,255,.15);border:1px solid rgba(191,0,255,.4);color:var(--neon-purple);}
.ai-cta{font-family:'Orbitron',monospace;font-size:.7rem;letter-spacing:3px;padding:12px 24px;border-radius:5px;border:2px solid var(--neon-purple);background:rgba(191,0,255,.15);color:var(--neon-purple);cursor:pointer;transition:all .2s;white-space:nowrap;}
.ai-cta:hover{background:var(--neon-purple);color:white;box-shadow:var(--glow-p);transform:scale(1.05);}
.subject-matrix{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:14px;margin-bottom:36px;}
.sub-cell{background:var(--bg-panel);border:1px solid rgba(0,245,255,.18);border-radius:8px;padding:22px 18px;cursor:pointer;position:relative;overflow:hidden;transition:all .3s;animation:cr .5s both;}
.sub-cell:hover{border-color:var(--neon-cyan);box-shadow:var(--glow-c);transform:translateY(-4px) scale(1.02);background:rgba(0,245,255,.06);}
@keyframes cr{from{opacity:0;transform:scale(.92)}to{opacity:1;transform:scale(1)}}
.sub-cell:nth-child(1){animation-delay:.05s}.sub-cell:nth-child(2){animation-delay:.1s}.sub-cell:nth-child(3){animation-delay:.15s}.sub-cell:nth-child(4){animation-delay:.2s}.sub-cell:nth-child(5){animation-delay:.25s}.sub-cell:nth-child(6){animation-delay:.3s}.sub-cell:nth-child(7){animation-delay:.35s}.sub-cell:nth-child(8){animation-delay:.4s}
.sub-cell::before{content:'';position:absolute;top:8px;left:8px;width:12px;height:12px;border-top:2px solid var(--neon-cyan);border-left:2px solid var(--neon-cyan);opacity:.5;}
.sub-cell::after{content:'';position:absolute;bottom:8px;right:8px;width:12px;height:12px;border-bottom:2px solid var(--neon-cyan);border-right:2px solid var(--neon-cyan);opacity:.5;}
.sub-icon{font-size:2.4rem;display:block;margin-bottom:8px;}
.sub-name{font-family:'Orbitron',monospace;font-size:.78rem;font-weight:700;letter-spacing:2px;color:var(--neon-cyan);margin-bottom:5px;}
.sub-desc{font-size:.75rem;color:var(--text-dim);line-height:1.5;}
.sub-tag{position:absolute;top:9px;right:9px;font-family:'Orbitron',monospace;font-size:.48rem;letter-spacing:2px;padding:3px 7px;border-radius:3px;}
.tag-hot{background:rgba(255,102,0,.2);color:var(--neon-orange);border:1px solid var(--neon-orange);}.tag-new{background:rgba(0,255,136,.1);color:var(--neon-green);border:1px solid var(--neon-green);}.tag-adv{background:rgba(191,0,255,.1);color:var(--neon-purple);border:1px solid var(--neon-purple);}
.sub-prog{margin-top:10px;background:rgba(0,245,255,.1);border-radius:2px;height:3px;overflow:hidden;}
.sub-prog-bar{height:100%;background:linear-gradient(90deg,var(--neon-cyan),var(--neon-purple));border-radius:2px;box-shadow:0 0 8px var(--neon-cyan);}
.quiz-module{background:var(--bg-panel);border:1px solid rgba(0,245,255,.28);border-radius:10px;padding:28px;margin-bottom:36px;position:relative;overflow:hidden;}
.quiz-module::before{content:'NEURAL QUIZ v3.7';position:absolute;top:12px;right:16px;font-family:'Orbitron',monospace;font-size:.52rem;letter-spacing:3px;color:var(--neon-cyan);opacity:.35;}
.quiz-lvl-tabs{display:flex;gap:8px;margin-bottom:18px;flex-wrap:wrap;}
.qlvl{font-family:'Orbitron',monospace;font-size:.58rem;letter-spacing:2px;padding:6px 14px;border-radius:3px;border:1px solid rgba(0,245,255,.25);color:var(--text-dim);cursor:pointer;transition:all .2s;}
.qlvl:hover,.qlvl.active{color:var(--neon-cyan);border-color:var(--neon-cyan);background:rgba(0,245,255,.08);box-shadow:0 0 10px rgba(0,245,255,.2);}
.quiz-label{font-family:'Orbitron',monospace;font-size:.58rem;letter-spacing:3px;color:var(--neon-purple);margin-bottom:10px;opacity:.8;}
.quiz-q{font-size:1rem;font-weight:700;color:var(--text-main);background:rgba(0,245,255,.05);border:1px solid rgba(0,245,255,.18);border-radius:6px;padding:16px 20px;margin-bottom:16px;line-height:1.55;}
.quiz-opts{display:grid;grid-template-columns:1fr 1fr;gap:10px;}
.qopt{background:rgba(0,245,255,.04);border:1px solid rgba(0,245,255,.18);border-radius:6px;padding:13px 16px;color:var(--text-main);font-family:'Exo 2',sans-serif;font-weight:600;font-size:.88rem;cursor:pointer;transition:all .2s;text-align:left;}
.qopt:hover{border-color:var(--neon-cyan);background:rgba(0,245,255,.1);box-shadow:0 0 12px rgba(0,245,255,.2);transform:translateX(4px);}
.qopt.correct{border-color:var(--neon-green);background:rgba(0,255,136,.12);box-shadow:var(--glow-g);animation:cf .4s;}
.qopt.wrong{border-color:var(--neon-red);background:rgba(255,34,68,.12);animation:ws .4s;}
@keyframes cf{0%,100%{transform:none}50%{transform:scale(1.03)}}@keyframes ws{0%,100%{transform:none}25%,75%{transform:translateX(-5px)}50%{transform:translateX(5px)}}
.quiz-feed{margin-top:12px;font-family:'Orbitron',monospace;font-size:.65rem;letter-spacing:2px;height:20px;transition:all .3s;}
.missions{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:14px;margin-bottom:36px;}
.mission-card{background:var(--bg-panel);border:1px solid rgba(0,245,255,.12);border-radius:8px;padding:20px;position:relative;overflow:hidden;transition:all .3s;cursor:pointer;}
.mission-card:hover{border-color:currentColor;transform:translateY(-3px);box-shadow:0 0 20px rgba(0,245,255,.2);}
.mission-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,currentColor,transparent);opacity:.6;}
.mc-p{color:var(--neon-green);}.mc-m{color:var(--neon-cyan);}.mc-o{color:var(--neon-purple);}.mc-a{color:var(--neon-yellow);}
.mission-icon{font-size:2rem;margin-bottom:8px;display:block;}
.mission-label{font-family:'Orbitron',monospace;font-size:.55rem;letter-spacing:3px;opacity:.65;margin-bottom:3px;}
.mission-title{font-size:.95rem;font-weight:800;color:var(--text-main);margin-bottom:5px;}
.mission-desc{font-size:.78rem;color:var(--text-dim);line-height:1.5;margin-bottom:10px;}
.mission-reward{display:inline-flex;align-items:center;gap:5px;font-family:'Orbitron',monospace;font-size:.55rem;letter-spacing:2px;padding:4px 10px;border-radius:3px;background:rgba(0,0,0,.3);border:1px solid currentColor;}
.mp{margin-top:10px;display:flex;align-items:center;gap:8px;font-family:'Orbitron',monospace;font-size:.55rem;color:var(--text-dim);}
.mp-bar{flex:1;height:3px;background:rgba(255,255,255,.08);border-radius:2px;overflow:hidden;}
.mp-fill{height:100%;border-radius:2px;background:currentColor;box-shadow:0 0 6px currentColor;}
.leaderboard{background:var(--bg-panel);border:1px solid rgba(0,245,255,.18);border-radius:10px;padding:26px;margin-bottom:36px;position:relative;overflow:hidden;}
.leaderboard::before{content:'TOP CADETS // RANKING';position:absolute;top:13px;right:18px;font-family:'Orbitron',monospace;font-size:.52rem;letter-spacing:4px;color:var(--neon-cyan);opacity:.3;}
.lb-row{display:flex;align-items:center;gap:12px;padding:11px 13px;border-radius:6px;margin-bottom:7px;border:1px solid transparent;transition:all .25s;cursor:pointer;}
.lb-row:hover{background:rgba(0,245,255,.04);border-color:rgba(0,245,255,.18);transform:translateX(6px);}
.lb-rank{font-family:'Orbitron',monospace;font-size:.95rem;font-weight:900;width:34px;text-align:center;}
.r1{color:var(--neon-yellow);text-shadow:0 0 12px var(--neon-yellow);}.r2{color:#c0c0c0;}.r3{color:#cd7f32;}.rx{color:var(--text-dim);}
.lb-ava{font-size:1.7rem;}.lb-info{flex:1;}.lb-name{font-weight:700;font-size:.88rem;color:var(--text-main);}.lb-grade{font-family:'Orbitron',monospace;font-size:.5rem;color:var(--text-dim);letter-spacing:2px;}
.lb-score{font-family:'Orbitron',monospace;font-size:.88rem;color:var(--neon-cyan);font-weight:700;}
.lb-bw{width:72px;height:3px;background:rgba(255,255,255,.07);border-radius:2px;overflow:hidden;}
.lb-b{height:100%;background:linear-gradient(90deg,var(--neon-cyan),var(--neon-purple));border-radius:2px;}
.feature-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px;margin-bottom:36px;}
.feat-card{background:var(--bg-panel);border:1px solid rgba(0,245,255,.1);border-radius:8px;padding:22px;transition:all .3s;animation:cr .5s both;position:relative;overflow:hidden;}
.feat-card:hover{transform:translateY(-4px);border-color:var(--neon-purple);box-shadow:var(--glow-p);}
.feat-card::after{content:'';position:absolute;bottom:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,var(--neon-purple),transparent);opacity:.4;}
.feat-icon{font-size:2rem;margin-bottom:10px;display:block;}
.feat-name{font-family:'Orbitron',monospace;font-size:.7rem;letter-spacing:2px;color:var(--neon-purple);margin-bottom:7px;}
.feat-desc{font-size:.8rem;color:var(--text-dim);line-height:1.55;}
.feat-badge{display:inline-block;margin-top:9px;font-family:'Orbitron',monospace;font-size:.48rem;letter-spacing:2px;padding:3px 9px;border-radius:3px;background:rgba(191,0,255,.12);color:var(--neon-purple);border:1px solid rgba(191,0,255,.3);}
footer{text-align:center;padding:26px 20px;border-top:1px solid rgba(0,245,255,.08);position:relative;z-index:10;}
.footer-logo{font-family:'Orbitron',monospace;font-size:.65rem;letter-spacing:6px;color:var(--neon-cyan);opacity:.45;margin-bottom:6px;}
.footer-copy{font-size:.7rem;color:var(--text-dim);letter-spacing:2px;}
#holo-popup{position:fixed;pointer-events:none;z-index:1000;opacity:0;transition:opacity .2s;}
.popup-box{background:rgba(2,8,30,.95);border:1px solid var(--neon-cyan);border-radius:8px;padding:12px 18px;font-family:'Orbitron',monospace;font-size:.65rem;color:var(--neon-cyan);letter-spacing:2px;box-shadow:var(--glow-c);max-width:220px;text-align:center;line-height:1.7;white-space:pre-line;}
.particle{position:fixed;pointer-events:none;z-index:500;width:6px;height:6px;border-radius:50%;animation:pb 1.2s ease-out forwards;}
@keyframes pb{0%{transform:translate(0,0) scale(1);opacity:1}100%{transform:translate(var(--dx),var(--dy)) scale(0);opacity:0}}
.fab-btn{position:fixed;bottom:26px;right:26px;z-index:100;width:62px;height:62px;border-radius:50%;background:linear-gradient(135deg,var(--neon-cyan),var(--neon-purple));border:none;cursor:pointer;font-size:1.4rem;box-shadow:var(--glow-c);transition:all .2s;display:flex;align-items:center;justify-content:center;animation:fp 3s ease-in-out infinite;}
.fab-btn:hover{transform:scale(1.12) rotate(20deg);}
@keyframes fp{0%,100%{box-shadow:var(--glow-c)}50%{box-shadow:var(--glow-p)}}
@media(max-width:600px){.quiz-opts{grid-template-columns:1fr;}.ai-panel{flex-direction:column;text-align:center;}}
</style>
</head>
<body>
<canvas id="canvas-bg"></canvas>
<div class="grid-overlay"></div>
<div class="scanline"></div>
<div id="holo-popup"><div class="popup-box" id="popup-text"></div></div>
<div class="app-wrap">
<header>
  <div class="hud-top">
    <span><div class="hud-dot"></div> ALL SYSTEMS ONLINE</span>
    <span>ZM-ACADEMY // COMMAND-CENTER</span>
    <span id="live-clock">--:--:--</span>
    <span>KARACHI // PKT+5</span>
  </div>
  <div class="logo-wrap">
    <div class="logo-ring"></div><div class="logo-ring2"></div>
    <h1 class="academy-title">ZM ACADEMY 2026</h1>
  </div>
  <div class="academy-sub">⬡ Galactic Learning Command ⬡ Class I → A-Level ⬡</div>
</header>
<div class="level-selector">
  <button class="level-btn lvl-p active" onclick="selectLevel(this,'p')">⬡ CLASS 1-5 · PRIMARY</button>
  <button class="level-btn lvl-m" onclick="selectLevel(this,'m')">⬡ CLASS 6-8 · MIDDLE</button>
  <button class="level-btn lvl-o" onclick="selectLevel(this,'o')">⬡ O-LEVEL · CADET</button>
  <button class="level-btn lvl-a" onclick="selectLevel(this,'a')">⬡ A-LEVEL · COMMANDER</button>
</div>
<div class="char-stage" id="charStage">
  <div class="char-pod c1 holo-float" onclick="charHit(this,'NOVA SAYS:\\nNever stop asking WHY!','CLASS 1-2 // AGE 5-7')" data-lv="p"><div class="char-holo">&#129498;</div><div class="char-shadow"></div><div class="char-label">NOVA<br><span class="char-grade">CLASS 1-2</span></div></div>
  <div class="char-pod c2 holo-flicker" onclick="charHit(this,'COSMO SAYS:\\nMath is the language of stars!','CLASS 3-4 // AGE 8-9')" data-lv="p"><div class="char-holo">&#129302;</div><div class="char-shadow"></div><div class="char-label">COSMO<br><span class="char-grade">CLASS 3-4</span></div></div>
  <div class="char-pod c3 holo-pulse" onclick="charHit(this,'LUNA SAYS:\\nEvery experiment reveals a secret!','CLASS 5 // AGE 10')" data-lv="p"><div class="char-holo">&#129516;</div><div class="char-shadow"></div><div class="char-label">LUNA<br><span class="char-grade">CLASS 5</span></div></div>
  <div class="char-pod c4 holo-scan" onclick="charHit(this,'VOLT SAYS:\\nCode the future you imagine!','CLASS 6-7 // AGE 11-12')" data-lv="m"><div class="char-holo">&#9889;</div><div class="char-shadow"></div><div class="char-label">VOLT<br><span class="char-grade">CLASS 6-7</span></div></div>
  <div class="char-pod c5 holo-float" onclick="charHit(this,'AXIOM SAYS:\\nLogic is your superpower!','CLASS 8 // AGE 13')" data-lv="m"><div class="char-holo">&#129470;</div><div class="char-shadow"></div><div class="char-label">AXIOM<br><span class="char-grade">CLASS 8</span></div></div>
  <div class="char-pod c6 holo-flicker" onclick="charHit(this,'NEXUS SAYS:\\nDepth of knowledge = true power.','O-LEVEL Y1 // AGE 14-15')" data-lv="o"><div class="char-holo">&#128301;</div><div class="char-shadow"></div><div class="char-label">NEXUS<br><span class="char-grade">O-LEVEL Y1</span></div></div>
  <div class="char-pod c7 holo-pulse" onclick="charHit(this,'CIPHER SAYS:\\nMaster concepts. Ace the exams.','O-LEVEL Y2 // AGE 15-16')" data-lv="o"><div class="char-holo">&#129504;</div><div class="char-shadow"></div><div class="char-label">CIPHER<br><span class="char-grade">O-LEVEL Y2</span></div></div>
  <div class="char-pod c8 holo-scan" onclick="charHit(this,'QUASAR SAYS:\\nThink critically. Lead fearlessly.','A-LEVEL AS // AGE 16-17')" data-lv="a"><div class="char-holo">&#9883;&#65039;</div><div class="char-shadow"></div><div class="char-label">QUASAR<br><span class="char-grade">A-LEVEL AS</span></div></div>
  <div class="char-pod c9 holo-float" onclick="charHit(this,'ZENITH SAYS:\\nYou are at the top. Keep climbing.','A-LEVEL A2 // AGE 17-18')" data-lv="a"><div class="char-holo">&#127776;</div><div class="char-shadow"></div><div class="char-label">ZENITH<br><span class="char-grade">A-LEVEL A2</span></div></div>
  <div class="char-pod c10 holo-spin" onclick="charHit(this,'ZAP SAYS:\\nThe ZM Champion awaits YOU!','ALL LEVELS // MASCOT')" data-lv="all"><div class="char-holo">&#127942;</div><div class="char-shadow"></div><div class="char-label">ZAP<br><span class="char-grade">MASCOT</span></div></div>
</div>
<div class="stat-pods">
  <div class="stat-pod"><div class="stat-val">4,820</div><div class="stat-lbl">STAR POINTS</div></div>
  <div class="stat-pod"><div class="stat-val">42</div><div class="stat-lbl">DAY STREAK</div></div>
  <div class="stat-pod"><div class="stat-val">LVL 9</div><div class="stat-lbl">COMMANDER</div></div>
  <div class="stat-pod"><div class="stat-val">18</div><div class="stat-lbl">BADGES WON</div></div>
</div>
<div class="ai-panel">
  <div class="ai-ava">&#129302;</div>
  <div class="ai-content">
    <div class="ai-name">COSMO — AI TUTOR UNIT</div>
    <div class="ai-tagline">Your AI companion adapts to your grade level — from Class 1 counting to A-Level Calculus!</div>
    <div class="ai-chips"><span class="ai-chip">ADAPTIVE ENGINE</span><span class="ai-chip">VOICE MODE</span><span class="ai-chip">O/A LEVEL PREP</span><span class="ai-chip">URDU + ENGLISH</span><span class="ai-chip">24/7 ONLINE</span></div>
  </div>
  <button class="ai-cta" onclick="burst(event,'#bf00ff')">&#11045; ACTIVATE COSMO</button>
</div>
<div class="section-hd">&#11045; SUBJECT MATRIX</div>
<div class="subject-matrix">
  <div class="sub-cell" onclick="openSub(event,'Mathematics')"><span class="sub-tag tag-hot">HOT</span><span class="sub-icon">&#8721;</span><div class="sub-name">MATHEMATICS</div><div class="sub-desc">Algebra · Calculus · Statistics · Pure Maths</div><div class="sub-prog"><div class="sub-prog-bar" style="width:78%"></div></div></div>
  <div class="sub-cell" onclick="openSub(event,'Physics')"><span class="sub-tag tag-adv">ADV</span><span class="sub-icon">&#9883;&#65039;</span><div class="sub-name">PHYSICS</div><div class="sub-desc">Mechanics · Waves · Quantum · Relativity</div><div class="sub-prog"><div class="sub-prog-bar" style="width:55%"></div></div></div>
  <div class="sub-cell" onclick="openSub(event,'Chemistry')"><span class="sub-icon">&#9879;&#65039;</span><div class="sub-name">CHEMISTRY</div><div class="sub-desc">Organic · Inorganic · Analytical · Biochem</div><div class="sub-prog"><div class="sub-prog-bar" style="width:48%"></div></div></div>
  <div class="sub-cell" onclick="openSub(event,'Biology')"><span class="sub-tag tag-new">NEW</span><span class="sub-icon">&#129516;</span><div class="sub-name">BIOLOGY</div><div class="sub-desc">Cells · Genetics · Ecology · Anatomy</div><div class="sub-prog"><div class="sub-prog-bar" style="width:62%"></div></div></div>
  <div class="sub-cell" onclick="openSub(event,'Computer Science')"><span class="sub-tag tag-hot">HOT</span><span class="sub-icon">&#128187;</span><div class="sub-name">COMPUTER SCI</div><div class="sub-desc">Python · Algorithms · AI · Data Structures</div><div class="sub-prog"><div class="sub-prog-bar" style="width:35%"></div></div></div>
  <div class="sub-cell" onclick="openSub(event,'English')"><span class="sub-icon">&#128220;</span><div class="sub-name">ENGLISH LANG</div><div class="sub-desc">Grammar · Writing · Literature · CIE</div><div class="sub-prog"><div class="sub-prog-bar" style="width:88%"></div></div></div>
  <div class="sub-cell" onclick="openSub(event,'Islamiat')"><span class="sub-icon">&#128332;</span><div class="sub-name">ISLAMIAT &amp; PAK</div><div class="sub-desc">History · Geography · Civics · Values</div><div class="sub-prog"><div class="sub-prog-bar" style="width:70%"></div></div></div>
  <div class="sub-cell" onclick="openSub(event,'Economics')"><span class="sub-tag tag-adv">ADV</span><span class="sub-icon">&#128200;</span><div class="sub-name">ECONOMICS</div><div class="sub-desc">Micro · Macro · Business · Markets</div><div class="sub-prog"><div class="sub-prog-bar" style="width:42%"></div></div></div>
</div>
<div class="section-hd">&#11045; NEURAL QUIZ MODULE</div>
<div class="quiz-module">
  <div class="quiz-lvl-tabs">
    <div class="qlvl active" onclick="setQL(this,0)">CLASS 1-5</div>
    <div class="qlvl" onclick="setQL(this,1)">CLASS 6-8</div>
    <div class="qlvl" onclick="setQL(this,2)">O-LEVEL</div>
    <div class="qlvl" onclick="setQL(this,3)">A-LEVEL</div>
  </div>
  <div class="quiz-label" id="qlabel">&#11045; PRIMARY CIRCUIT</div>
  <div class="quiz-q" id="quizQ"></div>
  <div class="quiz-opts" id="quizOpts"></div>
  <div class="quiz-feed" id="quizFeed"></div>
</div>
<div class="section-hd">&#11045; MISSION CONTROL</div>
<div class="missions">
  <div class="mission-card mc-p" onclick="burst(event,'#00ff88')"><span class="mission-icon">&#129529;</span><div class="mission-label">PRIMARY // CLASS 1-5</div><div class="mission-title">Puzzle Master Challenge</div><div class="mission-desc">Complete 5 Math puzzles to unlock the Puzzle Master badge!</div><div class="mission-reward">&#127873; +150 XP · PUZZLE BADGE</div><div class="mp"><span>3/5</span><div class="mp-bar"><div class="mp-fill" style="width:60%"></div></div><span>60%</span></div></div>
  <div class="mission-card mc-m" onclick="burst(event,'#00f5ff')"><span class="mission-icon">&#128300;</span><div class="mission-label">CADET // CLASS 6-8</div><div class="mission-title">Science Lab Sprint</div><div class="mission-desc">Finish 3 Science simulations to level up your lab rank!</div><div class="mission-reward">&#127873; +200 XP · LAB BADGE</div><div class="mp"><span>1/3</span><div class="mp-bar"><div class="mp-fill" style="width:33%"></div></div><span>33%</span></div></div>
  <div class="mission-card mc-o" onclick="burst(event,'#bf00ff')"><span class="mission-icon">&#128208;</span><div class="mission-label">O-LEVEL MISSION</div><div class="mission-title">Past Paper Blitz</div><div class="mission-desc">Attempt 2 CIE past paper questions with AI explanations!</div><div class="mission-reward">&#127873; +300 XP · SCHOLAR BADGE</div><div class="mp"><span>0/2</span><div class="mp-bar"><div class="mp-fill" style="width:0%"></div></div><span>0%</span></div></div>
  <div class="mission-card mc-a" onclick="burst(event,'#ffe600')"><span class="mission-icon">&#9883;&#65039;</span><div class="mission-label">A-LEVEL MISSION</div><div class="mission-title">University Readiness</div><div class="mission-desc">Complete the UCAS module and mock university interview!</div><div class="mission-reward">&#127873; +500 XP · COMMANDER BADGE</div><div class="mp"><span>2/4</span><div class="mp-bar"><div class="mp-fill" style="width:50%"></div></div><span>50%</span></div></div>
</div>
<div class="section-hd">&#11045; COMMAND RANKING</div>
<div class="leaderboard">
  <div class="lb-row"><span class="lb-rank r1">01</span><span class="lb-ava">&#127776;</span><div class="lb-info"><div class="lb-name">Zara Khan</div><div class="lb-grade">A-LEVEL A2 // ZENITH CREW</div></div><div class="lb-bw"><div class="lb-b" style="width:95%"></div></div><span class="lb-score">9,820</span></div>
  <div class="lb-row"><span class="lb-rank r2">02</span><span class="lb-ava">&#9883;&#65039;</span><div class="lb-info"><div class="lb-name">Ahmed Ali</div><div class="lb-grade">O-LEVEL Y2 // CIPHER CREW</div></div><div class="lb-bw"><div class="lb-b" style="width:88%"></div></div><span class="lb-score">8,610</span></div>
  <div class="lb-row"><span class="lb-rank r3">03</span><span class="lb-ava">&#129504;</span><div class="lb-info"><div class="lb-name">Sara Malik</div><div class="lb-grade">A-LEVEL AS // QUASAR CREW</div></div><div class="lb-bw"><div class="lb-b" style="width:82%"></div></div><span class="lb-score">8,200</span></div>
  <div class="lb-row"><span class="lb-rank rx">04</span><span class="lb-ava">&#128301;</span><div class="lb-info"><div class="lb-name">Omar Raza</div><div class="lb-grade">O-LEVEL Y1 // NEXUS CREW</div></div><div class="lb-bw"><div class="lb-b" style="width:74%"></div></div><span class="lb-score">7,450</span></div>
  <div class="lb-row"><span class="lb-rank rx">05</span><span class="lb-ava">&#9889;</span><div class="lb-info"><div class="lb-name">Fatima Shah</div><div class="lb-grade">CLASS 7 // VOLT CREW</div></div><div class="lb-bw"><div class="lb-b" style="width:66%"></div></div><span class="lb-score">6,700</span></div>
</div>
<div class="section-hd">&#11045; UPGRADE MODULES</div>
<div class="feature-grid">
  <div class="feat-card" style="animation-delay:.05s"><span class="feat-icon">&#129504;</span><div class="feat-name">ADAPTIVE AI ENGINE</div><div class="feat-desc">Learns your weak zones and auto-generates targeted drills. Gets smarter every session.</div><span class="feat-badge">AI POWERED</span></div>
  <div class="feat-card" style="animation-delay:.1s"><span class="feat-icon">&#127918;</span><div class="feat-name">GAMIFIED XP SYSTEM</div><div class="feat-desc">Earn XP, level up characters, unlock galaxy zones. Learning feels like an RPG!</div><span class="feat-badge">GAMIFICATION</span></div>
  <div class="feat-card" style="animation-delay:.15s"><span class="feat-icon">&#128225;</span><div class="feat-name">LIVE BATTLE ARENA</div><div class="feat-desc">Real-time quiz battles vs classmates or global students. Climb the galactic ranks!</div><span class="feat-badge">MULTIPLAYER</span></div>
  <div class="feat-card" style="animation-delay:.2s"><span class="feat-icon">&#128506;&#65039;</span><div class="feat-name">GALAXY LEARNING MAP</div><div class="feat-desc">Each planet = a subject. Conquer planets to unlock new solar systems!</div><span class="feat-badge">WORLD MAP</span></div>
  <div class="feat-card" style="animation-delay:.25s"><span class="feat-icon">&#128196;</span><div class="feat-name">PAST PAPER VAULT</div><div class="feat-desc">Full CIE O/A-Level archive with AI-powered analysis and mark schemes.</div><span class="feat-badge">O/A LEVEL</span></div>
  <div class="feat-card" style="animation-delay:.3s"><span class="feat-icon">&#127897;&#65039;</span><div class="feat-name">HOLO-VOICE TUTOR</div><div class="feat-desc">Speak in Urdu or English — get instant voice explanations from your character guide.</div><span class="feat-badge">VOICE AI</span></div>
  <div class="feat-card" style="animation-delay:.35s"><span class="feat-icon">&#128106;</span><div class="feat-name">PARENT COMMAND HQ</div><div class="feat-desc">Live dashboards and weekly AI-generated progress reports sent to parents.</div><span class="feat-badge">FAMILY PORTAL</span></div>
  <div class="feat-card" style="animation-delay:.4s"><span class="feat-icon">&#127942;</span><div class="feat-name">INTERSTELLAR OLYMPIAD</div><div class="feat-desc">Monthly national tournaments. Scholarships for top ranked cadets!</div><span class="feat-badge">COMPETITION</span></div>
</div>
</div>
<footer>
  <div class="footer-logo">&#11045; ZM ACADEMY 2026 &#11045; GALACTIC LEARNING COMMAND &#11045; ALL SYSTEMS OPERATIONAL &#11045;</div>
  <div class="footer-copy">CLASS I &#8594; A-LEVEL · KARACHI, PAKISTAN &#127477;&#127472; · MISSION: EDUCATE THE UNIVERSE</div>
</footer>
<button class="fab-btn" onclick="burst(event,'#00f5ff')" title="Energy Burst!">&#9889;</button>
<script>
const cv=document.getElementById('canvas-bg'),ctx=cv.getContext('2d');
let W,H,stars=[],nebulae=[];
function resize(){W=cv.width=window.innerWidth;H=cv.height=window.innerHeight;}
resize();window.addEventListener('resize',resize);
for(let i=0;i<240;i++)stars.push({x:Math.random(),y:Math.random(),r:.2+Math.random()*1.6,s:.2+Math.random()*.8,t:Math.random()*Math.PI*2,sp:.005+Math.random()*.015,c:['#00f5ff','#ffffff','#bf00ff','#00ff88','#ffe600'][Math.floor(Math.random()*5)]});
for(let i=0;i<6;i++)nebulae.push({x:Math.random(),y:Math.random(),r:120+Math.random()*220,c:['rgba(0,128,255,.04)','rgba(191,0,255,.04)','rgba(0,255,136,.03)','rgba(255,102,0,.03)','rgba(0,245,255,.03)','rgba(255,0,128,.03)'][i]});
function drawBG(){ctx.clearRect(0,0,W,H);nebulae.forEach(n=>{const g=ctx.createRadialGradient(n.x*W,n.y*H,0,n.x*W,n.y*H,n.r);g.addColorStop(0,n.c);g.addColorStop(1,'transparent');ctx.fillStyle=g;ctx.beginPath();ctx.arc(n.x*W,n.y*H,n.r,0,Math.PI*2);ctx.fill();});stars.forEach(s=>{s.t+=s.sp;const a=.3+.7*Math.abs(Math.sin(s.t));ctx.beginPath();ctx.arc(s.x*W,s.y*H,s.r,0,Math.PI*2);ctx.fillStyle=s.c;ctx.globalAlpha=a;ctx.fill();});ctx.globalAlpha=1;requestAnimationFrame(drawBG);}
drawBG();
function tick(){const d=new Date();document.getElementById('live-clock').textContent=d.toTimeString().slice(0,8)+' PKT';}
tick();setInterval(tick,1000);
const popup=document.getElementById('holo-popup'),popupText=document.getElementById('popup-text');
function showPopup(text,x,y){popupText.textContent=text;popup.style.left=Math.min(x+16,window.innerWidth-250)+'px';popup.style.top=Math.max(y-90,10)+'px';popup.style.opacity='1';clearTimeout(popup._t);popup._t=setTimeout(()=>{popup.style.opacity='0';},2800);}
function charHit(el,msg,grade){const r=el.getBoundingClientRect();showPopup('[ '+grade+' ]\\n'+msg,r.left,r.top);burst({clientX:r.left+r.width/2,clientY:r.top},'#00f5ff');}
function selectLevel(btn,level){document.querySelectorAll('.level-btn').forEach(b=>b.classList.remove('active'));btn.classList.add('active');document.querySelectorAll('.char-pod').forEach(p=>{const pl=p.dataset.lv;const show=pl===level||pl==='all';p.style.opacity=show?'1':'0.18';p.style.transform=show?'':'scale(.8)';p.style.transition='all .4s';});}
const QUIZZES=[{label:'&#11045; PRIMARY CIRCUIT — CLASS 1-5',qs:[{q:'&#128290; What is 9 x 7?',opts:['54','63','72','56'],ans:1},{q:'&#127757; Which is the largest planet?',opts:['Earth','Saturn','Jupiter','Neptune'],ans:2},{q:'&#128218; How many vowels in English?',opts:['4','5','6','7'],ans:1},{q:'&#128290; What is 144 / 12?',opts:['11','13','12','10'],ans:2}]},{label:'&#11045; CADET CIRCUIT — CLASS 6-8',qs:[{q:'&#9879;&#65039; Chemical symbol for water?',opts:['WO','H2O','HO2','OW'],ans:1},{q:'&#8721; Solve: 3x+7=22. Find x.',opts:['4','5','6','7'],ans:1},{q:'&#127757; Pakistan independence year?',opts:['1946','1947','1948','1945'],ans:1},{q:'&#9889; Speed of light approx?',opts:['3x10^7','3x10^8','3x10^9','3x10^6'],ans:1}]},{label:'&#11045; O-LEVEL CIRCUIT — CIE PREP',qs:[{q:'&#9883;&#65039; Atomic number of Carbon?',opts:['4','6','8','12'],ans:1},{q:'&#128208; Gradient of y=3x2 at x=2?',opts:['6','12','9','3'],ans:1},{q:'&#129516; What does mRNA stand for?',opts:["Messenger RNA","Mitochondrial RNA","Membrane RNA","Micro RNA"],ans:0},{q:'&#128161; What is Ohms Law?',opts:["V=IR","F=ma","E=mc2","P=IV"],ans:0}]},{label:'&#11045; A-LEVEL CIRCUIT — COMMANDER TIER',qs:[{q:'&#9883;&#65039; PV=nRT is called?',opts:["Boyle's Law","Charles' Law","Ideal Gas Law","Avogadro's Law"],ans:2},{q:'&#8747; What is integral of 2x dx?',opts:['2x2','x2+C','2x+C','x2'],ans:1},{q:'&#128161; Ceteris paribus means?',opts:['All else equal','Supply & demand','Price equilibrium','Market failure'],ans:0},{q:'&#129516; DNA replication occurs in?',opts:['G1 phase','S phase','G2 phase','M phase'],ans:1}]}];
let qLevel=0,qIdx=0,qDone=false;
function setQL(btn,level){document.querySelectorAll('.qlvl').forEach(b=>b.classList.remove('active'));btn.classList.add('active');qLevel=level;qIdx=0;renderQ();}
function renderQ(){qDone=false;const s=QUIZZES[qLevel],q=s.qs[qIdx%s.qs.length];document.getElementById('qlabel').textContent=s.label;document.getElementById('quizQ').innerHTML=q.q;document.getElementById('quizFeed').textContent='';const o=document.getElementById('quizOpts');o.innerHTML='';q.opts.forEach((opt,i)=>{const b=document.createElement('button');b.className='qopt';b.textContent=opt;b.onclick=()=>checkQ(b,i===q.ans);o.appendChild(b);});}
function checkQ(btn,correct){if(qDone)return;qDone=true;document.querySelectorAll('.qopt').forEach(b=>b.disabled=true);const feed=document.getElementById('quizFeed');if(correct){btn.classList.add('correct');feed.textContent='CORRECT — NEURAL XP +50 AWARDED';feed.style.color='var(--neon-green)';burst({clientX:btn.getBoundingClientRect().left+60,clientY:btn.getBoundingClientRect().top},'#00ff88');setTimeout(()=>{qIdx++;renderQ();},1700);}else{btn.classList.add('wrong');feed.textContent='INCORRECT — RECALIBRATING NEURAL LINK...';feed.style.color='var(--neon-red)';setTimeout(()=>{qIdx++;renderQ();},1900);}}
function openSub(e,name){showPopup('&#11045; LOADING:\\n'+name.toUpperCase(),e.clientX,e.clientY);burst(e,'#00f5ff');}
const PC=['#00f5ff','#bf00ff','#00ff88','#ffe600','#ff6600','#ff0080'];
function burst(e,col){for(let i=0;i<20;i++){const p=document.createElement('div');p.className='particle';const a=Math.random()*Math.PI*2,d=60+Math.random()*130;p.style.cssText='left:'+e.clientX+'px;top:'+e.clientY+'px;background:'+(col||PC[Math.floor(Math.random()*PC.length)])+';box-shadow:0 0 8px '+(col||'#00f5ff')+';--dx:'+Math.cos(a)*d+'px;--dy:'+Math.sin(a)*d+'px;animation-duration:'+(0.7+Math.random()*0.7)+'s;';document.body.appendChild(p);setTimeout(()=>p.remove(),1500);}}
renderQ();
</script>
</body>
</html>"""

# Render the full-screen app
st.components.v1.html(HTML_APP, height=4200, scrolling=True)
