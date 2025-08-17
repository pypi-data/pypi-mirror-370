import pytest
from speak2py.session import safe_exec

def test_sandbox_blocks_import():
    code = "import os\nresult = 1"
    with pytest.raises(RuntimeError):
        safe_exec(code, {})

def test_sandbox_blocks_open():
    code = "f = open('x.txt','w')\nresult = 1"
    with pytest.raises(RuntimeError):
        safe_exec(code, {})

def test_sandbox_blocks_eval():
    code = "x = eval('2+2')\nresult = x"
    with pytest.raises(RuntimeError):
        safe_exec(code, {})

def test_sandbox_allows_algorithm():
    code = """
def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5)+1):
        if n % i == 0:
            return False
    return True

nums = [2, 3, 4, 17, 21]
result = {n: is_prime(n) for n in nums}
"""
    out = safe_exec(code, {})
    assert "result" in out
    assert out["result"][2] is True
    assert out["result"][4] is False
