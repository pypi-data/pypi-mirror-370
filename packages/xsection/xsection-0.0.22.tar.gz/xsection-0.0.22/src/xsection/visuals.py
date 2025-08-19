import veux
def show_outline(shape):
    canvas = veux._create_canvas()
    canvas.plot_lines(shape.exterior())
    for hole in shape.interior():
        canvas.plot_lines(hole)
    
    return canvas


if __name__ == "__main__":

    import sys 
    from xsection.library import from_aisc
    veux.serve(show_outline(from_aisc(sys.argv[1])))