import os
import sys
import math
import json
import threading
import pygame
import inputhandler
import camera

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class LevelEditorState():
    def __init__(self):
        self.quit = False
        self.SCREEN_SIZE = pygame.display.get_surface().get_size()
        self.key_bindings = {"LEFT": pygame.K_a,
                             "RIGHT": pygame.K_d,
                             "UP": pygame.K_w,
                             "DOWN": pygame.K_s,
                             }
        self.direction_dict = {"LEFT": pygame.math.Vector2(-1, 0),
                               "RIGHT": pygame.math.Vector2(1, 0),
                               "UP": pygame.math.Vector2(0, -1),
                               "DOWN": pygame.math.Vector2(0, 1)
                               }
        self.number_keys = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3,
                            pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7,
                            pygame.K_8, pygame.K_9]
        # Size of sprites in pixels in the sprite sheet
        self.native_size = pygame.math.Vector2(8, 8)
        # Scale the sprite in the sprite sheet up by this ratio
        self.scale = 5
        # Dimensions of tile
        self.tile_size = self.native_size * self.scale
        
        # Position of camera viewpoint
        self.pos = pygame.math.Vector2(0, 0)
        self.speed = 3
        self.pressed_keys = pygame.key.get_pressed()
        
        # Camer object to handle scrolling of view
        self.cam = camera.Camera(self.camera_function, 0, 0)   

        self.tile_selector = 0   
        self.current_level = "new.json" 
    
    def startup(self):
        # Loading sprite sheet
        sprite_sheet = pygame.image.load("sprites.png").convert()
        self.sprite_list = self.split_sprites(sprite_sheet)
        self.scale_sprites()
        
        # Setting up level
        # Dimensions of levels in number of tiles, not pixels
        level_dim = pygame.math.Vector2(12, 12)
        self.level_rect = self.make_level_rect(*level_dim)
        self.level_data = self.make_empty_level(*level_dim)

    def cleanup(self):
        pass
        
    def get_event(self, event):
        if event.type in (pygame.KEYDOWN, pygame.KEYUP):
            self.pressed_keys = pygame.key.get_pressed()
            if self.pressed_keys[pygame.K_ESCAPE]:
                self.quit = True
        if event.type == pygame.KEYDOWN:
            for i, key in enumerate(self.number_keys):
                if key == event.key and i in range(len(self.sprite_list)):
                    self.tile_selector = i
            
    def update(self, screen):
        for key in self.key_bindings:
                if self.pressed_keys[self.key_bindings[key]]:
                    self.pos += self.direction_dict[key] * self.speed
        if pygame.mouse.get_pressed()[0]:
            self.place_tile(self.tile_selector, self.modified_mouse())
        self.cam.update(self.pos)
        # Draw
        screen.fill(WHITE)
        for i, row in enumerate(self.level_data):
            for j, tile in enumerate(row):
                if tile is not None:
                    rect = pygame.Rect(j * int(self.tile_size.x), i * int(self.tile_size.y), 0, 0)
                    screen.blit(self.sprite_list[tile], self.cam.apply(rect))
        pygame.draw.rect(screen, BLACK, self.cam.apply(self.level_rect), 5)
    
    def make_level_rect(self, x, y):
        # Make a rectangle to show boundaries of level
        return pygame.Rect(0, 0, int(x * self.tile_size.x), int(y * self.tile_size.y))

    def scale_sprites(self):
        for i, sprite in enumerate(self.sprite_list):
            self.sprite_list[i] = scale_image(sprite, self.scale)

    def modified_mouse(self):
        # Modify the mouse position by the camera to find relative position to use
        mouse_pos = pygame.math.Vector2(*pygame.mouse.get_pos())
        mouse_pos -= pygame.math.Vector2(*self.cam.state.topleft)
        return mouse_pos

    def place_tile(self, tile_type, mouse_pos):
        # Find what tile in the grid that the new mouse position is located in
        mouse_pos /= self.tile_size.x
        r, c = int(mouse_pos.y), int(mouse_pos.x)
        if r in range(len(self.level_data)) and c in range(len(self.level_data[r])):
            self.level_data[r][c] = tile_type

    def save_level(self):
        # Save level data into a json file
        with open(self.current_level, "w") as f:
                json.dump(self.level_data, f)

    def load_level(self, name):
        # Attempt to load a json file into the level data
        if os.path.isfile(name):
            with open(name, "r") as f:
                self.level_data = json.load(f)
        else:
            # Failed, file not found
            return False
        y = len(self.level_data)
        x = len(self.level_data[0])
        self.level_rect = self.make_level_rect(x, y)
        self.current_level = name
        return True


    def make_empty_level(self, x, y, default_tile=None):
        x, y = int(x), int(y)
        empty = []
        for i in range(y):
            empty.append([default_tile] * x)
        return empty
    
    def camera_function(self, camera, target):
        x, y = target
        _, _, w, h = camera # width, height
        # center on target rect
        return pygame.Rect(-int(x)+self.SCREEN_SIZE[0]/2, -int(y)+self.SCREEN_SIZE[1]/2, w, h)
    
    def split_sprites(self, sheet):
        indices = [[0, 0], [1, 0], [2, 0], [3, 0], [4, 0]]
        return get_images(sheet, indices, self.native_size)
        

def get_images(sheet, frame_indices, size):
    frames = []
    for cell in frame_indices:
        frame_rect = ((size[0]*cell[0], size[1] * cell[1]), size)
        frames.append(sheet.subsurface(frame_rect))
    return frames
    
def scale_image(image, scale):
    rect = image.get_rect()
    scaled_image = pygame.Surface((rect.width*scale, rect.height*scale))
    for x in range(rect.width):
        for y in range(rect.height):
            color =  image.get_at((x,y))
            scaled_pos = (x*scale, y*scale)
            for i in range(scale):
                for j in range(scale):
                    scaled_image.set_at((scaled_pos[0]+i, scaled_pos[1]+j), color)
    return scaled_image.convert()

def main():
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.init()

    SCREEN_SIZE = (720, 480)
    DESIRED_FPS = 60.0
    ms_per_update = 1000.0 / DESIRED_FPS

    pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption("Level Editor")

    screen = pygame.display.get_surface()
    CLOCK = pygame.time.Clock()

    editor = LevelEditorState()
    editor.startup()
    input_handler = inputhandler.InputHandler(editor)

    input_thread = threading.Thread(target=input_handler.main)
    input_thread.daemon = True
    input_thread.start()


    lag = 0.0
    while not editor.quit:
        lag += CLOCK.tick()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                editor.quit = True
            editor.get_event(event)

        while lag >= ms_per_update:
            editor.update(screen)
            lag -= ms_per_update

        pygame.display.update()

        if not input_thread.is_alive():
            input_thread = threading.Thread(target=input_handler.main)
            input_thread.daemon = True
            input_thread.start()

    editor.cleanup()
    print()

if __name__ == "__main__":
    main()
