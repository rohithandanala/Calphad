import os
#change dir location to current script location
os.chdir(os.getcwd())

from data_reader import data_reader
from calphad import CEF, select_element, select_phases, grab_phases, create_phases, print_params, save_to_csv
from save_data import save_data


data = data_reader()
data.scan_data(file_name = 'al.TDB')

ele, comp = select_element(data)
phases = grab_phases(ele, data)

sel_phase = select_phases(phases, data)
p_ob = create_phases(sel_phase, data, ele, comp)

print_params(p_ob)

save_to_csv(p_ob)

