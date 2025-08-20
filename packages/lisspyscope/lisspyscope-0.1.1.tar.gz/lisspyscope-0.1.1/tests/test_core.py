import numpy as np
import lisspyscope as ls
import pytest


def test_generate_shape_and_dtype():
    buf, sr = ls.generate_lissajous(base_freq=500, l_fact=1, r_fact=3, phase_deg=45)
    assert buf.ndim == 2 and buf.shape[1] == 2            # stereo
    assert buf.dtype == np.float32
    assert sr == 48_000


def test_amplitude_never_clips():
    buf, _ = ls.generate_lissajous(base_freq=700, l_fact=1, r_fact=2, phase_deg=0)
    assert np.max(np.abs(buf)) <= 1.0 + 1e-6


def test_invalid_ratio_raises():
    with pytest.raises(ValueError):
        ls.generate_lissajous(base_freq=440, l_fact=0)     # must be ≥1
