"""
88  88  88           vault_utils.py
88  ""  88           
88      88           Collection de fonctions pour la gestion des bases de données
88  88  88,dPPYba,   
88  88  88P'    "8a  Dépendants : main.py
88  88  88       d8  Dépendances : voir "Importations"
88  88  88b,   ,a8"  
88  88  8Y"Ybbd8"'   Notes : peut fonctionner tout seul, et pourra être utilisé pour une version dans la console de zPass
"""

# ═══════════════════════════════ IMPORTATIONS ═══════════════════════════════

import shutil
import os

from Crypto.Cipher import AES
from Crypto.Hash import HMAC, SHA256

# ═════════════════════════════════ FONCTIONS ════════════════════════════════

def does_vault_exist(name:str) -> bool: # Fonction permettant de vérifier si le coffre-fort existe déjà
    try: # On essaie d'ouvrir la base de données
        vault_file = open(f'vaults/{name}.zpdb')
        vault_file.close()
        return True # On retourne "True" pour indiquer que la base de données existe
    except FileNotFoundError:
        return False # En cas d'erreur, on retourne "False" pour indiquer que la base de données n'existe pas

def create_vault(name:str) -> int: # Fonction permettant de créer une nouvelle base de données
    if not does_vault_exist(name): # On vérifie qu'un coffre-fort du même nom n'existe pas déjà
        vault_file = open(f'vaults/{name}.zpdb', 'w')
        vault_file.write('{"vault_name":' + f'"{name}",' + '"entries": {}}') # On écrit la base du fichier
        vault_file.close() # On ferme le fichier pour éviter les problèmes

        shutil.copyfile(f'vaults/{name}.zpdb', '.temp_vault.zpdb') # On crée le fichier ".temp_vault.zpdb" à partir d'une copie
        return 200 # Succès de l'opération
    else:
        return 102 # Erreur 102 : Un coffre-fort avec le même nom éxiste déjà

def delete_vault(name:str, decrypted_vault_path='.temp_vault.zpdb') -> int: # Fonction permettant de supprimer un coffre-fort
    if does_vault_exist(name): # On vérifie si le coffre-fort que l'on essaie de supprimer éxiste
        os.remove(f'vaults/{name}.zpdb') # On supprime le fichier de la base de données
        try:
            os.remove(decrypted_vault_path) # On essaie de supprimer le fichier ".temp_vault.zpdb"
        except FileNotFoundError:
            pass # Si le fichier n'éxiste pas, on continue l'exécution normale du programme
        
        return 200 # Succès de l'opération
    else:
        return 402 # Erreur 402 : Le coffre-fort n'éxiste pas

def get_vault_data(path:str) -> bytes: # Fonction permettant de récupérer le contenu de la base de données chiffrée
    vault_file = open(path, 'rb') # On ouvre le coffre-fort en mode lecture binaire
    vault_data = vault_file.read()
    vault_file.close() # On ferme le fichier pour éviter les problèmes

    vault_data = vault_data.decode('latin-1').encode('utf-8') # Bidouille nécessaire au support caractères spéciaux

    return vault_data # On retroune les données du coffre-fort

# Fonction permettant de chiffrer la base de données
def encrypt_vault(name:str, master_password:bytes, vault_code:bytes, decrypted_vault_path='.temp_vault.zpdb') -> int:
    if not does_vault_exist(name): # On vérifie si le coffre-fort que l'on essaie de chiffrer éxiste
        return 402 # Erreur 402 : Le coffre-fort n'éxiste pas
    
    try: # On vérifie la présence du fichier temporaire
        decrypted_vault_file = open(decrypted_vault_path)
        decrypted_vault_file.close()
    except FileNotFoundError:
        return 100 # Erreur 100 : Le coffre-fort est déjà chiffré
    
    cipher = AES.new(master_password, AES.MODE_CTR) # On initialise le chiffrement
    vault_data = get_vault_data(decrypted_vault_path) # On récupère les données du coffre-fort déchiffré
    ciphertext = cipher.encrypt(vault_data) # On chiffre les données du coffre-fort

    hmac = HMAC.new(vault_code, digestmod=SHA256) # On initialise "hmac" qui permettra de vérifier l'intégrité des données
    nonce = cipher.nonce # Nombre aléatoire qui fera que les mêmes données chiffrées deux fois ne correspondront pas
    tag = hmac.update(nonce + ciphertext).digest() # On récupère "tag", qui sera utilisé pour vérifier l'intégrité des données

    with open(f'vaults/{name}.zpdb', 'wb') as vault_file: # On écrit toutes les données du coffre-fort
        vault_file.write(tag) # Permettra de vérifier l'intégrité des données
        vault_file.write(nonce) # Nombre aléatoire
        vault_file.write(ciphertext) # Mots de passe chiffrés
    
    os.remove(decrypted_vault_path) # On supprime le fichier temporaire

    return 200 # Succès de l'opération

# Fonction permettant de déchiffrer la base de données
def decrypt_vault(name:str, master_password:bytes, vault_code:bytes, decrypted_vault_path='.temp_vault.zpdb') -> int:
    if not does_vault_exist(name): # On vérifie si le coffre-fort que l'on essaie de déchiffrer éxiste
        return 402 # Erreur 402 : Le coffre-fort n'éxiste pas
    
    try: # On vérifie la présence du fichier temporaire
        decrypted_vault_file = open(decrypted_vault_path)
        decrypted_vault_file.close()

        return 101 # Erreur 101 : Le coffre-fort est déjà déchiffré
    except FileNotFoundError:
        pass # Le coffre-fort en question est bien chiffré, on continue l'exécution normale du programme
    
    with open(f'vaults/{name}.zpdb', 'rb') as vault_file:
        tag = vault_file.read(32) # On récupère "tag", situé dans les 32 premiers octets
        nonce = vault_file.read(8) # On récupère "nonce", situé dans les 8 octets suivants
        ciphertext = vault_file.read() # On récupère les mots de passe chiffrés dans le reste du fichier
    
    try:
        hmac = HMAC.new(vault_code, digestmod=SHA256) # On initialise la vérification d'intégrité des données
        tag = hmac.update(nonce + ciphertext).verify(tag) # On vérifie l'intégrité des données
    except ValueError:
        return 401 # Erreur 401 : Code d'authentification invalide, ou données endommagées
    
    cipher = AES.new(master_password, AES.MODE_CTR, nonce=nonce) # On initialise le déchiffrement
    try:
        message = cipher.decrypt(ciphertext).decode() # On essaie de déchiffrer les mots de passe
    except UnicodeDecodeError:
        return 400 # Erreur 400 : Mot de passe invalide

    with open(decrypted_vault_path, 'w') as vault_file:
        vault_file.write(message.replace('\r\n', '\n')) # On écrit les données déchiffrées au fichier temporaire

    return 200 # Succès de l'opération

# Fonction permettant de retourner un mot de passe dont la longueur est égale à une puissance de 2 supérieure à 16
def pad_master_password(master_password:str) -> bytes:
    padded_master_password_length = len(master_password)
    padded_master_password = master_password

    if len(padded_master_password) < 16: # Si la longueur du mot de passe est inférieure à 16
        while len(padded_master_password) < 16:
            padded_master_password += ' ' # On rajoute des espaces jusqu'à ce que la longueur soit égale à 16
        return bytes(padded_master_password, 'utf-8') # On retourne le mot de passe en format "bytes"

    done = False # Drapeau de fin d'opération
    next_power_of_two = 0 # On initialise la variable qui va contenir la prochaine puissance de 2
    
    while not done:
        padded_master_password_length /= 2 # Nous allons diviser par deux la longueur du mot de passe
        # Si le résultat est égal à 1, alors la longueur du mot de passe est déjà une puissance de 2
        if padded_master_password_length == 1: 
            done = True
            return bytes(padded_master_password, 'utf-8')
        elif padded_master_password_length < 1: # Si le résultat est inférieur à 1, on arrête
            done = True
        next_power_of_two += 1 # On ajoute 1 à "next_power_of_two" (prochaine puissance de 2)

    while len(padded_master_password) != 2**next_power_of_two:
        padded_master_password += ' ' # On rajoute des espaces jusqu'à ce que la longueur soit égale à 2^(next_power_of_two)
    
    return bytes(padded_master_password, 'utf-8') # On retourne le mot de passe en format "bytes"
