""" numerrin_pool

Module for operations on Numerrin pool

"""
from simphony.core.cuba import CUBA
from simphony.cuds.mesh import Mesh, Point, Edge, Face, Cell
from simphony.core.cuds_item import CUDSItem

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

    def export_mesh(self, name, boundaries):
        """ export Numerrin mesh from pool to SimPhoNy Mesh object

        Parameters
        ----------
        name : str
            name of mesh

        name : list int
            list of boundary numbers to be exported

        Return
        ------
        (simphonyMesh, mmap) : tuple
            tuple of SimPhoNy mesh object and mapping from low
            level objects uuid to Numerrin label

        """

        simphonyMesh = Mesh(name)
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

        simphonyMesh.add_points(spoints)

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
            simphonyMesh.add_edges(edges)

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
            simphonyMesh.add_faces(faces)

            faces_to_update = []
            for boundary in boundaries:
                boundary_name = name+"domains"+str(boundary)
                boundary_faces = numerrin.getelementnumbers(self.ph,
                                                            boundary_name)
                for boundary_face in boundary_faces:
                    face = simphonyMesh.get_face(labeluidmap[boundary_face])
                    # boundaryname ends to number which is used for label
                    face.data[CUBA.LABEL] = boundary
                    faces_to_update.append(face)
            simphonyMesh.update_faces(faces_to_update)

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
            simphonyMesh.add_cells(cells)

        return (simphonyMesh, mmap)

    def import_mesh(self, name, simphonyMesh):
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

        nPoints = simphonyMesh.count_of(CUDSItem.POINT)
        nEdges = simphonyMesh.count_of(CUDSItem.EDGE)
        nFaces = simphonyMesh.count_of(CUDSItem.FACE)
        nCells = simphonyMesh.count_of(CUDSItem.CELL)

        sizes = (nPoints, nEdges, nFaces, nCells)
        numerrin.initmesh(self.ph, name, 3, sizes)

        mmap = {}
        pmap = {}
        indx = 0
        for point in simphonyMesh.iter_points():
            numerrin.setnode(self.ph, name, indx, point.coordinates)
            mmap[point.uid] = indx
            pmap[indx] = point.uid
            indx = indx+1

        indx = 0
        emap = {}

        for edge in simphonyMesh.iter_edges():
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
        boundary_faces = {}
        for face in simphonyMesh.iter_faces():
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
            if CUBA.LABEL in face.data:
                blabel = face.data[CUBA.LABEL]
                bname = name + "domains" + str(blabel)
                if bname not in boundary_faces:
                    boundary_faces[bname] = []
                boundary_faces[bname].append(indx)
            indx = indx+1

        indx = 0
        cmap = {}
        cell_ids = []
        for cell in simphonyMesh.iter_cells():
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
        if not simphonyMesh.has_edges():
            numerrin.createedges(self.ph, name)
            # create mapping
            for i in range(self.mesh_size(name)[1]):
                points = []
                edge = Edge(points, uid=generate_uuid())
                emap[i] = edge.uid
                mmap[edge.uid] = i
        if not simphonyMesh.has_faces():
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
        face_boundary_list = []
        for boundary_name in boundary_faces:
            numerrin.createboundary(self.ph, boundary_name, name,
                                    2, tuple(boundary_faces[boundary_name]))
            # add boundary corresponding list of faces as a variable
            for indx in boundary_faces[boundary_name]:
                face_boundary_list.append(boundary_name+"Face"+str(indx))

        # this to get back face corresponding boundary name
        numerrin.putvariable(self.ph, name + "boundaryFaces",
                             tuple(face_boundary_list))

        return [mmap, pmap, emap, fmap, cmap]

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

    def get_face_boundary_label(self, name, label):
        """ get boundary label on which face belongs

        Parameters
        ----------
        name : str
            name of mesh
        label : int
            face label

        Return
        ------
        bname : int
            boundary label for face

        """
        face_boundary_list = self.get_variable(name+"boundaryFaces")
        face_label = "Face"+str(label)
        facew = next((w for w in face_boundary_list if face_label in w), None)
        bname = facew.replace(face_label, '')
        bnumber = bname.replace(name+"domains", '')
        return int(bnumber)
