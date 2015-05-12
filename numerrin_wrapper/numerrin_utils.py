""" numerrin_utils

Utility functions

"""


def face_renode(tab):
    """ renodes face nodes between SimPhoNy and Numerrin mesh

    """

    if len(tab) == 4:
        tmp = tab[2]
        tab[2] = tab[3]
        tab[3] = tmp
    return tab


def cell_renode(tab):
    """ renodes cell nodes between SimPhoNy and Numerrin mesh

    """

    if len(tab) == 8:
        tmp = tab[2]
        tab[2] = tab[3]
        tab[3] = tmp
        tmp = tab[6]
        tab[6] = tab[7]
        tab[7] = tmp
    return tab
