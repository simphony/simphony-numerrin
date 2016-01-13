"""Example to solve mixture model
"""

from simphony.core.cuba import CUBA

from simphony.engine import numerrin

wrapper = numerrin.Wrapper()
CUBAExt = numerrin.CUBAExt

name = 'dahl'

wrapper.CM[CUBA.NAME] = name

wrapper.CM_extensions[CUBAExt.GE] = (CUBAExt.INCOMPRESSIBLE,
                                     CUBAExt.LAMINAR_MODEL,
                                     CUBAExt.MIXTURE_MODEL)

wrapper.CM_extensions[CUBAExt.NUMBER_OF_CORES] = 4

wrapper.SP[CUBA.TIME_STEP] = 0.1
wrapper.SP[CUBA.NUMBER_OF_TIME_STEPS] = 1

wrapper.SP_extensions[CUBAExt.PHASE_LIST] = ('sludge', 'water')
wrapper.SP[CUBA.DENSITY] = {'sludge': 1900.0, 'water': 1000.0}
wrapper.SP[CUBA.DYNAMIC_VISCOSITY] = {'sludge': 0.01, 'water': 1e-3}
wrapper.SP_extensions[CUBAExt.STRESS_MODEL] = 'standard'
wrapper.SP_extensions[CUBAExt.RELATIVE_VELOCITY_MODEL] = 'simple'
wrapper.SP_extensions[CUBAExt.RELATIVE_VELOCITY_MODEL_COEFFS] =\
    {'V0': (0.0, -0.002, 0.0), 'a': 285.0, 'a1': 0.1, 'residualAlpha': 0}
wrapper.SP_extensions[CUBAExt.EXTERNAL_BODY_FORCE_MODEL] = 'gravitation'
wrapper.SP_extensions[CUBAExt.EXTERNAL_BODY_FORCE_MODEL_COEFFS] =\
    {'g': (0.0, -9.81, 0.0)}
wrapper.BC[CUBA.VELOCITY] = {'boundary0': ('fixedValue', (0.0191, 0, 0)),
                             'boundary1': 'zeroGradient',
                             'boundary2': ('fixedValue', (0, 0, 0)),
                             'boundary3': 'empty'}
wrapper.BC[CUBA.PRESSURE] = {'boundary0': 'zeroGradient',
                             'boundary1': ('fixedValue', 0),
                             'boundary2': 'zeroGradient',
                             'boundary3': 'empty'}
wrapper.BC[CUBA.VOLUME_FRACTION] = {'boundary0': ('fixedValue', 1),
                                    'boundary1': 'zeroGradient',
                                    'boundary2': 'zeroGradient',
                                    'boundary3': 'empty'}

corner_points=((0.0,0.0), (20.0e-3,0.0), (20.0e-3,1.0e-3), (0.0,1.0e-3))
extrude_length = 0.1e-3
nex = 10
ney = 4
nez = 1

## create mesh
#corner_points=((0.0,0.0), (8.65,0.0), (8.65,1.0), (0.0,1.0))
#extrude_length = 0.1
#nex = 33
#ney = 3
#nez = 1

numerrin.create_quad_mesh(name, wrapper, corner_points,
                 extrude_length, nex, ney, nez)

mesh_inside_wrapper = wrapper.get_dataset(name)


updated_points = []
for point in mesh_inside_wrapper.iter_points():
    point.data[CUBA.VOLUME_FRACTION] = 0.001
    point.data[CUBA.PRESSURE] = 0.0
    point.data[CUBA.VELOCITY] = [0.0191, 0.0, 0.0]
    updated_points.append(point)

mesh_inside_wrapper.update_points(updated_points)

wrapper.run()
print "Run up to time: ", mesh_inside_wrapper._time
