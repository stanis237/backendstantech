# ⚙️ STANTECH CONSULTING - Backend Django (REST API)

Ce dépôt contient l'API REST Django, le dashboard admin complet et ses templates Django. Il est déployé indépendamment du frontend statique Vercel sur PythonAnywhere.

---

## 📂 Structure du Backend

```
backend/
├── core/                   # Application principale (Modèles, API Views, Serializers, URLs)
├── stantech_project/       # Configuration Django (settings, wsgi, asgi, urls)
├── templates/              # Templates du Dashboard admin custom & SSR
├── static/                 # Fichiers statiques du backend et de l'administration
├── staticfiles/            # Générés par collectstatic (ne pas versionner)
├── media/                  # Fichiers média téléversés (images produits, APK Android)
├── manage.py               # Script de gestion Django
├── requirements.txt        # Dépendances Python
├── Procfile                # Fichier de démarrage Gunicorn (Render / Railway / Heroku)
└── .env.example            # Exemple de variables d'environnement
```

---

## 🌐 Endpoints de l'API REST

L'API utilise Django REST Framework et autorise le CORS pour communiquer de manière sécurisée avec le Frontend hébergé sur un autre domaine (Vercel, Netlify, etc.) :

| Méthode | Endpoint | Description |
|---|---|---|
| `GET` | `/api/home/` | Données complètes de la page d'accueil (services phares, produits, réalisations, apps) |
| `GET` | `/api/categories/?type=service\|product\|realization\|application` | Liste des catégories filtrées par type |
| `GET` | `/api/services/` | Liste de tous les services actifs (filtre optionnel `?category=slug`) |
| `GET` | `/api/services/<slug>/` | Détail d'un service par son slug ou ID |
| `GET` | `/api/products/` | Catalogue de la boutique (filtres : `category`, `search`, `sort`, `featured`) |
| `GET` | `/api/products/<slug>/` | Fiche détaillée d'un produit |
| `GET` | `/api/realisations/` | Portfolio des projets et réalisations |
| `GET` | `/api/applications/` | Suite d'applications SaaS, web et mobiles |
| `POST` | `/api/checkout/` | Validation et enregistrement d'une commande (génère un numéro `ST-XXXXXXXX`) |
| `POST` / `GET` | `/api/track-order/` | Suivi de commande en temps réel par son numéro |
| `POST` | `/api/contact/` | Réception des messages du formulaire de contact et demandes de devis |
| `GET` | `/api/app-info/` | Informations de téléchargement de l'application mobile APK |

---

## 🚀 Déploiement du Backend

### Déploiement sur PythonAnywhere
1. Dans PythonAnywhere, créez une application Web **Manual configuration** avec une version Python compatible avec `requirements.txt`.
2. Dans une console Bash, clonez `https://github.com/stanis237/backendstantech.git` dans votre compte, puis créez un virtualenv compatible avec la version Python choisie.
3. Installez les dépendances avec `pip install -r ~/backend/requirements.txt` et indiquez ce virtualenv dans l’onglet Web.
4. Configurez le fichier WSGI de l’application :
   ```python
   import os
   import sys

   project = '/home/VOTRE_UTILISATEUR/backend'
   if project not in sys.path:
       sys.path.insert(0, project)
   os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stantech_project.settings')
   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```
5. Créez `~/backend/.env` à partir de `.env.example`, avec une clé secrète privée et `DEBUG=False`. N’ajoutez jamais `.env` au dépôt.
6. Dans une console Bash, exécutez `cd ~/backend && python manage.py migrate && python manage.py collectstatic --noinput`.
7. Dans l’onglet Web, mappez `/static/` sur `/home/VOTRE_UTILISATEUR/backend/staticfiles` et `/media/` sur `/home/VOTRE_UTILISATEUR/backend/media`, puis rechargez l’application.

Le frontend appelle `https://stantechbackend.pythonanywhere.com`. Définissez `CORS_ALLOWED_ORIGINS=https://fronts-theta.vercel.app` et `CORS_ALLOW_ALL=False`. Définissez également `FRONTEND_URL=https://fronts-theta.vercel.app` : les liens « Voir le site » du login et du dashboard redirigent ainsi directement vers Vercel. Le dashboard Django reste accessible sous `/dashboard/login/`.

---

## 💻 Démarrage Local

```bash
cd backend
python -m venv venv
# Windows :
.\venv\Scripts\activate
# Linux/Mac :
source venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
L'API est accessible localement sur `http://127.0.0.1:8000`.
