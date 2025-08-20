# examples/circle.py
"""
Display and play the default Lissajous figure
—a perfect circle (ratio 1 : 1, phase 90°).

Usage
-----
python examples/circle.py
"""

import lisspyscope as ls

# 1. Show the figure (non-blocking).
ls.plot_lissajous()          # uses all default parameters

# 2. Start continuous audio.  Ctrl-C stops playback.
ls.play_lissajous()          # same defaults: 1000 Hz, ratio 1, phase 90°
