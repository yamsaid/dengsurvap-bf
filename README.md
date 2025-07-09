# Appi Dengue Client

Client Python officiel pour l'API de surveillance de la dengue Appi. Ce package permet d'accéder facilement aux données épidémiologiques, de gérer les alertes et d'effectuer des analyses avancées.

## 🚀 Installation

Pour utiliser le client Appi Dengue, commencez par installer le package. L'installation standard suffit pour la plupart des usages, mais vous pouvez ajouter `[analysis]` pour les fonctionnalités avancées d'analyse et de visualisation.

```bash
pip install dengsurvap-bf
```

Pour les fonctionnalités d'analyse avancées :
```bash
pip install dengsurvap-bf[analysis]
```

---

## 📖 Guide rapide

Cette section présente les étapes essentielles pour démarrer rapidement avec le client Python, de la connexion à l'API à la récupération et l'export des données.

### Connexion à l'API

Avant toute opération, il faut initialiser le client avec l'URL de l'API et (optionnellement) une clé API. L'authentification permet d'accéder aux fonctionnalités sécurisées.

```python
from dengsurvab import AppiClient

# Initialisation du client
client = AppiClient(
    base_url="https://votre-api-appi.com",
    api_key="votre-clé-api"
)

# Authentification
client.authenticate("votre-email", "votre-mot-de-passe")
```

### Récupération des données

Utilisez ces méthodes pour obtenir les cas de dengue, les indicateurs par période, ou d'autres informations épidémiologiques. Adaptez les filtres selon vos besoins (dates, région, etc.).

```python
# Récupérer les cas de dengue
cas = client.get_cas_dengue(
    annee=2024,
    mois=1,
    region="Antananarivo"
)

# Récupérer les indicateurs par période (hebdo, mensuel, etc.)
indicateurs = client.donnees_par_periode(
    date_debut="2024-01-01",
    date_fin="2024-12-31",
    region="Toutes"
)
```

### Exporter les données (nouvelle méthode)

Pour exporter les données ou les alertes dans différents formats (CSV, JSON, Excel), utilisez la classe `DataExporter`. Cela permet de sauvegarder ou d'analyser facilement les résultats.

```python
from dengsurvab import DataExporter
exporter = DataExporter(client)

# Exporter les données au format CSV
csv_bytes = exporter.export_data(
    format="csv",
    date_debut="2024-01-01",
    date_fin="2024-12-31"
)

# Exporter les alertes au format JSON
alertes_json = exporter.alertes(
    format="json",
    severity="critical"
)

# Export direct en DataFrame (pour l'analyse avec pandas)
df = exporter.export_to_dataframe(date_debut="2024-01-01", date_fin="2024-01-31")

# Export des alertes en DataFrame
df_alertes = exporter.alertes_to_dataframe(limit=100, severity="high", status="active")
```

### Gestion des alertes

Le système d'alertes permet de surveiller automatiquement les seuils critiques, de configurer des notifications et de suivre l'évolution des risques sanitaires.

```python
# Récupérer les alertes actives
alertes = client.get_alertes(severity="critical", status="active")

# Configurer les seuils d'alerte
client.configurer_seuils(
    seuil_positivite=10,
    seuil_hospitalisation=5,
    seuil_deces=2
)

# Vérifier les alertes
alertes_verifiees = client.verifier_alertes(
    date_debut="2024-01-01",
    date_fin="2024-12-31"
)
```

---

## 🔧 Fonctionnalités principales

### 📊 Données épidémiologiques
- Récupération des cas de dengue
- Indicateurs hebdomadaires et mensuels
- Analyses géographiques et démographiques
- Calculs de taux (hospitalisation, létalité, positivité)

### 🚨 Système d'alertes
- Configuration des seuils d'alerte
- Vérification automatique des alertes
- Historique des alertes
- Notifications personnalisées

### 📈 Outils d'analyse
- Séries temporelles
- Détection d'anomalies
- Analyses statistiques
- Visualisations

### 🔐 Authentification sécurisée
- Support JWT
- Gestion des rôles (user, analyst, admin, authority)
- Tokens automatiques
- Sécurité renforcée

### 📤 Export/Import
- Formats multiples (CSV, JSON, Excel)
- Filtrage avancé
- Validation des données
- Compression automatique

## 📚 Documentation complète

### Modèles de données

#### Cas de dengue
```python
from dengsurvab.models import CasDengue

cas = CasDengue(
    idCas=1,
    date_consultation="2024-01-15",
    region="Antananarivo",
    district="Analamanga",
    sexe="M",
    age=25,
    resultat_test="Positif",
    serotype="DENV2",
    hospitalise="Non",
    issue="Guéri",
    id_source=1
)
```

#### Alertes
```python
from dengsurvab.models import AlertLog

alerte = AlertLog(
    id=1,
    severity="critical",
    status="active",
    message="Seuil dépassé pour la région Antananarivo",
    region="Antananarivo",
    created_at="2024-01-15T10:30:00"
)
```

### Méthodes principales

#### Client API
```python
# Authentification
client.authenticate(email, password)
client.logout()

# Données
client.get_cas_dengue(annee=2024, mois=1, region="Centre")
client.donnees_par_periode(**params)
client.get_stats()

# Résumé statistique
client.resume()                    # Résumé JSON structuré
client.resume_display(verbose=True, show_details=True, graph=True)  # Affichage console avec graphiques

# Alertes
client.get_alertes(**params)
client.configurer_seuils(**params)
client.verifier_alertes(**params)

# Export
exporter.export_data(format="csv", **params)
exporter.alertes(format="json", **params)
```

#### Outils d'analyse
```python
from dengsurvab.analytics import EpidemiologicalAnalyzer

analyzer = EpidemiologicalAnalyzer(client)

# Analyses temporelles
series = analyzer.get_time_series(
    date_debut="2024-01-01",
    date_fin="2024-12-31",
    frequency="W"
)

# Détection d'anomalies
anomalies = analyzer.detect_anomalies(series)

# Calculs de taux
taux = analyzer.calculate_rates(
    date_debut="2024-01-01",
    date_fin="2024-12-31"
)
```

---

## 🧪 Tests

Les tests permettent de s'assurer que toutes les fonctionnalités du package fonctionnent correctement, et facilitent la maintenance et l'évolution du code.

```bash
# Installer les dépendances de développement
pip install dengsurvap-bf[dev]

# Lancer les tests
pytest

# Avec couverture
pytest --cov=dengsurvab

# Tests spécifiques
pytest tests/test_client.py
pytest tests/test_analytics.py
```

---

## 🔧 Configuration

Configurer le client via des variables d'environnement permet de sécuriser vos identifiants et de faciliter le déploiement sur différents environnements (local, serveur, cloud). C'est la méthode recommandée pour éviter de stocker des informations sensibles dans le code.

### Variables d'environnement
Pour une configuration plus flexible et sécurisée, vous pouvez utiliser les variables d’environnement suivantes :
```bash
export APPI_API_URL="https://api-bf-dengue-survey-production.up.railway.app/"
export APPI_API_KEY="votre-clé-api"
export APPI_DEBUG="false"
```

### Configuration programmatique
Vous pouvez aussi configurer le client directement dans votre code, en utilisant les variables d'environnement ou en passant les paramètres manuellement.

```python
import os
from dengsurvab import AppiClient

# Configuration via variables d'environnement
client = AppiClient.from_env()

# Configuration manuelle
client = AppiClient(
    base_url=os.getenv("APPI_API_URL"),
    api_key=os.getenv("APPI_API_KEY"),
    debug=os.getenv("APPI_DEBUG", "false").lower() == "true"
)
```

---

## 📊 Exemples avancés

### Résumé statistique avec graphiques
```python
from dengsurvab import AppiClient

client = AppiClient("https://api.example.com", "your-key")

# Résumé complet avec graphiques
client.resume_display(
    verbose=True,      # Afficher tous les détails
    show_details=True, # Statistiques détaillées
    graph=True        # Afficher les graphiques
)

# Résumé simplifié sans graphiques
client.resume_display(
    verbose=False,     # Affichage simplifié
    show_details=False, # Pas de détails
    graph=False       # Pas de graphiques
)

# Résumé avec graphiques mais sans détails
client.resume_display(
    verbose=False,     # Affichage simplifié
    show_details=False, # Pas de détails
    graph=True        # Afficher les graphiques
)
```

### Dashboard épidémiologique
```python
from dengsurvab import AppiClient
from dengsurvab.analytics import DashboardGenerator

client = AppiClient("https://api.example.com", "your-key")
dashboard = DashboardGenerator(client)

# Générer un rapport complet
rapport = dashboard.generate_report(
    date_debut="2024-01-01",
    date_fin="2024-12-31",
    region="Toutes",
    include_visualizations=True
)

# Sauvegarder le rapport
dashboard.save_report(rapport, "rapport_dengue_2024.pdf")
```

### Surveillance en temps réel
```python
from dengsurvab import AppiClient
import time

client = AppiClient("https://api.example.com", "your-key")

def surveillance_continue():
    while True:
        # Vérifier les nouvelles alertes
        alertes = client.get_alertes(status="active")
        
        for alerte in alertes:
            print(f"Nouvelle alerte: {alerte.message}")
            
        # Attendre 5 minutes
        time.sleep(300)

# Démarrer la surveillance
surveillance_continue()
```
---
## 📊 Utilisation avancée avec DataFrame

Pour l'analyse de données, il est souvent plus pratique d'obtenir directement un DataFrame pandas. Les méthodes `export_to_dataframe` et `alertes_to_dataframe` de la classe `DataExporter` ou les methodes `data` et `alertes` de la classe `AppiClient` permettent d'intégrer les données dans vos workflows analytiques Python.

### Export direct en DataFrame
```python
from dengsurvab import AppiClient
client = AppiClient("https://api-correcte.com", "your-key")
df = client.data(date_debut="2024-01-01", date_fin="2024-01-31", limit=100, ...)
```
ou 

```python
from dengsurvab import DataExporter
exporter = DataExporter(client)
df = exporter.export_to_dataframe(date_debut="2024-01-01", date_fin="2024-01-31", ...)
```

### Export des alertes en DataFrame
```python
df_alertes = client.alertes(limit=100, severity="warming", status="active")
```
ou

```python
df_alertes = exporter.alertes_to_dataframe(limit=100, severity="warming", status="active")
```

--- 

---

> **Note de migration :**
> - Les méthodes d'export (export_data, export_alertes, etc.) sont désormais accessibles via la classe `DataExporter`.
> - Pour la récupération de séries temporelles, utilisez `client.donnees_par_periode`.

--- 

---

**Appi Dengue Client** - Simplifiez l'accès aux données de surveillance de la dengue avec Python. 

---

## 🚀 Commande CLI rapide : `dab`

La CLI `dab` permet d'automatiser et de simplifier toutes les opérations courantes (authentification, export, alertes, etc.) directement depuis le terminal, sans écrire de code Python. Idéal pour les scripts, l'intégration continue ou les utilisateurs non-développeurs.

### Exemples d'utilisation de la CLI

#### Authentification
```bash
dab auth --email user@example.com --password monmotdepasse
```

#### Statistiques générales
```bash
dab stats
```

#### Récupérer les cas de dengue
```bash
dab cas --date-debut 2024-01-01 --date-fin 2024-01-31 --region Centre --limit 20
```

#### Lister les alertes critiques actives
```bash
dab alertes --severity critical --status active --limit 5
```

#### Exporter les données au format CSV
```bash
dab export --format csv --output donnees_janvier.csv --date-debut 2024-01-01 --date-fin 2024-01-31
```

#### Exporter les alertes au format JSON
```bash
dab export --format json --output alertes.json --date-debut 2024-01-01 --date-fin 2024-01-31 --region Centre
```

#### Lister toutes les régions
```bash
dab regions
```

#### Lister les districts d’une région
```bash
dab districts --region Centre
```

#### Obtenir de l’aide sur une commande
```bash
dab export --help
```

#### Script d’automatisation (exemple Bash)
```bash
dab auth --email user@example.com --password monmotdepasse
dab export --format csv --output export.csv --date-debut 2024-01-01 --date-fin 2024-01-31
dab alertes --severity warning --limit 10 > alertes.txt
```

> **Remarque :** Si la commande `dab` n'est pas reconnue, vérifiez que votre environnement Python est bien activé et que le package a été installé avec `pip install dengsurvap-bf`.




---

## 🐛 Dépannage

Cette section propose des solutions aux erreurs courantes (authentification, connexion, validation) pour vous aider à diagnostiquer rapidement les problèmes.

### Erreurs courantes

#### Erreur d'authentification
Vérifiez vos identifiants et assurez-vous que l'utilisateur existe sur la plateforme.
```python
client.authenticate("email@example.com", "mot-de-passe")
```

#### Erreur de connexion
Vérifiez l'URL de l'API et votre connexion internet.
```python
client = AppiClient("https://api-correcte.com", "your-key")
```

#### Erreur de validation
Vérifiez le format des dates et la cohérence des paramètres envoyés.
```python
cas = client.get_cas_dengue(
    date_debut="2024-01-01",  # Format YYYY-MM-DD
    date_fin="2024-12-31"
)
```
---
---

## 🤝 Contribution

Nous accueillons toutes les contributions ! Que ce soit pour corriger un bug, ajouter une fonctionnalité, ou améliorer la documentation.

### Comment contribuer :

1. **Fork le projet** sur GitHub
2. **Créer une branche** pour votre fonctionnalité :
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. **Développer** en suivant les bonnes pratiques :
   - Ajoutez des tests pour les nouvelles fonctionnalités
   - Respectez le style de code existant
   - Documentez les nouvelles APIs
4. **Commiter** avec un message clair :
   ```bash
   git commit -m 'feat: add new export format support'
   ```
5. **Pousser** vers votre fork :
   ```bash
   git push origin feature/AmazingFeature
   ```
6. **Ouvrir une Pull Request** avec une description détaillée

### Bonnes pratiques :
- Testez vos modifications avant de soumettre
- Suivez les conventions de nommage existantes
- Ajoutez des exemples si vous modifiez l'API

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 📞 Support

- 📧 Email: yamsaid74@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/yamsaid/dengsurvap-bf/issues)
- 📖 Documentation: [ReadTheDocs](https://dengsurvap-bf.readthedocs.io/)
 
## 🔄 Changelog

### Version 0.1.0
- ✅ Client API de base
- ✅ Authentification JWT
- ✅ Gestion des alertes
- ✅ Export de données
- ✅ Outils d'analyse épidémiologique
- ✅ Documentation complète
- ✅ Tests unitaires

---