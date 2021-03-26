import pygame
from math import *
import struct
import sys

def averageOfPoints(points):
    result = point(0,0,0)
    
    for p in points:
        result += p
        
    return result / len(points)
    
def dotProduct(a, b):
    return (a.x * b.x) + (a.y * b.y) + (a.z * b.z)

class camera:
    def __init__(self, position, orientation, surface):
        self.position = position #pinhole
        self.orientation = orientation #angle
        self.surface = surface #film surface RELATIVE TO PINHOLE
        
    def getCartOrientation(self): #This works fine I think
        return point(sin(self.orientation[1]) * cos(self.orientation[0]), sin(self.orientation[1]) * sin(self.orientation[0]), cos(self.orientation[1]))
        
'''
|         |
|   >*<   | surface
|         |
'''    
    
class point: #TODO overload = operator and other arithmetic ones
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        
    def __add__(self, other): #addition/subtraction operators
        return point(self.x + other.x, self.y + other.y, self.z + other.z)
        
    def __sub__(self, other):
        return point(self.x - other.x, self.y - other.y, self.z - other.z)
        
    def __truediv__(self, other): #overload operators for scalar multiplication/division
        return point(self.x / other, self.y / other, self.z / other)
        
    def __mul__(self, other):
        return point(self.x * other, self.y * other, self.z * other)
        
    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        self.z += other.z
        
        return self
        
    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        
        return self
        
    def __imul__(self, other):
        self.x *= other
        self.y *= other
        self.z *= other
        
        return self
        
    def __itruediv__(self, other):
        self.x /= other
        self.y /= other
        self.z /= other
        
        return self
        
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
        
        return (xoffset - bx, by + yoffset)
      
class vector: #or line
    def __init__(self, p1, p2):
        self.p1 = p1
        self.p2 = p2
        
    def draw(self, camera, screen, xoffset, yoffset):
        pr1 = self.p1.project(camera, 0, 0)
        pr2 = self.p2.project(camera, 0, 0)
        pygame.draw.line(screen, (255, 255, 255), (pr1[0] + xoffset, pr1[1] + yoffset), (pr2[0] + xoffset, pr2[1] + yoffset), 1)
        
class triangle:
    def __init__(self, normal, p1, p2, p3):
        self.normal = normal #surface normal vector
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
    
    def rotateX(self, angle): #rotate about X-axis (requires translation to maintain position)
        self.normal = point(self.normal.x, float(self.normal.y * cos(angle) - self.normal.z * sin(angle)), float(self.normal.y * sin(angle) + self.normal.z * cos(angle)))
        for p in self.pointlist:
            ny = float(p.y * cos(angle) - p.z * sin(angle))
            nz = float(p.y * sin(angle) + p.z * cos(angle))
            
            p.y = ny
            p.z = nz
            
    def rotateY(self, angle):
        self.normal = point(float(self.normal.x * cos(angle) + self.normal.z * sin(angle)), self.normal.y, float(self.normal.z * cos(angle) - self.normal.x * sin(angle)))
        for p in self.pointlist:
            nx = float(p.x * cos(angle) + p.z * sin(angle))
            nz = float(p.z * cos(angle) - p.x * sin(angle))
            
            p.x = nx
            p.z = nz
            
    def rotateZ(self, angle):
        self.normal = point(float(self.normal.x * cos(angle) - self.normal.y * sin(angle)), float(self.normal.x * sin(angle) + self.normal.y * cos(angle)), self.normal.z)
        for p in self.pointlist:
            nx = float(p.x * cos(angle) - p.y * sin(angle))
            ny = float(p.x * sin(angle) + p.y * cos(angle))
            
            p.x = nx
            p.y = ny
    
    def facingCamera(self, camera):
        ccart = camera.getCartOrientation()
        if dotProduct(self.normal, ccart) <= 0: #if dot product is negative, surface should be visable
            return True
        else:
            return False
            
    def getCOM(self): #get center of mass
        return averageOfPoints(self.pointlist)
    
    def drawWireframe(self, camera, screen, xoffset, yoffset):
        for v in self.vectlist:
            v.draw(camera, screen, xoffset, yoffset)
            
    def drawRaster(self, camera, screen, xoffset, yoffset, color, cull, shader): #draw triangle using pygame.draw.polygon()
        numdrawn = 0
        
        ppoints = []
        insideView = False
        ssize = screen.get_size()
        
        for p in self.pointlist:
            ppoints.append(p.project(camera, xoffset, yoffset))
            if (ppoints[-1][0] > 0 and ppoints[-1][1] > 0) and (ppoints[-1][0] < ssize[0] and ppoints[-1][1] < ssize[1]):
                insideView = True
            
        if (self.facingCamera(camera) or cull == False) and insideView == True: #draw if not culled and in the camera's FOV
            if (shader != None): #apply shader
                scalar = -cos(shader.getAngle(self))
                
                if (scalar < 0.5):
                    scalar = 0.5
                
                color = (floor(color[0] * scalar), floor(color[0] * scalar), floor(color[0] * scalar))
                #print(color)
            
            pygame.draw.polygon(screen, color, [ppoints[0], ppoints[1], ppoints[2]])
            numdrawn += 1
            
        return numdrawn

class object:
    def __init__(self):
        self.tlist = [] #list of triangles in body
        self.com = point(0,0,0) #center of mass
        
    def readSTL(self, filename): #unpack stl file into object
        try:
            flines = open(filename, 'r').readlines()
        except UnicodeDecodeError:
            flines = [""]
        
        print(flines[0])
        
        normal = point(0,0,0)
        points = []
        psize = 0
        if "solid" in str(flines[0]): #if ASCII file
            for l in flines: 
                if "facet normal" in l:
                    n = l.split()
                    normal = point(float(n[2]), float(n[3]), float(n[4]))
                elif "vertex" in l:
                    v = l.split()
                    p = point(float(v[1]), float(v[2]), float(v[3]))
                    points.append(p)
                    self.com += p
                elif "endfacet" in l:
                    self.tlist.append(triangle(normal, points[0], points[1], points[2]))
                    points.clear()
                    psize += 1
                    
            self.com /= (psize * 3)
    
        else: #if binary instead
            fdata = open(filename, 'rb').read()
            psize = struct.unpack('I', fdata[80:84]) #eat up header and get number of triangles
        
            print(psize)
        
            for i in range(psize[0]):
                entry = struct.unpack('<ffffffffffffH', fdata[84 + 50*i:134 + 50*i])
                print(entry)
                self.tlist.append(triangle(point(entry[0],entry[1],entry[2]), point(entry[3],entry[4],entry[5]), point(entry[6],entry[7],entry[8]), point(entry[9],entry[10],entry[11])))
                self.com.x += (entry[3] + entry[6] + entry[9])
                self.com.y += (entry[4] + entry[7] + entry[10])
                self.com.z += (entry[5] + entry[8] + entry[11])
        
            self.com /= (psize[0] * 3)
        
        print(self.com.x, self.com.y, self.com.z)
    
    def drawWireframe(self, camera, screen, xoffset, yoffset):
        for t in self.tlist:
            t.drawWireframe(camera, screen, xoffset, yoffset)
            
    def drawRaster(self, camera, screen, xoffset, yoffset, color, cull, shader):
        numdrawn = 0
    
        for t in self.tlist:
            numdrawn += t.drawRaster(camera, screen, xoffset, yoffset, color, cull, shader)
            
        return numdrawn
    
    def translate(self, offset): #offset should be a point object
        self.com = self.com + offset #move center of mass with offset
        for t in self.tlist:
            t.move(offset)
            
    def rotate(self, angles): #arg should be array or tuple of three values
        for t in self.tlist:
            t.move(point(-self.com.x,-self.com.y,-self.com.z)) #move center of mass to origin
            t.rotateX(angles[0])
            t.rotateY(angles[1])
            t.rotateZ(angles[2])
            t.move(point(self.com.x,self.com.y,self.com.z)) #move back

class pointSource: #point source of light for shading
    def __init__(self, pos):
        self.pos = pos #point object
        
    def getAngle(self, triangle): #get angle between surface normal and point source
        dv = triangle.getCOM() - self.pos
        n = triangle.normal
        
        return acos(dotProduct(n, dv)/(sqrt(dotProduct(dv, dv)) * sqrt(dotProduct(n, n)))) #return angle
    

def main(argv):
    pygame.init()
    
    pygame.display.set_caption("3D")
    screen = pygame.display.set_mode([1280,720], pygame.RESIZABLE)
    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    
    pfont = pygame.font.SysFont("Consolas", 14)
    
    cam = camera(point(0,0, -200), [0,0,0], point(0,0,1000)) #camera object

    motionMatrix = { # 1 = in direction, -1 opposite direction, 0 = no motion
        "forward": 0,
        "lateral": 0,
        "vertical": 0,
        "rotational": 0
    }
    
    mspeeed = 0.5
    
    blist = []
    
    for n in range(0, len(argv) - 1):
        blist.append(object())
        blist[n].readSTL(argv[n + 1])
        blist[n].rotate((radians(-90),0,0))

    
    #body.rotate((radians(-90),0,0))
    
    light = pointSource(point(10000, 0, 0))
    
    run = True
    while run == True:
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
            
        #apply camera translation
        cam.position.z += motionMatrix["forward"] * cos(cam.orientation[1])
        cam.position.x += motionMatrix["forward"] * sin(cam.orientation[1])
        cam.position.y -= motionMatrix["forward"] * sin(cam.orientation[0])
        cam.position.x += motionMatrix["lateral"] * sin(cam.orientation[1] + radians(90))
        cam.position.z += motionMatrix["lateral"] * cos(cam.orientation[1] + radians(90))
        cam.position.y += motionMatrix["vertical"]
        
        screen.fill((0,0,0)) #clear for next frame
        
        #draw crosshair
        chsize = 15
        pygame.draw.line(screen, (255, 255, 255), (mxcenter - chsize, mycenter), (mxcenter + chsize, mycenter), 1)
        pygame.draw.line(screen, (255, 255, 255), (mxcenter, mycenter - chsize), (mxcenter, mycenter + chsize), 1)
        
        cacoords = pfont.render("({}, {}, {})".format(cam.orientation[0], cam.orientation[1], cam.orientation[2]),True, (255,255,255))
        cccoords = pfont.render("({}, {}, {})".format(cam.getCartOrientation().x, cam.getCartOrientation().y, cam.getCartOrientation().z),True, (255,255,255))
        cloc = pfont.render("({}, {}, {})".format(cam.position.x, cam.position.y, cam.position.z),True, (255,255,255))
        screen.blit(cacoords, (10, 10))
        screen.blit(cccoords, (10, 30))
        screen.blit(cloc, (10, 50))
        
        numdrawn = 0
        for body in blist:
            body.rotate((radians(0),radians(0),radians(0)))
            
            numdrawn += body.drawRaster(cam, screen, mxcenter, mycenter, (255, 255, 255), True, light)
            #body.drawWireframe(cam, screen, mxcenter, mycenter)
        
        print(numdrawn)
        pygame.display.flip()

if __name__ == "__main__":
    main(sys.argv);
