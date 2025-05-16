from Enemies.Enemy import Enemy
from AssetManager import AssetManager

class Cancer(Enemy):
    def __init__(self, path_index=0):
        super().__init__(0, 0, 40, 40, path_index)
        self.images = [
            AssetManager.load_image(f"Game_assets/Cancer/Cancer_{i}.gif", (self.width, self.height)) for i in range(1, 3)
        ]
        self.health = 20
        self.max_health = 20
        self.velocity = 0.5
        self.money = 25