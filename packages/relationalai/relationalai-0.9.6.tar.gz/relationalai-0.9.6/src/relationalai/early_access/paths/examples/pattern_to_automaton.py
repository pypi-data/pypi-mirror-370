from relationalai.early_access.paths.api import path, union
from relationalai.early_access.builder import Concept

Node = Concept('Node')
OddNode = Concept('OddNode')
EvenNode = Concept('EvenNode')

# pattern = path(node(Node, lambda n: n.id > 3), star('-[A]->', '-[B]->'), Node)

# pattern = path(node(Node, lambda n: n.id > 3), Node)

# pattern = path(Node, '-[A]->', Node, '-[B]->', Node)

# pattern = path('-[B]->', node(Node, lambda n: n.id > 3), '-[A]->')

# pattern = path(OddNode, star('-[A]->', '-[B]->'), EvenNode)

# pattern = path(OddNode, star('-[A]->', node(OddNode, lambda n: n.id > 3)), EvenNode)

pattern = path(union("-[A]->", "-[B]->"), union("-[A]->", "-[B]->"))

g = pattern.glushkov()
a = g.automaton()
a.reduce()

print(a)


