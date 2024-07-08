# Utiliser une image officielle d'Ubuntu comme image de base
FROM ubuntu:20.04
LABEL authors="princegedeon03"

# Configurer le fuseau horaire
ENV TZ=Africa/Abidjan
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Installer les dépendances nécessaires pour ajouter les dépôts de Python 3.10
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update

# Installer Python 3.10, distutils, git, unrar et autres dépendances nécessaires
RUN apt-get install -y python3.10 python3.10-dev python3-pip python3.10-distutils git unrar-free tzdata && \
    apt-get clean

# Utiliser Python 3.10 comme version par défaut
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

# Installer rq (Redis Queue) et uvicorn
RUN pip3 install rq uvicorn

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
