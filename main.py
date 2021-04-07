import pygame
from math import *
import struct
import sys
import time
import random

import pg3d
import game

def main(argv):
    pygame.init()
    
    pygame.display.set_caption("3D")
    screen = pygame.display.set_mode([1280,720], pygame.RESIZABLE)
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    
    pfont = pygame.font.SysFont("Consolas", 14)

    motionMatrix = { # 1 = in direction, -1 opposite direction, 0 = no motion
        "forward": 0,
        "lateral": 0,
        "vertical": 0,
        "rotational": 0
    }
    
    mspeeed = 2
    
    blist = []
    
    colors = [(230,230,230),(200,200,200),(170,170,170),(140,140,140)]
    
    space = 20
    for cz in range(0, 4):
        for cy in range(0, 4):
            for cx in range(0, 4):
                if (cy) % 2 == 0:
                    if (cy + cz + cx) % 2 == 0:
                        color = colors[0]
                    else:
                        color = colors[1]
                else:
                    if (cy + cz + cx) % 2 == 0:
                        color = colors[2]
                    else:
                        color = colors[3]
                blist.append(game.cell(pg3d.point(cx * space, cy * space, cz * space), 10, color, (cx + cy * 4 + cz * 16)))
    
    light = []
    
    cam = pg3d.camera(pg3d.point(0,0, -75), [0,0,0], pg3d.point(0,0,1000)) #camera object
    s = pg3d.scene(screen, cam, blist, light)
    
    fps = 0
    
    ttt = game.board([game.player("Player 1", (255,0,0)), game.player("Player 2", (0,0,255))])
    
    usernum = 0
    run = True
    while run == True:
        startloop = time.time()
    
        mxcenter = int(screen.get_width()/2)
        mycenter = int(screen.get_height()/2)
        pygame.mouse.set_pos(mxcenter,mycenter)
        
        m = pygame.mouse.get_rel()
        
        if m[0] != 0: #if the mouse moved, move camera
            cam.orientation[1] -= radians(m[0]/10)
        if m[1] != 0:
            cam.orientation[0] -= radians(m[1]/10)
        
    
        for event in pygame.event.get(): #pygame event detection
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    run = False
            
                if event.key == pygame.K_w:
                    motionMatrix["forward"] = 1 * mspeeed
                elif event.key == pygame.K_s:
                    motionMatrix["forward"] = -1 * mspeeed
                elif event.key == pygame.K_a:
                    motionMatrix["lateral"] = 1 * mspeeed
                elif event.key == pygame.K_d:
                    motionMatrix["lateral"] = -1 * mspeeed
                elif event.key == pygame.K_r:
                    motionMatrix["vertical"] = -1 * mspeeed
                elif event.key == pygame.K_f:
                    motionMatrix["vertical"] = 1 * mspeeed
                    
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    motionMatrix["forward"] = 0
                elif event.key == pygame.K_s:
                    motionMatrix["forward"] = 0
                elif event.key == pygame.K_a:
                    motionMatrix["lateral"] = 0
                elif event.key == pygame.K_d:
                    motionMatrix["lateral"] = 0
                elif event.key == pygame.K_r:
                    motionMatrix["vertical"] = 0
                elif event.key == pygame.K_f:
                    motionMatrix["vertical"] = 0
                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                plist = []
            
                for p in s.polygons:
                    if p.insidePolygon2D(s.camera, mxcenter, mycenter, (mxcenter,mycenter)):
                       plist.append(p)
                       
                plist.sort(key = lambda x: x.getDistance(s.camera))
                
                if plist:
                    plist[0].parent.changeColor(ttt.playerlist[usernum].color)
                    validmove = ttt.makeMove(usernum, plist[0].parent.numToBin())
                    
                    if validmove:
                        if ttt.testWin(usernum):
                            print("{} won!".format(ttt.playerlist[usernum].name))
                        
                        usernum ^= 1
                        
                    
            
        #apply camera translation
        s.camera.position.z += motionMatrix["forward"] * cos(cam.orientation[1])
        s.camera.position.x += motionMatrix["forward"] * sin(cam.orientation[1])
        s.camera.position.y -= motionMatrix["forward"] * sin(cam.orientation[0])
        s.camera.position.x += motionMatrix["lateral"] * sin(cam.orientation[1] + radians(90))
        s.camera.position.z += motionMatrix["lateral"] * cos(cam.orientation[1] + radians(90))
        s.camera.position.y += motionMatrix["vertical"]
        
        screen.fill((0,0,0)) #clear for next frame
        
        s.drawPaintedRaster(False) #draw polygons in reverse depth order
        
        frames = pfont.render("{} fps".format(round(fps,1)),True, (255,255,255))
        screen.blit(frames, (10, 10))
        
        
        #draw crosshair
        chsize = 15
        pygame.draw.line(screen, (255, 255, 255), (mxcenter - chsize, mycenter), (mxcenter + chsize, mycenter), 1)
        pygame.draw.line(screen, (255, 255, 255), (mxcenter, mycenter - chsize), (mxcenter, mycenter + chsize), 1)
        
        pygame.display.flip()
        
        #print("{}ms".format((time.time() - startloop) * 100))
        fps = 1/(time.time() - startloop + 0.01)

if __name__ == "__main__":
    main(sys.argv)