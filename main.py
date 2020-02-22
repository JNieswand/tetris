#main
import numpy as np
import copy
import matplotlib.pyplot as plt
global SIZE_X, SIZE_Y
SIZE_X = 10
SIZE_Y = 20

def turn_coordinate(coordinate):
    turn_matrix = np.array([[0, 1],[-1, 0]])
    new_coord = np.matmul(np.array([coordinate.x, coordinate.y]), turn_matrix)
    return Coordinate(new_coord[0], new_coord[1])
class Coordinate:
    def __init__(self,x, y):
        self.x = x
        self.y = y
    def is_equal(self, coordinate):
        return self.x == coordinate.x and self.y == coordinate.y
    def add(self, coordinate):
        return Coordinate(self.x + coordinate.x, self.y + coordinate.y)
    def substract(self, coordinate):
        return Coordinate(self.x - coordinate.x, self.y - coordinate.y)
    
class Game:
    def __init__(self):
        self.board = Board()
        self.falling_block = FallingBlock(self.board)
        self.inputhandler = InputHandler(self.falling_block)
        
        self.drawer = Drawer(self.board, self.falling_block)
        self.inputhandler.connect_pressevent( self.drawer.fig, self.inputhandler.on_press)
        self.over = False
    def update(self):
        self.falling_block.fall()
        if self.falling_block.laying_time >=3:
            self.board.place_falling_block(copy.deepcopy(self.falling_block))
            self.falling_block.reset()
        self.board.update()
        if self.board.full == True:
            self.over = True
        self.drawer.draw()
    
    def lost(self):
        self.drawer.message_loose()

class Board:
    def __init__(self):
        self.array = np.zeros((SIZE_X, SIZE_Y))
        self.full = False
    def at(self, coordinate):
        return self.array[coordinate.x, coordinate.y]
    def is_in(self, coordinate):
        if (coordinate.x < 0 or coordinate.x >= SIZE_X
            or coordinate.y <0 or coordinate.y >= SIZE_Y):
            return False
        return True
    def place_falling_block(self, falling_block):
        for coord in falling_block.get_coordinates():
            self.place_brick(coord)
    def place_brick(self, coordinate):
        self.array[coordinate.x, coordinate.y] = 1
    def remove_brick(self, coordinate):
        self.array[coordinate.x, coordinate.y] = 0
    def remove_row(self, index):
        self.array[:, 1:index +1] = self.array[:, 0:index]
        self.array[:, 0] = 0
    def update(self):
        for index in np.arange(SIZE_Y):
            if np.sum(self.array[:, index]) == SIZE_X:
                self.remove_row(index)
        if np.sum(self.array[:, 0]) > 0:
            self.full = True

class FallingBlock:
    def __init__(self, board):
        self.board = board
        self.reset()
        
    def reset(self):
        self.coordinate = Coordinate(int(SIZE_X/2), 0)
        geometries = np.array(["block", "t", "l", "l_inverted", "z", "z_inverted", "I"])
        index = np.random.randint(geometries.size)
        self.geometry = get_falling_block_geometry(geometries[index])
        self.laying_time = 0
    
    def get_coordinates(self):
        return np.array([ self.coordinate.add(geometry_coord) for geometry_coord in self.geometry])
    
    def fall(self):
        if self.can_move_to("down"):
            self.coordinate.y += 1
            self.laying_time = 0
        else:
            self.laying_time += 1
    def local_to_global(self, coord):
        return coord.add(self.coordinate)
    def global_to_local(self, coord):
        return coord.substract(self.coordinate)
    def turn(self):
        
        turned_geometry = np.array([])
        for coord in self.geometry:
            turned_geometry = np.append(turned_geometry, turn_coordinate(coord))
        
        for moved_coord in turned_geometry:
            if not self.board.is_in(self.local_to_global(moved_coord)):
                return False
            if not self.board.at(self.local_to_global(moved_coord)) == 0:
                return False
        self.geometry = copy.deepcopy(turned_geometry)
        return True
    def move_left(self):
        if self.can_move_to("left"):
            self.coordinate.x -=1 
    
    def move_right(self):
        if self.can_move_to("right"):
            self.coordinate.x += 1
    
    def can_move_to(self, direction):
        moved_coordinates = np.array([])
        if direction == "left":
            moved_coordinates = np.array([Coordinate( coord.x -1, coord.y) for coord in self.get_coordinates()])
        elif direction == "right":
            moved_coordinates = np.array([Coordinate( coord.x +1, coord.y) for coord in self.get_coordinates()])
        elif direction == "down":
            moved_coordinates = np.array([Coordinate( coord.x, coord.y +1) for coord in self.get_coordinates()])
        else:
            print("unknown input param")
            return False
        print(moved_coordinates)
        for moved_coord in moved_coordinates:
            if not self.board.is_in(moved_coord):
                return False
            if not self.board.at(moved_coord) == 0:
                return False
        return True


def get_falling_block_geometry(geometry):
    if geometry == "block":
        return np.array([Coordinate(0,0), Coordinate(1,0), Coordinate(0,1), Coordinate(1,1)])
    elif geometry == "t":
        return np.array([Coordinate(0,0), Coordinate(0,1), Coordinate(1,1), Coordinate(0,2)])
    elif geometry == "l":
        return np.array([Coordinate(0,0), Coordinate(0,1), Coordinate(0,2), Coordinate(1,2)])
    elif geometry == "l_inverted":
        return np.array([Coordinate(0,0), Coordinate(0,1), Coordinate(0,2), Coordinate(-1,2)])
    elif geometry == "z":
        return np.array([Coordinate(0,0), Coordinate(0,1), Coordinate(-1, 1), Coordinate(-1,2)])
    elif geometry == "z_inverted":
        return np.array([Coordinate(0,0), Coordinate(0,1), Coordinate( 1,1), Coordinate(1,2)])
    elif geometry == "I":
        return np.array([Coordinate(0,0), Coordinate(0,1), Coordinate(0,2), Coordinate(0, 3)])
    else:
        print("unknown geometry, print I instead")
        return np.array([Coordinate(0,0), Coordinate(0,1), Coordinate(0,2), Coordinate(0, 3)])
    
        
        
                    
class InputHandler:
    
    def __init__(self, falling_block):
        self.falling_block = falling_block
    def connect_pressevent(self, figure, onpress):
        figure.canvas.mpl_connect('key_press_event', onpress)
    def connect_clickevent(self, figure, onclick):
        figure.canvas.mpl_connect('button_press_event', onclick)
    def on_press(self, event):
        if event.key == "left":
            self.falling_block.move_left()
        elif event.key == "right":
            self.falling_block.move_right()
        elif event.key == "down":
            self.falling_block.fall()
        elif event.key == "up":
            if not self.falling_block.turn():
                print("Didnt Turn!")
        return
            
class Drawer:
    def __init__(self, board, falling_block):
        self.board = board
        
        self.falling_block = falling_block
        
        self.draw_array = np.zeros((SIZE_X, SIZE_Y))
        self.fig = plt.figure()
        
        self.ax = self.fig.add_subplot(111)
        self.draw()
    def draw(self):
        self.ax.clear()
        self.draw_array = copy.deepcopy(self.board.array)
        
        for coordinate in self.falling_block.get_coordinates():
            self.draw_array[coordinate.x, coordinate.y] = 1.5
            
        self.ax.imshow(np.swapaxes(self.draw_array, 0, 1), cmap = "Reds", vmax = "2")
        plt.show() 
        self.fig.canvas.draw()
    def message_loose(self):
        self.ax.set_title("GAME OVER")
        
if __name__ == "__main__":
    game = Game()
    game.update()
    while (not game.over):
        plt.pause(0.15)
        game.update()

    game.lost()

        

    