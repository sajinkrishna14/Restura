import streamlit as st

def apply_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
        :root {
          --green: #246b50;
          --green-dark: #174936;
          --green-soft: #eaf3ed;
          --ink: #202a24;
          --muted: #69766e;
          --line: #e1e7e2;
          --paper: #ffffff;
          --page: #f6f8f6;
        }
        html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
        .stApp { background: var(--page); color: var(--ink); }
        header[data-testid="stHeader"] { background: transparent; }
        #MainMenu, footer { visibility: hidden; }
        .block-container { max-width: 1320px; padding-top: 1.4rem; padding-bottom: 2.5rem; }
        .brand-row { display:flex; align-items:center; justify-content:space-between; gap:1rem; margin-bottom:1.25rem; }
        .brand { font-size:1.55rem; font-weight:700; letter-spacing:-.8px; color:var(--green-dark); }
        .brand-dot { color:#78a58b; }
        .top-label { font-size:.72rem; color:var(--muted); letter-spacing:1.5px; text-transform:uppercase; font-weight:700; }
        .hero { background:var(--paper); border:1px solid var(--line); border-radius:18px; padding:26px 28px; margin-bottom:1.5rem; }
        .hero-kicker { color:var(--green); font-size:.72rem; font-weight:700; letter-spacing:1.5px; text-transform:uppercase; }
        .hero-title { font-size:clamp(1.8rem,3vw,2.45rem); line-height:1.15; letter-spacing:-1.2px; color:var(--green-dark); margin:.45rem 0 .55rem; font-weight:700; }
        .hero-copy { color:var(--muted); font-size:.98rem; margin:0; }
        .section-head { margin:.35rem 0 1rem; }
        .section-number { font-size:.72rem; letter-spacing:1.3px; font-weight:700; color:var(--green); }
        .section-name { font-size:1.15rem; font-weight:700; letter-spacing:-.3px; color:var(--ink); margin:.15rem 0 .2rem; }
        .section-description { font-size:.88rem; color:var(--muted); margin:0; }
        .total-panel { border-radius:14px; background:var(--green-dark); color:white; padding:18px 22px; margin:1rem 0; }
        .total-label { color:#c9dfd2; font-size:.72rem; font-weight:700; letter-spacing:1.4px; }
        .total-value { font-size:2rem; line-height:1.2; font-weight:700; margin-top:.3rem; }
        div.stButton > button { border-radius:10px; min-height:42px; font-weight:600; border:1px solid #d7e0d9; transition:background .16s ease, transform .16s ease; }
        div.stButton > button:hover { transform:translateY(-1px); border-color:#a9c5b4; }
        div.stButton > button[kind="primary"] { background:var(--green); border-color:var(--green); color:white; }
        div.stButton > button[kind="primary"]:hover { background:var(--green-dark); border-color:var(--green-dark); }
        div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea { border-radius:10px; }
        div[data-testid="stAudioInput"] { background:white; border:1px solid var(--line); border-radius:12px; padding:8px; }
        div[data-testid="stVerticalBlockBorderWrapper"] { border-color:var(--line); border-radius:12px; }
        [data-testid="stCaptionContainer"] { color:var(--muted); }
        @keyframes fade-up { from {opacity:0; transform:translateY(5px)} to {opacity:1; transform:translateY(0)} }
        .hero, .section-head { animation:fade-up .3s ease-out; }
        @media (max-width:760px) {
          .block-container { padding: .8rem .8rem 2rem; }
          .hero { padding:20px; border-radius:14px; }
          .brand-row { align-items:flex-start; flex-direction:column; gap:.25rem; }
        }
        @media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation:none !important; transition:none !important; } }
        </style>
        """,
        unsafe_allow_html=True,
    )

def render_header():
    st.markdown(
        """
        <div class="brand-row">
          <div class="brand">restura<span class="brand-dot">.</span></div>
          <div class="top-label">Waiter station · Malayalam voice ordering</div>
        </div>
        <section class="hero">
          <div class="hero-kicker">Restaurant order management</div>
          <div class="hero-title">Good service starts<br>with getting the order right.</div>
          <p class="hero-copy">Capture the order, review the details, and send it to the kitchen.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )

def render_section_title(number, title, description):
    st.markdown(
        f"""
        <div class="section-head">
          <div class="section-number">{number} / RESTURA</div>
          <div class="section-name">{title}</div>
          <p class="section-description">{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
