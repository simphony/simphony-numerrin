from simphony.core.cuba import CUBA

from .cuba_extension import CUBAExt

from .numerrin_templates import (solverFrames, functions, associations,
                                 functionSpaces, get_numerrin_solver,
                                 timeLoop, numname, to_numerrin_expression,
                                 multiphase_solvers, external_body_force_model,
                                 mixture_model, relative_velocity_code,
                                 check_boundary_names,
                                 non_fixed_boundary_types,
                                 zero_normal_velocity_types,
                                 solver_variables, solver_variable_names,
                                 solver_space_names, variable_dimension)
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
        extra_functions = ""
        for boundary in pressureBCs:
            if boundary not in boundaries:
                boundaries.append(boundary)
        for boundary in velocityBCs:
            if boundary not in boundaries:
                boundaries.append(boundary)
            if velocityBCs[boundary] in zero_normal_velocity_types:
                extra_functions += "Z" + boundary +\
                    "=Space(" + boundary + ",\"Split\",2)\n"
                for b in velocityBCs:
                    if b != boundary:
                        extra_functions += "Eliminate(Z" + boundary + "," +\
                            b + ")\n"
                extra_functions += "lambda" + boundary + " in Z" +\
                    boundary + "\n"
        for boundary in boundaries:
            domaincode += boundary + "->" + name + boundary + "\n"

        # functions
        code += functions[solver]
        # domains
        code += domaincode
        # spaces
        code += functionSpaces[solver]

        code += extra_functions

        # associations
        if solver in multiphase_solvers:
            i = 4
        else:
            i = 3
        extra_associations = ""
        for boundary in velocityBCs:
            if velocityBCs[boundary] in zero_normal_velocity_types:
                i += 1
                extra_associations += "q[" + str(i) + "]->lambda" +\
                    boundary + "\n"

        if solver in multiphase_solvers:
            code += associations[solver].format(
                phase1_name=SPExt[CUBAExt.PHASE_LIST][0],
                phase2_name=SPExt[CUBAExt.PHASE_LIST][1],
                extra_associations=extra_associations)
        else:
            code += associations[solver].format(
                extra_associations=extra_associations)

        code += external_body_force_model(SPExt)

        # initial values (all variables are assumed to be in pool)
        for variable in solver_variables[solver]:
            pool_name = name + numname[variable]
            v_dim = variable_dimension[variable]
            if v_dim > 1:
                code += "Constraint(omega," +\
                    solver_space_names[solver][variable] +\
                    ")\n"
                for i in range(v_dim):
                    code += solver_variable_names[variable] + "[" + str(i) +\
                        "]<-" + pool_name + "[" + str(i) + "](.)\n"
                code += "EndConstraint\n"
            else:
                code += "Constraint(omega," +\
                    solver_space_names[solver][variable] +\
                    ")\n"
                code += solver_variable_names[variable] +\
                    "<-" + pool_name + "(.)\n"
                code += "EndConstraint\n"

        return code

    def generate_code(self, CM, SP, SPExt, BC, CMExt, mesh):
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
        check_boundary_names(pressureBCs, mesh._boundaries.keys(),
                             CUBA.PRESSURE)
        velocityBCs = BC[CUBA.VELOCITY]
        check_boundary_names(velocityBCs, mesh._boundaries.keys(),
                             CUBA.VELOCITY)

        boundaries = []

        if solver == "timeDependentLaminar":
            for boundary in pressureBCs:
                if boundary not in boundaries:
                    boundaries.append(boundary)
                if pressureBCs[boundary] not in non_fixed_boundary_types:
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
                if velocityBCs[boundary] not in non_fixed_boundary_types:
                    velo = to_numerrin_expression(velocityBCs[boundary][1])
                    bccode += "Constraint(" + boundary + ",V)\n"
                    bccode += " up=u(.)\n"
                    bccode += " r[0] <- up[0] - " + velo[0] + "\n"
                    bccode += " r[1] <- up[1] - " + velo[1] + "\n"
                    bccode += " r[2] <- up[2] - " + velo[2] + "\n"
                    bccode += "EndConstraint\n"

        elif solver in multiphase_solvers:
            for boundary in pressureBCs:
                if boundary not in boundaries:
                    boundaries.append(boundary)
                if pressureBCs[boundary] not in non_fixed_boundary_types:
                    # integrate momentum on outflow boundaries
                    # (where pressure is fixed)
                    bccode += "? \"Mom fluxes\"\n"
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
                if velocityBCs[boundary] not in non_fixed_boundary_types:
                    velo = to_numerrin_expression(velocityBCs[boundary][1])
                    bccode += "Constraint(" + boundary + ",V)\n"
                    bccode += " up=u(.)\n"
                    bccode += " r[0] <- up[0] - " + velo[0] + "\n"
                    bccode += " r[1] <- up[1] - " + velo[1] + "\n"
                    bccode += " r[2] <- up[2] - " + velo[2] + "\n"
                    bccode += "EndConstraint\n"

            volumeFractionBCs = BC[CUBA.VOLUME_FRACTION]
            check_boundary_names(volumeFractionBCs, mesh._boundaries.keys(),
                                 CUBA.VOLUME_FRACTION)

            for boundary in volumeFractionBCs:
                if boundary not in boundaries:
                    boundaries.append(boundary)
                if volumeFractionBCs[boundary] not in non_fixed_boundary_types:
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
                bccode += "phip:=phi(.)\n"
                bccode += "betac=(1-phip)*rho1\n"
                bccode += "rhom=phip*rho2+betac\n"
                bccode += "vr={}\n".format(r_code)
                bccode += "coef=phip*betac/rhom\n"
                bccode += "r[3] <- sc*((phip*u(.)"
                bccode += "+ coef*vr) dot nor)*vf\n"
                bccode += "r[4] <- sc*rhom*u(.) dot nor*vf\n"
                bccode += "EndIntegral\n"
        elif solver == 'timeDependentLaminar':
            for boundary in boundaries:
                bccode += "Integral(" + boundary + ",\"VlFlx1\",3)\n"
                bccode += "nor:=NormalVector\n"
                bccode += "vf:=VolumeFunction\n"
                bccode += "r[3] <- u(.) dot nor*vf\n"
                bccode += "EndIntegral\n"

        if solver in multiphase_solvers:
            i = 4
        else:
            i = 3
        for boundary in velocityBCs:
            if velocityBCs[boundary] in zero_normal_velocity_types:
                i += 1
                bccode += "Integral(" + boundary + ",\"Lobatto\",2)\n"
                bccode += "nor:=NormalVector\n"
                bccode += "bf:=BasisFunction(V(.))\n"
                bccode += "r[0] <- lambda" + boundary + "(.)*nor[0]*bf\n"
                bccode += "r[1] <- lambda" + boundary + "(.)*nor[1]*bf\n"
                bccode += "r[2] <- lambda" + boundary + "(.)*nor[2]*bf\n"
                bccode += "EndIntegral\n"

                bccode += "Integral(" + boundary + ",\"Lobatto\",2)\n"
                bccode += "nor:=NormalVector\n"
                bccode += "r[" + str(i) +\
                    "] <- (u(.) dot nor)*BasisFunction(Z" + boundary +\
                    "(.))\n"
                bccode += "EndIntegral\n"

        if solver in multiphase_solvers:
            i = 4
        else:
            i = 3
        for boundary in pressureBCs:
            if boundary not in boundaries:
                boundaries.append(boundary)
            if pressureBCs[boundary] not in non_fixed_boundary_types:
                bccode += "Constraint(" + boundary + ",W)\n"
                bccode += " r[" + str(i) + "] <- p(.) - " +\
                    to_numerrin_expression(pressureBCs[boundary][1]) +\
                    "\n"
                bccode += "EndConstraint\n"

        for boundary in velocityBCs:
            if boundary not in boundaries:
                boundaries.append(boundary)
            if velocityBCs[boundary] not in non_fixed_boundary_types:
                velo = to_numerrin_expression(velocityBCs[boundary][1])
                bccode += "Constraint(" + boundary + ",V)\n"
                bccode += " up=u(.)\n"
                bccode += " r[0] <- up[0] - " + velo[0] + "\n"
                bccode += " r[1] <- up[1] - " + velo[1] + "\n"
                bccode += " r[2] <- up[2] - " + velo[2] + "\n"
                bccode += "EndConstraint\n"

        # time loop and initializations
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
        code += "normi=Norm(r)\n"
        code += "If inIt == 1\n"
        code += "  eps=reduc*normi\n"
        code += "EndIf\n"
        code += "? inIt, \":\", normi\n"
        code += "If ((normi < 1.0e-8 || ~(normi > eps)) && inIt >= 2)\n"
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

        # move solver variable values to point values
        for variable in solver_variables[solver]:
            pool_name = name + numname[variable]
            v_dim = variable_dimension[variable]
            if v_dim > 1:
                code += "Constraint(omega," + pool_name + "LS1)\n"
                for i in range(v_dim):
                    code += pool_name + "[" + str(i) + "]<-" +\
                        solver_variable_names[variable] + "[" +\
                        str(i) + "](.)\n"
                code += "EndConstraint\n"

            else:
                code += "Constraint(omega," + pool_name + "LS1)\n"
                code += pool_name + "<-" +\
                    solver_variable_names[variable] + "(.)\n"
                code += "EndConstraint\n"

#        code += "WriteCGNS(\"tulos.cgns\") "+name+",u,p\n"
        return code
