#!/bin/env python

""" tests/test_radiation.py:  
    2021-05-04, MvdS: initial version.
"""


import solarenergy as se
from solarenergy import d2r,r2d


def main():
    test_Perez()
    test_Bird()

    

def test_Perez():
    DoY = 94
    surfIncl = 45*d2r
    theta = 45*d2r
    
    alt = 50*d2r
    
    Gbeam_n = 600
    Gdif_hor = 300
    
    Gdif_inc = se.diffuse_radiation_projection_perez87(DoY, alt, surfIncl, theta, Gbeam_n,Gdif_hor)
    
    print("%4i  %7.1f%7.1f%7.1f  %8.1f%8.1f%8.1f" % (DoY, alt*r2d, surfIncl*r2d, theta*r2d,
                                                     Gbeam_n,Gdif_hor, Gdif_inc ))  # , Gdif_inc_cs, Gdif_inc_hz))
    
    # For pytest:
    assert Gdif_inc > 250
    assert Gdif_inc < 350
    
    return


def test_Bird():
    alt=40*d2r
    
    Io=1353
    Rsun=1
    
    Press=1013
    
    Uo=0.34
    Uw=1.42
    
    Ta5=0.2661
    Ta3=0.3538
    
    Ba=0.84
    K1=0.1
    
    Rg=0.2
    
    Itot, Idir, Idif, Igr = se.clearsky_bird(alt, Io,Rsun, Press, Uo,Uw, Ta5,Ta3, Ba,K1, Rg)
    
    print("%7.1f %8.1f%8.4f %8.1f %8.3f%8.3f %8.4f%8.4f %8.3f%8.3f %8.1f %8.1f%8.1f%8.1f%8.1f" %
          (alt*r2d, Io,Rsun, Press, Uo,Uw, Ta5,Ta3, Ba,K1, Rg,  Itot, Idir, Idif, Igr))
    
    assert Itot > 550
    assert Itot < 700
    
    assert Idir > 400
    assert Idir < 500
    
    assert Idif > 100
    assert Idif < 200
    
    assert Igr  > 8
    assert Igr  < 20
    
    return



if(__name__ == "__main__"): main()
