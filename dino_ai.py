#!/usr/bin/env python3

import pygame
from pygame.locals import *
import random
import nnet
from copy import deepcopy


SCR_HEIGHT = 250
SCR_WIDTH  = 800
GRAVITY    = 6
GRAV_ACC   = 0.1
GAME_SPEED = 6
GAME_ACC   = 0.1
L_Y 	   = 200
D_POS 	   = 30
D_Y 	   = L_Y-36
OBS_GAP	   = 300
N_OF_DINO  = 40
FPS		   = 60
AI 		   = True

class Dino_model:
	def __init__(self):
		self.dino = pygame.Rect(D_POS, L_Y, 30, 42)
		self.dinoY = L_Y-100
		self.fitness_score = 0
		self.dead = False
		self.sprite = 0
		self.jumpTime = 0
		self.jumpSpeed = 0
		self.gravity = GRAVITY
		self.dk = 0

		self.cls_x = SCR_WIDTH
		self.far_x = SCR_WIDTH
		self.cls_w = 40
		self.cls_h = 40
		self.speed = GAME_SPEED
		
		self.nn = nnet.neural_net(n_inputs=5,nrons=30,n_outputs=2)
	
	def __str__(self):
		return str(self.__dict__)

	def __eq__(self, other):
		return self.__dict__ == other.__dict__

	def jump(self):
		if self.dinoY>=D_Y:
			self.jumpTime = 29
			self.gravity = GRAVITY
			self.jumpSpeed = 16				#how much to jump
	def duck(self):
		if self.dinoY>=D_Y:
			self.dk=1
			self.dino[3]=30

	def think(self):
		out = self.nn.think([self.cls_x,
						self.far_x,
						self.cls_w,
						self.cls_h,
						self.speed])
		if out[0]>0.5:
			self.jump()
		elif out[1]>0.5:
			self.duck()

class obstacle(object):
	def __init__(self, obs_list):
		self.b_y = D_Y
		ind = random.choice(range(6))
		if ind>3:
			self.b_y+=10
		self.ob_img = obs_list[ind]
		self.obx = random.randint(SCR_WIDTH+100,SCR_WIDTH+200)
		self.Rect = pygame.Rect(self.obx,
							self.b_y,
							self.ob_img.get_width()-10,
							self.ob_img.get_height())
class cloud(object):
	def __init__(self, cloud_img):
		self.cloud_img = cloud_img
		self.cloudY = random.randint(15,140)
		self.cloudX = random.randint(SCR_WIDTH,SCR_WIDTH*2)
		self.speed = random.uniform(1,3)

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
		self.cloud_img = pygame.image.load("assets/cloud.png").convert_alpha()
		self.gap = OBS_GAP
		self.obs = [obstacle(self.obs_list) for i in range(2)]
		self.obs[1].obx+=self.gap
		self.clouds = [cloud(self.cloud_img) for i in range(4)]
		self.landx = 0
		self.land_width = self.land.get_width()
		self.land2x = self.land_width
		self.generation = 1
		self.pre_gen_scr = 0
		self.pre_best = Dino_model()
		self.high_scr = 0
		self.alive_count = N_OF_DINO
		self.gm_speed = GAME_SPEED

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
			if self.gm_speed<30:
				self.gm_speed+=GAME_ACC					# wall acceleration
		elif self.land2x < -self.land_width:
			self.land2x=self.landx+self.land_width
			if self.gm_speed<30:
				self.gm_speed+=GAME_ACC					# wall acceleration

	def genClouds(self):
		for i in range(4):
			if self.clouds[i].cloudX<-49:
				self.clouds[i]=cloud(self.cloud_img)
			self.clouds[i].cloudX-=self.clouds[i].speed

	def genObs(self):
		for i in range(2):
			if self.obs[i].obx<-60:
				self.obs[i] = obstacle(self.obs_list)
		diff=abs(self.obs[0].obx-self.obs[1].obx)
		while diff<self.gap:
			if self.obs[0].obx>SCR_WIDTH:
				self.obs[0].obx+=self.gap/2
			else:
				self.obs[1].obx+=self.gap/2
			diff=abs(self.obs[0].obx-self.obs[1].obx)
		self.gap+=GAME_ACC/8

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

		for dno in self.dinos:
			if not dno.dead:
				for oo in self.obs:
					if oo.obx<100:
						oo.Rect[0]=oo.obx+2
						if oo.Rect.colliderect(dno.dino):
							dno.dead = True
							self.alive_count-=1

		self.dinos.sort(key=lambda x: x.fitness_score, reverse=True)

		if self.dinos[0].fitness_score>self.high_scr:
					self.pre_best = deepcopy(self.dinos[0])
					self.high_scr = self.dinos[0].fitness_score

		if not self.alive_count:
				print("Generation",self.generation,":",self.dinos[0].fitness_score)
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
					dno.gravity = GRAVITY
				self.landx = 0
				self.land2x = self.land_width
				self.gap = OBS_GAP
				self.alive_count = N_OF_DINO
				self.generation+= 1
				self.gm_speed = GAME_SPEED
				self.obs = [obstacle(self.obs_list) for i in range(2)]
				self.obs[1].obx+=self.gap

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
		font = pygame.font.SysFont("Arial", 16)
		step=0
		n_exit_game = True
		while n_exit_game:
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
					n_exit_game=False

			self.screen.fill((255, 255, 255))
			self.screen.blit(self.land, (self.landx, L_Y))
			self.screen.blit(self.land, (self.land2x, L_Y))
			for oo in self.obs:
				self.screen.blit(oo.ob_img, (oo.obx, oo.b_y))
				# pygame.draw.rect(self.screen, (140,240,130), Rect((oo.obx,oo.b_y), (oo.ob_img.get_width(),oo.ob_img.get_height())),1)
			for cld in self.clouds:
				self.screen.blit(cld.cloud_img, (cld.cloudX, cld.cloudY))
			self.genClouds()
			self.screen.blit(font.render("Score: "+str(self.dinos[0].fitness_score)[:5],
										-1,
										(110,110,110)),
							(SCR_WIDTH/1.6, 10))
			self.screen.blit(font.render("Prev Score: "+str(self.pre_gen_scr)[:5],
										-1,
										(110,110,110)),
							(SCR_WIDTH/1.6, 40))
			self.screen.blit(font.render("High Score: "+str(self.high_scr)[:5],
										-1,
										(110,110,110)),
							(SCR_WIDTH/1.6, 70))
			self.screen.blit(font.render("Generation: "+str(self.generation),
										-1,
										(110,110,110)),
							(SCR_WIDTH/1.2, 10))
			self.screen.blit(font.render("Alive: "+str(self.alive_count),
										-1,
										(110,110,110)),
							(SCR_WIDTH/1.2, 40))
			if self.obs[0].obx>20:
				dx0=(self.obs[0].obx-40-D_POS)
			else:
				dx0=SCR_WIDTH
			if self.obs[1].obx>20:
				dx1=(self.obs[1].obx-40-D_POS)
			else:
				dx1=SCR_WIDTH
			if dx0<dx1:
				cls_x=dx0
				far_x=dx1
				cls_w=self.obs[0].ob_img.get_width()
				cls_h=self.obs[0].ob_img.get_height()
			else:
				cls_x=dx1
				far_x=dx0
				cls_w=self.obs[1].ob_img.get_width()
				cls_h=self.obs[1].ob_img.get_height()
			for dno in self.dinos:
				if not dno.dead:
					dno.cls_x = cls_x
					dno.far_x = far_x
					dno.cls_w = cls_w
					dno.cls_h = cls_h
					dno.speed = self.gm_speed
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
					self.screen.blit(self.dinomov[dno.sprite], (D_POS, dno.dinoY+DD))#D_POS, L_Y, 30, 42
					# pygame.draw.rect(self.screen, (240,140,130), Rect((D_POS+2,dno.dinoY+DD+2), (self.dinomov[dno.sprite].get_width()-4,self.dinomov[dno.sprite].get_height()-4)),1)

			self.updateLand()
			self.dinoUpdate()
			self.genObs()
			pygame.display.update()

if __name__ == "__main__":
	DinoGame().run()