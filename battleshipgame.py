""""""





class MoveInvalidError(Exception):
    pass
class GameLogicError(Exception):
    pass


class Dot:
    """"""
    _state = None
    def __init__(self, state):
        self.state = state


    @property
    def state(self):
        return self._state
    @state.setter
    def state(self, value):
        possible_states = ('empty', 'occupied', 'hit', 'sunk', 'checked')
        if not isinstance(value, str):
            raise TypeError(f'A string is expected here, got {type(value)} instead')
        value = value.lower()
        if value in possible_states:
            self._state = value
        else:
            raise ValueError(f"Possible states are {possible_states} and {value = } isn't one of them")
    def __str__(self):
        return self._state


class Playfield:
    """"""
    _grid = []
    _size = None
    _ships = []

    def __init__(self, size):
        if not(isinstance(size, int)):
            raise TypeError(f'An int is expected here, got {type(size)} instead')
        if not (3 <= size <=20):
            raise ValueError(f'Size of playfield is too {("big", "small")[size<3]}! Valid range is [3, 20]')
        self._size = size
        for i in range(size):
            self._grid.append([])
            for j in range(size):
                self._grid[i].append(Dot('empty'))


    @property
    def size(self):
        return self._size

    @property
    def grid(self):
        return self._grid

    def printgrid(self):  #for debug purposes
        charset = {'e': '.  ', 'o': 'O  ', 'h': 'X  ', 's': '#  ', 'c': 'o  ' }
        for row in self._grid:
            [print(charset[point.state[0]], end='') for point in row]
            print('')
        print('')

    @staticmethod
    def _transposed(grid):
        return list(zip(*grid))

    def row(self, row):
        # todo errorchecking and see if i need these at all
        return self._grid[row]

    def column(self, column):
        return self._transposed(self._grid)[column]



    def try_move(self, row, column):
        try:
            cell = self._grid[row][column]
        except IndexError:
            raise MoveInvalidError(f"Move index ({row, column}) is out of bounds")
        if cell.state in ('hit', 'sunk', 'checked'):
            raise MoveInvalidError(f"Couldn't play this move since {row, column} was already {cell.state}")
        # Missed. Change cell state and return False
        elif cell.state == 'empty':
            cell.state = 'checked'
            return False
        #Hit. Change cell state and...
        elif cell.state == 'occupied':
            cell.state = 'hit' # todo willitwork
            # ...figure out which ship was hit and ...
            for index, ship in enumerate(self._ships):
                if ship.was_hit(row, column):
                    break
            #...If it sunk mark surrounding area as 'checked', mark ship as sunk and remove ship from the list
            if self._ships[index].hp == 0:
                for row, column in self._calculate_ship_surroundings(self._ships[index]):
                    self._grid[row][column].state = 'checked'
                for row, column in ship.return_area():
                    self._grid[row][column].state = 'sunk'
                self._ships.pop(index)

            return True

    def try_to_place_ship(self, ship): #todo test
        """Checks if space to be occupied by ship (and adjacent space) is free. Raises GameLogicError otherwise"""
        #print(sorted(set(ship.return_area()).union(set(self._calculate_ship_surroundings(ship)))))



        # Checking if playfield is sufficiently empty
        # Trigger warning: "try, except" abuse
        for row, column in set(ship.return_area()).union(set(self._calculate_ship_surroundings(ship))):
            try:
                condition = self._grid[row][column].state != 'empty'
            except IndexError:
                continue
            if condition:
                raise GameLogicError("Can't place a ship here. Not enough room!")
        # Checking if ship fits inside playfield. In this particular stupid order since this loop does double duty
        # (both checks that ship fits (during first loop) and fills the grid with 'occupied
        # Trigger warning: general hackiness, more "try, except" abuse.
        for row, column in sorted(ship.return_area(), reverse=True):
            try:
                self._grid[row][column].state = 'occupied'
            except IndexError:
                raise GameLogicError("Can't place a ship outside of playfield")
        # if we somehow got here
        self._ships.append(ship)
        return True



    def sink_ship(self, ship): #todo ???
        pass

    def _calculate_ship_surroundings(self, ship):
        indexes = ship.return_area()
        output=[]
        for row, column in indexes:
            for offset_row in range(-1, 2):
                for offset_column in range(-1, 2):
                    if (row + offset_row) in range(0, self._size) and (column+offset_column) in range(0, self._size):

                        output.append((row + offset_row, column+offset_column))


            # Set() is nice! We love set()!
            # This removes dublicates from output and then removes ship's own coordinates
        return tuple(set(output).difference(set(indexes)))




class Ship:
    _hp=None
    _size=None
    _vertical=None
    _row=None
    _column=None
    # todo think _occupied_area=[]

    def __init__(self, size):
        if not isinstance(size, int):
            raise TypeError(f"Ship's size must be an int.")
        if size in range(1, 5):
            self._size = size
            self._hp = size
        else:
            raise GameLogicError(f"Can't make a ship with size {size}. Possible sizes are {(range(1, 5))}")
        pass
    @property
    def hp(self): return self._hp

    @property
    def vertical(self):
        return self._vertical

    @vertical.setter  # todo Once again, is this really necessary?
    def vertical(self, value):
        try:
            bool(value)
        except TypeError:
            raise GameLogicError('Vertical must be bool')
        if self._vertical is None:
            self._vertical = bool(value)
        else:
            raise GameLogicError("Can't reorient already placed ship.")
    def configure(self,row,column,vertical): #todo:errorchecking
        self._row = int(row)
        self._column = int(column)
        self._vertical = bool(vertical)

    # @hp.setter
    # def hp(self, value):#todo is this needed?
    #     if self._hp is None:
    #         raise GameLogicError("Can't directly change ship's hp after __init__")
    #     else: self._hp = value
    @property
    def size(self): return self._size
    def return_area(self):
        if self._vertical:
            return tuple((self._row + i, self._column) for i in range(self._size))
        else:
            return tuple((self._row, self._column + i) for i in range(self._size))
    def was_hit(self, row, column):
        if (row, column) in self.return_area():
            self._hp -= 1
            return True

class Player():
    _ships = []
    def __init__(self, name):
        pass
    def _iter_ships(self): #todo why?
        for i in len(self._ships):
            yield self._ships[i]
        raise StopIteration

class AiPlayer(Player):

    def __init__(self):
        pass
    def _init_ships(self,):
        pass



class BattleShipGame():
    def __init__(self, config ):
        pass



if __name__ == '__main__':
    a = Playfield(8)
    a.try_move(2, 0)
    a.printgrid()
    s = Ship(4)
    s.configure(4, 3, True)
    a.try_to_place_ship(s)
    a.printgrid()
    a.try_move(4, 3)
    a.try_move(5, 3)
    a.try_move(6, 3)
    a.printgrid()
    print(list(sorted(a._calculate_ship_surroundings(a._ships[0]))))
    a.try_move(7, 3)
    a.printgrid()
    print(a._ships[0])

    #print(str(a.column(3)[2].state))
    #a._grid[3][3].state = 'sunk'

    #a.try_move(3, 3)

    print("""Hey you tried to launch this file directly! This won't work!
    This file contains logic for running a battleship game.
    To actually play the game instance a battleshipgame.Game() and provide the logic for user to interact with it.
    or use the provided battleshiptk.py as an example.
    """)