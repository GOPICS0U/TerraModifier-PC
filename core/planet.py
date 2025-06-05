"""
Classe Planet - Représente une planète à terraformer
"""

import math
from typing import Dict, List, Optional
from config.constants import *

class Planet:
    """
    Classe représentant une planète avec ses paramètres atmosphériques
    et ses capacités de terraformation
    """
    
    def __init__(self, name: str, planet_data: Dict):
        """
        Initialise une planète
        
        Args:
            name: Nom de la planète
            planet_data: Données de la planète depuis le fichier JSON
        """
        self.name = name
        self.description = planet_data.get("description", "")
        self.image_path = planet_data.get("image", "")
        
        # Paramètres atmosphériques actuels
        self.temperature = planet_data.get("initial_temperature", 0.0)
        self.pressure = planet_data.get("initial_pressure", 0.0)
        self.oxygen = planet_data.get("initial_oxygen", 0.0)
        
        # Paramètres de base de la planète (ne changent pas)
        self.base_temperature = self.temperature
        self.base_pressure = self.pressure
        self.base_oxygen = self.oxygen
        
        # Modificateurs de terraformation (influence des bâtiments)
        self.temperature_modifier = 0.0
        self.pressure_modifier = 0.0
        self.oxygen_modifier = 0.0
        
        # Propriétés physiques de la planète
        self.mass = planet_data.get("mass", 1.0)  # Masse relative à la Terre
        self.distance_from_sun = planet_data.get("distance", 1.0)  # Distance relative
        self.day_length = planet_data.get("day_length", 24.0)  # Heures
        
        # Bâtiments construits sur la planète
        self.buildings = {}  # {building_type: count}
        
        # Historique des valeurs (pour les graphiques)
        self.history = {
            'temperature': [self.temperature],
            'pressure': [self.pressure],
            'oxygen': [self.oxygen],
            'habitability': [self.calculate_habitability()]
        }
        
        # Événements actifs sur la planète
        self.active_events = []
    
    def update(self, delta_time: float):
        """
        Met à jour les paramètres de la planète
        
        Args:
            delta_time: Temps écoulé depuis la dernière mise à jour (en secondes)
        """
        # Calculer les nouveaux paramètres basés sur les modificateurs
        self.temperature = self.base_temperature + self.temperature_modifier
        self.pressure = self.base_pressure + self.pressure_modifier
        self.oxygen = self.base_oxygen + self.oxygen_modifier
        
        # Appliquer les limites
        self.temperature = max(MIN_TEMPERATURE, min(MAX_TEMPERATURE, self.temperature))
        self.pressure = max(MIN_PRESSURE, min(MAX_PRESSURE, self.pressure))
        self.oxygen = max(MIN_OXYGEN, min(MAX_OXYGEN, self.oxygen))
        
        # Ajouter à l'historique (limiter à 100 entrées)
        if len(self.history['temperature']) >= 100:
            for key in self.history:
                self.history[key].pop(0)
        
        self.history['temperature'].append(self.temperature)
        self.history['pressure'].append(self.pressure)
        self.history['oxygen'].append(self.oxygen)
        self.history['habitability'].append(self.calculate_habitability())
        
        # Mettre à jour les événements actifs
        self._update_events(delta_time)
    
    def calculate_habitability(self) -> float:
        """
        Calcule le pourcentage d'habitabilité de la planète
        
        Returns:
            Pourcentage d'habitabilité (0-100)
        """
        # Calculer la distance par rapport aux valeurs cibles
        temp_diff = abs(self.temperature - TARGET_TEMPERATURE)
        pressure_diff = abs(self.pressure - TARGET_PRESSURE)
        oxygen_diff = abs(self.oxygen - TARGET_OXYGEN)
        
        # Calculer les scores individuels (0-1)
        temp_score = max(0, 1 - (temp_diff / HABITABILITY_TOLERANCE['temperature']))
        pressure_score = max(0, 1 - (pressure_diff / HABITABILITY_TOLERANCE['pressure']))
        oxygen_score = max(0, 1 - (oxygen_diff / HABITABILITY_TOLERANCE['oxygen']))
        
        # Score global (moyenne pondérée)
        habitability = (temp_score * 0.4 + pressure_score * 0.3 + oxygen_score * 0.3) * 100
        
        return min(100, max(0, habitability))
    
    def is_habitable(self) -> bool:
        """
        Détermine si la planète est habitable
        
        Returns:
            True si la planète est habitable
        """
        return self.calculate_habitability() >= 80.0
    
    def add_building(self, building_type: str, count: int = 1):
        """
        Ajoute des bâtiments à la planète
        
        Args:
            building_type: Type de bâtiment
            count: Nombre de bâtiments à ajouter
        """
        if building_type not in self.buildings:
            self.buildings[building_type] = 0
        self.buildings[building_type] += count
        
        # Recalculer les modificateurs
        self._update_modifiers()
    
    def remove_building(self, building_type: str, count: int = 1):
        """
        Retire des bâtiments de la planète
        
        Args:
            building_type: Type de bâtiment
            count: Nombre de bâtiments à retirer
        """
        if building_type in self.buildings:
            self.buildings[building_type] = max(0, self.buildings[building_type] - count)
            if self.buildings[building_type] == 0:
                del self.buildings[building_type]
        
        # Recalculer les modificateurs
        self._update_modifiers()
    
    def _update_modifiers(self):
        """
        Met à jour les modificateurs basés sur les bâtiments
        """
        # Réinitialiser les modificateurs
        self.temperature_modifier = 0.0
        self.pressure_modifier = 0.0
        self.oxygen_modifier = 0.0
        
        # Effets des bâtiments (à personnaliser selon les bâtiments)
        building_effects = {
            'heater': {'temperature': 5.0},
            'cooler': {'temperature': -5.0},
            'atmosphere_processor': {'pressure': 0.1},
            'oxygen_generator': {'oxygen': 2.0},
            'greenhouse': {'temperature': 2.0, 'oxygen': 1.0},
            'solar_panel': {},  # Génère de l'énergie mais pas d'effet atmosphérique
            'research_lab': {}  # Génère de la science
        }
        
        for building_type, count in self.buildings.items():
            if building_type in building_effects:
                effects = building_effects[building_type]
                self.temperature_modifier += effects.get('temperature', 0) * count
                self.pressure_modifier += effects.get('pressure', 0) * count
                self.oxygen_modifier += effects.get('oxygen', 0) * count
    
    def _update_events(self, delta_time: float):
        """
        Met à jour les événements actifs
        
        Args:
            delta_time: Temps écoulé
        """
        # Retirer les événements expirés
        self.active_events = [event for event in self.active_events 
                            if not event.is_expired()]
        
        # Appliquer les effets des événements actifs
        for event in self.active_events:
            event.apply_effects(self, delta_time)
    
    def apply_event(self, event):
        """
        Applique un événement à la planète
        
        Args:
            event: Événement à appliquer
        """
        self.active_events.append(event)
    
    def get_status_summary(self) -> Dict[str, str]:
        """
        Retourne un résumé du statut de la planète
        
        Returns:
            Dictionnaire avec les informations de statut
        """
        habitability = self.calculate_habitability()
        
        if habitability >= 80:
            status = "Habitable"
        elif habitability >= 50:
            status = "En cours de terraformation"
        elif habitability >= 20:
            status = "Hostile mais viable"
        else:
            status = "Inhabitable"
        
        return {
            'status': status,
            'habitability': f"{habitability:.1f}%",
            'temperature': f"{self.temperature:.1f}°C",
            'pressure': f"{self.pressure:.2f} atm",
            'oxygen': f"{self.oxygen:.1f}%",
            'buildings': len(self.buildings)
        }
    
    def to_dict(self) -> Dict:
        """
        Convertit la planète en dictionnaire pour la sauvegarde
        
        Returns:
            Dictionnaire représentant la planète
        """
        return {
            'name': self.name,
            'temperature': self.temperature,
            'pressure': self.pressure,
            'oxygen': self.oxygen,
            'base_temperature': self.base_temperature,
            'base_pressure': self.base_pressure,
            'base_oxygen': self.base_oxygen,
            'buildings': self.buildings.copy(),
            'history': self.history.copy()
        }
    
    @classmethod
    def from_dict(cls, data: Dict, planet_data: Dict):
        """
        Crée une planète depuis un dictionnaire de sauvegarde
        
        Args:
            data: Données de sauvegarde
            planet_data: Données de base de la planète
            
        Returns:
            Instance de Planet
        """
        planet = cls(data['name'], planet_data)
        planet.temperature = data.get('temperature', planet.temperature)
        planet.pressure = data.get('pressure', planet.pressure)
        planet.oxygen = data.get('oxygen', planet.oxygen)
        planet.buildings = data.get('buildings', {})
        planet.history = data.get('history', planet.history)
        
        # Recalculer les modificateurs
        planet._update_modifiers()
        
        return planet