"""
Gestionnaire des paramètres du jeu TerraGenesis PC
"""

import json
import os
from typing import Dict, Any

class GameSettings:
    """
    Classe pour gérer les paramètres du jeu
    Sauvegarde et charge automatiquement depuis un fichier JSON
    """
    
    def __init__(self, settings_file: str = "settings.json"):
        """
        Initialise les paramètres du jeu
        
        Args:
            settings_file: Nom du fichier de paramètres
        """
        self.settings_file = settings_file
        self.settings = self._load_default_settings()
        self.load_settings()
    
    def _load_default_settings(self) -> Dict[str, Any]:
        """
        Charge les paramètres par défaut
        
        Returns:
            Dictionnaire des paramètres par défaut
        """
        return {
            # Paramètres d'affichage
            "fullscreen": False,
            "window_width": 1200,
            "window_height": 800,
            "vsync": True,
            
            # Paramètres audio
            "music_enabled": True,
            "music_volume": 0.7,
            "sfx_enabled": True,
            "sfx_volume": 0.8,
            
            # Paramètres de gameplay
            "auto_save": True,
            "auto_save_interval": 300,  # 5 minutes
            "simulation_speed": 1.0,
            "show_tooltips": True,
            "difficulty": "normal",  # easy, normal, hard
            
            # Paramètres de langue
            "language": "fr",
            
            # Paramètres avancés
            "debug_mode": False,
            "show_fps": False
        }
    
    def load_settings(self):
        """
        Charge les paramètres depuis le fichier JSON
        """
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # Fusionner avec les paramètres par défaut
                    self.settings.update(loaded_settings)
                    print(f"Paramètres chargés depuis {self.settings_file}")
            else:
                print("Fichier de paramètres non trouvé, utilisation des valeurs par défaut")
                self.save_settings()  # Créer le fichier avec les valeurs par défaut
        except Exception as e:
            print(f"Erreur lors du chargement des paramètres: {e}")
            print("Utilisation des paramètres par défaut")
    
    def save_settings(self):
        """
        Sauvegarde les paramètres dans le fichier JSON
        """
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
            print(f"Paramètres sauvegardés dans {self.settings_file}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde des paramètres: {e}")
    
    def get(self, key: str, default=None):
        """
        Récupère une valeur de paramètre
        
        Args:
            key: Clé du paramètre
            default: Valeur par défaut si la clé n'existe pas
            
        Returns:
            Valeur du paramètre
        """
        return self.settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """
        Définit une valeur de paramètre
        
        Args:
            key: Clé du paramètre
            value: Nouvelle valeur
        """
        self.settings[key] = value
    
    # Propriétés pour un accès facile aux paramètres courants
    @property
    def fullscreen(self) -> bool:
        return self.settings["fullscreen"]
    
    @property
    def window_width(self) -> int:
        return self.settings["window_width"]
    
    @property
    def window_height(self) -> int:
        return self.settings["window_height"]
    
    @property
    def music_enabled(self) -> bool:
        return self.settings["music_enabled"]
    
    @property
    def music_volume(self) -> float:
        return self.settings["music_volume"]
    
    @property
    def sfx_enabled(self) -> bool:
        return self.settings["sfx_enabled"]
    
    @property
    def sfx_volume(self) -> float:
        return self.settings["sfx_volume"]
    
    @property
    def auto_save(self) -> bool:
        return self.settings["auto_save"]
    
    @property
    def simulation_speed(self) -> float:
        return self.settings["simulation_speed"]
    
    @property
    def difficulty(self) -> str:
        return self.settings["difficulty"]