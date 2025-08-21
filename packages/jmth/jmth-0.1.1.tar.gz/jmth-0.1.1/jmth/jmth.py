def volume_cube(s):
    """Calculate volume of cube with side s"""
    return s ** 3

def spldv(a1, b1, c1, a2, b2, c2):
    """
    Menyelesaikan sistem persamaan linear dua variabel (SPLDV) dengan metode eliminasi.
    
    Persamaan:
        a1*x + b1*y = c1
        a2*x + b2*y = c2

    Args:
        a1, b1, c1, a2, b2, c2 (float/int): koefisien dan konstanta

    Returns:
        tuple (x, y) jika ada solusi unik,
        str pesan error jika tidak bisa diselesaikan.
    """

    # Cari faktor pengali untuk eliminasi variabel x
    faktor1 = a2
    faktor2 = a1

    # Eliminasi variabel x
    new_b1 = b1 * faktor1
    new_c1 = c1 * faktor1
    new_b2 = b2 * faktor2
    new_c2 = c2 * faktor2

    elim_b = new_b1 - new_b2
    elim_c = new_c1 - new_c2

    if elim_b == 0:
        return "Unable to complete (elimination failed)."

    # Hitung y
    y = elim_c / elim_b

    # Hitung x
    if a2 != 0:
        x = (c2 - b2 * y) / a2
    elif a1 != 0:
        x = (c1 - b1 * y) / a1
    else:
        return "Cannot solve because the coefficient of x = 0 in both equations."

    return (x, y)
