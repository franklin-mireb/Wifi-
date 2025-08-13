import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Ajouter le répertoire parent au path pour importer app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import RouterManager, app

class TestRouterManager(unittest.TestCase):
    
    def setUp(self):
        self.router_manager = RouterManager()
    
    def test_router_types_loaded(self):
        """Test que les types de routeurs sont correctement chargés"""
        expected_types = ['tp-link', 'netgear', 'linksys', 'asus']
        for router_type in expected_types:
            self.assertIn(router_type, self.router_manager.routers)
    
    @patch('requests.get')
    def test_detect_router_type_tplink(self, mock_get):
        """Test de détection TP-Link"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "TP-Link Router Configuration"
        mock_get.return_value = mock_response
        
        result = self.router_manager.detect_router_type("192.168.1.1")
        self.assertEqual(result, 'tp-link')
    
    @patch('requests.get')
    def test_detect_router_type_netgear(self, mock_get):
        """Test de détection Netgear"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "NETGEAR Router Setup"
        mock_get.return_value = mock_response
        
        result = self.router_manager.detect_router_type("192.168.1.1")
        self.assertEqual(result, 'netgear')
    
    @patch('requests.get')
    def test_detect_router_type_unknown(self, mock_get):
        """Test de détection routeur inconnu"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Unknown Router Brand"
        mock_get.return_value = mock_response
        
        result = self.router_manager.detect_router_type("192.168.1.1")
        self.assertEqual(result, 'unknown')
    
    @patch('requests.get')
    def test_detect_router_type_connection_error(self, mock_get):
        """Test de gestion d'erreur de connexion"""
        mock_get.side_effect = Exception("Connection error")
        
        result = self.router_manager.detect_router_type("192.168.1.1")
        self.assertEqual(result, 'unknown')
    
    def test_get_connected_users_sample_data(self):
        """Test que la fonction retourne des données d'exemple"""
        users = self.router_manager.get_connected_users("192.168.1.1", "admin", "password")
        
        self.assertIsInstance(users, list)
        self.assertGreater(len(users), 0)
        
        # Vérifier la structure des données utilisateur
        user = users[0]
        required_fields = ['mac', 'device_name', 'ip', 'connected_time', 'status']
        for field in required_fields:
            self.assertIn(field, user)
    
    def test_block_user_success(self):
        """Test de blocage d'utilisateur"""
        success, message = self.router_manager.block_user(
            "192.168.1.1", "admin", "password", "00:11:22:33:44:55"
        )
        
        self.assertTrue(success)
        self.assertIn("bloqué", message)
    
    def test_unblock_user_success(self):
        """Test de déblocage d'utilisateur"""
        success, message = self.router_manager.unblock_user(
            "192.168.1.1", "admin", "password", "00:11:22:33:44:55"
        )
        
        self.assertTrue(success)
        self.assertIn("débloqué", message)

class TestFlaskApp(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
    
    def test_index_route(self):
        """Test de la route principale"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Gestionnaire WiFi', response.data)
    
    def test_connect_missing_data(self):
        """Test de connexion avec données manquantes"""
        response = self.app.post('/connect', 
                                json={'ip_address': '192.168.1.1'})
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertIn('requis', data['message'])
    
    def test_connect_invalid_ip(self):
        """Test de connexion avec IP invalide"""
        response = self.app.post('/connect', 
                                json={
                                    'ip_address': 'invalid-ip',
                                    'username': 'admin',
                                    'password': 'password'
                                })
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertIn('invalide', data['message'])
    
    def test_users_not_connected(self):
        """Test de récupération des utilisateurs sans connexion"""
        response = self.app.get('/users')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertFalse(data['success'])
        self.assertIn('Non connecté', data['message'])
    
    def test_disconnect(self):
        """Test de déconnexion"""
        response = self.app.get('/disconnect')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])

if __name__ == '__main__':
    unittest.main()
