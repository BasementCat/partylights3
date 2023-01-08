from lib.lights import DMXLightType, DMXLightTypeFunction, DMXLight
from lib.data import Transition, Effect, Program, Scene, CircleMovementTransition


DMXLightType('UnnamedGobo', 11, [
    DMXLightTypeFunction('pan', None, map_highres=('pan_coarse', 'pan_fine'), range_deg=540),
    DMXLightTypeFunction('pan_coarse', 1),
    DMXLightTypeFunction('pan_fine', 2),
    DMXLightTypeFunction('tilt', None, map_highres=('tilt_coarse', 'tilt_fine'), range_deg=220),
    DMXLightTypeFunction('tilt_coarse', 3),
    DMXLightTypeFunction('tilt_fine', 4),
    DMXLightTypeFunction('color', 5, mapping={
        'white': [0, 9],
        'yellow': [10, 19],
        'orange': [20, 29],
        'cyan': [30, 39],
        'blue': [40, 49],
        'green': [50, 59],
        'pink': [60, 69],
        'red': [70, 79],
        'pink_red': [80, 89],
        'green_pink': [90, 99],
        'blue_green': [100, 109],
        'cyan_blue': [110, 119],
        'orange_cyan': [120, 129],
        'yellow_orange': [130, 139],
    }),
    DMXLightTypeFunction('gobo', 6, mapping={
        'none': [0, 7],
        'broken_circle': [8, 15],
        'burst': [16, 23],
        '3_spot_circle': [24, 31],
        'square_spots': [32, 39],
        'droplets': [40, 47],
        'swirl': [48, 55],
        'stripes': [56, 63],
        'dither_none': [64, 71],
        'dither_broken_circle': [72, 79],
        'dither_burst': [80, 87],
        'dither_3_spot_circle': [88, 95],
        'dither_square_spots': [96, 103],
        'dither_droplets': [104, 111],
        'dither_swirl': [112, 119],
        'dither_stripes': [120, 127],
    }),
    DMXLightTypeFunction('strobe', 7, invert=True),
    DMXLightTypeFunction('dim', 8),
    DMXLightTypeFunction('speed', 9, invert=True),
    DMXLightTypeFunction('mode', 10, mapping={
        'manual': [0, 59],
        'auto0': [135, 159],
        'auto1': [110, 134],
        'auto2': [85, 109],
        'auto3': [60, 84],
        'sound0': [235, 255],
        'sound1': [210, 234],
        'sound2': [185, 209],
        'sound3': [160, 184],
    }),
    DMXLightTypeFunction('reset', 11, reset=(1, 255)),
])

DMXLightType('UKingGobo', 11, [
    DMXLightTypeFunction('pan', None, map_highres=('pan_coarse', 'pan_fine'), range_deg=540),
    DMXLightTypeFunction('pan_coarse', 1),
    DMXLightTypeFunction('pan_fine', 2),
    DMXLightTypeFunction('tilt', None, map_highres=('tilt_coarse', 'tilt_fine'), range_deg=220),
    DMXLightTypeFunction('tilt_coarse', 3),
    DMXLightTypeFunction('tilt_fine', 4),
    DMXLightTypeFunction('color', 5, mapping={
        'white': [0, 9],
        'red': [10, 19],
        'green': [20, 29],
        'blue': [30, 39],
        'yellow': [40, 49],
        'orange': [50, 59],
        'cyan': [60, 69],
        'pink': [70, 79],
        'pink_cyan': [80, 89],
        'cyan_orange': [90, 99],
        'orange_yellow': [100, 109],
        'yellow_blue': [110, 119],
        'blue_green': [120, 127],
    }),
    DMXLightTypeFunction('gobo', 6, mapping={
        'none': [0, 7],
        'broken_circle': [8, 15],
        'burst': [16, 23],
        '3_spot_circle': [24, 31],
        'square_spots': [32, 39],
        'droplets': [40, 47],
        'swirl': [48, 55],
        'stripes': [56, 63],
        'dither_none': [64, 71],
        'dither_broken_circle': [72, 79],
        'dither_burst': [80, 87],
        'dither_3_spot_circle': [88, 95],
        'dither_square_spots': [96, 103],
        'dither_droplets': [104, 111],
        'dither_swirl': [112, 119],
        'dither_stripes': [120, 127],
    }),
    DMXLightTypeFunction('strobe', 7, invert=True),
    DMXLightTypeFunction('dim', 8),
    DMXLightTypeFunction('speed', 9, invert=True),
    DMXLightTypeFunction('mode', 10),
    DMXLightTypeFunction('dim_mode', 11, reset=(101, 255), mapping={
        'standard': [0, 20],
        'stage': [21, 40],
        'tv': [41, 60],
        'building': [61, 80],
        'theater': [81, 100],
        'reset': [101, 255],
    }),
])

DMXLightType('TomshineMovingHead6in1', 18, [
    DMXLightTypeFunction('pan', None, map_highres=('pan_coarse', 'pan_fine'), range_deg=540),
    DMXLightTypeFunction('pan_coarse', 1),
    DMXLightTypeFunction('pan_fine', 2),
    DMXLightTypeFunction('tilt', None, map_highres=('tilt_coarse', 'tilt_fine'), range_deg=220),
    DMXLightTypeFunction('tilt_coarse', 3),
    DMXLightTypeFunction('tilt_fine', 4),
    DMXLightTypeFunction('speed', 5, invert=True),
    DMXLightTypeFunction('dim', 6),
    DMXLightTypeFunction('strobe', 7),
    DMXLightTypeFunction('rgb', None, map_multi=('red', 'green', 'blue')),
    DMXLightTypeFunction('red', 8),
    DMXLightTypeFunction('green', 9),
    DMXLightTypeFunction('blue', 10),
    DMXLightTypeFunction('white', 11),
    DMXLightTypeFunction('amber', 12),
    DMXLightTypeFunction('uv', 13),
    DMXLightTypeFunction('mode', 14, mapping={
        'manual': [0, 15],
        'auto0': [105, 128],
        'auto1': [75, 104],
        'auto2': [45, 74],
        'auto3': [16, 44],
        'sound0': [218, 255],
        'sound1': [188, 217],
        'sound2': [158, 187],
        'sound3': [128, 157],
    }),
    DMXLightTypeFunction('motor_sens', 15),
    DMXLightTypeFunction('effect', 16, mapping={
        'manual': [0, 0],
        'gradual': [1, 7],
        'auto1': [8, 39],
        'auto2': [40, 74],
        'auto3': [75, 108],
        'auto4': [109, 140],
        'sound1': [141, 168],
        'sound2': [169, 197],
        'sound3': [198, 226],
        'sound4': [227, 255],
    }),
    DMXLightTypeFunction('led_sens', 17),
    DMXLightTypeFunction('reset', 18, reset=(1, 255)),
])

DMXLightType('Generic4ColorLaser', 7, [
    DMXLightTypeFunction('mode', 1, mapping={
        'off': [0, 49],
        'static': [50, 99],
        'dynamic': [100, 149],
        'sound': [150, 199],
        'auto': [200, 255],
    }),
    DMXLightTypeFunction('pattern', 2, mapping=[
        [
            ['mode', 'static'],
            {
                'circle': [0, 4],
                'dot_circle_1': [5, 9],
                'dot_circle_2': [10, 14],
                'scan_circle': [15, 19],
                'horiz_line': [20, 24],
                'horiz_dot_line': [25, 29],
                'vert_line': [30, 34],
                'vert_dot_line': [35, 39],
                '45deg_diag': [40, 44],
                '45deg_dot_diag': [45, 49],
                '135deg_diag': [50, 54],
                '135deg_dot_diag': [55, 59],
                'v_line_1': [60, 64],
                'v_dot_line_1': [65, 69],
                'v_line_2': [70, 74],
                'v_dot_line_2': [75, 79],
                'triangle_1': [80, 84],
                'dot_triangle_1': [85, 89],
                'triangle_2': [90, 94],
                'dot_triangle_2': [95, 99],
                'square': [100, 104],
                'dot_square': [105, 109],
                'rectangle_1': [110, 114],
                'dot_rectangle_1': [115, 119],
                'rectangle_2': [120, 124],
                'dot_rectangle_2': [125, 129],
                'criscross': [130, 134],
                'chiasma_line': [135, 139],
                'horiz_extend_line': [140, 144],
                'horiz_shrink_line': [145, 149],
                'horiz_flex_line': [150, 154],
                'horiz_flex_dot_line': [155, 159],
                'vert_extend_line': [160, 164],
                'vert_shrink_line': [165, 169],
                'vert_flex_line': [170, 174],
                'vert_flex_dot_line': [175, 179],
                'ladder_line_1': [180, 184],
                'ladder_line_2': [185, 189],
                'ladder_line_3': [190, 194],
                'ladder_line_4': [195, 199],
                'tetragon_1': [200, 204],
                'tetragon_2': [205, 209],
                'pentagon_1': [210, 214],
                'pentagon_2': [215, 219],
                'pentagon_3': [220, 224],
                'pentagon_4': [225, 229],
                'wave_line': [230, 234],
                'wave_dot_line': [235, 239],
                'spiral_line': [240, 244],
                'many_dot_1': [245, 249],
                'many_dot_2': [250, 254],
                'square_dot': [255, 255],
            }
        ],
        [
            ['mode', 'dynamic'],
            {
                'circle_to_big': [0, 4],
                'dot_circle_to_big': [5, 9],
                'scan_circle_to_big': [10, 14],
                'circle_flash': [15, 19],
                'dot_circle_flash': [20, 24],
                'circle_roll': [25, 29],
                'dot_circle_roll': [30, 34],
                'circle_turn': [35, 39],
                'dot_circle_turn': [40, 44],
                'dot_circle_to_add': [45, 49],
                'scan_circle_extend': [50, 54],
                'circle_jump': [55, 59],
                'dot_circle_jump': [60, 64],
                'horiz_line_jump': [65, 69],
                'horiz_dot_line_jump': [70, 74],
                'vert_line_jump': [75, 79],
                'vert_dot_line_jump': [80, 84],
                'diag_jump': [85, 89],
                'dot_diag_jump': [90, 94],
                'short_sector_round_1': [95, 99],
                'short_sector_round_2': [100, 104],
                'long_sector_round_1': [105, 109],
                'long_sector_round_2': [110, 114],
                'line_scan': [115, 119],
                'dot_line_scan': [120, 124],
                '45deg_diag_move': [125, 129],
                'dot_diag_move': [130, 134],
                'horiz_line_flex': [135, 139],
                'horiz_dot_line_flex': [140, 144],
                'horiz_line_move': [145, 149],
                'horiz_dot_line_move': [150, 154],
                'vert_line_move': [155, 159],
                'vert_dot_line_move': [160, 164],
                'rect_extend': [165, 169],
                'dot_rect_extend': [170, 174],
                'square_extend': [175, 179],
                'dot_square_extend': [180, 184],
                'rect_turn': [185, 189],
                'dot_rect_turn': [190, 194],
                'square_turn': [195, 199],
                'dot_square_turn': [200, 204],
                'pentagon_turn': [205, 209],
                'dot_pentagon_turn': [210, 214],
                'tetragon_turn': [215, 219],
                'pentagon_star_turn': [220, 224],
                'bird_fly': [225, 229],
                'dot_bird_fly': [230, 234],
                'wave_flowing': [235, 239],
                'dot_wave_flowing': [240, 244],
                'many_dot_jump_1': [245, 249],
                'square_dot_jump': [250, 254],
                'many_dot_jump_2': [255, 255],
            }
        ]
    ]),
    DMXLightTypeFunction('x', 3),
    DMXLightTypeFunction('y', 4),
    DMXLightTypeFunction('scan_speed', 5, invert=True),
    DMXLightTypeFunction('pattern_speed', 6, invert=True),
    DMXLightTypeFunction('pattern_size', 7),
])

# TODO: that other multi-light
# TODO: 2nd laser
# TODO: uplights
# TODO: hue




DMXLight('back_1', 1, 'UnnamedGobo')
DMXLight('back_2', 12, 'UnnamedGobo')
DMXLight('mid_1', 23, 'UKingGobo')
DMXLight('mid_2', 34, 'UKingGobo')
DMXLight('mid_3', 45, 'UKingGobo')
DMXLight('mid_4', 56, 'UKingGobo')
DMXLight('front_1', 67, 'TomshineMovingHead6in1')
DMXLight('front_2', 85, 'TomshineMovingHead6in1')
DMXLight('laser', 103, 'Generic4ColorLaser')


scene = Scene('testscene', [
    # Program('testprogram', [
    #     Effect('chase', [
    #         Transition('dim', 0.5, start_value=0, end_value=1, delay=0, spread={'delay': 0.25}),
    #         Transition('dim', 0.5, start_value=1, end_value=0, delay=0.5, spread={'delay': 0.25}),
    #     ])
    # ]),
    Program('movement', [
        Effect('move', [
            CircleMovementTransition(180, 180, 20, 2, duration_beat=4, spread={'pan': 50}),
        ])
    ])
])