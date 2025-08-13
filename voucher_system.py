import uuid
import hashlib
import json
import os
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict
import secrets
import string

@dataclass
class VoucherPlan:
    """Plan de tarification pour les vouchers"""
    id: str
    name: str
    duration_days: int
    price_usd: float
    description: str
    features: List[str]

@dataclass
class Voucher:
    """Voucher/Ticket d'accès"""
    code: str
    plan_id: str
    created_at: datetime
    expires_at: datetime
    is_used: bool = False
    used_at: Optional[datetime] = None
    user_mac: Optional[str] = None
    user_device: Optional[str] = None
    payment_reference: Optional[str] = None

class VoucherManager:
    """Gestionnaire des vouchers/tickets"""
    
    def __init__(self, data_file: str = "vouchers.json"):
        self.data_file = data_file
        self.vouchers: Dict[str, Voucher] = {}
        
        # Plans de tarification prédéfinis
        self.plans = {
            "monthly": VoucherPlan(
                id="monthly",
                name="Accès Mensuel",
                duration_days=30,
                price_usd=7.0,
                description="Accès WiFi illimité pendant 30 jours",
                features=["Accès 24h/24", "Bande passante illimitée", "Support technique"]
            ),
            "daily": VoucherPlan(
                id="daily",
                name="Accès Journalier",
                duration_days=1,
                price_usd=0.6,
                description="Accès WiFi pour une journée",
                features=["Accès 24h", "Bande passante standard"]
            )
        }
        
        self.load_vouchers()
    
    def generate_voucher_code(self, length: int = 12) -> str:
        """Génère un code voucher unique"""
        # Utiliser des caractères facilement lisibles
        characters = string.ascii_uppercase + string.digits
        characters = characters.replace('0', '').replace('O', '').replace('1', '').replace('I', '')
        
        while True:
            code = ''.join(secrets.choice(characters) for _ in range(length))
            # Formatter le code avec des tirets pour la lisibilité
            formatted_code = f"{code[:4]}-{code[4:8]}-{code[8:]}"
            
            # Vérifier l'unicité
            if formatted_code not in self.vouchers:
                return formatted_code
    
    def create_voucher(self, plan_id: str, payment_reference: str = None) -> Voucher:
        """Crée un nouveau voucher"""
        if plan_id not in self.plans:
            raise ValueError(f"Plan {plan_id} non trouvé")
        
        plan = self.plans[plan_id]
        code = self.generate_voucher_code()
        now = datetime.now()
        expires_at = now + timedelta(days=plan.duration_days)
        
        voucher = Voucher(
            code=code,
            plan_id=plan_id,
            created_at=now,
            expires_at=expires_at,
            payment_reference=payment_reference
        )
        
        self.vouchers[code] = voucher
        self.save_vouchers()
        
        return voucher
    
    def validate_voucher(self, code: str) -> tuple[bool, str, Optional[Voucher]]:
        """Valide un code voucher"""
        code = code.strip().upper()
        
        if code not in self.vouchers:
            return False, "Code voucher invalide", None
        
        voucher = self.vouchers[code]
        
        if voucher.is_used:
            return False, f"Code déjà utilisé le {voucher.used_at.strftime('%d/%m/%Y à %H:%M')}", voucher
        
        if datetime.now() > voucher.expires_at:
            return False, f"Code expiré le {voucher.expires_at.strftime('%d/%m/%Y à %H:%M')}", voucher
        
        return True, "Code valide", voucher
    
    def use_voucher(self, code: str, user_mac: str, user_device: str = None) -> tuple[bool, str]:
        """Utilise un voucher (marque comme utilisé)"""
        is_valid, message, voucher = self.validate_voucher(code)
        
        if not is_valid:
            return False, message
        
        voucher.is_used = True
        voucher.used_at = datetime.now()
        voucher.user_mac = user_mac
        voucher.user_device = user_device
        
        self.save_vouchers()
        
        plan = self.plans[voucher.plan_id]
        return True, f"Accès activé pour {plan.duration_days} jour(s)"
    
    def get_voucher_info(self, code: str) -> Optional[Dict]:
        """Récupère les informations d'un voucher"""
        if code not in self.vouchers:
            return None
        
        voucher = self.vouchers[code]
        plan = self.plans[voucher.plan_id]
        
        return {
            "voucher": voucher,
            "plan": plan,
            "is_valid": not voucher.is_used and datetime.now() <= voucher.expires_at,
            "time_remaining": voucher.expires_at - datetime.now() if not voucher.is_used else None
        }
    
    def get_all_vouchers(self) -> List[Dict]:
        """Récupère tous les vouchers avec leurs informations"""
        result = []
        for code, voucher in self.vouchers.items():
            info = self.get_voucher_info(code)
            if info:
                result.append(info)
        return result
    
    def get_stats(self) -> Dict:
        """Statistiques des vouchers"""
        total = len(self.vouchers)
        used = sum(1 for v in self.vouchers.values() if v.is_used)
        expired = sum(1 for v in self.vouchers.values() if not v.is_used and datetime.now() > v.expires_at)
        active = total - used - expired
        
        revenue_total = 0
        revenue_monthly = 0
        revenue_daily = 0
        
        for voucher in self.vouchers.values():
            if voucher.is_used:
                plan = self.plans[voucher.plan_id]
                revenue_total += plan.price_usd
                if plan.id == "monthly":
                    revenue_monthly += plan.price_usd
                else:
                    revenue_daily += plan.price_usd
        
        return {
            "total_vouchers": total,
            "used_vouchers": used,
            "expired_vouchers": expired,
            "active_vouchers": active,
            "revenue_total": revenue_total,
            "revenue_monthly": revenue_monthly,
            "revenue_daily": revenue_daily
        }
    
    def save_vouchers(self):
        """Sauvegarde les vouchers dans un fichier"""
        data = {}
        for code, voucher in self.vouchers.items():
            voucher_dict = asdict(voucher)
            # Convertir les datetime en string pour JSON
            voucher_dict['created_at'] = voucher.created_at.isoformat()
            voucher_dict['expires_at'] = voucher.expires_at.isoformat()
            if voucher.used_at:
                voucher_dict['used_at'] = voucher.used_at.isoformat()
            data[code] = voucher_dict
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def load_vouchers(self):
        """Charge les vouchers depuis le fichier"""
        if not os.path.exists(self.data_file):
            return
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for code, voucher_dict in data.items():
                # Convertir les strings en datetime
                voucher_dict['created_at'] = datetime.fromisoformat(voucher_dict['created_at'])
                voucher_dict['expires_at'] = datetime.fromisoformat(voucher_dict['expires_at'])
                if voucher_dict.get('used_at'):
                    voucher_dict['used_at'] = datetime.fromisoformat(voucher_dict['used_at'])
                else:
                    voucher_dict['used_at'] = None
                
                self.vouchers[code] = Voucher(**voucher_dict)
        
        except Exception as e:
            print(f"Erreur lors du chargement des vouchers: {e}")
    
    def cleanup_expired_vouchers(self, days_old: int = 90):
        """Nettoie les vouchers expirés depuis X jours"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        to_remove = []
        for code, voucher in self.vouchers.items():
            if voucher.expires_at < cutoff_date and not voucher.is_used:
                to_remove.append(code)
        
        for code in to_remove:
            del self.vouchers[code]
        
        if to_remove:
            self.save_vouchers()
        
        return len(to_remove)

class PaymentSimulator:
    """Simulateur de paiement pour la démo"""
    
    @staticmethod
    def simulate_payment(plan_id: str, amount: float) -> tuple[bool, str, str]:
        """Simule un paiement"""
        # Dans une vraie implémentation, intégrer Stripe, PayPal, etc.
        
        # Simulation d'échec aléatoire (5% de chance)
        import random
        if random.random() < 0.05:
            return False, "Paiement refusé par la banque", None
        
        # Générer une référence de paiement
        payment_ref = f"PAY_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{secrets.token_hex(4).upper()}"
        
        return True, f"Paiement de ${amount:.2f} accepté", payment_ref
