#!/usr/bin/env python3
"""
Gestionnaire spécialisé pour routeur KUWFI
Gestion des utilisateurs connectés et contrôle d'accès
"""

import requests
import json
import re
from datetime import datetime
import base64
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

class KUWFIManager:
    def __init__(self, router_ip='192.168.1.254', username='admin', password='admin', simulation_mode=False):
        self.router_ip = router_ip
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.base_url = f"http://{router_ip}"
        self.authenticated = False
        self.simulation_mode = simulation_mode
        
        # URLs courantes pour routeurs KUWFI/générique
        self.endpoints = {
            'login': '/login.html',
            'admin': '/admin.html',
            'wireless': '/wireless.html', 
            'status': '/status.html',
            'dhcp': '/dhcp.html',
            'firewall': '/firewall.html'
        }
    
    def authenticate(self):
        """Authentification sur le routeur KUWFI"""
        try:
            # Méthode 1: Authentification Basic Auth
            auth_basic = base64.b64encode(f"{self.username}:{self.password}".encode()).decode()
            self.session.headers.update({
                'Authorization': f'Basic {auth_basic}',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            # Test de connexion
            response = self.session.get(f"{self.base_url}/")
            
            if response.status_code == 200:
                self.authenticated = True
                return True
                
            # Méthode 2: Authentification par formulaire
            login_data = {
                'username': self.username,
                'password': self.password,
                'submit': 'Login'
            }
            
            response = self.session.post(f"{self.base_url}/login.html", data=login_data)
            
            if response.status_code == 200 and 'admin' in response.text.lower():
                self.authenticated = True
                return True
                
            return False
            
        except Exception as e:
            print(f"Erreur authentification: {e}")
            return False
    
    def get_connected_devices(self):
        """Récupère la liste des appareils connectés"""
        if self.simulation_mode:
            return self._get_simulated_devices()
            
        if not self.authenticated:
            if not self.authenticate():
                return []
        
        try:
            devices = []
            
            # Méthode 1: Page DHCP clients
            response = self.session.get(f"{self.base_url}/dhcp.html")
            if response.status_code == 200:
                devices.extend(self._parse_dhcp_clients(response.text))
            
            # Méthode 2: Page status/statistiques
            response = self.session.get(f"{self.base_url}/status.html")
            if response.status_code == 200:
                devices.extend(self._parse_wireless_clients(response.text))
            
            # Méthode 3: API JSON si disponible
            try:
                response = self.session.get(f"{self.base_url}/api/devices")
                if response.status_code == 200:
                    api_data = response.json()
                    devices.extend(self._parse_api_devices(api_data))
            except:
                pass
            
            # Dédoublonner par adresse MAC
            unique_devices = {}
            for device in devices:
                mac = device.get('mac', '').lower()
                if mac and mac not in unique_devices:
                    unique_devices[mac] = device
            
            return list(unique_devices.values())
            
        except Exception as e:
            print(f"Erreur récupération devices: {e}")
            return []
    
    def _parse_dhcp_clients(self, html_content):
        """Parse les clients DHCP depuis le HTML"""
        devices = []
        
        # Recherche de patterns HTML courants
        patterns = [
            r'<tr[^>]*>.*?<td[^>]*>([^<]+)</td>.*?<td[^>]*>([a-fA-F0-9:]{17})</td>.*?<td[^>]*>([^<]+)</td>',
            r'(?i)ip[:\s]*([0-9.]+).*?mac[:\s]*([a-fA-F0-9:]{17})',
            r'([0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}).*?([a-fA-F0-9:]{17})'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                if len(match) >= 2:
                    device = {
                        'ip': match[0].strip(),
                        'mac': match[1].strip(),
                        'hostname': match[2].strip() if len(match) > 2 else 'Unknown',
                        'status': 'connected',
                        'connection_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'device_type': self._detect_device_type(match[1].strip())
                    }
                    devices.append(device)
        
        return devices
    
    def _parse_wireless_clients(self, html_content):
        """Parse les clients WiFi depuis le HTML"""
        devices = []
        
        # Patterns pour clients WiFi
        wifi_patterns = [
            r'wireless.*?([a-fA-F0-9:]{17}).*?([0-9.]+)',
            r'wlan.*?([a-fA-F0-9:]{17}).*?signal[:\s]*([0-9-]+)',
        ]
        
        for pattern in wifi_patterns:
            matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
            for match in matches:
                device = {
                    'mac': match[0].strip(),
                    'ip': match[1].strip() if '.' in match[1] else 'N/A',
                    'signal_strength': match[1].strip() if '-' in match[1] else 'N/A',
                    'connection_type': 'WiFi',
                    'status': 'connected',
                    'device_type': self._detect_device_type(match[0].strip())
                }
                devices.append(device)
        
        return devices
    
    def _parse_api_devices(self, api_data):
        """Parse les données d'API JSON"""
        devices = []
        
        if isinstance(api_data, dict):
            # Structure API courante
            if 'devices' in api_data:
                for device in api_data['devices']:
                    devices.append({
                        'mac': device.get('mac', ''),
                        'ip': device.get('ip', ''),
                        'hostname': device.get('name', device.get('hostname', 'Unknown')),
                        'status': device.get('status', 'connected'),
                        'connection_type': device.get('type', 'Unknown'),
                        'device_type': self._detect_device_type(device.get('mac', ''))
                    })
        
        return devices
    
    def _detect_device_type(self, mac_address):
        """Détecte le type d'appareil basé sur l'adresse MAC"""
        if not mac_address:
            return 'Unknown'
        
        # Préfixes MAC connus
        oui_database = {
            '00:50:56': 'VMware',
            '08:00:27': 'VirtualBox',
            '00:1B:63': 'Apple',
            '00:22:41': 'Apple',
            '28:CF:E9': 'Apple',
            '3C:07:54': 'Apple iPhone',
            '00:26:BB': 'Apple',
            'BC:85:56': 'Apple AirPods',
            '40:A6:D9': 'Apple',
            '00:15:5D': 'Microsoft',
            '00:03:FF': 'Microsoft',
            'AC:22:0B': 'Samsung',
            '00:16:32': 'Samsung',
            'E8:50:8B': 'Samsung',
            '34:23:87': 'Samsung Galaxy',
            '00:1A:11': 'Google',
            'F4:F5:E8': 'Google Pixel',
            'AC:37:43': 'HTC',
            '00:23:76': 'HTC',
            '00:90:4C': 'HTC',
            '2C:59:E5': 'Huawei',
            '00:E0:FC': 'Huawei',
            'C8:94:02': 'Huawei',
            '38:BC:1A': 'Xiaomi',
            '50:8F:4C': 'Xiaomi',
            '74:51:BA': 'Xiaomi',
            '00:15:00': 'D-Link',
            '00:05:5D': 'D-Link',
            '00:1B:11': 'TP-Link',
            '14:CC:20': 'TP-Link',
            '00:1E:58': 'Netgear',
            '00:09:5B': 'Netgear'
        }
        
        mac_prefix = mac_address[:8].upper()
        return oui_database.get(mac_prefix, 'Unknown Device')
    
    def block_device(self, mac_address):
        """Bloque un appareil par adresse MAC"""
        try:
            # Ajouter à la liste noire MAC
            block_data = {
                'mac_address': mac_address,
                'action': 'block',
                'submit': 'Apply'
            }
            
            response = self.session.post(f"{self.base_url}/firewall.html", data=block_data)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Erreur blocage device: {e}")
            return False
    
    def unblock_device(self, mac_address):
        """Débloque un appareil"""
        try:
            unblock_data = {
                'mac_address': mac_address,
                'action': 'allow',
                'submit': 'Apply'
            }
            
            response = self.session.post(f"{self.base_url}/firewall.html", data=unblock_data)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Erreur déblocage device: {e}")
            return False
    
    def _get_simulated_devices(self):
        """Retourne des appareils simulés pour les tests"""
        return [
            {
                'mac': 'de:b6:92:14:6a:15',
                'ip': '192.168.1.73',
                'hostname': 'Smartphone-User',
                'status': 'connected',
                'connection_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'device_type': 'Samsung Galaxy',
                'connection_type': 'WiFi',
                'signal_strength': '-45 dBm'
            },
            {
                'mac': '3c:07:54:12:34:56',
                'ip': '192.168.1.82',
                'hostname': 'iPhone-13',
                'status': 'connected',
                'connection_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'device_type': 'Apple iPhone',
                'connection_type': 'WiFi',
                'signal_strength': '-38 dBm'
            },
            {
                'mac': '00:1b:63:78:90:12',
                'ip': '192.168.1.95',
                'hostname': 'MacBook-Pro',
                'status': 'connected',
                'connection_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'device_type': 'Apple MacBook',
                'connection_type': 'WiFi',
                'signal_strength': '-42 dBm'
            },
            {
                'mac': 'ac:22:0b:45:67:89',
                'ip': '192.168.1.68',
                'hostname': 'Samsung-Tablet',
                'status': 'connected',
                'connection_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'device_type': 'Samsung Galaxy Tab',
                'connection_type': 'WiFi',
                'signal_strength': '-50 dBm'
            }
        ]
    
    def get_router_status(self):
        """Récupère le statut du routeur"""
        if self.simulation_mode:
            return {
                'status': 'online',
                'ip': self.router_ip,
                'uptime': '2 days, 14:30:25',
                'memory_usage': '45% (128MB/256MB)',
                'cpu_usage': '23%',
                'connected_devices': len(self._get_simulated_devices()),
                'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'model': 'KUWFI Access Point Simulator'
            }
        try:
            response = self.session.get(f"{self.base_url}/status.html")
            
            if response.status_code == 200:
                # Parse des informations système
                uptime_match = re.search(r'uptime[:\s]*([^<\n]+)', response.text, re.IGNORECASE)
                memory_match = re.search(r'memory[:\s]*([^<\n]+)', response.text, re.IGNORECASE)
                cpu_match = re.search(r'cpu[:\s]*([^<\n]+)', response.text, re.IGNORECASE)
                
                return {
                    'status': 'online',
                    'ip': self.router_ip,
                    'uptime': uptime_match.group(1).strip() if uptime_match else 'Unknown',
                    'memory_usage': memory_match.group(1).strip() if memory_match else 'Unknown',
                    'cpu_usage': cpu_match.group(1).strip() if cpu_match else 'Unknown',
                    'connected_devices': len(self.get_connected_devices()),
                    'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            
        except Exception as e:
            print(f"Erreur statut routeur: {e}")
            
        return {
            'status': 'offline',
            'ip': self.router_ip,
            'error': 'Connexion impossible',
            'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def test_connection(self):
        """Test de connexion au routeur"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except:
            return False

if __name__ == "__main__":
    # Test du gestionnaire
    manager = KUWFIManager('192.168.1.254', 'admin', 'admin')
    
    print("🔍 Test de connexion au routeur KUWFI...")
    if manager.test_connection():
        print("✅ Routeur accessible")
        
        if manager.authenticate():
            print("✅ Authentification réussie")
            
            devices = manager.get_connected_devices()
            print(f"📱 Appareils connectés: {len(devices)}")
            
            for device in devices[:5]:  # Afficher les 5 premiers
                print(f"  - {device.get('hostname', 'Unknown')} ({device.get('ip', 'N/A')}) - {device.get('device_type', 'Unknown')}")
                
        else:
            print("❌ Erreur d'authentification")
    else:
        print("❌ Routeur inaccessible")
