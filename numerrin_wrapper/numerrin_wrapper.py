""" numerrin_wrapper module

Wrapper module for Numerrin using native Numerrin-Python interface

"""

from simphony.cuds.abc_modeling_engine import ABCModelingEngine
from simphony.core.data_container import DataContainer

from .numerrin_pool import NumerrinPool
from .numerrin_code import NumerrinCode
from .numerrin_mesh import NumerrinMesh
from .numerrin_templates import numname, liccode, get_numerrin_solver
from .cuba_extension import CUBAExt

import numerrin


class Wrapper(ABCModelingEngine):
    """ Wrapper to Numerrin

    """

    def __init__(self):
        super(Wrapper, self).__init__()
        numerrin.initlocal("", "PYNUMERRIN_LICENSE", liccode)
        self.pool = NumerrinPool()
        self.code = NumerrinCode(self.pool.ph)
        self._meshes = {}
        self.CM = DataContainer()
        self.SP = DataContainer()
        self.BC = DataContainer()
        self.CM_extensions = {}
        self.SP_extensions = {}
        self._first = True

    def run(self):
        """Run Numerrin based on CM, BC and SP data

        Raises
        ------
        Exception when solver not supported.

        """

        # assume that only one dataset
        mesh = self.iter_datasets().next()

        # put SP parameters to pool
        for key in self.SP:
            self.pool.put_parameter(numname[key], self.SP[key])
        for key in self.SP_extensions:
            self.pool.put_parameter(numname[key], self.SP_extensions[key])
        # init variables to pool if not initialized
        mesh.init_point_variables(get_numerrin_solver(self.CM_extensions))
        # parse solver code
        if self._first:
            f = open('code.num', 'w')
            f.write(self.code.generate_init_code(self.CM,
                                                 self.SP,
                                                 self.SP_extensions,
                                                 self.BC,
                                                 self.CM_extensions) +
                    self.code.generate_code(self.CM,
                                            self.SP,
                                            self.SP_extensions,
                                            self.BC,
                                            self.CM_extensions,
                                            mesh))
            f.close()
            # initialize time
            self.pool.put_variable('curTime', 0.0)
            self.code.parse_string(
                self.code.generate_init_code(self.CM,
                                             self.SP,
                                             self.SP_extensions,
                                             self.BC,
                                             self.CM_extensions) +
                self.code.generate_code(self.CM,
                                        self.SP,
                                        self.SP_extensions,
                                        self.BC,
                                        self.CM_extensions,
                                        mesh))
            self._first = False
        else:
            self.code.clear()
            self.code.parse_string(
                self.code.generate_code(self.CM,
                                        self.SP,
                                        self.SP_extensions,
                                        self.BC,
                                        self.CM_extensions,
                                        mesh))

        # execute code
        number_of_cores = 1
        if CUBAExt.NUMBER_OF_CORES in self.CM_extensions:
            number_of_cores = self.CM_extensions[CUBAExt.NUMBER_OF_CORES]
        self.code.execute(number_of_cores)
        # save time
        mesh._time = self.pool.get_variable('curTime')

    def add_dataset(self, mesh):
        """Add a mesh to the Numerrin modeling engine.

        Parameters
        ----------
        mesh : ABCMesh
            mesh to be added.

        Returns
        -------
        proxy : NumerrinMesh
            A proxy mesh to be used to update/query the internal representation
            stored inside the modeling-engine. See get_mesh for more
            information.

        Raises
        ------
        Exception if mesh already exists

        """

        if mesh.name in self._meshes:
            raise ValueError('Mesh \'{}\` already exists'.format(mesh.name))

        self._meshes[mesh.name] = NumerrinMesh(mesh.name, mesh, self.pool)
        return self._meshes[mesh.name]

    def get_dataset(self, name):
        """Get a mesh.

        The returned mesh can be used to query and update the state of the
        mesh inside the Numerrin modeling engine.

        Parameters
        ----------
        name : str
            name of the mesh to be retrieved.

        Returns
        -------
        NumerrinMesh

        """

        return self._meshes[name]

    def iter_datasets(self, names=None):
        """Returns an iterator over a subset or all of the meshes.

        Parameters
        ----------
        names : list of str
            names of specific meshes to be iterated over.
            If names is not given, then all meshes will
            be iterated over.

        Returns
        ----------
        Iterator over a subset or all of the meshes

        Raises
        ------
        Exception if some mesh fron mesh names list not found

        """

        if names is None:
            for name in self._meshes:
                yield self._meshes[name]
        else:
            for name in names:
                yield self._meshes[name]

    def remove_dataset(self, name):
        """Delete mesh from the Numerrin modeling engine.

        Parameters
        ----------
        name : str
            name of the mesh to be deleted.


        Raises
        ------
        Exception if mesh not found

        """

        # here operation to pool of deleting mesh and
        # corresponding variables should be added
        del self._meshes[name]

    def get_dataset_names(self):
        """ Returns the names of the meshes.

        """

        return self._meshes.keys()
