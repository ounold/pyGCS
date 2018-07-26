from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput

from main import Main

graphviz = GraphvizOutput(output_file="gcs.png")

with PyCallGraph(output=graphviz):
    main = Main()
    main.start()