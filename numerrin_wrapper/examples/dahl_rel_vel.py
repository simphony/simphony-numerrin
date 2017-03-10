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

wrapper.CM_extensions[CUBAExt.NUMBER_OF_CORES] = 1

wrapper.SP[CUBA.TIME_STEP] = 0.1
wrapper.SP[CUBA.NUMBER_OF_TIME_STEPS] = 1

wrapper.SP_extensions[CUBAExt.PHASE_LIST] = ('sludge', 'water')
wrapper.SP[CUBA.DENSITY] = {'sludge': 1900.0, 'water': 1000.0}
wrapper.SP[CUBA.DYNAMIC_VISCOSITY] = {'sludge': 0.01, 'water': 1e-3}
wrapper.SP_extensions[CUBAExt.VISCOSITY_MODEL] =\
    {'sludge': 'BinghamPlastic', 'water': 'Newtonian'}
wrapper.SP_extensions[CUBAExt.VISCOSITY_MODEL_COEFFS] =\
    {'BinghamPlastic': {'coeff': 0.00023143, 'exponent': 179.26,
                        'BinghamCoeff': 0.0005966, 'BinghamExponent': 1050.8,
                        'BinghamOffset': 0, 'muMax': 10}}
wrapper.SP_extensions[CUBAExt.STRESS_MODEL] = 'standard'
wrapper.SP_extensions[CUBAExt.RELATIVE_VELOCITY_MODEL] = 'fromMesoscale'
wrapper.SP_extensions[CUBAExt.EXTERNAL_BODY_FORCE_MODEL] = 'gravitation'
wrapper.SP_extensions[CUBAExt.EXTERNAL_BODY_FORCE_MODEL_COEFFS] =\
    {'g': (0.0, -9.81, 0.0)}
wrapper.BC[CUBA.VELOCITY] = {'boundary0': ('fixedValue', (0.0191, 0, 0)),
                             'boundary1': ('pressureIOVelocity', (0, 0, 0)),
                             'boundary2': ('fixedValue', (0, 0, 0)),
                             'boundary3': ('fixedValue', (0, 0, 0)),
                             'boundary4': 'slip',
                             'boundary5': 'empty'}
# CUBA.CONCENTRATION is used for dynamic pressure while not in CUBA keys
wrapper.BC[CUBA.CONCENTRATION] = {'boundary0': 'fixedFluxPressure',
                                  'boundary1': ('fixedValue', 0),
                                  'boundary2': 'fixedFluxPressure',
                                  'boundary3': 'fixedFluxPressure',
                                  'boundary4': 'fixedFluxPressure',
                                  'boundary5': 'empty'}

wrapper.BC[CUBA.VOLUME_FRACTION] = {'boundary0': ('fixedValue', 0.001),
                                    'boundary1': ('inletOutlet', 0.001),
                                    'boundary2': 'zeroGradient',
                                    'boundary3': 'zeroGradient',
                                    'boundary4': 'zeroGradient',
                                    'boundary5': 'empty'}

# create mesh
corner_points = ((0.0, 0.0), (8.65, 0.0), (8.65, 1.0), (0.0, 1.0))
extrude_length = 0.1
nex = 33
ney = 3
nez = 1
mesh = numerrin.create_quad_mesh(name, corner_points,
                                 extrude_length, nex, ney, nez)
wrapper.add_dataset(mesh)

mesh_inside_wrapper = wrapper.get_dataset(name)


updated_points = []
for point in mesh_inside_wrapper.iter(item_type=CUBA.POINT):
    point.data[CUBA.VOLUME_FRACTION] = 0.001
    point.data[CUBA.PRESSURE] = 0.0
    point.data[CUBA.VELOCITY] = [0.0191, 0.0, 0.0]
    updated_points.append(point)

mesh_inside_wrapper.update(updated_points)

wrapper.run()

print "Update relative velocity"

V0 = [0.0, -0.002, 0.0]
a = 285.0

updated_points = []
for point in mesh_inside_wrapper.iter(item_type=CUBA.POINT):
    alphad = point.data[CUBA.VOLUME_FRACTION]
    vdj = [V*pow(10.0, -a*max(alphad, 0.0)) for V in V0]
    point.data[CUBA.ANGULAR_VELOCITY] = vdj
    updated_points.append(point)

mesh_inside_wrapper.update(updated_points)

print "Solve with updated relative velocity"
wrapper.run()
