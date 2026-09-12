# 🚀 Railway.app Deployment Guide (Digital Edge FYP)

Yeh guide aapke Django + React + Gemini Chatbot project ko **Railway.app** par live deploy karne ke aasan steps batati hai.

---

## 📋 Pre-requisites (Zaroori Cheezain)
1. **GitHub Account**: [github.com](https://github.com)
2. **Railway Account**: [railway.app](https://railway.app) (GitHub ke sath login karein)
3. **Google Gemini API Key**: [aistudio.google.com](https://aistudio.google.com/)

---

## Step 1: Project ko GitHub par Push karein

Apne computer par terminal / PowerShell open karein aur `Final_FYP` folder me jayein:

```bash
cd e:\Downloads\FYP\Final_FYP

# Git repository shuru karein
git init

# Saari files add karein
git add .

# Pehla commit karein
git commit -m "Initial commit for Railway deployment"

# Main branch set karein
git branch -M main
```

Ab **GitHub** par jayein:
1. `New Repository` create karein (e.g. `digital-edge-ecommerce`).
2. Repository ko **Public** ya **Private** rakhein.
3. GitHub par jo command aayegi use run karein:

```bash
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/digital-edge-ecommerce.git
git push -u origin main
```

---

## Step 2: Railway.app par Project Create karein

1. [Railway Dashboard](https://railway.app/dashboard) par jayein.
2. **+ New Project** button par click karein.
3. **Deploy from GitHub repo** select karein.
4. Apni GitHub repository (`digital-edge-ecommerce`) select karein.
5. Railway automated tarah se `Dockerfile` detect kar lega aur build shuru kar dega.

---

## Step 3: Free PostgreSQL Database Add karein

Permanent data store karne ke liye (products, orders, users):
1. Usi Railway project me upar **+ New** button par click karein.
2. **Database** par click karein.
3. **Add PostgreSQL** select karein.
4. Railway automated tarah se aapki web service ke sath `DATABASE_URL` link kar dega!

---

## Step 4: Environment Variables Add karein

Apni Web Service (Django app) par click karein aur **Variables** tab me jayein:
Neeche diye gaye variables add karein (**+ New Variable**):

| Variable Name | Value | Note |
| :--- | :--- | :--- |
| `GEMINI_API_KEY` | `AIzaSy...` | Aapki Google Gemini API key |
| `SECRET_KEY` | `django-insecure-railway-fyp-production-key-2025` | Random secure string |
| `DEBUG` | `False` | Production security ke liye |
| `ALLOWED_HOSTS` | `*` | Sabhi domains allow karne ke liye |

---

## Step 5: Live Domain Generate karein

1. Web service ki **Settings** tab me jayein.
2. **Networking** section me jayein.
3. **Generate Domain** button par click karein.
4. Aapko ek public URL mil jayega, jaise:
   `https://digital-edge-ecommerce-production.up.railway.app`

---

## Step 6: Initial Products & Data Load karein (Optional / Recommended)

Railway PostgreSQL database me products load karne ke liye:
1. Web service ke **Settings** tab me jayein.
2. Upar **Deployments** tab me ja kar **View Logs** ke sath **Terminal** / **Exec** ka icon hoga.
3. Terminal open karke yeh command run karein:
```bash
python manage.py loaddata products_seed.json
```
Ya superuser banane ke liye:
```bash
python manage.py createsuperuser
```

---

## 🎯 Verification (Check karein)
* Storefront open karein: `https://your-app.up.railway.app`
* Products aur images check karein.
* Right bottom par **AI Chatbot** icon par click karein aur prompt bhejein (jaise: *"What products do you have?"*).
* Admin portal access karein: `https://your-app.up.railway.app/admin`
