""" mesh_utils

Module for mesh operations

"""
from .numerrin_code import NumerrinCode


def create_quad_mesh(name, numerrin_wrapper, corner_points, extrude_length,
                     nex, ney, nez):
    """ create and add NumerrinMesh to wrapper

    Parameters
    ----------
    name : str
        name of mesh
    numerrin_wrapper : NumerrinWrapper
        Numerrin wrapper
    corner_points : tuple
        list of (x,y) corner points
    extrude_length : real
        extrude lenght in z -direction
    nex : int
        number of elements in x -direction
    ney : int
        number of elements in y -direction
    nez : int
        number of elements in z -direction

    """

    mesh_code = """
pts={%f,%f;%f,%f;%f,%f;%f,%f}
Quadmesh(pts,{%i,%i},{0,0,0,0},{1.0,1.0,-1.0,-1.0},mesh2d,domains2d)
dvec[0:1]=0.0
dvec[2]=%f
Extrude(mesh2d,domains2d,dvec,%i,0,0.0,%s,domains)
omega->domains[0]
%sdomains0->domains[3]
%sdomains1->domains[4]
%sdomains2=Union(domains[1],domains[2])
%sdomains3=Union(domains[5],domains[6])
""" % (corner_points[0][0], corner_points[0][1],
       corner_points[1][0], corner_points[1][1],
       corner_points[2][0], corner_points[2][1],
       corner_points[3][0], corner_points[3][1],
       nex, ney, extrude_length, nez, name, name,
       name, name, name)
    code = NumerrinCode(numerrin_wrapper.pool.ph)
    code.parse_string(mesh_code)
    code.execute(1)
    boundaries = [0, 1, 2, 3]
    (smesh, mmap) = numerrin_wrapper.pool.export_mesh(name, boundaries)

    # add mesh to wrapper

    numerrin_wrapper.add_dataset(smesh)
