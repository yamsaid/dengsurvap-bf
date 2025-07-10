"""
Module d'analyse épidémiologique pour le client Appi Dengue

Ce module fournit des outils d'analyse avancés pour les données
de surveillance de la dengue.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta
from tabulate import tabulate
import matplotlib.pyplot as plt
import seaborn as sns
import os

from .exceptions import AnalysisError, APIError


class EpidemiologicalAnalyzer:
    """
    Analyseur épidémiologique pour les données de dengue.
    
    Cette classe fournit des méthodes d'analyse avancées pour
    les données de surveillance épidémiologique.
    """
    
    def __init__(self, client):
        """
        Initialise l'analyseur épidémiologique.
        
        Args:
            client: Instance du client Appi
        """
        self.client = client
        self.logger = logging.getLogger(__name__)
    
    def get_time_series(self,
                       date_debut: str,
                       date_fin: str,
                       frequency: str = "W",
                       region: str = "Toutes",
                       district: str = "Tous") -> pd.DataFrame:
        """
        Récupère une série temporelle des données.
        
        Args:
            date_debut: Date de début
            date_fin: Date de fin
            frequency: Fréquence (W: hebdomadaire, M: mensuel)
            region: Région
            district: District
            
        Returns:
            DataFrame avec la série temporelle
            
        Raises:
            AnalysisError: En cas d'erreur d'analyse
        """
        try:
            # Récupérer les données par période
            df = self.client.donnees_par_periode(
                date_debut=date_debut,
                date_fin=date_fin,
                region=region,
                district=district,
                frequence=frequency
            )
            
            if not df.empty:
                # Convertir les dates
                df['date_debut'] = pd.to_datetime(df['date_debut'])
                df['date_fin'] = pd.to_datetime(df['date_fin'])
                
                # Trier par date
                df = df.sort_values('date_debut')
            
            self.logger.info(f"Série temporelle générée: {len(df)} points")
            return df
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération de la série temporelle: {e}")
            raise AnalysisError(
                f"Impossible de générer la série temporelle: {e}",
                analysis_type="time_series"
            )
    
    def detect_anomalies(self, data: pd.DataFrame, method: str = "zscore") -> pd.DataFrame:
        """
        Détecte les anomalies dans les données.
        
        Args:
            data: DataFrame avec les données
            method: Méthode de détection (zscore, iqr, isolation_forest)
            
        Returns:
            DataFrame avec les anomalies détectées
            
        Raises:
            AnalysisError: En cas d'erreur d'analyse
        """
        try:
            if data.empty:
                return pd.DataFrame()
            
            anomalies = data.copy()
            
            if method == "zscore":
                # Détection par score Z
                for col in ['total_cas', 'cas_positifs', 'hospitalisations', 'deces']:
                    if col in anomalies.columns:
                        z_scores = np.abs((anomalies[col] - anomalies[col].mean()) / anomalies[col].std())
                        anomalies[f'{col}_anomaly'] = z_scores > 2
            
            elif method == "iqr":
                # Détection par IQR (Interquartile Range)
                for col in ['total_cas', 'cas_positifs', 'hospitalisations', 'deces']:
                    if col in anomalies.columns:
                        Q1 = anomalies[col].quantile(0.25)
                        Q3 = anomalies[col].quantile(0.75)
                        IQR = Q3 - Q1
                        lower_bound = Q1 - 1.5 * IQR
                        upper_bound = Q3 + 1.5 * IQR
                        anomalies[f'{col}_anomaly'] = (anomalies[col] < lower_bound) | (anomalies[col] > upper_bound)
            
            elif method == "isolation_forest":
                # Détection par Isolation Forest (nécessite scikit-learn)
                try:
                    from sklearn.ensemble import IsolationForest
                    
                    # Sélectionner les colonnes numériques
                    numeric_cols = ['total_cas', 'cas_positifs', 'hospitalisations', 'deces']
                    available_cols = [col for col in numeric_cols if col in anomalies.columns]
                    
                    if available_cols:
                        # Préparer les données
                        X = anomalies[available_cols].fillna(0)
                        
                        # Entraîner le modèle
                        iso_forest = IsolationForest(contamination=0.1, random_state=42)
                        anomalies['isolation_forest_anomaly'] = iso_forest.fit_predict(X) == -1
                
                except ImportError:
                    self.logger.warning("scikit-learn non disponible, utilisation de la méthode zscore")
                    return self.detect_anomalies(data, method="zscore")
            
            else:
                raise AnalysisError(f"Méthode de détection non supportée: {method}")
            
            self.logger.info(f"Anomalies détectées avec la méthode {method}")
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la détection d'anomalies: {e}")
            raise AnalysisError(
                f"Impossible de détecter les anomalies: {e}",
                analysis_type="anomaly_detection"
            )
    
    def calculate_rates(self,
                       date_debut: str,
                       date_fin: str,
                       region: Optional[str] = None,
                       district: Optional[str] = None) -> Dict[str, float]:
        """
        Calcule les taux épidémiologiques.
        
        Args:
            date_debut: Date de début
            date_fin: Date de fin
            region: Région
            district: District
            
        Returns:
            Dictionnaire avec les taux calculés
            
        Raises:
            AnalysisError: En cas d'erreur d'analyse
        """
        try:
            # Récupérer les données
            df = self.get_time_series(
                date_debut=date_debut,
                date_fin=date_fin,
                region=region or "Toutes",
                district=district or "Toutes"
            )
            
            if df.empty:
                return {}
            
            # Calculer les taux
            total_cas = df['total_cas'].sum()
            total_positifs = df['cas_positifs'].sum()
            total_hospitalisations = df['hospitalisations'].sum()
            total_deces = df['deces'].sum()
            
            rates = {
                'taux_positivite': (total_positifs / total_cas * 100) if total_cas > 0 else 0,
                'taux_hospitalisation': (total_hospitalisations / total_cas * 100) if total_cas > 0 else 0,
                'taux_letalite': (total_deces / total_cas * 100) if total_cas > 0 else 0,
                'total_cas': total_cas,
                'total_positifs': total_positifs,
                'total_hospitalisations': total_hospitalisations,
                'total_deces': total_deces
            }
            
            self.logger.info("Taux épidémiologiques calculés")
            return rates
            
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul des taux: {e}")
            raise AnalysisError(
                f"Impossible de calculer les taux: {e}",
                analysis_type="rate_calculation"
            )
    
    def trend_analysis(self, data: pd.DataFrame, column: str = "total_cas") -> Dict[str, Any]:
        """
        Analyse les tendances dans les données.
        
        Args:
            data: DataFrame avec les données
            column: Colonne à analyser
            
        Returns:
            Dictionnaire avec l'analyse des tendances
            
        Raises:
            AnalysisError: En cas d'erreur d'analyse
        """
        try:
            if data.empty or column not in data.columns:
                return {}
            
            # Calculer les statistiques de tendance
            values = data[column].dropna()
            
            if len(values) < 2:
                return {}
            
            # Régression linéaire simple
            x = np.arange(len(values))
            slope, intercept = np.polyfit(x, values, 1)
            
            # Calculer le coefficient de corrélation
            correlation = np.corrcoef(x, values)[0, 1]
            
            # Déterminer la direction de la tendance
            if slope > 0:
                trend_direction = "croissante"
            elif slope < 0:
                trend_direction = "décroissante"
            else:
                trend_direction = "stable"
            
            # Calculer la pente en pourcentage
            if values.mean() > 0:
                slope_percentage = (slope / values.mean()) * 100
            else:
                slope_percentage = 0
            
            analysis = {
                'slope': slope,
                'intercept': intercept,
                'correlation': correlation,
                'trend_direction': trend_direction,
                'slope_percentage': slope_percentage,
                'mean': values.mean(),
                'std': values.std(),
                'min': values.min(),
                'max': values.max()
            }
            
            self.logger.info(f"Analyse de tendance effectuée pour {column}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse de tendance: {e}")
            raise AnalysisError(
                f"Impossible d'analyser les tendances: {e}",
                analysis_type="trend_analysis"
            )
    
    def seasonal_analysis(self, data: pd.DataFrame, column: str = "total_cas") -> Dict[str, Any]:
        """
        Analyse la saisonnalité des données.
        
        Args:
            data: DataFrame avec les données
            column: Colonne à analyser
            
        Returns:
            Dictionnaire avec l'analyse de saisonnalité
            
        Raises:
            AnalysisError: En cas d'erreur d'analyse
        """
        try:
            if data.empty or column not in data.columns:
                return {}
            
            # Extraire le mois de chaque date
            data_copy = data.copy()
            data_copy['month'] = data_copy['date_debut'].dt.month
            
            # Calculer les moyennes par mois
            monthly_means = data_copy.groupby('month')[column].mean()
            
            # Identifier les mois de pic et de creux
            peak_month = monthly_means.idxmax()
            trough_month = monthly_means.idxmin()
            
            # Calculer l'amplitude saisonnière
            seasonal_amplitude = monthly_means.max() - monthly_means.min()
            
            # Calculer l'indice de saisonnalité
            overall_mean = data_copy[column].mean()
            seasonal_index = (monthly_means / overall_mean) * 100 if overall_mean > 0 else 0
            
            analysis = {
                'peak_month': int(peak_month),
                'trough_month': int(trough_month),
                'seasonal_amplitude': float(seasonal_amplitude),
                'seasonal_index': seasonal_index.to_dict(),
                'monthly_means': monthly_means.to_dict()
            }
            
            self.logger.info(f"Analyse de saisonnalité effectuée pour {column}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Erreur lors de l'analyse de saisonnalité: {e}")
            raise AnalysisError(
                f"Impossible d'analyser la saisonnalité: {e}",
                analysis_type="seasonal_analysis"
            )
    
    def forecast_next_week(self, data: pd.DataFrame, column: str = "total_cas") -> Dict[str, Any]:
        """
        Prédit les valeurs pour la semaine suivante.
        
        Args:
            data: DataFrame avec les données historiques
            column: Colonne à prédire
            
        Returns:
            Dictionnaire avec les prédictions
            
        Raises:
            AnalysisError: En cas d'erreur d'analyse
        """
        try:
            if data.empty or column not in data.columns:
                return {}
            
            # Utiliser une moyenne mobile simple pour la prédiction
            recent_values = data[column].tail(4).values  # 4 dernières semaines
            
            if len(recent_values) == 0:
                return {}
            
            # Prédiction basée sur la moyenne mobile
            prediction = np.mean(recent_values)
            
            # Calculer l'intervalle de confiance simple
            std_error = np.std(recent_values) / np.sqrt(len(recent_values))
            confidence_interval = (prediction - 1.96 * std_error, prediction + 1.96 * std_error)
            
            forecast = {
                'prediction': float(prediction),
                'confidence_interval_lower': float(confidence_interval[0]),
                'confidence_interval_upper': float(confidence_interval[1]),
                'method': 'moving_average',
                'last_values_used': len(recent_values)
            }
            
            self.logger.info(f"Prédiction générée pour {column}")
            return forecast
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la prédiction: {e}")
            raise AnalysisError(
                f"Impossible de générer la prédiction: {e}",
                analysis_type="forecasting"
            )


class DashboardGenerator:
    """
    Générateur de tableaux de bord épidémiologiques.
    
    Cette classe génère des rapports et tableaux de bord
    complets à partir des données de surveillance.
    """
    
    def __init__(self, client):
        """
        Initialise le générateur de tableaux de bord.
        
        Args:
            client: Instance du client Appi
        """
        self.client = client
        self.analyzer = EpidemiologicalAnalyzer(client)
        self.logger = logging.getLogger(__name__)
    
    def generate_report(self,
                       date_debut: str,
                       date_fin: str,
                       region: str = "Toutes",
                       district: str = "Toutes",
                       include_visualizations: bool = True) -> Dict[str, Any]:
        """
        Génère un rapport épidémiologique complet.
        
        Args:
            date_debut: Date de début
            date_fin: Date de fin
            region: Région
            district: District
            include_visualizations: Inclure les visualisations
            
        Returns:
            Rapport complet
            
        Raises:
            AnalysisError: En cas d'erreur
        """
        try:
            # Récupérer les données de base
            data = self.analyzer.get_time_series(
                date_debut=date_debut,
                date_fin=date_fin,
                region=region,
                district=district
            )
            
            # Calculer les taux
            rates = self.analyzer.calculate_rates(
                date_debut=date_debut,
                date_fin=date_fin,
                region=region,
                district=district
            )
            
            # Analyser les tendances
            trend_analysis = self.analyzer.trend_analysis(data, "total_cas")
            
            # Analyser la saisonnalité
            seasonal_analysis = self.analyzer.seasonal_analysis(data, "total_cas")
            
            # Prédiction pour la semaine suivante
            forecast = self.analyzer.forecast_next_week(data, "total_cas")
            
            # Détecter les anomalies
            anomalies = self.analyzer.detect_anomalies(data)
            
            # Compiler le rapport
            report = {
                'metadata': {
                    'date_debut': date_debut,
                    'date_fin': date_fin,
                    'region': region,
                    'district': district,
                    'generated_at': datetime.now().isoformat(),
                    'data_points': len(data)
                },
                'summary': {
                    'total_cas': rates.get('total_cas', 0),
                    'total_positifs': rates.get('total_positifs', 0),
                    'total_hospitalisations': rates.get('total_hospitalisations', 0),
                    'total_deces': rates.get('total_deces', 0)
                },
                'rates': rates,
                'trend_analysis': trend_analysis,
                'seasonal_analysis': seasonal_analysis,
                'forecast': forecast,
                'anomalies': {
                    'count': len(anomalies[anomalies.get('total_cas_anomaly', False)]),
                    'periods': anomalies[anomalies.get('total_cas_anomaly', False)][['date_debut', 'date_fin', 'total_cas']].to_dict('records')
                },
                'data': data.to_dict('records') if not data.empty else []
            }
            
            self.logger.info("Rapport épidémiologique généré")
            return report
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération du rapport: {e}")
            raise AnalysisError(
                f"Impossible de générer le rapport: {e}",
                analysis_type="report_generation"
            )
    
    def save_report(self, report: Dict[str, Any], file_path: str) -> bool:
        """
        Sauvegarde un rapport dans un fichier.
        
        Args:
            report: Rapport à sauvegarder
            file_path: Chemin du fichier
            
        Returns:
            True si la sauvegarde a réussi
        """
        try:
            import json
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Rapport sauvegardé dans {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde du rapport: {e}")
            return False 


class SyntheseBase:
    """
    Classe de synthèse avancée pour l'analyse descriptive, graphique et temporelle des données de dengue.

    Cette classe permet de :
      - Résumer la base de données (statistiques, structure, informations générales)
      - Générer des visualisations descriptives (camemberts, barres, histogrammes)
      - Analyser l'évolution temporelle (par semaine/mois, par sous-groupes, avec taux de croissance)

    Peut être utilisée directement ou via les méthodes du client Appi (client.resumer, client.graph_desc, client.evolution).

    Exemples d'utilisation :
    >>> synth = SyntheseBase(client=client)
    >>> synth.resumer(annee=2024, region="Centre")
    >>> synth.graph_desc(date_debut="2024-01-01", date_fin="2024-12-31")
    >>> synth.evolution(by="sexe", frequence="M", taux_croissance=True)

    Migration :
    - Remplacez :
        - client.resume(...) → client.resumer(...)
        - client.resume_display(...) → client.graph_desc(...) ou client.evolution(...)
    """
    def __init__(self, client=None, df: pd.DataFrame = None, colonne_date: str = None):
        self.client = client
        self.df = df.copy() if df is not None else None
        self.colonne_date = colonne_date or self._detect_colonne_date(df) if df is not None else None

    def _detect_colonne_date(self, df):
        # Liste des noms de colonnes de date courants
        date_columns = ['date_consultation', 'date', 'date_notification', 'date_creation', 'date_debut', 'date_fin']
        for col in date_columns:
            if col in df.columns:
                return col
        # Si aucune colonne standard trouvée, chercher par pattern
        for col in df.columns:
            if 'date' in col.lower():
                return col
        return None

    def _get_data(self, df=None, date_debut=None, date_fin=None, region=None, district=None, limit=None, annee=None):
        if df is not None:
            data_df = df
        elif self.client is not None:
            if annee is not None:
                date_debut = f"{annee}-01-01"
                date_fin = f"{annee}-12-31"
            elif date_debut is None and date_fin is None:
                current_year = datetime.now().year
                date_debut = f"{current_year}-01-01"
                date_fin = f"{current_year}-12-31"
            data_df = self.client.data(
                date_debut=date_debut,
                date_fin=date_fin,
                region=region,
                district=district,
                limit=limit
            )
        else:
            raise ValueError("Aucune source de données disponible. Fournissez un DataFrame ou un client.")
        return self._prepare_df(data_df)

    def _prepare_df(self, df):
        # Renommage pour compatibilité
        df = df.rename(columns={
            'date_consultation': 'date',
            'hospitalise': 'hospitalisation'
        })
        # Colonnes dérivées
        if 'age' in df.columns and 'tranche_age' not in df.columns:
            bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 200]
            labels = ['0-9', '10-19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', '80+']
            df['tranche_age'] = pd.cut(df['age'], bins=bins, labels=labels, right=False)
        # Détection et traitement de la colonne date
        date_col = self._detect_colonne_date(df)
        if date_col:
            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
            df['annee'] = df[date_col].dt.year
            df['mois'] = df[date_col].dt.month
        return df

    def resumer(self, df=None, detail: bool = False, annee: int = None, max_lignes: int = None, 
                date_debut: str = None, date_fin: str = None, region: str = None, 
                district: str = None, limit: int = None):
        """
        Affiche un résumé structuré et enrichi de la base de données.

        - Période de couverture, nombre d'observations, régions, districts, dernière mise à jour
        - Statistiques descriptives quantitatives et qualitatives
        - Option d'affichage détaillé des modalités

        Paramètres :
            df (pd.DataFrame, optionnel) : DataFrame à analyser (sinon récupéré via le client)
            detail (bool) : Afficher le détail des modalités catégorielles
            annee (int, optionnel) : Limiter le résumé à une année
            max_lignes (int, optionnel) : Limiter le nombre de lignes analysées
            date_debut/date_fin/region/district/limit : Filtres pour la récupération des données

        Exemple :
            client.resumer(annee=2024, region="Centre")
        """
        df = self._get_data(df, date_debut, date_fin, region, district, limit, annee)
        if annee:
            df = df[df['annee'] == annee]
        if max_lignes:
            df = df.head(max_lignes)
        date_col = self._detect_colonne_date(df)
        # Récupération de la dernière mise à jour via l'API si possible
        derniere_mise_a_jour = None
        if hasattr(self, 'client') and self.client is not None:
            try:
                date_ = self.client._make_request("GET", "/api/derniere-mise-a-jour")
                derniere_mise_a_jour = date_["derniere_mise_a_jour"] if date_["statut"] == True else "Date non trouvée"
            except Exception:
                derniere_mise_a_jour = "Date non trouvée"
        # Période de couverture
        periode_couverture = {}
        if 'date_debut' in df.columns and 'date_fin' in df.columns:
            periode_couverture = {
                "date_debut": df['date_debut'].min().strftime("%Y-%m-%d") if not df['date_debut'].isna().all() else None,
                "date_fin": df['date_fin'].max().strftime("%Y-%m-%d") if not df['date_fin'].isna().all() else None,
                "duree_jours": (df['date_fin'].max() - df['date_debut'].min()).days if not df['date_debut'].isna().all() and not df['date_fin'].isna().all() else 0
            }
        elif date_col and date_col in df.columns:
            periode_couverture = {
                "date_debut": df[date_col].min().strftime("%Y-%m-%d") if not df[date_col].isna().all() else None,
                "date_fin": df[date_col].max().strftime("%Y-%m-%d") if not df[date_col].isna().all() else None,
                "duree_jours": (df[date_col].max() - df[date_col].min()).days if not df[date_col].isna().all() else 0
            }
        else:
            periode_couverture = {"date_debut": None, "date_fin": None, "duree_jours": 0}
        # Informations générales
        total_enregistrements = len(df)
        regions_couvertes = df['region'].nunique() if 'region' in df.columns else 0
        districts_couverts = df['district'].nunique() if 'district' in df.columns else 0
        print("\n==============================")
        print("  🗂️  Informations générales  ")
        print("==============================")
        print(f"📅 Période de couverture : {periode_couverture['date_debut']} → {periode_couverture['date_fin']}  (⏳ {periode_couverture['duree_jours']} jours)")
        print(f"🧾 Nombre d'observations : {total_enregistrements}")
        print(f"🗺️  Nombre de régions : {regions_couvertes}")
        print(f"🏘️  Nombre de districts : {districts_couverts}")
        print(f"🕒 Dernière mise à jour : {derniere_mise_a_jour if derniere_mise_a_jour else 'N/A'}")
        quanti = df.select_dtypes(include=[np.number])
        if not quanti.empty:
            desc = quanti.describe(percentiles=[.25, .5, .75]).T
            desc['manquantes'] = quanti.isna().sum()
            desc = desc.rename(columns={
                '25%': 'Q1', '50%': 'Médiane', '75%': 'Q3',
                'mean': 'Moyenne', 'std': 'Ecart-type', 'min': 'Min', 'max': 'Max', 'count': 'N'
            })
            print("\n=== Variables quantitatives ===")
            print(tabulate(desc[['Min', 'Max', 'Moyenne', 'Ecart-type', 'Q1', 'Médiane', 'Q3', 'manquantes']].fillna(''), headers='keys', tablefmt='github'))
        quali = df.select_dtypes(include=['object', 'category'])
        if not quali.empty:
            rows = []
            for col in quali.columns:
                if col == date_col:
                    continue
                mode = quali[col].mode().iloc[0] if not quali[col].mode().empty else 'N/A'
                n_modalites = quali[col].nunique(dropna=True)
                n_manquantes = quali[col].isna().sum()
                rows.append({
                    'Variable': col,
                    'Type': str(quali[col].dtype),
                    'Mode': mode,
                    'Nb modalités': n_modalites,
                    'Manquantes': n_manquantes
                })
            print("\n=== Variables qualitatives ===")
            print(tabulate(rows, headers='keys', tablefmt='github'))
            if detail:
                print("\n=== Détail des modalités (optionnel) ===")
                for col in quali.columns:
                    if col == date_col:
                        continue
                    print(f"{col} :")
                    print(tabulate(quali[col].value_counts().reset_index().rename(columns={'index': 'Modalité', col: 'N'}), headers='keys', tablefmt='github'))

    def graph_desc(self, df=None, save_dir: str = None, max_modalites: int = 15, boxplot_age: bool = False,
                   date_debut: str = None, date_fin: str = None, region: str = None, 
                   district: str = None, limit: int = None, annee: int = None):
        """
        Génère des graphiques descriptifs pour chaque variable d'intérêt de la base.

        - Camemberts pour les variables à peu de modalités
        - Barres pour les variables à nombreuses modalités
        - Histogramme et boxplot pour l'âge
        - Filtres temporels et géographiques disponibles

        Paramètres :
            df (pd.DataFrame, optionnel) : DataFrame à analyser (sinon récupéré via le client)
            save_dir (str, optionnel) : Dossier où sauvegarder les graphiques
            max_modalites (int) : Nombre max de modalités à afficher pour les barres
            boxplot_age (bool) : Afficher aussi un boxplot pour l'âge
            date_debut/date_fin/region/district/limit/annee : Filtres pour la récupération des données

        Exemple :
            client.graph_desc(date_debut="2024-01-01", date_fin="2024-12-31")
        """
        df = self._get_data(df, date_debut, date_fin, region, district, limit, annee)
        if annee:
            df = df[df['annee'] == annee]
        sns.set_theme(style="whitegrid")
        variables_categ = [
            ('issue', 'Camembert'),
            ('hospitalisation', 'Camembert'),
            ('serotype', 'Camembert'),
            ('resultat_test', 'Camembert'),
            ('sexe', 'Camembert'),
            ('district', 'Barres'),
            ('region', 'Barres')
        ]
        for var, typ in variables_categ:
            if var not in df.columns:
                print(f"[Info] Variable '{var}' absente de la base.")
                continue
            vc = df[var].value_counts(dropna=False)
            if typ == 'Barres':
                if len(vc) > max_modalites:
                    autres = vc[max_modalites:].sum()
                    vc = vc[:max_modalites]
                    vc['Autres'] = autres
                plt.figure(figsize=(10, 5))
                ax = sns.barplot(x=vc.index.astype(str), y=vc.values, palette="viridis")
                plt.title(f"Répartition de {var}")
                plt.xlabel(var)
                plt.ylabel("Nombre d'observations")
                plt.xticks(rotation=45, ha='right')
                if len(vc) <= 10:
                    for i, v in enumerate(vc.values):
                        ax.text(i, v + max(vc.values)*0.01, str(v), ha='center', va='bottom', fontsize=9)
                plt.tight_layout()
            else:
                plt.figure(figsize=(6, 6))
                labels = [str(x) for x in vc.index]
                patches, texts, autotexts = plt.pie(vc.values, labels=labels, autopct='%1.1f%%', startangle=90, colors=sns.color_palette('pastel'))
                plt.title(f"Répartition de {var}")
                for autotext in autotexts:
                    autotext.set_color('black')
                plt.tight_layout()
            if save_dir:
                os.makedirs(save_dir, exist_ok=True)
                plt.savefig(os.path.join(save_dir, f"desc_{var}.png"), bbox_inches='tight')
                plt.close()
            else:
                plt.show()
        if 'age' in df.columns:
            plt.figure(figsize=(8, 5))
            sns.histplot(df['age'].dropna(), bins=20, kde=True, color='skyblue')
            plt.title("Distribution de l'âge")
            plt.xlabel("Âge")
            plt.ylabel("Nombre d'observations")
            plt.tight_layout()
            if save_dir:
                os.makedirs(save_dir, exist_ok=True)
                plt.savefig(os.path.join(save_dir, "desc_age_hist.png"), bbox_inches='tight')
                plt.close()
            else:
                plt.show()
            if boxplot_age:
                plt.figure(figsize=(6, 4))
                sns.boxplot(x=df['age'].dropna(), color='lightcoral')
                plt.title("Boxplot de l'âge")
                plt.xlabel("Âge")
                plt.tight_layout()
                if save_dir:
                    plt.savefig(os.path.join(save_dir, "desc_age_boxplot.png"), bbox_inches='tight')
                    plt.close()
                else:
                    plt.show()

    def evolution(self, df=None, by=None, save_dir=None, date_debut: str = None, date_fin: str = None, 
                  region: str = None, district: str = None, limit: int = None, annee: int = None,
                  frequence: str = "W", taux_croissance: bool = True, max_graph: int = None):
        """
        Analyse l'évolution des variables cibles (issue, hospitalisation, resultat_test) par période (semaine ou mois),
        globalement ou par sous-groupes (ex: sexe, région, district, etc.).

        - Courbes d'évolution par semaine ou par mois
        - Analyse par sous-groupes (by)
        - Affichage optionnel des taux de croissance (absolu et en %)
        - Limitation du nombre de graphiques (max_graph)

        Paramètres :
            df (pd.DataFrame, optionnel) : DataFrame à analyser (sinon récupéré via le client)
            by (str ou list de str, optionnel) : Variable(s) de sous-groupe pour l'analyse croisée
            save_dir (str, optionnel) : Dossier où sauvegarder les graphiques
            frequence (str) : 'W' pour hebdomadaire, 'M' pour mensuelle
            taux_croissance (bool) : Afficher les graphiques de taux de croissance
            max_graph (int, optionnel) : Nombre maximum de graphiques à afficher
            date_debut/date_fin/region/district/limit/annee : Filtres pour la récupération des données

        Exemple :
            client.evolution(by="sexe", frequence="M", taux_croissance=True)
        """
        import matplotlib.pyplot as plt
        import seaborn as sns
        import os

        # Configuration du style professionnel
        plt.style.use('seaborn-v0_8-whitegrid')
        sns.set_palette("husl")
        
        # Configuration des couleurs professionnelles
        colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#6B5B95', '#88B04B']
        
        df = self._get_data(df, date_debut, date_fin, region, district, limit, annee)
        if annee:
            df = df[df['annee'] == annee]
        
        cibles = ['issue', 'hospitalisation', 'resultat_test']
        date_col = self._detect_colonne_date(df)
        if not date_col:
            print(f"[Erreur] Aucune colonne de date trouvée. Colonnes disponibles: {list(df.columns)}")
            print("Colonnes de date attendues: date_consultation, date, date_notification, etc.")
            return
        if date_col not in df.columns:
            print(f"[Erreur] Colonne de date '{date_col}' non trouvée dans le DataFrame.")
            return
            
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        if frequence == "W":
            df['periode'] = df[date_col].dt.to_period('W').apply(lambda r: r.start_time)
            freq_label = 'Hebdomadaire'
        elif frequence == "M":
            df['periode'] = df[date_col].dt.to_period('M').apply(lambda r: r.start_time)
            freq_label = 'Mensuel'
        else:
            print("[Erreur] frequence doit être 'W' (hebdomadaire) ou 'M' (mensuelle)")
            return
            
        if by is not None and not isinstance(by, list):
            by = [by]
            
        graph_count = 0
        
        for cible in cibles:
            if cible not in df.columns:
                print(f"[Info] Variable cible '{cible}' absente de la base.")
                continue
                
            group_cols = ['periode'] + (by if by else [])
            ct = df.groupby(group_cols)[cible].value_counts().unstack(fill_value=0).sort_index()
            croissance = ct.diff().fillna(0)
            croissance_pct = ct.pct_change().replace([np.inf, -np.inf], np.nan).fillna(0) * 100
            
            for i, modalite in enumerate(ct.columns):
                if max_graph is not None and graph_count >= max_graph:
                    return
                    
                # Graphique d'évolution - Style professionnel
                fig, ax = plt.subplots(figsize=(14, 8))
                
                if by:
                    for j, (key, subdf) in enumerate(ct[modalite].groupby(level=by)):
                        label = str(key) if isinstance(key, tuple) else key
                        color = colors[j % len(colors)]
                        ax.plot(subdf.index.get_level_values('periode'), subdf.values, 
                               marker='o', linewidth=3, markersize=8, label=label, color=color)
                else:
                    ax.plot(ct.index, ct[modalite], marker='o', linewidth=3, markersize=8, 
                           label=modalite, color=colors[0])
                
                # Amélioration du style
                ax.set_title(f"Évolution {freq_label} - {cible.title()} ({modalite})" + 
                           (f" par {', '.join(by)}" if by else ""), 
                           fontsize=16, fontweight='bold', pad=20)
                ax.set_xlabel(f"Période ({freq_label.lower()})", fontsize=12, fontweight='bold')
                ax.set_ylabel("Nombre d'observations", fontsize=12, fontweight='bold')
                ax.tick_params(axis='both', which='major', labelsize=10)
                ax.grid(True, alpha=0.3, linestyle='--')
                ax.legend(title=by[0] if by else cible.title(), fontsize=10, framealpha=0.9)
                
                # Rotation des labels x pour une meilleure lisibilité
                plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
                
                # Ajout d'une grille secondaire
                ax.grid(True, alpha=0.2, which='minor')
                ax.minorticks_on()
                
                plt.tight_layout()
                
                if save_dir:
                    os.makedirs(save_dir, exist_ok=True)
                    fname = f"evol_{cible}_{modalite}_{freq_label}" + (f"_par_{'_'.join(by)}" if by else "") + ".png"
                    plt.savefig(os.path.join(save_dir, fname), bbox_inches='tight', dpi=300)
                    plt.close()
                else:
                    plt.show()
                    
                graph_count += 1
                if max_graph is not None and graph_count >= max_graph:
                    return
                    
                if taux_croissance:
                    # Graphique de croissance absolue - Style professionnel
                    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
                    
                    # Croissance absolue
                    if by:
                        for j, (key, subdf) in enumerate(croissance[modalite].groupby(level=by)):
                            label = str(key) if isinstance(key, tuple) else key
                            color = colors[j % len(colors)]
                            bars = ax1.bar(subdf.index.get_level_values('periode'), subdf.values, 
                                          label=label, alpha=0.8, color=color, edgecolor='black', linewidth=0.5)
                    else:
                        bars = ax1.bar(croissance.index, croissance[modalite], 
                                      color=colors[0], alpha=0.8, edgecolor='black', linewidth=0.5)
                    
                    ax1.set_title(f"Taux de Croissance Absolu - {cible.title()} ({modalite})" + 
                                (f" par {', '.join(by)}" if by else ""), 
                                fontsize=14, fontweight='bold', pad=20)
                    ax1.set_ylabel("Croissance absolue", fontsize=12, fontweight='bold')
                    ax1.grid(True, alpha=0.3, linestyle='--')
                    ax1.legend(title=by[0] if by else cible.title(), fontsize=10, framealpha=0.9)
                    ax1.tick_params(axis='both', which='major', labelsize=10)
                    plt.setp(ax1.get_xticklabels(), rotation=45, ha='right')
                    
                    # Croissance en pourcentage
                    if by:
                        for j, (key, subdf) in enumerate(croissance_pct[modalite].groupby(level=by)):
                            label = str(key) if isinstance(key, tuple) else key
                            color = colors[j % len(colors)]
                            bars = ax2.bar(subdf.index.get_level_values('periode'), subdf.values, 
                                          label=label, alpha=0.8, color=color, edgecolor='black', linewidth=0.5)
                    else:
                        bars = ax2.bar(croissance_pct.index, croissance_pct[modalite], 
                                      color=colors[1], alpha=0.8, edgecolor='black', linewidth=0.5)
                    
                    ax2.set_title(f"Taux de Croissance en Pourcentage - {cible.title()} ({modalite})" + 
                                (f" par {', '.join(by)}" if by else ""), 
                                fontsize=14, fontweight='bold', pad=20)
                    ax2.set_xlabel(f"Période ({freq_label.lower()})", fontsize=12, fontweight='bold')
                    ax2.set_ylabel("Croissance (%)", fontsize=12, fontweight='bold')
                    ax2.grid(True, alpha=0.3, linestyle='--')
                    ax2.legend(title=by[0] if by else cible.title(), fontsize=10, framealpha=0.9)
                    ax2.tick_params(axis='both', which='major', labelsize=10)
                    plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')
                    
                    # Ajout d'une ligne de référence à zéro pour le pourcentage
                    ax2.axhline(y=0, color='red', linestyle='--', alpha=0.7, linewidth=2)
                    
                    plt.tight_layout()
                    
                    if save_dir:
                        fname = f"croissance_{cible}_{modalite}_{freq_label}" + (f"_par_{'_'.join(by)}" if by else "") + ".png"
                        plt.savefig(os.path.join(save_dir, fname), bbox_inches='tight', dpi=300)
                        plt.close()
                    else:
                        plt.show()
                        
                    graph_count += 1
                    if max_graph is not None and graph_count >= max_graph:
                        return

if __name__ == "__main__":
    # Exemple d'utilisation
    import pandas as pd
    from dengsurvab.client import AppiClient
    
    # Option 1: Avec un DataFrame existant
    data = {
        'date_consultation': pd.date_range('2024-01-01', periods=100, freq='D'),
        'region': ['A', 'B'] * 50,
        'district': ['X', 'Y'] * 50,
        'age': np.random.randint(0, 90, 100),
        'sexe': np.random.choice(['M', 'F'], 100),
        'resultat_test': np.random.choice(['positif', 'negatif'], 100),
        'hospitalise': np.random.choice(['Oui', 'Non'], 100),
        'issue': np.random.choice(['Guéri', 'En cours'], 100)
    }
    df = pd.DataFrame(data)
    
    # Créer une instance avec un DataFrame
    synth = SyntheseBase(df=df)
    synth.resumer(detail=True)
    synth.graph_desc()
    synth.evolution(by='sexe')
    
    # Option 2: Avec un client (nécessite une connexion API)
    # client = AppiClient()
    # synth = SyntheseBase(client=client)
    # synth.resumer(annee=2024, region="Centre")
    # synth.graph_desc(date_debut="2024-01-01", date_fin="2024-12-31")
    # synth.evolution(by=['region', 'sexe'], annee=2024)
    
    # Option 3: Mélange - client pour récupérer, puis analyse locale
    # client = AppiClient()
    # df_api = client.data(date_debut="2024-01-01", date_fin="2024-12-31", region="Centre")
    # synth = SyntheseBase(df=df_api)
    # synth.resumer(detail=True)
    # synth.graph_desc(save_dir="./figures")
    # synth.evolution(by='sexe', save_dir="./figures_evolution") 