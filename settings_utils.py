import shutil

def check_settings_file():
    try: # On essaie d'ouvrir le fichier paramètres
        settings_file = open('settings.json')
        settings_file.close()
    except FileNotFoundError: # En cas d'erreur, on en crée un nouveau en copiant "standard_settings.json"
        shutil.copyfile('standard/standard_settings.json', 'settings.json')