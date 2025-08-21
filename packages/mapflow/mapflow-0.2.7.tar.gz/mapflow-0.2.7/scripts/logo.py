import math
import random
from pathlib import Path
from typing import Iterable


def generate_random_rotating_stars_svg(
    output_file: str,
    radii: Iterable[float],
    colors: Iterable[str],
    width: int = 400,
    height: int = 400,
    min_duration: float = 5.0,
    max_duration: float = 20.0,
    star_size: float = 15.0,
) -> None:
    """
    Génère un SVG animé avec des étoiles tournantes à des rayons, angles initiaux et vitesses aléatoires.

    Args:
        output_file: Nom du fichier de sortie
        radii: Rayons de trajectoire pour chaque étoile
        colors: Couleurs pour chaque étoile
        width: Largeur de l'image SVG
        height: Hauteur de l'image SVG
        min_duration: Durée minimale de rotation (plus lent)
        max_duration: Durée maximale de rotation (plus rapide)
        star_size: Taille des étoiles
    """
    if len(radii) != len(colors):
        raise ValueError("Les listes de rayons et de couleurs doivent avoir la même longueur")

    center_x = width / 2
    center_y = height / 2

    # Préparation du SVG
    svg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
    <circle cx="{center_x}" cy="{center_y}" r="{min(width, height) / 2}" fill="#ffffff" />
    <circle cx="{center_x}" cy="{center_y}" r="{min(width, height) / 2 - 15}" fill="#090035" />
    
"""

    for radius, color in zip(radii, colors):
        # Angle initial aléatoire
        initial_angle = random.uniform(0, 360)
        # Durée aléatoire entre min et max
        duration = random.uniform(min_duration, max_duration)

        # Position initiale
        x = center_x + radius * math.cos(math.radians(initial_angle))
        y = center_y + radius * math.sin(math.radians(initial_angle))

        # Définition de l'étoile à 4 branches
        outer_radius = star_size
        inner_radius = star_size / 2
        star_path = []
        for i in range(8):
            angle = math.radians(i * 45)
            if i % 2 == 0:
                r = outer_radius
            else:
                r = inner_radius
            star_path.append((x + r * math.cos(angle), y + r * math.sin(angle)))

        star_path_str = "M" + " L".join(f"{px:.2f},{py:.2f}" for px, py in star_path) + " Z"

        svg_content += f"""
    <path d="{star_path_str}" fill="{color}">
        <animateTransform
            attributeName="transform"
            attributeType="XML"
            type="rotate"
            from="{initial_angle:.2f} {center_x:.2f} {center_y:.2f}"
            to="{initial_angle + 360:.2f} {center_x:.2f} {center_y:.2f}"
            dur="{duration:.2f}s"
            repeatCount="indefinite"
            additive="sum"/>
    </path>
"""

    svg_content += "</svg>"

    with open(output_file, "w") as f:
        f.write(svg_content)

    print(f"SVG animé créé: {output_file}")


if __name__ == "__main__":
    # Exemple d'utilisation
    random.seed(42)  # Pour des résultats reproductibles

    n = 10
    # Configuration
    config = {
        "output_file": Path(__file__).parent.parent / "_static" / "logo.svg",
        "radii": [30 + i * 25 for i in range(n)],
        "colors": ["#ffffff"] * n,
        "width": 600,
        "height": 600,
        "min_duration": 5,
        "max_duration": 50,
        "star_size": 8,
    }

    generate_random_rotating_stars_svg(**config)
