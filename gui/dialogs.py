"""
Boîtes de dialogue utilitaires pour TerraGenesis PC
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QListWidget, 
                            QListWidgetItem, QLabel, QPushButton,
                            QTextEdit, QGroupBox, QGridLayout, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from utils.helpers import format_time, format_number

class LoadGameDialog(QDialog):
    """
    Boîte de dialogue pour charger une partie sauvegardée
    """
    
    def __init__(self, save_files: list, parent=None):
        """
        Initialise la boîte de dialogue
        
        Args:
            save_files: Liste des fichiers de sauvegarde
            parent: Widget parent
        """
        super().__init__(parent)
        
        self.save_files = save_files
        self.selected_save = None
        
        self.setup_ui()
        self.setup_style()
        self.populate_saves()
    
    def setup_ui(self):
        """
        Configure l'interface
        """
        self.setWindowTitle("Charger une partie")
        self.setModal(True)
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # Titre
        title_label = QLabel("Sélectionnez une sauvegarde à charger")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Liste des sauvegardes
        self.saves_list = QListWidget()
        self.saves_list.itemSelectionChanged.connect(self.on_selection_changed)
        self.saves_list.itemDoubleClicked.connect(self.on_double_click)
        layout.addWidget(self.saves_list)
        
        # Zone d'informations détaillées
        self.info_group = QGroupBox("Détails de la sauvegarde")
        info_layout = QGridLayout(self.info_group)
        
        self.planet_label = QLabel("-")
        self.date_label = QLabel("-")
        self.time_label = QLabel("-")
        self.habitability_label = QLabel("-")
        self.credits_label = QLabel("-")
        self.science_label = QLabel("-")
        
        info_layout.addWidget(QLabel("Planète:"), 0, 0)
        info_layout.addWidget(self.planet_label, 0, 1)
        info_layout.addWidget(QLabel("Date de sauvegarde:"), 1, 0)
        info_layout.addWidget(self.date_label, 1, 1)
        info_layout.addWidget(QLabel("Temps de jeu:"), 2, 0)
        info_layout.addWidget(self.time_label, 2, 1)
        info_layout.addWidget(QLabel("Habitabilité:"), 0, 2)
        info_layout.addWidget(self.habitability_label, 0, 3)
        info_layout.addWidget(QLabel("Crédits:"), 1, 2)
        info_layout.addWidget(self.credits_label, 1, 3)
        info_layout.addWidget(QLabel("Science:"), 2, 2)
        info_layout.addWidget(self.science_label, 2, 3)
        
        layout.addWidget(self.info_group)
        
        # Boutons
        button_layout = QHBoxLayout()
        
        self.delete_button = QPushButton("Supprimer")
        self.delete_button.clicked.connect(self.delete_save)
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)
        
        button_layout.addStretch()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setEnabled(False)
        
        cancel_button = QPushButton("Annuler")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def setup_style(self):
        """
        Configure le style
        """
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QListWidget {
                background-color: #2d2d2d;
                border: 1px solid #555555;
                color: #ffffff;
                selection-background-color: #0078d4;
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
    
    def populate_saves(self):
        """
        Remplit la liste des sauvegardes
        """
        for save_data in self.save_files:
            item = QListWidgetItem()
            
            # Texte principal
            planet_name = save_data['planet_name']
            save_time = save_data['save_time_formatted']
            game_time = save_data['game_time_formatted']
            
            if save_data['is_autosave']:
                text = f"[AUTO] {planet_name} - {save_time}"
            else:
                text = f"{planet_name} - {save_time}"
            
            item.setText(text)
            item.setData(Qt.UserRole, save_data)
            
            # Couleur selon le type
            if save_data['is_autosave']:
                item.setForeground(Qt.yellow)
            
            self.saves_list.addItem(item)
    
    def on_selection_changed(self):
        """
        Appelé quand la sélection change
        """
        current_item = self.saves_list.currentItem()
        if current_item:
            save_data = current_item.data(Qt.UserRole)
            self.selected_save = save_data
            self.update_info_display(save_data)
            self.ok_button.setEnabled(True)
            self.delete_button.setEnabled(True)
        else:
            self.selected_save = None
            self.clear_info_display()
            self.ok_button.setEnabled(False)
            self.delete_button.setEnabled(False)
    
    def on_double_click(self, item):
        """
        Appelé lors d'un double-clic
        
        Args:
            item: Item cliqué
        """
        if item:
            self.accept()
    
    def update_info_display(self, save_data: dict):
        """
        Met à jour l'affichage des informations
        
        Args:
            save_data: Données de la sauvegarde
        """
        self.planet_label.setText(save_data['planet_name'])
        self.date_label.setText(save_data['save_time_formatted'])
        self.time_label.setText(save_data['game_time_formatted'])
        self.habitability_label.setText(f"{save_data['habitability']:.1f}%")
        self.credits_label.setText(format_number(save_data['credits']))
        self.science_label.setText(format_number(save_data['science']))
    
    def clear_info_display(self):
        """
        Efface l'affichage des informations
        """
        labels = [self.planet_label, self.date_label, self.time_label,
                 self.habitability_label, self.credits_label, self.science_label]
        for label in labels:
            label.setText("-")
    
    def delete_save(self):
        """
        Supprime la sauvegarde sélectionnée
        """
        if not self.selected_save:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirmer la suppression",
            f"Êtes-vous sûr de vouloir supprimer la sauvegarde '{self.selected_save['filename']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Supprimer de la liste
            current_row = self.saves_list.currentRow()
            self.saves_list.takeItem(current_row)
            
            # Supprimer le fichier (sera fait par le gestionnaire de sauvegarde)
            from utils.save_manager import SaveManager
            save_manager = SaveManager()
            save_manager.delete_save(self.selected_save['filename'])
            
            # Réinitialiser la sélection
            self.selected_save = None
            self.clear_info_display()
            self.ok_button.setEnabled(False)
            self.delete_button.setEnabled(False)
    
    def get_selected_save(self):
        """
        Retourne la sauvegarde sélectionnée
        
        Returns:
            Données de la sauvegarde sélectionnée
        """
        return self.selected_save

class TechnologyDetailsDialog(QDialog):
    """
    Boîte de dialogue pour afficher les détails d'une technologie
    """
    
    def __init__(self, technology, parent=None):
        """
        Initialise la boîte de dialogue
        
        Args:
            technology: Objet Technology
            parent: Widget parent
        """
        super().__init__(parent)
        
        self.technology = technology
        self.setup_ui()
        self.setup_style()
    
    def setup_ui(self):
        """
        Configure l'interface
        """
        self.setWindowTitle(f"Technologie: {self.technology.name}")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Nom de la technologie
        name_label = QLabel(self.technology.name)
        name_font = QFont()
        name_font.setPointSize(16)
        name_font.setBold(True)
        name_label.setFont(name_font)
        layout.addWidget(name_label)
        
        # Description
        desc_text = QTextEdit()
        desc_text.setReadOnly(True)
        desc_text.setMaximumHeight(100)
        desc_text.setText(self.technology.description)
        layout.addWidget(desc_text)
        
        # Informations
        info_group = QGroupBox("Informations")
        info_layout = QGridLayout(info_group)
        
        # Coût
        cost_text = ", ".join([f"{resource}: {amount}" 
                              for resource, amount in self.technology.cost.items()])
        info_layout.addWidget(QLabel("Coût:"), 0, 0)
        info_layout.addWidget(QLabel(cost_text), 0, 1)
        
        # Prérequis
        if self.technology.prerequisites:
            prereq_text = ", ".join(self.technology.prerequisites)
        else:
            prereq_text = "Aucun"
        info_layout.addWidget(QLabel("Prérequis:"), 1, 0)
        info_layout.addWidget(QLabel(prereq_text), 1, 1)
        
        # Débloque
        if self.technology.unlocks:
            unlocks_text = ", ".join(self.technology.unlocks)
        else:
            unlocks_text = "Rien"
        info_layout.addWidget(QLabel("Débloque:"), 2, 0)
        info_layout.addWidget(QLabel(unlocks_text), 2, 1)
        
        # État
        if self.technology.is_researched:
            status_text = "Recherchée"
            status_color = "#00FF00"
        elif self.technology.is_available:
            status_text = "Disponible"
            status_color = "#FFFF00"
        else:
            status_text = "Verrouillée"
            status_color = "#FF0000"
        
        status_label = QLabel(status_text)
        status_label.setStyleSheet(f"color: {status_color}; font-weight: bold;")
        info_layout.addWidget(QLabel("État:"), 3, 0)
        info_layout.addWidget(status_label, 3, 1)
        
        layout.addWidget(info_group)
        
        # Bouton de fermeture
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
    
    def setup_style(self):
        """
        Configure le style
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
        """)

class EventDetailsDialog(QDialog):
    """
    Boîte de dialogue pour afficher les détails d'un événement
    """
    
    def __init__(self, event_info: dict, parent=None):
        """
        Initialise la boîte de dialogue
        
        Args:
            event_info: Informations de l'événement
            parent: Widget parent
        """
        super().__init__(parent)
        
        self.event_info = event_info
        self.setup_ui()
        self.setup_style()
    
    def setup_ui(self):
        """
        Configure l'interface
        """
        self.setWindowTitle(f"Événement: {self.event_info['name']}")
        self.setModal(True)
        self.resize(400, 250)
        
        layout = QVBoxLayout(self)
        
        # Nom de l'événement
        name_label = QLabel(self.event_info['name'])
        name_font = QFont()
        name_font.setPointSize(16)
        name_font.setBold(True)
        name_label.setFont(name_font)
        
        # Couleur selon le type
        event_type = self.event_info.get('type', 'neutral')
        type_colors = {
            'positive': '#00FF00',
            'negative': '#FF0000',
            'mixed': '#FFFF00',
            'neutral': '#FFFFFF'
        }
        name_label.setStyleSheet(f"color: {type_colors.get(event_type, '#FFFFFF')};")
        layout.addWidget(name_label)
        
        # Description
        desc_text = QTextEdit()
        desc_text.setReadOnly(True)
        desc_text.setText(self.event_info['description'])
        layout.addWidget(desc_text)
        
        # Informations sur la durée
        remaining_time = self.event_info.get('remaining_time', 0)
        duration = self.event_info.get('duration', 0)
        
        if duration > 0:
            time_info = f"Temps restant: {format_time(remaining_time)} / {format_time(duration)}"
        else:
            time_info = "Événement instantané"
        
        time_label = QLabel(time_info)
        layout.addWidget(time_label)
        
        # Bouton de fermeture
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
    
    def setup_style(self):
        """
        Configure le style
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
        """)