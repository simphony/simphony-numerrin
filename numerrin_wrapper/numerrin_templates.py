""" numerrin_templates

Templates for Numerrin solver -codes

"""

from simphony.core.cuba import CUBA
from .cuba_extension import CUBAExt
import re

liccode =\
    """
30820275020100300D06092A864886F70D01010105000482025F3082025B02010002818100A3872911FFFFA0AEA14B0BB5B5ECE4960FFB3958F2D6754B891E4E3CCE343E9EEC8BF4DACA30A6580D3362E662479199D813A6EAD587D19758730AD4E519EBE270B207F657DAAB44105DDC94763E2B2E7A476AA182E0861FF347224880AA1AE456593FF7F92C55078935BB917559B29948E98DDAA32F5821D367965DB61AA7870201110281800334D8A5FFFFFE218AB12862EF7D1D9482D2BAD9965484CF48F68E15454C518AA543FFC80E00F433EC2E2F1D9D88EEC6C80062A53B670E261AD5144A72EC6E096D9B071259CE0B6911A94E8D9B8F687B54BF38A72BAC04CF1FA7043019A0846D5BBE53F0801315E33E8D8FF147B83AA3586FCE94B191EDD0D66954030E5D83E1024100DF8608BD9BC506F652DEA6B0783882BE0896AEFFA2AC08DCFE04F36D9FD8F9C8A28E26208A544B5B85E8CE195D200087E907BBD505D35BBDEE2256C9C3D11A99024100BB499690D8095E5F38C48FAE0073D7DE8F9872542CEF87FFA6FC5945C5D6BF526CE060EDEB0AAD668D194066CE860386C19BAA663D499BC92E4982F815A8471F024100B8140732BC8423D9E9E4894608A702422530CC5A0D7E9DE32B8B9B4B3858553BD129C50BBD365C2D411A1323F256970683AC0418D79F00420F6792C446E8704102401608A84D4697B0BFE88F986ED2E073BFD4A885EBC90D1F0F0496289ECBFB259139FC47A3851050A2A73025B1BDF1A60FDA8AC8C0BBEA8ACC5FCC69C2D55F176D0241008F243984C82285014EB8AE8AEECA22C7A8508B88C69892C909AF74ECED21B6B172B025484E8B7B7A8BE38934F28C50F48F117A3C8C5CC1B0885E0054CE53F314
    """

numvariables = [CUBA.VELOCITY, CUBA.PRESSURE, CUBA.VOLUME_FRACTION]

numname = {CUBA.RADIUS: "Radius",
           CUBA.MASS: "Mass",
           CUBA.VOLUME: "Volume",
           CUBA.ANGULAR_VELOCITY: "AngularVelocity",
           CUBA.ANGULAR_ACCELERATION: "AngularAcceleration",
           CUBA.DYNAMIC_VISCOSITY: "Viscosity",
           CUBA.DIFFUSION_COEFFICIENT: "DiffusionCoefficient",
           CUBA.FRICTION_COEFFICIENT: "FrictionCoefficient",
           CUBA.CONTANCT_ANGLE: "ContactAngle",
           CUBA.TIME_STEP: "TimeStep",
           CUBA.FORCE: "Force",
           CUBA.TORQUE: "Torque",
           CUBA.DENSITY: "Density",
           CUBA.YOUNG_MODULUS: "YoungModulus",
           CUBA.POISSON_RATIO: "PoissonRatio",
           CUBA.NUMBER_OF_TIME_STEPS: "NumberOfTimeSteps",
           CUBA.VELOCITY: "Velocity",
           CUBA.PRESSURE: "Pressure",
           CUBA.VOLUME_FRACTION: "VolumeFraction",
           CUBAExt.SURFACE_TENSION: "SurfaceTension",
           CUBAExt.PHASE_LIST: "PhaseList",
           CUBA.ANGULAR_VELOCITY: "RelativeVelocity",
           CUBA.ACCELERATION: "Sigma",
           CUBA.ANGULAR_ACCELERATION: "Strain",
           CUBAExt.RELATIVE_VELOCITY_MODEL: "RelativeVelocityModel",
           CUBAExt.RELATIVE_VELOCITY_MODEL_COEFFS:
               "RelativeVelocityModelCoeffs",
           CUBAExt.STRESS_MODEL: "StressModel",
           CUBAExt.EXTERNAL_BODY_FORCE_MODEL: "ExternalBodyForceModel",
           CUBAExt.EXTERNAL_BODY_FORCE_MODEL_COEFFS:
               "ExternalBodyForceModelCoeffs"
           }

multiphase_solvers = ("VOFLaminar", "mixtureModelLaminar")

timeLoop = {'steadyStateLaminar':
            """
For iteration=1:1
             """,
            'timeDependentLaminar':
                """
For iteration=1:NumberOfTimeSteps
    curTime +=TimeStep
    uoo=uo
    uo=u
    For id=0:2
     u[id][[:]] += uo[id][[:]]
     u[id][[:]] -= uoo[id][[:]]
    EndFor

             """,
            'VOFLaminar':
                """
For iteration=1:NumberOfTimeSteps
    curTime +=TimeStep
    uo=u
    phio=phi

             """,
            'mixtureModelLaminar':
                """
For iteration=1:NumberOfTimeSteps
    curTime +=TimeStep
    uo=u
    phio=phi
             """
            }

functionSpaces = {'steadyStateLaminar':
                  """
V=Space(omega,\"Lagrange\",1)
W=Space(omega,\"Lagrange\",1)
             """,
                  'timeDependentLaminar':
                      """
V=Space(omega,\"Split\",2)
W=Space(omega,\"Lagrange\",1)
             """,
                  'VOFLaminar':
                      """
V=Space(omega,\"Lagrange\",2)
W=Space(omega,\"Lagrange\",1)
             """,
                  'mixtureModelLaminar':
                      """
V=Space(omega,\"Lagrange\",2)
W=Space(omega,\"Lagrange\",1)
             """
                  }

associations = {'steadyStateLaminar':
                """
u[0:2] in V
p in W
q[0:2]->u
q[3]->p
r:=q
             """,
                'timeDependentLaminar':
                    """
u[0:2] in V
p in W
q[0:2]->u
q[3]->p
r:=q
uo=u
             """,
                'VOFLaminar':
                    """
u[0:2] in V
phi in W
p in W
q->u
q[3]->phi
q[4]->p
r:=q
pdt=1.0/TimeStep
uo=u
rho1={phase1_name}Density
rho2={phase2_name}Density
mu1={phase1_name}Viscosity
mu2={phase2_name}Viscosity
SurfaceTension={phase1_name}{phase2_name}SurfaceTension
sc=1.0e+3

             """,
                'mixtureModelLaminar':
                    """
u[0:2] in V
phi in W
p in W
q->u
q[3]->phi
q[4]->p
r:=q
pdt=1.0/TimeStep
uo=u
rho1={phase1_name}Density
rho2={phase2_name}Density
mu1={phase1_name}Viscosity
mu2={phase2_name}Viscosity
sc=1.0e+3

             """
                }

functions = {'steadyStateLaminar':
             """
Subroutine StabFF(u,rho,mu,tau,delta)
  hk=ElementSize
  unorm=norm(u)
  re=min(0.5*unorm*hk*rho/mu,1.0)
  If unorm > 1.0e-10
    tau=0.5*hk*re/unorm
    delta=unorm*hk*re
  Else
    tau=hk
    delta=hk
  EndIf
EndSubroutine

             """,
             'timeDependentLaminar':
                 """
Subroutine upwindv(v,rho,mu,nor,vf) result(vup)
  vn:=v(.) dot nor
  If vn > 0.0
    For i=0:Size(vf)-1
      If vf[i] > 0.1
        j=i
        Exit
      EndIf
    EndFor
  Else
    For i=0:Size(vf)-1
      If vf[i] < -0.1
        j=i
        Exit
      EndIf
    EndFor
  EndIf
  alpha:=Norm(v(.))*ElementSize*rho/(2*mu)
  If alpha > 1.0e-6
    ksi=1/Tanh(alpha)-1/alpha
  Else
    ksi=0.0
  EndIf
  For i=0:Size(v)-1
    vup[i]=ksi*BasisCoefficients(v[i](.))[j]+(1-ksi)*v[i](.)
  EndFor
EndSubroutine

             """,
             'VOFLaminar':
                 """
Subroutine upwindv(v,rho,mu,nor,vf) result(vup)
  vn:=v(.) dot nor
  If vn > 0.0
    For i=0:Size(vf)-1
      If vf[i] > 0.1
        j=i
        Exit
      EndIf
    EndFor
  Else
    For i=0:Size(vf)-1
      If vf[i] < -0.1
        j=i
        Exit
      EndIf
    EndFor
  EndIf
  alpha:=rho*Norm(v(.))*ElementSize/(2*mu)
  If alpha > 1.0e-6
    ksi=1/Tanh(alpha)-1/alpha
  Else
    ksi=0.0
  EndIf
  For i=0:Size(v)-1
    vup[i]=ksi*BasisCoefficients(v[i](.))[j]+(1-ksi)*v[i](.)
  EndFor
EndSubroutine

Subroutine upwindphi(v,nor,phi,vf) Result(phiu)
  vn:=v(.) dot nor
  If vn > 0.0
    For i=0:Size(vf)-1
      If vf[i] > 0.1
        up=i
        Exit
      EndIf
    EndFor
  Else
    For i=0:Size(vf)-1
      If vf[i] < -0.1
        up=i
        Exit
      EndIf
    EndFor
  EndIf

  phiu=BasisCoefficients(phi(.))[up]
EndSubroutine

             """,
             'mixtureModelLaminar':
                 """
Subroutine upwindv(v,rho,mu,nor,vf) result(vup)
  vn:=v(.) dot nor
  If vn > 0.0
    For i=0:Size(vf)-1
      If vf[i] > 0.1
        j=i
        Exit
      EndIf
    EndFor
  Else
    For i=0:Size(vf)-1
      If vf[i] < -0.1
        j=i
        Exit
      EndIf
    EndFor
  EndIf
  alpha:=rho*Norm(v(.))*ElementSize/(2*mu)
  If alpha > 1.0e-6
    ksi=1/Tanh(alpha)-1/alpha
  Else
    ksi=0.0
  EndIf
  For i=0:Size(v)-1
    vup[i]=ksi*BasisCoefficients(v[i](.))[j]+(1-ksi)*v[i](.)
  EndFor
EndSubroutine

Subroutine upwindphi(v,nor,phi,vf) Result(phiu)
  vn:=v(.) dot nor
  If vn > 0.0
    For i=0:Size(vf)-1
      If vf[i] > 0.1
        up=i
        Exit
      EndIf
    EndFor
  Else
    For i=0:Size(vf)-1
      If vf[i] < -0.1
        up=i
        Exit
      EndIf
    EndFor
  EndIf

  phiu=BasisCoefficients(phi(.))[up]
EndSubroutine

             """
             }

solverFrames = {'steadyStateLaminar':
                """
dim=3
A=Derivative(r,q)
  A=0.0
  r=0.0
  Integral(omega,"Gauss",3)
    up=u(.)
    gup=Grad(u(.))
    pp=p(.)
    gpp=Grad(p(.))

    % The second invariance of velocity
    uinv=pp
    uinv=0.0
    For j=0:dim-1
      For i=j:dim-1
        If i == j
          uinv += 2.0*gup[i,i]^2
        Else
          uinv += gup[i,j]*(gup[i,j]+gup[j,i])
        EndIf
      EndFor
    EndFor


    % Franca-Frey
    tmu=2.0*Viscosity
    StabFF(up,Density,tmu,tau,delta)

    phi=BasisFunction(V)
    gphi=BasisGradient(V)
    pd=up dot gphi
    phis=tau*pd


    % Stresses and residuals
    For i=0:dim-1
      For j=0:dim-1
        tauT[i,j]=Viscosity*(gup[i,j]+gup[j,i])
      EndFor
    EndFor
    For i=0:dim-1
      conv[i]=Density*(up dot gup[:,i])
      res[i]=conv[i]+gpp[i]
    EndFor
    resm=Density{{}}**gup{{i,i}}

    hk=ElementSize

    % Momentum
    For i=0:dim-1
      r[i] <- (tauT[i,:] dot gphi)+conv[i]*phi-pp*gphi[i,:]
              +delta*resm*gphi[i,:]+res[i]*phis
    EndFor

    % Continuity
    r[dim] <- -resm*phi-tau*(res dot gphi)

  EndIntegral

                """,
                'timeDependentLaminar':
                    """
    A=Derivative(r,q)
    A=0.0
    r=0.0
    Integral(omega,"VlSrc2",1)
      vf:=VolumeFunction
      up0=BasisCoefficients(u[0](.)) dot vf
      up1=BasisCoefficients(u[1](.)) dot vf
      up2=BasisCoefficients(u[2](.)) dot vf
      uop0=BasisCoefficients(uo[0](.)) dot vf
      uop1=BasisCoefficients(uo[1](.)) dot vf
      uop2=BasisCoefficients(uo[2](.)) dot vf
      uoop0=BasisCoefficients(uoo[0](.)) dot vf
      uoop1=BasisCoefficients(uoo[1](.)) dot vf
      uoop2=BasisCoefficients(uoo[2](.)) dot vf
      r[0] <- Density*0.5/TimeStep*(uoop0-4*uop0+3*up0)*vf
      r[1] <- Density*0.5/TimeStep*(uoop1-4*uop1+3*up1)*vf
      r[2] <- Density*0.5/TimeStep*(uoop2-4*uop2+3*up2)*vf
    EndIntegral

    Integral(omega,"VlFlx2",3)
      nor:=NormalVector
      vf:=VolumeFunction
      gup=Grad(u(.))

      tau:=Viscosity*(gup+gup')
      uu:=upwindv(u,Density,Viscosity,nor,vf)
      r[0] <- ((Density*uu[0]*u(.)-tau[:,0]) dot nor+p(.)*nor[0])*vf
      r[1] <- ((Density*uu[1]*u(.)-tau[:,1]) dot nor+p(.)*nor[1])*vf
      r[2] <- ((Density*uu[2]*u(.)-tau[:,2]) dot nor+p(.)*nor[2])*vf
    EndIntegral
    Integral(omega,"VlFlx1",3)
      nor:=NormalVector
      vf:=VolumeFunction
      r[3] <- u(.) dot nor*vf
    EndIntegral

             """,
                'VOFLaminar':
                    """
    A=Derivative(r,q)
    A=0.0
    r=0.0
    % Momentum time derivative
    ? "time der mom"
    Integral(omega,"VlSrc2",3)
      vf:=VolumeFunction
      rhop=phi(.)*rho2+(1-phi(.))*rho1
      rhopo=phio(.)*rho2+(1-phio(.))*rho1
      r[0] <- sc*pdt*(rhop*u[0](.)-rhopo*uo[0](.))*vf
      r[1] <- sc*pdt*(rhop*u[1](.)-rhopo*uo[1](.))*vf
      r[2] <- sc*pdt*(rhop*u[2](.)-rhopo*uo[2](.))*vf
    EndIntegral
    % Volume fraction time derivative
    ? "time der cont"
    Integral(omega,"VlSrc1",1)
      vf:=VolumeFunction
      phip:=BasisCoefficients(phi(.)) dot vf
      phiop:=BasisCoefficients(phio(.)) dot vf
      r[3] <- sc*pdt*(phip-phiop)*vf
    EndIntegral
    % Momentum flux
    ? "Mom flux"
    Integral(omega,"VlFlx2",3)
      nor:=NormalVector
      vf:=VolumeFunction
      gup=Grad(u(.))
      rhoEff=phi(.)*rho2+(1-phi(.))*rho1
      muEff=phi(.)*mu2+(1-phi(.))*mu1
      gpp=Grad(phi(.))
      ngp=Norm(gpp)
      % Surface tension
      If ngp > 1.0e-6
        T[0,0]=ngp-gpp[0]*gpp[0]/ngp
        T[0,1]=-gpp[0]*gpp[1]/ngp
        T[0,2]=-gpp[0]*gpp[2]/ngp
        T[1,0]=-gpp[1]*gpp[0]/ngp
        T[1,1]=ngp-gpp[1]*gpp[1]/ngp
        T[1,2]=-gpp[1]*gpp[2]/ngp
        T[2,0]=-gpp[2]*gpp[0]/ngp
        T[2,1]=-gpp[2]*gpp[1]/ngp
        T[2,2]=ngp-gpp[2]*gpp[2]/ngp
        T *= SurfaceTension
      Else
        T[0:2,0:2]=0.0
      EndIf
      tau:=muEff*(gup+gup')
      uu:=upwindv(u,rhoEff,muEff,nor,vf)
      r[0] <- sc*((rhoEff*uu[0]*u(.)-tau[:,0]-T[:,0]) dot nor+p(.)*nor[0])*vf
      r[1] <- sc*((rhoEff*uu[1]*u(.)-tau[:,1]-T[:,1]) dot nor+p(.)*nor[1])*vf
      r[2] <- sc*((rhoEff*uu[2]*u(.)-tau[:,2]-T[:,2]) dot nor+p(.)*nor[2])*vf
      Clear T
    EndIntegral

    Integral(omega,"VlFlx1",3)
      nor:=NormalVector
      vf:=VolumeFunction
      phiu:=upwindphi(u,nor,phi,vf)
      r[3] <- sc*phiu*(u(.) dot nor)*vf
      r[4] <- sc*u(.) dot nor*vf
    EndIntegral

             """,
                'mixtureModelLaminar':
                    """
    A=Derivative(r,q)
    A=0.0
    r=0.0
    % Momentum time derivative
    ? "time der mom"
    Integral(omega,"VlSrc2",3)
      vf:=VolumeFunction
      rhop=phi(.)*rho2+(1-phi(.))*rho1
      rhopo=phio(.)*rho2+(1-phio(.))*rho1
%      gradPhi = Grad(phi(.))
%      gradRhom = rho2*gradPhi-rho1*gradPhi
      r[0] <- sc*pdt*(rhop*u[0](.)-rhopo*uo[0](.))*vf %+ sc*G[0]*gradRhom[0]*vf
      r[1] <- sc*pdt*(rhop*u[1](.)-rhopo*uo[1](.))*vf %+ sc*G[1]*gradRhom[1]*vf
      r[2] <- sc*pdt*(rhop*u[2](.)-rhopo*uo[2](.))*vf %+ sc*G[2]*gradRhom[2]*vf
    EndIntegral
    ? "time der cont"
    % Volume fraction time derivative
    Integral(omega,"VlSrc1",1)
      vf:=VolumeFunction
      phip:=BasisCoefficients(phi(.)) dot vf
      phiop:=BasisCoefficients(phio(.)) dot vf
      r[3] <- sc*pdt*(phip-phiop)*vf
    EndIntegral
    % Momentum flux
    Integral(omega,"VlFlx2",3)
      nor:=NormalVector
      vf:=VolumeFunction
      gup=Grad(u(.))
      phip:=phi(.)
      rhom=phip*rho2+(1-phip)*rho1
      muEff=phip*mu2+(1-phip)*mu1

      tau:=muEff*(gup+gup')
      uu:=upwindv(u,rhom,muEff,nor,vf)
      cd=phip*rho2/rhom
      udm=rho1/rhom*{relative_velocity}
      % normaalijännitys myös mukaan !!!!!!!
      SigmaPrime:={sigma}-tau
      tauDm0:=rhom*cd*(1-cd)*udm[0]*udm+rhom*uu[0]*u(.)-tau[:,0]-SigmaPrime[:,0]
      tauDm1:=rhom*cd*(1-cd)*udm[1]*udm+rhom*uu[1]*u(.)-tau[:,1]-SigmaPrime[:,1]
      tauDm2:=rhom*cd*(1-cd)*udm[2]*udm+rhom*uu[2]*u(.)-tau[:,2]-SigmaPrime[:,2]
      r[0] <- sc*(tauDm0 dot nor+p(.)*nor[0])*vf
      r[1] <- sc*(tauDm1 dot nor+p(.)*nor[1])*vf
      r[2] <- sc*(tauDm2 dot nor+p(.)*nor[2])*vf
    EndIntegral
   % continuity flux
   Integral(omega,"VlFlx1",3)
      nor:=NormalVector
      vf:=VolumeFunction
      phiu:=upwindphi(u,nor,phi,vf)
      phip:=phi(.)
      rhom=phip*rho2+(1-phi(.))*rho1
      udm=rho1/rhom*{relative_velocity}
      cd=phip*rho1/rhom
      r[3] <- sc*phiu*((u(.) + (1-cd)*udm) dot nor)*vf
      r[4] <- sc*u(.) dot nor*vf
    EndIntegral

                   """

                }


def get_numerrin_solver(CM):
    GE = CM[CUBAExt.GE]
    if CUBAExt.VOF_MODEL in GE:
        solver = "VOFLaminar"
    elif CUBAExt.MIXTURE_MODEL in GE:
        solver = "mixtureModelLaminar"
    elif CUBAExt.LAMINAR_MODEL in GE:
        solver = "timeDependentLaminar"
    else:
        error_str = "GE does not define supported solver: GE = {}"
        raise NotImplementedError(error_str.format(GE))
    return solver


def to_numerrin_expression(expr):

    if isinstance(expr, list) or isinstance(expr, tuple):
        return_value = []
        for value in expr:
            return_value.append(to_numerrin_expression(value))
        return return_value

    return re.sub('(e|E)\+0', 'e+', re.sub('(e|E)\-0', 'e-',
                                           '{:.5e}'.format(expr)))


def relative_velocity_code(SPExt):

    if CUBAExt.RELATIVE_VELOCITY_MODEL in SPExt:
        rv = "RelativeVelocity"
        if SPExt[CUBAExt.RELATIVE_VELOCITY_MODEL] == 'simple':
            relative_velocity = "V0" + rv + "ModelCoeffs*10.0^(-" + "a" + rv\
                + "ModelCoeffs*Max(phip,0))"
        else:
            relative_velocity = rv
        return relative_velocity
    else:
        error_str = "Relative velocity model not specified"
        raise ValueError(error_str)


def mixture_model(SPExt):

    relative_velocity = relative_velocity_code(SPExt)

    if CUBAExt.STRESS_MODEL in SPExt:
        if SPExt[CUBAExt.STRESS_MODEL] == "standard":
            sigma = "tau"
        else:
            sigma = "Sigma(.)"
    else:
        error_str = "Stress model (standard or fromMesoscale) not specified"
        raise ValueError(error_str)

    return solverFrames["mixtureModelLaminar"].format(
        relative_velocity=relative_velocity,
        sigma=sigma)


def external_body_force_model(SPExt):

    if CUBAExt.EXTERNAL_BODY_FORCE_MODEL in SPExt:
        if SPExt[CUBAExt.EXTERNAL_BODY_FORCE_MODEL] == 'gravitation':
            g = SPExt[CUBAExt.EXTERNAL_BODY_FORCE_MODEL_COEFFS]["g"]
            return "G[0]=" + str(g[0]) + "\nG[1]=" + str(g[1]) + "\nG[2]="\
                + str(g[2]) + "\n"

    return "G[0]=0.0" + "\nG[1]=0.0" + "\nG[2]=0.0\n"
