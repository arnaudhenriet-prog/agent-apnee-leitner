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
    }

    .main-header {
        text-align: center;
        color: #004D40;
        margin-bottom: 10px;
        font-size: 2.5em;
        font-weight: 700;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
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
        transition: all 0.3s;
    }

    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 10px rgba(0,0,0,0.3);
    }

    .success {
        color: #00695C;
        font-weight: bold;
        font-size: 1.2em;
    }

    .error {
        color: #D32F2F;
        font-weight: bold;
        font-size: 1.2em;
    }

    .feedback {
        background: rgba(255, 255, 255, 0.8);
        padding: 15px;
        border-radius: 10px;
        margin: 15px 0;
        border-left: 4px solid #FF9800;
        font-size: 1.1em;
    }
</style>
""", unsafe_allow_html=True)

# --- Constantes ---
NOM_FICHIER_QUESTIONS = "questions.json"
INTERVALLES_BOITES = {1: 1, 2: 2, 3: 4, 4: 8, 5: 16}

# --- Fausses réponses ultra-plausibles ---
FAUSSES_REPONSES = {
    "Physiologie": [
        "C'est une réaction naturelle du corps pour éliminer le CO2 en excès.",
        "Cela indique que le plongeur a une excellente capacité pulmonaire.",
        "C'est un signe que la pression dans les poumons est trop élevée.",
        "Cela arrive uniquement lors des apnées statiques, pas en dynamique.",
    ],
    "Matériel": [
        "Pour éviter les buées sur le masque en eau froide.",
        "Pour permettre une meilleure vision périphérique.",
        "Pour réduire la résistance à l'avancement dans l'eau.",
        "Pour faciliter l'égalité des oreilles en profondeur.",
    ],
    "Procédures d'urgence": [
        "Lui faire boire de l'eau salée pour le réveiller.",
        "Le placer en position assise pour faciliter la respiration.",
        "Lui donner une bouffée d'oxygène pur si disponible.",
        "Attendre 5 minutes avant d'intervenir pour voir s'il se réveille seul.",
    ],
    "Environnement": [
        "Les courants aident à maintenir une flottabilité stable.",
        "Les courants sont sans danger si le plongeur est expérimenté.",
        "Les courants n'affectent pas la consommation d'oxygène.",
        "Les courants sont toujours prévisibles grâce aux bulletins météo.",
    ],
    "Techniques": [
        "Cela consiste à respirer profondément avant l'apnée pour saturer les poumons en O2.",
        "C'est une technique réservée aux apnéistes confirmés avec plus de 5 ans d'expérience.",
        "Cela permet de réduire la pression dans les sinus.",
        "C'est une méthode pour éviter les crampes en profondeur.",
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
    fausses_reponses = []
    autres_questions = [q for q in questions if q["id"] != question["id"] and q["theme"] == theme]
    if len(autres_questions) >= 2:
        for _ in range(2):
            q = random.choice(autres_questions)
            fausses_reponses.append(q["reponse"][0])
            autres_questions.remove(q)
    else:
        fausses_possibles = FAUSSES_REPONSES.get(theme, [])
        fausses_reponses = random.sample(fausses_possibles, 2)
    choix = [bonne_reponse] + fausses_reponses
    random.shuffle(choix)
    return choix, bonne_reponse

# --- Application principale ---
def main():
    st.markdown('<div class="main-header">🌊 Agent IA - Sécurité en Apnée</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Réviser avec la méthode de Leitner</div>', unsafe_allow_html=True)

    questions = charger_questions()
    date_aujourdhui = datetime.now()

    # Initialisation de la session
    if "progres" not in st.session_state:
        st.session_state.progres = {"derniere_revision": None, "questions": {}}
    if "reussites" not in st.session_state:
        st.session_state.reussites = 0
    if "erreurs" not in st.session_state:
        st.session_state.erreurs = 0
    if "index_question" not in st.session_state:
        st.session_state.index_question = 0
    if "reponse_selectionnee" not in st.session_state:
        st.session_state.reponse_selectionnee = None
    if "feedback" not in st.session_state:
        st.session_state.feedback = ""

    # Affichage du score
    st.markdown(f"""
    <div class="score-box">
        📊 Score: <span class="success">{st.session_state.reussites} ✅</span> |
        <span class="error">{st.session_state.erreurs} ❌</span>
    </div>
    """, unsafe_allow_html=True)

    # Sélection des questions à réviser
    a_reviser = questions_a_reviser(questions, st.session_state.progres, date_aujourdhui)
    if not a_reviser:
        st.success("Aucune question à réviser aujourd'hui ! 🎉")
        st.markdown(f"""
        <div class="score-box">
            📊 Score final: <span class="success">{st.session_state.reussites} ✅</span> |
            <span class="error">{st.session_state.erreurs} ❌</span>
        </div>
        """, unsafe_allow_html=True)
        return

    random.shuffle(a_reviser)
    st.info(f"🔹 Tu as **{len(a_reviser)}** questions à réviser aujourd'hui.")

    if st.session_state.index_question < len(a_reviser):
        question = a_reviser[st.session_state.index_question]
        choix, bonne_reponse = generer_choix(question, questions)

        # Affichage de la question
        st.markdown(f"""
        <div class="question-box">
            <h3>🏝️ Thème: {question['theme']} (Boîte {question['boite']})</h3>
            <p><strong>Question:</strong> {question['question']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Sélection de la réponse (SANS validation automatique)
        st.session_state.reponse_selectionnee = st.radio(
            "Sélectionne ta réponse:",
            choix,
            key=f"qcm_{question['id']}",
            label_visibility="collapsed"
        )

        # Boutons
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("✅ Valider", key=f"valider_{question['id']}"):
                if st.session_state.reponse_selectionnee == bonne_reponse:
                    st.session_state.reussites += 1
                    st.session_state.feedback = "✅ **Bonne réponse !**"
                    # Mise à jour de la boîte de Leitner
                    q_id = str(question["id"])
                    if q_id not in st.session_state.progres["questions"]:
                        st.session_state.progres["questions"][q_id] = {"boite": 1, "derniere_revision": None}
                    st.session_state.progres["questions"][q_id]["boite"] = min(
                        st.session_state.progres["questions"][q_id]["boite"] + 1, 5
                    )
                    st.session_state.progres["questions"][q_id]["derniere_revision"] = date_aujourdhui.strftime("%Y-%m-%d")
                else:
                    st.session_state.erreurs += 1
                    st.session_state.feedback = f"❌ **Mauvaise réponse !**<br>La bonne réponse était: **{bonne_reponse}**"
                    # Mise à jour de la boîte de Leitner
                    q_id = str(question["id"])
                    if q_id not in st.session_state.progres["questions"]:
                        st.session_state.progres["questions"][q_id] = {"boite": 1, "derniere_revision": None}
                    st.session_state.progres["questions"][q_id]["boite"] = max(
                        st.session_state.progres["questions"][q_id]["boite"] - 1, 1
                    )
                    st.session_state.progres["questions"][q_id]["derniere_revision"] = date_aujourdhui.strftime("%Y-%m-%d")

                st.session_state.index_question += 1
                st.rerun()

        with col2:
            if st.button("⏭️ Passer", key=f"passer_{question['id']}"):
                st.session_state.index_question += 1
                st.rerun()

        with col3:
            st.markdown("")  # Pour aligner les boutons

        # Affichage du feedback
        if st.session_state.feedback:
            st.markdown(f"""
            <div class="feedback">
                {st.session_state.feedback}
            </div>
            """, unsafe_allow_html=True)
            st.session_state.feedback = ""

    else:
        st.success("🎉 Tu as terminé toutes les questions pour aujourd'hui !")
        st.markdown(f"""
        <div class="score-box">
            📊 Score final: <span class="success">{st.session_state.reussites} ✅</span> |
            <span class="error">{st.session_state.erreurs} ❌</span>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()