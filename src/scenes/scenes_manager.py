from typing import Dict

# Import all scenes
from scenes.circle_scene import Circle_scene
from scenes.menu import Menu
from scenes.scene import Scene

# Dict of all registered scenes
SCENES_MAP: Dict[str, Scene] = {"Menu": Menu, "Circle_scene": Circle_scene}
