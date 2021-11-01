from wonder import *

GRID_WIDTH = 5
GRID_HEIGHT = 7

CELL_WIDTH = 64
CELL_HEIGHT = 64


class Level(Scene):
    def create(self) -> None:
        self.background_color = BLACK

        tilemap = TileMap(GRID_WIDTH,GRID_HEIGHT,CELL_WIDTH,CELL_HEIGHT)
        self.add(tilemap)

        tilemap.palette.add(TilePaletteItem(0, tile_type='ground', image=pygame.image.load('res_tile/ground.png')))
        tilemap.palette.add(TilePaletteItem(1, tile_type='wall', image=pygame.image.load('res_tile/wall.png')))
        
        #tilemap.create_tile_from_palette(0,0,'ground')
       
        # simple tilemap
        tilemap.set_all_tiles([[1,1,1,1,1],
                              [1,0,0,0,1],
                              [1,0,0,0,1],
                              [1,0,0,0,1],
                              [1,0,0,0,1],
                              [1,0,0,0,1],
                              [1,1,1,1,1]])


        tilemap.add(TileMapRenderer(tilemap))

if __name__ == "__main__":
    game = Game(width=GRID_WIDTH*CELL_WIDTH,height=GRID_HEIGHT*CELL_HEIGHT,name='example_tile.py', scenes=[Level()])
    game.quit()