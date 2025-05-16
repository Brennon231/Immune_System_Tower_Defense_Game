import pygame

class Shop:
    def __init__(self, x, y, towers):
        self.x = x
        self.y = y
        self.towers = towers  # List of (tower_class, img, cost, menu_bg, upgrade_button) tuples
        self.width = len(towers) * 60 + 40
        self.height = 110

    def get_clicked_tower(self, mx, my):
        """Return the tower class and cost if clicked within the shop area."""
        for i, (tower_class, _, cost, _, _) in enumerate(self.towers):
            tower_x = self.x - (len(self.towers) * 60) // 2 + i * 60
            tower_y = self.y - 35  # Moved up 10 pixels for better centering
            if tower_x <= mx < tower_x + 50 and tower_y <= my < tower_y + 50:
                return tower_class, cost
        return None, 0

    def draw(self, screen, font):
        """Draw the shop UI with tower images and text shifted upward."""
        # Draw the shop background with semi-transparent gray and rounded corners
        background_rect = pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, self.width, self.height)
        pygame.draw.rect(screen, (80, 80, 80, 180), background_rect, border_radius=10)

        # Calculate start_x to center the tower images horizontally
        start_x = self.x - (len(self.towers) * 60) // 2

        for i, (_, img, cost, _, _) in enumerate(self.towers):
            tower_x = start_x + i * 60
            tower_y = self.y - 35  # Moved up 10 pixels from self.y - 25
            screen.blit(img, (tower_x, tower_y))

            # Render the cost text with the provided font
            cost_text = font.render(str(cost), True, (255, 255, 255))
            text_width = cost_text.get_width()

            # Center the text below the tower image with a 10-pixel gap
            text_x = tower_x + 25 - text_width // 2  # 25 is half of image width (50/2)
            text_y = tower_y + 60  # Adjusted to maintain a 10-pixel gap
            screen.blit(cost_text, (text_x, text_y))