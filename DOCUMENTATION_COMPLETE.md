# Documentation Complète - Package dengsurvap-bf

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture du package](#architecture-du-package)
3. [Installation et configuration](#installation-et-configuration)
4. [Guide d'utilisation](#guide-dutilisation)
5. [API de référence](#api-de-référence)
6. [Modules spécialisés](#modules-spécialisés)
7. [Gestion des erreurs](#gestion-des-erreurs)
8. [Exemples d'utilisation](#exemples-dutilisation)
9. [Migration et nouvelles méthodes](#migration-et-nouvelles-méthodes)
10. [Tests et qualité](#tests-et-qualité)
11. [Déploiement](#déploiement)

---

## 🎯 Vue d'ensemble

Le package `dengsurvap-bf` est un client Python officiel pour l'API de surveillance de la dengue Appi ( La plateforme de surveillance de dengue au Burkina Faso ). Il fournit une interface complète pour :

- **Accéder aux données épidémiologiques** de la dengue
- **Gérer les alertes** et leur configuration
- **Effectuer des analyses avancées** (séries temporelles, détection d'anomalies)
- **Exporter les données** dans différents formats
- **Authentifier les utilisateurs** avec gestion des rôles

### Caractéristiques principales

- ✅ **Interface intuitive** avec validation automatique des données
- ✅ **Gestion d'erreurs robuste** avec exceptions spécialisées
- ✅ **Cache intelligent** pour optimiser les performances
- ✅ **Support multi-formats** (CSV, JSON, xlsx, PDF)
- ✅ **Analyses épidémiologiques avancées**
- ✅ **Système d'alertes configurable**
- ✅ **CLI intégré** pour utilisation en ligne de commande
- ✅ **Tests complets** avec couverture élevée

---

## 🏗️ Architecture du package

### Structure des modules

```
dengsurvap-bf/
├── dengsurvab/
│   ├── __init__.py          # Point d'entrée principal
│   ├── client.py            # Client principal AppiClient
│   ├── models.py            # Modèles Pydantic
│   ├── exceptions.py        # Exceptions personnalisées
│   ├── analytics.py         # Outils d'analyse
│   ├── alerts.py            # Gestion des alertes
│   ├── auth.py              # Authentification
│   ├── export.py            # Export de données
│   └── cli.py               # Interface CLI
├── tests/                   # Tests unitaires
├── examples/                # Exemples d'utilisation
├── pyproject.toml          # Configuration du projet
└── README.md               # Documentation de base
```

### Flux de données

```
Utilisateur → AppiClient → API Appi → Données épidémiologiques
                ↓
        Modules spécialisés:
        - Analytics (analyses)
        - Alerts (alertes)
        - Export (export)
        - Auth (authentification)
```

---

## 🚀 Installation

Pour utiliser le client Appi Dengue, il faut d'abord installer le package Python. L'installation standard suffit pour accéder à toutes les fonctionnalités principales (connexion, récupération de données, alertes, export). Si vous souhaitez réaliser des analyses statistiques avancées ou des visualisations, ajoutez l'option `[analysis]` pour installer les dépendances supplémentaires (pandas, matplotlib, seaborn, etc.).

---

## 📖 Guide rapide

Ce guide vous accompagne pas à pas pour démarrer avec le client Appi Dengue. Vous apprendrez à vous connecter à l'API, à récupérer et exporter des données, et à utiliser les principales fonctionnalités du package. Chaque exemple est conçu pour être directement réutilisable dans vos propres scripts ou notebooks.

---

## Connexion à l'API

Avant toute opération, il est nécessaire d'initialiser le client avec l'URL de l'API et, si besoin, une clé API. L'authentification permet d'accéder aux données sécurisées et de personnaliser l'expérience selon le profil utilisateur (droits, préférences, etc.).

---

## Récupération des données

Le client permet de récupérer facilement les cas de dengue, les indicateurs épidémiologiques par période, et d'autres informations utiles pour l'analyse ou la veille sanitaire. Utilisez les filtres (dates, région, district, etc.) pour cibler précisément les données qui vous intéressent. Ces méthodes sont adaptées aussi bien à l'exploration rapide qu'à l'intégration dans des pipelines d'analyse.

---

## Export de données

Pour sauvegarder ou partager les données, utilisez la classe `DataExporter` ou directement la calsse `AppiClient`. Elles permettent d'exporter les résultats dans différents formats (CSV, JSON, Excel) adaptés à vos besoins : archivage, reporting, import dans d'autres outils, ou analyse avancée avec pandas. L'export direct en DataFrame facilite l'intégration avec l'écosystème Python scientifique.

---

## Gestion des alertes

Le système d'alertes intégré vous aide à surveiller automatiquement les seuils critiques (taux de positivité, hospitalisations, décès, etc.), à configurer des notifications, et à suivre l'évolution des risques sanitaires. C'est un outil clé pour la veille épidémiologique et la prise de décision rapide.

---

## 🔧 Configuration

Configurer le client via des variables d'environnement est la méthode recommandée pour sécuriser vos identifiants. Cela évite de stocker des informations sensibles dans le code source et permet de changer facilement de configuration sans modifier vos scripts.

---

## Configuration programmatique

Vous pouvez aussi configurer le client directement dans votre code Python, en utilisant les variables d'environnement ou en passant les paramètres manuellement. Cette méthode est utile pour les scripts portables ou les environnements où la configuration par variables d'environnement n'est pas possible.

---

## 🚀 Commande CLI rapide : `dab`

La CLI `dab` permet d'automatiser et de simplifier toutes les opérations courantes (authentification, export, alertes, etc.) directement depuis le terminal, sans écrire de code Python. Elle est idéale pour les scripts, l'intégration continue, ou pour les utilisateurs non-développeurs qui souhaitent accéder rapidement aux données.

---

## 📊 Utilisation avancée avec DataFrame

Pour l'analyse de données, il est souvent plus pratique d'obtenir directement un DataFrame pandas. Les méthodes `data`, `export_to_dataframe`, `alertes`, et `alertes_to_dataframe` permettent d'intégrer les données dans vos workflows analytiques Python, facilitant ainsi la visualisation, le traitement statistique et la modélisation.

---

## 🧪 Tests (cette section addresse aux contributeurs)

Les tests sont essentiels pour garantir la fiabilité et la robustesse du package. Ils permettent de vérifier que toutes les fonctionnalités fonctionnent comme prévu, d'éviter les régressions lors des mises à jour, et de faciliter la maintenance du code.

---

## 🐛 Dépannage

Cette section propose des solutions concrètes aux erreurs courantes (authentification, connexion, validation) et des conseils pratiques pour diagnostiquer rapidement les problèmes. Elle vous aide à gagner du temps et à résoudre efficacement les blocages éventuels.

---

## 🔌 API de référence

### Classe AppiClient

#### Méthodes d'authentification

```python
def authenticate(self, email: str, password: str) -> Dict[str, Any]
```
Authentifie l'utilisateur et récupère un token JWT.

```python
def logout(self) -> bool
```
Déconnecte l'utilisateur et invalide le token.

```python
def get_profile(self) -> User
```
Récupère le profil de l'utilisateur connecté.

#### Méthodes de données

```python
def get_cas_dengue(self, 
                   annee: int = date.today().year,
                   mois: int = date.today().month,
                   region: Optional[str] = None,
                   district: Optional[str] = None) -> List[CasDengue]
```
Récupère les cas de dengue selon les critères.

```python
def get_stats(self) -> Statistiques
```
Récupère les statistiques générales.

```python
def donnees_par_periode(self,
                         date_debut: str,
                         date_fin: str,
                         region: str = "Toutes",
                         district: str = "Toutes",
                         frequence: str = "W") -> List[IndicateurHebdo]
```

Récupère les indicateurs hebdomadaires ou mensuelles. frequence : `W --> Semaine` et `M --> Mois`.
#### Méthodes d'alertes

```python
def get_alertes(self,
                limit: int = 10,
                severity: Optional[str] = None,
                status: Optional[str] = None,
                region: Optional[str] = None,
                district: Optional[str] = None,
                date_debut: Optional[str] = None,
                date_fin: Optional[str] = None) -> List[AlertLog]
```
Récupère les alertes selon les critères.

```python
def configurer_seuils(self, **kwargs) -> Dict[str, Any]
```
Configure les seuils d'alerte.

```python
def verifier_alertes(self,
                    date_debut: Optional[str] = None,
                    date_fin: Optional[str] = None,
                    region: str = "Toutes",
                    district: str = "Toutes") -> Dict[str, Any]
```
Vérifie les alertes selon les critères.

#### Méthodes d'export

```python
def save_to_file(self,
        filepath: Optional[str] = None,
        date_debut: Optional[str] = None,
        date_fin: Optional[str] = None,
        region: Optional[str] = None,
        district: Optional[str] = None,
        limit: Optional[int] = None,
        page: Optional[int] = None,
        format: str = "csv") -> bool:
```
Exporte les données dans le format spécifié.

```python
def alertes_to_file(self,
                          filepath: Optional[str] = None,
                          limit: int = 100,
                          severity: Optional[str] = None,
                          status: Optional[str] = None,
                          format: str = "csv") -> bool:
```
Exporte les alertes dans le format spécifié.

---

## 🔬 Modules spécialisés

### 1. Module Analytics

#### EpidemiologicalAnalyzer

```python
from dengsurvab import EpidemiologicalAnalyzer

analyzer = EpidemiologicalAnalyzer(client)

# Série temporelle
series = analyzer.get_time_series(
    date_debut="2024-01-01",
    date_fin="2024-01-31",
    frequency="W"
)

# Détection d'anomalies
anomalies = analyzer.detect_anomalies(series, method="zscore")

# Calcul de taux
taux = analyzer.calculate_rates(
    date_debut="2024-01-01",
    date_fin="2024-01-31"
)

# Analyse de tendance
tendance = analyzer.trend_analysis(series, column="total_cas")

# Analyse saisonnière
saisonnalite = analyzer.seasonal_analysis(series, column="total_cas")

# Prévision
prevision = analyzer.forecast_next_week(series, column="total_cas")
```

#### DashboardGenerator

```python
from dengsurvab import DashboardGenerator

generator = DashboardGenerator(client)

# Génération de rapport
rapport = generator.generate_report(
    date_debut="2024-01-01",
    date_fin="2024-01-31",
    region="Toutes",
    include_visualizations=True
)

# Sauvegarde
generator.save_report(rapport, "rapport_epidemio.json")
```

### 2. Module Alerts

```python
from dengsurvab import AlertManager

alert_manager = AlertManager(client)

# Récupération d'alertes
alertes = alert_manager.get_alertes(
    severity="critical",
    status="active",
    limit=10
)

# Configuration des seuils
config = alert_manager.configurer_seuils(
    seuil_positivite=10,
    seuil_hospitalisation=5,
    seuil_deces=2
)

# Vérification automatique
verification = alert_manager.verifier_alertes(
    date_debut="2024-01-01",
    date_fin="2024-01-31"
)

# Export des alertes
alertes_export = alert_manager.exporter_alertes(
    format="csv",
    severity="critical"
)
```

### 3. Module Export

```python
from dengsurvab import DataExporter

exporter = DataExporter(client)

# Export de données
data_csv = exporter.export_data(
    format="csv",
    date_debut="2024-01-01",
    date_fin="2024-01-31"
)

# Export d'alertes
alertes_csv = exporter.alertes(
    format="csv",
    severity="critical"
)

# Export de rapport
rapport_json = exporter.export_rapport(
    format="json",
    date_debut="2024-01-01",
    date_fin="2024-01-31"
)

# Sauvegarde
exporter.save_to_file(data_csv, "donnees.csv", "csv")
```

---

## 🧩 Classe avancée : SyntheseBase

La classe `SyntheseBase` est le cœur de l'analyse descriptive, graphique et temporelle du package. Elle est utilisée en interne par le client, mais peut aussi être instanciée directement pour des analyses personnalisées sur n'importe quel DataFrame compatible.

### Présentation générale

`SyntheseBase` permet de :
- Résumer la base de données (statistiques, structure, informations générales)
- Générer des visualisations descriptives (camemberts, barres, histogrammes)
- Analyser l'évolution temporelle (par semaine/mois, par sous-groupes, avec taux de croissance)

Elle s'appuie sur pandas, matplotlib et seaborn pour garantir des analyses rapides, robustes et visuellement agréables.

### Fonctionnement des principales méthodes

#### 1. `resumer`
Cette méthode affiche un résumé structuré et enrichi de la base de données :
- Période de couverture (date de début, date de fin, durée)
- Nombre d'observations, de régions, de districts
- Dernière mise à jour (si disponible via l'API)
- Statistiques quantitatives (min, max, moyenne, quartiles, valeurs manquantes)
- Statistiques qualitatives (type, mode, nombre de modalités, valeurs manquantes)
- Détail des modalités (optionnel)

Elle accepte de nombreux filtres (année, région, district, dates, etc.) pour cibler l'analyse.

#### 2. `graph_desc`
Cette méthode génère des graphiques descriptifs adaptés à chaque variable :
- Diagrammes en barres pour les variables à nombreuses modalités (district, région...)
- Camemberts pour les variables à peu de modalités (sexe, issue, serotype...)
- Histogramme et boxplot pour l'âge

Les graphiques peuvent être affichés à l'écran ou sauvegardés dans un dossier. Tous les filtres temporels et géographiques sont disponibles.

#### 3. `evolution`
Cette méthode analyse l'évolution des variables cibles (issue, hospitalisation, resultat_test) par période (semaine ou mois), globalement ou par sous-groupes (ex : sexe, région, district, etc.).
- Génère des courbes d'évolution, des graphiques de croissance absolue et en pourcentage
- Permet de choisir la fréquence (hebdomadaire ou mensuelle), d'afficher ou non les taux de croissance, et de limiter le nombre de graphiques

### Exemples d'utilisation Python

```python
from dengsurvab.analytics import SyntheseBase
from dengsurvab import AppiClient

client = AppiClient()
synth = SyntheseBase(client=client)

# Résumé statistique
synth.resumer(annee=2024, region="Centre", detail=True)

# Visualisation descriptive
synth.graph_desc(date_debut="2024-01-01", date_fin="2024-12-31", save_dir="./figures")

# Analyse temporelle avancée
synth.evolution(by="sexe", frequence="M", taux_croissance=True, max_graph=6)
```

Il est aussi possible d'utiliser un DataFrame pandas directement :
```python
import pandas as pd
df = pd.read_csv("mes_donnees.csv")
synth = SyntheseBase(df=df)
synth.resumer()
```

### Utilisation avec la CLI (dab)

Les fonctionnalités de SyntheseBase sont accessibles en ligne de commande via `dab` :

- Résumé statistique :
```bash
dab resumer --annee 2024 --region "Centre" --detail
```
- Visualisation descriptive :
```bash
dab graph_desc --date-debut 2024-01-01 --date-fin 2024-12-31 --save-dir ./figures
```
- Analyse temporelle :
```bash
dab evolution --by sexe --frequence M --taux-croissance --max-graph 6
```

### Bonnes pratiques et cas d'usage
- Utilisez les filtres pour limiter la quantité de données analysées et accélérer les traitements.
- Les graphiques peuvent être sauvegardés pour intégration dans des rapports ou des dashboards.
- La méthode `resumer` affiche automatiquement les informations générales, la période de couverture, et la dernière mise à jour (si disponible via l'API).
- Pour des analyses personnalisées, instanciez `SyntheseBase` avec un DataFrame local.

---

## 🚨 Gestion des erreurs

### Exceptions disponibles

```python
from dengsurvab import (
    AppiException,
    AuthenticationError,
    APIError,
    ValidationError,
    RateLimitError,
    ConnectionError,
    AnalysisError,
    AlertConfigurationError,
    DataExportError
)
```

### Gestion typique

```python
from dengsurvab import AppiClient, AuthenticationError, APIError

try:
    client = AppiClient("https://api.appi.com")
    cas = client.get_cas_dengue(annee=2024, mois=1)
    
except AuthenticationError as e:
    print(f"Erreur d'authentification: {e}")
    
except APIError as e:
    print(f"Erreur API: {e}")
    
except Exception as e:
    print(f"Erreur inattendue: {e}")
```

### Exemple 1: Surveillance épidémiologique

```python
from dengsurvab import AppiClient, EpidemiologicalAnalyzer

# Connexion
client = AppiClient("https://api.appi.com")
client.authenticate("epidemiologist@health.gov", "password")

# Récupération des données
cas = client.get_cas_dengue(
    annee=2024,
    mois=1,
    region="Antananarivo"
)

# Analyse épidémiologique
analyzer = EpidemiologicalAnalyzer(client)
series = analyzer.get_time_series(
    date_debut="2024-01-01",
    date_fin="2024-01-31",
    frequency="W"
)

# Détection d'anomalies
anomalies = analyzer.detect_anomalies(series, method="isolation_forest")

# Export du rapport
rapport = analyzer.generate_report(
    date_debut="2024-01-01",
    date_fin="2024-01-31",
    region="Antananarivo"
)

print(f"Cas analysés: {len(cas)}")
print(f"Anomalies détectées: {len(anomalies[anomalies['total_cas_anomaly']])}")
```

### Exemple 2: Système d'alertes

```python
from dengsurvab import AppiClient, AlertManager

# Connexion
client = AppiClient("https://api.appi.com")
client.authenticate("alert-manager@health.gov", "password")

# Configuration des seuils
alert_manager = AlertManager(client)
alert_manager.configurer_seuils(
    seuil_positivite=15,      # 15% de positivité
    seuil_hospitalisation=10,  # 10% d'hospitalisation
    seuil_deces=5             # 5% de décès
)

# Vérification des alertes
alertes = alert_manager.verifier_alertes(
    date_debut="2024-01-01",
    date_fin="2024-01-31",
    region="Toutes"
)

# Récupération des alertes critiques
alertes_critiques = alert_manager.get_alertes_critiques(limit=10)

# Export des alertes
alertes_export = alert_manager.exporter_alertes(
    format="csv",
    severity="critical"
)

print(f"Alertes actives: {len(alertes_critiques)}")
```

### Exemple 3: Export et reporting

```python
from dengsurvab import AppiClient, DataExporter

# Connexion
client = AppiClient("https://api.appi.com")
client.authenticate("data-analyst@health.gov", "password")

# Export de données
exporter = DataExporter(client)

# Export CSV des cas
cas_csv = exporter.export_data(
    format="csv",
    date_debut="2024-01-01",
    date_fin="2024-01-31",
    region="Toutes"
)

# Export JSON des alertes
alertes_json = exporter.alertes(
    format="json",
    severity="critical"
)

# Export Excel du rapport
rapport_excel = exporter.export_rapport(
    format="xlsx",
    date_debut="2024-01-01",
    date_fin="2024-01-31"
)

# Sauvegarde
exporter.save_to_file(cas_csv, "cas_dengue_janvier.csv", "csv")
exporter.save_to_file(alertes_json, "alertes_critiques.json", "json")
exporter.save_to_file(rapport_excel, "rapport_epidemio.xlsx", "xlsx")

print("Exports terminés avec succès")
```

---

## 📑 Exemples d'utilisation de la CLI

Voici des cas d'usage concrets de la commande `dab` :

### 1. Authentification

```bash
dab auth --email user@example.com --password monmotdepasse
```
*Authentifie l’utilisateur et prépare le token pour les autres commandes.*

---

### 2. Afficher les statistiques générales

```bash
dab stats
```
*Affiche le nombre total de cas, hospitalisations, décès, etc.*

---

### 3. Récupérer les cas de dengue sur une période

```bash
dab cas --date-debut 2024-01-01 --date-fin 2024-01-31 --region Centre --limit 20
```
*Récupère les 20 premiers cas de la région Centre pour janvier 2024.*

---

### 4. Lister les alertes critiques actives

```bash
dab alertes --severity critical --status active --limit 5
```
*Affiche les 5 alertes critiques actives les plus récentes.*

---

### 5. Exporter les données au format CSV

```bash
dab export --format csv --output donnees_janvier.csv --date-debut 2024-01-01 --date-fin 2024-01-31
```
*Exporte toutes les données de janvier 2024 dans un fichier CSV.*

---

### 6. Exporter les alertes au format JSON

```bash
dab export --format json --output alertes.json --date-debut 2024-01-01 --date-fin 2024-01-31 --region Centre
```
*Exporte les alertes de la région Centre en janvier 2024 au format JSON.*

---

### 7. Lister toutes les régions disponibles

```bash
dab regions
```

---

### 8. Lister les districts d’une région

```bash
dab districts --region Centre
```

---

### 9. Obtenir de l’aide sur une commande

```bash
dab export --help
```
*Affiche toutes les options disponibles pour la commande d’export.*

---

### 10. Script d’automatisation (exemple Bash)

```bash
dab auth --email user@example.com --password monmotdepasse
dab export --format csv --output export.csv --date-debut 2024-01-01 --date-fin 2024-01-31
dab alertes --severity warning --limit 10 > alertes.txt
```
*Automatise l’authentification, l’export et la récupération d’alertes dans un script.*

---

## 🖥️ Utilisation détaillée des commandes CLI

Le package `dengsurvap-bf` fournit une commande CLI officielle : **dab**

Après installation du package (`pip install dengsurvap-bf`), la commande `dab` est disponible partout dans votre terminal.

### Commandes principales

#### 1. Authentification

```bash
dab auth --email <email> --password <motdepasse>
```
- **Description** : Authentifie l'utilisateur et stocke le token pour les commandes suivantes.
- **Options** :
  - `--email` : Email de l'utilisateur (obligatoire)
  - `--password` : Mot de passe (obligatoire)
- **Exemple** :
  ```bash
  dab auth --email user@example.com --password monmotdepasse
  ```

#### 2. Statistiques générales

```bash
dab stats
```
- **Description** : Affiche les statistiques globales de la base de données (total cas, hospitalisations, décès, etc.).
- **Exemple** :
  ```bash
  dab stats
  ```

#### 3. Récupération de cas de dengue

```bash
dab cas --date-debut <YYYY-MM-DD> --date-fin <YYYY-MM-DD> [--region <nom>] [--district <nom>] [--limit <n>]
```
- **Description** : Récupère les cas de dengue selon les critères fournis.
- **Options** :
  - `--date-debut` : Date de début (obligatoire)
  - `--date-fin` : Date de fin (obligatoire)
  - `--region` : Région (optionnel)
  - `--district` : District (optionnel)
  - `--limit` : Nombre maximum de cas (optionnel)
- **Exemple** :
  ```bash
  dab cas --date-debut 2024-01-01 --date-fin 2024-01-31 --region Centre --limit 50
  ```

#### 4. Gestion des alertes

```bash
dab alertes [--severity <niveau>] [--status <statut>] [--limit <n>]
```
- **Description** : Affiche la liste des alertes selon la sévérité, le statut, etc.
- **Options** :
  - `--severity` : Niveau de sévérité (ex : critical, warning)
  - `--status` : Statut (active, resolved)
  - `--limit` : Nombre maximum d'alertes
- **Exemple** :
  ```bash
  dab alertes --severity critical --status active --limit 10
  ```

#### 5. Export de données

```bash
dab export --format <csv|json|xlsx|pdf> --output <fichier> --date-debut <YYYY-MM-DD> --date-fin <YYYY-MM-DD> [--region <nom>] [--district <nom>]
```
- **Description** : Exporte les données dans le format choisi.
- **Options** :
  - `--format` : Format d'export (csv, json, xlsx, pdf)
  - `--output` : Chemin du fichier de sortie
  - `--date-debut` / `--date-fin` : Période à exporter (obligatoire)
  - `--region` / `--district` : Filtres géographiques (optionnels)
- **Exemple** :
  ```bash
  dab export --format csv --output donnees.csv --date-debut 2024-01-01 --date-fin 2024-01-31
  ```

#### 6. Liste des régions

```bash
dab regions
```
- **Description** : Affiche la liste des régions disponibles.

#### 7. Liste des districts d'une région

```bash
dab districts --region <nom>
```

---

## Changements de version

### Version 0.2.0 - Changements majeurs

#### 🔄 Modifications des types de retour

**ATTENTION** : Cette version introduit des changements importants dans les types de retour de plusieurs méthodes pour améliorer la compatibilité avec pandas et les outils d'analyse.

##### `get_cas_dengue()`
- **AVANT** : `List[DonneesHebdomadaires]`
- **APRÈS** : `pandas.DataFrame`
- **Impact** : Meilleure intégration avec les workflows pandas

```python
# Ancien usage
donnees = client.get_cas_dengue(annee=2024, mois=1)
for semaine in donnees:
    print(semaine.cas_positifs)

# Nouveau usage
df = client.get_cas_dengue(annee=2024, mois=1)
print(df['cas_positifs'].sum())
```

##### `get_alertes()`
- **AVANT** : `List[AlertLog]`
- **APRÈS** : `pandas.DataFrame`
- **Amélioration** : Nettoyage automatique des tuples dans les données

```python
# Ancien usage
alertes = client.get_alertes(limit=10)
for alerte in alertes:
    print(alerte.message)

# Nouveau usage
df_alertes = client.get_alertes(limit=10)
print(f"Alertes critiques: {len(df_alertes[df_alertes['severity'] == 'critical'])}")
```

##### `calculate_rates()`
- **AVANT** : `Dict[str, Any]`
- **APRÈS** : `pandas.DataFrame`
- **Amélioration** : Plus facile à manipuler et à intégrer dans des analyses

```python
# Ancien usage
rates = client.calculate_rates(date_debut="2024-01-01", date_fin="2024-01-31")
print(f"Taux positivité: {rates['taux_positivite']}%")

# Nouveau usage
df_rates = client.calculate_rates(date_debut="2024-01-01", date_fin="2024-01-31")
print(f"Taux positivité: {df_rates['taux_positivite'].iloc[0]}%")
```

##### `detect_anomalies()`
- **Nouvelles fonctionnalités** :
  - Sélection des colonnes à analyser
  - Choix de la méthode de détection (zscore, iqr, isolation_forest)
  - Meilleure gestion des erreurs

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

#### 📊 Méthodes de statistiques unifiées

Toutes les méthodes de statistiques retournent maintenant des DataFrames :
- `get_stats()` → `pandas.DataFrame`
- `get_taux_positivite()` → `pandas.DataFrame`
- `get_taux_letalite()` → `pandas.DataFrame`
- `get_taux_hospitalisation()` → `pandas.DataFrame`

#### 🔧 Corrections techniques

- **Gestion des colonnes dans les graphiques** : Adaptation automatique aux colonnes disponibles
- **Optimisation des performances** : Option `full=True` pour la pagination automatique
- **Retry automatique** : Backoff exponentiel pour les erreurs réseau

#### ⚠️ Breaking Changes

1. **`get_cas_dengue()`** : Changement de type de retour (List → DataFrame)
2. **`get_alertes()`** : Changement de type de retour (List → DataFrame)
3. **`calculate_rates()`** : Changement de type de retour (Dict → DataFrame)
4. **Toutes les méthodes de stats** : Changement de type de retour vers DataFrame

#### 🔄 Guide de migration

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

### Version 0.1.0 - Version initiale

- Client Python complet pour l'API Appi Dengue
- Authentification et gestion des sessions
- Récupération des données épidémiologiques
- Système d'alertes
- Outils d'analyse et d'export
- Documentation complète
