# Appi Dengue Client

Client Python officiel pour l'API de surveillance de la dengue Appi. Ce package permet d'accéder facilement aux données épidémiologiques, de gérer les alertes et d'effectuer des analyses avancées.

---

# 🚨 MIGRATION : Nouvelle API d'analyse avancée

Depuis la version 0.2.0, les méthodes `resume` et `resume_display` sont supprimées et remplacées par trois méthodes puissantes et flexibles :

- `client.resumer(...)` : résumé statistique et structurel de la base
- `client.graph_desc(...)` : visualisation descriptive (camemberts, barres, histogrammes)
- `client.evolution(...)` : analyse temporelle (par semaine/mois, par sous-groupes, avec taux de croissance)

**Migration rapide :**
- Remplacez :
    - `client.resume(...)` → `client.resumer(...)`
    - `client.resume_display(...)` → `client.graph_desc(...)` ou `client.evolution(...)`

**Exemples d'utilisation :**
```python
client.resumer(annee=2024, region="Centre", detail=True)
client.graph_desc(date_debut="2024-01-01", date_fin="2024-12-31", save_dir="./figures")
client.evolution(by="sexe", frequence="M", taux_croissance=True, max_graph=6)
```

---

## 🚀 Installation

Pour utiliser le client Appi Dengue, commencez par installer le package. L'installation standard suffit pour la plupart des usages, mais vous pouvez ajouter `[analysis]` pour les fonctionnalités avancées d'analyse et de visualisation.

```bash
pip install dengsurvap-bf[analysis]
```

---

## 📖 Guide rapide

### Connexion à l'API

Avant toute opération, il faut initialiser le client avec l'URL de l'API et (optionnellement) une clé API. L'authentification permet d'accéder aux fonctionnalités sécurisées.

```python
from dengsurvab import AppiClient

client = AppiClient(
    base_url="https://votre-api-appi.com",
    api_key="votre-clé-api"
)

client.authenticate("votre-email", "votre-mot-de-passe")
```

### Récupération et analyse des données

Utilisez les nouvelles méthodes pour obtenir un résumé, des graphiques ou une analyse temporelle. Tous les filtres (dates, région, district, etc.) sont disponibles en paramètres.

```python
# Résumé statistique et structurel
client.resumer(annee=2024, region="Centre", detail=True)

# Visualisation descriptive
client.graph_desc(date_debut="2024-01-01", date_fin="2024-12-31", save_dir="./figures")

# Analyse temporelle avancée
client.evolution(by="sexe", frequence="M", taux_croissance=True, max_graph=6)
```

### Description détaillée des nouvelles méthodes

#### `client.resumer(...)`
- Affiche un résumé enrichi : période de couverture, nombre d'observations, régions, districts, dernière mise à jour, statistiques quantitatives et qualitatives, détail des modalités.
- Principaux paramètres : `annee`, `region`, `district`, `date_debut`, `date_fin`, `detail`, `max_lignes`.

#### `client.graph_desc(...)`
- Génère des graphiques pour chaque variable d'intérêt (camemberts, barres, histogramme/boxplot pour l'âge).
- Principaux paramètres : `save_dir`, `max_modalites`, `boxplot_age`, `annee`, `region`, `district`, `date_debut`, `date_fin`.

#### `client.evolution(...)`
- Analyse l'évolution des variables cibles (issue, hospitalisation, resultat_test) par semaine ou mois, globalement ou par sous-groupes.
- Principaux paramètres : `by`, `frequence` ('W' ou 'M'), `taux_croissance`, `max_graph`, `annee`, `region`, `district`, `date_debut`, `date_fin`.

---

## 📚 Documentation complète

Pour plus de détails sur chaque méthode, consultez la docstring Python ou la documentation HTML générée.

- Les méthodes acceptent tous les filtres temporels et géographiques.
- Les résultats sont optimisés pour l'affichage console et la visualisation.
- Les exemples de scripts sont mis à jour dans le dossier `examples/`.

---

## 📝 Historique des changements

Voir [CHANGELOG.md](CHANGELOG.md) pour la liste complète des évolutions et instructions de migration.

---

## 💡 Astuces et bonnes pratiques

- Utilisez les filtres pour limiter la quantité de données analysées et accélérer les traitements.
- Les graphiques peuvent être sauvegardés dans un dossier pour intégration dans des rapports.
- La méthode `resumer` affiche automatiquement les informations générales, la période de couverture, et la dernière mise à jour (si disponible via l'API).

---

## 🔗 Ressources complémentaires

- [Documentation API Appi Dengue](https://api-bf-dengue-survey-production.up.railway.app/docs)
- [CHANGELOG.md](CHANGELOG.md)
- [Exemples de scripts](./examples/)