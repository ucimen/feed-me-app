import streamlit as st
from supabase import create_client, Client
import datetime

# --- GÜVENLİK VE BAĞLANTI ---
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
except FileNotFoundError:
    st.error("HATA: Secrets bulunamadı! .streamlit/secrets.toml kontrol et.")
    st.stop()
except KeyError:
    st.error("HATA: SUPABASE_URL veya SUPABASE_KEY eksik.")
    st.stop()

supabase: Client = create_client(url, key)

# ==========================================
# 👤 KULLANICI İŞLEMLERİ (PROFIL)
# ==========================================

def get_user_profile(user_id):
    try:
        res = supabase.table('profiles').select("*").eq('id', user_id).execute()
        return res.data[0] if res.data else None
    except Exception as e:
        print(f"Error getting profile: {e}")
        return None

def update_profile(user_id, full_name, company, job_title):
    try:
        supabase.table('profiles').update({
            "full_name": full_name,
            "company": company,
            "job_title": job_title
        }).eq('id', user_id).execute()
        return True
    except Exception as e:
        print(f"Error updating profile: {e}")
        return False

# ==========================================
# ❓ SORU YÖNETİMİ
# ==========================================

def init_user_questions(user_id):
    default_questions = [
        {"text": "How would you rate my overall performance?", "type": "rating_5", "order": 1},
        {"text": "What are my strongest skills?", "type": "text", "order": 2},
        {"text": "Where do I need improvement?", "type": "text", "order": 3},
        {"text": "Would you recommend working with me?", "type": "rating_nps", "order": 4}
    ]
    for q in default_questions:
        add_question(user_id, q["text"], q["type"], None, q["order"])

def get_active_questions(user_id):
    try:
        # DÜZELTME: 'display_order' kullanıldı
        res = supabase.table('questions').select("*").eq('user_id', user_id).eq('is_active', True).order('display_order').execute()
        return res.data
    except Exception as e:
        print(f"Active questions error: {e}")
        return []

def get_all_questions(user_id):
    try:
        # DÜZELTME: 'display_order' kullanıldı
        res = supabase.table('questions').select("*").eq('user_id', user_id).order('display_order').execute()
        return res.data
    except Exception as e:
        return []

def add_question(user_id, text, q_type, options=None, order_no=99):
    try:
        supabase.table('questions').insert({
            "user_id": user_id,
            "question_text": text,
            "question_type": q_type,
            "options": options,
            "display_order": order_no, # DÜZELTME: display_order kolonuna yazıyoruz
            "is_active": True
        }).execute()
        return True
    except Exception as e:
        print(f"Error adding question: {e}")
        return False

def toggle_question_active(q_id, is_active):
    try:
        supabase.table('questions').update({"is_active": is_active}).eq("id", q_id).execute()
        return True
    except: return False

def delete_question(q_id):
    try:
        supabase.table('questions').delete().eq("id", q_id).execute()
        return True
    except: return False

# ==========================================
# 📝 YANITLAR (SUBMISSIONS)
# ==========================================

def save_submission(user_id, answers_dict):
    try:
        sub_res = supabase.table('submissions').insert({
            "user_id": user_id,
            "created_at": datetime.datetime.utcnow().isoformat()
        }).execute()
        
        if not sub_res.data: return False
        submission_id = sub_res.data[0]['id']
        
        answers_data = []
        for q_id, val in answers_dict.items():
            entry = {
                "submission_id": submission_id,
                "question_id": q_id,
                "answer_text": None,
                "answer_score": None,
                "answer_choice": None
            }
            if isinstance(val, int) or isinstance(val, float):
                entry["answer_score"] = val
            elif isinstance(val, str):
                entry["answer_text"] = val 
                entry["answer_choice"] = val 
            
            answers_data.append(entry)
            
        if answers_data:
            supabase.table('answers').insert(answers_data).execute()
        return True
    except Exception as e:
        print(f"Error saving submission: {e}")
        return False

def get_submissions(user_id):
    try:
        res = supabase.table('submissions').select("*").eq('user_id', user_id).order('created_at', desc=True).execute()
        return res.data
    except: return []

def get_answers_by_submission_ids(submission_ids):
    if not submission_ids: return []
    try:
        res = supabase.table('answers').select("*, questions(question_text, question_type)").in_('submission_id', submission_ids).execute()
        return res.data
    except Exception as e:
        print(e)
        return []
