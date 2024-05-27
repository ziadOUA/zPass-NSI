"""
88  88  88           settings_utils.py
88  ""  88           
88      88           Collection de fonctions pour la gestion du fichier paramètres
88  88  88,dPPYba,   
88  88  88P'    "8a  Dépendants : main.py
88  88  88       d8  Dépendances : voir "Importations"
88  88  88b,   ,a8"  
88  88  8Y"Ybbd8"'   
"""

# ═════════════════════════════════ FONCTIONS ════════════════════════════════

def check_settings_file():
    try: # On essaie d'ouvrir le fichier paramètres
        settings_file = open('settings.json')
        settings_file.close()
    except FileNotFoundError: # En cas d'erreur, on en crée un nouveau
        settings_file = open('settings.json', 'w') 
        settings_file.write('{"vaults": {},"use_dark_theme": false}')
