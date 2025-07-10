"""
Tests pour le client Appi principal.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date

from dengsurvab import AppiClient
from dengsurvab.exceptions import AuthenticationError, APIError


class TestAppiClient:
    """Tests pour la classe AppiClient."""
    
    @pytest.fixture
    def client(self):
        """Fixture pour créer un client de test."""
        return AppiClient("https://test-api.com")
    
    @pytest.fixture
    def mock_session(self):
        """Fixture pour mocker la session."""
        session = Mock()
        session.headers = {}
        return session
    
    def test_init(self, client):
        """Test l'initialisation du client."""
        assert client.base_url == "https://test-api.com"
        assert client.api_key is None
        assert client.session is not None
    
    def test_init_with_api_key(self):
        """Test l'initialisation avec une clé API."""
        client = AppiClient("https://test-api.com", api_key="test-key")
        assert client.api_key == "test-key"
    
    @patch('dengsurvab.client.requests.Session')
    def test_authenticate_success(self, mock_session_class, client):
        """Test l'authentification réussie."""
        # Mock de la session
        mock_session = Mock()
        mock_session.post.return_value.status_code = 200
        mock_session.post.return_value.json.return_value = {
            "success": True,
            "token": "test-token",
            "user": {"email": "test@example.com"}
        }
        mock_session_class.return_value = mock_session
        
        # Test
        result = client.authenticate("test@example.com", "password")
        
        assert result is True
        assert client.session.headers.get("Authorization") == "Bearer test-token"
    
    @patch('dengsurvab.client.requests.Session')
    def test_authenticate_failure(self, mock_session_class, client):
        """Test l'échec d'authentification."""
        # Mock de la session
        mock_session = Mock()
        mock_session.post.return_value.status_code = 401
        mock_session.post.return_value.json.return_value = {
            "success": False,
            "message": "Invalid credentials"
        }
        mock_session_class.return_value = mock_session
        
        # Test
        result = client.authenticate("test@example.com", "wrong-password")
        
        assert result is False
    
    def test_is_authenticated(self, client):
        """Test la vérification d'authentification."""
        # Non authentifié
        assert client.is_authenticated() is False
        
        # Authentifié
        client.session.headers["Authorization"] = "Bearer test-token"
        assert client.is_authenticated() is True
    
    @patch('dengsurvab.client.requests.Session')
    def test_get_cas_dengue(self, mock_session_class, client):
        """Test la récupération des cas de dengue."""
        # Mock de la session
        mock_session = Mock()
        mock_session.get.return_value.status_code = 200
        mock_session.get.return_value.json.return_value = {
            "data": [
                {
                    "date_debut": "2024-01-01",
                    "date_fin": "2024-01-07",
                    "cas_positifs": 10,
                    "hospitalisations": 2,
                    "deces": 0,
                    "taux_positivite": 15.5,
                    "taux_hospitalisation": 3.1,
                    "taux_letalite": 0.0
                },
                {
                    "date_debut": "2024-01-08",
                    "date_fin": "2024-01-14",
                    "cas_positifs": 15,
                    "hospitalisations": 3,
                    "deces": 1,
                    "taux_positivite": 18.2,
                    "taux_hospitalisation": 3.7,
                    "taux_letalite": 0.8
                }
            ]
        }
        mock_session_class.return_value = mock_session
        
        # Test
        result = client.get_cas_dengue(annee=2024, mois=1)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "cas_positifs" in result.columns
        assert "hospitalisations" in result.columns
        assert "deces" in result.columns
        assert result["cas_positifs"].sum() == 25
    
    @patch('dengsurvab.client.requests.Session')
    def test_get_alertes(self, mock_session_class, client):
        """Test la récupération des alertes."""
        # Mock de la session
        mock_session = Mock()
        mock_session.get.return_value.status_code = 200
        mock_session.get.return_value.json.return_value = {
            "data": [
                {
                    "id": 1,
                    "severity": "critical",
                    "status": "active",
                    "message": "Seuil dépassé",
                    "region": "Antananarivo",
                    "created_at": "2024-01-15T10:30:00"
                },
                {
                    "id": 2,
                    "severity": "warning",
                    "status": "resolved",
                    "message": "Alerte résolue",
                    "region": "Toamasina",
                    "created_at": "2024-01-14T15:45:00"
                }
            ]
        }
        mock_session_class.return_value = mock_session
        
        # Test
        result = client.get_alertes(limit=10)
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2
        assert "severity" in result.columns
        assert "message" in result.columns
        assert result["severity"].iloc[0] == "critical"
    
    @patch('dengsurvab.client.requests.Session')
    def test_calculate_rates(self, mock_session_class, client):
        """Test le calcul des taux."""
        # Mock de la session
        mock_session = Mock()
        mock_session.get.return_value.status_code = 200
        mock_session.get.return_value.json.return_value = {
            "data": [
                {
                    "date_debut": "2024-01-01",
                    "date_fin": "2024-01-31",
                    "total_cas": 100,
                    "cas_positifs": 25,
                    "hospitalisations": 8,
                    "deces": 2
                }
            ]
        }
        mock_session_class.return_value = mock_session
        
        # Test
        result = client.calculate_rates(
            date_debut="2024-01-01",
            date_fin="2024-01-31"
        )
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert "taux_positivite" in result.columns
        assert "taux_hospitalisation" in result.columns
        assert "taux_letalite" in result.columns
    
    @patch('dengsurvab.client.requests.Session')
    def test_detect_anomalies(self, mock_session_class, client):
        """Test la détection d'anomalies."""
        # Créer des données de test
        test_data = pd.DataFrame({
            "cas_positifs": [10, 15, 8, 20, 12, 18, 25, 30, 22, 16],
            "hospitalisations": [2, 3, 1, 4, 2, 3, 5, 6, 4, 3]
        })
        
        # Test
        result = client.detect_anomalies(
            test_data,
            columns=["cas_positifs"],
            method="zscore"
        )
        
        assert isinstance(result, pd.DataFrame)
        assert "cas_positifs_anomaly" in result.columns
        assert len(result) == len(test_data)
    
    @patch('dengsurvab.client.requests.Session')
    def test_get_stats(self, mock_session_class, client):
        """Test la récupération des statistiques."""
        # Mock de la session
        mock_session = Mock()
        mock_session.get.return_value.status_code = 200
        mock_session.get.return_value.json.return_value = {
            "data": [
                {
                    "total_cas": 1000,
                    "cas_positifs": 250,
                    "hospitalisations": 80,
                    "deces": 5,
                    "regions_actives": ["Antananarivo", "Toamasina"]
                }
            ]
        }
        mock_session_class.return_value = mock_session
        
        # Test
        result = client.get_stats()
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 1
        assert "total_cas" in result.columns
        assert "cas_positifs" in result.columns
    
    @patch('dengsurvab.client.requests.Session')
    def test_verifier_alertes(self, mock_session_class, client):
        """Test la vérification des alertes."""
        # Mock de la session
        mock_session = Mock()
        mock_session.get.return_value.status_code = 200
        mock_session.get.return_value.json.return_value = {
            "alertes_detectees": [
                {
                    "type": "seuil_positivite",
                    "region": "Antananarivo",
                    "valeur": 25.5,
                    "seuil": 20.0
                }
            ],
            "total_alertes": 1
        }
        mock_session_class.return_value = mock_session
        
        # Test
        result = client.verifier_alertes(
            date_debut="2024-01-01",
            date_fin="2024-01-31"
        )
        
        assert isinstance(result, dict)
        assert "alertes_detectees" in result
        assert len(result["alertes_detectees"]) == 1
    
    def test_logout(self, client):
        """Test la déconnexion."""
        # Simuler une session authentifiée
        client.session.headers["Authorization"] = "Bearer test-token"
        
        # Test
        result = client.logout()
        
        assert result is True
        assert "Authorization" not in client.session.headers
    
    @patch('dengsurvab.client.requests.Session')
    def test_make_request_error(self, mock_session_class, client):
        """Test la gestion des erreurs de requête."""
        # Mock de la session
        mock_session = Mock()
        mock_session.get.return_value.status_code = 500
        mock_session.get.return_value.json.return_value = {
            "error": "Internal server error"
        }
        mock_session_class.return_value = mock_session
        
        # Test
        with pytest.raises(APIError):
            client._make_request("GET", "/api/test")
    
    @patch('dengsurvab.client.requests.Session')
    def test_make_request_authentication_error(self, mock_session_class, client):
        """Test la gestion des erreurs d'authentification."""
        # Mock de la session
        mock_session = Mock()
        mock_session.get.return_value.status_code = 401
        mock_session.get.return_value.json.return_value = {
            "error": "Unauthorized"
        }
        mock_session_class.return_value = mock_session
        
        # Test
        with pytest.raises(AuthenticationError):
            client._make_request("GET", "/api/test")
    
    def test_show_available_columns(self, client):
        """Test l'affichage des colonnes disponibles."""
        # Mock des méthodes de données
        with patch.object(client, 'donnees_par_periode') as mock_aggregated:
            mock_aggregated.return_value = pd.DataFrame({
                'cas_positifs': [10, 15, 20],
                'hospitalisations': [2, 3, 4],
                'deces': [0, 1, 0]
            })
            
            result = client.show_available_columns(use_aggregated=True)
            
            assert result["success"] is True
            assert "cas_positifs" in result["columns"]
            assert "hospitalisations" in result["columns"]
            assert result["data_type"] == "aggregated"
    
    # MIGRATION : Les fonctions resume/resume_display sont remplacées par resumer, graph_desc, evolution
    # @patch('dengsurvab.client.requests.Session')
    # def test_resume(self, mock_session_class, client):
    #     """Test la génération du résumé."""
    #     # Mock de la session
    #     mock_session = Mock()
    #     mock_session.get.return_value.status_code = 200
    #     mock_session.get.return_value.json.return_value = {
    #         "periode_couverture": {"debut": "2024-01-01", "fin": "2024-01-31"},
    #         "informations_generales": {"total_enregistrements": 1000},
    #         "variables": {
    #             "numeriques": {"cas_positifs": {"min": 0, "max": 50}},
    #             "qualitatives": {"region": {"valeurs_uniques": 5}}
    #         }
    #     }
    #     mock_session_class.return_value = mock_session
        
    #     # Test
    #     result = client.resume(limit=100)
        
    #     assert isinstance(result, dict)
    #     assert "periode_couverture" in result
    #     assert "informations_generales" in result
    #     assert "variables" in result 