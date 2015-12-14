from simphony.core.cuba import CUBA

from .numerrin_templates import solverFrames, functions
from .numerrin_templates import functionSpaces, get_numerrin_solver
from .numerrin_templates import timeLoop
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

    def generate_init_code(self, CM, SP, BC, CMExt):
        """ generate Numerrin code for function domain and space definitions
            according to user settings

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

        solver = get_numerrin_solver(CMExt)
        name = CM[CUBA.NAME]
        code = ""
        domaincode = ""

        nonFixedBoundaryTypes = ["zeroGradient",
                                 "fixedFluxPressure",
                                 "empty"]
        pressureBCs = BC[CUBA.PRESSURE]
        velocityBCs = BC[CUBA.VELOCITY]
        for boundary in pressureBCs:
            if pressureBCs[boundary] not in nonFixedBoundaryTypes:
                bi = int(boundary.replace('boundary', ''))
                domaincode += boundary + "->" + name + "domains" +\
                    str(bi) + "\n"

        for boundary in velocityBCs:
            if velocityBCs[boundary] not in nonFixedBoundaryTypes:
                bi = int(boundary.replace('boundary', ''))
                domaincode += boundary + "->" + name + "domains" +\
                    str(bi) + "\n"

        # define associations
        assoccode = "u[0:2] in V\n"
        assoccode += "p in W\n"
        assoccode += "q[0:2]->u\n"
        assoccode += "q[3]->p\n"
        assoccode += "r:=q\n"

        # functions
        code += functions[solver]
        # domains
        code += domaincode
        # spaces
        code += functionSpaces[solver]
        # associations
        code += assoccode

        return code

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
        solver = get_numerrin_solver(CMExt)
        code = ""

        # define boundary conditions
        bccode = ""
        pressureBCs = BC[CUBA.PRESSURE]
        velocityBCs = BC[CUBA.VELOCITY]

        nonFixedBoundaryTypes = ["zeroGradient",
                                 "fixedFluxPressure",
                                 "empty"]
        boundaries = []
        if solver == "steadyStateLaminar":
            for boundary in pressureBCs:
                if boundary not in boundaries:
                    boundaries.append(boundary)
                if pressureBCs[boundary] not in nonFixedBoundaryTypes:
                    bccode += "Constraint(" + boundary + ",W)\n"
                    bccode += " r[3] <- p(.) - " +\
                        str(pressureBCs[boundary]) +\
                        "\n"
                    bccode += "EndConstraint\n"

            for boundary in velocityBCs:
                if boundary not in boundaries:
                    boundaries.append(boundary)
                if velocityBCs[boundary] not in nonFixedBoundaryTypes:
                    velo = velocityBCs[boundary]
                    bccode += "Constraint(" + boundary + ",V)\n"
                    bccode += " up=u(.)\n"
                    bccode += " r[0] <- up[0] - " + str(velo[0]) + "\n"
                    bccode += " r[1] <- up[1] - " + str(velo[1]) + "\n"
                    bccode += " r[2] <- up[2] - " + str(velo[2]) + "\n"
                    bccode += "EndConstraint\n"

        elif solver == "timeDependentLaminar":
            for boundary in pressureBCs:
                if boundary not in boundaries:
                    boundaries.append(boundary)
                if pressureBCs[boundary] not in nonFixedBoundaryTypes:
                    # integrate momentum on outflow boundaries
                    # (where pressure is fixed)
                    bccode += "Integral(" + boundary + ",\"VlFlx2\",1)\n"
                    bccode += "nor:=NormalVector\n"
                    bccode += "vf:=VolumeFunction\n"
                    bccode += "If u(.) dot nor > 0.0\n"
                    bccode += "r[0] <- Density*u[0](.)*u(.) dot nor*vf\n"
                    bccode += "r[1] <- Density*u[1](.)*u(.) dot nor*vf\n"
                    bccode += "r[2] <- Density*u[2](.)*u(.) dot nor*vf\n"
                    bccode += "EndIf\n"
                    bccode += "EndIntegral\n"
            for boundary in velocityBCs:
                if boundary not in boundaries:
                    boundaries.append(boundary)
                if velocityBCs[boundary] not in nonFixedBoundaryTypes:
                    velo = velocityBCs[boundary]
                    bccode += "Constraint(" + boundary + ",V)\n"
                    bccode += " up=u(.)\n"
                    bccode += " r[0] <- up[0] - " + str(velo[0]) + "\n"
                    bccode += " r[1] <- up[1] - " + str(velo[1]) + "\n"
                    bccode += " r[2] <- up[2] - " + str(velo[2]) + "\n"
                    bccode += "EndConstraint\n"
            # integrate flux over boundaries
            for boundary in boundaries:
                bccode += "Integral(" + boundary + ",\"VlFlx1\",3)\n"
                bccode += "nor:=NormalVector\n"
                bccode += "vf:=VolumeFunction\n"
                bccode += "r[3] <- u(.) dot nor*vf\n"
                bccode += "EndIntegral\n"

        # time loop and initializations
        code += timeLoop[solver]
        # main loop
        code += "NumberOfInnerSteps=2\n"
        code += "normi0=0.0\n"
        code += "relax=0.1\n"

        code += "For inIt=1:NumberOfInnerSteps\n"
        # solver frame
        code += solverFrames[solver]
        # boundary conditions
        code += bccode
        # linear solver
        code += "? inIt, \": \", Norm(r)\n"
#        code += "If Norm(r) < 1.0e-6\n"
#        code += "Exit\n"
#        code += "EndIf\n"
        code += "q -= relax*LU(A,r)\n"
        code += "if normi < normi0\n"
        code += " relax = 1.0\n"
        code += "endif\n"
        code += "normi0=normi\n"
        # loop end
        code += "EndFor\n"
        # time loop end
        code += "? \"Time step: \", curTime\n"
        code += "EndFor\n"
        code += name + numname[CUBA.VELOCITY] + "=u \n"
        code += name + numname[CUBA.PRESSURE] + "=p\n"
        return code
