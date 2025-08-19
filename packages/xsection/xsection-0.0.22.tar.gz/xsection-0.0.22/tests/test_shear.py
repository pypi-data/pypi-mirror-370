import veux
from veux.config import NodeStyle
from xsection.library import Rectangle, Circle, Ellipse
import math

def square_shear(depth, width, nu, n_terms=100):
    """
    The function first calculates C_4, which involves an infinite series
    approximated by summing up to n_terms. Then, it uses C_4 to calculate k.

    Args:
        a (float): Parameter 'a' in the formulas.
        b (float): Parameter 'b' in the formulas.
        nu (float): Parameter 'ν' (Poisson's ratio) in the formulas.
        n_terms (int, optional): The number of terms to use for approximating
                                 the infinite series for C_4. Defaults to 100.

    Returns:
        float: The computed value of k.
    """
    a = depth/2
    b = width/2
    # --- Step 1: Calculate C_4 ---

    # Calculate the first part of the C_4 expression
    c4_term1 = (4 / 45) * (a**3) * b * (-12 * a**2 - 15 * nu * a**2 + 5 * nu * b**2)

    # Calculate the summation part of the C_4 expression
    c4_series_sum = 0.0
    for n in range(1, n_terms + 1):
        # Numerator of the term inside the summation
        numerator = 16 * (nu**2) * (b**5) * (n * math.pi * a - b * math.tanh(n * math.pi * a / b))
        
        # Denominator of the term inside the summation
        denominator = ((n * math.pi)**5) * (1 + nu)
        
        c4_series_sum += numerator / denominator

    # Combine the two parts to get the final C_4 value
    c4 = c4_term1 + c4_series_sum

    # --- Step 2: Calculate k ---

    k_numerator = -2 * (1 + nu)

    k_denominator = (9 / (4 * (a**5) * b)) * c4 + nu * (1 - (b**2 / a**2))
    
    if k_denominator == 0:
        return float('inf')

    k = k_numerator / k_denominator

    return k

def ellipse_shear(depth, width, nu):
    """
    Calculates the value of k based on the provided formula.

    Args:
        a (float): The value of 'a'.
        b (float): The value of 'b'.
        nu (float): The value of 'ν' (Poisson's ratio).

    Returns:
        float: The calculated value of k.
    """
    a = depth / 2
    b = width / 2
    # Numerator calculation
    numerator = 6 * a**2 * (3 * a**2 + b**2) * (1 + nu)**2

    # Denominator calculation
    term1 = 20 * a**4 + 8 * a**2 * b**2
    term2 = nu * (37 * a**4 + 10 * a**2 * b**2 + b**4)
    term3 = nu**2 * (17 * a**4 + 2 * a**2 * b**2 - 3 * b**4)
    denominator = term1 + term2 + term3

    # Avoid division by zero
    if denominator == 0:
        return float('inf') # Or raise an error, depending on desired behavior

    return numerator / denominator

if __name__ == "__main__":
    depth  = 24.0

    # Iy = width * depth**3 / 12
    # Iz = depth * width**3 / 12

    for aspect in reversed([1, 1.5, 2]):
        width = depth/aspect
        print(f"{depth = }, {width = }")

        shape = Rectangle(d=depth, b=width, mesh_scale=1/600)
        # shape = Ellipse(depth, width, mesh_scale=1/400)

        # print(shape.summary())

        artist = veux.create_artist(shape.model, ndf=1)

        nu= [0, 0.2, 1/2]
        W = [
            shape._analysis.shear_warping(nui)
            for nui in nu
        ]
        i = 0
        w0 = min(w[i].max() for w in W)/2
        for j, w in enumerate(W):
            print(f"nu = {nu[j]}")
            print(shape._analysis.shear_factor(v=w, nu=nu[j]))
            shape._analysis.shear_enhance(w,nu[j])

            # print(nu[j])
            if isinstance(shape, Ellipse):
                print([ellipse_shear(depth, width, nu[j]),
                       ellipse_shear(width, depth, nu[j])], " (Series)")
                print((6*(1+nu[j])**2)/(7+14*nu[j]+8*nu[j]**2))
            else:
                print([square_shear(width, depth, nu[j]),
                    square_shear(depth, width, nu[j])], " (Series)")
                print((5+5*nu[j])/(6+5*nu[j]), " (Simple)")

            print("-"*10)

            wr = (w-shape._analysis.model.nodes.T)[i]/w0
            artist.draw_surfaces(field=wr, state=wr)
            artist.draw_outlines()
        
        if isinstance(shape, Circle):
            break


    veux.serve(artist)
