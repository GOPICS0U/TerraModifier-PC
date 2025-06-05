"""
Moteur principal du jeu TerraGenesis PC
"""

import json
import time
from typing import Dict, Optional
from PyQt5.QtCore import QTimer, QObject, pyqtSignal

from .planet import Planet
from .resources import ResourceManager
from .technology import TechnologyTree
from .events import EventManager
from config.constants import *

class GameEngine(QObject):
    """
    Moteur principal du jeu - Gère la logique de simulation
    """
    
    # Signaux pour notifier l'interface
    planet_updated = pyqtSignal()
    resources_updated = pyqtSignal()
    technology_updated = pyqtSignal()
    event_triggered = pyqtSignal(str, str)  # nom, description
    game_saved = pyqtSignal()
    
    def __init__(self):
        """
        Initialise le moteur de jeu
        """
        super().__init__()
        
        # État du jeu
        self.is_running = False
        self.is_paused = False
        self.simulation_speed = 1.0
        self.game_time = 0.0  # Temps de jeu en secondes
        
        # Composants principaux
        self.current_planet: Optional[Planet] = None
        self.resource_manager = ResourceManager()
        self.technology_tree = TechnologyTree()
        self.event_manager = EventManager()
        
        # Données des planètes disponibles
        self.available_planets = {}
        self.load_planet_data()
        
        # Timer pour la simulation
        self.simulation_timer = QTimer()
        self.simulation_timer.timeout.connect(self.update_simulation)
        self.last_update_time = time.time()
        
        # Timer pour la sauvegarde automatique
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.autosave)
        
        # Statistiques de jeu
        self.game_stats = {
            'start_time': time.time(),
            'total_credits_earned': 0,
            'total_science_generated': 0,
            'buildings_built': 0,
            'technologies_researched': 0,
            'events_encountered': 0
        }
    
    def load_planet_data(self):
        """
        Charge les données des planètes disponibles
        """
        try:
            with open(PLANETS_DATA_FILE, 'r', encoding='utf-8') as f:
                self.available_planets = json.load(f)
            print(f"Chargé {len(self.available_planets)} planètes")
        except Exception as e:
            print(f"Erreur lors du chargement des planètes: {e}")
    
    def start_new_game(self, planet_name: str) -> bool:
        """
        Démarre une nouvelle partie
        
        Args:
            planet_name: Nom de la planète à terraformer
            
        Returns:
            True si la partie a été créée avec succès
        """
        if planet_name not in self.available_planets:
            print(f"Planète '{planet_name}' non trouvée")
            return False
        
        # Créer la planète
        planet_data = self.available_planets[planet_name]
        self.current_planet = Planet(planet_name, planet_data)
        
        # Réinitialiser les composants
        self.resource_manager = ResourceManager()
        self.technology_tree = TechnologyTree()
        self.event_manager = EventManager()
        
        # Réinitialiser les statistiques
        self.game_stats = {
            'start_time': time.time(),
            'total_credits_earned': 0,
            'total_science_generated': 0,
            'buildings_built': 0,
            'technologies_researched': 0,
            'events_encountered': 0
        }
        
        # Démarrer la simulation
        self.start_simulation()
        
        print(f"Nouvelle partie démarrée sur {planet_name}")
        return True
    
    def start_simulation(self):
        """
        Démarre la simulation du jeu
        """
        if not self.current_planet:
            return
        
        self.is_running = True
        self.is_paused = False
        self.last_update_time = time.time()
        
        # Démarrer les timers
        self.simulation_timer.start(SIMULATION_TICK_RATE)
        self.autosave_timer.start(300000)  # Sauvegarde automatique toutes les 5 minutes
        
        print("Simulation démarrée")
    
    def pause_simulation(self):
        """
        Met en pause ou reprend la simulation
        """
        self.is_paused = not self.is_paused
        print(f"Simulation {'en pause' if self.is_paused else 'reprise'}")
    
    def stop_simulation(self):
        """
        Arrête la simulation
        """
        self.is_running = False
        self.simulation_timer.stop()
        self.autosave_timer.stop()
        print("Simulation arrêtée")
    
    def update_simulation(self):
        """
        Met à jour la simulation du jeu
        """
        if not self.is_running or self.is_paused or not self.current_planet:
            return
        
        current_time = time.time()
        delta_time = (current_time - self.last_update_time) * self.simulation_speed
        self.last_update_time = current_time
        self.game_time += delta_time
        
        # Calculer la production de ressources basée sur les bâtiments
        self.resource_manager.calculate_production(self.current_planet, self.current_planet.buildings)
        
        # Mettre à jour les composants
        self.current_planet.update(delta_time)
        self.resource_manager.update(delta_time)
        self.technology_tree.update_research(self.resource_manager.science_per_second, delta_time)
        self.event_manager.update(self.current_planet, self.resource_manager, delta_time)
        
        # Émettre les signaux de mise à jour
        self.planet_updated.emit()
        self.resources_updated.emit()
        self.technology_updated.emit()
    
    def build_structure(self, building_type: str, count: int = 1) -> bool:
        """
        Construit des bâtiments sur la planète
        
        Args:
            building_type: Type de bâtiment à construire
            count: Nombre de bâtiments à construire
            
        Returns:
            True si la construction a réussi
        """
        if not self.current_planet:
            return False
        
        # Vérifier si le bâtiment est débloqué
        if not self.technology_tree.is_building_unlocked(building_type):
            print(f"Bâtiment '{building_type}' non débloqué")
            return False
        
        # Calculer le coût
        building_costs = {
            'solar_panel': {'credits': 100, 'energy': 10},
            'heater': {'credits': 150, 'energy': 20},
            'cooler': {'credits': 150, 'energy': 20},
            'atmosphere_processor': {'credits': 300, 'energy': 50},
            'oxygen_generator': {'credits': 200, 'energy': 30},
            'greenhouse': {'credits': 250, 'energy': 25},
            'research_lab': {'credits': 400, 'energy': 40},
            'mining_facility': {'credits': 350, 'energy': 35}
        }
        
        if building_type not in building_costs:
            print(f"Type de bâtiment '{building_type}' inconnu")
            return False
        
        base_cost = building_costs[building_type]
        total_cost = {resource: cost * count for resource, cost in base_cost.items()}
        
        # Vérifier et dépenser les ressources
        if not self.resource_manager.spend_resources(total_cost):
            print(f"Ressources insuffisantes pour construire {count} {building_type}")
            return False
        
        # Construire le bâtiment
        self.current_planet.add_building(building_type, count)
        self.game_stats['buildings_built'] += count
        
        print(f"Construit {count} {building_type}")
        return True
    
    def start_research(self, tech_id: str) -> bool:
        """
        Commence la recherche d'une technologie
        
        Args:
            tech_id: ID de la technologie à rechercher
            
        Returns:
            True si la recherche a commencé
        """
        if self.technology_tree.start_research(tech_id):
            print(f"Recherche de '{tech_id}' commencée")
            return True
        return False
    
    def get_game_status(self) -> Dict:
        """
        Retourne le statut complet du jeu
        
        Returns:
            Dictionnaire avec toutes les informations de jeu
        """
        if not self.current_planet:
            return {}
        
        return {
            'planet': self.current_planet.get_status_summary(),
            'resources': self.resource_manager.get_status_summary(),
            'technology': self.technology_tree.get_research_status(),
            'events': self.event_manager.get_active_events_summary(self.current_planet),
            'game_time': self.game_time,
            'is_paused': self.is_paused,
            'simulation_speed': self.simulation_speed,
            'stats': self.game_stats.copy()
        }
    
    def set_simulation_speed(self, speed: float):
        """
        Définit la vitesse de simulation
        
        Args:
            speed: Multiplicateur de vitesse (0.5 = moitié, 2.0 = double, etc.)
        """
        self.simulation_speed = max(0.1, min(5.0, speed))
        print(f"Vitesse de simulation: {self.simulation_speed}x")
    
    def autosave(self):
        """
        Sauvegarde automatique du jeu
        """
        if self.current_planet:
            filename = f"autosave_{self.current_planet.name.lower()}.json"
            if self.save_game(filename):
                print("Sauvegarde automatique effectuée")
    
    def save_game(self, filename: str) -> bool:
        """
        Sauvegarde la partie actuelle
        
        Args:
            filename: Nom du fichier de sauvegarde
            
        Returns:
            True si la sauvegarde a réussi
        """
        if not self.current_planet:
            return False
        
        try:
            save_data = {
                'version': GAME_VERSION,
                'save_time': time.time(),
                'game_time': self.game_time,
                'planet': self.current_planet.to_dict(),
                'resources': self.resource_manager.to_dict(),
                'technology': self.technology_tree.to_dict(),
                'stats': self.game_stats.copy(),
                'simulation_speed': self.simulation_speed
            }
            
            save_path = f"{SAVES_DIRECTORY}/{filename}"
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            
            self.game_saved.emit()
            print(f"Partie sauvegardée: {save_path}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
            return False
    
    def load_game(self, filename: str) -> bool:
        """
        Charge une partie sauvegardée
        
        Args:
            filename: Nom du fichier de sauvegarde
            
        Returns:
            True si le chargement a réussi
        """
        try:
            save_path = f"{SAVES_DIRECTORY}/{filename}"
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Vérifier la version
            if save_data.get('version') != GAME_VERSION:
                print("Attention: Version de sauvegarde différente")
            
            # Charger les données
            planet_data = save_data['planet']
            planet_name = planet_data['name']
            
            if planet_name not in self.available_planets:
                print(f"Planète '{planet_name}' non trouvée")
                return False
            
            # Recréer les objets
            self.current_planet = Planet.from_dict(planet_data, self.available_planets[planet_name])
            self.resource_manager = ResourceManager.from_dict(save_data['resources'])
            self.technology_tree = TechnologyTree.from_dict(save_data['technology'])
            
            # Restaurer l'état du jeu
            self.game_time = save_data.get('game_time', 0.0)
            self.game_stats = save_data.get('stats', {})
            self.simulation_speed = save_data.get('simulation_speed', 1.0)
            
            # Redémarrer la simulation
            self.start_simulation()
            
            print(f"Partie chargée: {filename}")
            return True
            
        except Exception as e:
            print(f"Erreur lors du chargement: {e}")
            return False