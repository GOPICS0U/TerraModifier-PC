"""
Gestionnaire audio pour TerraGenesis PC
"""

import pygame
import os
from typing import Dict, Optional
from config.constants import DEFAULT_MUSIC_VOLUME, DEFAULT_SFX_VOLUME

class AudioManager:
    """
    Gestionnaire pour la musique et les effets sonores
    """
    
    def __init__(self):
        """
        Initialise le gestionnaire audio
        """
        self.is_initialized = False
        self.music_volume = DEFAULT_MUSIC_VOLUME
        self.sfx_volume = DEFAULT_SFX_VOLUME
        self.current_music = None
        self.sound_effects: Dict[str, pygame.mixer.Sound] = {}
        
        # Chemins des fichiers audio
        self.music_path = "assets/sounds/"
        self.sfx_path = "assets/sounds/"
    
    def initialize(self) -> bool:
        """
        Initialise le système audio
        
        Returns:
            True si l'initialisation a réussi
        """
        try:
            pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.init()
            self.is_initialized = True
            print("Système audio initialisé")
            return True
        except Exception as e:
            print(f"Erreur lors de l'initialisation audio: {e}")
            return False
    
    def play_background_music(self, filename: str, loop: bool = True) -> bool:
        """
        Joue une musique de fond
        
        Args:
            filename: Nom du fichier musical
            loop: Si True, la musique boucle indéfiniment
            
        Returns:
            True si la musique a été lancée
        """
        if not self.is_initialized:
            return False
        
        try:
            music_file = os.path.join(self.music_path, filename)
            
            # Vérifier si le fichier existe
            if not os.path.exists(music_file):
                print(f"Fichier musical non trouvé: {music_file}")
                return False
            
            pygame.mixer.music.load(music_file)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1 if loop else 0)
            
            self.current_music = filename
            print(f"Musique lancée: {filename}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de la lecture de la musique: {e}")
            return False
    
    def stop_music(self):
        """
        Arrête la musique de fond
        """
        if self.is_initialized:
            pygame.mixer.music.stop()
            self.current_music = None
    
    def pause_music(self):
        """
        Met en pause la musique de fond
        """
        if self.is_initialized:
            pygame.mixer.music.pause()
    
    def resume_music(self):
        """
        Reprend la musique de fond
        """
        if self.is_initialized:
            pygame.mixer.music.unpause()
    
    def set_music_volume(self, volume: float):
        """
        Définit le volume de la musique
        
        Args:
            volume: Volume entre 0.0 et 1.0
        """
        self.music_volume = max(0.0, min(1.0, volume))
        if self.is_initialized:
            pygame.mixer.music.set_volume(self.music_volume)
    
    def load_sound_effect(self, name: str, filename: str) -> bool:
        """
        Charge un effet sonore
        
        Args:
            name: Nom de l'effet sonore
            filename: Nom du fichier
            
        Returns:
            True si le chargement a réussi
        """
        if not self.is_initialized:
            return False
        
        try:
            sound_file = os.path.join(self.sfx_path, filename)
            
            if not os.path.exists(sound_file):
                print(f"Fichier sonore non trouvé: {sound_file}")
                return False
            
            sound = pygame.mixer.Sound(sound_file)
            sound.set_volume(self.sfx_volume)
            self.sound_effects[name] = sound
            
            print(f"Effet sonore chargé: {name}")
            return True
            
        except Exception as e:
            print(f"Erreur lors du chargement de l'effet sonore: {e}")
            return False
    
    def play_sound_effect(self, name: str) -> bool:
        """
        Joue un effet sonore
        
        Args:
            name: Nom de l'effet sonore
            
        Returns:
            True si l'effet a été joué
        """
        if not self.is_initialized or name not in self.sound_effects:
            return False
        
        try:
            self.sound_effects[name].play()
            return True
        except Exception as e:
            print(f"Erreur lors de la lecture de l'effet sonore: {e}")
            return False
    
    def set_sfx_volume(self, volume: float):
        """
        Définit le volume des effets sonores
        
        Args:
            volume: Volume entre 0.0 et 1.0
        """
        self.sfx_volume = max(0.0, min(1.0, volume))
        
        # Mettre à jour le volume de tous les effets chargés
        for sound in self.sound_effects.values():
            sound.set_volume(self.sfx_volume)
    
    def load_default_sounds(self):
        """
        Charge les effets sonores par défaut du jeu
        """
        default_sounds = {
            'button_click': 'button_click.wav',
            'building_built': 'building_built.wav',
            'research_complete': 'research_complete.wav',
            'event_positive': 'event_positive.wav',
            'event_negative': 'event_negative.wav',
            'notification': 'notification.wav'
        }
        
        for name, filename in default_sounds.items():
            self.load_sound_effect(name, filename)
    
    def cleanup(self):
        """
        Nettoie les ressources audio
        """
        if self.is_initialized:
            pygame.mixer.music.stop()
            pygame.mixer.quit()
            self.is_initialized = False
            print("Système audio fermé")
    
    def get_status(self) -> Dict:
        """
        Retourne le statut du système audio
        
        Returns:
            Dictionnaire avec les informations audio
        """
        return {
            'initialized': self.is_initialized,
            'music_volume': self.music_volume,
            'sfx_volume': self.sfx_volume,
            'current_music': self.current_music,
            'loaded_sounds': list(self.sound_effects.keys()),
            'music_playing': pygame.mixer.music.get_busy() if self.is_initialized else False
        }