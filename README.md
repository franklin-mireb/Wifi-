# Gestionnaire WiFi - Application de Gestion des Utilisateurs

Une application web simple pour gérer les utilisateurs WiFi connectés à différents types de routeurs.

## Fonctionnalités

- ✅ **Connexion Multi-Routeurs** : Support pour TP-Link, Netgear, Linksys, ASUS
- ✅ **Détection Automatique** : Détection automatique du type de routeur
- ✅ **Gestion des Utilisateurs** : Visualisation des utilisateurs connectés
- ✅ **Contrôle d'Accès** : Bloquer/Débloquer des utilisateurs par adresse MAC
- ✅ **Interface Moderne** : Interface utilisateur intuitive et responsive
- ✅ **Temps Réel** : Actualisation en temps réel des informations

## Installation

1. **Cloner le projet** :
   ```bash
   git clone <url-du-repo>
   cd Wifi-
   ```

2. **Installer les dépendances** :
   ```bash
   pip install -r requirements.txt
   ```

3. **Lancer l'application** :
   ```bash
   python app.py
   ```

4. **Accéder à l'application** :
   Ouvrez votre navigateur et allez à `http://localhost:5000`

## Utilisation

### Connexion au Routeur

1. **Entrez l'adresse IP** de votre routeur (par défaut : 192.168.1.1)
2. **Sélectionnez le type** de routeur ou laissez la détection automatique
3. **Entrez vos identifiants** (nom d'utilisateur et mot de passe du routeur)
4. **Cliquez sur "Se connecter"**

### Gestion des Utilisateurs

Une fois connecté, vous pouvez :

- **Voir tous les utilisateurs connectés** avec leurs informations :
  - Nom du périphérique
  - Adresse MAC
  - Adresse IP
  - Durée de connexion
  - Statut (Connecté/Inactif)

- **Bloquer un utilisateur** : Empêche l'accès au réseau WiFi
- **Débloquer un utilisateur** : Restaure l'accès au réseau WiFi
- **Actualiser la liste** : Met à jour les informations en temps réel

## Types de Routeurs Supportés

| Marque | Modèles | Méthode d'Auth |
|--------|---------|----------------|
| **TP-Link** | Archer, TL-WR, etc. | HTTP Basic Auth |
| **Netgear** | Nighthawk, R6000, etc. | Form Auth |
| **Linksys** | EA, WRT, etc. | Form Auth |
| **ASUS** | RT-AC, RT-AX, etc. | Form Auth |

## Structure du Projet

```
Wifi-/
├── app.py                 # Application Flask principale
├── templates/
│   └── index.html        # Interface utilisateur
├── requirements.txt      # Dépendances Python
└── README.md            # Documentation
```

## Configuration

### Paramètres par Défaut

- **Port** : 5000
- **Host** : 0.0.0.0 (accessible depuis le réseau local)
- **Debug** : Activé (à désactiver en production)

### Sécurité

⚠️ **Important** : Cette application est destinée à un usage local. Pour un déploiement en production :

1. Changez la `secret_key` dans `app.py`
2. Désactivez le mode debug
3. Utilisez HTTPS
4. Implémentez une authentification utilisateur
5. Utilisez une base de données pour stocker les sessions

## Fonctionnement Technique

### Détection Automatique

L'application détecte automatiquement le type de routeur en analysant :
- Le contenu de la page d'accueil
- Les chaînes de caractères spécifiques aux fabricants
- Les structures d'URL caractéristiques

### Authentification

Deux méthodes d'authentification sont supportées :
- **HTTP Basic Authentication** : Pour les routeurs TP-Link
- **Form Authentication** : Pour Netgear, Linksys, ASUS

### Gestion des Utilisateurs

L'application communique avec le routeur via :
- Requêtes HTTP/HTTPS
- Analyse du HTML des pages d'administration
- Envoi de commandes de configuration

## Dépannage

### Problèmes de Connexion

1. **Vérifiez l'adresse IP** du routeur
2. **Confirmez les identifiants** d'administration
3. **Assurez-vous** que l'interface web du routeur est activée
4. **Vérifiez la connectivité réseau** avec le routeur

### Routeur Non Supporté

Si votre routeur n'est pas automatiquement détecté :
1. Essayez de sélectionner manuellement le type
2. Vérifiez la documentation du routeur pour l'API/interface web
3. Contactez le support pour ajouter votre modèle

## Développement

### Ajouter un Nouveau Type de Routeur

1. **Ajoutez la configuration** dans `RouterManager.routers`
2. **Implémentez la logique** de détection dans `detect_router_type()`
3. **Testez** l'authentification et les commandes

### API Endpoints

- `POST /connect` : Connexion au routeur
- `GET /users` : Liste des utilisateurs connectés
- `POST /block_user` : Bloquer un utilisateur
- `POST /unblock_user` : Débloquer un utilisateur
- `GET /disconnect` : Déconnexion du routeur

## Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer de nouvelles fonctionnalités
- Ajouter le support pour de nouveaux routeurs
- Améliorer la documentation

## Auteur

Développé avec ❤️ pour simplifier la gestion des réseaux WiFi domestiques.
