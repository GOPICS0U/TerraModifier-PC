"""
Gestionnaire de sauvegarde pour TerraGenesis PC
"""

import os
import json
import time
from typing import List, Dict, Optional
from config.constants import SAVES_DIRECTORY

class SaveManager:
    """
    Gestionnaire pour les sauvegardes de jeu
    """
    
    def __init__(self):
        """
        Initialise le gestionnaire de sauvegarde
        """
        self.saves_directory = SAVES_DIRECTORY
        self._ensure_saves_directory()
    
    def _ensure_saves_directory(self):
        """
        S'assure que le répertoire de sauvegardes existe
        """
        if not os.path.exists(self.saves_directory):
            try:
                os.makedirs(self.saves_directory)
                print(f"Répertoire de sauvegardes créé: {self.saves_directory}")
            except Exception as e:
                print(f"Erreur lors de la création du répertoire de sauvegardes: {e}")
    
    def get_save_files(self) -> List[Dict]:
        """
        Retourne la liste des fichiers de sauvegarde disponibles
        
        Returns:
            Liste des sauvegardes avec leurs métadonnées
        """
        saves = []
        
        if not os.path.exists(self.saves_directory):
            return saves
        
        try:
            for filename in os.listdir(self.saves_directory):
                if filename.endswith('.json'):
                    save_path = os.path.join(self.saves_directory, filename)
                    save_info = self._get_save_info(save_path)
                    if save_info:
                        save_info['filename'] = filename
                        saves.append(save_info)
            
            # Trier par date de modification (plus récent en premier)
            saves.sort(key=lambda x: x.get('save_time', 0), reverse=True)
            
        except Exception as e:
            print(f"Erreur lors de la lecture des sauvegardes: {e}")
        
        return saves
    
    def _get_save_info(self, save_path: str) -> Optional[Dict]:
        """
        Extrait les informations d'un fichier de sauvegarde
        
        Args:
            save_path: Chemin vers le fichier de sauvegarde
            
        Returns:
            Dictionnaire avec les informations de la sauvegarde
        """
        try:
            with open(save_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # Informations du fichier
            file_stats = os.stat(save_path)
            file_size = file_stats.st_size
            
            # Extraire les informations importantes
            planet_name = save_data.get('planet', {}).get('name', 'Inconnu')
            save_time = save_data.get('save_time', file_stats.st_mtime)
            game_time = save_data.get('game_time', 0)
            version = save_data.get('version', 'Inconnue')
            
            # Informations sur l'état du jeu
            planet_data = save_data.get('planet', {})
            habitability = 0
            if 'temperature' in planet_data and 'pressure' in planet_data and 'oxygen' in planet_data:
                # Calculer approximativement l'habitabilité
                temp_diff = abs(planet_data['temperature'] - 15.0)
                pressure_diff = abs(planet_data['pressure'] - 1.0)
                oxygen_diff = abs(planet_data['oxygen'] - 21.0)
                
                temp_score = max(0, 1 - (temp_diff / 20.0))
                pressure_score = max(0, 1 - (pressure_diff / 0.3))
                oxygen_score = max(0, 1 - (oxygen_diff / 5.0))
                
                habitability = (temp_score * 0.4 + pressure_score * 0.3 + oxygen_score * 0.3) * 100
            
            resources = save_data.get('resources', {})
            credits = resources.get('credits', 0)
            science = resources.get('science', 0)
            
            return {
                'planet_name': planet_name,
                'save_time': save_time,
                'save_time_formatted': time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(save_time)),
                'game_time': game_time,
                'game_time_formatted': self._format_game_time(game_time),
                'version': version,
                'file_size': file_size,
                'file_size_formatted': self._format_file_size(file_size),
                'habitability': habitability,
                'credits': credits,
                'science': science,
                'is_autosave': 'autosave' in os.path.basename(save_path).lower()
            }
            
        except Exception as e:
            print(f"Erreur lors de la lecture de {save_path}: {e}")
            return None
    
    def _format_game_time(self, seconds: float) -> str:
        """
        Formate le temps de jeu en format lisible
        
        Args:
            seconds: Temps en secondes
            
        Returns:
            Temps formaté
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    def _format_file_size(self, size_bytes: int) -> str:
        """
        Formate la taille de fichier en format lisible
        
        Args:
            size_bytes: Taille en octets
            
        Returns:
            Taille formatée
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
    
    def delete_save(self, filename: str) -> bool:
        """
        Supprime un fichier de sauvegarde
        
        Args:
            filename: Nom du fichier à supprimer
            
        Returns:
            True si la suppression a réussi
        """
        try:
            save_path = os.path.join(self.saves_directory, filename)
            if os.path.exists(save_path):
                os.remove(save_path)
                print(f"Sauvegarde supprimée: {filename}")
                return True
            else:
                print(f"Fichier de sauvegarde non trouvé: {filename}")
                return False
        except Exception as e:
            print(f"Erreur lors de la suppression de {filename}: {e}")
            return False
    
    def backup_save(self, filename: str) -> bool:
        """
        Crée une sauvegarde de backup
        
        Args:
            filename: Nom du fichier à sauvegarder
            
        Returns:
            True si le backup a réussi
        """
        try:
            save_path = os.path.join(self.saves_directory, filename)
            if not os.path.exists(save_path):
                return False
            
            # Créer le nom du backup avec timestamp
            name_without_ext = os.path.splitext(filename)[0]
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            backup_filename = f"{name_without_ext}_backup_{timestamp}.json"
            backup_path = os.path.join(self.saves_directory, backup_filename)
            
            # Copier le fichier
            with open(save_path, 'r', encoding='utf-8') as src:
                with open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            
            print(f"Backup créé: {backup_filename}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de la création du backup: {e}")
            return False
    
    def cleanup_old_autosaves(self, max_autosaves: int = 5):
        """
        Nettoie les anciennes sauvegardes automatiques
        
        Args:
            max_autosaves: Nombre maximum de sauvegardes automatiques à conserver
        """
        try:
            saves = self.get_save_files()
            autosaves = [save for save in saves if save['is_autosave']]
            
            if len(autosaves) > max_autosaves:
                # Supprimer les plus anciennes
                autosaves_to_delete = autosaves[max_autosaves:]
                for save in autosaves_to_delete:
                    self.delete_save(save['filename'])
                
                print(f"Nettoyé {len(autosaves_to_delete)} anciennes sauvegardes automatiques")
                
        except Exception as e:
            print(f"Erreur lors du nettoyage des sauvegardes: {e}")
    
    def export_save(self, filename: str, export_path: str) -> bool:
        """
        Exporte une sauvegarde vers un autre répertoire
        
        Args:
            filename: Nom du fichier à exporter
            export_path: Chemin de destination
            
        Returns:
            True si l'export a réussi
        """
        try:
            save_path = os.path.join(self.saves_directory, filename)
            if not os.path.exists(save_path):
                return False
            
            with open(save_path, 'r', encoding='utf-8') as src:
                with open(export_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            
            print(f"Sauvegarde exportée vers: {export_path}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'export: {e}")
            return False
    
    def import_save(self, import_path: str, new_filename: Optional[str] = None) -> bool:
        """
        Importe une sauvegarde depuis un autre répertoire
        
        Args:
            import_path: Chemin du fichier à importer
            new_filename: Nouveau nom pour le fichier (optionnel)
            
        Returns:
            True si l'import a réussi
        """
        try:
            if not os.path.exists(import_path):
                return False
            
            # Déterminer le nom de destination
            if new_filename:
                dest_filename = new_filename
            else:
                dest_filename = os.path.basename(import_path)
            
            if not dest_filename.endswith('.json'):
                dest_filename += '.json'
            
            dest_path = os.path.join(self.saves_directory, dest_filename)
            
            # Vérifier que c'est un fichier de sauvegarde valide
            with open(import_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
                if 'planet' not in save_data or 'resources' not in save_data:
                    print("Fichier de sauvegarde invalide")
                    return False
            
            # Copier le fichier
            with open(import_path, 'r', encoding='utf-8') as src:
                with open(dest_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            
            print(f"Sauvegarde importée: {dest_filename}")
            return True
            
        except Exception as e:
            print(f"Erreur lors de l'import: {e}")
            return False