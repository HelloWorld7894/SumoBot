import numpy as np

"""
    Map setup on import
"""

Map = np.zeros((7, 7), dtype=np.uint8)
Map[0, :] = 1
Map[6, :] = 1
Map[:, 0] = 1
Map[:, 6] = 1

Map[2][3] = 3
Map[4][3] = 2

"""
    TODO: rework whole algorithm! add mapping!
"""