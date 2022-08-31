"""Configs for the game.
User is fully responsible for breaking the game by changing this file =)
At least there is a half-baked check, that shouldn't allow to get too many ships"""

configs = []

configs.append({
        'name': 'express',
        'grid_size': 5,
        'ships': (0, 0, 2, 3),
        'tkinterconfig': {
            'btn_width': 11,
            'btn_height': 5,
            'description': "A very quick game on a 4x4 field with 5 ships per player"
        }
    })

configs.append({
        'name': 'quick',
        'grid_size': 6,
        'ships': (0, 1, 2, 4),
        'tkinterconfig': {
            'btn_width': 9,
            'btn_height': 4,
            'description': "A quick game on a 6x6 field with 7 ships per player"
        }
    })

configs.append({
        'name': 'standard',
        'grid_size': 10,
        'ships': (1, 2, 3, 4),
        'tkinterconfig': {
            'btn_width': 5,
            'btn_height': 2,
            'description': "Garden variety battleship on a 10x10 field with 10 ships per player"
        }
    })

configs.append({
        'name': 'epic',
        'grid_size': 13,
        'ships': (3, 4, 5, 7),
        'tkinterconfig': {
            'btn_width': 4,
            'btn_height': 2,
            'description': "An epic game on a 13x13 field with 19 ships per player. Bring hot cocoa!",
            'win_height' : 540  # Since tkinter doesn't allow for 'btn_height': 1.9 X_X
        }
    })
