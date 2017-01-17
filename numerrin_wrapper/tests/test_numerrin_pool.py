""" test_numerrin_pool module

This module contains the unitary tests for the
numerrin_pool module functionalities

"""

import unittest

from simphony.cuds.mesh import Mesh, Face, Point, Cell, Edge
from simphony.core.cuba import CUBA
from simphony.core.data_container import DataContainer

from numerrin_wrapper.numerrin_pool import NumerrinPool
from numerrin_wrapper.numerrin_templates import liccode

import numerrin


class NumerrinPoolTestCase(unittest.TestCase):
    """Test case for NumerrinPool class"""
    def setUp(self):
        self.mesh = Mesh(name="mesh1")
        numerrin.initlocal("", "PYNUMERRIN_LICENSE", liccode)
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

        puids = self.mesh.add(self.points)

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

        self.edge = Edge([puids[0], puids[3]])

        self.mesh.add(self.faces)

        self.cells = [
            Cell(puids)
        ]

        self.puids = puids

        self.mesh.add(self.cells)

        self.variablename = self.mesh.name + "Velocity"
        self.variable = tuple([(0.0, 0.0, 0.0) for _ in self.points])

        self.boundaries = {}
        for i in range(6):
            self.boundaries['boundary'+str(i)] = [self.faces[i].uid]

    def test_import_mesh(self):
        """Test import_mesh method

        """

        pool = NumerrinPool()
        pool.import_mesh(self.mesh.name, self.mesh, self.boundaries)
        self.assertEqual(numerrin.meshsize(pool.ph, self.mesh.name)[0],
                         len(self.points))
        self.assertEqual(numerrin.meshsize(pool.ph, self.mesh.name)[2],
                         len(self.faces))
        self.assertEqual(numerrin.meshsize(pool.ph, self.mesh.name)[3],
                         len(self.cells))

    def test_clear(self):
        """Test clear method

        """

        pool = NumerrinPool()
        pool.import_mesh(self.mesh.name, self.mesh, self.boundaries)
        pool.clear()
        with self.assertRaises(RuntimeError):
            numerrin.meshsize(pool.ph, self.mesh.name)

    def test_variable_type(self):
        """Test variable_type method

        """

        pool = NumerrinPool()
        pool.import_mesh(self.mesh.name, self.mesh, self.boundaries)
        self.assertEqual(pool.variable_type(self.mesh.name), "Mesh")

    def test_variable_rank(self):
        """Test variable_rank method

        """

        pool = NumerrinPool()
        pool.put_variable(self.variablename, self.variable)
        self.assertEqual(pool.variable_rank(self.variablename), 2)

    def test_get_variable(self):
        """Test get_variable method

        """

        pool = NumerrinPool()
        pool.put_variable(self.variablename, self.variable)
        self.assertEqual(pool.get_variable(self.variablename), self.variable)

    def test_put_variable(self):
        """Test put_variable method

        """

        pool = NumerrinPool()
        pool.put_variable(self.variablename, self.variable)
        self.assertEqual(pool.get_variable(self.variablename), self.variable)

    def test_modify_variable(self):
        """Test modify_variable method

        """

        pool = NumerrinPool()
        pool.put_variable(self.variablename, self.variable)
        oldvar = pool.get_variable(self.variablename)
        modvar = tuple([(10.0, 10.0, 10.0) for _ in oldvar])
        pool.modify_variable(self.variablename, modvar)
        newvar = pool.get_variable(self.variablename)
        self.assertNotEqual(oldvar, newvar)

    def test_delete_mesh_and_variables(self):
        """Test delete_mesh_and_variables method

        """

        pool = NumerrinPool()
        pool.import_mesh(self.mesh.name, self.mesh, self.boundaries)
        pool.put_variable(self.variablename, self.variable)
        pool.delete_mesh_and_variables(self.mesh.name)

        with self.assertRaises(RuntimeError):
            pool.get_variable(self.variablename)
        with self.assertRaises(RuntimeError):
            numerrin.meshsize(pool.ph, self.mesh.name)

    def test_export_mesh(self):
        """Test export_mesh method

        """

        pool = NumerrinPool()
        pool.import_mesh(self.mesh.name, self.mesh, self.boundaries)
        boundary_names = self.boundaries.keys()
        (smesh, mmap, boundaries) = pool.export_mesh(self.mesh.name,
                                                     boundary_names)
        self.assertEqual(sum(1 for _ in smesh.iter(item_type=CUBA.POINT)),
                         sum(1 for _ in self.mesh.iter(item_type=CUBA.POINT)))
        self.assertEqual(sum(1 for _ in smesh.iter(item_type=CUBA.FACE)),
                         sum(1 for _ in self.mesh.iter(item_type=CUBA.FACE)))
        self.assertEqual(sum(1 for _ in smesh.iter(item_type=CUBA.CELL)),
                         sum(1 for _ in self.mesh.iter(item_type=CUBA.CELL)))
        self.assertEqual(set([p.coordinates
                              for p in smesh.iter(item_type=CUBA.POINT)]),
                         set([p.coordinates
                              for p in self.mesh.iter(item_type=CUBA.POINT)]))
        self.assertEqual(boundaries.keys(), boundary_names)


if __name__ == '__main__':
    unittest.main()
