from lib.lights import DMXLightType, DMXLightTypeFunction, DMXLight
from lib.data import Transition, Effect, Program, Scene, SceneController, CircleMovementTransition, SquareMovementTransition, SweepMovementTransition, Trigger
from lib.outputs.dmx import DMXOutput


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

DMXLightType('OPPSK_RGBWPar', 8, [
    DMXLightTypeFunction('dim', 1),
    DMXLightTypeFunction('rgb', None, map_multi=('red', 'green', 'blue')),
    DMXLightTypeFunction('red', 2),
    DMXLightTypeFunction('green', 3),
    DMXLightTypeFunction('blue', 4),
    DMXLightTypeFunction('white', 5),
    DMXLightTypeFunction('strobe_mode', 6, mapping={
        'par_strobe': [0, 99],
        'par': [100, 199],
        'strobe': [200, 255],
    }),
    # DMXLightTypeFunction('strobe', 7, invert=True),
    # TODO: should be inverted, but 0-9 or something is off, then fast->slow
    DMXLightTypeFunction('strobe', 7, invert=False),
    DMXLightTypeFunction('mode', 8, mapping={
        'manual': [0, 50],
        'jump': [51, 100],
        'gradual': [101, 150],
        'pulse': [151, 200],
        'auto': [201, 250],
        'sound': [251, 255],
    }),
])

DMXLightType('GenericRGBLaser', 10, [
    DMXLightTypeFunction('mode', 1, mapping={
        'off': [0, 63],
        'manual': [64, 127],
        'auto': [128, 191],
        'sound': [192, 255],
    }),
    DMXLightTypeFunction('pattern', 2),
    DMXLightTypeFunction('angle', 3),
    DMXLightTypeFunction('hz_angle', 4),
    DMXLightTypeFunction('vt_angle', 5),
    DMXLightTypeFunction('hz_pos', 6),
    DMXLightTypeFunction('vt_pos', 7),
    DMXLightTypeFunction('pattern_size', 8),
    DMXLightTypeFunction('color', 9),
    DMXLightTypeFunction('node', 10),
    # pattern: 51 patterns (5 values per) in manual mode, otherwise auto 1-4 & sound 1-4 modes)
    # angle: 0-127 rotation angle, 128-191 slow-fast positive rotation, 192-255 slow-fast negative rotation
    # hz_angle: 0-127 horizontal flip position, 128-255 slow-fast flip speed
    # vt_angle: 0-127 vertical flip position, 128-255 slow-fast flip speed
    # hz_pos: 0-127 horizontal position, 128-255 slow-fast horizontal movement speed
    # vt_pos: 0-127 vertical position, 128-255 slow-fast vertical movement speed
    # pattern_size: 0-63 large-small size, 64-127 slow-fast small->large size, 128-191 slow-fast large->small size, 192-255 slow-fast zoom
    # color: 0-63 monochrome color sel, 64-127 color sel, 128-191 monochrome auto, 192-255 color mixing
    # node: 0-127 dots and lines, 128-255 dotted pattern, wireless strip?
])


# TODO: that other multi-light
# TODO: hue




DMXLight('back_1', 1, 'UnnamedGobo', groups=['back', 'gobo', 'moving', 'odd'])
DMXLight('back_2', 12, 'UnnamedGobo', groups=['back', 'gobo', 'moving', 'even'])
DMXLight('mid_1', 23, 'UKingGobo', groups=['mid', 'gobo', 'moving', 'odd'])
DMXLight('mid_2', 34, 'UKingGobo', groups=['mid', 'gobo', 'moving', 'even'])
DMXLight('mid_3', 45, 'UKingGobo', groups=['mid', 'gobo', 'moving', 'odd'])
DMXLight('mid_4', 56, 'UKingGobo', groups=['mid', 'gobo', 'moving', 'even'])
DMXLight('front_1', 67, 'TomshineMovingHead6in1', groups=['front', 'rgb', 'white', 'uv', 'moving', 'odd'])
DMXLight('front_2', 85, 'TomshineMovingHead6in1', groups=['front', 'rgb', 'white', 'uv', 'moving', 'even'])
DMXLight('laser', 103, 'Generic4ColorLaser', groups=['laser'])
DMXLight('corner_par_1', 110, 'OPPSK_RGBWPar', groups=['par', 'rgb', 'white', 'odd'])
DMXLight('corner_par_2', 118, 'OPPSK_RGBWPar', groups=['par', 'rgb', 'white', 'even'])
DMXLight('corner_par_3', 126, 'OPPSK_RGBWPar', groups=['par', 'rgb', 'white', 'odd'])
DMXLight('corner_par_4', 134, 'OPPSK_RGBWPar', groups=['par', 'rgb', 'white', 'even'])
DMXLight('laser2', 142, 'GenericRGBLaser', groups=['laser'])


controller = SceneController([
    Scene('main', [
        Program('base', [
            Effect('base', [
                Transition('speed', 30, start_value=1, end_value=1),
                Transition('dim', 30, start_value=1, end_value=1),
            ]),
        ], multiple=True, multiple_all=True),
        Program('base_gobo', [
            Effect('base', [
                Transition('gobo', 30, start_value='RANDOM', end_value='START'),
                Transition('color', 30, start_value='RANDOM', end_value='START'),
            ]),
        ], multiple=True, multiple_all=True, groups=['gobo']),
        Program('base_par', [
            Effect('base', [
                Transition('strobe_mode', 30, start_value='par_strobe', end_value='START'),
                # Transition('strobe', 30, start_value=0, end_value='START'),
                Transition('mode', 30, start_value='manual', end_value='START'),
            ]),
        ]),

        Program('base_laser', [
            Effect('base_laser_1', [
                Transition('mode', 0.0000001, start_value=None, end_value='static'),
            ], lights=['laser']),
            Effect('base_laser_2', [
                Transition('mode', 0.0000001, start_value=None, end_value='manual'),
            ], lights=['laser2']),
        ], groups=['laser'], multiple=True, multiple_all=True),

        Program('back_move', [
            Effect('sweep_v', [
                SweepMovementTransition(300, 110, 360, 10, 2, duration_beat=4, groups=['odd']),
                SweepMovementTransition(370, 110, 300, 10, 2, duration_beat=4, groups=['even']),
            ]),
            # TODO: these are not at a good angle for this
            # Effect('sweep_x', [
            #     # TODO: will need adjustment
            #     SweepMovementTransition(300, 110, 360, 10, 2, duration_beat=4, groups=['odd']),
            #     SweepMovementTransition(370, 110, 300, 10, 2, duration_beat=4, groups=['even']),
            # ]),
            Effect('circles', [
                CircleMovementTransition(350, 55, 25, 2, duration_beat=4, spread={'pan': -50}),
            ]),
            Effect('squares', [
                SquareMovementTransition(350, 55, 25, 2, duration_beat=4, spread={'pan': -50}),
            ]),
        ], groups=['back'], autoplay=False, trigger_random=[Trigger('audio/beat/onbeat', 0.9, cooldown=4, cooldown_beat=8)]),
        Program('mid_move', [
            Effect('split_fb_circles', [
                CircleMovementTransition(200, 190, 35, 2, duration_beat=4, spread={'pan': -30}, groups=['odd']),
                CircleMovementTransition(220, 65, 35, 2, duration_beat=4, spread={'pan': -30, 'tilt': -15}, groups=['even']),
            ]),
            Effect('split_fb_squares', [
                SquareMovementTransition(200, 190, 60, 2, duration_beat=4, spread={'pan': -30}, groups=['odd']),
                SquareMovementTransition(220, 65, 60, 2, duration_beat=4, spread={'pan': -30, 'tilt': -15}, groups=['even']),
            ]),
            Effect('front_circles', [
                CircleMovementTransition(130, 190, 25, 2, duration_beat=4, spread={'pan': 30}),
            ]),
            Effect('floor_circles', [
                CircleMovementTransition(200, 45, 45, 2, duration_beat=4, spread={'pan': -30}),
            ]),
            Effect('front_squares', [
                SquareMovementTransition(130, 190, 35, 2, duration_beat=4, spread={'pan': 30}),
            ]),
            Effect('floor_squares', [
                SquareMovementTransition(200, 45, 45, 2, duration_beat=4, spread={'pan': -30}),
            ]),
            Effect('split_lr_circles', [
                CircleMovementTransition(50, 25, 20, 2, duration_beat=4, spread={'pan': 15}, groups=['odd']),
                CircleMovementTransition(300, 25, 20, 2, duration_beat=4, spread={'pan': -15}, groups=['even']),
            ]),
            Effect('split_lr_squares', [
                SquareMovementTransition(50, 25, 25, 2, duration_beat=4, spread={'pan': 15}, groups=['odd']),
                SquareMovementTransition(300, 25, 25, 2, duration_beat=4, spread={'pan': -15}, groups=['even']),
            ]),
            # Not quite ready for this yet, it's complex
            # Effect('front_sweep', [
            #     Transition('dim', 0.125, start_value=0, end_value=1, duration_beat=0.25, delay=0, delay_beat=0, spread={'delay': 0.5, 'delay_beat': 1}),
            #     SweepMovementTransition(110, 200, 210, None, 2, duration_beat=4, delay=0, delay_beat=0, spread={'delay': 0.5, 'delay_beat': 1}),
            #     Transition('dim', 0.125, start_value=1, end_value=0, duration_beat=0.25, delay=2 - 0.125, delay_beat=3.75, spread={'delay': 0.5, 'delay_beat': 1}),
            #     # Transition('pan', 0.000000001, start_value='CURRENT', end_value=110, delay=2, delay_beat=4, spread={'delay': 0.5, 'delay_beat': 1}),
            # ]),
            Effect('con_circles', [
                CircleMovementTransition(360, 110, 15, 2, duration_beat=4, spread={'radius': 30}),
            ]),
            Effect('full_double_x', [
                SweepMovementTransition(380, 20, None, 180, 2, duration_beat=4, groups=['odd']),
                SweepMovementTransition(110, 20, None, 180, 2, duration_beat=4, groups=['even']),
            ]),
            Effect('back_double_x', [
                SweepMovementTransition(100, 20, 190, 60, 2, duration_beat=4, groups=['odd']),
                SweepMovementTransition(190, 20, 100, 60, 2, duration_beat=4, groups=['even']),
            ]),
            Effect('front_double_x', [
                SweepMovementTransition(300, 10, 390, 60, 2, duration_beat=4, groups=['odd']),
                SweepMovementTransition(390, 10, 300, 60, 2, duration_beat=4, groups=['even']),
            ]),
            Effect('opposite_sweep', [
                SweepMovementTransition(425, 50, 270, None, 2, duration_beat=4, spread={'tilt': 100}, groups=['odd']),
                SweepMovementTransition(270, 20, 425, None, 2, duration_beat=4, spread={'tilt': 25}, groups=['even']),
            ]),
            # TODO: front wall bounce
        ], groups=['mid'], autoplay=False, trigger_random=[Trigger('audio/beat/onbeat', 0.9, cooldown=4, cooldown_beat=8)]),
        Program('gobo', [
            Effect('gobo', [
                Transition('gobo', 0.0000000001, start_value=None, end_value='CYCLE'),
            ], trigger_run=[Trigger('audio/hits/bass', 0.9, cooldown=1, cooldown_beat=2)]),
            Effect('color', [
                Transition('color', 0.0000000001, start_value=None, end_value='CYCLE'),
            ], trigger_run=[Trigger('audio/hits/bass', 0.9, cooldown=0.25, cooldown_beat=0.5)]),
        ], groups=['gobo'], multiple=True),
        Program('front_move', [
            Effect('up_circle', [
                CircleMovementTransition(180, 80, 30, 2, duration_beat=4),
            ]),
            Effect('sweep_up_lr', [
                SweepMovementTransition(270, 200, None, 0, 2, duration_beat=4),
            ]),
            Effect('sweep_up_lr_inv', [
                SweepMovementTransition(270, 200, None, 0, 2, duration_beat=4, groups=['odd']),
                SweepMovementTransition(270, 0, None, 200, 2, duration_beat=4, groups=['even']),
            ]),
            Effect('sweep_up_fb', [
                SweepMovementTransition(180, 200, None, 0, 2, duration_beat=4),
            ]),
            Effect('sweep_room_slow', [
                SweepMovementTransition(250, 0, 100, None, 8, duration_beat=16, groups=['odd']),
                SweepMovementTransition(100, 0, 250, None, 8, duration_beat=16, groups=['even']),
            ]),
            Effect('sweep_ceil_slow', [
                SweepMovementTransition(250, 60, 100, None, 8, duration_beat=16, groups=['odd']),
                SweepMovementTransition(100, 60, 250, None, 8, duration_beat=16, groups=['even']),
            ]),
        ], groups=['front'], autoplay=False, trigger_random=[Trigger('audio/beat/onbeat', 0.9, cooldown=4, cooldown_beat=8)]),
        Program('front_color', [
            Effect('base_dim', [
                Transition('dim', 0.00000001, start_value=None, end_value=0.7),
            ], trigger_run=[True]),
            Effect('pulse', [
                Transition('dim', 0.125, start_value=1, end_value=0.7),
            ], trigger_run=[Trigger('audio/hits/bass', 0.9)]),
            # TODO: this can't work now - mappings overwrite raw channels, reversing that breaks mappings, so need to determine what's explicitly set
            # Effect('rgb_bands', [
            #     Transition('red', 0.25, start_value=None, end_value='@audio/hits/bass', duration_beat=1),
            #     Transition('blue', 0.25, start_value=None, end_value='@audio/hits/mid', duration_beat=1),
            #     Transition('green', 0.25, start_value=None, end_value='@audio/hits/midhigh', duration_beat=1),
            #     Transition('white', 0.25, start_value=None, end_value='@audio/hits/high', duration_beat=1),
            # ], trigger_run=[True]),
            Effect('color', [
                Transition('rgb', 0.125, start_value=None, end_value='RANDOMRGB', duration_beat=1, keep=['end_value']),
            ], trigger_run=[Trigger('audio/hits/bass', 0.9)]),
        ], groups=['front'], multiple=True),
        Program('laser_effect', [
            Effect('pattern', [
                Transition('pattern', 0.0000001, start_value=None, end_value='RANDOM'),
                Transition('dummy', 4, start_value=0, end_value=1, duration_beat=8),
            ], trigger_run=[Trigger('audio/hits/bass', 0.9)]),
            Effect('size', [
                Transition('pattern_size', 0.125, start_value=1, end_value=0.5),
                # TODO: scale w/ volume (overall scale + diff somehow)
            ], trigger_run=[Trigger('audio/hits/bass', 0.9)]),
        ], groups=['laser'], multiple=True),

        Program('laser1_mode', [
            Effect('dynamic_mode', [
                Transition('mode', 0.00000001, start_value=None, end_value='dynamic'),
            ], trigger_run=[Trigger('audio/energy/intensity', 0.5)]),
        ], lights=['laser'], multiple=True),
        Program('laser2_mode', [
            Effect('color_node', [
                Transition('color', 0.0000001, start_value='RANDOM', end_value='START'),
                Transition('node', 0.0000001, start_value='RANDOM', end_value='START'),
            ], trigger_run=[Trigger('audio/hits/bass', 0.9)]),
        ], lights=['laser2'], multiple=True),

        # TODO: other multi light
        Program('uplights', [
            Effect('random_chase_fast', [
                Transition('rgb', 0.25, start_value=None, end_value='RANDOMRGB', delay=0, keep=['end_value']),
                Transition('dummy', 0.5, start_value=0, end_value=1, duration_beat=1),
            ]),
            Effect('random_pulse', [
                Transition('rgb', 0.25, start_value=None, end_value='RANDOMRGB', keep=['end_value']),
                Transition('dim', 0.125, start_value=1, end_value=0.8),
                Transition('dummy', 0.5, start_value=0, end_value=1, duration_beat=1),
            ]),
        ], groups=['par'], autoplay=False, trigger_random=[Trigger('audio/beat/onbeat', 0.9, cooldown=4, cooldown_beat=8)]),
        # # TODO: no audio: rgb&uv=dim 1, rgb 0, uv 1;rgb=dim 0.2,color=?;other=dim 0.2
        Program('autodim', [
            Effect('autodim', [
                Transition('dim', 0.125, start_value=None, end_value=0),
            ], trigger_run=[Trigger('audio/level/all', 0.05, below_threshold=True)]),
            Effect('autodim_laser', [
                Transition('mode', 0.125, start_value=None, end_value='off'),
            ], trigger_run=[Trigger('audio/level/all', 0.05, below_threshold=True)]),
        ], multiple=True),
    ])
])


output = DMXOutput('dmx')