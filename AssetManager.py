import pygame

class AssetManager:
    """Utility class for loading and caching images."""
    _image_cache = {}

    @staticmethod
    def load_image(path, size=None):
        """Load an image from the cache or file system, optionally resizing it."""
        if path not in AssetManager._image_cache:
            try:
                image = pygame.image.load(path).convert_alpha()
                if size:
                    image = pygame.transform.scale(image, size)
                AssetManager._image_cache[path] = image
            except pygame.error as e:
                print(f"Error loading image {path}: {e}")
                return None
        return AssetManager._image_cache[path]