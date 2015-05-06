""" numerrin_pool

Module for operations on Numerrin pool

"""
from simphony.core.cuba import CUBA
from simphony.cuds.mesh import Mesh, Point, Edge, Face, Cell

from .numerrin_code import NumerrinCode
from .numerrin_utils import face_renode, cell_renode
from .numerrin_templates import numvariables, numname
import numerrin


class NumerrinPool(object):
    """ Class for operations on Numerrin variable pool

    """

    def __init__(self):
        self.ph = numerrin.createpool()

    def __del__(self):
        numerrin.deletepool(self.ph)

    def export_mesh(self, name):
        """ export Numerrin mesh from pool to SimPhoNy Mesh object

        Parameters
        ----------
        name : str
            name of mesh

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
        for i in range(meshsize[0]):
            coord = numerrin.getnode(self.ph, name, i)
            spoint = Point(coord)
            simphonyMesh.add_point(spoint)
            uuids.append(spoint.uid)
            mmap[spoint.uid] = i

        if len(meshsize) > 1:
            for i in range(meshsize[1]):
                plbl = numerrin.getelement(self.ph, name, 1, i, 0)
                points = []
                for pi in range(len(plbl)):
                    points.append(uuids[plbl[pi]])
                ed = Edge(points)
                simphonyMesh.add_edge(ed)
                mmap[ed.uid] = i

        if len(meshsize) > 2:
            for i in range(meshsize[2]):
                plbl = numerrin.getelement(self.ph, name, 2, i, 0)
                points = []
                for pi in range(len(plbl)):
                    points.append(uuids[plbl[pi]])
                face_renode(points)
                fa = Face(points)
                simphonyMesh.add_face(fa)
                mmap[fa.uid] = i

        if len(meshsize) > 3:
            for i in range(meshsize[3]):
                plbl = numerrin.getelement(self.ph, name, 3, i, 0)
                points = []
                for pi in range(len(plbl)):
                    points.append(uuids[plbl[pi]])
                cell_renode(points)
                ce = Cell(points)
                simphonyMesh.add_cell(ce)
                mmap[ce.uid] = i

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

        nPoints = sum(1 for _ in simphonyMesh.iter_points())
        nEdges = sum(1 for _ in simphonyMesh.iter_edges())
        nFaces = sum(1 for _ in simphonyMesh.iter_faces())
        nCells = sum(1 for _ in simphonyMesh.iter_cells())

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
            indx = indx+1

        indx = 0
        cmap = {}
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
            indx = indx+1

        # add domains
        numcode = "omega = Domain(" + name + ")\n"
        boundaries = []
        elementcode = ""
        for face in simphonyMesh.iter_faces():
            if face.data:
                if CUBA.LABEL in face.data:
                    fuid = str(mmap[face.uid])
                    blabel = face.data[CUBA.LABEL]
                    if blabel not in boundaries:
                        boundaries.append(blabel)
                    elementcode += "AddElement(" + name +\
                                   "domains" + str(blabel) + "," +\
                                   fuid + "," + fuid + ")\n" +\
                                   "Face" + fuid + name +\
                                   "=" + str(blabel) + "\n"

        for boundary in boundaries:
            numcode += name + "domains" + str(boundary) +\
                "= Domain(" + name + ",2,2)\n"
        numcode += elementcode
        code = NumerrinCode(self.ph)
        code.parse_string(numcode)
        code.execute(1)

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

    def put_variable(self, name, var):
        """ put variable to Numerrin pool

        Parameters
        ----------
        name : str
            name of variable
        var : tuple
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
            try:
                dataName = numname[dkey]
                mDataName = name + dataName
                numerrin.clearvariable(self.ph, mDataName)
            except:
                pass
        numerrin.clearvariable(self.ph, name)

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
            list of face labels

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
        bname = "Face" + str(label) + name
        return self.get_variable(bname)
