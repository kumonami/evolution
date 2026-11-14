from core.genome import GENE_LABELS

SCREEN_X = 1280
SCREEN_Y = 800
TOPBAR_HEIGHT = 56
PANEL_WIDTH = 360
MAP_WIDTH = SCREEN_X - PANEL_WIDTH
REGION_GAP = 8
BASE_TICK_DURATION = 0.5
SPEEDS = (0.25, 0.5, 1, 2, 4, 8, 16)
DEFAULT_SPEED_INDEX = 2

TYPE_NAMES = {1: "травоядное", 2: "всеядное", 3: "хищник"}
BIOME_NAMES = {1: "Лес", 2: "Пустыня", 3: "Горы"}
GENE_NAMES = {gene: label.capitalize() for gene, label in GENE_LABELS.items()}
ORIGIN_NAMES = {"natural": "естественный", "influenced": "под влиянием игрока"}
