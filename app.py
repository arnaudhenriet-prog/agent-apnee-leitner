import streamlit as st
import json
import random
from datetime import datetime

# --- Configuration ---
st.set_page_config(page_title="Agent Apnée Leitner", page_icon="🌊", layout="centered")

# --- Style CSS ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #E0F7FA 0%, #B2EBF2 100%); font-family: Arial; }
    .score { font-size: 1.5em; text-align: center; color: #004D40; margin: 20px 0; }
    .question { background: white; padding: 20px; border-radius: 10px; margin: 20px 0; }
    .feedback { color: #D32F2F; font-weight: bold; margin: 10px 0; }
    .success { color: #00695C; font-weight: bold; margin: 10px 0; }
</style>
""", unsafe_allow_html=True)

# --- Données ---
def charger_questions():
    with open("questions.json", "r", encoding="utf-8") as f:
        return json.load(f)["questions"]

# --- Application ---
def main():
    # Initialisation
    if "reussites" not in st.session_state:
        st.session_state.reussites = 0
    if "erreurs" not in st.session_state:
        st.session_state.erreurs = 0
    if "index" not in st.session_state:
        st.session_state.index = 0
    if "feedback" not in st.session_state:
        st.session_state.feedback = ""

    st.title("🌊 Agent IA - Sécurité en Apnée")
    st.markdown("<div class='score'>📊 Score: {} ✅ | {} ❌</div>".format(
        st.session_state.reussites, st.session_state.erreurs), unsafe_allow_html=True)

    questions = charger_questions()
    if st.session_state.index >= len(questions):
        st.success("🎉 Tu as terminé toutes les questions !")
        st.markdown("<div class='score'>📊 Score final: {} ✅ | {} ❌</div>".format(
            st.session_state.reussites, st.session_state.erreurs), unsafe_allow_html=True)
        st.stop()

    question = questions[st.session_state.index]
    bonne_reponse = question["reponse"][0]
    fausses_reponses = random.sample(
        [q["reponse"][0] for q in questions if q["id"] != question["id"] and q["theme"] == question["theme"]],
        2
    )
    choix = [bonne_reponse] + fausses_reponses
    random.shuffle(choix)

    st.markdown(f"""
    <div class='question'>
        <h3>Thème: {question['theme']}</h3>
        <p><strong>Question:</strong> {question['question']}</p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.feedback:
        st.markdown(f"<div class='feedback'>{st.session_state.feedback}</div>", unsafe_allow_html=True)
        st.session_state.feedback = ""

    with st.form(key=f"form_{question['id']}"):
        reponse = st.radio("Choisis ta réponse:", choix, key=f"radio_{question['id']}")
        col1, col2 = st.columns(2)
        with col1:
            valider = st.form_submit_button("✅ Valider")
        with col2:
            passer = st.form_submit_button("⏭️ Passer")

        if valider:
            if reponse == bonne_reponse:
                st.session_state.reussites += 1
                st.session_state.feedback = "✅ Bonne réponse !"
            else:
                st.session_state.erreurs += 1
                st.session_state.feedback = f"❌ Mauvaise réponse ! La bonne réponse était: **{bonne_reponse}**"
            st.session_state.index += 1
            st.rerun()
        elif passer:
            st.session_state.index += 1
            st.rerun()

if __name__ == "__main__":
    main()