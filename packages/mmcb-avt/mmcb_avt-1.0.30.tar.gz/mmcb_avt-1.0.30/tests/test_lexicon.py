import itertools

import pytest

import lexicon

class TestInstrument:
	assert lexicon.instrument('dmm6500', 'identify') == b'*IDN?\r\n'
