import sys
from .core import run_with_ai_fix

def main():
    last_cmd = " ".join(sys.argv[1:])
    run_with_ai_fix(last_cmd)
