""" numerrin_wrapper module

Wrapper module for Numerrin using native Numerrin-Python interface

"""

from simphony.cuds.abc_modeling_engine import ABCModelingEngine
from simphony.core.data_container import DataContainer

from .numerrin_pool import NumerrinPool
from .numerrin_code import NumerrinCode
from .numerrin_mesh import NumerrinMesh
from .numerrin_templates import numname, liccode

import numerrin


class NumerrinWrapper(ABCModelingEngine):
    """ Wrapper to Numerrin

    """

    def __init__(self):
        super(NumerrinWrapper, self).__init__()
        numerrin.initlocal("", "PYNUMERRIN_LICENSE", liccode)
        self.pool = NumerrinPool()
        self.code = NumerrinCode(self.pool.ph)
        self._meshes = {}
        self.CM = DataContainer()
        self.SP = DataContainer()
        self.BC = DataContainer()
        self.CM_extensions = {}
        self._first = True

    def run(self):
        """Run Numerrin based on CM, BC and SP data

        Raises
        ------
        Exception when solver not supported.

        """

        # put SP parameters to pool
        for key in self.SP:
            self.pool.put_variable(numname[key], self.SP[key])
        # parse solver code
        if self._first:
            self.code.parse_string(
                self.code.generate_code(self.CM,
                                        self.SP,
                                        self.BC,
                                        self.CM_extensions))
            self._first = False

        # execute code
        self.code.execute(1)
        # save last iteration
        for mesh in self.iter_meshes():
            mesh._time = self.pool.get_variable('iteration')

    def add_mesh(self, mesh):
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

    def get_mesh(self, name):
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

    def iter_meshes(self, names=None):
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

    def delete_mesh(self, name):
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

    def add_particles(self, particle_container):
        message = 'NumerrinWrapper does not handle particle container'
        raise NotImplementedError(message)

    def get_particles(self, name):
        message = 'NumerrinWrapper does not handle particle container'
        raise NotImplementedError(message)

    def delete_particles(self, name):
        message = 'NumerrinWrapper does not handle particle container'
        raise NotImplementedError(message)

    def iter_particles(self, names=None):
        message = 'NumerrinWrapper does not handle particle container'
        raise NotImplementedError(message)

    def add_lattice(self, lattice):
        message = 'NumerrinWrapper does not handle lattice'
        raise NotImplementedError(message)

    def get_lattice(self, name):
        message = 'NumerrinWrapper does not handle lattice'
        raise NotImplementedError(message)

    def delete_lattice(self, name):
        message = 'NumerrinWrapper does not handle lattice'
        raise NotImplementedError(message)

    def iter_lattices(self, names=None):
        message = 'NumerrinWrapper does not handle lattice'
        raise NotImplementedError(message)
