"""
Constantes globales pour TerraGenesis PC
"""

# Configuration de la fenêtre
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600

# Informations du jeu
GAME_TITLE = "TerraGenesis PC"
GAME_VERSION = "1.0.0"

# Paramètres de gameplay
INITIAL_CREDITS = 1000
INITIAL_ENERGY = 100
INITIAL_SCIENCE = 0

# Vitesse de simulation (en millisecondes)
SIMULATION_TICK_RATE = 1000  # 1 seconde

# Limites des paramètres planétaires
MIN_TEMPERATURE = -273.15  # Zéro absolu en Celsius
MAX_TEMPERATURE = 1000.0   # Température maximale supportée
MIN_PRESSURE = 0.0         # Vide spatial
MAX_PRESSURE = 10.0        # 10 atmosphères
MIN_OXYGEN = 0.0           # Pas d'oxygène
MAX_OXYGEN = 100.0         # 100% d'oxygène

# Valeurs cibles pour une planète habitable (Terre)
TARGET_TEMPERATURE = 15.0   # 15°C
TARGET_PRESSURE = 1.0       # 1 atmosphère
TARGET_OXYGEN = 21.0        # 21% d'oxygène

# Tolérance pour considérer une planète comme habitable
HABITABILITY_TOLERANCE = {
    'temperature': 20.0,  # ±20°C
    'pressure': 0.3,      # ±0.3 atm
    'oxygen': 5.0         # ±5%
}

# Couleurs de l'interface (format RGB)
COLORS = {
    'background': (20, 25, 40),
    'panel': (40, 45, 60),
    'text': (255, 255, 255),
    'accent': (0, 150, 255),
    'success': (0, 200, 100),
    'warning': (255, 200, 0),
    'danger': (255, 100, 100),
    'temperature': (255, 100, 100),
    'pressure': (100, 150, 255),
    'oxygen': (100, 255, 150)
}

# Chemins des fichiers
PLANETS_DATA_FILE = "data/planets.json"
TECHNOLOGIES_DATA_FILE = "data/technologies.json"
EVENTS_DATA_FILE = "data/events.json"
SAVES_DIRECTORY = "data/saves"

# Configuration audio
DEFAULT_MUSIC_VOLUME = 0.7
DEFAULT_SFX_VOLUME = 0.8