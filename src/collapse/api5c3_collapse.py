import numpy as np

def plotAPI5C3Collapse(axes, grade, limits=(15,50), axialStress=0.0, innerPressure=0.0):

    Sa2Smys = axialStress/grade["yieldStress"]
    SMYSa=(np.sqrt(1-0.75*(Sa2Smys)**2)-.5*Sa2Smys)*grade["yieldStress"]
    _, colLimits = getAPI5C3Params(SMYSa)
    # txt =  '{:<15}{:^5}{:^4}{:^5}'
    # head = '{:^15}{:^14}'
    # print (head.format('TYPE', 'D/t range'))
    # for ct in ('Yield','Plastic','Transition','Elastic'):
    #     print (txt.format('%s:' %ct, '%.2f' %colLimits[ct][0], '-',  '%.2f' %colLimits[ct][1]))

    dummy_pipe = lambda x: {'OD': x*0.5, 'thickness': 0.5,
                            'ovality': 0.0, 'eccentricity': 0.0,
                 }

    slenders = np.linspace(*limits, 30)
    pcol = [DesignAPI5C3(dummy_pipe(x), grade, axialStress=0.0,
                        innerPressure=0.0) for x in slenders]

    axes.plot(slenders, pcol, 'b')

    pmax = max(pcol)
    for regime in ['yield','plastic','transition','elastic']:
        x0 = colLimits[regime][1]
        axes.plot((x0,x0), (0,pmax), '--k')

def verifyAPI5C3Regime(pipe, grade, axialStress=0.0, innerPressure=0.0):
    Sa2Smys = axialStress/grade["yieldStress"]
    SMYSa=(np.sqrt(1-0.75*(Sa2Smys)**2)-.5*Sa2Smys)*grade["yieldStress"]
    _, colLimits = getAPI5C3Params(SMYSa)
    slen = pipe["OD"] / pipe["thickness"]
    for regime in ['yield','plastic','transition','elastic']:
        if colLimits[regime][0] < slen <= colLimits[regime][1]:
             return regime
    return 'elastic'

    # if __name__ != "__main__":



        # import matplotlib.pyplot as plt
        # slen = [i for i in range(10,60,2)]
        # col = {'KLEVER_TAMANO': [0 for i in range(10,60,2)],
        #        'KLEVER_TAMANO_API': [0 for i in range(10,60,2)],
        #        'API5C3 (1962)': [0 for i in range(10,60,2)],
        #        'HUANG GAO': [0 for i in range(10,60,2)],
        #        'TIMOSHENKO': [0 for i in range(10,60,2)],
        #        'ELASTIC': [0 for i in range(10,60,2)],
        #        'PLASTIC': [0 for i in range(10,60,2)],}


        # fig, ax = plt.subplots(1,1)
        # for ov in (0.0,0.2,0.4):
        #   for i, s in enumerate(slen):
        #     dia = 20.
        #     t = dia/s
        #     mat= 80000.
        #     # ov = 0.0
        #     PC = Analytical_pipe_collapse(dia, 88.2, mat, t, OV=ov)
        #     for key in ('KLEVER_TAMANO',):
        #       col[key][i] = PC.collapse[key]
        #   ax.plot(slen, col[key], label=ov)


        # ax.grid(True)
        # ax.legend()
        # plt.show()


def KleverTamanoAPI5C3(pipe, grade, kels=1.089, kyls=0.991,
                               residualStress=0.0, kneedShape=False,
                               axialStress=0.0, innerPressure=0.0, **kwargs):
    hn = 0
    slen=pipe["OD"]/pipe["thickness"]
    if kneedShape:
        hn = 0.017

    Ht=0.127*pipe['ovality'] + 0.0039*pipe['eccentricity'] - 0.44*residualStress + hn
    Ht = max((0,Ht))

    Fa = axialStress*(np.pi*(pipe['OD']-pipe['thickness'])*pipe['thickness'])
    Sa = Fa*slen**2/(np.pi*pipe['OD']**2*(slen-1))
    Szeff = 0.5*(np.sqrt(4*grade['yieldStress']**2-3*axialStress**2)-axialStress)

    # Elastic
    Pe=kels*2*(grade["young"]/(1-grade["poisson"]**2))*(slen**-1)*((slen-1)**-2)
    # Yield
    Py=kyls*2*Szeff*((slen-1)/slen**2)*(1+1.5*(slen-1)**-1)

    # collapse definition based on slenderness ratio
    Pc=((Py+Pe)-((Pe-Py)**2 + 4*Pe*Py*Ht)**0.5)/(2*(1-Ht))
    return Pc

def getAPI5C3Params(SMYSa, **kwargs):

    A = 2.8762+.10679e-5*SMYSa+.2131e-10*SMYSa**2-.53132e-16*SMYSa**3
    B = .026233+.50609e-6*SMYSa
    C = -465.93+.030867*SMYSa-.10483e-7*SMYSa**2+.36989e-13*SMYSa**3
    F = (46.95e6*((3*B/A)/(2+B/A))**3)/(SMYSa*((3*B/A)/(2+B/A)-B/A)*(1-(3*B/A)/(2+B/A))**2)
    G = F*B/A

    # collapse definition based on slenderness ratio
    SlendYP = (np.sqrt((A-2)**2+8*(B+C/SMYSa))+(A-2))/(2*(B+C/SMYSa))
    SlendPT = (SMYSa*(A-F))/(C+SMYSa*(B-G))
    SlendTE = (2+B/A)/(3*B/A)

    params = {'A': A, 'B': B, 'C': C, 'F': F, 'G': G}
    regime_limits = {'yield': [0., SlendYP], 'plastic': [SlendYP, SlendPT],
                     'transition': [SlendPT, SlendTE], 'elastic': [SlendTE, 50.]}
    return params, regime_limits

def DesignAPI5C3(pipe, grade, axialStress=0.0, innerPressure=0.0, **kwargs):
    slen=pipe["OD"]/pipe["thickness"]
    axi_stress_2_yield = axialStress/grade['yieldStress']
    SMYSa=(np.sqrt(1-0.75*(axi_stress_2_yield)**2)
           -0.5*axi_stress_2_yield)*grade['yieldStress']

    params, OD_limits = getAPI5C3Params(SMYSa)

    # Yield Collapse
    if OD_limits['yield'][0] < slen <= OD_limits['yield'][1]:
        Pc = 2*SMYSa*((slen-1)/slen**2)
    elif OD_limits['plastic'][0] < slen <= OD_limits['plastic'][1]:
        Pc = SMYSa*(params['A']/slen-params['B'])-params['C']
    elif OD_limits['transition'][0] < slen <= OD_limits['transition'][1]:
        Pc = SMYSa*(params['F']/slen-params['G'])
    elif OD_limits['elastic'][0] < slen <= OD_limits['elastic'][1]:
        Pc = 46.95e6/(slen*(slen-1)**2)
    else:
        Pc = 46.95e6/(slen*(slen-1)**2)
    # efeitos da pressao interna
    Pc = Pc-(1-2/slen)*innerPressure
    return Pc

