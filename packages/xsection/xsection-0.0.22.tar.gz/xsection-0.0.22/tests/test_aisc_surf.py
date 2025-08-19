import sys
import veux
import numpy as np
from xsection.library import from_aisc
from xsection.analysis.interaction import limit_surface, plot_limit_surface
from xara.units.iks import kip, ksi, foot, inch

if __name__ == "__main__":
    c = "centroid"

    shape = from_aisc(sys.argv[1], mesh_scale=1/100)
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

    # print(shape.summary(shear=True))


#   _test_opensees(shape,
#                  section=os.environ.get("Section", "fiber"),
#                  center =os.environ.get("Center", None)
#   )

    # 1) create basic section
#   basic = shape.linearize()


    Fy = 60*ksi
    mat = [
        {
            "name": "rebar",
            "type": "Steel01",
            "E":   29e3*ksi,
            "Fy":    Fy,
            "b":   0.05
        }
    ]
    Pu = shape.area*Fy*0.9
    Mu = 1450*kip*foot*0.9

    print(f"{Pu = }, {Mu = }")
    samples = limit_surface(
        ("Fiber", shape, mat),
        control_dof=1,
        control_points=np.linspace(-Pu, Pu, 80), #35),
        dof_i=5,
        dof_j=6,
        nr=80, #80,
        max_scale=Mu,
        numIncr=60,
        linear_tol=0.02  # 2% departure from linear prediction
    )

    canvas = plot_limit_surface(samples)
    # canvas.plot_vectors(
    #     np.zeros((3,3)),
    #     np.eye(3)
    # )
    veux.serve(canvas)
