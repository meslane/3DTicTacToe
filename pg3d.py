import pygame
from math import *
import struct
import sys

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
        
    def project(self, camera, xoffset, yoffset): #project point onto 2d camera plane (this formula from wikipedia.org/wiki/3D_projection)
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
        
        return (bx + xoffset, by + yoffset)
      
class vector: #or line
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        
    def draw(self, camera, screen, xoffset, yoffset):
        pr1 = self.p1.project(camera, 0, 0)
        pr2 = self.p2.project(camera, 0, 0)
        pygame.draw.line(screen, (255, 255, 255), (pr1[0] + xoffset, pr1[1] + yoffset), (pr2[0] + xoffset, pr2[1] + yoffset), 1)
        
class triangle:
    def __init__(self, p1, p2, p3):
        self.pointlist = []
        self.vectlist = []
        
        self.pointlist.append(p1)
        self.pointlist.append(p2)
        self.pointlist.append(p3)
        
        self.vectlist.append(vector(p1, p2))
        self.vectlist.append(vector(p1, p3))
        self.vectlist.append(vector(p2, p3))
        
    def move(self, offset):
        for p in self.pointlist:
            p.x += offset.x
            p.y += offset.y
            p.z += offset.z
            
        self.vectlist[0] = vector(self.pointlist[0], self.pointlist[1])
        self.vectlist[1] = vector(self.pointlist[0], self.pointlist[2])
        self.vectlist[2] = vector(self.pointlist[1], self.pointlist[2])
    
    '''    
    def rotate(self, center, direction, angle): #TODO fix: objects don't seem to revolve around their COM if rotated about y (seems like x needs to be made negative?)
        a = center.x
        b = center.y
        c = center.z
        
        u = direction[0]
        v = direction[1]
        w = direction[2]
        
        L = u ** 2 + v ** 2 + w ** 2
        
        for p in self.pointlist:
            p.x = ((a * (v ** 2 + w ** 2) - u * (b * v + c * w - u * p.x - v * p.y - w * p.z)) * (1 - cos(angle)) + L * p.x * cos(angle) + sqrt(L) * (-c * v + b * w - w * p.y + v * p.z) * sin(angle))/L
            p.y = ((b * (u ** 2 + w ** 2) - v * (a * u + c * w - u * p.x - v * p.y - w * p.z)) * (1 - cos(angle)) + L * p.y * cos(angle) + sqrt(L) * (c * u - a * w + w * p.x - u * p.z) * sin(angle))/L
            p.z = ((c * (u ** 2 + v ** 2) - w * (a * u + b * v - u * p.x - v * p.y - w * p.z)) * (1 - cos(angle)) + L * p.z * cos(angle) + sqrt(L) * (-b * u - a * v - v * p.x + u * p.y) * sin(angle))/L
            
        self.vectlist[0] = vector(self.pointlist[0], self.pointlist[1])
        self.vectlist[1] = vector(self.pointlist[0], self.pointlist[2])
        self.vectlist[2] = vector(self.pointlist[1], self.pointlist[2])
    '''
    
    def rotateX(self, angle): #rotate about X-axis (requires translation to maintain position)
        for p in self.pointlist:
            p.y = p.y * cos(angle) - p.z * sin(angle)
            p.z = p.y * sin(angle) + p.z * cos(angle)
            
    def rotateY(self, angle):
        for p in self.pointlist:
            p.x = p.x * cos(angle) + p.z * sin(angle)
            p.z = p.z * cos(angle) - p.x * sin(angle)
            
    def rotateZ(self, angle):
        for p in self.pointlist:
            p.x = p.x * cos(angle) - p.y * sin(angle)
            p.y = p.x * sin(angle) + p.y * cos(angle)
        
    def drawWireframe(self, camera, screen, xoffset, yoffset):
        for v in self.vectlist:
            v.draw(camera, screen, xoffset, yoffset)
            
    def drawRaster(self, camera, screen, xoffset, yoffset, color): #draw triangle using pygame.draw.polygon()
        pygame.draw.polygon(screen, color, [self.pointlist[0].project(camera, xoffset, yoffset), self.pointlist[1].project(camera, xoffset, yoffset), self.pointlist[2].project(camera, xoffset, yoffset)])

class object:
    def __init__(self, triangles):
        self.tlist = triangles #list of triangles
        self.com = point(0,0,0) #center of mass
        
    def readSTL(self, filename): #unpack stl file into object
        fdata = open(filename, 'rb').read()
        psize = struct.unpack('I', fdata[80:84]) #eat up header and get number of triangles
    
        print(psize)
    
        for i in range(psize[0]):
            entry = struct.unpack('<ffffffffffffH', fdata[84 + 50*i:134 + 50*i])
            print(entry)
            self.tlist.append(triangle(point(entry[3],entry[4],entry[5]), point(entry[6],entry[7],entry[8]), point(entry[9],entry[10],entry[11])))
            self.com.x += (entry[3] + entry[6] + entry[9])
            self.com.y += (entry[4] + entry[7] + entry[10])
            self.com.z += (entry[5] + entry[8] + entry[11])
            
        self.com.x /= (psize[0] * 3)
        self.com.y /= (psize[0] * 3)
        self.com.z /= (psize[0] * 3)
        
        print(self.com.x, self.com.y, self.com.z)
    
    def drawWireframe(self, camera, screen, xoffset, yoffset):
        for t in self.tlist:
            t.drawWireframe(camera, screen, xoffset, yoffset)
            
    def drawRaster(self, camera, screen, xoffset, yoffset, color):
        for t in self.tlist:
            t.drawRaster(camera, screen, xoffset, yoffset, color)
    
    def translate(self, offset): #offset should be a point object
        for t in self.tlist:
            t.move(offset)
    
    def rotateX(self, angle):
        for t in self.tlist:
            t.move(point(-self.com.x,-self.com.y,-self.com.z))
            t.rotateX(angle)
            t.move(point(self.com.x,self.com.y,self.com.z))
            
    def rotateY(self, angle):
        for t in self.tlist:
            t.move(point(-self.com.x,-self.com.y,-self.com.z))
            t.rotateY(angle)
            t.move(point(self.com.x,self.com.y,self.com.z))
            
    def rotateZ(self, angle):
        for t in self.tlist:
            t.move(point(-self.com.x,-self.com.y,-self.com.z))
            t.rotateZ(angle)
            t.move(point(self.com.x,self.com.y,self.com.z))
            
    def rotate(self, angles): #arg should be array or tuple of three values
        for t in self.tlist:
            t.move(point(-self.com.x,-self.com.y,-self.com.z)) #move center of mass to origin
            t.rotateX(angles[0])
            t.rotateY(angles[1])
            t.rotateZ(angles[2])
            t.move(point(self.com.x,self.com.y,self.com.z))

def main(argv):
    pygame.init()
    
    pygame.display.set_caption("3D")
    screen = pygame.display.set_mode([1280,720], pygame.RESIZABLE)
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    
    cam = camera(point(0,0, -200), [0,0,0], point(0,0,-1000)) #camera object
    
    points = []
    vects = []

    motionMatrix = { # 1 = in direction, -1 opposite direction, 0 = no motion
        "forward": 0,
        "lateral": 0,
        "vertical": 0,
        "rotational": 0
    }
    
    mspeeed = 0.5
    
    body = object([])
    body.readSTL(argv)
    
    run = True
    while run == True:
        mxcenter = int(screen.get_width()/2)
        mycenter = int(screen.get_height()/2)
        pygame.mouse.set_pos(mxcenter,mycenter)
        
        m = pygame.mouse.get_rel()
        
        if m[0] != 0: #if the mouse moved, move camera
            cam.orientation[1] -= radians(m[0]/10)
        if m[1] != 0:
            cam.orientation[0] += radians(m[1]/10)
        
    
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
                    motionMatrix["vertical"] = 1 * mspeeed
                elif event.key == pygame.K_f:
                    motionMatrix["vertical"] = -1 * mspeeed
                    
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
            
        #apply camera translation
        cam.position.z += motionMatrix["forward"] * cos(cam.orientation[1])
        cam.position.x += motionMatrix["forward"] * sin(cam.orientation[1])
        cam.position.y -= motionMatrix["forward"] * sin(cam.orientation[0])
        cam.position.x += motionMatrix["lateral"] * sin(cam.orientation[1] + radians(90))
        cam.position.z += motionMatrix["lateral"] * cos(cam.orientation[1] + radians(90))
        cam.position.y += motionMatrix["vertical"]
        
        screen.fill((0,0.1,0)) #clear for next frame
        
        #draw crosshair
        chsize = 15
        pygame.draw.line(screen, (255, 255, 255), (mxcenter - chsize, mycenter), (mxcenter + chsize, mycenter), 1)
        pygame.draw.line(screen, (255, 255, 255), (mxcenter, mycenter - chsize), (mxcenter, mycenter + chsize), 1)
        
        #body.rotate(point(-45,50,10), [0, 0, 1], radians(0.1))
        body.rotate((radians(0.1),radians(0.1),radians(0)))
        body.drawRaster(cam, screen, mxcenter, mycenter, (255, 255, 255))
        
        pygame.display.flip()

if __name__ == "__main__":
    main(sys.argv[1])
