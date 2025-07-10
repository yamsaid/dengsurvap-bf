import sys
import os

# Ajouter le chemin du package dengsurvap-bf
current_dir = os.path.dirname(os.path.abspath(__file__))
#   dengsurvap_path = os.path.join(current_dir, 'dengsurvap-bf')
parent_dir = os.path.dirname(current_dir)  # Remonter d'un niveau depuis scripts/
sys.path.insert(0, parent_dir)
#sys.path.insert(0, dengsurvap_path)

from dengsurvab import AppiClient
from dengsurvab.analytics import SyntheseBase 
#import requests
import json
from datetime import datetime

# Définir la variable d'environnement

# Test de l'endpoint d'authentification
url = "https://api-bf-dengue-survey-production.up.railway.app/"
#url = "http://localhost:8000/login"

# Test avec différents formats
#client = AppiClient(url)
client = AppiClient.from_env()
client.authenticate("yamsaid74@gmail.com", "1122Aa")


'''cas = client.get_cas_dengue(
    annee=2024,
    mois=1,
    region="Centre"
)'''

"""print(client.get_cas_dengue(
    annee=2024,
    mois=1,
    region="Centre"
))"""


#print(client.get_stats())

#print(client.get_districts(region="Centre"))

'''print(client.get_taux_hospitalisation(
    date_debut="2024-01-01", 
    date_fin="2025-07-01",
    region="Centre"
))'''

"""print(client.get_taux_positivite(
    date_debut="2024-01-01", 
    date_fin="2025-07-01",
    region="Centre"
))"""

"""print(client.get_taux_letalite(
    date_debut="2024-01-01", 
    date_fin="2025-07-01",
   
))
"""

'''print(client.get_alertes(
    limit=10,
    
))'''
'''
print( client.configurer_seuils(
    seuil_positivite=20,
    seuil_hospitalisation=15,
    seuil_deces=2
))
'''
"""
print(client.verifier_alertes())
"""

#print(client.get_indicateurs_actuels()) a implementer
"""print(client.get_cas_dengue(
    date_debut="2024-01-01",
    date_fin="2025-07-01",
    region="Centre",
    district="Toutes",
    limit=100
))
"""


""" Test avec seulement les 3 premiers cas pour commencer
test_data = [
  {
   
    "sexe": "masculin",
    "age": 25,
    "region": "Centre",
    "date_consultation": "2024-01-15",
    "district": "DS Bogodogo",
    "resultat_test": "positif",
    "serotype": "denv2",
    "hospitalisation": True,
    "issue": "guéri",
    "id_source": 1
   
  }
  
]
print(f"Test avec {len(test_data)} cas de dengue...")
client.add_cas_dengue(test_data)
"""

"""
print(client.get_time_series(
    date_debut="2024-01-01",
    date_fin="2025-07-01",
    region="Centre",
    district="Toutes"
    
))"""
"""
print(client.data_period(
    date_debut="2024-01-01",
    date_fin="2025-07-01",
    region="Centre",
    district="Toutes",
    frequence="W"
))"""

#print(client.logout())

"""# Test de la fonction resume avec affichage professionnel
print("\n" + "="*50)
print("TEST DE LA FONCTION RESUME_DISPLAY")
print("="*50)

# Test de l'affichage professionnel
client.resume_display(verbose=True, show_details=True, graph=False)

print("\n" + "="*50)
print("TEST DE LA FONCTION RESUME_DISPLAY AVEC GRAPHIQUES")
print("="*50)

# Test de l'affichage avec graphiques
client.resume_display(verbose=True, show_details=True, graph=True)  
"""
"""
df = client.data(
    date_debut="2024-01-01",
    date_fin="2025-07-01",
    limit=20,
    page=1
)

print(df)"""
"""
client.save_to_file(
    date_debut="2024-01-01",
    date_fin="2025-07-01",
    limit=20,
    page=1
)
"""
"""client.alertes_to_file(limit=3)"""

#print(client.resume_display(limit=20, verbose=True, show_details=True, graph=True))

#print(client.calculate_rates(date_debut="2024-01-01", date_fin="2025-07-01"))

#print(client.donnees_par_periode(date_debut="2024-01-01", date_fin="2025-07-01"))

#print(client.donnees_par_periode(date_debut="2024-01-01", date_fin="2025-07-01", region="Centre"))

#print(client.resume_display(graph=True,max_graphs=4, use_aggregated=False))
synth = SyntheseBase(client=client)
df = client.data(date_debut="2024-01-01", date_fin="2025-07-01", region="Centre",limit=20)
#synth = SyntheseBase(df)

#print(synth.resumer(df=df))
#print(client.resumer(date_debut="2024-01-01", date_fin="2025-07-01", region="Centre",detail=True,limit=20))
#print(synth.graph_desc(date_debut="2024-01-01", date_fin="2025-07-01", region="Centre",detail=True,limit=20))
#ynth.graph_desc(date_debut="2024-01-01", date_fin="2025-07-01", region="Centre",limit=20, save_dir="./figures")
#synth.evolution(by='sexe',date_debut="2024-01-01", date_fin="2025-07-01", region="Centre",limit=20,max_graph=2)
#synth.evolution(df)

#print(synth._prepare_df(df))

