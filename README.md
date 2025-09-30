# FFGolf Scraper

Un scraper Python pour extraire les informations des terrains de golf depuis le site de la Fédération Française de Golf (FFGolf).

## Description

Ce scraper collecte automatiquement les informations détaillées des terrains de golf à travers toute la France depuis le site officiel de la FFGolf. Il navigue à travers toutes les régions françaises et extrait les données complètes de chaque terrain de golf, incluant les coordonnées, la localisation et les informations de contact.

## Fonctionnalités

- Scrape les terrains de golf de toutes les régions françaises
- Extrait les informations détaillées pour chaque terrain :
  - Nom
  - Adresse
  - Numéro de téléphone
  - Email
  - Site web
  - URL FFGolf
  - Région
- Exporte les données au format Excel
- Inclut une limitation du taux de requêtes pour respecter le serveur
- Mode test intégré (actuellement limité à 2 régions et 5 terrains par région)
- Sortie colorée pour une meilleure lisibilité

## Prérequis

- Python 3.7+
- Voir `requirements.txt` pour les dépendances des packages

## Installation

1. Clonez ce dépôt ou téléchargez le script
2. Installez les packages requis :

```bash
pip install -r requirements.txt
```

## Utilisation

### Utilisation de base

Par défaut, le scraper s'exécute en mode test (2 régions, 5 terrains de golf par région) :

```bash
python ffgolf_scraper.py
```

### Options de ligne de commande

```bash
# Mode test (par défaut) : 2 régions, 5 golfs par région
python ffgolf_scraper.py --test

# Scraper TOUTES les régions et TOUS les terrains de golf
python ffgolf_scraper.py --all

# Limiter à un nombre spécifique de régions
python ffgolf_scraper.py --max-regions 3

# Limiter à un nombre spécifique de golfs par région
python ffgolf_scraper.py --max-golfs 10

# Combiner les limites : 5 régions, 20 golfs par région
python ffgolf_scraper.py --max-regions 5 --max-golfs 20

# Ajuster le délai entre les requêtes (en secondes)
python ffgolf_scraper.py --all --delay 1.0

# Spécifier un nom de fichier de sortie personnalisé
python ffgolf_scraper.py --all --output mes_golfs.xlsx

# Exemple complet avec toutes les options
python ffgolf_scraper.py --max-regions 3 --max-golfs 10 --delay 0.8 --output golfs_sample.xlsx
```

### Drapeaux disponibles

- `--test` : Exécuter en mode test (2 régions, 5 golfs par région) - c'est le comportement par défaut
- `--all` : Scraper toutes les régions et tous les terrains de golf (supprime toutes les limites)
- `--max-regions N` : Nombre maximum de régions à scraper
- `--max-golfs N` : Nombre maximum de terrains de golf par région
- `--delay SECONDES` : Délai entre les requêtes en secondes (par défaut : 0.5)
- `--output NOMFICHIER` : Nom du fichier Excel de sortie (par défaut : golfs_france.xlsx)

### Aide

Pour voir toutes les options disponibles :

```bash
python ffgolf_scraper.py --help
```

## Sortie

Le scraper génère un fichier Excel (`golfs_france.xlsx`) avec les colonnes suivantes :

- **region** : La région française
- **nom** : Nom du terrain de golf
- **adresse** : Adresse
- **telephone** : Numéro de téléphone
- **email** : Adresse email
- **site_web** : URL du site web
- **url_ffgolf** : URL du profil FFGolf

## Sortie colorée

Le scraper utilise des codes couleur pour améliorer la lisibilité :

- 🟢 **Vert** : Messages de succès et résultats finaux
- 🟡 **Jaune** : Avertissements et erreurs (champs manquants)
- 🔵 **Bleu** : En-têtes de région et messages d'information
- 🟣 **Magenta** : En-têtes de mode
- 🔵 **Cyan** : Informations générales

## Notes importantes

- **Soyez respectueux** : Ce scraper inclut une limitation du taux de requêtes pour éviter de surcharger les serveurs FFGolf
- **Conditions d'utilisation** : Assurez-vous de respecter les conditions d'utilisation de FFGolf et le fichier robots.txt
- **Utilisation des données** : Utilisez les données scrapées de manière responsable et conformément aux lois applicables
- **Maintenance** : Les changements de structure du site web peuvent nécessiter des mises à jour du script

## Gestion des erreurs

Le scraper inclut la gestion des erreurs pour :
- Les requêtes HTTP échouées
- Les champs de données manquants
- Les problèmes de réseau

Les erreurs sont enregistrées dans la console avec des messages descriptifs et une indentation appropriée.

## Licence

Ce projet est fourni tel quel à des fins éducatives. Veuillez vous assurer d'avoir l'autorisation de scraper le site web cible et de respecter toutes les conditions d'utilisation applicables.

## Contribution

N'hésitez pas à soumettre des issues, forker le dépôt et créer des pull requests pour toute amélioration.

## Avertissement

Cet outil est à des fins éducatives. L'auteur n'est pas responsable de toute utilisation abusive de ce scraper. Respectez toujours les conditions d'utilisation des sites web et les fichiers robots.txt.