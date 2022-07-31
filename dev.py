# from tests.test_original_posting import test_version
# test_version()
from original_posting.ptags_tools import parse, generic_dumps, generic_loads

# npm install -g mathjax-node

x = parse('A[A[x, y, z], "2", 3]', "a")
d = generic_dumps(x)
print(d)
print(generic_loads(d))


print(x)
