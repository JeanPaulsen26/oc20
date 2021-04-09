# EXTENSION

import math
import random
from pygame.locals import *
import pygame

pygame.mixer.init() # initialiser mixer
pygame.font.init() # initialiser font

# taille écran
w = 1080
h = 720


class Game:
    
    def __init__(self):
        self.is_playing = False
        self.all_players = pygame.sprite.Group()
        self.player = Player(self) # générer joueur
        self.all_players.add(self.player)
        self.comet_event = CometFallEvent(self) #générer événement comet
        self.all_monsters = pygame.sprite.Group() # groupe monstre
        self.score = 0
        self.sound_manager = SoundManager()
        self.font = pygame.font.Font("assets/font.ttf", 20)
        self.pressed = {} # touche activé par joueur

    
    def start(self):
        self.is_playing = True
        self.spawn_monster()
        self.spawn_monster()
        
    def add_score(self, points):
        self.score += points
        
    def game_over(self):
        # restart game
        self.all_monsters = pygame.sprite.Group()
        self.comet_event.all_comets = pygame.sprite.Group()
        self.player.pv = self.player.max_pv
        self.comet_event.reset_percent()
        self.is_playing = False
        self.score = 0
        self.sound_manager.play('game_over')
        
    def update(self, screen):
        # afficher score
        score_text = self.font.render(f"Score : {self.score}", 1, (250, 250, 250))
        screen.blit(score_text, (20, 20))
        
        # appliquer image du joueur
        screen.blit(self.player.image, self.player.rect)
    
        # actualiser bar player
        self.player.update_pv_bar(screen)
        
        # actualiser la barre d'évémenement updatebar
        self.comet_event.update_bar(screen)
        
        # appliquer projectiles en mouvement
        for projectile in self.player.all_projectiles:
            projectile.move()
        
        # mouvement monstre
        for monster in self.all_monsters:
            monster.forward()
            monster.update_pv_bar(screen) # afficher health bar
            
        # chutes des cometes afficher
        for comet in self.comet_event.all_comets:
            comet.fall()
        
        self.player.all_projectiles.draw(screen)
    
        # appliquer images groupe monstre
        self.all_monsters.draw(screen)
        
        # appliquer image groupe cometes
        self.comet_event.all_comets.draw(screen)
    
        # gauche ou droite ?
        if self.pressed.get(pygame.K_RIGHT) and self.player.rect.x < 950:
            self.player.move_r()
            #print("go right:", game.player.rect.x)
    
        elif self.pressed.get(pygame.K_LEFT) and self.player.rect.x > -20:  
            self.player.move_l()    
            #print("go left:", game.player.rect.x)
    
    
    def check_collision(self, sprite, group):
        # régler collision 
        return pygame.sprite.spritecollide(sprite, group, False, pygame.sprite.collide_mask)
    
    def spawn_monster(self):
        monster = Monster(self)
        self.all_monsters.add(monster)
        

class Player(pygame.sprite.Sprite): # class sprite: élément graphique
    
    def __init__(self, game):
        super().__init__() # charger super class Sprite
        self.game = game
        self.pv = 100
        self.max_pv = 100
        self.attack = 10
        self.speed = 6
        self.all_projectiles = pygame.sprite.Group() #groupe projectiles
        
        # image joueur
        self.image = pygame.image.load('assets/p1.png')

        #self.image = pygame.image.load('assets/p3.png')
        self.image = pygame.transform.scale(self.image, (140, 140))
        self.rect = self.image.get_rect()
        self.rect.x = 425
        self.rect.y = 500
    
    def damage(self, amount):
        if self.pv - amount > amount: # limite dégat/pv
            self.pv -= amount
        else:
            # mort du joueur
            self.game.game_over()
    
    def update_pv_bar(self, surface):
        pygame.draw.rect(surface, (0, 0, 0), [self.rect.x + 25, self.rect.y - 25, self.max_pv, 5])
        pygame.draw.rect(surface, (111, 210, 46), [self.rect.x + 25, self.rect.y - 25, self.pv, 5])
        
    def launch_projectile(self):
        #instance classe projectile
        self.all_projectiles.add(Projectile(self)) #self: prendre coordonné player
        # jouer le son
        self.game.sound_manager.play('tir')
        
    # mouvement
    def move_r(self):
        # si 0 collision 
        if not self.game.check_collision(self, self.game.all_monsters):
            self.rect.x += self.speed
        
        #supprimer projectile plus présent
        if self.rect.x > 1080:
            self.remove()
                   
    def move_l(self):
        self.rect.x -= self.speed
        

class Projectile(pygame.sprite.Sprite):
    
    def __init__(self, player):
        super().__init__()
        self.speed = 3  #vitesse projectile
        self.player = player
        self.image = pygame.image.load('assets/projectile2.png')
        self.image = pygame.transform.scale(self.image, (50, 50)) # modifier taille image
        self.rect = self.image.get_rect()
        self.rect.x = player.rect.x + 100
        self.rect.y = player.rect.y + 50
        
        # Valeurs pour rotation
        self.origin_image = self.image 
        self.angle = 0 #angle initiale
        
    def rotation(self):
        # tourner projectile
        self.angle += 3 #vitesse rotation
        self.image = pygame.transform.rotozoom(self.origin_image, self.angle, 1)
        self.rect = self.image.get_rect(center=self.rect.center) # rotation centré
    
    def remove(self):
        self.player.all_projectiles.remove(self)
        
    # mouvement du projectile
    def move(self):    
        self.rect.x += self.speed
        self.rotation()
        
        # si 0 collision
        for monster in self.player.game.check_collision(self, self.player.game.all_monsters):
            # delete projectile
            self.remove()
            # infliger dégat
            monster.damage(self.player.attack)


class Monster(pygame.sprite.Sprite):
    
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.pv = 60
        self.max_pv = 60
        self.attack = 0.3
        self.image = pygame.image.load('assets/a1.png')
        self.rect = self.image.get_rect()
        # lieu spawn aléatoire
        self.rect.x = 1000 + random.randint(0, 300)
        self.rect.y = 520
        self.speed = random.randint(1, 3)
        self.loot_amount = 10
        
    
    def damage(self, amount):
        # infliger les dégat
        self.pv -= amount
        
        # vérifier si pv <= 0 : mort
        if self.pv <= 0:
            self.rect.x = 1000 + random.randint(0, 300)
            self.speed = random.randint(1, 5)
            self.pv = self.max_pv
            # ajouter nb score
            self.game.add_score(self.loot_amount)
            
            # vérifier si event bar au max et tout les monstres sont mort
            if self.game.comet_event.full_loaded():
                # retirer du jeu
                self.game.all_monsters.remove(self)
                self.game.comet_event.attempt_fall() # pluie de comète activer
           
            # rajouter pv au joueur
            if self.game.player.pv <= 95:
                self.game.player.pv += 5
        
    def update_pv_bar(self, surface):
        # définir jauge de vie ( position xy, largeur, épaisseur
            #bar_position = [self.rect.x + 10, self.rect.y - 10, self.pv, 5]
            #bar_back_position = [self.rect.x + 10, self.rect.y - 10, self.max_pv, 5]
        # dessiner la bar
        pygame.draw.rect(surface, (0, 0, 0), [self.rect.x + 20, self.rect.y - 10, self.max_pv, 5])
        pygame.draw.rect(surface, (111, 210, 46), [self.rect.x + 20, self.rect.y - 10, self.pv, 5])
        
    def forward(self):
        # si 0 collision
        if not self.game.check_collision(self, self.game.all_players):
            self.rect.x -= self.speed
        
        # si collision: dégat au joueur
        else:
            self.game.player.damage(self.attack)



class CometFallEvent:
    
    # céer un compteur
    def __init__(self, game):
        self.percent = 0 # pourcent initial de la jauge
        self.percent_speed = 10 # temps entre cometes
        self.game = game
        self.fall_mode = False
        
        # groupe sprite cometes
        self.all_comets = pygame.sprite.Group()
    
    def add_percent(self):
        self.percent += self.percent_speed / 100
        
    def full_loaded(self):
        return self.percent >= 100
    
    def reset_percent(self):
        self.percent = 0
    
    def meteor_fall(self):
        # boucle comets fall
        for i in range(1, 35):
            self.all_comets.add(Comet(self)) # 1er comete
        
    def attempt_fall(self):
        # jauge pleine et 0 monstre 
        if self.full_loaded() and len(self.game.all_monsters) == 0:
            print("Comet Fall Event !")
            self.meteor_fall()
            self.fall_mode = True # activer événement
            
    def update_bar(self, surface):
        
        self.add_percent() # ajouter du pourcentage à la barre
        
        
        pygame.draw.rect(surface, (0, 0, 0), [ 
            0, # axe x
            surface.get_height() - 10, # axe y 
            surface.get_width(), # longeur de la barre 
            10 # hauteur de la barre  
        ])   
        
        pygame.draw.rect(surface, (187, 11, 11),[ 
            0, 
            surface.get_height() - 10,
            self.percent_speed * self.percent, #longueur fenetre
            10 
        ])
        
class Comet(pygame.sprite.Sprite):
    
    def __init__(self, comet_event):
        super().__init__()
        self.image = pygame.image.load('assets/comet.png')
        self.image = pygame.transform.scale(self.image, (130, 130))
        self.rect = self.image.get_rect()
        self.speed = random.randint(5, 7)
        self.rect.x = random.randint(-30, 1000)
        self.rect.y = - random.randint(0, 2500)
        self.comet_event = comet_event
    
    def remove(self):
        self.comet_event.all_comets.remove(self)
        # jouer le son
        self.comet_event.game.sound_manager.play('meteorite')
        
        # vérifier que nb comete = 0
        if len(self.comet_event.all_comets) == 0:
            self.comet_event.reset_percent() # remettre barre à 0
            
            self.comet_event.game.spawn_monster()  
            self.comet_event.game.spawn_monster()
            
    def fall(self):
        self.rect.y += self.speed
        # sol
        if self.rect.y >= 550:
            self.remove()
            
            # boucle comete 
            if len(self.comet_event.all_comets) == 0:
                print("Comet Fall Event END")
                # remettre jauge au départ
                self.comet_event.reset_percent()
                self.comet_event.fall_mode = False
            
        # collision joueur
        if self.comet_event.game.check_collision(
            self, self.comet_event.game.all_players
        ):
            print("joueur touché !")
            self.remove()
            self.comet_event.game.player.damage(20) # dégat comete
            
class SoundManager:
    
    def __init__(self):
        self.sounds = {
            'click': pygame.mixer.Sound("assets/sounds/click.ogg"),
            'game_over': pygame.mixer.Sound("assets/sounds/game_over.ogg"),
            'meteorite': pygame.mixer.Sound("assets/sounds/meteorite.ogg"),
            'tir': pygame.mixer.Sound("assets/sounds/tir.ogg"),
        }
    
    def play(self, name):
        self.sounds[name].play()
            
                  
# générer la fenêtre
pygame.display.set_caption("SPACE INVASION GAME")
screen = pygame.display.set_mode((w, h))

# Accueil console
print("")
print("")
print("WELCOME TO SPACE INVASION GAME !")


# importer arrière plan du jeu
background = pygame.image.load('assets/space2.jpg')

# importer banière START
banner = pygame.image.load('assets/a1.png')
banner = pygame.transform.scale(banner, (150, 150)) # taille bannière
banner_rect = banner.get_rect()
banner_rect.x = math.ceil(screen.get_width()/2.23)
banner_rect.y = math.ceil(screen.get_height()/1.5)

# bouton START
play_button = pygame.image.load('assets/play2.png')
play_button = pygame.transform.scale(play_button, (200, 150))
play_button_rect = play_button.get_rect()
play_button_rect.x = math.ceil(screen.get_width()/ 2.5)
play_button_rect.y = math.ceil(screen.get_height()/ 4.8)

#charger Game
game = Game()

# charger Player
#player = Player()

# garder fenêtre ouverte
running = True

# boucle du jeu MAIN
while running:
    
    # appliquer arrière plan 
    screen.blit(background, (-100, 0))
       
    # vérifier si jeu à commencé
    if game.is_playing:
        
        #déclencher instructions de la partie
        game.update(screen)
    
    # vérifier si jeu à pas commencé
    else:
        # ajouter bannière
        screen.blit(banner, banner_rect)
        screen.blit(play_button, play_button_rect)
     
    # mettre à jour l'écran
    pygame.display.flip()
    
    # si le joueur ferme la fenêtre
    for event in pygame.event.get():
        # Vérifier fermeture de fenêtre
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            print("Fermeture du jeu")
        # detecter contact clavier
        elif event.type == pygame.KEYDOWN:
            game.pressed[event.key] = True
            
            # SPACE pour projectile
            if event.key == pygame.K_SPACE:
                game.player.launch_projectile()
            
        elif event.type == pygame.KEYUP:
            game.pressed[event.key] = False
            
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # vérifier si START activé
            if play_button_rect.collidepoint(event.pos):
                # lancer le jeu
                game.start()
                # play sounds
                game.sound_manager.play('click')
    
    
 # Source : pygame.org
 #          youtube.com/Collisons in Pygame
 #          youtube.com/Pygame in 90 Minutes - For beginners
 #          youtube.com/Python Final Fantasy Style RPG Battle Beginner Tutorial in Pygame