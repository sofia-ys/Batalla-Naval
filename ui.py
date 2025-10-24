import pygame as pg

pg.init()
pg.font.init() 

# screen setup
scrWidth, scrHeight = 600, 750
scr = pg.display.set_mode((scrWidth, scrHeight))
pg.display.set_caption("Batalla Naval")
clock = pg.time.Clock()

running = True
while running:
    scr.fill(black)