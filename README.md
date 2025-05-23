Bien vu ! Voici le contenu prêt à être **copié-collé** directement dans ton fichier `monreadme.md` :

---

```md
# 🎤 ailyricsgen

Générateur de musique assisté par IA avec intégration de NGROK, Redis et traitement de fichiers Excel.

---

## ⚙️ Installation & Setup

### 1. Lancer le serveur Redis

```bash
redis-server
```

---

### 2. Créer et activer un environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Installer les dépendances Python

```bash
pip install -r requirements.txt
```

---

### 4. Lancer l'application Flask

```bash
python3 app.py
```

L’application écoute par défaut sur le port `8080`.

---

## 🌍 Rendre l'API publique avec ngrok

Dans un autre terminal :

```bash
ngrok http 8080
```

Copiez le lien `https://xxxx.ngrok.io` généré par ngrok.

---

## 🛠️ Configuration manuelle

### Modifier le lien dans `generate_song.py`

Ouvrir le fichier :

```
utils/sunowrapper/generate_song.py
```

Dans la fonction `generate_music`, remplacer l’ancienne URL par le lien ngrok copié précédemment.

---

### Génération de musique depuis un fichier Excel

Dans le fichier :

```
job.py
```

Utiliser la fonction :

```python
process_lyrics_from_theme()
```

Elle permet de lire les fichiers `.xlsx` et de générer automatiquement des musiques/thèmes.

---

## ✅ Récapitulatif des commandes

```bash
redis-server
source venv/bin/activate
pip install -r requirements.txt
python3 app.py
ngrok http 8080
```

---

## 📁 Arborescence utile

```
ailyricsgen/
├── app.py
├── job.py
├── requirements.txt
├── utils/
│   └── sunowrapper/
│       └── generate_song.py
```

---

## 📌 Remarques

- Crée un compte [ngrok](https://ngrok.com/) pour avoir des liens stables.
- Assure-toi que tes fichiers Excel ont une structure correcte avant d'utiliser `generate_from_theme()`.
```