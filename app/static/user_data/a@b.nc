GSFLOW Control File for Lehman Creek Chao Chen 
####
aniOutON_OFF
1
1
1
####
print_debug
1
1
7
####
aniOutVar_names
7
4
hru_ppt
tmaxf
tminf
pkwater_equiv
pk_depth
swrad
potet
####
ani_output_file
1
4
.\output\animation.out
####
csv_output_file
1
4
.\output\gsflow.csv
####
model_output_file
1
4
.\output\prms.out
####
data_file
1
4
.\input\LC.data
####
dispGraphsBuffSize
1
4
15
####
dispVar_element
20
4
1
1
1
1
1
1
1
1
1
1
1
1
525
1337
2202
1
1
1
1
1
####
dispVar_names
20
4
basin_cfs
runoff
basin_sroff_cfs
basin_ssflow_cfs
basin_gwflow_cfs
basin_pweqv
basin_dunnian
basin_prefflow
basin_slowflow
basin_rain
basin_snow
basin_ppt
hru_rain
hru_rain
hru_rain
basin_tmax
basin_tmin
basin_temp
tmin
tmax
####
dispVar_plot
20
1
1
1
2
2
2
3
3
4
4
5
5
5
6
6
6
7
7
7
8
8
####
end_time
6
1
2010
9
30
0
0
0
####
et_module
1
4
potet_jh
####
executable_desc
1
4
GSFLOW model
####
executable_model
1
4
..\..\bin\prms
####
gsflow_output_file
1
4
.\output\gsflow.out
####
init_vars_from_file
1
1
0
####
initial_deltat
1
2
24.0
####
mms_user_dir
1
4
.\
####
mms_user_out_dir
1
4
.\output\
####
model_mode
1
4
PRMS
####
modflow_name
1
4
LC.nam
####
naniOutVars
1
1
7
####
ndispGraphs
1
1
8
####
nstatVars
1
1
14
####
param_file
1
4
.\input\LC.param
####
precip_module
1
4
precip_1sta
####
param_print_file
1
4
.\output\LC.parprt
####
save_vars_to_file
1
1
1
####
solrad_module
1
4
ddsolrad
####
srunoff_module
1
4
srunoff_smidx
####
start_time
6
1
2002
10
1
0
0
0
####
statVar_element
41
4
525
1337
1243
1
1
1
1
1
2894
1
1
525
1337
1243
1
1
1243
1324
2401
2989
3772
4310
4704
2
3
1
2
3
1
2
3
1
2
3
1
2490
1
1
1
1
2
####
statVar_names
41
4
swrad
swrad
swrad
basin_cfs
runoff
basin_tmax
basin_tmin
basin_actet
potet
precip
basin_ppt
hru_ppt
hru_ppt
hru_ppt
subinc_pkweqv
basin_sroff_yr
swrad
swrad
swrad
swrad
swrad
swrad
swrad
sub_sroff
sub_sroff
subinc_pkweqv
subinc_pkweqv
subinc_pkweqv
subinc_precip
subinc_precip
subinc_precip
subinc_snowmelt
subinc_snowmelt
subinc_snowmelt
basin_potet
swrad
basin_ppt
basin_hortonian
basin_dunnian
subinc_snowmelt
subinc_snowmelt
####
stat_var_file
1
4
.\output\statvar.dat
####
statsON_OFF
1
1
1
####
cascade_flag
1
1
1
####
cascadegw_flag
1
1
1
####
temp_module
1
4
temp_1sta
####
var_save_file
1
4
.\output\prms_ic.out
####
stats_output_file
1
4
.\output\stats.out
####
var_init_file
1
4
vars
####
rpt_days
1
1
1
####
capillary_module
1
4
soilzone_prms
####
strmflow_module
1
4
strmflow
####
basin_summary_module
1
4
basin_sum_prms
####
print_type
1
1
3
