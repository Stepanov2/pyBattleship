import battleshipgame
from config import *
from time import sleep
class ConsoleBattleship(battleshipgame.BattleShipGame):


    def __init__(args, **kwargs):
        size = kwargs['grid_size']
        ships = kwargs['ships']
        super().__init__(size, ships)


    @staticmethod
    def _print_proto(what, charset):
        print('   ', end='')
        [print(n, end='  ') for n in range(len(what))]
        print('')
        for index, row in enumerate(what):
            print(index, end='  ')
            [print(charset[point.state[0]], end='') for point in row]
            print('')
        print('')

    def print_own(self):
        _CHARSET_OWN = {'e': '.  ', 'o': 'O  ', 'h': 'X  ', 's': '#  ', 'c': 'o  '}
        self._print_proto(self.human_player._playfield.grid, _CHARSET_OWN)

    def print_enemy(self):
        _CHARSET_ENEMY = {'e': '.  ', 'o': '.  ', 'h': 'X  ', 's': '#  ', 'c': 'o  '}
        self._print_proto(self.human_player._playfield.grid, _CHARSET_ENEMY)

    def print_enemy__(self):
        charset = {'e': '.  ', 'o': '.  ', 'h': 'X  ', 's': '#  ', 'c': 'o  '}
        print('   ', end='')
        [print(n, end='  ') for n in range(len(self.ai_player._playfield._grid))]
        print('')
        for index, row in enumerate(self.ai_player._playfield._grid):
            print(index, end='  ')
            [print(charset[point.state[0]], end='') for point in row]
            print('')
        print('')


# ======== chosing game parameters ========


#========= init game ======================
print(configs[1])
try:
    game = ConsoleBattleship(**configs[1])
except battleshipgame.GameInitError as e:
    print(e)
    print('Someone must have tinkered with config.py')
    quit(1)

#========= query player ships ============

game.human_player.place_ships_randomly() # temp


try:
    game.start()
except battleshipgame.GameInitError:
    quit(42)

try:
    while True:
        playerturn = True

        while playerturn:
            game.print_enemy()
            playerinput = input('Your move! ')
            try:
                row, column = playerinput.split(maxsplit=2)

                playerturn = game.make_a_human_move(int(row), int(column))
            except battleshipgame.MoveInvalidError as e:
                game.print_enemy()
                print(e)
                continue
            except ValueError:
                game.print_enemy()
                print('Try again!')
                continue
            print('HIT!')
        aiturn = False
        while aiturn:
            aiturn = game.make_an_ai_move()
            game.print_own()

except battleshipgame.GameOverException as e:
    print (e)
    quit(0)
