from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
import requests
import base64
import json
from datetime import datetime
import re
import os
from security import SecurityLogger, RouterSecurity, RateLimiter
from voucher_system import VoucherManager, PaymentSimulator
from kuwfi_manager import KUWFIManager
from config import Config

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

# Configuration du routeur KUWFI depuis les variables d'environnement
ROUTER_IP = os.environ.get('ROUTER_IP', '192.168.1.254')
ROUTER_USER = os.environ.get('ROUTER_USER', 'admin') 
ROUTER_PASS = os.environ.get('ROUTER_PASS', 'admin')
WIFI_SSID = os.environ.get('WIFI_SSID', 'mireb wifi')
WIFI_PASSWORD = os.environ.get('WIFI_PASSWORD', '0816448961')

# Initialiser les composants
security_logger = SecurityLogger()
rate_limiter = RateLimiter()
voucher_manager = VoucherManager()
kuwfi_manager = KUWFIManager(ROUTER_IP, ROUTER_USER, ROUTER_PASS)

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
    ip_address = data.get('ip_address', '').strip()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    router_type = data.get('router_type', '')
    
    # Obtenir l'IP du client pour le rate limiting
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', ''))
    
    # Vérifier le rate limiting
    if rate_limiter.is_rate_limited(client_ip):
        security_logger.log_error(f"Rate limit exceeded for IP {client_ip}")
        return jsonify({'success': False, 'message': 'Trop de tentatives. Veuillez réessayer plus tard.'})
    
    # Enregistrer la tentative
    rate_limiter.record_attempt(client_ip)
    
    if not all([ip_address, username, password]):
        return jsonify({'success': False, 'message': 'Tous les champs sont requis'})
    
    # Validation de l'adresse IP avec sécurité renforcée
    if not RouterSecurity.validate_ip_address(ip_address):
        security_logger.log_error(f"Invalid IP address attempted: {ip_address}")
        return jsonify({'success': False, 'message': 'Adresse IP invalide'})
    
    # Nettoyer les entrées utilisateur
    username = RouterSecurity.sanitize_input(username)
    ip_address = RouterSecurity.sanitize_input(ip_address)
    
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
        security_logger.log_connection_attempt(ip_address, username, True)
        return jsonify({'success': True, 'message': f'Connexion réussie en mode démo ({ip_address})'})
    
    # Authentification normale
    success, message = router_manager.authenticate(ip_address, username, password, router_type)
    
    # Logger la tentative de connexion
    security_logger.log_connection_attempt(ip_address, username, success)
    
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
    mac_address = data.get('mac_address', '').strip()
    
    router_info = app.config.get('ROUTER_INFO')
    if not router_info:
        return jsonify({'success': False, 'message': 'Non connecté au routeur'})
    
    # Validation de l'adresse MAC
    if not RouterSecurity.validate_mac_address(mac_address):
        security_logger.log_error(f"Invalid MAC address attempted: {mac_address}")
        return jsonify({'success': False, 'message': 'Adresse MAC invalide'})
    
    success, message = router_manager.block_user(
        router_info['ip'],
        router_info['username'],
        router_info['password'],
        mac_address,
        router_info['type']
    )
    
    # Logger l'action
    security_logger.log_user_action(f"BLOCK_{('SUCCESS' if success else 'FAILED')}", mac_address, router_info['ip'])
    
    return jsonify({'success': success, 'message': message})

@app.route('/unblock_user', methods=['POST'])
def unblock_user():
    data = request.get_json()
    mac_address = data.get('mac_address', '').strip()
    
    router_info = app.config.get('ROUTER_INFO')
    if not router_info:
        return jsonify({'success': False, 'message': 'Non connecté au routeur'})
    
    # Validation de l'adresse MAC
    if not RouterSecurity.validate_mac_address(mac_address):
        security_logger.log_error(f"Invalid MAC address attempted: {mac_address}")
        return jsonify({'success': False, 'message': 'Adresse MAC invalide'})
    
    success, message = router_manager.unblock_user(
        router_info['ip'],
        router_info['username'],
        router_info['password'],
        mac_address,
        router_info['type']
    )
    
    # Logger l'action
    security_logger.log_user_action(f"UNBLOCK_{('SUCCESS' if success else 'FAILED')}", mac_address, router_info['ip'])
    
    return jsonify({'success': success, 'message': message})

@app.route('/disconnect')
def disconnect():
    app.config.pop('ROUTER_INFO', None)
    return jsonify({'success': True, 'message': 'Déconnecté du routeur'})

# ========== SYSTÈME DE VOUCHERS ==========

@app.route('/vouchers')
def vouchers_page():
    """Page de gestion des vouchers"""
    return render_template('vouchers.html')

@app.route('/api/voucher/plans', methods=['GET'])
def get_voucher_plans():
    """Récupère les plans de tarification"""
    plans = []
    for plan in voucher_manager.plans.values():
        plans.append({
            'id': plan.id,
            'name': plan.name,
            'duration_days': plan.duration_days,
            'price_usd': plan.price_usd,
            'description': plan.description,
            'features': plan.features
        })
    
    return jsonify({'success': True, 'plans': plans})

@app.route('/api/voucher/create', methods=['POST'])
def create_voucher():
    """Crée un nouveau voucher après paiement"""
    data = request.get_json()
    plan_id = data.get('plan_id')
    
    if not plan_id or plan_id not in voucher_manager.plans:
        return jsonify({'success': False, 'message': 'Plan invalide'})
    
    plan = voucher_manager.plans[plan_id]
    
    # Simuler le paiement
    payment_success, payment_message, payment_ref = PaymentSimulator.simulate_payment(
        plan_id, plan.price_usd
    )
    
    if not payment_success:
        security_logger.log_error(f"Payment failed for plan {plan_id}: {payment_message}")
        return jsonify({'success': False, 'message': payment_message})
    
    try:
        # Créer le voucher
        voucher = voucher_manager.create_voucher(plan_id, payment_ref)
        
        # Logger la création
        security_logger.log_user_action(
            f"VOUCHER_CREATED", 
            voucher.code, 
            f"Plan: {plan_id}, Price: ${plan.price_usd}"
        )
        
        return jsonify({
            'success': True,
            'message': 'Voucher créé avec succès',
            'voucher': {
                'code': voucher.code,
                'plan_name': plan.name,
                'expires_at': voucher.expires_at.strftime('%d/%m/%Y à %H:%M'),
                'payment_reference': payment_ref
            }
        })
        
    except Exception as e:
        security_logger.log_error(f"Error creating voucher: {str(e)}")
        return jsonify({'success': False, 'message': 'Erreur lors de la création du voucher'})

@app.route('/api/voucher/validate', methods=['POST'])
def validate_voucher():
    """Valide un code voucher"""
    data = request.get_json()
    code = data.get('code', '').strip().upper()
    
    if not code:
        return jsonify({'success': False, 'message': 'Code voucher requis'})
    
    # Validation du code
    is_valid, message, voucher = voucher_manager.validate_voucher(code)
    
    result = {
        'success': is_valid,
        'message': message
    }
    
    if voucher:
        plan = voucher_manager.plans[voucher.plan_id]
        result['voucher_info'] = {
            'code': voucher.code,
            'plan_name': plan.name,
            'duration_days': plan.duration_days,
            'created_at': voucher.created_at.strftime('%d/%m/%Y à %H:%M'),
            'expires_at': voucher.expires_at.strftime('%d/%m/%Y à %H:%M'),
            'is_used': voucher.is_used,
            'used_at': voucher.used_at.strftime('%d/%m/%Y à %H:%M') if voucher.used_at else None
        }
    
    # Logger la validation
    security_logger.log_user_action(
        f"VOUCHER_VALIDATE_{'SUCCESS' if is_valid else 'FAILED'}", 
        code, 
        message
    )
    
    return jsonify(result)

@app.route('/api/voucher/activate', methods=['POST'])
def activate_voucher():
    """Active un voucher pour un utilisateur"""
    data = request.get_json()
    code = data.get('code', '').strip().upper()
    user_mac = data.get('user_mac', '').strip()
    user_device = data.get('user_device', '').strip()
    
    if not code or not user_mac:
        return jsonify({'success': False, 'message': 'Code voucher et adresse MAC requis'})
    
    # Validation de l'adresse MAC
    if not RouterSecurity.validate_mac_address(user_mac):
        return jsonify({'success': False, 'message': 'Adresse MAC invalide'})
    
    # Activer le voucher
    success, message = voucher_manager.use_voucher(code, user_mac, user_device)
    
    if success:
        # Dans une vraie implémentation, ici on débloquerait l'utilisateur sur le routeur
        router_info = app.config.get('ROUTER_INFO')
        if router_info:
            # Débloquer automatiquement l'utilisateur
            router_manager.unblock_user(
                router_info['ip'],
                router_info['username'],
                router_info['password'],
                user_mac,
                router_info['type']
            )
    
    # Logger l'activation
    security_logger.log_user_action(
        f"VOUCHER_ACTIVATE_{'SUCCESS' if success else 'FAILED'}", 
        f"{code}:{user_mac}", 
        message
    )
    
    return jsonify({'success': success, 'message': message})

@app.route('/api/voucher/stats', methods=['GET'])
def get_voucher_stats():
    """Récupère les statistiques des vouchers"""
    stats = voucher_manager.get_stats()
    return jsonify({'success': True, 'stats': stats})

@app.route('/api/voucher/list', methods=['GET'])
def list_vouchers():
    """Liste tous les vouchers (pour admin)"""
    # Cette route pourrait nécessiter une authentification admin
    vouchers = voucher_manager.get_all_vouchers()
    
    # Formater les données pour l'affichage
    formatted_vouchers = []
    for voucher_info in vouchers:
        voucher = voucher_info['voucher']
        plan = voucher_info['plan']
        
        formatted_vouchers.append({
            'code': voucher.code,
            'plan_name': plan.name,
            'price': plan.price_usd,
            'created_at': voucher.created_at.strftime('%d/%m/%Y %H:%M'),
            'expires_at': voucher.expires_at.strftime('%d/%m/%Y %H:%M'),
            'is_used': voucher.is_used,
            'used_at': voucher.used_at.strftime('%d/%m/%Y %H:%M') if voucher.used_at else None,
            'user_mac': voucher.user_mac,
            'user_device': voucher.user_device,
            'is_valid': voucher_info['is_valid'],
            'payment_reference': voucher.payment_reference
        })
    
    return jsonify({'success': True, 'vouchers': formatted_vouchers})

# ============================================================================
# ROUTES KUWFI ROUTER MANAGEMENT
# ============================================================================

@app.route('/api/router/status')
def router_status():
    """Statut du routeur KUWFI"""
    try:
        status = kuwfi_manager.get_router_status()
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        security_logger.log_error(f"Erreur statut routeur: {e}", request.remote_addr)
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/router/devices')
def connected_devices():
    """Liste des appareils connectés au routeur"""
    try:
        devices = kuwfi_manager.get_connected_devices()
        return jsonify({'success': True, 'devices': devices, 'count': len(devices)})
    except Exception as e:
        security_logger.log_error(f"Erreur récupération devices: {e}", request.remote_addr)
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/router/block', methods=['POST'])
def block_device():
    """Bloque un appareil"""
    try:
        data = request.get_json()
        mac_address = data.get('mac_address')
        
        if not mac_address:
            return jsonify({'success': False, 'error': 'Adresse MAC requise'})
        
        success = kuwfi_manager.block_device(mac_address)
        
        if success:
            security_logger.log_info(f"Device bloqué: {mac_address}", request.remote_addr)
            return jsonify({'success': True, 'message': f'Appareil {mac_address} bloqué'})
        else:
            return jsonify({'success': False, 'error': 'Échec du blocage'})
            
    except Exception as e:
        security_logger.log_error(f"Erreur blocage device: {e}", request.remote_addr)
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/router/unblock', methods=['POST'])
def unblock_device():
    """Débloque un appareil"""
    try:
        data = request.get_json()
        mac_address = data.get('mac_address')
        
        if not mac_address:
            return jsonify({'success': False, 'error': 'Adresse MAC requise'})
        
        success = kuwfi_manager.unblock_device(mac_address)
        
        if success:
            security_logger.log_info(f"Device débloqué: {mac_address}", request.remote_addr)
            return jsonify({'success': True, 'message': f'Appareil {mac_address} débloqué'})
        else:
            return jsonify({'success': False, 'error': 'Échec du déblocage'})
            
    except Exception as e:
        security_logger.log_error(f"Erreur déblocage device: {e}", request.remote_addr)
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/router/config')
def router_config():
    """Configuration actuelle du routeur"""
    return jsonify({
        'success': True,
        'config': {
            'router_ip': ROUTER_IP,
            'router_model': 'KUWFI Access Point',
            'wifi_ssid': WIFI_SSID,
            'network_info': {
                'subnet': '192.168.1.0/24',
                'gateway': '192.168.1.254',
                'dns': '192.168.1.254'
            },
            'management_features': [
                'Device blocking/unblocking',
                'Connected devices list',
                'Voucher integration',
                'Real-time monitoring'
            ]
        }
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
