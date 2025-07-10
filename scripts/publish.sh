#!/bin/bash

# 📦 Script de Publication sur PyPI
# Usage: ./scripts/publish.sh [test|prod]

set -e  # Arrêter en cas d'erreur

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier les arguments
if [ $# -eq 0 ]; then
    print_error "Usage: $0 [test|prod]"
    echo "  test: Publier sur TestPyPI"
    echo "  prod: Publier sur PyPI production"
    exit 1
fi

MODE=$1

if [ "$MODE" != "test" ] && [ "$MODE" != "prod" ]; then
    print_error "Mode invalide. Utilisez 'test' ou 'prod'"
    exit 1
fi

print_status "🚀 Début de la publication en mode: $MODE"

# 1. Vérifier que nous sommes dans le bon répertoire
if [ ! -f "pyproject.toml" ]; then
    print_error "pyproject.toml non trouvé. Assurez-vous d'être dans le répertoire du projet."
    exit 1
fi

# 2. Vérifier que git est propre
if [ -n "$(git status --porcelain)" ]; then
    print_warning "⚠️  Des changements non commités détectés. Continuer ? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_status "Publication annulée."
        exit 1
    fi
fi

# 3. Nettoyer les anciennes distributions
print_status "🧹 Nettoyage des anciennes distributions..."
rm -rf dist/ build/ *.egg-info/ 2>/dev/null || true

# 4. Installer/upgrader les outils
print_status "📦 Installation des outils de build..."
pip install --upgrade build twine

# 5. Construire la distribution
print_status "🔨 Construction de la distribution..."
python -m build

# 6. Vérifier la distribution
print_status "✅ Vérification de la distribution..."
twine check dist/*

# 7. Publier selon le mode
if [ "$MODE" = "test" ]; then
    print_status "🧪 Publication sur TestPyPI..."
    twine upload --repository testpypi dist/*
    print_success "✅ Publication sur TestPyPI réussie !"
    print_status "📦 Test d'installation depuis TestPyPI..."
    pip install --index-url https://test.pypi.org/simple/ --no-deps dengsurvap-bf
    print_success "✅ Installation depuis TestPyPI réussie !"
    
elif [ "$MODE" = "prod" ]; then
    print_warning "⚠️  Êtes-vous sûr de vouloir publier sur PyPI production ? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_status "Publication annulée."
        exit 1
    fi
    

    print_status "🚀 Publication sur PyPI production..."
    twine upload dist/*
    print_success "✅ Publication sur PyPI production réussie !"
    print_status "📦 Test d'installation depuis PyPI..."
    pip install --upgrade dengsurvap-bf
    print_success "✅ Installation depuis PyPI réussie !"
fi

# 8. Afficher les informations finales
print_success "🎉 Publication terminée avec succès !"
echo ""
echo "📋 Informations utiles :"
if [ "$MODE" = "test" ]; then
    echo "   • TestPyPI: https://test.pypi.org/project/dengsurvap-bf/"
    echo "   • Installation: pip install --index-url https://test.pypi.org/simple/ dengsurvap-bf"
else
    echo "   • PyPI: https://pypi.org/project/dengsurvap-bf/"
    echo "   • Installation: pip install dengsurvap-bf"
fi
echo "   • Documentation: https://github.com/yamsaid/dengsurvap-bf"
echo ""

print_status "✨ N'oubliez pas de :"
echo "   • Commiter les changements de version"
echo "   • Créer un tag git pour cette version"
echo "   • Mettre à jour la documentation si nécessaire" 