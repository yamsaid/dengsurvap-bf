# 📦 Guide de Publication sur PyPI

Ce guide détaille les étapes pour publier le package `dengsurvap-bf` sur PyPI.

## 🎯 Objectif

Publier une nouvelle version du package sur PyPI pour le rendre disponible aux utilisateurs via `pip install dengsurvap-bf`.

## 📋 Prérequis

- Compte PyPI créé sur https://pypi.org/account/register/
- Compte TestPyPI créé sur https://test.pypi.org/account/register/
- Outils installés : `build`, `twine`

## 🔄 Étapes de Publication

### 1. **Préparation de la Version**

#### 1.1 Mettre à jour la version
```bash
# Éditer pyproject.toml
version = "0.2.0"  # Incrémenter selon les changements
```

#### 1.2 Créer/Mettre à jour le changelog
```bash
# Éditer CHANGELOG.md avec les changements de la version
# Format recommandé : Keep a Changelog
```

### 2. **Nettoyage et Construction**

#### 2.1 Nettoyer les anciennes distributions
```bash
rm -rf dist/ build/ *.egg-info/
```

#### 2.2 Installer les outils de build
```bash
pip install --upgrade build twine
```

#### 2.3 Construire la distribution
```bash
python -m build
```

#### 2.4 Vérifier la distribution
```bash
twine check dist/*
```

### 3. **Test sur TestPyPI (Recommandé)**

#### 3.1 Publier sur TestPyPI
```bash
twine upload --repository testpypi dist/*
```

#### 3.2 Tester l'installation depuis TestPyPI
```bash
pip install --index-url https://test.pypi.org/simple/ dengsurvap-bf==0.2.0
```

#### 3.3 Tester le package installé
```python
import dengsurvab
print(dengsurvab.__version__)
```

### 4. **Publication sur PyPI Production**

#### 4.1 Publier sur PyPI
```bash
twine upload dist/*
```

#### 4.2 Vérifier la publication
- Visiter https://pypi.org/project/dengsurvap-bf/
- Vérifier que la nouvelle version est visible

## 🔐 Configuration des Identifiants

### Option 1 : Variables d'environnement
```bash
export TWINE_USERNAME=votre_username
export TWINE_PASSWORD=votre_password
```

### Option 2 : Fichier .pypirc
Créer `~/.pypirc` :
```ini
[pypi]
username = votre_username
password = votre_password

[testpypi]
username = votre_username
password = votre_password
```

### Option 3 : Authentification interactive
```bash
# Twine demandera les identifiants automatiquement
twine upload dist/*
```

## 📊 Gestion des Versions

### Semantic Versioning (SemVer)
- **MAJOR.MINOR.PATCH**
- **MAJOR** : Changements incompatibles
- **MINOR** : Nouvelles fonctionnalités compatibles
- **PATCH** : Corrections de bugs

### Exemples de versions
- `0.1.0` → `0.2.0` : Nouvelles fonctionnalités
- `0.2.0` → `0.2.1` : Corrections de bugs
- `0.2.1` → `1.0.0` : Version stable

## 🚨 Résolution de Problèmes

### Erreur "File already exists"
```bash
# Utiliser --skip-existing pour ignorer les fichiers existants
twine upload --skip-existing dist/*
```

### Erreur d'authentification
```bash
# Vérifier les identifiants
twine check --repository testpypi dist/*
```

### Erreur de build
```bash
# Nettoyer et reconstruire
rm -rf dist/ build/ *.egg-info/
python -m build
```

## 📝 Checklist de Publication

### Avant la publication
- [ ] Version mise à jour dans `pyproject.toml`
- [ ] Changelog mis à jour
- [ ] Tests passent localement
- [ ] Documentation à jour
- [ ] Distribution construite et vérifiée

### Après la publication
- [ ] Package installable depuis PyPI
- [ ] Documentation visible sur PyPI
- [ ] Tests d'installation réussis
- [ ] Changelog accessible

## 🔄 Workflow Complet

```bash
# 1. Préparation
git checkout main
git pull origin main
# Éditer pyproject.toml et CHANGELOG.md

# 2. Construction
rm -rf dist/ build/ *.egg-info/
python -m build
twine check dist/*

# 3. Test sur TestPyPI
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ dengsurvap-bf==0.2.0

# 4. Publication sur PyPI
twine upload dist/*

# 5. Vérification
pip install dengsurvap-bf==0.2.0
```

## 📚 Ressources Utiles

- [Guide officiel PyPI](https://packaging.python.org/guides/distributing-packages-using-setuptools/)
- [TestPyPI](https://test.pypi.org/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)

## 🎯 Commandes Rapides

```bash
# Publication rapide (après configuration)
./scripts/publish.sh

# Test rapide
pip install --upgrade dengsurvap-bf

# Vérification de version
python -c "import dengsurvab; print(dengsurvab.__version__)"
```

---

**Note** : Toujours tester sur TestPyPI avant de publier sur PyPI production pour éviter les erreurs. 