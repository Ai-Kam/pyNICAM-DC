#-------------------------------------------------------------------------------
#> Module generic tool
#
# @par Description
#         This module is for the generic subroutine, e.g., global mean.
#
# @author NICAM developers

import numpy as np
from mod_adm import adm

class Gtl:

    _instance = None

    def __init__(self):
        pass


    def GTL_max(self, var, var_pl, kdim, kstart, kend, cnst, comm, rdtype):
        """Compute the global maximum value in the given 3D array."""

        vmax = -cnst.CONST_HUGE

        # Loop over main grid
        for l in range(adm.ADM_lall):
            for k in range(kstart, kend + 1):
                for j in range(adm.ADM_gmin, adm.ADM_gmax + 1):
                    for i in range(adm.ADM_gmin, adm.ADM_gmax + 1):
                        vmax = max(vmax, var[i, j, k, l])

        # If ADM_have_pl is True, check additional values
        if adm.ADM_have_pl:
            for l in range(adm.ADM_lall_pl):
                for k in range(kstart, kend + 1):
                    vmax = max(vmax, var_pl[adm.ADM_gslf_pl, k, l])

        # Perform global max communication across processes
        vmax_g = comm.Comm_Stat_max(vmax,rdtype)
        
        return vmax_g
    
    def GTL_min(self, var, var_pl, kdim, kstart, kend, cnst, comm, rdtype, nonzero=False):
        """Compute the global minimum value in the given 3D array."""

        vmin = cnst.CONST_HUGE

        if nonzero:
            #vmin = cnst.CONST_HUGE

            # Loop over main grid
            for l in range(adm.ADM_lall):
                for k in range(kstart, kend + 1):
                    for j in range(adm.ADM_gmin, adm.ADM_gmax + 1):
                        for i in range(adm.ADM_gmin, adm.ADM_gmax + 1):
                            val = var[i, j, k, l]
                            if 0.0 < val < vmin:
                                vmin = val
                            
                            #vmin = min(vmin, var[i, j, k, l])

            # If ADM_have_pl is True, check additional values
            if adm.ADM_have_pl:
                for l in range(adm.ADM_lall_pl):
                    for k in range(kstart, kend + 1):
                        val = var_pl[adm.ADM_gslf_pl, k, l]
                        if 0.0 < val < vmin:
                            vmin = val

        else:  # If nonzero is False, find the absolute minimum
            for l in range(adm.ADM_lall):
                for k in range(kstart, kend + 1):
                    for j in range(adm.ADM_gmin, adm.ADM_gmax + 1):
                        for i in range(adm.ADM_gmin, adm.ADM_gmax + 1):
                            vmin = min(vmin, var[i, j, k, l])

            if adm.ADM_have_pl:
                for l in range(adm.ADM_lall_pl):
                    for k in range(kstart, kend + 1):
                        vmin = min(vmin, var_pl[adm.ADM_gslf_pl, k, l])

        # Perform global min communication across processes
        vmin_g = comm.Comm_Stat_min(vmin,rdtype)
        
        return vmin_g