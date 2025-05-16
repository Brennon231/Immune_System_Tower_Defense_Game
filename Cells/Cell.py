import pygame
import math
import os
from AssetManager import AssetManager

class Cell:
    """Base class for towers with attack, range, and upgrade logic."""
    def __init__(self, x, y, damage, range_radius, cooldown, should_rotate=True):
        self.x = x
        self.y = y
        self.level = 1
        self.base_damage = damage
        self.base_range_radius = range_radius
        self.base_cooldown = cooldown
        self.damage = damage
        self.range_radius = range_radius
        self.cooldown = cooldown
        self.is_boosted = False
        self.should_rotate = should_rotate
        self.tower_imgs = []
        self.last_attack_time = 0
        self.target_enemy = None
        self.inRange = False
        self.selected = False
        self.menu = None
        self.offset = -110

    def can_attack(self):
        """Check if the tower can attack based on cooldown."""
        return pygame.time.get_ticks() - self.last_attack_time >= self.cooldown

    def attack(self, enemies):
        """Attack the first enemy in range if possible."""
        if not self.can_attack():
            return
        for enemy in enemies:
            if math.hypot(self.x - enemy.x, self.y - enemy.y) <= self.range_radius:
                enemy.hit(self.damage)
                self.target_enemy = enemy
                self.inRange = True
                self.last_attack_time = pygame.time.get_ticks()
                break
        else:
            self.inRange = False
            self.target_enemy = None

    def update(self, enemies, is_paused):
        """Placeholder for per-frame updates, such as animations or AOE attacks."""
        pass

    def _rotate_image(self, image):
        """Rotate the tower image to face the target enemy."""
        if not self.inRange or not self.target_enemy:
            return image
        dx, dy = self.target_enemy.x - self.x, self.target_enemy.y - self.y
        angle = math.degrees(math.atan2(dy, dx)) + (getattr(self, 'image_offset_angle', 0))
        return pygame.transform.rotate(image, -angle)

    def draw_range_circle(self, screen):
        """Draw the tower's range circle on the screen."""
        circle_surface = pygame.Surface((self.range_radius * 2, self.range_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(circle_surface, (180, 180, 180, 100), (self.range_radius, self.range_radius), self.range_radius)
        screen.blit(circle_surface, (self.x - self.range_radius, self.y - self.range_radius))

    def draw_info_overlay(self, screen):
        """Draw the tower's info overlay when selected."""
        font = pygame.font.Font(None, 24)
        attack_speed = self.cooldown / 1000
        info = [f"Level: {self.level}", f"Damage: {self.damage}", f"Range: {self.range_radius}", f"Attack Speed: {attack_speed}"]
        for i, text in enumerate(info):
            surface = font.render(text, True, (255, 255, 255))
            screen.blit(surface, (self.x - 50, self.y + i * 20 - 10 + self.offset))

    def upgrade(self):
        """Upgrade the tower's level, increasing damage and range."""
        if self.level < 3:
            self.level += 1
            self.base_damage += 1
            self.base_range_radius += 20
            if not self.is_boosted:
                self.damage = self.base_damage
                self.range_radius = self.base_range_radius

    def get_upgrade_cost(self):
        """Get the cost for the next upgrade."""
        if self.menu is None or not hasattr(self.menu, 'item_cost'):
            return 0
        return self.menu.item_cost[min(self.level - 1, len(self.menu.item_cost) - 1)]

    def draw(self, screen):
        """Draw the tower on the screen."""
        if not self.tower_imgs:
            pygame.draw.rect(screen, (0, 0, 255), (self.x - 25, self.y - 25, 50, 50))
        else:
            img = self.tower_imgs[0]
            if self.should_rotate:
                img = self._rotate_image(img)
            screen.blit(img, (self.x - img.get_width() // 2, self.y - img.get_height() // 2))
        if self.selected:
            self.draw_range_circle(screen)