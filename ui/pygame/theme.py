import os
import pygame

FONT_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "fonts")

BACKGROUND = (15, 17, 23)
TOPBAR = (22, 25, 34)
PANEL = (24, 27, 37)
CARD = (34, 38, 52)
CARD_BORDER = (52, 58, 78)
TEXT = (232, 235, 243)
MUTED = (140, 148, 170)
ACCENT = (96, 165, 250)
GOLD = (255, 200, 87)
GREEN = (102, 200, 128)
RED = (239, 100, 100)
CYAN = (94, 214, 224)

BUTTON = (50, 56, 78)
BUTTON_HOVER = (68, 76, 106)
BUTTON_PRESSED = (38, 43, 62)
BUTTON_ACCENT = (58, 112, 196)
BUTTON_ACCENT_HOVER = (78, 134, 222)
BUTTON_DISABLED = (38, 41, 54)

TYPE_COLORS = {1: (96, 165, 250), 2: (192, 132, 252), 3: (248, 113, 113)}
ORIGIN_COLORS = {"natural": GREEN, "influenced": GOLD}
BIOME_COLORS = {
    1: ((44, 120, 70), (24, 78, 48)),
    2: ((232, 202, 128), (196, 160, 92)),
    3: ((140, 146, 160), (88, 94, 110)),
}
LOG_COLORS = {"evolution": GOLD, "player": CYAN, "migration": MUTED, "death": RED}


class Fonts:
    def __init__(self):
        regular = os.path.join(FONT_DIR, "NotoSans-Regular.ttf")
        bold = os.path.join(FONT_DIR, "NotoSans-Bold.ttf")
        self.small = pygame.font.Font(regular, 13)
        self.body = pygame.font.Font(regular, 15)
        self.bold = pygame.font.Font(bold, 15)
        self.title = pygame.font.Font(bold, 18)
        self.big = pygame.font.Font(bold, 24)


def mix(first, second, amount: float):
    return tuple(int(a + (b - a) * amount) for a, b in zip(first, second))
