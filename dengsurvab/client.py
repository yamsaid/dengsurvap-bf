"""
Client principal pour l'API Appi Dengue

Ce module contient la classe AppiClient qui fournit une interface
complète pour interagir avec l'API de surveillance de la dengue.
"""

import os
import requests
import pandas as pd
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, date, timedelta
import json
import logging
from urllib.parse import urljoin

from .models import (
    CasDengue, SoumissionDonnee, AlertLog, SeuilAlert, User,
    ValidationCasDengue, IndicateurHebdo, Statistiques,
    LoginRequest, RegisterRequest, AlertConfigRequest
)
from .exceptions import (
    AppiException, AuthenticationError, APIError, ValidationError,
    RateLimitError, ConnectionError, create_exception_from_response
)
from .auth import AuthManager
from .alerts import AlertManager
from .export import DataExporter
from .analytics import EpidemiologicalAnalyzer

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
   
    def get_cas_dengue(self,
                       annee : int = date.today().year,
                       mois : int = date.today().month,
                       region : Optional[str] = None,
                       district : Optional[str] = None,
                       ) -> List[CasDengue]:
        """_summary_

        Args:
            annee (int, optional): _description_. Defaults to date.today().year.
            mois (int, optional): _description_. Defaults to date.today().month.
            region (Optional[str], optional): _description_. Defaults to None.
            district (Optional[str], optional): _description_. Defaults to None.

        Returns:
            List[CasDengue]: _description_
        """
        params = {
            'annee': annee,
            'mois': mois,
            'region': region,
            'district': district
        }
        
        data = self._make_request("GET", "/api/data/hebdomadaires", params=params)
        
        
        # Conversion en objets CasDengue
        cas_list = []
        for cas_data in data if isinstance(data, list) else data.get('data', []):
            try:
                cas = CasDengue(**cas_data)
                cas_list.append(cas)
            except Exception as e:
                self.logger.warning(f"Erreur de validation du cas: {e}")
        
        return cas_list
    
    # a revoir
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
    
    # ==================== INDICATEURS ÉPIDÉMIOLOGIQUES ====================
    # a revoir
    def donnees_par_periode(self,
        date_debut: Optional[str] = None,
        date_fin: Optional[str] = None,
        region: Optional[str] = None,
        district: Optional[str] = None,
        frequence: str = "W"
        ) -> List[IndicateurHebdo]:

        """
        Récupère les indicateurs hebdomadaires.
        
        Args:
            date_debut: Date de début
            date_fin: Date de fin
            region: Région
            district: District
            frequence: Fréquence (W: hebdomadaire, M: mensuel)
            
        Returns:
            Liste des indicateurs hebdomadaires
        """
        params = {
            'date_debut': date_debut,
            'date_fin': date_fin,
            'region': region,
            'district': district,
            'frequence': frequence
        }
        
        data = self._make_request("GET", "/api/time-series", params=params)
        
        indicateurs = []
        for ind_data in data:
            try:
                #indicateur = IndicateurHebdo(**ind_data)
                indicateurs.append(ind_data)
            except Exception as e:
                self.logger.warning(f"Erreur de validation de l'indicateur: {e}")
        
        return indicateurs
    
    def get_taux_hospitalisation(self,
                                date_debut: str,
                                date_fin: str,
                                region: str = "Toutes",
                                district: str = "Toutes") -> Dict[str, Any]:
        """
        Récupère le taux d'hospitalisation.
        
        Args:
            date_debut: Date de début
            date_fin: Date de fin
            region: Région
            district: District
            
        Returns:
            Données du taux d'hospitalisation
        """
        params = {
            'date_debut': date_debut,
            'date_fin': date_fin
        }
        
        if region != "Toutes":
            params['region'] = region
        if district != "Toutes":
            params['district'] = district
        
        return self._make_request("GET", "/indicateurs/taux-hospitalisation", params=params)
    
    def get_taux_letalite(self,
                          date_debut: str,
                          date_fin: str,
                          niveau: Optional[str] = None,
                          serotype: Optional[str] = None) -> Dict[str, Any]:
        """
        Récupère le taux de létalité.
        
        Args:
            date_debut: Date de début
            date_fin: Date de fin
            niveau: Niveau d'agrégation (region, district)
            serotype: Sérotype/variante à filtrer 
            
        Returns:
            Données du taux de létalité
        """
        params = {
            'date_debut': date_debut,
            'date_fin': date_fin,
            'niveau': niveau if niveau else "region",
            'serotype': serotype if serotype else "Tous"
        }
        
        return self._make_request("GET", "/indicateurs/taux-deletalite", params=params)
    
    def get_taux_positivite(self,
                           date_debut: str,
                           date_fin: str,
                           region: Optional[str] = None,
                           district: Optional[str] = None) -> Dict[str, Any]:
        """
        Récupère le taux de positivité.
        
        Args:
            date_debut: Date de début
            date_fin: Date de fin
            region: Région
            district: District
            
        Returns:
            Données du taux de positivité
        """
        params = {
            'date_debut': date_debut,
            'date_fin': date_fin
        }
        
        if region:
            params['region'] = region
        if district:
            params['district'] = district
        
        return self._make_request("GET", "/indicateurs/taux-positivite", params=params)
    
    # ==================== SYSTÈME D'ALERTES ====================
    
    def get_alertes(self,
                    limit: int = 10,
                    severity: Optional[str] = None,
                    status: Optional[str] = None,
                    region: Optional[str] = None,
                    district: Optional[str] = None,
                    date_debut: Optional[str] = None,
                    date_fin: Optional[str] = None) -> List[AlertLog]:
        """
        Récupère les alertes selon les critères.
        
        Args:
            limit: Nombre maximum d'alertes
            severity: Sévérité (warning, critical, info)
            status: Statut (active, resolved)
            region: Région
            district: District
            date_debut: Date de début
            date_fin: Date de fin
            
        Returns:
            Liste des alertes
        """
        return self.alerts.get_alertes(
            limit=limit,
            severity=severity,
            status=status,
            region=region,
            district=district,
            date_debut=date_debut,
            date_fin=date_fin
        )
    
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
                        district: str = "Toutes") -> Dict[str, Any]:
        """
        Vérifie les alertes selon les critères.
        
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
    
    def data(self,
            date_debut: Optional[str] = None,
            date_fin: Optional[str] = None,
            region: Optional[str] = None,
            district: Optional[str] = None,
            limit: Optional[int] = None,
            page: Optional[int] = None) -> pd.DataFrame:
        """
        Récupère les données de dengue sous forme de DataFrame.
        
        Args:
            date_debut: Date de début (format YYYY-MM-DD)
            date_fin: Date de fin (format YYYY-MM-DD)
            region: Région à filtrer
            district: District à filtrer
            limit: Nombre maximum de résultats
            
        Returns:
            DataFrame avec les données de dengue
        """
        # Récupérer les cas de dengue
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
            if alertes:
                data_list = []
                for alerte in alertes:
                    alerte_dict = alerte.model_dump()
                    # Convertir les dates
                    if alerte_dict.get('created_at'):
                        alerte_dict['created_at'] = str(alerte_dict['created_at'])
                    data_list.append(alerte_dict)
                
                df = pd.DataFrame(data_list)
            else:
                df = pd.DataFrame(columns=[
                    'id', 'id_seuil', 'usermail', 'severity', 'status', 'message',
                    'region', 'district', 'notification_type', 'recipient', 'created_at'
                ])
            
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
    
    
    def detect_anomalies(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Détecte les anomalies dans les données.
        
        Args:
            data: DataFrame avec les données
            
        Returns:
            DataFrame avec les anomalies détectées
        """
        return self.analyzer.detect_anomalies(data)
    
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
        """
        return self.analyzer.calculate_rates(
            date_debut=date_debut,
            date_fin=date_fin,
            region=region,
            district=district
        )
    
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
    def resume(self,limit: int = None,date_debut: Optional[str] = None,date_fin: Optional[str] = None) -> Dict[str, Any]:
        """
        Génère un résumé statistique complet et professionnel de la base de données.
        
        Cette fonction analyse la base de données de surveillance de la dengue et fournit
        un aperçu détaillé incluant les informations générales, les statistiques descriptives
        pour chaque variable, et la qualité des données.
        
        Returns:
            Dict contenant le résumé complet de la base de données avec la structure suivante:
            {
                "success": bool,
                "message": str,
                "periode_couverture": dict,
                "derniere_mise_a_jour": str,
                "informations_generales": dict,
                "variables": dict,
                "qualite_donnees": dict
            }
            
        Raises:
            APIError: En cas d'erreur lors de la récupération des données
            ValueError: En cas d'erreur dans les calculs statistiques
        """
        try:
            # Récupérer toutes les données
            df = self.data(limit=limit,date_debut=date_debut,date_fin=date_fin)
            
            if df.empty:
                return {
                    "success": True,
                    "message": "Base de données vide - aucun enregistrement trouvé",
                    "periode_couverture": {},
                    "derniere_mise_a_jour": None,
                    "informations_generales": {
                        "total_enregistrements": 0,
                        "regions_couvertes": 0,
                        "districts_couverts": 0
                    },
                    "variables": {},
                    "qualite_donnees": {
                        "variables_completes": [],
                        "variables_avec_manquants": [],
                        "taux_completude_global": 0.0
                    }
                }
            
            # 1. Informations générales
            periode_couverture = {
                "date_debut": df['date_consultation'].min().strftime("%Y-%m-%d") if not df['date_consultation'].isna().all() else None,
                "date_fin": df['date_consultation'].max().strftime("%Y-%m-%d") if not df['date_consultation'].isna().all() else None,
                "duree_jours": (df['date_consultation'].max() - df['date_consultation'].min()).days if not df['date_consultation'].isna().all() else 0
            }
            
            informations_generales = {
                "total_enregistrements": len(df),
                "regions_couvertes": df['region'].nunique() if 'region' in df.columns else 0,
                "districts_couverts": df['district'].nunique() if 'district' in df.columns else 0
            }
            
            # 2. Analyse des variables
            variables = {
                "numeriques": {},
                "qualitatives": {}
            }
            
            # Identifier les types de variables
            for col in df.columns:
                if col in ['age', 'idCas', 'id_source'] or df[col].dtype in ['int64', 'float64']:
                    # Variables numériques
                    col_data = pd.to_numeric(df[col], errors='coerce')
                    manquantes = col_data.isna().sum()
                    
                    variables["numeriques"][col] = {
                        "type": str(df[col].dtype),
                        "valeurs_manquantes": int(manquantes),
                        "pourcentage_manquantes": round((manquantes / len(df)) * 100, 2),
                        "min": float(col_data.min()) if not col_data.isna().all() else None,
                        "max": float(col_data.max()) if not col_data.isna().all() else None,
                        "moyenne": round(float(col_data.mean()), 2) if not col_data.isna().all() else None,
                        "ecart_type": round(float(col_data.std()), 2) if not col_data.isna().all() else None,
                        "quartiles": {
                            "Q1": float(col_data.quantile(0.25)) if not col_data.isna().all() else None,
                            "Q2": float(col_data.quantile(0.50)) if not col_data.isna().all() else None,
                            "Q3": float(col_data.quantile(0.75)) if not col_data.isna().all() else None
                        },
                        "valeurs_uniques": int(col_data.nunique())
                    }
                else:
                    # Variables qualitatives
                    col_data = df[col].astype(str)
                    manquantes = col_data.isna().sum() + (col_data == 'nan').sum() + (col_data == 'None').sum()
                    
                    # Calculer le mode
                    mode_value = col_data.mode().iloc[0] if not col_data.empty else None
                    
                    # Distribution des valeurs (top 5)
                    value_counts = col_data.value_counts().head(5)
                    distribution = {str(k): int(v) for k, v in value_counts.items()}
                    
                    variables["qualitatives"][col] = {
                        "type": str(df[col].dtype),
                        "valeurs_manquantes": int(manquantes),
                        "pourcentage_manquantes": round((manquantes / len(df)) * 100, 2),
                        "mode": str(mode_value) if mode_value else None,
                        "valeurs_uniques": int(col_data.nunique()),
                        "distribution": distribution
                    }
            
            # 3. Qualité des données
            variables_completes = []
            variables_avec_manquants = []
            
            for col in df.columns:
                manquantes = df[col].isna().sum()
                if manquantes == 0:
                    variables_completes.append(col)
                else:
                    variables_avec_manquants.append(col)
            
            taux_completude = round(((len(df) * len(df.columns)) - df.isna().sum().sum()) / (len(df) * len(df.columns)) * 100, 2)
            
            qualite_donnees = {
                "variables_completes": variables_completes,
                "variables_avec_manquants": variables_avec_manquants,
                "taux_completude_global": taux_completude
            }
            
            # 4. Dernière mise à jour (utiliser la date la plus récente)
            date_ = self._make_request("GET", "/api/derniere-mise-a-jour")

            derniere_mise_a_jour = date_["derniere_mise_a_jour"] if date_["statut"] == True else "Date non trouvée"
            return {
                "success": True,
                "message": f"Résumé de la base de données généré avec succès - {len(df)} enregistrements analysés",
                "periode_couverture": periode_couverture,
                "derniere_mise_a_jour": derniere_mise_a_jour,
                "informations_generales": informations_generales,
                "variables": variables,
                "qualite_donnees": qualite_donnees
            }
            
        except Exception as e:
            self.logger.error(f"Erreur lors de la génération du résumé: {e}")
            return {
                "success": False,
                "message": f"Erreur lors de la génération du résumé: {str(e)}",
                "periode_couverture": {},
                "derniere_mise_a_jour": None,
                "informations_generales": {},
                "variables": {},
                "qualite_donnees": {}
            }
    
    def resume_display(self, limit: int = None, verbose: bool = True, show_details: bool = True, graph: bool = False,date_debut: Optional[str] = None,date_fin: Optional[str] = None) -> None:
        """
        Affiche un résumé statistique professionnel de la base de données dans la console.
        
        Cette méthode génère un affichage formaté similaire aux méthodes info() et describe()
        de pandas, avec une présentation claire et structurée des informations.
        
        Parameters:
            verbose: bool, default True
                Afficher les détails complets pour chaque variable
            show_details: bool, default True
                Afficher les statistiques détaillées (quartiles, distribution, etc.)
            graph: bool, default False
                Afficher des graphiques descriptifs (histogrammes, diagrammes en barres, etc.)
        """
        try:
            # Récupérer le résumé
            resume_data = self.resume(limit=limit,date_debut=date_debut,date_fin=date_fin)
            
            if not resume_data.get('success'):
                print(f"❌ Erreur: {resume_data.get('message')}")
                return
            
            # En-tête principal
            print("=" * 80)
            print("📊 RÉSUMÉ STATISTIQUE - BASE DE DONNÉES SURVEILLANCE DENGUE")
            print("=" * 80)
            
            # Informations générales
            info_gen = resume_data.get('informations_generales', {})
            periode = resume_data.get('periode_couverture', {})
            
            print(f"\n📈 INFORMATIONS GÉNÉRALES")
            print(f"   Total enregistrements: {info_gen.get('total_enregistrements', 0):,}")
            print(f"   Régions couvertes: {info_gen.get('regions_couvertes', 0)}")
            print(f"   Districts couverts: {info_gen.get('districts_couverts', 0)}")
            
            if periode.get('date_debut') and periode.get('date_fin'):
                print(f"   Période: {periode['date_debut']} → {periode['date_fin']}")
                print(f"   Durée: {periode.get('duree_jours', 0)} jours")
            
            # Qualité des données
            qualite = resume_data.get('qualite_donnees', {})
            print(f"\n🔍 QUALITÉ DES DONNÉES")
            print(f"   Taux de complétude global: {qualite.get('taux_completude_global', 0):.1f}%")
            print(f"   Variables complètes: {len(qualite.get('variables_completes', []))}")
            print(f"   Variables avec manquants: {len(qualite.get('variables_avec_manquants', []))}")
            
            if verbose:
                # Variables complètes
                variables_completes = qualite.get('variables_completes', [])
                if variables_completes:
                    print(f"\n✅ VARIABLES COMPLÈTES ({len(variables_completes)})")
                    for var in variables_completes[:10]:  # Limiter à 10 pour l'affichage
                        print(f"   • {var}")
                    if len(variables_completes) > 10:
                        print(f"   ... et {len(variables_completes) - 10} autres")
                
                # Variables avec manquants
                variables_manquants = qualite.get('variables_avec_manquants', [])
                if variables_manquants:
                    print(f"\n⚠️  VARIABLES AVEC VALEURS MANQUANTES ({len(variables_manquants)})")
                    for var in variables_manquants[:10]:
                        print(f"   • {var}")
                    if len(variables_manquants) > 10:
                        print(f"   ... et {len(variables_manquants) - 10} autres")
            
            # Variables numériques
            variables = resume_data.get('variables', {})
            numeriques = variables.get('numeriques', {})
            
            if numeriques:
                print(f"\n📊 VARIABLES NUMÉRIQUES ({len(numeriques)})")
                print("-" * 60)
                
                if show_details:
                    # En-tête du tableau
                    print(f"{'Variable':<20} {'Type':<10} {'Min':<8} {'Max':<8} {'Moyenne':<10} {'Manquants':<12}")
                    print("-" * 60)
                    
                    for var, stats in numeriques.items():
                        manquants_pct = stats.get('pourcentage_manquantes', 0)
                        manquants_str = f"{stats.get('valeurs_manquantes', 0)} ({manquants_pct:.1f}%)"
                        
                        print(f"{var:<20} {stats.get('type', ''):<10} "
                              f"{stats.get('min', 'N/A'):<8} {stats.get('max', 'N/A'):<8} "
                              f"{stats.get('moyenne', 'N/A'):<10} {manquants_str:<12}")
                else:
                    # Affichage simplifié
                    for var, stats in numeriques.items():
                        print(f"   {var}: {stats.get('type', '')} "
                              f"[{stats.get('min', 'N/A')} - {stats.get('max', 'N/A')}] "
                              f"({stats.get('pourcentage_manquantes', 0):.1f}% manquants)")
            
            # Variables qualitatives
            qualitatives = variables.get('qualitatives', {})
            
            if qualitatives:
                print(f"\n📋 VARIABLES QUALITATIVES ({len(qualitatives)})")
                print("-" * 60)
                
                if show_details:
                    # En-tête du tableau
                    print(f"{'Variable':<20} {'Type':<10} {'Mode':<15} {'Uniques':<10} {'Manquants':<12}")
                    print("-" * 60)
                    
                    for var, stats in qualitatives.items():
                        manquants_pct = stats.get('pourcentage_manquantes', 0)
                        manquants_str = f"{stats.get('valeurs_manquantes', 0)} ({manquants_pct:.1f}%)"
                        mode = stats.get('mode', 'N/A')
                        if mode and len(mode) > 12:
                            mode = mode[:9] + "..."
                        
                        print(f"{var:<20} {stats.get('type', ''):<10} {mode:<15} "
                              f"{stats.get('valeurs_uniques', 0):<10} {manquants_str:<12}")
                else:
                    # Affichage simplifié
                    for var, stats in qualitatives.items():
                        print(f"   {var}: {stats.get('type', '')} "
                              f"Mode: {stats.get('mode', 'N/A')} "
                              f"({stats.get('valeurs_uniques', 0)} valeurs uniques, "
                              f"{stats.get('pourcentage_manquantes', 0):.1f}% manquants)")
            
            # Dernière mise à jour
            derniere_maj = resume_data.get('derniere_mise_a_jour')
            if derniere_maj:
                print(f"\n🕒 DERNIÈRE MISE À JOUR: {derniere_maj}")
            
            print("\n" + "=" * 80)
            
            # Affichage des graphiques si demandé
            if graph:
                self._display_graphs(resume_data)
            
        except Exception as e:
            print(f"❌ Erreur lors de l'affichage du résumé: {str(e)}")
            self.logger.error(f"Erreur lors de l'affichage du résumé: {e}")
    
    def _display_graphs(self, resume_data: Dict[str, Any], limit: int = None,date_debut: Optional[str] = None,date_fin: Optional[str] = None) -> None:
        """
        Affiche des graphiques descriptifs pour les variables de la base de données.
        
        Parameters:
            resume_data: Données du résumé statistique
        """
        try:
            # Importer les bibliothèques nécessaires
            import matplotlib.pyplot as plt
            import seaborn as sns
            import pandas as pd
            import numpy as np
            
            # Configuration du style
            plt.style.use('default')
            sns.set_palette("husl")
            
            # Récupérer les données
            df = self.data(limit=limit,date_debut=date_debut,date_fin=date_fin)
            if df.empty:
                print("⚠️  Aucune donnée disponible pour les graphiques")
                return
            
            variables = resume_data.get('variables', {})
            numeriques = variables.get('numeriques', {})
            qualitatives = variables.get('qualitatives', {})
            
            # Calculer le nombre de graphiques à afficher
            total_graphs = len(numeriques) + min(len(qualitatives), 5)  # Limiter les qualitatives
            if total_graphs == 0:
                print("⚠️  Aucune variable disponible pour les graphiques")
                return
            
            # Configuration de la grille de graphiques
            cols = 3
            rows = (total_graphs + cols - 1) // cols
            
            print(f"\n📊 GRAPHIQUES DESCRIPTIFS ({total_graphs} variables)")
            print("=" * 80)
            
            # Créer la figure principale
            fig = plt.figure(figsize=(15, 4 * rows))
            fig.suptitle('Analyse Descriptive - Base de Données Surveillance Dengue', 
                        fontsize=16, fontweight='bold', y=0.98)
            
            plot_idx = 1
            
            # Graphiques pour les variables numériques
            for var, stats in numeriques.items():
                if var in ['idCas', 'id_source']:
                    continue  # Ne pas afficher les identifiants
                if plot_idx > total_graphs:
                    break
                    
                plt.subplot(rows, cols, plot_idx)
                
                # Filtrer les valeurs non-nulles
                data_clean = pd.to_numeric(df[var], errors='coerce').dropna()
                
                if len(data_clean) > 0:
                    # Histogramme avec courbe de densité
                    plt.hist(data_clean, bins=min(20, len(data_clean)//5), 
                            alpha=0.7, density=True, color='skyblue', edgecolor='black')
                    
                    # Courbe de densité uniquement si plus d'une valeur unique
                    if len(data_clean) > 10 and data_clean.nunique() > 1:
                        from scipy import stats
                        kde_x = np.linspace(data_clean.min(), data_clean.max(), 100)
                        try:
                            kde = stats.gaussian_kde(data_clean)
                            plt.plot(kde_x, kde(kde_x), 'r-', linewidth=2, label='Densité')
                        except Exception as kde_err:
                            print(f"⚠️  Densité non tracée pour {var}: {kde_err}")
                    else:
                        print(f"⚠️  Densité non tracée pour {var}: données constantes ou insuffisantes.")
                    
                    plt.title(f'Distribution de {var}', fontweight='bold')
                    plt.xlabel(var)
                    plt.ylabel('Densité')
                    plt.legend()
                    plt.grid(True, alpha=0.3)
                    
                    # Ajouter des statistiques en texte
                    mean_val = data_clean.mean()
                    std_val = data_clean.std()
                    plt.text(0.02, 0.98, f'Moyenne: {mean_val:.2f}\nÉcart-type: {std_val:.2f}', 
                            transform=plt.gca().transAxes, verticalalignment='top',
                            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
                
                plot_idx += 1
            
            # Graphiques pour les variables qualitatives (top 5)
            qual_vars = [(k, v) for k, v in list(qualitatives.items())[:5] if k not in ['idCas', 'id_source']]
            for var, stats in qual_vars:
                if plot_idx > total_graphs:
                    break
                    
                plt.subplot(rows, cols, plot_idx)
                
                # Compter les valeurs
                value_counts = df[var].value_counts().head(10)  # Top 10
                
                if len(value_counts) > 0:
                    # Diagramme en barres
                    bars = plt.bar(range(len(value_counts)), value_counts.values, 
                                 color=plt.cm.Set3(np.linspace(0, 1, len(value_counts))))
                    
                    plt.title(f'Distribution de {var}', fontweight='bold')
                    plt.xlabel(var)
                    plt.ylabel('Fréquence')
                    
                    # Rotation des labels si nécessaire
                    plt.xticks(range(len(value_counts)), value_counts.index, 
                              rotation=45, ha='right')
                    
                    # Ajouter les valeurs sur les barres
                    for i, (bar, count) in enumerate(zip(bars, value_counts.values)):
                        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01*max(value_counts.values),
                                f'{count}', ha='center', va='bottom', fontweight='bold')
                    
                    plt.grid(True, alpha=0.3, axis='y')
                
                plot_idx += 1
            
            # Ajuster la mise en page
            plt.tight_layout()
            plt.subplots_adjust(top=0.92)
            
            # Afficher le graphique
            plt.show()
            
            # Graphiques supplémentaires pour les variables importantes
            self._display_special_graphs(df, resume_data)
            
        except ImportError as e:
            print(f"⚠️  Bibliothèques de graphiques non disponibles: {e}")
            print("   Installez matplotlib et seaborn: pip install matplotlib seaborn scipy")
        except Exception as e:
            print(f"❌ Erreur lors de la génération des graphiques: {str(e)}")
            self.logger.error(f"Erreur lors de la génération des graphiques: {e}")
    
    def _display_special_graphs(self, df: pd.DataFrame, resume_data: Dict[str, Any]) -> None:
        """
        Affiche des graphiques spéciaux pour des analyses plus avancées.
        
        Parameters:
            df: DataFrame avec les données
            resume_data: Données du résumé statistique
        """
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            import pandas as pd
            import numpy as np
            
            # Vérifier si nous avons des variables temporelles
            if 'date_consultation' in df.columns:
                print("\n📈 ANALYSE TEMPORELLE")
                print("-" * 40)
                
                # Convertir en datetime si nécessaire
                df['date_consultation'] = pd.to_datetime(df['date_consultation'], errors='coerce')
                df_temp = df.dropna(subset=['date_consultation'])
                
                if len(df_temp) > 0:
                    # Évolution temporelle des cas
                    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
                    
                    # Graphique 1: Évolution mensuelle
                    monthly_cases = df_temp.groupby(df_temp['date_consultation'].dt.to_period('M')).size()
                    monthly_cases.plot(kind='line', marker='o', ax=ax1, color='red', linewidth=2)
                    ax1.set_title('Évolution Mensuelle des Cas de Dengue', fontweight='bold')
                    ax1.set_xlabel('Mois')
                    ax1.set_ylabel('Nombre de cas')
                    ax1.grid(True, alpha=0.3)
                    
                    # Graphique 2: Répartition par région (si disponible)
                    if 'region' in df.columns:
                        region_counts = df_temp['region'].value_counts().head(8)
                        region_counts.plot(kind='bar', ax=ax2, color='lightcoral')
                        ax2.set_title('Répartition par Région', fontweight='bold')
                        ax2.set_xlabel('Région')
                        ax2.set_ylabel('Nombre de cas')
                        ax2.tick_params(axis='x', rotation=45)
                        ax2.grid(True, alpha=0.3, axis='y')
                    
                    plt.tight_layout()
                    plt.show()
            
            # Analyse des variables numériques importantes
            if 'age' in df.columns:
                print("\n👥 ANALYSE DÉMOGRAPHIQUE")
                print("-" * 40)
                
                age_data = pd.to_numeric(df['age'], errors='coerce').dropna()
                if len(age_data) > 0:
                    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
                    
                    # Distribution des âges
                    ax1.hist(age_data, bins=20, alpha=0.7, color='lightblue', edgecolor='black')
                    ax1.set_title('Distribution des Âges', fontweight='bold')
                    ax1.set_xlabel('Âge')
                    ax1.set_ylabel('Fréquence')
                    ax1.grid(True, alpha=0.3)
                    
                    # Box plot des âges
                    ax2.boxplot(age_data, patch_artist=True, 
                              boxprops=dict(facecolor='lightgreen', alpha=0.7))
                    ax2.set_title('Box Plot des Âges', fontweight='bold')
                    ax2.set_ylabel('Âge')
                    ax2.grid(True, alpha=0.3)
                    
                    plt.tight_layout()
                    plt.show()
            
            # Analyse des issues (si disponible)
            if 'issue' in df.columns:
                print("\n🏥 ANALYSE DES ISSUES")
                print("-" * 40)
                
                issue_counts = df['issue'].value_counts()
                if len(issue_counts) > 0:
                    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
                    
                    # Diagramme circulaire
                    colors = plt.cm.Pastel1(np.linspace(0, 1, len(issue_counts)))
                    wedges, texts, autotexts = ax1.pie(issue_counts.values, labels=issue_counts.index, 
                                                       autopct='%1.1f%%', colors=colors, startangle=90)
                    ax1.set_title('Répartition des Issues', fontweight='bold')
                    
                    # Diagramme en barres
                    bars = ax2.bar(range(len(issue_counts)), issue_counts.values, 
                                 color=colors)
                    ax2.set_title('Nombre par Issue', fontweight='bold')
                    ax2.set_xlabel('Issue')
                    ax2.set_ylabel('Nombre de cas')
                    ax2.set_xticks(range(len(issue_counts)))
                    ax2.set_xticklabels(issue_counts.index, rotation=45, ha='right')
                    
                    # Ajouter les valeurs sur les barres
                    for i, (bar, count) in enumerate(zip(bars, issue_counts.values)):
                        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01*max(issue_counts.values),
                                f'{count}', ha='center', va='bottom', fontweight='bold')
                    
                    plt.tight_layout()
                    plt.show()
                    
        except Exception as e:
            print(f"⚠️  Erreur lors de la génération des graphiques spéciaux: {str(e)}")
            self.logger.error(f"Erreur lors de la génération des graphiques spéciaux: {e}") 