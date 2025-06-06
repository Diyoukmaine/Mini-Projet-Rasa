# 🤖 Mini-Projet Rasa

Ce projet est un chatbot conversationnel développé avec [Rasa](https://rasa.com/), une plateforme open source de traitement du langage naturel (NLP) pour créer des assistants virtuels personnalisés.

## 📌 Fonctionnalités

- Compréhension du langage naturel (NLU)
- Classification d’intentions
- Réponses contextuelles selon des règles ou du machine learning
- Actions personnalisées
- Extensible et modulaire

## 🛠️ Technologies

- Python 3
- Rasa (NLU + Core)
- YAML (pour les fichiers de configuration)

## 🚀 Installation

1. **Cloner le dépôt** :

```bash
git clone https://github.com/Diyoukmaine/Mini-Projet-Rasa.git
cd Mini-Projet-Rasa
```
2. **Créer un environnement virtuel (optionnel mais recommandé) **:

```bash
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
```
3. **Installer les dépendances** : 

```bash
pip install rasa
pip install requests
```
## Utilisation :
A. **Entraîner le modèle **:
  ```bash
  rasa train
  ```
  B. **Lancer le chatbot** :
  ```bash
  rasa run --enable-api --cors "*" --debug
  ```
  C. **Lancer le serveur d’actions personnalisées** :
  ```bash
  rasa run actions
  
  ```

