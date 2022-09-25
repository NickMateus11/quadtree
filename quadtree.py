from __future__ import annotations

import pygame
import random
import time


WHITE   = (255, 255, 255)
GRAY    = (100, 100, 100)
BLACK   = (0, 0, 0)
RED     = (255, 0, 0)
GREEN   = (0, 255, 0)


class axis_aligned_bounding_box:
    def __init__(self, c, halfdim):
        self.center = c
        self.halfdim = halfdim
    
    def containsPoint(self, p):
        return abs(self.center[0]-p[0]) <= self.halfdim and abs(self.center[1]-p[1]) <= self.halfdim

    def intersects(self, bound: axis_aligned_bounding_box):
        return abs(self.center[0] - bound.center[0]) < (self.halfdim + bound.halfdim) \
            and abs(self.center[1] - bound.center[1]) < (self.halfdim + bound.halfdim) 

    def asRect(self):
        return pygame.Rect(
            self.center[0]-self.halfdim, 
            self.center[1]-self.halfdim,
            self.halfdim * 2,
            self.halfdim * 2
        )


class QT_InsertionError(Exception):
    pass


class Quadtree_node:

    QT_NODE_CAPACITY = 1

    def __init__(self, center, halfdim):
        self.boundary = axis_aligned_bounding_box(center, halfdim)
        
        self.nw = None
        self.ne = None
        self.sw = None
        self.se = None
        
        self.points = []
    
    def insert(self, p):
        if (not self.boundary.containsPoint(p)):
            return False
        
        if (len(self.points) < self.QT_NODE_CAPACITY and self.nw is None):
            self.points.append(p)
            return True
        
        if (self.nw is None):
            self.subdivide()

        if (self.nw.insert(p)): return True
        if (self.ne.insert(p)): return True
        if (self.sw.insert(p)): return True
        if (self.se.insert(p)): return True

        raise QT_InsertionError

    def query(self, bound_range: axis_aligned_bounding_box):
        points_in_range = []
        
        if (not self.boundary.intersects(bound_range)):
            return points_in_range
        
        if (self.nw is None): 
            for p in self.points:
                if (bound_range.containsPoint(p)):
                    points_in_range.append(p)
        else:
            points_in_range = points_in_range + self.nw.query(bound_range)
            points_in_range = points_in_range + self.ne.query(bound_range)
            points_in_range = points_in_range + self.sw.query(bound_range)
            points_in_range = points_in_range + self.se.query(bound_range)

        return points_in_range


    def subdivide(self):
        cx, cy = self.boundary.center
        new_halfdim = self.boundary.halfdim/2

        self.nw = Quadtree_node((cx-new_halfdim, cy-new_halfdim), new_halfdim)
        self.ne = Quadtree_node((cx+new_halfdim, cy-new_halfdim), new_halfdim)
        self.sw = Quadtree_node((cx-new_halfdim, cy+new_halfdim), new_halfdim)
        self.se = Quadtree_node((cx+new_halfdim, cy+new_halfdim), new_halfdim)

        for p in self.points:
            if (self.nw.insert(p)): continue
            if (self.ne.insert(p)): continue
            if (self.sw.insert(p)): continue
            if (self.se.insert(p)): continue

            raise QT_InsertionError
        
    def asRect(self):
        return pygame.Rect(
            self.boundary.center[0] - self.boundary.halfdim, 
            self.boundary.center[1] - self.boundary.halfdim,
            self.boundary.halfdim * 2,
            self.boundary.halfdim * 2
        )


def draw_quadtree_node(node):
    if node is None:
        return
    
    if (node.nw is not None):
        draw_quadtree_node(node.nw)
        draw_quadtree_node(node.ne)
        draw_quadtree_node(node.sw)
        draw_quadtree_node(node.se)
    else: # only draw leaf nodes - these are the nodes that contain points
        pygame.draw.rect(screen, GRAY, node.asRect(), 1)
    
    return

checks = 0

def main():

    num_points = 1000
    points = [(random.random() * (screen_rect.w-1), random.random() * (screen_rect.h-1)) for _ in range(num_points)]

    quadtree = Quadtree_node(screen_rect.center, screen_rect.width / 2)
    for p in points:
        quadtree.insert(p)

    mouse_bound_dim = 50

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        mx, my = pygame.mouse.get_pos()

        #clear the screen
        screen.fill(BLACK)

        draw_quadtree_node(quadtree)

        for p in points:
            pygame.draw.circle(screen, WHITE, p, 2)

        m_bound = axis_aligned_bounding_box((mx,my), mouse_bound_dim / 2)
        pygame.draw.rect(screen, GREEN, m_bound.asRect(), 1)

        ### Quad tree method
        t1 = time.time()
        query_points = quadtree.query(m_bound)
        t2 = time.time()

        ### naive method
        t3 = time.time()
        query_points = []
        for p in points:
            if m_bound.containsPoint(p):
                query_points.append(p)   
        t4 = time.time()

        for p in query_points:
            pygame.draw.circle(screen, RED, p, 2)

        # print(t2-t1, t4-t3)  
        
        # flip() updates the screen to make our changes visible
        pygame.display.flip()
        
        # maintain framerate
        clock.tick(60)
    
    pygame.quit()


if __name__ == '__main__':
    # initialize pygame
    pygame.init()
    screen_dim = 512
    screen_size = (screen_dim,)*2
    
    # create a window
    screen = pygame.display.set_mode(screen_size)
    screen_rect = screen.get_rect()
    pygame.display.set_caption("pygame Test")
    
    # clock is used to set a max fps
    clock = pygame.time.Clock()  
    
    main()