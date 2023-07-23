#from __future__ import division
import sys
import pygame
import random
from os import path
import sqlite3

## assets folder
img_dir = path.join(path.dirname(__file__), 'assets')
sound_folder = path.join(path.dirname(__file__), 'sounds')
img_meteor = path.join(path.dirname(__file__), 'assets\meteor')
img_ship =  path.join(path.dirname(__file__), 'assets\ships')
###############################
FPS = 60
POWERUP_TIME = 7000
BAR_LENGTH = 150
BAR_HEIGHT = 20
# Define Colors 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
###############################
global all_sprites
global frames,c,ship
global player_img,ship_images,selected
ship_no=1
ship=1
selected_player=1
conn = sqlite3.connect('SpaceShooter.db')   #db for storing scores of players
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS scorestb(id INTEGER PRIMARY KEY AUTOINCREMENT,name text, score integer)''')

###############################
## initialize pygame and create window
pygame.init()
display_info = pygame.display.Info()
WIDTH =display_info.current_w
HEIGHT =display_info.current_h
pygame.mixer.init()  ## For sound
screen = pygame.display.set_mode((WIDTH, HEIGHT),pygame.FULLSCREEN)
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()     ## For syncing the FPS

all_sprites = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()

font_name = pygame.font.match_font('arial')
font = pygame.font.Font(None, 32)

## Load all game image
menu_background = pygame.image.load(path.join(img_dir, 'space-11.png')).convert()
menu_background = pygame.transform.scale(menu_background,(WIDTH,HEIGHT ))
text_background=pygame.image.load(path.join(img_dir, 'spaceshootertext.png'))
background = pygame.image.load(path.join(img_dir, 'space-1.png')).convert()
background_rect = background.get_rect()
img_height=background_rect.height
background = pygame.transform.scale(background,(WIDTH,img_height ))
## ^^ draw this rect first
ship_images=[]
bullet_img=[] 
ship_name = 'player_ship ({}).png'.format(ship)#selecting player ship
for i in range(1,9):
    filename = 'player_ship ({}).png'.format(i)
    ship_arr = pygame.image.load(path.join(img_ship,filename)).convert_alpha()
    ship_arr.set_colorkey(BLACK)
    ## resize the explosion
    ship_scale = pygame.transform.scale(ship_arr, (100, 100))
    ship_images.append(ship_scale)
player_img1 = pygame.image.load(path.join(img_ship,ship_name)).convert()
player_mini_img = pygame.transform.scale(player_img1, (25, 19))
player_mini_img.set_colorkey(BLACK)
for i in range(1,9):
    filename = 'bullet{}.png'.format(i)
    bullet_arr = pygame.image.load(path.join(img_dir,filename)).convert_alpha()
    bullet_img.append(bullet_arr)
missile_img = pygame.image.load(path.join(img_dir, 'missile.png')).convert_alpha()
# meteor_img = pygame.image.load(path.join(img_dir, 'meteorBrown_med1.png')).convert()
meteor_images = []
meteor_list = [
    'meteor.png',
    'meteor0.png', 
    'meteor1.png', 
    #'meteor3.png',
    #'meteor.png',
    'meteor0.png',
    #'meteor3.png'
    'meteorM (2).png',
    'meteorM (3).png',
    'meteorM (4).png',
    'meteorM (6).png',
    'meteorS (1).png',
    'meteorS (2).png', 
]
for image in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_meteor, image)).convert())
## meteor explosion
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'explosion_{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir,filename)).convert()
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
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'blue-laser.png')).convert()
###################################################


###################################################
### Load all game 
shooting_sounds=[]
for sound in ['pew.wav','9mm.mp3','9mm.mp3','plasma.wav','pew.wav','plasma.wav','plasma.wav','plasma.wav',]:
    shooting_sounds.append(pygame.mixer.Sound(path.join(sound_folder,sound)))
missile_sound = pygame.mixer.Sound(path.join(sound_folder, 'rocket.ogg'))
expl_sounds = []
for sound in [ 'expl6.wav','explosion_02.wav','explosion_03.wav','explosion_04.mp3']:
    expl_sounds.append(pygame.mixer.Sound(path.join(sound_folder, sound)))
click_sound=pygame.mixer.Sound(path.join(sound_folder,'click_sound.wav'))
## main background music
#pygame.mixer.music.load(path.join(sound_folder, 'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
pygame.mixer.music.set_volume(0.2)      ## simmered the sound down a little

player_die_sound = pygame.mixer.Sound(path.join(sound_folder, 'HQ_explosion.mp3'))
###################################################
#############################
## Game loop
def main():
    global selected_player
    running = True
    menu_display = True
    p_list=get_player_list()
    scores = get_high_scores() 
    for s in scores:
        high_score = s[1]
        break
    bg_y=-HEIGHT   #for scrolling background
    #high_score=1
    while running:
        if menu_display:  
            main_menu()
            for p in p_list:
                p_name = str(p[1])
                p_id = p[0]
                p_score=p[2]
                try:
                    if str(p[0]) == str(selected_player):
                        break
                except NameError:
                    if str(p[0]) == '1':
                        break
            ready = pygame.mixer.Sound(path.join(sound_folder,'getready.ogg'))
            ready.play()
            screen.fill(BLACK)
            draw_text(screen, "GET READY!", 40, WIDTH/2, HEIGHT/2)
            #pygame.time.wait(1000)
        #Stop menu music
            pygame.mixer.music.stop()
        #Play the gameplay music
            pygame.mixer.music.load(path.join(sound_folder, 'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
            pygame.mixer.music.play(-1)     ## makes the gameplay sound in an endless loop
            menu_display = False 
        ## group all the sprites together for ease of update    
            for i in all_sprites:    #clearing previous game sprites(otherwise when click play again previous game sprites will also include)
                i.kill()
            player = Player()
            all_sprites.add(player)
        ## spawn a group of mob    
            for i in range(10):      ## 10 mobs
            # mob_element = Mob()
            # all_sprites.add(mob_element)
            # mobs.add(mob_element)
                newmob()

        ## group for bullets
          
        #### Score board variable
            score = 0 
        #1 Process input/events
        clock.tick(FPS)     ## will make the loop run at the same speed all the time
        for event in pygame.event.get():        # gets all the events which have occured till now and keeps tab of them.
            ## listening for the the X button at the top
            if event.type == pygame.QUIT:
                running = False

            ## Press ESC to exit game
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    final_score(p_name,score)
                    running = False
        # ## event for shooting the bullets
        # elif event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_SPACE:
        #         player.shoot()      ## we have to define the shoot()  function
        #2 Update
        all_sprites.update()
        ## check if a bullet hit a mob
        ## now we have a group of bullets and a group of mob
        hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    ## now as we delete the mob element when we hit one with a bullet, we need to respawn them again
    ## as there will be no mob_elements left out 
        for hit in hits:
            print (hit.radius)
            score += 100 - hit.radius         ## give different scores for hitting big and small metoers
            random.choice(expl_sounds).play()
        # m = Mob()
        # all_sprites.add(m)
        # mobs.add(m)
            expl = Explosion(hit.rect.center, 'lg')
            all_sprites.add(expl)
            if random.random() > 0.9:  #10% chance
                pow = Pow(hit.rect.center)
                all_sprites.add(pow)
                powerups.add(pow)
            newmob()        ## spawn a new mob
    ## ^^ the above loop will create the amount of mob objects which were killed spawn again
    #########################
    ## check if the player collides with the mob
        hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)        ## gives back a list, True makes the mob element disappear
        for hit in hits:
            print(player.lives)
            player.shield -= hit.radius * 2
            expl = Explosion(hit.rect.center, 'sm')
            all_sprites.add(expl)
            newmob()
            if player.shield <= 0: 
                player_die_sound.play()
                death_explosion = Explosion(player.rect.center, 'player')
                all_sprites.add(death_explosion)
            # running = False     ## GAME OVER 3:D
                player.hide()
                player.lives -= 1
                player.shield = 100

    ## if the player hit a power up
        hits = pygame.sprite.spritecollide(player, powerups, True)
        for hit in hits:
            if hit.type == 'shield':
                player.shield += random.randrange(10, 30)
                if player.shield >= 100:
                    player.shield = 100
            if hit.type == 'gun':
                player.powerup()

    ## if player died and the explosion has finished, end game
        if player.lives == 0 and not death_explosion.alive():
            final_score(p_name,score)
            running = False
        # menu_display = True
        # pygame.display.update()
        bg_y += 1  # Adjust the speed of movement by changing the value
        # If the background image reaches the end, reset its position
        if bg_y > 0:
            bg_y = -HEIGHT
        # Blit the background image onto the screen at the current position
        screen.blit(background, (0, bg_y))
        # Blit the background image again to create the looping effect
        screen.blit(background, ( 0 ,bg_y + HEIGHT))
        #pygame.display.flip()
        all_sprites.draw(screen)
        draw_text(screen, "current score:"+str(score), 18, WIDTH / 2, 10)## 10px down from the screen
        if score > high_score:
            high_score = score
        if score > p_score:
            insert_highscore(p_id,p_name,score)
        
        draw_text(screen, "HIGH SCORE:", 30, WIDTH / 4, 10)
        draw_text(screen, str(high_score), 30, WIDTH / 3, 10)
        draw_text(screen, p_name+"'s Best:"+str(p_score), 30, WIDTH-300, 10)
        draw_shield_bar(screen, 5, 5, player.shield)
        # Draw lives
        draw_lives(screen, WIDTH - 100, 5, player.lives, player_mini_img)
        ## Done after drawing everything to the screen
        pygame.display.update()
    main()
#title = pygame.image.load(path.join(img_dir, "space-1.png")).convert()
#title = pygame.transform.scale(title, (WIDTH, HEIGHT), screen)
def main_menu():
    global screen,selected_player
    pygame.mixer.music.load(path.join(sound_folder, "adam.mp3"))
    pygame.mixer.music.play(-1)
    p_list=get_player_list()
    start_button = Button(300, 250, 200, 100,"START !", WHITE)
    highscore_bn= Button(300, 400, 200, 100,"Highscores",WHITE)
    quit_bn= Button(300, 550, 200, 100,"QUIT", WHITE)
    profile_bn= Button((WIDTH/2)+300, 250, 200, 100,"PLAYERS", WHITE)
    ships_bn=Button((WIDTH/2)+300, 400, 200, 100,"select ship", WHITE)
    while True:
        p_list=get_player_list()
        
        e_v = pygame.event.poll()
        if e_v.type == pygame.KEYDOWN:
            click_sound.play()
            if e_v.key == pygame.K_RETURN:
                break
            elif e_v.key == pygame.K_ESCAPE:
                pygame.quit()
                quit()
            elif e_v.key == pygame.K_h:
                highscore()
            elif e_v.key == pygame.K_i:
                instructions()
            elif e_v.key == pygame.K_s:
                select_ship()
            elif e_v.key == pygame.K_p:
                selected_player=users() 
            elif e_v.type == pygame.QUIT:
                pygame.quit()
                quit()
                 
        elif e_v.type == pygame.MOUSEBUTTONDOWN:
            if start_button.is_clicked(e_v):
                    click_sound.play()
                    break
            elif highscore_bn.is_clicked(e_v):
                    click_sound.play()
                    highscore()
            elif quit_bn.is_clicked(e_v):
                    click_sound.play()
                    #pygame.quit()
                    sys.exit()
                    
            elif profile_bn.is_clicked(e_v):
                    click_sound.play()
                    selected_player=users()
            elif ships_bn.is_clicked(e_v):
                    click_sound.play()
                    select_ship()

        for p in p_list:
            p_name = str(p[1])
            try:
                if str(p[0]) == str(selected_player):
                    break
            except NameError:
                if str(p[0]) == '1':
                    break
        screen.blit(menu_background, (0,0))
        screen.blit(text_background,((WIDTH/2)-230,100))
        start_button.draw()
        highscore_bn.draw()
        quit_bn.draw()
        profile_bn.draw()
        ships_bn.draw()
        draw_text(screen,"PLAYER :"+str(p_name),30,WIDTH-200,30)
        pygame.display.update()
    pygame.mixer.music.stop()
    pygame.display.update()

def users():#dispaly list of players to select
    add_bn= Button(100, HEIGHT-200, 200, 100,"ADD player", GREEN)
    del_bn= Button((WIDTH/2)+500, HEIGHT-200, 200, 100,"Delete a player", RED)
    user_running=True
    while user_running:
            select_bn=[]
           
            screen.fill(BLACK)
            screen.blit(background,(0,0))
            add_bn.draw()
            del_bn.draw()
            scores = get_player_list()
            i=0
            slot=0
            count=len(scores)
            count_button=count
            if count_button >= 7:
                draw_text(screen,"SLOT FULL",30,WIDTH/2,HEIGHT-100)
           # text_surface = font.render( "SELECT PLAYER" , True, (255, 255, 255))
            #screen.blit(text_surface, ((WIDTH / 2) - 50, 10))
            #text_surface = font.render( "SLOT NO :    NAME" , True, (255, 255, 255))
           # screen.blit(text_surface, ((WIDTH / 2) - 50, 50))
            for s in scores:
                
                i += 100
                id=str(s[0])
                name=str(s[1])
                score=str(s[2])
                select_bn.append(Button((WIDTH/2)-100, i, 200, 100,name, WHITE))
                #text_surface = font.render( "PRESS ["+str(slot)+"] TO SELECT PLAYER :      "+ name , True, (255, 255, 255))
                #screen.blit(text_surface, ( 500, 100 + i))
                select_bn[slot].draw()
                slot+=1
                
            #draw_text(screen,"PRESS [ A ] TO NEW PLAYER", 30, 200, HEIGHT-200)  
            #draw_text(screen,"PRESS  [ D ]  TO DELETE A PLAYER", 30, (WIDTH/2)+500, HEIGHT-200)  
            pygame.display.update()
            ev = pygame.event.poll()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if add_bn.is_clicked(ev):
                    click_sound.play()
                    count+=1
                    name=playername()
                    if count_button < 7:
                        add_player(count,name)
                        
                if del_bn.is_clicked(ev):
                    click_sound.play()
                    delete_player_screen()
                for cb in range(0,count_button):
                    if select_bn[cb].is_clicked(ev):
                        return select_player_button(cb)
                         
def select_player_button(id):  #to return player id if the player is selected from user()
    scores = get_player_list()
    try:
        r=scores[id]
        id=r[0]
        return id
    except IndexError:
        return
                     
def delete_player_screen(): #display list of players  to delete
    while True:
            screen.fill(BLACK)
            scores = get_player_list()
            i=0
            slot=0
            text_surface = font.render( "DELETE PLAYER" , True, (255, 255, 255))
            screen.blit(text_surface, ((WIDTH / 2) - 50, 10))
            text_surface = font.render( "SLOT NO :    NAME" , True, (255, 255, 255))
            screen.blit(text_surface, ((WIDTH / 2) - 50, 50))
            for s in scores:
                slot+=1
                i += 50
                id=str(s[0])
                name=str(s[1])
                score=str(s[2])
                text_surface = font.render( "PRESS "+str(slot)+" TO DELETE :      "+ name , True, (255, 255, 255))
                screen.blit(text_surface, ((WIDTH / 2) - 50, 100 + i))
            pygame.display.update()
            ev = pygame.event.poll()
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_RETURN:
                    break   
                if ev.key == pygame.K_ESCAPE:
                    break 
                if ev.key == pygame.K_1:
                    try:
                        r=scores[0]
                        id=r[0]
                        delete_player(id)
                    except IndexError:
                        continue     
                if ev.key == pygame.K_2:
                    try:
                        r=scores[1]
                        id=r[0]
                        delete_player(id)
                    except IndexError:
                        continue
                if ev.key == pygame.K_3:
                    try:
                        r=scores[2]
                        id=r[0]
                        delete_player(id)
                    except IndexError:
                        continue
                if ev.key == pygame.K_4:
                    try:
                        r=scores[3]
                        id=r[0]
                        delete_player(id)
                    except IndexError:
                        continue
                if ev.key == pygame.K_5:
                    try:
                        r=scores[4]
                        id=r[0]
                        delete_player(id)
                    except IndexError:
                        continue
                if ev.key == pygame.K_6:
                    try:
                        r=scores[5]
                        id=r[0]
                        delete_player(id)
                    except IndexError:
                        continue
                if ev.key == pygame.K_7:
                    try:
                        r=scores[6]
                        id=r[0]
                        delete_player(id)
                    except IndexError:
                        continue
                if ev.key == pygame.K_8:
                    try:
                        r=scores[7]
                        id=r[0]
                        delete_player(id)
                    except IndexError:
                        continue
                if ev.key == pygame.K_9:
                    try:
                        r=scores[8]
                        id=r[0]
                        delete_player(id)
                    except IndexError:
                        continue
                    
def playername():#funtion for insert name
    name = ""
    is_entering_name = True
    while is_entering_name:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return name
                    #is_entering_name = False  # Exit name input loop
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]  # Remove last character from the name
                else:
                    name += event.unicode  # Add typed character to the name

        screen.fill(BLACK)  # Clear the screen
        text_surface = font.render("Enter your name: " + name, True, (255, 255, 255))
        screen.blit(text_surface, (WIDTH / 2, HEIGHT / 2))

        pygame.display.flip()  # Update the display

def instructions():
    while True:
        screen.fill(BLACK)
        inst = pygame.image.load(path.join(img_dir, "instructions.PNG")).convert()
        screen.blit(inst,(0,0))
       # draw_text(screen, "INSTRUCTIONS", 50, WIDTH / 2, HEIGHT / 3)
        #draw_text(screen, "USE ARROW KEYS TO MOVE", 30, WIDTH / 2, HEIGHT / 2)
        draw_text(screen, "PRESS ENTER TO MAIN MENU", 30, WIDTH -500, (HEIGHT - 100))
        pygame.display.update()
        ev = pygame.event.poll()
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RETURN:
                    break

def insert_highscore(id,name, score):#update highscore to scoresdb
    c.execute("UPDATE scorestb set name=?,score=? where id=?", (name, score,id) )
    conn.commit()

def get_high_scores(): #select list of players in sorted order to get highscore
    c.execute("SELECT name, MAX(score) FROM scorestb GROUP BY name ORDER BY MAX(score) DESC")
    rows = c.fetchall()
    return rows

def final_score(name,score):#to display name and score after a game
    back_bn=Button((WIDTH/2)-100, HEIGHT-200, 200, 100,"BACK", BLACK)
    while True:
        screen.fill(BLACK)
        draw_text(screen, "WELL DONE CAPTAIN "+name, 30, WIDTH / 2, 100)
        draw_text(screen, "YOUR SCORE : " +str(score), 30, WIDTH / 2, HEIGHT / 2)
        #draw_text(screen, str(score), 30, (WIDTH / 2) + 100, HEIGHT / 2)
        back_bn.draw()
        pygame.display.update()
        ev = pygame.event.poll()
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RETURN:
                    break
        elif ev.type == pygame.MOUSEBUTTONDOWN:
                if back_bn.is_clicked(ev):
                    click_sound.play()
                    break

def get_player_list():#select all player deleils from scoresdb
    c.execute('SELECT * FROM scorestb LIMIT 10')
    rows =c.fetchall()
    s=len(rows)
    if s==0:
        add_player(1,"default")
        c.execute('SELECT * FROM scorestb LIMIT 10')
        rows =c.fetchall()
    return rows

def add_player(count,name):#insert new row to scores db
    try:
        c.execute("INSERT INTO scorestb (id,name,score) VALUES (?,?, ?)",(count,name,1))
        conn.commit()
    except:
        add_player(count+1,name)

def delete_player(id):#delete a player data from scoresdb
    id=int(id)
    c.execute("DELETE FROM scorestb WHERE id = ?", (id,))
    conn.commit()

def highscore():#to display highscores in screen
    back_bn=Button((WIDTH/2)-100, HEIGHT-200, 200, 100,"BACK", BLACK)
    while True:
            screen.fill(BLACK)
            screen.blit(background,(0,0))
            scores = get_high_scores()
            draw_text(screen,"HIGHSCORES",60,WIDTH/2,50)
            i=0
            for s in scores:
                i += 50
                name=str(s[0])
                score=str(s[1])
                text_surface = font.render( name +" : "+ score , True, (255, 255, 255))
                screen.blit(text_surface, ((WIDTH / 2) - 50, 100 + i))
            back_bn.draw()
                
                
            pygame.display.flip()
            ev = pygame.event.poll()
            if ev.type == pygame.KEYDOWN:
                click_sound.play()
                if ev.key == pygame.K_RETURN:
                    break
            elif ev.type == pygame.MOUSEBUTTONDOWN:
                if back_bn.is_clicked(ev):
                    click_sound.play()
                    break                       
       
def draw_text(surf, text, size, x, y):
    ## selecting a cross platform font to display the score
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)       ## True denotes the font to be anti-aliased 
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)

def draw_shield_bar(surf, x, y, pct):
    pct = max(pct, 0) 
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect= img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)

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
        self.frame_rate = 30

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
        global ship_no
        ship=1
        image_s=[]
        
        #ship_no=self.select_ship()
        
        
        player_img = ship_images[ship_no-1]
        self.image = pygame.transform.scale(player_img, (100, 100))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0
        self.speedy = 0
        self.shield = 100
        for s in range(1,9):
            delay=600
            if ship_no==s:
                self.shoot_delay = delay-s*25
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        print(self.lives)
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
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 100:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 30

        self.speedx = 0
        self.speedy = 1              ## makes the player static in the screen by default. 
        #update :added small speed to y axis to feel like moving with background
        # then we have to check whether there is an event hanlding being done for the arrow keys being 
        ## pressed 

        ## will give back a list of the keys which happen to be pressed down at that moment
        keystate = pygame.key.get_pressed()     
        if keystate[pygame.K_LEFT]:
            self.speedx = -5
        elif keystate[pygame.K_RIGHT]:
            self.speedx = 5
        elif keystate[pygame.K_UP]:
            self.speedy = -5
        elif keystate[pygame.K_DOWN]:
           self.speedy = 5

        #Fire weapons by holding spacebar
        if keystate[pygame.K_SPACE]:
            self.shoot()

        ## check for the borders at the left and right
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT - 10:
            self.rect.bottom = HEIGHT - 10
           

        self.rect.x += self.speedx
        self.rect.y += self.speedy


    def shoot(self):
        global ship_no
        ## to tell the bullet where to spawn
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shooting_sounds[ship_no-1].play()
            if self.power == 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shooting_sounds[ship_no-1].play()

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
                shooting_sounds[ship_no-1].play()
                missile_sound.play()

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)
    
def select_ship():
        global ship_no,selected_player
        scores = get_player_list()
        r=scores[selected_player-1]
        p_highscore=r[2]
        ship_bn=[]
        ship_fake_bn=[]
        select_ship_running=True
        while select_ship_running:
            screen.blit(background, (0,0))
            x=50
            bn_no=0
            fake_no=0
            req_score=0
            for i in ship_images: 
                clock.tick(FPS)
                screen.blit(i,(x,HEIGHT / 2))
                if p_highscore>req_score:
                    ship_bn.append(Button(x-50,(HEIGHT / 2)+100, 200, 100,"select", BLACK))
                    bn_no+=1
                else:
                    ship_fake_bn.append(Button(x-50,(HEIGHT / 2)+100, 200, 100,"Score "+str(req_score), RED))
                    fake_no+=1

                #draw_text(screen,"press"+str(n), 20, x, (HEIGHT / 2)+100)
                x+=190
                req_score+=1000
                try:
                    ship_bn[bn_no-1].draw()
                except IndexError:
                    continue
                try:
                    ship_fake_bn[fake_no-1].draw()
                except IndexError:
                    continue     
            pygame.display.update()
            ev = pygame.event.poll()
            if ev.type == pygame.KEYDOWN:
                click_sound.play() 
                if ev.key == pygame.K_1 :
                    ship_no=1 
                    break  
                elif ev.key == pygame.K_2:
                    ship_no=2
                    break  
                elif ev.key == pygame.K_3:
                    ship_no=3
                    break  
                elif ev.key == pygame.K_4:
                    ship_no=4
                    break 
                elif ev.key == pygame.K_5:
                     ship_no=5
                     break  
                elif ev.key == pygame.K_6:
                    ship_no=6 
                    break
                elif ev.key == pygame.K_7:
                     ship_no=7
                     break  
                elif ev.key == pygame.K_8:
                     ship_no=8
                     break  
                elif ev.key == pygame.K_9:
                     ship_no=9
                     break
            if ev.type == pygame.MOUSEBUTTONDOWN:
                try:
                    if ship_bn[0].is_clicked(ev):
                        ship_no=1
                        break
                    elif ship_bn[1].is_clicked(ev):
                        ship_no=2
                        break
                    elif ship_bn[2].is_clicked(ev):
                        ship_no=3
                        break
                    elif ship_bn[3].is_clicked(ev):
                        ship_no=4
                        break
                    elif ship_bn[4].is_clicked(ev):
                        ship_no=5
                        break
                    elif ship_bn[5].is_clicked(ev):
                        ship_no=6
                        break
                    elif ship_bn[6].is_clicked(ev):
                        ship_no=7
                        break
                    elif ship_bn[7].is_clicked(ev):
                        ship_no=8
                        break
                    elif ship_bn[8].is_clicked(ev):
                        ship_no=9
                        break
                except IndexError:
                    continue
                
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
            self.speedy = random.randrange(5, 8)        ## for randomizing the speed of the Mob

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
        self.speedy = 5

    def update(self):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        ## kill the sprite after it moves over the top border
        if self.rect.top > HEIGHT:
            self.kill()

## defines the sprite for bullets
class Bullet(pygame.sprite.Sprite):
    global ship_no
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img[ship_no-1]
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
        self.speedy = -15

    def update(self):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Button:
    def __init__(self, x, y, width, height, text, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.text_color = text_color
        self.image = pygame.image.load(path.join(img_dir, 'button.png'))

    def draw(self):
        screen.blit(self.image, self.rect)
        font = pygame.font.Font(None, 30)
        text = font.render(self.text, True, self.text_color)
        text_rect = text.get_rect(center=self.rect.center)
        screen.blit(text, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False
###################################################
main()
c.close()
#pygame.quit()
quit()
