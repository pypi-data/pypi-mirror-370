import sys
import veux
import numpy as np
from xsection.library import from_aisc
from xsection.analysis.interaction import limit_surface, plot_limit_surface


if __name__ == "__main__":
    c = "centroid"

    shape = from_aisc(sys.argv[1])
    d = shape.d

    if False:
        pass
    elif c == "shear-center":
        shape = shape.translate(-shape._analysis.shear_center())

    elif c == "centroid":
        print(f"{shape.centroid = }")
        shape = shape.translate(-shape.centroid)

    else:
        shape = shape.translate(c)

    print(shape.summary(shear=True))

    print("tan(alpha): ", np.tan(shape._principal_rotation()))

#   _test_opensees(shape,
#                  section=os.environ.get("Section", "fiber"),
#                  center =os.environ.get("Center", None)
#   )

    # 1) create basic section
#   basic = shape.linearize()

    field = shape._analysis.warping()

    # 3) view warping modes
    artist = veux.create_artist(shape.model, ndf=1, ndm=2)

    field = {node: value/100.0 for node, value in enumerate(field)}

    artist.draw_surfaces(field = field,
                         #state=field
                         )
    artist.draw_outlines()
    R = artist._plot_rotation

    artist.canvas.plot_vectors([[0,0,0] for i in range(3)], d/5*R.T, extrude=True)
    artist.canvas.plot_vectors([R@[*shape._analysis.shear_center(), 0] for i in range(3)], d/5*R.T, extrude=True)
    artist.draw_outlines()
    veux.serve(artist)
