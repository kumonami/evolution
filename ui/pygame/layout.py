from dataclasses import dataclass
import pygame
import ui.pygame.constants as ui


@dataclass
class Layout:
    width: int
    height: int
    panel_visible: bool = True

    @property
    def topbar(self) -> pygame.Rect:
        return pygame.Rect(0, 0, self.width, ui.TOPBAR_HEIGHT)

    @property
    def panel_width(self) -> int:
        return ui.PANEL_WIDTH if self.panel_visible else 0

    @property
    def map_rect(self) -> pygame.Rect:
        return pygame.Rect(0, ui.TOPBAR_HEIGHT, self.width - self.panel_width, self.height - ui.TOPBAR_HEIGHT)

    @property
    def panel_rect(self) -> pygame.Rect:
        return pygame.Rect(self.width - ui.PANEL_WIDTH, ui.TOPBAR_HEIGHT, ui.PANEL_WIDTH, self.height - ui.TOPBAR_HEIGHT)
