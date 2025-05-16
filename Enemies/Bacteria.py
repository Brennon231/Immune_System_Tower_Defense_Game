from Enemies.Enemy import Enemy
from AssetManager import AssetManager

class Bacteria(Enemy):
    def __init__(self, path_index=0):
        super().__init__(0, 0, 35, 35, path_index)
        self.images = [
            AssetManager.load_image(f"Game_assets/Bacteria/Bacteria_{i}.gif", (self.width, self.height)) for i in range(1, 5)
        ]
        self.health = 10
        self.max_health = 10
        self.velocity = 1
        self.money = 15