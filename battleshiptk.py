import battleshipgame
from config import *
from time import sleep, time_ns
import tkinter as tk
from tkinter import ttk
from random import choice
from tkinter import messagebox

class SetupPlayer(battleshipgame.Player):
    def __init__(self, size, ships):
        super().__init__(size, ships)
        self.place_ships_orderly()
    def place_ships_orderly(self):
        max = self._playfield.size
        # todo tihs works well enough but not exactly as intended %)
        generator_func = self.iter_unplaced_ships()  # restarting generator for each attempt
        try:
            for ship in generator_func:
                for row in range(max):
                    for column in range(0, max, 2):
                        try:
                            ship.configure(row, column, True)
                            self._playfield.try_to_place_ship(ship)
                        except battleshipgame.GameLogicError:
                            continue
                        break  # found a spot for ship
                    else:  # (NoBreak) failed to find a spot
                        continue # for row loop
                    break # for row loop
        except battleshipgame.IterationSuccess:
             print (f'Orederly placement successful!')
             self._unplaced_ships = []

             return
        else:
            raise battleshipgame.GameInitError(f'Failed, to orderly place ships!')



class TkinterBattleship(battleshipgame.BattleShipGame):

    @staticmethod
    def configure_enemy_button(button, state):
        _CHARSET_ENEMY = {'e': '.', 'o': '.', 'h': 'X', 's': '#', 'c': 'o'}
        _BG_ENEMY = {'e': '#DDDDFF', 'o': '#DDDDFF', 'h': '#FF7777', 's': '#770000', 'c': '#AAAAAA'}
        _STATE_ENEMY = {'e': 'normal', 'o': 'normal', 'h': 'disabled', 's': 'disabled', 'c': 'disabled'}
        _RELIEF_ENEMY = {'e': 'raised', 'o': 'raised', 'h': 'raised', 's': 'raised', 'c': 'sunken'}
        state = state[0]
        button.configure(text=_CHARSET_ENEMY[state],
                         bg=_BG_ENEMY[state],
                         state=_STATE_ENEMY[state],
                         relief=_RELIEF_ENEMY[state]
                         )

    @staticmethod
    def configure_own_button(button, state):
        _CHARSET_OWN = {'e': '.', 'o': '.', 'h': 'X', 's': '#', 'c': 'o'}
        _BG_OWN = {'e': '#DDDDFF', 'o': '#777777', 'h': '#FF7777', 's': '#770000', 'c': '#AAAAAA'}
        _STATE_OWN = {'e': 'normal', 'o': 'normal', 'h': 'disabled', 's': 'disabled', 'c': 'normal'}
        _RELIEF_OWN = {'e': 'sunken', 'o': 'raised', 'h': 'raised', 's': 'raised', 'c': 'sunken'}
        state = state[0]
        button.configure(text=_CHARSET_OWN[state],
                         bg=_BG_OWN[state],
                         state=_STATE_OWN[state],
                         relief=_RELIEF_OWN[state]
                         )
    def __init__(self, *args, **kwargs):
        start_time = time_ns()
        size = kwargs['grid_size']
        ships = kwargs['ships']
        try:
            super().__init__(size, ships)
        except battleshipgame.GameInitError as e:
            print(e)
            quit(1)

        try:
            self.setup_player = SetupPlayer(size, ships)
        except battleshipgame.GameInitError as e:
            print(e)
            quit(1)
        #self.setup_player._playfield.print_grid()

        self.hovered_ship=battleshipgame.Ship(1)
        btn_width = kwargs['tkinterconfig']['btn_width']
        btn_height = kwargs['tkinterconfig']['btn_height']
        # ==== begin tkinter main window
        self.root = tk.Tk()
        self.root.title('Quick and dirty Battleship for python')

        window_width = 1000
        window_height = 500
        try:
            window_height = kwargs['tkinterconfig']['win_height']
        except KeyError:
            pass
        #print(window_height)


        center_x = int((self.root.winfo_screenwidth() - window_width) / 2)
        center_y = int((self.root.winfo_screenheight() - window_height) / 2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.root.resizable(False, False)



        grid_size = size
        num_columns = grid_size * 2 + 3
        for i in range(num_columns):
            self.root.columnconfigure(i, weight=1)
        for i in range(grid_size + 2):
            self.root.rowconfigure(i, weight=1)
        self.enemy_buttons = [[] for _ in range(grid_size)]
        self.own_buttons = [[] for _ in range(grid_size)]

        self.top_label = ttk.Label(self.root, text="Welcome to the game, buddy!", anchor=tk.CENTER, background="#fefefe")
        self.top_label.grid(column=0, row=0, columnspan=num_columns, sticky=tk.N)
        for i in range(0, grid_size):
            ttk.Label(self.root, text='#').grid(row=i + 1, column=0)
            for j in range(0, grid_size):
                self.enemy_buttons[i].append(tk.Button(self.root,
                                                  text=' ',
                                                  command=lambda i1=i, j1=j: self.enemy_clicked(i1, j1)))

                self.enemy_buttons[i][j].bind("<Enter>", lambda e, i1=i, j1=j: self.enemy_hover(e, index=(i1, j1)))
                self.enemy_buttons[i][j].config(width=btn_width, height=btn_height)
                self.enemy_buttons[i][j].grid(row=i + 1, column=j + 1)
                #print(j + 1)
            ttk.Label(self.root, text='#').grid(row=i + 1, column=grid_size + 1)

            for j in range(0, grid_size):
                self.own_buttons[i].append(tk.Button(self.root,
                                                text=' ',
                                                command=lambda i1=i, j1=j: self.own_clicked(i1, j1)))
                self.own_buttons[i][j].bind("<Enter>", lambda e, i1=i, j1=j: self.own_hover(e, index=(i1, j1)))
                self.own_buttons[i][j].config(width=btn_width, height=btn_height)
                self.own_buttons[i][j].grid(row=i + 1, column=grid_size + j + 2)
                #print(grid_size + j + 2)

            ttk.Label(self.root, text='#').grid(row=i + 1, column=(grid_size + 1) * 2)
            #print((grid_size + 1) * 2)

        self.btm_label = ttk.Label(self.root, text="Make a move!", anchor=tk.CENTER,
                              background="#fefefe")
        self.btm_label.grid(column=0, row=grid_size + 1, columnspan=num_columns, sticky=tk.S)


        self.human_player.place_ships_randomly()  # only for debug, hopefully
        self.start() # both of theese should be called by buttons

        #========= Linking buttons to grid =============



        for row in range(size):
            for column in range(size):
                own_state = self.human_player._playfield.grid[row][column].state
                enemy_state = self.ai_player._playfield.grid[row][column].state
                self.configure_enemy_button(self.enemy_buttons[row][column], enemy_state)
                self.configure_own_button(self.own_buttons[row][column], own_state)






        print(f"Initialized in {(time_ns() - start_time) / 1000 ** 2} ms")
        self.root.mainloop()




    def enemy_clicked(self, *args, **kwargs):
        if self.enemy_buttons[args[0]][args[1]].cget('state') == 'disabled':
            return

        # ==== Human's turn==============
        if self._game_started and not self.winner:
            playerturn=''
            try:
                playerturn = self.make_a_human_move(args[0], args[1])
                self.configure_enemy_button(self.enemy_buttons[args[0]][args[1]], playerturn)
                if playerturn == 'hit':
                    return
                if playerturn == 'sunk':
                    for row, column in self.ai_player.get_sunk_ship.return_area():
                        self.configure_enemy_button(self.enemy_buttons[row][column], 'sunk')
                    surroundings = self.ai_player._playfield.calculate_ship_surroundings(self.ai_player.get_sunk_ship)
                    for row, column in surroundings:
                        self.configure_enemy_button(self.enemy_buttons[row][column], 'checked')

            except battleshipgame.GameOverException:
                surroundings = self.ai_player._playfield.calculate_ship_surroundings(self.ai_player.get_sunk_ship)
                for row, column in self.ai_player.get_sunk_ship.return_area():
                    self.configure_enemy_button(self.enemy_buttons[row][column], 'sunk')
                for row, column in surroundings:
                    self.configure_enemy_button(self.enemy_buttons[row][column], 'checked')
                messagebox.showinfo(title="We have a winner",
                                    message=f'{self.winner} have won. All hail {self.winner}!')
                return
            if playerturn == 'checked':

                # ======== AI's turn==========
                aiturn = ['', (-1, -1)]
                try:
                    #self.top_label.configure(text="AI's turn!")
                    self.btm_label.configure(text="AI is thinking!")
                    while aiturn[0] != 'checked':
                        self.btm_label.configure(text="AI is thinking!")
                        aiturn = self.make_an_ai_move()
                        self.btm_label.configure(text=(aiturn[0].upper() if aiturn[0] != 'checked' else 'MISS') + '! ')
                        self.configure_own_button(self.own_buttons[aiturn[1][0]][aiturn[1][1]], aiturn[0])
                        if aiturn[0] == 'hit':
                            continue
                        if aiturn[0] == 'sunk':
                            for row, column in self.human_player.get_sunk_ship.return_area():
                                self.configure_own_button(self.own_buttons[row][column], 'sunk')
                            surroundings = self.human_player._playfield.calculate_ship_surroundings(
                                self.human_player.get_sunk_ship)
                            for row, column in surroundings:
                                self.configure_own_button(self.own_buttons[row][column], 'checked')
                            continue
                except battleshipgame.GameOverException:
                    surroundings = self.human_player._playfield.calculate_ship_surroundings(self.human_player.get_sunk_ship)
                    for row, column in self.human_player.get_sunk_ship.return_area():
                        self.configure_own_button(self.own_buttons[row][column], 'sunk')
                    for row, column in surroundings:

                        self.configure_own_button(self.own_buttons[row][column], 'checked')
                    messagebox.showinfo(title="We have a winner",
                                        message=f'{self.winner} have won. All hail {self.winner}!')
                    self.top_label.configure(text="AI won!")
                    return
                #self.top_label.configure(text="Human's turn!")

        else:
            pass  # todo

    def own_clicked(self, *args, **kwargs):
        #print(*args, 'Friend playfield!')
        if self._game_started:
            pass
        else:
            pass #todo

    def enemy_hover(self,*args, **kwargs):
        return


    def own_hover(self, *args, **kwargs):
        return





def pick(*args):

    global chosen_gamemode
    chosen_gamemode = args[0]
    print(args)
    gameinitwindow.destroy()
if __name__ == '__main__':

    chosen_gamemode=0
    gameinitwindow = tk.Tk()
    for item in configs:
        tk.Button()

    gameinitwindow.title('Quick and dirty Battleship for python')

    window_width = 600
    window_height = 150
    center_x = int((gameinitwindow.winfo_screenwidth() - window_width) / 2)
    center_y = int((gameinitwindow.winfo_screenheight() - window_height) / 2)
    gameinitwindow.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    gameinitwindow.resizable(False, False)
    for index, item in enumerate(configs):
        button = tk.Button()
        button.configure(text=item['name'], width=30)
        button.configure(command=lambda index1=index: pick(index1))
        label = tk.Label()
        label.configure(text=item['tkinterconfig']['description'], justify=tk.LEFT)
        label.grid(row=index, column=1)
        button.grid(row=index, column=0)

    gameinitwindow.mainloop()
    print(chosen_gamemode)
    game = TkinterBattleship(**configs[chosen_gamemode])
