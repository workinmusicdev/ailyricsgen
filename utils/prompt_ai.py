
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

def get_lyrics_generator_prompt(mode):
    if mode=="auto":
        music_template = r""""
                    En te basant entièrement sur les informations suivantes : {elements},
                    Générez lyrics en français abordant essentiellement {orientation}  dans le style {style} avec un refrain et des couplets dont tu déterminenras automatiquement le nombre en fonction du contenu.
                    La chanson doit comporter :
                    1. Un refrain répétitif et mémorable, résumant les idées principales.
                    2. plusieurs  couplets dont tu détermineras le nombre.
                    3. Chaque couplet, refrain et pont doit contenir au minimum 4 vers.Et chaque vers séparé par \n"
                    4. La taille minimum est 1500 caractères.
                    
                    \n{format_instruction}
                    """
    else:
        music_template = r""""
            En te basant entièrement sur les informations suivantes : {elements},
            Générez lyrics en français abordant essentiellement {orientation}  dans le style {style} avec un refrain, {num_verses} couplets et un pont.
            La chanson doit comporter :
            1. Un refrain répétitif et mémorable, résumant les idées principales.
            2. {num_verses} couplets.
            3. Chaque couplet, refrain et pont doit contenir au minimum 4 vers.Et chaque vers séparé par \n"
            4. La taille minimum est 1200 caractères et au maximum 1400 caraactères.
            
            \n{format_instruction}
            """

    music_prompt_template = PromptTemplate(
        template=music_template,
        input_variables=['elements', 'style', 'num_verses', 'taille','orientation'],
        partial_variables={'format_instruction': music_lyrics_parser.get_format_instructions()}
    )

    return music_prompt_template