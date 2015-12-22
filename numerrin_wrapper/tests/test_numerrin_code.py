""" test_numerrin_code module

This module contains the unitary tests for the
numerrin_code module functionalities

"""

import unittest
import os

from simphony.cuds.mesh import Mesh, Face, Point, Cell
from simphony.core.cuba import CUBA
from simphony.core.data_container import DataContainer

from numerrin_wrapper.numerrin_pool import NumerrinPool
from numerrin_wrapper.numerrin_code import NumerrinCode
from numerrin_wrapper.numerrin_templates import liccode, numname
from numerrin_wrapper.cuba_extension import CUBAExt

import numerrin


class NumerrinCodeTestCase(unittest.TestCase):
    """Test case for NumerrinCode class"""
    def setUp(self):
        numerrin.initlocal("", "PYNUMERRIN_LICENSE", liccode)
        self.pool = NumerrinPool()
        self.code = NumerrinCode(self.pool.ph)
        self.codestring = "a = 10.0\n"
        self.errorcodestring = "a = 10/b\n"
        self.exceptionstring = "Exception(\"Exception\")\n"
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

        self.mesh.add_faces(self.faces)

        self.cells = [
            Cell(puids)
        ]

        self.puids = puids

        self.mesh.add_cells(self.cells)

    def test_parse_file(self):
        """Test parse_file method

        """
        codefile = 'test.num'
        with open(codefile, 'w') as f:
            f.write(self.codestring)
        self.code.parse_file(codefile)
        os.remove(codefile)

    def test_parse_string(self):
        """Test parse_string method

        """
        self.code.parse_string(self.codestring)
        with self.assertRaises(RuntimeError):
            self.code.parse_string(self.errorcodestring)

    def test_execute(self):
        """Test execute method

        """
        self.code.parse_string(self.codestring)
        self.code.execute(1)

    def test_clear(self):
        """Test clear method

        """

        self.code.parse_string(self.exceptionstring)
        with self.assertRaises(RuntimeError):
            self.code.execute(1)
        self.code.clear()
        self.code.execute(1)

    def test_generate_code(self):
        """Test generate_init_code and generate_code method

        """
        CM = DataContainer()
        SP = DataContainer()
        BC = DataContainer()
        CMExt = {}
        CM[CUBA.NAME] = self.mesh.name
        CMExt[CUBAExt.GE] = (CUBAExt.INCOMPRESSIBLE,
                             CUBAExt.LAMINAR_MODEL)
        SP[CUBA.TIME_STEP] = 1
        SP[CUBA.NUMBER_OF_TIME_STEPS] = 2
        SP[CUBA.DENSITY] = 1.0
        SP[CUBA.DYNAMIC_VISCOSITY] = 1.0
        BC[CUBA.VELOCITY] = {'boundary0': (0.1, 0, 0)}
        BC[CUBA.PRESSURE] = {'boundary0': 'zeroGradient'}

        self.pool.import_mesh(self.mesh.name, self.mesh)
        for key in SP:
            self.pool.put_variable(numname[key], SP[key])

        codestring = self.code.generate_init_code(CM, SP, BC, CMExt) +\
                     self.code.generate_code(CM, SP, BC, CMExt)

        self.code.parse_string(codestring)

        self.assertEqual(self.pool.variable_type(self.mesh.name), "Mesh")
        self.assertEqual(self.pool.variable_type(numname[CUBA.TIME_STEP]),
                         "Integer")
        self.assertEqual(self.pool.variable_type(numname[CUBA.DENSITY]),
                         "Real")


if __name__ == '__main__':
    unittest.main()
