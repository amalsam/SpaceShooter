
from __future__ import division
import pygame
import random
from os import path
import pickle


## assets folder
img_dir = path.join(path.dirname(__file__), 'assets')
sound_folder = path.join(path.dirname(__file__), 'sounds')

###############################
## to be placed in "constant.py" later 
#WIDTH = 800
#HEIGHT = 600
FPS = 60
POWERUP_TIME = 5000
BAR_LENGTH = 100
BAR_HEIGHT = 10

# Define Colors 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
###############################
global all_sprites


###############################
## to placed in "__init__.py" later
## initialize pygame and create window
pygame.init()
display_info = pygame.display.Info()
WIDTH = display_info.current_w
HEIGHT = display_info.current_h
pygame.mixer.init()  ## For sound
screen = pygame.display.set_mode((WIDTH, HEIGHT),pygame.FULLSCREEN)
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()     ## For syncing the FPS
###############################
all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()



font_name = pygame.font.match_font('arial')

def main_menu():
    global screen

    menu_song = pygame.mixer.music.load(path.join(sound_folder, "adam.mp3"))
    pygame.mixer.music.play(-1)

    title = pygame.image.load(path.join(img_dir, "marvel1.PNG")).convert()
    title = pygame.transform.scale(title, (WIDTH, HEIGHT), screen)

    screen.blit(title, (0,0))
    pygame.display.update()
    h=highscore()

    while True:
        ev = pygame.event.poll()
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RETURN:
                break
            elif ev.key == pygame.K_q:
                pygame.quit()
                quit()
            elif ev.type == pygame.QUIT:
                pygame.quit()
                quit() 
        else:
            screen.blit(title, (0,0))
            draw_text(screen, "Press [ENTER] To Begin", 30, WIDTH/2, HEIGHT/2)
            draw_text(screen, "or [Q] To Quit", 30, WIDTH/2, (HEIGHT/2)+40)
           
            draw_text(screen, "high score:", 30, WIDTH/2-50, (HEIGHT/2)+80)
            draw_text(screen, str(h), 30, WIDTH/2+50, (HEIGHT/2)+80)
            
            pygame.display.update()

    #pygame.mixer.music.stop()
    ready = pygame.mixer.Sound(path.join(sound_folder,'getready.ogg'))
    ready.play()
    screen.fill(BLACK)
    draw_text(screen, "GET READY!", 40, WIDTH/2, HEIGHT/2)
    pygame.display.update()
    

def highscore():
    try:
        with open("highscore.txt", "rb") as file:
            high_score = pickle.load(file)
            return high_score
            #print("High Score:", high_score)
            #draw_text(screen, "High Score:", 30, WIDTH/2-50, HEIGHT/2)
            #draw_text(screen, str(high_score), 30, WIDTH/2+50, HEIGHT/2)
            #draw_text(screen, "Press [M] To Main Menu", 30, WIDTH/2, HEIGHT/2+40)
            #pygame.display.update()
            #ev = pygame.event.poll()
            #if ev.type == pygame.KEYDOWN:
                #if ev.key == pygame.K_m:
                    #main()
                        
    except FileNotFoundError:
        print("No high score found.")
    

def draw_text(surf, text, size, x, y):
    ## selecting a cross platform font to display the score
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)       ## True denotes the font to be anti-aliased 
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def draw_shield_bar(surf, x, y, pct):
    # if pct < 0:
    #     pct = 0
    pct = max(pct, 0) 
    ## moving them to top
    # BAR_LENGTH = 100
    # BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


# def draw_lives(surf, x, y, lives, img):
#     for i in range(lives):
#         img_rect= img.get_rect()
#         img_rect.x = x + 30 * i
#         img_rect.y = y
#         surf.blit(img, img_rect)



def newmob():
    mob_element = Mob()
    all_sprites.add(mob_element)
    mobs.add(mob_element)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0 
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        ## scale the player img down
        self.image = pygame.transform.scale(player_img, (100, 100))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0 
        self.shield = 100
        self.shoot_delay = 800
        self.last_shot = pygame.time.get_ticks()
        # self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_timer = pygame.time.get_ticks()

    def update(self):
        ## time out for powerups
        if self.power >=2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

        ## unhide 
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 30

        self.speedx = 0               ## makes the player static in the screen by default. 
        # then we have to check whether there is an event hanlding being done for the arrow keys being 
        ## pressed 

        ## will give back a list of the keys which happen to be pressed down at that moment
        # keystate = pygame.key.get_pressed()     
        # if keystate[pygame.K_LEFT]:
        #     self.speedx = -5
        # elif keystate[pygame.K_RIGHT]:
        #     self.speedx = 5
        # elif keystate[pygame.K_UP]:
        #     self.speedy = 5
        # elif keystate[pygame.K_DOWN]:
        #     self.speedy = -5

        # #Fire weapons by holding spacebar
        # if keystate[pygame.K_SPACE]:
        #     self.shoot()

        ## check for the borders at the left and right
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.centerx < 0:
            self.rect.centerx = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

        self.rect.x += self.speedx

    def shoot(self):
        ## to tell the bullet where to spawn
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shooting_sound.play()
            if self.power == 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shooting_sound.play()

            """ MOAR POWAH """
            if self.power >= 3:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                missile1 = Missile(self.rect.centerx, self.rect.top) # Missile shoots from center of ship
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                all_sprites.add(missile1)
                bullets.add(bullet1)
                bullets.add(bullet2)
                bullets.add(missile1)
                shooting_sound.play()
                missile_sound.play()

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    # def hide(self):
    #     self.hidden = True
    #     self.hide_timer = pygame.time.get_ticks()
    #     self.rect.center = (WIDTH / 2, HEIGHT + 200)


# defines the enemies
class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width *.90 / 2)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-150, -100)
        self.speedy = random.randrange(5, 20)        ## for randomizing the speed of the Mob

        ## randomize the movements a little more 
        self.speedx = random.randrange(-3, 3)

        ## adding rotation to the mob element
        self.rotation = 0
        self.rotation_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()  ## time when the rotation has to happen
        
    def rotate(self):
        time_now = pygame.time.get_ticks()
        if time_now - self.last_update > 50: # in milliseconds
            self.last_update = time_now
            self.rotation = (self.rotation + self.rotation_speed) % 360 
            new_image = pygame.transform.rotate(self.image_orig, self.rotation)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        ## now what if the mob element goes out of the screen

        if (self.rect.top > HEIGHT + 10) or (self.rect.left < -25) or (self.rect.right > WIDTH + 20):
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)        ## for randomizing the speed of the Mob

## defines the sprite for Powerups
class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        ## place the bullet according to the current position of the player
        self.rect.center = center
        self.speedy = 2

    def update(self):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        ## kill the sprite after it moves over the top border
        if self.rect.top > HEIGHT:
            self.kill()

            

## defines the sprite for bullets
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        ## place the bullet according to the current position of the player
        self.rect.bottom = y 
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        ## kill the sprite after it moves over the top border
        if self.rect.bottom < 0:
            self.kill()

        ## now we need a way to shoot
        ## lets bind it to "spacebar".
        ## adding an event for it in Game loop

## FIRE  MISSILES
class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = missile_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10

    def update(self):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


###################################################
## Load all game images

background = pygame.image.load(path.join(img_dir, 'space-1.png')).convert()
background_rect = background.get_rect()
background11 = pygame.transform.scale(background, (WIDTH, HEIGHT), screen)

## ^^ draw this rect first 

player_img = pygame.image.load(path.join(img_dir, 'player_ship.png')).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(path.join(img_dir, 'laserRed16.png')).convert()
missile_img = pygame.image.load(path.join(img_dir, 'missile.png')).convert_alpha()
# meteor_img = pygame.image.load(path.join(img_dir, 'meteorBrown_med1.png')).convert()
meteor_images = []
meteor_list = [
    'meteor.png',
    'meteor0.png', 
    'meteor1.png', 
    # 'meteor3.png',
    # 'meteor3.png',
    # 'meteor3.png',
    # 'meteor3.png'
]

for image in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, image)).convert())

## meteor explosion
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    ## resize the explosion
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)

    ## player explosion
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)

## load power ups
powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'shield_gold.png')).convert()
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'bolt_gold.png')).convert()


###################################################


###################################################
### Load all game sounds
shooting_sound = pygame.mixer.Sound(path.join(sound_folder, 'pew.wav'))
missile_sound = pygame.mixer.Sound(path.join(sound_folder, 'rocket.ogg'))
expl_sounds = []
for sound in ['expl3.wav', 'expl6.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(sound_folder, sound)))
## main background music
#pygame.mixer.music.load(path.join(sound_folder, 'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
pygame.mixer.music.set_volume(0.2)      ## simmered the sound down a little

player_die_sound = pygame.mixer.Sound(path.join(sound_folder, 'rumble1.ogg'))
###################################################
global gen
gen=0
#############################
## Game loop
def eval_genomes(genomes,config):
    for i in all_sprites:
        i.kill()
    players=[]
    nets=[]
    ge=[]
    running = True
    menu_display = True
    global gen
    gen+=1

    for genome_id, genome in genomes:
                genome.fitness = 0  # start with fitness level of 0
                net = neat.nn.FeedForwardNetwork.create(genome, config)
                nets.append(net)
                player=Player()
                players.append(player)
                all_sprites.add(player)
                ge.append(genome)
    try:
        with open("highscore.txt", "rb") as file:
            high_score = pickle.load(file)
    except FileNotFoundError:
    # If the file doesn't exist, set the high score to 0
        high_score = 0
    while running and len(players)>0:
        all_sprites.update()
        if menu_display:  
        #Play the gameplay music
            # pygame.mixer.music.load(path.join(sound_folder, 'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
            # pygame.mixer.music.play(-1)     ## makes the gameplay sound in an endless loop
        
            menu_display = False
        
        ## 
            

           

        ## spawn a group of mob
            
            for i in range(13):      ## 8 mobs
            # mob_element = Mob()
            # all_sprites.add(mob_element)
            # mobs.add(mob_element)
                newmob()

        ## group for bullets
            

        #### Score board variable
            score = 0
        
    #1 Process input/events
        clock.tick(FPS)
        ## will make the loop run at the same speed all the time
        for event in pygame.event.get():        # gets all the events which have occured till now and keeps tab of them.
        ## listening for the the X button at the top
            if event.type == pygame.QUIT:
                running = False

        ## Press ESC to exit game
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    quit()
        # ## event for shooting the bullets
        # elif event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_SPACE:
        #         player.shoot()      ## we have to define the shoot()  function

    #2 Update
        for x,player in enumerate(players):
            ge[x].fitness+=(abs(player.rect.centery-HEIGHT))/10000
            if player.rect.centery<(HEIGHT/2):
                ge[x].fitness-=0.5
                player.rect.centery=(HEIGHT/2)-1


            testx,testy=0,0
            for mob in mobs:
                # pathxs=[]
                # pathys=[]
                # pathx=mob.rect.x
                # pathy=mob.rect.y
                # for i in range(0,30):
                #     pathx+=mob.speedx
                #     pathx+=mob.speedy
                #     pathxs.append(pathx)
                #     pathys.append(pathy)

                # for ii in pathxs:
                #     if player.rect.centerx - 5 <= ii <= player.rect.centerx + 5:
                #         testx=1
                # for ii in pathys:
                #     if player.rect.centery - 5 <= ii <= player.rect.centery + 5:
                #         testy=1

                
                # output =nets[x].activate((testx,testy,player.rect.centerx))
                output =nets[x].activate((mob.rect.x,mob.rect.y,mob.speedx,mob.speedy,player.rect.centerx))

                # print(output,testx,testy,player.rect.centerx)
                # print(output)
                if output[1]>0.5:
                    player.shoot()

                if output[2]>0.5:
                    ge[x].fitness+=.1
                    player.rect.centery+=1
                else:
                    ge[x].fitness+=.2
                    player.rect.centery-=1
                if output[0]>0.5:
                    if player.rect.centerx>WIDTH-74:
                        ge[x].fitness-=.5
                       
                    else:
                        player.rect.centerx+=1
                        ge[x].fitness-=.2                         
                else:
                    if player.rect.centerx<74:
                        ge[x].fitness-=.5                     
        
                    else:
                        ge[x].fitness+=.2                     
        
                        player.rect.centerx-=1
                
                


        


    ## check if a bullet hit a mob
    ## now we have a group of bullets and a group of mob
        hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    ## now as we delete the mob element when we hit one with a bullet, we need to respawn them again
    ## as there will be no mob_elements left out 
        for hit in hits:
            score += 50 - hit.radius         ## give different scores for hitting big and small metoers
            random.choice(expl_sounds).play()
        # m = Mob()
        # all_sprites.add(m)
        # mobs.add(m)
            expl = Explosion(hit.rect.center, 'lg')
            all_sprites.add(expl)
            if random.random() > 0.9:
                pow = Pow(hit.rect.center)
                all_sprites.add(pow)
                powerups.add(pow)
            newmob()        ## spawn a new mob

    ## ^^ the above loop will create the amount of mob objects which were killed spawn again
    #########################

    ## check if the player collides with the mob
        for x,player in enumerate(players):
            if player.rect.centerx>WIDTH-75 or player.rect.centerx<76 or player.rect.centery>HEIGHT-15 or player.rect.centery<0 :
                death_explosion = Explosion(player.rect.center, 'player')
                all_sprites.add(death_explosion)
                ge[x].fitness-=1                     
                players.pop(x)
                for u in all_sprites:
                    if u==player: 
                        u.kill()
                nets.pop(x)
                ge.pop(x)
        for x,player in enumerate(players):
            hits = pygame.sprite.spritecollide(player, mobs,False, pygame.sprite.collide_circle)        ## gives back a list, True makes the mob element disappear
            for hit in hits:
                ge[x].fitness-=1
                death_explosion = Explosion(player.rect.center, 'player')
                all_sprites.add(death_explosion)
                players.pop(x)
                for u in all_sprites:
                    if u==player:
                        
                        u.kill()
               
                nets.pop(x)
                ge.pop(x)
                player.shield = 0
                expl = Explosion(hit.rect.center, 'sm')
                all_sprites.add(expl)
                
                # if player.shield <= 0: 
                #     player_die_sound.play()
                #     death_explosion = Explosion(player.rect.center, 'player')
                #     all_sprites.add(death_explosion)
                # running = False     ## GAME OVER 3:D
                    # player.hide()
                    # player.lives -= 1
                    # player.shield = 100

    ## if the player hit a power up
            # hits = pygame.sprite.spritecollide(player, powerups, True)
            # for hit in hits:
            #     if hit.type == 'shield':
            #         player.shield += random.randrange(10, 30)
            #         if player.shield >= 100:
            #             player.shield = 100
            #     if hit.type == 'gun':
            #         player.powerup()

        ## if player died and the explosion has finished, end game
            # if player.lives == 0 and not death_explosion.alive():
                
                
                # running = False
        # menu_display = True
        pygame.display.update()
        
       
    #3 Draw/render
        screen.fill(BLACK)
    ## draw the stargaze.png image
        screen.blit(background,background_rect)

        all_sprites.draw(screen)
        draw_text(screen, str(score), 18, WIDTH / 2, 10)## 10px down from the screen
        if score > high_score:
            high_score = score
        draw_text(screen, "high score:", 18, WIDTH / 4, 10)
        draw_text(screen, str(high_score), 18, WIDTH / 3, 10)
        draw_text(screen, "GENERATION:", 30, WIDTH / 2, HEIGHT/2)
        draw_text(screen, str(gen), 30, (WIDTH / 2)+150, HEIGHT/2)

        draw_text(screen, "Neural networks left:", 25, WIDTH / 2, (HEIGHT/2)+40)
        draw_text(screen, str(len(players)), 25, (WIDTH / 2)+150, (HEIGHT/2)+40)
        # draw_shield_bar(screen, 5, 5, player.shield)

    # Draw lives
        # draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)

    ## Done after drawing everything to the screen
        pygame.display.flip()
    with open("highscore.txt", "wb") as file:
        pickle.dump(high_score, file)
    
# main(genomes,config)




import neat

def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    

    p=neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    
    stats= neat.StatisticsReporter()
    p.add_reporter(stats)
    
    winner = p.run(eval_genomes, 10)
    with open("best_genome.pkl", "wb") as file:
        pickle.dump(winner, file)

    print('\nBest genome:\n{!s}'.format(winner))
import os
if __name__=="__main__":
    loc_dir=os.path.dirname(__file__)
    config_path=os.path.join(loc_dir,"config-feedforward.txt")
    run(config_path)

