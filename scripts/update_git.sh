#!/bin/bash

# Script de mise à jour automatique du dépôt GitHub
# Permet de committer et pousser les changements facilement

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
REPO_PATH=$(pwd)
BRANCH="main"  # ou "master" selon votre configuration

# Fonction pour exécuter une commande
run_command() {
    local command="$1"
    local capture_output="${2:-true}"
    
    if [ "$capture_output" = "true" ]; then
        if eval "$command" 2>&1; then
            return 0
        else
            echo -e "${RED}❌ Erreur lors de l'exécution de la commande: $command${NC}"
            return 1
        fi
    else
        eval "$command"
        return $?
    fi
}

# Fonction pour vérifier le statut Git
check_git_status() {
    echo -e "${BLUE}🔍 Vérification du statut Git...${NC}"
    
    if ! run_command "git status --porcelain" true > /tmp/git_status 2>&1; then
        echo -e "${RED}❌ Erreur lors de la vérification du statut Git${NC}"
        return 1
    fi
    
    local changes=$(cat /tmp/git_status)
    if [ -z "$changes" ]; then
        echo -e "${GREEN}✅ Aucun changement détecté${NC}"
        return 1
    fi
    
    echo -e "${CYAN}📝 Changements détectés:${NC}"
    while IFS= read -r line; do
        if [ -n "$line" ]; then
            local status="${line:0:2}"
            local file="${line:3}"
            echo -e "   ${status} ${file}"
        fi
    done < /tmp/git_status
    
    rm -f /tmp/git_status
    return 0
}

# Fonction pour ajouter tous les changements
add_all_changes() {
    echo -e "${BLUE}📦 Ajout des changements...${NC}"
    
    if run_command "git add ." true; then
        echo -e "${GREEN}✅ Changements ajoutés avec succès${NC}"
        return 0
    else
        echo -e "${RED}❌ Erreur lors de l'ajout des fichiers${NC}"
        return 1
    fi
}

# Fonction pour committer les changements
commit_changes() {
    local message="$1"
    
    if [ -z "$message" ]; then
        local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
        message="Update: $timestamp"
    fi
    
    echo -e "${BLUE}💾 Commit avec le message: '${message}'${NC}"
    
    if run_command "git commit -m \"$message\"" true; then
        echo -e "${GREEN}✅ Commit effectué avec succès${NC}"
        return 0
    else
        echo -e "${RED}❌ Erreur lors du commit${NC}"
        return 1
    fi
}

# Fonction pour pousser les changements
push_changes() {
    echo -e "${BLUE}🚀 Push vers GitHub...${NC}"
    
    if run_command "git push origin $BRANCH" true; then
        echo -e "${GREEN}✅ Push effectué avec succès${NC}"
        return 0
    else
        echo -e "${RED}❌ Erreur lors du push${NC}"
        return 1
    fi
}

# Fonction pour afficher l'historique des commits
get_commit_history() {
    local limit="${1:-5}"
    echo -e "${CYAN}📜 Derniers $limit commits:${NC}"
    
    if run_command "git log --oneline -$limit" true; then
        echo ""
    fi
}

# Fonction pour vérifier le statut du dépôt distant
check_remote_status() {
    echo -e "${BLUE}🌐 Vérification du dépôt distant...${NC}"
    
    if run_command "git remote -v" true; then
        echo -e "${CYAN}📡 Dépôts distants configurés:${NC}"
        git remote -v | while read -r line; do
            if [ -n "$line" ]; then
                echo -e "   $line"
            fi
        done
    fi
}

# Fonction pour la mise à jour interactive
interactive_update() {
    echo -e "${PURPLE}🔄 Mise à jour interactive du dépôt GitHub${NC}"
    echo "=================================================="
    
    # Vérifier s'il y a des changements
    if ! check_git_status; then
        return
    fi
    
    # Demander le message de commit
    echo -e "\n${YELLOW}💬 Message de commit (laissez vide pour utiliser la date/heure):${NC}"
    read -p "> " message
    
    # Ajouter les changements
    if ! add_all_changes; then
        return
    fi
    
    # Commiter
    if ! commit_changes "$message"; then
        return
    fi
    
    # Pousser
    if ! push_changes; then
        return
    fi
    
    echo -e "\n${GREEN}🎉 Mise à jour terminée avec succès!${NC}"
    get_commit_history
}

# Fonction pour la mise à jour automatique
auto_update() {
    local message="$1"
    
    echo -e "${PURPLE}🤖 Mise à jour automatique du dépôt GitHub${NC}"
    echo "=================================================="
    
    # Vérifier s'il y a des changements
    if ! check_git_status; then
        return 0
    fi
    
    # Ajouter les changements
    if ! add_all_changes; then
        return 1
    fi
    
    # Commiter
    if ! commit_changes "$message"; then
        return 1
    fi
    
    # Pousser
    if ! push_changes; then
        return 1
    fi
    
    echo -e "\n${GREEN}🎉 Mise à jour automatique terminée!${NC}"
    return 0
}

# Fonction d'aide
show_help() {
    echo -e "${CYAN}
🔄 Script de mise à jour GitHub

Usage:
    ./update_git.sh                    # Mode interactif
    ./update_git.sh auto [message]    # Mise à jour automatique
    ./update_git.sh status            # Vérifier le statut
    ./update_git.sh remote            # Vérifier les dépôts distants
    ./update_git.sh help              # Afficher cette aide

Options:
    auto [message]  - Mise à jour automatique avec message optionnel
    status          - Affiche le statut et l'historique des commits
    remote          - Affiche les dépôts distants configurés
    help            - Affiche cette aide
${NC}"
}

# Fonction principale
main() {
    # Vérifier que nous sommes dans un dépôt Git
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        echo -e "${RED}❌ Erreur: Ce répertoire n'est pas un dépôt Git${NC}"
        exit 1
    fi
    
    # Traitement des arguments
    case "${1:-}" in
        "auto")
            local message="$2"
            if auto_update "$message"; then
                exit 0
            else
                exit 1
            fi
            ;;
        "status")
            check_git_status
            get_commit_history
            exit 0
            ;;
        "remote")
            check_remote_status
            exit 0
            ;;
        "help"|"-h"|"--help")
            show_help
            exit 0
            ;;
        "")
            # Mode interactif par défaut
            interactive_update
            ;;
        *)
            echo -e "${RED}❌ Commande inconnue: $1${NC}"
            echo -e "${YELLOW}💡 Utilisez './update_git.sh help' pour voir les options${NC}"
            exit 1
            ;;
    esac
}

# Exécuter la fonction principale
main "$@" 