""" Mesh module

This module contains the implementation to store, access,
and modify a mesh and related data

"""
from simphony.cuds.abstractmesh import ABCMesh
from simphony.cuds.mesh import Face, Point, Cell
from simphony.core.cuba import CUBA

from .numerrin_templates import numname

import numerrin


class NumerrinMesh(ABCMesh):
    """ Proxy class to communicate with Numerrin pool mesh data

    Parameters
    ----------
    name : str
        name of mesh

    mesh : ABCMesh
       mesh to store

    pool : NumerrinPool
       Numerrin variable pool

    Attributes
    ----------
    name : str
        name of mesh

    mesh : ABCMesh
       mesh to store

    pool : NumerrinPool
       Numerrin variable pool

    _uuidToNumLabel : dictionary
        Mapping from uuid to Numerrin label number
    _numCellLabelToUuid : dictionary
        Mapping from Numerrin cell label number to uuid
    _numFaceLabelToUuid : dictionary
        Mapping from Numerrin face label number to uuid
    _numEdgeLabelToUuid : dictionary
        Mapping from Numerrin edge label number to uuid
    _numPointLabelToUuid : dictionary
        Mapping from Numerrin point label number to uuid


    """

    def __init__(self, name, mesh, pool):

        self.name = name
        self.pool = pool
        maps = self.pool.import_mesh(name, mesh)
        self._uuidToNumLabel = maps[0]
        self._numPointLabelToUuid = maps[1]
        self._numEdgeLabelToUuid = maps[2]
        self._numFaceLabelToUuid = maps[3]
        self._numCellLabelToUuid = maps[4]
        # point data
        for point in mesh.iter_points():
            self.update_point(point)

    def get_point(self, uuid):
        """Returns a point with a given uuid.

        Returns the point stored in the mesh
        identified by uuid. If such point do not
        exists an exception is raised.

        Parameters
        ----------
        uuid
            uuid of the desired point.

        Returns
        -------
        Point
            Mesh point identified by uuid

        Raises
        ------
        Exception
            If the point identified by uuid was not found

        """

        try:
            coords = numerrin.getnode(self.pool.ph, self.name,
                                      self._uuidToNumLabel[uuid])
            point = Point(coords, uuid)
            dataNames = ["Velocity", "Pressure"]
            for dataName in dataNames:
                try:
                    mDataName = self.name + dataName
                    if numerrin.gettype(self.pool.ph, mDataName) == "Function":
                        dataV = numerrin.getrealfunction(self.pool.ph,
                                                         mDataName)
                    else:
                        dataV = numerrin.getvariable(self.pool.ph, mDataName)
                    dkey = [key for key, value in numname.iteritems() if
                            value == dataName][0]
                    point.data[dkey] = dataV[self._uuidToNumLabel[uuid]]
                except:
                    pass

            return point
        except KeyError:
            error_str = "Trying to get an non-existing point with uuid: {}"
            raise ValueError(error_str.format(uuid))

    def get_edge(self, uuid):
        """Returns an edge with a given uuid.

        Returns the edge stored in the mesh
        identified by uuid. If such edge do not
        exists an exception is raised.

        Parameters
        ----------
        uuid
            uuid of the desired edge.

        Returns
        -------
        Edge
            Edge identified by uuid

        Raises
        ------
        Exception
            If the edge identified by uuid was not found

        """
        message = "Edges are not supported yet in Numerrin engine"
        raise NotImplementedError(message)

    def get_face(self, uuid):
        """Returns a face with a given uuid.

        Returns the face stored in the mesh
        identified by uuid. If such face do not
        exists an exception is raised.

        Parameters
        ----------
        uuid
            uuid of the desired face.

        Returns
        -------
        Face
            Face identified by uuid

        Raises
        ------
        Exception
            If the face identified by uuid was not found

        """

        try:
            pointLabels = self.pool.get_face_points(self.name,
                                                    self._uuidToNumLabel[uuid])
            puids = [self._numPointLabelToUuid[lbl] for lbl in pointLabels]
            face = Face(puids, uuid)
            try:
                blabel = self.pool.get_face_boundary_label(
                    self.name, self._uuidToNumLabel[uuid])
                face.data[CUBA.LABEL] = blabel
            except:
                pass
            return face
        except KeyError:
            error_str = "Trying to get an non-existing edge with uuid: {}"
            raise ValueError(error_str.format(uuid))

    def get_cell(self, uuid):
        """Returns a cell with a given uuid.

        Returns the cell stored in the mesh
        identified by uuid . If such cell do not
        exists an exception is raised.

        Parameters
        ----------
        uuid
            uuid of the desired cell.

        Returns
        -------
        Cell
            Cell with id identified by uuid

        Raises
        ------
        Exception
            If the cell identified by uuid was not found

        """

        try:
            pointLabels = numerrin.getelement(self.pool.ph, self.name,
                                              3, self._uuidToNumLabel[uuid],
                                              0)
            puids = [self._numPointLabelToUuid[lbl] for lbl in pointLabels]
            cell = Cell(puids, uuid)
            return cell

        except KeyError:
            error_str = "Trying to get an non-existing cell with uuid: {}"
            raise ValueError(error_str.format(uuid))

    def add_point(self, point):
        message = 'Point addition not supported yet'
        raise NotImplementedError(message)

    def add_edge(self, edge):
        message = 'Edge addition not supported yet'
        raise NotImplementedError(message)

    def add_face(self, face):
        message = 'Face addition not supported yet'
        raise NotImplementedError(message)

    def add_cell(self, cell):
        message = 'Cell addition not supported yet'
        raise NotImplementedError(message)

    def update_point(self, point):
        """ Updates the information of a point.

        Gets the mesh point identified by the same
        uuid as the provided point and updates its data
        with the one provided with the new point.

        Parameters
        ----------
        point : Point
            Point to be updated

        Raises
        ------
        KeyError
            If the point was not found in the mesh

        """

        if point.uid not in self._uuidToNumLabel:
            error_str = "Trying to update a non-existing point with uuid: "\
                + str(point.uid)
            raise KeyError(error_str)

        dataNames = ["Velocity", "Pressure"]
        for dataName in dataNames:
            vname = self.name + dataName
            vkey = [key for key, value in numname.iteritems() if
                    value == dataName][0]
            try:
                if vkey in point.data:
                    vdata = list(self.pool.get_variable(vname))
                    vdata[self._uuidToNumLabel[point.uid]] = point.data[vkey]
                    self.pool.modify_variable(vname, tuple(vdata))
            except:
                # create variable
                if vkey in point.data:
                    var = point.data[vkey]
                    if type(var) is tuple:
                        vdata = list([(0, 0, 0) for _ in self.iter_points()])
                    else:
                        vdata = list([0 for _ in self.iter_points()])

                    vdata[self._uuidToNumLabel[point.uid]] = point.data[vkey]
                    self.pool.put_variable(vname, tuple(vdata))

    def update_edge(self, edge):
        message = 'Edge update not supported yet'
        raise NotImplementedError(message)

    def update_face(self, face):
        message = 'Face update not supported yet'
        raise NotImplementedError(message)

    def update_cell(self, cell):
        message = 'Cell update not supported yet'
        raise NotImplementedError(message)

    def iter_points(self, point_uuids=None):
        """Returns an iterator over the selected points.

        Returns an iterator over the points with uuid in
        point_ids. If none of the ids in point_ids exists,
        an empty iterator is returned. If there is no ids
        inside point_ids, a iterator over all points of
        the mesh is returned instead.

        Parameters
        ----------
        point_uuids : list of uuids, optional
            uuids of the desired points, default empty

        Returns
        -------
        iter
            Iterator over the selected points

        """

        if point_uuids is None:
            pointCount = numerrin.meshsize(self.pool.ph, self.name)[0]
            for label in range(pointCount):
                yield self.get_point(self._numPointLabelToUuid[label])
        else:
            for uid in point_uuids:
                point = self.get_point(uid)
                yield point

    def iter_edges(self, edge_uuids=None):
        """Returns an iterator over the selected edges.

        Returns an iterator over the edges with uuid in
        cell_uuids. If none of the uuids in edge_uuids exists,
        an empty iterator is returned. If there is no uuids
        inside edge_uuids, a iterator over all edges of
        the mesh is returned instead.

        Parameters
        ----------
        edge_uuids : list of uuids, optional
            Uuids of the desired edge, default empty

        Returns
        -------
        iter
            Iterator over the selected edges

        """

        if edge_uuids is None:
            edgeCount = numerrin.meshsize(self.pool.ph, self.name)[1]
            for label in range(edgeCount):
                yield self.get_edge(self._numEdgeLabelToUuid[label])
        else:
            for uid in edge_uuids:
                edge = self.get_edge(uid)
                yield edge

    def iter_faces(self, face_uuids=None):
        """Returns an iterator over the selected faces.

        Returns an iterator over the faces with uuid in
        face_uuids. If none of the uuids in face_uuids exists,
        an empty iterator is returned. If there is no uuids
        inside face_uuids, a iterator over all faces of
        the mesh is returned instead.

        Parameters
        ----------
        face_uuids : list of uuids, optional
            Uuids of the desired face, default empty

        Returns
        -------
        iter
            Iterator over the selected faces

        """

        if face_uuids is None:
            faceCount = numerrin.meshsize(self.pool.ph, self.name)[2]
            for label in range(faceCount):
                yield self.get_face(self._numFaceLabelToUuid[label])
        else:
            for uid in face_uuids:
                face = self.get_face(uid)
                yield face

    def iter_cells(self, cell_uuids=None):
        """Returns an iterator over the selected cells.

        Returns an iterator over the cells with uuid in
        cell_uuids. If none of the uuids in cell_uuids exists,
        an empty iterator is returned. If there is no uuids
        inside cell_uuids, a iterator over all cells of
        the mesh is returned instead.

        Parameters
        ----------
        cell_uuids : list of uuids, optional
            Uuids of the desired cell, default empty

        Returns
        -------
        iter
            Iterator over the selected cells

        """

        if cell_uuids is None:
            cellCount = numerrin.meshsize(self.pool.ph, self.name)[3]
            for label in range(cellCount):
                yield self.get_cell(self._numCellLabelToUuid[label])
        else:
            for uid in cell_uuids:
                cell = self.get_cell(uid)
                yield cell

    def has_edges(self):
        """Check if the mesh has edges

        Returns
        -------
        bool
            True of there are edges inside the mesh,
            False otherwise

        """

        numberEdges = numerrin.meshsize(self.pool.ph, self.name)[1]
        return numberEdges > 0

    def has_faces(self):
        """Check if the mesh has faces

        Returns
        -------
        bool
            True of there are faces inside the mesh,
            False otherwise

        """
        numberFaces = numerrin.meshsize(self.pool.ph, self.name)[2]
        return numberFaces > 0

    def has_cells(self):
        """Check if the mesh has cells

        Returns
        -------
        bool
            True of there are cells inside the mesh,
            False otherwise

        """
        numberCells = numerrin.meshsize(self.pool.ph, self.name)[3]
        return numberCells > 0
