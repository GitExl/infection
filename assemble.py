import sys

from wadassembler.assembler import Assembler
from wadassembler.context import Context

if len(sys.argv) != 2:
    raise Exception('Not enough arguments.')
target = sys.argv[1]

print('Targeting "{}"'.format(target))
context = Context(target)

assembler = Assembler(context)
assembler.assemble()
