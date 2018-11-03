#!/usr/bin/env python3

import pygame
from pygame.locals import *
import sys
import random
import nnet
from copy import deepcopy


SCR_HEIGHT = 600
SCR_WIDTH  = 600
SHW_PR_BST = True
GRAVITY    = 10
G_ACC	   = 0.1
GAME_SPEED = 5
W_ACC	   = 0.01
D_POS	   = 50
N_OF_DRAGS = 40
FPS		   = 60
AI 		   = True

class Dragon_model:
	def __init__(self):
		self.dragon = pygame.Rect(B_POS, 50, 40, 30)
		self.dragonY = 200
		self.fitness_score = 0
		self.dead = False
		self.sprite = 0
		self.jumpTime = 0
		self.jumpSpeed = 0
		self.gravity = GRAVITY
		self.points = 0
		self.d_x_srt = 300
		self.d_x_end = 300
		self.d_y = 100
		self.d_top = 100
		self.d_bottom = 100
		self.par = 0
		self.nn = nnet.neural_net(n_inputs=8,nrons=30,n_outputs=1)
	
	def __str__(self):
		return str(self.__dict__)

	def __eq__(self, other):
		return self.__dict__ == other.__dict__

	def flap(self):
		self.jumpTime = 15
		self.gravity = GRAVITY
		self.jumpSpeed = 12				#how much to jump

	def think(self):
		if self.nn.think([self.d_x_srt,
						self.d_x_end,
						(self.d_x_srt+400),
						self.birdY,
						(SCR_HEIGHT-self.birdY),
						self.d_y,
						self.d_top,
						self.d_bottom]) > 0.5:
			self.flap()

class FlappyBird:
	def __init__(self):
		self.dragons = [Dragon_model() for i in range(N_OF_BIRDS)]
		self.screen = pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT))
		self.background = pygame.image.load("assets/background.png").convert()
		self.birdSprites = [pygame.image.load("assets/1.png").convert_alpha(),
							pygame.image.load("assets/2.png").convert_alpha(),
							pygame.image.load("assets/dead.png")]
		self.wallDown = pygame.image.load("assets/bottom.png").convert_alpha()
		self.wallUp = pygame.image.load("assets/top.png").convert_alpha()
		self.pre_champ = pygame.image.load("assets/1.png").convert_alpha()
		self.gap = 130
		self.wallx = 400
		self.wall2x = self.wallx+400
		self.offset = random.randint(0,200)
		self.offset2 = random.randint(0,200)
		self.cls_off = self.offset
		self.generation = 1
		self.pre_gen_scr = 0
		self.pre_best = Dragon_model()
		self.high_scr = 0
		self.alive_count = N_OF_BIRDS
		self.w_speed = WALL_SPEED

	def updateWalls(self):
		self.wallx -= self.w_speed
		self.wall2x-= self.w_speed
		for brd in self.birds:
			if not brd.dead:
				brd.fitness_score+=0.1

		if self.wallx < -self.wallUp.get_width():
			self.wallx = self.wall2x+400
			for brd in self.birds:
				if not brd.dead:
					brd.points += 1
					brd.fitness_score+=5				# reward for points
					self.w_speed+=W_ACC					# wall acceleration
			self.offset = random.randint(20,200)

		elif self.wall2x < -self.wallUp.get_width():
			self.wall2x = self.wallx+400
			for brd in self.birds:
				if not brd.dead:
					brd.points += 1
					brd.fitness_score+=5				# reward for points
					self.w_speed+=W_ACC					# wall acceleration
			self.offset2 = random.randint(0,200)

	def birdUpdate(self):
		for brd in self.birds:
			if brd.jumpTime:
				brd.jumpSpeed -= 1
				brd.birdY -= brd.jumpSpeed
				brd.jumpTime -= 1
			elif brd.birdY < SCR_HEIGHT+10:
				brd.birdY += brd.gravity
				brd.gravity += G_ACC				# gravitational acceleration
			brd.bird[1] = brd.birdY					# for collision detect

		upRect = pygame.Rect(self.wallx+10,
							0 - self.gap - self.offset - 10,
							self.wallUp.get_width()-10,
							self.wallUp.get_height())
		downRect = pygame.Rect(self.wallx+10,
							self.wallUp.get_height() - self.offset + 10,
							self.wallDown.get_width()-10,
							self.wallDown.get_height())
		upRect2 = pygame.Rect(self.wall2x+10,
							0 - self.gap - self.offset2 - 10,
							self.wallUp.get_width()-10,
							self.wallUp.get_height())
		downRect2 = pygame.Rect(self.wall2x+10,
							self.wallUp.get_height() - self.offset2 + 10,
							self.wallDown.get_width()-10,
							self.wallDown.get_height())
		for brd in self.birds:
			if not brd.dead:
				all_dead=False
				if upRect.colliderect(brd.bird):
					brd.dead = True
					brd.gravity=GRAVITY+3
				elif downRect.colliderect(brd.bird):
					brd.dead = True
					brd.gravity=GRAVITY+3
				elif upRect2.colliderect(brd.bird):
					brd.dead = True
					brd.gravity=GRAVITY+3
				elif downRect2.colliderect(brd.bird):
					brd.dead = True
					brd.gravity=GRAVITY+3
				if not 0<brd.bird[1]<SCR_HEIGHT+10:
					brd.dead = True
				if brd.dead:
					self.alive_count-=1
					self.last=brd

		self.birds.sort(key=lambda x: x.fitness_score, reverse=True)

		al_ded=True
		for brd in self.birds:				#check all birds for death
			if not brd.dead:
				al_ded=False
				break

		if self.birds[0].fitness_score>self.high_scr:
					self.pre_best = deepcopy(self.birds[0])
					self.high_scr = self.birds[0].fitness_score

		if al_ded:
			if (not self.last.bird[1]<SCR_HEIGHT+10):
				print("Points:",self.last.points)
				self.pre_gen_scr=self.birds[0].fitness_score
				if AI:
					self.clone_best()
					self.cross_gen()
					self.mutate_b()
					self.mutate_w()
					self.rand_gen()
				for brd in self.birds:
					brd.bird[1] = 50
					brd.birdY = 200
					brd.fitness_score = 0
					brd.dead = False
					brd.points = 0
					brd.gravity = GRAVITY
				self.wallx = 400
				self.wall2x = self.wallx+400
				self.offset = random.randint(0,200)
				self.offset2 = random.randint(0,200)
				self.alive_count = N_OF_BIRDS
				self.generation+= 1
				self.w_speed = WALL_SPEED

	def clone_best(self):
		self.birds.pop()										# 1 to 3
		self.birds.insert(0,Dragon_model())
		self.birds[0]=deepcopy(self.pre_best)
	def cross_gen(self):
		x=3*int(N_OF_BIRDS/10)
		y=4*int(N_OF_BIRDS/10)
		z=5*int(N_OF_BIRDS/10)
		for i in range(x,y):									# 3 to 4
			self.birds[i].nn.w1[:]=self.birds[i-x].nn.w1[:]
			self.birds[i].nn.w2[:]=self.birds[i-x].nn.w2[:]
		for i in range(y,z):									# 4 to 5
			self.birds[i].nn.w1[:]=self.birds[i-y].nn.w1[:]
			self.birds[i].nn.w2[:]=self.birds[i+1-y].nn.w2[:]
		for i in range(z,6*int(N_OF_BIRDS/10)):					# 5 to 6
			self.birds[i].nn.w1[:]=self.birds[i-z].nn.w1[:]
	def mutate_b(self):
		x=6*int(N_OF_BIRDS/10)
		for i in range(x,8*int(N_OF_BIRDS/10)):					# 6 to 8
			self.birds[i].nn.w1[:]=self.birds[i-x].nn.w1[:]
			self.birds[i].nn.w2[:]=self.birds[i-x].nn.w2[:]
			self.birds[i].nn.gen_bias()
	def mutate_w(self):
		x=8*int(N_OF_BIRDS/10)
		for i in range(x,9*int(N_OF_BIRDS/10)):					# 8 to 9
			self.birds[i].nn.b1[:]=self.birds[i-x].nn.b1[:]
			self.birds[i].nn.b2=0
			self.birds[i].nn.b2+=self.birds[i-x].nn.b2
			self.birds[i].nn.gen_w8s()
	def rand_gen(self):
		for i in range(9*int(N_OF_BIRDS/10),int(N_OF_BIRDS)):	# 9 to 10
			self.birds[i].nn.gen_bias()
			self.birds[i].nn.gen_w8s()

	def run(self):
		clock = pygame.time.Clock()
		pygame.font.init()
		font = pygame.font.SysFont("Arial", 20)
		while True:
			clock.tick(FPS)
			for event in pygame.event.get():
				if (event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN):
					for brd in self.birds:
						if not brd.dead:
							brd.flap()
				elif event.type == pygame.QUIT:
					sys.exit()

			self.screen.fill((255, 255, 255))
			self.screen.blit(self.background, (0, 0))
			self.screen.blit(self.background, (395, 0))
			self.screen.blit(self.wallUp,
							(self.wallx, 0 - self.gap - self.offset))
			self.screen.blit(self.wallDown,
							(self.wallx, self.wallUp.get_height() - self.offset))
			self.screen.blit(self.wallUp,
							(self.wall2x, 0 - self.gap - self.offset2))
			self.screen.blit(self.wallDown,
							(self.wall2x, self.wallUp.get_height() - self.offset2))
			
			self.screen.blit(font.render("Points: "+str(self.birds[0].points),
										-1,
										(255, 255, 255)),
							(SCR_WIDTH/3, 20))
			self.screen.blit(font.render("Fit Score: "+str(self.birds[0].fitness_score)[:5],
										-1,
										(255, 255, 255)),
							(SCR_WIDTH/3, 50))
			self.screen.blit(font.render("Best Fit Score: "+str(self.high_scr)[:5],
										-1,
										(255, 255, 255)),
							(SCR_WIDTH/3, 80))
			self.screen.blit(font.render("Generation: "+str(self.generation),
										-1,
										(255, 255, 255)),
							(SCR_WIDTH/1.5, 20))
			self.screen.blit(font.render("Alive: "+str(self.alive_count),
										-1,
										(255, 255, 255)),
							(SCR_WIDTH/1.4, 50))
			self.screen.blit(font.render("Prev Score: "+str(self.pre_gen_scr)[:5],
										-1,
										(255, 255, 255)),
							(SCR_WIDTH/1.5+20, 80))
			
			if self.wallx>0 and self.wall2x>0:
				self.cls_x=min(self.wallx, self.wall2x)
			else:
				self.cls_x=max(self.wallx, self.wall2x)
			if self.cls_x==self.wallx:
				self.cls_off=self.offset
			else:
				self.cls_off=self.offset2
			for brd in self.birds:
				if not brd.dead:
					brd.d_x_srt = (self.cls_x-30-B_POS)
					brd.d_x_end = brd.d_x_srt+self.wallDown.get_width()
					brd.d_bottom = self.wallUp.get_height()-self.cls_off-brd.birdY
					brd.d_top = brd.d_bottom-3-self.gap
					brd.d_y = brd.d_bottom-self.gap/2
					brd.d_bottom-=20
					if AI:
						brd.think()
					brd.sprite = 0
					if brd.jumpTime:
						brd.sprite = 1
				else:
					brd.sprite = 2
				self.screen.blit(self.birdSprites[brd.sprite], (B_POS, brd.birdY))

			self.updateWalls()
			self.birdUpdate()
			pygame.display.update()

if __name__ == "__main__":
	FlappyBird().run()