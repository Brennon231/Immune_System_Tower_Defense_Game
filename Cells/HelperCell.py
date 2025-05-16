import pygame
import math
from Cells.Cell import Cell
from Menu.Menu import Menu
from AssetManager import AssetManager

class HelperTCell(Cell):
    """Tower subclass for boosting nearby towers' stats."""
    def __init__(self, x, y, menu_bg, upgrade_button, range_radius=120, damage_boost=0.2, range_boost=0.15, attack_speed_boost=0.1):
        super().__init__(x, y, damage=0, range_radius=range_radius, cooldown=1000, should_rotate=False)
        self.tower_imgs = [
            AssetManager.load_image("Game_assets/HelperCells/Helper_T_Cell.gif", (50, 50))
        ]
        self.range_radius = range_radius
        self.damage_boost = damage_boost
        self.range_boost = range_boost
        self.attack_speed_boost = attack_speed_boost
        self.active_boosted_towers = []
        self.pulse_scale = 1.0
        self.pulse_speed = 0.005
        self.menu = Menu(self, menu_bg, [500, 1000, "MAX"])
        self.menu.add_button(upgrade_button, "Upgrade")

    def _is_in_range(self, tower):
        """Check if a tower is within the boost range."""
        return math.hypot(self.x - tower.x, self.y - tower.y) <= self.range_radius

    def apply_boost(self, all_towers):
        """Apply boosts to towers within range."""
        self.revert_boosts()
        for tower in all_towers:
            if tower == self or not hasattr(tower, "base_damage"):
                continue
            if self._is_in_range(tower):
                tower.is_boosted = True
                tower.damage = round(tower.base_damage * (1 + self.damage_boost), 1)
                tower.range_radius = round(tower.base_range_radius * (1 + self.range_boost))
                tower.cooldown = round(tower.base_cooldown * (1 - self.attack_speed_boost))
                self.active_boosted_towers.append(tower)

    def revert_boosts(self):
        """Revert boosts from previously boosted towers."""
        for tower in self.active_boosted_towers[:]:
            tower.damage = tower.base_damage
            tower.range_radius = tower.base_range_radius
            tower.cooldown = tower.base_cooldown
            tower.is_boosted = False
            self.active_boosted_towers.remove(tower)

    def update(self, enemies, is_paused):
        """Update the pulsing animation for visual effect."""
        if is_paused:
            return
        self.pulse_scale = 1.0 + 0.1 * math.sin(pygame.time.get_ticks() * self.pulse_speed)

    def upgrade(self):
        """Upgrade the tower's level, increasing range and boost effects."""
        if self.level < 3:
            self.level += 1
            self.range_radius += 20
            self.damage_boost += 0.1
            self.range_boost += 0.05
            self.attack_speed_boost += 0.05

    def draw_info_overlay(self, screen):
        """Display support-specific information: level, range, and boost percentages."""
        font = pygame.font.Font(None, 24)
        info = [
            f"Level: {self.level}",
            f"Range: {self.range_radius}",
            f"Damage: {self.damage_boost * 100:.0f}%",
            f"Range: {self.range_boost * 100:.0f}%",
            f"Attack Speed: {self.attack_speed_boost * 100:.0f}%"
        ]
        for i, text in enumerate(info):
            surface = font.render(text, True, (255, 255, 255))
            screen.blit(surface, (self.x - 55, self.y + i * 20 - 20 + self.offset))

    def draw(self, screen):
        """Draw the tower with a pulsing effect."""
        img = pygame.transform.scale(self.tower_imgs[0], (int(50 * self.pulse_scale), int(50 * self.pulse_scale)))
        screen.blit(img, (self.x - img.get_width() // 2, self.y - img.get_height() // 2))
        if self.selected:
            self.draw_range_circle(screen)
            self.draw_info_overlay(screen)