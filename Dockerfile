# Utiliser une image officielle d'Ubuntu comme image de base
FROM ubuntu:20.04
LABEL authors="princegedeon03"

# Installer Python, git, unrar et autres dépendances nécessaires
RUN apt-get update && \
    apt-get install -y python3 python3-pip git unrar-free && \
    apt-get clean

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY req.txt .

# Installer les dépendances
RUN pip3 install --no-cache-dir -r req.txt

# Copier le reste de l'application
COPY . .

# Exposer le port de l'application
EXPOSE 8080

# Commande pour lancer l'application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
