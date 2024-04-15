import streamlit as st
import pandas as pd
import base64
import datetime
import pymongo
import hmac
#from bson import ObjectId

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

@st.cache_resource
def init_connection():
    return pymongo.MongoClient(**st.secrets["mongo"])

client = init_connection()

sex_mapping = {'male': 0, 'female': 1}
answers = {}

#Comp = [
#    "Organisation du matériel (ex. matériel rangé sur la table)",
#    "Concentration sur tâches exigeantes (ex. reste sur une activité sans se distraire)",
#    "Application des instructions (ex. suit une directive sans rappel)",
#    "Réactivité modérée aux distractions externes (ex. ignore les bruits alentours lors d'une tâche)",
#    "Fluidité dans les transitions (ex. change d'activité sans délai)",
#    "Capacité à rester calme (ex. reste assis pendant une histoire)",
#    "Gestion des mouvements et manipulations (ex. ne met pas d'objets à la bouche)",
#    "Régulation des prises de parole (ex. parle à des moments appropriés)",
#    "Adaptation sociale et émotionnelle (ex. joue sans exclure les autres)",
#    "Engagement dans les jeux collectifs (ex. suit les règles du jeu)"
#    ]

Comp = [
    "Est capable de suivre des instructions verbales simples en deux étapes, telles que 'va chercher tes chaussures et apporte-les ici'.",
    "Comprend ce qui est dit sans avoir besoin de répétitions fréquentes lorsqu'on lui parle directement dans un environnement sans distractions majeures.",
    "Interprète correctement le ton de la voix et l'ironie dans les situations sociales, évitant de prendre les choses trop littéralement.",
    "Résume efficacement les événements principaux ou les points clés après avoir écouté des histoires ou des récits.",
    "Saisit l'essentiel des discussions environnantes, même sans être directement impliqué dans la conversation.",
    "Remarque quand quelqu'un semble triste ou contrarié pendant une conversation, même sans expression verbale explicite.",
    "Peut interpréter le langage corporel fermé d'un camarade comme un désir d'intimité et réagit de façon appropriée.",
    "Comprend les perspectives variées lors d'un conflit entre amis pour saisir les raisons du désaccord.",
    "Interprète correctement les subtilités du langage corporel et des expressions faciales indiquant l'intérêt ou l'ennui lors des interactions.",
    "Capable d'interpréter les variations de ton de voix comme des indicateurs émotionnels.",
    "Comprend et suit les instructions données par l'enseignant(e) pour les activités de classe.",
    "Exécute de manière autonome une tâche domestique simple lorsqu'elle est demandée avec des instructions claires.",
    "Mémorise et applique une nouvelle routine à la maison après qu'elle a été expliquée.",
    "Demande rarement des clarifications lors de la réception d'instructions dans un contexte social ou scolaire.",
    "S'adapte et suit de manière autonome les étapes d'utilisation d'un nouvel appareil électronique ou jeu.",
    "Communique son inconfort ou ses préférences de manière efficace lorsqu'il est confronté à des situations inattendues ou des changements de plans.",
    "Manifeste un intérêt et participe de manière appropriée à des conversations, même sur des sujets qui ne le captivent pas spécifiquement.",
    "Aborde des inconnus avec assurance pour demander de l'aide ou des informations et formule ses requêtes clairement.",
    "S'efforce de comprendre les différents points de vue en cas de désaccord ou de conflit et adapte sa communication en conséquence.",
    "Explique les problèmes ou situations complexes de manière mesurée, en s'assurant de la compréhension de son interlocuteur.",
    "Exprime clairement la cause de sa frustration ou de son mécontentement lorsqu'il se sent contrarié.",
    "Partage avec enthousiasme ses centres d'intérêt, montrant clairement ce qui le passionne.",
    "Partage volontiers ses pensées ou idées sur un sujet ou une activité qui l'intéresse avec son entourage.",
    "Contribue aux conversations de groupe en partageant activement ses propres idées et opinions.",
    "Exprime ses préférences ou inquiétudes face à des changements dans sa routine habituelle de façon adaptée.",
    "Gère les situations où il doit s'exprimer en public, telles que parler devant la classe ou répondre à des questions, en évitant les situations où il se sent mal à l'aise.",
    "Interprète et répond de manière adéquate aux signaux non-verbaux comme les gestes et les expressions faciales durant les échanges.",
    "Initie des conversations avec ses pairs ou des adultes de manière autonome.",
    "Accepte et intègre de façon constructive le feedback et les critiques reçus lors des conversations.",
    "Se montre engagé et réactif lors des conversations avec des pairs ou des adultes, évitant de se retirer dans le silence.",
    "Comprend les consignes écrites après une lecture attentive sans nécessiter de multiples révisions.",
    "Aborde la lecture d'instructions pour de nouvelles activités sans frustration notable.",
    "Fait preuve d'attention aux détails lorsqu'il suit des instructions écrites pour minimiser les erreurs.",
    "Gère l'assemblage de meubles ou de jouets avec des instructions écrites de manière persévérante, sans abandonner facilement.",
    "Identifie clairement les points clés et les attentes dans les e-mails ou lettres reçus.",
    "Planifie et structure ses idées de manière logique et ordonnée pour des projets scolaires impliquant de la recherche et de la rédaction.",
    "Répond de manière appropriée et en temps voulu lorsqu'une réponse écrite rapide est nécessaire.",
    "Mène à terme ses projets écrits à long terme, tels que les rédactions ou les rapports, démontrant de la persévérance et une bonne gestion du temps.",
    "Quand il est invité à rédiger un texte sur un sujet d'intérêt, il organise ses idées clairement et exprime ses pensées de manière structurée.",
    "Est capable de retranscrire ses idées de manière expressive et organisée dans un journal ou un blog.",
    "Suit une routine matinale, comme se préparer pour l'école, de manière autonome sans avoir besoin de rappel.",
    "Participe activement et régulièrement à des tâches ménagères simples telles que ranger sa chambre ou mettre la table.",
    "Planifie et exécute de manière autonome des tâches ménagères assignées, sans se laisser distraire ou oublier leur achèvement.",
    "Gère efficacement les tâches multi-étapes qui nécessitent organisation et planification, telles que la préparation d'un petit déjeuner.",
    "Identifie et accomplit de manière appropriée les tâches domestiques supplémentaires sans besoin d'instructions explicites.",
    "Distingue entre les situations nécessitant une action immédiate et celles qui peuvent attendre et réagit en conséquence.",
    "Conserve son calme et trouve des solutions lors d'urgences mineures à la maison.",
    "Réagit de façon adéquate et appropriée face à des situations inattendues à la maison, comme un dysfonctionnement d'appareil électrique ou une fuite d'eau.",
    "Suit les instructions orales ou écrites pour résoudre efficacement un problème lors d'une urgence domestique.",
    "Utilise correctement des équipements de sécurité de base à la maison, tels qu'un extincteur, en cas d'urgence.",
    "Prépare de manière autonome ses affaires scolaires pour le lendemain sans nécessiter de rappel.",
    "Suit une routine quotidienne pour gérer ses repas, devoirs et le coucher de façon régulière et indépendante.",
    "Priorise de manière efficace les tâches domestiques, en décidant quelles sont les plus importantes à accomplir en premier.",
    "Maintient son espace personnel organisé pour une récupération aisée de ses affaires.",
    "Évalue avec justesse le temps nécessaire pour accomplir une tâche domestique.",
    "Gère calmement les réactions aux bruits forts ou inattendus dans des lieux publics.",
    "Navigue habilement dans des espaces publics encombrés, en évitant les obstacles et les gens.",
    "Agit avec assurance dans des établissements tels que les restaurants ou cafés, en passant des commandes et en interagissant avec le personnel sans hésitation.",
    "Répond positivement et avec résilience aux retours négatifs ou aux moqueries en public.",
    "S'adapte rapidement aux changements inattendus ou aux nouveaux environnements dans des espaces publics.",
    "Fait face aux situations stressantes à l'école, comme les confrontations avec des camarades, sans se replier sur soi-même.",
    "Gère le stress et l'anxiété de manière positive lors de changements soudains, comme le retour à l'école après une absence ou un changement d'emploi du temps.",
    "Reste calme et ne montre pas d'irritabilité face à des environnements bruyants ou surchargés.",
    "Participe à des activités de groupe sans montrer de malaise significatif.",
    "Fait face aux retours négatifs de manière constructive, sans colère ou tristesse excessive.",
    "Se comporte de manière sociable et coopérative lors d'activités familiales en groupe.",
    "Contribue activement et de manière constructive aux projets de groupe à l'école.",
    "Apprécie le travail en équipe et participe de manière collaborative.",
    "Établit des liens aisément avec d'autres enfants lors d'activités collectives et participe de manière inclusive.",
    "Est régulièrement inclus dans les jeux de groupe et interagit bien avec ses pairs.",
    "Affiche de l'enthousiasme lors de la rencontre avec de nouveaux enfants de son âge.",
    "Maintient des relations d'amitié stables et durables sur le long terme.",
    "Gère les conflits avec ses amis de façon constructive, sans mettre fin à l'amitié ou éviter inutilement l'autre personne.",
    "Établit des liens avec d'autres enfants et participe à des activités communes sans difficulté.",
    "Communique ouvertement ses besoins et désirs dans ses relations amicales.",
    "Remarque et répond adéquatement aux tentatives d'interaction de ses pairs.",
    "Interprète correctement les expressions faciales et le ton de voix des autres pour comprendre leurs émotions.",
    "Comprend et navigue dans les enjeux sociaux lors de conflits ou de situations complexes.",
    "Fait preuve de flexibilité face aux changements inattendus dans les routines sociales.",
    "Comprend rapidement les situations surprenantes et ajuste son comportement en conséquence.",
    "S'engage volontiers et avec aisance dans des interactions sociales inattendues.",
    "Aborde les désaccords avec ses pairs en cherchant des solutions constructives.",
    "Voit les critiques et le feedback négatif comme des occasions d'apprendre et de s'améliorer.",
    "Démontre de l'excitation et de l'enthousiasme pour participer à des événements sociaux, tels que les fêtes d'anniversaire.",
    "Gère bien les petits changements imprévus, comme une modification d'horaire à l'école, sans se montrer excessivement perturbé.",
    "Exprime la joie et l'excitation de manière positive en présence de ses amis.",
    "Gère ses sentiments d'inconfort ou d'anxiété de façon à ce qu'ils n'affectent pas excessivement son comportement en public.",
    "Communique ses émotions de manière constructive quand il/elle est frustré(e) par une interaction sociale.",
    "Montre une évolution et une maturité dans la façon d'exprimer ses émotions en présence d'autres au fil du temps.",
    "Identifie et répond de manière adéquate et sensible aux émotions d'autrui lors des interactions avec ses pairs."
]

#Comp = [
#    "L'utilisation de la planche permet d'améliorer ma mobilité.",
#    "L'utilisation de la planche améliore mon indépendance dans les activités quotidiennes.",
#    "Je trouve que la planche s'adapte facilement à différents environnements et situations.",
#    "Je pense que l'utilisation de la planche réduit mon risque de blessures lors des transferts.",
#    "Je trouve globalement la planche encombrante et difficile à transporter.",
#    "J'ai peur de basculer ou de tomber quand j'utilise la planche.",
#    "L'utilisation de la planche est inconfortable.",
#    "J'utilise la planche uniquement parce que je n'ai pas d'autres options.",
#    "Je préfère utiliser d'autres méthodes que la planche pour les transferts (aide d'un aidant, support mural, etc.).",
#    "Le bois semble adapté en terme de poids.",
#    "Le bois semble adapté en terme de durabilité.",
#    "Le polycarbonate semble adapté en terme de poids.",
#    "Le polycarbonate semble adapté en terme de durabilité.",
#    "Les matériaux en résine semblent adaptés en terme de poids.",
#    "Les matériaux en résine semblent adaptés en terme de durabilité.",
#    "Les matériaux en composite semblent adaptés en terme de poids.",
#    "Les matériaux en composite semblent adaptés en terme de durabilité.",
#    "La planche offre actuellement un équilibre optimal pour prévenir le glissement non désiré.",
#    "Un antidérapant semble nécessaire pour améliorer la sécurité de la glisse.",
#     "Ma glisse est identique peu importe les vêtements que je porte.",
#    "Je peux réaliser la glisse en sécurité même en étant totalement dénudé.",
#    "Une forme courbe me semblerait adaptée en terme de fonctionnalité.",
#    "Une forme courbe me semblerait adaptée en terme de stabilité et de sécurité.",
#    "Une encoche sur la planche me semblerait adaptée en terme de fonctionnalité.",
#    "Une encoche sur la planche me semblerait adaptée en terme de stabilité et de sécurité.",
#    "Une accroche permettant de fixer la planche au fauteuil semble indispensable à une planche innovante.",
#    "Un système permettant à la planche de se plier semble indispensable à une planche innovante.",
#    "Un système permettant à la planche de se monter sur plusieurs supports semble indispensable à une planche innovante.",
#    "Une technologie intégrée à la planche pour prévenir les escarres serait une innovation notable pour les utilisateurs.",
#    "Une technologie intégrée à la planche pour réaliser sa pesée lors des transferts serait une innovation notable pour les utilisateurs.",
#    "Des capteurs intégrés à la planche pour surveiller la glisse lors des transferts représenteraient une innovation notable pour les utilisateurs."]





st.markdown(
        """<style>
        div[class*="stSlider"] > label > div[data-testid="stMarkdownContainer"] > p {
        font-size: 20px;
                }
        </style>
                """, unsafe_allow_html=True)


st.markdown(
    """
    <style>
    .centered_button {
        display: flex;
        justify-content: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)


st.write("""
# Questionnaire d'hétéro-évaluation du comportement pour enfants (Version parents V1)
""")


st.sidebar.header('Informations')

#slider_values = [1,2,3,4]
slider_values = [1,2,3]
#slider_strings = ["Très insuffisant", "Insuffisant", "Satisfaisant", "Très satisfaisant"]
slider_strings = ["Jamais", "Parfois", "Tout le temps"]

def stringify(i:int = 0) -> str:
    return slider_strings[i-1]

#T1 = st.select_slider(
#    "Je quitte souvent ma place sans nécessité lors d'une réunion.",
#    options=slider_values,
#    value=1,
#    format_func=stringify)

#def save_and_download_csv(df):
#    csv_string = df.to_csv(index=False,sep=';')
    #b64 = base64.b64encode(csv_string.encode()).decode()
    #href = f'<a href="data:file/csv;base64,{b64}" download="features.csv">Download CSV File</a>'
    #st.markdown(href, unsafe_allow_html=True)

# def custom_date_input(label, min_date=None, max_date=None):
#     if min_date is None:
#         min_date = datetime.datetime(year=1900, month=1, day=1)
#     if max_date is None:
#         max_date = datetime.datetime(year=2100, month=12, day=31)
#     year = st.number_input("Year", min_value=min_date.year, max_value=max_date.year, step=1, value=min_date.year)
#     month = st.number_input("Month", min_value=1, max_value=12, step=1, value=min_date.month)
#     day = st.number_input("Day", min_value=1, max_value=31, step=1, value=min_date.day)
#     try:
#         date_input = datetime.datetime(year=year, month=month, day=day)
#         if min_date <= date_input <= max_date:
#             return date_input
#         else:
#             st.error("Please enter a date within the specified range.")
#             return None
#     except ValueError:
#         st.error("Please enter a valid date.")
#         return None

def write_data(new_data):
    # Write new data to the database
    db = client.Questionnaire
    db.Trognon.insert_one(new_data)
    


def user_input_features():
        #current_date = datetime.date.today()
        surname = st.sidebar.text_input("Nom")
        name = st.sidebar.text_input("Prénom")
        date = st.sidebar.date_input("Date de naissance", datetime.date(2010, 1, 1))
        #age = current_date.year - date.year - ((current_date.month, current_date.day) < (date.month, date.day))
        sex = st.sidebar.selectbox('Sex',('Homme','Femme'))
        #study = st.sidebar.selectbox("Niveau d'etude",('CAP/BEP','Baccalauréat professionnel','Baccalauréat général', 'Bac +2 (DUT/BTS)', 'Bac +3 (Licence)',
        #                                               'Bac +5 (Master)', 'Bac +7 (Doctorat, écoles supérieurs)'))
        #questionnaire = st.sidebar.selectbox('Questionnaire',('TRAQ','FAST','TRAQ+FAST'))
        #st.write("""## Concernant mon utilisation de la planche de transfert:""")
        for i, question in enumerate(Comp, start=1):
            slider_output = st.select_slider(
            f"{question}",
            options=slider_values,
            value=1,
            format_func=stringify
            )
            answers[f"THERM{i}"] = slider_output


        user_data = {"lastName": surname,
                     'firstName': name,
                     'birthDate': date.isoformat(),
                     'sex': sex}
                     #'educationalLevel': study}
        answers_data = answers

        document = {
        #"_id": ObjectId(),  # Generate a new ObjectId
        "user": user_data,
        "answers": answers_data
        #"__v": 0
        }
                
        return document



document = user_input_features()

#if st.button('Enregisterez'):
#    write_data(document)
#save_and_download_csv(df)
#st.write(document)
# for centering the page
#input_date = custom_date_input("Select a date")
#if input_date:
#    st.write("Selected date:", input_date)
     
     
left_co, cent_co,last_co = st.columns(3)
with cent_co:
    button = st.button('Enregistrez')
    st.image("clinicogImg.png", width=200)
    
if button:
     write_data(document)
     st.write("Merci d'avoir participé(e) à ce questionnaire")
     


     

