import pygame
import math
from Cells.Cell import Cell
from Menu.Menu import Menu
from AssetManager import AssetManager

class Macrophage(Cell):
    """Tower subclass with AOE attack and animation."""
    def __init__(self, x, y, menu_bg, upgrade_button):
        super().__init__(x, y, damage=3, range_radius=100, cooldown=800, should_rotate=False)
        self.attack_imgs = [
            AssetManager.load_image(f"Game_assets/Macrophage/Macrophage_{i}.gif", (50, 50)) for i in range(1, 5)
        ]
        self.tower_imgs = [self.attack_imgs[0]]
        self.is_attacking = False
        self.current_frame = 0
        self.attack_animation_count = 0
        self.animation_speed = 0.2
        self.menu = Menu(self, menu_bg, [200, 500, "MAX"])
        self.menu.add_button(upgrade_button, "Upgrade")

    def attack(self, enemies):
        """Start the AOE attack animation if enemies are in range and cooldown allows."""
        if not self.is_attacking and self.can_attack():
            for enemy in enemies:
                if math.hypot(enemy.x - self.x, enemy.y - self.y) <= self.range_radius:
                    self.is_attacking = True
                    self.current_frame = 0
                    self.attack_animation_count = 0
                    self.last_attack_time = pygame.time.get_ticks()
                    break

    def update(self, enemies, is_paused):
        """Progress the animation and apply AOE damage on the last frame."""
        if is_paused:
            return
        if self.is_attacking:
            self.attack_animation_count += self.animation_speed
            if self.attack_animation_count >= 1:
                self.attack_animation_count -= 1
                self.current_frame += 1
                if self.current_frame >= len(self.attack_imgs):
                    # Apply damage to all enemies in range
                    for enemy in enemies:
                        if math.hypot(enemy.x - self.x, enemy.y - self.y) <= self.range_radius:
                            enemy.hit(self.damage)
                    self.is_attacking = False
                    self.current_frame = 0

    def draw(self, screen):
        """Draw the current animation frame or idle image."""
        if self.is_attacking:
            frame = min(self.current_frame, len(self.attack_imgs) - 1)
            img = self.attack_imgs[frame]
        else:
            img = self.tower_imgs[0]
        screen.blit(img, (self.x - img.get_width() // 2, self.y - img.get_height() // 2))
        if self.selected:
            self.draw_range_circle(screen)