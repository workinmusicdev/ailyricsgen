import whisper
import re

# Charger le modèle Whisper à l'extérieur
def load_whisper_model(model_name="large"):
    return whisper.load_model(model_name)

# Fonction pour convertir les secondes en format LRC [mm:ss.xx]
def seconds_to_lrc_timestamp(seconds):
    minutes = int(seconds // 60)
    seconds = seconds % 60
    return f"{minutes:02}:{seconds:05.2f}".replace('.', ':')

# Fonction pour générer un fichier LRC à partir d'un fichier audio

def generate_lrc_from_audio(model, audio_path, output_lrc_path):
    # Transcrire l'audio
    result = model.transcribe(audio_path, language="fr")
    # Récupérer les segments de la transcription
    segments = result["segments"]
    # Créer le contenu LRC
    lrc_content = ""
    for segment in segments:
        start_time = seconds_to_lrc_timestamp(segment["start"])
        text = re.sub(r'\s+', ' ', segment["text"]).strip()  # Nettoyer le texte
        lrc_content += f"[{start_time}]{text}\n"


    # Enregistrer le contenu LRC dans un fichier
    with open(output_lrc_path, "w", encoding="utf-8") as lrc_file:
        lrc_file.write(lrc_content)

    print("LRC file generated successfully.")



def seconds_to_lrc_timestamp(seconds):
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    milliseconds = int((seconds % 1) * 100)
    return f"{minutes:02d}:{seconds:02d}.{milliseconds:02d}"

def generate_audio_to_lrc(model, audio_path):
    # Transcrire l'audio
    result = model.transcribe(audio_path, language="fr")
    # Récupérer les segments de la transcription
    segments = result["segments"]
    # Créer le contenu LRC
    lrc_content = ""
    for segment in segments:
        start_time = seconds_to_lrc_timestamp(segment["start"])
        text = re.sub(r'\s+', ' ', segment["text"]).strip()  # Nettoyer le texte
        lrc_content += f"[{start_time}]{text}\n"

    return lrc_content

# Exemple d'utilisation
if __name__ == "__main__":
    # Charger le modèle Whisper
    model = load_whisper_model("large")

    # Spécifiez le chemin du fichier audio et le chemin de sortie LRC
    audio_path = "./539b31d8-6c87-49b1-a1b4-9a3a33a9eca0.mp3"
    output_lrc_path = "output.lrc"

    # Générer le fichier LRC
    o=generate_audio_to_lrc(model, "https://cdn1.suno.ai/df36fdb9-143b-40e7-8ad8-441be1ceb1b6.mp3")
    print(o)
