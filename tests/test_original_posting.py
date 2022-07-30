from original_posting import __version__
from original_posting import process, Runtime
import os
Runtime.search_path.append('scripts')
def test_version():
    assert __version__ == '0.1.0'
    z = process("f", r"""



""")
    print(z)