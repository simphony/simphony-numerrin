""" test_foamwrapper module

This module contains the unitary tests for the
mesh module functionalities

"""

import unittest
from numerrin_wrapper.numerrin_wrapper import NumerrinPool, NumerrinCode, NumerrinWrapper

class NumerrinWrapperTestCase(unittest.TestCase):
    """Test case for NumerrinWrapper class"""
    def setUp(self):
        """Creates dummy model to perform tests"""
        
    def test_meshRead(self):
        """Test mesh read from Numerrin to Simphony"""
        numerrin_wrapper = NumerrinWrapper()
        numerrin_wrapper.parseProgramFile("numerrin_wrapper/tests/mesh_extrusion.num")
        numerrin_wrapper.run()
        (simphonyMesh,numerrinMeshMap)=numerrin_wrapper.get_mesh("mesh")
        assert(sum(1 for _ in simphonyMesh.iter_points()) == 9261)
        assert(sum(1 for _ in simphonyMesh.iter_cells()) == 8000)
        assert(sum(1 for _ in simphonyMesh.iter_faces()) == 25200)

if __name__ == '__main__':
    unittest.main()
