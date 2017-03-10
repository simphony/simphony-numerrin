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
from numerrin_wrapper.numerrin_templates import (liccode, numname,
                                                 get_numerrin_solver)
from numerrin_wrapper.numerrin_mesh import NumerrinMesh

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
        SPExt = DataContainer()
        BC = DataContainer()
        CMExt = {}
        mesh_name = "Mesh"
        CM[CUBA.NAME] = mesh_name
        CMExt[CUBAExt.GE] = (CUBAExt.INCOMPRESSIBLE,
                             CUBAExt.LAMINAR_MODEL)
        SP[CUBA.TIME_STEP] = 1
        SP[CUBA.NUMBER_OF_TIME_STEPS] = 2
        SP[CUBA.DENSITY] = 1.0
        SP[CUBA.DYNAMIC_VISCOSITY] = 1.0
        BC[CUBA.VELOCITY] = {'boundary0': ('fixedValue', (0.1, 0, 0))}
        BC[CUBA.PRESSURE] = {'boundary0': 'zeroGradient'}

        boundary_names = ['boundary0', 'boundary1', 'boundary2', 'boundary3']

       
        corner_points = ((0.0, 0.0), (20.0e-3, 0.0), (20.0e-3, 1.0e-3),
                 (0.0, 1.0e-3))
        mesh_code = """
pts={%f,%f;%f,%f;%f,%f;%f,%f}
Quadmesh(pts,{%i,%i},{0,0,0,0},{1.0,1.0,-1.0,-1.0},mesh2d,domains2d)
dvec[0:1]=0.0
dvec[2]=%f
Extrude(mesh2d,domains2d,dvec,%i,0,0.0,%s,domains)
omega->domains[0]
%s->domains[6]
%s->domains[4]
%s=Union(domains[3],domains[5])
%s=Union(domains[1],domains[2])
""" % (corner_points[0][0], corner_points[0][1],
       corner_points[1][0], corner_points[1][1],
       corner_points[2][0], corner_points[2][1],
       corner_points[3][0], corner_points[3][1],
       1, 1, 1.0, 1, mesh_name, mesh_name+boundary_names[0],
       mesh_name+boundary_names[1],  mesh_name+boundary_names[2],
       mesh_name+boundary_names[3])

        
        self.code.parse_string(mesh_code)
        self.code.execute(1)
        smesh, _, boundaries = self.pool.export_mesh('simmesh', mesh_name,
                                              boundary_names)
        nummesh = NumerrinMesh(mesh_name, smesh, self.pool)
        uidmap = nummesh._uuidToNumLabel
        boundary_faces = {}
        for boundary in boundaries:
            boundary_faces[boundary] = []
            for fuid in boundaries[boundary]:
                boundary_faces[boundary].append(uidmap[fuid])
        nummesh.pool.add_boundaries(mesh_name, boundaries,
                                 boundary_faces)
        nummesh._boundaries = boundaries

        for key in SP:
            self.pool.put_variable(numname[key], SP[key])

        nummesh.init_point_variables(get_numerrin_solver(CMExt))

        codestring = self.code.generate_init_code(CM, SP, SPExt, BC, CMExt)
        codestring +=self.code.generate_code(CM, SP, SPExt, BC, CMExt, nummesh)

        self.code.parse_string(codestring)

        self.assertEqual(self.pool.variable_type(mesh_name), "Mesh")
        self.assertEqual(self.pool.variable_type(numname[CUBA.TIME_STEP]),
                         "Integer")
        self.assertEqual(self.pool.variable_type(numname[CUBA.DENSITY]),
                         "Real")


if __name__ == '__main__':
    unittest.main()
