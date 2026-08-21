import numpy as np
in2m  = lambda x: x*(25.4/1000.0)
ft2m = lambda x: x*0.3048
lb2kg = lambda x: x*0.453592
# psi2pa = lambda x: x*6894.76
# pa2psi = lambda x: x/6894.76
# m2in = lambda x: x/(25.4/1000.0)
ppg2kgm3 = lambda x: x*119.826427
# days2sec = lambda x: x*86400
grav = 9.81

def buoyancy_stress(phase, depth):
        h0 = phase['shoe'] - depth
        h1 = phase['toc'] #-phase['LDA']
        if phase['cement plug height'] > 0:
            h2 = phase['shoe'] - phase['cement plug height'] - phase['toc']
            h3 = phase['cement plug height']
        else:
            h2 = phase['shoe'] - phase['toc']
            h3 = 0.0

        area = (np.pi/4)*(phase['od']**2 - (phase['od']-2*phase['thickness'])**2)
        rhoRev = phase['nw']*lb2kg(1)/(ft2m(1)*in2m(1)**2*area)
        rhoFld = ppg2kgm3(phase['mud_weight1'])
        rhoCem1 = ppg2kgm3(phase['cement weight'])
        rhoCem2 = ppg2kgm3(phase['cement plug weight'])
        
        wcsg = rhoRev*grav*h0
        wmud1 = rhoFld*grav*h1
        wcem1 = rhoCem1*grav*h2
        wcem2 = rhoCem2*grav*h3
        smud1 = -wcsg+wmud1+wcem1+wcem2
        pipeStress = smud1*1e-6
        if depth < phase['toc']:
            cemStress = None
        elif depth < (phase['shoe'] - phase['cement plug height']):
            wcem = rhoCem1*grav*(depth - phase['toc'])
            cemStress = (wmud1+wcem)*1e-6
        else:
            wcem = rhoCem2*grav*(depth - (phase['shoe'] - phase['cement plug height']))
            cemStress = (+wmud1+wcem1+wcem)*1e-6
        # mud1 = ppg2kgm3(phase['mud_weight1'])*grav*depth*1e-6
        # mud2 = ppg2kgm3(phase['MUD_WEIGHT2'])*grav*depth*1e-6
        mud1 = phase['mud_weight1']
        mud2 = phase['mud_weight2']
        
        if depth > phase['shoe']:
            return {'PIPE':0.0, 'CEMENT':0.0, 'FLUID': 0.0}
        
        return {'PIPE':pipeStress, 'CEMENT':cemStress, 'FLUID': mud1}