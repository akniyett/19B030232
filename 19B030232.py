import pygame
import pika
from pygame.locals import *
from threading import Thread
from enum import Enum
import random
import time
import glob
import json
import sys
import math
import uuid





pygame.init()
pygame.font.init()


screen = pygame.display.set_mode((1000, 800))
pygame.time.set_timer(pygame.USEREVENT, 1000)
FPS = 30
clock = pygame.time.Clock()
second = 0
current_time = 0
power_time = 0
value = 0
wall_time = 0
a = 0
my_map = """

ww                      www                     ww                                            
w                        w                       w   
w                                                w    
                                


    ww                                  wwwwww
                                        w     www
        wwwwwww                     wwwwwww
          www                         
           w                           


                                       
                      wwwwww
                                                                   
wwwww                                   w
    w                           wwwwwwwwwwwwww
    w                                   w
    w                                   w
                                   wwwwww
                                        w
                                  wwwwwww 

ww
  w           wwwwwwwwwwww                  
                w                
                w                              www
                w             
         wwwwwwwwwwwww          
                    wwwwwww            
                          www


                                   w
w                       wwwwwwwwwwwwww           w
w                           ww                   w   
ww                                              ww"""



global my_score, small, med, large
global tank_name, menu
global nick
global room_info


base = pygame.mixer.Sound('background1.wav')
# base.play()

small = pygame.font.SysFont('comicsansms', 25)
med = pygame.font.SysFont('comicsansms', 35)
large = pygame.font.SysFont('comicsansms', 85)

class Direction(Enum):
    right = 1
    left = 2
    up = 3
    down = 4

    


class Tank:
    def __init__(self, x, y, speed, color, life, d_right = pygame.K_RIGHT, d_left = pygame.K_LEFT, d_up = pygame.K_UP, d_down = pygame.K_DOWN):
        self.x = x
        self.y = y
        self.speed = speed
        self.color = color 
        self.life = 3
        self.width = 25
        self.height = 25
        self.direction = Direction.right
        self.KEY = {d_right: Direction.right, d_left: Direction.left,
                    d_up: Direction.up, d_down: Direction.down}

    def draw(self):
        barrel = (self.x + self.width // 2, self.y + self.height // 2)
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), 2)
        pygame.draw.circle(screen, self.color, barrel, self.width // 2)

        if self.direction == Direction.right:
            pygame.draw.line(screen, self.color, barrel, (self.x + self.width + self.width // 2, self.y + self.height // 2), 4)

        if self.direction == Direction.left:
            pygame.draw.line(screen, self.color, barrel, (self.x - self.width + self.width // 2, self.y + self.width // 2), 4)
        
        if self.direction == Direction.up:
            pygame.draw.line(screen, self.color, barrel, (self.x + self.width // 2, self.y - self.width // 2), 4)

        if self.direction == Direction.down:
            pygame.draw.line(screen, self.color, barrel, (self.x + self.width // 2, self.y + self.height + self.width // 2), 4)

    def change_direction(self, direction):
        self.direction = direction

    def move(self):
        if self.direction == Direction.left:
            self.x -= self.speed
        if self.direction == Direction.right:
            self.x += self.speed
        if self.direction == Direction.up:
            self.y -= self.speed
        if self.direction == Direction.down:
            self.y += self.speed
        self.draw()
    
    
    def field(self):
        if self.x > 1000:
            self.x = 0
        if self.x < 0:
           self.x = 1000 
        if self.y < 0:
            self.y = 800
        if self.y > 800:
            self.y = 0
    
    def lifely(self):
        if self.life == 0:
            self.x = 1000
            self.y = 1000



tank1 = Tank(300, 300, 5, (243,77,255), 3)
tank2 = Tank(100, 100, 5, (50, 70, 194), 3, pygame.K_d, pygame.K_a, pygame.K_w, pygame.K_s)
tanks = [tank1, tank2]



class Bullet:
    def __init__(self, x, y, color, dx, dy):
        self.x = x
        self.y = y
        self.color = color
        self.dx = dx
        self.dy = dy
        self.drop = False
        
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 2)

    def shoot(self):
        a = self.dx
        a = self.dy
        self.x += self.dx
        self.y += self.dy
        self.draw()

    def launch(self, Tank):
        if Tank.direction == Direction.right:
            self.x = Tank.x + Tank.width + Tank.width // 2
            self.y = Tank.y + Tank.height // 2
            self.dx = a
            self.dy = 0 
        if Tank.direction == Direction.left:
            self.x = Tank.x - Tank.width + Tank.width // 2
            self.y = Tank.y + Tank.height // 2
            self.dx = -a
            self.dy = 0 
        if Tank.direction == Direction.up:
            self.x = Tank.x + Tank.height // 2
            self.y = Tank.y - Tank.height // 2
            self.dx = 0
            self.dy = -a
        if Tank.direction == Direction.down:
            self.x = Tank.x + Tank.height // 2
            self.y = Tank.y + Tank.width + Tank.width // 2
            self.dx = 0
            self.dy = a
        self.shoot()
    

bullet1 = Bullet(900, 800, (243,77,255), 0, 0)
bullet2 = Bullet(900, 800, (50, 70, 194), 0, 0)
bullets = [bullet1, bullet2]


class Food:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), 10)

col = False
pause = False
    


def collision(Bullet, Tank):
    col = False
    for bullet in bullets:
        if bullet.x in range(Tank.x, Tank.x + Tank.width) and bullet.y in range(Tank.y, Tank.y + Tank.width):
            bullet.x = 900
            bullet.y = 800
            col = True
    if col == True:
        Tank.life -= 1
           

def show():
    player_1 = small.render("player_1:", True, (243,77,255))
    screen.blit(player_1, (0, 5))
    life_count1 = small.render(str(tank1.life), True, (0, 0, 0))
    screen.blit(life_count1, (110, 5))
    player_2 = small.render("player_2:", True, (50, 70, 194))
    screen.blit(player_2, (870, 5))
    life_count2 = small.render(str(tank2.life), True, (0, 0, 0))
    screen.blit(life_count2, (980, 5))

def lost(Tank):
    if Tank.life == 0:
        Tank.x = 1000
        Tank.y = 1000

        
removed = [[0, 40], [20, 40], [480, 40], [500, 40], [520, 40], [960, 40], [980, 40], [0, 60], [500, 60], [980, 60], [0, 80], [980, 80], [80, 160], [100, 160], [800, 160], [820, 160], [840, 160], [860, 160], [880, 160], [900, 160], [800, 180], [920, 180], [940, 180], [960, 180], [160, 200], [180, 200], [200, 200], [220, 200], [240, 200], [260, 200], [280, 200], [720, 200], [740, 200], [760, 200], [780, 200], [800, 200], [820, 200], [840, 200], [200, 220], [220, 220], [240, 220], [220, 240], [440, 320], [460, 320], [480, 320], [500, 320], [520, 320], [540, 320], [0, 360], [20, 360], [40, 360], [60, 360], [80, 360], [800, 360], [80, 380], [640, 
380], [660, 380], [680, 380], [700, 380], [720, 380], [740, 380], [760, 380], [780, 380], [800, 380], [820, 380], [840, 380], [860, 380], [880, 380], [900, 380], [80, 400], [800, 400], [80, 420], [800, 420], [700, 440], [720, 440], [740, 440], [760, 440], [780, 440], [800, 440], [800, 460], [680, 480], [700, 480], [720, 480], [740, 480], [760, 480], [780, 480], [800, 480], [0, 520], [20, 520], [40, 540], [280, 540], [300, 540], [320, 540], [340, 540], [360, 540], [380, 540], [400, 540], [420, 540], [440, 540], [460, 540], [480, 540], [500, 540], [320, 560], [320, 580], [940, 580], [960, 580], [980, 580], [320, 600], [180, 620], [200, 620], [220, 620], [240, 620], [260, 620], [280, 620], [300, 620], [320, 620], [340, 620], [360, 620], 
[380, 620], [400, 620], [420, 620], [400, 640], [420, 640], [440, 640], [460, 640], [480, 640], [500, 640], [520, 640], [520, 660], [540, 660], [560, 660], [700, 720], [0, 740], [480, 740], [500, 740], [520, 740], [540, 740], [560, 740], [580, 740], [600, 740], [620, 740], [640, 740], [660, 740], [680, 740], [700, 740], [720, 740], [740, 740], [980, 740], [0, 760], [560, 760], [580, 760], [980, 760], [0, 780], [20, 780], [960, 780], [980, 780]]

def text_objects(text, color, size = "small"):
    if size == "small":
        textSurface = small.render(text, True, color)
    if size == "medium":
        textSurface = med.render(text, True, color)
    if size == "large":
        textSurface = large.render(text, True, color)
    return textSurface, textSurface.get_rect()

def text_to_button(msg, color, buttonx, buttony, buttonwidth, buttonheight, size = "small"):
    textSurf, textRect = text_objects(msg, color, size)
    textRect.center = ((buttonx + (buttonwidth//2)), buttony + (buttonheight // 2))
    screen.blit(textSurf, textRect)

def sup():
    if second >= value:
        super_power.draw()



super_power = Food(random.randint(0, 990), random.randint(0, 790), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))


    


def init__display():
    global screen, title
    tile = pygame.image.load("wall.png")
def titles(my_map):
    global tile
    for i in removed:
        screen.blit(tile, i)
            
                



muz = pygame.mixer.Sound('shooting.wav')

menu = True
running = True

start = pygame.mixer.Sound('start.wav')



mouse = pygame.mouse.get_pos()
click = pygame.mouse.get_pressed()

value = random.randint(5, 25)
print(value)
my_map = my_map.splitlines()



def bullet_check(Bullet):
    for bullet in bullets:
        for i in removed:
            if bullet.x in range(i[0], i[0] + 20) and bullet.y in range(i[1], i[1] + 20):
                    removed.remove(i)
    

def wall_check(Tank):
    for i in removed:
        if Tank.x in range(i[0], i[0] + 20) and Tank.y in range(i[1], i[1] + 20):
            removed.remove(i)
            Tank.life -= 1


global label


IP = '34.254.177.17'
PORT = 5672
VIRTUAL_HOST = 'dar-tanks'
USERNAME = 'dar-tanks'
PASSWORD = '5orPLExUYnyVYZg48caMpX'

pygame.init()


class TankRpcClient:
    def __init__(self):
        self.connection  = pika.BlockingConnection(pika.ConnectionParameters('34.254.177.17', 5672, 'dar-tanks', credentials=pika.PlainCredentials('dar-tanks', '5orPLExUYnyVYZg48caMpX')))
        self.channel = self.connection.channel()                    
        queue = self.channel.queue_declare(queue='',exclusive=True,auto_delete=True)  
        self.callback_queue = queue.method.queue 
        self.channel.queue_bind(exchange='X:routing.topic',queue=self.callback_queue)
        self.channel.basic_consume(queue=self.callback_queue, on_message_callback=self.on_response, auto_ack=True) 
        self.response= None    
        self.corr_id = None
        self.token = None
        self.tank_id = None
        self.room_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = json.loads(body)
            print(self.response)

    def call(self, key, message={}):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='X:routing.topic',
            routing_key=key,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps(message)
        )
        while self.response is None:
            self.connection.process_data_events()

    def check_server_status(self):
        self.call('tank.request.healthcheck')
        return self.response['status']== '200' 

    def obtain_token(self, room_id):
        global nick
        
        message = {
            'roomId': room_id
        }
        self.call('tank.request.register', message)
        if 'token' in self.response:
            self.token = self.response['token']
            self.tank_id = self.response['tankId']
            nick = self.tank_id
            self.room_id = self.response['roomId']
            return True
        return False

    def turn_tank(self, token, direction):
        message = {
            'token': token,
            'direction': direction
        }
        self.call('tank.request.turn', message)

    def fire_bullet(self, token):
        message = {
            'token': token
        }
        self.call('tank.request.fire', message)

class TankConsumerClient(Thread):

    def __init__(self, room_id):
        super().__init__()
        self.connection  = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=IP,                                                
                port=PORT,
                virtual_host=VIRTUAL_HOST,
                credentials=pika.PlainCredentials(
                    username=USERNAME,
                    password=PASSWORD
                )
            )
        )
        self.channel = self.connection.channel()                      
        queue = self.channel.queue_declare(queue='',exclusive=True,auto_delete=True)
        event_listener = queue.method.queue
        self.channel.queue_bind(exchange='X:routing.topic',queue=event_listener,routing_key='event.state.'+room_id)
        self.channel.basic_consume(
            queue=event_listener,
            on_message_callback=self.on_response,
            auto_ack=True
        )
        self.response = None

    def on_response(self, ch, method, props, body):
        global room_info
        self.response = json.loads(body)
        room_info = self.response
        # print(room_info)

    def run(self):
        self.channel.start_consuming()

UP = 'UP'
DOWN = 'DOWN'
LEFT = 'LEFT'
RIGHT = 'RIGHT'


MOVE_KEYS = {
    pygame.K_UP: UP,
    pygame.K_LEFT: LEFT,
    pygame.K_DOWN: DOWN,
    pygame.K_RIGHT: RIGHT
}



def draw_tank(x, y, width, height, color, direction, name):
    tank_c = (x + int(width / 2), y + int(width / 2))
    pygame.draw.rect(screen, color, (x, y, width, width), 2)
    pygame.draw.circle(screen, color, tank_c, int(width / 2))
    if direction == RIGHT:
        pygame.draw.line(screen, color, tank_c, (x + width + width // 2, y + height // 2), 2)
    if direction == LEFT:
        pygame.draw.line(screen, color, tank_c, (x - width + width // 2, y + width // 2), 2)
    if direction == UP:
        pygame.draw.line(screen, color, tank_c, (x + width // 2, y - width // 2), 2)
    if direction == DOWN:
        pygame.draw.line(screen, color, tank_c, (x + width // 2, y + height + width // 2), 2)


    small = pygame.font.SysFont('comicsansms', 14) 
    for_name = small.render(name, True, (255,255,255))
    for_nameRect = for_name.get_rect() 
    for_nameRect.center = (x, y)
    screen.blit(for_name, for_nameRect)


def Game_Over():
    med = pygame.font.SysFont('comicsansms', 35)
    mainloop = False
    launch = False
    if kicked == True:
        base.stop()
        start.play()
        screen.fill((153, 153, 255))
        lable = med.render("You were kicked!", True, (255, 255, 102))
        screen.blit(lable, (300, 300)) 
        game_over = large.render("Game Over!", True, (255, 255, 102))
        screen.blit(game_over, (350, 100))
        score_blit = med.render("Your score:" + str(my_score), True, (255, 255, 102))
        screen.blit(score_blit, (350, 400))

    if winner == True:
        base.stop()
        start.play()
        screen.fill((153, 153, 255))
        lable = med.render("You win!", True, (255, 255, 102))
        screen.blit(lable, (300, 300)) 
        game_over = large.render("Game Over!", True, (255, 255, 102))
        screen.blit(game_over, (350, 100))
        score_blit = med.render("Your score:" + str(my_score), True, (255, 255, 102))
        screen.blit(score_blit, (350, 400))
    
    if loser == True:
        base.stop()
        start.play()
        screen.fill((153, 153, 255))
        lable = med.render("You lose!", True, (255, 255, 102))
        screen.blit(lable, (300, 300)) 
        game_over = large.render("Game Over!", True, (255, 255, 102))
        screen.blit(game_over, (350, 100))
        score_blit = med.render("Your score:" + str(my_score), True, (255, 255, 102))
        screen.blit(score_blit, (350, 400))

                 

global tank_name

def multi_mode():
    global my_score, med, small, kicked, winner, loser
    kicked = False
    winner = False
    loser = False
    event_client = TankConsumerClient('room-6')
    client = TankRpcClient()
    client.check_server_status()
    client.obtain_token('room-6')
    event_client.daemon = True
    event_client.start()
    screen = pygame.display.set_mode((1035, 600))
    mainloop = True
    panel_info = {}
    med = pygame.font.SysFont('comicsansms', 20)
    while mainloop:
        start.stop()
        base.play()
        screen.fill((157,92,255))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainloop = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    mainloop = False
                if event.key == pygame.K_r:
                    mainloop = False
                    menu = True
                    intro()
               
                if event.key in MOVE_KEYS:
                    client.turn_tank(client.token, MOVE_KEYS[event.key])
                if event.key == pygame.K_SPACE:
                    client.fire_bullet(client.token)
                    muz.play()
        for tank in event_client.response['kicked']:
        
            if tank_name == nick:
                kicked = True
                
            
                    
                    
        for tank in event_client.response['winners']:
            if tank_name == nick:
                winner = True
               

        for tank in event_client.response['losers']:
            if tank_name == nick:
                loser = True
               

        if kicked == True or winner == True or loser == True:
            Game_Over()
            event_client.channel.stop_consuming()
           
 

        try:
            remaining_time = event_client.response['remainingTime']
            timer = med.render('Remaining Time: {}'.format(remaining_time), True, (255, 255, 255))
            timerRect = timer.get_rect()
            timerRect.center = (925, 30)
            screen.blit(timer, timerRect)
            bullets = event_client.response['gameField']['bullets']
            tanks = event_client.response['gameField']['tanks']
            pygame.draw.rect(screen, (0, 102, 255), (825, 0, 210, 600), 7)
            i = 110
            panel_info = {tank['id']: [tank['score'],tank['health']] for tank in tanks}
            panel_set = reversed(sorted(panel_info.items(), key=lambda kv: kv[1]))
            info_set = med.render('tank-id'+'  '+'HP'+'  '+'SCORE', True, (255, 255, 255))
            info_setRect = info_set.get_rect()
            info_setRect.center = (930, 70)
           
            for tank in panel_set:
                if tank[0] == nick:
                    color = (0, 0, 255)
                else:
                    color = (243,77,255)
                ind_info = med.render(str(tank[0])+":   "+str(tank[1][1])+'    '+str(tank[1][0]), True, color)
                ind_infoRect = (830, i)
                screen.blit(info_set, info_setRect)
                screen.blit(ind_info, ind_infoRect)
                i+=40
            for tank in tanks:
                tank_x = tank['x']
                tank_y = tank['y']
                tank_width = tank['width']
                tank_height = tank['height']
                tank_direction = tank['direction']
                tank_name = tank['id']
                
                if tank_name == nick:
                    my_score = tank['score']
                    draw_tank(tank_x, tank_y, tank_width, tank_height, (0, 0, 255), tank_direction, 'me')
                else:
                    draw_tank(tank_x, tank_y, tank_width, tank_height, (243,77,255), tank_direction, tank_name)
                for bullet in bullets:
                    bullet_x = bullet['x']
                    bullet_y = bullet['y']
                    if bullet['owner'] == nick:
                        pygame.draw.circle(screen, (0, 0, 255), (bullet_x, bullet_y), 4)
                    else:
                        pygame.draw.circle(screen, (243,77,255), (bullet_x, bullet_y), 4)

           
        except Exception as e:
            pass
      
       
        pygame.display.update()
    
    client.connection.close()
    event_client.channel.stop_consuming()
    exit()


def bot():
    global my_score, med, small, kicked, winner, loser
    kicked = False
    winner = False
    loser = False
    launch = True
    panel_info = {}
    event_client = TankConsumerClient('room-20')
    client = TankRpcClient()
    client.check_server_status()
    client.obtain_token('room-20')
    event_client.daemon = True
    event_client.start()
    screen = pygame.display.set_mode((1035, 600))
    med = pygame.font.SysFont('comicsansms', 20)
    bulletx = ['LEFT', 'RIGHT']
    bullety = ['UP', 'DOWN']
    while launch:
        start.stop()
        base.play()
        screen.fill((157,92,255))
        Direction = ['UP', 'DOWN', 'RIGHT', 'LEFT']
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                launch = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    launch = False
                if event.key == pygame.K_r:
                    mainloop = False
                    menu = True
                    intro()

        for tank in event_client.response['kicked']:
            if tank_name == nick:
                kicked = True
                
                    
                    
        for tank in event_client.response['winners']:
            if tank_name == nick:
                winner = True

        for tank in event_client.response['losers']:
            if tank_name == nick:
                loser = True

        if kicked == True or winner == True or loser == True:
            Game_Over()     
            event_client.channel.stop_consuming()
            
        

        
  
               
        try:
            remaining_time = event_client.response['remainingTime']
            timer = med.render('Remaining Time: {}'.format(remaining_time), True, (255, 255, 255))
            timerRect = timer.get_rect()
            timerRect.center = (930, 30)
            screen.blit(timer, timerRect)
            bullets = event_client.response['gameField']['bullets']
            tanks = event_client.response['gameField']['tanks']
            pygame.draw.rect(screen, (0, 102, 255), (825, 0, 210, 600), 7)
            i = 110
            panel_info = {tank['id']: [tank['score'],tank['health']] for tank in tanks} 
            panel_set = reversed(sorted(panel_info.items(), key=lambda kv: kv[1]))
            info_set = med.render('tank-id'+'  '+'HP'+'  '+'SCORE', True, (255, 255, 255))
            info_setRect = info_set.get_rect()
            info_setRect.center = (930, 70)
           
            for tank in panel_set:
                if tank[0] == nick:
                    color = (0, 0, 255)
                else:
                    color = (243,77,255)
                ind_info = med.render(str(tank[0])+":   "+str(tank[1][1])+'    '+str(tank[1][0]), True, color)
                ind_infoRect = (830, i)
                screen.blit(info_set, info_setRect)
                screen.blit(ind_info, ind_infoRect)
                i+=40
            for bullet in bullets:
                bullet_x = bullet['x']
                bullet_y = bullet['y']
                if bullet['owner'] == nick:
                    bul_x = bullet_x
                    bul_y = bullet_y
                    pygame.draw.circle(screen, (0, 0, 255), (bullet_x, bullet_y), 4)
                else:
                    pygame.draw.circle(screen, (243,77,255), (bullet_x, bullet_y), 4)
            for tank in tanks:
                tank_x = tank['x']
                tank_y = tank['y']
                tank_width = tank['width']
                tank_height = tank['height']
                tank_direction = tank['direction']
                tank_name = tank['id']
                if tank_name == nick:
                    if tank['direction'] == 'UP':
                        Direction.pop(0)
                        client.turn_tank(client.token, random.choice(Direction))
                    my_direction = tank_direction    
                    my_x = tank_x
                    my_y = tank_y
                    my_score = tank['score']
                    draw_tank(tank_x, tank_y, tank_width, tank_height, (0, 0, 255), tank_direction, 'me')
                else:
                    draw_tank(tank_x, tank_y, tank_width, tank_height, (243,77,255), tank_direction, tank_name)
                    if my_y in range(tank_y - 25, tank_y+46) and tank_x > my_x:
                        client.turn_tank(client.token, 'RIGHT')
                        client.fire_bullet(client.token)
                        muz.play()
                        client.turn_tank(client.token, 'DOWN')
                    elif my_y in range(tank_y - 25, tank_y+46) and tank_x < my_x:
                        client.turn_tank(client.token, 'LEFT')
                        client.fire_bullet(client.token)
                        muz.play()
                        client.turn_tank(client.token, 'DOWN')
                    elif my_x in range(tank_x - 25, tank_x+46) and tank_y > my_y:
                        client.turn_tank(client.token, 'DOWN')
                        client.fire_bullet(client.token)
                        muz.play()
                        client.turn_tank(client.token, 'LEFT')
                    elif my_x in range(tank_x - 25, tank_x+46) and tank_y < my_y:
                        client.turn_tank(client.token, 'UP')
                        client.fire_bullet(client.token)
                        muz.play()
                        client.turn_tank(client.token, 'RIGHT')
                    elif my_y > tank_y and my_x > tank_x and tank_direction == 'LEFT':
                        client.turn_tank(client.token, 'UP')
                        if my_x == tank_x + 300:
                            client.turn_tank(client.token, 'RIGHT')
                            client.fire_bullet(client.token)
                    elif my_y > tank_y and my_x > tank_x and tank_direction == 'RIGHT':
                        client.turn_tank(client.token, 'UP')
                        if my_x == tank_x + 300:
                            client.turn_tank(client.token, 'RIGHT')
                            client.fire_bullet(client.token)
                    elif my_y > tank_y and my_x > tank_x and tank_direction == 'UP':
                        client.turn_tank(client.token, 'RIGHT')
                        client.fire_bullet(client.token)
                        client.turn_tank(client.token, 'DOWN')
                    elif my_y > tank_y and my_x > tank_x and tank_direction == 'DOWN':
                        client.turn_tank(client.token, 'RIGHT')
                    elif my_y < tank_y and my_x < tank_x and tank_direction == 'UP':
                        client.turn_tank(client.token, 'RIGHT') 
                    elif my_y < tank_y and my_x < tank_x and tank_direction == 'DOWN':
                        client.turn_tank(client.token, 'RIGHT')  
                    elif my_y < tank_y and my_x < tank_x and tank_direction == 'LEFT':
                        client.turn_tank(client.token, 'RIGHT')
                        client.fire_bullet(client.token)
                        muz.play()
                    elif my_y < tank_y and my_x < tank_x and tank_direction == 'RIGHT':
                        client.turn_tank(client.token, 'DOWN')
                    elif my_y < tank_y and my_x > tank_y and tank_direction == 'RIGHT':
                        client.turn_tank(client.token, 'DOWN')
                        if my_x == tank_x + 300:
                            client.fire_bullet(client.token)
                            muz.play()
                    elif my_y < tank_y and my_x > tank_y and tank_direction == 'LEFT': 
                        client.turn_tank(client.token, 'DOWN')
                    elif my_y < tank_y and my_x > tank_y and tank_direction == 'UP': 
                        client.turn_tank(client.token, 'DOWN')
                    elif my_y < tank_y and my_x > tank_y and tank_direction == 'DOWN': 
                        client.turn_tank(client.token, 'LEFT')
                    elif my_y > tank_y and my_x < tank_y and tank_direction == 'UP': 
                        client.turn_tank(client.token, 'LEFT')
                    elif my_y > tank_y and my_x < tank_y and tank_direction == 'DOWN': 
                        client.turn_tank(client.token, 'RIGHT')
                    elif my_y > tank_y and my_x < tank_y and tank_direction == 'LEFT': 
                        client.turn_tank(client.token, 'UP')
                    elif my_y > tank_y and my_x < tank_y and tank_direction == 'RIGHT': 
                        client.turn_tank(client.token, 'UP')
                    elif my_y in range(tank_y - 25, tank_y+46) and tank_x > my_x + 250 and tank_direction == 'LEFT':
                        client.turn_tank(client.token, 'RIGHT')
                        client.fire_bullet(client.token)
                        muz.play()
                        client.turn_tank(client.token, 'DOWN')
                    elif my_y in range(tank_y - 25, tank_y+46) and tank_x > my_x + 250 and tank_direction == 'RIGHT':
                        client.turn_tank(client.token, 'LEFT')
                        client.fire_bullet(client.token)
                        muz.play()
                        client.turn_tank(client.token, 'DOWN')
                    elif my_y in range(tank_y - 25, tank_y+46) and tank_x > my_x + 250 and tank_direction == 'UP':
                        client.turn_tank(client.token, 'LEFT')
                    elif my_y in range(tank_y - 25, tank_y+46) and tank_x > my_x + 250 and tank_direction == 'DOWN':
                        client.turn_tank(client.token, 'LEFT')
                    elif my_y in range(tank_y - 25, tank_y+46) and tank_x + 250 < my_x and tank_direction == 'RIGHT':
                        client.turn_tank(client.token, 'LEFT')
                        client.fire_bullet(client.token)
                        muz.play()
                        client.turn_tank(client.token, 'DOWN')
                    elif my_y in range(tank_y - 25, tank_y+46) and tank_x + 250 < my_x and tank_direction == 'LEFT':
                        client.turn_tank(client.token, 'RIGHT')
                        client.fire_bullet(client.token)
                        muz.play()
                        client.turn_tank(client.token, 'UP')
                    elif my_y in range(tank_y - 25, tank_y+46) and tank_x + 250 < my_x and tank_direction == 'UP':
                        client.turn_tank(client.token, 'LEFT')
                    elif my_y in range(tank_y - 25, tank_y+46) and tank_x + 250 < my_x and tank_direction == 'DOWN':
                        client.turn_tank(client.token, 'RIGHT')
                    elif my_x in range(tank_x - 25, tank_x+46) and tank_y > my_y + 250 and tank_direction == 'LEFT':
                        client.turn_tank(client.token, 'RIGHT')
                    elif my_x in range(tank_x - 25, tank_x+46) and tank_y > my_y + 250 and tank_direction == 'RIGHT':
                        client.turn_tank(client.token, 'UP')
                    elif my_x in range(tank_x - 25, tank_x+46) and tank_y > my_y + 250 and tank_direction == 'UP':
                        client.turn_tank(client.token, 'DOWN')
                        client.fire_bullet(client.token)
                        muz.play()
                        client.turn_tank(client.token, 'RIGHT')
                    elif my_x in range(tank_x - 25, tank_x+46) and tank_y > my_y + 250 and tank_direction == 'DOWN':
                        client.turn_tank(client.token, 'UP')
                        client.fire_bullet(client.token)
                        muz.play()
                        client.turn_tank(client.token, 'RIGHT')
                    elif my_x in range(tank_x - 25, tank_x+46) and tank_y + 250 < my_y and tank_direction == 'RIGHT':
                        client.turn_tank(client.token, 'UP')
                        client.fire_bullet(client.token)
                        muz.play()
                        client.turn_tank(client.token, 'LEFT') 
                    elif my_x in range(tank_x - 25, tank_x+46) and tank_y + 250 < my_y and tank_direction == 'LEFT':
                        client.turn_tank(client.token, 'UP')
                        client.fire_bullet(client.token)
                        muz.play()
                        client.turn_tank(client.token, 'RIGHT')
                    elif my_x in range(tank_x - 25, tank_x+46) and tank_y + 250 < my_y and tank_direction == 'UP':
                        client.turn_tank(client.token, 'DOWN')
                        client.fire_bullet(client.token)
                        muz.play()
                        client.turn_tank(client.token, 'LEFT')
                    elif my_x in range(tank_x - 25, tank_x+46) and tank_y + 250 < my_y and tank_direction == 'DOWN':
                        client.turn_tank(client.token, 'UP')
                        client.fire_bullet(client.token)
                        muz.play()
                        client.turn_tank(client.token, 'RIGHT')
            
            for bullet in bullets:
                if bullet_x in range(my_x, my_x+31) and (my_y < tank_y or my_y > tank_y):
                    client.turn_tank(client.token, random.choice(bulletx))
                if bullet_y in range(my_y, my_y+31) and (my_x < tank_x or my_x > tank_x):
                    client.turn_tank(client.token, random.choice(bullety))           

        except Exception as e:
            pass
       
        pygame.display.update()
    
    client.connection.close()
    event_client.channel.stop_consuming()
    exit()


def intro():
    global menu, room_info, launch
    screen = pygame.display.set_mode((1000, 800))
    while menu:
        start.play()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                menu = False
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu = False
                    running = False
            
            

            screen.fill((153, 153, 255))
            welcome = large.render("Welcome to Tanks!", True, (255, 255, 102))
            screen.blit(welcome, (100, 100))
            pygame.draw.rect(screen, (255, 153, 255), (200, 500, 100, 50))
            pygame.draw.rect(screen, (153, 204, 255), (400, 600, 100, 50))
            pygame.draw.rect(screen, (255, 102, 255), (400, 500, 100, 50))
            pygame.draw.rect(screen, (204, 0, 204), (600, 500, 100, 50))

            text_to_button('single', (0, 0, 0),  200, 500, 100, 50)
            text_to_button('exit', (0, 0, 0),  400, 600, 100, 50)
            text_to_button('multi', (0, 0, 0), 400, 500, 100, 50)
            text_to_button('AI', (0, 0, 0), 600, 500, 100, 50)

            mouse = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
            if 200 < mouse[0] < 300 and 500 < mouse[1] < 550:  #single
                pygame.draw.line(screen, (0, 0, 0), (220, 542), (280, 542))
                if click[0] == 1:
                    menu = False
                    running = True
                    tank1.life = 3
                    tank2.life = 3
                    tank1.speed = 5
                    tank2.speed = 5
                    for bullet in bullets:
                        a = 10
                    

            if 400 < mouse[0] < 500 and 500 < mouse[1] < 550:  #multi
                pygame.draw.line(screen, (0, 0, 0), (420, 542), (480, 542))
                if click[0] == 1:
                    mainloop = True
                    multi_mode()
                    menu = False
                   
                    

            if 600 < mouse[0] < 700 and 500 < mouse[1] < 550:  #AI
                pygame.draw.line(screen, (0, 0, 0), (620, 542), (680, 542))
                if click[0] == 1:
                    launch = True
                    bot()
                    menu = False
                   


            if 400 < mouse[0] < 500 and 600 < mouse[1] < 650:   #exit
                pygame.draw.line(screen, (0, 0, 0), (420, 642), (480, 642))
                if click[0] == 1:
                    running = False
                    menu = False
                    launch = False


        pygame.display.update()


intro()
screen = pygame.display.set_mode((1000, 800))
while running:
    start.stop()
    base.play()
    global tile
    mill = clock.tick(FPS)
    tile = pygame.image.load("wall.png")
   

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.USEREVENT:
            second += 1
        
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
                
            for i in tanks:
                if event.key in i.KEY.keys():
                    i.change_direction(i.KEY[event.key])



        
            if event.key == pygame.K_RETURN:
                muz.play()
                for i in bullets:
                    bullet1.launch(tank1)
            
            if event.key == pygame.K_SPACE:
                muz.play()
                for i in bullets:
                    bullet2.launch(tank2)

            pressed = pygame.key.get_pressed()
            
            if pressed[pygame.K_RETURN]:
                if len(bullets) >= 0:
                    bullet = Bullet(900, 800, (243,77,255), 0, 0)
                    bullets.append(bullet)
                    bullet.launch(tank1)
            if pressed[pygame.K_SPACE]:
                if len(bullets) >= 0:
                    bullet = Bullet(900, 800, (50, 70, 194), 0, 0)
                    bullets.append(bullet)
                    bullet.launch(tank2)

    current_time = pygame.time.get_ticks()

  
    

    if super_power.x in range(tank1.x, tank1.x + tank1.width) and super_power.y in range(tank1.y, tank1.y + tank1.height):
        for bullet in bullets:
            a = a*2
        tank1.speed = tank1.speed*2
        power_time = pygame.time.get_ticks()
        super_power.x = 1500
        super_power.y = 1500
        value = random.randint(5, 20)
        print(value)
        second = 0
        done = True
        
                
    if super_power.x in range(tank2.x, tank2.x + tank2.width) and super_power.y in range(tank2.y, tank2.y + tank2.height):
        for bullet in bullets:
            a = a*2
        tank2.speed = tank2.speed*2
        power_time = pygame.time.get_ticks()
        super_power.x = 1500
        super_power.y = 1500
        value = random.randint(5, 20)
        print(value)
        second = 0
        done = True
    if current_time - power_time > 5000:
        tank1.speed = 5
        a = 10
    
    if current_time - power_time > 5000:
        tank2.speed = 5
        a = 10  


    

    screen.fill((41,255,62))

    if tank2.life <= 0 or tank1.life <= 0:
        base.stop()
        start.play()
        screen.fill((153, 153, 255))

        tank1.speed = 0
        tank2.speed = 0
        tank1.x = 200
        tank1.y = 250
        tank2.x = 600
        tank2.y = 250
        tank2.draw()
        tank1.draw()


        game_over = large.render("Game Over!", True, (255, 255, 102))
        screen.blit(game_over, (150, 100))
        if tank2.life == 0:
            winner_1 = med.render("Player_1  WON!", True, (51, 255, 153))
            screen.blit(winner_1, (250,350))
        if tank1.life == 0:
            winner_2 = med.render("Player_2 WON!", True, (51, 255, 153))
            screen.blit(winner_2, (250, 350))

        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_r]:        
            running = False
            menu = True
            intro()
        # pygame.display.update()
       
        

        
    for i in tanks:
        i.move()
        i.field()
        

    for i in bullets:
        i.shoot()

    init__display()
    titles(my_map)

    bullet_check(bullet1)
    bullet_check(bullet2)
    
    # brick()
    
    collision(bullet1, tank2)
    collision(bullet2, tank1)
    sup()
    wall_check(tank1)
    wall_check(tank2)
    lost(tank1)
    lost(tank2)
    show()
    pygame.display.flip()




pygame.quit()

 
