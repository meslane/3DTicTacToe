import pygame
from math import *
import struct
import sys
import time
import random

import pg3d
import gui
import game


def mainMenu():
    pass
    
def runGame(screen, ttt, pfont, bfont, cam): #ttt is the board object
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
    
    #cam = pg3d.camera(pg3d.point(0,0, -75), [0,0,0], pg3d.point(0,0,1000)) #camera object
    s = pg3d.scene(screen, cam, blist, light)
    
    fps = 0
    
    #usernum = 0
    locked = True
    run = True
    winner = None
    while run == True:
        startloop = time.time()
    
        mxcenter = int(screen.get_width()/2)
        mycenter = int(screen.get_height()/2)
        
        if locked:
            pygame.mouse.set_pos(mxcenter,mycenter)
            
            m = pygame.mouse.get_rel()
            
            if m[0] != 0 and abs(m[0]) < 300: #if the mouse moved, move camera
                cam.orientation[1] -= radians(m[0]/10)
            if m[1] != 0 and abs(m[1]) < 300:
                cam.orientation[0] -= radians(m[1]/10)
        
    
        for event in pygame.event.get(): #pygame event detection
            if event.type == pygame.QUIT:
                run = False
                sys.exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    locked = False
                    pygame.mouse.set_visible(True)
                    pygame.event.set_grab(False)
                    
                if event.key == pygame.K_SPACE and winner != None:
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
                if locked and winner == None:
                    plist = []
                    
                    for p in s.polygons: #get closest polygon to mouse
                        if p.insidePolygon2D(s.camera, mxcenter, mycenter, (mxcenter,mycenter)):
                           plist.append(p)
                           
                    plist.sort(key = lambda x: x.getDistance(s.camera))
                    
                    if plist and ttt.currentPlayer.type == 0: #if it is a human's turn
                        #validmove = ttt.makeMove(usernum, plist[0].parent.numToBin())
                        validmove = ttt.currentPlayer.makeMove(plist[0].parent.numToBin())
                        
                        if validmove:
                            plist[0].parent.changeColor(ttt.currentPlayer.color)
                            plist[0].parent.occupied = True
                            
                            if ttt.testWin():
                                winner = ttt.currentPlayer
                                
                            #print(ttt.playerlist[usernum].numWinningMoves(ttt))
                            '''
                            if usernum == len(ttt.playerlist) - 1:
                                usernum = 0
                            else:
                                usernum += 1
                            '''
                            ttt.gotoNextPlayer()
                                
                else:
                    locked = True
                    pygame.mouse.set_visible(False)
                    pygame.event.set_grab(True)
                    
        
        if ttt.currentPlayer.type == 1 and winner == None: #if it is a bot's turn
            cellNum = ttt.currentPlayer.doRandomMove()
            blist[cellNum].occupied = True
            blist[cellNum].changeColor(ttt.currentPlayer.color)
            
            if ttt.testWin():
                winner = ttt.currentPlayer
            
            '''
            if usernum == len(ttt.playerlist) - 1:
                usernum = 0
            else:
                usernum += 1
            '''
            ttt.gotoNextPlayer()
                
        if ttt.boardstate == 0xffffffffffffffff and winner == None:
            winner = False
        
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
        
        if winner == None:
            toptext = bfont.render("{}'s Turn".format(ttt.currentPlayer.name), True, ttt.currentPlayer.color)
        else:
            if winner == False:
                toptext = bfont.render("Draw", True, (255, 255, 255))
            else:
                toptext = bfont.render("{} Wins!".format(winner.name), True, winner.color)
            
            bottomtext = bfont.render("Press SPACE to Continue", True, (255, 255, 255))
            brect = bottomtext.get_rect(center = (mxcenter, screen.get_height() - 25))
            screen.blit(bottomtext, brect)
        
        trect = toptext.get_rect(center = (mxcenter, 25))
        screen.blit(frames, (10, 10))
        screen.blit(toptext, trect)
        
        #draw crosshair
        chsize = 15
        pygame.draw.line(screen, (255, 255, 255), (mxcenter - chsize, mycenter), (mxcenter + chsize, mycenter), 1)
        pygame.draw.line(screen, (255, 255, 255), (mxcenter, mycenter - chsize), (mxcenter, mycenter + chsize), 1)
        
        pygame.display.flip()
        
        #print("{}ms".format((time.time() - startloop) * 100))
        fps = 1/(time.time() - startloop + 0.01)

def main(argv):
    pygame.init()
    
    pygame.display.set_caption("3D Tic Tac Toe")
    screen = pygame.display.set_mode([1280,720], pygame.RESIZABLE)
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    
    pfont = pygame.font.SysFont("Consolas", 14)
    bfont = pygame.font.SysFont("Arial", 32)
    
    cam = pg3d.camera(pg3d.point(0,0, -75), [0,0,0], pg3d.point(0,0,1000))
    
    #while True:
        #ttt = game.board([game.bot("Player 1", (255,0,0)), game.bot("Player 2", (0,0,255)), game.bot("Player 3", (0,255,0)), game.bot("Player 4", (255,255,0))], 0)
        #runGame(screen, ttt, pfont, bfont, cam)
        
    ttt = game.board([game.bot("Player 1", (255,0,0)), game.bot("Player 2", (0,0,255)), game.bot("Player 3", (0,255,0)), game.bot("Player 4", (255,255,0))], 0)
    print("start tree creation")
    ttt.createChildTree(4)
    print("finish tree creation")

if __name__ == "__main__":
    main(sys.argv)