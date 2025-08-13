# 🚀 WiFi Manager - Déploiement GitHub

## 📦 Repository
- **GitHub**: https://github.com/franklin-mireb/Wifi-
- **Auteur**: franklin-mireb
- **Technologie**: Python Flask + Docker + Système de Vouchers

## 🎯 Fonctionnalités
- ✅ Gestion WiFi avancée
- ✅ Système de tickets payants (7$/mois, 0.6$/jour)
- ✅ Interface d'administration
- ✅ API REST complète
- ✅ Sécurité renforcée
- ✅ Docker & déploiement automatique

## 🚀 Déploiement Automatique

### GitHub Actions configurées :
1. **🧪 Tests** - Validation du code
2. **🏗️ Build** - Construction image Docker
3. **🚀 Deploy** - Déploiement automatique
4. **📊 Health Check** - Vérification santé

### Options de déploiement :
- 🐳 **Docker** (Recommandé)
- 🌐 **Vercel** (Alternative)
- 🖥️ **VPS/Cloud** (Production)

## 📋 Variables d'environnement requises

```env
# Application
SECRET_KEY=votre-clé-secrète-32-caractères-minimum
FLASK_ENV=production

# Routeur WiFi
ROUTER_IP=192.168.1.1
ROUTER_USER=admin
ROUTER_PASS=votre-mot-de-passe

# Déploiement (Secrets GitHub)
HOST=votre-serveur-ip
USERNAME=votre-username
SSH_KEY=votre-clé-privée-ssh
APP_URL=https://votre-domaine.com

# Vercel (Optionnel)
VERCEL_TOKEN=votre-token-vercel
ORG_ID=votre-org-id
PROJECT_ID=votre-project-id
```

## 🛠️ Configuration GitHub Secrets

Dans votre repository GitHub → Settings → Secrets → Actions :

```
HOST: IP de votre serveur
USERNAME: Utilisateur SSH
SSH_KEY: Clé privée SSH
APP_URL: URL de votre application
SECRET_KEY: Clé secrète Flask
ROUTER_IP: IP du routeur
ROUTER_USER: Username routeur
ROUTER_PASS: Password routeur
```

## 🚀 Instructions de déploiement

### 1. Push vers GitHub
```bash
git add .
git commit -m "🚀 Déploiement WiFi Manager avec vouchers"
git push origin main
```

### 2. GitHub Actions se déclenchent automatiquement
- Tests exécutés ✅
- Image Docker construite ✅
- Déploiement automatique ✅

### 3. Application disponible
- 🌐 Application principale
- 🎫 Système de vouchers
- 📊 Monitoring

## 📊 Monitoring

- **Health Check**: `/health`
- **Status**: Monitoring automatique
- **Logs**: Via Docker ou GitHub Actions

## 🔄 Workflow de développement

1. **Développement local** → Tests
2. **Commit & Push** → GitHub
3. **GitHub Actions** → Build & Test
4. **Déploiement automatique** → Production
5. **Health Check** → Validation

## 🆘 Support

- **Repository**: https://github.com/franklin-mireb/Wifi-
- **Issues**: Créer un ticket GitHub
- **Documentation**: README.md

---

**🎉 Votre WiFi Manager est prêt pour la production !**
