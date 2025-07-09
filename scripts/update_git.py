#!/usr/bin/env python3
"""
Script de mise à jour automatique du dépôt GitHub
Permet de committer et pousser les changements facilement
"""

import subprocess
import sys
import os
from datetime import datetime
import json

class GitUpdater:
    def __init__(self):
        self.repo_path = os.getcwd()
        self.branch = "main"  # ou "master" selon votre configuration
        
    def run_command(self, command, capture_output=True):
        """Exécute une commande et retourne le résultat"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=capture_output,
                text=True,
                cwd=self.repo_path
            )
            return result
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution de la commande: {e}")
            return None
    
    def check_git_status(self):
        """Vérifie le statut du dépôt Git"""
        print("🔍 Vérification du statut Git...")
        result = self.run_command("git status --porcelain")
        
        if result is None:
            return False
            
        if result.returncode != 0:
            print("❌ Erreur lors de la vérification du statut Git")
            return False
            
        changes = result.stdout.strip()
        if not changes:
            print("✅ Aucun changement détecté")
            return False
            
        print("📝 Changements détectés:")
        for line in changes.split('\n'):
            if line.strip():
                status = line[:2]
                file = line[3:]
                print(f"   {status} {file}")
        return True
    
    def add_all_changes(self):
        """Ajoute tous les changements au staging area"""
        print("📦 Ajout des changements...")
        result = self.run_command("git add .")
        
        if result is None or result.returncode != 0:
            print("❌ Erreur lors de l'ajout des fichiers")
            return False
            
        print("✅ Changements ajoutés avec succès")
        return True
    
    def commit_changes(self, message=None):
        """Commite les changements avec un message personnalisé"""
        if not message:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"Update: {timestamp}"
        
        print(f"💾 Commit avec le message: '{message}'")
        result = self.run_command(f'git commit -m "{message}"')
        
        if result is None or result.returncode != 0:
            print("❌ Erreur lors du commit")
            return False
            
        print("✅ Commit effectué avec succès")
        return True
    
    def push_changes(self):
        """Pousse les changements vers le dépôt distant"""
        print("🚀 Push vers GitHub...")
        result = self.run_command(f"git push origin {self.branch}")
        
        if result is None or result.returncode != 0:
            print("❌ Erreur lors du push")
            return False
            
        print("✅ Push effectué avec succès")
        return True
    
    def get_commit_history(self, limit=5):
        """Affiche l'historique des commits récents"""
        print(f"📜 Derniers {limit} commits:")
        result = self.run_command(f"git log --oneline -{limit}")
        
        if result and result.returncode == 0:
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    print(f"   {line}")
    
    def check_remote_status(self):
        """Vérifie le statut du dépôt distant"""
        print("🌐 Vérification du dépôt distant...")
        result = self.run_command("git remote -v")
        
        if result and result.returncode == 0:
            print("📡 Dépôts distants configurés:")
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    print(f"   {line}")
    
    def interactive_update(self):
        """Interface interactive pour la mise à jour"""
        print("🔄 Mise à jour interactive du dépôt GitHub")
        print("=" * 50)
        
        # Vérifier s'il y a des changements
        if not self.check_git_status():
            return
        
        # Demander le message de commit
        print("\n💬 Message de commit (laissez vide pour utiliser la date/heure):")
        message = input("> ").strip()
        
        # Ajouter les changements
        if not self.add_all_changes():
            return
        
        # Commiter
        if not self.commit_changes(message):
            return
        
        # Pousser
        if not self.push_changes():
            return
        
        print("\n🎉 Mise à jour terminée avec succès!")
        self.get_commit_history()
    
    def auto_update(self, message=None):
        """Mise à jour automatique sans interaction"""
        print("🤖 Mise à jour automatique du dépôt GitHub")
        print("=" * 50)
        
        # Vérifier s'il y a des changements
        if not self.check_git_status():
            return True
        
        # Ajouter les changements
        if not self.add_all_changes():
            return False
        
        # Commiter
        if not self.commit_changes(message):
            return False
        
        # Pousser
        if not self.push_changes():
            return False
        
        print("\n🎉 Mise à jour automatique terminée!")
        return True

def main():
    """Fonction principale"""
    updater = GitUpdater()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "auto":
            message = sys.argv[2] if len(sys.argv) > 2 else None
            success = updater.auto_update(message)
            sys.exit(0 if success else 1)
            
        elif command == "status":
            updater.check_git_status()
            updater.get_commit_history()
            sys.exit(0)
            
        elif command == "remote":
            updater.check_remote_status()
            sys.exit(0)
            
        elif command == "help":
            print("""
🔄 Script de mise à jour GitHub

Usage:
    python update_git.py                    # Mode interactif
    python update_git.py auto [message]    # Mise à jour automatique
    python update_git.py status            # Vérifier le statut
    python update_git.py remote            # Vérifier les dépôts distants
    python update_git.py help              # Afficher cette aide

Options:
    auto [message]  - Mise à jour automatique avec message optionnel
    status          - Affiche le statut et l'historique des commits
    remote          - Affiche les dépôts distants configurés
    help            - Affiche cette aide
            """)
            sys.exit(0)
        else:
            print(f"❌ Commande inconnue: {command}")
            print("💡 Utilisez 'python update_git.py help' pour voir les options")
            sys.exit(1)
    else:
        # Mode interactif par défaut
        updater.interactive_update()

if __name__ == "__main__":
    main() 