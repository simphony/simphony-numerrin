""" Mesh module

This module contains the implementation to store, access,
and modify a mesh and related data

"""
from simphony.cuds.abc_mesh import ABCMesh
from simphony.core.cuba import CUBA
from simphony.cuds.mesh import Point, Edge, Face, Cell

from .numerrin_templates import (numname, numvariables,
                                 solver_variables, variable_dimension)

import simphony.core.data_container as dc

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
        super(NumerrinMesh, self).__init__()
        self.name = name
        self.data = dc.DataContainer()
        self.pool = pool
        self._time = str(0)
        self._boundaries = {}
        maps = self.pool.import_mesh(name, mesh, self._boundaries)

        if hasattr(mesh, '_boundaries'):
            boundary_faces = {}
            for boundary in mesh._boundaries:
                boundary_faces[boundary] = []
                for fuid in mesh._boundaries[boundary]:
                    boundary_faces[boundary].append(maps[0][fuid])
            self.pool.add_boundaries(name, mesh._boundaries,
                                     boundary_faces)
            # this assumes that face uids are remained
            self._boundaries = mesh._boundaries

        self._uuidToNumLabel = maps[0]
        self._numPointLabelToUuid = maps[1]
        self._numEdgeLabelToUuid = maps[2]
        self._numFaceLabelToUuid = maps[3]
        self._numCellLabelToUuid = maps[4]
        # point data
        self.update_points(mesh.iter_points())

    def _get_point(self, uuid):
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
            for dkey in numvariables:
                dataName = numname[dkey]
                mDataName = self.name + dataName
                try:
                    if self.pool.variable_type(mDataName) == "Function":
                        dataV = self.pool.get_real_function(mDataName)
                    else:
                        dataV = self.pool.get_variable(mDataName)
                    point.data[dkey] = dataV[self._uuidToNumLabel[uuid]]
                except RuntimeError:
                    pass

            return point
        except KeyError:
            error_str = "Trying to get an non-existing point with uuid: {}"
            raise ValueError(error_str.format(uuid))

    def _get_edge(self, uuid):
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

        try:
            pointLabels = self.pool.get_edge_points(self.name,
                                                    self._uuidToNumLabel[uuid])
            puids = [self._numPointLabelToUuid[lbl] for lbl in pointLabels]
            return Edge(puids, uuid)
        except KeyError:
            error_str = "Trying to get an non-existing edge with uuid: {}"
            raise ValueError(error_str.format(uuid))

    def _get_face(self, uuid):
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
            return face
        except KeyError:
            error_str = "Trying to get an non-existing face with uuid: {}"
            raise ValueError(error_str.format(uuid))

    def _get_cell(self, uuid):
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
            pointLabels = self.pool.get_cell_points(self.name,
                                                    self._uuidToNumLabel[uuid])
            puids = [self._numPointLabelToUuid[lbl] for lbl in pointLabels]
            cell = Cell(puids, uuid)
            return cell

        except KeyError:
            error_str = "Trying to get an non-existing cell with uuid: {}"
            raise ValueError(error_str.format(uuid))

    def _add_points(self, points):
        message = 'Points addition not supported yet'
        raise NotImplementedError(message)

    def _add_edges(self, edges):
        message = 'Edges addition not supported yet'
        raise NotImplementedError(message)

    def _add_faces(self, faces):
        message = 'Faces addition not supported yet'
        raise NotImplementedError(message)

    def _add_cells(self, cells):
        message = 'Cells addition not supported yet'
        raise NotImplementedError(message)

    def init_point_variables(self, solver):
        for dkey in solver_variables[solver]:
            dataName = numname[dkey]
            vname = self.name + dataName
            try:
                self.pool.get_real_function(vname)
            except:
                # create variable if not in pool
                v_size = variable_dimension[dkey]
                # Lagrange 1 space
                space_name = vname + "LS1"
                domain_name = "omega"
                self.pool.create_space(space_name, domain_name,
                                       'Lagrange', 1)
                self.pool.create_realfunction(vname, space_name,
                                              v_size)

    def _update_points(self, points):
        """ Updates the information of a set of points.

        Gets the mesh point from set identified by the same
        uuid as the provided point and updates its data
        with the one provided with the new point.

        Parameters
        ----------
        points : iterable of Point
            Points to be updated

        Raises
        ------
        KeyError
            If the point was not found in the mesh

        """

        vdata = {}
        for point in points:
            if point.uid not in self._uuidToNumLabel:
                error_str =\
                    "Trying to update a non-existing point with uuid: "\
                    + str(point.uid)
                raise KeyError(error_str)
            label = self._uuidToNumLabel[point.uid]
            for dkey in numvariables:
                dataName = numname[dkey]
                vname = self.name + dataName
                if dkey in point.data:
                    try:
                        var = point.data[dkey]
                        if vname not in vdata:
                            point_list = self.pool.get_real_function(vname)
                            if type(var) is tuple or type(var) is list:
                                vdata[vname] =\
                                    list(list([value[i] for value in
                                               point_list])
                                         for i in range(len(var)))
                            else:
                                vdata[vname] =\
                                    list(list([value for value in
                                               point_list])
                                         for i in range(1))
                        if type(var) is tuple or type(var) is list:
                            for i in range(len(var)):
                                vdata[vname][i][label] =\
                                    float(var[i])
                        else:
                            vdata[vname][0][label] = float(var)
                    except:
                        # create variable if not in pool
                        var = point.data[dkey]
                        if type(var) is tuple or type(var) is list:
                            v_size = len(var)
                            vdata[vname] =\
                                list(list([0 for _ in self._iter_points()])
                                     for i in range(len(var)))
                            for i in range(len(var)):
                                vdata[vname][i][label] =\
                                    float(var[i])
                        else:
                            v_size = 1
                            vdata[vname] =\
                                list(list([0 for _ in self._iter_points()])
                                     for i in range(1))
                            vdata[vname][0][label] = float(point.data[dkey])
                        # Lagrange 1 space
                        space_name = vname + "LS1"
                        domain_name = "omega"
                        self.pool.create_space(space_name, domain_name,
                                               'Lagrange', 1)
                        self.pool.create_realfunction(vname, space_name,
                                                      v_size)

        for vname in vdata:
            for i in range(len(vdata[vname])):
                if len(vdata[vname]) > 1:
                    var_name = vname + "[" + str(i) + "][[:]]"
                else:
                    var_name = vname + "[[:]]"
                self.pool.modify_variable(var_name, tuple(vdata[vname][i]))

    def _update_edges(self, edges):
        message = 'Edges update not supported yet'
        raise NotImplementedError(message)

    def _update_faces(self, faces):
        message = 'Faces update not supported yet'
        raise NotImplementedError(message)

    def _update_cells(self, cells):
        message = 'Cells update not supported yet'
        raise NotImplementedError(message)

    def _iter_points(self, point_uuids=None):
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
            pointCount = self.pool.mesh_size(self.name)[0]
            for label in range(pointCount):
                yield self._get_point(self._numPointLabelToUuid[label])
        else:
            for uid in point_uuids:
                point = self._get_point(uid)
                yield point

    def _iter_edges(self, edge_uuids=None):
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
            edgeCount = self.pool.mesh_size(self.name)[1]
            for label in range(edgeCount):
                yield self._get_edge(self._numEdgeLabelToUuid[label])
        else:
            for uid in edge_uuids:
                edge = self._get_edge(uid)
                yield edge

    def _iter_faces(self, face_uuids=None):
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
            faceCount = self.pool.mesh_size(self.name)[2]
            for label in range(faceCount):
                yield self._get_face(self._numFaceLabelToUuid[label])
        else:
            for uid in face_uuids:
                face = self._get_face(uid)
                yield face

    def _iter_cells(self, cell_uuids=None):
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
            cellCount = self.pool.mesh_size(self.name)[3]
            for label in range(cellCount):
                yield self._get_cell(self._numCellLabelToUuid[label])
        else:
            for uid in cell_uuids:
                cell = self._get_cell(uid)
                yield cell

    def _has_edges(self):
        """Check if the mesh has edges

        Returns
        -------
        bool
            True of there are edges inside the mesh,
            False otherwise

        """

        numberEdges = self.pool.mesh_size(self.name)[1]
        return numberEdges > 0

    def _has_faces(self):
        """Check if the mesh has faces

        Returns
        -------
        bool
            True of there are faces inside the mesh,
            False otherwise

        """
        numberFaces = self.pool.mesh_size(self.name)[2]
        return numberFaces > 0

    def _has_cells(self):
        """Check if the mesh has cells

        Returns
        -------
        bool
            True of there are cells inside the mesh,
            False otherwise

        """
        numberCells = self.pool.mesh_size(self.name)[3]
        return numberCells > 0

    def count_of(self, item_type):
        """ Return the count of item_type in the container.

        Parameters
        ----------
        item_type : CUBA item
            The CUDSItem enum of the type of the items to return the count of.

        Returns
        -------
        count : int
            The number of items of item_type in the container.

        Raises
        ------
        ValueError :
            If the type of the item is not supported in the current
            container.

        """

        if item_type == CUBA.POINT:
            return self.pool.mesh_size(self.name)[0]
        elif item_type == CUBA.EDGE:
            return self.pool.mesh_size(self.name)[1]
        elif item_type == CUBA.FACE:
            return self.pool.mesh_size(self.name)[2]
        elif item_type == CUBA.CELL:
            return self.pool.mesh_size(self.name)[3]
        else:
            error_str = 'Item type {} not supported'
            raise ValueError(error_str.format(item_type))
