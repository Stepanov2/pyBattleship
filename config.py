"""User is fully responsible for any changes to this file"""
configs = []
configs[0] = {
        'name': 'express',
        'grid_size': 4,
        'ships': (0, 0, 2, 3),
        'tkinterconfig': {
            'pad_x': 15,
            'pad_y': 10,
            'description': "A very quick game on a 4x4 field with 5 ships per player"
        }
    }
configs[1] = {
        'name': 'quick',
        'grid_size': 6,
        'ships': (0, 1, 2, 4),
        'tkinterconfig': {
            'pad_x': 15,
            'pad_y': 10,
            'description': "A quick game on a 6x6 field with 7 ships per player"
        }
    }
configs[2] = {
        'name': 'standard',
        'grid_size': 10,
        'ships': (1, 2, 3, 4),
        'tkinterconfig': {
            'pad_x': 15,
            'pad_y': 10,
            'description': "Garden variety battleship on a 10x10 field with 10 ships per player"
        }
    }
configs[3] = {
        'name': 'epic',
        'grid_size': 13,
        'ships': (2, 3, 5, 7),
        'tkinterconfig': {
            'pad_x': 10,
            'pad_y': 8,
            'description': "An epic game on a 13x13 field with 17 ships per player. Bring hot cocoa!"
        }
    }
