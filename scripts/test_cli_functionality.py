#!/usr/bin/env python3
"""
Script de test pour vérifier les fonctionnalités CLI dab
"""

import subprocess
import sys
import os

def test_cli_help():
    """Test que l'aide de dab fonctionne."""
    print("🔍 Test de l'aide CLI...")
    try:
        result = subprocess.run(['dab', '--help'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Aide CLI fonctionne")
            return True
        else:
            print(f"❌ Erreur aide CLI: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception aide CLI: {e}")
        return False

def test_command_help(command):
    """Test l'aide d'une commande spécifique."""
    print(f"🔍 Test de l'aide pour '{command}'...")
    try:
        result = subprocess.run(['dab', command, '--help'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Aide pour '{command}' fonctionne")
            return True
        else:
            print(f"❌ Erreur aide '{command}': {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception aide '{command}': {e}")
        return False

def test_new_commands():
    """Test les nouvelles commandes."""
    new_commands = ['resumer', 'graph_desc', 'evolution']
    
    print("\n🚀 Test des nouvelles commandes...")
    all_ok = True
    
    for cmd in new_commands:
        if not test_command_help(cmd):
            all_ok = False
    
    return all_ok

def test_existing_commands():
    """Test les commandes existantes."""
    existing_commands = ['stats', 'cas', 'alertes', 'export', 'auth', 'regions', 'districts']
    
    print("\n🔧 Test des commandes existantes...")
    all_ok = True
    
    for cmd in existing_commands:
        if not test_command_help(cmd):
            all_ok = False
    
    return all_ok

def main():
    """Fonction principale de test."""
    print("🧪 Test des fonctionnalités CLI dab")
    print("=" * 50)
    
    # Test aide générale
    if not test_cli_help():
        print("❌ Test aide générale échoué")
        sys.exit(1)
    
    # Test commandes existantes
    if not test_existing_commands():
        print("❌ Test commandes existantes échoué")
        sys.exit(1)
    
    # Test nouvelles commandes
    if not test_new_commands():
        print("❌ Test nouvelles commandes échoué")
        sys.exit(1)
    
    print("\n🎉 Tous les tests CLI sont passés avec succès !")
    print("\n📋 Résumé des commandes disponibles:")
    
    # Afficher toutes les commandes
    try:
        result = subprocess.run(['dab', '--help'], capture_output=True, text=True)
        if result.returncode == 0:
            # Extraire les commandes de la sortie
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Commandes disponibles' in line or any(cmd in line for cmd in ['stats', 'cas', 'alertes', 'export', 'auth', 'regions', 'districts', 'resumer', 'graph_desc', 'evolution']):
                    print(f"   {line.strip()}")
    except Exception as e:
        print(f"❌ Erreur lors de l'affichage du résumé: {e}")

if __name__ == "__main__":
    main() 