from simphony.core.cuba import CUBA
from numerrin_wrapper import NumerrinWrapper

numerrin_wrapper = NumerrinWrapper()
numerrin_wrapper.CM[CUBA.NAME]="numerrin_wrapper/examples/poiseuille.num"

numerrin_wrapper.run()
(simphonyMesh,numerrinMeshMap)=numerrin_wrapper.get_mesh("mesh")
numerrin_wrapper.get_node_data(simphonyMesh,numerrinMeshMap,"Un",CUBA.VELOCITY)
numerrin_wrapper.get_node_data(simphonyMesh,numerrinMeshMap,"p",CUBA.PRESSURE)
numerrin_wrapper.get_edge_data(simphonyMesh,numerrinMeshMap,"Ue",CUBA.VELOCITY)
numerrin_wrapper.get_face_data(simphonyMesh,numerrinMeshMap,"Uf",CUBA.VELOCITY)
