#!/usr/bin/env python3
"""
Exemple d'utilisation basique du client Appi Dengue

Ce script démontre les fonctionnalités principales du client :
- Authentification
- Récupération de données
- Gestion des alertes
- Export de données
- Analyses épidémiologiques
"""

import sys
import os
from datetime import datetime, timedelta

# Ajouter le répertoire parent au path pour importer le package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dengsurvab import AppiClient

def main():
    """Exemple d'utilisation basique du client."""
    
    print("🚀 EXEMPLE D'UTILISATION - CLIENT APPI DENGUE")
    print("=" * 60)
    
    # Configuration
    API_URL = "https://api.appi.com"  # Remplacez par votre URL
    EMAIL = "user@example.com"         # Remplacez par votre email
    PASSWORD = "password"               # Remplacez par votre mot de passe
    
    # Initialisation du client
    print("\n1. Initialisation du client...")
    try:
        client = AppiClient(API_URL)
        print(f"✅ Client initialisé avec l'URL: {API_URL}")
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation: {e}")
        return
    
    # Authentification
    print("\n2. Authentification...")
    try:
        success = client.authenticate(EMAIL, PASSWORD)
        if success:
            print("✅ Authentification réussie")
        else:
            print("❌ Échec de l'authentification")
            return
    except Exception as e:
        print(f"❌ Erreur lors de l'authentification: {e}")
        return
    
    # Vérification de la connexion
    print("\n3. Vérification de la connexion...")
    try:
        if client.is_authenticated():
            print("✅ Connexion active")
        else:
            print("❌ Connexion inactive")
            return
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return
    
    # Récupération des données de base
    print("\n4. Récupération des données de base...")
    try:
        # Données hebdomadaires (DataFrame)
        df_hebdo = client.get_cas_dengue(annee=2024, mois=1)
        print(f"📊 Données hebdomadaires récupérées: {len(df_hebdo)} semaines")
        
        if not df_hebdo.empty:
            print(f"   Total cas positifs: {df_hebdo['cas_positifs'].sum()}")
            print(f"   Moyenne par semaine: {df_hebdo['cas_positifs'].mean():.1f}")
            print(f"   Pic hebdomadaire: {df_hebdo['cas_positifs'].max()}")
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des données: {e}")
    
    # Récupération des statistiques
    print("\n5. Récupération des statistiques...")
    try:
        stats = client.get_stats()
        print(f"📈 Statistiques récupérées: {len(stats)} indicateurs")
        
        if not stats.empty:
            print(f"   Total cas: {stats['total_cas'].iloc[0] if 'total_cas' in stats.columns else 'N/A'}")
            print(f"   Total positifs: {stats['cas_positifs'].iloc[0] if 'cas_positifs' in stats.columns else 'N/A'}")
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des statistiques: {e}")
    
    # Récupération des indicateurs par période
    print("\n6. Récupération des indicateurs par période...")
    try:
        # Calculer les dates pour le dernier mois
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        indicateurs = client.donnees_par_periode(
            date_debut=start_date.strftime("%Y-%m-%d"),
            date_fin=end_date.strftime("%Y-%m-%d"),
            region="Toutes"
        )
        
        print(f"📈 Indicateurs hebdomadaires récupérés: {len(indicateurs)}")
        if not indicateurs.empty:
            latest = indicateurs.iloc[-1]
            print(f"   Dernière semaine: {latest.get('date_debut', 'N/A')} - {latest.get('date_fin', 'N/A')}")
            print(f"   Total cas: {latest.get('total_cas', 'N/A')}")
            print(f"   Taux positivité: {latest.get('taux_positivite', 'N/A')}")
            print(f"   Taux hospitalisation: {latest.get('taux_hospitalisation', 'N/A')}")
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des indicateurs: {e}")
    
    # Récupération des alertes
    print("\n7. Récupération des alertes...")
    try:
        df_alertes = client.get_alertes(limit=5)
        print(f"🚨 Alertes récupérées: {len(df_alertes)}")
        
        if not df_alertes.empty:
            for _, alerte in df_alertes.head(3).iterrows():
                print(f"   - {alerte.get('severity', 'N/A')}: {alerte.get('message', 'N/A')}")
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des alertes: {e}")
    
    # Export de données
    print("\n8. Export de données...")
    try:
        from dengsurvab import DataExporter
        exporter = DataExporter(client)
        
        # Export au format CSV
        csv_data = exporter.export_data(
            format="csv",
            date_debut=start_date.strftime("%Y-%m-%d"),
            date_fin=end_date.strftime("%Y-%m-%d"),
            limit=100
        )
        
        # Sauvegarder le fichier
        with open("donnees_dengue.csv", "wb") as f:
            f.write(csv_data)
        
        print(f"💾 Données exportées dans 'donnees_dengue.csv' ({len(csv_data)} bytes)")
    except Exception as e:
        print(f"❌ Erreur lors de l'export: {e}")
    
    # Analyse épidémiologique
    print("\n9. Analyse épidémiologique...")
    try:
        # Calculer les taux
        df_rates = client.calculate_rates(
            date_debut=(end_date - timedelta(days=30)).strftime("%Y-%m-%d"),
            date_fin=end_date.strftime("%Y-%m-%d")
        )
        
        print(f"📈 Taux calculés:")
        if not df_rates.empty:
            print(f"   - Positivité: {df_rates['taux_positivite'].iloc[0]:.1f}%")
            print(f"   - Hospitalisation: {df_rates['taux_hospitalisation'].iloc[0]:.1f}%")
            print(f"   - Létalité: {df_rates['taux_letalite'].iloc[0]:.1f}%")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'analyse: {e}")
    
    # Configuration des alertes
    print("\n10. Configuration des alertes...")
    try:
        # Configurer les seuils d'alerte
        config_result = client.configurer_seuils(
            seuil_positivite=15,
            seuil_hospitalisation=10,
            seuil_deces=5
        )
        
        print("✅ Seuils d'alerte configurés")
        print(f"   - Seuil positivité: 15%")
        print(f"   - Seuil hospitalisation: 10%")
        print(f"   - Seuil décès: 5%")
    except Exception as e:
        print(f"❌ Erreur lors de la configuration des alertes: {e}")
    
    # Résumé statistique
    print("\n11. Résumé statistique...")
    try:
        # MIGRATION : Les fonctions resume/resume_display sont remplacées par resumer, graph_desc, evolution
        # Exemple :
        # client.resumer(annee=2024, region="Centre")
        # client.graph_desc(date_debut="2024-01-01", date_fin="2024-12-31")
        # client.evolution(by="sexe", frequence="M", taux_croissance=True)
        resume = client.resumer(limit=100, annee=2024)
        print(f"📊 Résumé généré:")
        print(f"   - Total enregistrements: {resume['informations_generales']['total_enregistrements']}")
        print(f"   - Période couverture: {resume['periode_couverture']['debut']} à {resume['periode_couverture']['fin']}")
        print(f"   - Variables numériques: {len(resume['variables']['numeriques'])}")
        print(f"   - Variables qualitatives: {len(resume['variables']['qualitatives'])}")
    except Exception as e:
        print(f"❌ Erreur lors du résumé: {e}")
    
    print("\n=== Exemple terminé ===")
    print("📚 Consultez la documentation pour plus d'exemples et de fonctionnalités.")

if __name__ == "__main__":
    main() 