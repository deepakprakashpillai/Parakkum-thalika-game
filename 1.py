#                                    GAME 1
# IMPORTING FILES
import pygame
import os
import random
import time

# initializations
pygame.init()
pygame.mixer.init()

# Predefining colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Power Ups
POWERUP_TIME = 5000


# Setting up directories
game_folder = os.path.dirname(__file__)
image_folder = os.path.join(game_folder, "img")
sound_folder = os.path.join(game_folder, "sound")

# Initialising screen
WIDTH = 600
HEIGHT = 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Game 1")

# Loading images--------------------------------------------------------------------------------------------------------
background = pygame.image.load(os.path.join(image_folder, 'bg1.png')).convert()
backgroundrect = background.get_rect()
player_img = pygame.image.load(os.path.join(image_folder, 'playership1.png')).convert()
player_life_icon = pygame.transform.scale(player_img, (25, 20))
player_life_icon.set_colorkey(BLACK)
laser_img = pygame.image.load(os.path.join(image_folder, 'laserred.png')).convert()
meteor_img = []
# meteor list
meteor_list = ['meteorbig1.png', 'meteorbig2.png', 'meteormed1.png', 'meteormed2.png',
               'meteorsmall1.png', 'meteorsmall2.png']
# Loading meteor images
for meteor in meteor_list:
    meteor_img.append(pygame.image.load(os.path.join(image_folder, meteor)).convert())
# Explosions
explosion_anim = {}
explosion_anim['large'] = []
explosion_anim['small'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(image_folder, filename)).convert()
    small_image = pygame.transform.scale(img, (50, 50))
    large_image = pygame.transform.scale(img, (100, 100))
    explosion_anim['large'].append(large_image)
    explosion_anim['small'].append(small_image)
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(os.path.join(image_folder, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)
# Powerups
powerup_image_level1 = {}
powerup_image_level1['shield'] = pygame.image.load(os.path.join(image_folder, 'shield_silver.png')).convert()
powerup_image_level1['gun'] = pygame.image.load(os.path.join(image_folder, 'bolt_silver.png')).convert()
powerup_image_level1['star'] = pygame.image.load(os.path.join(image_folder, 'star_silver.png')).convert()
powerup_image_level2 = {}
powerup_image_level2['shield'] = pygame.image.load(os.path.join(image_folder, 'shield_gold.png')).convert()
powerup_image_level2['gun'] = pygame.image.load(os.path.join(image_folder, 'bolt_gold.png')).convert()
powerup_image_level2['star'] = pygame.image.load(os.path.join(image_folder, 'star_gold.png')).convert()

# ----------------------------------------------------------------------------------------------------------------------
# Loading Sounds
laser_sound1 = pygame.mixer.Sound(os.path.join(sound_folder, 'laser.ogg'))
explosion_sound = pygame.mixer.Sound(os.path.join(sound_folder, 'explosion1.wav'))
player_explosion_sound = pygame.mixer.Sound(os.path.join(sound_folder, 'explosion2.wav'))
shield_powerup_sound = pygame.mixer.Sound(os.path.join(sound_folder, 'shield.wav'))
gun_powerup_sound = pygame.mixer.Sound(os.path.join(sound_folder, 'gun.wav'))
pygame.mixer.music.load(os.path.join(sound_folder, 'music.mp3'))
pygame.mixer.music.set_volume(0.7)


# Draw Text
def draw_text(surface, text, x, y, size, color):
    font = pygame.font.SysFont('comicsans', size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surface.blit(text_surface, text_rect)

# Draw bar
def draw_bar(surface, value, x, y, length, height, fill_color, outline_color):
    if value < 0:
        value = 0
    percent = (value / 100) * length
    outline_rect = pygame.Rect(x, y, length, height)
    fill_rect = pygame.Rect(x, y, percent, height)
    pygame.draw.rect(surface, fill_color, fill_rect)
    pygame.draw.rect(surface, outline_color, outline_rect, 2 )

# Draw Lives
def draw_lives(surface, x, y, lives, image):
    for i in range(lives):
        image_rect = image.get_rect()
        image_rect.x = x + 30 * i
        image_rect.y = y
        surface.blit(image, image_rect)

# Defining clock and FPS
clock = pygame.time.Clock()
FPS = 60


# class for player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (57, 50))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 10
        self.speed = 0
        self.radius = self.rect.height // 2
        self.score = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.gun_level = 1
        self.gun_level_timer = pygame.time.get_ticks()
        self.rapid_shoot_timer = pygame.time.get_ticks()
        self.rs_mode = False


    def update(self):
        # Set the timing for hide
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 2000:
            self.hidden = False
            self.rect.centerx = WIDTH // 2
            self.rect.bottom = HEIGHT - 10
        # Set the timing for gun powerup
        if self.gun_level >= 2 and pygame.time.get_ticks() - self.gun_level_timer > POWERUP_TIME:
            self.gun_level -= 1
            self.gun_level_timer = pygame.time.get_ticks()
        # Set timing of rapid Fire
        if self.rs_mode and pygame.time.get_ticks() - self.rapid_shoot_timer > POWERUP_TIME:
            self.rs_mode = False
            self.shoot_delay = 250

        self.speed = 0
        press = pygame.key.get_pressed()
        if press[pygame.K_LEFT]:
            self.speed = -5
        if press[pygame.K_RIGHT]:
            self.speed = 5
        self.rect.x += self.speed
        if press[pygame.K_SPACE] and not self.hidden:
            self.shoot()
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            laser_sound1.play()
            if self.gun_level == 1:
                bullet = Bullets(self.rect.centerx, self.rect.bottom)
                all_sprites.add(bullet)
                bullets.add(bullet)
                self.last_shot = now
            if self.gun_level >= 2:
                bullet1 = Bullets(self.rect.left + 3, self.rect.centery - 3)
                all_sprites.add(bullet1)
                bullets.add(bullet1)
                bullet2 = Bullets(self.rect.right, self.rect.centery)
                all_sprites.add(bullet2)
                bullets.add(bullet2)
                self.last_shot = now

    def hide(self):
        self.hide_timer = pygame.time.get_ticks()
        self.hidden = True
        self.rect.center = (WIDTH // 2, HEIGHT + 50)

    def gun_powerup(self):
        self.gun_level_timer = pygame.time.get_ticks()
        self.gun_level += 1
    def rapid_shoot(self):
        self.shoot_delay = 50
        self.rapid_shoot_timer = pygame.time.get_ticks()
        self.rs_mode = True




class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.orig_image = random.choice(meteor_img)
        self.orig_image.set_colorkey(BLACK)
        self.image = self.orig_image.copy()
        self.rect = self.image.get_rect()
        self.rect.left = random.randrange(WIDTH - self.rect.width)
        self.rect.bottom = random.randrange(-400, -200)
        self.speedy = random.randrange(1, 15)
        self.speedx = random.randrange(-4, 4)
        self.radius = self.rect.height // 2
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_img = pygame.transform.rotate(self.orig_image, self.rot)
            old_center = self.rect.center
            self.image = new_img
            self.rect = self.image.get_rect()
            self.rect.center = old_center


    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left > WIDTH + 5 or self.rect.right < -5:
            self.rect.left = random.randrange(WIDTH - self.rect.width)
            self.rect.bottom = random.randrange(-10, 0)
            self.speedy = random.randrange(1, 8)
            self.speedx = random.randrange(-2, 2)


class Bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(laser_img, (10, 40))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speed = -15

    def update(self):
        self.rect.bottom += self.speed
        if self.rect.bottom < 0:
            self.kill()


class PowerUps_level1(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['gun', 'shield', 'star'])
        self.image = powerup_image_level1[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speed = 5

    def update(self):
        self.rect.bottom += self.speed
        if self.rect.x < -5:
            self.kill()

class PowerUps_level2(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['gun', 'shield', 'star'])
        self.image = powerup_image_level2[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speed = 7

    def update(self):
        self.rect.bottom += self.speed
        if self.rect.x < -5:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, size, center):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[size][0]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.refresh_rate = 25
        self.last_update = pygame.time.get_ticks()
        self.frame = 0

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.refresh_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                old_center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.image.set_colorkey(BLACK)
                self.rect = self.image.get_rect()
                self.rect.center = old_center




pygame.mixer.music.play(-1)


def home_screen():
    waiting = True

    screen.blit(background, backgroundrect)
    draw_text(screen, "Game", WIDTH // 2, HEIGHT // 4, 50, WHITE)
    draw_text(screen, "press any key to play", WIDTH // 2, HEIGHT * 3 / 4, 25, WHITE)
    pygame.display.flip()
    time.sleep(3)
    while waiting:
        clock.tick(FPS)
        screen.blit(background, backgroundrect)
        draw_text(screen, "Game", WIDTH // 2, HEIGHT // 4, 50, WHITE)
        draw_text(screen, "press any key to play", WIDTH // 2, HEIGHT * 3 / 4, 25, WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYUP:
                waiting = False
        pygame.display.flip()




# Main Loop
hscreen = True
run = True
while run:
    if hscreen:
        home_screen()
        hscreen = False
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        power_ups_level1 = pygame.sprite.Group()
        power_ups_level2 = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        start_time = pygame.time.get_ticks()
        no_of_mobs = 0
        puloop_count = 0

    # Setting FPS
    clock.tick(FPS)

    # Inputs (EVENTS)
    for event in pygame.event.get():

        # Checking for quit
        if event.type == pygame.QUIT:
            run = False
    # Update
    # Spawning new mobs to increase difficulty
    if no_of_mobs == 0:
        for i in range(12):
            mob = Mob()
            all_sprites.add(mob)
            mobs.add(mob)
            no_of_mobs += 1
    if pygame.time.get_ticks() - start_time > 10000:
        mob = Mob()
        all_sprites.add(mob)
        mobs.add(mob)
        start_time = pygame.time.get_ticks()
    all_sprites.update()


    # Check whether bullet collides with mob
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        expl = Explosion('large', hit.rect.center)
        all_sprites.add(expl)
        explosion_sound.play()
        player.score += ((48 - hit.radius) // 10) + 2
        mob = Mob()
        all_sprites.add(mob)
        mobs.add(mob)
        # Creating powerup level 1
        if 0.4 < random.random() < 0.43:
            powup = PowerUps_level1(hit.rect.center)
            all_sprites.add(powup)
            power_ups_level1.add(powup)
        # Creating powerup level 2
        if puloop_count % 8 == 0 and puloop_count > 0:
            powup = PowerUps_level2(hit.rect.center)
            all_sprites.add(powup)
            power_ups_level2.add(powup)
            puloop_count += 1



    # check whether player collides with mob
    if not player.hidden:
        hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
        for hit in hits:
            expl = Explosion('small', hit.rect.center)
            all_sprites.add(expl)
            mob = Mob()
            all_sprites.add(mob)
            mobs.add(mob)
            player.shield -= hit.radius * 2
            if player.shield <= 0:
                player_explosion_sound.play()
                player_expl = Explosion('player', player.rect.center)
                all_sprites.add(player_expl)
                player.hide()
                player.lives -= 1
                player.shield = 100

    # Check whether player collects powerups
    if not player.hidden:
        hits = pygame.sprite.spritecollide(player, power_ups_level1, True)
        for hit in hits:
            puloop_count += 1
            if hit.type == 'shield':
                shield_powerup_sound.play()
                player.shield += random.randrange(10, 30)
                if player.shield >= 100:
                    player.shield = 100
            if hit.type == 'gun':
                gun_powerup_sound.play()
                player.gun_powerup()
            if hit.type == 'star':
                player.score += 200
        hits = pygame.sprite.spritecollide(player, power_ups_level2, True)
        for hit in hits:
            if hit.type == 'gun':
                player.rapid_shoot()




    # Exit if the player is not alive and Animation has finished
    if player.lives == 0 and not player_expl.alive():
        hscreen = True


    # Render
    screen.fill(BLACK)
    screen.blit(background, backgroundrect)
    all_sprites.draw(screen)
    draw_text(screen, 'Score :' + str(player.score),WIDTH //2, 20, 30, WHITE)
    draw_bar(screen, player.shield, 5, 5, 100, 10, GREEN, WHITE)
    draw_lives(screen, WIDTH - 100, 10, player.lives, player_life_icon)

    # Refresh Screen
    pygame.display.flip()

pygame.quit()
