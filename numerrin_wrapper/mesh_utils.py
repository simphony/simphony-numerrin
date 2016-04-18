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

    boundary_names = ['inflow', 'outflow', 'walls', 'frontAndBack']

    p_name = name + "Mesh"
    mesh_code = """
pts={%f,%f;%f,%f;%f,%f;%f,%f}
Quadmesh(pts,{%i,%i},{0,0,0,0},{1.0,1.0,-1.0,-1.0},mesh2d,domains2d)
dvec[0:1]=0.0
dvec[2]=%f
Extrude(mesh2d,domains2d,dvec,%i,0,0.0,%s,domains)
omega->domains[0]
%s->domains[6]
%s->domains[4]
%s=Union(domains[3],domains[5])
%s=Union(domains[1],domains[2])
""" % (corner_points[0][0], corner_points[0][1],
       corner_points[1][0], corner_points[1][1],
       corner_points[2][0], corner_points[2][1],
       corner_points[3][0], corner_points[3][1],
       nex, ney, extrude_length, nez, p_name, p_name+boundary_names[0],
       p_name+boundary_names[1],  p_name+boundary_names[2],
       p_name+boundary_names[3])
    code = NumerrinCode(numerrin_wrapper.pool.ph)
    code.parse_string(mesh_code)
    f = open('mesh.num', 'w')
    f.write(mesh_code)
    f.close()
    code.execute(1)
    (smesh, mmap, boundaries) =\
        numerrin_wrapper.pool.export_mesh(name, p_name,
                                          boundary_names)

    # add mesh to wrapper
    numerrin_wrapper.add_dataset(smesh)

    # add boundaries
    uidmap = numerrin_wrapper.get_dataset(name)._uuidToNumLabel
    boundary_faces = {}
    for boundary in boundaries:
        boundary_faces[boundary] = []
        for fuid in boundaries[boundary]:
            boundary_faces[boundary].append(uidmap[fuid])
    numerrin_wrapper.get_dataset(name).pool.add_boundaries(name, boundaries,
                                                           boundary_faces)
    numerrin_wrapper.get_dataset(name)._boundaries = boundaries
