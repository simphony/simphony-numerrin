""" test_numerrinwrapper module

This module contains the unitary tests for the
numerrin_wrapper module functionalities

"""

import unittest
import math

from simphony.cuds.mesh import Mesh, Face, Point, Cell
from simphony.core.cuba import CUBA

from numerrin_wrapper.numerrin_wrapper import Wrapper
from numerrin_wrapper.cuba_extension import CUBAExt
from numerrin_wrapper.mesh_utils import create_quad_mesh


class WrapperTestCase(unittest.TestCase):
    """Test case for Wrapper class"""
    def setUp(self):
        self.mesh = Mesh(name="mesh1")

        self.points = [
            Point(
                (0.0, 0.0, 0.0)),
            Point(
                (1.0, 0.0, 0.0)),
            Point(
                (1.0, 1.0, 0.0)),
            Point(
                (0.0, 1.0, 0.0)),
            Point(
                (0.0, 0.0, 1.0)),
            Point(
                (1.0, 0.0, 1.0)),
            Point(
                (1.0, 1.0, 1.0)),
            Point(
                (0.0, 1.0, 1.0))
        ]

        puids = self.mesh.add(self.points)

        self.faces = [
            Face([puids[0], puids[3], puids[7], puids[4]]),
            Face([puids[1], puids[2], puids[6], puids[5]]),
            Face([puids[0], puids[1], puids[5], puids[4]]),
            Face([puids[3], puids[2], puids[6], puids[7]]),
            Face([puids[0], puids[1], puids[2], puids[3]]),
            Face([puids[4], puids[5], puids[6], puids[7]])
        ]

        self.mesh.add(self.faces)

        self.cells = [
            Cell(puids)
        ]

        self.puids = puids

        self.mesh.add(self.cells)

    def test_add_dataset(self):
        """Test add_dataset method

        """

        wrapper = Wrapper()
        wrapper.add_dataset(self.mesh)
        self.assertEqual(sum(1 for _ in wrapper.iter_datasets()), 1)

    def test_remove_dataset(self):
        """Test remove_dataset method

        """

        wrapper = Wrapper()
        wrapper.add_dataset(self.mesh)
        wrapper.remove_dataset(self.mesh.name)
        with self.assertRaises(KeyError):
            wrapper.get_dataset(self.mesh.name)

    def test_get_dataset(self):
        """Test get_dataset method

        """

        wrapper = Wrapper()
        wrapper.add_dataset(self.mesh)
        mesh_inside_wrapper = wrapper.get_dataset(self.mesh.name)
        self.assertEqual(self.mesh.name, mesh_inside_wrapper.name)

        for point in self.mesh.iter(item_type=CUBA.POINT):
            point_w = mesh_inside_wrapper._get_point(point.uid)
            self.assertEqual(point.coordinates, point_w.coordinates)

        for face in self.mesh.iter(item_type=CUBA.FACE):
            face_w = mesh_inside_wrapper._get_face(face.uid)
            self.assertEqual(face.points, face_w.points)

        for cell in self.mesh.iter(item_type=CUBA.CELL):
            cell_w = mesh_inside_wrapper._get_cell(cell.uid)
            self.assertEqual(set(cell.points), set(cell_w.points))

    def test_iter_datasets(self):
        """Test iter_datsets method

        """

        wrapper = Wrapper()
        wrapper.add_dataset(self.mesh)
        mesh2 = self.mesh
        mesh2.name = "mesh2"
        wrapper.add_dataset(mesh2)

        self.assertEqual(sum(1 for _ in wrapper.iter_datasets()), 2)

    def test_multiple_meshes(self):
        """Test multiple meshes inside wrapper

        """

        wrapper = Wrapper()
        wrapper.add_dataset(self.mesh)
        mesh2 = self.mesh
        mesh2.name = "mesh2"
        wrapper.add_dataset(mesh2)
        mesh_inside_wrapper1 = wrapper.get_dataset(self.mesh.name)
        mesh_inside_wrapper2 = wrapper.get_dataset(mesh2.name)

        self.assertEqual(
            sum(1 for _ in mesh_inside_wrapper1.iter(item_type=CUBA.POINT)),
            sum(1 for _ in mesh_inside_wrapper2.iter(item_type=CUBA.POINT)))

    def test_run_time(self):
        """Test that field variable value is changed after
        consecutive calls of run method

        """

        wrapper = Wrapper()
        name = 'simplemesh'
        corner_points = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))
        extrude_length = 1
        nex = 3
        ney = 3
        nez = 1
        create_quad_mesh(name, wrapper, corner_points,
                         extrude_length, nex, ney, nez)

        wrapper.CM[CUBA.NAME] = name
        wrapper.CM_extensions[CUBAExt.GE] = (CUBAExt.INCOMPRESSIBLE,
                                             CUBAExt.LAMINAR_MODEL)
        wrapper.SP[CUBA.TIME_STEP] = 1
        wrapper.SP[CUBA.NUMBER_OF_TIME_STEPS] = 1
        wrapper.SP[CUBA.DENSITY] = 1.0
        wrapper.SP[CUBA.DYNAMIC_VISCOSITY] = 1.0
        wrapper.BC[CUBA.VELOCITY] = {'inflow': ('fixedValue', (0.1, 0, 0)),
                                     'outflow': 'zeroGradient',
                                     'walls': ('fixedValue', (0, 0, 0)),
                                     'frontAndBack': 'empty'}
        wrapper.BC[CUBA.PRESSURE] = {'inflow': 'zeroGradient',
                                     'outflow': ('fixedValue', 0),
                                     'walls': 'zeroGradient',
                                     'frontAndBack': 'empty'}

        mesh_inside_wrapper = wrapper.get_dataset(name)

        wrapper.run()

        # sum data pointwise
        old_vel = 0.0
        old_pres = 0.0
        for point in mesh_inside_wrapper.iter(item_type=CUBA.POINT):
            velo = point.data[CUBA.VELOCITY]
            old_vel += math.sqrt(velo[0]*velo[0] + velo[1]*velo[1] +
                                 velo[2]*velo[2])
            old_pres += point.data[CUBA.PRESSURE]

        wrapper.SP[CUBA.DENSITY] = 5.0

        wrapper.run()

        # sum data pointwise
        new_vel = 0.0
        new_pres = 0.0
        for point in mesh_inside_wrapper.iter(item_type=CUBA.POINT):
            velo = point.data[CUBA.VELOCITY]
            new_vel += math.sqrt(velo[0]*velo[0] + velo[1]*velo[1] +
                                 velo[2]*velo[2])
            new_pres += point.data[CUBA.PRESSURE]

        self.assertNotAlmostEqual(old_vel, new_vel, 5)
        self.assertNotAlmostEqual(old_pres, new_pres, 5)


if __name__ == '__main__':
    unittest.main()
