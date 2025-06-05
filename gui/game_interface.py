"""
Interface principale du jeu TerraGenesis PC
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QLabel, QPushButton, QProgressBar, QTabWidget,
                            QScrollArea, QFrame, QGroupBox, QListWidget,
                            QListWidgetItem, QTextEdit, QSlider, QSpinBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor

from utils.helpers import (format_number, format_temperature, format_pressure, 
                          format_percentage, get_habitability_color)

class ResourceWidget(QFrame):
    """
    Widget d'affichage des ressources
    """
    
    def __init__(self, resource_name: str, resource_type: str):
        """
        Initialise le widget de ressource
        
        Args:
            resource_name: Nom affiché de la ressource
            resource_type: Type de ressource (credits, energy, science)
        """
        super().__init__()
        
        self.resource_name = resource_name
        self.resource_type = resource_type
        
        self.setup_ui()
        self.setup_style()
    
    def setup_ui(self):
        """
        Configure l'interface du widget
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Nom de la ressource
        self.name_label = QLabel(self.resource_name)
        name_font = QFont()
        name_font.setBold(True)
        self.name_label.setFont(name_font)
        self.name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.name_label)
        
        # Valeur actuelle
        self.value_label = QLabel("0")
        value_font = QFont()
        value_font.setPointSize(14)
        self.value_label.setFont(value_font)
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        # Production par seconde
        self.production_label = QLabel("+0/s")
        self.production_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.production_label)
    
    def setup_style(self):
        """
        Configure le style du widget
        """
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(1)
        self.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #555555;
                border-radius: 4px;
            }
            QLabel {
                color: #ffffff;
                border: none;
            }
        """)
    
    def update_values(self, current: float, production: float, max_value: float = None):
        """
        Met à jour les valeurs affichées
        
        Args:
            current: Valeur actuelle
            production: Production par seconde
            max_value: Valeur maximale (optionnel)
        """
        if max_value:
            self.value_label.setText(f"{format_number(current)}/{format_number(max_value)}")
        else:
            self.value_label.setText(format_number(current))
        
        if production >= 0:
            self.production_label.setText(f"+{format_number(production)}/s")
            self.production_label.setStyleSheet("color: #00FF00;")
        else:
            self.production_label.setText(f"{format_number(production)}/s")
            self.production_label.setStyleSheet("color: #FF0000;")

class PlanetStatusWidget(QGroupBox):
    """
    Widget d'affichage du statut de la planète
    """
    
    def __init__(self):
        """
        Initialise le widget de statut
        """
        super().__init__("Statut de la planète")
        
        self.setup_ui()
        self.setup_style()
    
    def setup_ui(self):
        """
        Configure l'interface
        """
        layout = QGridLayout(self)
        
        # Habitabilité
        layout.addWidget(QLabel("Habitabilité:"), 0, 0)
        self.habitability_label = QLabel("0%")
        self.habitability_progress = QProgressBar()
        self.habitability_progress.setRange(0, 100)
        layout.addWidget(self.habitability_label, 0, 1)
        layout.addWidget(self.habitability_progress, 0, 2)
        
        # Température
        layout.addWidget(QLabel("Température:"), 1, 0)
        self.temperature_label = QLabel("0°C")
        layout.addWidget(self.temperature_label, 1, 1, 1, 2)
        
        # Pression
        layout.addWidget(QLabel("Pression:"), 2, 0)
        self.pressure_label = QLabel("0 atm")
        layout.addWidget(self.pressure_label, 2, 1, 1, 2)
        
        # Oxygène
        layout.addWidget(QLabel("Oxygène:"), 3, 0)
        self.oxygen_label = QLabel("0%")
        layout.addWidget(self.oxygen_label, 3, 1, 1, 2)
    
    def setup_style(self):
        """
        Configure le style
        """
        self.setStyleSheet("""
            QGroupBox {
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
            }
            QLabel {
                color: #ffffff;
            }
            QProgressBar {
                border: 1px solid #555555;
                border-radius: 2px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 2px;
            }
        """)
    
    def update_status(self, planet):
        """
        Met à jour l'affichage du statut
        
        Args:
            planet: Objet Planet
        """
        habitability = planet.calculate_habitability()
        
        # Habitabilité
        self.habitability_label.setText(f"{habitability:.1f}%")
        self.habitability_progress.setValue(int(habitability))
        
        # Couleur de la barre selon l'habitabilité
        color = get_habitability_color(habitability)
        self.habitability_progress.setStyleSheet(f"""
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 2px;
            }}
        """)
        
        # Autres paramètres
        self.temperature_label.setText(format_temperature(planet.temperature))
        self.pressure_label.setText(format_pressure(planet.pressure))
        self.oxygen_label.setText(format_percentage(planet.oxygen))

class BuildingWidget(QFrame):
    """
    Widget pour construire des bâtiments
    """
    
    building_requested = pyqtSignal(str, int)  # type, count
    
    def __init__(self, building_type: str, building_name: str, building_cost: dict):
        """
        Initialise le widget de bâtiment
        
        Args:
            building_type: Type de bâtiment
            building_name: Nom affiché
            building_cost: Coût du bâtiment
        """
        super().__init__()
        
        self.building_type = building_type
        self.building_name = building_name
        self.building_cost = building_cost
        
        self.setup_ui()
        self.setup_style()
    
    def setup_ui(self):
        """
        Configure l'interface
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Nom du bâtiment
        name_label = QLabel(self.building_name)
        name_font = QFont()
        name_font.setBold(True)
        name_label.setFont(name_font)
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)
        
        # Coût
        cost_text = ", ".join([f"{resource}: {amount}" 
                              for resource, amount in self.building_cost.items()])
        cost_label = QLabel(f"Coût: {cost_text}")
        cost_label.setWordWrap(True)
        layout.addWidget(cost_label)
        
        # Contrôles de construction
        controls_layout = QHBoxLayout()
        
        self.count_spinbox = QSpinBox()
        self.count_spinbox.setRange(1, 100)
        self.count_spinbox.setValue(1)
        controls_layout.addWidget(self.count_spinbox)
        
        build_button = QPushButton("Construire")
        build_button.clicked.connect(self.request_building)
        controls_layout.addWidget(build_button)
        
        layout.addLayout(controls_layout)
        
        # Nombre actuel
        self.current_label = QLabel("Actuel: 0")
        layout.addWidget(self.current_label)
    
    def setup_style(self):
        """
        Configure le style
        """
        self.setFrameStyle(QFrame.Box)
        self.setLineWidth(1)
        self.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border: 1px solid #555555;
                border-radius: 4px;
            }
            QLabel {
                color: #ffffff;
                border: none;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #999999;
            }
            QSpinBox {
                background-color: #404040;
                color: white;
                border: 1px solid #555555;
                padding: 2px;
            }
        """)
    
    def request_building(self):
        """
        Demande la construction du bâtiment
        """
        count = self.count_spinbox.value()
        self.building_requested.emit(self.building_type, count)
    
    def update_current_count(self, count: int):
        """
        Met à jour le nombre actuel de bâtiments
        
        Args:
            count: Nombre actuel
        """
        self.current_label.setText(f"Actuel: {count}")

class GameInterface(QWidget):
    """
    Interface principale du jeu
    """
    
    def __init__(self, game_engine):
        """
        Initialise l'interface de jeu
        
        Args:
            game_engine: Moteur de jeu
        """
        super().__init__()
        
        self.game_engine = game_engine
        self.resource_widgets = {}
        self.building_widgets = {}
        
        self.setup_ui()
        self.setup_style()
        self.setup_connections()
        
        # Timer pour les mises à jour d'affichage
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_displays)
        self.update_timer.start(1000)  # Mise à jour chaque seconde
    
    def setup_ui(self):
        """
        Configure l'interface
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Barre de ressources en haut
        resources_layout = QHBoxLayout()
        
        self.resource_widgets['credits'] = ResourceWidget("Crédits", "credits")
        self.resource_widgets['energy'] = ResourceWidget("Énergie", "energy")
        self.resource_widgets['science'] = ResourceWidget("Science", "science")
        
        for widget in self.resource_widgets.values():
            resources_layout.addWidget(widget)
        
        layout.addLayout(resources_layout)
        
        # Zone principale avec onglets
        self.tab_widget = QTabWidget()
        
        # Onglet Planète
        planet_tab = self.create_planet_tab()
        self.tab_widget.addTab(planet_tab, "Planète")
        
        # Onglet Construction
        building_tab = self.create_building_tab()
        self.tab_widget.addTab(building_tab, "Construction")
        
        # Onglet Recherche
        research_tab = self.create_research_tab()
        self.tab_widget.addTab(research_tab, "Recherche")
        
        # Onglet Événements
        events_tab = self.create_events_tab()
        self.tab_widget.addTab(events_tab, "Événements")
        
        layout.addWidget(self.tab_widget)
        
        # Contrôles de simulation en bas
        controls_layout = QHBoxLayout()
        
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.toggle_pause)
        controls_layout.addWidget(self.pause_button)
        
        controls_layout.addWidget(QLabel("Vitesse:"))
        
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 10)  # 0.5x à 5x
        self.speed_slider.setValue(2)  # 1x par défaut
        self.speed_slider.valueChanged.connect(self.change_speed)
        controls_layout.addWidget(self.speed_slider)
        
        self.speed_label = QLabel("1x")
        controls_layout.addWidget(self.speed_label)
        
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
    
    def create_planet_tab(self):
        """
        Crée l'onglet de la planète
        
        Returns:
            Widget de l'onglet planète
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Nom de la planète
        if self.game_engine.current_planet:
            planet_name = QLabel(self.game_engine.current_planet.name)
            planet_font = QFont()
            planet_font.setPointSize(18)
            planet_font.setBold(True)
            planet_name.setFont(planet_font)
            planet_name.setAlignment(Qt.AlignCenter)
            layout.addWidget(planet_name)
        
        # Statut de la planète
        self.planet_status = PlanetStatusWidget()
        layout.addWidget(self.planet_status)
        
        # Description et informations
        info_group = QGroupBox("Informations")
        info_layout = QVBoxLayout(info_group)
        
        self.planet_description = QTextEdit()
        self.planet_description.setReadOnly(True)
        self.planet_description.setMaximumHeight(100)
        if self.game_engine.current_planet:
            planet_data = self.game_engine.available_planets.get(
                self.game_engine.current_planet.name, {})
            self.planet_description.setText(planet_data.get('description', ''))
        info_layout.addWidget(self.planet_description)
        
        layout.addWidget(info_group)
        
        layout.addStretch()
        
        return widget
    
    def create_building_tab(self):
        """
        Crée l'onglet de construction
        
        Returns:
            Widget de l'onglet construction
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Zone de défilement pour les bâtiments
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        buildings_widget = QWidget()
        buildings_layout = QGridLayout(buildings_widget)
        
        # Définir les bâtiments disponibles
        buildings_data = {
            'solar_panel': {
                'name': 'Panneau solaire',
                'cost': {'credits': 100, 'energy': 10}
            },
            'heater': {
                'name': 'Réchauffeur',
                'cost': {'credits': 150, 'energy': 20}
            },
            'cooler': {
                'name': 'Refroidisseur',
                'cost': {'credits': 150, 'energy': 20}
            },
            'atmosphere_processor': {
                'name': 'Processeur atmosphérique',
                'cost': {'credits': 300, 'energy': 50}
            },
            'oxygen_generator': {
                'name': 'Générateur d\'oxygène',
                'cost': {'credits': 200, 'energy': 30}
            },
            'greenhouse': {
                'name': 'Serre',
                'cost': {'credits': 250, 'energy': 25}
            },
            'research_lab': {
                'name': 'Laboratoire de recherche',
                'cost': {'credits': 400, 'energy': 40}
            },
            'mining_facility': {
                'name': 'Installation minière',
                'cost': {'credits': 350, 'energy': 35}
            }
        }
        
        # Créer les widgets de bâtiments
        row, col = 0, 0
        max_cols = 3
        
        for building_type, data in buildings_data.items():
            building_widget = BuildingWidget(
                building_type, 
                data['name'], 
                data['cost']
            )
            building_widget.building_requested.connect(self.build_structure)
            
            buildings_layout.addWidget(building_widget, row, col)
            self.building_widgets[building_type] = building_widget
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        scroll_area.setWidget(buildings_widget)
        layout.addWidget(scroll_area)
        
        return widget
    
    def create_research_tab(self):
        """
        Crée l'onglet de recherche
        
        Returns:
            Widget de l'onglet recherche
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Recherche actuelle
        current_group = QGroupBox("Recherche actuelle")
        current_layout = QVBoxLayout(current_group)
        
        self.current_research_label = QLabel("Aucune recherche en cours")
        current_layout.addWidget(self.current_research_label)
        
        self.research_progress = QProgressBar()
        self.research_progress.setRange(0, 100)
        current_layout.addWidget(self.research_progress)
        
        layout.addWidget(current_group)
        
        # Technologies disponibles
        available_group = QGroupBox("Technologies disponibles")
        available_layout = QVBoxLayout(available_group)
        
        self.tech_list = QListWidget()
        self.tech_list.itemDoubleClicked.connect(self.start_research)
        available_layout.addWidget(self.tech_list)
        
        layout.addWidget(available_group)
        
        return widget
    
    def create_events_tab(self):
        """
        Crée l'onglet des événements
        
        Returns:
            Widget de l'onglet événements
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Événements actifs
        active_group = QGroupBox("Événements actifs")
        active_layout = QVBoxLayout(active_group)
        
        self.events_list = QListWidget()
        active_layout.addWidget(self.events_list)
        
        layout.addWidget(active_group)
        
        # Historique des événements
        history_group = QGroupBox("Historique")
        history_layout = QVBoxLayout(history_group)
        
        self.events_history = QTextEdit()
        self.events_history.setReadOnly(True)
        self.events_history.setMaximumHeight(150)
        history_layout.addWidget(self.events_history)
        
        layout.addWidget(history_group)
        
        return widget
    
    def setup_style(self):
        """
        Configure le style de l'interface
        """
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #2d2d2d;
            }
            QTabBar::tab {
                background-color: #404040;
                color: #ffffff;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #0078d4;
            }
            QTabBar::tab:hover {
                background-color: #555555;
            }
            QGroupBox {
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 8px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 4px 0 4px;
            }
            QListWidget {
                background-color: #2d2d2d;
                border: 1px solid #555555;
                color: #ffffff;
            }
            QTextEdit {
                background-color: #2d2d2d;
                border: 1px solid #555555;
                color: #ffffff;
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
            QSlider::groove:horizontal {
                border: 1px solid #555555;
                height: 8px;
                background: #404040;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #0078d4;
                border: 1px solid #555555;
                width: 18px;
                margin: -2px 0;
                border-radius: 3px;
            }
        """)
    
    def setup_connections(self):
        """
        Configure les connexions de signaux
        """
        pass
    
    def toggle_pause(self):
        """
        Bascule la pause de la simulation
        """
        self.game_engine.pause_simulation()
        if self.game_engine.is_paused:
            self.pause_button.setText("Reprendre")
        else:
            self.pause_button.setText("Pause")
    
    def change_speed(self, value):
        """
        Change la vitesse de simulation
        
        Args:
            value: Valeur du slider (1-10)
        """
        speed = value * 0.5  # 0.5x à 5x
        self.game_engine.set_simulation_speed(speed)
        self.speed_label.setText(f"{speed}x")
    
    def build_structure(self, building_type: str, count: int):
        """
        Construit des bâtiments
        
        Args:
            building_type: Type de bâtiment
            count: Nombre à construire
        """
        if self.game_engine.build_structure(building_type, count):
            print(f"Construit {count} {building_type}")
        else:
            print(f"Impossible de construire {count} {building_type}")
    
    def start_research(self, item):
        """
        Démarre une recherche
        
        Args:
            item: Item de la liste sélectionné
        """
        tech_id = item.data(Qt.UserRole)
        if tech_id:
            self.game_engine.start_research(tech_id)
    
    def update_displays(self):
        """
        Met à jour tous les affichages
        """
        self.update_planet_display()
        self.update_resources_display()
        self.update_technology_display()
        self.update_events_display()
    
    def update_planet_display(self):
        """
        Met à jour l'affichage de la planète
        """
        if self.game_engine.current_planet:
            self.planet_status.update_status(self.game_engine.current_planet)
            
            # Mettre à jour les compteurs de bâtiments
            for building_type, widget in self.building_widgets.items():
                count = self.game_engine.current_planet.buildings.get(building_type, 0)
                widget.update_current_count(count)
    
    def update_resources_display(self):
        """
        Met à jour l'affichage des ressources
        """
        rm = self.game_engine.resource_manager
        net_production = rm.get_net_production()
        
        self.resource_widgets['credits'].update_values(
            rm.credits, net_production['credits'])
        self.resource_widgets['energy'].update_values(
            rm.energy, net_production['energy'], rm.max_energy)
        self.resource_widgets['science'].update_values(
            rm.science, net_production['science'], rm.max_science)
    
    def update_technology_display(self):
        """
        Met à jour l'affichage des technologies
        """
        tech_tree = self.game_engine.technology_tree
        
        # Recherche actuelle
        if tech_tree.current_research:
            tech = tech_tree.technologies[tech_tree.current_research]
            self.current_research_label.setText(f"Recherche: {tech.name}")
            self.research_progress.setValue(int(tech.research_progress))
        else:
            self.current_research_label.setText("Aucune recherche en cours")
            self.research_progress.setValue(0)
        
        # Technologies disponibles
        self.tech_list.clear()
        for tech in tech_tree.get_available_technologies():
            item = QListWidgetItem(tech.name)
            item.setData(Qt.UserRole, tech.id)
            self.tech_list.addItem(item)
    
    def update_events_display(self):
        """
        Met à jour l'affichage des événements
        """
        if self.game_engine.current_planet:
            self.events_list.clear()
            
            events_summary = self.game_engine.event_manager.get_active_events_summary(
                self.game_engine.current_planet)
            
            for event_info in events_summary:
                item_text = f"{event_info['name']}"
                if event_info['duration'] > 0:
                    remaining = event_info['remaining_time']
                    item_text += f" ({remaining:.0f}s restant)"
                
                item = QListWidgetItem(item_text)
                
                # Couleur selon le type
                if event_info['type'] == 'positive':
                    item.setForeground(QColor('#00FF00'))
                elif event_info['type'] == 'negative':
                    item.setForeground(QColor('#FF0000'))
                elif event_info['type'] == 'mixed':
                    item.setForeground(QColor('#FFFF00'))
                
                self.events_list.addItem(item)