import pygame
from math import *

class camera:
    def __init__(self, position, orientation, surface):
        self.position = position #pinhole
        self.orientation = orientation #angle
        self.surface = surface #film surface RELATIVE TO PINHOLE
        
'''
|         |
|   >*<   | surface
|         |
'''    
    
class point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        
    def project(self, camera): #project point onto 2d camera plane (this fomula from wikipedia.org/wiki/3D_projection)
        cx, cy, cz = camera.position.x, camera.position.y, camera.position.z
        thx, thy, thz = camera.orientation[0], camera.orientation[1], camera.orientation[2]
        ex, ey, ez = camera.surface.x, camera.surface.y, camera.surface.z
        
        x = self.x - cx
        y = self.y - cy
        z = self.z - cz
        
        dx = cos(thy) * (sin(thz) * y + cos(thz) * x) - sin(thy) * z
        dy = sin(thx) * (cos(thy) * z + sin(thy) * (sin(thz) * y + cos(thz) * x)) + cos(thx) * (cos(thz) * y - sin(thz) * x)
        dz = cos(thx) * (cos(thy) * z + sin(thy) * (sin(thz) * y + cos(thz) * x)) - sin(thx) * (cos(thz) * y - sin(thz) * x)
        
        bx = (ez/dz) * dx + ex
        by = (ez/dz) * dy + ey
        
        return (bx, by)
      
class vector: #or line
    def init(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        
        
def main():
    pygame.init()
    
    pygame.display.set_caption("3D")
    screen = pygame.display.set_mode([1280,720], pygame.RESIZABLE)
    
    cam = camera(point(0,0, -20), (0,0,0), point(0,0,-50))
    
    points = []
    
    #draw square of points
    points.append(point(-5,-5,-5))
    points.append(point(-5,-5, 5))
    points.append(point(-5, 5,-5))
    points.append(point(-5, 5, 5))
    points.append(point( 5,-5,-5))
    points.append(point( 5,-5, 5))
    points.append(point( 5, 5,-5))
    points.append(point( 5, 5, 5))
    
    run = True
    while run == True:
        mxcenter = int(screen.get_width()/2)
        mycenter = int(screen.get_height()/2)
    
        for event in pygame.event.get(): #pygame event detection
            if event.type == pygame.QUIT:
                run = False
        
        for p in points:
            pc = p.project(cam)
            print(p.project(cam))
            pygame.draw.circle(screen, (255, 255, 255), (pc[0] + mxcenter, pc[1] + mycenter), 2)
            
        pygame.display.flip()

main()
