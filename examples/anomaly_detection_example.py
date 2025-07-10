#!/usr/bin/env python3
"""
Exemple d'utilisation de la fonction detect_anomalies

Ce script montre comment utiliser la fonction detect_anomalies
pour identifier des valeurs anormales dans les données de dengue.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dengsurvab import AppiClient
import pandas as pd

def main():
    """Exemple principal d'utilisation de detect_anomalies."""
    
    # Initialiser le client
    client = AppiClient()
    
    print("=== Exemple de détection d'anomalies ===\n")
    
    # 1. Récupérer des données de dengue
    print("1. Récupération des données de dengue...")
    try:
        df = client.get_cas_dengue(annee=2024, mois=12)
        print(f"   Données récupérées: {len(df)} enregistrements")
        print(f"   Colonnes disponibles: {list(df.columns)}")
        
        if df.empty:
            print("   Aucune donnée disponible pour l'analyse")
            return
            
    except Exception as e:
        print(f"   Erreur lors de la récupération des données: {e}")
        return
    
    # 2. Détection d'anomalies avec la méthode Z-score
    print("\n2. Détection d'anomalies avec la méthode Z-score...")
    try:
        anomalies_zscore = client.detect_anomalies(df, method="zscore")
        
        # Afficher les colonnes d'anomalies ajoutées
        anomaly_cols = [col for col in anomalies_zscore.columns if col.endswith('_anomaly')]
        print(f"   Colonnes d'anomalies créées: {anomaly_cols}")
        
        # Compter les anomalies
        if 'total_anomalies' in anomalies_zscore.columns:
            total_anomalies = anomalies_zscore['total_anomalies'].sum()
            print(f"   Total d'anomalies détectées: {total_anomalies}")
            
            # Afficher les lignes avec anomalies
            anomalies_rows = anomalies_zscore[anomalies_zscore['has_anomalies'] == True]
            if not anomalies_rows.empty:
                print(f"   Lignes avec anomalies: {len(anomalies_rows)}")
                print("\n   Exemples d'anomalies détectées:")
                for idx, row in anomalies_rows.head(3).iterrows():
                    print(f"      - Ligne {idx}: {row.get('total_anomalies', 0)} anomalies")
        
    except Exception as e:
        print(f"   Erreur lors de la détection Z-score: {e}")
    
    # 3. Détection d'anomalies avec la méthode IQR
    print("\n3. Détection d'anomalies avec la méthode IQR...")
    try:
        anomalies_iqr = client.detect_anomalies(df, method="iqr")
        
        if 'total_anomalies' in anomalies_iqr.columns:
            total_anomalies = anomalies_iqr['total_anomalies'].sum()
            print(f"   Total d'anomalies détectées (IQR): {total_anomalies}")
            
            # Comparer avec Z-score
            if 'total_anomalies' in anomalies_zscore.columns:
                zscore_total = anomalies_zscore['total_anomalies'].sum()
                print(f"   Comparaison - Z-score: {zscore_total}, IQR: {total_anomalies}")
        
    except Exception as e:
        print(f"   Erreur lors de la détection IQR: {e}")
    
    # 4. Analyse spécifique de colonnes
    print("\n4. Analyse spécifique de colonnes...")
    try:
        # Analyser seulement certaines colonnes
        columns_to_analyze = ['total_cas', 'cas_positifs', 'hospitalisations']
        available_columns = [col for col in columns_to_analyze if col in df.columns]
        
        if available_columns:
            print(f"   Colonnes analysées: {available_columns}")
            specific_anomalies = client.detect_anomalies(
                df, 
                method="zscore", 
                columns=available_columns
            )
            
            # Afficher les détails des anomalies par colonne
            for col in available_columns:
                anomaly_col = f'{col}_anomaly'
                if anomaly_col in specific_anomalies.columns:
                    anomalies_count = specific_anomalies[anomaly_col].sum()
                    print(f"      - {col}: {anomalies_count} anomalies")
        else:
            print("   Aucune des colonnes spécifiées n'est disponible")
            
    except Exception as e:
        print(f"   Erreur lors de l'analyse spécifique: {e}")
    
    # 5. Affichage des résultats détaillés
    print("\n5. Résultats détaillés...")
    try:
        # Sélectionner les colonnes importantes pour l'affichage
        display_cols = ['date_debut', 'date_fin', 'region', 'district']
        anomaly_cols = [col for col in anomalies_zscore.columns if col.endswith('_anomaly')]
        
        # Combiner les colonnes d'affichage et d'anomalies
        all_display_cols = display_cols + anomaly_cols + ['total_anomalies', 'has_anomalies']
        available_display_cols = [col for col in all_display_cols if col in anomalies_zscore.columns]
        
        if available_display_cols:
            # Afficher les premières lignes avec anomalies
            anomalies_only = anomalies_zscore[anomalies_zscore['has_anomalies'] == True]
            if not anomalies_only.empty:
                print("   Premières anomalies détectées:")
                print(anomalies_only[available_display_cols].head(5).to_string(index=False))
            else:
                print("   Aucune anomalie détectée dans les données")
        
    except Exception as e:
        print(f"   Erreur lors de l'affichage des résultats: {e}")
    
    print("\n=== Fin de l'exemple ===")

if __name__ == "__main__":
    main() 