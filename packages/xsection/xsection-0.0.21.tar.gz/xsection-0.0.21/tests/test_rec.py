"""
Composite (reinforced concrete) rectangular section.
"""

import json
import veux
import numpy as np
from xara.units.iks import kip, ksi
import xsection as xs
from xsection.analysis import SectionInteraction
"""
A_cover = 24*15 - 21*12 = 108
A_core  = 21*12         = 252
A_rebar = (7/16)**2*pi*8 = 0.6013204688511713 * 8
"""

from xsection.library import Circle, Rectangle
from curvature import section_interaction
from collections import defaultdict
import matplotlib.pyplot as plt

def render(model, tag):
    for section in model["StructuralAnalysisModel"]["properties"]["sections"]:
        if int(section["name"]) == int(tag):
            break

    fibers = defaultdict(lambda : {"coords": [], "areas": []})

    for fiber in section["fibers"]:
        fibers[int(fiber["material"])]["coords"].append(fiber["coord"])
        fibers[int(fiber["material"])]["areas"].append(fiber["area"])

    fig, ax = plt.subplots()
    for i, fiber in enumerate(fibers):
        print(f"A_{fiber} = {sum(fibers[fiber]["areas"])}")
        ax.plot(*zip(*fibers[fiber]["coords"]), label=f"{fiber}", marker="o", markersize=2, linestyle="None")

    fig.legend()
    ax.axis("equal")
    plt.show()


if __name__ == "__main__":
    h = 24
    b = 15
    d = 7/8
    r = 0 #d/2

    c = 1.5

    bar = Circle(d/2, z=2, mesh_scale=1/2, divisions=4)

    # veux.serve(veux.render(bar.model))

    shape = xs.CompositeSection([
                Rectangle(    b, h,     z=0),
                Rectangle(b-2*c, h-2*c, z=1),
                *bar.linspace([-b/2+c+r, -h/2+c+r], [ b/2-c-r,-h/2+c+r], 3), # Top bars
                *bar.linspace([-b/2+c+r,        0], [ b/2-c-r,       0], 2), # Center bars
                *bar.linspace([-b/2+c+r,  h/2-c-r], [ b/2-c-r, h/2-c-r], 3)  # Bottom bars
            ])

    for patch in shape._patches:
        for outline in patch.interior():
            plt.plot(*zip(*outline))

    plt.show()
    artist = veux.create_artist(shape._patches[0].model)
    artist.draw_outlines()
    artist.draw_surfaces()
    veux.serve(artist)


    mat = [
        { # Confined
                "type": "Concrete01",
                "Fpc": -6*ksi,
                "ec0": -0.004,
                "Fcu": -5*ksi,
                "ecu": -0.014,
        },
        { # Unconfined
                "type": "Concrete01",
                "Fpc": -5*ksi,
                "ec0": -0.002,
                "Fcu":  0,
                "ecu": -0.006,
        },
        { # Steel
                "type": "Steel01",
                "E":  30000*ksi,
                "Fy":    60*ksi,
                "b":   0.01
        }
    ]

    axial = np.linspace(0*kip, -180*kip, 10)

    SectionInteraction(("Fiber", shape, mat),
                       axial=axial).analyze(nstep=100, incr=1e-4)


    section_interaction("Fiber", shape, mat, axial)

    with open("a.json") as f:
        render(json.load(f), 1)

