# 🚀 Déploiement Vercel - WiFi Manager

## 📋 **Guide Étape par Étape**

### **1. 🌐 Aller sur Vercel**
Ouvrez : https://vercel.com/new

### **2. 🔗 Connecter GitHub**
- Cliquez "Continue with GitHub"
- Autorisez Vercel à accéder à vos repos

### **3. 📦 Importer votre Repository**
- Recherchez : `franklin-mireb/Wifi-`
- Cliquez "Import"

### **4. ⚙️ Configuration Projet**

**Framework Preset:** Other
**Root Directory:** ./
**Build Command:** (laisser vide)
**Output Directory:** (laisser vide)
**Install Command:** pip install -r requirements.txt

### **5. 🔐 Variables d'Environnement**

Ajoutez ces variables dans Vercel :

```
SECRET_KEY = votre-clé-secrète-32-caractères-minimum
ROUTER_IP = 192.168.1.1
ROUTER_USER = admin
ROUTER_PASS = votre-mot-de-passe-routeur
FLASK_ENV = production
```

### **6. 🚀 Déployer**
- Cliquez "Deploy"
- Attendez 2-3 minutes
- Votre app sera disponible sur : `https://wifi-manager-xxx.vercel.app`

## 📊 **Post-Déploiement**

### ✅ **Fonctionnalités Disponibles**
- 🌐 Interface principale
- 🎫 Système de vouchers
- 📱 Interface responsive
- 🔐 Sécurité intégrée

### ⚠️ **Limitations Vercel**
- 🔄 Fonctions serverless (pas de persistance session routeur)
- 💾 Stockage temporaire (vouchers.json réinitialisé)
- ⏱️ Timeout 10 secondes max

### 💡 **Solutions**
- Base de données externe (MongoDB, PostgreSQL)
- Stockage Redis pour sessions
- API externes pour persistance

## 🔧 **Optimisations**

### **Performance**
- CDN global automatique
- Mise en cache intelligente
- Compression automatique

### **Monitoring**
- Analytics Vercel intégrés
- Logs en temps réel
- Alertes automatiques

## 🎯 **URL de votre Application**

Après déploiement, votre WiFi Manager sera accessible sur :
- **URL principale :** `https://wifi-manager-xxx.vercel.app`
- **Système vouchers :** `https://wifi-manager-xxx.vercel.app/vouchers`

## 🔄 **Déploiements Automatiques**

Chaque `git push` vers la branche `main` déclenchera un redéploiement automatique !

```bash
# Faire une modification
git add .
git commit -m "✨ Nouvelle fonctionnalité"
git push origin main
# → Redéploiement automatique sur Vercel
```

## 📞 **Support Vercel**

- **Dashboard :** https://vercel.com/dashboard
- **Documentation :** https://vercel.com/docs
- **Support :** https://vercel.com/support

---

**🎉 Votre WiFi Manager sera en ligne en quelques minutes !**
