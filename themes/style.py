"""
88  88  88           style.py
88  ""  88           
88      88           Fonction servant à générer la feuille de style CSS qui sera appliquée au programme
88  88  88,dPPYba,   
88  88  88P'    "8a  Dépendants : main.py
88  88  88       d8  Dépendances : Aucune dépendance
88  88  88b,   ,a8"  
88  88  8Y"Ybbd8"'   Notes : Les variables CSS standard (--variable: 10px) ne fonctionnent pas avec l'implémentation CSS de Qt,
                             il nous faut donc utiliser une méthode customisée. L'implémentation sera la suivante :
                             $variable = valeur;
                             Exemple : $md_sys_color_tertiary = rgb(58, 101, 111);
"""

# ═════════════════════════════════ FONCTIONS ════════════════════════════════

def get_style_sheet(path='./themes/style.css', dark_theme=False) -> str:
    stylesheet = open(path).read() # On lit le fichier CSS

    colors_path = './themes/light/colors.txt' if not dark_theme else './themes/dark/colors.txt'

    colors = open(colors_path) # On ouvre le fichier contenant la palette de couleurs
    colors_list = [] # On initialise la liste "colors_list"
    colors_dictionary = dict() # On initialise le dictionnaire "colors_dictionary"

    for line in colors.readlines():
        colors_list.append(line.strip()) # On ajoute chaque ligne (sans saut de ligne) du fichier à la liste

    for color in colors_list:
        split_color = color.split(' = ') # On divise les variables de leurs valeurs
        colors_dictionary[split_color[0]] = split_color[1] # split_color[0] contient la variable, split_color[1] sa valeur

    for variable in colors_dictionary:
        # On cherche et remplace chaque variable dans le fichier CSS par la valeur définie
        stylesheet = stylesheet.replace(f'{variable};', colors_dictionary[variable]) 
    
    return stylesheet
