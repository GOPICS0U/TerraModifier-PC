"""
Système d'événements aléatoires pour TerraGenesis PC
"""

import json
import random
import time
from typing import Dict, List, Optional
from config.constants import EVENTS_DATA_FILE

class GameEvent:
    """
    Classe représentant un événement de jeu
    """
    
    def __init__(self, event_id: str, event_data: Dict):
        """
        Initialise un événement
        
        Args:
            event_id: Identifiant unique de l'événement
            event_data: Données de l'événement depuis le JSON
        """
        self.id = event_id
        self.name = event_data.get("name", "")
        self.description = event_data.get("description", "")
        self.type = event_data.get("type", "neutral")  # positive, negative, mixed, neutral
        self.probability = event_data.get("probability", 0.01)
        self.duration = event_data.get("duration", 0)  # Durée en secondes (0 = instantané)
        self.effects = event_data.get("effects", {})
        self.requirements = event_data.get("requirements", {})
        
        # État de l'événement
        self.start_time = time.time()
        self.is_active = True
        self.has_been_applied = False

class ActiveEvent:
    """
    Classe pour un événement actif sur une planète
    """
    
    def __init__(self, event: GameEvent):
        """
        Initialise un événement actif
        
        Args:
            event: Événement de base
        """
        self.event = event
        self.start_time = time.time()
        self.duration = event.duration
        self.effects_applied = False
    
    def is_expired(self) -> bool:
        """
        Vérifie si l'événement a expiré
        
        Returns:
            True si l'événement a expiré
        """
        if self.duration == 0:
            return self.effects_applied  # Événement instantané
        
        return time.time() - self.start_time >= self.duration
    
    def get_remaining_time(self) -> float:
        """
        Retourne le temps restant de l'événement
        
        Returns:
            Temps restant en secondes
        """
        if self.duration == 0:
            return 0.0
        
        remaining = self.duration - (time.time() - self.start_time)
        return max(0.0, remaining)
    
    def apply_effects(self, planet, resource_manager):
        """
        Applique les effets de l'événement
        
        Args:
            planet: Planète affectée
            resource_manager: Gestionnaire de ressources
        """
        effects = self.event.effects
        
        # Effets instantanés (appliqués une seule fois)
        if not self.effects_applied:
            # Bonus/malus de ressources
            if 'credits_bonus' in effects:
                resource_manager.add_resources({'credits': effects['credits_bonus']})
            if 'credits_cost' in effects:
                resource_manager.spend_resources({'credits': effects['credits_cost']})
            if 'energy_bonus' in effects:
                resource_manager.add_resources({'energy': effects['energy_bonus']})
            if 'energy_cost' in effects:
                resource_manager.spend_resources({'energy': effects['energy_cost']})
            if 'science_bonus' in effects:
                resource_manager.add_resources({'science': effects['science_bonus']})
            
            # Dégâts aux bâtiments
            if 'building_damage_chance' in effects:
                damage_chance = effects['building_damage_chance']
                for building_type in list(planet.buildings.keys()):
                    if random.random() < damage_chance:
                        planet.remove_building(building_type, 1)
                        print(f"Événement '{self.event.name}': {building_type} endommagé!")
            
            self.effects_applied = True
        
        # Effets continus (appliqués pendant toute la durée)
        if self.duration > 0 and not self.is_expired():
            # Modificateurs atmosphériques temporaires
            temp_modifier = effects.get('temperature_modifier', 0)
            pressure_modifier = effects.get('pressure_modifier', 0)
            oxygen_modifier = effects.get('oxygen_modifier', 0)
            
            # Ces modificateurs sont appliqués directement aux valeurs de base
            # (ils seront automatiquement supprimés quand l'événement expire)
            planet.base_temperature += temp_modifier * 0.001  # Application graduelle
            planet.base_pressure += pressure_modifier * 0.001
            planet.base_oxygen += oxygen_modifier * 0.001

class EventManager:
    """
    Gestionnaire des événements aléatoires
    """
    
    def __init__(self):
        """
        Initialise le gestionnaire d'événements
        """
        self.event_templates: Dict[str, GameEvent] = {}
        self.last_event_check = time.time()
        self.event_check_interval = 60.0  # Vérifier les événements toutes les 60 secondes
        
        # Charger les événements depuis le fichier JSON
        self.load_events()
    
    def load_events(self):
        """
        Charge les événements depuis le fichier JSON
        """
        try:
            with open(EVENTS_DATA_FILE, 'r', encoding='utf-8') as f:
                events_data = json.load(f)
            
            for event_id, data in events_data.items():
                self.event_templates[event_id] = GameEvent(event_id, data)
            
            print(f"Chargé {len(self.event_templates)} types d'événements")
            
        except FileNotFoundError:
            print(f"Fichier {EVENTS_DATA_FILE} non trouvé")
        except json.JSONDecodeError as e:
            print(f"Erreur de décodage JSON: {e}")
        except Exception as e:
            print(f"Erreur lors du chargement des événements: {e}")
    
    def update(self, planet, resource_manager, delta_time: float):
        """
        Met à jour le système d'événements
        
        Args:
            planet: Planète actuelle
            resource_manager: Gestionnaire de ressources
            delta_time: Temps écoulé depuis la dernière mise à jour
        """
        current_time = time.time()
        
        # Vérifier s'il faut déclencher de nouveaux événements
        if current_time - self.last_event_check >= self.event_check_interval:
            self._check_for_new_events(planet, resource_manager)
            self.last_event_check = current_time
        
        # Mettre à jour les événements actifs
        for active_event in planet.active_events[:]:  # Copie de la liste
            if active_event.is_expired():
                planet.active_events.remove(active_event)
                print(f"Événement '{active_event.event.name}' terminé")
            else:
                active_event.apply_effects(planet, resource_manager)
    
    def _check_for_new_events(self, planet, resource_manager):
        """
        Vérifie et déclenche potentiellement de nouveaux événements
        
        Args:
            planet: Planète actuelle
            resource_manager: Gestionnaire de ressources
        """
        for event_template in self.event_templates.values():
            # Vérifier la probabilité
            if random.random() > event_template.probability:
                continue
            
            # Vérifier les prérequis
            if not self._check_event_requirements(event_template, planet, resource_manager):
                continue
            
            # Vérifier qu'un événement du même type n'est pas déjà actif
            if any(ae.event.id == event_template.id for ae in planet.active_events):
                continue
            
            # Déclencher l'événement
            self.trigger_event(event_template.id, planet, resource_manager)
    
    def _check_event_requirements(self, event: GameEvent, planet, resource_manager) -> bool:
        """
        Vérifie si les prérequis d'un événement sont remplis
        
        Args:
            event: Événement à vérifier
            planet: Planète actuelle
            resource_manager: Gestionnaire de ressources
            
        Returns:
            True si les prérequis sont remplis
        """
        req = event.requirements
        
        # Vérifier le nombre minimum de bâtiments
        if 'min_buildings' in req:
            total_buildings = sum(planet.buildings.values())
            if total_buildings < req['min_buildings']:
                return False
        
        # Vérifier les planètes spécifiques
        if 'planets' in req:
            if planet.name not in req['planets']:
                return False
        
        # Vérifier l'habitabilité minimale
        if 'min_habitability' in req:
            if planet.calculate_habitability() < req['min_habitability']:
                return False
        
        # Vérifier les ressources minimales
        if 'min_science' in req:
            if resource_manager.science < req['min_science']:
                return False
        
        # Vérifier les bâtiments spécifiques
        if 'min_research_labs' in req:
            labs = planet.buildings.get('research_lab', 0)
            if labs < req['min_research_labs']:
                return False
        
        if 'min_mining_facilities' in req:
            mines = planet.buildings.get('mining_facility', 0)
            if mines < req['min_mining_facilities']:
                return False
        
        # Vérifier la pression minimale
        if 'min_pressure' in req:
            if planet.pressure < req['min_pressure']:
                return False
        
        return True
    
    def trigger_event(self, event_id: str, planet, resource_manager) -> bool:
        """
        Déclenche un événement spécifique
        
        Args:
            event_id: ID de l'événement à déclencher
            planet: Planète affectée
            resource_manager: Gestionnaire de ressources
            
        Returns:
            True si l'événement a été déclenché
        """
        if event_id not in self.event_templates:
            return False
        
        event_template = self.event_templates[event_id]
        active_event = ActiveEvent(event_template)
        planet.active_events.append(active_event)
        
        print(f"Événement déclenché: {event_template.name}")
        print(f"Description: {event_template.description}")
        
        return True
    
    def get_active_events_summary(self, planet) -> List[Dict]:
        """
        Retourne un résumé des événements actifs
        
        Args:
            planet: Planète à analyser
            
        Returns:
            Liste des événements actifs avec leurs informations
        """
        summary = []
        
        for active_event in planet.active_events:
            event_info = {
                'name': active_event.event.name,
                'description': active_event.event.description,
                'type': active_event.event.type,
                'remaining_time': active_event.get_remaining_time(),
                'duration': active_event.duration
            }
            summary.append(event_info)
        
        return summary
    
    def force_event(self, event_id: str, planet, resource_manager) -> bool:
        """
        Force le déclenchement d'un événement (pour les tests/debug)
        
        Args:
            event_id: ID de l'événement
            planet: Planète affectée
            resource_manager: Gestionnaire de ressources
            
        Returns:
            True si l'événement a été déclenché
        """
        return self.trigger_event(event_id, planet, resource_manager)