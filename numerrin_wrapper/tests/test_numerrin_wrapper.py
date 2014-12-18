""" test_foamwrapper module

This module contains the unitary tests for the
mesh module functionalities

"""

import unittest
from foam_wrapper.model import Model
from numerrin_wrapper.numerrin_wrapper import NumerrinPool, NumerrinCode, NumerrinWrapper

class NumerrinWrapperTestCase(unittest.TestCase):
    """Test case for NumerrinWrapper class"""
    def setUp(self):
        """Creates dummy model to perform tests"""
        self.model = Model(1)

        
    def test_meshRead(self):
        """Test mesh read from Numerrin to Simphony"""
        numerrin_wrapper = NumerrinWrapper(self.model)
        numerrin_wrapper.setProgramFile("numerrin_wrapper/tests/mesh_extrusion.num")
        numerrin_wrapper.run()
        simphonyMesh=numerrin_wrapper.exportMesh()
        print "Number of mesh points: ",sum(1 for _ in simphonyMesh.iter_points())
        print "Number of mesh cells : ",sum(1 for _ in simphonyMesh.iter_cells())
        print "Number of mesh faces : ",sum(1 for _ in simphonyMesh.iter_faces())



if __name__ == '__main__':
    unittest.main()
