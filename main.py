import streamlit as st
import time
import pandas as pd
import altair as alt
import os
import base64

# Kendi modüllerimizi çağırıyoruz
from utils import get_text, language_selector, MAX_ACTIVE_QUESTIONS, MAX_TOTAL_QUESTIONS, MAX_TEXT_CHARS, MAX_CHOICE_OPTIONS, LOGO_DOSYA_ADI
import database as db

# --- SAYFA AYARI ---
BASE_URL = "https://feedmedemo.streamlit.app" 
st.set_page_config(page_title="Feed Me", page_icon="🦄", layout="centered")

# --- SESSION STATE (HAFIZA) BAŞLATMA ---
if 'lang' not in st.session_state:
    st.session_state.lang = "en"
if 'session' not in st.session_state:
    st.session_state.session = None
# Form gönderildi mi kontrolü için yeni değişken
if 'submission_success' not in st.session_state:
    st.session_state.submission_success = False

# ==========================================
# 🎨 CSS (TASARIM - ORTALAMA & CLEAN UI)
# ==========================================
st.markdown("""
<style>
    /* 1. GENEL ARKA PLAN */
    .stApp { background-color: #FFFFFF !important; }

    /* 2. BAŞARI EKRANI ORTALAMA (FLEXBOX) */
    /* Bu sınıfı başarı mesajını saran kutuya vereceğiz */
    .success-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-align: center;
        padding: 40px;
        margin-top: 50px;
        background-color: #F8F9FA; /* Çok hafif gri kutu */
        border-radius: 16px;
        border: 1px solid #E0E0E0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    }

    .success-title {
        color: #00C4B4;
        font-weight: 900;
        font-size: 2rem;
        margin-bottom: 10px;
    }

    .success-text {
        color: #555;
        font-size: 1.2rem;
        margin-bottom: 30px;
    }

    /* 3. AKORDİYON (EXPANDER) MAKYAJI */
    div[data-testid="stExpander"] {
        border: 1px solid #F0F2F6 !important;
        border-radius: 8px !important;
        background-color: #FFFFFF !important;
        margin-bottom: 10px !important;
    }
    div[data-testid="stExpander"] details summary {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        color: #00C4B4 !important;
        font-weight: 700 !important;
        font-size: 1.1rem !important;
        padding: 10px !important;
    }
    div[data-testid="stExpander"] details summary svg {
        fill: #00C4B4 !important;
        color: #00C4B4 !important;
        margin-right: 8px !important;
    }
    div[data-testid="stExpander"] details div[data-testid="stMarkdownContainer"] {
        padding-bottom: 20px;
    }

    /* 4. TABLARI MOBİLE SIĞDIRMA */
    .stTabs [data-baseweb="tab-list"] { gap: 2px !important; }
    .stTabs [data-baseweb="tab-list"] button {
        padding: 5px 10px !important;
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 0.9rem !important;
        font-weight: 600 !important;
    }

    /* 5. INPUT ALANLARI */
    .stTextInput input, .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #333333 !important;
        border: 1px solid #E0E0E0 !important;
        border-radius: 8px !important;
    }
    .stTextInput input:disabled {
        background-color: #F0F2F6 !important;
        color: #999999 !important;
        cursor: not-allowed !important;
    }
    div[data-testid="stTextInput"] button {
        background-color: transparent !important;
        color: #555555 !important;
        border: none !important;
    }
    div[data-testid="stTextInput"] button svg { fill: #555555 !important; }

    /* 6. DROPDOWN (DİL SEÇİMİ) */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #00C4B4 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }
    .stSelectbox div[data-baseweb="select"] svg { fill: #FFFFFF !important; }
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[data-baseweb="menu"] {
        background-color: #00C4B4 !important;
        border: none !important;
    }
    li[data-baseweb="option"] {
        background-color: #00C4B4 !important; color: #FFFFFF !important;
    }
    li[aria-selected="true"], li[data-baseweb="option"]:hover {
        background-color: #009688 !important;
        color: #FFFFFF !important;
        font-weight: bold !important;
    }

    /* 7. BUTONLAR */
    div.stButton > button, 
    div[data-testid="stFormSubmitButton"] > button {
        background-color: #00C4B4 !important; 
        border: none !important;
        border-radius: 8px !important;
        color: #FFFFFF !important;
        padding: 10px 24px !important;
        transition: all 0.3s ease !important;
        width: 100%;
    }
    div.stButton > button p, 
    div[data-testid="stFormSubmitButton"] > button p {
        color: #FFFFFF !important; 
        font-weight: 700 !important;
        font-size: 16px !important;
    }
    div.stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {
        background-color: #00A896 !important;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,196,180,0.4);
    }

    /* İkincil Butonlar (SİL BUTONU & LOGOUT) */
    button[kind="secondary"] {
        background-color: #FFEBEE !important;
        color: #FF5252 !important;
        border: 1px solid #FFCDD2 !important;
        font-weight: 700 !important;
        padding-top: 10px !important;
        padding-bottom: 10px !important;
    }
    button[kind="secondary"]:hover {
        background-color: #FF5252 !important;
        color: #FFFFFF !important;
        border-color: #FF5252 !important;
    }
    button[kind="secondary"] p {
        color: #FF5252 !important;
    }
    button[kind="secondary"]:hover p {
        color: #FFFFFF !important;
    }

    /* 8. LINK KUTUSU */
    div[data-testid="stCode"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E0E0E0 !important;
        border-radius: 8px !important;
    }
    div[data-testid="stCode"] pre { background-color: #FFFFFF !important; padding: 1rem !important; }
    div[data-testid="stCode"] code {
        background-color: #FFFFFF !important;
        color: #333333 !important;
        font-family: monospace !important;
        font-weight: 600 !important;
    }
    div[data-testid="stCode"] button {
        background-color: #00C4B4 !important;
        color: #FFFFFF !important;
        opacity: 1 !important;
        border-radius: 4px !important;
    }
    div[data-testid="stCode"] button svg { fill: #FFFFFF !important; }

    /* 9. DİĞER METİNLER */
    h1, h2, h3, h4, label, .stMarkdown, p, li, span { color: #333333 !important; }
    [data-testid="stMetricValue"] { color: #00C4B4 !important; }
    .stTabs [aria-selected="true"] p { color: #00C4B4 !important; }
    label[data-baseweb="checkbox"] { margin-top: 10px !important; }

</style>
""", unsafe_allow_html=True)

# --- LOGO ÇİZİMİ ---
def render_logo(centered=True):
    if os.path.exists(LOGO_DOSYA_ADI):
        try:
            with open(LOGO_DOSYA_ADI, "rb") as f:
                data = base64.b64encode(f.read()).decode("utf-8")
            style = "display: block; margin-left: auto; margin-right: auto; width: 220px; max-width: 100%; margin-bottom: 20px;" if centered else "width: 120px; margin-top: 5px;"
            st.markdown(f'<img src="data:image/png;base64,{data}" style="{style}">', unsafe_allow_html=True)
        except:
            st.markdown(f"<h1 style='text-align: {'center' if centered else 'left'}; color:#00C4B4'>FM</h1>", unsafe_allow_html=True)
    else:
        st.markdown(f"<h1 style='text-align: {'center' if centered else 'left'}; color:#00C4B4'>FM</h1>", unsafe_allow_html=True)

# --- HERO SECTION ---
def render_hero_content():
    st.markdown(f"""
    <div style="text-align: center; padding: 10px 0;">
        <h3 style="color: #00C4B4; font-weight: 800; margin-bottom: 5px;">{get_text('hero_title')}</h3>
        <p style="color: #666; font-size: 1rem; margin-bottom: 20px;">{get_text('hero_sub')}</p>
    </div>
    """, unsafe_allow_html=True)
    hc1, hc2, hc3 = st.columns(3)
    with hc1: st.markdown(f"<div style='text-align:center;'><h1 style='margin:0; font-size:3rem;'>🎯</h1><p style='font-weight:bold; font-size:0.8rem;'>{get_text('feat_1')}</p></div>", unsafe_allow_html=True)
    with hc2: st.markdown(f"<div style='text-align:center;'><h1 style='margin:0; font-size:3rem;'>🔗</h1><p style='font-weight:bold; font-size:0.8rem;'>{get_text('feat_2')}</p></div>", unsafe_allow_html=True)
    with hc3: st.markdown(f"<div style='text-align:center;'><h1 style='margin:0; font-size:3rem;'>🚀</h1><p style='font-weight:bold; font-size:0.8rem;'>{get_text('feat_3')}</p></div>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 🚦 ANA UYGULAMA AKIŞI
# ==========================================

target_user_id = None
try:
    qp = st.query_params if hasattr(st, "query_params") else st.experimental_get_query_params()
    if "u" in qp: 
        val = qp["u"]
        target_user_id = val[0] if isinstance(val, list) else val
except: target_user_id = None

# --- SENARYO 1: FEEDBACK VERME (HALKA AÇIK) ---
if target_user_id:
    # EĞER DAHA ÖNCE FORM GÖNDERİLDİYSE -> BAŞARI EKRANINI GÖSTER
    if st.session_state.submission_success:
        render_logo(centered=True)

        # Ekranın ortasına şık bir kutu koyuyoruz (HTML/CSS)
        st.markdown(f"""
        <div class="success-container">
            <h1 style="font-size: 4rem;">🎉</h1>
            <div class="success-title">{get_text("success_msg")}</div>
            <div class="success-text">{get_text('promo_header')}</div>
        </div>
        """, unsafe_allow_html=True)

        # Balonlar hemen görünsün
        st.balloons()

        st.markdown("<br>", unsafe_allow_html=True)

        # Buton artık çalışır çünkü session state'deyiz
        if st.button(get_text("promo_btn"), type="primary", use_container_width=True):
            st.query_params.clear() # Linki temizle
            st.session_state.submission_success = False # Durumu sıfırla
            st.session_state.session = None # Oturumu sıfırla (garanti olsun)
            st.rerun() # Ana sayfaya (Login) dön

    # EĞER FORM GÖNDERİLMEDİYSE -> FORMU GÖSTER
    else:
        c1, c2 = st.columns([10, 2])
        with c2: language_selector("public")
        render_logo(centered=True)

        user_data = db.get_user_profile(target_user_id)

        if not user_data:
            st.error(get_text("error_user_not_found"))
        else:
            u_comp = user_data.get('company', '')
            u_title = user_data.get('job_title', '')
            st.markdown(f"""
            <div style="text-align:center; margin-bottom:20px;">
                <h3 style="color:#333333; margin:0;">{user_data['full_name']}</h3>
                <p style="color:#666;">{u_comp} {f'| {u_title}' if u_comp and u_title else u_title}</p>
            </div>
            """, unsafe_allow_html=True)

            st.info(f"👋 {get_text('giving_feedback_to')}")
            questions = db.get_active_questions(target_user_id)

            if questions:
                with st.form("feedback_form"):
                    answers = {}
                    for q in questions:
                        st.markdown(f"**{q['question_text']}**")
                        key = str(q['id'])

                        if q['question_type'] == 'rating_5':
                            answers[q['id']] = st.slider(get_text("rating_label"), 1, 5, 3, key=key)
                        elif q['question_type'] == 'rating_10':
                            answers[q['id']] = st.slider(get_text("rating_10_label"), 1, 10, 5, key=key)
                        elif q['question_type'] == 'rating_nps':
                            answers[q['id']] = st.slider(get_text("nps_label"), 0, 10, 5, key=key)
                        elif q['question_type'] == 'text':
                            answers[q['id']] = st.text_area(get_text("text_label"), max_chars=MAX_TEXT_CHARS, key=key)
                        elif q['question_type'] == 'choice':
                            opts = q['options'].split(',') if q['options'] else ["Yes", "No"]
                            answers[q['id']] = st.selectbox(get_text("choice_label"), opts, index=None, placeholder=get_text("select_placeholder"), key=key)

                        st.divider()

                    # FORM GÖNDERME BUTONU
                    submitted = st.form_submit_button(get_text("submit_btn"))

                if submitted:
                    if db.save_submission(target_user_id, answers):
                        # BURASI KRİTİK: Hafızayı güncelle ve sayfayı yenile
                        st.session_state.submission_success = True
                        st.rerun()

# --- SENARYO 2: YÖNETİM PANELİ (LOGIN/DASHBOARD) ---
else:
    if not st.session_state.session:
        # GİRİŞ YAPILMAMIŞSA
        c_space, c_lang = st.columns([10, 2])
        with c_lang: language_selector("login")
        render_logo(centered=True)

        with st.expander(get_text("hero_expander_label"), expanded=False):
            render_hero_content()

        t1, t2 = st.tabs([get_text("login_btn"), get_text("register_btn")])
        with t1:
            l_mail = st.text_input(get_text("email"), key="l_m")
            l_pass = st.text_input(get_text("pass"), type="password", key="l_p")
            if st.button(get_text("login_btn")):
                try:
                    res = db.supabase.auth.sign_in_with_password({"email": l_mail, "password": l_pass})
                    st.session_state.session = res.session
                    st.rerun()
                except Exception as e: st.error(f"Error: {e}")
        with t2:
            r_name = st.text_input(get_text("name"), key="r_n")
            r_comp = st.text_input(get_text("company"), key="r_c")
            r_title = st.text_input(get_text("title"), key="r_t")
            r_mail = st.text_input(get_text("email"), key="r_m")
            r_pass = st.text_input(get_text("pass"), type="password", key="r_p")
            if st.button(get_text("register_btn")):
                try:
                    res = db.supabase.auth.sign_up({"email": r_mail, "password": r_pass})
                    if res.user:
                        db.supabase.table('profiles').insert({
                            "id": res.user.id, "full_name": r_name, "company": r_comp, "job_title": r_title
                        }).execute()
                        db.init_user_questions(res.user.id)
                        st.success(get_text("register_success"))
                except Exception as e: st.error(f"Error: {e}")

    else:
        # GİRİŞ YAPILMIŞSA (DASHBOARD)
        user = st.session_state.session.user
        col_h1, col_h2, col_h3, col_h4 = st.columns([6, 4, 2, 2])
        with col_h1: render_logo(centered=False)
        with col_h3: language_selector("dashboard")
        with col_h4:
            if st.button(f"👋 {get_text('logout')}", type="secondary"): 
                db.supabase.auth.sign_out()
                st.session_state.session = None
                st.rerun()

        st.divider()
        info_text = "Sana özel değerlendirme anketinin linkini kopyala ve paylaş:" if st.session_state.lang == "tr" else "Copy and share the link to your private evaluation survey:"
        st.info(f"👇 {info_text}")
        st.code(f"{BASE_URL}?u={user.id}")

        tab_profile, tab_summary, tab_details, tab_settings = st.tabs([
            get_text("tab_profile"), get_text("tab_summary"), get_text("tab_details"), get_text("tab_settings")
        ])

        with tab_profile:
            p_data = db.get_user_profile(user.id)
            if p_data:
                with st.form("profile_update"):
                    u_name = st.text_input(get_text("name"), value=p_data.get('full_name', ''))
                    u_comp = st.text_input(get_text("company"), value=p_data.get('company', ''))
                    u_title = st.text_input(get_text("title"), value=p_data.get('job_title', ''))
                    if st.form_submit_button(get_text("update_profile")):
                        db.update_profile(user.id, u_name, u_comp, u_title)
                        st.success(get_text("profile_updated"))
                        time.sleep(1)
                        st.rerun()

        with tab_summary:
            submissions = db.get_submissions(user.id)
            sub_ids = [s['id'] for s in submissions]
            st.metric(get_text("total_resp"), len(submissions))

            if not sub_ids:
                st.warning(get_text("no_data"))
            else:
                all_ans = db.get_answers_by_submission_ids(sub_ids)
                df = pd.DataFrame(all_ans)
                df['question_text'] = df['questions'].apply(lambda x: x['question_text'] if x else 'Deleted')
                df['question_type'] = df['questions'].apply(lambda x: x['question_type'] if x else '')
                df_analysis = df[df['question_type'] != 'text']

                if not df_analysis.empty:
                    st.markdown("---")
                    for q_text in df_analysis['question_text'].unique():
                        subset = df_analysis[df_analysis['question_text'] == q_text]
                        q_type = subset.iloc[0]['question_type']
                        st.markdown(f"#### {q_text}")
                        c1, c2 = st.columns(2)
                        c1.metric(get_text("resp_count"), len(subset))
                        if 'rating' in q_type:
                            c2.metric(get_text("avg_score"), f"{subset['answer_score'].mean():.1f}")
                        chart_df = None
                        if 'rating' in q_type:
                            chart_df = subset['answer_score'].value_counts().reset_index()
                        elif 'choice' in q_type:
                            chart_df = subset['answer_choice'].value_counts().reset_index()
                        if chart_df is not None:
                            chart_df.columns = ["Answer", "Count"]
                            c = alt.Chart(chart_df).mark_bar().encode(
                                x=alt.X('Count', title=get_text("chart_x_axis")),
                                y=alt.Y('Answer', type='nominal', title=get_text("chart_y_axis"), sort='-x'),
                                color=alt.value("#00C4B4"),
                                tooltip=['Answer', 'Count']
                            ).properties(height=200, background='#FFFFFF').configure_axis(
                                labelColor='#333333', titleColor='#333333', gridColor='#F0F2F6'
                            ).configure_view(strokeWidth=0).configure_title(color='#333333')
                            st.altair_chart(c, use_container_width=True)
                        st.divider()

        with tab_details:
             submissions = db.supabase.table('submissions').select("*").eq('user_id', user.id).order('created_at', desc=True).execute().data
             if submissions:
                for sub in submissions:
                    with st.expander(f"📅 {sub['created_at'][:10]}"):
                        ans = db.supabase.table('answers').select("*, questions(question_text)").eq('submission_id', sub['id']).execute().data
                        for a in ans:
                            q_txt = a['questions']['question_text'] if a['questions'] else "---"
                            val = a.get('answer_score') or a.get('answer_text') or a.get('answer_choice')
                            st.markdown(f"**{q_txt}**: {val}")
             else:
                st.info(get_text("no_data"))

# --- AYARLAR SEKMESİ (DÜZELTİLDİ: FORM TEMİZLEME ÖZELLİĞİ EKLENDİ) ---
        with tab_settings:
            all_qs = db.get_all_questions(user.id)
            active_count = sum(1 for q in all_qs if q['is_active'])
            st.metric("Active Questions", f"{active_count} / {MAX_ACTIVE_QUESTIONS}")
            
            with st.expander(f"➕ {get_text('add_q')}", expanded=False):
                # BURASI DEĞİŞTİ: clear_on_submit=True ile form otomatik temizlenir
                with st.form("add_question_form", clear_on_submit=True):
                    n_text = st.text_input(get_text("q_text"))
                    n_type_label = st.selectbox(get_text("q_type"), [
                        ("rating_5", "⭐ 1-5"), ("rating_10", "🔢 1-10"), 
                        ("rating_nps", "📊 NPS (0-10)"), ("text", "✍️ Text"), ("choice", "🔘 Choice")
                    ], format_func=lambda x: x[1])
                    
                    is_choice = (n_type_label[0] == "choice")
                    n_options = st.text_input(get_text("options"), disabled=not is_choice, placeholder="Yes, No, Maybe" if is_choice else "---")
                    
                    # Otomatik sıra numarası (Mevcut soru sayısı + 1)
                    n_order = st.number_input(get_text("order"), min_value=1, value=len(all_qs)+1)
                    
                    # Normal button yerine form_submit_button kullanıyoruz
                    submitted = st.form_submit_button(get_text("save"))
                    
                    if submitted:
                        if n_text:
                            db.add_question(user.id, n_text, n_type_label[0], n_options if is_choice else None, n_order)
                            st.success("Saved! / Kaydedildi!") # Kullanıcıya geri bildirim
                            time.sleep(0.5) # Mesajın görünmesi için kısa bir bekleme
                            st.rerun()
                        else:
                            st.warning("Please enter question text.")

            st.divider()
            
            # SORU LİSTESİ
            for q in all_qs:
                c1, c2, c3 = st.columns([0.5, 8, 2])
                
                act = c1.checkbox("", value=q['is_active'], key=f"ac_{q['id']}", label_visibility="collapsed")
                if act != q['is_active']:
                    db.toggle_question_active(q['id'], act)
                    st.rerun()
                
                c2.write(f"**{q['question_text']}**")
                
                if c3.button(get_text("delete"), key=f"del_{q['id']}", type="secondary"):
                    db.delete_question(q['id'])
                    st.rerun()
                
                st.markdown("<hr style='margin-top: 5px; margin-bottom: 5px; opacity: 0.3;'>", unsafe_allow_html=True)
