from Enemies.Enemy import Enemy
from AssetManager import AssetManager

class Virus(Enemy):
    def __init__(self, path_index=0):
        super().__init__(0, 0, 30, 30, path_index)
        self.images = [
            AssetManager.load_image(f"Game_assets/Virus/Virus_{i}.gif", (self.width, self.height)) for i in range(1, 5)
        ]
        self.health = 5
        self.max_health = 5
        self.velocity = 2
        self.money = 10