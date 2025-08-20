# -*- coding: utf-8 -*-

import time
from key_stroke import KeyStroke

k = KeyStroke()
print('Press ESC to terminate!')

while True:

    # do your stuff here, for this example we use a sleep and a print instead.
    time.sleep(0.5)
    print('.', end = '', flush = True)

    # check whether a key from the list has been pressed
    if k.check(['\x1b', 'q', 'x']):
        break

print('\nfinito!')
