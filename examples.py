"""
Exemples d'utilisation avancée du Gestionnaire WiFi

Ce fichier contient des exemples de scripts pour automatiser
la gestion des utilisateurs WiFi.
"""

import requests
import json
import time
from datetime import datetime

class WiFiManagerAPI:
    """Classe pour interagir avec l'API du Gestionnaire WiFi"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def connect_router(self, ip_address, username, password, router_type=None):
        """Se connecter à un routeur"""
        data = {
            'ip_address': ip_address,
            'username': username,
            'password': password,
            'router_type': router_type
        }
        
        response = self.session.post(f"{self.base_url}/connect", json=data)
        return response.json()
    
    def get_users(self):
        """Récupérer la liste des utilisateurs connectés"""
        response = self.session.get(f"{self.base_url}/users")
        return response.json()
    
    def block_user(self, mac_address):
        """Bloquer un utilisateur"""
        data = {'mac_address': mac_address}
        response = self.session.post(f"{self.base_url}/block_user", json=data)
        return response.json()
    
    def unblock_user(self, mac_address):
        """Débloquer un utilisateur"""
        data = {'mac_address': mac_address}
        response = self.session.post(f"{self.base_url}/unblock_user", json=data)
        return response.json()
    
    def disconnect(self):
        """Se déconnecter du routeur"""
        response = self.session.get(f"{self.base_url}/disconnect")
        return response.json()

def example_basic_usage():
    """Exemple d'utilisation basique"""
    print("🔧 Exemple d'utilisation basique")
    print("=" * 40)
    
    # Initialiser l'API
    api = WiFiManagerAPI()
    
    # Se connecter au routeur
    print("📡 Connexion au routeur...")
    result = api.connect_router("192.168.1.1", "admin", "password")
    
    if result['success']:
        print("✅ Connexion réussie!")
        
        # Récupérer les utilisateurs
        print("👥 Récupération des utilisateurs...")
        users_result = api.get_users()
        
        if users_result['success']:
            users = users_result['users']
            print(f"📊 {len(users)} utilisateurs trouvés:")
            
            for user in users:
                print(f"  • {user['device_name']} ({user['mac']}) - {user['status']}")
        
        # Déconnexion
        api.disconnect()
        print("👋 Déconnecté du routeur")
    else:
        print(f"❌ Échec de connexion: {result['message']}")

def example_monitoring():
    """Exemple de monitoring continu"""
    print("📊 Exemple de monitoring continu")
    print("=" * 40)
    
    api = WiFiManagerAPI()
    
    # Configuration du monitoring
    router_config = {
        'ip_address': '192.168.1.1',
        'username': 'admin',
        'password': 'password'
    }
    
    # Connexion initiale
    result = api.connect_router(**router_config)
    if not result['success']:
        print(f"❌ Impossible de se connecter: {result['message']}")
        return
    
    print("🔄 Monitoring en cours... (Ctrl+C pour arrêter)")
    
    try:
        previous_users = set()
        
        while True:
            # Récupérer les utilisateurs actuels
            users_result = api.get_users()
            
            if users_result['success']:
                current_users = {user['mac']: user for user in users_result['users']}
                current_macs = set(current_users.keys())
                
                # Détecter les nouveaux utilisateurs
                new_users = current_macs - previous_users
                if new_users:
                    for mac in new_users:
                        user = current_users[mac]
                        print(f"🔵 Nouvel utilisateur: {user['device_name']} ({mac})")
                
                # Détecter les utilisateurs déconnectés
                disconnected_users = previous_users - current_macs
                if disconnected_users:
                    for mac in disconnected_users:
                        print(f"🔴 Utilisateur déconnecté: {mac}")
                
                # Afficher le statut actuel
                active_count = len([u for u in current_users.values() if u['status'] == 'Connecté'])
                print(f"📈 [{datetime.now().strftime('%H:%M:%S')}] "
                      f"{active_count}/{len(current_users)} utilisateurs actifs")
                
                previous_users = current_macs
            
            # Attendre avant la prochaine vérification
            time.sleep(30)  # Vérifier toutes les 30 secondes
    
    except KeyboardInterrupt:
        print("\n⏹️  Arrêt du monitoring")
        api.disconnect()

def example_scheduled_actions():
    """Exemple d'actions programmées"""
    print("⏰ Exemple d'actions programmées")
    print("=" * 40)
    
    api = WiFiManagerAPI()
    
    # Configuration
    router_config = {
        'ip_address': '192.168.1.1',
        'username': 'admin',
        'password': 'password'
    }
    
    # Règles de contrôle parental (exemple)
    parental_rules = {
        '00:11:22:33:44:55': {  # MAC address de l'appareil enfant
            'name': 'Tablette enfant',
            'blocked_hours': [(22, 0), (7, 0)],  # Bloqué de 22h à 7h
            'max_daily_hours': 4  # Maximum 4h par jour
        }
    }
    
    # Connexion
    result = api.connect_router(**router_config)
    if not result['success']:
        print(f"❌ Impossible de se connecter: {result['message']}")
        return
    
    print("👨‍👩‍👧‍👦 Contrôle parental actif...")
    
    try:
        while True:
            current_time = datetime.now()
            current_hour = current_time.hour
            
            for mac, rules in parental_rules.items():
                # Vérifier les heures de blocage
                for start_hour, end_hour in rules['blocked_hours']:
                    if start_hour <= current_hour < end_hour or \
                       (start_hour > end_hour and (current_hour >= start_hour or current_hour < end_hour)):
                        
                        print(f"🚫 Blocage programmé: {rules['name']} ({mac})")
                        api.block_user(mac)
                        break
                else:
                    # Débloquer si on n'est pas dans une période de blocage
                    print(f"✅ Déblocage: {rules['name']} ({mac})")
                    api.unblock_user(mac)
            
            # Vérifier toutes les heures
            time.sleep(3600)
    
    except KeyboardInterrupt:
        print("\n⏹️  Arrêt du contrôle parental")
        api.disconnect()

def example_backup_configuration():
    """Exemple de sauvegarde de configuration"""
    print("💾 Exemple de sauvegarde de configuration")
    print("=" * 40)
    
    api = WiFiManagerAPI()
    
    # Configuration du routeur
    router_config = {
        'ip_address': '192.168.1.1',
        'username': 'admin',
        'password': 'password'
    }
    
    # Connexion
    result = api.connect_router(**router_config)
    if not result['success']:
        print(f"❌ Impossible de se connecter: {result['message']}")
        return
    
    # Récupérer les utilisateurs
    users_result = api.get_users()
    
    if users_result['success']:
        # Créer une sauvegarde
        backup_data = {
            'timestamp': datetime.now().isoformat(),
            'router': router_config['ip_address'],
            'users': users_result['users']
        }
        
        # Sauvegarder dans un fichier
        filename = f"wifi_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Sauvegarde créée: {filename}")
        print(f"📊 {len(backup_data['users'])} utilisateurs sauvegardés")
    
    api.disconnect()

if __name__ == "__main__":
    print("🌟 Exemples d'utilisation du Gestionnaire WiFi")
    print("=" * 50)
    
    examples = [
        ("Utilisation basique", example_basic_usage),
        ("Monitoring continu", example_monitoring),
        ("Actions programmées", example_scheduled_actions),
        ("Sauvegarde configuration", example_backup_configuration)
    ]
    
    print("Choisissez un exemple:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    
    try:
        choice = int(input("\nVotre choix (1-4): ")) - 1
        if 0 <= choice < len(examples):
            print(f"\n🚀 Exécution: {examples[choice][0]}")
            print("-" * 50)
            examples[choice][1]()
        else:
            print("❌ Choix invalide")
    except (ValueError, KeyboardInterrupt):
        print("\n👋 Au revoir!")
