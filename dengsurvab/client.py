"""
Client principal pour l'API Appi Dengue

Ce module contient la classe AppiClient qui fournit une interface
complète pour interagir avec l'API de surveillance de la dengue.
"""

import os
import requests
import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date, timedelta
import json
import logging
from urllib.parse import urljoin

from .models import (
    CasDengue, SoumissionDonnee, AlertLog, SeuilAlert, User,
    ValidationCasDengue, IndicateurHebdo, Statistiques,
    LoginRequest, RegisterRequest, AlertConfigRequest, DonneesHebdomadaires
)
from .exceptions import (
    AppiException, AuthenticationError, APIError, ValidationError,
    RateLimitError, ConnectionError, create_exception_from_response, AnalysisError
)
from .auth import AuthManager
from .alerts import AlertManager
from .export import DataExporter
from .analytics import EpidemiologicalAnalyzer, SyntheseBase

os.environ['APPI_API_URL'] = "https://api-bf-dengue-survey-production.up.railway.app/"

class AppiClient:
    """
    Client principal pour l'API de surveillance de la dengue Appi.
    
    Cette classe fournit une interface complète pour accéder aux données
    épidémiologiques, gérer les alertes et effectuer des analyses.
    """
    
    def __init__(self, 
                 
                 base_url: str = "https://api-bf-dengue-survey-production.up.railway.app/"
                                    , 
                 api_key: Optional[str] = None,
                 timeout: int = 30,
                 retry_attempts: int = 3,
                 retry_delay: float = 1.0,
                 debug: bool = False):
        """
        Initialise le client Appi.
        
        Args:
            base_url: URL de base de l'API
            api_key: Clé API optionnelle
            timeout: Timeout des requêtes en secondes
            retry_attempts: Nombre de tentatives en cas d'échec
            retry_delay: Délai entre les tentatives en secondes
            debug: Mode debug pour les logs détaillés
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.debug = debug
        
        # Configuration du logging
        if debug:
            logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(__name__)
        
        # Session HTTP avec configuration
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'dengsurvap-bf/0.1.0',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
        
        if api_key:
            self.session.headers.update({'Authorization': f'Bearer {api_key}'})
        
        # Modules spécialisés
        self.auth = AuthManager(self)
        self.alerts = AlertManager(self)
        self.exporter = DataExporter(self)
        self.analyzer = EpidemiologicalAnalyzer(self)
        
        # Cache pour les requêtes fréquentes
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
        
    @classmethod
    def from_env(cls) -> 'AppiClient':
        """
        Crée une instance du client à partir des variables d'environnement.
        
        Returns:
            Instance du client configurée
            
        Raises:
            ConfigurationError: Si les variables requises sont manquantes
        """
        base_url = os.getenv('APPI_API_URL')
        api_key = os.getenv('APPI_API_KEY')
        debug = os.getenv('APPI_DEBUG', 'false').lower() == 'true'
        
        if not base_url:
            raise AppiException("Variable d'environnement APPI_API_URL requise")
        
        return cls(
            base_url=base_url,
            api_key=api_key,
            debug=debug
        )
    
    def _make_request(self, 
                     method: str, 
                     endpoint: str, 
                     params: Optional[Dict[str, Any]] = None,
                     data: Optional[Dict[str, Any]] = None,
                     files: Optional[Dict[str, Any]] = None,
                     headers: Optional[Dict[str, str]] = None,
                     use_form_data: bool = False) -> Dict[str, Any]:
        """
        Effectue une requête HTTP vers l'API avec gestion d'erreurs et retry.
        
        Args:
            method: Méthode HTTP (GET, POST, etc.)
            endpoint: Endpoint de l'API
            params: Paramètres de requête
            data: Données à envoyer
            files: Fichiers à envoyer
            headers: Headers HTTP supplémentaires
            use_form_data: Si True, utilise data au lieu de json pour l'envoi
            
        Returns:
            Données de la réponse
            
        Raises:
            APIError: En cas d'erreur de l'API
            ConnectionError: En cas d'erreur de connexion
            AuthenticationError: En cas d'erreur d'authentification
        """
        url = urljoin(self.base_url, endpoint)
        
        # Headers personnalisés
        request_headers = headers or {}
        
        # Tentatives avec retry
        for attempt in range(self.retry_attempts):
            try:
                self.logger.debug(f"Requête {method} vers {url} (tentative {attempt + 1})")
                
                # Préparer les paramètres de la requête
                request_kwargs = {
                    'method': method,
                    'url': url,
                    'params': params,
                    'files': files,
                    'headers': request_headers,
                    'timeout': self.timeout
                }
                
                # Choisir entre json et data selon le paramètre use_form_data
                if data is not None:
                    if use_form_data:
                        request_kwargs['data'] = data
                        # Retirer le Content-Type de la session pour permettre à requests de le définir automatiquement
                        if 'Content-Type' in self.session.headers:
                            del self.session.headers['Content-Type']
                    else:
                        request_kwargs['json'] = data
                
                response = self.session.request(**request_kwargs)
                
                # Gestion des codes de statut
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 204:
                    return {}
                else:
                    # Créer l'exception appropriée
                    try:
                        error_data = response.json()
                    except json.JSONDecodeError:
                        error_data = {"detail": response.text}
                    
                    exception = create_exception_from_response(
                        response.status_code, error_data
                    )
                    raise exception
                    
            except requests.exceptions.RequestException as e:
                if attempt == self.retry_attempts - 1:
                    raise ConnectionError(
                        f"Erreur de connexion après {self.retry_attempts} tentatives: {e}",
                        url=url,
                        timeout=self.timeout
                    )
                
                self.logger.warning(f"Tentative {attempt + 1} échouée: {e}")
                import time
                time.sleep(self.retry_delay)
        
        raise ConnectionError("Toutes les tentatives ont échoué")
    
    # ==================== AUTHENTIFICATION ====================
    
    def authenticate(self, email: str, password: str) -> Dict[str, Any]:
        """
        Authentifie l'utilisateur et récupère un token JWT.
        
        Args:
            email: Adresse email
            password: Mot de passe
            
        Returns:
            Informations d'authentification
            
        Raises:
            AuthenticationError: En cas d'échec d'authentification
        """
        return self.auth.authenticate(email, password)
    
    def logout(self) -> bool:
        """
        Déconnecte l'utilisateur.
        
        Returns:
            True si la déconnexion a réussi
        """
        return self.auth.logout()
    
    def get_profile(self) -> User:
        """
        Récupère le profil de l'utilisateur connecté.
        
        Returns:
            Informations du profil utilisateur
        """
        return self.auth.get_profile()
    
    def update_profile(self, **kwargs) -> User:
        """
        Met à jour le profil utilisateur.
        
        Args:
            **kwargs: Champs à mettre à jour
            
        Returns:
            Profil utilisateur mis à jour
        """
        return self.auth.update_profile(**kwargs)
    
    # ==================== DONNÉES DE DENGUE ====================
     
    def data(self,
            date_debut: Optional[str] = None,
            date_fin: Optional[str] = None,
            region: Optional[str] = None,
            district: Optional[str] = None,
            limit: Optional[int] = None,
            page: Optional[int] = None,
            full: bool = False) -> pd.DataFrame:
        """
        Récupère les données de dengue sous forme de DataFrame.
        
        Args:
            date_debut: Date de début (format YYYY-MM-DD)
            date_fin: Date de fin (format YYYY-MM-DD)
            region: Région à filtrer
            district: District à filtrer
            limit: Nombre maximum de résultats
            page: Page à récupérer (pour la pagination)
            full: Si True, récupère toute la base (pagination automatique)
        
        Returns:
            DataFrame avec les données de dengue
        """
        if full:
            # Pagination automatique pour tout charger
            all_data = []
            page = 1
            while True:
                df = self.data(date_debut=date_debut, date_fin=date_fin, region=region, district=district, limit=1000, page=page, full=False)
                if df.empty:
                    break
                all_data.append(df)
                if len(df) < 1000:
                    break
                page += 1
            if all_data:
                return pd.concat(all_data, ignore_index=True)
            else:
                return pd.DataFrame()
        # --- Comportement normal ---
        params = {}
        if date_debut:
            params['date_debut'] = date_debut
        if date_fin:
            params['date_fin'] = date_fin
        if region:
            params['region'] = region
        if district:
            params['district'] = district
        if limit:
            params['limit'] = limit
        if page:
            params['page'] = page
        
        data = self._make_request("GET", "/api/data", params=params)
        
        cas_list = data if isinstance(data, list) else data.get('data', [])
        
        # Convertir en DataFrame
        if cas_list:
            # Créer une liste de dictionnaires
            data_list = []
            for cas in cas_list:
                # cas_dict = cas.model_dump()
                # Convertir les dates en string pour pandas
                if cas.get('date_consultation'):
                    cas['date_consultation'] = str(cas['date_consultation'])
                data_list.append(cas)
            
            df = pd.DataFrame(data_list)
            
            # Convertir les colonnes de dates
            if 'date_consultation' in df.columns:
                df['date_consultation'] = pd.to_datetime(df['date_consultation'], errors='coerce')
            
            return df
        else:
            # Retourner un DataFrame vide avec les colonnes attendues
            return pd.DataFrame(columns=[
                'idCas', 'date_consultation', 'region', 'district', 'sexe', 'age',
                'resultat_test', 'serotype', 'hospitalise', 'issue', 'id_source'
            ])

    def get_cas_dengue(self,
                       annee : int = date.today().year,
                       mois : int = date.today().month,
                       region : Optional[str] = None,
                       district : Optional[str] = None,
                       ) -> pd.DataFrame:
        """
        Récupère les données hebdomadaires de dengue.
        
        Args:
            annee: Année des données (défaut: année courante)
            mois: Mois des données (défaut: mois courant)
            region: Région pour filtrer les données
            district: District pour filtrer les données
            
        Returns:
            DataFrame pandas contenant les données hebdomadaires
        """
        params = {}
        if annee:
            params['annee'] = annee
        if mois:
            params['mois'] = mois
        if region:
            params['region'] = region
        if district:
            params['district'] = district
        
        data = self._make_request("GET", "/api/data/hebdomadaires", params=params)
        
        # Conversion directe en DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        else:
            df = pd.DataFrame(data.get('data', []))
        
        # Si le DataFrame n'est pas vide, on peut ajouter des colonnes calculées
        if not df.empty:
            # Ajouter des colonnes calculées si les données existent
            if 'positifs' in df.columns and 'total_cas' in df.columns:
                df['taux_positivite'] = (df['positifs'] / df['total_cas'] * 100).round(2)
            
            if 'hospitalises' in df.columns and 'total_cas' in df.columns:
                df['taux_hospitalisation'] = (df['hospitalises'] / df['total_cas'] * 100).round(2)
            
            if 'deces' in df.columns and 'total_cas' in df.columns:
                df['taux_letalite'] = (df['deces'] / df['total_cas'] * 100).round(2)
        
        return df
    
    
    def add_cas_dengue(self, cas_list: List[ValidationCasDengue]) -> Dict[str, Any]:
        """
        Ajoute une liste de cas de dengue.
        
        Args:
            cas_list: Liste des cas à ajouter
            
        Returns:
            Résultat de l'ajout
        """
        try:
            data = [cas.model_dump() for cas in cas_list]
        except Exception as e:
            data = cas_list
            
        return self._make_request("POST", "/add-listCasDengue-json/", data=data)
    
    def get_stats(self) -> Statistiques:
        """
        Récupère les statistiques générales.
        
        Returns:
            Statistiques du système
        """
        data = self._make_request("GET", "/api/stats")
        
        # Transformer les données de l'API au format attendu par le modèle Statistiques
        # L'API retourne une structure imbriquée, on extrait les données de l'année en cours
        annee_courante = data.get('annee_en_cours', {})
        
        # Créer un dictionnaire au format attendu par le modèle Statistiques
        stats_data = {
            'total_cas': annee_courante.get('total_cases', 0),
            'total_positifs': annee_courante.get('total_positives', 0),
            'total_hospitalisations': annee_courante.get('total_hospitalized', 0),
            'total_deces': annee_courante.get('total_deaths', 0),
            'regions_actives': [annee_courante.get('top_region', '')] if annee_courante.get('top_region') else [],
            'districts_actifs': [annee_courante.get('top_district', '')] if annee_courante.get('top_district') else [],
            'derniere_mise_a_jour': datetime.now()  # L'API ne fournit pas cette info, on utilise maintenant
        }
        
        return Statistiques(**stats_data)
    
    def get_regions(self) -> List[str]:
        """
        Récupère la liste des régions.
        
        Returns:
            Liste des régions disponibles
        """
        data = self._make_request("GET", "/api/regions")
        return data if isinstance(data, list) else data.get('regions', [])
    
    def get_districts(self, region: Optional[str] = None) -> List[str]:
        """
        Récupère la liste des districts.
        
        Args:
            region: Région pour filtrer les districts
            
        Returns:
            Liste des districts
        """
        params = {}
        if region:
            params['region'] = region
        
        data = self._make_request("GET", "/api/districts", params=params)
        return data if isinstance(data, list) else data.get('districts', [])
    
    def alertes(self,
                      
            limit: int = 100,
            severity: Optional[str] = None,
            status: Optional[str] = None) -> pd.DataFrame:
        """
        Exporte les alertes dans différents formats.
        
        Args:
            format: Format d'export (csv, json, xlsx)
            limit: Nombre maximum d'alertes
            severity: Sévérité
            status: Statut
            
        Returns:
            Alertes exportées en bytes
        """
        return self.exporter.alertes_to_dataframe(
            #format=format,
            limit=limit,
            severity=severity,
            status=status
        )
    
    # ==================== INDICATEURS ÉPIDÉMIOLOGIQUES ====================
    
    def donnees_par_periode(self,
        date_debut: Optional[str] = None,
        date_fin: Optional[str] = None,
        region: Optional[str] = None,
        district: Optional[str] = None,
        frequence: str = "W"
        ) -> pd.DataFrame:
        """
        Récupère les indicateurs épidémiologiques par période et retourne un DataFrame pandas.
        
        Args:
            date_debut: Date de début
            date_fin: Date de fin
            region: Région
            district: District
            frequence: Fréquence (W: hebdomadaire, M: mensuel)
        Returns:
            DataFrame pandas des indicateurs épidémiologiques
        """
        params = {
            'date_debut': date_debut,
            'date_fin': date_fin,
            'region': region,
            'district': district,
            'frequence': frequence
        }
        data = self._make_request("GET", "/api/time-series", params=params)
        import pandas as pd
        df = pd.DataFrame(data)
        return df
    
    def get_taux_hospitalisation(self,
                                date_debut: str,
                                date_fin: str,
                                region: str = "Toutes",
                                district: str = "Toutes") -> pd.DataFrame:
        """
        Récupère le taux d'hospitalisation et retourne un DataFrame pandas.
        
        Args:
            date_debut: Date de début
            date_fin: Date de fin
            region: Région
            district: District
            
        Returns:
            DataFrame pandas avec les taux d'hospitalisation
        """
        params = {
            'date_debut': date_debut,
            'date_fin': date_fin
        }
        
        if region != "Toutes":
            params['region'] = region
        if district != "Toutes":
            params['district'] = district
        
        data = self._make_request("GET", "/indicateurs/taux-hospitalisation", params=params)
        import pandas as pd
        df = pd.DataFrame(data if isinstance(data, list) else [data])
        return df
    
    def get_taux_letalite(self,
                          date_debut: str,
                          date_fin: str,
                          niveau: Optional[str] = None,
                          serotype: Optional[str] = None) -> pd.DataFrame:
        """
        Récupère le taux de létalité et retourne un DataFrame pandas.
        
        Args:
            date_debut: Date de début
            date_fin: Date de fin
            niveau: Niveau d'agrégation (region, district)
            serotype: Sérotype/variante à filtrer 
            
        Returns:
            DataFrame pandas avec les taux de létalité
        """
        params = {
            'date_debut': date_debut,
            'date_fin': date_fin,
            'niveau': niveau if niveau else "region",
            'serotype': serotype if serotype else "Tous"
        }
        
        data = self._make_request("GET", "/indicateurs/taux-deletalite", params=params)
        import pandas as pd
        df = pd.DataFrame(data if isinstance(data, list) else [data])
        return df
    
    def get_taux_positivite(self,
                           date_debut: str,
                           date_fin: str,
                           region: Optional[str] = None,
                           district: Optional[str] = None) -> pd.DataFrame:
        """
        Récupère le taux de positivité et retourne un DataFrame pandas.
        
        Args:
            date_debut: Date de début
            date_fin: Date de fin
            region: Région
            district: District
            
        Returns:
            DataFrame pandas avec les taux de positivité
        """
        params = {
            'date_debut': date_debut,
            'date_fin': date_fin
        }
        
        if region:
            params['region'] = region
        if district:
            params['district'] = district
        
        data = self._make_request("GET", "/indicateurs/taux-positivite", params=params)
        import pandas as pd
        df = pd.DataFrame(data if isinstance(data, list) else [data])
        return df
    
    # ==================== SYSTÈME D'ALERTES ====================
    
    def get_alertes(self,
                    limit: int = 10,
                    severity: Optional[str] = None,
                    status: Optional[str] = None,
                    region: Optional[str] = None,
                    district: Optional[str] = None,
                    date_debut: Optional[str] = None,
                    date_fin: Optional[str] = None) -> pd.DataFrame:
        """
        Récupère les alertes selon les critères et retourne un DataFrame pandas.
        
        Args:
            limit: Nombre maximum d'alertes
            severity: Sévérité (warning, critical, info)
            status: Statut (active, resolved)
            region: Région
            district: District
            date_debut: Date de début
            date_fin: Date de fin
            
        Returns:
            DataFrame pandas avec les alertes
        """
        alertes = self.alerts.get_alertes(
            limit=limit,
            severity=severity,
            status=status,
            region=region,
            district=district,
            date_debut=date_debut,
            date_fin=date_fin
        )
        
        import pandas as pd
        
        # Convertir les objets Pydantic en dictionnaires et nettoyer les tuples
        if isinstance(alertes, list):
            data_list = []
            for alerte in alertes:
                if hasattr(alerte, 'model_dump'):
                    # Objet Pydantic
                    alerte_dict = alerte.model_dump()
                elif isinstance(alerte, dict):
                    # Déjà un dictionnaire
                    alerte_dict = alerte
                else:
                    # Autre type, essayer de convertir
                    alerte_dict = dict(alerte)
                
                # Nettoyer les tuples dans le dictionnaire
                cleaned_dict = {}
                for key, value in alerte_dict.items():
                    if isinstance(value, tuple):
                        # Prendre le premier élément du tuple
                        cleaned_dict[key] = value[0] if len(value) > 0 else None
                    else:
                        cleaned_dict[key] = value
                
                data_list.append(cleaned_dict)
            df = pd.DataFrame(data_list)
        else:
            # Cas où alertes n'est pas une liste
            if hasattr(alertes, 'model_dump'):
                alerte_dict = alertes.model_dump()
            elif isinstance(alertes, dict):
                alerte_dict = alertes
            else:
                alerte_dict = dict(alertes)
            
            # Nettoyer les tuples
            cleaned_dict = {}
            for key, value in alerte_dict.items():
                if isinstance(value, tuple):
                    cleaned_dict[key] = value[0] if len(value) > 0 else None
                else:
                    cleaned_dict[key] = value
            
            df = pd.DataFrame([cleaned_dict])
        
        return df
    
    # A revoir
    def configurer_seuils(self, **kwargs) -> Dict[str, Any]:
        """
        Configure les seuils d'alerte.
        
        Args:
            **kwargs: Paramètres de configuration
            
        Returns:
            Résultat de la configuration
        """
        return self.alerts.configurer_seuils(**kwargs)
    
    def verifier_alertes(self,
                        date_debut: Optional[str] = None,
                        date_fin: Optional[str] = None,
                        region: str = "Toutes",
                        district: str = "Toutes") -> pd.DataFrame:
        """
        Vérifie les alertes selon les critères et retourne un DataFrame pandas.
        
        Args:
            date_debut: Date de début
            date_fin: Date de fin
            region: Région
            district: District
            
        Returns:
            Résultat de la vérification
        """
        return self.alerts.verifier_alertes(
            date_debut=date_debut,
            date_fin=date_fin,
            region=region,
            district=district
        )
    
    # ==================== EXPORT DE DONNÉES ====================
   
    def save_to_file(self,
        filepath: Optional[str] = None,
        date_debut: Optional[str] = None,
        date_fin: Optional[str] = None,
        region: Optional[str] = None,
        district: Optional[str] = None,
        limit: Optional[int] = None,
        page: Optional[int] = None,
        format: str = "csv") -> bool:
            
        """
        Sauvegarde les données dans un fichier.
        
        Args:
            filepath: Chemin du fichier de sortie (optionnel, utilise le répertoire courant si non fourni)
            date_debut: Date de début (format YYYY-MM-DD)
            date_fin: Date de fin (format YYYY-MM-DD)
            region: Région à filtrer
            district: District à filtrer
            limit: Nombre maximum de résultats
            format: Format de sortie (csv, json, xlsx, parquet)
            
        Returns:
            True si la sauvegarde a réussi
            
        Raises:
            ValueError: Si le format n'est pas supporté
            IOError: En cas d'erreur d'écriture
        """
        # Récupérer les données
        df = self.data(
            date_debut=date_debut,
            date_fin=date_fin,
            region=region,
            district=district,
            limit=limit,
            page=page
        )
        
        # Si aucun filepath n'est fourni, utiliser le répertoire courant
        if filepath is None:
            import os
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"dengue_data_{timestamp}"
            filepath = os.path.join(os.getcwd(), filename)
        
        # Déterminer l'extension si non fournie
        if not filepath.endswith(('.csv', '.json', '.xlsx', '.parquet')):
            if format == "csv":
                filepath += ".csv"
            elif format == "json":
                filepath += ".json"
            elif format == "xlsx":
                filepath += ".xlsx"
            elif format == "parquet":
                filepath += ".parquet"
        
        # Sauvegarder selon le format
        try:
            if format == "csv":
                df.to_csv(filepath, index=False, encoding='utf-8')
            elif format == "json":
                df.to_json(filepath, orient='records', indent=2, date_format='iso')
            elif format == "xlsx":
                df.to_excel(filepath, index=False, engine='openpyxl')
            elif format == "parquet":
                df.to_parquet(filepath, index=False)
            else:
                raise ValueError(f"Format non supporté: {format}. Formats supportés: csv, json, xlsx, parquet")
            
            self.logger.info(f"Données sauvegardées dans {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la sauvegarde: {e}")
            raise IOError(f"Impossible de sauvegarder le fichier {filepath}: {e}")

    
    def alertes_to_file(self,
                          filepath: Optional[str] = None,
                          limit: int = 100,
                          severity: Optional[str] = None,
                          status: Optional[str] = None,
                          format: str = "csv") -> bool:
            """
            Sauvegarde les alertes dans un fichier.
            
            Args:
                filepath: Chemin du fichier de sortie
                limit: Nombre maximum d'alertes
                severity: Sévérité
                status: Statut
                format: Format de sortie (csv, json, xlsx)
                
            Returns:
                True si la sauvegarde a réussi
            """
            # Récupérer les alertes
            alertes = self.get_alertes(
                limit=limit,
                severity=severity,
                status=status
            )
            
             # Si aucun filepath n'est fourni, utiliser le répertoire courant
            if filepath is None:
                import os
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"alertes_data_{timestamp}"
                filepath = os.path.join(os.getcwd(), filename)
            
            # Convertir en DataFrame
            if alertes.empty: # Check if the DataFrame is empty
                df = pd.DataFrame(columns=[
                    'id', 'id_seuil', 'usermail', 'severity', 'status', 'message',
                    'region', 'district', 'notification_type', 'recipient', 'created_at'
                ])
            else:
                data_list = []
                for alerte in alertes.to_dict(orient='records'): # Convert DataFrame to list of dicts
                    alerte_dict = alerte
                    # Convertir les dates
                    if alerte_dict.get('created_at'):
                        alerte_dict['created_at'] = str(alerte_dict['created_at'])
                    data_list.append(alerte_dict)
                
                df = pd.DataFrame(data_list)
            
            # Déterminer l'extension si non fournie
            if not filepath.endswith(('.csv', '.json', '.xlsx')):
                if format == "csv":
                    filepath += ".csv"
                elif format == "json":
                    filepath += ".json"
                elif format == "xlsx":
                    filepath += ".xlsx"
            
            # Sauvegarder selon le format
            try:
                if format == "csv":
                    df.to_csv(filepath, index=False, encoding='utf-8')
                elif format == "json":
                    df.to_json(filepath, orient='records', indent=2, date_format='iso')
                elif format == "xlsx":
                    df.to_excel(filepath, index=False, engine='openpyxl')
                else:
                    raise ValueError(f"Format non supporté: {format}. Formats supportés: csv, json, xlsx")
                
                self.logger.info(f"Alertes sauvegardées dans {filepath}")
                return True
                
            except Exception as e:
                self.logger.error(f"Erreur lors de la sauvegarde des alertes: {e}")
                raise IOError(f"Impossible de sauvegarder le fichier {filepath}: {e}")        

    # ==================== OUTILS D'ANALYSE ====================
    
    
    def detect_anomalies(self, data: pd.DataFrame, method: str = "zscore", columns: Optional[List[str]] = None) -> pd.DataFrame:
        """
        Détecte les anomalies dans les données de dengue.
        
        Cette fonction analyse les données pour identifier des valeurs anormales
        qui pourraient indiquer des situations épidémiologiques préoccupantes.
        
        Args:
            data: DataFrame avec les données à analyser
            method: Méthode de détection ("zscore", "iqr", "isolation_forest")
            columns: Colonnes à analyser (par défaut: colonnes numériques)
            
        Returns:
            DataFrame avec les données originales et les colonnes d'anomalies ajoutées
            
        Raises:
            AnalysisError: En cas d'erreur lors de la détection
        """
        try:
            if data.empty:
                self.logger.warning("DataFrame vide - aucune anomalie à détecter")
                return data
            
            # Déterminer les colonnes à analyser
            if columns is None:
                # Colonnes numériques par défaut pour la dengue
                numeric_columns = data.select_dtypes(include=[np.number]).columns.tolist()
                # Prioriser les colonnes importantes pour la dengue
                priority_columns = ['total_cas', 'cas_positifs', 'hospitalisations', 'deces', 
                                  'taux_positivite', 'taux_hospitalisation', 'taux_letalite']
                columns = [col for col in priority_columns if col in numeric_columns]
                if not columns:
                    columns = numeric_columns[:5]  # Limiter à 5 colonnes
            
            if not columns:
                self.logger.warning("Aucune colonne numérique trouvée pour l'analyse")
                return data
            
            self.logger.info(f"Détection d'anomalies avec la méthode {method} sur {len(columns)} colonnes")
            
            # Copier les données
            anomalies_df = data.copy()
            
            if method == "zscore":
                # Détection par score Z (valeurs à plus de 2 écarts-types de la moyenne)
                for col in columns:
                    if col in anomalies_df.columns:
                        col_data = pd.to_numeric(anomalies_df[col], errors='coerce')
                        if not col_data.isna().all():
                            mean_val = col_data.mean()
                            std_val = col_data.std()
                            if std_val > 0:
                                z_scores = np.abs((col_data - mean_val) / std_val)
                                anomalies_df[f'{col}_anomaly'] = z_scores > 2
                                anomalies_df[f'{col}_zscore'] = z_scores
                            else:
                                anomalies_df[f'{col}_anomaly'] = False
                                anomalies_df[f'{col}_zscore'] = 0
            
            elif method == "iqr":
                # Détection par IQR (Interquartile Range)
                for col in columns:
                    if col in anomalies_df.columns:
                        col_data = pd.to_numeric(anomalies_df[col], errors='coerce')
                        if not col_data.isna().all():
                            Q1 = col_data.quantile(0.25)
                            Q3 = col_data.quantile(0.75)
                            IQR = Q3 - Q1
                            if IQR > 0:
                                lower_bound = Q1 - 1.5 * IQR
                                upper_bound = Q3 + 1.5 * IQR
                                anomalies_df[f'{col}_anomaly'] = (col_data < lower_bound) | (col_data > upper_bound)
                                anomalies_df[f'{col}_iqr_lower'] = lower_bound
                                anomalies_df[f'{col}_iqr_upper'] = upper_bound
                            else:
                                anomalies_df[f'{col}_anomaly'] = False
            
            elif method == "isolation_forest":
                # Détection par Isolation Forest (nécessite scikit-learn)
                try:
                    from sklearn.ensemble import IsolationForest
                    
                    # Préparer les données
                    available_cols = [col for col in columns if col in anomalies_df.columns]
                    if available_cols:
                        X = anomalies_df[available_cols].fillna(0)
                        
                        # Entraîner le modèle
                        iso_forest = IsolationForest(contamination=0.1, random_state=42)
                        anomalies_df['isolation_forest_anomaly'] = iso_forest.fit_predict(X) == -1
                        
                        self.logger.info("Isolation Forest appliqué avec succès")
                    else:
                        self.logger.warning("Aucune colonne disponible pour Isolation Forest")
                
                except ImportError:
                    self.logger.warning("scikit-learn non disponible, utilisation de la méthode zscore")
                    return self.detect_anomalies(data, method="zscore", columns=columns)
            
            else:
                raise AnalysisError(f"Méthode de détection non supportée: {method}")
            
            # Ajouter un résumé des anomalies détectées
            anomaly_columns = [col for col in anomalies_df.columns if col.endswith('_anomaly')]
            if anomaly_columns:
                anomalies_df['total_anomalies'] = anomalies_df[anomaly_columns].sum(axis=1)
                anomalies_df['has_anomalies'] = anomalies_df['total_anomalies'] > 0
            
            # Log des résultats
            total_anomalies = anomalies_df.get('total_anomalies', pd.Series(0)).sum()
            self.logger.info(f"Détection terminée: {total_anomalies} anomalies détectées")
            
            return anomalies_df
            
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
                       district: Optional[str] = None) -> pd.DataFrame:
        """
        Calcule les taux épidémiologiques et retourne un DataFrame à une ligne.
        
        Args:
            date_debut: Date de début
            date_fin: Date de fin
            region: Région
            district: District
        
        Returns:
            DataFrame à une ligne avec les taux calculés et les totaux
        """
        rates = self.analyzer.calculate_rates(
            date_debut=date_debut,
            date_fin=date_fin,
            region=region,
            district=district
        )
        import pandas as pd
        return pd.DataFrame([rates])
    
    # ==================== MÉTHODES UTILITAIRES ====================
    
    def clear_cache(self) -> None:
        """Vide le cache des requêtes."""
        self._cache.clear()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Récupère les informations sur le cache.
        
        Returns:
            Informations sur le cache
        """
        return {
            'size': len(self._cache),
            'ttl': self._cache_ttl,
            'keys': list(self._cache.keys())
        }
    
    def set_cache_ttl(self, ttl: int) -> None:
        """
        Définit la durée de vie du cache.
        
        Args:
            ttl: Durée de vie en secondes
        """
        self._cache_ttl = ttl
    
    def __enter__(self):
        """Support du context manager."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Nettoyage lors de la sortie du context manager."""
        self.session.close()

    # ==================== RESUME ====================

    def resumer(self, *args, **kwargs):
        """
        Résumé statistique et structurel de la base de données.
        (Remplace l'ancienne méthode resume)

        Voir : SyntheseBase.resumer pour la liste complète des paramètres et options.

        Exemple :
            client.resumer(annee=2024, region="Centre")
        """
        from .analytics import SyntheseBase
        synth = SyntheseBase(client=self)
        return synth.resumer(*args, **kwargs)

    def graph_desc(self, *args, **kwargs):
        """
        Visualisation descriptive de la base (camemberts, barres, histogrammes).
        (Remplace l'ancienne méthode resume_display)

        Voir : SyntheseBase.graph_desc pour la liste complète des paramètres et options.

        Exemple :
            client.graph_desc(date_debut="2024-01-01", date_fin="2024-12-31")
        """
        from .analytics import SyntheseBase
        synth = SyntheseBase(client=self)
        return synth.graph_desc(*args, **kwargs)

    def evolution(self, *args, **kwargs):
        """
        Analyse d'évolution temporelle (par semaine/mois, par sous-groupes, avec taux de croissance).
        (Remplace l'ancienne méthode resume_display)

        Voir : SyntheseBase.evolution pour la liste complète des paramètres et options.

        Exemple :
            client.evolution(by="sexe", frequence="M", taux_croissance=True)
        """
        from .analytics import SyntheseBase
        synth = SyntheseBase(client=self)
        return synth.evolution(*args, **kwargs)