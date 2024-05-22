"""
          88                     88  Projet : zPass
          ""                     88  But : Créer un gestionnaire de mots de passe
                                 88  Création : 04/04/2024
888888888 88 ,adPPYYba,  ,adPPYb,88  
     a8P" 88 ""     `Y8 a8"    `Y88  
  ,d8P'   88 ,adPPPPP88 8b       88  
,d8"      88 88,    ,88 "8a,   ,d88  GitHub : 
888888888 88 `"8bbdP"88  `"8bbdP"88  GPLv3 - NSI
"""

# ═══════════════════════════════ IMPORTATIONS ═══════════════════════════════

import sys
import os
import string
import json
import random
import time

from vault_utils import create_vault, delete_vault, encrypt_vault, decrypt_vault, pad_master_password
from themes.style import get_style_sheet
from settings_utils import check_settings_file
from error_codes import get_error_codes_dictionnary

from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLineEdit, QLabel, QMessageBox, QVBoxLayout,
                               QHBoxLayout, QWidget, QScrollArea, QSplitter, QFrame, QMenuBar, QMenu, QToolBar, QComboBox,
                               QFileDialog)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPixmap, QAction, QClipboard, QImageReader, QIcon, QFontDatabase

# ════════════════════════════════════════════════════════════════════════════
# ════════════════════════════ CORPS DU PROGRAMME ════════════════════════════
# ════════════════════════════════════════════════════════════════════════════

# ══════════ Fichier paramètres
# NB : Le fichier paramètres est un fichier au format JSON (JavaScript Object Notation)
#      La fonction json.load() récupère les données d'un fichier .json pour renvoyer un 
#      dictionnaire

check_settings_file() # On vérifie la présence du fichier paramètres (settings.json)
settings_file = open('settings.json', 'r') # On ouvre le fichier paramètres
settings = json.load(settings_file) # On charge les données du fichier paramètres
settings_file.close() # On ferme le fichier paramètres pour éviter les problèmes

if settings['vaults'] == {}: # "has_already_created_a_vault" dépend de si un coffre a déjà été créé ou pas
    has_already_created_a_vault = False
else:
    has_already_created_a_vault = True

# ══════════ Variables & Constantes

version = '0.1.3-beta' # Version du programme

last_correct_master_password = b'' # On garde le dernier mot de passe correct pour pouvoir vérouiller le coffre en quittant
last_correct_vault_code = b'' # On garde le dernier code de coffre correct pour pouvoir vérouiller le coffre en quittant
error_codes_dictionnary = get_error_codes_dictionnary() # On récupère le dictionnaire qui contient les codes d'erreurs

selected_vault = '' # Nom du coffre sélectionné
selected_entry = None # Index de l'entrée séléctionnée, None car aucune ne l'est

# ══════════ Classe principale


class zPass(QMainWindow):
    def __init__(self):
        super().__init__()

        minimum_width = 720 # Largeur minimum de la fenêtre
        minimum_height = 550 # Hauteur minimum de la fenêtre

        self.setWindowIcon(QIcon('./themes/logo_64.png')) # Icône de la fenêtre
        self.setWindowTitle('zPass') # On met le titre de la fenêtre
        self.setMinimumSize(QSize(minimum_width, minimum_height)) # On fixe la taille minimum de la fenêtre

        self.launch_checks() # On appelle la fonction qui vérifie si le programme a été fermé correctement
        self.init_ui() # On appelle la fonction qui initialise l'IU

    def init_ui(self):
        global decrypt_action, encrypt_action, delete_vault_action, new_vault_action
        global new_entry_action, remove_entry_action, modify_entry_action

        # ════════════════════ Barre de menu ════════════════════
        
        menu_bar = QMenuBar(self)

        # ══════════ Menus de la barre de menu
        
        vault_menu = QMenu('Coffre fort')
        entries_menu = QMenu('Entrées')
        tools_menu = QMenu('Outils')
        help_menu = QMenu('Aide')

        # ══════════ Actions du menu "Coffre fort"
        
        decrypt_action = QAction('Déchiffrer le coffre fort', self)
        decrypt_action.triggered.connect(self.decrypt_button_clicked)
        decrypt_action.setIcon(QIcon('./themes/light/lock_open.png'))
        
        encrypt_action = QAction('Chiffrer le coffre fort', self)
        encrypt_action.triggered.connect(self.encrypt_button_clicked)
        encrypt_action.setIcon(QIcon('./themes/light/lock.png'))
        
        new_vault_action = QAction('Nouveau coffre fort', self)
        new_vault_action.triggered.connect(self.show_vault_creation_ui)
        new_vault_action.setIcon(QIcon('./themes/light/add.png'))
        
        delete_vault_action = QAction('Supprimer le coffre fort', self)
        delete_vault_action.triggered.connect(self.delete_vault_button_clicked)
        delete_vault_action.setIcon(QIcon('./themes/light/delete.png'))
        
        leave_action = QAction('Quitter zPass', self)
        leave_action.triggered.connect(self.exit_zPass)
        leave_action.setIcon(QIcon('./themes/light/leave.png'))

        vault_menu.addActions([decrypt_action, encrypt_action])
        vault_menu.addSeparator()
        vault_menu.addActions([new_vault_action, delete_vault_action])
        vault_menu.addSeparator()
        vault_menu.addActions([leave_action])

        # ══════════ Actions du menu "Entrées"
        
        new_entry_action = QAction('Nouvelle entrée...', self)
        new_entry_action.triggered.connect(self.new_entry_action_clicked)
        new_entry_action.setIcon(QIcon('./themes/light/add.png'))
        
        modify_entry_action = QAction('Modifier l\'entrée', self)
        modify_entry_action.triggered.connect(self.modify_entry_action_clicked)
        modify_entry_action.setIcon(QIcon('./themes/light/edit.png'))

        remove_entry_action = QAction('Supprimer l\'entrée...', self)
        remove_entry_action.triggered.connect(self.remove_entry_action_clicked)
        remove_entry_action.setIcon(QIcon('./themes/light/delete.png'))

        entries_menu.addActions([new_entry_action, modify_entry_action, remove_entry_action])

        # ══════════ Actions du menu "Outils"
        
        generate_password_action = QAction('Générateur de mot de passe', self)
        generate_password_action.setIcon(QIcon('./themes/light/dice.png'))

        tools_menu.addActions([generate_password_action])

        # ══════════ Actions du menu "Aide"
        
        about_action = QAction('À propos', self)
        about_action.triggered.connect(self.about_action)
        about_action.setIcon(QIcon('./themes/light/info.png'))

        help_menu.addActions([about_action])

        menu_bar.addMenu(vault_menu)
        menu_bar.addMenu(entries_menu)
        menu_bar.addMenu(tools_menu)
        menu_bar.addMenu(help_menu)

        self.setMenuBar(menu_bar)

        # ════════════════════ Barre d'actions  ════════════════════
        
        toolbar_container = QWidget()
        toolbar_container.setFixedHeight(50)
        toolbar_container.setContentsMargins(9, 9, 9, 0)

        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(0)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)

        toolbar_background = QWidget()
        toolbar_background.setContentsMargins(3, 0, 0, 0)
        toolbar_background.setObjectName('toolbar_background')

        toolbar_background_layout = QHBoxLayout()
        toolbar_background_layout.setSpacing(0)
        toolbar_background_layout.setContentsMargins(0, 0, 0, 0)

        toolbar_background.setLayout(toolbar_background_layout)

        toolbar = QToolBar('Barre d\'actions')
        toolbar.setFixedHeight(40)
        toolbar.setMovable(False)

        toolbar.addActions([decrypt_action, encrypt_action])
        toolbar.addSeparator()
        toolbar.addActions([new_entry_action, modify_entry_action, remove_entry_action])

        toolbar_background_layout.addWidget(toolbar)

        toolbar_layout.addWidget(toolbar_background)
        toolbar_container.setLayout(toolbar_layout)

        # ════════════════════

        self.root_container = QWidget() # Contenant racine de la fenêtre, contiendra "main_container" et la barre d'actions
        self.root_container.setContentsMargins(0, 0, 0, 0)
        self.root_layout = QVBoxLayout()
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)
        self.root_container.setLayout(self.root_layout)

        self.main_container = QWidget() # Élément qui sera directement affecté comme widget principal de la fenêtre
        self.main_layout = QVBoxLayout() # On crée un contenant principal pour tous les éléments d'interface
        self.main_layout.setAlignment(Qt.AlignHCenter) # On centre dans "main_layout" tout ce qui ne prend pas toute la place

        self.root_layout.addWidget(toolbar_container) # On ajoute à l'interface la barre d'actions
        self.root_layout.addWidget(self.main_container) # on ajoute le contenant principal "main_container"

        self.init_decrypt_vault_ui() # On appelle ces fonctions pour créer tous les éléments qui s'y rapportent
        self.init_new_vault_creation_ui()
        self.init_passwords_ui()

        if has_already_created_a_vault:
            self.show_vault_decrypt_ui() # Si un coffre existe déjà, on montre l'interface de déchiffrement
        else:
            self.show_vault_creation_ui() # Si aucun coffre n'est détecté, on montre l'interface de création de coffre

        self.main_container.setLayout(self.main_layout) # On définit "main_layout" comme mise en page de "main_container"
        self.setCentralWidget(self.root_container) # "root_container", contenant à présent tout les éléments nécessaires

    def about_action(self):
        self.create_dialog('zPass', f'zPass {version}\n© 2024 ziadOUA')
    
    def init_decrypt_vault_ui(self):
        global selected_vault

        # ═ RACINE ══ decrypt_vault_root & decrypt_vault_layout : Contenant principal

        self.decrypt_vault_root = QWidget()
        self.decrypt_vault_root.setFixedSize(QSize(700, 350))
        self.decrypt_vault_root.setObjectName('panel')

        decrypt_vault_layout = QVBoxLayout()
        decrypt_vault_layout.setContentsMargins(20, 20, 20, 20)
        
        # ═══════════---> zPass_logo_container : Contient le logo & le nom du logiciel
        
        zPass_logo_container = QHBoxLayout()

        # ═══════════--->---> zPass_logo : Logo du logiciel

        zPass_logo = QLabel() # On crée un contenant pour l'image
        zPass_logo.setFixedSize(QSize(64, 64))
        zPass_icon = QPixmap('./themes/logo.png').scaled(QSize(64, 64), mode=Qt.SmoothTransformation, aspectMode=Qt.KeepAspectRatio)
        zPass_logo.setPixmap(zPass_icon)

        # ═══════════--->---> zPass_label : Texte contenant le nom du logiciel

        zPass_label = QLabel()
        zPass_label.setFixedHeight(64)
        zPass_label.setText('zPass')
        zPass_label.setObjectName('zPass_label')

        zPass_logo_container.addWidget(zPass_logo) # Ajout des éléments
        zPass_logo_container.addWidget(zPass_label)
        
        # ═══════════---> vault_selection_layout : Contient la liste déroulante permettant de choisir le coffre à déchiffrer
        
        vault_selection_layout = QHBoxLayout()
        
        # ═══════════--->---> decrypt_label : Texte contenant l'action qui est sur le point d'être réalisée
        
        decrypt_label = QLabel()
        decrypt_label.setText('Déverouillage du coffre fort')
        decrypt_label.setStyleSheet('color: grey')
        
        # ═══════════--->---> vault_selection_dropdown : Liste déroulante permettant de choisir le coffre à déchiffrer
        
        self.vault_selection_dropdown = QComboBox()
        vault_list = self.list_available_vaults() # On obtient la liste des coffres forts existants
        self.vault_selection_dropdown.addItems(vault_list) # On ajoute les coffres à la liste déroulante
        self.vault_selection_dropdown.currentTextChanged.connect(self.get_selected_vault_name)

        vault_selection_layout.addWidget(decrypt_label, 4) # Ajout des éléments
        vault_selection_layout.addWidget(self.vault_selection_dropdown, 2)
        
        # ═══════════---> enter_master_password_label
        
        enter_master_password_label = QLabel()
        enter_master_password_label.setText('Mot de passe principal')
        enter_master_password_label.setObjectName('m_label')
        
        # ═══════════---> master_password_text_box_layout
        
        master_password_text_box_layout = QHBoxLayout()
        
        # ═══════════--->---> master_password_text_box : Champ pour la saisie du mot de passe principal
        
        self.master_password_text_box = QLineEdit(self)
        self.master_password_text_box.setEchoMode(QLineEdit.Password) # Le champ affiche "●●●●●" lors de la saisie
        self.master_password_text_box.setFixedHeight(28)
        
        # ═══════════--->---> show_master_password_button : Bouton qui servira à afficher le mot de passe principal
        
        self.show_master_password_button = QPushButton()
        self.show_master_password_button.setIcon(QIcon('./themes/light/visibility_off.png'))
        self.show_master_password_button.setCheckable(True)
        self.show_master_password_button.clicked.connect(lambda *args, arg1=self.master_password_text_box, arg2=self.show_master_password_button: self.toggle_echo_mode(arg1, arg2))
        self.show_master_password_button.setMaximumSize(QSize(28, 28))
        self.show_master_password_button.setObjectName('checkable')

        master_password_text_box_layout.addWidget(self.master_password_text_box) # Ajout des éléments
        master_password_text_box_layout.addWidget(self.show_master_password_button)

        # ═══════════---> wrong_master_password_label : Texte indiquant à l'utilisateur qu'il y a une erreur dans la saisie

        self.wrong_master_password_label = QLabel()
        self.wrong_master_password_label.setText('Mot de passe invalide')
        self.wrong_master_password_label.setStyleSheet('color: transparent')
        self.wrong_master_password_label.setObjectName('wrong_input')

        # On vérifie la validité du mot de passe principal lors de la saisie
        self.master_password_text_box.textChanged.connect(lambda *args, arg1=self.master_password_text_box, arg2=self.wrong_master_password_label: self.check_master_password_validity(arg1, arg2))
        
        # ═══════════---> enter_vault_code_label
        
        enter_vault_code_label = QLabel()
        enter_vault_code_label.setText('Code d\'authentification')
        enter_vault_code_label.setObjectName('m_label')

        # ═══════════---> vault_code_text_box_layout
        
        vault_code_text_box_layout = QHBoxLayout()
        
        # ═══════════--->---> vault_code_text_box : Champ pour la saisie du code d'authentification
        
        self.vault_code_text_box = QLineEdit(self)
        self.vault_code_text_box.setEchoMode(QLineEdit.Password) # Le champ affiche ●●●●● lors de la saisie
        self.vault_code_text_box.setFixedHeight(28)
        
        # ═══════════--->---> show_vault_code_button : Bouton qui servira à afficher le code d'authentification
        
        self.show_vault_code_button = QPushButton()
        self.show_vault_code_button.setIcon(QIcon('./themes/light/visibility_off.png'))
        self.show_vault_code_button.setCheckable(True)
        self.show_vault_code_button.clicked.connect(lambda *args, arg1=self.vault_code_text_box, arg2=self.show_vault_code_button: self.toggle_echo_mode(arg1, arg2))
        self.show_vault_code_button.setMaximumSize(QSize(28, 28))
        self.show_vault_code_button.setObjectName('checkable')

        vault_code_text_box_layout.addWidget(self.vault_code_text_box) # Ajout des éléments
        vault_code_text_box_layout.addWidget(self.show_vault_code_button)

        # ═══════════---> wrong_vault_code_label : Texte indiquant à l'utilisateur qu'il y a une erreur dans la saisie

        self.wrong_vault_code_label = QLabel()
        self.wrong_vault_code_label.setText('Code de coffre invalide')
        self.wrong_vault_code_label.setStyleSheet('color: transparent')
        self.wrong_vault_code_label.setObjectName('wrong_input')

        # On vérifie la validité du code de coffre lors de la saisie
        self.vault_code_text_box.textChanged.connect(lambda *args, arg1=self.vault_code_text_box, arg2=self.wrong_vault_code_label: self.check_vault_code_validity(arg1, arg2))
        
        # ═══════════---> actions_layout : Contiendra les boutons d'actions
        
        actions_layout = QHBoxLayout()
        
        # ═══════════--->---> decrypt_button : Bouton qui servira à déchiffrer le coffre
        
        decrypt_button = QPushButton('Déchiffrer', self)
        decrypt_button.clicked.connect(self.decrypt_button_clicked)
        
        # ═══════════--->---> close_button : Bouton pour quitter le programme
        
        close_button = QPushButton('Quitter', self)
        close_button.clicked.connect(self.exit_zPass)
        close_button.setObjectName('red_button')

        actions_layout.addStretch() # On ajoute un espace pour aligner les boutons à droite
        actions_layout.addWidget(decrypt_button) # Ajout des éléments
        actions_layout.addWidget(close_button)

        decrypt_vault_layout.addLayout(zPass_logo_container) # Ajout des éléments
        decrypt_vault_layout.addLayout(vault_selection_layout)
        decrypt_vault_layout.addWidget(enter_master_password_label)
        decrypt_vault_layout.addLayout(master_password_text_box_layout)
        decrypt_vault_layout.addWidget(self.wrong_master_password_label)
        decrypt_vault_layout.addWidget(enter_vault_code_label)
        decrypt_vault_layout.addLayout(vault_code_text_box_layout)
        decrypt_vault_layout.addWidget(self.wrong_vault_code_label)
        decrypt_vault_layout.addLayout(actions_layout)

        self.decrypt_vault_root.setLayout(decrypt_vault_layout)

        self.main_layout.addWidget(self.decrypt_vault_root) # Ajout de "decrypt_vault_root" au contenant principal "main_layout"

    def init_new_vault_creation_ui(self):
        global new_vault_cancel_button

        # ═ RACINE ══ new_vault_creation_root & new_vault_creation_layout : Contenant principal

        self.new_vault_creation_root = QWidget()
        self.new_vault_creation_root.setMinimumSize(QSize(700, 450))
        self.new_vault_creation_root.setFixedSize(QSize(700, 450))
        self.new_vault_creation_root.setObjectName('panel')
        
        new_vault_creation_layout = QVBoxLayout()
        new_vault_creation_layout.setContentsMargins(20, 20, 20, 20)

        # ═══════════---> zPass_logo_container : Contient le logo & le nom du logiciel

        zPass_logo_container = QHBoxLayout()

        # ═══════════--->---> zPass_logo : Logo du logiciel

        zPass_logo = QLabel()
        zPass_logo.setFixedSize(QSize(64, 64))
        zPass_icon = QPixmap('./themes/logo.png').scaled(QSize(64, 64), mode=Qt.SmoothTransformation, aspectMode=Qt.KeepAspectRatio)
        zPass_logo.setPixmap(zPass_icon)

        # ═══════════--->---> zPass_label : Texte contenant le nom du logiciel

        zPass_label = QLabel()
        zPass_label.setFixedHeight(64)
        zPass_label.setText('zPass')
        zPass_label.setObjectName('zPass_label')

        zPass_logo_container.addWidget(zPass_logo) # Ajout des éléments
        zPass_logo_container.addWidget(zPass_label)

        # ═══════════--->---> new_vault_label : Texte contenant l'action qui est sur le point d'être réalisée

        new_vault_label = QLabel()
        new_vault_label.setText('Création du coffre fort')
        new_vault_label.setStyleSheet('color: grey')

        # ═══════════---> enter_vault_name_label

        enter_vault_name_label = QLabel()
        enter_vault_name_label.setText('Nom du coffre fort')
        enter_vault_name_label.setObjectName('m_label')

        # ═══════════---> vault_name_text_box : Champ pour la saisie du nom de coffre

        self.vault_name_text_box = QLineEdit(self)
        self.vault_name_text_box.textChanged.connect(self.check_vault_name_validity)
        self.vault_name_text_box.setFixedHeight(28)

        # ═══════════---> wrong_vault_name_label : Texte indiquant à l'utilisateur qu'il y a une erreur dans la saisie 

        self.wrong_vault_name_label = QLabel()
        self.wrong_vault_name_label.setText('Nom déjà éxistant')
        self.wrong_vault_name_label.setStyleSheet('color: transparent')
        self.wrong_vault_name_label.setObjectName('wrong_input')

        # ═══════════---> enter_master_password_label

        enter_master_password_label = QLabel()
        enter_master_password_label.setText('Mot de passe principal')
        enter_master_password_label.setObjectName('m_label')

        # ═══════════---> master_password_text_box_layout

        master_password_text_box_layout = QHBoxLayout()

        # ═══════════--->---> new_master_password_text_box : Champ pour la saisie du mot de passe principal

        self.new_master_password_text_box = QLineEdit(self)
        self.new_master_password_text_box.setEchoMode(QLineEdit.Password)
        self.new_master_password_text_box.setFixedHeight(28)

        # ═══════════--->---> show_new_master_password_button : Bouton qui servira à afficher le mot de passe principal

        self.show_new_master_password_button = QPushButton()
        self.show_new_master_password_button.setIcon(QIcon('./themes/light/visibility_off.png'))
        self.show_new_master_password_button.setCheckable(True)
        self.show_new_master_password_button.clicked.connect(lambda *args, arg1=self.new_master_password_text_box, arg2=self.show_new_master_password_button: self.toggle_echo_mode(arg1, arg2))
        self.show_new_master_password_button.setMaximumSize(QSize(28, 28))
        self.show_new_master_password_button.setObjectName('checkable')

        master_password_text_box_layout.addWidget(self.new_master_password_text_box) # Ajout des éléments
        master_password_text_box_layout.addWidget(self.show_new_master_password_button)

        # ═══════════---> wrong_new_master_password_label : Texte indiquant à l'utilisateur qu'il y a une erreur dans la saisie

        self.wrong_new_master_password_label = QLabel()
        self.wrong_new_master_password_label.setText('Mot de passe invalide')
        self.wrong_new_master_password_label.setStyleSheet('color: transparent')
        self.wrong_new_master_password_label.setObjectName('wrong_input')

        # On vérifie la validité du mot de passe principal lors de la saisie
        self.new_master_password_text_box.textChanged.connect(lambda *args, arg1=self.new_master_password_text_box, arg2=self.wrong_new_master_password_label: self.check_master_password_validity(arg1, arg2))

        # ═══════════---> enter_vault_code_label

        enter_vault_code_label = QLabel()
        enter_vault_code_label.setText('Code d\'authentification')
        enter_vault_code_label.setObjectName('m_label')

        # ═══════════---> vault_code_text_box_layout

        vault_code_text_box_layout = QHBoxLayout()

        # ═══════════--->---> new_vault_code_text_box : Champ pour la saisie du code d'authentification

        self.new_vault_code_text_box = QLineEdit(self) # On crée un deuxième champ pour le code de coffre
        self.new_vault_code_text_box.setEchoMode(QLineEdit.Password)
        self.new_vault_code_text_box.setFixedHeight(28)

        # ═══════════--->---> show_new_vault_code_button : Bouton qui servira à afficher le code d'authentification

        self.show_new_vault_code_button = QPushButton()
        self.show_new_vault_code_button.setIcon(QIcon('./themes/light/visibility_off.png'))
        self.show_new_vault_code_button.setCheckable(True)
        self.show_new_vault_code_button.clicked.connect(lambda *args, arg1=self.new_vault_code_text_box, arg2=self.show_new_vault_code_button: self.toggle_echo_mode(arg1, arg2))
        self.show_new_vault_code_button.setMaximumSize(QSize(28, 28))
        self.show_new_vault_code_button.setObjectName('checkable')

        vault_code_text_box_layout.addWidget(self.new_vault_code_text_box) # Ajout des éléments
        vault_code_text_box_layout.addWidget(self.show_new_vault_code_button)

        # ═══════════---> wrong_new_vault_code_label : Texte indiquant à l'utilisateur qu'il y a une erreur dans la saisie

        self.wrong_new_vault_code_label = QLabel()
        self.wrong_new_vault_code_label.setText('Code de coffre invalide')
        self.wrong_new_vault_code_label.setStyleSheet('color: transparent')
        self.wrong_new_vault_code_label.setObjectName('wrong_input')

        # On vérifie la validité du code d'authentification lors de la saisie
        self.new_vault_code_text_box.textChanged.connect(lambda *args, arg1=self.new_vault_code_text_box, arg2=self.wrong_new_vault_code_label: self.check_vault_code_validity(arg1, arg2))

        # ═══════════---> actions_layout : Contiendra les boutons d'actions

        actions_layout = QHBoxLayout()

        # ═══════════--->---> create_new_vault_button : Bouton qui servira à créer le coffre

        create_new_vault_button = QPushButton('Créer', self) # On crée un bouton qui servira à déchiffrer le coffre
        create_new_vault_button.clicked.connect(self.create_new_vault_button_clicked)
        create_new_vault_button.setDefault(True)

        # ═══════════--->---> new_close_button : Bouton pour quitter le programme

        new_close_button = QPushButton('Quitter', self)
        new_close_button.clicked.connect(self.exit_zPass)
        new_close_button.setObjectName('red_button')

        # ═══════════--->---> new_vault_cancel_button : Bouton pour annuler la création et revenir à l'écran de déchiffrement

        new_vault_cancel_button = QPushButton('Annuler', self)
        new_vault_cancel_button.clicked.connect(self.show_vault_decrypt_ui)
        new_vault_cancel_button.setObjectName('tertiary_button')

        actions_layout.addStretch() # On ajoute un espace pour aligner les boutons à droite
        actions_layout.addWidget(create_new_vault_button) # Ajout des éléments
        actions_layout.addWidget(new_vault_cancel_button)
        actions_layout.addWidget(new_close_button)

        new_vault_creation_layout.addLayout(zPass_logo_container) # Ajout des éléments
        new_vault_creation_layout.addWidget(new_vault_label)
        new_vault_creation_layout.addWidget(enter_vault_name_label)
        new_vault_creation_layout.addWidget(self.vault_name_text_box)
        new_vault_creation_layout.addWidget(self.wrong_vault_name_label)
        new_vault_creation_layout.addWidget(enter_master_password_label)
        new_vault_creation_layout.addLayout(master_password_text_box_layout)
        new_vault_creation_layout.addWidget(self.wrong_new_master_password_label)
        new_vault_creation_layout.addWidget(enter_vault_code_label)
        new_vault_creation_layout.addLayout(vault_code_text_box_layout)
        new_vault_creation_layout.addWidget(self.wrong_new_vault_code_label)
        new_vault_creation_layout.addLayout(actions_layout)

        self.new_vault_creation_root.setLayout(new_vault_creation_layout)

        self.main_layout.addWidget(self.new_vault_creation_root) # Ajout de "new_vault_creation_root" au contenant principal "main_layout"

    def init_passwords_ui(self):

        # ═ RACINE ══ entries_splitter_root, entries_view_root & entries_view_root_layout : Contenant principal

        self.entries_splitter_root = QSplitter()
        self.entries_splitter_root.setHandleWidth(10)

        entries_view_root = QWidget()
        entries_view_root.setMinimumWidth(50)
        entries_view_root.setObjectName('panel')
        
        entries_view_root_layout = QHBoxLayout()
        entries_view_root_layout.setContentsMargins(0, 0, 0, 0)

        entries_view_root.setLayout(entries_view_root_layout)

        # ═══════════---> entries_view_container & entries_view_layout : Affichage principal des entrées

        entries_view_container = QWidget()
        entries_view_container.setStyleSheet('background-color: transparent; border: none;')

        entries_view_layout = QVBoxLayout()
        entries_view_layout.setSpacing(0)
        entries_view_layout.setContentsMargins(0, 0, 0, 0)

        entries_view_container.setLayout(entries_view_layout)

        # ═══════════--->---> entries_view_scroll_area : Permet de défiler dans la liste d'entrées

        entries_view_scroll_area = QScrollArea()
        entries_view_scroll_area.setWidgetResizable(True)
        entries_view_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        entries_view_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # entries_view_scroll_area.setStyleSheet('')

        entries_view_layout.addWidget(entries_view_scroll_area) # Ajout des éléments
        entries_view_root_layout.addWidget(entries_view_container)

        entries_view_scroll_area_container = QWidget()
        entries_view_scroll_area.setWidget(entries_view_scroll_area_container)

        # ═══════════--->--->---> main_entries_view_layout : Contiendra les colonnes des entrées

        self.main_entries_view_layout = QHBoxLayout(entries_view_scroll_area_container)
        self.main_entries_view_layout.setSpacing(0)
        entries_view_container.setLayout(self.main_entries_view_layout)

        # ═══════════--->--->---> icon_column, ... & password_column : Colonnes contenant les informations sur les entrées

        self.icon_column = QVBoxLayout() # Contiendra l'icône des entrées
        self.name_column = QVBoxLayout() # Contiendra le nom des entrées
        self.gap_1_column = QVBoxLayout() # Espace entre deux colonnes
        self.username_column = QVBoxLayout() # Contiendra le nom d'utilisateur des entrées
        self.gap_2_column = QVBoxLayout() # Espace entre deux colonnes
        self.password_column = QVBoxLayout() # Contiendra le mot de passe des entrées, affichés avec des "●●●●●"

        self.main_entries_view_layout.addLayout(self.icon_column) # Ajout des éléments
        self.main_entries_view_layout.addLayout(self.name_column)
        self.main_entries_view_layout.addLayout(self.gap_1_column)
        self.main_entries_view_layout.addLayout(self.username_column)
        self.main_entries_view_layout.addLayout(self.gap_2_column)
        self.main_entries_view_layout.addLayout(self.password_column)

        # ═══════════---> right_panel_root, right_panel_root_layout & right_panel_container : Affichage de l'entrée séléctionnée

        right_panel_root = QWidget()
        right_panel_root.setMinimumWidth(50)
        right_panel_root.setObjectName('right_panel')

        right_panel_root_layout = QHBoxLayout()
        right_panel_root_layout.setContentsMargins(0, 0, 0, 0)

        right_panel_root.setLayout(right_panel_root_layout)

        right_panel_container = QWidget()
        right_panel_container.setStyleSheet(get_style_sheet() + get_style_sheet('./themes/right_panel_override.css'))

        right_panel_layout = QVBoxLayout()
        right_panel_layout.setSpacing(0)
        right_panel_layout.setContentsMargins(0, 0, 0, 0)

        right_panel_container.setLayout(right_panel_layout)

        # ═══════════--->---> right_panel_scroll_area : Permet de défiler dans les détails de l'entrée

        right_panel_scroll_area = QScrollArea()
        right_panel_scroll_area.setWidgetResizable(True)
        right_panel_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        right_panel_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        right_panel_scroll_area_container = QWidget()
        right_panel_scroll_area.setWidget(right_panel_scroll_area_container)

        right_panel_layout.addWidget(right_panel_scroll_area) # Ajout des éléments
        right_panel_root_layout.addWidget(right_panel_container)

        self.main_right_panel_layout = QVBoxLayout(right_panel_scroll_area_container)
        right_panel_container.setLayout(self.main_right_panel_layout)

        self.entries_splitter_root.addWidget(entries_view_root) # On ajoute les deux affichages principaux
        self.entries_splitter_root.addWidget(right_panel_root)
        self.entries_splitter_root.setSizes([300, 100]) # On définit les tailles initiales des éléments

        self.main_layout.addWidget(self.entries_splitter_root) # Ajout de "entries_splitter_root" au contenant principal "main_layout"

    def show_vault_decrypt_ui(self):
        global selected_vault

        # encrypt_state / decrypt_state / delete_vault_state / new_vault_state / new_entry_state / modify_entry_state / remove_entry_state
        self.toggle_actions(True, False, False, False, True, True, True)

        self.new_vault_creation_root.setHidden(True)
        self.decrypt_vault_root.setHidden(False)
        self.entries_splitter_root.setHidden(True)

        vault_list = self.list_available_vaults()
        selected_vault = vault_list[0]
        self.vault_selection_dropdown.setCurrentIndex(0)

        self.master_password_text_box.clear()
        self.master_password_text_box.setStyleSheet('')
        self.wrong_master_password_label.setStyleSheet('color: transparent')
        self.show_master_password_button.setIcon(QIcon('./themes/light/visibility_off.png'))
        self.show_master_password_button.setChecked(False)
        self.vault_code_text_box.clear()
        self.vault_code_text_box.setStyleSheet('')
        self.wrong_vault_code_label.setStyleSheet('color: transparent')
        self.show_vault_code_button.setIcon(QIcon('./themes/light/visibility_off.png'))
        self.show_vault_code_button.setChecked(False)

        self.master_password_text_box.setEchoMode(QLineEdit.Password)
        self.vault_code_text_box.setEchoMode(QLineEdit.Password)

    def show_vault_creation_ui(self):
        # encrypt_state / decrypt_state / delete_vault_state / new_vault_state / new_entry_state / modify_entry_state / remove_entry_state
        self.toggle_actions(True, True, True, False, True, True, True)

        self.new_vault_creation_root.setHidden(False)
        self.decrypt_vault_root.setHidden(True)
        self.entries_splitter_root.setHidden(True)

        self.vault_name_text_box.clear()
        self.vault_name_text_box.setStyleSheet('')
        self.wrong_vault_name_label.setStyleSheet('color: transparent')
        self.new_master_password_text_box.clear()
        self.new_master_password_text_box.setStyleSheet('')
        self.wrong_new_master_password_label.setStyleSheet('color: transparent')
        self.show_new_master_password_button.setIcon(QIcon('./themes/light/visibility_off.png'))
        self.show_new_master_password_button.setChecked(False)
        self.new_vault_code_text_box.clear()
        self.new_vault_code_text_box.setStyleSheet('')
        self.wrong_new_vault_code_label.setStyleSheet('color: transparent')
        self.show_new_vault_code_button.setIcon(QIcon('./themes/light/visibility_off.png'))
        self.show_new_vault_code_button.setChecked(False)

        self.new_master_password_text_box.setEchoMode(QLineEdit.Password)
        self.new_vault_code_text_box.setEchoMode(QLineEdit.Password)

        if self.list_available_vaults() != []:
            new_vault_cancel_button.setHidden(False)
        else:
            new_vault_cancel_button.setHidden(True)

    def reset_text_boxes(self):
        

    def show_passwords_ui(self):
        global selected_entry

        # encrypt_state / decrypt_state / delete_vault_state / new_vault_state / new_entry_state / modify_entry_state / remove_entry_state
        self.toggle_actions(False, True, False, True, False, True, True)

        self.new_vault_creation_root.setHidden(True)
        self.decrypt_vault_root.setHidden(True)
        self.entries_splitter_root.setHidden(False)

        selected_entry = None

        self.populate_entries()
    
    def toggle_actions(self, encrypt_state, decrypt_state, delete_vault_state, new_vault_state, new_entry_state, modify_entry_state, remove_entry_state):
        encrypt_action.setDisabled(encrypt_state)
        decrypt_action.setDisabled(decrypt_state)
        delete_vault_action.setDisabled(delete_vault_state)
        new_vault_action.setDisabled(new_vault_state)

        new_entry_action.setDisabled(new_entry_state)
        modify_entry_action.setDisabled(modify_entry_state)
        remove_entry_action.setDisabled(remove_entry_state)

    def list_available_vaults(self) -> list:
        vault_list = []
        for vault in settings['vaults']:
            vault_list.append(vault)
        
        return vault_list

    def get_selected_vault_name(self, s): # Simple fonction qui met à jour le coffre sélectionné par l'utilisateur
        global selected_vault

        selected_vault = s
    
    def check_vault_code_validity(self, text_box:QLineEdit, label_wrong:QLabel) -> bool:
        valid = True

        label_wrong.setStyleSheet('color: transparent')
        
        try:
            if len(text_box.text()) != 6: 
                int(text_box.text())
                valid = False
                label_wrong.setStyleSheet('')
                label_wrong.setText('Le code contient 6 chiffres')
        except ValueError:
            valid = False
            label_wrong.setStyleSheet('')
            label_wrong.setText('Le code ne contient que des chiffres')
        
        if valid:
            text_box.setStyleSheet('')
            label_wrong.setStyleSheet('color: transparent;')
        return valid
    
    def check_master_password_validity(self, text_box:QLineEdit, label_wrong:QLabel) -> bool:
        valid = True
        
        label_wrong.setStyleSheet('color: transparent')

        if len(text_box.text()) == 0:
            valid = False
            label_wrong.setStyleSheet('')
            label_wrong.setText('Saisissez un mot de passe')
        
        if valid:
            label_wrong.setStyleSheet('color: transparent')
        return valid
    
    def check_vault_name_validity(self) -> bool:
        valid = True
        self.wrong_vault_name_label.setStyleSheet('color: transparent')
        possible_new_vault_name = self.vault_name_text_box.text() # On récupère le contenu du champ "possible_new_vault_name"
        # Pas idéal : Permet d'acccepter les accents, mais permet aussi d'avoir des noms de coffre comme "Super coffre 🧰"
        forbidden_characters = list(string.punctuation + string.whitespace) 
        forbidden_characters.remove(' ') # L'espace est retiré de la liste des charactères interdits
        
        # On vérifie si le nom éxiste déjà
        if possible_new_vault_name in settings['vaults']:
            valid = False
            self.wrong_vault_name_label.setText('Nom de coffre déjà existant')
            self.wrong_vault_name_label.setStyleSheet('')
        # On vérifie que la longueur du nom ne soi pas de zéro. On vérifie aussi qu'elle soit inférieure à 32¹.
        elif len(possible_new_vault_name) == 0 or len(possible_new_vault_name) >= 32:
            valid = False
            self.wrong_vault_name_label.setText('La longueur du nom de coffre doit être comprise entre 0 et 32')
            self.wrong_vault_name_label.setStyleSheet('')
        else:
            for character in possible_new_vault_name: # On réalise une boucle sur l'ensemble des charactères du nouveau nom
                if character in forbidden_characters: # On teste si le charactère est dans la liste des charactères interdits
                    valid = False
                    self.wrong_vault_name_label.setText('Seuls les caractères alphanumériques sont autorisés')
                    self.wrong_vault_name_label.setStyleSheet('')

        return valid

    def closeEvent(self, event): # Lorsque le bouton de sortie est cliqué
        master_password = pad_master_password(self.master_password_text_box.text()) # On récupère le mot de passe principal depuis le champ correspondant
        vault_code = bytes(self.vault_code_text_box.text(), 'utf-8') # On récupère le code depuis le champ correspondant

        close = QMessageBox()
        close.setWindowTitle('Quitter ?')
        close.setWindowIcon(QIcon('./themes/logo_64.png'))
        close.setText('Fermer zPass ?')
        close.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        close = close.exec()

        if last_correct_master_password != '':
            encrypt_vault(selected_vault, master_password, vault_code) # On essaie de chiffrer le coffre dès la sortie, pour plus de sécurité

        if close == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
    
    def exit_zPass(self):
        master_password = pad_master_password(self.master_password_text_box.text()) # On récupère le mot de passe principal depuis le champ correspondant
        vault_code = bytes(self.vault_code_text_box.text(), 'utf-8') # On récupère le code depuis le champ correspondant

        close = QMessageBox()
        close.setWindowTitle('Quitter ?')
        close.setWindowIcon(QIcon('./themes/logo_64.png'))
        close.setText('Fermer zPass ?')
        close.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        close = close.exec()

        if last_correct_master_password != '':
            encrypt_vault(selected_vault, master_password, vault_code) # On essaie de chiffrer le coffre dès la sortie, pour plus de sécurité

        if close == QMessageBox.Yes:
            sys.exit()
        else:
            pass

    def decrypt_button_clicked(self):
        global last_correct_vault_code, last_correct_master_password

        is_master_password_valid = self.check_master_password_validity(self.master_password_text_box, self.wrong_master_password_label)
        is_vault_code_valid = self.check_vault_code_validity(self.vault_code_text_box, self.wrong_vault_code_label)

        if is_master_password_valid and is_vault_code_valid:
            self.master_password = pad_master_password(self.master_password_text_box.text())
            self.vault_code = bytes(self.vault_code_text_box.text(), 'utf-8')

            decrypt_status = decrypt_vault(selected_vault, self.master_password, self.vault_code) # On exécute la fonction qui essaie de déchiffrer le coffre, tout en récupérant le code d'erreur reçu dans la variable "decrypt_status"
            
            # On indique à l'utilisateur que le mot de passe est / code d'authentification est invalide
            if decrypt_status == 400:
                time.sleep(0.5) # On force une attente de 500 ms pour éviter des tentatives par "force brute"
                self.wrong_master_password_label.setStyleSheet('')
                self.wrong_master_password_label.setText('Mot de passe invalide')
                self.wrong_vault_code_label.setStyleSheet('color: transparent')
            elif decrypt_status == 401:
                time.sleep(0.5)
                self.wrong_master_password_label.setStyleSheet('color: transparent')
                self.wrong_vault_code_label.setStyleSheet('')
                self.wrong_vault_code_label.setText('Code de coffre invalide')
            elif decrypt_status == 200:
                last_correct_master_password = self.master_password
                last_correct_vault_code = self.vault_code
                self.wrong_master_password_label.setStyleSheet('color: transparent')
                self.wrong_vault_code_label.setStyleSheet('color: transparent')
                self.show_passwords_ui()
    
    def get_passwords(self) -> dict:
        with open('.temp_vault.zpdb', 'r') as password_file: # Ouverture initiale du fichier paramètres (nommé settings.json)
            passwords = json.load(password_file) # On récupère les données du fichier
        return passwords
    
    def populate_entries(self):
        global passwords

        entries_view = self.get_entries_view_colum_lists()

        for widget in entries_view['icon_column']:
            self.icon_column.removeWidget(widget)
            widget.setParent(None)
        for widget in entries_view['name_column']:
            self.name_column.removeWidget(widget)
            widget.setParent(None)
        for widget in entries_view['gap_1_column']:
            self.gap_1_column.removeWidget(widget)
            widget.setParent(None)
        for widget in entries_view['username_column']:
            self.username_column.removeWidget(widget)
            widget.setParent(None)
        for widget in entries_view['gap_2_column']:
            self.gap_2_column.removeWidget(widget)
            widget.setParent(None)
        for widget in entries_view['password_column']:
            self.password_column.removeWidget(widget)
            widget.setParent(None)

        self.main_entries_view_layout.addLayout(self.icon_column)
        self.main_entries_view_layout.addLayout(self.name_column)
        self.main_entries_view_layout.addLayout(self.gap_1_column)
        self.main_entries_view_layout.addLayout(self.username_column)
        self.main_entries_view_layout.addLayout(self.gap_2_column)
        self.main_entries_view_layout.addLayout(self.password_column)
        
        self.clear_right_panel()

        passwords = self.get_passwords()

        if passwords['entries'] == {}:
            name_label = QLabel()
            name_label.setText('Aucun mot de passe enregistré : cliquez sur "Nouvelle entrée" pour en ajouter une')
            name_label.setStyleSheet('color: grey')
            name_label.setFixedHeight(24)
            self.name_column.addWidget(name_label)
        else:
            for entry in passwords['entries']:
                name = passwords['entries'][entry]['name']
                icon_path = passwords['entries'][entry]['icon_path']
                if icon_path == '':
                    icon_path = './themes/light/no_icon.png'
                username = passwords['entries'][entry]['user_name']
                password = passwords['entries'][entry]['password']

                icon_container = QLabel()
                icon_container.setFixedWidth(34)
                icon_container.setFixedHeight(24)
                icon = QPixmap(icon_path).scaled(QSize(16, 16), mode=Qt.SmoothTransformation, aspectMode=Qt.KeepAspectRatio)
                icon_container.setPixmap(icon)
                self.icon_column.addWidget(icon_container)

                name_label = QLabel()
                name_label.setText(name)
                name_label.setFixedHeight(24)
                self.name_column.addWidget(name_label)

                gap_1 = QFrame()
                gap_1.setFixedWidth(10)
                gap_1.setFixedHeight(24)
                self.gap_1_column.addWidget(gap_1)
                
                username_label = QLabel()
                username_label.setText(username)
                username_label.setFixedHeight(24)
                self.username_column.addWidget(username_label)

                gap_2 = QFrame()
                gap_2.setFixedWidth(10)
                gap_2.setFixedHeight(24)
                self.gap_2_column.addWidget(gap_2)

                password_label = QLabel()
                password_label.setStyleSheet('padding: 0 8px 0 0')
                password_label.setText('●' * len(password) + '  ')
                password_label.setFixedHeight(24)
                self.password_column.addWidget(password_label)

                for widget in [icon_container, name_label, gap_1, username_label, gap_2, password_label]:
                    widget.enterEvent = lambda *args, arg=icon_container: self.hovered_entry(arg)
                    widget.leaveEvent = lambda *args, arg=icon_container: self.unhovered_entry(arg)
                    widget.mousePressEvent = lambda *args, arg=icon_container, arg2=passwords['entries'][entry]: self.clicked_entry(arg, arg2)

                icon_container.setStyleSheet('padding: 0 0 0 4px; background-color: transparent')
                name_label.setStyleSheet('background-color: transparent')
                gap_1.setStyleSheet('background-color: transparent')
                username_label.setStyleSheet('background-color: transparent')
                gap_2.setStyleSheet('background-color: transparent')
                password_label.setStyleSheet('background-color: transparent')
            
        icon_spacer = QWidget()
        icon_spacer.setFixedWidth(32)
        name_spacer = QWidget()
        gap_1_spacer = QWidget()
        gap_1_spacer.setFixedWidth(10)
        username_spacer = QWidget()
        gap_2_spacer = QWidget()
        gap_2_spacer.setFixedWidth(10)
        password_spacer = QWidget()

        for element in [icon_spacer, name_spacer, gap_1_spacer, username_spacer, gap_2_spacer, password_spacer]:
            element.mousePressEvent = lambda *args: self.deselect_entry()

        self.icon_column.addWidget(icon_spacer, 1)
        self.name_column.addWidget(name_spacer, 1)
        self.gap_1_column.addWidget(gap_1_spacer, 1)
        self.username_column.addWidget(username_spacer, 1)
        self.gap_2_column.addWidget(gap_2_spacer, 1)
        self.password_column.addWidget(password_spacer, 1)
    
    def clicked_entry(self, element, entry_data):
        global selected_entry
        global selected_entry_password, selected_entry_hidden_password
        global selected_entry_password_label
        global is_selected_entry_password_visible
        global show_password_button

        entries_view = self.get_entries_view_colum_lists()

        if element in entries_view['icon_column']:
            entry_index = entries_view['icon_column'].index(element)

        if selected_entry == None:
            selected_entry = entry_index
        
        entries_view['icon_column'][selected_entry].setStyleSheet('padding: 0 0 0 4px; background-color: transparent')
        entries_view['name_column'][selected_entry].setStyleSheet('background-color: transparent')
        entries_view['gap_1_column'][selected_entry].setStyleSheet('background-color: transparent')
        entries_view['username_column'][selected_entry].setStyleSheet('background-color: transparent')
        entries_view['gap_2_column'][selected_entry].setStyleSheet('background-color: transparent')
        entries_view['password_column'][selected_entry].setStyleSheet('background-color: transparent')

        selected_entry = entry_index

        entries_view['icon_column'][selected_entry].setStyleSheet('padding: 0 0 0 4px; background-color: rgb(179, 241, 191); border-top-left-radius: 8px; border-bottom-left-radius: 8px;')
        entries_view['name_column'][selected_entry].setStyleSheet('background-color: rgb(179, 241, 191)')
        entries_view['gap_1_column'][selected_entry].setStyleSheet('background-color: rgb(179, 241, 191)')
        entries_view['username_column'][selected_entry].setStyleSheet('background-color: rgb(179, 241, 191)')
        entries_view['gap_2_column'][selected_entry].setStyleSheet('background-color: rgb(179, 241, 191)')
        entries_view['password_column'][selected_entry].setStyleSheet('background-color: rgb(179, 241, 191); border-top-right-radius: 8px; border-bottom-right-radius: 8px;')

        remove_entry_action.setDisabled(False)
        new_entry_action.setDisabled(False)
        modify_entry_action.setDisabled(False)

        self.clear_right_panel()
        
        icon_path = entry_data['icon_path']
        if icon_path == '':
            icon_path = './themes/light/no_icon_dp.png'
        entry_name = entry_data['name']
        password = entry_data['password']
        username = entry_data['user_name']

        selected_entry_icon_container = QLabel()
        selected_entry_icon_container.setFixedSize(QSize(128, 128))
        icon = QPixmap(icon_path).scaled(QSize(128, 128), mode=Qt.SmoothTransformation, aspectMode=Qt.KeepAspectRatio)
        selected_entry_icon_container.setPixmap(icon)
        selected_entry_icon_container.setFixedSize(QSize(128, 128))
        
        selected_entry_name_title_label = QLabel()
        selected_entry_name_title_label.setText('Nom')
        selected_entry_name_title_label.setObjectName('m_label')
        
        selected_entry_name_label_container = QWidget()
        selected_entry_name_label_layout = QHBoxLayout()
        selected_entry_name_label_layout.setContentsMargins(0, 0, 0, 0)
        selected_entry_name_label_container.setLayout(selected_entry_name_label_layout)

        selected_entry_name_label = QLabel()
        selected_entry_name_label.setText(entry_name)
        selected_entry_name_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        selected_entry_name_label.setCursor(Qt.IBeamCursor)

        selected_entry_name_label_layout.addWidget(selected_entry_name_label)
        selected_entry_name_label_layout.addWidget(QWidget(), 1)

        selected_entry_username_title_label = QLabel()
        selected_entry_username_title_label.setText('Nom d\'utilisateur')
        selected_entry_username_title_label.setObjectName('m_label')

        selected_entry_username_label_container = QWidget()
        selected_entry_username_label_layout = QHBoxLayout()
        selected_entry_username_label_layout.setContentsMargins(0, 0, 0, 0)
        selected_entry_username_label_container.setLayout(selected_entry_username_label_layout)

        selected_entry_username_label = QLabel()
        selected_entry_username_label.setText(entry_data['user_name'])
        selected_entry_username_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        selected_entry_username_label.setCursor(Qt.IBeamCursor)

        selected_entry_username_label_layout.addWidget(selected_entry_username_label)
        selected_entry_username_label_layout.addWidget(QWidget(), 1)

        selected_entry_password_title_label = QLabel()
        selected_entry_password_title_label.setText('Mot de passe')
        selected_entry_password_title_label.setObjectName('m_label')

        selected_entry_password_container = QWidget()
        selected_entry_password_layout = QHBoxLayout()
        selected_entry_password_layout.setContentsMargins(0, 0, 0, 0)
        selected_entry_password_container.setLayout(selected_entry_password_layout)

        is_selected_entry_password_visible = False
        selected_entry_password_label = QLabel()
        selected_entry_password = entry_data['password']
        selected_entry_hidden_password = '•' * len(selected_entry_password)
        selected_entry_password_label.setText(selected_entry_hidden_password)
        selected_entry_password_label.setObjectName('selected_entry_password_label')

        show_password_button = QPushButton()
        show_password_button.setIcon(QIcon('./themes/light/visibility_off.png'))
        show_password_button.setObjectName('checkable')
        show_password_button.setMaximumSize(QSize(28, 28))
        show_password_button.clicked.connect(self.selected_entry_show_password_button_clicked)
        show_password_button.setCheckable(True)

        copy_password_button = QPushButton()
        copy_password_button.setIcon(QIcon('./themes/light/copy.png'))
        copy_password_button.setMaximumSize(QSize(28, 28))
        copy_password_button.clicked.connect(self.selected_entry_copy_password_button_clicked)

        copy_password_button.enterEvent = lambda *args: copy_password_button.setIcon(QIcon('./themes/light/copy_hover.png'))
        copy_password_button.leaveEvent = lambda *args: copy_password_button.setIcon(QIcon('./themes/light/copy.png'))

        selected_entry_password_layout.addWidget(selected_entry_password_label, 1)
        selected_entry_password_layout.addWidget(show_password_button)
        selected_entry_password_layout.addWidget(copy_password_button)

        self.main_right_panel_layout.addWidget(selected_entry_icon_container, alignment=Qt.AlignCenter)
        self.main_right_panel_layout.addWidget(selected_entry_name_title_label)
        self.main_right_panel_layout.addWidget(selected_entry_name_label_container)
        if username != '':
            self.main_right_panel_layout.addWidget(selected_entry_username_title_label)
            self.main_right_panel_layout.addWidget(selected_entry_username_label_container)
        if password != '':
            self.main_right_panel_layout.addWidget(selected_entry_password_title_label)
            self.main_right_panel_layout.addWidget(selected_entry_password_container)
        self.main_right_panel_layout.addWidget(QWidget(), 1)
    
    def deselect_entry(self):
        global selected_entry

        entries_view = self.get_entries_view_colum_lists()

        if selected_entry != None:
            entries_view['icon_column'][selected_entry].setStyleSheet('padding: 0 0 0 4px; background-color: transparent')
            entries_view['name_column'][selected_entry].setStyleSheet('background-color: transparent')
            entries_view['gap_1_column'][selected_entry].setStyleSheet('background-color: transparent')
            entries_view['username_column'][selected_entry].setStyleSheet('background-color: transparent')
            entries_view['gap_2_column'][selected_entry].setStyleSheet('background-color: transparent')
            entries_view['password_column'][selected_entry].setStyleSheet('background-color: transparent')

            selected_entry = None
            
            self.clear_right_panel()

            remove_entry_action.setDisabled(True)
            modify_entry_action.setDisabled(True)
    
    def clear_right_panel(self):
        for widget in [self.main_right_panel_layout.itemAt(i).widget() for i in range(self.main_right_panel_layout.count())]:
            self.main_right_panel_layout.removeWidget(widget)
            widget.setParent(None)
    
    def new_entry_action_clicked(self):
        global new_entry_selected_icon_path

        self.deselect_entry()
        new_entry_action.setDisabled(True)

        self.new_entry_icon_container = QLabel()
        self.new_entry_icon_container.setFixedSize(QSize(128, 128))
        icon = QPixmap('./themes/light/no_icon_dp.png').scaled(QSize(128, 128), mode=Qt.SmoothTransformation, aspectMode=Qt.KeepAspectRatio)
        self.new_entry_icon_container.setPixmap(icon)
        self.new_entry_icon_container.setFixedSize(QSize(128, 128))

        new_entry_selected_icon_path = ''

        new_entry_icon_actions_container = QWidget()
        new_entry_icon_actions_layout = QHBoxLayout()
        new_entry_icon_actions_layout.setContentsMargins(0, 0, 0, 0)
        new_entry_icon_actions_container.setLayout(new_entry_icon_actions_layout)

        self.select_new_entry_icon_button = QPushButton('Sélectionner l\'icône')
        self.select_new_entry_icon_button.clicked.connect(self.select_new_entry_icon_button_clicked)

        self.clear_new_entry_icon_button = QPushButton()
        self.clear_new_entry_icon_button.setMaximumSize(QSize(28, 28))
        self.clear_new_entry_icon_button.setIcon(QIcon('./themes/light/close.png'))
        self.clear_new_entry_icon_button.setObjectName('red_button')
        self.clear_new_entry_icon_button.clicked.connect(self.clear_new_entry_icon_button_clicked)
        self.clear_new_entry_icon_button.setHidden(True)

        self.clear_new_entry_icon_button.enterEvent = lambda *args: self.clear_new_entry_icon_button.setIcon(QIcon('./themes/light/close_hover.png'))
        self.clear_new_entry_icon_button.leaveEvent = lambda *args: self.clear_new_entry_icon_button.setIcon(QIcon('./themes/light/close.png'))

        new_entry_icon_actions_layout.addWidget(self.select_new_entry_icon_button)
        new_entry_icon_actions_layout.addWidget(self.clear_new_entry_icon_button)

        new_entry_name_title_label = QLabel()
        new_entry_name_title_label.setText('Nom')
        new_entry_name_title_label.setObjectName('m_label')
        
        self.new_entry_name_text_box = QLineEdit()
        self.new_entry_name_text_box.setFixedHeight(28)
        self.new_entry_name_text_box.textChanged.connect(self.check_new_entry_name_validity)

        new_entry_username_title_label = QLabel()
        new_entry_username_title_label.setText('Nom d\'utilisateur')
        new_entry_username_title_label.setObjectName('m_label')

        self.new_entry_username_text_box = QLineEdit()
        self.new_entry_username_text_box.setFixedHeight(28)

        new_entry_password_title_label = QLabel()
        new_entry_password_title_label.setText('Mot de passe')
        new_entry_password_title_label.setObjectName('m_label')

        new_entry_password_text_box_container = QWidget()
        new_entry_password_text_box_layout = QHBoxLayout()
        new_entry_password_text_box_layout.setContentsMargins(0, 0, 0, 0)
        new_entry_password_text_box_container.setLayout(new_entry_password_text_box_layout)

        self.new_entry_password_text_box = QLineEdit()
        self.new_entry_password_text_box.setEchoMode(QLineEdit.Password)
        self.new_entry_password_text_box.setFixedHeight(28)

        show_password_button = QPushButton()
        show_password_button.setObjectName('checkable')
        show_password_button.setIcon(QIcon('./themes/light/visibility_off.png'))
        show_password_button.setMaximumSize(QSize(28, 28))
        show_password_button.clicked.connect(lambda *args, arg1=self.new_entry_password_text_box, arg2=show_password_button: self.toggle_echo_mode(arg1, arg2))
        show_password_button.setCheckable(True)

        new_entry_password_text_box_layout.addWidget(self.new_entry_password_text_box, 1)
        new_entry_password_text_box_layout.addWidget(show_password_button)

        actions_container = QWidget()
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_container.setLayout(actions_layout)

        create_new_entry_button = QPushButton('Créer')
        create_new_entry_button.clicked.connect(self.create_new_entry_button_clicked)

        cancel_entry_creation_button = QPushButton('Annuler')
        cancel_entry_creation_button.clicked.connect(self.cancel_entry_creation_button_clicked)
        cancel_entry_creation_button.setObjectName('red_button')

        actions_layout.addWidget(QWidget(), 1)
        actions_layout.addWidget(create_new_entry_button)
        actions_layout.addWidget(cancel_entry_creation_button)

        self.main_right_panel_layout.addWidget(self.new_entry_icon_container, alignment=Qt.AlignCenter)
        self.main_right_panel_layout.addWidget(new_entry_icon_actions_container)
        self.main_right_panel_layout.addWidget(new_entry_name_title_label)
        self.main_right_panel_layout.addWidget(self.new_entry_name_text_box)
        self.main_right_panel_layout.addWidget(new_entry_username_title_label)
        self.main_right_panel_layout.addWidget(self.new_entry_username_text_box)
        self.main_right_panel_layout.addWidget(new_entry_password_title_label)
        self.main_right_panel_layout.addWidget(new_entry_password_text_box_container)
        self.main_right_panel_layout.addWidget(actions_container)
        self.main_right_panel_layout.addWidget(QWidget(), 1)
    
    def select_new_entry_icon_button_clicked(self):
        global new_entry_selected_icon_path

        new_selected_icon_path = self.get_icon_path()
        
        if new_selected_icon_path:
            new_entry_selected_icon_path = new_selected_icon_path
            new_entry_icon = QPixmap(new_selected_icon_path).scaled(QSize(128, 128), mode=Qt.SmoothTransformation, aspectMode=Qt.KeepAspectRatio)
            self.new_entry_icon_container.setPixmap(new_entry_icon)

            self.clear_new_entry_icon_button.setHidden(False)
    
    def get_icon_path(self):
        new_icon_path = QFileDialog.getOpenFileName(self, 'Open file', 'c:\\', 'Image files (*.jpg *.png *.gif)')
        if new_icon_path[0] != '':
            icon = QPixmap(new_icon_path[0]).scaled(QSize(128, 128), mode=Qt.SmoothTransformation, aspectMode=Qt.KeepAspectRatio)
            valid = False
            while not valid:
                random_id = ''.join([str(random.randint(0, 9)) for _ in range(10)])
                try:
                    with open(f'./icons/{random_id}.png') as test:
                        test.close()
                except FileNotFoundError:
                    valid = True
            icon_path = f'./icons/{random_id}.png'
            icon.save(icon_path)
            return icon_path
        return False

    def modify_entry_icon_button_clicked(self):
        global modified_icon_path

        test_modified_icon_path = self.get_icon_path()
        if test_modified_icon_path:
            modified_icon_path = test_modified_icon_path
            modified_icon = QPixmap(modified_icon_path).scaled(QSize(128, 128), mode=Qt.SmoothTransformation, aspectMode=Qt.KeepAspectRatio)
            self.modified_icon_container.setPixmap(modified_icon)
            self.clear_modified_entry_icon_button.setHidden(False)
    
    def modify_entry_action_clicked(self):
        global modified_icon_path
        global old_entry_name

        if selected_entry != None:
            passwords_keys = [i for i in passwords['entries']]
            entry_data = passwords['entries'][passwords_keys[selected_entry]]

            self.clear_right_panel()

            modified_icon_path = entry_data['icon_path']
            if modified_icon_path == '':
                modified_icon_path = './themes/light/no_icon_dp.png'
            old_entry_name = entry_data['name']
            password = entry_data['password']
            username = entry_data['user_name']

            self.modified_icon_container = QLabel()
            self.modified_icon_container.setFixedSize(QSize(128, 128))
            icon = QPixmap(modified_icon_path).scaled(QSize(128, 128), mode=Qt.SmoothTransformation, aspectMode=Qt.KeepAspectRatio)
            self.modified_icon_container.setPixmap(icon)

            modified_entry_icon_actions_container = QWidget()
            modified_entry_icon_actions_layout = QHBoxLayout()
            modified_entry_icon_actions_layout.setContentsMargins(0, 0, 0, 0)
            modified_entry_icon_actions_container.setLayout(modified_entry_icon_actions_layout)

            self.clear_modified_entry_icon_button = QPushButton()
            self.clear_modified_entry_icon_button.setMaximumSize(QSize(28, 28))
            self.clear_modified_entry_icon_button.setObjectName('red_button')
            self.clear_modified_entry_icon_button.clicked.connect(self.clear_modified_entry_icon_button_clicked)
            self.clear_modified_entry_icon_button.setIcon(QIcon('./themes/light/close.png'))

            self.clear_modified_entry_icon_button.enterEvent = lambda *args: self.clear_modified_entry_icon_button.setIcon(QIcon('./themes/light/close_hover.png'))
            self.clear_modified_entry_icon_button.leaveEvent = lambda *args: self.clear_modified_entry_icon_button.setIcon(QIcon('./themes/light/close.png'))

            if modified_icon_path == './themes/light/no_icon_dp.png':
                self.clear_modified_entry_icon_button.setHidden(True)

            self.modify_entry_icon_button = QPushButton('Changer l\'icône')
            self.modify_entry_icon_button.clicked.connect(self.modify_entry_icon_button_clicked)

            modified_entry_icon_actions_layout.addWidget(self.modify_entry_icon_button)
            modified_entry_icon_actions_layout.addWidget(self.clear_modified_entry_icon_button)

            new_entry_name_title_label = QLabel()
            new_entry_name_title_label.setText('Nom')
            new_entry_name_title_label.setObjectName('m_label')
            
            self.modify_entry_name_text_box = QLineEdit()
            self.modify_entry_name_text_box.setFixedHeight(28)
            self.modify_entry_name_text_box.textChanged.connect(self.check_modified_entry_name)
            self.modify_entry_name_text_box.setText(old_entry_name)

            new_entry_username_title_label = QLabel()
            new_entry_username_title_label.setText('Nom d\'utilisateur')
            new_entry_username_title_label.setObjectName('m_label')

            self.modify_entry_username_text_box = QLineEdit()
            self.modify_entry_username_text_box.setFixedHeight(28)
            self.modify_entry_username_text_box.setText(username)

            new_entry_password_title_label = QLabel()
            new_entry_password_title_label.setText('Mot de passe')
            new_entry_password_title_label.setObjectName('m_label')

            modify_entry_password_text_box_container = QWidget()
            modify_entry_password_text_box_layout = QHBoxLayout()
            modify_entry_password_text_box_layout.setContentsMargins(0, 0, 0, 0)
            modify_entry_password_text_box_container.setLayout(modify_entry_password_text_box_layout)

            self.modify_entry_password_text_box = QLineEdit()
            self.modify_entry_password_text_box.setFixedHeight(28)
            self.modify_entry_password_text_box.setEchoMode(QLineEdit.Password)
            self.modify_entry_password_text_box.setText(password)

            show_password_button = QPushButton()
            show_password_button.setIcon(QIcon('./themes/light/visibility_off.png'))
            show_password_button.setObjectName('checkable')
            show_password_button.setMaximumSize(QSize(28, 28))
            show_password_button.clicked.connect(lambda *args, arg1=self.modify_entry_password_text_box, arg2=show_password_button: self.toggle_echo_mode(arg1, arg2))
            show_password_button.setCheckable(True)

            modify_entry_password_text_box_layout.addWidget(self.modify_entry_password_text_box, 1)
            modify_entry_password_text_box_layout.addWidget(show_password_button)

            actions_container = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_container.setLayout(actions_layout)

            save_modifications_button = QPushButton('Sauvegarder')
            save_modifications_button.clicked.connect(self.save_modifications_button_clicked)

            cancel_modification_button = QPushButton('Annuler')
            cancel_modification_button.clicked.connect(self.cancel_modification_button_clicked)
            cancel_modification_button.setObjectName('red_button')

            actions_layout.addWidget(QWidget(), 1)
            actions_layout.addWidget(save_modifications_button)
            actions_layout.addWidget(cancel_modification_button)

            self.main_right_panel_layout.addWidget(self.modified_icon_container, alignment=Qt.AlignCenter)
            self.main_right_panel_layout.addWidget(modified_entry_icon_actions_container)
            self.main_right_panel_layout.addWidget(new_entry_name_title_label)
            self.main_right_panel_layout.addWidget(self.modify_entry_name_text_box)
            self.main_right_panel_layout.addWidget(new_entry_username_title_label)
            self.main_right_panel_layout.addWidget(self.modify_entry_username_text_box)
            self.main_right_panel_layout.addWidget(new_entry_password_title_label)
            self.main_right_panel_layout.addWidget(modify_entry_password_text_box_container)
            self.main_right_panel_layout.addWidget(actions_container)
            self.main_right_panel_layout.addWidget(QWidget(), 1)

    def save_modifications_button_clicked(self):
        if self.check_modified_entry_name():
            del passwords['entries'][old_entry_name]

            modified_entry_name = self.modify_entry_name_text_box.text()
            modified_entry_icon_path = modified_icon_path
            modified_entry_username = self.modify_entry_username_text_box.text()
            modified_entry_password = self.modify_entry_password_text_box.text()

            new_entry_object =  {modified_entry_name: {
                                        'name': modified_entry_name,
                                        'icon_path': modified_entry_icon_path,
                                        "user_name": modified_entry_username,
                                        "password": modified_entry_password
                                    }
                                }

            passwords['entries'].update(new_entry_object)
            passwords_json = json.dumps(passwords, indent=4, sort_keys=True)
            with open('.temp_vault.zpdb', 'w') as passwords_file:
                passwords_file.write(passwords_json)
            
            self.deselect_entry()
            self.populate_entries()
            passwords_keys = [i for i in passwords['entries']]
            selected_entry = passwords_keys.index(modified_entry_name)
            entry_data = passwords['entries'][passwords_keys[selected_entry]]
            self.clicked_entry(self.get_entries_view_colum_lists()['icon_column'][selected_entry], entry_data)
    
    def cancel_entry_creation_button_clicked(self):
        global selected_entry

        selected_entry = None
        
        self.clear_right_panel()

        new_entry_action.setDisabled(False)
        remove_entry_action.setDisabled(True)
        modify_entry_action.setDisabled(True)

    def cancel_modification_button_clicked(self):
        if selected_entry != None:
            self.clear_right_panel()
            passwords_keys = [i for i in passwords['entries']] #!
            entry_data = passwords['entries'][passwords_keys[selected_entry]]

            self.clicked_entry(self.get_entries_view_colum_lists()['icon_column'][selected_entry], entry_data)
    
    def clear_modified_entry_icon_button_clicked(self):
        global modified_icon_path

        icon = QPixmap('./themes/light/no_icon_dp.png').scaled(QSize(128, 128), mode=Qt.SmoothTransformation, aspectMode=Qt.KeepAspectRatio)
        self.modified_icon_container.setPixmap(icon)
        os.remove(modified_icon_path)

        modified_icon_path = ''

        self.clear_modified_entry_icon_button.setHidden(True)

    def clear_new_entry_icon_button_clicked(self):
        global new_entry_selected_icon_path

        icon = QPixmap('./themes/light/no_icon_dp.png').scaled(QSize(128, 128), mode=Qt.SmoothTransformation, aspectMode=Qt.KeepAspectRatio)
        self.new_entry_icon_container.setPixmap(icon)
        os.remove(new_entry_selected_icon_path)

        new_entry_selected_icon_path = ''

        self.clear_new_entry_icon_button.setHidden(True)
    
    def create_new_entry_button_clicked(self):
        if self.check_new_entry_name_validity():
            new_entry_name = self.new_entry_name_text_box.text()
            new_entry_icon_path = new_entry_selected_icon_path
            new_entry_username = self.new_entry_username_text_box.text()
            new_entry_password = self.new_entry_password_text_box.text()

            new_entry_object =  {new_entry_name: {
                                        'name': new_entry_name,
                                        'icon_path': new_entry_icon_path,
                                        "user_name": new_entry_username,
                                        "password": new_entry_password
                                    }
                                }

            passwords['entries'].update(new_entry_object)
            passwords_json = json.dumps(passwords, indent=4, sort_keys=True)
            with open('.temp_vault.zpdb', 'w') as passwords_file:
                passwords_file.write(passwords_json)
            
            self.deselect_entry()
            self.populate_entries()

            new_entry_action.setDisabled(False)

    def remove_entry_action_clicked(self):
        if selected_entry != None:
            passwords_keys = [i for i in passwords['entries']]
            del passwords['entries'][passwords_keys[selected_entry]]

            passwords_json = json.dumps(passwords, indent=4, sort_keys=True)
            with open('.temp_vault.zpdb', 'w') as passwords_file:
                passwords_file.write(passwords_json)

            self.deselect_entry()
            self.populate_entries()
    
    def check_new_entry_name_validity(self):
        valid = True
        
        possible_new_entry_name = self.new_entry_name_text_box.text()
        
        if len(possible_new_entry_name) == 0 or possible_new_entry_name in passwords['entries']:
            valid = False

        return valid

    def check_modified_entry_name(self):
        valid = True

        possible_modified_entry_name = self.modify_entry_name_text_box.text()
        
        if selected_entry != None:
            passwords_keys = [i for i in passwords['entries']]
        
            if len(possible_modified_entry_name) == 0 or possible_modified_entry_name in passwords['entries']:
                valid = False
                if possible_modified_entry_name == passwords_keys[selected_entry]:
                    valid = True

            return valid

    def selected_entry_show_password_button_clicked(self):
        global is_selected_entry_password_visible

        if is_selected_entry_password_visible:
            show_password_button.setIcon(QIcon('./themes/light/visibility_off.png'))
            selected_entry_password_label.setText(selected_entry_hidden_password)
            is_selected_entry_password_visible = False
        else:
            show_password_button.setIcon(QIcon('./themes/light/visibility_on.png'))
            selected_entry_password_label.setText(selected_entry_password)
            is_selected_entry_password_visible = True
    
    def selected_entry_copy_password_button_clicked(self):
        clipboard = QClipboard()
        clipboard.setText(selected_entry_password)
    
    def hovered_entry(self, element):
        entries_view = self.get_entries_view_colum_lists()

        if element in entries_view['icon_column']:
            entry_index = entries_view['icon_column'].index(element)
        
        if entry_index != selected_entry:
            entries_view['icon_column'][entry_index].setStyleSheet('padding: 0 0 0 4px; background-color: rgb(235, 239, 231); border-top-left-radius: 8px; border-bottom-left-radius: 8px;')
            entries_view['name_column'][entry_index].setStyleSheet('background-color: rgb(235, 239, 231)')
            entries_view['gap_1_column'][entry_index].setStyleSheet('background-color: rgb(235, 239, 231)')
            entries_view['username_column'][entry_index].setStyleSheet('background-color: rgb(235, 239, 231)')
            entries_view['gap_2_column'][entry_index].setStyleSheet('background-color: rgb(235, 239, 231)')
            entries_view['password_column'][entry_index].setStyleSheet('background-color: rgb(235, 239, 231); border-top-right-radius: 8px; border-bottom-right-radius: 8px;')
    
    def get_entries_view_colum_lists(self) -> dict:
        return {
            'icon_column': [self.icon_column.itemAt(i).widget() for i in range(self.icon_column.count())],
            'name_column': [self.name_column.itemAt(i).widget() for i in range(self.name_column.count())],
            'gap_1_column': [self.gap_1_column.itemAt(i).widget() for i in range(self.gap_1_column.count())],
            'username_column': [self.username_column.itemAt(i).widget() for i in range(self.username_column.count())],
            'gap_2_column': [self.gap_2_column.itemAt(i).widget() for i in range(self.gap_2_column.count())],
            'password_column': [self.password_column.itemAt(i).widget() for i in range(self.password_column.count())]
        }

    def unhovered_entry(self, element):
        entries_view = self.get_entries_view_colum_lists()

        if element in entries_view['icon_column']:
            entry_index = entries_view['icon_column'].index(element)
        
        if entry_index != selected_entry:
            entries_view['icon_column'][entry_index].setStyleSheet('padding: 0 0 0 4px; background-color: transparent')
            entries_view['name_column'][entry_index].setStyleSheet('background-color: transparent')
            entries_view['gap_1_column'][entry_index].setStyleSheet('background-color: transparent')
            entries_view['username_column'][entry_index].setStyleSheet('background-color: transparent')
            entries_view['gap_2_column'][entry_index].setStyleSheet('background-color: transparent')
            entries_view['password_column'][entry_index].setStyleSheet('background-color: transparent')
    
    def encrypt_button_clicked(self):
        if last_correct_master_password == '':
            self.master_password = pad_master_password(self.master_password_text_box.text())
            self.vault_code = bytes(self.vault_code_text_box.text(), 'utf-8')
        else:
            self.master_password = last_correct_master_password
            self.vault_code = last_correct_vault_code

        encrypt_status = encrypt_vault(selected_vault, self.master_password, self.vault_code)

        if encrypt_status != 200:
            dialog = QMessageBox(self)
            dialog.setWindowIcon(QIcon('./themes/logo_64.png'))
            dialog.setWindowTitle(error_codes_dictionnary[encrypt_status][0])
            dialog.setText(error_codes_dictionnary[encrypt_status][1])
            dialog.setStandardButtons(QMessageBox.Ok)
            if encrypt_status == 402:
                dialog.setIcon(QMessageBox.Critical)
                dialog.exec()
            
        else:
            encrypt_action.setDisabled(True)
            decrypt_action.setDisabled(False)
            self.show_vault_decrypt_ui()
    
    def create_new_vault_button_clicked(self):
        global selected_vault

        is_master_password_valid = self.check_master_password_validity(self.new_master_password_text_box, self.wrong_new_master_password_label)
        is_vault_code_valid = self.check_vault_code_validity(self.new_vault_code_text_box, self.wrong_new_vault_code_label)
        is_vault_name_valid = self.check_vault_name_validity()

        if is_master_password_valid and is_vault_code_valid and is_vault_name_valid:
            vault_name = self.vault_name_text_box.text()
            create_vault_status = create_vault(vault_name)

            if create_vault_status == 200:
                selected_vault = vault_name
                new_vault_object =  {vault_name: {
                                            "file_path": f'vaults/{vault_name}.zpdb'
                                        }
                                    }

                settings['vaults'].update(new_vault_object)
                settings_json = json.dumps(settings, indent=4, sort_keys=True)
                with open('settings.json', 'w') as settings_file:
                    settings_file.write(settings_json)
                
                self.vault_selection_dropdown.addItem(selected_vault)
                
                new_master_password = pad_master_password(self.new_master_password_text_box.text())
                new_vault_code = bytes(self.new_vault_code_text_box.text(), 'utf-8')
                
                encrypt_vault(selected_vault, new_master_password, new_vault_code)
                
                self.show_vault_decrypt_ui()
    
    def delete_vault_button_clicked(self):
        dialog = QMessageBox(self)
        dialog.setWindowIcon(QIcon('./themes/logo_64.png'))
        dialog.setWindowTitle('Supprimer ?')
        dialog.setText('Voulez-vous supprimer le coffre fort ?')
        dialog.setIcon(QMessageBox.Warning)
        dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        choice = dialog.exec()

        if choice == QMessageBox.Yes:
            delete_vault(selected_vault) # On supprime le coffre
            selected_vault_index = 0
            
            for vault in settings['vaults']:
                if vault == selected_vault:
                    break
                else:
                    selected_vault_index += 1

            del settings['vaults'][selected_vault]
            settings_json = json.dumps(settings, indent=4, sort_keys=True)
            with open('settings.json', 'w') as settings_file:
                settings_file.write(settings_json)
                settings_file.close()

            self.vault_selection_dropdown.removeItem(selected_vault_index)

            if self.list_available_vaults() == []:
                self.show_vault_creation_ui()
            else:
                self.show_vault_decrypt_ui()
    
    def create_dialog(self, title, content): # Petite fonction ayant pour but de créer de simple boîtes de dialogue
        dialog = QMessageBox(self)
        dialog.setWindowIcon(QIcon('./themes/logo_64.png'))
        dialog.setWindowTitle(title)
        dialog.setText(content)
        dialog.exec()
    
    def toggle_echo_mode(self, text_box, button):
        if text_box.echoMode() == QLineEdit.Password: # Si le champ est en mode mot de passe...
            text_box.setEchoMode(QLineEdit.Normal) # ...On le fait passer en mode normal
            button.setChecked(True) # On change l'apparence du bouton
            button.setIcon(QIcon('./themes/light/visibility_on.png'))
        else: # Sinon = si le champ est en mode normal...
            text_box.setEchoMode(QLineEdit.Password) # ...On le fait passer en mode mot de passe
            button.setChecked(False)
            button.setIcon(QIcon('./themes/light/visibility_off.png'))
    
    def launch_checks(self):
        try: # Pour vérifier si le programme a été fermé correctement, on vérifie si le coffre temporaire existe toujours
            decrypted_vault_file = open('.temp_vault.zpdb')
            decrypted_vault_file.close()
            dialog = QMessageBox(self)
            dialog.setWindowIcon(QIcon('./themes/logo_64.png'))
            dialog.setWindowTitle('Erreur')
            dialog.setText('zPass n\' pas été fermé correctement\nVos modifications seront perdues')
            dialog.setIcon(QMessageBox.Critical)
            dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            choice = dialog.exec()

            if choice == QMessageBox.Ok:
                os.remove('.temp_vault.zpdb') # On supprime le fichier temporaire si l'utilisateur accepte
            else:
                sys.exit() # On ferme le programme si l'utilisateur refuse
        
        except FileNotFoundError:
            pass # Le fichier n'existe pas, continuer l'exécution normale du programme

        try: os.mkdir('./vaults/'); # On vérifie si le dossier "vaults" éxiste
        except FileExistsError: pass; # Le dossier éxiste déjà, continuer
        
        try: os.mkdir('./icons/'); # On vérifie si le dossier "icons" éxiste
        except FileExistsError: pass; # Le dossier éxiste déjà, continuer  


if __name__ == '__main__':
    root = QApplication(sys.argv)

    root.setStyleSheet(get_style_sheet()) # On applique la feuille de style au programme

    QImageReader.setAllocationLimit(0) # Permet de charger des icônes plus lourdes
    QFontDatabase.addApplicationFont('./themes/fonts/Urbanist-Light.ttf') # On charge les polices utilisées dans le programme
    QFontDatabase.addApplicationFont('./themes/fonts/Inter-Regular.ttf')
    QFontDatabase.addApplicationFont('./themes/fonts/JetBrainsMono-Regular.ttf')
    
    splash_window = zPass()
    splash_window.show()

    sys.exit(root.exec())

# ¹ Il s'agit d'une limite arbitraire que je me suis permis d'instaurer. La raison est la suivante : la longueur maximale
#   d'un chemin pour un fichier est définie par la clé de registre "MAX_PATH", et est limitée à 256. Cette limite de 32
#   caractères pour le nom de tout nouveau coffre est là pour éviter tout problème s'y relatant. Dans le cas de Python,
#   et de la fonction "open()", un chemin d'accès trop long génère une OSError [Errno 22] sur Windows.
