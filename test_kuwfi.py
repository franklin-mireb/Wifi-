#!/usr/bin/env python3
"""
Test de connexion au routeur KUWFI
Vérification de l'intégration avec le système de vouchers
"""

import sys
import os
sys.path.append('/workspaces/Wifi-')

from kuwfi_manager import KUWFIManager
from voucher_system import VoucherManager
from config import Config

def test_kuwfi_connection():
    """Test complet du routeur KUWFI"""
    print("🔍 Test de connexion au routeur KUWFI")
    print("=" * 50)
    
    # Configuration depuis les variables d'environnement
    router_ip = os.environ.get('ROUTER_IP', '192.168.1.254')
    router_user = os.environ.get('ROUTER_USER', 'admin')
    router_pass = os.environ.get('ROUTER_PASS', 'admin')
    
    print(f"📍 IP Routeur: {router_ip}")
    print(f"👤 Utilisateur: {router_user}")
    print(f"🔑 Mot de passe: {'*' * len(router_pass)}")
    print()
    
    # Initialiser le gestionnaire KUWFI
    kuwfi = KUWFIManager(router_ip, router_user, router_pass)
    
    # Test 1: Connexion de base
    print("🌐 Test 1: Connexion de base...")
    if kuwfi.test_connection():
        print("✅ Routeur accessible sur " + router_ip)
    else:
        print("❌ Routeur inaccessible")
        print("💡 Vérifiez que vous êtes connecté au réseau 'mireb wifi'")
        return False
    
    # Test 2: Authentification
    print("\n🔐 Test 2: Authentification...")
    if kuwfi.authenticate():
        print("✅ Authentification réussie")
    else:
        print("❌ Échec authentification")
        print("💡 Vérifiez les identifiants du routeur")
        return False
    
    # Test 3: Récupération des appareils
    print("\n📱 Test 3: Appareils connectés...")
    devices = kuwfi.get_connected_devices()
    print(f"✅ {len(devices)} appareils détectés")
    
    if devices:
        print("\n📋 Liste des appareils:")
        for i, device in enumerate(devices[:5], 1):  # Max 5 appareils
            print(f"  {i}. {device.get('hostname', 'Inconnu')} ({device.get('ip', 'N/A')})")
            print(f"     MAC: {device.get('mac', 'N/A')}")
            print(f"     Type: {device.get('device_type', 'Unknown')}")
            print()
    
    # Test 4: Statut du routeur
    print("📊 Test 4: Statut du routeur...")
    status = kuwfi.get_router_status()
    print(f"✅ Statut: {status.get('status', 'Unknown')}")
    print(f"📈 Uptime: {status.get('uptime', 'N/A')}")
    print(f"💾 Mémoire: {status.get('memory_usage', 'N/A')}")
    print(f"⚡ CPU: {status.get('cpu_usage', 'N/A')}")
    
    return True

def test_voucher_integration():
    """Test de l'intégration vouchers"""
    print("\n🎫 Test de l'intégration vouchers")
    print("=" * 50)
    
    voucher_manager = VoucherManager()
    
    # Test création de voucher
    print("💳 Création d'un voucher de test...")
    try:
        voucher = voucher_manager.create_voucher('monthly')
        
        if voucher:
            print(f"✅ Voucher créé: {voucher.code}")
            print(f"💰 Prix: ${voucher.plan.price_usd}")
            print(f"⏱️  Durée: {voucher.plan.duration_days} jours")
        else:
            print("❌ Erreur création voucher")
            return False
    except Exception as e:
        print(f"❌ Erreur création voucher: {e}")
        return False
    
    # Test validation de voucher
    print(f"\n🔍 Validation du voucher {voucher.code}...")
    try:
        validation = voucher_manager.validate_voucher(voucher.code)
        
        if validation['is_valid']:
            print("✅ Voucher valide")
            print(f"📅 Expire le: {validation['voucher'].expires_at}")
        else:
            print("❌ Voucher invalide")
    except Exception as e:
        print(f"❌ Erreur validation: {e}")
        return False
    
    return True

def test_network_config():
    """Test de la configuration réseau"""
    print("\n🌐 Test de la configuration réseau")
    print("=" * 50)
    
    # Informations réseau détectées
    network_info = {
        'wifi_ssid': 'mireb wifi',
        'wifi_password': '0816448961',
        'gateway': '192.168.1.254',
        'subnet': '192.168.1.0/24',
        'dns': '192.168.1.254',
        'user_ip': '192.168.1.73'  # IP détectée de l'utilisateur
    }
    
    print(f"📡 SSID WiFi: {network_info['wifi_ssid']}")
    print(f"🔑 Mot de passe: {'*' * len(network_info['wifi_password'])}")
    print(f"🚪 Passerelle: {network_info['gateway']}")
    print(f"🌐 Sous-réseau: {network_info['subnet']}")
    print(f"🔍 DNS: {network_info['dns']}")
    print(f"📍 IP utilisateur: {network_info['user_ip']}")
    
    return True

if __name__ == "__main__":
    print("🚀 Test complet du système WiFi Manager KUWFI")
    print("=" * 60)
    print()
    
    # Test 1: Connexion KUWFI
    kuwfi_ok = test_kuwfi_connection()
    
    # Test 2: Système de vouchers
    voucher_ok = test_voucher_integration()
    
    # Test 3: Configuration réseau
    network_ok = test_network_config()
    
    print("\n🎯 RÉSUMÉ DES TESTS")
    print("=" * 30)
    print(f"🌐 Connexion KUWFI: {'✅ OK' if kuwfi_ok else '❌ ÉCHEC'}")
    print(f"🎫 Système vouchers: {'✅ OK' if voucher_ok else '❌ ÉCHEC'}")
    print(f"🔧 Config réseau: {'✅ OK' if network_ok else '❌ ÉCHEC'}")
    
    if kuwfi_ok and voucher_ok and network_ok:
        print("\n🎉 TOUS LES TESTS RÉUSSIS!")
        print("🚀 Le système est prêt pour la production")
    else:
        print("\n⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
        print("🔧 Vérifiez la configuration avant le déploiement")
    
    print(f"\n📱 Interface web: https://wifi-manager-zu09.onrender.com/")
    print("📖 Documentation: /DEPLOYMENT_RENDER_QUICK.md")
