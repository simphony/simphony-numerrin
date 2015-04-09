""" numerrin_pool

Module for operations on Numerrin pool

"""
from simphony.core.cuba import CUBA

from .numerrin_code import NumerrinCode
from .numerrin_utils import face_renode, cell_renode
import numerrin


class NumerrinPool(object):

    def __init__(self):
        self.ph = numerrin.createpool()

    def __del__(self):
        numerrin.deletepool(self.ph)

 
    def export_mesh(self, numerrinName):
        simphonyMesh = Mesh(numerrinName)
        uuids = []
        mmap = NumerrinMeshMap()
        meshsize = numerrin.meshsize(self.ph,numerrinName)
        for i in range(meshsize[0]):
            coord = numerrin.getnode(self.ph,numerrinName,i)
            spoint = Point(coord)
            simphonyMesh.add_point(spoint)
            uuids.append(spoint.uid)
            mmap.setindex(spoint.uid,i)

        if len(meshsize) > 1:
            for i in range(meshsize[1]):
                plbl = numerrin.getelement(self.ph,numerrinName,1,i,0)
                points = []
                for pi in range(len(plbl)):
                    points.append(uuids[plbl[pi]])
                ed = Edge(points)
                simphonyMesh.add_edge(ed)
                mmap.setindex(ed.uid,i)

        if len(meshsize) > 2:
            for i in range(meshsize[2]):
                plbl = numerrin.getelement(self.ph,numerrinName,2,i,0)
                points = []
                for pi in range(len(plbl)):
                    points.append(uuids[plbl[pi]])
                face_renode(points)           
                fa = Face(points)
                simphonyMesh.add_face(fa)
                mmap.setindex(fa.uid,i)

        if len(meshsize) > 3:
            for i in range(meshsize[3]):
                plbl = numerrin.getelement(self.ph,numerrinName,3,i,0)
                points = []
                for pi in range(len(plbl)):
                    points.append(uuids[plbl[pi]])
                cell_renode(points)
                ce = Cell(points)
                simphonyMesh.add_cell(ce)
                mmap.setindex(ce.uid,i)

        return (simphonyMesh,mmap)

    def import_mesh(self, numerrinName, simphonyMesh):

        nPoints = sum(1 for _ in simphonyMesh.iter_points())
        nEdges = sum(1 for _ in simphonyMesh.iter_edges())
        nFaces = sum(1 for _ in simphonyMesh.iter_faces())
        nCells = sum(1 for _ in simphonyMesh.iter_cells())

        sizes=(nPoints, nEdges, nFaces, nCells)
        numerrin.initmesh(self.ph,numerrinName,3,sizes)
        
        mmap = {}
        pmap = {}
        indx = 0
        for point in simphonyMesh.iter_points():
            numerrin.setnode(self.ph,numerrinName,indx,point.coordinates)
            mmap[point.uid] = indx
            pmap[indx] = point.uid
            indx = indx+1

        indx = 0
        emap = {}
        for edge in simphonyMesh.iter_edges():
            pind = []
            for point in edge.points:
                pind.append(mmap[point])
            numerrin.setelementtype(self.ph,numerrinName,1,indx,1)
            numerrin.setelement(self.ph,numerrinName,1,indx,0,tuple(pind))
            mmap[edge.uid] = indx
            emap[indx] = edge.uid
            indx = indx+1

        indx = 0
        fmap = {}
        for face in simphonyMesh.iter_faces():
            pind = []
            for point in face.points:
                pind.append(mmap[point])
            face_renode(pind)
            if len(pind) == 3:
                numerrin.setelementtype(self.ph,numerrinName,2,indx,2)
            else:
                numerrin.setelementtype(self.ph,numerrinName,2,indx,3)
            numerrin.setelement(self.ph,numerrinName,2,indx,0,tuple(pind))
            mmap[face.uid] = indx
            fmap[indx] = face.uid
            indx = indx+1

        indx = 0
        cmap = {}
        for cell in simphonyMesh.iter_cells():
            pind = []
            for point in cell.points:
                pind.append(mmap[point])
            cell_renode(pind)
            if len(pind) == 4:
                numerrin.setelementtype(self.ph,numerrinName,3,indx,4)
            elif len(pind) == 6:
                numerrin.setelementtype(self.ph,numerrinName,3,indx,6)
            else:
                numerrin.setelementtype(self.ph,numerrinName,3,indx,7)
            numerrin.setelement(self.ph,numerrinName,3,indx,0,tuple(pind))
            mmap[cell.uid] = indx
            cmap[indx] = cell.uid
            indx = indx+1

        # add domains
        numcode = "omega = Domain(" + numerrinName + ")\n" 
        boundaries = []
        elementcode = ""
        for face in simphonyMesh.iter_faces():
            if face.data:
                if CUBA.LABEL in face.data:
                    fuid = str(mmap[face.uid])
                    blabel = face.data[CUBA.LABEL]
                    if blabel not in boundaries:
                        boundaries.append(blabel)
                    elementcode += "AddElement(" + numerrinName +\
                                   "domains" + str(blabel) + "," +\
                                   fuid + "," + fuid + ")\n" +\
                                   "Face" + fuid +  numerrinName +\
                                   "=" + str(blabel) +"\n"
                                   
        for boundary in boundaries:
            numcode += numerrinName + "domains" + str(boundary) +\
                       "= Domain(" + numerrinName + ",2,2)\n"
        numcode += elementcode
        code = NumerrinCode(self)
        code.parse_string(numcode)
        code.execute(1)

        return [mmap, pmap, emap, fmap, cmap]

    def clear(self):
        numerrin.clearpool(self.ph)

    def variable_type(self, name):
        typ=numerrin.gettype(self.ph, name)
        return typ

    def variable_rank(self, name):
        ran=numerrin.getrank(self.ph, name)
        return ran

    def variable_size(self, name):
        siz=numerrin.getsize(self.ph, name)
        return siz

    def get_variable(self, name):
        var=numerrin.getvariable(self.ph, name)
        return var

    def put_variable(self, name, var):
        numerrin.putvariable(self.ph, name, var)

    def modify_variable(self, name, var):
        numerrin.modifyvariable(self.ph, name, var)

    def get_face_points(self, name, label):
        pointLabels = numerrin.getelement(self.ph, name,
                                          2, label, 0)
        return face_renode(list(pointLabels))

    def get_face_boundary_label(self, name, label):
        bname = "Face" + str(label) +  name
        return self.get_variable(bname)

    def add_node_data(self,simphonyMesh,mmap,dataName,key):
        if numerrin.gettype(self.ph,dataName) == "Function":
            data=numerrin.getvariable(self.ph,dataName+"[[:]]")
        else:
            data=numerrin.getvariable(self.ph,dataName)
        for point in simphonyMesh.iter_points():
            point.data.update({key:data[mmap.getindex(point.uid)]})
            simphonyMesh.update_point(point)

    def add_edge_data(self,simphonyMesh,mmap,dataName,key):
        if numerrin.gettype(self.ph,dataName) == "Function":
            data=numerrin.getvariable(self.ph,dataName+"[[:]]")
        else:
            data=numerrin.getvariable(self.ph,dataName)
        for edge in simphonyMesh.iter_edges():
            edge.data.update({key:data[mmap.getindex(edge.uid)]})
            simphonyMesh.update_edge(edge)

    def add_face_data(self,simphonyMesh,mmap,dataName,key):
        if numerrin.gettype(self.ph,dataName) == "Function":
            data=numerrin.getvariable(self.ph,dataName+"[[:]]")
        else:
            data=numerrin.getvariable(self.ph,dataName)
        for face in simphonyMesh.iter_faces():
            face.data.update({key:data[mmap.getindex(face.uid)]})
            simphonyMesh.update_face(face)

    def add_cell_data(self,simphonyMesh,mmap,dataName,key):
        if numerrin.gettype(self.ph,dataName) == "Function":
            data=numerrin.getvariable(self.ph,dataName+"[[:]]")
        else:
            data=numerrin.getvariable(self.ph,dataName)
        for cell in simphonyMesh.iter_cells():
            cell.data.update({key:data[mmap.getindex(cell.uid)]})
            simphonyMesh.update_cell(cell)
