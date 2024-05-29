from dotenv import load_dotenv

from inference.infer_extraction import inference, inference_by_theme
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
data=inference(path,orientation=orientation,min_nombre_caracteres=min_char,max_nombre_caracteres=min_char,mode="chroma",k=niv_detail)
#print(data)
elements=data['answer']
print(f"------Contexte--------\n{elements}\n-----------------\n")

data=generate_music_lyrics(elements=elements  , style=style,num_verses=3,taille=1300 ,orientation=orientation)
print(data)

## format phrase time , phrase time
## Titre -------> parole de musique | Agent

# Theme + orientation --Agent cherche----> Parole
# Intégrer API mettre sur le vps
# FastSpeech manuel
# Repo FastSpeech | LJSpeech"""
orientation="Comprendre l'intelligence artificielle et des exemples d'application"
a=inference_by_theme("L'intelligence artificielle",orientation)
print(a)

data=generate_music_lyrics(elements=a  , style="Rap",num_verses=3,taille=1300 ,orientation=orientation)
print(data)