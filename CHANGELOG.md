# Changelog

Toutes les modifications importantes apportées au package `dengsurvap-bf` sont documentées dans ce fichier.

## [0.2.3] - 2024-12-19

### 🔧 Corrections de bugs
- **CLI Export** : Ajout de l'argument `--filepath` pour l'exportation
- **CLI Export** : Support du format Excel dans les commandes d'export
- **CLI Export** : Création automatique des répertoires parents si nécessaire
- **CLI Cas** : Correction de l'erreur `'str' object has no attribute 'date_consultation'`
- **Client** : Amélioration de la gestion des données malformées dans les méthodes de récupération

### 🆕 Nouvelles fonctionnalités CLI
- **Export Excel** : Support complet du format Excel (.xlsx) pour l'exportation
- **Argument filepath** : Nouvel argument `--filepath` pour spécifier le chemin de sortie
- **Création de répertoires** : Création automatique des répertoires parents lors de l'export

### 📝 Améliorations de la documentation
- Mise à jour des exemples d'utilisation pour les nouvelles fonctionnalités CLI
- Documentation des nouveaux arguments d'export

### 🧪 Tests
- Tests mis à jour pour les nouvelles fonctionnalités d'export
- Tests de robustesse pour la gestion des données malformées

## [0.2.0] - 2024-12-19

### 🔄 Modifications majeures des méthodes de données

#### `get_cas_dengue()` - Changement de type de retour
- **AVANT** : Retournait une liste d'objets `DonneesHebdomadaires` (Pydantic models)
- **APRÈS** : Retourne un `pandas.DataFrame` avec les données agrégées
- **Raison** : Meilleure compatibilité avec les outils d'analyse et de visualisation
- **Impact** : Tous les scripts utilisant cette méthode doivent être adaptés pour utiliser pandas

```python
# Ancien usage
donnees = client.get_cas_dengue(annee=2024, mois=1)
for semaine in donnees:
    print(f"Semaine: {semaine.date_debut} - {semaine.date_fin}")
    print(f"Cas positifs: {semaine.cas_positifs}")

# Nouveau usage
df = client.get_cas_dengue(annee=2024, mois=1)
print(f"Total cas positifs: {df['cas_positifs'].sum()}")
print(f"Moyenne par semaine: {df['cas_positifs'].mean()}")
```

#### `get_alertes()` - Conversion automatique en DataFrame
- **AVANT** : Retournait une liste d'objets `AlertLog` (Pydantic models)
- **APRÈS** : Retourne un `pandas.DataFrame` avec nettoyage automatique des tuples
- **Amélioration** : Nettoyage automatique des données pour éviter les tuples dans les colonnes
- **Impact** : Plus facile à manipuler avec pandas et à exporter

```python
# Ancien usage
alertes = client.get_alertes(limit=10)
for alerte in alertes:
    print(f"Alerte: {alerte.message}")

# Nouveau usage
df_alertes = client.get_alertes(limit=10)
print(f"Alertes critiques: {len(df_alertes[df_alertes['severity'] == 'critical'])}")
```

#### `verifier_alertes()` - Retour au format original
- **AVANT** : Retournait un DataFrame (modification temporaire)
- **APRÈS** : Retourne un dictionnaire brut (comme l'API originale)
- **Raison** : Cette méthode nécessite le format original pour la compatibilité
- **Impact** : Retour à l'utilisation originale

```python
# Usage (inchangé)
alertes_verifiees = client.verifier_alertes(
    date_debut="2024-01-01",
    date_fin="2024-01-31"
)
# Retourne un dict avec les données brutes de l'API
```

### 🔬 Modifications des méthodes d'analyse

#### `calculate_rates()` - Retour en DataFrame
- **AVANT** : Retournait un dictionnaire avec les taux calculés
- **APRÈS** : Retourne un `pandas.DataFrame` avec les taux et métadonnées
- **Amélioration** : Plus facile à manipuler et à intégrer dans des analyses
- **Impact** : Meilleure intégration avec les workflows pandas

```python
# Ancien usage
rates = client.calculate_rates(date_debut="2024-01-01", date_fin="2024-01-31")
print(f"Taux positivité: {rates['taux_positivite']}%")

# Nouveau usage
df_rates = client.calculate_rates(date_debut="2024-01-01", date_fin="2024-01-31")
print(f"Taux positivité: {df_rates['taux_positivite'].iloc[0]}%")
```

#### `detect_anomalies()` - Amélioration de la flexibilité
- **AVANT** : Méthode basique avec détection limitée
- **APRÈS** : Méthode améliorée avec options de colonnes et méthodes de détection
- **Nouvelles fonctionnalités** :
  - Sélection des colonnes à analyser
  - Choix de la méthode de détection (zscore, iqr, isolation_forest)
  - Meilleure gestion des erreurs
- **Impact** : Plus de contrôle sur la détection d'anomalies

```python
# Ancien usage
anomalies = client.detect_anomalies(df)

# Nouveau usage
anomalies = client.detect_anomalies(
    df, 
    columns=['cas_positifs', 'hospitalisations'],
    method="zscore"
)
```

### 📊 Modifications des méthodes de statistiques

#### `get_stats()`, `get_taux_positivite()`, `get_taux_letalite()`, `get_taux_hospitalisation()`
- **AVANT** : Retournaient des listes ou dictionnaires
- **APRÈS** : Retournent des `pandas.DataFrame`
- **Amélioration** : Cohérence avec le reste de l'API
- **Impact** : Interface unifiée pour toutes les méthodes de données

```python
# Toutes ces méthodes retournent maintenant des DataFrames
stats = client.get_stats()  # DataFrame
taux_pos = client.get_taux_positivite()  # DataFrame
taux_let = client.get_taux_letalite()  # DataFrame
taux_hosp = client.get_taux_hospitalisation()  # DataFrame
```

### 🔧 Corrections techniques

#### Gestion des colonnes dans les graphiques
- **Problème** : Erreur `'total_cas'` lors de la génération de graphiques
- **Solution** : Adaptation automatique aux colonnes disponibles
- **Amélioration** : Vérification de l'existence des colonnes avant utilisation
- **Impact** : Plus de robustesse dans l'affichage des graphiques

#### Optimisation des performances
- **Ajout** : Option `full=True` pour la pagination automatique
- **Ajout** : Cache des résultats pour éviter les requêtes répétées
- **Ajout** : Retry automatique avec backoff exponentiel
- **Impact** : Meilleures performances pour les gros volumes de données

### 📚 Documentation mise à jour

- **README.md** : Exemples mis à jour pour refléter les nouveaux types de retour
- **DOCUMENTATION_COMPLETE.md** : Documentation complète des nouvelles fonctionnalités
- **Exemples** : Scripts d'exemple mis à jour
- **Tests** : Tests unitaires adaptés aux nouveaux comportements

### 🧪 Tests mis à jour

- **test_client.py** : Tests adaptés aux nouveaux types de retour
- **test_analytics.py** : Tests pour les nouvelles fonctionnalités d'analyse
- **test_export.py** : Tests pour les nouvelles méthodes d'export

### ⚠️ Breaking Changes

1. **`get_cas_dengue()`** : Changement de type de retour (List → DataFrame)
2. **`get_alertes()`** : Changement de type de retour (List → DataFrame)
3. **`calculate_rates()`** : Changement de type de retour (Dict → DataFrame)
4. **Toutes les méthodes de stats** : Changement de type de retour vers DataFrame

### 🔄 Migration Guide

Pour migrer du code existant :

```python
# Ancien code
donnees = client.get_cas_dengue(annee=2024, mois=1)
for semaine in donnees:
    print(semaine.cas_positifs)

# Nouveau code
df = client.get_cas_dengue(annee=2024, mois=1)
for _, row in df.iterrows():
    print(row['cas_positifs'])

# Ou encore plus simple
print(df['cas_positifs'].tolist())
```

## [0.1.0] - 2024-12-18

### 🎉 Version initiale
- Client Python complet pour l'API Appi Dengue
- Authentification et gestion des sessions
- Récupération des données épidémiologiques
- Système d'alertes
- Outils d'analyse et d'export
- Documentation complète 

## [Unreleased]
### Breaking Changes
- Suppression des méthodes `resume` et `resume_display` du client.
- Ajout de trois nouvelles méthodes avancées : `resumer`, `graph_desc`, `evolution` (issues de la classe SyntheseBase).
- Migration automatique : tous les usages de `resume`/`resume_display` doivent être remplacés par les nouveaux wrappers.
- Les nouvelles méthodes offrent plus de flexibilité, de filtrage, de visualisation et une meilleure compatibilité pandas.

### Migration
- Remplacez :
    - `client.resume(...)` → `client.resumer(...)`
    - `client.resume_display(...)` → `client.graph_desc(...)` ou `client.evolution(...)` selon le besoin
- Voir README pour des exemples détaillés.

### Améliorations
- Documentation enrichie pour toutes les nouvelles méthodes.
- Exemples d'utilisation ajoutés dans le README et les scripts. 