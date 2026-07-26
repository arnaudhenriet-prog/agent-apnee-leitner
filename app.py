import streamlit as st
import json
import random
from datetime import datetime, timedelta
import os

# --- Constantes ---
NOM_FICHIER_QUESTIONS = "questions.json"
NOM_FICHIER_PROGRES = "progres.json"
INTERVALLES_BOITES = {1: 1, 2: 2, 3: 4, 4: 8, 5: 16}  # Jours entre révisions

# --- Fonctions ---
def charger_questions():
    with open(NOM_FICHIER_QUESTIONS, "r", encoding="utf-8") as f:
        return json.load(f)["questions"]

def charger_progres():
    if os.path.exists(NOM_FICHIER_PROGRES):
        with open(NOM_FICHIER_PROGRES, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"derniere_revision": None, "questions": {}}

def sauvegarder_progres(progres):
    with open(NOM_FICHIER_PROGRES, "w", encoding="utf-8") as f:
        json.dump(progres, f, indent=4, ensure_ascii=False)

def questions_a_reviser(questions, progres, date_aujourdhui):
    a_reviser = []
    for question in questions:
        q_id = question["id"]
        boite = progres["questions"].get(str(q_id), {}).get("boite", 1)
        derniere_revision = progres["questions"].get(str(q_id), {}).get("derniere_revision")

        if derniere_revision is None:
            a_reviser.append(question)
        else:
            jours_ecoules = (date_aujourdhui - datetime.strptime(derniere_revision, "%Y-%m-%d")).days
            if jours_ecoules >= INTERVALLES_BOITES[boite]:
                a_reviser.append(question)
    return a_reviser

# --- Interface Streamlit ---
def main():
    st.set_page_config(page_title="Agent Apnée Leitner", page_icon="🌊")
    st.title("🌊 Agent IA - Sécurité en Apnée + Leitner")
    st.markdown("Réponds aux questions pour réviser selon la méthode de Leitner.")

    # Charger les données
    questions = charger_questions()
    date_aujourdhui = datetime.now()

    # Charger ou initialiser les progrès
    if "progres" not in st.session_state:
        st.session_state.progres = charger_progres()

    # Sélectionner les questions à réviser
    a_reviser = questions_a_reviser(questions, st.session_state.progres, date_aujourdhui)
    if not a_reviser:
        st.success("Aucune question à réviser aujourd'hui ! 🎉")
        return

    random.shuffle(a_reviser)
    st.info(f"Tu as **{len(a_reviser)}** questions à réviser aujourd'hui.")

    # Poser une question
    if "index_question" not in st.session_state:
        st.session_state.index_question = 0

    if st.session_state.index_question < len(a_reviser):
        question = a_reviser[st.session_state.index_question]
        st.subheader(f"Thème: {question['theme']} (Boîte {question['boite']})")
        st.write(f"**Question:** {question['question']}")

        reponse_utilisateur = st.text_area("Ta réponse :", key=f"reponse_{question['id']}")
        if st.button("Valider la réponse"):
            st.write("**Réponse attendue:**")
            for ligne in question["reponse"]:
                st.write(f"- {ligne}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ J'ai réussi !"):
                    q_id = str(question["id"])
                    if q_id not in st.session_state.progres["questions"]:
                        st.session_state.progres["questions"][q_id] = {"boite": 1, "derniere_revision": None}
                    st.session_state.progres["questions"][q_id]["boite"] = min(
                        st.session_state.progres["questions"][q_id]["boite"] + 1, 5
                    )
                    st.session_state.progres["questions"][q_id]["derniere_revision"] = date_aujourdhui.strftime("%Y-%m-%d")
                    st.session_state.progres["derniere_revision"] = date_aujourdhui.strftime("%Y-%m-%d")
                    sauvegarder_progres(st.session_state.progres)

                    st.success("Bravo ! La question passe à la boîte supérieure. 🎉")
                    st.session_state.index_question += 1
                    st.rerun()

            with col2:
                if st.button("❌ J'ai échoué"):
                    q_id = str(question["id"])
                    if q_id not in st.session_state.progres["questions"]:
                        st.session_state.progres["questions"][q_id] = {"boite": 1, "derniere_revision": None}
                    st.session_state.progres["questions"][q_id]["boite"] = max(
                        st.session_state.progres["questions"][q_id]["boite"] - 1, 1
                    )
                    st.session_state.progres["questions"][q_id]["derniere_revision"] = date_aujourdhui.strftime("%Y-%m-%d")
                    sauvegarder_progres(st.session_state.progres)

                    st.error("La question redescend d'une boîte. Retente ta chance plus tard !")
                    st.session_state.index_question += 1
                    st.rerun()

        if st.button("Passer cette question"):
            st.session_state.index_question += 1
            st.rerun()
    else:
        st.success("Tu as terminé toutes les questions pour aujourd'hui ! 🎉")

if __name__ == "__main__":
    main()