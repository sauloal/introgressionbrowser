
def fixsppname(spp):
    """
    Fix species name to be tree printable
    """
    return spp.replace(' ', '_').replace('(', '').replace(')', '').replace("'", '')
