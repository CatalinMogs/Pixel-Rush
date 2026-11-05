import pygame
from sys import exit
from random import randint, choice
import os
import sys

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.player_walk_1 = pygame.image.load(resource_path('graphics/Player/player_walk_1.png')).convert_alpha()
        self.player_walk_2 = pygame.image.load(resource_path('graphics/Player/player_walk_2.png')).convert_alpha()
        self.player_walk = [self.player_walk_1, self.player_walk_2]
        self.player_index = 0
        self.player_jump = pygame.image.load(resource_path('graphics/Player/jump.png')).convert_alpha()

        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom = (80, 300))
        self.gravity = 0

        self.jump_sound = pygame.mixer.Sound(resource_path('audio/jump.mp3'))
        self.jump_sound.set_volume(0.5)

    def player_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and self.rect.bottom >= 300:
            self.gravity = -20
            self.jump_sound.play()

    def apply_gravity(self):
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 300:
            self.rect.bottom = 300

    def animation_state(self):
        if self.rect.bottom < 300:
            self.image = self.player_jump
        else:
            self.player_index += 0.1
            if self.player_index >= len(self.player_walk):self.player_index = 0
            self.image = self.player_walk[int(self.player_index)]

    def update(self):
        self.player_input()
        self.apply_gravity()
        self.animation_state()

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()

        if type == 'fly':
            fly_1 = pygame.image.load(resource_path('graphics/Fly/Fly1.png')).convert_alpha()
            fly_2 = pygame.image.load(resource_path('graphics/Fly/Fly2.png')).convert_alpha()
            self.frames = [fly_1, fly_2]
            y_pos = 210
        else:
            snail_1 = pygame.image.load(resource_path('graphics/Snail/snail1.png')).convert_alpha()
            snail_2 = pygame.image.load(resource_path('graphics/Snail/snail2.png')).convert_alpha()
            self.frames = [snail_1, snail_2]
            y_pos = 300

        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(midbottom = (randint(900, 1100), y_pos))

    def animation_state(self):
        self.animation_index += 0.1
        if self.animation_index >= len(self.frames): self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def update(self):
        self.animation_state()
        self.rect.x -= 6
        self.destroy()

    def destroy(self):
        if self.rect.x <= -100:
            self.kill()

class Coin(pygame.sprite.Sprite):
    def __init__(self, y_pos, x_pos = None):
        super().__init__()

        self.image = pygame.image.load(resource_path('graphics/coin.png')).convert_alpha()

        if x_pos is None:
            x_pos = randint(850, 1100)

        self.rect = self.image.get_rect(midbottom = (x_pos, y_pos))

    def update(self):
        self.rect.x -= 6

        if self.rect.x <= -100:
            self.kill()

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)

def high_score_path():
    app_data = os.getenv('LOCALAPPDATA') or os.path.expanduser('~')
    save_folder = os.path.join(app_data, 'PixelRush')
    os.makedirs(save_folder, exist_ok = True)

    return os.path.join(save_folder, 'high_score.txt')

def display_score():
    current_time = int(pygame.time.get_ticks() / 1000) - start_time
    score_surf = test_font.render(f'Score: {current_time}', False, (64, 64, 64))
    score_rect = score_surf.get_rect(center = (400, 50))
    screen.blit(score_surf, score_rect)
    return current_time

def coins_collected():
    coin_surf = test_font.render(
        f'Coins: {coin_count}',
        False,
        (255, 215, 0)
    )

    coin_rect = coin_surf.get_rect(topright = (780, 10))
    screen.blit(coin_surf, coin_rect)

def obstacle_movement(obstacle_list):
    if obstacle_list:
        for obstacle_rect in obstacle_list:
            obstacle_rect.x -= 5

            if obstacle_rect.bottom == 300:
                screen.blit(snail_surf, obstacle_rect)
            else:
                screen.blit(fly_surf, obstacle_rect)

        obstacle_list = [obstacle for obstacle in obstacle_list if obstacle.x > -100]

        return obstacle_list
    else: return []

def collisions(player, obstacles):
    if obstacles:
        for obstacle_rect in obstacles:
            if player.colliderect(obstacle_rect): return False
    return True

def collision_sprite():
    if pygame.sprite.spritecollide(player.sprite, obstacle_group, False):
        obstacle_group.empty()
        coin_group.empty()
        return False
    else:
        return True

def player_animation():
    global player_surf, player_index

    if player_rect.bottom < 300:
        player_surf = player_jump
    else:
        player_index += 0.1
        if player_index >= len(player_walk):player_index = 0
        player_surf = player_walk[int(player_index)]

def spawn_coin():
    y_pos = choice([200, 300])

    new_coin = Coin(y_pos)

    keep_distance(new_coin, obstacle_group)

    coin_group.add(new_coin)

def keep_distance(sprite, group, distance = 180):
    while True:
        conflict = None

        for other in group:
            too_close = (
                sprite.rect.left < other.rect.right + distance
                and sprite.rect.right > other.rect.left - distance
            )

            if too_close:
                conflict = other
                break

        if conflict is None:
            break

        sprite.rect.left = conflict.rect.right + distance

def spawn_obstacle():
    new_obstacle = Obstacle(choice(['fly', 'snail', 'snail', 'snail']))

    keep_distance(new_obstacle, coin_group)

    obstacle_group.add(new_obstacle)

def load_high_score():
    try:
        with open(high_score_path(), 'r') as file:
            return int(file.read())
    except (FileNotFoundError, ValueError):
        return 0
    
def save_high_score(score):
    with open(high_score_path(), 'w') as file:
        file.write(str(score))

pygame.init()
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption('Pixel Rush')
clock = pygame.time.Clock()
test_font = pygame.font.Font(resource_path('font/Pixeltype.ttf'), 50)
game_active = False
start_time = 0
score = 0
coin_count = 0
high_score = 0
bg_music = pygame.mixer.Sound(resource_path('audio/music.wav'))
bg_music.play(loops = -1)

# Groups
player = pygame.sprite.GroupSingle() 
player.add(Player())

obstacle_group = pygame.sprite.Group()

coin_group = pygame.sprite.Group()

sky_surface = pygame.image.load(resource_path('graphics/Sky.png')).convert()
ground_surface = pygame.image.load(resource_path('graphics/ground.png')).convert()

# Coin
coin = pygame.image.load(resource_path('graphics/coin.png')).convert_alpha()

# Snail
snail_frame_1 = pygame.image.load(resource_path('graphics/Snail/snail1.png')).convert_alpha()
snail_frame_2 = pygame.image.load(resource_path('graphics/Snail/snail2.png')).convert_alpha()
snail_frames = [snail_frame_1, snail_frame_2]
snail_frame_index = 0
snail_surf = snail_frames[snail_frame_index]

# Fly
fly_frame_1 = pygame.image.load(resource_path('graphics/Fly/Fly1.png')).convert_alpha()
fly_frame_2 = pygame.image.load(resource_path('graphics/Fly/Fly2.png')).convert_alpha()
fly_frames = [fly_frame_1, fly_frame_2]
fly_frame_index = 0
fly_surf = fly_frames[fly_frame_index]

obstacle_rect_list = []

player_walk_1 = pygame.image.load(resource_path('graphics/Player/player_walk_1.png')).convert_alpha()
player_walk_2 = pygame.image.load(resource_path('graphics/Player/player_walk_2.png')).convert_alpha()
player_walk = [player_walk_1, player_walk_2]
player_index = 0
player_jump = pygame.image.load(resource_path('graphics/Player/jump.png')).convert_alpha()

player_surf = player_walk[player_index]
player_rect = player_surf.get_rect(midbottom = (80, 300))
player_gravity = 0

# Intro screen
player_stand = pygame.image.load(resource_path('graphics/Player/player_stand.png')).convert_alpha()
player_stand = pygame.transform.rotozoom(player_stand, 0, 2)
player_stand_rect = player_stand.get_rect(center = (400, 200))

game_name = test_font.render('Pixel Rush', False, (111, 196, 169))
game_name_rect = game_name.get_rect(center = (400, 80))

game_message = test_font.render('Press Space to run', False, (111, 196, 169))
game_message_rect = game_message.get_rect(center = (400, 340))

# Timer
obstacle_timer = pygame.USEREVENT + 1
pygame.time.set_timer(obstacle_timer, 1500)

snail_animation_timer = pygame.USEREVENT + 2
pygame.time.set_timer(snail_animation_timer, 500)

fly_animation_timer = pygame.USEREVENT + 3
pygame.time.set_timer(fly_animation_timer, 200)

coin_timer = pygame.USEREVENT + 4
pygame.time.set_timer(coin_timer, 2000)

high_score = load_high_score()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        if not game_active:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                game_active = True
                start_time = int(pygame.time.get_ticks() / 1000)
                coin_count = 0

                obstacle_group.empty()
                coin_group.empty()

        if game_active:
            if event.type == obstacle_timer:
                spawn_obstacle()

            if event.type == snail_animation_timer:
                if snail_frame_index == 0:
                    snail_frame_index = 1
                else:
                    snail_frame_index = 0
                snail_surf = snail_frames[snail_frame_index]

            if event.type == fly_animation_timer:
                if fly_frame_index == 0:
                    fly_frame_index = 1
                else:
                    fly_frame_index = 0
                fly_surf = fly_frames[fly_frame_index]

            if event.type == coin_timer:
                spawn_coin()

    if game_active:    
        screen.blit(sky_surface, (0, 0))
        screen.blit(ground_surface, (0, 300))

        score = display_score()

        coins = coins_collected()

        # Player
        player.draw(screen)
        player.update()

        obstacle_group.draw(screen)
        obstacle_group.update()

        coin_group.draw(screen)
        coin_group.update()

        collected_coins = pygame.sprite.spritecollide(
            player.sprite,
            coin_group,
            True
        )

        coin_count += len(collected_coins)

        # collision
        game_active = collision_sprite()

        if not game_active and score > high_score:
            high_score = score
            save_high_score(high_score)

    else:
        screen.fill((94, 129, 162))
        screen.blit(player_stand, player_stand_rect)

        obstacle_rect_list.clear()
        player.sprite.rect.midbottom = (80, 300)
        player.sprite.gravity = 0

        score_message = test_font.render(f'Your score: {score}', False, (111, 196, 169))
        score_message_rect = score_message.get_rect(center = (400, 300))

        high_score_message = test_font.render(
            f'High Score: {high_score}',
            False,
            (255, 215, 0)
        )

        high_score_rect = high_score_message.get_rect(center = (400, 380))
        screen.blit(high_score_message, high_score_rect)

        screen.blit(game_name, game_name_rect)

        if score == 0:
            screen.blit(game_message, game_message_rect)
        else:
            screen.blit(score_message, score_message_rect)

    pygame.display.update()
    clock.tick(60)