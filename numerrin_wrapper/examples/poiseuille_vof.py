"""Example to solve 2D 2 -phase poiseuille flow

"""

from simphony.core.cuba import CUBA

from simphony.engine import numerrin

wrapper = numerrin.Wrapper()
CUBAExt = numerrin.CUBAExt

path = '.'
name = 'poiseuille_vof'

wrapper.CM[CUBA.NAME] = name

wrapper.CM_extensions[CUBAExt.GE] = (CUBAExt.INCOMPRESSIBLE,
                                     CUBAExt.LAMINAR_MODEL,
                                     CUBAExt.VOF_MODEL)
wrapper.CM_extensions[CUBAExt.NUMBER_OF_CORES] = 4

wrapper.SP[CUBA.TIME_STEP] = 0.001
wrapper.SP[CUBA.NUMBER_OF_TIME_STEPS] = 1

wrapper.SP_extensions[CUBAExt.PHASE_LIST] = ('water', 'air')
wrapper.SP[CUBA.DENSITY] = {'water': 1000.0, 'air': 1.0}
wrapper.SP[CUBA.DYNAMIC_VISCOSITY] = {'water': 0.001, 'air': 1.8e-5}
wrapper.SP_extensions[CUBAExt.SURFACE_TENSION] = {('water', 'air'): 72.86e-3}

# this is just an example. It is not enough for general setting of BC's
wrapper.BC[CUBA.VELOCITY] = {'boundary0': ('fixedValue', (0.01e-3, 0, 0)),
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
numerrin.create_quad_mesh(name, wrapper, corner_points,
                          extrude_length, nex, ney, nez)

mesh_inside_wrapper = wrapper.get_dataset(name)

# initial state. In VOF only one velocity and pressure field

updated_points = []
for point in mesh_inside_wrapper.iter_points():
    x = point.coordinates[0]    
    if x < 0.02/3.0:
#        print x
        point.data[CUBA.VOLUME_FRACTION] = 1.0
    else:
        point.data[CUBA.VOLUME_FRACTION] = 0.0

    point.data[CUBA.PRESSURE] = 0.0
    point.data[CUBA.VELOCITY] = [0.0, 0.0, 0.0]

    updated_points.append(point)

mesh_inside_wrapper.update_points(updated_points)

wrapper.run()
print "Run up to time: ", mesh_inside_wrapper._time
