"""
Système d'arbre technologique pour TerraGenesis PC
"""

import json
from typing import Dict, List, Set, Optional
from config.constants import TECHNOLOGIES_DATA_FILE

class Technology:
    """
    Classe représentant une technologie individuelle
    """
    
    def __init__(self, tech_id: str, tech_data: Dict):
        """
        Initialise une technologie
        
        Args:
            tech_id: Identifiant unique de la technologie
            tech_data: Données de la technologie depuis le JSON
        """
        self.id = tech_id
        self.name = tech_data.get("name", "")
        self.description = tech_data.get("description", "")
        self.icon = tech_data.get("icon", "")
        self.cost = tech_data.get("cost", {})
        self.prerequisites = set(tech_data.get("prerequisites", []))
        self.unlocks = tech_data.get("unlocks", [])
        
        # État de la technologie
        self.is_researched = False
        self.is_available = len(self.prerequisites) == 0  # Disponible si pas de prérequis
        self.research_progress = 0.0  # Progression de la recherche (0-100)

class TechnologyTree:
    """
    Gestionnaire de l'arbre technologique
    """
    
    def __init__(self):
        """
        Initialise l'arbre technologique
        """
        self.technologies: Dict[str, Technology] = {}
        self.researched_technologies: Set[str] = set()
        self.current_research: Optional[str] = None
        self.research_progress = 0.0
        
        # Charger les technologies depuis le fichier JSON
        self.load_technologies()
        
        # Déverrouiller les technologies de base
        self._update_availability()
    
    def load_technologies(self):
        """
        Charge les technologies depuis le fichier JSON
        """
        try:
            with open(TECHNOLOGIES_DATA_FILE, 'r', encoding='utf-8') as f:
                tech_data = json.load(f)
            
            for tech_id, data in tech_data.items():
                self.technologies[tech_id] = Technology(tech_id, data)
            
            print(f"Chargé {len(self.technologies)} technologies")
            
        except FileNotFoundError:
            print(f"Fichier {TECHNOLOGIES_DATA_FILE} non trouvé")
        except json.JSONDecodeError as e:
            print(f"Erreur de décodage JSON: {e}")
        except Exception as e:
            print(f"Erreur lors du chargement des technologies: {e}")
    
    def start_research(self, tech_id: str) -> bool:
        """
        Commence la recherche d'une technologie
        
        Args:
            tech_id: ID de la technologie à rechercher
            
        Returns:
            True si la recherche a commencé
        """
        if tech_id not in self.technologies:
            return False
        
        tech = self.technologies[tech_id]
        
        # Vérifier si la technologie est disponible et pas déjà recherchée
        if not tech.is_available or tech.is_researched:
            return False
        
        # Arrêter la recherche actuelle si elle existe
        if self.current_research:
            self.technologies[self.current_research].research_progress = 0.0
        
        self.current_research = tech_id
        self.research_progress = 0.0
        tech.research_progress = 0.0
        
        return True
    
    def update_research(self, science_points: float, delta_time: float):
        """
        Met à jour la progression de la recherche
        
        Args:
            science_points: Points de science disponibles
            delta_time: Temps écoulé depuis la dernière mise à jour
        """
        if not self.current_research:
            return
        
        tech = self.technologies[self.current_research]
        science_cost = tech.cost.get('science', 100)
        
        # Calculer la progression (1 point de science = 1% de progression)
        progress_per_second = science_points / science_cost * 100
        progress_increase = progress_per_second * delta_time
        
        tech.research_progress += progress_increase
        self.research_progress = tech.research_progress
        
        # Vérifier si la recherche est terminée
        if tech.research_progress >= 100.0:
            self.complete_research(self.current_research)
    
    def complete_research(self, tech_id: str):
        """
        Termine la recherche d'une technologie
        
        Args:
            tech_id: ID de la technologie terminée
        """
        if tech_id not in self.technologies:
            return
        
        tech = self.technologies[tech_id]
        tech.is_researched = True
        tech.research_progress = 100.0
        self.researched_technologies.add(tech_id)
        
        # Réinitialiser la recherche actuelle
        if self.current_research == tech_id:
            self.current_research = None
            self.research_progress = 0.0
        
        # Mettre à jour la disponibilité des autres technologies
        self._update_availability()
        
        print(f"Technologie '{tech.name}' recherchée avec succès!")
    
    def _update_availability(self):
        """
        Met à jour la disponibilité des technologies basée sur les prérequis
        """
        for tech in self.technologies.values():
            if not tech.is_researched:
                # Une technologie est disponible si tous ses prérequis sont recherchés
                tech.is_available = tech.prerequisites.issubset(self.researched_technologies)
    
    def get_available_technologies(self) -> List[Technology]:
        """
        Retourne la liste des technologies disponibles pour la recherche
        
        Returns:
            Liste des technologies disponibles
        """
        return [tech for tech in self.technologies.values() 
                if tech.is_available and not tech.is_researched]
    
    def get_researched_technologies(self) -> List[Technology]:
        """
        Retourne la liste des technologies déjà recherchées
        
        Returns:
            Liste des technologies recherchées
        """
        return [tech for tech in self.technologies.values() if tech.is_researched]
    
    def get_unlocked_buildings(self) -> List[str]:
        """
        Retourne la liste des bâtiments débloqués par les technologies recherchées
        
        Returns:
            Liste des bâtiments disponibles
        """
        unlocked = []
        for tech in self.get_researched_technologies():
            unlocked.extend(tech.unlocks)
        return list(set(unlocked))  # Supprimer les doublons
    
    def is_building_unlocked(self, building_type: str) -> bool:
        """
        Vérifie si un bâtiment est débloqué
        
        Args:
            building_type: Type de bâtiment à vérifier
            
        Returns:
            True si le bâtiment est débloqué
        """
        return building_type in self.get_unlocked_buildings()
    
    def get_research_status(self) -> Dict:
        """
        Retourne le statut actuel de la recherche
        
        Returns:
            Dictionnaire avec les informations de recherche
        """
        status = {
            'current_research': None,
            'progress': 0.0,
            'researched_count': len(self.researched_technologies),
            'available_count': len(self.get_available_technologies()),
            'total_count': len(self.technologies)
        }
        
        if self.current_research:
            tech = self.technologies[self.current_research]
            status['current_research'] = {
                'id': tech.id,
                'name': tech.name,
                'progress': tech.research_progress,
                'cost': tech.cost
            }
        
        return status
    
    def to_dict(self) -> Dict:
        """
        Convertit l'arbre technologique en dictionnaire pour la sauvegarde
        
        Returns:
            Dictionnaire représentant l'arbre technologique
        """
        return {
            'researched_technologies': list(self.researched_technologies),
            'current_research': self.current_research,
            'research_progress': self.research_progress,
            'technology_progress': {
                tech_id: tech.research_progress 
                for tech_id, tech in self.technologies.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """
        Crée un arbre technologique depuis un dictionnaire de sauvegarde
        
        Args:
            data: Données de sauvegarde
            
        Returns:
            Instance de TechnologyTree
        """
        tree = cls()
        
        # Restaurer les technologies recherchées
        tree.researched_technologies = set(data.get('researched_technologies', []))
        for tech_id in tree.researched_technologies:
            if tech_id in tree.technologies:
                tree.technologies[tech_id].is_researched = True
        
        # Restaurer la recherche actuelle
        tree.current_research = data.get('current_research')
        tree.research_progress = data.get('research_progress', 0.0)
        
        # Restaurer la progression des technologies
        tech_progress = data.get('technology_progress', {})
        for tech_id, progress in tech_progress.items():
            if tech_id in tree.technologies:
                tree.technologies[tech_id].research_progress = progress
        
        # Mettre à jour la disponibilité
        tree._update_availability()
        
        return tree