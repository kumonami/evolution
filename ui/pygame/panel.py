import pygame
import config.constants as constants
import ui.pygame.constants as ui
import ui.pygame.theme as theme
import ui.pygame.widgets as widgets
from core.genome import GENES
from ui.pygame.series import feed_lines, species_series, total_series

PADDING = 12
GAP = 10
GENE_ROW = 21
GRAPH_HEIGHT = 92


class SidePanel:
    """
    Правая панель. В режиме карты показывает выбранный регион и популяцию
    с кнопками вмешательства (на одну популяцию или на весь вид), график
    численности и ленту событий. В режиме дерева показывает карточку вида.
    """

    def __init__(self, screen, fonts: theme.Fonts, ui_kit: widgets.Ui, layout):
        self.screen = screen
        self.fonts = fonts
        self.kit = ui_kit
        self.rect = layout.panel_rect

    def draw_map(self, world, region_id, population_id, actions) -> None:
        self._background()
        region = world.get_region(region_id) if region_id else None
        population = world.get_population(population_id) if population_id else None
        y = self.rect.top + PADDING
        if not region:
            y = self._hint(y)
        else:
            y = self._region_card(world, region, y, actions)
        if population:
            y = self._population_card(world, population, y, actions)
        title, series, color = self._series(world, population)
        widgets.sparkline(self.screen, self.fonts, self._slot(y, GRAPH_HEIGHT), series, color, title)
        y += GRAPH_HEIGHT + GAP
        self._log(world, y)

    def draw_species(self, world, species, actions) -> None:
        self._background()
        y = self.rect.top + PADDING
        if not species:
            card = self._slot(y, 70)
            widgets.rounded(self.screen, theme.CARD, card, 10, theme.CARD_BORDER)
            widgets.text(self.screen, self.fonts.body, "Выберите вид на дереве", card.center, theme.MUTED, "center")
            return
        populations = world.species_populations(species.id)
        genome = world.species_genome(species.id)
        alive = not species.is_extinct
        card = self._slot(y, 40 + 21 * 5 + 22 + len(GENES) * GENE_ROW + 16)
        widgets.rounded(self.screen, theme.CARD, card, 10, theme.CARD_BORDER)
        x = card.left + PADDING
        top = card.top + 10
        widgets.text(self.screen, self.fonts.title, f"Вид #{species.id}", (x, top))
        self._chip(species, card.right - PADDING, top + 2)
        top += 32
        influenced = species.origin == "influenced"
        rows = [
            ("Происхождение", ui.ORIGIN_NAMES.get(species.origin, species.origin), theme.GOLD if influenced else theme.GREEN),
            ("Родитель", f"#{species.parent_id}" if species.parent_id else "нет", theme.TEXT),
            ("Появился", f"тик {species.born_tick}", theme.TEXT),
            ("Статус", "жив" if alive else f"вымер на тике {species.extinct_tick}", theme.GREEN if alive else theme.RED),
            ("Популяции", f"{len(populations)} · особей {sum(p.size for p in populations)}" if alive else "нет", theme.TEXT),
        ]
        for label, value, color in rows:
            widgets.text(self.screen, self.fonts.small, label, (x, top), theme.MUTED)
            widgets.text(self.screen, self.fonts.small, value, (card.right - PADDING, top), color, "topright")
            top += 21
        top += 4
        title = "Средний геном · влияет на весь вид" if alive else "Родоначальный геном"
        widgets.text(self.screen, self.fonts.small, title, (x, top), theme.MUTED)
        top += 22
        genes = (genome or species.anchor).as_dict()
        handler = actions.nudge_species if alive and genome else None
        for gene in GENES:
            self._gene_row(card, top, gene, genes[gene], handler)
            top += GENE_ROW
        y += card.height + GAP
        series = species_series(world.history, species.id)
        color = theme.TYPE_COLORS.get(species.type_id, theme.GREEN)
        widgets.sparkline(self.screen, self.fonts, self._slot(y, 110), series, color, f"Численность вида #{species.id}")

    def _background(self) -> None:
        pygame.draw.rect(self.screen, theme.PANEL, self.rect)
        pygame.draw.line(self.screen, theme.CARD_BORDER, self.rect.topleft, self.rect.bottomleft, 1)

    def _slot(self, y: int, height: int) -> pygame.Rect:
        return pygame.Rect(self.rect.left + PADDING, y, self.rect.width - PADDING * 2, height)

    def _hint(self, y: int) -> int:
        card = self._slot(y, 84)
        widgets.rounded(self.screen, theme.CARD, card, 10, theme.CARD_BORDER)
        widgets.text(self.screen, self.fonts.bold, "Ничего не выбрано", (card.left + PADDING, card.top + 12))
        widgets.text(self.screen, self.fonts.small, "Нажмите на регион или популяцию,", (card.left + PADDING, card.top + 38), theme.MUTED)
        widgets.text(self.screen, self.fonts.small, "чтобы изменить мир.", (card.left + PADDING, card.top + 56), theme.MUTED)
        return y + card.height + GAP

    def _chip(self, species, right: int, top: int) -> None:
        label = ui.TYPE_NAMES.get(species.type_id, "?")
        color = theme.TYPE_COLORS.get(species.type_id, theme.TEXT)
        width = self.fonts.small.size(label)[0] + 18
        rect = pygame.Rect(right - width, top, width, 22)
        widgets.rounded(self.screen, theme.mix(theme.CARD, color, 0.3), rect, 11)
        widgets.text(self.screen, self.fonts.small, label, rect.center, theme.TEXT, "center")

    def _control(self, card, y: int, label: str, value: str, buttons: list) -> None:
        widgets.text(self.screen, self.fonts.body, label, (card.left + PADDING, y + 4))
        widgets.text(self.screen, self.fonts.small, value, (card.left + 130, y + 7), theme.MUTED)
        right = card.right - PADDING
        for icon, label_text, handler, enabled in reversed(buttons):
            width = 30 if icon else 54
            rect = pygame.Rect(right - width, y, width, 28)
            self.kit.button(self.screen, rect, label=label_text, icon=icon, on_click=handler, enabled=enabled)
            right -= width + 6

    def _region_card(self, world, region, y: int, actions) -> int:
        card = self._slot(y, 196)
        widgets.rounded(self.screen, theme.CARD, card, 10, theme.CARD_BORDER)
        biome = region.biome
        x, top = card.left + PADDING, card.top + 10
        widgets.text(self.screen, self.fonts.title, f"{ui.BIOME_NAMES.get(biome.id, 'Регион')} · регион {region.id}", (x, top))
        top += 28
        widgets.text(self.screen, self.fonts.small,
                     f"растения {int(region.plants_stock)} из {int(region.plants_limit)} · прирост {region.plants_growth_rate:.0f}",
                     (x, top), theme.MUTED)
        top += 19
        widgets.text(self.screen, self.fonts.small,
                     f"температура {biome.temperature:.0f} · нагрузка {world.region_load(region):.2f}", (x, top), theme.MUTED)
        top += 19
        satiety = world.plant_eaters_satiety(region)
        if satiety is None:
            note, color = "растительноядных нет", theme.MUTED
        else:
            hungry = satiety < constants.HUNGER_THRESHOLD
            note, color = f"сытость травоядных {satiety:.2f}" + (" · голод" if hungry else ""), theme.RED if hungry else theme.GREEN
        widgets.text(self.screen, self.fonts.small, note, (x, top), color)
        top += 24
        step = constants.PLAYER_WATER_STEP
        self._control(card, top, "Влажность", f"{biome.humidity:.0f}", [
            ("minus", None, lambda: actions.water(-step), biome.humidity > 0),
            ("plus", None, lambda: actions.water(step), biome.humidity < 100),
        ])
        top += 32
        self._control(card, top, "Растения", f"{int(region.plants_stock)}", [
            (None, f"+{int(constants.PLAYER_PLANTS_AMOUNT)}", actions.plants, True),
        ])
        top += 32
        cap = constants.PLAYER_CAPACITY_STEP
        self._control(card, top, "Вместимость", f"{region.capacity}", [
            ("minus", None, lambda: actions.capacity(-cap), region.capacity > constants.MIN_REGION_CAPACITY),
            ("plus", None, lambda: actions.capacity(cap), True),
        ])
        return y + card.height + GAP

    def _population_card(self, world, population, y: int, actions) -> int:
        card = self._slot(y, 108 + len(GENES) * GENE_ROW + 8)
        widgets.rounded(self.screen, theme.CARD, card, 10, theme.CARD_BORDER)
        x, top = card.left + PADDING, card.top + 10
        species = population.species
        widgets.text(self.screen, self.fonts.title, f"Популяция {population.id} · вид #{species.id}", (x, top))
        self._chip(species, card.right - PADDING, top + 26)
        widgets.text(self.screen, self.fonts.small, f"особей {population.size} · сытость {population.satiety:.2f}", (x, top + 28), theme.MUTED)
        top += 50
        fitness = population.genome.fitness(population.region.biome)
        origin = "влияние игрока" if population.influenced else "естественная"
        color = theme.GOLD if population.influenced else theme.GREEN
        widgets.text(self.screen, self.fonts.small, f"пригодность {fitness:.2f} · стресс {population.stress:.2f}", (x, top), theme.MUTED)
        widgets.text(self.screen, self.fonts.small, origin, (card.right - PADDING, top), color, "topright")
        top += 24
        self._scope_toggle(world, population, card, top, actions)
        top += 32
        genes = population.genome.as_dict()
        for gene in GENES:
            self._gene_row(card, top, gene, genes[gene], actions.nudge)
            top += GENE_ROW
        return y + card.height + GAP

    def _scope_toggle(self, world, population, card, y: int, actions) -> None:
        count = len(world.species_populations(population.species.id))
        half = (card.width - PADDING * 2 - 6) // 2
        left = pygame.Rect(card.left + PADDING, y, half, 26)
        right = pygame.Rect(left.right + 6, y, half, 26)
        self.kit.button(self.screen, left, label="Эта популяция", font=self.fonts.small,
                        on_click=lambda: actions.set_scope("population"), active=actions.scope == "population")
        self.kit.button(self.screen, right, label=f"Весь вид · {count} поп.", font=self.fonts.small,
                        on_click=lambda: actions.set_scope("species"), active=actions.scope == "species")

    def _gene_row(self, card, y: int, gene: str, value: float, handler) -> None:
        x = card.left + PADDING
        widgets.text(self.screen, self.fonts.small, ui.GENE_NAMES.get(gene, gene), (x, y + 2), theme.TEXT)
        widgets.bar(self.screen, (x + 100, y + 7, 112, 8), value, 100, theme.ACCENT if gene in GENES[:5] else theme.CYAN)
        widgets.text(self.screen, self.fonts.small, f"{value:.0f}", (x + 222, y + 2), theme.MUTED)
        if not handler:
            return
        step = constants.PLAYER_GENE_STEP
        right = card.right - PADDING
        self.kit.button(self.screen, (right - 22, y, 22, 19), icon="plus", on_click=lambda: handler(gene, step), enabled=value < 100)
        self.kit.button(self.screen, (right - 48, y, 22, 19), icon="minus", on_click=lambda: handler(gene, -step), enabled=value > 0)

    def _series(self, world, population):
        if population:
            return (f"Численность вида #{population.species.id}", species_series(world.history, population.species.id),
                    theme.TYPE_COLORS.get(population.species.type_id, theme.ACCENT))
        return "Всего особей в мире", total_series(world.history), theme.ACCENT

    def _log(self, world, y: int) -> None:
        card = pygame.Rect(self.rect.left + PADDING, y, self.rect.width - PADDING * 2, self.rect.bottom - y - PADDING)
        if card.height < 50:
            return
        widgets.rounded(self.screen, theme.CARD, card, 10, theme.CARD_BORDER)
        widgets.text(self.screen, self.fonts.small, "События", (card.left + PADDING, card.top + 6), theme.MUTED)
        count = max(1, (card.height - 34) // 17)
        top = card.top + 28
        for tick, kind, message in reversed(feed_lines(world.logger.entries, count)):
            line = widgets.fit_text(self.fonts.small, f"{tick}  {message}", card.width - PADDING * 2)
            widgets.text(self.screen, self.fonts.small, line, (card.left + PADDING, top), theme.LOG_COLORS.get(kind, theme.TEXT))
            top += 17
