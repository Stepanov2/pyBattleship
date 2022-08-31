""""""
from random import choice, randint
import copy





class MoveInvalidError(Exception):
    pass
class GameLogicError(Exception):
    pass
class GameInitError(Exception):
    pass

class FoundValidPlacement(Exception):
    pass


class IterationSuccess(Exception):
    pass

class GameOverException(Exception):
    pass

class Dot:
    """"""
    #_state = None
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


    def __init__(self, size):
        # It is assumed, that size is checked for validity during Battleship.__init__
        self._grid = []


        self._size = size
        for i in range(size):
            self._grid.append([])
            for _ in range(size):
                self._grid[i].append(Dot('empty'))
        self._ships = []


    @property
    def size(self):
        return self._size

    @property
    def grid(self):
        return self._grid

    def printgrid(self):  #for debug purposes
        charset = {'e': '.  ', 'o': 'O  ', 'h': 'X  ', 's': '#  ', 'c': 'o  ' }
        print('   ', end='')
        [print(n, end='  ') for n in range(len(self._grid))]
        print('')
        for index, row in enumerate(self._grid):
            print(index, end='  ')
            [print(charset[point.state[0]], end='') for point in row]
            print('')
        print('')

    @staticmethod
    def _transposed(grid): #todo same as below
        return list(zip(*grid))

    def row(self, row):
        # todo errorchecking and see if i need these at all
        return self._grid[row]

    def column(self, column):
        return self._transposed(self._grid)[column]



    def try_move(self, row, column):
        if not isinstance(row, int) or not isinstance(column, int):
            raise MoveInvalidError(f'Both row and column must be int, not {type(row)} and {type(column)}')
        try:
            cell = self._grid[row][column]
        except IndexError:
            raise MoveInvalidError(f"Move index ({row, column}) is out of bounds")
        if cell.state in ('hit', 'sunk', 'checked'):
            raise MoveInvalidError(f"Couldn't play this move since {row, column} was already {cell.state}")
        # Missed. Change cell state and return False
        elif cell.state == 'empty':
            self._grid[row][column].state = 'checked'
            #self.printgrid()
            return self._grid[row][column].state
        #Hit. Change cell state and...
        elif cell.state == 'occupied':
            self._grid[row][column].state = 'hit' # todo willitwork
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
            #self.printgrid()
            return self._grid[row][column].state

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


    def __init__(self, size):
        if not isinstance(size, int):
            raise GameLogicError(f"Ship's size must be an int.")
        if size in range(1, 5):
            self._size = size
            self._hp = size
        else:
            raise GameLogicError(f"Can't make a ship with size {size}. Possible sizes are {(range(1, 5))}")
        # self._hp = None
        # self._size = None
        self._vertical = None
        self._row = None
        self._column = None
        # todo think _occupied_area=[]
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

    def __init__(self, gridsize, ships):
        # gridsize and ships are assumed to be correct
        self._setup_complete = False
        self._playfield = None  # Playfield()
        self._unplaced_ships = []
        self._size = gridsize


        self._playfield = Playfield(gridsize)
        print(f'player.__init__ was called !')
        for ship_minus_size, ship_count in enumerate(ships):
            for _ in range(ship_count):
                self._unplaced_ships.append(Ship(4-ship_minus_size))
                print(len(self._unplaced_ships))

    def place_ships_randomly(self):
        max=self._playfield.size - 1
        playfield_copy = copy.deepcopy(self._playfield)  # this allows us to partially set up the ships by
                                                    # hand and only fill the rest
        try:  # sooooooooo
            for num_reshufles in range(40):  # do 40 attempts
                self._playfield = copy.deepcopy(playfield_copy) # re-init playfield for each attempt
                generator_func = self.iter_unplaced_ships() # restarting generator for each attempt
                for ship in generator_func:  # of itering through every ship
                    for attempts_to_place_current_ship in range(100):  # and trying 100 random placements
                        ship.configure(randint(0, max), randint(0, max), choice((True, False)))  # randomizing it
                        try:
                            self._playfield.try_to_place_ship(ship)
                        except GameLogicError:
                            continue  # next attempt
                        #self._playfield.printgrid()
                        break  # on successful ship placement
                    else:  # if no successful ship placement:
                        break  # for ship loop and start over
                else:  # if nothing breaked for ship loop we're done
                    break  # out of for num_reshufles loop

        except IterationSuccess:
             print (f'Passed, {num_reshufles+1} attempts')
             self._unplaced_ships = []

             return
        else:
            raise GameInitError(f'Failed, to place ships after {num_reshufles + 1} attempts')


    @property
    def count_ships(self):
        return len(self._playfield._ships)
    @property
    def count_unplaced_ships(self):
        return len(self._unplaced_ships)

    def iter_ships(self): #todo why? nvm it's ok
        for ship in sorted(self._playfield._ships, key=lambda x: x.size, reverse=True):
            yield ship
        raise IterationSuccess('No more ships!')

    def iter_unplaced_ships(self): #todo why? nvm it's ok but will it work if ships are popped in process?
        for ship in sorted(self._unplaced_ships, key=lambda x: x.size, reverse=True):
            yield ship
        raise IterationSuccess('No more unplaced ships!')

    def configure(self):
        pass #todo

    def attemt_to_place_ship(self, index):
    # similar to playfield method, but deletes ship from unplaced_ships on success
        try:
            self._playfield.try_to_place_ship(self._unplaced_ships[index])
        except TypeError:
            raise GameInitError('Bad index')

    def try_move(self, row, column):
        return self._playfield.try_move(row, column)




class AiPlayer(Player):

    def __init__(self, size, ships):
        super().__init__(size, ships)
        self.place_ships_randomly()

        pass
    def _init_ships(self, size, ships):

        pass


class HumanPlayer(Player):

    def __init__(self, size, ships):
        super().__init__(size, ships)
        pass
    def _init_ships(self, **kwargs):

        pass

class BattleShipGame():
    def __init__(self, size, ships):
        # Checking size
        if not (isinstance(size, int)):
            raise GameInitError(f'An int is expected here, got {type(size)} instead')
        if not (3 <= size <= 20):
            raise GameInitError(f'Size of playfield is too {("big", "small")[size < 3]}! Valid range is [3, 20]')

        # Checking ship config
        if not (isinstance(ships, tuple) or isinstance(ships, list)):
            raise GameInitError(f'Expected list or tuple of four ship counts, got something else: '
                                f'({type(ships), ships})')
        if len(ships) != 4:
            raise GameInitError(f'Expected exactly four ship counts, got {len(ships)}')
        for i in ships:
            if not isinstance(i, int):
                raise GameInitError(f'{i} is not a valid number of ships! Expecting int, 0 or more.')
        sum_ships = 0
        for i in range(0, len(ships)):
            sum_ships += ships[i] * (4 - i)
        if sum_ships > size * size * 0.33:
            raise GameInitError(f"Ships can't occupy more than 33% of playfield")
        # If all is golden, initialize Ai player and Human player
        self.human_player = HumanPlayer(size, ships)
        self.ai_player = AiPlayer(size, ships)
        self._game_started = False
        self._game_winner = None
        self._size = size

    def start(self):
        if self.human_player.count_unplaced_ships != 0:
            raise GameInitError(f'Pesky human failed to place all his ships!')
        else:
            self._game_started = True

    @property
    def has_winner(self):
        return self._game_winner
    def make_a_human_move(self, i, j):
        # error_checking?
        if self._game_started and not self._game_winner:
            result = self.ai_player.try_move(i, j)
            if self.ai_player.count_ships == 0:
                self._game_winner = 'Human'
                raise GameOverException(f"{self._game_winner} won this game!")
            return result
    def make_an_ai_move(self):
        if self._game_started and not self._game_winner:
            for _ in range(1024):
                move=(randint(0, self._size), randint(0, self._size))
                try:
                    result =  self.human_player.try_move(*move)
                except MoveInvalidError:
                    continue
                else:
                    break
            else: # no break
                raise GameOverException('AI was unable to make a move, stupid AI!')
            #result = self.human_player.try_ai_move()
            if result != 'sunk':
                return [result, move]
            else:
                if self.human_player.count_ships == 0:
                    self._game_winner = 'AI'
                    raise GameOverException(f"{self._game_winner} won this game!")
                return [result, move]









if __name__ == '__main__':
    # a = Playfield(8)
    # a.try_move(0, 0)
    # a.printgrid()
    # s = Ship(4)
    # s.configure(4, 3, True)
    # a.try_to_place_ship(s)
    # a.printgrid()
    # a.try_move(4, 3)
    # a.try_move(5, 3)
    # a.try_move(6, 3)
    # a.printgrid()
    # print(list(sorted(a._calculate_ship_surroundings(a._ships[0]))))
    # a.try_move(7, 3)
    # a.printgrid()
    #print(a._ships[0])
    g = BattleShipGame(8, (1,2,3,4))
    for i in range(len(g.ai_player._unplaced_ships)):
        print(g.human_player._unplaced_ships[i]._size, end=' ')
    print('')
    for i in range(len(g.ai_player._unplaced_ships)):
         print(g.human_player._unplaced_ships[i]._size, end=' ')
    print('')
    g.ai_player._playfield.printgrid()
    g.ai_player._unplaced_ships[0].configure(0, 0, True)
    g.ai_player._playfield.try_to_place_ship( g.ai_player._unplaced_ships[0])
    g.ai_player._unplaced_ships.pop(0)
    g.ai_player.place_ships_randomly()
    #g.ai_player.place_ships_randomly()

    g.ai_player._playfield.printgrid()




    print("""Hey you tried to launch this file directly! This won't work!
    This file contains logic for running a battleship game.
    To actually play the game instance a battleshipgame.Game() and provide the logic for user to interact with it.
    or use the provided battleshiptk.py as an example.
    """)