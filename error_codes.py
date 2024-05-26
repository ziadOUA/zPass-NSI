"""
88  88  88           error_codes.py
88  ""  88           
88      88           Dictionnaire des erreurs
88  88  88,dPPYba,   
88  88  88P'    "8a  Dépendants : main.py
88  88  88       d8  Dépendances : Aucune dépendance
88  88  88b,   ,a8"  
88  88  8Y"Ybbd8"'   
"""

# ═════════════════════════════════ FONCTIONS ════════════════════════════════

def get_error_codes_dictionary():
    return  {
                100 : ['INFO', 'VAULT ALREADY ENCRYPTED'],
                101 : ['INFO', 'VAULT ALREADY DECRYPTED'],
                102 : ['INFO', 'A VAULT WITH THE SAME NAME ALREADY EXISTS'],
                200 : ['INFO', 'OPERATION SUCCESSFUL'],
                400 : ['ERROR', 'WRONG MASTER PASSWORD'],
                401 : ['ERROR', 'WRONG VAULT CODE'],
                402 : ['ERROR', 'NO VAULT WAS FOUND']
            }
