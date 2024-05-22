import shutil
import os
from Crypto.Cipher import AES
from Crypto.Hash import HMAC, SHA256
import io
import json


# Fonction qui se charge de vérifier si une base de données de mots de passe existe déjà
def does_vault_exist(path:str) -> bool:
    try:
        vault_file = open(path)
        vault_file.close()
        return True
    except FileNotFoundError:
        return False


# # Fonction qui se charge de créer une nouvelle base de données
# def create_vault(path='vault.zpdb'):
#     if not does_vault_exist(path):
#         shutil.copyfile('standard/standard_vault.zpdb', path)
#         shutil.copyfile('standard/standard_vault.zpdb', '.temp_vault.zpdb')
#         return 200
#     else:
#         return 102

# Fonction qui se charge de créer une nouvelle base de données
def create_vault(name:str) -> int: #TODO Nettoyer la fonction
    if not does_vault_exist(f'vaults/{name}.zpdb'):
        # shutil.copyfile('standard/standard_vault.zpdb', f'vaults/{name}.zpdb')
        vault_file = open(f'vaults/{name}.zpdb', 'w')
        vault_file.write('{}')
        vault_file.close()
        vault_file = open(f'vaults/{name}.zpdb', 'r')
        vault = json.load(vault_file)
        vault_file.close()
        vault.update({'vault_name': name, 'entries': {}})
        with open(f'vaults/{name}.zpdb', 'w') as vault_file:
            vault_file.write(json.dumps(vault, indent=4))
        
        shutil.copyfile(f'vaults/{name}.zpdb', '.temp_vault.zpdb')
        return 200
    else:
        return 102


# Fonction qui se charge de supprimer une base de données existante par son nom
def delete_vault(name:str, decrypted_vault_path='.temp_vault.zpdb') -> int:
    if does_vault_exist(f'vaults/{name}.zpdb'):
        os.remove(f'vaults/{name}.zpdb')
        try:
            os.remove(decrypted_vault_path)
        except FileNotFoundError:
            pass

        return 200
    else:
        return 402


# Fonction qui se charge de récupérer le contenu de la base de données chiffrée
def get_vault_data(path:str) -> bytes:
    vault_file = open(path, 'rb')
    vault_data = vault_file.read()
    vault_file.close()

    vault_data = vault_data.decode('latin-1').encode('utf-8')

    return vault_data


# Fonction qui se charge de chiffrer la base de données
def encrypt_vault(name:str, master_password:bytes, vault_code:bytes, decrypted_vault_path='.temp_vault.zpdb') -> int:
    try:
        encrypted_vault_file = open(f'vaults/{name}.zpdb')
        encrypted_vault_file.close()
    except FileNotFoundError:
        return 402
    
    try:
        decrypted_vault_file = open(decrypted_vault_path)
        decrypted_vault_file.close()
    except FileNotFoundError:
        return 100
    
    cipher = AES.new(master_password, AES.MODE_CTR)
    vault_data = get_vault_data(decrypted_vault_path)
    ciphertext = cipher.encrypt(vault_data)

    hmac = HMAC.new(vault_code, digestmod=SHA256)
    tag = hmac.update(cipher.nonce + ciphertext).digest()
    nonce = cipher.nonce

    with open(f'vaults/{name}.zpdb', 'wb') as vault_file:
        vault_file.write(tag)
        vault_file.write(nonce)
        vault_file.write(ciphertext)
    
    os.remove(decrypted_vault_path)

    return 200


# Fonction qui se charge de déchiffrer la base de données
def decrypt_vault(name:str, master_password:bytes, vault_code:bytes, decrypted_vault_path='.temp_vault.zpdb') -> int:
    if not does_vault_exist(f'vaults/{name}.zpdb'):
        return 402
    
    try:
        decrypted_vault_file = open(decrypted_vault_path)
        decrypted_vault_file.close()

        return 101
    except FileNotFoundError:
        pass
    
    with open(f'vaults/{name}.zpdb', 'rb') as vault_file:
        tag = vault_file.read(32)
        nonce = vault_file.read(8)
        ciphertext = vault_file.read()
    
    try:
        hmac = HMAC.new(vault_code, digestmod=SHA256)
        tag = hmac.update(nonce + ciphertext).verify(tag)
    except ValueError:
        return 401
    
    cipher = AES.new(master_password, AES.MODE_CTR, nonce=nonce)
    try:
        message = cipher.decrypt(ciphertext).decode()
    except UnicodeDecodeError:
        return 400

    with open(decrypted_vault_path, 'w') as vault_file:
        vault_file.write(message.replace('\r\n', '\n'))

    return 200


def pad_master_password(master_password:str) -> bytes:
    padded_master_password_length = len(master_password)
    padded_master_password = master_password

    if len(padded_master_password) < 16:
        while len(padded_master_password) < 16:
            padded_master_password += ' '
        return bytes(padded_master_password, 'utf-8')

    done = False
    next_power_of_two = 0
    
    while not done:
        padded_master_password_length /= 2
        if padded_master_password_length == 1:
            done = True
            return bytes(padded_master_password, 'utf-8')
        elif padded_master_password_length < 1:
            done = True
        next_power_of_two += 1

    while len(padded_master_password) != 2**next_power_of_two:
        padded_master_password += ' '
    
    return bytes(padded_master_password, 'utf-8')