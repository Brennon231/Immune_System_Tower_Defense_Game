import pygame
import math

class Enemy:
    """Base class for enemies with path movement and drawing logic."""
    PATHS = [
        [(10, 287), (54, 286), (91, 299), (155, 313), (210, 314), (336, 311), (390, 319), (439, 324), (497, 314), (537, 324), (583, 349), (625, 389), (658, 416), (709, 432), (765, 442), (824, 445), (875, 444), (996, 440), (1122, 401), (1182, 386), (1246, 395), (1276, 401)],
        [(40, 5), (53, 17), (55, 35), (49, 53), (44, 64), (43, 80), (48, 97), (65, 105), (83, 109), (101, 113), (117, 118), (130, 129), (130, 143), (124, 156), (117, 167), (112, 181), (112, 196), (121, 210), (138, 216), (155, 218), (171, 216), (188, 212), (205, 215), (222, 220), (244, 227), (263, 238), (274, 254), (287, 267), (326, 295), (368, 318), (428, 324), (479, 318), (530, 321), (572, 342), (608, 374), (637, 399), (671, 422), (713, 434), (765, 441), (808, 445), (870, 446), (934, 444), (984, 441), (1010, 471), (1038, 497), (1069, 511), (1109, 528), (1156, 546), (1276, 581)],
        [(5, 403), (33, 402), (67, 409), (109, 415), (147, 414), (182, 403), (218, 383), (252, 358), (288, 316), (342, 314), (405, 323), (459, 322), (504, 316), (542, 327), (594, 356), (654, 414), (722, 435), (806, 445), (903, 439), (957, 400), (1008, 387), (1058, 376), (1103, 350), (1141, 299), (1152, 239), (1152, 180), (1152, 130), (1167, 83), (1187, 44), (1219, 15), (1246, 3)]
    ]

    def __init__(self, x, y, width, height, path_index=0):
        self.width = width
        self.height = height
        self.images = []
        self.animation_count = 0
        self.animation_speed = 0.1
        self.health = 1
        self.max_health = 2
        self.velocity = 1
        self.path = self.PATHS[path_index]
        self.path_pos = 0
        self.x = self.path[0][0]
        self.y = self.path[0][1]
        self.flipped = False
        self.last_dir_x = 0
        self.is_finished = False
        self.money = 5

    def move(self):
        """Move the enemy along its path."""
        if self.path_pos + 1 >= len(self.path):
            self.is_finished = True
            return
        next_x, next_y = self.path[self.path_pos + 1]
        dx, dy = next_x - self.x, next_y - self.y
        distance = math.hypot(dx, dy)
        if distance < self.velocity:
            self.path_pos += 1
        else:
            # Move towards the next point
            self.x += (dx / distance) * self.velocity
            self.y += (dy / distance) * self.velocity
            self.last_dir_x = dx
            self.flipped = dx < 0
        self.animation_count += self.animation_speed
        if self.animation_count >= len(self.images):
            self.animation_count = 0

    def hit(self, damage):
        """Reduce enemy health by the given damage."""
        self.health -= damage

    def draw(self, screen):
        """Draw the enemy and its health bar on the screen."""
        if not self.images:
            pygame.draw.rect(screen, (255, 0, 0), (self.x - self.width // 2, self.y - self.height // 2, self.width, self.height))
        else:
            img = self.images[int(self.animation_count)]
            if self.flipped:
                img = pygame.transform.flip(img, True, False)
            screen.blit(img, (self.x - self.width // 2, self.y - self.height // 2))
            # Draw health bar
            health_bar_width = self.width * (self.health / self.max_health)
            pygame.draw.rect(screen, (255, 0, 0), (self.x - self.width // 2, self.y - self.height - 10, self.width, 5))
            pygame.draw.rect(screen, (0, 255, 0), (self.x - self.width // 2, self.y - self.height - 10, health_bar_width, 5))