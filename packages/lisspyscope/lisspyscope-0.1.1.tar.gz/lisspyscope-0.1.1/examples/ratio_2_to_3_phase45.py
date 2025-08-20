# examples/ratio_2_to_3_phase45.py
"""
Play and plot a 2 : 3 Lissajous figure with a 45 ° phase offset.

• First shows a snapshot in a Matplotlib window (non-blocking).
• Then starts an endless audio loop so you can view it on a real-time
  X-Y oscilloscope.  Press Ctrl-C to stop playback.

Usage
-----
python examples/ratio_2_to_3_phase45.py
"""

import lisspyscope as ls

# 1 . Visual snapshot (returns immediately)
ls.plot_lissajous(base_freq=500, l_fact=3, r_fact=5, phase_deg=105)

# 2 . Continuous tone — Ctrl-C to stop
ls.play_lissajous(base_freq=500, l_fact=3, r_fact=5, phase_deg=105)
