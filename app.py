import streamlit as st
import os
import time
import pandas as pd
import altair as alt  # GRAFİK MOTORU EKLENDİ

# --- 1. SABİTLER VE LİMİTLER ---
MAX_ACTIVE_QUESTIONS = 10   
MAX_TOTAL_QUESTIONS = 50    
MAX_TEXT_CHARS = 500        
MAX_CHOICE_OPTIONS = 10     

BASE_URL = "https://feedme-app.streamlit.app" 
LOGO_DOSYA_ADI = "logo.png"

# --- 2. KÜTÜPHANE KONTROLÜ ---
try:
    from supabase import create_client, Client
except ImportError:
    st.error("Supabase package not found.")
    st.stop()

st.set_page_config(page_title="Feed Me", page_icon="🦄", layout="centered")

# --- 3. CSS (TASARIM) ---
st.markdown("""
<style>
    .stApp { background-color: #FFFFFF; }

    /* BUTONLAR */
    div.stButton > button {
        background-color: #00A896 !important;
        border: none !important;
        border-radius: 8px !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,168,150,0.3);
    }

    /* İKİNCİL BUTONLAR (KIRMIZI) */
    button[kind="secondary"] {
        background-color: #FF5252 !important;
        color: white !important;
        border: none !important;
    }

    /* GENEL YAZILAR */
    h1, h2, h3, h4, label, .stMarkdown, p, li { color: #333333; }

    /* METRİKLER */
    [data-testid="stMetricValue"] { color: #00A896 !important; }

    /* INPUT ALANLARI */
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        border-radius: 8px;
    }

    /* LOGO HİZALAMA */
    div[data-testid="stImage"] {
        display: flex;
        align-items: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. SUPABASE BAĞLANTISI ---
try:
    url = os.environ['SUPABASE_URL']
    key = os.environ['SUPABASE_KEY']
    supabase = create_client(url, key)
except KeyError:
    st.error("Secrets Error: SUPABASE_URL/KEY missing.")
    st.stop()

# --- 5. DİL YÖNETİMİ ---
if 'lang' not in st.session_state: st.session_state.lang = "en"

SOZLUK = {
    "en": {
        "welcome_feedback": "Feedback Time",
        "giving_feedback_to": "Who are you evaluating?",
        "submit_btn": "Submit Feedback",
        "success_msg": "Feedback sent! Thanks!",
        "error_user_not_found": "User not found.",
        "rating_label": "Rating (1-5)",
        "rating_10_label": "Rating (1-10)",
        "nps_label": "Recommendation (0-10)",
        "text_label": "Your Comment",
        "choice_label": "Your Choice",
        "select_placeholder": "Select...",
        "welcome_user": "Welcome,",
        "share_info": "👇 Share this link:",
        "tab_profile": "👤 Profile",
        "tab_summary": "📊 Summary",
        "tab_details": "📝 All Feedbacks",
        "tab_settings": "⚙️ Settings",
        "update_profile": "Update Profile",
        "profile_updated": "Profile updated successfully!",
        "total_resp": "Total Responses",
        "avg_score": "Avg Score",
        "resp_count": "Responses",
        "no_data": "No responses yet.",
        "chart_rating": "Average Score by Question",
        "chart_choice": "Distribution of Choices",
        "login_btn": "Login",
        "register_btn": "Register",
        "email": "Email", "pass": "Password", "name": "Full Name", "company": "Company", "title": "Title",
        "register_success": "Registration successful!",
        "logout": "Logout",
        "add_q": "Add Question",
        "my_qs": "My Questions",
        "save": "Save", "delete": "Delete",
        "chart_x_axis": "Count",
        "chart_y_axis": "Answer"
    },
    "tr": {
        "welcome_feedback": "Geri Bildirim Zamanı",
        "giving_feedback_to": "Kimi Değerlendiriyorsun?",
        "submit_btn": "Geri Bildirimi Gönder",
        "success_msg": "Geri bildirim iletildi! Teşekkürler!",
        "error_user_not_found": "Kullanıcı bulunamadı.",
        "rating_label": "Puanınız (1-5)",
        "rating_10_label": "Puanınız (1-10)",
        "nps_label": "Tavsiye (0-10)",
        "text_label": "Yorumunuz",
        "choice_label": "Seçiminiz",
        "select_placeholder": "Seçiniz...",
        "welcome_user": "Hoşgeldin,",
        "share_info": "👇 Bu linki paylaş:",
        "tab_profile": "👤 Profilim",
        "tab_summary": "📊 Özet",
        "tab_details": "📝 Tüm Yanıtlar",
        "tab_settings": "⚙️ Anket Ayarları",
        "update_profile": "Profili Güncelle",
        "profile_updated": "Profil başarıyla güncellendi!",
        "total_resp": "Toplam Yanıt",
        "avg_score": "Ortalama",
        "resp_count": "Yanıt Sayısı",
        "no_data": "Henüz veri yok.",
        "chart_rating": "Soru Bazlı Ortalama Puanlar",
        "chart_choice": "Seçenek Dağılımları",
        "login_btn": "Giriş Yap",
        "register_btn": "Kayıt Ol",
        "email": "E-Posta", "pass": "Şifre", "name": "Ad Soyad", "company": "Şirket", "title": "Unvan",
        "register_success": "Kayıt başarılı!",
        "logout": "Çıkış",
        "add_q": "Soru Ekle",
        "my_qs": "Sorularım",
        "save": "Kaydet", "delete": "Sil",
        "chart_x_axis": "Adet",
        "chart_y_axis": "Cevap"
    }
}

def get_text(key):
    lang = st.session_state.lang
    return SOZLUK.get(lang, SOZLUK["en"]).get(key, key)

# --- 6. YARDIMCI FONKSİYONLAR ---
def init_user_questions(user_id):
    standard_questions = [
        {"text": "How would you rate my overall performance?", "type": "rating_5", "order": 1},
        {"text": "How do you find my communication skills?", "type": "rating_5", "order": 2},
        {"text": "In which areas should I improve?", "type": "text", "order": 3},
        {"text": "What is my strongest quality?", "type": "text", "order": 4},
        {"text": "Would you work with me again?", "type": "choice", "options": "Yes,Maybe,No", "order": 5}
    ]
    for q in standard_questions:
        supabase.table('questions').insert({
            "user_id": user_id, "question_text": q["text"], "question_type": q["type"], 
            "options": q.get("options", None), "display_order": q["order"], "is_active": True
        }).execute()

def get_active_questions(user_id):
    return supabase.table('questions').select("*").eq('user_id', user_id).eq('is_active', True).order('display_order').execute().data

def get_all_questions(user_id):
    return supabase.table('questions').select("*").eq('user_id', user_id).order('display_order').execute().data

def save_submission(target_id, answers):
    try:
        res = supabase.table('submissions').insert({"user_id": target_id}).execute()
        if not res.data: return False
        sub_id = res.data[0]['id']
        data_to_insert = []
        for q_id, val in answers.items():
            entry = {"submission_id": sub_id, "question_id": q_id}
            if isinstance(val, int): entry["answer_score"] = val
            elif isinstance(val, str):
                if len(val) < 50: entry["answer_choice"] = val
                else: entry["answer_text"] = val
            data_to_insert.append(entry)
        supabase.table('answers').insert(data_to_insert).execute()
        return True
    except: return False

def render_logo(centered=True):
    if os.path.exists(LOGO_DOSYA_ADI):
        if centered:
            c1, c2, c3 = st.columns([1,4,1])
            c2.image(LOGO_DOSYA_ADI, width=200) 
        else:
            st.image(LOGO_DOSYA_ADI, width=150)
    else:
        st.markdown(f"<h1 style='text-align: {'center' if centered else 'left'}; color:#00A896'>FM</h1>", unsafe_allow_html=True)

def language_selector(key_suffix):
    current_idx = 0 if st.session_state.lang == "en" else 1 
    selected = st.selectbox("Language", ["EN", "TR"], index=current_idx, label_visibility="collapsed", key=f"lang_{key_suffix}")
    new_lang = "en" if selected == "EN" else "tr"
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

# ==========================================
# 🚦 ANA UYGULAMA
# ==========================================

if 'session' not in st.session_state: st.session_state.session = None

target_user_id = None
try:
    qp = st.query_params if hasattr(st, "query_params") else st.experimental_get_query_params()
    if "u" in qp: 
        val = qp["u"]
        target_user_id = val[0] if isinstance(val, list) else val
except: target_user_id = None

# --- SENARYO 1: FEEDBACK VERME ---
if target_user_id:
    c1, c2 = st.columns([10, 2])
    with c2: language_selector("public")
    render_logo(centered=True)

    try:
        res = supabase.table('profiles').select("*").eq('id', target_user_id).execute()
        user_data = res.data[0] if res.data else None
    except: user_data = None

    if not user_data:
        st.error(get_text("error_user_not_found"))
    else:
        u_comp = user_data.get('company', '')
        u_title = user_data.get('job_title', '')
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:20px;">
            <h3 style="color:#00A896; margin:0;">{user_data['full_name']}</h3>
            <p style="color:#666;">{u_comp} {f'| {u_title}' if u_comp and u_title else u_title}</p>
        </div>
        """, unsafe_allow_html=True)

        st.info(f"👋 {get_text('giving_feedback_to')}")
        questions = get_active_questions(target_user_id)

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

                if st.form_submit_button(get_text("submit_btn")):
                    if save_submission(target_user_id, answers):
                        st.success(get_text("success_msg"))
                        st.balloons()
                        time.sleep(2)

# --- SENARYO 2: YÖNETİM PANELİ ---
else:
    if not st.session_state.session:
        c_space, c_lang = st.columns([10, 2])
        with c_lang: language_selector("login")
        render_logo(centered=True)

        t1, t2 = st.tabs([get_text("login_btn"), get_text("register_btn")])

        with t1:
            l_mail = st.text_input(get_text("email"), key="l_m")
            l_pass = st.text_input(get_text("pass"), type="password", key="l_p")
            if st.button(get_text("login_btn")):
                try:
                    res = supabase.auth.sign_in_with_password({"email": l_mail, "password": l_pass})
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
                    res = supabase.auth.sign_up({"email": r_mail, "password": r_pass})
                    if res.user:
                        supabase.table('profiles').insert({
                            "id": res.user.id, "full_name": r_name, "company": r_comp, "job_title": r_title
                        }).execute()
                        init_user_questions(res.user.id)
                        st.success(get_text("register_success"))
                except Exception as e: st.error(f"Error: {e}")

    # --- DASHBOARD (LOGGED IN) ---
    else:
        user = st.session_state.session.user

        # Header
        col_h1, col_h2, col_h3, col_h4 = st.columns([6, 4, 2, 2])
        with col_h1: render_logo(centered=False)
        with col_h3: language_selector("dashboard")
        with col_h4:
            if st.button(get_text("logout"), type="secondary"):
                supabase.auth.sign_out()
                st.session_state.session = None
                st.rerun()

        st.divider()
        st.info(get_text("share_info"))
        st.code(f"{BASE_URL}?u={user.id}")

        # --- SEKME YAPISI ---
        tab_profile, tab_summary, tab_details, tab_settings = st.tabs([
            get_text("tab_profile"), get_text("tab_summary"), get_text("tab_details"), get_text("tab_settings")
        ])

        # 1. PROFİLİM
        with tab_profile:
            p_res = supabase.table('profiles').select("*").eq('id', user.id).execute()
            if p_res.data:
                p_data = p_res.data[0]
                with st.form("profile_update"):
                    u_name = st.text_input(get_text("name"), value=p_data.get('full_name', ''))
                    u_comp = st.text_input(get_text("company"), value=p_data.get('company', ''))
                    u_title = st.text_input(get_text("title"), value=p_data.get('job_title', ''))

                    if st.form_submit_button(get_text("update_profile")):
                        supabase.table('profiles').update({
                            "full_name": u_name, "company": u_comp, "job_title": u_title
                        }).eq('id', user.id).execute()
                        st.success(get_text("profile_updated"))
                        time.sleep(1)
                        st.rerun()

        # 2. ÖZET (ALTAIR KULLANARAK YATAY GRAFİK)
        with tab_summary:
            try:
                submissions = supabase.table('submissions').select("id").eq('user_id', user.id).execute().data
                sub_ids = [s['id'] for s in submissions]

                st.metric(get_text("total_resp"), len(submissions))

                if not sub_ids:
                    st.warning(get_text("no_data"))
                else:
                    all_ans = supabase.table('answers').select("*, questions(question_text, question_type)").in_('submission_id', sub_ids).execute().data
                    df = pd.DataFrame(all_ans)

                    df['question_text'] = df['questions'].apply(lambda x: x['question_text'] if x else 'Deleted')
                    df['question_type'] = df['questions'].apply(lambda x: x['question_type'] if x else '')

                    df_analysis = df[df['question_type'] != 'text']

                    if df_analysis.empty:
                        st.info("No analytic questions found.")
                    else:
                        st.markdown("---")
                        unique_questions = df_analysis['question_text'].unique()

                        for q_text in unique_questions:
                            subset = df_analysis[df_analysis['question_text'] == q_text]
                            q_type = subset.iloc[0]['question_type']

                            st.markdown(f"#### {q_text}")

                            col_stat1, col_stat2 = st.columns(2)
                            col_stat1.metric(get_text("resp_count"), len(subset))

                            if 'rating' in q_type:
                                avg_val = subset['answer_score'].mean()
                                col_stat2.metric(get_text("avg_score"), f"{avg_val:.1f}")

                            # VERİ HAZIRLIĞI
                            chart_df = None
                            if 'rating' in q_type:
                                # Sayıları hesapla ve DataFrame'e çevir
                                chart_data = subset['answer_score'].value_counts()
                                chart_df = chart_data.reset_index()
                                chart_df.columns = ["Answer", "Count"] # Kolon adlarını sabitle
                            elif 'choice' in q_type:
                                chart_data = subset['answer_choice'].value_counts()
                                chart_df = chart_data.reset_index()
                                chart_df.columns = ["Answer", "Count"]

                            # ALTAIR GRAFİK (YATAY)
                            if chart_df is not None:
                                c = alt.Chart(chart_df).mark_bar().encode(
                                    x=alt.X('Count', title=get_text("chart_x_axis")),
                                    y=alt.Y('Answer', type='nominal', title=get_text("chart_y_axis"), sort='-x'),
                                    color=alt.value("#00A896"),
                                    tooltip=['Answer', 'Count']
                                ).properties(height=200) # Grafik yüksekliği

                                st.altair_chart(c, use_container_width=True)

                            st.divider()

            except Exception as e:
                st.error(f"Analysis Error: {e}")

        # 3. TÜM YANITLAR
        with tab_details:
             try:
                submissions = supabase.table('submissions').select("*").eq('user_id', user.id).order('created_at', desc=True).execute().data
                if submissions:
                    for sub in submissions:
                        with st.expander(f"📅 {sub['created_at'][:10]}"):
                            ans = supabase.table('answers').select("*, questions(question_text)").eq('submission_id', sub['id']).execute().data
                            for a in ans:
                                q_txt = a['questions']['question_text'] if a['questions'] else "---"
                                val = a.get('answer_score') or a.get('answer_text') or a.get('answer_choice')
                                st.markdown(f"**{q_txt}**: {val}")
                else:
                    st.info(get_text("no_data"))
             except: pass

        # 4. AYARLAR
        with tab_settings:
            all_qs = get_all_questions(user.id)
            active_count = sum(1 for q in all_qs if q['is_active'])

            st.metric("Active Questions", f"{active_count} / {MAX_ACTIVE_QUESTIONS}")

            with st.expander(get_text("add_q"), expanded=False):
                with st.form("add_q_form"):
                    n_text = st.text_input(get_text("q_text"))
                    n_type_label = st.selectbox(get_text("q_type"), [
                        ("rating_5", "⭐ 1-5"), ("rating_10", "🔢 1-10"), 
                        ("rating_nps", "📊 NPS (0-10)"), ("text", "✍️ Text"), ("choice", "🔘 Choice")
                    ], format_func=lambda x: x[1])
                    n_options = st.text_input(get_text("options"))
                    n_order = st.number_input(get_text("order"), min_value=1, value=len(all_qs)+1)

                    if st.form_submit_button(get_text("save")):
                        n_type = n_type_label[0]
                        supabase.table('questions').insert({
                            "user_id": user.id, "question_text": n_text, "question_type": n_type,
                            "options": n_options if n_type == "choice" else None,
                            "display_order": n_order, "is_active": True
                        }).execute()
                        st.rerun()

            st.divider()
            for q in all_qs:
                c1, c2, c3 = st.columns([1, 5, 2])
                act = c1.checkbox("✓", value=q['is_active'], key=f"ac_{q['id']}")
                if act != q['is_active']:
                    supabase.table('questions').update({"is_active": act}).eq('id', q['id']).execute()
                    st.rerun()
                c2.write(f"**{q['question_text']}**")
                if c3.button(get_text("delete"), key=f"del_{q['id']}", type="secondary"):
                    supabase.table('questions').delete().eq('id', q['id']).execute()
                    st.rerun()
                st.markdown("---")
