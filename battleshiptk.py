import battleshipgame
from config import *
from time import sleep, time_ns
import tkinter as tk
from tkinter import ttk
from random import choice

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
        self.setup_player._playfield.print_grid()

        self.hovered_ship=battleshipgame.Ship(1)
        pad_x = kwargs['tkinterconfig']['pad_x']
        pad_y = kwargs['tkinterconfig']['pad_y']
        # ==== begin tkinter main window
        self.root = tk.Tk()
        self.root.title('Quick and dirty Battleship for python')

        window_width = 1000
        window_height = 500

        center_x = int((self.root.winfo_screenwidth() - window_width) / 2)
        center_y = int((self.root.winfo_screenheight() - window_height) / 2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.root.resizable(False, False)

        # message = tk.Label(root, text="Hello, World!", foreground="#FF0000", background="#00FF00")
        # message.pack()
        # buttons = [tk.Button(root, text='F') for _ in range(10)]
        # for button in buttons:
        # button.pack()
        self.testbutton = tk.Button(self.root)
        self.testbutton.config(bg="#fffffa")
        self.testbutton.config(padx=25, pady=25)

        # testbutton.bound_index(2,4)
        # print(testbutton.bound_index)
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
            ttk.Label(self.root, text='1').grid(row=i + 1, column=0)
            for j in range(0, grid_size):
                self.enemy_buttons[i].append(tk.Button(self.root,
                                                  text=' ',
                                                  command=lambda i1=i, j1=j: self.enemy_clicked(i1, j1)))
                # enemy_buttons[i][j].bound_index(i,j)
                # enemy_buttons[i][j]['command'] = f'lambda: enemy_clicked({i},{j})'
                self.enemy_buttons[i][j].bind("<Enter>", lambda e, i1=i, j1=j: self.enemy_hover(e, index=(i1, j1)))
                self.enemy_buttons[i][j].config(padx=pad_x, pady=pad_y)
                self.enemy_buttons[i][j].grid(row=i + 1, column=j + 1)
                print(j + 1)
            ttk.Label(self.root, text='2').grid(row=i + 1, column=grid_size + 1)
            print(grid_size + 1)
            for j in range(0, grid_size):
                self.own_buttons[i].append(tk.Button(self.root,
                                                text=' ',
                                                command=lambda i1=i, j1=j: self.own_clicked(i1, j1)))
                self.own_buttons[i][j].bind("<Enter>", lambda e, i1=i, j1=j: self.own_hover(e, index=(i1, j1)))
                self.own_buttons[i][j].config(padx=pad_x, pady=pad_y)
                self.own_buttons[i][j].grid(row=i + 1, column=grid_size + j + 2)
                print(grid_size + j + 2)

            ttk.Label(self.root, text='3').grid(row=i + 1, column=(grid_size + 1) * 2)
            print((grid_size + 1) * 2)

        btm_label = ttk.Label(self.root, text="Place your ships to begin the madness!", anchor=tk.CENTER,
                              background="#fefefe")
        btm_label.grid(column=0, row=grid_size + 1, columnspan=num_columns, sticky=tk.S)
        print(f"Initialized in {(time_ns() - start_time) / 1000 ** 2} ms")

        self.human_player.place_ships_randomly()  # only for debug, hopefully
        self.root.mainloop()



    def enemy_clicked(self, *args, **kwargs):

        if self.enemy_buttons[args[0]][args[1]]['state'] != 'disabled':
            print(*args, 'Enemy playfield!')
            self.enemy_buttons[args[0]][args[1]].configure(state="disabled", relief="sunken")

    def own_clicked(self, *args, **kwargs):
        print(*args, 'Friend playfield!')
        #testbutton.config()

    def enemy_hover(self,*args, **kwargs):
        print(args, kwargs)
        index = kwargs['index']
        possiblecolors = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F')
        chosencolor = "#"
        for _ in range(6):
            chosencolor += choice(possiblecolors)
        print(args)
        print(kwargs)
        self.enemy_buttons[index[0]][index[1]].configure(text='F')


    def own_hover(self, *args, **kwargs):
        print(args, kwargs)
        index = kwargs['index']
        possiblecolors = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F')
        chosencolor = "#"
        for _ in range(6):
            chosencolor += choice(possiblecolors)
        print(args)
        print(kwargs)
        self.own_buttons[index[0]][index[1]].configure(bg=chosencolor)






if __name__ == '__main__':
    game = TkinterBattleship(**configs[3])
