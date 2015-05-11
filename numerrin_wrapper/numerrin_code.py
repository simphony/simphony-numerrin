from simphony.core.cuba import CUBA

from .numerrin_templates import solverFrames, functions
from .cuba_extension import CUBAExt
from .numerrin_templates import numname

import numerrin


class NumerrinCode(object):
    """ Class for handling Numerring code

    """

    def __init__(self, ph):
        self.ph = ph
        self.ch = numerrin.createcode()

    def __del__(self):
        numerrin.deletecode(self.ch)

    def parse_file(self, fileName):
        """ parse Numerrin code in file

        Parameters
        ----------
        fileName : str
            name of file

        """
        numerrin.parsefile(self.ph, self.ch, fileName)

    def parse_string(self, codeString):
        """ parse numerrin code in string

        Parameters
        ----------
        codeString : str
            Numerrin code

        """
        numerrin.parsestring(self.ph, self.ch, codeString)

    def execute(self, nproc):
        """ execute Numerrin code

        Parameters
        ----------
        nproc : int
            number of processor cores

        """
        numerrin.execute(self.ph, self.ch, nproc)

    def clear(self):
        """ clear Numerrin code

        """
        numerrin.clearcode(self.ch)

    def generate_code(self, CM, SP, BC, CMExt):
        """ generate Numerrin code according to user settings

        Parameters
        ----------
        CM : DataContainer
            Computational Method
        SP : DataContainer
            System Parameters
        BC : DataContainer
            Boundary Conditions
        CMExt : dictionary
            extension to CM

        Return
        ------
        code : str
            Numerrin code as a string

        """

        name = CM[CUBA.NAME]
        code = ""

        funccode = ""
        # define spaces
        spacecode = "V=Space(omega,\"Lagrange\",1)\n"
        spacecode += "W=Space(omega,\"Lagrange\",1)\n"
        # define associations
        assoccode = "u[0:2] in V\n"
        assoccode += "p in W\n"
        assoccode += "q[0:2]->u\n"
        assoccode += "q[3]->p\n"
        assoccode += "r:=q\n"
        # define domains and boundary conditions
        domaincode = ""
        bccode = ""
        pressureBCs = BC[CUBA.PRESSURE]
        nonFixedBoundaryTypes = ["zeroGradient",
                                 "fixedFluxPressure",
                                 "empty"]
        for boundary in pressureBCs:
            if pressureBCs[boundary] not in nonFixedBoundaryTypes:
                bi = int(boundary.replace('boundary', ''))
                domaincode += boundary + "->" + name + "domains" +\
                    str(bi) + "\n"
                bccode += "Constraint(" + boundary + ",W)\n"
                bccode += " r[3] <- p(.) - " +\
                    str(pressureBCs[boundary]) +\
                    "\n"
                bccode += "EndConstraint\n"

        velocityBCs = BC[CUBA.VELOCITY]
        for boundary in velocityBCs:
            if velocityBCs[boundary] not in nonFixedBoundaryTypes:
                bi = int(boundary.replace('boundary', ''))
                velo = velocityBCs[boundary]
                domaincode += boundary + "->" + name + "domains" +\
                    str(bi) + "\n"
                bccode += "Constraint(" + boundary + ",V)\n"
                bccode += " up=u(.)\n"
                bccode += " r[0] <- up[0] - " + str(velo[0]) + "\n"
                bccode += " r[1] <- up[1] - " + str(velo[1]) + "\n"
                bccode += " r[2] <- up[2] - " + str(velo[2]) + "\n"
                bccode += "EndConstraint\n"

        GE = CMExt[CUBAExt.GE]
        if CUBAExt.LAMINAR_MODEL in GE:
            solver = "stabilizedLaminarNS3D"
            funccode += functions[solver]
        else:
            error_str = "GE does not define supported solver: GE = {}"
            raise NotImplementedError(error_str.format(GE))
        # functions
        code += funccode
        # domains
        code += domaincode
        # spaces
        code += spacecode
        # associations
        code += assoccode
        # main loop
        code += "For iteration=1:NumberOfTimeSteps\n"
        # solver frame
        code += solverFrames[solver].format(integrationDegree=3)
        # boundary conditions
        code += bccode
        # linear solver
        #        code += "? iteration, \": \", Norm(r)\n"
        code += "If Norm(r) < 1.0e-6\n"
        code += "Exit\n"
        code += "EndIf\n"
        code += "q -= LU(A,r)\n"
        # loop end
        code += "EndFor\n"
        code += name + numname[CUBA.VELOCITY] + "=u \n"
        code += name + numname[CUBA.PRESSURE] + "=p\n"
        return code
