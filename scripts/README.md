# 📦 Scripts de Publication

Ce répertoire contient les scripts automatisés pour la publication du package `dengsurvap-bf` sur PyPI.
# Installer localement pour tester
pip install dist/dengsurvap_bf-0.2.0-py3-none-any.whl
## 🚀 Scripts Disponibles

### 1. `setup_pypi.sh` - Configuration des identifiants
```bash
./scripts/setup_pypi.sh
```
- Configure les identifiants PyPI et TestPyPI
- Crée le fichier `~/.pypirc` avec les permissions appropriées
- Sécurisé : les mots de passe ne sont pas affichés

### 2. `publish.sh` - Publication automatisée
```bash
# Publication sur TestPyPI
./scripts/publish.sh test

# Publication sur PyPI production
./scripts/publish.sh prod
```

## 📋 Fonctionnalités du Script de Publication

### ✅ Vérifications automatiques
- Présence de `pyproject.toml`
- État du repository git
- Outils de build installés

### 🔄 Étapes automatisées
1. **Nettoyage** : Suppression des anciennes distributions
2. **Installation** : Mise à jour de `build` et `twine`
3. **Construction** : Build de la distribution
4. **Vérification** : Test de la distribution
5. **Publication** : Upload sur PyPI/TestPyPI
6. **Test** : Installation et vérification

### 🛡️ Sécurité
- Confirmation avant publication production
- Vérification des changements non commités
- Gestion des erreurs avec arrêt automatique

## 🎯 Utilisation Rapide

### Première configuration
```bash
# 1. Configurer les identifiants
./scripts/setup_pypi.sh

# 2. Tester sur TestPyPI
./scripts/publish.sh test

# 3. Publier sur PyPI production
./scripts/publish.sh prod
```

### Publication régulière
```bash
# Après avoir mis à jour la version dans pyproject.toml
./scripts/publish.sh test  # Test d'abord
./scripts/publish.sh prod  # Puis production
```

## 📊 Workflow Recommandé

```bash
# 1. Préparation
git checkout main
git pull origin main
# Éditer pyproject.toml (version)
# Éditer CHANGELOG.md

# 2. Test
./scripts/publish.sh test

# 3. Production (si test OK)
./scripts/publish.sh prod

# 4. Post-publication
git add .
git commit -m "Release v0.2.0"
git tag v0.2.0
git push origin main --tags
```

## 🚨 Résolution de Problèmes

### Erreur de permissions
```bash
chmod +x scripts/*.sh
```

### Erreur d'authentification
```bash
./scripts/setup_pypi.sh
```

### Erreur de build
```bash
rm -rf dist/ build/ *.egg-info/
python -m build
```

## 📚 Ressources

- [Guide complet](./../GUIDE_PUBLICATION_PYPI.md)
- [Documentation PyPI](https://packaging.python.org/)
- [TestPyPI](https://test.pypi.org/)

---

**Note** : Toujours tester sur TestPyPI avant de publier sur PyPI production ! 

# MIGRATION : Les fonctions resume/resume_display sont remplacées par resumer, graph_desc, evolution

## Nouvelles méthodes d'analyse avancée

- `client.resumer(...)` : résumé statistique et structurel de la base
- `client.graph_desc(...)` : visualisation descriptive (camemberts, barres, histogrammes)
- `client.evolution(...)` : analyse temporelle (par semaine/mois, par sous-groupes, avec taux de croissance)

### Exemples d'utilisation dans les scripts
```python
client.resumer(annee=2024, region="Centre")
client.graph_desc(date_debut="2024-01-01", date_fin="2024-12-31")
client.evolution(by="sexe", frequence="M", taux_croissance=True)
``` 