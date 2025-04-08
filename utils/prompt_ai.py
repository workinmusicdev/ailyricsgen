
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from utils.parsers_ai import music_lyrics_parser


def load_extraction_prompt():
    system_prompt = (
        "Utiliser le contexte pour extraire des points clés"
        "Le texte extrait doit avoir une taille minimale de {nombre_caracteres} caractères et une taille maximale de {nombre_caracteres_max} caractères. "
        "Si l'orientation n'est pas clairement définie dans le contexte, fournissez tout ce qui est pertinent."
        "Context: {context}"
    )

    #system_prompt = system_prompt.format(orientation=orientation, nombre_caracteres=nombre_caracteres)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "Vous devez extraire autant d'informations pertinentes que possible basées sur l'orientation suivante : {input}"),
        ]
    )

    return prompt


def load_extraction_prompt_from_context():
    human_prompt = r"""En te basant uniquement sur les informations ci-après  pour extraire des éléments clés de taille maximale {taille} en te basant sur {orientation}.
     Voici les informations : {elements}
     
     
     \n{format_instruction}"""

    prompt = PromptTemplate(
        template=human_prompt,
        input_variables=["elements", "orientation", "taille"],
        partial_variables={'format_instruction': music_lyrics_parser.get_format_instructions()}
    )

    return prompt

def prompt_format_to_human_lyrics():

    human_prompt = r"""
    Prends ces paroles de musique : {elements}.
    Régénère-moi ces mêmes paroles de musique mais :
    1. Garde-les telles quelles,
    2. Remplace les formules scientifiques et les opérations non textuelles par des mots.
    3. Par exemple, '>' devient 'est supérieur', '+' devient 'plus', et 'f(x)' devient 'f de x'.
    Voici les paroles : {elements}

    \n{format_instruction}
    """



    prompt = PromptTemplate(
        template=human_prompt,
        input_variables=["elements"],
        partial_variables={'format_instruction': lyrics_parser.get_format_instructions()}

    )

    return prompt

def get_lyrics_generator_prompt(mode, langue:str):

    print("################## ***")
    print(langue.lower())
    print("################## ***")

    
    # if langue.lower() == "anglais":

    #     print("################## 00000")
    #     print(langue,"anglais mode")
    #     print("################## 00000")

        # music_template = r"""En te basant entièrement sur les informations suivantes : {elements},
        # Génère des paroles en {langue} et en français, abordant essentiellement {orientation} dans le style {style}, avec un refrain et plusieurs couplets dont tu détermineras automatiquement le nombre en fonction du contenu.
        # L'objectif est d'aider un élève francophone à apprendre l'anglais à travers une combinaison harmonieuse des deux langues dans la chanson. Le français doit être utilisé comme soutien pour introduire ou clarifier des concepts en anglais, de manière fluide et naturelle.

        # La chanson doit comporter :

        # 1. Un refrain répétitif et mémorable, où l'anglais et le français se complètent pour renforcer la mémorisation des idées principales.
        # 2. Plusieurs couplets dont tu détermineras le nombre, avec une alternance fluide entre l'anglais et le français dans chaque couplet pour aider à comprendre le vocabulaire et les structures anglaises.
        # 3. Chaque couplet, refrain et pont doit contenir au minimum 4 vers, avec une combinaison naturelle des deux langues, et chaque vers séparé par un \n.
        # 4. La taille minimum est de 1500 caractères.
        # \n{format_instruction}
        # """
        # être adaptée au thème spécifique suivant ({{thème}}) et

        #         music_template = r"""En te basant entièrement sur les informations suivantes : {elements},
        #         Génère des lyrics sous forme de conversation pour une chanson éducative conçue pour aider des élèves débutants à apprendre l'{langue}. Ces élèves n'ont aucune connaissance préalable de l'anglais et leur langue maternelle est le français. La chanson doit suivre un format de dialogue entre deux personnes, l'un posant des questions et l'autre répondant, en se concentrant sur cette orientation ({orientation})  dans le style suivant {style}. Le but est de permettre aux élèves d'apprendre {orientation}, tout en rendant les mots et les phrases facilement reconnaissables et mémorables.

        # Chaque ligne ou phrase en anglais doit être accompagnée de sa traduction en français pour établir une association linguistique claire. Le dialogue doit être répétitif et amical, avec un rythme modéré pour faciliter l'apprentissage. Des répétitions doivent être utilisées pour renforcer la mémorisation, et le ton doit être ludique et encourageant pour rendre l'expérience d'apprentissage agréable. Aucune mention de "personne 1", "personne 2", "réponse A", "réponse B" ou autres termes similaires ne doit être utilisée dans les lyrics générés.
        # \n{format_instruction}
        # """


        # (elements, style, orientation,num_verses=3, taille=1500, mode="auto", langue="français", theme="", niveau="")
        
    music_template = r"""Tu es un expert en création de chansons éducatives pour apprendre l’espagnol à travers la musique.

Tu travailles avec ChatGPT (OpenAI) pour générer une chanson claire, progressive, interactive, et adaptée à des apprenants de niveau A1.

Chaque chanson est centrée sur un objectif pédagogique concret, atteint grâce à une structure musicale répétitive, dialoguée, et basée sur des situations de la vie réelle.



La langue utilisée est l’espagnol, avec une traduction complète en français (entre parenthèses) immédiatement après chaque phrase espagnole.

🔧 Informations à renseigner (à insérer dans les champs entre accolades) :
Langue d’apprentissage : Espagnol (avec traduction en français)

{elements} : Contexte pédagogique général ou module (ex. : “Module 2 – Leçon 4 : les expressions de politesse”)

{theme} : Thème principal de la chanson (ex. : “Exprimer ce qu’on aime”, “Saluer”, “Parler des couleurs primaires”, etc.)

{orientation} : Objectif pédagogique clair (ex. : “À la fin de la chanson, l’élève doit savoir dire ce qu’il aime ou n’aime pas.”)

{niveau} : Niveau CECRL visé → A1

{style} : Style musical souhaité (ex. : Pop, Rap)

{format_instruction} : Précision sur le format attendu. Ex. : “Génère les lyrics avec la structure demandée + une fiche technique à part.”

🎶 STRUCTURE MUSICALE OBLIGATOIRE (à respecter strictement) :
[Introduction – tous ensemble]

➤ Introduction très courte qui annonce clairement le thème.

[Refrain – ensemble]

➤ Obligatoire : ce refrain doit absolument apparaître deux fois à l’identique dans la chanson (une première fois ici, puis une deuxième fois après le couplet).

➤ Il est court, rythmé, répétable, mémorisable, et résume les éléments clés de la leçon.

[Couplet – dialogue A & B]

➤ Dialogue entre deux personnages (“A” et “B”).

➤ Minimum 3 à 5 échanges réels avec utilisation concrète du vocabulaire ou des structures en contexte.

➤ Les phrases sont très simples, courtes, et adaptées au niveau A1 strict.

➤ Utilise des exemples concrets de la vie quotidienne.

➤ Tu peux réutiliser du vocabulaire vu précédemment pour créer des ponts pédagogiques.

[Refrain – identique]

➤ Exactement le même que précédemment. Il doit être copié-collé à l’identique.

➤ Il sert à renforcer la mémorisation.

[Mini-dialogue – optionnel]

➤ Une reprise courte ou une variation ludique.

[Outro – optionnel]

➤ Une dernière ligne simple, de type au revoir ou félicitation.

🗣️ BILINGUISME (à respecter absolument) :
Chaque phrase en espagnol est suivie immédiatement de sa traduction complète en français entre parenthèses.

➤ Exemple : "Me gusta la pizza." (J’aime la pizza.)

Ne pas surcharger en français. Utiliser le français uniquement pour la compréhension.

🎯 OBJECTIF PÉDAGOGIQUE :
Le texte vise un objectif précis et atteignable à la fin de la chanson (ex. : savoir dire ce qu’on aime, saluer quelqu’un, utiliser des couleurs, etc.).

La pédagogie est prioritaire sur le rythme musical : le texte doit être lisible à haute voix en classe, simple, et immédiatement compréhensible pour des élèves débutants.

📄 FICHE TECHNIQUE À FOURNIR AVEC LA CHANSON :
Titre de la chanson

Langue cible : Espagnol

Objectif CECRL : ex. A1 – se présenter, parler de ses goûts…

Objectif pédagogique de la chanson

Vocabulaire cible

Structures grammaticales utilisées

Compétence(s) visée(s) : CO (Compréhension orale), PO (Production orale), CE (Compréhension écrite), etc."""



# 📄 Fiche technique à générer avec chaque chanson :

# À fournir en complément du texte (séparément ou après les lyrics) :

# Titre de la chanson
# Langue cible : ex. Espagnol
# Objectif CECRL : ex. A1 – se présenter / décrire
# Objectif pédagogique de la chanson
# Vocabulaire cible
# Structures grammaticales utilisées
# Compétence(s) visée(s) : CO (Compréhension orale), PO (Production orale), etc.
# Chaque couplet, refrain et pont doit contenir au minimum 4 vers.Et chaque vers séparé par '\n'. La taille minimum est 1500 caractères.
# entre parenthèses

    
    # else:

    #     print("##################")
    #     print(langue,"français mode") 
    #     print("##################")

    #     if mode=="auto":
    #         music_template = r""""
    #                     En te basant entièrement sur les informations suivantes : {elements},
    #                     Générez lyrics en {langue} abordant essentiellement {orientation}  dans le style {style} avec un refrain et des couplets dont tu déterminenras automatiquement le nombre en fonction du contenu.
    #                     La chanson doit comporter :
    #                     1. Un refrain répétitif et mémorable, résumant les idées principales.
    #                     2. plusieurs  couplets dont tu détermineras le nombre.
    #                     3. Chaque couplet, refrain et pont doit contenir au minimum 4 vers.Et chaque vers séparé par \n"
    #                     4. La taille minimum est 1500 caractères.
                        
    #                     \n{format_instruction}
    #                     """
    #     else:
    #         music_template = r""""
    #             En te basant entièrement sur les informations suivantes : {elements},
    #             Générez lyrics en {langue} abordant essentiellement {orientation}  dans le style {style} avec un refrain, {num_verses} couplets et un pont.
    #             La chanson doit comporter :
    #             1. Un refrain répétitif et mémorable, résumant les idées principales.
    #             2. {num_verses} couplets.
    #             3. Chaque couplet, refrain et pont doit contenir au minimum 4 vers.Et chaque vers séparé par \n"
    #             4. La taille minimum est 1200 caractères et au maximum 1400 caraactères.
                
    #             \n{format_instruction}
    #             """

    # Si la langue est anglais, ne génère pas de paroles en français

    music_prompt_template = PromptTemplate(
        template=music_template,
        input_variables=['elements','theme','orientation', 'niveau','style'],
        partial_variables={'format_instruction': music_lyrics_parser.get_format_instructions()}
    )

    print(music_prompt_template)

    return music_prompt_template