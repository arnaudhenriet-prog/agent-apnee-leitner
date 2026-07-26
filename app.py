import streamlit as st
import json
import random
from datetime import datetime

# --- Constantes ---
NOM_FICHIER_QUESTIONS = "questions.json"
INTERVALLES_BOITES = {1: 1, 2: 2, 3: 4, 4: 8, 5: 16}  # Jours entre révisions

# --- Fonctions ---
def charger_questions():
    with open(NOM_FICHIER_QUESTIONS, "r", encoding="utf-8") as f:
        return json.load(f)["questions"]

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
    st.title("🌊 Agent IA - Sécurité en Apnée + Leitner (QCM)")
    st.markdown("Réponds aux QCM pour réviser selon la méthode de Leitner.")

    # Charger les données
    questions = charger_questions()
    date_aujourdhui = datetime.now()

    # Initialiser les progrès et compteurs
    if "progres" not in st.session_state:
        st.session_state.progres = {"derniere_revision": None, "questions": {}}
    if "reussites" not in st.session_state:
        st.session_state.reussites = 0
    if "erreurs" not in st.session_state:
        st.session_state.erreurs = 0

    # Sélectionner les questions à réviser
    a_reviser = questions_a_reviser(questions, st.session_state.progres, date_aujourdhui)
    if not a_reviser:
        st.success("Aucune question à réviser aujourd'hui ! 🎉")
        st.write(f"📊 **Bilan :** {st.session_state.reussites} ✅ | {st.session_state.erreurs} ❌")
        return

    random.shuffle(a_reviser)
    st.info(f"Tu as **{len(a_reviser)}** questions à réviser aujourd'hui.")

    # Poser une question
    if "index_question" not in st.session_state:
        st.session_state.index_question = 0

    if st.session_state.index_question < len(a_reviser):
        question = a_reviser[st.session_state.index_question]

        # Afficher la question
        st.subheader(f"Thème: {question['theme']} (Boîte {question['boite']})")
        st.write(f"**Question:** {question['question']}")

        # Générer les choix (3 réponses : 1 bonne + 2 fausses)
        bonne_reponse = question["reponse"][0]  # On prend la première réponse comme bonne
        choix = [bonne_reponse]
        # Ajouter 2 fausses réponses (aléatoires parmi les autres questions)
        autres_questions = [q for q in questions if q["id"] != question["id"]]
        for _ in range(2):
            fausse_question = random.choice(autres_questions)
            fausse_reponse = fausse_question["reponse"][0]
            choix.append(fausse_reponse)

        # Mélanger les choix
        random.shuffle(choix)

        # Afficher les choix sous forme de boutons radio
        reponse_utilisateur = st.radio(
            "Choisis la bonne réponse :",
            choix,
            key=f"qcm_{question['id']}"
        )

        if st.button("Valider"):
            if reponse_utilisateur == bonne_reponse:
                st.success("✅ **Bonne réponse !**")
                st.session_state.reussites += 1

                # Mettre à jour la boîte de Leitner
                q_id = str(question["id"])
                if q_id not in st.session_state.progres["questions"]:
                    st.session_state.progres["questions"][q_id] = {"boite": 1, "derniere_revision": None}
                st.session_state.progres["questions"][q_id]["boite"] = min(
                    st.session_state.progres["questions"][q_id]["boite"] + 1, 5
                )
                st.session_state.progres["questions"][q_id]["derniere_revision"] = date_aujourdhui.strftime("%Y-%m-%d")
                st.session_state.progres["derniere_revision"] = date_aujourdhui.strftime("%Y-%m-%d")
            else:
                st.error(f"❌ **Mauvaise réponse !** La bonne réponse était : **{bonne_reponse}**")
                st.session_state.erreurs += 1

                # Mettre à jour la boîte de Leitner (redescend d'une boîte)
                q_id = str(question["id"])
                if q_id not in st.session_state.progres["questions"]:
                    st.session_state.progres["questions"][q_id] = {"boite": 1, "derniere_revision": None}
                st.session_state.progres["questions"][q_id]["boite"] = max(
                    st.session_state.progres["questions"][q_id]["boite"] - 1, 1
                )
                st.session_state.progres["questions"][q_id]["derniere_revision"] = date_aujourdhui.strftime("%Y-%m-%d")

            # Passer à la question suivante
            st.session_state.index_question += 1
            st.rerun()

        if st.button("Passer cette question"):
            st.session_state.index_question += 1
            st.rerun()

    else:
        st.success("Tu as terminé toutes les questions pour aujourd'hui ! 🎉")
        st.write(f"📊 **Bilan final :** {st.session_state.reussites} ✅ | {st.session_state.erreurs} ❌")

if __name__ == "__main__":
    main()