
import unittest
import battleshipgame

class TestDotSetter(unittest.TestCase):

    def test_dot_proper(self):

        proper_phrases = ('empty', 'hit', 'occupied', 'sunk', 'checked',
                          'EMPTY', 'HIT', 'OCCUPIED', 'SUNK', 'CHECKED',
                          'eMpTy', 'hIt', 'OCCUpied', 'SuNk', 'cHeCkeD')

        for value in proper_phrases:
            testdot = battleshipgame.Dot(value)
            self.assertEqual(testdot.state, value.lower(), msg='Completly broken')
            testdot.state = value
            self.assertEqual(testdot.state, value.lower(), msg='Completly broken')


    def test_dot_silly_phrases(self):
        silly_phrases = ('doo', 'dad', 'go_fish', '', '\n', '')
        dot = battleshipgame.Dot('empty')
        for value in silly_phrases:

            with self.assertRaises(ValueError):
                dot.state = value

    def test_dot_silly_types(self):
        silly_types = (4, 3.14, (2, 5), [2, 3], set((1, 1, 2)), range(3), None)
        dot = battleshipgame.Dot('empty')
        for value in silly_types:
            with self.assertRaises(TypeError):
                dot.state = value

class TestShip(unittest.TestCase):
    def test_normal_creation(self):
        valid_sizes = (1,2,3,4)
        for value in valid_sizes:
            ship = battleshipgame.Ship(value)
            self.assertEqual(ship.hp, value)
            self.assertEqual(ship.size, value)
        pass
    def test_broken_creation(self):
        invalid_sizes = (0,5)
        silly_types = ('2', '', ' ', 3.14, (2, 5), [2, 3], set((1, 1, 2)), range(3), None)
        for value in silly_types:
            with self.assertRaises(TypeError):
                _ = battleshipgame.Ship(value)
        for value in invalid_sizes:
            with self.assertRaises(battleshipgame.GameLogicError):
                _ = battleshipgame.Ship(value)
    def test_return_area(self):
        ship = battleshipgame.Ship(3)
        ship._row = 2
        ship._column = 2
        ship._vertical = False
        print(*ship.return_area())
        self.assertEqual(tuple(ship.return_area()), ((2, 2), (2, 3), (2, 4)))

        ship._vertical = True
        self.assertEqual(tuple(ship.return_area()), ((2, 2), (3, 2), (4, 2)))
        print(*ship.return_area())

class TestPlayfield(unittest.TestCase):
    def test_normal_creation(self):
        for i in range(3,20):
            test = battleshipgame.Playfield(i)
            self.assertEqual(test._grid[0][0].state, 'empty')
            self.assertEqual(test._grid[i-1][i-1].state, 'empty')
            with self.assertRaises(IndexError):
                _= test._grid[i - 1][i]
                _= test._grid[i][i - 1]

    def test_broken_creation(self):
        pass #todo

    def test_return_surroundings(self): #todo this test is still fucking broken it seems
        test = battleshipgame.Playfield(5)
        for size in range(1,5):
            # This doesn't test every possible case, but I fell this should be sufficient
            # Not sure what will happen if 3 long ship gets placed on 3 by 3 playfield
            testship = battleshipgame.Ship(size)
            for row in range(0, 6):
                for column in range(0, 7 - size):
                    testship._row = row
                    testship._column = column
                    testship._vertical = False
                    playfieldedges = (0, 5)
                    maxoffsetedges = (0, 6 - size)



                    #                area surrounding horizontal ship =
                    #                           8 for smallest ship
                    #                           + 2 for each additional tile of the ship
                    #                           - (shipsize + 2) if ship is in the first or last row
                    #                           - 3 if ship is in the first column, or ends in column
                    #                           + 1 if both above conditions are met (i.e. ends or starts in corner)
                    #                                 exact same logic for vertical ships, but flip rows anc columns


                    numberofneighbours = 8 + \
                                         (size-1) * 2 - \
                                         (row in playfieldedges) * (size + 2) - \
                                         (column in maxoffsetedges) * 3 + \
                                         ((row in playfieldedges) and (column in maxoffsetedges))
                    testshipsurroundings = test._calculate_ship_surroundings(testship)
                    self.assertEqual(len(testshipsurroundings), numberofneighbours, msg=f'unflipped{row,column,size}\n')

                    # swapping rows and collumns for vertical ships
                    testship._row, testship._column = testship._column, testship._row
                    testship._vertical = True

                    testshipsurroundings = test._calculate_ship_surroundings(testship)
                    self.assertEqual(len(testshipsurroundings), numberofneighbours, msg=f'flipped{column,row,size}\n')


                    print(row, column, size, len(testshipsurroundings), '\n', testship.return_area(), '\n',
                         list(sorted(testshipsurroundings)))



"""
class TestPointSetter(unittest.TestCase):

    def test_wins(self):

        for globals.grid_size in range(3, 11):
            zeroed_matrix = np.zeros((globals.grid_size, globals.grid_size), dtype=np.int8)
            h_in_matrix = zeroed_matrix.copy()
            v_in_matrix = zeroed_matrix.copy()
            d1_in_matrix = zeroed_matrix.copy()
            d2_in_matrix = zeroed_matrix.copy()

            for globals.in_line in range(3, globals.grid_size + 1):
                print(f'{globals.grid_size =} {globals.in_line =}')
                # testing lines
                for offset_y in range(globals.grid_size):
                    for offset_x in range(globals.grid_size - globals.in_line + 1):
                        h_in_matrix = zeroed_matrix.copy()
                        v_in_matrix = zeroed_matrix.copy()
                        for i in range(globals.in_line):
                            h_in_matrix[offset_y, offset_x + i] = 1
                            v_in_matrix[offset_x + i, offset_y] = 1
                        print(h_in_matrix)
                        print(v_in_matrix)
                        globals.playfield = h_in_matrix.copy()
                        self.assertEqual(check_win_condition(), 1,
                                         msg=f'{globals.grid_size = }, {globals.in_line = }\n{globals.playfield}')
                        globals.playfield = np.negative(globals.playfield)
                        self.assertEqual(check_win_condition(), -1,
                                         msg=f'{globals.grid_size = }, {globals.in_line = }\n{globals.playfield}')
                        globals.playfield = v_in_matrix.copy()
                        self.assertEqual(check_win_condition(), 1,
                                         msg=f'{globals.grid_size = }, {globals.in_line = }\n{globals.playfield}')
                        globals.playfield = np.negative(globals.playfield)
                        self.assertEqual(check_win_condition(), -1,
                                         msg=f'{globals.grid_size = }, {globals.in_line = }\n{globals.playfield}')
                # testing diagonals
                max_offset = globals.grid_size - globals.in_line + 1

                for offset_y in range(max_offset):
                    for offset_x in range(max_offset):
                        d1_in_matrix = zeroed_matrix.copy()
                        d2_in_matrix = zeroed_matrix.copy()
                        for i in range(globals.in_line):
                            d1_in_matrix[offset_y + i, offset_x + i] = 1
                            d2_in_matrix[globals.grid_size - 1 - offset_y - i, offset_x + i] = 1
                        print(d1_in_matrix)
                        print(d2_in_matrix)
                        globals.playfield = d1_in_matrix.copy()
                        self.assertEqual(check_win_condition(), 1,
                                         msg=f'{globals.grid_size = }, {globals.in_line = }\n{globals.playfield}')
                        globals.playfield = np.negative(globals.playfield)
                        self.assertEqual(check_win_condition(), -1,
                                         msg=f'{globals.grid_size = }, {globals.in_line = }\n{globals.playfield}')
                        globals.playfield = d2_in_matrix.copy()
                        self.assertEqual(check_win_condition(), 1,
                                         msg=f'{globals.grid_size = }, {globals.in_line = }\n{globals.playfield}')
                        globals.playfield = np.negative(globals.playfield)
                        self.assertEqual(check_win_condition(), -1,
                                         msg=f'{globals.grid_size = }, {globals.in_line = }\n{globals.playfield}')
"""


