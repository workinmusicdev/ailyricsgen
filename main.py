from dotenv import load_dotenv

from inference.infer_extraction import inference, inference_by_theme
from utils.extraction_ai import extraire_elements_key_from_context
from utils.music_generator_ai import generate_music_lyrics


load_dotenv()
path="./docs/test.pdf"
orientation="Origine de Nappoléon et dates marquant de son ascension et comment il est mort"
min_char=1000
max_char=1500
niv_detail=5
#-------------
style="Rap"
nombre_couplet=3
#data=inference(path,orientation=orientation,min_nombre_caracteres=min_char,max_nombre_caracteres=min_char,mode="chroma",k=niv_detail)
#print(data)
#elements=data['answer']
#print(f"------Contexte--------\n{elements}\n-----------------\n")

#data=generate_music_lyrics(elements=elements  , style=style,num_verses=3,taille=1300 ,orientation=orientation)
#print(data)

## format phrase time , phrase time
## Titre -------> parole de musique | Agent

# Theme + orientation --Agent cherche----> Parole
# Intégrer API mettre sur le vps
# FastSpeech manuel
# Repo FastSpeech | LJSpeech"""
#orientation="Comprendre l'intelligence artificielle et des exemples d'application"
#a=inference_by_theme("L'intelligence artificielle",orientation)
#print(a)

#data=generate_music_lyrics(elements=a  , style="Rap",num_verses=3,taille=1300 ,orientation=orientation)
#print(data)
f=""" L'intelligence artificielle (IA) est un domaine de recherche en informatique dédié à la création de systèmes informatiques qui peuvent effectuer des tâches qui nécessitent normalement l'intelligence humaine. Ces tâches comprennent l'apprentissage, la compréhension du langage naturel, la perception visuelle, la reconnaissance de la parole, la prise de décision et la traduction entre les langues.\\n\\nL'IA est utilisée dans une variété d'applications. Par exemple, dans le domaine de la santé, l'IA peut aider à diagnostiquer les maladies, prédire les résultats des patients et personnaliser les traitements. Dans le domaine de l'éducation, l'IA peut aider à personnaliser l'apprentissage pour chaque élève, en adaptant le matériel d'apprentissage à leurs besoins spécifiques. Dans le domaine des affaires, l'IA peut aider à analyser les données pour prendre des décisions éclairées, automatiser les tâches routinières et améliorer l'efficacité opérationnelle.\\n\\nIl existe deux types principaux d'IA : l'IA faible et l'IA forte. L'IA faible est conçue pour effectuer une tâche spécifique, comme la reconnaissance vocale. L'IA forte, en revanche, est une IA qui a la capacité de comprendre, d'apprendre et d'appliquer le savoir.\\n\\nIl est important de noter que, bien que l'IA ait le potentiel d'améliorer de nombreux aspects de notre vie, elle soulève également des questions éthiques et sociétales. Par exemple, l'IA pourrait éventuellement remplacer certains emplois, ce qui pourrait avoir des conséquences économiques et sociales. De plus, l'utilisation de l'IA dans des domaines tels que la surveillance et la prise de décision peut soulever des questions sur la vie privée et l'équité
"""
orientation="Comprendre l'IA et les exemples d'applications"
v=extraire_elements_key_from_context(f,orientation,1300)
print(v.content)