# Changelog

Toutes les modifications notables de ce projet seront documentées dans ce fichier.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-07-09

### 🚀 Ajouté
- **Nouvelle classe `DataExporter`** pour l'export de données
- **Méthodes DataFrame** : `export_to_dataframe()` et `alertes_to_dataframe()`
- **Commande CLI `dab`** pour utilisation en ligne de commande
- **Fonctions de résumé** : `resume()` et `resume_display()` avec graphiques
- **Exclusion automatique** des identifiants (`idCas`, `id_source`) dans les graphiques
- **Gestion sécurisée** de la densité (kde) pour éviter les erreurs sur variables constantes

### 🔄 Modifié
- **`get_cas_dengue()`** : Nouveaux paramètres `annee` et `mois` au lieu de `date_debut`/`date_fin`
- **`donnees_par_periode()`** : Renommé depuis `data_period()`
- **Export** : Déplacé vers la classe `DataExporter` (`exporter.export_data()`, `exporter.alertes()`)
- **Documentation** : Mise à jour complète avec exemples et guide d'utilisation

### 🐛 Corrigé
- **Erreur gaussian_kde** : Gestion des variables constantes dans les graphiques
- **Validation des données** : Amélioration de la gestion des erreurs
- **CLI** : Correction des paramètres pour toutes les commandes

### 📚 Documentation
- **README.md** : Ajout d'exemples détaillés et guide d'installation
- **DOCUMENTATION_COMPLETE.md** : Documentation exhaustive avec cas d'usage
- **Exemples** : Ajout de scripts d'exemple et de tests

### 🔧 Technique
- **Tests** : Mise à jour des tests unitaires pour les nouvelles APIs
- **Configuration** : Amélioration de la gestion des variables d'environnement
- **Logging** : Amélioration des messages d'erreur et de debug

## [0.1.0] - 2025-07-08

### 🚀 Première version
- Client Python pour l'API de surveillance de la dengue
- Authentification JWT
- Gestion des alertes
- Export de données (CSV, JSON, Excel)
- Outils d'analyse épidémiologique
- Interface CLI basique
- Tests unitaires
- Documentation de base

---

## Types de changements

- **🚀 Ajouté** : Nouvelles fonctionnalités
- **🔄 Modifié** : Changements dans les fonctionnalités existantes
- **🐛 Corrigé** : Corrections de bugs
- **📚 Documentation** : Mises à jour de la documentation
- **🔧 Technique** : Améliorations techniques
- **⚠️ Déprécié** : Fonctionnalités qui seront supprimées
- **🗑️ Supprimé** : Fonctionnalités supprimées 