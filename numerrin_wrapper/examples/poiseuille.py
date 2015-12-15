"""Example to solve 2D poiseuille flow

"""

from simphony.core.cuba import CUBA
from simphony.engine import numerrin
import os


wrapper = numerrin.NumerrinWrapper()
CUBAExt = numerrin.CUBAExt

name = 'poiseuille'

wrapper.CM[CUBA.NAME] = name

wrapper.CM_extensions[CUBAExt.GE] = (CUBAExt.INCOMPRESSIBLE,
                                     CUBAExt.LAMINAR_MODEL)
wrapper.SP[CUBA.TIME_STEP] = 1
wrapper.SP[CUBA.NUMBER_OF_TIME_STEPS] = 10
wrapper.SP[CUBA.DENSITY] = 1.0
wrapper.SP[CUBA.DYNAMIC_VISCOSITY] = 1.0

# this is just an example. It is not enough for general setting of BC's
wrapper.BC[CUBA.VELOCITY] = {'boundary0': (0.1, 0, 0),
                             'boundary1': 'zeroGradient',
                             'boundary2': (0, 0, 0),
                             'boundary3': 'empty'}
wrapper.BC[CUBA.PRESSURE] = {'boundary0': 'zeroGradient',
                             'boundary1': 0,
                             'boundary2': 'zeroGradient',
                             'boundary3': 'empty'}

corner_points=((0.0,0.0), (30.0e-3,0.0), (30.0e-3,5.0e-3), (0.0,5.0e-3))
extrude_length = 0.1e-3
nex = 30
ney = 4
nez = 1
numerrin.create_quad_mesh(name, wrapper, corner_points,
                          extrude_length, nex, ney, nez)
mesh_inside_wrapper = wrapper.get_dataset(name)

wrapper.run()
print "Steps taken ", mesh_inside_wrapper._time
