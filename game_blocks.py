from wonder import *

class Paddle(GameObject):
    DISTANCE = 20
    SPEED = 120
    def __init__(self):
        super().__init__()
        self.sprite_renderer = self.add(SpriteRenderer(self, load_from_file='res_blocks/paddleBlu.png'))
        self.transform.position = Vector2(Game.instance.width//4*3//2, 
                                          Game.instance.height - self.sprite_renderer.rect.height - self.DISTANCE)

        self.rigidbody = self.add(Rigidbody(self,DYNAMIC_BODY))
        self.rigidbody.fixed_rotation = True
        self.add(BoxCollider(self,self.rigidbody,box=(self.sprite_renderer.rect.width,
                                                      self.sprite_renderer.rect.height)))

    def update(self, delta_time):
        direction = 0.0

        keys=pygame.key.get_pressed()
    
        if keys[pygame.K_RIGHT]:
            direction = 1
        elif keys[pygame.K_LEFT]:
            direction = -1

        if keys[pygame.K_ESCAPE]:
            Game.instance.debug_physic_system_tag = not Game.instance.debug_physic_system_tag

        self.rigidbody.velocity = Vector2(1,0) * direction * self.SPEED

    @property
    def width(self)->int:
        return self.sprite_renderer.rect.width
        
class Ball(GameObject):
    SPEED = 240
    def __init__(self):
        super().__init__()
        sprite_renderer = self.add(SpriteRenderer(self, load_from_file='res_blocks/ballGrey.png'))
        self.transform.position = Vector2(Game.instance.width//4*3//2, Game.instance.height//2)
        self.rigidbody:Rigidbody = self.add(Rigidbody(self,DYNAMIC_BODY))
        self.add(CircleCollider(self,self.rigidbody,radius=sprite_renderer.rect.width//2,restitution=1.0,friction=0))
        self.rigidbody.velocity = Vector2(0,0) * self.SPEED
        self.rigidbody.mass = 0.2
        self.limit = Game.instance.height //4 * 5
    
    def start(self):
        self.rigidbody.velocity = Vector2(0,-1) * self.SPEED

    def restart(self):
        self.transform.position = Vector2(Game.instance.width//4*3//2, Game.instance.height//2)
        self.rigidbody.velocity = Vector2(0,0)

    def on_collision_enter(self, collider, impulse):
        if isinstance(collider,Paddle):
            factor = self.hit_factor(self.transform.position, collider.transform.position,collider.width)
            direction = Vector2(factor,1).normalize()
            self.rigidbody.velocity = direction * self.SPEED

    def hit_factor(self, ball_position, paddle_position, paddle_width):
        return (ball_position.x - paddle_position.x) / float(paddle_width)

    def update(self, delta_time: float):
        if self.transform.position.y > self.limit:
            get_object(ScoreManager).restart()

class Block(GameObject):
    def __init__(self, file_name):
        super().__init__()
        self.sprite_renderer = self.add(SpriteRenderer(self,load_from_file=file_name))
        self.rigidbody = self.add(Rigidbody(self,DYNAMIC_BODY))
        self.rigidbody.fixed_rotation = True
        self.add(BoxCollider(self,self.rigidbody,box=(self.sprite_renderer.rect.width,self.sprite_renderer.rect.height)))

    def on_collision_enter(self, collider, impulse):
        get_object(ScoreManager).add(80)
        destroy(self)

class Border(GameObject):
    HEIGHT = 20
    def __init__(self, width, height, position):
        super().__init__()
        image = pygame.Surface((width, height))
        image.fill(GRAY)
        self.add(SpriteRenderer(self, image=image))
        self.transform.position = position

        rigidbody = self.add(Rigidbody(self,STATIC_BODY))
        self.add(BoxCollider(self, rigidbody, box=(width,height)))

class BlockManager(GameObject):
    FILES = ['res_blocks/element_blue_rectangle.png',
             'res_blocks/element_green_rectangle.png',
             'res_blocks/element_red_rectangle.png',
             'res_blocks/element_yellow_rectangle.png']
    SPACE = 10

    def __init__(self, scene:Scene) -> None:
        super().__init__()
        self.scene = scene
        self.count = 0

    def make(self, block_pattern) -> None:
        for i, value in enumerate(block_pattern):
            for j, file_nr in enumerate(value):
                self.count += 1
                block = self.scene.add(Block(self.FILES[file_nr]))
                block.transform.position = Vector2(Border.HEIGHT+self.SPACE+block.sprite_renderer.rect.width*(j+0.5)+self.SPACE*j,
                                                   Border.HEIGHT+self.SPACE+block.sprite_renderer.rect.height*(i+0.5)+self.SPACE*i)

class ScoreManager(GameObject,MixinDraw):
    def __init__(self):
        super().__init__()
        
        self.init()

        self.text_in_play_field = Vector2(Game.instance.width//4*3//2,Game.instance.height//4*3)
        self.text_right = Vector2(Game.instance.width//4*3+Game.instance.width//4//2, Game.instance.height//8)
        self.text_space = 40

    def init(self):
        self.score = 0
        self.level = 1
        self.ball = 48

        self.block_manager = GetObject(BlockManager)
        self.start_tag = True

    def update(self, delta_time: float):
        if self.start_tag:
            keys=pygame.key.get_pressed()
        
            if keys[pygame.K_SPACE]:
                self.start_tag = False
                Game.instance.get_object(Ball).start()

    def draw(self, screen: pygame.Surface):
        if self.start_tag:
            draw_text(screen, 'press space to start game',48, ORANGE,self.text_in_play_field,alignment=TEXT_ALIGNMENT_MID)

        draw_text(screen, f'Score {self.score}',48, ORANGE,self.text_right,alignment=TEXT_ALIGNMENT_MID)
        draw_text(screen, f'Level {self.level}',48, ORANGE,Vector2(self.text_right.x, self.text_right.y+self.text_space),alignment=TEXT_ALIGNMENT_MID)
        draw_text(screen, f'Ball {self.ball}',48, ORANGE,Vector2(self.text_right.x, self.text_right.y+2*self.text_space),alignment=TEXT_ALIGNMENT_MID)

    def add(self, value):
        self.score += value

        self.block_manager.count -=1
        #print(self.block_manager.count)
        if self.block_manager.count == 0:
            Game.instance.load_scene(self.level)
            self.level += 1
            self.ball += 2 
    
    def restart(self):
        self.ball -=1
        if self.ball >= 0:
            self.start_tag = True
            get_object(Ball).restart()
        else:
            Game.instance.load_scene(0)
            self.init()

class Level(Scene):
    def create_level(self,pattern):
        self.background_color = WHITE
        Game.instance.physic_system.gravity = (0.0,0.0)

        score_manager = Game.instance.get_object(ScoreManager)

        if not score_manager:
            score_manager = self.add(ScoreManager())
            self.dont_destroy_on_load(score_manager)
            
        self.add(Paddle())

        three_quarter = Game.instance.width//4*3

        self.add(Border(three_quarter, Border.HEIGHT, Vector2(three_quarter//2,Border.HEIGHT//2)))
        self.add(Border(Border.HEIGHT, Game.instance.height-Border.HEIGHT,Vector2(Border.HEIGHT//2, (Game.instance.height+Border.HEIGHT)//2) ))
        self.add(Border(Border.HEIGHT, Game.instance.height-Border.HEIGHT,Vector2(three_quarter-Border.HEIGHT//2, (Game.instance.height+Border.HEIGHT)//2) ))

        self.add(Ball())

        block_manager = self.add(BlockManager(self))
        block_manager.make(pattern)

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

if __name__ == "__main__":
    game = Game(width=860,height=600,name='game_blocks.py',scenes=[Level1(), Level2()])
    game.quit()