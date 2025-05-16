import asyncio
import platform
import os
import math
import random
import pygame
from AssetManager import AssetManager
from Cells.HelperCell import HelperTCell
from Cells.Macrophage import Macrophage
from Cells.Neutrophil import Neutrophil
from Enemies.Bacteria import Bacteria
from Enemies.Virus import Virus
from Enemies.Cancer import Cancer
from Menu.Shop import Shop
from Enemies.Enemy import Enemy

# Game constants
FPS = 30
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
SPAWN_DELAY_BASE = 1000
WAVE_COOLDOWN_DURATION = 5000
MIN_TOWER_DISTANCE = 50

class Game:
    """Main game class managing the tower defense game loop and state."""
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tower Defense")
        self.clock = pygame.time.Clock()

        # Load assets
        self._load_assets()
        self.path_color = self.background.get_at(Enemy.PATHS[0][0])
        self.enemies = []
        self.wave_enemies = []
        self.cells = []
        self.lives = 100
        self.resources = 1000
        self.selected_tower = None
        self.dragging_tower = None
        self.dragging_tower_cost = 0
        self.current_wave = 0
        self.spawn_timer = 0
        self.wave_cooldown = 0
        self.spawn_delay = SPAWN_DELAY_BASE
        self.is_paused = True
        self.pause_button_rect = pygame.Rect(WINDOW_WIDTH - 70, 10, 60, 60)
        self.running = True

        # Initialize shop centered at the bottom of the screen
        self._init_shop()

    def _load_assets(self):
        """Load and cache shared images and fonts."""
        self.menu_bg = AssetManager.load_image("Game_assets/Menu/Shop_background.gif", (200, 150))
        self.upgrade_button = AssetManager.load_image("Game_assets/UI/Upgrade_Button.gif", (50, 50))
        self.lives_img = AssetManager.load_image('Game_assets/Heart_icon.gif', (100, 100))
        self.resources_img = AssetManager.load_image('Game_assets/Resource_icon.gif', (100, 100))
        self.pause_button = AssetManager.load_image("Game_assets/UI/Pause_button.gif", (60, 60))
        self.play_button = AssetManager.load_image("Game_assets/UI/Play_button.gif", (60, 60))
        self.background = AssetManager.load_image("Graphics/Background.gif", (WINDOW_WIDTH, WINDOW_HEIGHT))
        font_path = os.path.join("Game_assets", "Fonts", "PublicPixel-rv0pA.ttf")
        self.pixel_font = pygame.font.Font(font_path, 34)
        self.credit_font = pygame.font.Font(font_path, 16)
        self.shop_font = pygame.font.Font(font_path, 18)  # Font for shop item prices

    def _init_shop(self):
        """Initialize the shop with tower options, positioned at the bottom center."""
        # Load tower images for the shop
        neutrophil_img = AssetManager.load_image("Game_assets/Neutrophil/Neutrophil_1.gif", (50, 50))
        macrophage_img = AssetManager.load_image("Game_assets/Macrophage/Macrophage_1.gif", (50, 50))
        helper_img = AssetManager.load_image("Game_assets/HelperCells/Helper_T_Cell.gif", (50, 50))
        # Create shop with towers, centered horizontally at y = WINDOW_HEIGHT - 60
        self.shop = Shop(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 60, [
            (Neutrophil, neutrophil_img, 100, self.menu_bg, self.upgrade_button),
            (Macrophage, macrophage_img, 150, self.menu_bg, self.upgrade_button),
            (HelperTCell, helper_img, 120, self.menu_bg, self.upgrade_button)
        ])

    def generate_wave(self):
        """Generate enemies for the current wave based on wave number and probabilities."""
        self.current_wave += 1
        # Decrease spawn delay as waves progress, minimum 200ms
        self.spawn_delay = max(200, SPAWN_DELAY_BASE - 100 * (self.current_wave - 1))
        base_count = 10
        scaling_factor = 5
        enemy_count = base_count + scaling_factor * (self.current_wave - 1)

        # Determine enemy type probabilities based on wave number
        if self.current_wave <= 3:
            virus_prob, bacteria_prob, cancer_prob = 0.9, 0.1, 0.0
        elif self.current_wave <= 6:
            virus_prob, bacteria_prob, cancer_prob = 0.7, 0.25, 0.05
        else:
            virus_prob, bacteria_prob, cancer_prob = 0.5, 0.3, 0.2

        for _ in range(enemy_count):
            rand = random.random()
            path_index = random.randint(0, 2)
            if rand < virus_prob:
                enemy = Virus(path_index)
            elif rand < virus_prob + bacteria_prob:
                enemy = Bacteria(path_index)
            else:
                enemy = Cancer(path_index)
            self.wave_enemies.append(enemy)

    def is_valid_placement(self, x, y):
        """Check if a tower can be placed at (x, y) by verifying it's within bounds, not on a path, and not too close to other towers."""
        if not (0 <= x < WINDOW_WIDTH and 0 <= y < WINDOW_HEIGHT):
            return False
        # Check if the pixel color matches the path color (approximately)
        color = self.background.get_at((int(x), int(y)))
        if all(abs(c - p) < 10 for c, p in zip(color[:3], self.path_color[:3])):
            return False
        # Ensure minimum distance from other towers
        for cell in self.cells:
            if math.hypot(cell.x - x, cell.y - y) < MIN_TOWER_DISTANCE:
                return False
        return True

    def handle_click(self, pos):
        """Handle mouse click events for selecting towers."""
        mx, my = pos
        for cell in self.cells:
            if math.hypot(cell.x - mx, cell.y - my) < 25:
                if self.selected_tower == cell:
                    self.selected_tower = None
                    cell.menu.visible = False
                else:
                    self.selected_tower = cell
                    cell.menu.visible = True
                for c in self.cells:
                    c.selected = (c == self.selected_tower)
                return
        self.selected_tower = None
        for cell in self.cells:
            cell.menu.visible = False
            cell.selected = False

    def handle_events(self):
        """Handle all pygame events, including quitting, mouse clicks, and dragging towers."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Quit the game when the window is closed
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    pos = pygame.mouse.get_pos()
                    if self.pause_button_rect.collidepoint(pos):
                        # Toggle pause when pause button is clicked
                        self._toggle_pause()
                        return
                    tower_class, cost = self.shop.get_clicked_tower(*pos)
                    if tower_class and self.resources >= cost:
                        # Start dragging a new tower if a shop item is clicked and affordable
                        self._start_dragging_tower(tower_class, cost, pos)
                    elif self.selected_tower and self.selected_tower.menu.visible:
                        # Handle clicks on the selected tower's menu
                        self._handle_menu_click(pos)
                    else:
                        # Select or deselect towers
                        self.handle_click(pos)
                elif event.button == 3:  # Right click
                    # Cancel dragging a tower
                    self._cancel_dragging_tower()
            elif event.type == pygame.MOUSEBUTTONUP and self.dragging_tower:
                # Place the dragged tower when the mouse button is released
                self._place_dragging_tower()

    def _toggle_pause(self):
        """Toggle the pause state of the game."""
        self.is_paused = not self.is_paused
        if not self.is_paused and self.current_wave == 0:
            self.generate_wave()
            self.spawn_timer = pygame.time.get_ticks()

    def _start_dragging_tower(self, tower_class, cost, pos):
        """Start dragging a new tower from the shop."""
        self.dragging_tower = tower_class(*pos, self.menu_bg, self.upgrade_button)
        self.dragging_tower_cost = cost

    def _handle_menu_click(self, pos):
        """Handle clicks on the selected tower's menu."""
        button_clicked = self.selected_tower.menu.get_clicked(*pos)
        if button_clicked == "Upgrade":
            upgrade_cost = self.selected_tower.get_upgrade_cost()
            if upgrade_cost != "MAX" and self.resources >= upgrade_cost:
                self.resources -= upgrade_cost
                self.selected_tower.upgrade()
        else:
            self.handle_click(pos)

    def _cancel_dragging_tower(self):
        """Cancel dragging a tower."""
        self.dragging_tower = None
        self.dragging_tower_cost = 0

    def _place_dragging_tower(self):
        """Place the dragged tower if the position is valid."""
        mx, my = pygame.mouse.get_pos()
        if self.is_valid_placement(mx, my):
            self.dragging_tower.x, self.dragging_tower.y = mx, my
            self.cells.append(self.dragging_tower)
            self.resources -= self.dragging_tower_cost
        self.dragging_tower = None
        self.dragging_tower_cost = 0

    def update_enemies(self):
        """Update enemies, spawn new ones, and manage wave progression."""
        if self.is_paused:
            return
        current_time = pygame.time.get_ticks()

        # Spawn enemies from the wave queue
        if self.wave_enemies:
            if current_time - self.spawn_timer >= self.spawn_delay:
                self.enemies.append(self.wave_enemies.pop(0))
                self.spawn_timer = current_time

        # Update and remove enemies
        for enemy in self.enemies[:]:
            enemy.move()
            if enemy.health <= 0:
                self.resources += enemy.money
                self.enemies.remove(enemy)
            elif enemy.is_finished:
                self.lives -= 1
                self.enemies.remove(enemy)

        # Check for wave completion and start next wave after cooldown
        if not self.wave_enemies and not self.enemies and self.current_wave > 0:
            if current_time - self.wave_cooldown >= WAVE_COOLDOWN_DURATION:
                self.is_paused = True
                self.generate_wave()
                self.wave_cooldown = 0
                self.spawn_timer = current_time
            else:
                if self.wave_cooldown == 0:
                    self.wave_cooldown = current_time

    def update_cells(self):
        """Update all towers, applying boosts and attacks."""
        if self.is_paused:
            return
        for cell in self.cells:
            cell.update(self.enemies, self.is_paused)
            if isinstance(cell, HelperTCell):
                cell.revert_boosts()
                cell.apply_boost(self.cells)
            cell.attack(self.enemies)
            if hasattr(cell, 'update_projectiles'):
                cell.update_projectiles(self.enemies)

    def draw(self):
        """Draw the game state to the screen."""
        self.screen.blit(self.background, (0, 0))
        for enemy in self.enemies:
            enemy.draw(self.screen)
        for cell in self.cells:
            cell.draw(self.screen)
        if self.selected_tower and self.selected_tower.menu.visible:
            self.selected_tower.menu.draw(self.screen)
            self.selected_tower.draw_info_overlay(self.screen)
        if self.dragging_tower:
            mx, my = pygame.mouse.get_pos()
            self.dragging_tower.x, self.dragging_tower.y = mx, my
            self.dragging_tower.draw_range_circle(self.screen)
            if not self.is_valid_placement(mx, my):
                pygame.draw.circle(self.screen, (255, 0, 0), (mx, my), 25, 2)
            self.dragging_tower.draw(self.screen)
        # Draw the shop with the smaller font for item prices
        self.shop.draw(self.screen, self.shop_font)
        self.screen.blit(self.lives_img, (400, -10))
        self.screen.blit(self.pixel_font.render(str(self.lives), True, (255, 255, 255)), (485, 30))
        self.screen.blit(self.resources_img, (600, -10))
        self.screen.blit(self.pixel_font.render(str(self.resources), True, (255, 255, 255)), (690, 30))
        wave_text = self.pixel_font.render(f"Wave: {self.current_wave}", True, (255, 255, 255))
        self.screen.blit(wave_text, (WINDOW_WIDTH / 2 - 150, 90))
        button_img = self.pause_button if not self.is_paused else self.play_button
        self.screen.blit(button_img, (WINDOW_WIDTH - 70, 10))
        creator_credit = self.credit_font.render("Created by Brennon O'Leary", True, (255, 255, 255))
        credit_rect = creator_credit.get_rect(bottomright=(WINDOW_WIDTH - 20, WINDOW_HEIGHT - 10))
        self.screen.blit(creator_credit, credit_rect)
        pygame.display.update()

    async def run(self):
        """Run the game loop, handling updates and rendering."""
        while self.running and self.lives > 0:
            self.clock.tick(FPS)
            self.handle_events()
            self.update_enemies()
            self.update_cells()
            self.draw()
            if platform.system() == "Emscripten":
                await asyncio.sleep(1.0 / FPS)
        print("Game Over")
        pygame.quit()

if platform.system() == "Emscripten":
    asyncio.ensure_future(Game().run())
else:
    if __name__ == "__main__":
        asyncio.run(Game().run())