import pygame

class Menu:
    """Menu class for handling tower upgrades and interactions."""
    def __init__(self, tower, bg, item_cost):
        self.tower = tower
        self.bg = bg
        self.item_cost = item_cost
        self.buttons = []  # List of (img, name) tuples
        self.width = self.bg.get_width()
        self.height = self.bg.get_height()
        self.offset = -100  # Menu appears above the tower
        self.visible = False  # Control menu visibility

    def add_button(self, img, name):
        """Add a button to the menu with an image and name."""
        self.buttons.append((img, name))

    def get_clicked(self, mx, my):
        """Check if a button was clicked based on mouse position."""
        if not self.visible:
            return None
        # Calculate button positions dynamically based on tower's current position
        x, y = self.tower.x, self.tower.y + self.offset
        for i, (_, name) in enumerate(self.buttons):
            bx = x - self.width // 2 + 10
            by = y - self.height // 2 + i * 60 + 20
            if bx <= mx < bx + 50 and by <= my < by + 50:
                return name
        return None

    def draw(self, screen):
        """Draw the menu on the screen if visible."""
        if not self.visible:
            return
        # Update menu position based on tower's current position
        x, y = self.tower.x, self.tower.y + self.offset
        screen.blit(self.bg, (x - self.width // 2, y - self.height // 2))
        font = pygame.font.Font(None, 24)
        for i, (img, name) in enumerate(self.buttons):
            bx = x - self.width // 2 + 10
            by = y - self.height // 2 + i * 60 + 20
            screen.blit(img, (bx, by))
            cost = self.item_cost[min(self.tower.level - 1, len(self.item_cost) - 1)]
            text = font.render(f"{name}: {cost}", True, (255, 255, 255))
            screen.blit(text, (bx + 45, by + 2))