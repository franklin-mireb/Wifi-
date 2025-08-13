import unittest
import tempfile
import os
from datetime import datetime, timedelta
from voucher_system import VoucherManager, PaymentSimulator

class TestVoucherSystem(unittest.TestCase):
    
    def setUp(self):
        # Créer un fichier temporaire pour les tests
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
        self.temp_file.close()
        
        self.voucher_manager = VoucherManager(self.temp_file.name)
    
    def tearDown(self):
        # Nettoyer le fichier temporaire
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_voucher_code_generation(self):
        """Test de génération de codes voucher"""
        code1 = self.voucher_manager.generate_voucher_code()
        code2 = self.voucher_manager.generate_voucher_code()
        
        # Les codes doivent être différents
        self.assertNotEqual(code1, code2)
        
        # Format correct (XXXX-XXXX-XXXX)
        self.assertEqual(len(code1), 14)  # 12 caractères + 2 tirets
        self.assertTrue('-' in code1)
    
    def test_create_monthly_voucher(self):
        """Test de création d'un voucher mensuel"""
        voucher = self.voucher_manager.create_voucher("monthly", "PAY_TEST_123")
        
        self.assertEqual(voucher.plan_id, "monthly")
        self.assertIsNotNone(voucher.code)
        self.assertFalse(voucher.is_used)
        self.assertEqual(voucher.payment_reference, "PAY_TEST_123")
        
        # Vérifier la durée (30 jours)
        expected_expiry = voucher.created_at + timedelta(days=30)
        self.assertEqual(voucher.expires_at.date(), expected_expiry.date())
    
    def test_create_daily_voucher(self):
        """Test de création d'un voucher journalier"""
        voucher = self.voucher_manager.create_voucher("daily")
        
        self.assertEqual(voucher.plan_id, "daily")
        self.assertIsNotNone(voucher.code)
        self.assertFalse(voucher.is_used)
        
        # Vérifier la durée (1 jour)
        expected_expiry = voucher.created_at + timedelta(days=1)
        self.assertEqual(voucher.expires_at.date(), expected_expiry.date())
    
    def test_validate_voucher_valid(self):
        """Test de validation d'un voucher valide"""
        voucher = self.voucher_manager.create_voucher("daily")
        
        is_valid, message, returned_voucher = self.voucher_manager.validate_voucher(voucher.code)
        
        self.assertTrue(is_valid)
        self.assertEqual(message, "Code valide")
        self.assertEqual(returned_voucher.code, voucher.code)
    
    def test_validate_voucher_invalid_code(self):
        """Test de validation avec un code invalide"""
        is_valid, message, voucher = self.voucher_manager.validate_voucher("INVALID-CODE")
        
        self.assertFalse(is_valid)
        self.assertEqual(message, "Code voucher invalide")
        self.assertIsNone(voucher)
    
    def test_validate_voucher_used(self):
        """Test de validation d'un voucher déjà utilisé"""
        voucher = self.voucher_manager.create_voucher("daily")
        
        # Utiliser le voucher
        self.voucher_manager.use_voucher(voucher.code, "AA:BB:CC:DD:EE:FF")
        
        # Tenter de le valider à nouveau
        is_valid, message, returned_voucher = self.voucher_manager.validate_voucher(voucher.code)
        
        self.assertFalse(is_valid)
        self.assertIn("déjà utilisé", message)
    
    def test_validate_voucher_expired(self):
        """Test de validation d'un voucher expiré"""
        voucher = self.voucher_manager.create_voucher("daily")
        
        # Modifier manuellement la date d'expiration pour simuler l'expiration
        voucher.expires_at = datetime.now() - timedelta(days=1)
        self.voucher_manager.vouchers[voucher.code] = voucher
        
        is_valid, message, returned_voucher = self.voucher_manager.validate_voucher(voucher.code)
        
        self.assertFalse(is_valid)
        self.assertIn("expiré", message)
    
    def test_use_voucher_success(self):
        """Test d'utilisation réussie d'un voucher"""
        voucher = self.voucher_manager.create_voucher("monthly")
        
        success, message = self.voucher_manager.use_voucher(
            voucher.code, 
            "AA:BB:CC:DD:EE:FF", 
            "iPhone de Test"
        )
        
        self.assertTrue(success)
        self.assertIn("Accès activé", message)
        
        # Vérifier que le voucher est marqué comme utilisé
        updated_voucher = self.voucher_manager.vouchers[voucher.code]
        self.assertTrue(updated_voucher.is_used)
        self.assertIsNotNone(updated_voucher.used_at)
        self.assertEqual(updated_voucher.user_mac, "AA:BB:CC:DD:EE:FF")
        self.assertEqual(updated_voucher.user_device, "iPhone de Test")
    
    def test_use_voucher_invalid(self):
        """Test d'utilisation d'un voucher invalide"""
        success, message = self.voucher_manager.use_voucher(
            "INVALID-CODE", 
            "AA:BB:CC:DD:EE:FF"
        )
        
        self.assertFalse(success)
        self.assertEqual(message, "Code voucher invalide")
    
    def test_get_stats(self):
        """Test des statistiques"""
        # Créer quelques vouchers
        voucher1 = self.voucher_manager.create_voucher("monthly")  # $7
        voucher2 = self.voucher_manager.create_voucher("daily")    # $0.6
        voucher3 = self.voucher_manager.create_voucher("daily")    # $0.6
        
        # Utiliser quelques vouchers
        self.voucher_manager.use_voucher(voucher1.code, "AA:BB:CC:DD:EE:FF")
        self.voucher_manager.use_voucher(voucher2.code, "11:22:33:44:55:66")
        
        stats = self.voucher_manager.get_stats()
        
        self.assertEqual(stats['total_vouchers'], 3)
        self.assertEqual(stats['used_vouchers'], 2)
        self.assertEqual(stats['active_vouchers'], 1)
        self.assertEqual(stats['revenue_total'], 7.6)  # 7 + 0.6
        self.assertEqual(stats['revenue_monthly'], 7.0)
        self.assertEqual(stats['revenue_daily'], 0.6)
    
    def test_save_and_load_vouchers(self):
        """Test de sauvegarde et chargement"""
        # Créer un voucher
        original_voucher = self.voucher_manager.create_voucher("monthly")
        original_code = original_voucher.code
        
        # Créer un nouveau manager avec le même fichier
        new_manager = VoucherManager(self.temp_file.name)
        
        # Vérifier que le voucher a été chargé
        self.assertIn(original_code, new_manager.vouchers)
        loaded_voucher = new_manager.vouchers[original_code]
        
        self.assertEqual(loaded_voucher.plan_id, "monthly")
        self.assertEqual(loaded_voucher.code, original_code)
        self.assertFalse(loaded_voucher.is_used)
    
    def test_invalid_plan_id(self):
        """Test avec un plan_id invalide"""
        with self.assertRaises(ValueError):
            self.voucher_manager.create_voucher("invalid_plan")

class TestPaymentSimulator(unittest.TestCase):
    
    def test_payment_simulation_success(self):
        """Test de simulation de paiement réussi"""
        success, message, ref = PaymentSimulator.simulate_payment("monthly", 7.0)
        
        # La plupart des paiements devraient réussir (95%)
        if success:
            self.assertIn("accepté", message)
            self.assertIsNotNone(ref)
            self.assertTrue(ref.startswith("PAY_"))
        else:
            self.assertIn("refusé", message)
            self.assertIsNone(ref)
    
    def test_payment_reference_format(self):
        """Test du format de référence de paiement"""
        success, message, ref = PaymentSimulator.simulate_payment("daily", 0.6)
        
        if success:
            # Format: PAY_YYYYMMDD_HHMMSS_XXXXXXXX
            parts = ref.split('_')
            self.assertEqual(len(parts), 4)  # PAY, date, time, token
            self.assertEqual(parts[0], "PAY")
            self.assertEqual(len(parts[1]), 8)  # Date YYYYMMDD
            self.assertEqual(len(parts[2]), 6)  # Time HHMMSS  
            self.assertEqual(len(parts[3]), 8)  # Token hex (4 bytes = 8 chars)

if __name__ == '__main__':
    unittest.main()
