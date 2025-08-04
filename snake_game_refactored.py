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

            
# --Game Class--
class Game:
    
    def start(self):
        print("Game is starting...")
        
        Info_Object = pg.display.Info()
        
        # In Game Constants
        global SCREEN_WIDTH, SCREEN_HEIGHT, GRID_COUNT, GRID_SIZE, HEAD_SIZE
        SCREEN_WIDTH = SCREEN_HEIGHT = (Info_Object.current_h)*4//5 if Info_Object.current_h < Info_Object.current_w else (Info_Object.current_h)*4//5
        GRID_COUNT = 12
        GRID_SIZE = SCREEN_WIDTH // GRID_COUNT
        HEAD_SIZE = GRID_SIZE + (GRID_SIZE // 5) * 2
        
        # In Game Dependencies
        global SCREEN, CLOCK, FPS, FRANES_PER_MOVE, SCORE
        SCREEN = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
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
                "background": pg.transform.scale(pg.image.load(resource_path("graphs/background.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT)),
                "food": pg.transform.scale(pg.image.load(resource_path("graphs/food.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
                "snake_head": pg.transform.scale(pg.image.load(resource_path("graphs/snake_head.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)),
                "under_head": pg.transform.scale(pg.image.load(resource_path("graphs/under_head.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)),
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
        
        
    def run(self):
        self.start()
        
        while self.running:
            continue
        
        
if __name__ == "__main__":
    game = Game()
    game.run()