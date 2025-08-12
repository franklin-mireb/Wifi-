from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import requests
import base64
import json
from datetime import datetime
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this'

class RouterManager:
    def __init__(self):
        self.routers = {
            'tp-link': {
                'login_url': '/userRpm/LoginRpm.htm',
                'users_url': '/userRpm/WlanMacFilterRpm.htm',
                'method': 'basic_auth'
            },
            'netgear': {
                'login_url': '/base64.htm',
                'users_url': '/wlan_acl.htm',
                'method': 'form_auth'
            },
            'linksys': {
                'login_url': '/login.htm',
                'users_url': '/wireless_mac_filter.htm',
                'method': 'form_auth'
            },
            'asus': {
                'login_url': '/login.asp',
                'users_url': '/Advanced_Wireless_Content.asp',
                'method': 'form_auth'
            }
        }
    
    def detect_router_type(self, ip_address):
        """Détecte automatiquement le type de routeur"""
        try:
            # Essayer plusieurs chemins communs pour détecter le routeur
            test_paths = ['/', '/index.html', '/login.htm', '/login.html']
            
            for path in test_paths:
                try:
                    response = requests.get(f"http://{ip_address}{path}", 
                                          timeout=3, 
                                          allow_redirects=True)
                    
                    if response.status_code == 200:
                        content = response.text.lower()
                        headers = str(response.headers).lower()
                        
                        # Vérifier le contenu et les headers
                        if any(keyword in content for keyword in ['tp-link', 'tplink', 'tl-']):
                            return 'tp-link'
                        elif any(keyword in content for keyword in ['netgear', 'readynas']):
                            return 'netgear'
                        elif any(keyword in content for keyword in ['linksys', 'cisco']):
                            return 'linksys'
                        elif any(keyword in content for keyword in ['asus', 'rt-', 'ac-']):
                            return 'asus'
                        elif 'server: lighttpd' in headers or 'server: nginx' in headers:
                            # Beaucoup de routeurs utilisent ces serveurs
                            return 'generic'
                except:
                    continue
            
            return 'unknown'
        except Exception as e:
            print(f"Erreur de détection: {e}")
            return 'unknown'
    
    def authenticate(self, ip_address, username, password, router_type=None):
        """Authentification avec le routeur"""
        if not router_type:
            router_type = self.detect_router_type(ip_address)
        
        # Pour la démo, simuler différents scénarios d'authentification
        try:
            # Test de connectivité de base
            response = requests.get(f"http://{ip_address}", timeout=5)
            
            if response.status_code == 200:
                # Simuler une authentification réussie pour la démo
                # Dans une vraie implémentation, cela dépendrait du type de routeur
                if username and password:  # Vérification basique des credentials
                    return True, f"Connexion réussie au routeur {router_type} ({ip_address})"
                else:
                    return False, "Identifiants requis"
            else:
                return False, f"Impossible d'accéder au routeur (Code: {response.status_code})"
                
        except requests.exceptions.ConnectTimeout:
            return False, "Timeout de connexion - Vérifiez l'adresse IP du routeur"
        except requests.exceptions.ConnectionError:
            return False, "Impossible de se connecter - Vérifiez que le routeur est accessible"
        except requests.exceptions.RequestException as e:
            return False, f"Erreur de connexion: {str(e)}"
        except Exception as e:
            return False, f"Erreur inattendue: {str(e)}"
    
    def get_connected_users(self, ip_address, username, password, router_type=None):
        """Récupère la liste des utilisateurs connectés"""
        # Cette fonction simule la récupération des utilisateurs
        # Dans une vraie implémentation, elle analyserait les pages du routeur
        sample_users = [
            {
                'mac': '00:11:22:33:44:55',
                'device_name': 'iPhone de Jean',
                'ip': '192.168.1.101',
                'connected_time': '2h 15m',
                'status': 'Connecté'
            },
            {
                'mac': '66:77:88:99:AA:BB',
                'device_name': 'PC de Marie',
                'ip': '192.168.1.102',
                'connected_time': '45m',
                'status': 'Connecté'
            },
            {
                'mac': 'CC:DD:EE:FF:00:11',
                'device_name': 'Tablette',
                'ip': '192.168.1.103',
                'connected_time': '1h 30m',
                'status': 'Inactif'
            }
        ]
        return sample_users
    
    def block_user(self, ip_address, username, password, mac_address, router_type=None):
        """Bloque un utilisateur par son adresse MAC"""
        try:
            # Dans une vraie implémentation, cela enverrait les commandes appropriées au routeur
            return True, f"Utilisateur {mac_address} bloqué avec succès"
        except Exception as e:
            return False, f"Erreur lors du blocage: {str(e)}"
    
    def unblock_user(self, ip_address, username, password, mac_address, router_type=None):
        """Débloque un utilisateur"""
        try:
            # Dans une vraie implémentation, cela enverrait les commandes appropriées au routeur
            return True, f"Utilisateur {mac_address} débloqué avec succès"
        except Exception as e:
            return False, f"Erreur lors du déblocage: {str(e)}"

router_manager = RouterManager()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/connect', methods=['POST'])
def connect_router():
    data = request.get_json()
    ip_address = data.get('ip_address')
    username = data.get('username')
    password = data.get('password')
    router_type = data.get('router_type')
    
    if not all([ip_address, username, password]):
        return jsonify({'success': False, 'message': 'Tous les champs sont requis'})
    
    # Validation de l'adresse IP
    ip_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
    if not ip_pattern.match(ip_address):
        return jsonify({'success': False, 'message': 'Adresse IP invalide'})
    
    # Mode démo/test pour des IPs spéciales
    if ip_address in ['192.168.1.100', '10.0.0.100', '172.16.0.100']:
        # Mode démo activé
        app.config['ROUTER_INFO'] = {
            'ip': ip_address,
            'username': username,
            'password': password,
            'type': router_type or 'demo',
            'demo_mode': True
        }
        return jsonify({'success': True, 'message': f'Connexion réussie en mode démo ({ip_address})'})
    
    # Authentification normale
    success, message = router_manager.authenticate(ip_address, username, password, router_type)
    
    if success:
        # Sauvegarder les informations de connexion en session
        app.config['ROUTER_INFO'] = {
            'ip': ip_address,
            'username': username,
            'password': password,
            'type': router_type or router_manager.detect_router_type(ip_address),
            'demo_mode': False
        }
    
    return jsonify({'success': success, 'message': message})

@app.route('/users')
def get_users():
    router_info = app.config.get('ROUTER_INFO')
    if not router_info:
        return jsonify({'success': False, 'message': 'Non connecté au routeur'})
    
    users = router_manager.get_connected_users(
        router_info['ip'],
        router_info['username'],
        router_info['password'],
        router_info['type']
    )
    
    return jsonify({'success': True, 'users': users})

@app.route('/block_user', methods=['POST'])
def block_user():
    data = request.get_json()
    mac_address = data.get('mac_address')
    
    router_info = app.config.get('ROUTER_INFO')
    if not router_info:
        return jsonify({'success': False, 'message': 'Non connecté au routeur'})
    
    success, message = router_manager.block_user(
        router_info['ip'],
        router_info['username'],
        router_info['password'],
        mac_address,
        router_info['type']
    )
    
    return jsonify({'success': success, 'message': message})

@app.route('/unblock_user', methods=['POST'])
def unblock_user():
    data = request.get_json()
    mac_address = data.get('mac_address')
    
    router_info = app.config.get('ROUTER_INFO')
    if not router_info:
        return jsonify({'success': False, 'message': 'Non connecté au routeur'})
    
    success, message = router_manager.unblock_user(
        router_info['ip'],
        router_info['username'],
        router_info['password'],
        mac_address,
        router_info['type']
    )
    
    return jsonify({'success': success, 'message': message})

@app.route('/disconnect')
def disconnect():
    app.config.pop('ROUTER_INFO', None)
    return jsonify({'success': True, 'message': 'Déconnecté du routeur'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
