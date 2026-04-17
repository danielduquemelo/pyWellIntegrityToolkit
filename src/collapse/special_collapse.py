def Huang_Gao(pipe, grade, **kwargs):
    slen=pipe["OD"]/pipe["thickness"]
    t = pipe['thickness']*(0.187+0.813*(1-pipe['eccentricity']/2)**3)**(1/3)
    # Er = E*(1-tp/t)
    Pe = 2*(grade["young"]/(1-grade["poisson"]**2))*slen**-1*(slen-1)**-2
    OV_crit = 2.
    PeOV = Pe*(1-pipe['ovality']/OV_crit)

    Sp=grade['yieldStress']
    Pp=2.*Sp*((slen-1)/slen**2)
    delta_ov = pipe['ovality']/100.
    aux = 1+Pp/Pe+3*delta_ov*grade['yieldStress']/Pp
    PpOV=2.*Pp*(aux+np.sqrt((aux)**2-4*Pp/Pe))**-1
    k=2.*(slen-1)/(slen**2-2*slen+2)
    Pc=1./((1./(1-k)*PpOV)**-1+(k*((k-1)*PeOV)**-1))
    if Pc > Pe:
        Pc=Pe
    return Pc

