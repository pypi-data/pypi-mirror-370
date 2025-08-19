from ._simple import (
    WideFlange,
    Rectangle,
    Circle,
    Ellipse,
    Equigon,
    HollowRectangle,
    Angle,
    Channel,
    Pipe
)
from ._rebar import Rebar


def from_library(identifier: str,  **kwds):
    pass

def from_aisc(identifier: str, units=None, **kwds):
    """Create a homogeneous cross-section from an AISC identifier.

    Parameters:
        identifier: str
            AISC section identifier (e.g., "W10x15").

        units: object
            Units object to use for conversion (default: ``english``).

        material: object
            Material properties (default: None).

        **kwds:
            Additional keyword arguments for the section constructor.

    Returns:
        section: a subclass of :class:`~xsection.PolygonSection` representing the cross-section.
    """
    if units is None:
        import xara.units.english as _units
        units = _units

    aisc_data = aisc_data(identifier, units=units)

    if aisc_data is None:
        raise ValueError(f"Cannot find section with identifier {identifier}")

    if identifier[0] == "W":
        return WideFlange(d=aisc_data["d"],
                          b=aisc_data["bf"],
                          tf=aisc_data["tf"],
                          tw=aisc_data["tw"],
                          k=aisc_data.get("k1", None),
                          **kwds)

    elif identifier[0] == "L":
        return Angle(d=aisc_data["d"],
                     b=aisc_data["b2"],
                     t=aisc_data["t"],
                     k=aisc_data["kdes"])

    elif identifier[0] == "C":
        return Channel(d=aisc_data["d"],
                       b=aisc_data["bf"],
                       tf=aisc_data["tf"],
                       tw=aisc_data["tw"],
                       sf=2/12)

    elif identifier[:3] == "HSS":
        return HollowRectangle(d=aisc_data["h/tdes"]*aisc_data["tdes"],
                               b=aisc_data["b/tdes"]*aisc_data["tdes"],
                               t=aisc_data["tdes"],
        )

    else:
        raise ValueError(f"Cannot create section from identifier {identifier}")



def aisc_data(SectionName, props="", units=None)->dict:
    """Return a dictionary of cross section properties from the AISC database.

    To automatically create a Section object from the AISC database, use the
    :func:`~xsection.library.from_aisc` function.

    Parameters:
        SectionName: str
            The name of the section (e.g., "W10x15").

    Example:

    >>> from xsection.library import aisc_data
    >>> aisc_data("W12x136")
    >>> # {'d': 13.4, 'bf': 12.4, 'tw': 0.79, 'tf': 1.25, 'A': 39.9, 'Ix': 1240.0, 'Iy': 398.0, 'kdes': 1.85}
    """

    if units is None:
        import opensees.units.english as _units
        units = _units

    from shps.frame.shapes.aisc_imperial import imperial
    SectData = imperial[SectionName.upper()]


    if props == "simple":
        props = ""
        return

    elif props:
        props = props.replace(" ", "").split(",")
        sectData = {k: v for k, v in SectData.items() if k in props}
        if "I" in props:
            sectData.update({"I": SectData["Ix"]})
        return sectData

    for k,v in list(SectData.items()):
        try:
            SectData[k] = float(v)
        except:
            continue

    UNITS = [
        ("d"  ,     units.inch ),
        ("k1"  ,    units.inch ),
        ("h/tdes",  1 ),
        ("b/tdes",  1 ),
        ("tdes",    units.inch ),
        ("bf" ,     units.inch ),
        ("tw" ,     units.inch ),
        ("tf" ,     units.inch ),
        ("A"  ,     units.inch**2 ),
        ("Ix" ,     units.inch**4 ),
        ("Iy" ,     units.inch**4 ),
        # Angle
        ("b2", units.inch),
        ("t",  units.inch),
        ("kdes", units.inch)
    ]

    return {
        k: SectData[k]*scale
        for k, scale in UNITS if k in SectData and isinstance(SectData[k], (float, int))
    }

# backwards compatibility
load_aisc = aisc_data

if __name__ == "__main__":
    import veux
    d  = 100
    tw = 3
    bf = 75
    tf = 3

    mesh = WideFlange(d=d, b=bf, t=tf, tw=tw).create_shape()

    print(mesh.summary())

#   from shps.frame.solvers.plastic import PlasticLocus
#   PlasticLocus(mesh).plot()#(phi=0.5, ip=5)
#   import matplotlib.pyplot as plt
#   plt.show()

    artist = veux.create_artist(((mesh.mesh.nodes, mesh.mesh.cells())), ndf=1)

    field = mesh.torsion.warping()
    field = {node: value for node, value in enumerate(field)}

    artist.draw_surfaces(field = field)
    artist.draw_origin()
#   R = artist._plot_rotation
#   artist.canvas.plot_vectors([R@[*geometry.centroid, 0] for i in range(3)], R.T)
    artist.draw_outlines()
    veux.serve(artist)
