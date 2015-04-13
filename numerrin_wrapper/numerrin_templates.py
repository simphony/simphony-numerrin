""" numerrin_templates

Templates for Numerrin solver -codes

"""

from simphony.core.cuba import CUBA

liccode =\
          """
30820275020100300D06092A864886F70D01010105000482025F3082025B02010002818100A3872911FFFFA0AEA14B0BB5B5ECE4960FFB3958F2D6754B891E4E3CCE343E9EEC8BF4DACA30A6580D3362E662479199D813A6EAD587D19758730AD4E519EBE270B207F657DAAB44105DDC94763E2B2E7A476AA182E0861FF347224880AA1AE456593FF7F92C55078935BB917559B29948E98DDAA32F5821D367965DB61AA7870201110281800334D8A5FFFFFE218AB12862EF7D1D9482D2BAD9965484CF48F68E15454C518AA543FFC80E00F433EC2E2F1D9D88EEC6C80062A53B670E261AD5144A72EC6E096D9B071259CE0B6911A94E8D9B8F687B54BF38A72BAC04CF1FA7043019A0846D5BBE53F0801315E33E8D8FF147B83AA3586FCE94B191EDD0D66954030E5D83E1024100DF8608BD9BC506F652DEA6B0783882BE0896AEFFA2AC08DCFE04F36D9FD8F9C8A28E26208A544B5B85E8CE195D200087E907BBD505D35BBDEE2256C9C3D11A99024100BB499690D8095E5F38C48FAE0073D7DE8F9872542CEF87FFA6FC5945C5D6BF526CE060EDEB0AAD668D194066CE860386C19BAA663D499BC92E4982F815A8471F024100B8140732BC8423D9E9E4894608A702422530CC5A0D7E9DE32B8B9B4B3858553BD129C50BBD365C2D411A1323F256970683AC0418D79F00420F6792C446E8704102401608A84D4697B0BFE88F986ED2E073BFD4A885EBC90D1F0F0496289ECBFB259139FC47A3851050A2A73025B1BDF1A60FDA8AC8C0BBEA8ACC5FCC69C2D55F176D0241008F243984C82285014EB8AE8AEECA22C7A8508B88C69892C909AF74ECED21B6B172B025484E8B7B7A8BE38934F28C50F48F117A3C8C5CC1B0885E0054CE53F314
          """

numvariables = ["Velocity",
                "Pressure"]

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
           CUBA.PRESSURE: "Pressure"}

functions = {'stabilizedLaminarNS3D':
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

             """}

solverFrames = {'stabilizedLaminarNS3D':
                """
dim=3
A=Derivative(r,q)
  A=0.0
  r=0.0
  Integral(omega,"Gauss",{integrationDegree})
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

                """}
