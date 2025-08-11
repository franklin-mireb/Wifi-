import logging
from datetime import datetime

class SecurityLogger:
    def __init__(self):
        # Configuration du logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('wifi_manager.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def log_connection_attempt(self, ip_address, username, success):
        """Log des tentatives de connexion"""
        status = "SUCCESS" if success else "FAILED"
        self.logger.info(f"Connection attempt to {ip_address} with user {username}: {status}")
    
    def log_user_action(self, action, mac_address, ip_address):
        """Log des actions sur les utilisateurs"""
        self.logger.info(f"User action: {action} on MAC {mac_address} from router {ip_address}")
    
    def log_error(self, error_message, context=""):
        """Log des erreurs"""
        self.logger.error(f"Error: {error_message} | Context: {context}")

class RouterSecurity:
    @staticmethod
    def validate_ip_address(ip):
        """Validation renforcée de l'adresse IP"""
        import re
        # Pattern pour IPv4
        ipv4_pattern = re.compile(r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$')
        
        if not ipv4_pattern.match(ip):
            return False
        
        # Vérifier que ce n'est pas une adresse réservée problématique
        forbidden_ranges = [
            '0.0.0.0',
            '255.255.255.255',
            '127.0.0.1'  # localhost seulement si explicitement autorisé
        ]
        
        if ip in forbidden_ranges:
            return False
        
        return True
    
    @staticmethod
    def validate_mac_address(mac):
        """Validation de l'adresse MAC"""
        import re
        mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
        return bool(mac_pattern.match(mac))
    
    @staticmethod
    def sanitize_input(input_string):
        """Nettoyage des entrées utilisateur"""
        if not isinstance(input_string, str):
            return ""
        
        # Supprimer les caractères dangereux
        dangerous_chars = ['<', '>', '"', "'", '&', '\n', '\r', '\t']
        for char in dangerous_chars:
            input_string = input_string.replace(char, '')
        
        return input_string.strip()

class RateLimiter:
    def __init__(self):
        self.attempts = {}
        self.max_attempts = 5
        self.window_minutes = 15
    
    def is_rate_limited(self, ip_address):
        """Vérifier si une IP est limitée"""
        now = datetime.now()
        
        if ip_address not in self.attempts:
            self.attempts[ip_address] = []
        
        # Nettoyer les tentatives anciennes
        self.attempts[ip_address] = [
            attempt for attempt in self.attempts[ip_address]
            if (now - attempt).total_seconds() < (self.window_minutes * 60)
        ]
        
        return len(self.attempts[ip_address]) >= self.max_attempts
    
    def record_attempt(self, ip_address):
        """Enregistrer une tentative"""
        now = datetime.now()
        
        if ip_address not in self.attempts:
            self.attempts[ip_address] = []
        
        self.attempts[ip_address].append(now)
