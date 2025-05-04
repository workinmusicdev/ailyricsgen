import json
import re
from typing import List, Dict, Any

def convert_alignment_to_lrc(alignment_data: Dict[str, Any], output_lrc_path: str) -> None:
    """
    Convertit les données d'alignement en format LRC groupé.
    
    Args:
        alignment_data: Les données d'alignement au format JSON
        output_lrc_path: Le chemin du fichier LRC de sortie
    """
    if not alignment_data or "alignment" not in alignment_data:
        print(f"❌ Données invalides. Clé 'alignment' manquante.")
        return

    words = alignment_data["alignment"]
    grouped_lines = []
    current_line = ""
    current_timestamp = None

    for word_info in words:
        word = word_info["word"].strip()
        if not word:
            continue

        # Si le mot contient un retour à la ligne
        if "\n" in word:
            parts = word.split("\n")
            
            # Ajouter la première partie à la ligne courante
            if parts[0]:
                current_line += parts[0] + " "
            
            # Si on a une ligne en cours, la terminer
            if current_line and current_timestamp is not None:
                mins = int(current_timestamp // 60)
                secs = int(current_timestamp % 60)
                hundredths = int((current_timestamp - int(current_timestamp)) * 100)
                timestamp = f"[{mins:02d}:{secs:02d}.{hundredths:02d}]"
                grouped_lines.append(f"{timestamp} {current_line.strip()}")
            
            # Commencer une nouvelle ligne avec la deuxième partie
            current_line = parts[1] if len(parts) > 1 else ""
            current_timestamp = word_info["start_s"]
            continue

        # Si c'est le début d'une nouvelle ligne
        if not current_line:
            current_timestamp = word_info["start_s"]

        current_line += word + " "

    # Ajouter la dernière ligne si elle existe
    if current_line and current_timestamp is not None:
        mins = int(current_timestamp // 60)
        secs = int(current_timestamp % 60)
        hundredths = int((current_timestamp - int(current_timestamp)) * 100)
        timestamp = f"[{mins:02d}:{secs:02d}.{hundredths:02d}]"
        grouped_lines.append(f"{timestamp} {current_line.strip()}")

    with open(output_lrc_path, "w", encoding="utf-8") as f:
        for line in grouped_lines:
            f.write(line + "\n")

    print(f"✅ Fichier .lrc généré : {output_lrc_path}")

def main():
    # Charger les données depuis le fichier JSON
    try:
        with open("out1.lrc.json", "r", encoding="utf-8") as f:
            input_json = json.load(f)
    except FileNotFoundError:
        print("❌ Fichier out.lrc.json non trouvé")
        return
    except json.JSONDecodeError:
        print("❌ Erreur de décodage JSON")
        return
    
    output_path = "output1.lrc"
    convert_alignment_to_lrc(input_json, output_path)
    
    # Afficher les premières lignes du fichier généré
    print("\nPremières lignes du fichier généré :")
    try:
        with open(output_path, "r", encoding="utf-8") as f:
            for i, line in enumerate(f):
                if i < 5:  # Afficher les 5 premières lignes
                    print(line.strip())
                else:
                    break
    except FileNotFoundError:
        print("❌ Fichier de sortie non généré")

if __name__ == "__main__":
    main() 