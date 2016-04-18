"""Example to solve 2D poiseuille flow

"""

from simphony.core.cuba import CUBA
from simphony.engine import numerrin

from mayavi.scripts import mayavi2


wrapper = numerrin.Wrapper()
CUBAExt = numerrin.CUBAExt
name = 'poiseuille'

wrapper.CM[CUBA.NAME] = name

wrapper.CM_extensions[CUBAExt.GE] = (CUBAExt.INCOMPRESSIBLE,
                                     CUBAExt.LAMINAR_MODEL)
wrapper.CM_extensions[CUBAExt.NUMBER_OF_CORES] = 4
wrapper.SP[CUBA.TIME_STEP] = 0.1
wrapper.SP[CUBA.NUMBER_OF_TIME_STEPS] = 10
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

corner_points = ((0.0, 0.0), (20.0e-3, 0.0), (20.0e-3, 1.0e-3),
                 (0.0, 1.0e-3))
extrude_length = 0.1e-3
nex = 10
ney = 3
nez = 1
numerrin.create_quad_mesh(name, wrapper, corner_points,
                          extrude_length, nex, ney, nez)
mesh_inside_wrapper = wrapper.get_dataset(name)

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
