import os
import sys
import veux
import numpy as np
import matplotlib.pyplot as plt
import opensees.openseespy as ops
from shps.shapes import Channel, Rectangle, WideFlange

def _test_opensees(shape, section, center=None):
    model = ops.Model(ndm=3, ndf=6)
    E    = 1e3 #29000*ksi,
    nu   = 0.3
    G = 0.5*E/(1+nu)
    model.material("ElasticIsotropic", 1, E, nu, 0.0)
    model.section("ShearFiber", 1, GJ=0)

    if section == "fiber":
        for fiber in shape.create_fibers(center=center):
            model.fiber(**fiber,  section=1, material=1)
    else:
        print("Section = Elastic")
        cnn = shape._analysis.cnn()
        cnm = shape._analysis.cnm()
#       cnw = shape._analysis.cnw()
        cnv = shape._analysis.cnv()
        cmm = shape._analysis.cmm()
        cww = shape._analysis.cww()
        cmv = shape._analysis.cmv()
        cmw = shape._analysis.cmw()
        A = cnn[0,0]
        model.section("ElasticFrame", 1,
                        E=E,
                        G=G,
                        A=A,
                        Ay=1*A,
                        Az=1*A,
                        Qy=cnm[0,1],
                        Qz=cnm[2,0],
                        Iy=cmm[1,1],
                        Iz=cmm[2,2],
#                       Iyz=-cmm[1,2],
                        J =shape._analysis.torsion_constant(),
                        Cw= cww[0,0],
#                       Rw= 0, #cnw[0,0], # this is pretty much always 0.0
                        Ry= cnv[1,0],
                        Rz= cnv[2,0],
                        Sa= cmv[0,0],
                        Sy= cmw[1,0],
                        Sz= cmw[2,0]
        )
        del cnn, cnm, cnv, cmm, cww, cmv, cmw

    tangent = model.invoke("section", 1, [
                           "update  "+" ".join(["0"]*12)+";",
                           "tangent"
            ])

    n = int(np.sqrt(len(tangent)))
    Ks = np.array(tangent).reshape(n,n).T
#   plt.spy(Ks)
#   plt.imshow(Ks,interpolation='none',cmap='binary')
#   plt.show()
    # Ks = np.round(Ks, 4)
    # print(pd.DataFrame(Ks))

    cnn = Ks[:3,:3]
    cmm = Ks[3:6,3:6]
    cnm = Ks[:3,3:6]
    cnw = Ks[:3,6:9]
    cnv = Ks[:3,9:12]
    cmw = Ks[3:6,6:9]
    cmv = Ks[3:6,9:12]
    cww = Ks[6:9,6:9]
    cvv = Ks[9:12,9:12]
    # print(f"{cnm = }")
    # print(f"{cnw = }")

    s = ""
    tol=1e-14

    EA = cnn[0,0]
    A  = EA/E
    GA = G*A

    Qy = cnm[0,1] # int z
    Qz = cnm[2,0] # int y
    # Compute centroid
    cx, cy = float(Qz/GA), float(Qy/EA)
    cx, cy = map(lambda i: i if abs(i)>tol else 0.0, (cx, cy))


    Ivv = cvv[0,0]
    Isv = cmm[0,0] - Ivv

    s += f"""

  [nn]    Area               {A           :>10.4}
  [nm]    Centroid           {0.0         :>10.4}  {cx          :>10.4}, {cy          :>10.4}
  [nw|v]                     {cnw[0,0]/GA :>10.4}  {cnv[1,0]/GA :>10.4}, {cnv[2,0]/GA :>10.4}

  [mm]    Flexural moments   {cmm[0,0]/G  :>10.4}  {cmm[1,1]/E  :>10.4}, {cmm[2,2]/E  :>10.4}, {cmm[1,2]/E :>10.4}
  [mv|w]                     {cmv[0,0]/G  :>10.4}  {cmw[1,0]/E  :>10.4}, {cmw[2,0]/E  :>10.4}


  [ww]    Warping constant   {cww[0,0]/E  :>10.4}
          Torsion constant   {Isv/G       :>10.4}
  [vv]    Bishear            {Ivv/G       :>10.4}
    """
    print(s)

if __name__ == "__main__":
    case = "e0011" if len(sys.argv) < 2 else sys.argv[1]

    # shaft-
    benchmarks = dict(
        # B&P, 
        e0010 = dict(
            section=Rectangle(
                d  = 10,
                b  = .5
            ),
            center="centroid"
        ),
        # L&H, Example 1; W21x93
        e0011 = dict(
            section=WideFlange(
                tf = 0.93,
                tw = 0.58,
                d  = 21.62,
                b  = 8.42,
                mesh_scale=1/5,
                # saint_venant="linear"
            ),
            center="centroid"
        ),
        # G, S & W, 6.2
        e0012 = dict(
            section=Channel(
                tf =  1.6,
                tw =  1.0,
                b  = 10.0,
                d  = 30.0
            ),
            center = (0,0),
            offset = {
                "A": ( - 3.571, 0),
                "B": (0, 0),
                "C": (2.449, 0),
                "D": (0, 15),
                "E": ( - 5.571, 0),
            }
        ),
        # G, S & W, 6.2
        e0013 = dict(
            section=Channel(
                tf =  1.6,
                tw =  1.0,
                b  = 10.0,
                d  = 30.0
            ),
            center = (0,0),
        ),
        e0014 = dict(
            section=Channel(
        # G, S & W, 6.1
                tf =  0.2,
                tw =  0.2,
                b  = 10.0,
                d  = 10.0
            ),
            center = "centroid"
        ),
        e0015 = dict(
            section=Channel(
                tf =  0.2,
                tw =  0.2,
                b  =  3.5,
                d  =  5.2
            ),
            center = (0,0),
            offset = {
            }
        ),
        # Plastic hinging, W?x94
        e0030 = dict(
            section=WideFlange(
                tf = 0.93,
                tw = 0.58,
                d  = 21.62,
                b  = 8.42,
                # saint_venant="linear"
            ),
            center="centroid"
        ),
    )

    # 
    # Pilkey ?
#   t =  1.0
#   w = t
#   b = 8.50
#   h = 19.0

#   t =  12.7
#   w = t
#   b = 74.0
#   h = 305.0

    # Lacarbonara, Example 6.4
#   t = 10.5
#   w = 7.5
#   d = 160
#   b = 65
#   o = "centroid"


    shape = benchmarks[case]["section"] #.create_shape()
    d = benchmarks[case]["section"].d

    offset = os.environ.get("Offset", None)
    if "offset" in benchmarks[case] and offset is not None:
        c = benchmarks[case]["offset"][offset]
    else:
        c = benchmarks[case]["center"]


#   section = section.translate(section._analysis.centroid()).translate([-18.4, 0])
#   print(section.summary())

    if c == "shear-center":
        shape = shape.translate(-shape._analysis.shear_center())

    elif c == "centroid":
        shape = shape.translate(-shape._analysis.centroid())

    else:
        shape = shape.translate(c)

    print(shape.summary())

    _test_opensees(shape,
                   section=os.environ.get("Section", "fiber"),
                   center =os.environ.get("Center", None)
    )

    # 1) create basic section
    basic = shape.elastic #linearize()

    field = shape._analysis.warping()

    # 3) view warping modes
    artist = veux.create_artist(shape.model, ndf=1, ndm=2)

    field = {node: value/100.0 for node, value in enumerate(field)}

    artist.draw_surfaces(field = field,
                         #state=field
                         )
    artist.draw_outlines()
    R = artist._plot_rotation

    artist.canvas.plot_vectors([[0,0,0] for i in range(3)], d/5*R.T)
    artist.canvas.plot_vectors([R@[*shape._analysis.shear_center(), 0] for i in range(3)], d/5*R.T)
    artist.draw_outlines()
    veux.serve(artist)

