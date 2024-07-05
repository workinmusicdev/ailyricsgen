

# Utiliser une image officielle de Python comme image de base
FROM python:3.9-slim
LABEL authors="princegedeon03"

# Installer git et autres dépendances nécessaires
RUN apt-get update && \
    apt install bsdtar &&\
    apt-get install unrar &&\g
    apt-get install -y git && \
    apt-get clean \

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de dépendances
COPY req.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r req.txt

# Copier le reste de l'application
COPY . .

# Exposer le port de l'application
EXPOSE 8080

# Commande pour lancer l'application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
