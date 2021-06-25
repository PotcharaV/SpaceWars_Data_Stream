#!/usr/bin/env python3
"""
Game name:		Space Wars (change to cooler name)
Author:			Dan Petersson
Github link:	https://github.com/DanPetersson/SpaceWars

Description:
---------------------------------------------------------
- Survive as long as possible as shoot as many aliens as possible to get good score

---------------------------------------------------------
Python:			3.8 						
PyGame:			1.9.6

Revision updates:
---------------------------------------------------------
Backlog_revision_history.txt

"""

import pygame
import random
import math
import os
import time
import sqlite3
from datetime import datetime
from high_scores import high_scores
#import space_wars_settings as sws

# initialize pygame 
pygame.init()

# Initialize global fonts
font_huge	= pygame.font.Font('freesansbold.ttf', 128)
font_large	= pygame.font.Font('freesansbold.ttf', 64)
font_medium	= pygame.font.Font('freesansbold.ttf', 32)
font_small	= pygame.font.Font('freesansbold.ttf', 16)
font_tiny	= pygame.font.Font('freesansbold.ttf', 8)

# Initialize global Game Colors
black 			= (  0,   0,   0)
white 			= (255, 255, 255)

red 			= (200,   0,   0)
green 			= (  0, 200,   0)
blue 			= (  0,   0, 200)
yellow 			= (200, 200,   0)

light_red 		= (255,   0,   0)
Light_green 	= (  0, 255,   0)
light_blue 		= (  0,   0, 255)
light_yellow	= (255, 255,   0)


# ----------------------------
# 		Define Classes
# ----------------------------

class SpaceObject:

	def __init__(self, image, explosion_image, posX=0, posY=0, speedX = 0, speedY = 0, sizeX = 64, sizeY = 64, 
					state = 'show', sound = ' ', hit_points = 1):
		#self.namme	= name
		self.image  = image
		self.explosion_image = explosion_image 
		self.sizeX  = sizeX
		self.sizeY  = sizeY
		self.posX   = posX
		self.posY   = posY
		self.speedX = speedX
		self.speedY	= speedY
		self.state	= state		# 'hide', 'show'
		self.sound 	= sound
		self.explosion_counter = -1
		self.hit_points = hit_points

	def show(self):
		if self.state == 'show' and self.explosion_counter <= 0:
			screen.blit(self.image, (int(self.posX), int(self.posY)))
		elif self.explosion_counter > 0:
			screen.blit(self.explosion_image, (int(self.posX), int(self.posY)))
			
class SpaceShip(SpaceObject):
    
    # def __init__(self):
    #     super().__init__()

	def update_player_postion(self, screen_sizeX, screen_sizeY):

		# Update X position (update with min/max)
		self.posX += self.speedX
		if self.posX < 0:
			self.posX = 0
		elif self.posX > screen_sizeX-self.sizeX:
			self.posX = screen_sizeX-self.sizeX

		# Update Y position (update with min/max)
		self.posY += self.speedY
		if self.posY < 0:
			self.posY = 0
		elif self.posY > screen_sizeY-self.sizeY:
			self.posY = screen_sizeY-self.sizeY


class SpaceEnemy(SpaceObject):

	def update_enemy_position(self, screen_sizeX, screen_sizeY):

		# Update X position
		self.posX += self.speedX

		# Update Y position
		self.posY += self.speedY

class Coin(SpaceObject):

	def update_coin_position(self, screen_sizeX, screen_sizeY):

		# Update X position
		self.posX += self.speedX

		# Update Y position
		self.posY += self.speedY

class Bullet(SpaceObject):

	def update_bullet_position(self, screen_sizeX, screen_sizeY):

		# Update X position
		self.posX += self.speedX

		# Update Y position, and change state if outside screen
		self.posY += self.speedY
		if self.posY < -self.sizeY:
			self.state = 'hide'

	def fire_bullet(self, player):

		self.posX = player.posX + player.sizeX/2 - self.sizeX/2
		self.posY = player.posY
		self.sound.play()
		self.state = 'show'


class Button:

	def __init__(self, centerX, centerY, width, hight, text='', color=yellow, color_hoover=light_yellow, 
		text_color=black, text_hoover=black, font=font_small):
		self.centerX 		= int(centerX)
		self.centerY		= int(centerY)
		self.width 			= int(width)
		self.hight 			= int(hight)
		self.X				= int(centerX - width/2)
		self.Y				= int(centerY - hight/2)

		self.text 			= text
		self.color 			= color
		self.color_hoover	= color_hoover
		self.text_color		= text_color
		self.text_hoover	= text_hoover
		self.font 			= font
		self.clicked		= False

	# internal only function ?
	def text_objects(text, font, color):
	    text_surface = font.render(text, True, color)
	    return text_surface, text_surface.get_rect()

	# internal only function ?
	def message_display_center(text, font, color, centerX, centerY):
	    text_surface, text_rectangle = text_objects(text, font, color)
	    text_rectangle.center = (centerX,centerY)
	    screen.blit(text_surface, text_rectangle)

	def show(self, mouse=(0,0)):
		if self.X < mouse[0] < self.X + self.width and self.Y < mouse[1] < self.Y + self.hight:
			pygame.draw.rect(screen, self.color_hoover, (self.X, self.Y, self.width, self.hight))
		else:
			pygame.draw.rect(screen, yellow, (self.X, self.Y, self.width, self.hight))
		message_display_center(self.text, self.font, black, self.centerX, self.centerY)

	def check_clicked(self, mouse, mouse_click):
		if self.X < mouse[0] < self.X + self.width and self.Y < mouse[1] < self.Y + self.hight and mouse_click[0] == 1:
			self.clicked = True
		else:
			self.clicked = False



# ----------------------------
# 		Define Procedures
# ----------------------------


def text_objects(text, font, color):
	# Mainly supporting for function message_dipslay
    text_surface = font.render(text, True, color)
    return text_surface, text_surface.get_rect()

def message_display_center(text, font, color, centerX, centerY):
    text_surface, text_rectangle = text_objects(text, font, color)
    text_rectangle.center = (centerX,centerY)
    screen.blit(text_surface, text_rectangle)

def message_display_left(text, font, color, leftX, centerY):
    text_surface, text_rectangle = text_objects(text, font, color)
    text_rectangle.midleft = (leftX, centerY)
    screen.blit(text_surface, text_rectangle)

def message_display_right(text, font, color, rightX, centerY):
    text_surface, text_rectangle = text_objects(text, font, color)
    text_rectangle.midright = (rightX, centerY)
    screen.blit(text_surface, text_rectangle)

def show_high_scores():

#	global db_connection

	high_scores_screen = True
	while high_scores_screen:

		screen.fill(background_color)
		screen.blit(background_image[0], (0,0))

		message_display_center('High Scores', font_large, yellow, int(screen_sizeX/2), int(screen_sizeY * 1/10))
		message_display_center('Press (D)elete or any other key to continue', font_medium, yellow, int(screen_sizeX/2), int(screen_sizeY *9/10))

		top_5 = high_scores.high_scores_top_list(db_connection)

		index = 0
		for entry in top_5:
			# timestamp, name, score, date
			index += 1
			message_display_left(str(entry[1]), font_medium, yellow, int(screen_sizeX * 1/8), int(screen_sizeY *(2+index)/10))
			message_display_right(str(entry[2]), font_medium, yellow, int(screen_sizeX * 2/4), int(screen_sizeY *(2+index)/10))
			message_display_center(str(entry[3]), font_medium, yellow, int(screen_sizeX * 3/4), int(screen_sizeY *(2+index)/10))


		for event in pygame.event.get():	
			if event.type == pygame.QUIT:
				# add even mouse click ?
				high_scores_screen = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_d:
					# Deletes high score db table and recreates empty one
					high_scores.high_scores_db_delete(db_connection)
					high_scores.high_scores_create_table(db_connection)
				else:
					high_scores_screen = False

		# Display intro screen
		pygame.display.update()


def menu():
	# into screen 
	
	intro_screen = True
	while intro_screen:

		screen.fill(background_color)
		screen.blit(background_image[0], (0,0))

		message_display_center('SPACE WARS Online', font_large, yellow, int(screen_sizeX/2), int(screen_sizeY/3))
		message_display_center('New Game (Y/N)', font_medium, yellow, int(screen_sizeX/2), int(screen_sizeY *3/5))

		# get mouse position
		mouse = pygame.mouse.get_pos()
		mouse_click = pygame.mouse.get_pressed()

		# Define and draw buttons
		button_width 	= 130
		button_hight 	= 50

		# Define and draw "Yes" button
		yes_button_X 	= int(screen_sizeX*1/4)
		yes_button_Y 	= 450
		yes_button 		= Button(yes_button_X, yes_button_Y, button_width, button_hight, 'Yes')
		yes_button.show(mouse)
		yes_button.check_clicked(mouse, mouse_click)

		# Define and draw "No" button
		no_button_X 	= int(screen_sizeX*2/4)
		no_button_Y 	= yes_button_Y
		no_button  		= Button(no_button_X,  no_button_Y,  button_width, button_hight, 'No')
		no_button.show(mouse)
		no_button.check_clicked(mouse, mouse_click)

		# Define and draw "High Scores" (hs) button
		hs_button_X 	= int(screen_sizeX*3/4)
		hs_button_Y 	= yes_button_Y
		hs_button  		= Button(hs_button_X,  hs_button_Y,  button_width, button_hight, 'High Scores')
		hs_button.show(mouse)
		hs_button.check_clicked(mouse, mouse_click)

		if yes_button.clicked:
			intro_screen = False
			quit_game = False
		if no_button.clicked:
			intro_screen = False
			quit_game = True

		if hs_button.clicked:
			show_high_scores()

		for event in pygame.event.get():	
			if event.type == pygame.QUIT:
				intro_screen = False
				quit_game = True

		# if 'Y' or 'N' key is pressed
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_y or event.key == pygame.K_z or event.key == pygame.K_RETURN:
					intro_screen = False
					quit_game = False
				if event.key == pygame.K_n:
					intro_screen = False
					quit_game = True

		# Display intro screen
		pygame.display.update()

	return quit_game

def paused(screen_sizeX, screen_sizeY):

	largeText = pygame.font.SysFont("freesansbold",115)
	TextSurf, TextRect = text_objects("Paused", largeText)
	TextRect.center = ((screen_sizeX/2),(screen_sizeX/2))
	screen.blit(TextSurf, TextRect)

	pause = True
	while pause:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				quit()
			if event.type == pygame.KEYDOWN:
				# 'p' for unpause 
				if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
					pause = False
		screen.blit(TextSurf, TextRect)
		pygame.display.update()

		

def enemy_respawn(enemy, level):
	enemy.explosion_counter = -1	
	enemy.posX 	= random.randint(0, screen_sizeX - enemy.sizeX) 
	enemy.posY 	= random.randint(-screen_sizeY, -100)
	if enemy.posX < screen_sizeX / 3:
		enemy.speedX = random.randint(0, 10) / 10 * enemy.speedY
	elif enemy.posX > screen_sizeX * 2 / 3:
		enemy.speedX = random.randint(-10, 0) / 10 * enemy.speedY
	else:
		enemy.speedX = random.randint(-5, 5) / 10 * enemy.speedY
	
#	enemy.speedY = level
	
def coin_respawn(coin, level):
	coin.explosion_counter = -1	
	coin.posX 	= random.randint(0, screen_sizeX - coin.sizeX) 
	coin.posY 	= random.randint(-screen_sizeY, -100)
	#if enemy.posX < screen_sizeX / 3:
	#	enemy.speedX = random.randint(0, 10) / 10 * enemy.speedY
	#elif enemy.posX > screen_sizeX * 2 / 3:
	#	enemy.speedX = random.randint(-10, 0) / 10 * enemy.speedY
	#else:
	#	enemy.speedX = random.randint(-5, 5) / 10 * enemy.speedY


def is_collision(object1, object2):

	obj1_midX = object1.posX + object1.sizeX
	obj1_midY = object1.posY + object1.sizeY
	obj2_midX = object2.posX + object2.sizeX
	obj2_midY = object2.posY + object2.sizeY

	# think if I want to improve this...
	distance = math.sqrt(math.pow(obj1_midX-obj2_midX,2) + math.pow(obj1_midY-obj2_midY,2))
	collision_limit = (object1.sizeX + object1.sizeY + object2.sizeX + object2.sizeY) / 5

	return distance < collision_limit

def show_explosion(object, image):
	screen.blit(image, (int(object.posX), int(object.posY)))


def show_score(score, level, font_size = 16, x=10, y=10):
	score_font = pygame.font.Font('freesansbold.ttf', font_size)
	level_text = score_font.render("Level  : " + str(level), True, (255, 255, 0))
	score_text = score_font.render("Score : " + str(score), True, (255, 255, 0))
	name_text = score_font.render("Player  :  SCORE ", True, (255, 255, 0))						# Name
	show_axisX = score_font.render("Axis X : " + str(player.posX), True, (255, 255, 0))						#A0
	show_axisY = score_font.render("Axis Y : " + str(player.posY), True, (255, 255, 0))						#A1
	coin_collected_text = score_font.render("Coin Collected : " + str(coin_collected), True, (255, 255, 0))	#A2
	enemy_killed_text = score_font.render("Enemy Destroyed : " + str(enemy_killed), True, (255, 255, 0)) 	#A3
	bullet_count_text = score_font.render("Bullet Shot : " + str(bullet_count), True, (255, 255, 0)) 		#A4
	bullet_missed_text = score_font.render("Bullet Missed : " + str(bullet_missed), True, (255, 255, 0)) 	#A5
	
	screen.blit(level_text, (x, y))
	screen.blit(score_text, (x, y + 5 + font_size))

	screen.blit(show_axisX, (x, y + 5 + (font_size*6) + font_size))				#A0
	screen.blit(show_axisY, (x, y + 5 + (font_size*7) + font_size))				#A1

	screen.blit(coin_collected_text, (x, y + 5 + (font_size*1) + font_size))	#A2
	screen.blit(enemy_killed_text, (x, y + 5 + (font_size*2) + font_size))		#A3
	screen.blit(bullet_count_text, (x, y + 5 + (font_size*3) + font_size))		#A4
	screen.blit(bullet_missed_text, (x, y + 5 + (font_size*4) + font_size))		#A5

	screen.blit(name_text, ( int(screen_sizeX - 150 ) , y ))	# Name

	if len(RANK_ONLINE_PLAYER) > 0 :
		RANK_1_text = score_font.render(str(RANK_ONLINE_PLAYER[0]), True, (255, 255, 0))
		screen.blit(RANK_1_text, ( int(screen_sizeX - 100 - (len(RANK_ONLINE_PLAYER[0])*2)) , y + 5 + font_size ))	# 1
	if len(RANK_ONLINE_PLAYER) > 1 :
		RANK_2_text = score_font.render(str(RANK_ONLINE_PLAYER[1]), True, (255, 255, 0))
		screen.blit(RANK_2_text, ( int(screen_sizeX - 100 - (len(RANK_ONLINE_PLAYER[1])*2)) , y + 5 + font_size*2 ))	# 2
	if len(RANK_ONLINE_PLAYER) > 2 :
		RANK_3_text = score_font.render(str(RANK_ONLINE_PLAYER[2]), True, (255, 255, 0))
		screen.blit(RANK_3_text, ( int(screen_sizeX - 100 - (len(RANK_ONLINE_PLAYER[2])*2)) , y + 5 + font_size*3 ))	# 3
	if len(RANK_ONLINE_PLAYER) > 3 :
		RANK_3_text = score_font.render(str(RANK_ONLINE_PLAYER[3]), True, (255, 255, 0))
		screen.blit(RANK_3_text, ( int(screen_sizeX - 100 - (len(RANK_ONLINE_PLAYER[2])*2)) , y + 5 + font_size*4 ))	# 3
	if len(RANK_ONLINE_PLAYER) > 4 :
		RANK_3_text = score_font.render(str(RANK_ONLINE_PLAYER[4]), True, (255, 255, 0))
		screen.blit(RANK_3_text, ( int(screen_sizeX - 100 - (len(RANK_ONLINE_PLAYER[2])*2)) , y + 5 + font_size*5 ))	# 3


def show_game_over(screen_sizeX, screen_sizeY, score, high_score):
	
	# Move enemies below screen (is there a better way?)
	for i in range(num_of_enemies):
		enemy[i].posY = screen_sizeY + 100

	# Display text and score
	message_display_center('GAME OVER', font_large, yellow, int(screen_sizeX/2), int(screen_sizeY * 3/10))
	message_display_center('Your Score              : ' + str(score), font_medium, yellow, int(screen_sizeX/2), int(screen_sizeY *5/10))
	message_display_center('Session Top Score : ' + str(high_score), font_medium, yellow, int(screen_sizeX/2), int(screen_sizeY *6/10))
	message_display_center('Press any key to continue', font_medium, yellow, int(screen_sizeX/2), int(screen_sizeY *8/10))


#############################
#		Main Program		#
#############################
#if __name__ == '__main__':

# # initialize pygame 
# pygame.init()

# # Initialize fonts
# font_huge	= pygame.font.Font('freesansbold.ttf', 128)
# font_large	= pygame.font.Font('freesansbold.ttf', 64)
# font_medium	= pygame.font.Font('freesansbold.ttf', 32)
# font_small	= pygame.font.Font('freesansbold.ttf', 16)
# font_tiny	= pygame.font.Font('freesansbold.ttf', 8)



#name = input('What is your name? ')
import microgear.client as client
import logging
import time
import json
import tkinter as tk
from tkinter import simpledialog

ROOT = tk.Tk()

ROOT.withdraw()
# the input dialog
name = simpledialog.askstring(title="Hello Player.",
                                  prompt="What's your Name? : ")

# Initialize Global CONSTANTS from space_wars_settings.py (sws)
MUSIC 		= False 		#sws.MUSIC 		# True
GAME_SPEED 	= 5 		#sws.GAME_SPEED 	# 1 to 5
PLAYER_NAME	= name		#sws.PLAYER_NAME	# 'DAN'
ONLINE_PLAYER = {}
RANK_ONLINE_PLAYER = []


def updateOnlineScore(data) :
	_data = json.loads(data)
	ONLINE_PLAYER[_data['name']] = _data['score']

	ONLINE_PLAYER_SORTED = sorted(ONLINE_PLAYER.items(), key=lambda x: x[1], reverse=True)
	global RANK_ONLINE_PLAYER
	RANK_ONLINE_PLAYER = []


	for i in ONLINE_PLAYER_SORTED :
		RANK_ONLINE_PLAYER.append(f'{i[0]} : {i[1]}')
		#print(f'{i[0]} : {i[1]}')

	print(RANK_ONLINE_PLAYER)


appid = 'NidaGame' # ชื่อแอพของเรา
gearkey = 'we4wOEbGjaam8RC' #'jtD9ag08syPtqiK' # key
gearsecret = 'ExO62uNUYJuDjtXZR0NI5flU2' #'vDEEIuw9Ssj4OvbrBHmM4hZfa' # secret

client.create(gearkey,gearsecret,appid,{'debugmode': True}) # สร้างข้อมูลสำหรับใช้เชื่อมต่อ

client.setalias(name) # ตั้งชื่้อ

def callback_connect() :
    print ("Now I am connected with netpie")
    
def callback_message(topic, message) :
    #print(topic, ": ", message)
	data = str(message)[2:-1]
	updateOnlineScore(data)
	#print(topic, ": ", data)

def callback_error(msg) :
    print("error", msg)

client.on_connect = callback_connect # แสดงข้อความเมื่อเชื่อมต่อกับ netpie สำเร็จ
client.on_message= callback_message # ให้ทำการแสดงข้อความที่ส่งมาให้
client.on_error = callback_error # หากมีข้อผิดพลาดให้แสดง
client.subscribe("/abzab") # ชื่อช่องทางส่งข้อมูล ต้องมี / นำหน้า และต้องใช้ช่องทางเดียวกันจึงจะรับส่งข้อมูลระหว่างกันได้
client.connect(False) # เชื่อมต่อ ถ้าใช้ True เป็นการค้างการเชื่อมต่อclient.on_message= callback_message # ให้ทำการแสดงข้อความที่ส่งมาให้

# Initialize Global variables
screen_sizeX = 800
screen_sizeY = 600
screen_size = (screen_sizeX, screen_sizeY)
background_color = black
# Initialize screen
screen = pygame.display.set_mode((screen_sizeX, screen_sizeY))
#screen = pygame.display.set_mode((screen_sizeX, screen_sizeY), flags=pygame.FULLSCREEN)


# Get working directory and subdirectories
dir_path = os.getcwd()
images_path = os.path.join(dir_path, 'images')
sounds_path = os.path.join(dir_path, 'sounds')


# Initialize images
icon_image			= pygame.image.load(os.path.join(images_path , 'icon_07.png'))
player_image		= pygame.image.load(os.path.join(images_path, 'MilFal_03.png'))
bullet_image		= pygame.image.load(os.path.join(images_path, 'bullet.png'))
enemy_image	    	= [pygame.image.load(os.path.join(images_path, 'ufo_01.png')),
				       pygame.image.load(os.path.join(images_path, 'ufo_02.png')),
				       pygame.image.load(os.path.join(images_path, 'ufo_03.png')),
				       pygame.image.load(os.path.join(images_path, 'ufo_04.png')),
				       pygame.image.load(os.path.join(images_path, 'spaceship_03_usd.png')),
				       pygame.image.load(os.path.join(images_path, 'spaceship_01_usd.png')),
					   pygame.image.load(os.path.join(images_path, 'death_star_02.png')),
					   pygame.image.load(os.path.join(images_path, 'death_star_03.png'))]
coin_image			= pygame.image.load(os.path.join(images_path, 'coin.png'))
explosion_image		= [pygame.image.load(os.path.join(images_path, 'explosion_01.png')),
				       pygame.image.load(os.path.join(images_path, 'explosion_02.png'))]
background_image	= [pygame.image.load(os.path.join(images_path, 'background_03.jpg')), 
					   pygame.image.load(os.path.join(images_path, 'background_03_usd.jpg'))]
background_image_hight = 600
				      
# Caption and Icon
pygame.display.set_caption("Space Wars")
pygame.display.set_icon(icon_image)

# Initialize sounds
bullet_sound		= pygame.mixer.Sound(os.path.join(sounds_path, 'laser.wav'))
explosion_sound		= pygame.mixer.Sound(os.path.join(sounds_path, 'explosion.wav'))

# Start backgound music
if MUSIC:
	pygame.mixer.music.load(os.path.join(sounds_path, 'background.wav'))
	pygame.mixer.music.play(-1)

# Initialize game speed settings
frames_per_second = 20 + 10 * GAME_SPEED
clock = pygame.time.Clock()

# Initialize connection to high score database
db_connection = high_scores.high_scores_connect_to_db('high_scores.db')
high_scores.high_scores_create_table(db_connection)

# Initialize settings
player_maxSpeedX	= 3.5			# recommended: 3
player_maxSpeedY	= 3.5			# recommended: 3
enemy_maxSpeedX		= 2
enemy_maxSpeedY		= 2
bullet_speed		= 10

session_high_score 	= 0


# --------------------
# Full Game Play Loop
# --------------------

quit_game = False
while not quit_game:

	# Start manu
	quit_game = menu()

	# Game settings
	num_of_enemies	= 5				# recommended: 5
	num_of_coins = 3
	level_change	= 1000			# recommended: 1000
	level_score_increase = 10
	level_enemy_increase = 5

	# initialize other variables / counters
	score 		 = 0

	coin_collected	 = 0    #A2
	enemy_killed = 0        #A3
	bullet_count = 0        #A4
	bullet_missed = 0		#A5

	
	level		 = 1
	level_iter	 = 0
	loop_iter	 = 0
	keyX_pressed = 0
	keyY_pressed = 0
	game_over 	 = False
	go_to_menu 	 = False

	backgound_Y_lower = 0
	backgound_Y_upper = backgound_Y_lower - background_image_hight
	upper_index = 0
	lower_index = 1


	# initialize player and bullet
	player = SpaceShip(player_image, explosion_image[0], screen_sizeX/2-32, screen_sizeY-100)
	bullet = Bullet(bullet_image, explosion_image[0], speedY = -bullet_speed, sound = bullet_sound, state = 'hide', sizeX = 32, sizeY = 32)

	# initialize enemies
	enemy = []
	enemy_image_index = 0
	for i in range(num_of_enemies):
		enemy.append(SpaceEnemy(enemy_image[enemy_image_index], explosion_image[1], speedY = level, hit_points = level))
		enemy_respawn(enemy[i], level)

	# initialize coins
	coin = []
	coin_image_index = 0
	for i in range(num_of_coins):
		coin.append(Coin(coin_image, explosion_image[1], speedY = level))
		coin_respawn(coin[i], level)

	# --------------------
	# Main Game Play Loop
	# --------------------

	pygame.time.set_timer(pygame.USEREVENT, 1000)

	while not go_to_menu and not quit_game:

		# Fill screen and background image	
		screen.fill(background_color)

		# Background images moving
		backgound_Y_lower += 1
		backgound_Y_upper += 1
		if backgound_Y_lower > screen_sizeY:
			backgound_Y_lower = backgound_Y_upper
			backgound_Y_upper = backgound_Y_lower - background_image_hight
			temp = upper_index
			upper_index = lower_index
			lower_index = temp
		screen.blit(background_image[upper_index], (0,backgound_Y_upper))
		screen.blit(background_image[lower_index], (0,backgound_Y_lower))

		# check if increase level
		level_iter += 1
		if level_iter > level_change and not game_over:
			level_iter = 0
			level += 1
			# increase number of enemies with higher speed
			enemy_image_index = (level -1) % len(enemy_image)
			for i in range(num_of_enemies, num_of_enemies+level_enemy_increase):
				enemy.append(SpaceEnemy(enemy_image[enemy_image_index], explosion_image[1], speedY = level, hit_points = level))
				enemy_respawn(enemy[i], level)
			num_of_enemies	+= level_enemy_increase

			# increase score when reaching new level
#			score += level_score_increase

		# Check events and take action
		for event in pygame.event.get():	
			if event.type == pygame.QUIT:
				quit_game = True	

			if event.type == pygame.USEREVENT and not game_over : 
				# A0) Position in X axis
				# A1) Position in Y axis
				# A2) Number of coins collected
				# A3) Number of destroyed enemies
				# A4) Number of shots
				# A5) Number of shots without enemies
				data = f'"name" : "{name}", "X" : {player.posX}, "Y" : {player.posY} , "score" : {score}, "coin" : {coin_collected}, "killed" : {enemy_killed}, "shots" : {bullet_count}, "miss" : {bullet_missed}'
				client.publish("/abzab", '{'+ data + '}')

			# if key is pressed
			if event.type == pygame.KEYDOWN:
				
				# if Game Over and any key, go to menu 				
				if game_over:
					go_to_menu = True

				# 'p' or ESC' for pause 
				elif event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
				 	paused(screen_sizeX, screen_sizeY)

				# 'arrow keys' for movement
				elif event.key == pygame.K_LEFT:
					player.speedX = -player_maxSpeedX
					keyX_pressed += 1
				elif event.key == pygame.K_RIGHT:
					player.speedX = player_maxSpeedX
					keyX_pressed += 1
				elif event.key == pygame.K_UP:
					player.speedY = -player_maxSpeedY
					keyY_pressed += 1
				elif event.key == pygame.K_DOWN:
					player.speedY = player_maxSpeedY
					keyY_pressed += 1

				# if space key, fire bullet			
				elif (event.key == pygame.K_SPACE or event.key == pygame.K_a) and bullet.state == 'hide':
					bullet.fire_bullet(player)
					bullet_count += 1

				if bullet.state == 'hide':
					bullet_missed = bullet_count - enemy_killed

			# if key is released, stop movement in a nice way
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
					keyX_pressed -= 1
					if keyX_pressed == 0:
						player.speedX = 0
				if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
					keyY_pressed -= 1
					if keyY_pressed == 0:
						player.speedY = 0

		# Move player and check not out of screen
		player.update_player_postion(screen_sizeX, screen_sizeY)
		bullet.update_bullet_position(screen_sizeX, screen_sizeY)

		if game_over:
			player.explosion_counter = 0
			show_game_over(screen_sizeX, screen_sizeY, score, session_high_score)
			show_score(score, level)
		else:
			
			# Move enemies and check collisions
			for i in range(num_of_enemies):
				
				# if enemy exploding
				if enemy[i].explosion_counter >= 1:
					enemy[i].explosion_counter -= 1
				elif enemy[i].explosion_counter == 0:
					enemy_respawn(enemy[i], level)				
				else:
					enemy[i].update_enemy_position(screen_sizeX, screen_sizeY)
					if enemy[i].posY > screen_sizeY:
						enemy_respawn(enemy[i], level)
					enemy[i].show()
					
					# if enemy collision with player
					if is_collision(enemy[i], player):
						explosion_sound.play()
						player.explosion_counter = 5
						if score > session_high_score:
							session_high_score = score
						game_over = True
					
					# if bullet hits enemy 
					elif bullet.state == 'show' and is_collision(enemy[i], bullet) :
						explosion_sound.play()
						enemy[i].explosion_counter = 10
						score += enemy[i].hit_points
						enemy_killed += 1
						#bullet_missed = bullet_count - enemy_killed
						bullet.state = 'hide'
										

				enemy[i].show()



			# Move coins and check collisions
			for i in range(num_of_coins):
				
				# if coin exploding
				if coin[i].explosion_counter >= 1:
					coin[i].explosion_counter -= 1
				elif coin[i].explosion_counter == 0:
					coin_respawn(coin[i], level)				
				else:
					coin[i].update_coin_position(screen_sizeX, screen_sizeY)
					if coin[i].posY > screen_sizeY:
						coin_respawn(coin[i], level)              #######
					coin[i].show()
					

					# if coin collision with player
					if is_collision(coin[i], player):
						#explosion_sound.play()
						coin[i].explosion_counter = 4
						#player.explosion_counter = 5
						score += 10
						coin_collected += 1
				
				coin[i].show()








			# show player
			bullet.show()
			player.show()
			show_score(score, level)
			
			

			

		pygame.display.flip()
		
		clock.tick(frames_per_second)

		if player.explosion_counter > 0 :
			# to freeze and show player explosion longer
			time.sleep(1)

	# Update High Score database
	if score > 0:
		high_scores.high_scores_update_db(db_connection, PLAYER_NAME, score)

db_connection.close()
print('Successfully quit Space Wars!')