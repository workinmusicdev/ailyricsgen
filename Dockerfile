# Utiliser une image officielle Python 3.10 slim comme image de base
FROM python:3.10-slim
LABEL authors="princegedeon03"

# Configurer le fuseau horaire
ENV TZ=Africa/Abidjan
RUN apt-get update && \
    apt-get install -y tzdata && \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Installer git, unrar et autres dépendances nécessaires
RUN apt-get install -y git  && \
    apt-get clean

# Installer rq (Redis Queue) et uvicorn
RUN pip install rq uvicorn

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
