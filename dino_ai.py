#!/usr/bin/env python3

import pygame
from pygame.locals import *
import sys
import random
import nnet
from copy import deepcopy


SCR_HEIGHT = 300
SCR_WIDTH  = 800
GRAVITY    = 6
GRAV_ACC   = 0.1
GAME_SPEED = 5
GAME_ACC   = 0.1
L_Y 	   = 200
D_X 	   = 30
D_Y 	   = L_Y-36
N_OF_DINO  = 1
FPS		   = 60
AI 		   = False

class Dino_model:
	def __init__(self):
		self.dino = pygame.Rect(D_X, L_Y, 30, 42)
		self.dinoY = L_Y-100
		self.fitness_score = 0
		self.dead = False
		self.sprite = 0
		self.jumpTime = 0
		self.jumpSpeed = 0
		self.gravity = GRAVITY
		self.points = 0
		self.dk = 0
		self.d_x_srt = 300
		self.d_x_end = 300
		self.d_y = 100
		self.d_top = 100
		self.d_bottom = 100
		self.par = 0
		self.nn = nnet.neural_net(n_inputs=8,nrons=30,n_outputs=2)
	
	def __str__(self):
		return str(self.__dict__)

	def __eq__(self, other):
		return self.__dict__ == other.__dict__

	def jump(self):
		if self.dinoY>=D_Y:
			self.jumpTime = 28
			self.gravity = GRAVITY
			self.jumpSpeed = 15				#how much to jump
	def duck(self):
		if self.dinoY>=D_Y:
			self.dk=1
			self.dino[3]=30

	def think(self):
		out = self.nn.think([self.d_x_srt,
						self.d_x_end,
						(self.d_x_srt+400),
						self.dinoY,
						(SCR_HEIGHT-self.dinoY),
						self.d_y,
						self.d_top,
						self.d_bottom])
		if out[0]> 0.5:
			self.jump()

class obstacle(object):
	def __init__(self, obs_list):
		self.b_y = D_Y
		ind = random.choice(range(6))
		if ind>3:
			self.b_y+=10
		self.ob_img = obs_list[ind]
		self.obx = random.randint(SCR_WIDTH+100,SCR_WIDTH+200)

class DinoGame:
	def __init__(self):
		self.dinos = [Dino_model() for i in range(N_OF_DINO)]
		self.screen = pygame.display.set_mode((SCR_WIDTH, SCR_HEIGHT))
		self.land = pygame.image.load("assets/land.png").convert_alpha()
		self.dinomov = [pygame.image.load("assets/step1.png").convert_alpha(),
							pygame.image.load("assets/step2.png").convert_alpha(),
							pygame.image.load("assets/air.png").convert_alpha(),
							pygame.image.load("assets/dead.png").convert_alpha(),
							pygame.image.load("assets/down1.png").convert_alpha(),
							pygame.image.load("assets/down2.png").convert_alpha()]
		self.obs_list = [pygame.image.load("assets/cac_l2.png").convert_alpha(),
							pygame.image.load("assets/cac_l3.png").convert_alpha(),
							pygame.image.load("assets/cac_l4.png").convert_alpha(),
							pygame.image.load("assets/cac_l.png").convert_alpha(),
							pygame.image.load("assets/cac_s2.png").convert_alpha(),
							pygame.image.load("assets/cac_s.png").convert_alpha()]
		self.landx = 0
		self.land2x = self.land.get_width()
		self.land_width = self.land.get_width()
		self.gap = 400
		self.generation = 1
		self.pre_gen_scr = 0
		self.pre_best = Dino_model()
		self.high_scr = 0
		self.alive_count = N_OF_DINO
		self.gm_speed = GAME_SPEED
		self.obs = [obstacle(self.obs_list) for i in range(2)]
		self.obs[1].obx+=400

	def updateLand(self):
		self.landx -= self.gm_speed
		self.land2x -= self.gm_speed
		for oo in self.obs:
			oo.obx-=self.gm_speed
		for dno in self.dinos:
			if not dno.dead:
				dno.fitness_score+=self.gm_speed/(GAME_SPEED*10) #0.1
		if self.landx < -self.land_width:
			self.landx=self.land2x+self.land_width
			self.gm_speed+=GAME_ACC					# wall acceleration
		elif self.land2x < -self.land_width:
			self.land2x=self.landx+self.land_width
			self.gm_speed+=GAME_ACC					# wall acceleration

	def genObs(self):
		for i in range(len(self.obs)):
			if self.obs[i].obx<-80:
				self.obs[i] = obstacle(self.obs_list)
		diff=abs(self.obs[0].obx-self.obs[1].obx)
		if diff<self.gap:
			print(self.gap,self.gm_speed)
			if self.obs[0].obx>SCR_WIDTH:
				self.obs[0].obx+=self.gap
			else:
				self.obs[1].obx+=self.gap
			diff=abs(self.obs[0].obx-self.obs[1].obx)
		self.gap+=GAME_ACC/5

	def dinoUpdate(self):
		for dno in self.dinos:
			if dno.dk>0:
				dno.dk -= 1
				dno.dino[3] = 42
			if dno.jumpTime:
				dno.jumpSpeed -= 1
				dno.dinoY -= dno.jumpSpeed
				dno.jumpTime -= 1
			elif dno.dinoY < D_Y:
				dno.dinoY += dno.gravity
				dno.gravity += GRAV_ACC				# gravitational acceleration
			dno.dino[1] = dno.dinoY					# for collision detect

		# upRect = pygame.Rect(self.wallx+10,
							# 0 - self.gap - self.offset - 10,
							# self.wallUp.get_width()-10,
							# self.wallUp.get_height())
		# downRect = pygame.Rect(self.wallx+10,
							# self.wallUp.get_height() - self.offset + 10,
		# 					self.wallDown.get_width()-10,
		# 					self.wallDown.get_height())
		# upRect2 = pygame.Rect(self.wall2x+10,
							# 0 - self.gap - self.offset2 - 10,
							# self.wallUp.get_width()-10,
							# self.wallUp.get_height())
		# downRect2 = pygame.Rect(self.wall2x+10,
							# self.wallUp.get_height() - self.offset2 + 10,
		# 					self.wallDown.get_width()-10,
		# 					self.wallDown.get_height())
		# for dno in self.dinos:
		# 	if not dno.dead:
		# 		all_dead=False
		# 		if upRect.colliderect(dno.dino):
		# 			dno.dead = True
		# 			dno.gravity=GRAVITY+3
		# 		elif downRect.colliderect(dno.dino):
		# 			dno.dead = True
		# 			dno.gravity=GRAVITY+3
		# 		elif upRect2.colliderect(dno.dino):
		# 			dno.dead = True
		# 			dno.gravity=GRAVITY+3
		# 		elif downRect2.colliderect(dno.dino):
		# 			dno.dead = True
		# 			dno.gravity=GRAVITY+3
		# 		if not 0<dno.dino[1]<SCR_HEIGHT+10:
		# 			dno.dead = True
		# 		if dno.dead:
		# 			self.alive_count-=1
		# 			self.last=dno

		self.dinos.sort(key=lambda x: x.fitness_score, reverse=True)

		al_ded=True
		for dno in self.dinos:				#check all dinos for death
			if not dno.dead:
				al_ded=False
				break

		if self.dinos[0].fitness_score>self.high_scr:
					self.pre_best = deepcopy(self.dinos[0])
					self.high_scr = self.dinos[0].fitness_score

		if al_ded:
			if (not self.last.dino[1]<SCR_HEIGHT+10):
				print("Points:",self.last.points)
				self.pre_gen_scr=self.dinos[0].fitness_score
				if AI:
					self.clone_best()
					self.cross_gen()
					self.mutate_b()
					self.mutate_w()
					self.rand_gen()
				for dno in self.dinos:
					dno.dino[1] = 50
					dno.dinoY = L_Y-100
					dno.fitness_score = 0
					dno.dead = False
					dno.points = 0
					dno.gravity = GRAVITY
				self.wallx = 400
				self.wall2x = self.wallx+400
				# self.offset = random.randint(0,200)
				# self.offset2 = random.randint(0,200)
				self.alive_count = N_OF_DINO
				self.generation+= 1
				self.gm_speed = GAME_SPEED

	def clone_best(self):
		self.dinos.pop()										# 1 to 3
		self.dinos.insert(0,Dino_model())
		self.dinos[0]=deepcopy(self.pre_best)
	def cross_gen(self):
		x=3*int(N_OF_DINO/10)
		y=4*int(N_OF_DINO/10)
		z=5*int(N_OF_DINO/10)
		for i in range(x,y):									# 3 to 4
			self.dinos[i].nn.w1[:]=self.dinos[i-x].nn.w1[:]
			self.dinos[i].nn.w2[:]=self.dinos[i-x].nn.w2[:]
		for i in range(y,z):									# 4 to 5
			self.dinos[i].nn.w1[:]=self.dinos[i-y].nn.w1[:]
			self.dinos[i].nn.w2[:]=self.dinos[i+1-y].nn.w2[:]
		for i in range(z,6*int(N_OF_DINO/10)):					# 5 to 6
			self.dinos[i].nn.w1[:]=self.dinos[i-z].nn.w1[:]
	def mutate_b(self):
		x=6*int(N_OF_DINO/10)
		for i in range(x,8*int(N_OF_DINO/10)):					# 6 to 8
			self.dinos[i].nn.w1[:]=self.dinos[i-x].nn.w1[:]
			self.dinos[i].nn.w2[:]=self.dinos[i-x].nn.w2[:]
			self.dinos[i].nn.gen_bias()
	def mutate_w(self):
		x=8*int(N_OF_DINO/10)
		for i in range(x,9*int(N_OF_DINO/10)):					# 8 to 9
			self.dinos[i].nn.b1[:]=self.dinos[i-x].nn.b1[:]
			self.dinos[i].nn.b2=0
			self.dinos[i].nn.b2+=self.dinos[i-x].nn.b2
			self.dinos[i].nn.gen_w8s()
	def rand_gen(self):
		for i in range(9*int(N_OF_DINO/10),int(N_OF_DINO)):	# 9 to 10
			self.dinos[i].nn.gen_bias()
			self.dinos[i].nn.gen_w8s()

	def run(self):
		clock = pygame.time.Clock()
		pygame.font.init()
		font = pygame.font.SysFont("Arial", 20)
		step=0
		while True:
			clock.tick(FPS)
			keys=pygame.key.get_pressed()
			for dno in self.dinos:
				if not dno.dead:
					if keys[K_DOWN]:
						dno.duck()
					elif keys[K_UP]:
						dno.jump()
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					sys.exit()

			self.screen.fill((255, 255, 255))
			self.screen.blit(self.land, (self.landx, L_Y))
			self.screen.blit(self.land, (self.land2x, L_Y))
			for oo in self.obs:
				self.screen.blit(oo.ob_img, (oo.obx, oo.b_y))
			# self.screen.blit(self.obstacles[1], (self.land2x, D_Y))
			# self.screen.blit(self.wallDown,
							# (self.wallx, self.wallUp.get_height() - self.offset))
			
			self.screen.blit(font.render("Points: "+str(self.dinos[0].points),
										-1,
										(110,110,110)),
							(SCR_WIDTH/3, 20))
			self.screen.blit(font.render("Fit Score: "+str(self.dinos[0].fitness_score)[:5],
										-1,
										(110,110,110)),
							(SCR_WIDTH/3, 50))
			self.screen.blit(font.render("Best Fit Score: "+str(self.high_scr)[:5],
										-1,
										(110,110,110)),
							(SCR_WIDTH/3, 80))
			self.screen.blit(font.render("Generation: "+str(self.generation),
										-1,
										(110,110,110)),
							(SCR_WIDTH/1.5, 20))
			self.screen.blit(font.render("Alive: "+str(self.alive_count),
										-1,
										(110,110,110)),
							(SCR_WIDTH/1.4, 50))
			self.screen.blit(font.render("Prev Score: "+str(self.pre_gen_scr)[:5],
										-1,
										(110,110,110)),
							(SCR_WIDTH/1.5+20, 80))
			
			# if self.wallx>0 and self.wall2x>0:
				# self.cls_x=min(self.wallx, self.wall2x)
			# else:
				# self.cls_x=max(self.wallx, self.wall2x)
			# if self.cls_x==self.wallx:
				# self.cls_off=self.offset
			# else:
				# self.cls_off=self.offset2
			for dno in self.dinos:
				if not dno.dead:
					# dno.d_x_srt = (self.cls_x-30-D_X)
					# dno.d_x_end = dno.d_x_srt+self.wallDown.get_width()
					# dno.d_bottom = self.wallUp.get_height()-self.cls_off-dno.dinoY
					# dno.d_top = dno.d_bottom-3-self.gap
					# dno.d_y = dno.d_bottom-self.gap/2
					# dno.d_bottom-=20
					N=0
					DD=0
					if AI:
						dno.think()
					if dno.dk:
							N=4
							DD=15
					else:
						N=0
					if dno.jumpTime:
						dno.sprite = 2
					elif step>5:
						dno.sprite = 0+N
						if step>10:
							step=0
					else:
						dno.sprite = 1+N
					step+=1
				else:
					dno.sprite = 3
				self.screen.blit(self.dinomov[dno.sprite], (D_X, dno.dinoY+DD))

			self.updateLand()
			self.dinoUpdate()
			self.genObs()
			pygame.display.update()

if __name__ == "__main__":
	DinoGame().run()