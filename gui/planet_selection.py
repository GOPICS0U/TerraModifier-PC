"""
Boîte de dialogue de sélection de planète
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QPushButton, QScrollArea, QWidget, QFrame,
                            QTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QPalette

from utils.helpers import format_temperature, format_pressure, format_percentage

class PlanetCard(QFrame):
    """
    Carte représentant une planète sélectionnable
    """
    
    planet_selected = pyqtSignal(str)  # Signal émis quand une planète est sélectionnée
    
    def __init__(self, planet_name: str, planet_data: dict):
        """
        Initialise une carte de planète
        
        Args:
            planet_name: Nom de la planète
            planet_data: Données de la planète
        """
        super().__init__()
        
        self.planet_name = planet_name
        self.planet_data = planet_data
        self.is_selected = False
        
        self.setup_ui()
        self.setup_style()
    
    def setup_ui(self):
        """
        Configure l'interface de la carte
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)
        
        # Nom de la planète
        name_label = QLabel(self.planet_name)
        name_font = QFont()
        name_font.setPointSize(14)
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)
        
        # Image de la planète (placeholder pour l'instant)
        image_label = QLabel()
        image_label.setFixedSize(120, 120)
        image_label.setAlignment(Qt.AlignCenter)
        image_label.setStyleSheet("""
            QLabel {
                background-color: #404040;
                border: 2px solid #606060;
                border-radius: 60px;
                color: #ffffff;
            }
        """)
        image_label.setText(self.planet_name[0])  # Première lettre comme placeholder
        image_font = QFont()
        image_font.setPointSize(36)
        image_font.setBold(True)
        image_label.setFont(image_font)
        layout.addWidget(image_label, 0, Qt.AlignCenter)
        
        # Informations de la planète
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        # Température
        temp_label = QLabel(f"Température: {format_temperature(self.planet_data['initial_temperature'])}")
        info_layout.addWidget(temp_label)
        
        # Pression
        pressure_label = QLabel(f"Pression: {format_pressure(self.planet_data['initial_pressure'])}")
        info_layout.addWidget(pressure_label)
        
        # Oxygène
        oxygen_label = QLabel(f"Oxygène: {format_percentage(self.planet_data['initial_oxygen'])}")
        info_layout.addWidget(oxygen_label)
        
        # Difficulté
        difficulty = self.planet_data.get('difficulty', 'normal')
        difficulty_colors = {
            'easy': '#00FF00',
            'normal': '#FFFF00', 
            'hard': '#FF0000'
        }
        difficulty_label = QLabel(f"Difficulté: {difficulty.title()}")
        difficulty_label.setStyleSheet(f"color: {difficulty_colors.get(difficulty, '#FFFFFF')};")
        info_layout.addWidget(difficulty_label)
        
        layout.addLayout(info_layout)
        
        # Description (tronquée)
        description = self.planet_data.get('description', '')
        if len(description) > 100:
            description = description[:97] + "..."
        
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #CCCCCC; font-size: 10px;")
        layout.addWidget(desc_label)
        
        # Bouton de sélection
        select_button = QPushButton("Sélectionner")
        select_button.clicked.connect(self.select_planet)
        layout.addWidget(select_button)
    
    def setup_style(self):
        """
        Configure le style de la carte
        """
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(2)
        self.setFixedSize(200, 350)
        self.update_style()
    
    def update_style(self):
        """
        Met à jour le style selon l'état de sélection
        """
        if self.is_selected:
            self.setStyleSheet("""
                QFrame {
                    background-color: #2a4a2a;
                    border: 2px solid #00FF00;
                    border-radius: 8px;
                }
                QLabel {
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #00AA00;
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #00CC00;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #2d2d2d;
                    border: 2px solid #555555;
                    border-radius: 8px;
                }
                QFrame:hover {
                    border-color: #777777;
                }
                QLabel {
                    color: #ffffff;
                }
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
            """)
    
    def select_planet(self):
        """
        Sélectionne cette planète
        """
        self.planet_selected.emit(self.planet_name)
    
    def set_selected(self, selected: bool):
        """
        Définit l'état de sélection
        
        Args:
            selected: True si la planète est sélectionnée
        """
        self.is_selected = selected
        self.update_style()

class PlanetSelectionDialog(QDialog):
    """
    Boîte de dialogue pour sélectionner une planète
    """
    
    def __init__(self, available_planets: dict, parent=None):
        """
        Initialise la boîte de dialogue
        
        Args:
            available_planets: Dictionnaire des planètes disponibles
            parent: Widget parent
        """
        super().__init__(parent)
        
        self.available_planets = available_planets
        self.selected_planet = None
        self.planet_cards = {}
        
        self.setup_ui()
        self.setup_style()
    
    def setup_ui(self):
        """
        Configure l'interface de la boîte de dialogue
        """
        self.setWindowTitle("Sélection de planète")
        self.setModal(True)
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Titre
        title_label = QLabel("Choisissez une planète à terraformer")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Zone de défilement pour les planètes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Widget conteneur pour les cartes de planètes
        planets_widget = QWidget()
        planets_layout = QGridLayout(planets_widget)
        planets_layout.setSpacing(16)
        
        # Créer les cartes de planètes
        row, col = 0, 0
        max_cols = 3
        
        for planet_name, planet_data in self.available_planets.items():
            card = PlanetCard(planet_name, planet_data)
            card.planet_selected.connect(self.on_planet_selected)
            
            planets_layout.addWidget(card, row, col)
            self.planet_cards[planet_name] = card
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        scroll_area.setWidget(planets_widget)
        layout.addWidget(scroll_area)
        
        # Zone d'informations détaillées
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(120)
        self.info_text.setReadOnly(True)
        self.info_text.setText("Sélectionnez une planète pour voir les détails...")
        layout.addWidget(self.info_text)
        
        # Boutons
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setEnabled(False)
        
        cancel_button = QPushButton("Annuler")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
    
    def setup_style(self):
        """
        Configure le style de la boîte de dialogue
        """
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #555555;
                color: #ffffff;
                padding: 8px;
            }
            QScrollArea {
                background-color: #1e1e1e;
                border: none;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #999999;
            }
        """)
    
    def on_planet_selected(self, planet_name: str):
        """
        Appelé quand une planète est sélectionnée
        
        Args:
            planet_name: Nom de la planète sélectionnée
        """
        # Désélectionner toutes les autres cartes
        for name, card in self.planet_cards.items():
            card.set_selected(name == planet_name)
        
        self.selected_planet = planet_name
        self.ok_button.setEnabled(True)
        
        # Afficher les informations détaillées
        self.show_planet_details(planet_name)
    
    def show_planet_details(self, planet_name: str):
        """
        Affiche les détails d'une planète
        
        Args:
            planet_name: Nom de la planète
        """
        if planet_name not in self.available_planets:
            return
        
        planet_data = self.available_planets[planet_name]
        
        details = f"""
        <h3>{planet_name}</h3>
        <p><b>Description:</b> {planet_data.get('description', 'Aucune description disponible.')}</p>
        
        <p><b>Conditions initiales:</b></p>
        <ul>
        <li>Température: {format_temperature(planet_data['initial_temperature'])}</li>
        <li>Pression: {format_pressure(planet_data['initial_pressure'])}</li>
        <li>Oxygène: {format_percentage(planet_data['initial_oxygen'])}</li>
        <li>Masse: {planet_data.get('mass', 1.0):.2f} × Terre</li>
        <li>Distance du soleil: {planet_data.get('distance', 1.0):.2f} UA</li>
        <li>Durée du jour: {planet_data.get('day_length', 24.0):.1f} heures</li>
        </ul>
        
        <p><b>Difficulté:</b> {planet_data.get('difficulty', 'normal').title()}</p>
        """
        
        self.info_text.setHtml(details)
    
    def get_selected_planet(self) -> str:
        """
        Retourne la planète sélectionnée
        
        Returns:
            Nom de la planète sélectionnée ou None
        """
        return self.selected_planet