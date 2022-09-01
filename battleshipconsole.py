"""Console variant of the game. Game logic is in battleshipgame.py
Also try battleshiptk.py =)"""

import battleshipgame
from config import *
from time import sleep


class ConsoleBattleship(battleshipgame.BattleShipGame):
    """This extends BattleShipGame and adds methods for output as well as mainloop."""
    # Well, I promised I won't fix anything after midnight, so I am not adding that "self, *" before args=)
    # Funnily enough it still works somehow=)
    def __init__(args, **kwargs): #
        size = kwargs['grid_size']
        ships = kwargs['ships']
        super().__init__(size, ships)


    @staticmethod
    def _print_proto(what, charset):
        """A prototype for a printing function. Should've used decorators instead =)"""
        print('   ', end='')
        [print(n, end='  ') for n in range(len(what))]
        print('')
        for index, row in enumerate(what):
            print(index, end='  ')
            [print(charset[point.state[0]], end='') for point in row]
            print('')
        #print('')

    def print_own(self):
        """Prints human player's playfield."""
        _CHARSET_OWN = {'e': '.  ', 'o': 'O  ', 'h': 'X  ', 's': '#  ', 'c': 'o  '}
        self._print_proto(self.human_player._playfield.grid, _CHARSET_OWN)

    def print_enemy(self):
        """Prints AI's playfield. The only difference is that both 'occupied' and 'empty' tiles displayed as '.'"""
        _CHARSET_ENEMY = {'e': '.  ', 'o': '.  ', 'h': 'X  ', 's': '#  ', 'c': 'o  '}
        self._print_proto(self.ai_player._playfield.grid, _CHARSET_ENEMY)

    def main_loop(self):
        game.print_own()
        print('Your ships! Starting in 3')
        sleep(3)
        aiturn = ['', (-1, -1)]  # init this for later

        try:
            while True:
                # ======= Game loop ============
                playerturn = ''
                print("It's your turn!")
                # sleep(1)

                # ======= Player's turn ===========
                while playerturn != 'checked':
                    if not playerturn:  # only if first turn
                        self.print_enemy()

                    playerinput = input('Your move: ')
                    try:  # ...to execute a turn
                        row, column = playerinput.split(maxsplit=2)
                        playerturn = self.make_a_human_move(int(row), int(column))
                    except battleshipgame.MoveInvalidError as e:
                        self.print_enemy()
                        print(e)
                        continue  # back to the top of the loop if player makes invalid move
                    except ValueError:
                        self.print_enemy()
                        print(f'{playerinput} is not a valid turn. Try again! ')
                        continue  # back to the top of the loop if player types gibberish

                    self.print_enemy()
                    print((playerturn.upper() if playerturn != 'checked' else 'MISS!') + '! ')
                    if playerturn == "checked":  # give player a moment to contemplate his misfortune)
                        sleep(2)

                # ========= Ai's turn ===============
                self.print_own()
                print("It's computer's turn!")
                # sleep(1)
                aiturn[0] = ''
                while aiturn[0] != 'checked':
                    aiturn = self.make_an_ai_move()
                    print(f"Computer goes {aiturn[1]}")
                    sleep(2)
                    self.print_own()
                    print((aiturn[0].upper() if aiturn[0] != 'checked' else 'MISS') + '! ')
                    sleep(2)

        # ===== If the game was won, raise exception ====
        except battleshipgame.GameOverException as e:
            print(e)
            return
        # otherwise, loop "while True"


if __name__ == '__main__':

    # ======== chosing game parameters ========


    while True:
        playerinput = input("Type 1, 2 or 3 for small, medium or large game respectively! ")
        try:
            playerinput = int(playerinput)
        except ValueError:
            continue
        if not playerinput in range(1,4):
            continue
        chosenconfig = playerinput - 1
        break




    #========= init game ======================
    while True:


        try:
            game = ConsoleBattleship(**configs[chosenconfig])
        except battleshipgame.GameInitError as e:
            print(e)
            print('Someone must have tinkered with config.py!')
            quit(1)

        # ========= query player ships ============

        game.human_player.place_ships_randomly()  # HAX!

        # ====== setup is completed =========
        try:
            game.start()
        except battleshipgame.GameInitError:
            quit(42)

        game.main_loop()

        # ========game.ended=========
        if game.winner == 'Human':
            game.print_enemy()
            print("You've won, pal! Congrats!")
        else:
            game.print_own()
            print("You've lost, pal! Tough luck!")

        # ====== another go? =============
        while True:
            query = input("Press enter to quit or type \"MORE\" to play again")
            if not query.upper() in ('', 'MORE'):
                continue
            if query == '':
                quit(0)
            if query.upper() == 'MORE':
                break


