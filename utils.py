import streamlit as st

MAX_ACTIVE_QUESTIONS = 10   
MAX_TOTAL_QUESTIONS = 50    
MAX_TEXT_CHARS = 500        
MAX_CHOICE_OPTIONS = 10     
LOGO_DOSYA_ADI = "logo.png"

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
        "tab_details": "📝 Feedbacks",
        "tab_settings": "⚙️ Config",
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
        "logout": "Bye",
        "add_q": "Add Question",
        "my_qs": "My Questions",
        "save": "Save",
        "delete": "🗑️",
        "chart_x_axis": "Count",
        "chart_y_axis": "Answer",
        "q_text": "Question Text",
        "q_type": "Question Type",
        "options": "Options (Comma separated)",
        "order": "Order No",
        "limit_reached": "Limit Reached!",
        "hero_expander_label": "What is Feed Me?",
        "hero_title": "Grow with honest feedback.",
        "hero_sub": "Collect anonymous feedback, analyze data, improve yourself.",
        "feat_1": "Create Questions",
        "feat_2": "Share Link",
        "feat_3": "Analyze Data",
        "promo_header": "Want to receive honest feedback like this?",
        "promo_btn": "🚀 Create Your Own Survey Now",
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
        "tab_profile": "👤 Profil",
        "tab_summary": "📊 Özet",
        "tab_details": "📝 Yanıtlar",
        "tab_settings": "⚙️ Ayarlar",
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
        "chart_y_axis": "Cevap",
        "q_text": "Soru Metni",
        "q_type": "Soru Tipi",
        "options": "Seçenekler (Virgülle ayır)",
        "order": "Sıra No",
        "limit_reached": "Lim,te Ulaşıldı!",
        "hero_expander_label": "Feed Me Nedir?", 
        "hero_title": "Dürüst geri bildirimlerle büyü.",
        "hero_sub": "Anonim geri bildirim topla, verileri analiz et, kendini geliştir.",
        "feat_1": "Sorularını Hazırla",
        "feat_2": "Linkini Paylaş",
        "feat_3": "Verileri Analiz Et",
        "promo_header": "Sen de böyle dürüst geri bildirimler almak ister misin?",
        "promo_btn": "🚀 Kendi Anketini Hemen Oluştur",
    }
}

def get_text(key):
    if 'lang' not in st.session_state: st.session_state.lang = "en"
    lang = st.session_state.lang
    return SOZLUK.get(lang, SOZLUK["en"]).get(key, key)

def language_selector(key_suffix):
    current_idx = 0 if st.session_state.lang == "en" else 1 
    selected = st.selectbox("Language", ["EN", "TR"], index=current_idx, label_visibility="collapsed", key=f"lang_{key_suffix}")
    new_lang = "en" if selected == "EN" else "tr"
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()
