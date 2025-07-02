import pygame as pg
import sys
from random import randint
from time import sleep
import os

# --- Oyun Sabitleri (Game Constants) ---
# Pygame'i başlatıp ekran bilgilerini alıyoruz.
pg.init()
Info_Object = pg.display.Info()
SCREEN_HEIGHT = (Info_Object.current_h) * 4 // 5
SCREEN_WIDTH = SCREEN_HEIGHT
GRID_SIZE = 50
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
HEAD_SIZE = GRID_SIZE + (GRID_SIZE // 5) * 2

# --- Oyun Ayarları (Game Settings) ---
FPS = 60
FRAMES_PER_MOVE = 7
MAX_MOVE_QUEUE = 2

# --- Renk Tanımlamaları (Color Definitions) ---
BLACK = (0, 0, 0)
GRID_COLOR = (169, 217, 131)
SCORE_COLOR = (149, 197, 111)

# --- Özel Pygame Olayları (Custom Pygame Events) ---
BLINK_EVENT = pg.USEREVENT + 1


# --- Yardımcı Fonksiyonlar (Helper Functions) ---
def resource_path(relative_path):
    """
    Oyunun dosyalarının (resimler, sesler) yolunu doğru bir şekilde bulmasını sağlar.
    Özellikle PyInstaller ile tek bir .exe dosyası oluşturulduğunda kritik öneme sahiptir.
    """
    try:
        # PyInstaller geçici bir klasör oluşturur ve yolu _MEIPASS içinde saklar.
        base_path = sys._MEIPASS
    except AttributeError:
        # Eğer oyun normal bir Python scripti olarak çalıştırılıyorsa, mevcut dosya konumunu temel alır.
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def load_graphics():
    """Tüm oyun içi görselleri yükler, ölçeklendirir ve bir sözlükte döndürür."""
    # Tekrarlayan kodları azaltmak için liste üreteçleri kullanıldı.
    return {
        "background": pg.transform.scale(pg.image.load(resource_path("graphs/background.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT)),
        "food_image": pg.transform.scale(pg.image.load(resource_path("graphs/food.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "snake_head": pg.transform.scale(pg.image.load(resource_path("graphs/snake_head.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)),
        "under_head": pg.transform.scale(pg.image.load(resource_path("graphs/under_head.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "snake_body": pg.transform.scale(pg.image.load(resource_path("graphs/snake_body.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "body_corner": [pg.transform.scale(pg.image.load(resource_path(f"graphs/{img}")).convert_alpha(), (GRID_SIZE, GRID_SIZE)) for img in ["corner_tl.png", "corner_tr.png", "corner_bl.png", "corner_br.png"]],
        "snake_tail": pg.transform.scale(pg.image.load(resource_path("graphs/snake_tail.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "snake_blink": [pg.transform.scale(pg.image.load(resource_path(f"graphs/snake_blink{i}.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)) for i in range(2)] + ["finish"],
        "snake_see": [pg.transform.scale(pg.image.load(resource_path(f"graphs/snake_see{i}.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)) for i in range(3)],
        "snake_eat": [pg.transform.scale(pg.image.load(resource_path(f"graphs/snake_eat{i}.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)) for i in range(4)] + ["finish"],
        "body_eat": [pg.transform.scale(pg.image.load(resource_path(f"graphs/body_eat{i}.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)) for i in range(3)],
        "eat_corner": [pg.transform.scale(pg.image.load(resource_path(f"graphs/{img}")).convert_alpha(), (GRID_SIZE, GRID_SIZE)) for img in ["eat_tl.png", "eat_tr.png", "eat_bl.png", "eat_br.png"]],
        "snake_dead": [pg.transform.scale(pg.image.load(resource_path(f"graphs/snake_dead{i}.png")).convert_alpha(), (SCREEN_WIDTH, SCREEN_HEIGHT)) for i in range(2)],
        "snake_xx": pg.transform.scale(pg.image.load(resource_path("graphs/snake_xx.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE))
    }


def load_sounds():
    """Tüm ses dosyalarını yükler ve bir sözlükte döndürür."""
    notes = ["A4", "A5", "B4", "B5", "C5", "C6", "D5", "E5", "F5", "G5", "C1"]
    sharps = {"C#6": "Cb6", "D#5": "Db5", "F#5": "Fb5", "G#4": "Gb4", "G#5": "Gb5"}
    
    music_notes = {note: pg.mixer.Sound(resource_path(f"music_notes/{note}.wav")) for note in notes}
    music_notes.update({sharp_key: pg.mixer.Sound(resource_path(f"music_notes/{wav_file}.wav")) for sharp_key, wav_file in sharps.items()})
    return music_notes


# --- Yılan Sınıfı (Snake Class) ---
class Snake:
    """Yılanın tüm özelliklerini ve davranışlarını yönetir."""
    def __init__(self, graphics):
        self.graphics = graphics
        self.body_grid = [(GRID_WIDTH // 2, GRID_HEIGHT // 2), (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2)]
        self.direction = [(1, 0), (1, 0)]
        self.l_direction = (1, 0)
        self.is_growing = False
        self.bulge_indices = []
        self.emotion = None
        self.body_pixels = [pg.Vector2(pos) * GRID_SIZE for pos in self.body_grid]
        self.head_direction = (1, 0)
        self.head_cooldown = 0
        self.event_start_time = 0

    @staticmethod
    def _rotate_surface(surface, direction_vector):
        """Bir yüzeyi, hareket yönüne göre döndürür."""
        angle = 0
        if direction_vector == (1, 0): angle = 270
        elif direction_vector == (-1, 0): angle = 90
        elif direction_vector == (0, 1): angle = 180
        elif direction_vector == (0, -1): angle = 0
        return pg.transform.rotate(surface, angle)

    def change_direction(self, new_direction):
        """Geriye gitmeyi engelleyerek yılanın yönünü değiştirir."""
        if (new_direction[0] * -1, new_direction[1] * -1) != self.l_direction:
            self.direction[0] = new_direction

    def move(self):
        """Yılanı mevcut yönünde bir kare ilerletir."""
        self.l_direction = self.direction[0]
        head_x, head_y = self.body_grid[0]
        dir_x, dir_y = self.direction[0]
        new_head = (head_x + dir_x, head_y + dir_y)

        if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT) or new_head in self.body_grid:
            return False  # Oyun biter.

        self.body_grid.insert(0, new_head)
        self.direction.insert(0, self.direction[0])
        self.body_pixels.insert(0, self.body_pixels[0].copy())
        
        self.bulge_indices = [i + 2 for i in self.bulge_indices]

        if self.is_growing:
            self.emotion = "eat"
            self.event_start_time = pg.time.get_ticks()
            self.is_growing = False
            self.bulge_indices.append(1)
        else:
            self.body_grid.pop()
            self.direction.pop()
            self.body_pixels.pop()

        self.bulge_indices = [i for i in self.bulge_indices if i < len(self.body_grid)]
        return True

    def grow(self):
        """Yılanın bir sonraki hamlede büyümesini sağlar."""
        self.is_growing = True

    def animate(self):
        """Yılanın kareler arasında akıcı bir şekilde kaymasını sağlar."""
        for i in range(len(self.body_pixels)):
            target_pixel_pos = pg.Vector2(self.body_grid[i]) * GRID_SIZE
            self.body_pixels[i] = self.body_pixels[i].lerp(target_pixel_pos, 0.25)
    
    def _draw_body(self, surface):
        """Yılanın gövdesini ve kuyruğunu çizer."""
        body_eat_anim_index = (pg.time.get_ticks() // 200) % len(self.graphics["body_eat"])
        for i, pixel_pos in enumerate(self.body_pixels[1:], start=1):
            center_pos = (pixel_pos.x + GRID_SIZE / 2, pixel_pos.y + GRID_SIZE / 2)
            
            image_to_draw = None
            if i == len(self.body_pixels) - 1: # Kuyruk
                image_to_draw = self._rotate_surface(self.graphics["snake_tail"], self.direction[i])
            else: # Gövde
                vec_from_head = pg.Vector2(self.body_grid[i - 1]) - pg.Vector2(self.body_grid[i])
                vec_to_tail = pg.Vector2(self.body_grid[i + 1]) - pg.Vector2(self.body_grid[i])
                
                if vec_from_head == vec_to_tail * -1: # Düz gövde
                    base_image = self.graphics["body_eat"][body_eat_anim_index] if i in self.bulge_indices else self.graphics["snake_body"]
                    image_to_draw = self._rotate_surface(base_image, self.direction[i])
                else: # Köşe gövde
                    turn_vectors = {(int(vec_from_head.x), int(vec_from_head.y)), (int(vec_to_tail.x), int(vec_to_tail.y))}
                    corner_set = self.graphics["eat_corner"] if i in self.bulge_indices else self.graphics["body_corner"]
                    if turn_vectors == {(0, -1), (-1, 0)}: image_to_draw = corner_set[0]
                    elif turn_vectors == {(0, -1), (1, 0)}: image_to_draw = corner_set[1]
                    elif turn_vectors == {(0, 1), (-1, 0)}: image_to_draw = corner_set[2]
                    elif turn_vectors == {(0, 1), (1, 0)}: image_to_draw = corner_set[3]
            
            if image_to_draw:
                surface.blit(image_to_draw, image_to_draw.get_rect(center=center_pos))

    def _draw_head(self, surface):
        """Yılanın başını ve animasyonlarını çizer."""
        head_pixel_pos = self.body_pixels[0]
        center_pos = (head_pixel_pos.x + GRID_SIZE / 2, head_pixel_pos.y + GRID_SIZE / 2)
        
        rotated_under_head = self._rotate_surface(self.graphics["under_head"], self.l_direction)
        surface.blit(rotated_under_head, rotated_under_head.get_rect(center=center_pos))

        head_surface = self.graphics["snake_head"]
        if self.emotion:
            now = pg.time.get_ticks()
            if self.emotion == "eat":
                idx = (now - self.event_start_time) // 200 % len(self.graphics["snake_eat"])
                if idx != len(self.graphics["snake_eat"]) - 1: head_surface = self.graphics["snake_eat"][idx]
                else: self.emotion = None
            elif self.emotion == "see":
                head_surface = self.graphics["snake_see"][(now // 50) % len(self.graphics["snake_see"])]
            elif self.emotion == "blink":
                idx = (now - self.event_start_time) // 50 % len(self.graphics["snake_blink"])
                if idx != len(self.graphics["snake_blink"]) - 1: head_surface = self.graphics["snake_blink"][idx]
                else: self.emotion = None
            elif self.emotion == "dead":
                head_surface = self.graphics["snake_xx"]
        
        if pg.time.get_ticks() - self.head_cooldown > 100:
            self.head_direction = self.l_direction
            self.head_cooldown = pg.time.get_ticks()

        rotated_head = self._rotate_surface(head_surface, self.head_direction)
        surface.blit(rotated_head, rotated_head.get_rect(center=center_pos))

    def draw(self, surface):
        """Yılanın tüm parçalarını ekrana çizer."""
        self._draw_body(surface)
        self._draw_head(surface)


# --- Yem Sınıfı (Food Class) ---
class Food:
    """Yemin özelliklerini ve davranışlarını yönetir."""
    def __init__(self, snake_body, graphics):
        self.graphics = graphics
        self.position = (0, 0)
        self.randomize_position(snake_body)

    def randomize_position(self, snake_body):
        """Yemin pozisyonunu, yılanın üzerinde olmayacak şekilde rastgele belirler."""
        while True:
            self.position = (randint(0, GRID_WIDTH - 1), randint(0, GRID_HEIGHT - 1))
            if self.position not in snake_body:
                break

    def draw(self, surface):
        """Yemi ekrana çizer."""
        rect = self.graphics["food_image"].get_rect(topleft=(self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE))
        surface.blit(self.graphics["food_image"], rect)


# --- Ana Oyun Sınıfı (Main Game Class) ---
class Game:
    """Oyunun ana döngüsünü ve durumunu yönetir."""
    MELODY = ['B4', 'A4', 'G#4', 'A4', 'C5', 'D5', 'C5', 'B4', 'C5', 'E5', 'F5', 'E5', 'D#5', 'E5', 'B5', 'A5', 'G#5', 'A5', 'B5', 'A5', 'G#5', 'A5', 'C6', 'A5', 'C6', 'G5', 'A5', 'B5', 'A5', 'G5', 'A5', 'G5', 'A5', 'B5', 'A5', 'G5', 'A5', 'G5', 'A5', 'B5', 'A5', 'G5', 'F#5', 'E5', 'E5', 'F5', 'G5', 'G5', 'A5', 'G5', 'F5', 'E5', 'D5', 'E5', 'F5', 'G5', 'G5', 'A5', 'G5', 'F5', 'E5', 'D5', 'C5', 'D5', 'E5', 'E5', 'F5', 'E5', 'D5', 'C5', 'B4', 'C5', 'D5', 'E5', 'E5', 'F5', 'E5', 'D5', 'C5', 'B4', 'B4', 'A4', 'G#4', 'A4', 'C5', 'D5', 'C5', 'B4', 'C5', 'E5', 'F5', 'E5', 'D#5', 'E5', 'B5', 'A5', 'G#5', 'A5', 'B5', 'A5', 'G#5', 'A5', 'C6', 'A5', 'B5', 'C#6', 'A5', 'B5', 'C#6', 'B5', 'A5', 'G#5', 'F#5', 'G#5', 'A5', 'B5', 'G#5', 'E5', 'A5', 'B5', 'C#6', 'A5', 'B5', 'C#6', 'B5', 'A5', 'G#5', 'F#5', 'B5', 'G#5', 'E5', 'A5', 'A5', 'B5', 'C#6', 'A5', 'B5', 'C#6', 'B5', 'A5', 'G#5', 'F#5', 'G#5', 'A5', 'B5', 'G#5', 'E5', 'A5', 'B5', 'C#6', 'A5', 'B5', 'C#6', 'B5', 'A5', 'G#5', 'F#5', 'B5', 'G#5', 'E5', 'A5']

    def __init__(self):
        pg.display.set_caption("Snake Game")
        self.screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pg.time.Clock()
        self.graphics = load_graphics()
        self.sounds = load_sounds()
        self.text_font = pg.font.Font(resource_path("graphs/snake_game_font.ttf"), 20)
        
        icon = pg.transform.rotate(self.graphics["snake_head"], 180)
        pg.display.set_icon(icon)

        self.reset_game()

    def reset_game(self):
        """Oyunu başlangıç durumuna sıfırlar."""
        self.snake = Snake(self.graphics)
        self.food = Food(self.snake.body_grid, self.graphics)
        self.score = 0
        self.game_over = False
        self.running = True
        self.move_queue = []
        self.snake_move_counter = 0
        self.note_order = 0
        
    def _play_note(self, list_name="MELODY"):
        """Nota çalar."""
        for note in self.sounds.values(): note.stop()
        
        if list_name == "MELODY":
            note_key = self.MELODY[self.note_order % len(self.MELODY)]
            self.sounds[note_key].play()
            self.note_order += 1
        elif list_name == "DEAD":
            self.sounds["C1"].play()

    def _draw_grid(self):
        """Ekrana kılavuz çizgilerini çizer."""
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pg.draw.line(self.screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pg.draw.line(self.screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))
            
    def _handle_events(self):
        """Kullanıcı girdilerini ve özel olayları yönetir."""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.game_over = True
                self.running = False

            if event.type == pg.KEYDOWN:
                key_map = {pg.K_UP: (0, -1), pg.K_DOWN: (0, 1), pg.K_LEFT: (-1, 0), pg.K_RIGHT: (1, 0)}
                if event.key in key_map and len(self.move_queue) < MAX_MOVE_QUEUE:
                    new_move = key_map[event.key]
                    last_move = self.move_queue[-1] if self.move_queue else self.snake.direction[0]
                    if new_move[0] * -1 != last_move[0] or new_move[1] * -1 != last_move[1]:
                        self.move_queue.append(new_move)
            
            if event.type == BLINK_EVENT:
                if not self.snake.emotion:
                    self.snake.emotion = "blink"
                    self.snake.event_start_time = pg.time.get_ticks()

    def _update_game_state(self):
        """Oyun mantığını ve nesnelerin durumunu günceller."""
        self.snake_move_counter += 1
        if self.snake_move_counter >= FRAMES_PER_MOVE:
            self.snake_move_counter = 0
            if self.move_queue:
                self._play_note()
                self.snake.change_direction(self.move_queue.pop(0))
            
            if not self.snake.move():
                if not hasattr(self.snake, 'dead_counter'):
                    self.snake.emotion = "dead"
                    self.snake.dead_counter = pg.time.get_ticks()
                if pg.time.get_ticks() - self.snake.dead_counter >= 100:
                    self.game_over = True
            elif self.snake.emotion == "dead":
                self.snake.emotion = None

        if self.snake.body_grid[0] == self.food.position:
            self.score += 1
            self.snake.grow()
            self.food.randomize_position(self.snake.body_grid)
        else:
            self._check_food_proximity()
        
        self.snake.animate()

    def _check_food_proximity(self):
        """Yılanın yeme yakın olup olmadığını kontrol eder."""
        head_pos = self.snake.body_grid[0]
        food_pos = self.food.position
        is_close = abs(head_pos[0] - food_pos[0]) <= 3 and abs(head_pos[1] - food_pos[1]) <= 3
        
        if is_close and self.snake.emotion not in ["eat", "dead"]: self.snake.emotion = "see"
        elif not is_close and self.snake.emotion == "see": self.snake.emotion = None

    def _draw_elements(self):
        """Tüm oyun elemanlarını ekrana çizer."""
        self.screen.blit(self.graphics["background"], (0, 0))
        self._draw_grid()
        self.snake.draw(self.screen)
        self.food.draw(self.screen)
        score_surface = self.text_font.render(f"Score: {self.score}", True, SCORE_COLOR)
        self.screen.blit(score_surface, (10, 10))
        pg.display.flip()

    def _run_game_over_sequence(self):
        """Oyun bittiğinde gösterilecek animasyonu çalıştırır."""
        self._play_note("DEAD")
        dead_start_time = pg.time.get_ticks()
        dead_screen_capture = self.screen.copy()
        dead_animate_time = randint(400, 600)
        while pg.time.get_ticks() - dead_start_time < 3000:
            for event in pg.event.get():
                if event.type == pg.QUIT: return

            self.screen.blit(dead_screen_capture, (0, 0))
            idx = (pg.time.get_ticks() // dead_animate_time) % len(self.graphics["snake_dead"])
            self.screen.blit(self.graphics["snake_dead"][idx], (0, 0))
            pg.display.flip()
            self.clock.tick(FPS)

    def run(self):
        """Ana oyun döngüsünü başlatır ve yönetir."""
        pg.time.set_timer(BLINK_EVENT, randint(1000, 2000))
        sleep(0.05)

        while self.running:
            self._handle_events()
            self._update_game_state()
            self._draw_elements()
            self.clock.tick(FPS)
            
            if self.game_over:
                if self.running: self._run_game_over_sequence()
                self.running = False
        
        pg.quit()
        sys.exit()

# --- Ana Çalıştırma Bloğu (Main Execution Block) ---
if __name__ == "__main__":
    game = Game()
    game.run()