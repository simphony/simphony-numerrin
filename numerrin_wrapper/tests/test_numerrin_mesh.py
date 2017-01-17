""" test_numerrin_mesh module

This module contains the unitary tests for the
numerrin_mesh module functionalities

"""

import unittest

from simphony.cuds.mesh import Mesh, Face, Point, Cell, Edge
from simphony.core.cuba import CUBA
from simphony.core.data_container import DataContainer

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
        self.puids = puids

        self.faces = [
            Face([puids[0], puids[3], puids[7], puids[4]]),
            Face([puids[1], puids[2], puids[6], puids[5]]),
            Face([puids[0], puids[1], puids[5], puids[4]]),
            Face([puids[3], puids[2], puids[6], puids[7]]),
            Face([puids[0], puids[1], puids[2], puids[3]]),
            Face([puids[4], puids[5], puids[6], puids[7]])
        ]

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
        point_f = num_mesh.get(point.uid)
        self.assertEqual(point.coordinates, point_f.coordinates)
        self.assertEqual(point.data[CUBA.PRESSURE],
                         point_f.data[CUBA.PRESSURE])
        self.assertEqual(point.data[CUBA.VELOCITY],
                         point_f.data[CUBA.VELOCITY])

    def test_get_edge(self):
        """Test get_edge method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        uid = num_mesh._numEdgeLabelToUuid[0]
        edge = num_mesh.get(uid)
        self.assertEqual(edge.uid, uid)

    def test_get_face(self):
        """Test get_face method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        face = self.faces[4]
        face_f = num_mesh.get(face.uid)
        self.assertEqual(face.points, face_f.points)

    def test_get_cell(self):
        """Test get_cell method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        cell = self.cells[0]
        cell_f = num_mesh.get(cell.uid)
        self.assertEqual(set(cell.points), set(cell_f.points))

    def test_add_points(self):
        """Test add_points method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        with self.assertRaises(NotImplementedError):
            num_mesh.add(self.points)

    def test_add_edges(self):
        """Test add_edges method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        with self.assertRaises(NotImplementedError):
            num_mesh.add([Edge([self.puids[0], self.puids[3]])])

    def test_add_faces(self):
        """Test add_faces method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        with self.assertRaises(NotImplementedError):
            num_mesh.add(self.faces)

    def test_add_cells(self):
        """Test add_cells method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        with self.assertRaises(NotImplementedError):
            num_mesh.add(self.cells)

    def test_update_points(self):
        """Test update_points method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        points = self.points
        points[0].data[CUBA.VELOCITY] = (2, 1, 3)
        num_mesh.update(points)
        point_f = num_mesh.get(points[0].uid)
        self.assertIsInstance(point_f.data, DataContainer)
        self.assertEqual(points[0].data, point_f.data)

    def test_update_edges(self):
        """Test update_edges method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        with self.assertRaises(NotImplementedError):
            num_mesh.update([Edge([self.puids, self.puids[3]])])

    def test_update_faces(self):
        """Test update_faces method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        with self.assertRaises(NotImplementedError):
            num_mesh.update(self.faces)

    def test_iter_edges(self):
        """Test iter_edges method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        self.assertEqual(sum(1 for _ in num_mesh.iter(item_type=CUBA.EDGE)),
                         num_mesh.count_of(CUBA.EDGE))

    def test_iter_faces(self):
        """Test iter_faces method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        for face_f in num_mesh.iter(item_type=CUBA.FACE):
            face = self.mesh.get(face_f.uid)
            self.assertEqual(face.points, face_f.points)

    def test_iter_points(self):
        """Test iter_points method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        for point_f in num_mesh.iter(item_type=CUBA.POINT):
            point = self.mesh.get(point_f.uid)
            self.assertEqual(point.data[CUBA.VELOCITY],
                             point_f.data[CUBA.VELOCITY])
            self.assertEqual(point.data[CUBA.PRESSURE],
                             point_f.data[CUBA.PRESSURE])

    def test_has_faces(self):
        """Test has_faces method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        self.assertTrue(num_mesh.has_type(CUBA.FACE))

    def test_has_cells(self):
        """Test has_cells method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)
        self.assertTrue(num_mesh.has_type(CUBA.CELL))

    def test_count_of(self):
        """Test count_of method

        """

        num_mesh = NumerrinMesh('test_mesh', self.mesh, self.pool)

        item_type = CUBA.POINT
        self.assertEqual(num_mesh.count_of(item_type),
                         self.mesh.count_of(item_type))

        item_type = CUBA.EDGE
        self.assertEqual(num_mesh.count_of(item_type), 12)

        item_type = CUBA.FACE
        self.assertEqual(num_mesh.count_of(item_type),
                         self.mesh.count_of(item_type))

        item_type = CUBA.CELL
        self.assertEqual(num_mesh.count_of(item_type),
                         self.mesh.count_of(item_type))


if __name__ == '__main__':
    unittest.main()
