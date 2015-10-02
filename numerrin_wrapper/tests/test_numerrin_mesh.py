""" test_numerrin_mesh module

This module contains the unitary tests for the
numerrin_mesh module functionalities

"""

import unittest

from simphony.cuds.mesh import Mesh, Face, Point, Cell, Edge
from simphony.core.cuba import CUBA
from simphony.core.data_container import DataContainer
from simphony.core.cuds_item import CUDSItem

from numerrin_wrapper.numerrin_mesh import NumerrinMesh
from numerrin_wrapper.numerrin_pool import NumerrinPool
from numerrin_wrapper.numerrin_templates import liccode

import numerrin


class NumerrinMeshTestCase(unittest.TestCase):
    """Test case for NumerrinMesh class"""

    def setUp(self):
        self.mesh = Mesh(name="mesh1")
        numerrin.initlocal("", "PYNUMERRIN_LICENSE", liccode)
        self.pool = NumerrinPool()
        self.points = [
            Point(
                (0.0, 0.0, 0.0),
                data=DataContainer({CUBA.VELOCITY: (1, 0, 0),
                                    CUBA.PRESSURE: 4.0})),
            Point(
                (1.0, 0.0, 0.0),
                data=DataContainer({CUBA.VELOCITY: (1, 0, 0),
                                    CUBA.PRESSURE: 4.0})),
            Point(
                (1.0, 1.0, 0.0),
                data=DataContainer({CUBA.VELOCITY: (1, 0, 0),
                                    CUBA.PRESSURE: 4.0})),
            Point(
                (0.0, 1.0, 0.0),
                data=DataContainer({CUBA.VELOCITY: (1, 0, 0),
                                    CUBA.PRESSURE: 4.0})),
            Point(
                (0.0, 0.0, 1.0),
                data=DataContainer({CUBA.VELOCITY: (1, 0, 0),
                                    CUBA.PRESSURE: 4.0})),
            Point(
                (1.0, 0.0, 1.0),
                data=DataContainer({CUBA.VELOCITY: (1, 0, 0),
                                    CUBA.PRESSURE: 4.0})),
            Point(
                (1.0, 1.0, 1.0),
                data=DataContainer({CUBA.VELOCITY: (1, 0, 0),
                                    CUBA.PRESSURE: 4.0})),
            Point(
                (0.0, 1.0, 1.0),
                data=DataContainer({CUBA.VELOCITY: (1, 0, 0),
                                    CUBA.PRESSURE: 4.0}))
        ]

        puids = self.mesh.add_points(self.points)

        self.faces = [
            Face([puids[0], puids[3], puids[7], puids[4]],
                 data=DataContainer({CUBA.LABEL: 0})),
            Face([puids[1], puids[2], puids[6], puids[5]],
                 data=DataContainer({CUBA.LABEL: 1})),
            Face([puids[0], puids[1], puids[5], puids[4]],
                 data=DataContainer({CUBA.LABEL: 2})),
            Face([puids[3], puids[2], puids[6], puids[7]],
                 data=DataContainer({CUBA.LABEL: 3})),
            Face([puids[0], puids[1], puids[2], puids[3]],
                 data=DataContainer({CUBA.LABEL: 4})),
            Face([puids[4], puids[5], puids[6], puids[7]],
                 data=DataContainer({CUBA.LABEL: 5}))

        ]

        self.edges = [Edge([puids[0], puids[3]])]

        self.mesh.add_faces(self.faces)

        self.cells = [
            Cell(puids)
        ]

        self.puids = puids

        self.mesh.add_cells(self.cells)

    def test_get_point(self):
        """Test get_point method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        point = self.points[4]
        point_f = num_mesh.get_point(point.uid)
        self.assertEqual(point.coordinates, point_f.coordinates)
        self.assertEqual(point.data[CUBA.PRESSURE],
                         point_f.data[CUBA.PRESSURE])
        self.assertEqual(point.data[CUBA.VELOCITY],
                         point_f.data[CUBA.VELOCITY])

    def test_get_edge(self):
        """Test get_edge method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        with self.assertRaises(NotImplementedError):
            num_mesh.get_edge(self.edges[0])

    def test_get_face(self):
        """Test get_face method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        face = self.faces[4]
        face_f = num_mesh.get_face(face.uid)
        self.assertEqual(face.points, face_f.points)

    def test_get_cell(self):
        """Test get_cell method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        cell = self.cells[0]
        cell_f = num_mesh.get_cell(cell.uid)
        self.assertEqual(set(cell.points), set(cell_f.points))

    def test_add_points(self):
        """Test add_points method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        with self.assertRaises(NotImplementedError):
            num_mesh.add_points(self.points)

    def test_add_edges(self):
        """Test add_edges method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        with self.assertRaises(NotImplementedError):
            num_mesh.add_edges(self.edges)

    def test_add_faces(self):
        """Test add_faces method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        with self.assertRaises(NotImplementedError):
            num_mesh.add_faces(self.faces)

    def test_add_cells(self):
        """Test add_cells method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        with self.assertRaises(NotImplementedError):
            num_mesh.add_cells(self.cells)

    def test_update_points(self):
        """Test update_points method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        points = self.points
        points[0].data[CUBA.VELOCITY] = (2, 1, 3)
        num_mesh.update_points(points)
        point_f = num_mesh.get_point(points[0].uid)
        self.assertIsInstance(point_f.data, DataContainer)
        self.assertEqual(points[0].data, point_f.data)

    def test_update_edges(self):
        """Test update_edges method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        with self.assertRaises(NotImplementedError):
            num_mesh.update_edges(self.edges)

    def test_update_faces(self):
        """Test update_faces method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        with self.assertRaises(NotImplementedError):
            num_mesh.update_faces(self.faces)

    def test_iter_edges(self):
        """Test iter_edges method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        self.assertEqual(sum(1 for _ in num_mesh.iter_edges()), 0)

    def test_iter_faces(self):
        """Test iter_faces method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        for face_f in num_mesh.iter_faces():
            face = self.mesh.get_face(face_f.uid)
            self.assertEqual(face.data[CUBA.LABEL],
                             face_f.data[CUBA.LABEL])

    def test_iter_points(self):
        """Test iter_points method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        for point_f in num_mesh.iter_points():
            point = self.mesh.get_point(point_f.uid)
            self.assertEqual(point.data[CUBA.VELOCITY],
                             point_f.data[CUBA.VELOCITY])
            self.assertEqual(point.data[CUBA.PRESSURE],
                             point_f.data[CUBA.PRESSURE])

    def test_has_faces(self):
        """Test has_faces method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        self.assertTrue(num_mesh.has_faces())

    def test_has_cells(self):
        """Test has_cells method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        self.assertTrue(num_mesh.has_cells())

    def test_count_of(self):
        """Test count_of method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)

        item_type = CUDSItem.POINT
        self.assertEqual(num_mesh.count_of(item_type),
                         self.mesh.count_of(item_type))

        item_type = CUDSItem.EDGE
        self.assertEqual(num_mesh.count_of(item_type),
                         self.mesh.count_of(item_type))

        item_type = CUDSItem.FACE
        self.assertEqual(num_mesh.count_of(item_type),
                         self.mesh.count_of(item_type))

        item_type = CUDSItem.CELL
        self.assertEqual(num_mesh.count_of(item_type),
                         self.mesh.count_of(item_type))

if __name__ == '__main__':
    unittest.main()
