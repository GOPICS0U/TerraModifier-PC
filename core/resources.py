"""
Gestionnaire des ressources du jeu (crédits, énergie, science)
"""

from typing import Dict, Optional
from config.constants import INITIAL_CREDITS, INITIAL_ENERGY, INITIAL_SCIENCE

class ResourceManager:
    """
    Classe pour gérer les ressources du joueur
    """
    
    def __init__(self):
        """
        Initialise le gestionnaire de ressources
        """
        # Ressources actuelles
        self.credits = INITIAL_CREDITS
        self.energy = INITIAL_ENERGY
        self.science = INITIAL_SCIENCE
        
        # Taux de production par seconde
        self.credits_per_second = 0.0
        self.energy_per_second = 0.0
        self.science_per_second = 0.0
        
        # Consommation par seconde
        self.energy_consumption = 0.0
        
        # Capacités maximales
        self.max_energy = 1000
        self.max_science = 10000
        # Les crédits n'ont pas de limite
        
        # Historique pour les graphiques
        self.history = {
            'credits': [self.credits],
            'energy': [self.energy],
            'science': [self.science]
        }
    
    def update(self, delta_time: float):
        """
        Met à jour les ressources basées sur la production
        
        Args:
            delta_time: Temps écoulé depuis la dernière mise à jour (en secondes)
        """
        # Calculer les changements
        credits_change = self.credits_per_second * delta_time
        energy_change = (self.energy_per_second - self.energy_consumption) * delta_time
        science_change = self.science_per_second * delta_time
        
        # Appliquer les changements
        self.credits += credits_change
        self.energy += energy_change
        self.science += science_change
        
        # Appliquer les limites
        self.credits = max(0, self.credits)  # Les crédits ne peuvent pas être négatifs
        self.energy = max(0, min(self.max_energy, self.energy))
        self.science = max(0, min(self.max_science, self.science))
        
        # Ajouter à l'historique (limiter à 100 entrées)
        if len(self.history['credits']) >= 100:
            for key in self.history:
                self.history[key].pop(0)
        
        self.history['credits'].append(self.credits)
        self.history['energy'].append(self.energy)
        self.history['science'].append(self.science)
    
    def can_afford(self, cost: Dict[str, float]) -> bool:
        """
        Vérifie si le joueur peut se permettre un coût
        
        Args:
            cost: Dictionnaire des coûts {'credits': X, 'energy': Y, 'science': Z}
            
        Returns:
            True si le joueur peut se permettre le coût
        """
        credits_needed = cost.get('credits', 0)
        energy_needed = cost.get('energy', 0)
        science_needed = cost.get('science', 0)
        
        return (self.credits >= credits_needed and 
                self.energy >= energy_needed and 
                self.science >= science_needed)
    
    def spend_resources(self, cost: Dict[str, float]) -> bool:
        """
        Dépense des ressources si possible
        
        Args:
            cost: Dictionnaire des coûts
            
        Returns:
            True si les ressources ont été dépensées
        """
        if not self.can_afford(cost):
            return False
        
        self.credits -= cost.get('credits', 0)
        self.energy -= cost.get('energy', 0)
        self.science -= cost.get('science', 0)
        
        return True
    
    def add_resources(self, resources: Dict[str, float]):
        """
        Ajoute des ressources
        
        Args:
            resources: Dictionnaire des ressources à ajouter
        """
        self.credits += resources.get('credits', 0)
        self.energy += resources.get('energy', 0)
        self.science += resources.get('science', 0)
        
        # Appliquer les limites
        self.credits = max(0, self.credits)
        self.energy = max(0, min(self.max_energy, self.energy))
        self.science = max(0, min(self.max_science, self.science))
    
    def calculate_production(self, planet, buildings: Dict[str, int]):
        """
        Calcule la production de ressources basée sur les bâtiments
        
        Args:
            planet: Planète actuelle
            buildings: Dictionnaire des bâtiments {type: count}
        """
        # Réinitialiser la production
        self.credits_per_second = 0.0
        self.energy_per_second = 0.0
        self.science_per_second = 0.0
        self.energy_consumption = 0.0
        
        # Production de base (revenus passifs)
        self.credits_per_second += 1.0  # 1 crédit par seconde de base
        
        # Effets des bâtiments
        building_effects = {
            'solar_panel': {
                'energy_production': 5.0,
                'credits_production': 0.5
            },
            'research_lab': {
                'science_production': 2.0,
                'energy_consumption': 3.0
            },
            'mining_facility': {
                'credits_production': 3.0,
                'energy_consumption': 2.0
            },
            'heater': {
                'energy_consumption': 4.0
            },
            'cooler': {
                'energy_consumption': 4.0
            },
            'atmosphere_processor': {
                'energy_consumption': 6.0,
                'credits_production': 1.0
            },
            'oxygen_generator': {
                'energy_consumption': 5.0
            },
            'greenhouse': {
                'energy_consumption': 2.0,
                'science_production': 1.0
            }
        }
        
        # Calculer les effets de tous les bâtiments
        for building_type, count in buildings.items():
            if building_type in building_effects:
                effects = building_effects[building_type]
                
                self.credits_per_second += effects.get('credits_production', 0) * count
                self.energy_per_second += effects.get('energy_production', 0) * count
                self.science_per_second += effects.get('science_production', 0) * count
                self.energy_consumption += effects.get('energy_consumption', 0) * count
        
        # Bonus basés sur l'habitabilité de la planète
        habitability = planet.calculate_habitability()
        habitability_bonus = habitability / 100.0
        
        # Plus la planète est habitable, plus elle génère de revenus
        self.credits_per_second *= (1.0 + habitability_bonus * 0.5)
        self.science_per_second *= (1.0 + habitability_bonus * 0.3)
    
    def get_net_production(self) -> Dict[str, float]:
        """
        Retourne la production nette par seconde
        
        Returns:
            Dictionnaire avec la production nette
        """
        return {
            'credits': self.credits_per_second,
            'energy': self.energy_per_second - self.energy_consumption,
            'science': self.science_per_second
        }
    
    def get_status_summary(self) -> Dict[str, str]:
        """
        Retourne un résumé du statut des ressources
        
        Returns:
            Dictionnaire avec les informations formatées
        """
        net_production = self.get_net_production()
        
        return {
            'credits': f"{self.credits:.0f} (+{net_production['credits']:.1f}/s)",
            'energy': f"{self.energy:.0f}/{self.max_energy} ({net_production['energy']:+.1f}/s)",
            'science': f"{self.science:.0f}/{self.max_science} (+{net_production['science']:.1f}/s)"
        }
    
    def to_dict(self) -> Dict:
        """
        Convertit les ressources en dictionnaire pour la sauvegarde
        
        Returns:
            Dictionnaire représentant les ressources
        """
        return {
            'credits': self.credits,
            'energy': self.energy,
            'science': self.science,
            'max_energy': self.max_energy,
            'max_science': self.max_science,
            'history': self.history.copy()
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """
        Crée un gestionnaire de ressources depuis un dictionnaire
        
        Args:
            data: Données de sauvegarde
            
        Returns:
            Instance de ResourceManager
        """
        manager = cls()
        manager.credits = data.get('credits', INITIAL_CREDITS)
        manager.energy = data.get('energy', INITIAL_ENERGY)
        manager.science = data.get('science', INITIAL_SCIENCE)
        manager.max_energy = data.get('max_energy', 1000)
        manager.max_science = data.get('max_science', 10000)
        manager.history = data.get('history', manager.history)
        
        return manager