# --- Gerekli Kütüphanelerin Yüklenmesi ---
import pygame as pg
import sys
from random import randint
from time import sleep
import os




# --- Ana Fonksiyon ---
# Oyunun tüm mantığının ve döngüsünün bulunduğu ana fonksiyon.
def main():
    pg.init()

    Info_Object = pg.display.Info()
    # --- Oyun Sabitleri ---
    # Bu değerler oyunun temel özelliklerini belirler ve kod içinde kolayca değiştirilebilir.
    SCREEN_WIDTH = SCREEN_HEIGHT = (Info_Object.current_h)*4 //5                       # Oyun penceresinin genişliği (piksel)                          # Oyun penceresinin yüksekliği (piksel).
    GRID_SIZE = 50                               # Oyun alanındaki her bir karenin boyutu (piksel).
    GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE       # Ekranın kaç adet kareden oluştuğunu hesaplar (genişlik).
    GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE     # Ekranın kaç adet kareden oluştuğunu hesaplar (yükseklik).
    HEAD_SIZE = GRID_SIZE + (GRID_SIZE // 5) * 2 # Yılanın başının gövdesinden daha büyük görünmesi için özel bir boyut hesaplaması.
    print(f"SCREEN SIZE: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")


    # Yılanın bir kare hareket etmesi için geçmesi gereken ekran çerçevesi (frame) sayısı.
    # Bu değer ne kadar yüksek olursa, yılan o kadar yavaş hareket eder.
    FRAMES_PER_MOVE = 7

    # --- Renk Tanımlamaları ---
    # Renkler, RGB (Kırmızı, Yeşil, Mavi) formatında tanımlanır.
    WHITE = (255, 255, 255)
    GREEN = (0, 150, 0)
    DARK_GREEN = (0, 100, 0)
    RED = (200, 0, 0)
    BLACK = (0, 0, 0)
    GRID_COLOR = (169, 217, 131) # Izgara çizgilerinin rengi.
    SCORE = 0                   # Oyuncunun başlangıç skoru.

    # Bu yardımcı fonksiyon, oyunun dosyalarının (resimler, sesler) yolunu doğru bir şekilde bulmasını sağlar.
    # Özellikle PyInstaller ile tek bir .exe dosyası oluşturulduğunda kritik öneme sahiptir.
    def resource_path(relative_path):
        try:
            # PyInstaller geçici bir klasör oluşturur ve yolu _MEIPASS içinde saklar.
            base_path = sys._MEIPASS
        except Exception:
            # Eğer oyun normal bir Python scripti olarak çalıştırılıyorsa, mevcut dosya konumunu temel alır.
            base_path = os.path.abspath(".")
        # İstenen dosyanın tam yolunu döndürür.
        return os.path.join(base_path, relative_path)

    # Pygame kütüphanesini başlatır.

    # Oyun penceresini belirtilen genişlik ve yükseklikte oluşturur.
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    # Pencerenin başlığını ayarlar.
    pg.display.set_caption("Snake Game")

    # Skor gibi metinleri ekranda göstermek için kullanılacak yazı tipini ve boyutunu yükler.
    text_font = pg.font.Font(resource_path("graphs/snake_game_font.ttf"), 20)
    
    # --- Grafiklerin Yüklenmesi ---
    # Tüm oyun içi görseller (grafikler) yüklenir, ölçeklendirilir ve bir sözlükte saklanır.
    # Bu sayede koda erişimleri kolaylaşır.
    global note_order
    note_order = 0
    music_notes = {
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

    MELODY = [
    'B4', 'A4', 'G#4', 'A4', 'C5',
    'D5', 'C5', 'B4', 'C5', 'E5',
    'F5', 'E5', 'D#5', 'E5',
    'B5', 'A5', 'G#5', 'A5', 'B5', 'A5', 'G#5', 'A5', 'C6',
    'A5', 'C6', 'G5', 'A5', 'B5', 'A5',
    'G5', 'A5', 'G5', 'A5', 'B5', 'A5',
    'G5', 'A5', 'G5', 'A5', 'B5', 'A5', 'G5', 'F#5', 'E5',

    'E5', 'F5', 'G5', 'G5', 'A5', 'G5', 'F5', 'E5', 'D5',
    'E5', 'F5', 'G5', 'G5', 'A5', 'G5', 'F5', 'E5', 'D5',
    'C5', 'D5', 'E5', 'E5', 'F5', 'E5', 'D5', 'C5', 'B4',
    'C5', 'D5', 'E5', 'E5', 'F5', 'E5', 'D5', 'C5', 'B4',

    'B4', 'A4', 'G#4', 'A4', 'C5',
    'D5', 'C5', 'B4', 'C5', 'E5',
    'F5', 'E5', 'D#5', 'E5',
    'B5', 'A5', 'G#5', 'A5', 'B5', 'A5', 'G#5', 'A5', 'C6',

    'A5', 'B5', 'C#6', 'A5', 'B5', 'C#6',
    'B5', 'A5', 'G#5', 'F#5', 'G#5', 'A5', 'B5', 'G#5', 'E5',

    'A5', 'B5', 'C#6', 'A5', 'B5', 'C#6',
    'B5', 'A5', 'G#5', 'F#5', 'B5', 'G#5', 'E5', 'A5',

    'A5', 'B5', 'C#6', 'A5', 'B5', 'C#6',
    'B5', 'A5', 'G#5', 'F#5', 'G#5', 'A5', 'B5', 'G#5', 'E5',

    'A5', 'B5', 'C#6', 'A5', 'B5', 'C#6',
    'B5', 'A5', 'G#5', 'F#5', 'B5', 'G#5', 'E5', 'A5'
]

    graphics = {
        "background": pg.transform.scale(pg.image.load(resource_path("graphs/background.png")).convert(), (SCREEN_WIDTH, SCREEN_HEIGHT)),
        "food_image": pg.transform.scale(pg.image.load(resource_path("graphs/food.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "snake_head": pg.transform.scale(pg.image.load(resource_path("graphs/snake_head.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)),
        "under_head": pg.transform.scale(pg.image.load(resource_path("graphs/under_head.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "snake_body": pg.transform.scale(pg.image.load(resource_path("graphs/snake_body.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "body_corner": [pg.transform.scale(pg.image.load(resource_path("graphs/corner_tl.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)), # [0] -> top-left
        pg.transform.scale(pg.image.load(resource_path("graphs/corner_tr.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)), # [1] -> top-right
        pg.transform.scale(pg.image.load(resource_path("graphs/corner_bl.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)), # [2] -> bottom-left
        pg.transform.scale(pg.image.load(resource_path("graphs/corner_br.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE))], # [3] -> bottom-right
        "snake_tail": pg.transform.scale(pg.image.load(resource_path("graphs/snake_tail.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        "snake_blink": [pg.transform.scale(pg.image.load(resource_path("graphs/snake_blink0.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)),
        pg.transform.scale(pg.image.load(resource_path("graphs/snake_blink1.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)), 
        "finish"],
        "snake_see": [pg.transform.scale(pg.image.load(resource_path("graphs/snake_see0.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)),
        pg.transform.scale(pg.image.load(resource_path("graphs/snake_see1.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)),
        pg.transform.scale(pg.image.load(resource_path("graphs/snake_see2.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE))],
        "snake_eat": [pg.transform.scale(pg.image.load(resource_path("graphs/snake_eat0.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)),
        pg.transform.scale(pg.image.load(resource_path("graphs/snake_eat1.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)),
        pg.transform.scale(pg.image.load(resource_path("graphs/snake_eat2.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)),
        pg.transform.scale(pg.image.load(resource_path("graphs/snake_eat3.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE)),
        "finish"],
        "body_eat": [pg.transform.scale(pg.image.load(resource_path("graphs/body_eat0.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        pg.transform.scale(pg.image.load(resource_path("graphs/body_eat1.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
        pg.transform.scale(pg.image.load(resource_path("graphs/body_eat2.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),],
        "eat_corner": [pg.transform.scale(pg.image.load(resource_path("graphs/eat_tl.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
                       pg.transform.scale(pg.image.load(resource_path("graphs/eat_tr.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
                       pg.transform.scale(pg.image.load(resource_path("graphs/eat_bl.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE)),
                       pg.transform.scale(pg.image.load(resource_path("graphs/eat_br.png")).convert_alpha(), (GRID_SIZE, GRID_SIZE))],
        "snake_dead": [(pg.image.load(resource_path("graphs/snake_dead0.png"))).convert_alpha(),
        (pg.image.load(resource_path("graphs/snake_dead1.png"))).convert_alpha()],
        "snake_xx": pg.transform.scale(pg.image.load(resource_path("graphs/snake_xx.png")).convert_alpha(), (HEAD_SIZE, HEAD_SIZE))
    }

    def play_note(order= note_order, List = "MELODY"):
        for note in music_notes.values():
            note.stop()
        if List == "MELODY":
            order = order % len(MELODY)
            music_notes[MELODY[order]].play()
            # Stop any currently playing note before playing a new one
        elif List == "DEAD": music_notes["C1"].play()
        else: print("miss spell")

    # --- Ses Efektlerinin Yüklenmesi ---
    # Tüm ses efektleri (SFX) yüklenir ve bir sözlükte saklanır.
    
    # Oyunun hızını (FPS) kontrol etmek için bir saat nesnesi oluşturur.
    clock = pg.time.Clock()
    # Oyunun bitip bitmediğini kontrol eden bayrak (flag).
    game_over = False

    # Oyun penceresinin ikonunu ayarlar.
    icon_surface = pg.image.load(resource_path("graphs/snake_head.png")).convert_alpha()
    pg.display.set_icon(pg.transform.rotate(icon_surface, 180))

    # Ekrana kılavuz çizgilerini çizen fonksiyon.
    def draw_grid(surface):
        # Dikey çizgiler
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pg.draw.line(surface, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
        # Yatay çizgiler
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pg.draw.line(surface, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))

# --- Yılan Sınıfı (Snake Class) ---
# Yılanın tüm özelliklerini ve davranışlarını yönetir.
    class Snake:
        # Yılan nesnesi ilk oluşturulduğunda çalışan metot.
        def __init__(self):
            # Yılanın gövdesini oluşturan karelerin grid üzerindeki koordinatları.
            # En az 2 segment ile başlamalıdır çünkü çizim mantığı buna dayanır.
            self.body_grid = [(GRID_WIDTH // 2, GRID_HEIGHT // 2), (GRID_WIDTH // 2 - 1, GRID_HEIGHT // 2)]
            # Her bir gövde parçasının yönünü saklar.
            self.direction = [(1, 0), (1, 0)]
            # Yılanın bir önceki hamledeki yönünü saklar (geriye gitmeyi engellemek için).
            self.l_direction = (1, 0)
            # Yılanın yemek yiyip büyümesi gerekip gerekmediğini belirten bayrak.
            self.is_growing = False
            # Yılanın gövdesindeki "yeme" animasyonunun (şişkinliğin) hangi segmentlerde olduğunu takip eder.
            self.bulge_indices = []
            # Yılanın mevcut duygusal durumunu saklar (animasyonlar için: "blink", "see", "eat").
            self.emotion = None
            # Yılanın gövde parçalarının piksel koordinatları. Bu, akıcı animasyonlar için kullanılır.
            self.body_pixels = [pg.Vector2(pos) * GRID_SIZE for pos in self.body_grid]

        # Yılanın hareket yönünü değiştiren metot.
        def change_direction(self, new_direction):
            global note_order
            play_note(note_order)
            note_order += 1
            if (new_direction[0] * -1, new_direction[1] * -1) != self.l_direction:
                self.direction[0] = new_direction

        # Bir resmi, yılanın hareket yönüne göre döndüren yardımcı metot.
        def rotate(self, name, direction_vector):
            if direction_vector == (1, 0):    # Sağ
                return pg.transform.rotate(name, 270)
            elif direction_vector == (-1, 0): # Sol
                return pg.transform.rotate(name, 90)
            elif direction_vector == (0, 1):  # Aşağı
                return pg.transform.rotate(name, 180)
            elif direction_vector == (0, -1): # Yukarı
                return pg.transform.rotate(name, 0)
            return name

        # Yılanı mevcut yönünde bir kare ilerleten metot.
        def front_fonction(self):
            # Mevcut yönü, bir sonraki hamle için "son yön" olarak kaydeder.
            self.l_direction = self.direction[0]
            head_x, head_y = self.body_grid[0]
            dir_x, dir_y = self.direction[0]
            
            # Yeni baş pozisyonunu hesaplar.
            new_head = (head_x + dir_x, head_y + dir_y)

            # Kaybetme koşulları: Duvarlara veya kendine çarpma.
            if not (0 <= new_head[0] < GRID_WIDTH and 0 <= new_head[1] < GRID_HEIGHT) or new_head in self.body_grid:
                return False # Oyun biter.

            # Yılanın listelerini günceller: yeni başı ekler.
            self.body_grid.insert(0, new_head)
            self.direction.insert(0, self.direction[0])
            self.body_pixels.insert(0, self.body_pixels[0].copy())

            self.bulge_indices = [i + 2 for i in self.bulge_indices]
            self.bulge_indices = [i for i in self.bulge_indices if i < len(self.body_pixels)]

            # Eğer yılanın büyümesi gerekiyorsa (yemek yemişse):
            if self.is_growing:
                self.emotion = "eat" # Yeme animasyonunu tetikler.
                # Yeme animasyonunun her seferinde baştan başlaması için zamanlayıcıyı başlatır.
                self.event_start_time = pg.time.get_ticks()
                self.is_growing = False # Büyüme bayrağını sıfırlar.
                # Başın hemen arkasına (indeks 1) yeni bir şişkinlik ekler.
                self.bulge_indices.append(1)
            else:
                # Büyümüyorsa, kuyruktan bir segment siler.
                self.body_grid.pop()
                self.direction.pop()
                self.body_pixels.pop()

            # Kuyruğu geçmiş olan şişkinlikleri listeden temizler.
            self.bulge_indices = [i for i in self.bulge_indices if i < len(self.body_grid)]

            return True # Hareket başarılı.

        # Yılanın bir sonraki hamlede büyümesini sağlar.
        def grow(self):
            self.is_growing = True

        # Yılanın kareler arasında akıcı bir şekilde kaymasını sağlayan metot.
        def animate(self):
            for i in range(len(self.body_pixels)):
                # Hedef pozisyon (grid'e göre).
                target_pixel_pos = pg.Vector2(self.body_grid[i]) * GRID_SIZE
                # Mevcut piksel pozisyonunu hedefe doğru küçük bir adımla yaklaştırır (Linear Interpolation).
                self.body_pixels[i] = self.body_pixels[i].lerp(target_pixel_pos, 0.25)

        # Yılanı ekrana çizen metot.
        def draw(self, surface):
            print(self.direction)
            # Gövdedeki tüm şişkinlikler için ortak bir "atma" animasyon indeksi oluşturur.
            # Bu, `body_eat` listesindeki görseller arasında geçişi sağlar.
            body_eat_anim_index = (pg.time.get_ticks() // 200) % len(graphics["body_eat"])
            if not hasattr(self, "head_direction"): self.head_direction = (1, 0)

            # Gövdenin her bir parçasını çizer.
            for i, pixel_pos in enumerate(self.body_pixels):
                center_pos = (pixel_pos.x + GRID_SIZE / 2, pixel_pos.y + GRID_SIZE / 2)

                # KUYRUK (En son segment)
                if i == len(self.body_pixels) - 1:
                    rotated_image = self.rotate(graphics["snake_tail"], self.direction[i])
                    rect = rotated_image.get_rect(center=center_pos)
                    surface.blit(rotated_image, rect)

                # GÖVDE (Düz veya Köşe)
                elif i != 0:
                    current_grid_pos = pg.Vector2(self.body_grid[i])
                    head_side_grid_pos = pg.Vector2(self.body_grid[i-1]) # Başa doğru olan komşu
                    tail_side_grid_pos = pg.Vector2(self.body_grid[i+1]) # Kuyruğa doğru olan komşu
                    
                    vec_from_head = head_side_grid_pos - current_grid_pos
                    vec_to_tail = tail_side_grid_pos - current_grid_pos

                    # DÜZ GİDİYORSA:
                    if vec_from_head == vec_to_tail * -1:
                        # Mevcut segmentin bir şişkinliğe sahip olup olmadığını kontrol et.
                        if i in self.bulge_indices:
                            # Eğer varsa, animasyonlu "yeme" gövde parçasını kullan.
                            image_to_draw = graphics["body_eat"][body_eat_anim_index]
                        else:
                            # Yoksa, normal gövde parçasını kullan.
                            image_to_draw = graphics["snake_body"]
                        
                        rotated_image = self.rotate(image_to_draw, self.direction[i])
                        rect = rotated_image.get_rect(center=center_pos)
                        surface.blit(rotated_image, rect)
                    # KÖŞE DÖNÜYORSA: Doğru köşe resmini seçer.
                    else:
                        turn_vectors = {(int(vec_from_head.x), int(vec_from_head.y)), (int(vec_to_tail.x), int(vec_to_tail.y))}
                        
                        # Kullanılacak köşe görselleri setini belirle (normal veya yeme).
                        if i in self.bulge_indices:
                            corner_image_set = graphics["eat_corner"]
                        else:
                            corner_image_set = graphics["body_corner"]
                        
                        image_to_draw = None
                        if turn_vectors == {(0, -1), (-1, 0)}: image_to_draw = corner_image_set[0] # top-left
                        elif turn_vectors == {(0, -1), (1, 0)}: image_to_draw = corner_image_set[1] # top-right
                        elif turn_vectors == {(0, 1), (-1, 0)}: image_to_draw = corner_image_set[2] # bottom-left
                        elif turn_vectors == {(0, 1), (1, 0)}: image_to_draw = corner_image_set[3] # bottom-right
                        
                        if image_to_draw:
                            rect = image_to_draw.get_rect(center=center_pos)
                            surface.blit(image_to_draw, rect)
            
            # KAFA (En son çizilir, diğer her şeyin üzerinde görünür)
            head_pixel_pos = self.body_pixels[0]
            center_pos = (head_pixel_pos.x + GRID_SIZE / 2, head_pixel_pos.y + GRID_SIZE / 2)
            
            # Kafanın alt katmanını çizer.
            rotated_under_head_image = self.rotate(graphics["under_head"], self.l_direction)
            under_rect = rotated_under_head_image.get_rect(center=center_pos)
            surface.blit(rotated_under_head_image, under_rect)

            if not hasattr(self, "head_cooldown"): self.head_cooldown = pg.time.get_ticks()
            # Eğer bir animasyon aktifse, onu çizer.
            if self.emotion:
                if self.emotion == "eat":
                    eat_index = (pg.time.get_ticks() - self.event_start_time) // 200 % len(graphics["snake_eat"])
                    if eat_index != len(graphics["snake_eat"]) - 1:
                        head_surface = graphics["snake_eat"][eat_index]
    
                    else:
                        head_surface = graphics["snake_head"]
                        self.emotion = None # Animasyon bitince durumu sıfırlar.
                        del self.event_start_time

                elif self.emotion == "see":
                    see_index = (pg.time.get_ticks() // 50) % len(graphics["snake_see"])
                    head_surface = graphics["snake_see"][see_index]

                    
                elif self.emotion == "blink":
                    blink_index = (pg.time.get_ticks() - self.event_start_time) // 50 % len(graphics["snake_blink"])
                    if blink_index != len(graphics["snake_blink"]) - 1:
                        head_surface = graphics["snake_blink"][blink_index]
    
                    else:
                        head_surface = graphics["snake_head"]
                        self.emotion = None # Animasyon bitince durumu sıfırlar.
                        del self.event_start_time
                elif self.emotion == "dead":
                    head_surface = graphics["snake_xx"]

            # Eğer animasyon yoksa, normal kafa resmini çizer.
            else:
                head_surface = graphics["snake_head"]

            if pg.time.get_ticks() - self.head_cooldown > 100:
                self.head_direction = self.l_direction
                del self.head_cooldown 
            
            surface.blit(self.rotate(head_surface, self.head_direction), head_surface.get_rect(center=center_pos))


    # --- Yem Sınıfı (Food Class) ---
    # Yemin özelliklerini ve davranışlarını yönetir.
    class Food:
        # Yem nesnesi ilk oluşturulduğunda çalışır.
        def __init__(self, snake_body):
            # Yemin pozisyonunu, yılanın üzerinde olmayacak şekilde rastgele belirler.
            self.ramdomize_position(snake_body)
        
        # Yemin pozisyonunu rastgele değiştiren metot.
        def ramdomize_position(self, snake_body):
            while True:
                self.position = (randint(0, GRID_WIDTH - 1), randint(0, GRID_HEIGHT - 1))
                # Eğer belirlenen pozisyon yılanın gövdesinin üzerinde değilse döngüden çıkar.
                if self.position not in snake_body:
                    break

        # Yemi ekrana çizen metot.
        def draw(self, surface):
            surface.blit(graphics["food_image"], (self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE))

    # Yılan ve yem nesnelerini oluşturur.
    snake = Snake()
    food = Food(snake.body_grid)
    
    # Oyuncunun hızlıca bastığı yön tuşlarını saklamak için bir kuyruk.
    # Bu, kontrollerin daha akıcı ve tepkisel olmasını sağlar.
    move_queue = []
    MAX_MOVE_QUEUE = 2 # Kuyrukta en fazla 2 hamle saklanabilir.

    # Yılan hareketini zamanlamak için kullanılan çerçeve sayacı.
    snake_move_counter = 0

    # --- Özel Pygame Olayları (Event) ---
    # Belirli aralıklarla özel olaylar tetiklemek için kullanılır.
    BLINK_EVENT = pg.USEREVENT + 1   # Göz kırpma olayı

    # Rastgele 1-2 saniyede bir BLINK_EVENT'i tetiklemesi için zamanlayıcı kurulur.
    pg.time.set_timer(BLINK_EVENT, randint(1000, 2000))

    # Oyun başlangıcında kısa bir bekleme.
    sleep(0.05)
    # Başlangıç ses efektini çalar.

    # --- Ana Oyun Döngüsü ---
    # `game_over` True olana kadar sürekli çalışır.
    while not game_over:
        # Pygame tarafından algılanan tüm olayları (klavye, fare, vb.) işler.
        for event in pg.event.get():
            # Eğer kullanıcı pencereyi kapatırsa:
            if event.type == pg.QUIT:
                pg.quit() # Pygame'i durdurur.
                sys.exit() # Programı kapatır.

            # Eğer bir tuşa basıldıysa:
            if event.type == pg.KEYDOWN:
                new_move = None
                if event.key == pg.K_UP: new_move = (0, -1)
                elif event.key == pg.K_DOWN: new_move = (0, 1)
                elif event.key == pg.K_LEFT: new_move = (-1, 0)
                elif event.key == pg.K_RIGHT: new_move = (1, 0)
                
                # Eğer bir yön tuşuna basıldıysa ve hareket kuyruğu dolu değilse:
                if new_move and len(move_queue) < MAX_MOVE_QUEUE:
                    # Kuyruktaki son hareketin tersi bir hareketi engelle.
                    last_move_in_queue = move_queue[-1] if move_queue else snake.direction[0]
                    if new_move[0] * -1 != last_move_in_queue[0] or new_move[1] * -1 != last_move_in_queue[1]:
                         move_queue.append(new_move)

            # Göz kırpma zamanlayıcısı tetiklendiğinde:
            if event.type == BLINK_EVENT:
                if not snake.emotion: # Eğer yılan başka bir animasyonda değilse
                    snake.emotion = "blink"
                    snake.event_start_time = pg.time.get_ticks() # Animasyon zamanlayıcısını başlat

            # Ses efekti zamanlayıcısı tetiklendiğinde ve yılan "see" modundaysa:

        # --- Oyun Mantığı ---
        snake_move_counter += 1
        # Yılanın hareket etme zamanı geldiyse (belirlenen çerçeve sayısına ulaşıldıysa):
        if snake_move_counter >= FRAMES_PER_MOVE:
            snake_move_counter = 0 # Sayacı sıfırla.

            # Eğer hareket kuyruğunda bekleyen bir hamle varsa, onu kullan.
            if move_queue:
                next_direction = move_queue.pop(0) # Kuyruktaki ilk hamleyi al.
                snake.change_direction(next_direction)
            
            # Yılanı bir adım hareket ettir. Eğer hareket başarısız olursa (çarpma), oyunu bitir.
            if not snake.front_fonction():
                # Çarpma anında hemen değil, kısa bir gecikmeyle oyunu bitirir.
                if not hasattr(snake, 'dead_counter'):
                    snake.emotion = "dead"
                    snake.dead_counter = pg.time.get_ticks()
                if pg.time.get_ticks() - snake.dead_counter >= 100:
                    game_over = True
            elif hasattr(snake, 'dead_counter'): 
                del snake.dead_counter # Eğer çarpma durumu düzelirse sayacı sil.

            elif snake.emotion == "dead":
                snake.emotion = None

        # Yılanın başı yemin pozisyonuna ulaştıysa (yemi yediyse):
        if snake.body_grid[0] == food.position:
            SCORE += 1 # Skoru artır.
            snake.grow() # Yılanın büyümesini tetikle.
            food.ramdomize_position(snake.body_grid) # Yemi yeni bir yere koy.

        else:
            # Yemi yememişse, yemin yakında olup olmadığını kontrol et.
            TRESHOLD = 3 # Yakınlık eşiği (kare cinsinden).
            close_to_food = False
            # Yılanın başının etrafındaki bir alanı kontrol eder.
            for i in range(-1 * TRESHOLD, TRESHOLD + 1, 1):
                if food.position[0] + i == snake.body_grid[0][0]:
                    for j in range(-1 * TRESHOLD, TRESHOLD + 1, 1):
                        if food.position[1] + j == snake.body_grid[0][1]:
                            if snake.emotion != "eat" and snake.emotion != "dead": snake.emotion = "see" # "see" animasyonunu tetikle.
                            close_to_food = True
                            break
            # Eğer yem artık yakın değilse ve yılan "see" modundaysa, durumu sıfırla.
            if not close_to_food and snake.emotion == "see": snake.emotion = None
        
        # --- Çizim İşlemleri ---
        screen.fill(BLACK) # Ekranı temizle (genelde arka plan resmi bunu kapattığı için görünmez).
        screen.blit(graphics["background"], (0, 0)) # Arka planı çiz.
        draw_grid(screen) # Izgarayı çiz.

        snake.animate() # Yılanın akıcı hareket animasyonunu hesapla.
        snake.draw(screen) # Yılanı ekrana çiz.
        food.draw(screen) # Yemi ekrana çiz.

        # Skoru ekrana yazdır.
        screen.blit(text_font.render(f"Score: {SCORE}", True, (149, 197, 111)), (10, 10))

        # Ekranda yapılan tüm çizimleri görünür hale getir.
        pg.display.flip()
        # Oyunun saniyede 60 çerçeve (FPS) ile çalışmasını sağlar.
        clock.tick(60)

    # --- Oyun Bitti Döngüsü ---
    # `game_over` True olduğunda bu döngü başlar.
    dead_start_time = pg.time.get_ticks()
    dead_screen = screen.copy() # Oyunun son anının ekran görüntüsünü alır.
    animate_speed = randint(400, 600)

    play_note(note_order, "DEAD")
    # 3 saniye boyunca oyun sonu ekranını gösterir.
    while pg.time.get_ticks() - dead_start_time < 3000:
        dead_index = (pg.time.get_ticks() // animate_speed) % len(graphics["snake_dead"])
        screen.blit(dead_screen, (0, 0)) # Arka plana son anı çizer.
        # Üzerine oyun sonu animasyonunu çizer.
        screen.blit(pg.transform.scale(graphics["snake_dead"][dead_index], (SCREEN_WIDTH, SCREEN_HEIGHT)), graphics["snake_dead"][dead_index].get_rect(topleft=(0, 0)))
        
        pg.display.flip()
        clock.tick(60)

    # Pygame modüllerini durdurur.
    pg.quit()
    sys.exit()
    # Programdan tamamen çıkar.

# Bu standart Python kontrolü, script'in doğrudan çalıştırıldığında `main()` fonksiyonunu çağırmasını sağlar.
# Eğer bu script başka bir script tarafından import edilirse, `main()` otomatik olarak çalışmaz.
if __name__ == "__main__":
    main()