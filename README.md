# ⚙️ STANTECH CONSULTING - Backend Django (REST API)

Ce dossier `backend/` contient l'API REST complète et le back-office d'administration de **STANTECH CONSULTING**, prêt pour un déploiement indépendant (sur Render, Railway, Heroku, Fly.io ou un VPS).

---

## 📂 Structure du Backend

```
backend/
├── core/                   # Application principale (Modèles, API Views, Serializers, URLs)
├── stantech_project/       # Configuration Django (settings, wsgi, asgi, urls)
├── templates/              # Templates du Dashboard admin custom & SSR
├── static/                 # Fichiers statiques du backend et de l'administration
├── staticfiles/            # Fichiers compilés par collectstatic
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

### Option A : Déploiement sur Render (Recommandé - Gratuit)
1. Créez un compte sur [render.com](https://render.com).
2. Cliquez sur **New +** -> **Web Service**.
3. Connectez votre dépôt GitHub.
4. Définissez :
   * **Root Directory** : `backend`
   * **Environment** : `Python 3`
   * **Build Command** : `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   * **Start Command** : `gunicorn stantech_project.wsgi:application`
5. Ajoutez les variables d'environnement :
   * `SECRET_KEY` : *(votre clé secrète Django)*
   * `DEBUG` : `False`
   * `ALLOWED_HOSTS` : `*` ou `.onrender.com`
   * `CORS_ALLOW_ALL` : `True`

### Option B : Déploiement sur Railway
1. Ouvrez [railway.app](https://railway.app) -> **New Project** -> **Deploy from GitHub repo**.
2. Dans les paramètres, indiquez **Root Directory** = `backend`.
3. Railway détecte automatiquement le `Procfile` et le `requirements.txt`.

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
