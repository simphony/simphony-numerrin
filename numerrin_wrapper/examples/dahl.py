"""Example to solve mixture model
"""

from simphony.core.cuba import CUBA

from simphony.engine import numerrin
from simphony.engine import openfoam_file_io

from mayavi.scripts import mayavi2

import dahl_mesh
import tempfile

wrapper = numerrin.Wrapper()
CUBAExt = numerrin.CUBAExt

name = 'dahl'

wrapper.CM[CUBA.NAME] = name

wrapper.CM_extensions[CUBAExt.GE] = (CUBAExt.INCOMPRESSIBLE,
                                     CUBAExt.LAMINAR_MODEL,
                                     CUBAExt.MIXTURE_MODEL)

wrapper.CM_extensions[CUBAExt.NUMBER_OF_CORES] = 4

wrapper.SP[CUBA.TIME_STEP] = 0.1
wrapper.SP[CUBA.NUMBER_OF_TIME_STEPS] = 10

wrapper.SP_extensions[CUBAExt.PHASE_LIST] = ('water', 'sludge')
wrapper.SP[CUBA.DENSITY] = {'sludge': 1900.0, 'water': 1000.0}
wrapper.SP[CUBA.DYNAMIC_VISCOSITY] = {'sludge': 0.01, 'water': 1e-3}
wrapper.SP_extensions[CUBAExt.STRESS_MODEL] = 'standard'
wrapper.SP_extensions[CUBAExt.RELATIVE_VELOCITY_MODEL] = 'simple'
wrapper.SP_extensions[CUBAExt.RELATIVE_VELOCITY_MODEL_COEFFS] =\
    {'V0': (0.0, -0.002, 0.0), 'a': 285.0, 'a1': 0.1, 'residualAlpha': 0}
wrapper.SP_extensions[CUBAExt.EXTERNAL_BODY_FORCE_MODEL] = 'gravitation'
wrapper.SP_extensions[CUBAExt.EXTERNAL_BODY_FORCE_MODEL_COEFFS] =\
    {'g': (0.0, -9.81, 0.0)}
wrapper.BC[CUBA.VELOCITY] = {'inlet': ('fixedValue', (0.0191, 0, 0)),
                             'outlet': 'zeroGradient',
                             'bottomWall': ('fixedValue', (0, 0, 0)),
                             'endWall': ('fixedValue', (0, 0, 0)),
                             'top': 'slip',
                             'frontAndBack': 'empty'}
wrapper.BC[CUBA.PRESSURE] = {'inlet': 'zeroGradient',
                             'outlet': ('fixedValue', 0),
                             'bottomWall': 'zeroGradient',
                             'endWall': 'zeroGradient',
                             'top': 'zeroGradient',
                             'frontAndBack': 'empty'}

wrapper.BC[CUBA.VOLUME_FRACTION] = {'inlet': ('fixedValue', 0.001),
                                    'outlet': 'zeroGradient',
                                    'bottomWall': 'zeroGradient',
                                    'endWall': 'zeroGradient',
                                    'top': 'zeroGradient',
                                    'frontAndBack': 'empty'}

# create mesh
mesh = openfoam_file_io.create_block_mesh(tempfile.mkdtemp(), name,
                                   dahl_mesh.blockMeshDict)
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
print "Run up to time: ", mesh_inside_wrapper._time


@mayavi2.standalone
def view():
    from mayavi.modules.surface import Surface
    from simphony_mayavi.sources.api import CUDSSource

    mayavi.new_scene()  # noqa
    src = CUDSSource(cuds=mesh_inside_wrapper)
    mayavi.add_source(src)  # noqa
    s = Surface()
    mayavi.add_module(s)  # noqa


if __name__ == '__main__':
    view()
