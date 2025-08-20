'''pytest functions for making sure the build has expected members (version, etc)'''

import opencos

def test_version():
    '''tests that opencos.__version__ works'''
    __version__ = opencos.__version__
    print(f'{__version__=}')
    assert __version__
    assert __version__ != 'unknown'
    numbers = __version__.split('.')
    assert any(int(number) != 0 for number in numbers)
