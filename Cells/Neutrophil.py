import pygame
import math
from Cells.Cell import Cell
from Menu.Menu import Menu
from AssetManager import AssetManager

class Neutrophil(Cell):
    """Tower subclass with projectile-based attacks and animation."""
    def __init__(self, x, y, menu_bg, upgrade_button):
        super().__init__(x, y, damage=2, range_radius=120, cooldown=1000)
        self.attack_imgs = [AssetManager.load_image(f"Game_assets/Neutrophil/Neutrophil_{i}.gif", (50, 50)) for i in range(1, 7)]
        self.tower_imgs = [self.attack_imgs[0]]
        self.projectile_img = AssetManager.load_image("Game_assets/Neutrophil/Neutrophil_Projectile_1.gif")
        self.projectiles = []
        self.projectile_speed = 5
        self.attack_animation_count = 0
        self.animation_speed = 0.2
        self.image_offset_angle = -180
        self.menu = Menu(self, menu_bg, [300, 700, "MAX"])
        self.menu.add_button(upgrade_button, "Upgrade")

    def attack(self, enemies):
        """Launch a projectile at the first enemy in range if possible."""
        if not self.can_attack():
            return
        for enemy in enemies:
            if math.hypot(self.x - enemy.x, self.y - enemy.y) <= self.range_radius:
                self.projectiles.append({'x': self.x, 'y': self.y, 'target': enemy})
                self.last_attack_time = pygame.time.get_ticks()
                self.attack_animation_count = 0.1
                self.target_enemy = enemy
                self.inRange = True
                break
        else:
            self.inRange = False
            self.target_enemy = None

    def update(self, enemies, is_paused):
        """Update the attack animation if active."""
        if is_paused:
            return
        if self.attack_animation_count > 0:
            self.attack_animation_count += self.animation_speed
            if self.attack_animation_count >= len(self.attack_imgs):
                self.attack_animation_count = 0

    def update_projectiles(self, enemies):
        """Move projectiles towards their targets and apply damage on hit."""
        for proj in self.projectiles[:]:
            enemy = proj['target']
            if enemy not in enemies:
                self.projectiles.remove(proj)
                continue
            dx, dy = enemy.x - proj['x'], enemy.y - proj['y']
            dist = math.hypot(dx, dy)
            if dist < 10:
                enemy.hit(self.damage)
                self.projectiles.remove(proj)
            else:
                proj['x'] += (dx / dist) * self.projectile_speed
                proj['y'] += (dy / dist) * self.projectile_speed

    def draw(self, screen):
        """Draw the tower and its projectiles."""
        img = self.attack_imgs[int(self.attack_animation_count)] if self.attack_animation_count > 0 else self.tower_imgs[0]
        if self.should_rotate:
            img = self._rotate_image(img)
        screen.blit(img, (self.x - img.get_width() // 2, self.y - img.get_height() // 2))
        for proj in self.projectiles:
            screen.blit(self.projectile_img, (proj['x'] - self.projectile_img.get_width() // 2, proj['y'] - self.projectile_img.get_height() // 2))
        if self.selected:
            self.draw_range_circle(screen)