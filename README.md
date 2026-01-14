# LBC Immo Tracker

## Description
LBC Immo Tracker est un outil d'automatisation conçu pour simplifier le suivi et l'analyse d'annonces immobilières provenant de la plateforme Leboncoin. L'application permet de centraliser des données extraites via URL dans un tableau de bord interactif, facilitant ainsi la comparaison des biens et la prise de décision.

## Objectif
L'objectif principal est de s'affranchir de la saisie manuelle des informations. En fournissant simplement le lien d'une annonce, l'utilisateur récupère automatiquement les caractéristiques clés (prix, surface, prix au m², DPE) et peut enrichir ces données avec des notes personnelles, des estimations de travaux ou des détails sur l'exposition et les charges.

## Technologies et Outils utilisés

### Langage et Frameworks
* Python : Langage de programmation principal du projet.
* Streamlit : Framework utilisé pour la création de l'interface utilisateur web et le déploiement du tableau de bord interactif.
* Pandas : Bibliothèque de manipulation de données utilisée pour la gestion du tableau et le traitement des fichiers CSV.

### Extraction de données
* Leboncoin-API (Wrapper Python) : Interface permettant de communiquer avec les services de la plateforme pour extraire les métadonnées des annonces.
* Expressions régulières (Regex) : Utilisées pour le nettoyage des chaînes de caractères et l'extraction d'identifiants uniques à partir des URLs.

### Stockage et Déploiement
* CSV (Comma-Separated Values) : Format de stockage local pour la persistance des données.
* GitHub : Gestionnaire de versions et hébergement du code source.
* Streamlit Community Cloud : Plateforme d'hébergement pour l'exécution de l'application en ligne.

## Installation
Le projet nécessite l'installation des dépendances répertoriées dans le fichier requirements.txt via la commande :
pip install -r requirements.txt