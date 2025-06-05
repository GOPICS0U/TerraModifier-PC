#!/usr/bin/env python3
"""
TerraGenesis PC - Jeu de simulation de terraformation
Point d'entrée principal du jeu

Auteur: Assistant IA
Version: 1.0.0
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# Ajouter le répertoire racine au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow
from utils.audio_manager import AudioManager
from config.settings import GameSettings

def main():
    """
    Fonction principale - Lance l'application TerraGenesis
    """
    # Créer l'application Qt
    app = QApplication(sys.argv)
    app.setApplicationName("TerraGenesis PC")
    app.setApplicationVersion("1.0.0")
    
    # Configuration de l'application
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Initialiser les paramètres du jeu
    settings = GameSettings()
    
    # Initialiser le gestionnaire audio
    audio_manager = AudioManager()
    audio_manager.initialize()
    
    # Créer et afficher la fenêtre principale
    main_window = MainWindow()
    main_window.show()
    
    # Démarrer la musique d'ambiance si activée
    if settings.music_enabled:
        audio_manager.play_background_music("space_ambient.ogg")
    
    # Lancer la boucle d'événements
    try:
        exit_code = app.exec_()
    except KeyboardInterrupt:
        print("\nArrêt du jeu demandé par l'utilisateur")
        exit_code = 0
    finally:
        # Nettoyage avant fermeture
        audio_manager.cleanup()
    
    return exit_code

if __name__ == "__main__":
    sys.exit(main())