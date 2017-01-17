""" numerrin_pool

Module for operations on Numerrin pool

"""
from simphony.cuds.mesh import Mesh, Point, Edge, Face, Cell
from simphony.core.cuba import CUBA

from .numerrin_utils import (face_renode, cell_renode, generate_uuid)
from .numerrin_templates import (numvariables, numname)
import numerrin


class NumerrinPool(object):
    """ Class for operations on Numerrin variable pool

    """

    def __init__(self):
        self.ph = numerrin.createpool()

    def __del__(self):
        numerrin.deletepool(self.ph)

    def export_mesh(self, s_name, name, boundary_names):
        """ export Numerrin mesh from pool to SimPhoNy Mesh object

        Parameters
        ----------
        name : str
            name of mesh

        boundary_names : list str
            list of boundary domain names

        Return
        ------
        (simphonyMesh, mmap) : tuple
            tuple of SimPhoNy mesh object and mapping from low
            level objects uuid to Numerrin label

        """

        simphonyMesh = Mesh(s_name)
        uuids = []
        mmap = {}
        meshsize = numerrin.meshsize(self.ph, name)
        spoints = []
        for i in range(meshsize[0]):
            coord = numerrin.getnode(self.ph, name, i)
            spoint = Point(coord, uid=generate_uuid())
            spoints.append(spoint)
            uuids.append(spoint.uid)
            mmap[spoint.uid] = i

        simphonyMesh.add(spoints)

        if len(meshsize) > 1:
            edges = []
            for i in range(meshsize[1]):
                plbl = numerrin.getelement(self.ph, name, 1, i, 0)
                points = []
                for pi in range(len(plbl)):
                    points.append(uuids[plbl[pi]])
                ed = Edge(points, uid=generate_uuid())
                edges.append(ed)
                mmap[ed.uid] = i
            simphonyMesh.add(edges)

        if len(meshsize) > 2:
            labeluidmap = {}
            faces = []
            for i in range(meshsize[2]):
                plbl = numerrin.getelement(self.ph, name, 2, i, 0)
                points = []
                for pi in range(len(plbl)):
                    points.append(uuids[plbl[pi]])
                face_renode(points)
                fa = Face(points, uid=generate_uuid())
                faces.append(fa)
                mmap[fa.uid] = i
                labeluidmap[i] = fa.uid
            simphonyMesh.add(faces)

            boundaries = {}
            for boundary in boundary_names:
                boundaries[boundary] = []
                boundary_faces = numerrin.getelementnumbers(self.ph,
                                                            name+boundary)
                for boundary_face in boundary_faces:
                    boundaries[boundary].append(
                        labeluidmap[boundary_face])

        if len(meshsize) > 3:
            cells = []
            for i in range(meshsize[3]):
                plbl = numerrin.getelement(self.ph, name, 3, i, 0)
                points = []
                for pi in range(len(plbl)):
                    points.append(uuids[plbl[pi]])
                cell_renode(points)
                ce = Cell(points, uid=generate_uuid())
                cells.append(ce)
                mmap[ce.uid] = i
            simphonyMesh.add(cells)

        return (simphonyMesh, mmap, boundaries)

    def import_mesh(self, name, simphonyMesh, boundaries):
        """ import SimPhoNy mesh to Numerrin pool as Numerrin mesh

        Parameters
        ----------
        name : str
            name of mesh
        SimphonyMesh : Mesh
            Mesh object to import

        Return
        ------
        maps : list
            list of maps from SImPhoNy mesh low level objects
            uid's to corresponding Numerrin mesh objects
            mmap : dictionary
                map from uuid to Numerrin label
            pmap : dictionary
                map from Numerrin point label to uuid
            emap : dictionary
                map from Numerrin edge label to uuid
            fmap : dictionary
                map from Numerrin face label to uuid
            cmap : dictionary
                map from Numerrin cell label to uuid

        """

        nPoints = simphonyMesh.count_of(CUBA.POINT)
        nEdges = simphonyMesh.count_of(CUBA.EDGE)
        nFaces = simphonyMesh.count_of(CUBA.FACE)
        nCells = simphonyMesh.count_of(CUBA.CELL)

        sizes = (nPoints, nEdges, nFaces, nCells)
        numerrin.initmesh(self.ph, name, 3, sizes)

        mmap = {}
        pmap = {}
        indx = 0
        for point in simphonyMesh.iter(item_type=CUBA.POINT):
            numerrin.setnode(self.ph, name, indx, point.coordinates)
            mmap[point.uid] = indx
            pmap[indx] = point.uid
            indx = indx+1

        indx = 0
        emap = {}

        for edge in simphonyMesh.iter(item_type=CUBA.EDGE):
            pind = []
            for point in edge.points:
                pind.append(mmap[point])
            numerrin.setelementtype(self.ph, name, 1, indx, 1)
            numerrin.setelement(self.ph, name, 1, indx, 0, tuple(pind))
            mmap[edge.uid] = indx
            emap[indx] = edge.uid
            indx = indx+1

        indx = 0
        fmap = {}
        for face in simphonyMesh.iter(item_type=CUBA.FACE):
            pind = []
            for point in face.points:
                pind.append(mmap[point])
            face_renode(pind)
            if len(pind) == 3:
                numerrin.setelementtype(self.ph, name, 2, indx, 2)
            else:
                numerrin.setelementtype(self.ph, name, 2, indx, 3)
            numerrin.setelement(self.ph, name, 2, indx, 0, tuple(pind))
            mmap[face.uid] = indx
            fmap[indx] = face.uid
            indx = indx+1

        boundary_faces = {}
        for boundary in boundaries:
            boundary_faces[boundary] = []
            for fuid in boundaries[boundary]:
                boundary_faces[boundary].append(mmap[fuid])

        indx = 0
        cmap = {}
        cell_ids = []
        for cell in simphonyMesh.iter(item_type=CUBA.CELL):
            pind = []
            for point in cell.points:
                pind.append(mmap[point])
            cell_renode(pind)
            if len(pind) == 4:
                numerrin.setelementtype(self.ph, name, 3, indx, 4)
            elif len(pind) == 6:
                numerrin.setelementtype(self.ph, name, 3, indx, 6)
            else:
                numerrin.setelementtype(self.ph, name, 3, indx, 7)
            numerrin.setelement(self.ph, name, 3, indx, 0, tuple(pind))
            mmap[cell.uid] = indx
            cmap[indx] = cell.uid
            cell_ids.append(indx)
            indx = indx+1

        # create edges and faces if not exists
        if not simphonyMesh.has_type(CUBA.EDGE):
            numerrin.createedges(self.ph, name)
            # create mapping
            for i in range(self.mesh_size(name)[1]):
                points = []
                edge = Edge(points, uid=generate_uuid())
                emap[i] = edge.uid
                mmap[edge.uid] = i
        if not simphonyMesh.has_type(CUBA.FACE):
            numerrin.createfaces(self.ph, name)
            # create mapping
            for i in range(self.mesh_size(name)[2]):
                uid = generate_uuid()
                fmap[i] = uid
                mmap[uid] = i
        # create neighbor lists
        numerrin.createneighbors(self.ph, name, 1)
        numerrin.createneighbors(self.ph, name, 2)
        numerrin.createneighbors(self.ph, name, 3)
        # create references between different levels
        numerrin.createrefs(self.ph, name, 2, 1)
        numerrin.createrefs(self.ph, name, 3, 1)
        numerrin.createrefs(self.ph, name, 3, 2)

        # add inner domain
        numerrin.createdomain(self.ph, "omega", name, 3, tuple(cell_ids))
        # add boundary domains
        self.add_boundaries(name, boundaries, boundary_faces)

        return [mmap, pmap, emap, fmap, cmap]

    def add_boundaries(self, name, boundaries, boundary_faces):
        for boundary_name in boundaries:
            numerrin.createboundary(self.ph, name+boundary_name, name,
                                    2, tuple(boundary_faces[boundary_name]))

    def clear(self):
        """ clear Numerrin pool
        """
        numerrin.clearpool(self.ph)

    def variable_type(self, name):
        """ get Numerrin variable type

        Parameters
        ----------
        name : str
            name of variable
        Return
        -----
        type : str
            variable type
        """

        return numerrin.gettype(self.ph, name)

    def variable_rank(self, name):
        """ get Numerrin variable rank

        Parameters
        ----------
        name : str
            name of variable
        Return
        -----
        rank : int
           variable rank
        """
        return numerrin.getrank(self.ph, name)

    def variable_size(self, name):
        """ get Numerrin variable size

        Parameters
        ----------
        name : str
            name of variable
        Return
        -----
        size : int
           variable size
        """
        return numerrin.getsize(self.ph, name)

    def get_variable(self, name):
        """ get Numerrin variable values

        Parameters
        ----------
        name : str
            name of variable
        Return
        -----
        values : tuple
            variable values as tuple or tuple of tuples
            if vector valued variable
        """
        return numerrin.getvariable(self.ph, name)

    def get_real_function(self, name):
        """ get Numerrin function values

        Parameters
        ----------
        name : str
            name of variable
        Return
        -----
        values : tuple
            variable values as tuple or tuple of tuples
            if vector valued variable
        """
        return numerrin.getrealfunction(self.ph, name)

    def put_parameter(self, name, par):
        """ put parameter to Numerrin pool

        Parameters
        ----------
        name : str
            name of parameter
        par : value, tuple or dictionary
            tuple of variable values or tuple of
            tuples if vector valued variable
            or
            dictionary of tuple of variable values or tuple of
            tuples if vector valued variable
        """
        if isinstance(par, dict):
            for pari in par:
                pool_name = ''.join(pari) + name
                numerrin.putvariable(self.ph, pool_name, par[pari])
        else:
            numerrin.putvariable(self.ph, name, par)

    def put_variable(self, name, var):
        """ put variable to Numerrin pool

        Parameters
        ----------
        name : str
            name of variable
        var : value or tuple
            tuple of variable values or tuple of
            tuples if vector valued variable
        """
        numerrin.putvariable(self.ph, name, var)

    def create_space(self, name, domain_name, basis_name, basis_degree):
        """ create space to Numerrin pool

        Parameters
        ----------
        name : str
            name of space
        domain_name : str
            name of domain
        basis_name : str
            name of function basis
        basis_degree : int
            degree of basis function
        """
        numerrin.createspace(self.ph, name, domain_name, basis_name,
                             basis_degree)

    def create_realfunction(self, name, space_name, function_size):
        """ create space to Numerrin pool

        Parameters
        ----------
        name : str
            name of realfunction
        space_name : str
            name of function space
        function_size : int or tuple
            size of the function space
        """
#        print type(self.ph)
#        print type(name)
#        print type(space_name)
#        print type(function_size)
        numerrin.createrealfunction(self.ph, name, space_name, function_size)

    def modify_variable(self, name, var):
        """ modify variable values in pool

        Parameters
        ----------
        name : str
            name of variable
        var : tuple
            tuple of variable new values or tuple of
            tuples if vector valued variable
        """
        numerrin.modifyvariable(self.ph, name, var)

    def delete_mesh_and_variables(self, name):
        """ delete mesh and corresponding variables from pool

        Parameters
        ----------
        name : str
            name of mesh

        """

        for dkey in numvariables:
            dataName = numname[dkey]
            mDataName = name + dataName
            try:
                numerrin.clearvariable(self.ph, mDataName)
            except RuntimeError:
                pass
        numerrin.clearvariable(self.ph, name)

    def mesh_size(self, name):
        """ get Numerrin mesh size

        Parameters
        ----------
        name : str
            name of variable
        Return
        -----
        size : int tuple
           mesh size in different levels
        """
        return numerrin.meshsize(self.ph, name)

    def get_edge_points(self, name, label):
        """ get mesh edge points from pool

        Parameters
        ----------
        name : str
            name of mesh
        label : int
            edge label

        Return
        ------
        labels : list
            list of edge points labels

        """
        return numerrin.getelement(self.ph, name,
                                   1, label, 0)

    def get_face_points(self, name, label):
        """ get mesh face points from pool

        Parameters
        ----------
        name : str
            name of mesh
        label : int
            face label

        Return
        ------
        labels : list
            list of face points labels

        """
        pointLabels = numerrin.getelement(self.ph, name,
                                          2, label, 0)
        return face_renode(list(pointLabels))

    def get_cell_points(self, name, label):
        """ get mesh cell points from pool

        Parameters
        ----------
        name : str
            name of mesh
        label : int
            cell label

        Return
        ------
        labels : list
            list of face points labels

        """
        pointLabels = numerrin.getelement(self.ph, name,
                                          3, label, 0)
        return cell_renode(list(pointLabels))
