"""Main game class and its dependants.
Making this completely separate from UI was hard. But fun. But hard."""

from random import choice, randint
import copy
from math import copysign


# ========== begin exceptions ===============

class MoveInvalidError(Exception):
    """Raised, when player (or AI) tries to make illegal moves."""
    pass
class GameLogicError(Exception):
    """Basicaly a general exception for situations not covered by more specific cases."""
    pass
class GameInitError(Exception):
    """Raised if game settings are bust.
    Or if player clicked "start game" prior to placing all of his ships.*

    *Regrettably in this version there is no "start game" button. Or a way to place your own ships. ¯\_(ツ)_/¯ """
    pass

class FoundValidPlacement(Exception):
    """Raised to fall out of convoluted nested loop during random ship placement."""
    pass


class IterationSuccess(Exception):
    """Raised to inform ship_placer_function it succeeded"""
    pass

class GameOverException(Exception):
    """Self-explanatory. UI should be watching for this one and acr accordingly."""
    pass

class FoundGoodMove(Exception):
    """Raised to escape the convoluted web of nested loops, when trying to find a move that is better than random guess."""
    pass

class Dot:
    """Single element of the playfield.
    TODO: more memory efficient way to store statr than str"""
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
    """A list of lists of class Dot. It also contains player's ships."""


    def __init__(self, size):
        # It is assumed, that size is checked for validity during Battleship.__init__
        self._grid = []


        self._size = size
        for i in range(size):
            self._grid.append([])
            for _ in range(size):
                self._grid[i].append(Dot('empty'))
        self._ships = []
        self.recently_sunk_ship = None


    @property
    def size(self):
        return self._size

    @property
    def grid(self):
        # todo I'm accessing this via playfield._grid instead in 75+% of the cases. For no reason whatsoever.
        return self._grid

    def print_grid(self):  #
        """Prints grid to console. For debug only. Doesn't work for size > 10."""
        charset = {'e': '.  ', 'o': 'O  ', 'h': 'X  ', 's': '#  ', 'c': 'o  ' }
        print('   ', end='')
        [print(n, end='  ') for n in range(len(self._grid))]
        print('')
        for index, row in enumerate(self._grid):
            print(index, end='  ')
            [print(charset[point.state[0]], end='') for point in row]
            print('')
        print('')

    def try_move(self, row, column):
        """Either makes a move or raises MoveInvalidError. Sinks ships if necessary.
         Returns new state after the move if move is valid.
         Does NOT check if the game was won after this move.
         (see BattleShipGame.make_a_human_move and BattleShipGame.make_an_ai_move)"""
        if not isinstance(row, int) or not isinstance(column, int):
            raise MoveInvalidError(f'Both row and column must be int, not {type(row)} and {type(column)}')
        try:
            cell = self._grid[row][column]
        except IndexError:
            raise MoveInvalidError(f"Move index ({row, column}) is out of bounds")

        if cell.state in ('hit', 'sunk', 'checked'):
            raise MoveInvalidError(f"Couldn't play this move since {row, column} was already {cell.state}")

        # =========== Missed. Change cell state and return False==========
        elif cell.state == 'empty':
            self._grid[row][column].state = 'checked'
            # self.printgrid()
            return self._grid[row][column].state

        # =========Hit! Change cell state and...
        elif cell.state == 'occupied':
            self._grid[row][column].state = 'hit'

            # ======= ...figure out which ship was hit and ...
            for index, ship in enumerate(self._ships):  # todo: I wrote a separate method for this, damnit!
                if ship.was_hit(row, column):
                    break

            # ===...If it sunk, mark surrounding area as 'checked', mark ship as sunk, and remove ship from the list.
            if self._ships[index].hp == 0:
                for row, column in self.calculate_ship_surroundings(self._ships[index]):
                    self._grid[row][column].state = 'checked'
                for row, column in ship.return_area():
                    self._grid[row][column].state = 'sunk'
                self.recently_sunk_ship = copy.deepcopy(ship)
                self._ships.pop(index)
            # self.printgrid()
            return self._grid[row][column].state

    def try_to_place_ship(self, ship): #todo test
        """Checks if space to be occupied by ship (and adjacent space) is free. Raises GameLogicError otherwise"""

        # =====Checking if playfield is sufficiently empty
        # =====Trigger warning: "try, except" abuse.
        for row, column in set(ship.return_area()).union(set(self.calculate_ship_surroundings(ship))):
            # ====== set() is nice=)
            try:
                condition = self._grid[row][column].state != 'empty'
            except IndexError:
                continue
            if condition:
                raise GameLogicError("Can't place a ship here. Not enough room!")

        # ==== Checking if ship fits inside playfield.
        for row, column in sorted(ship.return_area(), reverse=True):
            try:
                self._grid[row][column].state = 'occupied'
            except IndexError:
                raise GameLogicError("Can't place a ship outside of playfield")

        # finally:
        self._ships.append(ship)
        return True




    def calculate_ship_surroundings(self, ship):
        """Returns coordinates of cells around the ships.
        The fact that iterable[-1] returns last element, necessitates manual checking if cell is in bounds."""
        indexes = ship.return_area()
        output=[]
        for row, column in indexes:
            for offset_row in range(-1, 2):
                for offset_column in range(-1, 2):
                    if (row + offset_row) in range(0, self._size) and (column+offset_column) in range(0, self._size):
                        output.append((row + offset_row, column+offset_column))

        # Set() is nice! We love set()!
        # This removes duplicates from output and then removes ship's own coordinates.
        # todo:tuple() may not be necessary.
        return tuple(set(output).difference(set(indexes)))


class Ship:
    """SHIP!"""

    def __init__(self, size):
        """Create an instance of ship. Only size is necessary at this point."""
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
    def vertical(self):  # todo: the usual. Not actualy using this.
        return self._vertical

    # @vertical.setter  # todo Once again, is this really necessary?
    # def vertical(self, value):
    #     try:
    #         bool(value)
    #     except TypeError:
    #         raise GameLogicError('Vertical must be bool')
    #     if self._vertical is None:
    #         self._vertical = bool(value)
    #     else:
    #         raise GameLogicError("Can't reorient already placed ship.")
    def configure(self,row,column,vertical): # todo: errorchecking
        self._row = int(row)
        self._column = int(column)
        self._vertical = bool(vertical)

    # @hp.setter #todo ....
    # def hp(self, value):
    #     if self._hp is None:
    #         raise GameLogicError("Can't directly change ship's hp after __init__")
    #     else: self._hp = value

    @property
    def size(self): return self._size

    def return_area(self):
        """Returns coordinates of cells, occupied by this ship.
        If you are calling this before calling Ship.configure - congratulations, you broke the code!"""
        if self._vertical:
            return tuple((self._row + i, self._column) for i in range(self._size))
        else:
            return tuple((self._row, self._column + i) for i in range(self._size))
    def was_hit(self, row, column):
        """Used in Playfield.try_move(). Self-explanatory."""
        if (row, column) in self.return_area():
            self._hp -= 1
            return True


class Player():
    """Contains common methods/properties for different players.
    Should not be instanced directly."""

    def __init__(self, gridsize, ships):
        # gridsize and ships are assumed to be correct at this point
        # ships = (1,2,3,4) yields one flagship, two big ships etc.
        self._setup_complete = False
        self._playfield = None  # Playfield()
        self._unplaced_ships = []
        self._size = gridsize
        self._playfield = Playfield(gridsize)

        # ships wait to be placed in self._unplaced_ships
        for ship_minus_size, ship_count in enumerate(ships):
            for _ in range(ship_count):
                self._unplaced_ships.append(Ship(4-ship_minus_size))

    @property
    def get_sunk_ship(self):  # todo I swear I use this somewhere. PyCharm insists I don't.
        return self._playfield.recently_sunk_ship
    def place_ships_randomly(self):
        """Tries (very hard) to place every ship onto playfield."""
        max=self._playfield.size - 1

        playfield_copy = copy.deepcopy(self._playfield)
        # === If attempt to place ships fails, we can roll back to playfield_copy and try again.
        # Also, this makes it possible to call this function to only shuffle ships that weren't placed by hand. (Neat!)

        try:  # sooooooooo
            for num_reshufles in range(40):  # do 40 attempts
                self._playfield = copy.deepcopy(playfield_copy)  # roll back playfield for each attempt
                generator_func = self.iter_unplaced_ships()  # restarting generator for each attempt...
                # iter_unplaced_ships raises IterationSuccess if there are no more ships to place.
                for ship in generator_func:  # ...of itering through every ship...
                    for attempts_to_place_current_ship in range(100):  # ...and trying 100 random placements for each.
                        ship.configure(randint(0, max), randint(0, max), choice((True, False)))  # Randomizing ship.
                        try:
                            self._playfield.try_to_place_ship(ship)
                        except GameLogicError:
                            continue  # next attempt
                        break  # on successful ship placement
                    else:  # (nobreak) if no successful ship placement, go ahead and...
                        break  # break the "for ship..." loop and start over
                else:  # (nobreak) if nothing breaked the "for ship..." loop. We're done bby!
                    break  # out of for num_reshufles loop

        except IterationSuccess:
            # we telport here if we succeeded to place all ships.
            print (f'Passed, {num_reshufles+1} attempts')  # debug
            self._unplaced_ships = []
            return

        # we end up here if generation failed.
        else:
            raise GameInitError(f'Failed, to place ships after {num_reshufles + 1} attempts')


    @property
    def count_ships(self):
        return len(self._playfield._ships)
    @property
    def count_unplaced_ships(self):
        return len(self._unplaced_ships)

    def iter_ships(self): # todo this is unused :-/
        """Yields all ships from biggest to smallest. Raises IterationSuccess when done."""
        for ship in sorted(self._playfield._ships, key=lambda x: x.size, reverse=True):
            yield ship
        raise IterationSuccess('No more ships!')

    def iter_unplaced_ships(self):
        """Yields all _unplaced_ ships from biggest to smallest. Raises IterationSuccess when done."""
        for ship in sorted(self._unplaced_ships, key=lambda x: x.size, reverse=True):
            yield ship
        raise IterationSuccess('No more unplaced ships!')

    # def configure(self): #todo unused
    #     pass
    #
    # def attemt_to_place_ship(self, index): # todo unused
    # # similar to playfield method, but deletes ship from unplaced_ships on success
    #     try:
    #         self._playfield.try_to_place_ship(self._unplaced_ships[index])
    #     except TypeError:
    #         raise GameInitError('Bad index')

    def try_move(self, row, column):
        """Passthrough for Playfield.try_move"""
        return self._playfield.try_move(row, column)


class AiPlayer(Player):
    """Fun fact: all it takes to turn AI into Human is removing self.place_ships_randomly() =)"""

    def __init__(self, size, ships):
        super().__init__(size, ships)
        self.place_ships_randomly()
        pass



class HumanPlayer(Player):
    """Fun fact: to turn Human into AI add self.place_ships_randomly() =)"""
    def __init__(self, size, ships):
        super().__init__(size, ships)
        pass


"""364 lines later:"""
class BattleShipGame():
    """This does nothing by itself, but provides the methods to create an interface with the game.
    Well, mostly. I tried my best anyway."""
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

        # Quick and dirty check that ships occupy 33% of playfield or less
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
        """Try to start the game. If __init__ was successful, only thing preventing game from starting is this:"""
        if self.human_player.count_unplaced_ships != 0:
            raise GameInitError(f'Pesky human failed to place all his ships!')
        else:
            self._game_started = True

    @property
    def winner(self):
        """Returns winner (AI or Human) or None."""
        return self._game_winner
    def make_a_human_move(self, i, j):
        """Tries a move chosen by player and returns state of ai_player._grid[i][j] after the move.
        try_move will raise MoveInvalidError if needed, so no additional input checking required."""

        if self._game_started and not self._game_winner:
            result = self.ai_player.try_move(i, j)
            #
            if self.ai_player.count_ships == 0:
                self._game_winner = 'Human'
                raise GameOverException(f"{self._game_winner} won this game!")
            return result
    @classmethod
    def search_for_good_move(cls, grid, initial_row, initial_column, diff_row, diff_column):
        """Helper that tries to find a cell in certain direction, that wasn't hit or checked.
        See BattleshipGame.make_an_ai_move first.
        Trigger warning: recursion"""

        if abs(diff_row) > 3 or abs(diff_column) > 3:  # this should never happen, but just in case =)
            return None

        try:  # are we trying to search outside the grid?
            _ = grid[initial_row + diff_row][initial_column + diff_column]
        except IndexError:
            return None  # no point in continuing then

        else:  # is this cell a potential move?
            if grid[initial_row + diff_row][initial_column + diff_column].state in ("occupied", "empty"):
                move = (initial_row + diff_row, initial_column + diff_column)      # still no cheating=)
                return move # we struck gold

            # if this cell is 'checked'...
            elif grid[initial_row - diff_row][initial_column - diff_column].state == 'checked':
                return None # we need to search in opposite direction

            # if none of the above:
            else: #searching deeper
                return cls.search_for_good_move(grid, initial_row, initial_column,
                                            int(diff_row + copysign(1, diff_row)) if diff_row else 0 ,
                                            int(diff_column + copysign(1, diff_column)) if diff_column else 0)
                                            # copysign (1, value) returns sign of value. As float....

    def make_an_ai_move(self):
        """This tries to sink 'hit' ships. If there are None, does a random move instead
        Important note: 
        Unlike make_player_move,this returns list[outcome_of_move, tuple(coordinates_of_move)] instead of just outcome.
        This is dumb and make_player_move should be changed to the same format for consistency"""  # todo <--

        if self._game_started and not self._game_winner:
            try:

                """
                Общий алгоритм:
                1. находим подбитую клетку
                2. если у подбитой клетки нет подбитых соседей, бьем в первого 'occupied' или 'empty' соседа
                3. если у клетки есть подбитый сосед, то, в том же направлении ищем, либо 
                -свободную клетку и фигачим по ней
                -проверенную клетку или конец поля и прекращаем поиск.
                4. то же, но в обратном направлении.
                5. если ничего не нашлось, то:
                во-первых, что-то в этой функции или внутренней логике игры сломано
                во-вторых, AI всё равно попробует случайный ход из чувства глубокого сострадания к недалёкому прогеру)
                Спасибо, AI =)
                """

                grid=self.human_player._playfield.grid
                for rowindex, row in enumerate(grid):  # for each row...
                    for cellindex, cell in enumerate(row): # in every cell...
                        if cell.state == 'hit':  # (step 1) searching for first 'hit' but not 'sunk' one
                            neighbours = self.get_neighbours(rowindex, cellindex)
                            # getting indexes of four (or less than four if literally edge case;) ) adjacent cells
                            for neighbour in neighbours: # (step 2)
                                if not (grid[neighbour[0]][neighbour[1]].state == 'hit'):
                                    continue
                                break
                            else:  # (nobreak) if none of the neighbours are hit yet:
                                for i, j in neighbours:
                                    if grid[i][j].state != "checked":
                                        move = (i,j)
                                        # print('No neighbours')
                                        raise FoundGoodMove
                                # note: above cycle should always result in a valid move

                            # preparation for steps 3 and 4. Figuring out ship's direction
                            for neighbour in neighbours:
                                if grid[neighbour[0]][neighbour[1]].state == 'hit':
                                    diff_row =  neighbour[0] - rowindex
                                    diff_column = neighbour[1] - cellindex
                                    break

                            # step 3 searching in positive direction
                            move = BattleShipGame.search_for_good_move(grid,
                                                                       rowindex + diff_row,
                                                                       cellindex + diff_column,
                                                                       diff_row, diff_column)
                            if not move is None:
                                raise FoundGoodMove

                            # step 4 searching in negative direction
                            move = BattleShipGame.search_for_good_move(grid, rowindex, cellindex,
                                                                       -diff_row, -diff_column)
                            if not move is None:
                                raise FoundGoodMove

            # if at any point above we found a good move, we end up here:
            except FoundGoodMove:
                # print(move)
                result = self.human_player.try_move(*move)  # note: can't return this just yet.

            # if no ships on fire (or broken algorithm above)
            else:
                for _ in range(2048):  # trying a random move 2048 times
                    move=(randint(0, self._size), randint(0, self._size))
                    try:
                        result = self.human_player.try_move(*move)
                    except MoveInvalidError:
                        continue
                    else:
                        break
                else: # no break
                    raise GameOverException('AI was unable to make a move, stupid AI!')  # more like stupid developer=)

            if result != 'sunk':
                return [result, move]
            # if last move sunk a ship, there is a chance, that game is over now.
            else:
                if self.human_player.count_ships == 0:
                    self._game_winner = 'AI'
                    raise GameOverException(f"{self._game_winner} won this game!")
                return [result, move]


    def get_neighbours(self, row, column):
        """Returns indexes for adjecent cells"""
        output = [(row-1, column), (row+1, column), (row, column-1), (row, column+1)]
        for index, value in enumerate(output):
            if not (0 <= value[0] < self._size) or not (0 <= value[1] < self._size):
                output.pop(index)
        return output









if __name__ == '__main__':

    print(
    """    Hey! You tried to launch this file directly! This won't work!
    This file contains logic for running a battleship game.
    Launch battleshiptk.py to play a GUI version of the game
    or battleshipconsole.tk to play a console version of the game.
    Or you can instance a battleshipgame.Game() and create your own UI=)
    IMPORTANT: if you want to read the code do it in following order:
    config.py, battleshipgame.py, battleshiptk.py or battleshipconsole.py
    """)