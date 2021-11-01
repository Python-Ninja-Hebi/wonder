from __future__ import annotations
from Box2D.Box2D import b2Body, b2Contact, b2ContactImpulse, b2Fixture, b2RevoluteJoint #forward references

import pygame
from pygame import Color, surface, color, Rect
from pygame.math import Vector2, Vector3
from pygame.font import Font

import random
import math

from typing import Dict, List, OrderedDict, Set, Optional, Union, Tuple, Any, Type
import traceback

from Box2D import b2World, b2ContactListener, b2_dynamicBody, b2_staticBody, b2_kinematicBody, b2Vec2, b2PolygonShape, b2DistanceJoint, b2AABB, b2QueryCallback
from pygame.surface import Surface

MAROON = (128, 0, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
OLIVE = (128, 128, 0)
GREEN = (0, 128, 0)
PURPLE = (128, 0, 128)
FUCHSIA = (255, 0, 255)
LIME = (0, 255, 0)
TEAL = (0, 128, 128)
AQUA = (0, 255, 255)
BLUE = (0, 0, 255)
NAVY = (0, 0, 128)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
DARKGRAY = (169,169,169)
SILVER = (192, 192, 192)
WHITE = (255, 255, 255)

# ----- central game engine systems ----

class MixinGameSystem:
    def on_load_scene(self, scene:Scene):
        pass

    def on_start_load_scene(self):
        pass

    def on_add_gameobject(self, gameobject:GameObject, layer:str)->None:
        pass

    def on_remove_gameobject(self, gameobject:GameObject)->None:
        pass

# ----- gameobject and scene system ----

class MixinUpdate:
    def update(self, delta_time:float):
        pass

    def late_update(self):
        pass

class MixinDraw:
    def draw(self, screen:pygame.Surface):
        pass

class Transform:
    def __init__(self):
        self.position:Vector2 = Vector2(0.0, 0.0)
        self.rotation:float = 0.0
        self.scale:Vector2 = Vector2(1.0, 1.0)

    def translate(self,v:Vector2)->None:
        self.position = self.position + v

class Component(MixinUpdate):
    def __init__(self, gameobject:GameObject):
        self.gameobject = gameobject

class GameObject(MixinUpdate):
    def __init__(self):
        self.transform:Transform = Transform()
        self.components = []

    def add(self, component:Component):
        self.components.append(component)
        return component

    def on_collision_enter(self, collider:GameObject, impulse:b2ContactImpulse)->None:
        pass

    def on_trigger_enter(self, collider:GameObject)->None:
        pass

    def get_component(self, classinfo):
        r = None
        for c in self.components:
            if isinstance(c,classinfo):
                r = c
        return r

class Scene:
    def __init__(self) -> None:
        self.init()

    def init(self)->None:
        self.name = ""
        self.background_color = BLACK

        self.dont_destroy_on_load_list = []
        self.layers = OrderedDict()
        self.layers['default'] = []

    def create(self)->None:
        pass

    def add(self, gameobject:GameObject, layer:str='default')->GameObject:
        self.layers[layer].append(gameobject)
        Game.instance.on_add_gameobject(self, gameobject, layer)
        return gameobject

    def add_layer(self, name, to_bottom=False, to_top=False):
        if not name in self.layers:
            self.layers[name] = []
        if to_bottom:
            self.layers.move_to_end(name, last=False)
        if to_top:
            self.layers.move_to_end(name, last=True)

    def dont_destroy_on_load(self, gameobject:GameObject, layer:str='default')->None:
        self.dont_destroy_on_load_list.append((gameobject, layer))




class SceneSystem(MixinGameSystem):
    def __init__(self, scenes) -> None:
        self.current_scene:Scene = None
        self.current_scene_index:int = 0

        if not isinstance(scenes, list):
            scenes = [scenes]
        self.scenes:List[Scene] = scenes

    def load_scene(self, scene_index:int) -> None:

        dont_destroy_list = []
        if self.current_scene:
            dont_destroy_list = self.current_scene.dont_destroy_on_load_list.copy()

        scene = self.scenes[scene_index]
        self.current_scene = scene
        self.current_scene_index = scene_index
        scene.init()

        for g in dont_destroy_list:
            scene.add(g[0],layer=g[1])
            scene.dont_destroy_on_load(g[0],layer=g[1])

        scene.create()

        Game.instance.background_color = self.current_scene.background_color
        Game.instance.name = self.current_scene.name

    def on_remove_gameobject(self, gameobject: GameObject) -> None:
        if self.current_scene:
            for l in  self.current_scene.layers:
                if gameobject in self.current_scene.layers[l]:
                    self.current_scene.layers[l].remove(gameobject)

            
        
class ObserverSet:
    def __init__(self,typeinfo) -> None:
        self.typeinfo = typeinfo
        self.items:Set = None

    def init(self, scene:Scene)->None:
        self.items = set()
        for l in scene.layers:
            for g in scene.layers[l]:
                self.add(g)
                
    def add(self, gameobject:GameObject)->None:
        if isinstance(gameobject, self.typeinfo):
            self.items.add(gameobject)
        for c in gameobject.components:
            if isinstance(c, self.typeinfo):
                self.items.add(c)
    
    def remove(self, gameobject:GameObject)->None:
        if isinstance(gameobject,self.typeinfo):
            if gameobject in self.items: self.items.remove(gameobject)
        for c in gameobject.components:
            if isinstance(gameobject, self.typeinfo):
                if c in self.items: self.items.remove(c)


class ObserverOrderedDict:
    def __init__(self, typeinfo) -> None:
        self.typeinfo = typeinfo
        self.layers:OrderedDict = None

    def init(self, scene:Scene)->None:
        self.layers = OrderedDict()
        for layer_key, layer_value in scene.layers.items():
            self.layers[layer_key] = set()
            for g in layer_value:
                self.add(g, layer_key)
                
    def add(self, gameobject:GameObject, layer:str)->None:
        if isinstance(gameobject, self.typeinfo):
            self.layers[layer].add(gameobject)
        for c in gameobject.components:
            if isinstance(c, self.typeinfo):
                self.layers[layer].add(c)

    def remove(self, gameobject:GameObject)->None:
        if isinstance(gameobject,self.typeinfo):
            for l in self.layers:
                if gameobject in self.layers[l]: self.layers[l].remove(gameobject)
        for c in gameobject.components:
            if isinstance(c, self.typeinfo):
                for l in self.layers:
                    if c in self.layers[l]: self.layers[l].remove(c)


# ----- event system ----
class MixinEvent:
    def on_event(self, event:pygame.eventtype)->None:
        pass

class EventSystem(MixinGameSystem):
    def __init__(self) -> None:
        self.observer = ObserverSet(MixinEvent)

    def on_event(self, event:pygame.eventtype)->None:
        #print(event,self.observer.items)
        for o in self.observer.items:
            o.on_event(event)

    def on_load_scene(self, scene:Scene):
        self.observer.init(scene)

    def on_add_gameobject(self, gameobject: GameObject, layer: str) -> None:
        self.observer.add(gameobject)

    def on_remove_gameobject(self, gameobject: GameObject) -> None:
        self.observer.remove(gameobject)

# ----- render system ----

import os

class SpriteRenderer(Component,MixinDraw):
    def __init__(self, gameobject, image:pygame.Surface = None, load_from_file:str = None, animator:Animator=None, scale:Vector2=None):
        super().__init__(gameobject)

        self._image = None

        if image:
            self._image = image

        if load_from_file:
            #print('current directory', os.getcwd())
            self._image = pygame.image.load(load_from_file)

        self.animator = animator

        if scale:
            if self.animator:
                self.animator.scale(scale)
            else:
                new_size = Vector2(self.image.get_width()*scale.x,self.image.get_height()*scale.y)
                self._image = pygame.transform.scale(self.image, (int(new_size.x), int(new_size.y))) 

        self._rect = self.image.get_rect()

    @property
    def image(self)->Surface:
        if self.animator:
            return self.animator.image
        else:
            return self._image

    @image.setter
    def image(self,v:Surface)->None:
        self._image = v
        self._rect = self._image.get_rect()

    @property
    def rect(self) -> pygame.Rect:
        self._rect.center = self.gameobject.transform.position
        return self._rect

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)
        #print("SpriteRenderer.draw")


class LineRenderer(Component,MixinDraw):
    def __init__(self, gameobject: GameObject, positions:List[Vector2], width:int=1, color:color=GREEN, loop:bool=False, 
                 use_world_space:bool = False):
        super().__init__(gameobject)

        self.width:int = width
        self.color:color = color
        self.loop:bool = loop

        self.positions:List[Vector2]=positions

        self._last_pos = None
        self._last_rot = None
        self.points = []

        if use_world_space:
            for i,n in enumerate(self.positions):
                self.positions[i] = self.positions[i] - self.gameobject.transform.position


    def draw(self, screen: pygame.Surface):
        pos = self.gameobject.transform.position
        rot = self.gameobject.transform.rotation
        #print(f'LineRenderer.draw pos {pos} {self._last_pos} rot {rot} {self._last_rot}')
        if self._last_pos != pos or self._last_rot != rot:
            self.points = [Vector2(x.x*math.cos(rot)-x.y*math.sin(rot),
                                   x.x*math.sin(rot)+x.y*math.cos(rot)) for x in self.positions]
            self.points = [x+pos for x in self.points]
            
            #print(f'LineRender changed')
            self._last_pos = Vector2(pos.x,pos.y)
            self._last_rot = rot

        if self.loop:
            pygame.draw.polygon(screen, self.color, self.points, self.width)


class RenderSystem(MixinGameSystem):
    def __init__(self) -> None:
        self.observer = ObserverOrderedDict(MixinDraw)

    def on_load_scene(self, scene: Scene):
        self.observer.init(scene)
    
    def on_add_gameobject(self, gameobject: GameObject, layer: str) -> None:
        self.observer.add(gameobject, layer)
    
    def on_remove_gameobject(self, gameobject: GameObject) -> None:
        self.observer.remove(gameobject)

    def draw(self, screen:pygame.Surface)->None:
        for layer_key, layer_value in self.observer.layers.items():
            for c in layer_value:
                c.draw(screen)

class AnimationClip:
    def __init__(self,file_name:str, duration:int) -> None:
        self.duration = duration
        self.image = pygame.image.load(file_name)

    def scale(self, v:Vector2)->None:
        new_size = Vector2(self.image.get_width()*v.x,self.image.get_height()*v.y)
        self.image = pygame.transform.scale(self.image, (int(new_size.x), int(new_size.y))) 

class AnimationState:
    def __init__(self, name:str, clips:List[AnimationClip]) -> None:
        self.name = name
        self.clips = clips

        self.length = 0
        for c in self.clips:
            self.length += c.duration

        self.duration_dif = 0
        self.clip = 0
    
    def scale(self, v:Vector2)->None:
        for c in self.clips:
            c.scale(v)

    def update(self, delta_time:float)->None:
        self.duration_dif += delta_time * 1000
        while self.duration_dif > self.clips[self.clip].duration:
            self.duration_dif -= self.clips[self.clip].duration
            self.clip += 1
            if self.clip >= len(self.clips):
                self.clip = 0

    @property
    def image(self)->Surface:
        return self.clips[self.clip].image


class Animator(Component):
    def __init__(self, gameobject: GameObject, states:List[AnimationState],start_state:str):
        super().__init__(gameobject)

        self.states = {}
        for c in states:
            self.states[c.name] = c

        self.start_state = start_state
        self.state = self.start_state

    def scale(self, v:Vector2)->None:
        for c in self.states.items():
            c.scale(v)

    @property
    def image(self)->Surface:
        return self.states[self.state].image

    def update(self, delta_time: float)->None:
        self.states[self.state].update(delta_time)

# ----- particle system ----

class Particle:
    def __init__(self,image:Surface = None,
                 position:Vector2 = None,
                 velocity:Vector2 = Vector2(1,1),
                 angle:float = 1,
                 angle_velocity:float = 0,
                 color:pygame.Color = YELLOW,
                 size:float = 1.0,
                 time:float = 1.0) -> None:
        self.image:Surface = image
        self.rect:pygame.Rect = self.image.get_rect()
        self.position:Vector2 = position
        self.velocity:Vector2 = velocity
        self.angle:float = angle
        self.angle_velocity:float = angle_velocity
        self.color:pygame.Color = color
        self.size:float = size
        self.time:float = time


class ParticleSystem(Component, MixinDraw):
    """
    duration .. length of time the system runs
    looping	.. if enabled, the system starts again at the end of its duration time
    Start Lifetime	.. initial lifetime for particles
    start_speed	.. initial speed for particles
    Start Size  .. initial size for particles
    Start Rotation 	The initial rotation angle of each particle.
    Start Color	The initial color of each particle.
    force .. gravity or other force
    Max Particles	The maximum number of particles in the system at once. If the limit is reached, some particles are removed.
    start_range_from .. angle for start begins
    start_range_to .. angle for start ends
    image .. image of the particles
    rate_over_time .. number of particles emitted per second
    """
    def __init__(self, gameobject: GameObject, duration:float=1.0, looping:bool=True, image=None, 
                 rate_over_time:float=1.0, force:Vector2=Vector2(0,0), start_speed:float=10,
                 start_range_from:float=0, start_range_to:float = 0):
        super().__init__(gameobject)
        self.duration:float = duration
        self.looping:bool = looping
        self.active = True
        self.particles = []
        self.image = image
        self.rate_over_time = rate_over_time
        self.next_emit = 1 / self.rate_over_time
        self.force = force
        self.start_speed = start_speed
        self.start_range_from = start_range_from
        self.start_range_to = start_range_to
        self.append_particle()

    def append_particle(self):
        a = random.uniform(self.start_range_from,self.start_range_to)
        v = Vector2(math.cos(a)*self.start_speed,math.sin(a)*self.start_speed)
        self.particles.append(Particle(image=self.image, 
                   position=self.gameobject.transform.position, time=8, velocity=v))

    def update(self, delta_time: float):
        if not self.active: return

        if not self.looping:
            self.duration -= delta_time
            if self.duration <= 0:
                self.active = False
                return
        
        self.next_emit -= delta_time
        if self.next_emit <= 0:
            self.append_particle()
            self.next_emit = 1 / self.rate_over_time
        remove_list = []

        for i in self.particles:
            i.velocity += self.force * delta_time
            i.position += i.velocity * delta_time
            i.time -= delta_time
            if i.time <= 0:
                remove_list.append(i)
        
        for i in remove_list:
            self.particles.remove(i)


    def draw(self, screen: pygame.Surface):
        if not self.active: return

        for i in self.particles:
            i.rect.center = i.position
            screen.blit(i.image,i.rect)

# ----- tile system ----    
class TilePaletteItem:
    def __init__(self, id:int, tile_type:str, image:Surface, tile_controller_class:Type[TileController]=None) -> None:
        self.id:int = id
        self.tile_type = tile_type
        self.image:Surface = image
        self.tile_controller_class = tile_controller_class

class Tile:
    def __init__(self,tile_palette:TilePaletteItem) -> None:
        self.tile_palette:TilePaletteItem = tile_palette
        self.visible:bool = True
        self._image:Surface = None
        self.controller:TileController = None
        if tile_palette.tile_controller_class:
            self.controller = tile_palette.tile_controller_class(self)
        self._position:Vector2=None
        self.layer:TileMapLayer = None

    @property
    def image(self)->Surface:
        if self._image:
            return self._image
        return self.tile_palette.image

    @image.setter
    def image(self, value:Surface)->None:
        self._image = value

    def get_position(self)->Vector2:
        return self._position

    def set_position(self, value:Vector2)->None:
        self.layer.tile_map.set_tile(self,value,self.layer.id)

    def has_type(self, tile_type:str)->bool:
        return self.tile_palette.tile_type == tile_type



class TileController(MixinUpdate):
    def __init__(self, tile:Tile) -> None:
        self.tile:Tile = tile

    def get_position(self)->Vector2:
        return self.tile.position

    def set_position(self,value:Vector2)->None:
        self.tile.set_position(value)

    def get_tile(self, pos:Vector2)->Tile:
        return self.tile.layer.tile_map.get_tile(pos)

    

class TileMapRenderer(Component,MixinDraw):
    def __init__(self, gameobject: GameObject):
        super().__init__(gameobject)
        self.tilemap:TileMap = gameobject

    def draw(self, screen):
        min_x = 0
        max_x = self.tilemap.width
        min_y = 0
        max_y = self.tilemap.height

        pos = self.tilemap.transform.position

        #if Game.instance.camera and not self._all:
        #    c = self.gameobject.world_to_cell(Game.instance.camera.transform.position)
        #    min_x = max(0,int(c.x - self._half_width))
        #    max_x = min(int(c.x + self._half_width),self.gameobject.width)
        #    min_y = max(0,int(c.y - self._half_height))
        #    max_y = min(int(c.y + self._half_height),self.gameobject.height)

        for x in range(min_x,max_x):
            for y in range(min_y, max_y):
                for z in range(len(self.tilemap.layer)):
                    t = self.tilemap.layer[z].get_tile(x,y)
                    if t:
                        if t.visible:
                            #if not Game.instance.camera:
                            screen.blit(t.image, (pos.x+self.tilemap.tile_width*x ,pos.y+self.tilemap.tile_height*y ,
                                                    self.tilemap.tile_width,self.tilemap.tile_height))
                                
                            #else:
                            #    screen.blit(t.image, (self.tilemap.tile_width*x-Game.instance.camera.offset_x ,
                            #                          self.tilemap.tile_height*y-Game.instance.camera.offset_y,
                            #                          self.tilemap.tile_width,
                            #                          self.tilemap.tile_height))

class TileMapLayer:
    def __init__(self,tilemap:TileMap,id:int) -> None:
        self.tile_map:TileMap = tilemap
        self.id:int = id
        self._tiles = [[None] * self.tile_map.height for _ in range(self.tile_map.width)]

    def set_tile(self, tile:Tile, x:int, y:int)->None:
        self._tiles[int(x)][int(y)]=tile
        if tile:
            tile.layer = self
            tile.position = Vector2(x,y)

    def get_tile(self, x:int, y:int)->Tile:
        return self._tiles[int(x)][int(y)]

class TilePalette:
    def __init__(self) -> None:
        self._store = {}

    def __getitem__(self,key)->TilePaletteItem:
        if isinstance(key,str):
            return self._store[key]
        elif isinstance(key,int):
            for _, item in self._store.items():
                if item.id == key:
                    return item
        return None

    def add(self, item:TilePaletteItem)->TilePaletteItem:
        self._store[item.tile_type]=item
        return item

class TileMap(GameObject):
    def __init__(self, width:int, height:int, tile_width:int, tile_height:int) -> None:
        super().__init__()
        self.width:int = width
        self.height:int = height
        self.tile_width:int = tile_width
        self.tile_height :int= tile_height
        self.layer = [TileMapLayer(self,0)]
        self.controller_list:List[TileController]=[]
        self.palette:TilePalette  = TilePalette()

    def add_layer(self)->int:
        new_layer = len(self.layer)
        self.layer.append(TileMapLayer(self,new_layer))
        return new_layer

    def get_tile(self,pos,layer=-1)->Tile:
        if layer == -1:
            for i in reversed(self.layer):
                t = i.get_tile(pos.x,pos.y)
                if t:
                    return t
            return None
        else:
            return self.layer[layer]
    
    def set_tile(self,tile:Tile,pos:Vector2,layer=0)->None:
        old_pos = tile.position
        old_layer = tile.layer.id
        self.layer[layer].set_tile(tile,pos.x,pos.y)
        self.layer[old_layer].set_tile(None,old_pos.x,old_pos.y)


    def create_tile_from_palette(self, x:int, y:int, tile_type:str|TilePaletteItem, tile_layer = 0)->Tile:
        tile = None
        item = None
        if isinstance(tile_type,TilePaletteItem):
            item = tile_type
        elif tile_type:
            item = self.palette[tile_type]
        if item:
            tile = Tile(item)
    
        self.layer[tile_layer].set_tile(tile,x,y)
        if tile:
            if tile.controller:
                self.controller_list.append(tile.controller)
        return tile

    def set_all_tiles(self,all_tiles:List[List[int|str]], tile_layer=0)->None:
        for y, line in enumerate(all_tiles):
            for x, value in enumerate(line):
                self.create_tile_from_palette(x,y,self.palette[value],tile_layer=tile_layer)

    def update(self, delta_time: float):
        for c in self.controller_list:
            c.update(delta_time)

# ----- physic system ----

STATIC_BODY = b2_staticBody
KINEMATIC_BODY = b2_kinematicBody
DYNAMIC_BODY = b2_dynamicBody

FORCE_MODE_FORCE = 1
FORCE_MODE_ACCELERATION = 2
FORCE_MODE_IMPULSE = 3
FORCE_MODE_VELOCITY_CHANGE = 4

class MixinSynchroniser:
    def get_position(self)->Vector2:
        pass

    def set_position(self, value:Vector2)->None:
        pass

    def get_rotation(self)->float:
        pass

    def set_rotation(self, value:float)->None:
        pass

    def get_position_x(self) -> float:
        return self.get_position().x

    def set_position_x(self, value)->None:
        v = self.get_position()
        n = Vector2(value, v.y)
        self.set_position(n)


    def get_position_y(self)-> float:
        return self.get_position().y

    def set_position_y(self, value)->None:
        v = self.get_position()
        self.set_position(Vector2(v.x, value))

class SynchronisedVector2(Vector2):        
    def __init__(self, x: Optional[Union[float, Vector2, Tuple[float, float], List[float]]], y: Optional[float],synchroniser=None) -> None:
        super().__init__(x=x, y=y)
        self._synchroniser:MixinSynchroniser = synchroniser

    @property 
    def x (self):
        return self._synchroniser.get_position_x()

    @x.setter
    def x (self, v:float)->None:
        self._synchroniser.set_position_x(v)

    @property
    def y (self)->float:
        return self._synchroniser.get_position_y()

    @y.setter
    def y (self,v:float)->None:
        self._synchroniser.set_position_y(v)


class SynchronisedTransform:
    def __init__(self, transform:Transform, synchroniser:MixinSynchroniser):
        self._synchroniser = synchroniser
        self.position = transform.position
        self.rotation = transform.rotation
        self.scale = transform.scale

    @property
    def position(self)->SynchronisedVector2:
        v = self._synchroniser.get_position()
        return SynchronisedVector2(v.x,v.y,synchroniser=self._synchroniser)

    @position.setter
    def position(self, value)->None:
        self._synchroniser.set_position(value)

    @property
    def rotation(self)->float:
        return self._synchroniser.get_rotation()

    @rotation.setter
    def rotation(self,value:float)->None:
        return self._synchroniser.set_rotation(value)

class AbstractCollider(Component):
    """
    Restitution is used to make objects bounce. between 0 and 1. 
        Consider dropping a ball on a table. A value of zero means the ball won't bounce. 
        This is called an inelastic collision. A value of one means the ball's velocity will be exactly reflected. 
        This is called a perfectly elastic collision.
    """
    def __init__(self, gameobject: GameObject, body:Rigidbody, box=None, radius=None, vertices=None, density:float=1.0, friction:float=1.0, restitution:float=0.0):
        super().__init__(gameobject)

        self.fixture = None

        if box:
            physic_box = (Game.instance.physic_system.to_world_value(box[0]//2), Game.instance.physic_system.to_world_value(box[1]//2))
            self.fixture = body.physic_body.CreatePolygonFixture(box=physic_box, density=density, friction=friction)
        elif radius:
            physic_radius = Game.instance.physic_system.to_world_value(radius)
            self.fixture =  body.physic_body.CreateCircleFixture(radius=physic_radius, density=density, friction=friction)

        elif vertices:
            physic_vertices = []
            for i in vertices:
                physic_vertices.append(Game.instance.physic_system.to_world(i)-body.physic_body.position)
            self.fixture = body.physic_body.CreatePolygonFixture(vertices=physic_vertices, density=density, friction=friction)

        self.fixture.restitution = restitution
        #print(self.fixture)
        
    @property
    def is_trigger(self):
        return self.fixture.sensor

    @is_trigger.setter
    def is_trigger(self, value):
        self.fixture.sensor = value


class BoxCollider(AbstractCollider):
    def __init__(self, gameobject:GameObject, body:Rigidbody, box=(1,1), density:float=1.0, friction:float=1.0, restitution:float=0.0):
        super().__init__(gameobject,body, box=box, density=density, friction=friction, restitution=restitution)
        
class CircleCollider(AbstractCollider):
    def __init__(self, gameobject:GameObject, body:Rigidbody, radius=10, density:float=1.0, friction:float=1.0, restitution:float=0.0):
        super().__init__(gameobject, body, radius=radius, density=density, friction=friction, restitution=restitution)

class PolygonCollider(AbstractCollider):
    def __init__(self, gameobject: GameObject, body: Rigidbody, vertices=None, density:float=1.0, friction:float=1.0, restitution:float=0.0):
        super().__init__(gameobject, body, vertices=vertices, density=density, friction=friction, restitution=restitution)
        

    @property
    def is_trigger(self):
        return self.fixture.sensor

    @is_trigger.setter
    def is_trigger(self, value):
        self.fixture.sensor = value
        
class Rigidbody(Component,MixinSynchroniser):
    """ STATIC_BODY
            physic system does not simulate this body
            body has zero velocity
            body does not collide with other static or kinematic bodies

        KINEMATIC_BODY
            physic system simulates this body
            body does not respond to forces
            program can move body normally by setting velocity
            body does not collide with other static or kinematic bodies

        DYNAMIC_BODY
            physic system simulates this body
            body collides with other bodies

    """
    def __init__(self, gameobject: GameObject, body_type):
        super().__init__(gameobject)
        self.physic:PhysicSystem = Game.instance.physic_system
        physic_position = self.physic.to_world(gameobject.transform.position)

        self.physic_body:b2Body = self.physic.CreateBody(type=body_type, position=physic_position, userData=gameobject)

        gameobject.transform = SynchronisedTransform(gameobject.transform, self)

    def get_position(self)->Vector2:
        return self.physic.to_screen(b2Vec2(self.physic_body.position))

    def set_position(self, value)->None:
        self.physic_body.position = self.physic.to_world(value)

    def get_rotation(self) -> float:
        return self.physic_body.angle

    def set_rotation(self, value: float) -> None:
        self.physic_body.angle = value

    @property
    def velocity(self)->Vector2:
        return Game.instance.physic_system.to_screen_vector(self.physic_body.linearVelocity)

    @velocity.setter
    def velocity(self, value:Vector2):
        self.physic_body.linearVelocity = Game.instance.physic_system.to_world_vector(value)


    @property
    def fixed_rotation(self)->bool:
        return self.physic_body.fixedRotation
    
    @fixed_rotation.setter
    def fixed_rotation(self,v:bool)->None:
        self.physic_body.fixedRotation = v

    @property
    def mass(self)->float:
        return self.physic_body.mass

    @mass.setter
    def mass(self,v:float)->None:
        self.physic_body.mass = v

    """ Damping reduces the velocity of bodies
        Damping is always
        Friction only with contact
    """
    @property
    def linear_damping(self)->float:
        return self.physic_body.linearDamping

    @linear_damping.setter
    def linear_damping(self, v:float)->None:
        self.physic_body.linearDamping = v

    @property
    def angular_damping(self)->float:
        return self.physic_body.angularDamping

    @angular_damping.setter
    def angular_damping(self, v:float)->None:
        self.physic_body.angularDamping = v

    @property
    def gravity_scale(self)->float:
        """The degree to which this object is affected by gravity. 0 .. 1"""
        return self.physic_body.gravityScale
    
    @gravity_scale.setter
    def gravity_scale(self, value:float)->None:
        """The degree to which this object is affected by gravity."""
        self._body.gravityScale = value

    @property
    def awake(self)->bool:
        return self.physic_body.awake

    @awake.setter
    def awake(self, value:bool)->None:
        self.physic_body.awake = value

    @property
    def allow_sleep(self)->bool:
        return self.physic_body.sleepingAllowed

    @allow_sleep.setter
    def allow_sleep(self, value:bool)->None:
        self.physic_body.sleepingAllowed = value

    def AddForce(self, direction:Vector2, mode:int)->None:
        if mode == FORCE_MODE_IMPULSE:
            self.physic_body.ApplyLinearImpulse(self.physic.to_world(direction), self.physic_body.worldCenter, wake=True)
        else:
            raise Exception('mode not implemented')

    @property
    def gravity_scale(self)->float:
        return self.physic_body.gravityScale

    @gravity_scale.setter
    def gravity_scale(self,v:float)->None:
        self.physic_body.gravityScale = v

class DistanceJoint(Component):
    """
    the distance between two points on two bodies must be constant
    Softness is achieved by changing: 
       frequency and damping ratio. 
       
       frequency of a harmonic oscillator in Hertz. 
            should be less than a half the frequency of the time step

        damping ratio is between 0 and 1.
    """
    def __init__(self, gameobject: GameObject, body_a:Rigidbody, body_b:Rigidbody, 
                       anchor_a:Vector2, anchor_b:Vector2, collide_connected=True):
        super().__init__(gameobject)
        self.physic = Game.instance.physic_system
        self.physic_joint:b2DistanceJoint = self.physic.CreateDistanceJoint(bodyA=body_a.physic_body, 
                                                            bodyB=body_b.physic_body, 
                                                            anchorA=self.physic.to_world(anchor_a), 
                                                            anchorB=self.physic.to_world(anchor_b),
                                                            collideConnected=collide_connected)

        #print(self.physic_joint)

    @property
    def frequency_hz(self)->float:
        return self.physic_joint.frequencyHz

    @frequency_hz.setter
    def frequency_hz(self,v:float)->None:
        self.physic_joint.frequencyHz = v

class RevoluteJoint(Component):
    def __init__(self, gameobject:GameObject, body_a:Rigidbody, body_b:Rigidbody,anchor:Vector2)->None:
        super().__init__(gameobject)
        self.physic = Game.instance.physic_system
        self.physic_joint:b2RevoluteJoint = self.physic.CreateRevoluteJoint(bodyA=body_a.physic_body,
                                                            bodyB=body_b.physic_body,
                                                            anchor=self.physic.to_world(anchor))
        #print(self.physic_joint)

    def test(self):
        self.physic_joint.motorEnabled = True
        self.physic_joint.motorSpeed = 1.0

class PhysicsEventList:
    def __init__(self) -> None:
        self.data = []

class ContactListener(b2ContactListener):
    def __init__(self,physic_system:PhysicSystem, event_list:PhysicsEventList):
        b2ContactListener.__init__(self)

        self.physics = physic_system
        self.event_list = event_list

    def BeginContact(self, contact:b2Contact)->None:

        if contact.fixtureA.sensor:
            self.event_list.data.append(('on_trigger_enter', contact.fixtureA.body.userData,contact.fixtureB.body.userData))

        if contact.fixtureB.sensor:
            self.event_list.data.append(('on_trigger_enter', contact.fixtureB.body.userData,contact.fixtureA.body.userData))

    def PostSolve(self, contact:b2Contact, impulse:b2ContactImpulse)->None:
        try:
            a = contact.fixtureA.body.userData
            b = contact.fixtureB.body.userData

            if a :
                #a.on_collision_enter(b,impulse)
                self.event_list.data.append(('on_collision_enter',a,b,impulse))
            if b :
                #b.on_collision_enter(a,impulse)
                self.event_list.data.append(('on_collision_enter',b,a,impulse))
        except Exception as e:
            print(e)
            traceback.print_exc()
            raise e

class QueryCallback(b2QueryCallback):
    def __init__(self, p):
        super(QueryCallback, self).__init__()
        self.point = p
        self.fixture = None

    def ReportFixture(self, fixture:b2Fixture)->bool:
        body = fixture.body
        if body.type == b2_dynamicBody or body.type == b2_kinematicBody:
            inside = fixture.TestPoint(self.point)
            if inside:
                self.fixture = fixture
                # We found the object, so stop the query
                return False
        # Continue the query
        return True

class PhysicSystem(b2World, MixinGameSystem):
    def __init__(self, ppm:float=20.0, time_step:float=1.0 / 30.0, gravity=(0, -10)):
        super().__init__(gravity, doSleep=True)
        self.game = Game.instance
        self.time_step = time_step
        self.ppm = ppm # pixel per meter
        self.debug_line_width = 4
        self.event_list = PhysicsEventList()

        self.contactListener = ContactListener(self,self.event_list)

    def update(self):
        self.Step(self.time_step, 10, 10)

        for e in self.event_list.data:
            if e[0] == 'on_trigger_enter':
                e[1].on_trigger_enter(e[2])
            elif e[0] == 'on_collision_enter':
                e[1].on_collision_enter(e[2],e[3])

        self.event_list.data = []


    def draw_debug(self, screen):
        for body in self.bodies:

            color = BLUE

            if body.type == STATIC_BODY:
                color = DARKGRAY
            elif body.type == KINEMATIC_BODY:
                color = GREEN

            for fixture in body.fixtures:

                shape = fixture.shape

                if isinstance(shape, b2PolygonShape):
                    vertices = [self.to_screen(body.transform * v) for v in shape.vertices]
                    pygame.draw.polygon(screen, color, vertices, self.debug_line_width)
                else:
                    position = self.to_screen(body.transform * shape.pos)
                    pygame.draw.circle(screen, color, [int(x) for x in position], int(shape.radius * self.ppm),
                                       self.debug_line_width)

        for joint in self.joints:
            a = self.to_screen(joint.anchorA)
            b = self.to_screen(joint.anchorB)
            pygame.draw.line(screen, YELLOW, a, b, self.debug_line_width)

    def on_start_load_scene(self):
        for body in self.bodies:
            self.DestroyBody(body)

    def on_remove_gameobject(self, gameobject: GameObject) -> None:
        rigidbody =  gameobject.get_component(Rigidbody)
        if rigidbody:
            self.DestroyBody(rigidbody.physic_body)
        
    
    def to_screen(self, v):
        result = (v[0] * self.ppm, v[1] * self.ppm)
        return Vector2(int(result[0]), int(self.game.height - result[1]))

    def to_screen_value(self, v:float)->int:
        return int(v * self.ppm)

    def to_screen_vector(self,v:b2Vec2)->Vector2:
        return Vector2(self.to_screen_value(v[0]),self.to_screen_value(v[1]))

    def get_body(self, position)->b2Body:
        body = None

        aabb = b2AABB(lowerBound=position - (0.001, 0.001),
                      upperBound=position + (0.001, 0.001))

        query = QueryCallback(position)

        self.QueryAABB(query, aabb)

        if query.fixture:
            body = query.fixture.body

        return body

    def get_gameobject(self, postition)->GameObject:
        gameobject = None
        body = self.get_body(self.to_world(postition))
        if body:
            gameobject = body.userData
        return gameobject

    def to_world(self, v):
        return b2Vec2(v[0] / self.ppm, (self.game.height - v[1]) / self.ppm)

    def to_world_value(self,v:int)->float:
        return v / self.ppm

    def to_world_vector(self, v:Vector2)->b2Vec2:
        return b2Vec2(self.to_world_value(v.x),self.to_world_value(v.y))

# ---- ui system ----
TEXT_ALIGNMENT_LEFT = 1
TEXT_ALIGNMENT_MID = 2

def draw_text(screen:Surface, text, size:int, color, position:Vector2, alignment=TEXT_ALIGNMENT_LEFT, draw=True)->Rect:
    result_rect:Rect = None

    font = pygame.font.Font(None, size)

    if not isinstance(text,List):
        text = [text]
    
    position = Vector2(position.x, position.y)

    for t in text:
        img = font.render(t, True, color)
        rect:pygame.Rect = img.get_rect()
        if alignment == TEXT_ALIGNMENT_LEFT:
            rect.topleft = position
        else:
            rect.midtop = position
        if draw:
            screen.blit(img, rect)
        else:
            if result_rect == None:
                result_rect = rect
            else:
                result_rect = result_rect.union(rect)

        position.y += rect.height

    return result_rect

class MixinSurface:
    def get_surface(self,rect:Rect)->Surface:
        pass

class Text(GameObject, MixinDraw):
    def __init__(self,text:str,position:Vector2(),font_size:int=12, color:color=WHITE, alignment:int=TEXT_ALIGNMENT_LEFT, 
                      surface_element:MixinSurface=None):
        super().__init__()
        self.text = text
        self.transform.position = position
        self.font_size = font_size
        self.color = color
        self.surface_element = surface_element

    def draw(self, screen: pygame.Surface):
        #print(screen)
        if self.surface_element:
            rect = draw_text(screen,self.text,size=self.font_size,color=self.color,position=self.transform.position,draw=False)
            surface = self.surface_element.get_surface(rect)
            draw_text(surface,self.text,size=self.font_size,color=self.color,position=Vector2(0,0))
            screen.blit(surface,rect)
        else:
            draw_text(screen,self.text,size=self.font_size,color=self.color,position=self.transform.position)
    
class MixinButtonClick:
    def on_click(self):
        pass

class Button(GameObject,MixinSurface):
    def __init__(self,text:Text=None,color:Color=BLACK, highlighted_color=GRAY, pressed_color=WHITE, on_click:MixinButtonClick=None):
        super().__init__()
        self.text = text
        if not self.text:
            self.text = Text('Button', self.transform.position)
        self.text.surface_element=self
        self.color = color
        self.highlighted_color = highlighted_color
        self.pressed_color = pressed_color
        self.on_click = on_click
        self.mouse_down = False

    def get_surface(self, rect: Rect) -> Surface:
        color = self.color
        #print(self.mouse_down)
        if rect.collidepoint(pygame.mouse.get_pos()):
            color = self.highlighted_color
            if pygame.mouse.get_pressed()[0]:
                color = self.pressed_color
                self.mouse_down = True
            else:
                if self.mouse_down:
                    self.mouse_down = False
                    self.on_click.on_click()

        surface = Surface((rect.width, rect.height))
        surface.fill(color)
        return surface

class Image(GameObject, MixinDraw):
    def __init__(self, image:pygame.Surface = None, load_from_file:str = None, scale:Vector2=None):
        super().__init__()

        self._image = None

        if image:
            self._image = image

        if load_from_file:
            #print('current directory', os.getcwd())
            self._image = pygame.image.load(load_from_file)

        if scale:
            new_size = Vector2(self.image.get_width()*scale.x,self.image.get_height()*scale.y)
            self._image = pygame.transform.scale(self.image, (int(new_size.x), int(new_size.y))) 

        self._rect = self.image.get_rect()

    @property
    def image(self)->Surface:
        return self._image

    @image.setter
    def image(self,v:Surface)->None:
        self._image = v
        self._rect = self._image.get_rect()

    @property
    def rect(self) -> pygame.Rect:
        self._rect.center = self.transform.position
        return self._rect

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.rect)


# ----- central game engine ----

class Game:

    instance:Game = None

    def __init__(self, width:int=800, height:int=600, name:str="", fps:int=30, scenes:List[Scene]=None) -> None:

        if not Game.instance:
            Game.instance = self
        else:
            raise Exception('Only one Game Object')

        self.width = width
        self.height = height
        self.name = name
        self.background_color = BLACK

        self._fps = fps

        self.event_system = EventSystem()
        self.render_system = RenderSystem()
        self.physic_system = PhysicSystem(time_step=1.0/self._fps)
        self.scene_system = SceneSystem(scenes)
        self._load_scene = 0
        self.systems = [self.event_system, self.scene_system,
                        self.render_system, self.physic_system]

        pygame.init()

        self.screen = pygame.display.set_mode((self.width, self.height))

        pygame.display.set_caption(self.name)

        self.running = False
        self.delta_time = 0

        self.remove_gameobject_list=[]
        self.add_gameobject_list=[]

        self.loading_scene_tag = False
        self.debug_physic_system_tag = False
        self.debug_physic_system_overlay_tag = False

        self.clock = pygame.time.Clock()

        self.start_gameloop()

    @property
    def fps(self):
        return self._fps

    @fps.setter
    def fps(self, value:int)->None:
        self._fps = value
        self.physic_system.time_step = 1.0/self._fps

    def start_gameloop(self)->None:
        self.running = True

        while self.running:

            if self._load_scene != -1:
                self.do_load_scene()
                self._load_scene = -1
        
            self.delta_time = self.clock.tick(self.fps) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    #print(event)
                    self.event_system.on_event(event)

            self.update()

            for g in self.remove_gameobject_list:
                self.on_remove_gameobject(g)
            self.remove_gameobject_list = []

            for g in self.add_gameobject_list:
                self.scene_system.current_scene.add(g[0],g[2])
                if g[1]:
                    g[0].transform.position = g[1]
            self.add_gameobject_list = []

            self.late_update()

            self.draw()

            pygame.display.flip()


    def update(self)->None:
        for layer_key, layer_value in self.scene_system.current_scene.layers.items():
            for g in layer_value:
                g.update(self.delta_time)
                for c in g.components:
                    c.update(self.delta_time)
        self.physic_system.update()

    def late_update(self)->None:
        pass

    def draw(self)->None:
        self.screen.fill(self.background_color)

        if self.debug_physic_system_tag:
            if self.debug_physic_system_overlay_tag:
                self.render_system.draw(self.screen)
            self.physic_system.draw_debug(self.screen)
        else:
            self.render_system.draw(self.screen)

    def get_object(self, classinfo):
        r = None

        for l in self.scene_system.current_scene.layers:
            for g in self.scene_system.current_scene.layers[l]:
                if isinstance(g,classinfo):
                    r = g
                    break
        return r

    def load_scene(self, scene:int)->None:
        if self._load_scene == -1:
            self._load_scene = scene

    def remove_gameobject(self, gameobject:GameObject)->None:
        self.remove_gameobject_list.append(gameobject)

    def add_gameobject(self,gameobject,position:Vector2=None, layer='default')->GameObject:
        self.add_gameobject_list.append((gameobject,position,layer))
        return gameobject
    
    def do_load_scene(self)->None:
        self.loading_scene_tag = True
        self.on_start_load_scene()
        self.scene_system.load_scene(self._load_scene)
        self.on_load_scene(self.scene_system.current_scene)
        self.loading_scene_tag = False

    def on_start_load_scene(self)->None:
        for s in self.systems:
            s.on_start_load_scene()

    def on_load_scene(self, scene:Scene)->None:
        for s in self.systems:
            s.on_load_scene(scene)

    def on_add_gameobject(self, scene:Scene, gameobject:GameObject, layer:str):
        if scene == self.scene_system.current_scene and not self.loading_scene_tag:
            for s in self.systems:
                s.on_add_gameobject(gameobject, layer)

    def on_remove_gameobject(self, gameobject:GameObject)->None:
        for s in self.systems:
                s.on_remove_gameobject(gameobject)

    def quit(self)->None:
        pygame.quit()
        
class GetObject:
    def __init__(self, classinfo):
        self._getobject_classinfo = classinfo
        self._getobject_value = None
    def __getattr__(self, attr):
        if self._getobject_value == None:
            self._getobject_value = Game.instance.get_object(self._getobject_classinfo)
        return getattr(self._getobject_value, attr)
    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith('_getobject_'):
            self.__dict__[name] = value
            return
        if self._getobject_value == None:
            self._getobject_value = Game.instance.get_object(self._getobject_classinfo)
        setattr(self._getobject_value,name,value)

def destroy(gameobject:GameObject):
    Game.instance.remove_gameobject(gameobject)

def instantiate(gameobject:GameObject, position:Vector2=None, layer='default')->GameObject:
    return Game.instance.add_gameobject(gameobject,position,layer)

def get_object(classinfo):
    return Game.instance.get_object(classinfo)