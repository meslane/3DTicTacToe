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
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        
    def draw(self, camera, screen, xoffset, yoffset):
        pr1 = self.p1.project(camera)
        pr2 = self.p2.project(camera)
        pygame.draw.line(screen, (255, 255, 255), (pr1[0] + xoffset, pr1[1] + yoffset), (pr2[0] + xoffset, pr2[1] + yoffset), 1)
        
class triangle:
    def __init__(self, p1, p2, p3):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        
        self.v1 = vector(p1, p2)
        self.v2 = vector(p1, p3)
        self.v3 = vector(p2, p3)
        
    def draw(self, camera, screen, xoffset, yoffset):
        self.v1.draw(camera, screen, xoffset, yoffset)
        self.v2.draw(camera, screen, xoffset, yoffset)
        self.v3.draw(camera, screen, xoffset, yoffset)


def main():
    pygame.init()
    
    pygame.display.set_caption("3D")
    screen = pygame.display.set_mode([1280,720], pygame.RESIZABLE)
    
    cam = camera(point(0,0, -21), [0,0,0], point(0,0,-1000))
    
    points = []
    vects = []
    
    #draw square of points
    points.append(point(-5,-5,-5))
    points.append(point(-5,-5, 5))
    points.append(point(-5, 5,-5))
    points.append(point(-5, 5, 5))
    points.append(point( 5,-5,-5))
    points.append(point( 5,-5, 5))
    points.append(point( 5, 5,-5))
    points.append(point( 5, 5, 5))
    
    vects.append(vector(points[0], points[1]))
    vects.append(vector(points[0], points[4]))
    vects.append(vector(points[0], points[2]))
    vects.append(vector(points[2], points[3]))
    vects.append(vector(points[2], points[6]))
    vects.append(vector(points[6], points[7]))
    vects.append(vector(points[6], points[4]))
    vects.append(vector(points[4], points[5]))
    vects.append(vector(points[5], points[7]))
    vects.append(vector(points[7], points[3]))
    vects.append(vector(points[3], points[1]))
    vects.append(vector(points[1], points[5]))
    
    tr = triangle(point(20, 10, 10), point(10, 20, 10), point(10, 10, 20))
    
    run = True
    while run == True:
        mxcenter = int(screen.get_width()/2)
        mycenter = int(screen.get_height()/2)
    
        for event in pygame.event.get(): #pygame event detection
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    cam.position.z += 5
                elif event.key == pygame.K_s:
                    cam.position.z -= 5
                    
                elif event.key == pygame.K_a:
                    cam.position.x += 5
                elif event.key == pygame.K_d:
                    cam.position.x -= 5
                    
                elif event.key == pygame.K_r:
                    cam.position.y += 5
                elif event.key == pygame.K_f:
                    cam.position.y -= 5
                    
                elif event.key == pygame.K_o:
                    cam.orientation[2] += radians(15)
                elif event.key == pygame.K_u:
                    cam.orientation[2] -= radians(15)
                    
                elif event.key == pygame.K_j:
                    cam.orientation[1] += radians(15)
                elif event.key == pygame.K_l:
                    cam.orientation[1] -= radians(15)
                    
                elif event.key == pygame.K_i:
                    cam.orientation[0] -= radians(15)
                elif event.key == pygame.K_k:
                    cam.orientation[0] += radians(15)
            
        screen.fill((0,0,0))
        for v in vects:
            v.draw(cam, screen, mxcenter, mycenter)
            
        tr.draw(cam, screen, mxcenter, mycenter)
        
        pygame.display.flip()

main()
