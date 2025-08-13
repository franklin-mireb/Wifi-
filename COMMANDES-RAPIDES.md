# 🚀 COMMANDES RAPIDES - Gestionnaire WiFi

## ⚡ Démarrage Ultra-Rapide

### 🎮 Démo instantanée (30 secondes)
```bash
./demo.sh
```
- Lance l'app automatiquement
- Trouve un port libre
- Configuration automatique
- **Immédiatement disponible !**

### 🚀 Déploiement complet (2 minutes)
```bash
./deploy-facile.sh
```
- Menu interactif
- 4 options de déploiement
- Configuration automatique
- **Zéro configuration manuelle !**

---

## 🎯 Commandes Spécifiques

### 📱 Test local immédiat
```bash
# Option 1 : Script démo
./demo.sh

# Option 2 : Manuel rapide
source .venv/bin/activate
python run.py
```

### 🐳 Docker en 1 ligne
```bash
docker run -d -p 5000:5000 --name wifi-manager $(docker build -q .)
```

### 🌐 Package Web LWS
```bash
./deploy-facile.sh  # Choisir option 3
# Fichier wifi-manager-web.tar.gz créé automatiquement
```

### 🖥️ Installation VPS automatique
```bash
./deploy-facile.sh  # Choisir option 4
# Script install-vps-lws.sh créé automatiquement
```

---

## 🎮 Mode Démo - Credentials

**Pour tous les tests :**
- 🌐 **IP Routeur** : `192.168.1.100`
- 👤 **Utilisateur** : `demo`
- 🔑 **Mot de passe** : `demo`

---

## 🆘 Dépannage Express

### Port occupé ?
```bash
# Le script demo.sh trouve automatiquement un port libre
./demo.sh
```

### Permissions ?
```bash
chmod +x *.sh
```

### Dépendances manquantes ?
```bash
# Ubuntu/Debian
sudo apt install python3 python3-pip python3-venv

# Le reste est automatique avec les scripts
```

---

## 📋 Checklist de Déploiement

- [ ] `./demo.sh` → Test local réussi
- [ ] `./deploy-facile.sh` → Package créé
- [ ] Upload sur hébergement → Application en ligne
- [ ] Test avec mode démo → Fonctionnel
- [ ] Configuration routeur réel → Production

**🎯 Temps total : 5-10 minutes maximum !**

---

## 🎨 Interface Incluse

✅ **Dashboard moderne** avec Bootstrap  
✅ **Mode responsive** (mobile/tablet/desktop)  
✅ **Animations et effets visuels**  
✅ **Aide intégrée** avec modales  
✅ **Mode démo intégré** (aucun routeur requis)  
✅ **Gestion d'erreurs avancée**  
✅ **Feedback temps réel**  

---

**🏆 Promesse : Application fonctionnelle en moins de 5 minutes !**
