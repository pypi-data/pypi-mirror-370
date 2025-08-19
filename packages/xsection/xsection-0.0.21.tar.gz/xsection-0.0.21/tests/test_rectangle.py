import veux
from veux.config import NodeStyle
from xsection.library import Rectangle

if __name__ == "__main__":
    width  = 12
    depth  = 18

    Iy = width * depth**3 / 12
    Iz = depth * width**3 / 12
    print(f"Iy = {Iy}, Iz = {Iz}")

    shape = Rectangle(d=depth, b=width, mesh_scale=3)

    print(shape.summary())

    a = veux.render(shape.model)

    for fiber in shape.create_fibers():
        print(fiber)

    Rc = a._plot_rotation.T
    for fiber in shape.create_fibers():
        a.canvas.plot_nodes([Rc@[fiber["y"], fiber["z"], 0]], style=NodeStyle(color="blue", scale=1))

    veux.serve(a)
