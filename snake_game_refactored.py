# --Gerekli Kütüphaneler--
import pygame as pg
import os
import sys
pg.init()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --Snake Class--
class Snake:
    
    def __init__(self):
        super().__init__()
        self.direction = [(1, 0), (1, 0)]
        self.body_grid = [((SCREEN_SIZE//GRID_SIZE) // 2 - 1, (SCREEN_SIZE//GRID_SIZE) // 2), ((SCREEN_SIZE//GRID_SIZE) // 2 - 2, (SCREEN_SIZE//GRID_SIZE) // 2)]
        self.body_pixels = [pg.Vector2(pos) * GRID_SIZE for pos in self.body_grid]
        
    @staticmethod    
    def rotate(image, direction):
        if direction == (1, 0):  return pg.transform.rotate(image, 270) # Right
        if direction == (-1, 0): return pg.transform.rotate(image, 90) # Left
        if direction == (0, 1):  return pg.transform.rotate(image, 180) # Down
        if direction == (0, -1): return image  # Up (no rotation)
        
    def draw(self, screen, graphics):
        # -- Draw Snake -- !!! Head must be drawn last !!!
        for i, pos in enumerate(self.body_pixels):
            center_pos = pos + pg.Vector2(GRID_SIZE // 2, GRID_SIZE // 2)
            # Draw tail
            if i == len(self.body_pixels) - 1:
                screen.blit(self.rotate(graphics["snake_tail"], self.direction[i]), graphics["snake_tail"].get_rect(center=center_pos))
            
            # Draw body    
            elif i != 0:
                # Draw all body parts as body for now TODO: make a func to draw body parts because it is so complicated
                screen.blit(self.rotate(graphics["snake_body"], self.direction[i]), graphics["snake_body"].get_rect(center=center_pos))

            # Draw head
            else:               
                screen.blit(self.rotate(graphics["under_head"], self.direction[i]), graphics["under_head"].get_rect(center=center_pos)) # Draw under head
                screen.blit(self.rotate(graphics["snake_head"], self.direction[i]), graphics["snake_head"].get_rect(center=center_pos)) # Draw head head
            

            
# --Game Class--
class Game:
    
    def start(self):
        print("Game is starting...")
        
        Info_Object = pg.display.Info()
        
        # In Game Constants
        global SCREEN_SIZE, GRID_COUNT, GRID_SIZE, HEAD_SIZE
        SCREEN_SIZE = (Info_Object.current_h)*4//5 if Info_Object.current_h < Info_Object.current_w else (Info_Object.current_h)*4//5
        GRID_COUNT = 12
        GRID_SIZE = SCREEN_SIZE // GRID_COUNT
        HEAD_SIZE = GRID_SIZE + (GRID_SIZE // 5) * 2
        
        # In Game Dependencies
        global SCREEN, CLOCK, FPS, FRANES_PER_MOVE, SCORE
        SCREEN = pg.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
        CLOCK = pg.time.Clock()
        FPS = 60
        FRANES_PER_MOVE = 8
        SCORE = 0
        
        self.running = True
        self.game_over = False
        
        self.graphics = self.load_images()
        
        print("Game has started!")
        
    @staticmethod    
    def load_images():
        print("Loading images...")
        # Loading assests like images, sounds, etc.
        try:
            return {
                "background": pg.transform.scale(pg.image.load(resource_path("graphs/background.png")).convert(), (SCREEN_SIZE, SCREEN_SIZE)),
                "food": pg.transform.scale(pg.image.load(resource_path("graphs/food.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
                "snake_head": pg.transform.scale(pg.image.load(resource_path("graphs/snake_head.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)),
                "under_head": pg.transform.scale(pg.image.load(resource_path("graphs/under_head.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
                "snake_body": pg.transform.scale(pg.image.load(resource_path("graphs/snake_body.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
                "body_corner": [pg.transform.scale(pg.image.load(resource_path(f"graphs/corner_{i}.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)) for i in ["tl", "tr", "bl", "br"]],
                "snake_tail": pg.transform.scale(pg.image.load(resource_path("graphs/snake_tail.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
                "snake_blink": [pg.transform.scale(pg.image.load(resource_path(f"graphs/snake_blink{i}.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)) for i in range(2)] + ["finish"],
                "snake_see": [pg.transform.scale(pg.image.load(resource_path(f"graphs/snake_see{i}.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)) for i in range(3)],
                "snake_eat": [pg.transform.scale(pg.image.load(resource_path(f"graphs/snake_eat{i}.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)) for i in range(4)] + ["finish"],
                "body_eat": [pg.transform.scale(pg.image.load(resource_path(f"graphs/body_eat{i}.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)) for i in range(3)],
                "eat_corner": [pg.transform.scale(pg.image.load(resource_path(f"graphs/eat_{i}.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)) for i in ["tl", "tr", "bl", "br"]],
                "snake_dead": [pg.transform.scale(pg.image.load(resource_path(f"graphs/snake_dead{i}.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)) for i in range(2)],
                "snake_xx": pg.transform.scale(pg.image.load(resource_path("graphs/snake_xx.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE))
            }
        except Exception as e:
            print(f"Error loading images: {e}")
            sys.exit(1)
        print("Assets loaded successfully!")
        
    @staticmethod
    def load_sounds():
        print("Loading sounds...")
        # Loading sounds
        try:
            return {
                "A4": pg.mixer.Sound(resource_path("music_notes/A4.wav")),
                "A5": pg.mixer.Sound(resource_path("music_notes/A5.wav")),
                "B4": pg.mixer.Sound(resource_path("music_notes/B4.wav")),
                "B5": pg.mixer.Sound(resource_path("music_notes/B5.wav")),
                "C5": pg.mixer.Sound(resource_path("music_notes/C5.wav")),
                "C6": pg.mixer.Sound(resource_path("music_notes/C6.wav")),
                "C#6": pg.mixer.Sound(resource_path("music_notes/Cb6.wav")),
                "D5": pg.mixer.Sound(resource_path("music_notes/D5.wav")),
                "D#5": pg.mixer.Sound(resource_path("music_notes/Db5.wav")),
                "E5": pg.mixer.Sound(resource_path("music_notes/E5.wav")),
                "F5": pg.mixer.Sound(resource_path("music_notes/F5.wav")),
                "F#5": pg.mixer.Sound(resource_path("music_notes/Fb5.wav")),
                "G5": pg.mixer.Sound(resource_path("music_notes/G5.wav")),
                "G#4": pg.mixer.Sound(resource_path("music_notes/Gb4.wav")),
                "G#5": pg.mixer.Sound(resource_path("music_notes/Gb5.wav")),
                "C1": pg.mixer.Sound(resource_path("music_notes/C1.wav"))
            }
        except Exception as e:
            print(f"Error loading sounds: {e}")
            sys.exit(1)
        print("Sounds loaded successfully!")
        
        
    def draw_objects(self, *args):
        SCREEN.blit(self.graphics["background"], (0, 0))
        for obj in args:
            obj.draw(SCREEN, self.graphics)
        
    def run(self):
        self.start()
        snake = Snake()
        
        while self.running:
            
            pg.display.flip()
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                    
            self.draw_objects(snake)
            
            CLOCK.tick(FPS)
            
        print("Game Over!")
        
        
if __name__ == "__main__":
    game = Game()
    game.run()