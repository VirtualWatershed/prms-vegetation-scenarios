__author__ = 'jerickson'

# Lookup table for snow_intcp variable
def lookup_snow_intcp(covtype):
    snow_intcp = [0.01, 0.01, 0.002, 0.01, 0.0]
    return snow_intcp[covtype]
lookup_snow_intcp_ref = lookup_snow_intcp

# Lookup table for srain_intcp variable
def lookup_srain_intcp(covtype):
    srain_intcp = [0.05, 0.05, 0.05, 0.05, 0.0]
    return srain_intcp[covtype]
lookup_srain_intcp_ref = lookup_srain_intcp

# Lookup table for wrain_intcp variable
def lookup_wrain_intcp(covtype):
    wrain_intcp = [0.01, 0.01, 0.002, 0.01, 0.0]
    return wrain_intcp[covtype]
lookup_wrain_intcp_ref = lookup_wrain_intcp

# Lookup table for covden_sum variable
def lookup_covden_sum(covtype):
    covden_sum = [0.2, 0.13, 0.27, 0.54, 0.0]
    return covden_sum[covtype]
lookup_covden_sum_ref = lookup_covden_sum

# Lookup table for covden_win variable
def lookup_covden_win(covtype):
    covden_win = [0.2, 0.13, 0.27, 0.54, 0.0]
    return covden_win[covtype]
lookup_covden_win_ref = lookup_covden_win

# Lookup table for jh_coef_hru variable
def lookup_jh_coef_hru(covtype):
    jh_coef_hru = [18.82953863, 18.95732546, 19.80030636, 18.85014941, 0.0]
    return jh_coef_hru[covtype]
lookup_jh_coef_hru_ref = lookup_jh_coef_hru

# Lookup table for snow_intcp variable
def lookup_rad_trncf(covtype):
    rad_trncf = [0.433855115, 0.144088925, 0.2949815, 0.433855115, 0.0]
    return rad_trncf[covtype]
lookup_rad_trncf_ref = lookup_rad_trncf

lookup_vars = ['snow_intcp',
               'srain_intcp',
               'wrain_intcp',
               'covden_sum',
               'covden_win',
               'jh_coef_hru',
               'rad_trncf']

lookup_funcs = { "snow_intcp" : lookup_snow_intcp_ref,
                 "srain_intcp" : lookup_srain_intcp_ref,
                 "wrain_intcp" : lookup_wrain_intcp_ref,
                 "covden_sum" : lookup_covden_sum_ref,
                 "covden_win" : lookup_covden_win_ref,
                 "jh_coef_hru" : lookup_jh_coef_hru_ref,
                 "rad_trncf" : lookup_rad_trncf_ref}

def look_up(varname, cov_type):
    if varname not in lookup_vars:
        return None
    if cov_type < 0 or cov_type > 4:
        return None
    return lookup_funcs[varname](cov_type)

if __name__ == "__main__":
    print look_up("snow_intcp", 0)
    print look_up("srain_intcp", 1)
    print look_up("wrain_intcp", 2)
    print look_up("covden_sum", 3)
    print look_up("covden_win", 4)
    print look_up("jh_coef_hru", 0)
    print look_up("rad_trncf", 2)
    print look_up("bad_var", 0)
    print look_up("rad_trncf", 5)