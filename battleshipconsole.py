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
        #print('')

    def print_own(self):
        _CHARSET_OWN = {'e': '.  ', 'o': 'O  ', 'h': 'X  ', 's': '#  ', 'c': 'o  '}
        self._print_proto(self.human_player._playfield.grid, _CHARSET_OWN)

    def print_enemy(self):
        _CHARSET_ENEMY = {'e': '.  ', 'o': '.  ', 'h': 'X  ', 's': '#  ', 'c': 'o  '}
        self._print_proto(self.ai_player._playfield.grid, _CHARSET_ENEMY)




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

game.print_own()
print('Your ships! Starting in 3')
sleep(3)
aiturn = ['', (-1, -1)]
try:
    while True:
        playerturn = ''
        print("It's your turn!")
        #sleep(1)
        while playerturn != 'checked':
            if not playerturn:
                game.print_enemy()
            playerinput = input('Your move: ')
            try:
                row, column = playerinput.split(maxsplit=2)

                playerturn = game.make_a_human_move(int(row), int(column))
            except battleshipgame.MoveInvalidError as e:
                game.print_enemy()
                print(e)
                continue
            except ValueError:
                game.print_enemy()
                print(f'{playerinput} is not a valid turn. Try again! ')
                continue
            game.print_enemy()
            print((playerturn.upper() if playerturn != 'checked' else 'MISS!') + '! ')
            if playerturn == "checked":
                sleep(2)


        # ========= Ai's turn ===============
        game.print_own()
        print("It's computer's turn!")
        #sleep(1)
        aiturn[0] = ''
        while aiturn[0] != 'checked':
            aiturn = game.make_an_ai_move()
            print(f"Computer goes {aiturn[1]}")
            sleep(2)
            game.print_own()
            print((aiturn[0].upper() if aiturn[0] != 'checked' else 'MISS') + '! ')
            sleep(2)

except battleshipgame.GameOverException as e:
    print (e)
    quit(0)
