"""
Fonctions utilitaires pour TerraGenesis PC
"""

import math
from typing import Union

def format_time(seconds: float) -> str:
    """
    Formate un temps en secondes en format lisible
    
    Args:
        seconds: Temps en secondes
        
    Returns:
        Temps formaté (ex: "2h 30m 15s")
    """
    if seconds < 0:
        return "0s"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if secs > 0 or not parts:  # Afficher les secondes si c'est le seul élément
        parts.append(f"{secs}s")
    
    return " ".join(parts)

def format_number(number: Union[int, float], precision: int = 1) -> str:
    """
    Formate un nombre avec des suffixes (K, M, B, etc.)
    
    Args:
        number: Nombre à formater
        precision: Nombre de décimales
        
    Returns:
        Nombre formaté (ex: "1.2K", "3.4M")
    """
    if abs(number) < 1000:
        if isinstance(number, int):
            return str(number)
        else:
            return f"{number:.{precision}f}"
    
    suffixes = ['', 'K', 'M', 'B', 'T', 'P']
    magnitude = 0
    
    while abs(number) >= 1000 and magnitude < len(suffixes) - 1:
        number /= 1000
        magnitude += 1
    
    return f"{number:.{precision}f}{suffixes[magnitude]}"

def format_percentage(value: float, precision: int = 1) -> str:
    """
    Formate un pourcentage
    
    Args:
        value: Valeur entre 0 et 100
        precision: Nombre de décimales
        
    Returns:
        Pourcentage formaté (ex: "75.5%")
    """
    return f"{value:.{precision}f}%"

def format_temperature(celsius: float) -> str:
    """
    Formate une température avec l'unité
    
    Args:
        celsius: Température en Celsius
        
    Returns:
        Température formatée (ex: "-60.5°C")
    """
    return f"{celsius:.1f}°C"

def format_pressure(atm: float) -> str:
    """
    Formate une pression atmosphérique
    
    Args:
        atm: Pression en atmosphères
        
    Returns:
        Pression formatée (ex: "0.006 atm")
    """
    if atm < 0.001:
        return f"{atm:.6f} atm"
    elif atm < 0.1:
        return f"{atm:.3f} atm"
    else:
        return f"{atm:.2f} atm"

def clamp(value: float, min_val: float, max_val: float) -> float:
    """
    Limite une valeur entre min et max
    
    Args:
        value: Valeur à limiter
        min_val: Valeur minimale
        max_val: Valeur maximale
        
    Returns:
        Valeur limitée
    """
    return max(min_val, min(max_val, value))

def lerp(start: float, end: float, t: float) -> float:
    """
    Interpolation linéaire entre deux valeurs
    
    Args:
        start: Valeur de départ
        end: Valeur d'arrivée
        t: Facteur d'interpolation (0-1)
        
    Returns:
        Valeur interpolée
    """
    return start + (end - start) * clamp(t, 0.0, 1.0)

def calculate_distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """
    Calcule la distance entre deux points
    
    Args:
        x1, y1: Coordonnées du premier point
        x2, y2: Coordonnées du second point
        
    Returns:
        Distance entre les points
    """
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def get_color_for_value(value: float, min_val: float, max_val: float, 
                       color_low: tuple, color_high: tuple) -> tuple:
    """
    Calcule une couleur interpolée basée sur une valeur
    
    Args:
        value: Valeur actuelle
        min_val: Valeur minimale
        max_val: Valeur maximale
        color_low: Couleur RGB pour la valeur minimale
        color_high: Couleur RGB pour la valeur maximale
        
    Returns:
        Couleur RGB interpolée
    """
    if max_val == min_val:
        return color_low
    
    t = clamp((value - min_val) / (max_val - min_val), 0.0, 1.0)
    
    r = int(lerp(color_low[0], color_high[0], t))
    g = int(lerp(color_low[1], color_high[1], t))
    b = int(lerp(color_low[2], color_high[2], t))
    
    return (r, g, b)

def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    Convertit une couleur RGB en hexadécimal
    
    Args:
        r, g, b: Composantes RGB (0-255)
        
    Returns:
        Couleur en format hexadécimal (ex: "#FF0000")
    """
    return f"#{r:02x}{g:02x}{b:02x}"

def hex_to_rgb(hex_color: str) -> tuple:
    """
    Convertit une couleur hexadécimale en RGB
    
    Args:
        hex_color: Couleur en format hexadécimal (ex: "#FF0000")
        
    Returns:
        Tuple RGB (r, g, b)
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def get_habitability_color(habitability: float) -> str:
    """
    Retourne une couleur basée sur le niveau d'habitabilité
    
    Args:
        habitability: Pourcentage d'habitabilité (0-100)
        
    Returns:
        Couleur en format hexadécimal
    """
    if habitability >= 80:
        return "#00FF00"  # Vert - Habitable
    elif habitability >= 60:
        return "#80FF00"  # Vert clair
    elif habitability >= 40:
        return "#FFFF00"  # Jaune
    elif habitability >= 20:
        return "#FF8000"  # Orange
    else:
        return "#FF0000"  # Rouge - Inhabitable

def get_resource_color(resource_type: str) -> str:
    """
    Retourne la couleur associée à un type de ressource
    
    Args:
        resource_type: Type de ressource ('credits', 'energy', 'science')
        
    Returns:
        Couleur en format hexadécimal
    """
    colors = {
        'credits': "#FFD700",  # Or
        'energy': "#00BFFF",   # Bleu ciel
        'science': "#9370DB"   # Violet
    }
    return colors.get(resource_type, "#FFFFFF")

def calculate_building_efficiency(planet_habitability: float) -> float:
    """
    Calcule l'efficacité des bâtiments basée sur l'habitabilité
    
    Args:
        planet_habitability: Habitabilité de la planète (0-100)
        
    Returns:
        Multiplicateur d'efficacité (0.5-1.5)
    """
    # Plus la planète est habitable, plus les bâtiments sont efficaces
    base_efficiency = 0.5
    bonus_efficiency = (planet_habitability / 100.0) * 1.0
    return base_efficiency + bonus_efficiency

def generate_planet_description(planet_name: str, habitability: float, 
                              temperature: float, pressure: float, oxygen: float) -> str:
    """
    Génère une description dynamique de la planète
    
    Args:
        planet_name: Nom de la planète
        habitability: Habitabilité (0-100)
        temperature: Température en Celsius
        pressure: Pression en atmosphères
        oxygen: Oxygène en pourcentage
        
    Returns:
        Description textuelle de l'état de la planète
    """
    descriptions = []
    
    # État général
    if habitability >= 80:
        descriptions.append(f"{planet_name} est maintenant une planète habitable")
    elif habitability >= 50:
        descriptions.append(f"{planet_name} progresse vers l'habitabilité")
    else:
        descriptions.append(f"{planet_name} reste hostile à la vie")
    
    # Température
    if temperature < -50:
        descriptions.append("avec des températures glaciales")
    elif temperature < 0:
        descriptions.append("avec des températures froides")
    elif temperature < 30:
        descriptions.append("avec des températures modérées")
    elif temperature < 60:
        descriptions.append("avec des températures chaudes")
    else:
        descriptions.append("avec des températures extrêmes")
    
    # Atmosphère
    if pressure < 0.1:
        descriptions.append("et une atmosphère très fine")
    elif pressure < 0.5:
        descriptions.append("et une atmosphère légère")
    elif pressure < 2.0:
        descriptions.append("et une atmosphère dense")
    else:
        descriptions.append("et une atmosphère très dense")
    
    return ", ".join(descriptions) + "."