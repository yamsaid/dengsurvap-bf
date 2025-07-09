#!/bin/bash

# 🔐 Script de Configuration PyPI
# Usage: ./scripts/setup_pypi.sh

set -e

# Couleurs pour les messages
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_status "🔐 Configuration des identifiants PyPI"

# Vérifier si .pypirc existe déjà
if [ -f ~/.pypirc ]; then
    print_warning "⚠️  Le fichier ~/.pypirc existe déjà. Voulez-vous le remplacer ? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_status "Configuration annulée."
        exit 0
    fi
fi

# Demander les identifiants
echo ""
print_status "📝 Entrez vos identifiants PyPI :"
echo ""

read -p "Username PyPI: " pypi_username
read -s -p "Password PyPI: " pypi_password
echo ""
read -p "Username TestPyPI: " testpypi_username
read -s -p "Password TestPyPI: " testpypi_password
echo ""

# Créer le fichier .pypirc
cat > ~/.pypirc << EOF
[pypi]
username = $pypi_username
password = $pypi_password

[testpypi]
username = $testpypi_username
password = $testpypi_password
EOF

# Définir les permissions appropriées
chmod 600 ~/.pypirc

print_success "✅ Configuration PyPI terminée !"
echo ""
print_status "📋 Fichier créé : ~/.pypirc"
print_status "🔒 Permissions définies : 600 (lecture/écriture pour l'utilisateur uniquement)"
echo ""
print_status "🧪 Pour tester la configuration :"
echo "   • TestPyPI: twine upload --repository testpypi dist/*"
echo "   • PyPI: twine upload dist/*"
echo ""
print_status "📚 Ressources utiles :"
echo "   • PyPI: https://pypi.org/"
echo "   • TestPyPI: https://test.pypi.org/"
echo "   • Guide: ./GUIDE_PUBLICATION_PYPI.md" 