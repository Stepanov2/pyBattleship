"""User is fully responsible for breaking the game by changing this file =)"""
configs = []
configs.append({
        'name': 'express',
        'grid_size': 5,
        'ships': (0, 0, 2, 3),
        'tkinterconfig': {
            'pad_x': 40,
            'pad_y': 30,
            'description': "A very quick game on a 4x4 field with 5 ships per player"
        }
    })
configs.append({
        'name': 'quick',
        'grid_size': 6,
        'ships': (0, 1, 2, 4),
        'tkinterconfig': {
            'pad_x': 32,
            'pad_y': 24,
            'description': "A quick game on a 6x6 field with 7 ships per player"
        }
    })
configs.append({
        'name': 'standard',
        'grid_size': 10,
        'ships': (1, 2, 3, 4),
        'tkinterconfig': {
            'pad_x': 18,
            'pad_y': 11,
            'description': "Garden variety battleship on a 10x10 field with 10 ships per player"
        }
    })
configs.append({
        'name': 'epic',
        'grid_size': 13,
        'ships': (2, 3, 5, 7),
        'tkinterconfig': {
            'pad_x': 11,
            'pad_y': 5,
            'description': "An epic game on a 13x13 field with 17 ships per player. Bring hot cocoa!"
        }
    })
