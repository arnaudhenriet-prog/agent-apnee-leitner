import streamlit as st
import json
import random
from datetime import datetime

# --- Configuration de la page ---
st.set_page_config(
    page_title="Agent Apnée Leitner",
    page_icon="🌊",
    layout="centered"
)

# --- Style CSS pour le thème mer/zen ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    .stApp {
        background: linear-gradient(135deg, #E0F7FA 0%, #B2EBF2 100%);
        font-family: 'Roboto', sans-serif;
        color: #01579B;
    }
    .main-header {
        text-align: center;
        color: #004D40;
        margin-bottom: 10px;
        font-size: 2.5em;
        font-weight: 700;
    }
    .sub-header {
        text-align: center;
        color: #0277BD;
        margin-bottom: 30px;
        font-size: 1.2em;
        font-weight: 300;
    }
    .score-box {
        background: rgba(255, 255, 255, 0.85);
        border-radius: 15px;
        padding: 15px;
        margin: 20px auto;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        font-size: 1.3em;
        color: #004D40;
        border-left: 5px solid #2196F3;
    }
    .question-box {
        background: rgba(255, 255, 255, 0.9);
        border-radius: 15px;
        padding: 25px;
        margin: 20px auto;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border-left: 5px solid #00ACC1;
    }
    .stRadio > div {
        background: rgba(245, 245, 245, 0.7);
        padding: 12px;
        border-radius: 10px;
        margin: 8px 0;
    }
    .stButton > button {
        background: linear-gradient(to right, #0288D1, #01579B);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 24px;
        font-size: 1em;
        font-weight: 600;
        margin: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.2);
    }
    .feedback {
        background: rgba(255, 255, 255, 0.8);
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
        border-left: 4px solid #FF9800;
        font-size: 1.1em;
    }
    .success { color: #00695C; font-weight: bold; }
    .error { color: #D32F2F; font-weight: bold; }
    .box-info {
        font-size: 0.9em;
        color: #0277BD;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- Constantes ---
NOM_FICHIER_QUESTIONS = "questions.json"
INTERVALLES_BOITES = {1: 1, 2: 2, 3: 4, 4: 8, 5: 16}  # Jours entre révisions

# --- Fausses réponses plausibles ---
FAUSSES_REPONSES = {
    "Physiologie": [
        "C'est une réaction naturelle pour éliminer le CO2 en excès.",
        "Cela indique une excellente capacité pulmonaire.",
        "C'est un signe de pression trop élevée dans les poumons.",
        "Cela n'arrive qu'en apnée statique."
    ],
    "Matériel": [
        "Pour éviter les buées sur le masque en eau froide.",
        "Pour permettre une meilleure vision périphérique.",
        "Pour réduire la résistance à l'avancement dans l'eau.",
        "Pour faciliter l'égalité des oreilles."
    ],
    "Procédures d'urgence": [
        "Lui faire boire de l'eau salée pour le réveiller.",
        "Le placer en position assise pour faciliter la respiration.",
        "Lui donner une bouffée d'oxygène pur si disponible.",
        "Attendre 5 minutes avant d'intervenir."
    ],
    "Environnement": [
        "Les courants aident à maintenir une flottabilité stable.",
        "Les courants sont sans danger pour les plongeurs expérimentés.",
        "Les courants n'affectent pas la consommation d'oxygène.",
        "Les courants sont toujours prévisibles."
    ],
    "Techniques": [
        "Respirer profondément avant l'apnée pour saturer les poumons.",
        "Technique réservée aux apnéistes confirmés.",
        "Réduit la pression dans les sinus.",
        "Méthode pour éviter les crampes."
    ]
}

# --- Fonctions ---
def charger_questions():
    """Charge les questions depuis le fichier JSON."""
    with open(NOM_FICHIER_QUESTIONS, "r", encoding="utf-8") as f:
        return json.load(f)["questions"]

def initialiser_boites(questions):
    """Initialise les boîtes de Leitner pour toutes les questions."""
    boites = {}
    for question in questions:
        q_id = str(question["id"])
        boites[q_id] = {
            "boite": question.get("boite", 1),  # Boîte par défaut = 1
            "derniere_revision": None
        }
    return boites

def questions_a_reviser(questions, boites):
    """Sélectionne les questions à réviser aujourd'hui selon la méthode de Leitner."""
    a_reviser = []
    date_aujourdhui = datetime.now()
    for question in questions:
        q_id = str(question["id"])
        boite = boites[q_id]["boite"]
        derniere_revision = boites[q_id]["derniere_revision"]

        # Si jamais révisée ou intervalle écoulé, ajouter à la liste
        if derniere_revision is None or (
            (date_aujourdhui - datetime.strptime(derniere_revision, "%Y-%m-%d")).days
            >= INTERVALLES_BOITES[boite]
        ):
            a_reviser.append(question)
    return a_reviser

def generer_choix(question, questions):
    """Génère les choix pour un QCM (1 bonne réponse + 2 fausses)."""
    bonne_reponse = question["reponse"][0]
    theme = question["theme"]
    fausses_reponses = []

    # Prendre 2 fausses réponses du même thème si possible
    autres_questions = [q for q in questions if str(q["id"]) != str(question["id"]) and q["theme"] == theme]
    if len(autres_questions) >= 2:
        for _ in range(2):
            q = random.choice(autres_questions)
            fausses_reponses.append(q["reponse"][0])
            autres_questions.remove(q)
    else:
        # Sinon, utiliser des fausses réponses prédéfinies
        fausses_reponses = random.sample(FAUSSES_REPONSES.get(theme, ["Option 1", "Option 2"]), 2)

    choix = [bonne_reponse] + fausses_reponses
    random.shuffle(choix)
    return choix, bonne_reponse

# --- Application principale ---
def main():
    # --- Initialisation de la session ---
    # Scores (temporaires, réinitialisés à chaque session)
    if "scores" not in st.session_state:
        st.session_state.scores = {"reussites": 0, "erreurs": 0}

    # Boîtes de Leitner (persistantes pendant la session)
    if "boites" not in st.session_state:
        questions = charger_questions()
        st.session_state.boites = initialiser_boites(questions)

    # Autres variables de session
    if "index_question" not in st.session_state:
        st.session_state.index_question = 0
    if "feedback_message" not in st.session_state:
        st.session_state.feedback_message = ""

    # --- En-tête ---
    st.markdown('<div class="main-header">🌊 Agent IA - Sécurité en Apnée</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Réviser avec la méthode de Leitner</div>', unsafe_allow_html=True)

    # --- Affichage du score (toujours à jour) ---
    st.markdown(f"""
    <div class="score-box">
        📊 Score: <span class="success">{st.session_state.scores["reussites"]} ✅</span> |
        <span class="error">{st.session_state.scores["erreurs"]} ❌</span>
    </div>
    """, unsafe_allow_html=True)

    # --- Affichage du feedback (si présent) ---
    if st.session_state.feedback_message:
        st.markdown(f"""
        <div class="feedback">
            {st.session_state.feedback_message}
        </div>
        """, unsafe_allow_html=True)
        st.session_state.feedback_message = ""  # Réinitialiser après affichage

    # --- Chargement des questions ---
    questions = charger_questions()
    a_reviser = questions_a_reviser(questions, st.session_state.boites)

    if not a_reviser:
        st.success("Aucune question à réviser aujourd'hui ! 🎉")
        st.markdown(f"""
        <div class="score-box">
            📊 Score final: <span class="success">{st.session_state.scores["reussites"]} ✅</span> |
            <span class="error">{st.session_state.scores["erreurs"]} ❌</span>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # --- Mélanger les questions à réviser ---
    random.shuffle(a_reviser)
    st.info(f"🔹 Tu as **{len(a_reviser)}** questions à réviser aujourd'hui.")

    # --- Afficher la question actuelle ---
    if st.session_state.index_question < len(a_reviser):
        question = a_reviser[st.session_state.index_question]
        choix, bonne_reponse = generer_choix(question, questions)
        q_id = str(question["id"])

        # Affichage de la question et de sa boîte
        boite_actuelle = st.session_state.boites[q_id]["boite"]
        st.markdown(f"""
        <div class="question-box">
            <h3>🏝️ Thème: {question['theme']}</h3>
            <p><strong>Question:</strong> {question['question']}</p>
            <p class="box-info">
                Boîte: {boite_actuelle} |
                Prochaine révision dans {INTERVALLES_BOITES[boite_actuelle]} jours
            </p>
        </div>
        """, unsafe_allow_html=True)

        # --- Formulaire pour la réponse (évite le rerun automatique) ---
        with st.form(key=f"form_{q_id}_{st.session_state.index_question}"):
            reponse_selectionnee = st.radio(
                "Sélectionne ta réponse:",
                choix,
                key=f"qcm_{q_id}",
                label_visibility="collapsed"
            )

            col1, col2 = st.columns([1, 1])
            with col1:
                submitted = st.form_submit_button("✅ Valider")
            with col2:
                passer = st.form_submit_button("⏭️ Passer")

            if submitted:
                # Mise à jour des scores
                if reponse_selectionnee == bonne_reponse:
                    st.session_state.scores["reussites"] += 1
                    st.session_state.feedback_message = "✅ **Bonne réponse !**"
                    # Monte d'une boîte (max 5)
                    st.session_state.boites[q_id]["boite"] = min(
                        st.session_state.boites[q_id]["boite"] + 1, 5
                    )
                else:
                    st.session_state.scores["erreurs"] += 1
                    st.session_state.feedback_message = (
                        f"❌ **Mauvaise réponse !**<br>"
                        f"La bonne réponse était: **{bonne_reponse}**"
                    )
                    # Descend d'une boîte (min 1)
                    st.session_state.boites[q_id]["boite"] = max(
                        st.session_state.boites[q_id]["boite"] - 1, 1
                    )

                # Mise à jour de la date de révision
                st.session_state.boites[q_id]["derniere_revision"] = datetime.now().strftime("%Y-%m-%d")

                # Passer à la question suivante
                st.session_state.index_question += 1
                st.rerun()  # Le feedback est déjà stocké dans st.session_state

            elif passer:
                st.session_state.index_question += 1
                st.rerun()

if __name__ == "__main__":
    main()