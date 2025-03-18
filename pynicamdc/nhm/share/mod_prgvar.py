import toml
import numpy as np
#from mpi4py import MPI
from mod_adm import adm
from mod_stdio import std
from mod_process import prc
#from mod_prof import prf


class Prgv:
    
    _instance = None
    
    # --- Public Variables ---
    PRG_var = None  # Equivalent to allocatable array PRG_var(:,:,:,:)
    DIAG_var = None  # Equivalent to allocatable array DIAG_var(:,:,:,:)

    restart_input_basename = ""  
    restart_output_basename = ""

    # --- Private Variables ---
    PRG_var_pl = None  # Equivalent to private allocatable array PRG_var_pl(:,:,:,:)
    DIAG_var_pl = None  # Equivalent to private allocatable array DIAG_var_pl(:,:,:,:)

    TRC_vmax_input = 0  # Number of input tracer variables

    layername = ""       # Equivalent to character(len=H_SHORT)
    input_io_mode = "ADVANCED"
    output_io_mode = "ADVANCED"
    allow_missingq = False  # Equivalent to logical variable

    restart_ref_basename = ""
    ref_io_mode = "ADVANCED"
    verification = False  # Equivalent to logical variable


    def __init__(self):
        pass

    def prgvar_setup(self, fname_in, rcnf, rdtype):

        input_basename    = ''
        output_basename   = 'restart'
        ref_basename      = 'reference'
        restart_layername = ''

        TRC_vmax_input = rcnf.TRC_vmax

        if std.io_l: 
            with open(std.fname_log, 'a') as log_file:
                print("+++ Module[prgvar]/Category[nhm share]", file=log_file)        
                print(f"*** input toml file is ", fname_in, file=log_file)
 
        with open(fname_in, 'r') as  file:
            cnfs = toml.load(file)

        if 'restartparam' not in cnfs:
            with open(std.fname_log, 'a') as log_file:
                print("*** restartparam not found in toml file! Use default.", file=log_file)
                #prc.prc_mpistop(std.io_l, std.fname_log)

        else:
            cnfs = cnfs['restartparam']
            input_io_mode     = cnfs['input_io_mode']
            input_basename    = cnfs['input_basename']
            output_io_mode    = cnfs['output_io_mode']
            output_basename   = cnfs['output_basename']
            restart_layername = cnfs['restart_layername']

        if std.io_nml: 
            if std.io_l:
                with open(std.fname_log, 'a') as log_file: 
                    print(cnfs,file=log_file)

        self.restart_input_basename  = input_basename
        self.restart_output_basename = output_basename
        self.restart_ref_basename    = ref_basename
        self.layername               = restart_layername
        self.input_io_mode           = input_io_mode
        self.output_io_mode          = output_io_mode

        if std.io_l:
            with open(std.fname_log, 'a') as log_file:
                print("", file=log_file)
                print(f"*** io_mode for restart, input : {self.input_io_mode.strip()}", file=log_file)
                
        valid_input_modes = {"json", "POH5", "ADVANCED", "IDEAL", "IDEAL_TRACER"}
        if input_io_mode not in valid_input_modes:
            print("xxx [prgvar] Invalid input_io_mode. STOP.")
            prc.prc_mpistop(std.io_l, std.fname_log)

        if std.io_l:
            with open(std.fname_log, 'a') as log_file:
                print(f"*** io_mode for restart, output: {output_io_mode.strip()}", file=log_file)

        valid_output_modes = {"POH5", "ADVANCED"}
        if output_io_mode not in valid_output_modes:
            print("xxx [prgvar] Invalid output_io_mode. STOP")
            prc.prc_mpistop(std.io_l, std.fname_log)

        if self.allow_missingq:
            if std.io_l:
                with open(std.fname_log, 'a') as log_file:
                    print("*** Allow missing tracer in restart file.", file=log_file)
                    print("*** Value will be set to zero for missing tracer.", file=log_file)
            
        self.PRG_var = np.zeros((adm.ADM_gall_1d, adm.ADM_gall_1d, adm.ADM_kall, adm.ADM_lall, rcnf.PRG_vmax), dtype=rdtype)
        self.PRG_var_pl = np.zeros((adm.ADM_gall_pl, adm.ADM_kall, adm.ADM_lall_pl, rcnf.PRG_vmax), dtype=rdtype)

        self.DIAG_var = np.zeros((adm.ADM_gall_1d, adm.ADM_gall_1d, adm.ADM_kall, adm.ADM_lall, rcnf.DIAG_vmax), dtype=rdtype)
        self.DIAG_var_pl = np.zeros((adm.ADM_gall_pl, adm.ADM_kall, adm.ADM_lall_pl, rcnf.DIAG_vmax), dtype=rdtype)

        return
    
    def restart_input(self, fname_in, comm, gtl, cnst, rcnf, grd, idi, rdtype):

        if std.io_l:
            with open(std.fname_log, 'a') as log_file:
                print("\n*** read restart/initial data", file=log_file)

        if self.input_io_mode == "ADVANCED":
            print("ADVANCED input not implemented yet")
            prc.prc_mpistop(std.io_l, std.fname_log)
            ## Read diagnostic variables
            #for nq in range(DIAG_vmax0):
            #    FIO_input(rcnf.DIAG_var[:, :, :, nq], basename, rcnf.DIAG_name[nq],
            #              layername, 1, adm.ADM_kall, 1)

            ## Read tracer variables
            #for nq in range(1, TRC_vmax_input + 1):
            #    FIO_input(rcnf.DIAG_var[:, :, :, DIAG_vmax0 + nq - 1], basename, rcnf.TRC_name[nq - 1],
            #              layername, 1, adm.ADM_kall, 1, allow_missingq=allow_missingq)

        elif self.input_io_mode == "json":
            with open(std.fname_log, 'a') as log_file:
                    print("*** reading json file", file=log_file)

            import json
            fullname = self.restart_input_basename+str(prc.prc_myrank).zfill(8)+".json"
            #print(f"fullname: {fullname}")
            with open(fullname, "r") as json_file:
                loaded_data = json.load(json_file)

            cnt=0
            for varname, var_data in loaded_data["Variables"].items():
                variable_array = np.array(var_data["Data"])
                #print(f"{varname}: {variable_array.shape}")
                for i in range(adm.ADM_gall_1d):
                    for j in range(adm.ADM_gall_1d):
                        ij = i * adm.ADM_gall_1d + j
                        self.DIAG_var[i,j,:,:,cnt] = variable_array[ij,:,:]
                cnt += 1 

            #print("DIAG_vmax ", rcnf.DIAG_vmax, cnt)

        elif self.input_io_mode == "POH5":
            print("POH5 not implemented yet")
            prc.prc_mpistop(std.io_l, std.fname_log)
            # Read diagnostic variables
            #for nq in range(1, DIAG_vmax0 + 1):
            #    HIO_input(rcnf.DIAG_var[:, :, :, nq - 1], basename, rcnf.DIAG_name[nq - 1],
            #              layername, 1, adm.ADM_kall, 1)

            ## Read tracer variables
            #for nq in range(1, TRC_vmax_input + 1):
            #    HIO_input(rcnf.DIAG_var[:, :, :, DIAG_vmax0 + nq - 1], basename, rcnf.TRC_name[nq - 1],
            #              layername, 1, adm.ADM_kall, 1, allow_missingq=allow_missingq)

        elif self.input_io_mode == "IDEAL":
            if std.io_l:
                with open(std.fname_log, 'a') as log_file:
                    print("*** IDEAL initials is slow and untested", file=log_file)
                    print("*** make ideal initials", file=log_file) 
        
            self.DIAGvar = idi.dycore_input(fname_in, cnst, rcnf, grd, idi, rdtype)

        elif self.input_io_mode == "IDEAL_TRACER":
            print("IDEAL_TRACER not implemented yet")
            prc.prc_mpistop(std.io_l, std.fname_log)
            ## Read diagnostic variables
            #for nq in range(1, DIAG_vmax0 + 1):
            #    FIO_input(rcnf.DIAG_var[:, :, :, nq - 1], basename, rcnf.DIAG_name[nq - 1],
            #          layername, 1, adm.ADM_kall, 1)
            if std.io_l:
                with open(std.fname_log, 'a') as log_file:
                    print("*** make ideal initials for tracer", file=log_file)
            # Call tracer_input for tracer initialization
            idi.tracer_input(self.DIAG_var[:, :, :, rcnf.DIAG_vmax0:rcnf.DIAG_vmax0 + rcnf.TRC_vmax])

        #print(self.DIAG_var.shape) 
        #print(self.DIAG_var_pl.shape) 
        comm.COMM_var(self.DIAG_var, self.DIAG_var_pl)

        
        if std.io_l:
            with open(std.fname_log, 'a') as log_file:
                print("\n====== Data Range Check: Diagnostic Variables ======", file=log_file)

                for nq in range(rcnf.DIAG_vmax0):
                    #print("nq=", nq)
                    val_max = gtl.GTL_max(self.DIAG_var[:,:,:,:, nq], self.DIAG_var_pl[:,:,:, nq], 
                                        adm.ADM_kall, adm.ADM_kmin, adm.ADM_kmax, cnst, comm, rdtype
                                        )
                    val_min = gtl.GTL_min(self.DIAG_var[:,:,:,:, nq], self.DIAG_var_pl[:,:,:, nq], 
                                        adm.ADM_kall, adm.ADM_kmin, adm.ADM_kmax, cnst, comm, rdtype
                                        )
                    print(f"--- {rcnf.DIAG_name[nq]:16}: max={val_max:24.17E}, min={val_min:24.17E}", file=log_file)

                #print("TRC_vmax", rcnf.TRC_vmax)

                for nq in range(rcnf.TRC_vmax):  # Fortran 1-based index → Python 0-based range
                    val_max = gtl.GTL_max(self.DIAG_var[:,:,:,:, rcnf.DIAG_vmax0 + nq],  
                                            self.DIAG_var_pl[:,:,:, rcnf.DIAG_vmax0 + nq],
                                            adm.ADM_kall, adm.ADM_kmin, adm.ADM_kmax, cnst, comm, rdtype
                                            )
                    val_min = gtl.GTL_min(self.DIAG_var[:,:,:,:, rcnf.DIAG_vmax0 + nq],  
                                            self.DIAG_var_pl[:,:,:, rcnf.DIAG_vmax0 + nq],
                                            adm.ADM_kall, adm.ADM_kmin, adm.ADM_kmax, cnst, comm, rdtype
                                            )
                    
                    nonzero = val_max > 0.0  # Direct boolean conversion
                    val_min = gtl.GTL_min(self.DIAG_var[:,:,:,:, rcnf.DIAG_vmax0 + nq],
                                            self.DIAG_var_pl[:,:,:, rcnf.DIAG_vmax0 + nq],
                                            adm.ADM_kall, adm.ADM_kmin, adm.ADM_kmax, cnst, comm, rdtype, nonzero
                                            )
                    print(f"--- {rcnf.TRC_name[nq]:16}: max={val_max:24.17E}, min={val_min:24.17E}", file=log_file)


    #!!!!!  call cnvvar_diag2prg( PRG_var (:,:,:,:), PRG_var_pl (:,:,:,:), & ! [OUT]
    #                      DIAG_var(:,:,:,:), DIAG_var_pl(:,:,:,:)  ) ! [IN]

    # # Logging
    # if IO_L:
    #     print(f"--- {TRC_name[nq]}: max={val_max:24.17E}, min={val_min:24.17E}")



    #     return
    
