
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

from utils.parsers_ai import music_lyrics_parser, lyrics_parser


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
        
    music_template = r"""Tu es un expert en création de lyrics éducatifs pour apprendre l’anglais à travers la musique. Ta mission est de générer une chanson très courte, claire et extrêmement précise, exclusivement axée sur l'objectif pédagogique indiqué. Chaque phrase doit directement contribuer à faciliter l'apprentissage du thème, sans aucune digression inutile. La pédagogie est centrale et primordiale : il s'agit d'aider à apprendre un cours par la musique.

En te basant entièrement sur les informations suivantes : {elements},

Respecte rigoureusement ces consignes spécifiques :

Thème précis : {theme}.
Ce thème sera le cœur de l’apprentissage.

Orientation pédagogique : {orientation}.
L’objectif est d’expliquer clairement comment utiliser ou comprendre ce terme. Chaque phrase doit impérativement être utile à la compréhension directe du thème enseigné.

Niveau de l'élève : {niveau}.
Adapte strictement le vocabulaire, la complexité grammaticale et la longueur des phrases au niveau indiqué de l’élève.

Style musical : {style}.
Adapte précisément le ton, le rythme et la structure musicale selon le style demandé.

Structure interactive et pédagogique (très important) :
La chanson doit obligatoirement suivre cette structure précise :

Introduction : très courte, présentant simplement le thème de façon attractive pour capter l’attention immédiatement.

Refrain (très important) :

C'est la partie centrale et essentielle.

Le refrain doit être extrêmement court, rythmé, accrocheur et facile à mémoriser.

Il doit résumer clairement les éléments clés du thème à retenir absolument.

Couplet sous forme de dialogue :

Présenté sous forme de dialogue dynamique entre deux personnages clairement identifiés (Personnage A et Personnage B).

Chaque échange du dialogue doit absolument montrer l’utilisation concrète et réelle du thème dans une situation quotidienne réelle.

Chaque phrase doit contenir un exemple concret tiré de la vie réelle, pour illustrer précisément le thème enseigné (par exemple, "My name is Anna (Je m’appelle Anna)", ou "Please pass the salt (S'il te plaît, passe-moi le sel)").

Évite toute phrase générique ou incomplète (par exemple, ne dis pas "Je m'appelle TON NOM", utilise plutôt un exemple réel : "My name is Paul (Je m'appelle Paul)").

Refrain (répété à l’identique) : pour renforcer la mémorisation des éléments essentiels.

Bilinguisme (important) :
Chaque phrase anglaise doit être immédiatement suivie de sa traduction complète en français entre parenthèses. Pour chaque expression spécifique enseignée, la traduction française doit apparaître directement après le mot anglais (exemple : "Thank you (Merci)").

Dynamisme, clarté et concision :
Utilise uniquement un langage simple, direct, très court, rythmé et engageant.
La chanson doit rester très concise et focalisée exclusivement sur l’essentiel pédagogique indiqué.

Génère les lyrics en respectant strictement ces consignes et en intégrant précisément tous les paramètres spécifiés.

{format_instruction}
"""
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