"""
Fenêtre principale de TerraGenesis PC
"""

import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QMenuBar, QMenu, QAction, QStatusBar, QMessageBox,
                            QFileDialog, QDialog)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence

from .planet_selection import PlanetSelectionDialog
from .game_interface import GameInterface
from core.game_engine import GameEngine
from utils.save_manager import SaveManager
from config.settings import GameSettings
from config.constants import *

class MainWindow(QMainWindow):
    """
    Fenêtre principale de l'application
    """
    
    def __init__(self):
        """
        Initialise la fenêtre principale
        """
        super().__init__()
        
        # Composants principaux
        self.game_engine = GameEngine()
        self.save_manager = SaveManager()
        self.settings = GameSettings()
        
        # Interface
        self.game_interface = None
        self.status_timer = QTimer()
        
        # Configuration de la fenêtre
        self.setup_window()
        self.setup_menu()
        self.setup_status_bar()
        self.setup_connections()
        
        # Afficher la sélection de planète au démarrage
        self.show_planet_selection()
    
    def setup_window(self):
        """
        Configure la fenêtre principale
        """
        self.setWindowTitle(GAME_TITLE)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resize(self.settings.window_width, self.settings.window_height)
        
        # Centrer la fenêtre
        self.center_window()
        
        # Widget central vide au démarrage
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Appliquer le style sombre
        self.apply_dark_theme()
    
    def center_window(self):
        """
        Centre la fenêtre sur l'écran
        """
        screen = self.screen().availableGeometry()
        window = self.frameGeometry()
        window.moveCenter(screen.center())
        self.move(window.topLeft())
    
    def apply_dark_theme(self):
        """
        Applique un thème sombre à l'interface
        """
        dark_style = """
        QMainWindow {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        QMenuBar {
            background-color: #2d2d2d;
            color: #ffffff;
            border-bottom: 1px solid #555555;
        }
        QMenuBar::item {
            background-color: transparent;
            padding: 4px 8px;
        }
        QMenuBar::item:selected {
            background-color: #404040;
        }
        QMenu {
            background-color: #2d2d2d;
            color: #ffffff;
            border: 1px solid #555555;
        }
        QMenu::item:selected {
            background-color: #404040;
        }
        QStatusBar {
            background-color: #2d2d2d;
            color: #ffffff;
            border-top: 1px solid #555555;
        }
        """
        self.setStyleSheet(dark_style)
    
    def setup_menu(self):
        """
        Configure la barre de menu
        """
        menubar = self.menuBar()
        
        # Menu Jeu
        game_menu = menubar.addMenu('&Jeu')
        
        # Nouvelle partie
        new_game_action = QAction('&Nouvelle partie', self)
        new_game_action.setShortcut(QKeySequence.New)
        new_game_action.setStatusTip('Commencer une nouvelle partie')
        new_game_action.triggered.connect(self.show_planet_selection)
        game_menu.addAction(new_game_action)
        
        game_menu.addSeparator()
        
        # Sauvegarder
        save_action = QAction('&Sauvegarder', self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.setStatusTip('Sauvegarder la partie actuelle')
        save_action.triggered.connect(self.save_game)
        game_menu.addAction(save_action)
        
        # Charger
        load_action = QAction('&Charger', self)
        load_action.setShortcut(QKeySequence.Open)
        load_action.setStatusTip('Charger une partie sauvegardée')
        load_action.triggered.connect(self.load_game)
        game_menu.addAction(load_action)
        
        game_menu.addSeparator()
        
        # Quitter
        quit_action = QAction('&Quitter', self)
        quit_action.setShortcut(QKeySequence.Quit)
        quit_action.setStatusTip('Quitter le jeu')
        quit_action.triggered.connect(self.close)
        game_menu.addAction(quit_action)
        
        # Menu Simulation
        sim_menu = menubar.addMenu('&Simulation')
        
        # Pause/Reprendre
        self.pause_action = QAction('&Pause', self)
        self.pause_action.setShortcut(Qt.Key_Space)
        self.pause_action.setStatusTip('Mettre en pause ou reprendre la simulation')
        self.pause_action.triggered.connect(self.toggle_pause)
        sim_menu.addAction(self.pause_action)
        
        sim_menu.addSeparator()
        
        # Vitesses de simulation
        speed_menu = sim_menu.addMenu('&Vitesse')
        
        speeds = [('0.5x', 0.5), ('1x', 1.0), ('2x', 2.0), ('3x', 3.0), ('5x', 5.0)]
        for name, speed in speeds:
            action = QAction(name, self)
            action.triggered.connect(lambda checked, s=speed: self.set_simulation_speed(s))
            speed_menu.addAction(action)
        
        # Menu Affichage
        view_menu = menubar.addMenu('&Affichage')
        
        # Plein écran
        fullscreen_action = QAction('&Plein écran', self)
        fullscreen_action.setShortcut(Qt.Key_F11)
        fullscreen_action.setStatusTip('Basculer en mode plein écran')
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # Menu Aide
        help_menu = menubar.addMenu('&Aide')
        
        # À propos
        about_action = QAction('&À propos', self)
        about_action.setStatusTip('À propos de TerraGenesis PC')
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """
        Configure la barre de statut
        """
        self.status_bar = self.statusBar()
        self.status_bar.showMessage('Prêt')
        
        # Timer pour mettre à jour la barre de statut
        self.status_timer.timeout.connect(self.update_status_bar)
        self.status_timer.start(1000)  # Mise à jour chaque seconde
    
    def setup_connections(self):
        """
        Configure les connexions de signaux
        """
        # Connexions du moteur de jeu
        self.game_engine.planet_updated.connect(self.on_planet_updated)
        self.game_engine.resources_updated.connect(self.on_resources_updated)
        self.game_engine.technology_updated.connect(self.on_technology_updated)
        self.game_engine.event_triggered.connect(self.on_event_triggered)
        self.game_engine.game_saved.connect(self.on_game_saved)
    
    def show_planet_selection(self):
        """
        Affiche la boîte de dialogue de sélection de planète
        """
        dialog = PlanetSelectionDialog(self.game_engine.available_planets, self)
        if dialog.exec_() == QDialog.Accepted:
            selected_planet = dialog.get_selected_planet()
            if selected_planet:
                self.start_new_game(selected_planet)
    
    def start_new_game(self, planet_name: str):
        """
        Démarre une nouvelle partie
        
        Args:
            planet_name: Nom de la planète sélectionnée
        """
        if self.game_engine.start_new_game(planet_name):
            # Créer l'interface de jeu
            self.game_interface = GameInterface(self.game_engine)
            self.setCentralWidget(self.game_interface)
            
            # Mettre à jour le titre de la fenêtre
            self.setWindowTitle(f"{GAME_TITLE} - {planet_name}")
            
            # Mettre à jour la barre de statut
            self.status_bar.showMessage(f"Nouvelle partie démarrée sur {planet_name}")
            
            print(f"Nouvelle partie démarrée sur {planet_name}")
        else:
            QMessageBox.critical(self, "Erreur", 
                               f"Impossible de démarrer une partie sur {planet_name}")
    
    def save_game(self):
        """
        Sauvegarde la partie actuelle
        """
        if not self.game_engine.current_planet:
            QMessageBox.information(self, "Information", 
                                  "Aucune partie en cours à sauvegarder")
            return
        
        # Demander le nom du fichier
        filename, _ = QFileDialog.getSaveFileName(
            self, 
            "Sauvegarder la partie",
            f"save_{self.game_engine.current_planet.name.lower()}.json",
            "Fichiers de sauvegarde (*.json)"
        )
        
        if filename:
            # S'assurer que le fichier a l'extension .json
            if not filename.endswith('.json'):
                filename += '.json'
            
            # Extraire juste le nom du fichier
            import os
            filename = os.path.basename(filename)
            
            if self.game_engine.save_game(filename):
                QMessageBox.information(self, "Succès", 
                                      f"Partie sauvegardée: {filename}")
            else:
                QMessageBox.critical(self, "Erreur", 
                                   "Erreur lors de la sauvegarde")
    
    def load_game(self):
        """
        Charge une partie sauvegardée
        """
        saves = self.save_manager.get_save_files()
        
        if not saves:
            QMessageBox.information(self, "Information", 
                                  "Aucune sauvegarde trouvée")
            return
        
        # Créer une liste des sauvegardes pour la sélection
        from .dialogs import LoadGameDialog
        dialog = LoadGameDialog(saves, self)
        
        if dialog.exec_() == QDialog.Accepted:
            selected_save = dialog.get_selected_save()
            if selected_save and self.game_engine.load_game(selected_save['filename']):
                # Créer l'interface de jeu
                self.game_interface = GameInterface(self.game_engine)
                self.setCentralWidget(self.game_interface)
                
                # Mettre à jour le titre
                planet_name = self.game_engine.current_planet.name
                self.setWindowTitle(f"{GAME_TITLE} - {planet_name}")
                
                QMessageBox.information(self, "Succès", 
                                      f"Partie chargée: {selected_save['filename']}")
            else:
                QMessageBox.critical(self, "Erreur", 
                                   "Erreur lors du chargement")
    
    def toggle_pause(self):
        """
        Bascule la pause de la simulation
        """
        if self.game_engine.current_planet:
            self.game_engine.pause_simulation()
            
            # Mettre à jour le texte de l'action
            if self.game_engine.is_paused:
                self.pause_action.setText('&Reprendre')
                self.status_bar.showMessage('Simulation en pause')
            else:
                self.pause_action.setText('&Pause')
                self.status_bar.showMessage('Simulation en cours')
    
    def set_simulation_speed(self, speed: float):
        """
        Définit la vitesse de simulation
        
        Args:
            speed: Multiplicateur de vitesse
        """
        self.game_engine.set_simulation_speed(speed)
        self.status_bar.showMessage(f'Vitesse de simulation: {speed}x')
    
    def toggle_fullscreen(self):
        """
        Bascule le mode plein écran
        """
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def show_about(self):
        """
        Affiche la boîte de dialogue À propos
        """
        about_text = f"""
        <h2>{GAME_TITLE}</h2>
        <p>Version {GAME_VERSION}</p>
        <p>Jeu de simulation de terraformation inspiré de TerraGenesis</p>
        <p>Développé avec Python et PyQt5</p>
        <br>
        <p><b>Fonctionnalités:</b></p>
        <ul>
        <li>Terraformation de planètes du système solaire</li>
        <li>Système de ressources (crédits, énergie, science)</li>
        <li>Arbre technologique</li>
        <li>Événements aléatoires</li>
        <li>Sauvegarde/chargement</li>
        </ul>
        """
        
        QMessageBox.about(self, "À propos", about_text)
    
    def update_status_bar(self):
        """
        Met à jour la barre de statut
        """
        if self.game_engine.current_planet and not self.game_engine.is_paused:
            status = self.game_engine.get_game_status()
            planet_status = status.get('planet', {})
            habitability = planet_status.get('habitability', '0%')
            
            message = f"Habitabilité: {habitability}"
            if self.game_engine.simulation_speed != 1.0:
                message += f" | Vitesse: {self.game_engine.simulation_speed}x"
            
            self.status_bar.showMessage(message)
    
    def on_planet_updated(self):
        """
        Appelé quand la planète est mise à jour
        """
        if self.game_interface:
            self.game_interface.update_planet_display()
    
    def on_resources_updated(self):
        """
        Appelé quand les ressources sont mises à jour
        """
        if self.game_interface:
            self.game_interface.update_resources_display()
    
    def on_technology_updated(self):
        """
        Appelé quand les technologies sont mises à jour
        """
        if self.game_interface:
            self.game_interface.update_technology_display()
    
    def on_event_triggered(self, name: str, description: str):
        """
        Appelé quand un événement est déclenché
        
        Args:
            name: Nom de l'événement
            description: Description de l'événement
        """
        # Afficher une notification
        QMessageBox.information(self, f"Événement: {name}", description)
    
    def on_game_saved(self):
        """
        Appelé quand le jeu est sauvegardé
        """
        self.status_bar.showMessage("Jeu sauvegardé", 3000)
    
    def closeEvent(self, event):
        """
        Gère la fermeture de la fenêtre
        
        Args:
            event: Événement de fermeture
        """
        # Demander confirmation si une partie est en cours
        if self.game_engine.current_planet:
            reply = QMessageBox.question(
                self, 
                "Quitter",
                "Une partie est en cours. Voulez-vous sauvegarder avant de quitter?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Yes:
                self.save_game()
                event.accept()
            elif reply == QMessageBox.No:
                event.accept()
            else:
                event.ignore()
                return
        
        # Sauvegarder les paramètres de la fenêtre
        if not self.isFullScreen():
            self.settings.set('window_width', self.width())
            self.settings.set('window_height', self.height())
        
        self.settings.save_settings()
        
        # Arrêter le moteur de jeu
        self.game_engine.stop_simulation()
        
        event.accept()