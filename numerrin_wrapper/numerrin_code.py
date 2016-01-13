from simphony.core.cuba import CUBA

from .cuba_extension import CUBAExt

from .numerrin_templates import solverFrames, functions, associations
from .numerrin_templates import functionSpaces, get_numerrin_solver
from .numerrin_templates import timeLoop
from .numerrin_templates import numname, to_numerrin_expression
from .numerrin_templates import multiphase_solvers, external_body_force_model
from .numerrin_templates import mixture_model, relative_velocity_code
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

    def generate_init_code(self, CM, SP, SPExt, BC, CMExt):
        """ generate Numerrin code for function domain and space definitions
            according to user settings

        Parameters
        ----------
        CM : DataContainer
            Computational Method
        SP : DataContainer
            System Parameters
        SPExt : dictionary
            extension to SP
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

        pressureBCs = BC[CUBA.PRESSURE]
        velocityBCs = BC[CUBA.VELOCITY]
        boundaries = []
        for boundary in pressureBCs:
            if boundary not in boundaries:
                boundaries.append(boundary)
        for boundary in velocityBCs:
            if boundary not in boundaries:
                boundaries.append(boundary)
        for boundary in boundaries:
            bi = int(boundary.replace('boundary', ''))
            domaincode += boundary + "->" + name + "domains" +\
                str(bi) + "\n"

        # functions
        code += functions[solver]
        # domains
        code += domaincode
#        code += "Save(poiseuille)\n"
#        code += "Save(omega)\n"
#        code += "Save(poiseuilledomains0)\n"
        # spaces
        code += functionSpaces[solver]
        # associations
        if solver in multiphase_solvers:
            code += associations[solver].format(
                phase1_name=SPExt[CUBAExt.PHASE_LIST][0],
                phase2_name=SPExt[CUBAExt.PHASE_LIST][1])
        else:
            code += associations[solver]

        code += external_body_force_model(SPExt)

        return code

    def generate_code(self, CM, SP, SPExt, BC, CMExt):
        """ generate Numerrin code according to user settings

        Parameters
        ----------
        CM : DataContainer
            Computational Method
        SP : DataContainer
            System Parameters
        SPExt : dictionary
            extension to SP
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
                                 "empty", "slip"]
        boundaries = []
        if solver == "steadyStateLaminar":
            for boundary in pressureBCs:
                if boundary not in boundaries:
                    boundaries.append(boundary)
                if pressureBCs[boundary] not in nonFixedBoundaryTypes:
                    bccode += "Constraint(" + boundary + ",W)\n"
                    bccode += " r[3] <- p(.) - " +\
                        to_numerrin_expression(pressureBCs[boundary][1]) +\
                        "\n"
                    bccode += "EndConstraint\n"

            for boundary in velocityBCs:
                if boundary not in boundaries:
                    boundaries.append(boundary)
                if velocityBCs[boundary] not in nonFixedBoundaryTypes:
                    velo = to_numerrin_expression(velocityBCs[boundary][1])
                    bccode += "Constraint(" + boundary + ",V)\n"
                    bccode += " up=u(.)\n"
                    bccode += " r[0] <- up[0] - " + velo[0] + "\n"
                    bccode += " r[1] <- up[1] - " + velo[1] + "\n"
                    bccode += " r[2] <- up[2] - " + velo[2] + "\n"
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
                    velo = to_numerrin_expression(velocityBCs[boundary][1])
                    bccode += "Constraint(" + boundary + ",V)\n"
                    bccode += " up=u(.)\n"
                    bccode += " r[0] <- up[0] - " + velo[0] + "\n"
                    bccode += " r[1] <- up[1] - " + velo[1] + "\n"
                    bccode += " r[2] <- up[2] - " + velo[2] + "\n"
                    bccode += "EndConstraint\n"

        elif solver in multiphase_solvers:
            for boundary in pressureBCs:
                bccode += "? \"Mom fluxes\"\n"
                if boundary not in boundaries:
                    boundaries.append(boundary)
                if pressureBCs[boundary] not in nonFixedBoundaryTypes:
                    # integrate momentum on outflow boundaries
                    # (where pressure is fixed)
                    bccode += "Integral(" + boundary + ",\"VlFlx2\",1)\n"
                    bccode += "nor:=NormalVector\n"
                    bccode += "vf:=VolumeFunction\n"
                    bccode += "rhoEff=phi(.)*rho2+(1-phi(.))*rho1\n"
                    bccode += "up:=u(.)\n"
                    bccode += "If up dot nor > 0.0\n"
                    bccode += "r[0] <- sc*(rhoEff*u[0](.)*u(.) dot nor)*vf\n"
                    bccode += "r[1] <- sc*(rhoEff*u[1](.)*u(.) dot nor)*vf\n"
                    bccode += "r[2] <- sc*(rhoEff*u[2](.)*u(.) dot nor)*vf\n"
                    bccode += "EndIf\n"
                    bccode += "EndIntegral\n"
            for boundary in velocityBCs:
                if boundary not in boundaries:
                    boundaries.append(boundary)
                if velocityBCs[boundary] not in nonFixedBoundaryTypes:
                    velo = to_numerrin_expression(velocityBCs[boundary][1])
                    bccode += "Constraint(" + boundary + ",V)\n"
                    bccode += " up=u(.)\n"
                    bccode += " r[0] <- up[0] - " + velo[0] + "\n"
                    bccode += " r[1] <- up[1] - " + velo[1] + "\n"
                    bccode += " r[2] <- up[2] - " + velo[2] + "\n"
                    bccode += "EndConstraint\n"

            volumeFractionBCs = BC[CUBA.VOLUME_FRACTION]

            for boundary in volumeFractionBCs:
                if boundary not in boundaries:
                    boundaries.append(boundary)
                if volumeFractionBCs[boundary] not in nonFixedBoundaryTypes:
                    bccode += "Constraint(" + boundary + ",W)\n"
                    bccode += " r[3] <- phi(.) - " +\
                        to_numerrin_expression(volumeFractionBCs[boundary][1])\
                        + "\n"
                    bccode += "EndConstraint\n"

        # integrate flux over boundaries
        if solver == "VOFLaminar":
            bccode += "? \"Boundary fluxes\"\n"
            for boundary in boundaries:
                bccode += "Integral(" + boundary + ",\"VlFlx1\",3)\n"
                bccode += "nor:=NormalVector\n"
                bccode += "vf:=VolumeFunction\n"
                bccode += "r[3] <- sc*phi(.)*(u(.) dot nor)*vf\n"
                bccode += "r[4] <- sc*u(.) dot nor*vf\n"
                bccode += "EndIntegral\n"
        elif solver == "mixtureModelLaminar":
            r_code = relative_velocity_code(SPExt)
            for boundary in boundaries:
                bccode += "Integral(" + boundary + ",\"VlFlx1\",3)\n"
                bccode += "nor:=NormalVector\n"
                bccode += "vf:=VolumeFunction\n"
                bccode += "rhom=phi(.)*rho2+(1-phi(.))*rho1\n"
                bccode += "udm=rho1/rhom*{}\n".format(r_code)
                bccode += "cd=phi(.)*rho2/rhom\n"
                bccode += "r[3] <- sc*phi(.)*((u(.)"
                bccode += "+ (1-cd)*udm) dot nor)*vf\n"
                bccode += "r[4] <- sc*u(.) dot nor*vf\n"
                bccode += "EndIntegral\n"
        else:
            for boundary in boundaries:
                bccode += "Integral(" + boundary + ",\"VlFlx1\",3)\n"
                bccode += "nor:=NormalVector\n"
                bccode += "vf:=VolumeFunction\n"
                bccode += "r[3] <- u(.) dot nor*vf\n"
                bccode += "EndIntegral\n"

        # time loop and initializations
#        code += "? \"waterDensity\", waterDensity\n"                
#        code += "? \"airDensity\", airDensity\n"                
#        code += "? \"waterViscosity\", waterViscosity\n"                
#        code += "? \"airViscosity\", airViscosity\n"                
#        code += "? \"waterairSurfaceTension\","
#        code += "waterairSurfaceTension\n"                
#        code += "? \"TimeStep\", TimeStep\n"                
        code += timeLoop[solver]
        code += "? \"Time: \", curTime\n"
        # main loop
        code += "NumberOfInnerSteps=10\n"
        code += "normi0=0.0\n"
        code += "relax=0.1\n"
        code += "reduc=1.0e-4\n"

        code += "For inIt=1:NumberOfInnerSteps\n"
        # solver frame
        if solver == "mixtureModelLaminar":
            code += mixture_model(SPExt)
        else:
            code += solverFrames[solver]
        # boundary conditions
        code += bccode
        # linear solver
        code += "normi =  Norm(r)\n"
        code += "If inIt == 1\n"
        code += "  eps=reduc*normi\n"
        code += "EndIf\n"
        code += "? inIt, \":\", normi\n"
        code += "If (normi < 1.0e-8) || (~(normi > eps) && inIt >= 2)\n"
        code += " Exit\n"
        code += "EndIf\n"
        code += "? \"Start linear system solving\"\n"
        code += "q -= relax*LU(A,r)\n"
        code += "? \"End linear system solving\"\n"
        code += "if normi < normi0\n"
        code += " relax = 1.0\n"
        code += "endif\n"
        code += "normi0=normi\n"
        # loop end
        code += "EndFor\n"
        # time loop end
        code += "EndFor\n"
#        code += "WriteCGNS(\"tulos.cgns\") poiseuille,u,p\n"
        code += name + numname[CUBA.VELOCITY] + "=u \n"
        code += name + numname[CUBA.PRESSURE] + "=p\n"
        return code
