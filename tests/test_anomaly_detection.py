#!/usr/bin/env python3
"""
Tests pour la fonction detect_anomalies

Ce module teste la détection d'anomalies dans les données de dengue.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import sys
import os

# Ajouter le répertoire parent au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dengsurvab import AppiClient
from dengsurvab.exceptions import AnalysisError


class TestAnomalyDetection:
    """Tests pour la détection d'anomalies."""
    
    def setup_method(self):
        """Initialisation avant chaque test."""
        self.client = AppiClient()
        
        # Créer des données de test
        self.test_data = pd.DataFrame({
            'date_debut': pd.date_range('2024-01-01', periods=20, freq='W'),
            'date_fin': pd.date_range('2024-01-07', periods=20, freq='W'),
            'region': ['Centre'] * 20,
            'district': ['Ouagadougou'] * 20,
            'total_cas': [10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 
                          60, 65, 70, 75, 80, 85, 90, 95, 100, 200],  # 200 est une anomalie
            'cas_positifs': [5, 8, 12, 15, 18, 22, 25, 28, 32, 35,
                            38, 42, 45, 48, 52, 55, 58, 62, 65, 150],  # 150 est une anomalie
            'hospitalisations': [2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
                               12, 13, 14, 15, 16, 17, 18, 19, 20, 50],  # 50 est une anomalie
            'deces': [0, 0, 1, 1, 1, 1, 2, 2, 2, 2,
                     3, 3, 3, 3, 4, 4, 4, 4, 5, 10]  # 10 est une anomalie
        })
    
    def test_detect_anomalies_empty_dataframe(self):
        """Test avec un DataFrame vide."""
        empty_df = pd.DataFrame()
        result = self.client.detect_anomalies(empty_df)
        
        assert result.empty
        assert len(result) == 0
    
    def test_detect_anomalies_zscore_method(self):
        """Test de la méthode Z-score."""
        result = self.client.detect_anomalies(self.test_data, method="zscore")
        
        # Vérifier que les colonnes d'anomalies sont ajoutées
        expected_anomaly_cols = ['total_cas_anomaly', 'cas_positifs_anomaly', 
                                'hospitalisations_anomaly', 'deces_anomaly']
        
        for col in expected_anomaly_cols:
            assert col in result.columns
        
        # Vérifier que les colonnes de z-score sont ajoutées
        expected_zscore_cols = ['total_cas_zscore', 'cas_positifs_zscore', 
                               'hospitalisations_zscore', 'deces_zscore']
        
        for col in expected_zscore_cols:
            assert col in result.columns
        
        # Vérifier que les colonnes de résumé sont ajoutées
        assert 'total_anomalies' in result.columns
        assert 'has_anomalies' in result.columns
        
        # Vérifier que les anomalies sont détectées (dernière ligne avec valeurs élevées)
        assert result.iloc[-1]['total_cas_anomaly'] == True
        assert result.iloc[-1]['cas_positifs_anomaly'] == True
        assert result.iloc[-1]['hospitalisations_anomaly'] == True
        assert result.iloc[-1]['deces_anomaly'] == True
    
    def test_detect_anomalies_iqr_method(self):
        """Test de la méthode IQR."""
        result = self.client.detect_anomalies(self.test_data, method="iqr")
        
        # Vérifier que les colonnes d'anomalies sont ajoutées
        expected_anomaly_cols = ['total_cas_anomaly', 'cas_positifs_anomaly', 
                                'hospitalisations_anomaly', 'deces_anomaly']
        
        for col in expected_anomaly_cols:
            assert col in result.columns
        
        # Vérifier que les colonnes de bornes IQR sont ajoutées
        expected_iqr_cols = ['total_cas_iqr_lower', 'total_cas_iqr_upper',
                            'cas_positifs_iqr_lower', 'cas_positifs_iqr_upper',
                            'hospitalisations_iqr_lower', 'hospitalisations_iqr_upper',
                            'deces_iqr_lower', 'deces_iqr_upper']
        
        for col in expected_iqr_cols:
            assert col in result.columns
        
        # Vérifier que les colonnes de résumé sont ajoutées
        assert 'total_anomalies' in result.columns
        assert 'has_anomalies' in result.columns
    
    def test_detect_anomalies_specific_columns(self):
        """Test avec des colonnes spécifiques."""
        columns_to_analyze = ['total_cas', 'cas_positifs']
        result = self.client.detect_anomalies(
            self.test_data, 
            method="zscore", 
            columns=columns_to_analyze
        )
        
        # Vérifier que seules les colonnes spécifiées sont analysées
        expected_anomaly_cols = ['total_cas_anomaly', 'cas_positifs_anomaly']
        unexpected_anomaly_cols = ['hospitalisations_anomaly', 'deces_anomaly']
        
        for col in expected_anomaly_cols:
            assert col in result.columns
        
        for col in unexpected_anomaly_cols:
            assert col not in result.columns
    
    def test_detect_anomalies_invalid_method(self):
        """Test avec une méthode invalide."""
        with pytest.raises(AnalysisError, match="Méthode de détection non supportée"):
            self.client.detect_anomalies(self.test_data, method="invalid_method")
    
    def test_detect_anomalies_no_numeric_columns(self):
        """Test avec un DataFrame sans colonnes numériques."""
        non_numeric_df = pd.DataFrame({
            'region': ['Centre'] * 10,
            'district': ['Ouagadougou'] * 10,
            'status': ['active'] * 10
        })
        
        result = self.client.detect_anomalies(non_numeric_df)
        
        # Le DataFrame original devrait être retourné sans modification
        assert len(result.columns) == len(non_numeric_df.columns)
        assert 'total_anomalies' not in result.columns
    
    def test_detect_anomalies_isolation_forest_method(self):
        """Test de la méthode Isolation Forest."""
        # Mock pour simuler l'absence de scikit-learn
        with patch('builtins.__import__') as mock_import:
            mock_import.side_effect = ImportError("No module named 'sklearn'")
            
            # Devrait fallback vers zscore
            result = self.client.detect_anomalies(self.test_data, method="isolation_forest")
            
            # Vérifier que le fallback fonctionne
            assert 'total_cas_anomaly' in result.columns
            assert 'total_anomalies' in result.columns
    
    def test_detect_anomalies_with_nan_values(self):
        """Test avec des valeurs NaN."""
        data_with_nan = self.test_data.copy()
        data_with_nan.loc[0, 'total_cas'] = np.nan
        data_with_nan.loc[1, 'cas_positifs'] = np.nan
        
        result = self.client.detect_anomalies(data_with_nan, method="zscore")
        
        # Vérifier que le traitement des NaN fonctionne
        assert 'total_cas_anomaly' in result.columns
        assert 'cas_positifs_anomaly' in result.columns
        assert 'total_anomalies' in result.columns
    
    def test_detect_anomalies_summary_statistics(self):
        """Test des statistiques de résumé."""
        result = self.client.detect_anomalies(self.test_data, method="zscore")
        
        # Vérifier que les statistiques sont cohérentes
        total_anomalies = result['total_anomalies'].sum()
        has_anomalies_count = result['has_anomalies'].sum()
        
        assert total_anomalies >= 0
        assert has_anomalies_count >= 0
        assert has_anomalies_count <= len(result)
        
        # Vérifier que les lignes avec des anomalies ont has_anomalies=True
        anomalies_rows = result[result['has_anomalies'] == True]
        for _, row in anomalies_rows.iterrows():
            assert row['total_anomalies'] > 0
    
    def test_detect_anomalies_data_integrity(self):
        """Test de l'intégrité des données originales."""
        original_columns = set(self.test_data.columns)
        result = self.client.detect_anomalies(self.test_data, method="zscore")
        
        # Vérifier que toutes les colonnes originales sont préservées
        for col in original_columns:
            assert col in result.columns
        
        # Vérifier que les données originales ne sont pas modifiées
        for col in original_columns:
            pd.testing.assert_series_equal(
                self.test_data[col], 
                result[col], 
                check_names=False
            )


if __name__ == "__main__":
    pytest.main([__file__]) 