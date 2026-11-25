# BET261 VIRTUAL AI PRO V1.0

Starter Flask + HTML pour hébergement web et utilisation depuis Android.

## Ce que contient cette V1
- Interface web responsive.
- Enregistrement de matchs et cotes 1/X/2 dans SQLite.
- Enregistrement des scores finaux.
- Historique consultable et export CSV.
- OCR de captures d'écran dans le navigateur (Tesseract.js) : le texte est extrait pour vérification, il n'est pas automatiquement converti en matchs.
- Fréquences historiques de scores, uniquement à partir des résultats enregistrés.

## Limite importante concernant BET261
Cette version ne se connecte PAS automatiquement au compte BET261. Elle n'inclut aucun contournement de connexion, aucune extraction de session et aucun scraping non autorisé. Pour activer un collecteur automatique, il faut une API ou un flux officiel/autorisé, sa documentation et ses conditions d'utilisation. Les variables BET261_API_BASE_URL et BET261_API_TOKEN sont des emplacements réservés, pas une API déjà fonctionnelle.

Ne communiquez jamais votre mot de passe BET261 ni une clé API dans le code, une capture ou un chat.

## Déploiement Render
1. Décompressez le ZIP sur un ordinateur ou dans un dépôt GitHub.
2. Créez un dépôt GitHub privé et ajoutez les fichiers du projet.
3. Sur Render, créez un nouveau Web Service et connectez le dépôt.
4. Build command : `pip install -r requirements.txt`
5. Start command : `gunicorn app:app`
6. Ajoutez un disque persistant si vous voulez conserver `bet261.db` entre les redéploiements. Sans stockage persistant, les données SQLite locales peuvent être perdues.
7. Ouvrez l'URL HTTPS fournie depuis Chrome Android.

## Test local
`pip install -r requirements.txt`
`python app.py`

## Prochaine étape
Obtenir auprès de BET261 une documentation/API ou autorisation d'accès aux données virtuelles. Ensuite seulement, développer le connecteur dans un module séparé.
