wonder - Python Game Engine
===========================

Whenever I have played a great computer game for the first time, I was **wonder**\ ing how they do it. Then I tried to recreate it.
-----------------------------------------------------------------------------------------------------------------------------------



**Pygame** (https://www.pygame.org) is a great library for making your
own game with python.

When starting a new game from scratch you always need to build the basic
structure. The game engine ``wonder`` gives you a collection of
components you can use with **Pygame**.

The game engine ``wonder`` is only a frame for your programming, so you
have to know Pygame for creating new games.

Many ideas in ``wonder`` are inspired by *Unity 3D* (https://unity.com)

If you are looking for more simple to use Pygame frameworks:

-  **pygame zero** https://github.com/lordmauve/pgzero
-  **python arcade library** https://arcade.academy

The game engine ``wonder`` includes Box2D as physics engine.

Goals:

-  explicit is better then implicit - wonder is only the frame for your
   game
-  Component based - more components, less classes
-  Inspired by Unity 3D - Similar names for object types and methods
-  Physics engine included



If you like it, use it. If you have some suggestions, tell me
(hebi@ninja-python.com).

All game assets that I use in examples are free and from
https://www.kenney.nl. Thank you.

acclaimer
---------

You can use this alpha version 0.1.0 of the ``wonder`` game engine but
there will be some changes in the future.

installing wonder game engine
-----------------------------

Install with pip

.. code:: ipython3

    pip install wonder

If that does not work on your platform you can install the different
components separately

Install **pygame**

.. code:: ipython3

    pip install pygame

Install physics engine **Box2D**

.. code:: ipython3

    pip install box2d

For installing **wonder** simply copy file **wonder.py** to your
directory.

.. code:: ipython3

    cp wonder.py

wonder game engine - making a new game
--------------------------------------

The first game with ``wonder``\ game engine is a classical ‘Ball and
Paddle game’ like Arkanoid, Breakout or Alleyway.

| Arkanoid https://en.wikipedia.org/wiki/Arkanoid
| Breakeout https://en.wikipedia.org/wiki/Breakout_(video_game)
| Alleyway https://en.wikipedia.org/wiki/Alleyway_(video_game)

You can find the complete game in the file *game_blocks.py*



main game
~~~~~~~~~

The easiest way to get access to all classes of the **wonder** game
engine is to include them completely.

.. code:: ipython3

    from wonder import *

First you need an object of the class **Game**. It represents the game
itself.

.. code:: ipython3

    if __name__ == "__main__":
        game = Game(width=860,height=600,name='game_blocks.py',scenes=[Level()])
        game.quit()

Class **Game**: \* *width* .. screen width in pixel \* *height* ..
screen height in pixel \* *name* .. name of the game, shown as window
title \* *scenes* .. list of sences, levels of the game

Method **game.quit()** stops the game.

scene
~~~~~

An object of the class **Scene** is a container that contains all things
(gameobjects) that are currently required by the game. Often a scene
corresponds to a level.

.. code:: ipython3

    class Level(Scene):
        def create(self):
            self.background_color = WHITE
            #create gameobjects

To create a new level you have to derive your own class from the
**Scene** class. The **create** method is called by the game engine to
create all game objects of the scene.



gameobject
~~~~~~~~~~

The first part of the game is the **paddle**, on which the player has to
bounce the ball with it in order to hit colored blocks.

The paddle has its own class **Paddle** that is derived from the
**GameObject** class.

.. code:: ipython3

    class Paddle(GameObject):
        def __init__(self):
            super().__init__()
    
        def update(self, delta_time):
            # all action
            pass

Class **GameObject**:

-  *\__init_\_* .. creates all components and property, allways have to
   call super().__init__()
-  *update* .. is called as often as possible by the game engine.
-  *delta_time* .. describes the time since the last call

A **GameObject** can have **Components** that do some jobs for them.

The component **SpriteRender** draws an image (sprite) on the screen
that represents the **GameObject**. position add Racket to Scene

.. code:: ipython3

    class Paddle(GameObject):
        DISTANCE = 20
        def __init__(self):
            super().__init__()
            self.sprite_renderer = self.add(SpriteRenderer(self, 
                                            load_from_file='res_blocks/paddleBlu.png'))
            self.transform.position = Vector2(Game.instance.width//4*3//2, 
                   Game.instance.height - self.sprite_renderer.rect.height - self.DISTANCE)


-  *self.add* .. method self.add adds the component *SpriteRenderer* to
   the gameobject and returns the added component
-  *self.transform.position* .. a gameobject has *transform* property.
   With *transform.position* you can change the position.

**wonder** game engine uses pygame **Vector2** for positions.

With **Game.instance** you get the current game object.

To see anything you have to add the gameobject to the scene.

.. code:: ipython3

    class Level(Scene):
        def create(self):
            ..
    
            self.add(Paddle())



In order for the physics engine to realistically calculate for example
the movements of the ball, it needs information about the physical
properties of the paddle.

.. code:: ipython3

    class Paddle(GameObject):
        DISTANCE = 20
        def __init__(self):
            super().__init__()
            ..
            self.rigidbody = self.add(Rigidbody(self,DYNAMIC_BODY))
            self.rigidbody.fixed_rotation = True
            self.add(BoxCollider(self,self.rigidbody,
                                 box=(self.sprite_renderer.rect.width,
                                      self.sprite_renderer.rect.height)))


-  *Rigidbody(self,DYNAMIC_BODY)* .. the component **Rigidbody** defines
   the gameobject as a rigid object. It is not soft.
-  *DYNAMIC_BODY* .. means that the gameobject can be moved by the
   physics engien
-  *self.rigidbody.fixed_rotation = True* .. The paddle is always level.
   It shouldn’t be rotated.
-  *BoxCollider(self,self.rigidbody,box=(width,height))* .. the
   component **BoxCollider** defines the extension of the gameobject.
   The paddle is like a box. You can get width and height from the
   **SpriteRenderer**. It is the width and height of the image.

.. code:: ipython3

    class Level(Scene):
        def create(self):
            ..
            Game.instance.physic_system.gravity = (0.0,0.0)

In this game should not be used any gravity.

create border
~~~~~~~~~~~~~

The game has a border on the left, one on the right, and one on top. The
ball can bounce off these. There is no limit below. There it goes out.



A border object is from the **Border** class that is derived from the
**GameObject** class.

.. code:: ipython3

    class Border(GameObject):
        HEIGHT = 20
        def __init__(self, width, height, position):
            super().__init__()
            image = pygame.Surface((width, height))
            image.fill(GRAY)
            self.add(SpriteRenderer(self, image=image))
            self.transform.position = position

Class **Border**

-  *\__init__(self, width, height, position)* .. with, height and
   position of the border that should be created
-  *image = pygame.Surface((width, height))* .. the **Surface** class of
   pygame can create a local image
-  *image.fill(GRAY)* .. the image is a grey rectangle
-  *self.add(SpriteRenderer(self, image=image))* .. add
   **SpriteRenderer** component
-  *self.transform.position = position* .. set border position

.. code:: ipython3

    class Border(GameObject):
        HEIGHT = 20
        def __init__(self, width, height, position):
            ..
            rigidbody = self.add(Rigidbody(self,STATIC_BODY))
            self.add(BoxCollider(self, rigidbody, box=(width,height)))

-  *Rigidbody(self,STATIC_BODY)* .. the border is also a rigid body.
-  *STATIC_BODY* .. means that the gameobject can not be moved by the
   physics engine
-  *BoxCollider(self,self.rigidbody,box=(width,height))* .. the border
   is like a box.

The **Scene** class creates the borders.

.. code:: ipython3

    class Level(Scene):
        def create(self):
            ..
            three_quarter = Game.instance.width//4*3
    
            self.add(Border(three_quarter, Border.HEIGHT, 
                            Vector2(three_quarter//2,Border.HEIGHT//2)))
            self.add(Border(Border.HEIGHT, Game.instance.height-Border.HEIGHT,
                            Vector2(Border.HEIGHT//2,
                                    (Game.instance.height+Border.HEIGHT)//2) ))
            self.add(Border(Border.HEIGHT, 
                            Game.instance.height-Border.HEIGHT,
                            Vector2(three_quarter-Border.HEIGHT//2, 
                                    (Game.instance.height+Border.HEIGHT)//2) ))

move paddle
~~~~~~~~~~~

The user can move the paddle with the left and write arrow keys.

.. code:: ipython3

    class Paddle(GameObject):
        ..
        SPEED = 120
        
        ..
        def update(self, delta_time):
            direction = 0.0
    
            keys=pygame.key.get_pressed()
        
            if keys[pygame.K_RIGHT]:
                direction = 1
            elif keys[pygame.K_LEFT]:
                direction = -1
    
            self.rigidbody.velocity = Vector2(1,0) * direction * self.SPEED

-  *SPEED = 120* .. constant speed when paddle is moved. It is 120 pixle
   per second.
-  *direction* .. 0 not moved, -1 moving left, 1 moving right
-  *keys=pygame.key.get_pressed()* .. pygame list with pressed or not
   pressed keys
-  *keys[pygame.K_RIGHT]* .. is True when right arrow key is pressed
-  *keys[pygame.K_LEFT]* .. is True when left arrow key is pressed
-  *self.rigidbody.velocity = Vector2(1,0)* direction \* self.SPEED\* ..
   sets the velocity of the paddle for the game engine

debug physics
~~~~~~~~~~~~~

You can switch to a special display for troubleshooting in connection
with the physics engine.



.. code:: ipython3

    class Paddle(GameObject):
        ..
        def update(self, delta_time):
            ..
            if keys[pygame.K_ESCAPE]:
                Game.instance.debug_physic_system_tag = not Game.instance.debug_physic_system_tag

-  *Game.instance.debug_physic_system_tag* .. when this property is True
   the game engine debug display is shown

create ball
~~~~~~~~~~~

A ball has a **SpriteRenderer**, a **Rigidbody**, and a
**CircleBollider** component.

.. code:: ipython3

    class Ball(GameObject):
        SPEED = 240
        def __init__(self):
            super().__init__()
            sprite_renderer = self.add(SpriteRenderer(self, 
                                       load_from_file='res_blocks/ballGrey.png'))
            self.transform.position = Vector2(Game.instance.width//4*3//2, 
                                              Game.instance.height//2)
            
            self.rigidbody = self.add(Rigidbody(self,DYNAMIC_BODY))
            self.add(CircleCollider(self,self.rigidbody,
                                    radius=sprite_renderer.rect.width//2,
                                    restitution=1.0,friction=0))
            self.rigidbody.velocity = Vector2(0,0) * self.SPEED
            self.rigidbody.mass = 0.2

-  *self.rigidbody = self.add(Rigidbody(self,DYNAMIC_BODY))* .. add
   Rigidbody component
-  *self.add(CircleCollider(self,self.rigidbody,radius=sprite_renderer.rect.width//2,restitution=1.0,friction=0))*
   .. CircleCollider component
-  *self.rigidbody.velocity = Vector2(0,0)* .. sets start velocity to
   zero
-  *self.rigidbody.mass = 0.2* .. sets mass

Add ball to scene.

.. code:: ipython3

    class Level(Scene):
        def create(self):
            ..
            self.add(Ball())



create block
~~~~~~~~~~~~

A single block has a **SpriteRenderer**, a **Rigidbody**, and a
**BoxCollider** component.

.. code:: ipython3

    class Block(GameObject):
        def __init__(self, file_name):
            super().__init__()
            self.sprite_renderer = self.add(SpriteRenderer(self,load_from_file=file_name))
            self.rigidbody = self.add(Rigidbody(self,DYNAMIC_BODY))
            self.rigidbody.fixed_rotation = True
            self.add(BoxCollider(self,self.rigidbody,
                                 box=(self.sprite_renderer.rect.width,
                                      self.sprite_renderer.rect.height)))

Every level has a different pattern of blocks. An object of the class
**BlockManager** creates the blocks according to the pattern of the
level.

.. code:: ipython3

    class BlockManager(GameObject):
        FILES = ['res_blocks/element_blue_rectangle.png',
                 'res_blocks/element_green_rectangle.png',
                 'res_blocks/element_red_rectangle.png',
                 'res_blocks/element_yellow_rectangle.png']
        SPACE = 10
    
        def __init__(self, scene):
            super().__init__()
            self.scene = scene
            self.count = 0

The pattern of the first level is

| [[0,1,2,3,0,1,2,3],
| [0,1,2,3,0,1,2,3],
| [0,1,2,3,0,1,2,3],
| [0,1,2,3,0,1,2,3]]

Every number represents a different color. The number 0 means an empty
space.

The **BlockManager.make** method creates the blocks.

.. code:: ipython3

    class BlockManager(GameObject):
        ..
    
        def make(self, block_pattern) -> None:
            for i, value in enumerate(block_pattern):
                for j, file_nr in enumerate(value):
                    self.count += 1
                    block = self.scene.add(Block(self.FILES[file_nr]))
                    block.transform.position = Vector2(Border.HEIGHT+self.SPACE+block.sprite_renderer.rect.width*(j+0.5)+self.SPACE*j,
                                                       Border.HEIGHT+self.SPACE+block.sprite_renderer.rect.height*(i+0.5)+self.SPACE*i)
            

-  *for i, value in enumerate(block_pattern)* .. for every line in
   block_pattern
-  *for j, file_nr in enumerate(value)* .. for every value in line,
   value represents different png-file
-  *block = self.scene.add(Block(self.FILES[file_nr]))* .. add Block
   GameObject to scene
-  *block.transform.position = Vector2(..)* .. set position

Add **BlockManager** to **Level**. So that the **create** method of the
**Level** class does not come across to the standard **create** method,
this is renamed to **create_level**.

.. code:: ipython3

    class Level(Scene):
        def create_level(self,pattern):
            ..
            block_manager = self.add(BlockManager(self))
            block_manager.make(pattern)

Create two levels with different block pattern.

.. code:: ipython3

    class Level1(Level):
        def create(self) -> None:
            self.create_level([[0,1,2,3,0,1,2,3],
                                [0,1,2,3,0,1,2,3],
                                [0,1,2,3,0,1,2,3],
                                [0,1,2,3,0,1,2,3]])        
    
    class Level2(Level):
        def create(self):
            self.create_level([[0,1,2,3,2,1,2,0],
                                [0,1,2,0,0,1,2,0],
                                [0,1,0,3,1,0,2,0],
                                [0,0,2,3,1,1,0,0]])

Add levels to *Game* object.

.. code:: ipython3

    if __name__ == "__main__":
        game = Game(width=860,height=600,name='game_blocks.py', 
                    scenes=[Level1(), Level2()])
        game.quit()



create scoremanager
~~~~~~~~~~~~~~~~~~~

Tasks of the **ScoreManager** are

-  managing the game
-  restarting the game
-  do the scoring

.. code:: ipython3

    class ScoreManager(GameObject,MixinDraw):
        def __init__(self):
            super().__init__()
            
            self.init()
    
            self.text_in_play_field = Vector2(Game.instance.width//4*3//2,
                                              Game.instance.height//4*3)
            self.text_right = Vector2(Game.instance.width//4*3+Game.instance.width//4//2,
                                      Game.instance.height//8)
            self.text_space = 40
    
        def init(self):
            self.score = 0
            self.level = 1
            self.ball = 48
    
            self.block_manager = GetObject(BlockManager)
            self.start_tag = True

-  *self.text_in_play_field = Vector2(..)* .. position of the central
   text, like ‘press key to start game’

-  *self.text_right = Vector2(..)* .. position of text right, like score

-  *self.text_space = 40* .. space between texts

-  *def init(self)* .. when game restarts, some properties of the
   ScoreManageer has to be initialized

-  *self.block_manager = GetObject(BlockManager)* .. get the
   BlockManager

-  *self.start_tag = True* .. ScoreManager is in starting mode

The ScoreManager draws the numbers of current score itself. There is no
special object like a SpriteRenderer. The ScoreManager is also inhereted
by MixinDraw so it gets the draw method which is called every frame by
the game engine.

.. code:: ipython3

    class ScoreManager(GameObject,MixinDraw):
        ..
        def draw(self, screen: pygame.Surface):
            if self.start_tag:
                draw_text(screen, 'press space to start game',48, ORANGE,
                          self.text_in_play_field,alignment=TEXT_ALIGNMENT_MID)
    
            draw_text(screen, f'Score {self.score}',48, ORANGE,
                      self.text_right,alignment=TEXT_ALIGNMENT_MID)
            draw_text(screen, f'Level {self.level}',48, ORANGE,
                      Vector2(self.text_right.x, 
                              self.text_right.y+self.text_space),
                      alignment=TEXT_ALIGNMENT_MID)
            draw_text(screen, f'Ball {self.ball}',48, ORANGE,
                      Vector2(self.text_right.x, 
                              self.text_right.y+2*self.text_space),
                      alignment=TEXT_ALIGNMENT_MID)

-  *if self.start_tag* .. when in starting mode show text ‘press space
   to start game’
-  *draw_text(screen, f’Score {self.score}’,48,
   ORANGE,self.text_right,alignment=TEXT_ALIGNMENT_MID)* .. text to be
   drawn in pygame, the convinient draw_text methods helps

Parameter of draw_text

-  *screen* .. on which Surface should be drawn
-  *text* .. the text itself
-  *number of pixels*
-  *color*
-  *alignment* .. left or mid

.. code:: ipython3

    class ScoreManager(GameObject,MixinDraw):
        ..
        def update(self, delta_time: float):
            if self.start_tag:
                keys=pygame.key.get_pressed()
            
                if keys[pygame.K_SPACE]:
                    self.start_tag = False
                    Game.instance.get_object(Ball).start()

-  *if self.start_tag:* .. when **ScoreManager** is in starting mode it
   waits until a key is pressed

-  *if keys[pygame.K_SPACE]:* .. is it the space key?

-  *self.start_tag = False* .. than starting mode is over

-  *Game.instance.get_object(Ball).start()* .. get ball object and start
   it

.. code:: ipython3

    class Ball(GameObject):
    ..     
        def start(self):
            self.rigidbody.velocity = Vector2(0,-1) * self.SPEED

Add **ScoreManager** to **Level**

.. code:: ipython3

    class Level(Scene):
        def create_level(self,pattern):
            self.background_color = WHITE
            Game.instance.physic_system.gravity = (0.0,0.0)
    
            score_manager = Game.instance.get_object(ScoreManager)
    
            if not score_manager:
                score_manager = self.add(ScoreManager())
                self.dont_destroy_on_load(score_manager)

-  *score_manager = Game.instance.get_object(ScoreManager)* .. search
   for **ScoreManager**
-  *if not score_manager* .. if not available, create one
-  *score_manager = self.add(ScoreManager())* .. create **ScoreManager**
   and add to scene
-  *self.dont_destroy_on_load(score_manager)* .. tell game engine never
   destroy **ScoreManager**

When changing to a new scene (level), the game engine removes all old
GameObjects before generating the new ones. However, the ScoreManager
should always remain so that information such as highscores or the like
do not disappear.

blocks and ball
~~~~~~~~~~~~~~~

When the ball hits against the paddle it bounces.

.. code:: ipython3

    class Ball(GameObject):
        SPEED = 240
        ..
            
        def on_collision_enter(self, collider, impulse):
            if isinstance(collider,Paddle):
                factor = self.hit_factor(self.transform.position, 
                                         collider.transform.position,collider.width)
                direction = Vector2(factor,1).normalize()
                self.rigidbody.velocity = direction * self.SPEED

-  *def on_collision_enter(self, collider, impulse)* .. this methode is
   called if something collides with the ball
-  *if isinstance(collider,Paddle):* .. is the collider the paddle?
-  *factor = self.hit_factor(..)* .. the further the ball is from the
   center of the paddle, the more obliquely it will bounce off

.. code:: ipython3

    class Ball(GameObject):
        ..
        def hit_factor(self, ball_position, paddle_position, paddle_width):
            return (ball_position.x - paddle_position.x) / float(paddle_width)


The width of the paddle depends on the with of the picture that the
**SpriteRenderer** is using.

.. code:: ipython3

    class Paddle(GameObject):
        ..
        @property
        def width(self)->int:
            return self.sprite_renderer.rect.width

If an block object collides with something, what only can be the ball,
it will be removed.

.. code:: ipython3

    class Block(GameObject):
        ..
        def on_collision_enter(self, collider, impulse):
            get_object(ScoreManager).add(80)
            destroy(self)

-  *get_object(ScoreManager).add(80)* .. get the ScoreManger and add 80
   points to the score
-  *destroy(self)* .. the game engine will remove this block

.. code:: ipython3

    class ScoreManager(GameObject,MixinDraw):
         ..
        def add(self, value):
            self.score += value
    
            self.block_manager.count -=1
    
            if self.block_manager.count == 0:
                Game.instance.load_scene(self.level)
                self.level += 1
                self.ball += 2 

ScoreManager.add

-  *self.score += value* .. add points to the score
-  *self.block_manager.count -=1* .. tell **BlockManager** that one
   block is removed
-  *if self.block_manager.count == 0* .. are blocks available?
-  *Game.instance.load_scene(self.level)* .. if not, tell game engine to
   load next scene

restart
~~~~~~~

If the ball flies out below, restart the game.

.. code:: ipython3

    class Ball(GameObject):
        SPEED = 240
        ..
        def __init__(self):
            ..
            self.limit = Game.instance.height //4 * 5
    
        def update(self, delta_time: float):
            if self.transform.position.y > self.limit:
                get_object(ScoreManager).restart()

The **ScoreManager** restarts the game.

.. code:: ipython3

    class ScoreManager(GameObject,MixinDraw):
        ..
        def restart(self):
            self.ball -=1
            if self.ball >= 0:
                self.start_tag = True
                get_object(Ball).restart()
            else:
                Game.instance.load_scene(0)
                self.init()

-  *self.ball -=1* .. one ball less
-  *if self.ball >= 0* .. is a ball left?
-  *self.start_tag = True* .. set starting mode
-  *get_object(Ball).restart()* .. restart ball
-  *Game.instance.load_scene(0)* .. if no ball left, start from level 0

First game is completed.

wonder game engine - behind the curtain
---------------------------------------

central engine and the systems
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


pattern singleton
^^^^^^^^^^^^^^^^^


game loop update draw
^^^^^^^^^^^^^^^^^^^^^

| event
| update
| late_update
| draw

timing
^^^^^^


event system
^^^^^^^^^^^^

on_load_scene

observer pattern

get_object
^^^^^^^^^^

GetObject
^^^^^^^^^

gameobject
~~~~~~~~~~

mixin
^^^^^


transform
^^^^^^^^^


components
^^^^^^^^^^

SpriteRenderer

scene
-----

layered container for gameobject
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


render system
~~~~~~~~~~~~~

layered observer

Component SpriteRenderer
^^^^^^^^^^^^^^^^^^^^^^^^

| Surface
| load_from_file

consists of surface and rect

change current scene
~~~~~~~~~~~~~~~~~~~~

add or remove gameobject
^^^^^^^^^^^^^^^^^^^^^^^^

add or remove component
^^^^^^^^^^^^^^^^^^^^^^^


physic and collision system
---------------------------

| using Box2D
  https://box2d.org/documentation/md__d_1__git_hub_box2d_docs_dynamics.html
| python https://github.com/pybox2d/pybox2d

bodies
~~~~~~

Component Rigidbody is b2Body

synchornize transform
^^^^^^^^^^^^^^^^^^^^^


body types
^^^^^^^^^^

| STATIC_BODY
| physic system does not simulate this body
| body has zero velocity
| body does not collide with other static or kinematic bodies

| KINEMATIC_BODY
| physic system simulates this body
| body does not respond to forces
| program can move body normally by setting velocity
| body does not collide with other static or kinematic bodies

| DYNAMIC_BODY
| physic system simulates this body
| body collides with other bodies

fixtures
^^^^^^^^

component collider is b2Fixture

boxcollider

debug
^^^^^

joints
~~~~~~

distance joints
^^^^^^^^^^^^^^^

get_gameobject

animator component
------------------

| animator has states
| state has clips


particle system
---------------


tile system
-----------

| A **TileMap** is an GameObject and consists of *width* x *height*
  tiles.
| Every tile has a width of *tile_width* pixels and a height of
  *tile_height*.

.. code:: ipython3

    GRID_WIDTH = 5
    GRID_HEIGHT = 7
    
    CELL_WIDTH = 64
    CELL_HEIGHT = 64
    
    tilemap = TileMap(GRID_WIDTH,GRID_HEIGHT,CELL_WIDTH,CELL_HEIGHT)

The tilemap.transform.position is always the top left position of the
map. With changing position you can move the complete map.

| A TileMap has a **palette** with different **TilePaletteItem** you can
  use in a tilemap.
| A **TilePaletteItem** has an unique **id**, an unique **tile_type**
  and an **image**.

.. code:: ipython3

    tilemap.palette.add(TilePaletteItem(0, tile_type='ground', 
                                        image=pygame.image.load('res_tile/ground.png')))
    tilemap.palette.add(TilePaletteItem(1, tile_type='wall', 
                                        image=pygame.image.load('res_tile/wall.png')))
    ..

To create a tile from the palette at a specific position in the tile map
use the function
**create_tile_from_palette**\ (*position_x*,\ *position_y*,\ *tile_type*
or *id*)

.. code:: ipython3

    tilemap.create_tile_from_palette(0,0,'ground')



You can create a complete tile map with **set_all_tiles**

.. code:: ipython3

    tilemap.set_all_tiles([[1,1,1,1,1],
                           [1,0,0,0,1],
                           [1,0,0,0,1],
                           [1,0,0,0,1],
                           [1,0,0,0,1],
                           [1,0,0,0,1],
                           [1,1,1,1,1]])



A class **TileMap** can have more than one layer of tiles. Negative
values are None.

.. code:: ipython3

    new_layer = tilemap.add_layer()
    
    tilemap.set_all_tiles([[-1,-1,-1,-1,-1],
                           [-1, 4,-1,-1,-1],
                          ..
                           [-1,-1,-1, 2,-1],
                           [-1,-1,-1,-1,-1]],tile_layer=new_layer)



To see something tilemap as gameobject needs rendering component

.. code:: ipython3

    tilemap.add(TileMapRenderer(tilemap))

With class **TileController** a tile can react

.. code:: ipython3

    tilemap.palette.add(TilePaletteItem(4, tile_type='player', 
                                        image=pygame.image.load('res_tile/player_01.png'),
                                        tile_controller_class=Player))

Class **Player** is in gameloop update cycle

.. code:: ipython3

    class Player(TileController):
        def __init__(self,tile:Tile):
            super().__init__(tile)
            ..
            
        def update(self, delta_time: float):
            ..

Class **TileController** has some convinient methods.

| ``get_position()`` .. current tile position
| ``tile = self.get_tile(pos)`` .. get tile at postion
| ``tile.has_type('ground')`` .. has tile the that type
| ``set_position(new_pos)``.. change position of tile

using editor tiled
~~~~~~~~~~~~~~~~~~

You can also use the free editor **Tiled** for creating **TileMap**.
https://www.mapeditor.org



All things are saved in a JSON file (res_tile/tile.json). You can work
with layers.

.. code:: ipython3

    tilemap = TileMap.createFromTiledJSON('res_tile/tile.json')

In Tiled you can give every tile a specific tile type.



.. code:: ipython3

    tilemap = TileMap.createFromTiledJSON('res_tile/tile.json',
                                          {'box':Box, 'player':Player})

So every tile type can have its own controller.

Complete example *game_tile_tiled.py*

Changelog
---------

======= ===================================================
Version 
======= ===================================================
0.1.0   first version - August 2021
0.1.1   one tutorial and some documentation - Dezember 2021
======= ===================================================

