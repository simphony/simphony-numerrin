""" numerrin_wrapper module

Wrapper module for Numerrin using native Numerrin-Python interface
  
"""
from simphony.core.cuba import CUBA
from simphony.core.data_container import DataContainer
from simphony.cuds.mesh import Mesh, Point, Face, Edge, Cell
import inspect
import numerrin

class NumerrinMeshMap(object):

    def __init__(self):
        self.uuidmap = {}

    def getindex(self,uuid):
        return self.uuidmap[uuid]

    def setindex(self,uuid,idx):
        self.uuidmap[uuid] = idx

class NumerrinPool(object):

    def __init__(self):
        self.ph = numerrin.createpool()

    def __del__(self):
        numerrin.deletepool(self.ph)

    def faceRenode(self,tab):
        if len(tab) == 4:
            tmp = tab[2]
            tab[2] = tab[3]
            tab[3] = tmp

    def cellRenode(self,tab):
        if len(tab) == 8:
            tmp = tab[2]
            tab[2] = tab[3]
            tab[3] = tmp
            tmp = tab[6]
            tab[6] = tab[7]
            tab[7] = tmp

    def exportMesh(self, numerrinName):
        simphonyMesh = Mesh()
        uuids = []
        mmap = NumerrinMeshMap()
        meshsize = numerrin.meshsize(self.ph,numerrinName)
        for i in range(meshsize[0]):
            coord = numerrin.getnode(self.ph,numerrinName,i)
            spoint = Point(coord)
            simphonyMesh.add_point(spoint)
            uuids.append(spoint.uuid)
            mmap.setindex(spoint.uuid,i)

        if len(meshsize) > 1:
            for i in range(meshsize[1]):
                plbl = numerrin.getelement(self.ph,numerrinName,1,i,0)
                points = []
                for pi in range(len(plbl)):
                    points.append(uuids[plbl[pi]])
                ed = Edge(points)
                simphonyMesh.add_edge(ed)
                mmap.setindex(ed.uuid,i)

        if len(meshsize) > 2:
            for i in range(meshsize[2]):
                plbl = numerrin.getelement(self.ph,numerrinName,2,i,0)
                points = []
                for pi in range(len(plbl)):
                    points.append(uuids[plbl[pi]])
                self.faceRenode(points)           
                fa = Face(points)
                simphonyMesh.add_face(fa)
                mmap.setindex(fa.uuid,i)

        if len(meshsize) > 3:
            for i in range(meshsize[3]):
                plbl = numerrin.getelement(self.ph,numerrinName,3,i,0)
                points = []
                for pi in range(len(plbl)):
                    points.append(uuids[plbl[pi]])
                self.cellRenode(points)
                ce = Cell(points)
                simphonyMesh.add_cell(ce)
                mmap.setindex(ce.uuid,i)

        return (simphonyMesh,mmap)

    def importMesh(self, numerrinName, simphonyMesh):

        sizes=(len(simphonyMesh._points),len(simphonyMesh._edges),len(simphonyMesh._faces),len(simphonyMesh._cells))
        numerrin.initmesh(self.ph,numerrinName,3,sizes)
        
        mmap = NumerrinMeshMap()
        indx = 0
        for point in simphonyMesh.iter_points():
            numerrin.setnode(self.ph,numerrinName,indx,point.coordinates)
            mmap.setindex(point.uuid,indx)
            indx = indx+1

        indx = 0
        for edge in simphonyMesh.iter_edges():
            pind = []
            for point in edge.points:
                pind.append(mmap.getindex(point))
            numerrin.setelementtype(self.ph,numerrinName,1,indx,1)
            numerrin.setelement(self.ph,numerrinName,1,indx,0,tuple(pind))
            mmap.setindex(edge.uuid,indx)
            indx = indx+1

        indx = 0
        for face in simphonyMesh.iter_faces():
            pind = []
            for point in face.points:
                pind.append(mmap.getindex(point))
            self.faceRenode(pind)
            if len(pind) == 3:
                numerrin.setelementtype(self.ph,numerrinName,2,indx,2)
            else:
                numerrin.setelementtype(self.ph,numerrinName,2,indx,3)
            numerrin.setelement(self.ph,numerrinName,2,indx,0,tuple(pind))
            mmap.setindex(face.uuid,indx)
            indx = indx+1

        indx = 0
        for cell in simphonyMesh.iter_cells():
            pind = []
            for point in cell.points:
                pind.append(mmap.getindex(point))
            self.cellRenode(pind)
            if len(pind) == 4:
                numerrin.setelementtype(self.ph,numerrinName,3,indx,4)
            elif len(pind) == 6:
                numerrin.setelementtype(self.ph,numerrinName,3,indx,5)
            else:
                numerrin.setelementtype(self.ph,numerrinName,3,indx,6)
            numerrin.setelement(self.ph,numerrinName,3,indx,0,tuple(pind))
            mmap.setindex(cell.uuid,indx)
            indx = indx+1

        return mmap

    def clear(self):
        numerrin.clearpool(self.ph)

    def variableType(self, name):
        typ=numerrin.gettype(self.ph, name)
        return typ

    def variableRank(self, name):
        ran=numerrin.getrank(self.ph, name)
        return ran

    def variableSize(self, name):
        siz=numerrin.getsize(self.ph, name)
        return siz

    def getVariable(self, name):
        var=numerrin.getvariable(self.ph, name)
        return var

    def putVariable(self, name, var):
        numerrin.putvariable(self.ph, name, var)

    def modifyVariable(self,name,var):
        numerrin.modifyvariable(self.ph, name, var)

    def addNodeData(self,simphonyMesh,mmap,dataName,key):
        if numerrin.gettype(self.ph,dataName) == "Function":
            data=numerrin.getvariable(self.ph,dataName+"[[:]]")
        else:
            data=numerrin.getvariable(self.ph,dataName)
        for point in simphonyMesh.iter_points():
            point.data.update({key:data[mmap.getindex(point.uuid)]})
            simphonyMesh.update_point(point)

    def addEdgeData(self,simphonyMesh,mmap,dataName,key):
        if numerrin.gettype(self.ph,dataName) == "Function":
            data=numerrin.getvariable(self.ph,dataName+"[[:]]")
        else:
            data=numerrin.getvariable(self.ph,dataName)
        for edge in simphonyMesh.iter_edges():
            edge.data.update({key:data[mmap.getindex(edge.uuid)]})
            simphonyMesh.update_edge(edge)

    def addFaceData(self,simphonyMesh,mmap,dataName,key):
        if numerrin.gettype(self.ph,dataName) == "Function":
            data=numerrin.getvariable(self.ph,dataName+"[[:]]")
        else:
            data=numerrin.getvariable(self.ph,dataName)
        for face in simphonyMesh.iter_faces():
            face.data.update({key:data[mmap.getindex(face.uuid)]})
            simphonyMesh.update_face(face)

    def addCellData(self,simphonyMesh,mmap,dataName,key):
        if numerrin.gettype(self.ph,dataName) == "Function":
            data=numerrin.getvariable(self.ph,dataName+"[[:]]")
        else:
            data=numerrin.getvariable(self.ph,dataName)
        for cell in simphonyMesh.iter_cells():
            cell.data.update({key:data[mmap.getindex(cell.uuid)]})
            simphonyMesh.update_cell(cell)

class NumerrinCode(object):

    def __init__(self, pool):
        if not isinstance(pool, NumerrinPool):
            raise KeyError("NumerrinPool required in creating numerrin_code")
        self.ph = pool.ph
        self.ch = numerrin.createcode()

    def __del__(self):
        numerrin.deletecode(self.ch)

    def parseFile(self,fileName):
        numerrin.parsefile(self.ph, self.ch, fileName)

    def parseString(self,codeString):
        numerrin.parsestring(self.ph, self.ch, codeString)

    def execute(self,nproc):
        numerrin.execute(self.ph, self.ch, nproc)

    def clear(self):
        numerrin.clearcode(self.ch)

class NumerrinWrapper(object):

    numname={CUBA.RADIUS:"Radius",CUBA.MASS:"Mass",CUBA.VOLUME:"Volume",
             CUBA.ANGULAR_VELOCITY:"AngularVelocity",
             CUBA.ANGULAR_ACCELERATION:"AngularAcceleration",
             CUBA.DYNAMIC_VISCOSITY:"Viscosity",
             CUBA.DIFFUSION_COEFFICIENT:"DiffusionCoefficient",
             CUBA.FRICTION_COEFFICIENT:"FrictionCoefficient",
             CUBA.CONTANCT_ANGLE:"ContactAngle",
             CUBA.TIME_STEP:"TimeStep",
             CUBA.FORCE:"Force",
             CUBA.TORQUE:"Torque",
             CUBA.DENSITY:"Density",
             CUBA.YOUNG_MODULUS:"YoungModulus",
             CUBA.POISSON_RATIO:"PoissonRatio"}

    def __init__(self):
        numerrin.initlocal("","PYNUMERRIN_LICENSE","30820275020100300D06092A864886F70D01010105000482025F3082025B02010002818100A3872911FFFFA0AEA14B0BB5B5ECE4960FFB3958F2D6754B891E4E3CCE343E9EEC8BF4DACA30A6580D3362E662479199D813A6EAD587D19758730AD4E519EBE270B207F657DAAB44105DDC94763E2B2E7A476AA182E0861FF347224880AA1AE456593FF7F92C55078935BB917559B29948E98DDAA32F5821D367965DB61AA7870201110281800334D8A5FFFFFE218AB12862EF7D1D9482D2BAD9965484CF48F68E15454C518AA543FFC80E00F433EC2E2F1D9D88EEC6C80062A53B670E261AD5144A72EC6E096D9B071259CE0B6911A94E8D9B8F687B54BF38A72BAC04CF1FA7043019A0846D5BBE53F0801315E33E8D8FF147B83AA3586FCE94B191EDD0D66954030E5D83E1024100DF8608BD9BC506F652DEA6B0783882BE0896AEFFA2AC08DCFE04F36D9FD8F9C8A28E26208A544B5B85E8CE195D200087E907BBD505D35BBDEE2256C9C3D11A99024100BB499690D8095E5F38C48FAE0073D7DE8F9872542CEF87FFA6FC5945C5D6BF526CE060EDEB0AAD668D194066CE860386C19BAA663D499BC92E4982F815A8471F024100B8140732BC8423D9E9E4894608A702422530CC5A0D7E9DE32B8B9B4B3858553BD129C50BBD365C2D411A1323F256970683AC0418D79F00420F6792C446E8704102401608A84D4697B0BFE88F986ED2E073BFD4A885EBC90D1F0F0496289ECBFB259139FC47A3851050A2A73025B1BDF1A60FDA8AC8C0BBEA8ACC5FCC69C2D55F176D0241008F243984C82285014EB8AE8AEECA22C7A8508B88C69892C909AF74ECED21B6B172B025484E8B7B7A8BE38934F28C50F48F117A3C8C5CC1B0885E0054CE53F314")
        self.pool=NumerrinPool()
        self.code=NumerrinCode(self.pool)

        self.CM=DataContainer()
        self.SP=DataContainer()
        self.BC=DataContainer()

        self.first=True

    def parseProgramFile(self, fileName):
        self.code.parseFile(fileName)

    def parseProgramString(self, str):
        self.code.parseString(str)

    def run(self,nproc=1):
        if self.first and CUBA.NAME in self.CM:
            for key in self.SP:
                self.pool.putVariable(self.numname[key],self.SP[key])
            self.parseProgramFile(self.CM[CUBA.NAME])
            self.first=False
        self.code.execute(nproc)

    def add_mesh(self, simphonyMesh, name):
        return self.pool.importMesh(name, simphonyMesh)

    def get_mesh(self, name):
        return self.pool.exportMesh(name)

    def get_node_data(self, simphonyMesh, numerrinMeshMap, dataName, key):
        self.pool.addNodeData(simphonyMesh,numerrinMeshMap,dataName,key)

    def get_edge_data(self, simphonyMesh, numerrinMeshMap, dataName, key):
        self.pool.addEdgeData(simphonyMesh,numerrinMeshMap,dataName,key)

    def get_face_data(self, simphonyMesh, numerrinMeshMap, dataName, key):
        self.pool.addFaceData(simphonyMesh,numerrinMeshMap,dataName,key)

    def get_cell_data(self, simphonyMesh, numerrinMeshMap, dataName, key):
        self.pool.addCellData(simphonyMesh,numerrinMeshMap,dataName,key)
