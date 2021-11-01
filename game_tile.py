from wonder import *

GRID_WIDTH = 5
GRID_HEIGHT = 7

CELL_WIDTH = 64
CELL_HEIGHT = 64

class Player(TileController):
    def __init__(self,tile:Tile):
        super().__init__(tile)
        self.right = Vector2(1,0)
        self.left = Vector2(-1,0)
        self.up = Vector2(0,-1)
        self.down = Vector2(0,1)
        self.direction = None
        self.move_time = 0.3
        self.time = 0


    def update(self, delta_time: float):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_RIGHT]:
            self.direction = self.right
        elif keys[pygame.K_LEFT]:
            self.direction = self.left
        elif keys[pygame.K_DOWN]:
            self.direction = self.down
        elif keys[pygame.K_UP]:
            self.direction = self.up

        self.time += delta_time
        if self.time > self.move_time:
            self.move()
            self.time = 0
    
    def move(self):
        if self.direction:
            pos = self.get_position()
            new_pos = pos + self.direction
            tile = self.get_tile(new_pos)
            if tile is None or tile.has_type('ground'):
                self.set_position(new_pos)
            elif tile.has_type('box'):
                new_box_pos = new_pos + self.direction
                if tile.controller.can_move(new_box_pos):
                    tile.controller.move(new_box_pos)
                    self.set_position(new_pos)
            self.direction = None
                    
class Box(TileController):
    def __init__(self, tile: Tile) -> None:
        super().__init__(tile)
        self.at_home = False

    def can_move(self, pos:Vector2)->bool:
        tile = self.get_tile(pos)
        return (tile is None or tile.has_type('ground') or tile.has_type('home')) and not self.at_home

    def move(self, pos:Vector2)->None:
        if self.can_move(pos):
            if self.get_tile(pos).has_type('home'):
                self.tile.image = pygame.image.load('res_tile/box_home.png')
                self.at_home = True
            self.set_position(pos)         


class Level(Scene):
    def create(self) -> None:
        self.background_color = BLACK

        tilemap = TileMap(GRID_WIDTH,GRID_HEIGHT,CELL_WIDTH,CELL_HEIGHT)
        self.add(tilemap)

        tilemap.palette.add(TilePaletteItem(0, tile_type='ground', image=pygame.image.load('res_tile/ground.png')))
        tilemap.palette.add(TilePaletteItem(1, tile_type='wall', image=pygame.image.load('res_tile/wall.png')))
        tilemap.palette.add(TilePaletteItem(2, tile_type='home', image=pygame.image.load('res_tile/home.png')))
        tilemap.palette.add(TilePaletteItem(3, tile_type='box', image=pygame.image.load('res_tile/box.png'),tile_controller_class=Box))
        tilemap.palette.add(TilePaletteItem(4, tile_type='player', image=pygame.image.load('res_tile/player_01.png'),tile_controller_class=Player))

        tilemap.set_all_tiles([[1,1,1,1,1],
                               [1,0,0,0,1],
                               [1,0,0,0,1],
                               [1,1,1,0,1],
                               [1,0,0,0,1],
                               [1,0,0,0,1],
                               [1,1,1,1,1]])

        new_layer = tilemap.add_layer()

        tilemap.set_all_tiles([[-1,-1,-1,-1,-1],
                               [-1, 4,-1,-1,-1],
                               [-1,-1, 3,-1,-1],
                               [-1,-1,-1,-1,-1],
                               [-1, 2, 3,-1,-1],
                               [-1,-1,-1, 2,-1],
                               [-1,-1,-1,-1,-1]],tile_layer=new_layer)

        tilemap.add(TileMapRenderer(tilemap))

if __name__ == "__main__":
    game = Game(width=GRID_WIDTH*CELL_WIDTH,height=GRID_HEIGHT*CELL_HEIGHT,name='game_tile.py', scenes=[Level()])
    game.quit()