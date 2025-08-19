import veux
import numpy as np
from veux.config import NodeStyle
from xsection import CompositeSection
from xsection.library import Rectangle, Circle, Rebar
from xara.units import iks

if __name__ == "__main__":
    rebar = Rebar("us", iks)

    d   = 18*iks.inch
    b   = 20*iks.inch
    t   =  6*iks.inch
    cv  =  2*iks.inch
    bar = Circle(0.4, z=2, mesh_scale=1/2, divisions=10)
#   bar = Circle(0.4, z=2, mesh_scale=1.2, divisions=8)
    c = CompositeSection([
           Rectangle(t,d, z=0, mesh_scale=1/5),
           Rectangle(b,t, z=1, mesh_scale=1/5).translate([0, -d/2-t/2]),
#          Circle(0.4, z=2, mesh_scale=1).translate([0, 4]),
           *bar.linspace([-(b/2-cv), -d/2-t/1.5], [b/2-cv, -d/2-t/1.5], 4, z=2)
        ])

    m = c.model
    a = veux.create_artist(c.model) #(m.nodes, m.cells()))
    a.draw_surfaces() #field=c.torsion_warping())
    a.draw_outlines()
    Rc = np.eye(3) # a._plot_rotation.T
    for fiber in c.create_fibers(group=2):
        a.canvas.plot_nodes([Rc@[fiber["y"], fiber["z"], 0]]) #, style=NodeStyle(color="red", scale=1))
    for fiber in c.create_fibers(group=1):
        a.canvas.plot_nodes([Rc@[fiber["y"], fiber["z"], 0]], style=NodeStyle(color="blue", scale=1))
    veux.serve(a)
