import streamlit as st
import json
import random
from datetime import datetime

# --- Constantes ---
NOM_FICHIER_QUESTIONS = "questions.json"
INTERVALLES_BOITES = {1: 1, 2: 2, 3: 4, 4: 8, 5: 16}  # Jours entre révisions

# --- Fausses réponses plausibles par thème ---
FAUSSES_REPONSES = {
    "Physiologie": [
        "C'est une augmentation du rythme cardiaque pour compenser le manque d'oxygène.",
        "C'est un phénomène normal qui ne nécessite pas d'attention particulière.",
        "C'est dû à une surcharge en oxygène dans le sang.",
        "Cela arrive uniquement en plongée avec bouteille, pas en apnée.",
        "C'est un signe de bonne adaptation du corps à l'apnée.",
        "Cela est causé par une pression trop élevée dans les poumons."
    ],
    "Matériel": [
        "Pour éviter les fuites d'eau dans le masque.",
        "Pour améliorer la visibilité sous l'eau.",
        "Pour réduire le poids total du plongeur.",
        "Pour faciliter la respiration en surface.",
        "Pour protéger les yeux des UV.",
        "Pour augmenter la flottabilité."
    ],
    "Procédures d'urgence": [
        "Appeler immédiatement les secours sans intervenir soi-même.",
        "Lui donner de l'eau à boire pour le réveiller.",
        "Le laisser seul pour éviter de le stresser.",
        "Lui faire respirer dans un sac en papier.",
        "Attendre qu'il se réveille tout seul.",
        "Lui donner une claque dans le dos."
    ],
    "Environnement": [
        "Les courants n'ont aucun impact sur l'apnée.",
        "Les courants permettent de se déplacer plus facilement.",
        "Les courants sont toujours dangereux, il faut éviter de plonger.",
        "Les courants sont visibles depuis la surface.",
        "Les courants n'existent pas en eau douce.",
        "Les courants aident à remonter à la surface."
    ],
    "Techniques": [
        "C'est une technique réservée aux plongeurs expérimentés.",
        "Cela consiste à retenir sa respiration le plus longtemps possible.",
        "C'est une méthode pour compenser plus rapidement.",
        "Cela n'a aucun impact sur la sécurité.",
        "C'est une technique interdite en compétition.",
        "Cela permet de plonger plus profondément sans risque."
    ]
}

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

def generer_choix(question, questions):
    bonne_reponse = question["reponse"][0]
    theme = question["theme"]

    # Sélectionner 2 fausses réponses plausibles dans le même thème
    fausses_reponses = []
    autres_questions = [q for q in questions if q["id"] != question["id"] and q["theme"] == theme]

    # Si assez de questions dans le même thème, en prendre 2
    if len(autres_questions) >= 2:
        for _ in range(2):
            q = random.choice(autres_questions)
            fausse_reponse = q["reponse"][0]
            fausses_reponses.append(fausse_reponse)
            autres_questions.remove(q)  # Éviter les doublons
    else:
        # Sinon, prendre des fausses réponses prédéfinies pour le thème
        fausses_possibles = FAUSSES_REPONSES.get(theme, [])
        fausses_reponses = random.sample(fausses_possibles, 2)

    choix = [bonne_reponse] + fausses_reponses
    random.shuffle(choix)
    return choix, bonne_reponse

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

    # Afficher le compteur en haut de la page
    st.write(f"📊 **Bilan actuel :** {st.session_state.reussites} ✅ | {st.session_state.erreurs} ❌")

    # Sélectionner les questions à réviser
    a_reviser = questions_a_reviser(questions, st.session_state.progres, date_aujourdhui)
    if not a_reviser:
        st.success("Aucune question à réviser aujourd'hui ! 🎉")
        st.write(f"📊 **Bilan final :** {st.session_state.reussites} ✅ | {st.session_state.erreurs} ❌")
        return

    random.shuffle(a_reviser)
    st.info(f"Tu as **{len(a_reviser)}** questions à réviser aujourd'hui.")

    # Poser une question
    if "index_question" not in st.session_state:
        st.session_state.index_question = 0

    if st.session_state.index_question < len(a_reviser):
        question = a_reviser[st.session_state.index_question]
        choix, bonne_reponse = generer_choix(question, questions)

        # Afficher la question
        st.subheader(f"Thème: {question['theme']} (Boîte {question['boite']})")
        st.write(f"**Question:** {question['question']}")

        # Afficher les choix sous forme de boutons
        for i, option in enumerate(choix):
            if st.button(f"{i+1}. {option}", key=f"option_{i}_{question['id']}"):
                if option == bonne_reponse:
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
                    st.error(f"❌ **Mauvaise réponse !**")
                    st.write(f"**La bonne réponse était :** **{bonne_reponse}**")
                    st.session_state.erreurs += 1

                    # Mettre à jour la boîte de Leitner (redescend d'une boîte)
                    q_id = str(question["id"])
                    if q_id not in st.session_state.progres["questions"]:
                        st.session_state.progres["questions"][q_id] = {"boite": 1, "derniere_revision": None}
                    st.session_state.progres["questions"][q_id]["boite"] = max(
                        st.session_state.progres["questions"][q_id]["boite"] - 1, 1
                    )
                    st.session_state.progres["questions"][q_id]["derniere_revision"] = date_aujourdhui.strftime("%Y-%m-%d")

                # Passer à la question suivante après un délai
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