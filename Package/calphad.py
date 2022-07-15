from data_reader import data_reader
import math
import random
import copy
from save_data import save_data


def LN(x):
    return math.log(x)

def ln(x):
    return math.log(x)

R =  8.31432


class CEF(data_reader):
    def __init__(self, phase_name, data, elements_list, composition, attachments = []):
        self.constituents = data.data['phase_constituents'][phase_name]    #----unfiltered constituents-------
        self.comp = composition
        self.lattice_composition = [float(x) for x in data.data['phase_compositions'][phase_name]]
        self.phase_name = phase_name
        self.elements = elements_list
        self.attachments = copy.deepcopy(attachments)
        self.selected_cons = []                 #-------filtered constituents splitted list acc to lattice.-------
        self.parameters = {}
        self.exs_params = []
        self.data = data
        self.total_moles = 0.0
        self.sub_totals = []
        self.cons_params()    #-- returns filtered elements according to constituents.--------
        self.grab_params()
        self.__update_fractions()
        self.__exs_params()
        self.attachments.append(self.phase_name)
        
        #/////////////-----extra functions for data processing---------////////////
        
    def reset(self):
        self.cons_params()    #-- returns filtered elements according to constituents.--------
        self.grab_params()
        self.__update_fractions()
        self.__exs_params()
        
    def mole_fractions(self, el = None):
        if el != None and self.comp[el] == 0.0:
            return 0.0
        for element in self.elements:
            if element != 'VA':
                el_frac = (self.comp[element] / self.data.data['elements'][element]['mass [g/mol]']) / self.total_moles
                
                if element == el and el != None:
                    return el_frac
                elif el == None:
                    print(element,'-',el_frac)
            
        
        
    def __cons_stripper(self, x,*argv):
        for arg in argv:
            x = x.replace(arg, "")
        return x
   
    def get_keylist(self, x):
        l = []
        for el in x.keys():
            l.append(el)
        return l
    
    def __con_splitter(self, x, *argv):   #---do not add " " in the arguement
        for arg in argv:
            x = x.split(arg)
            x = " ".join(x)
        return x.split()
    
    #//////////--------functions for value processing---------///////////
    
    def __update_fractions(self):       #--returns total values of each lattice for fraction calculation.
        self.sub_totals = []
        for sub in range(len(self.selected_cons)):
            moles_per_sublattice = 0
            for element in self.selected_cons[sub]:
                if element != 'VA':
                    x = 0
                    for subl in self.selected_cons:
                        if element in subl:
                            x += 1
                    moles_per_sublattice += self.comp[element] / self.data.data['elements'][element]['mass [g/mol]']  / x
            
            self.sub_totals.append(moles_per_sublattice * self.lattice_composition[sub])
        self.total_moles = sum(self.sub_totals)

    def update_composition(self, composition):
        self.comp = composition
        self.__update_fractions()
        
    def lattice_fraction(self, el, sub):
        
        if el not in self.selected_cons[sub]:
            print(el, 'not in sublattice',sub)
            return 1.0
        
        if self.comp[el] == 0.0:
            print(el, 'composition is', self.comp[el])
            return 0.0
        x = 0
        if self.sub_totals[sub] > 0:
            for lattice in self.selected_cons:
                if el in lattice :
                    x += 1
                    
            return self.mole_fractions(el) / x
            
        else:
            print(el, 'does not exist in sublattice', sub + 1)
                
    
    def grab_params(self):
        p_list = self.get_keylist(self.data.data['parameters'])
        sel_p_list = []
        for p in p_list:
            px = p[p.index('(') + 1 : p.index(')')]
            if self.phase_name in px.split(','):
                sel_p_list.append(p)
        del(p_list)
        for p in sel_p_list:
            pr = p[p.index(self.phase_name )+ len(self.phase_name) + 1 : p.index(')')]
            pr = pr.split(';')
            pr_cons = pr[0]
            pr_cons = pr_cons.split(':')
            if len(self.selected_cons) == len(pr_cons):
                check = None
                
                
                for cons in range(len(pr_cons)):
                    if all(el in self.selected_cons[cons] for el in pr_cons[cons].split(',') if el != '*'):
                        check = True
                    
                    else:
                        check = False
                        break
                
                if check:
                    if '*' in p:
                        for cons in range(len(pr_cons)):
                            
                            if '*' in pr_cons[cons]:
                                for el in self.selected_cons[cons]:
                                    if p.replace('*',el) not in sel_p_list:
                                        self.parameters[p.replace('*',el)] = self.data.data['parameters'][p]
                    else:
                        self.parameters[p] = self.data.data['parameters'][p]
                
    
    def cons_params(self):              #-------filter out the unwanted elements in phase constituents--------
        self.selected_cons = []
        eles = self.__cons_stripper(self.constituents, '%','!', ' ')
        #print(type(eles), eles)
        eles = eles.split(':')[1:-1]
        #print(eles)
        for x in range(len(eles)):
            cons = [] 
            e = eles[x]
            #print(e)
            for ele in self.elements:
                for ex in e.split(','):
                    if ele == ex:
                        cons.append(ele)
                        #print(ele,cons)
            if len(cons) != 0:
                #print(cons)
                self.selected_cons.append(cons)
            

    
    def func_chooser(self, func, t):   #use this function to get CP value of a function w.r.t temperature
        functions = self.data.data['functions'][func]
        for f in range(len(functions)):
            if t >= float(functions[f][0]) and t < float(functions[f + 1][0]):
                function = functions[f][1]
        return function

    def func_detector(func, func_str, key_list):
        
        func_list = []
        for i in key_list:
            if i in func_str:
                func_list.append(i)
        func_list = func_list.sort(key = len)
        return func_list[-1]
        

    def func_processor(self, temperature, func_str):       #use this function to obtain comple CP w.r.t temperature
       
        def func_detector(func, func_str, key_list):
        
            f_list = []
            for i in key_list:
                if i in func_str:
                    f_list.append(i)
          
            f_list = sorted(f_list,key = len)
            print(f_list)
            return f_list[-1]
    
        functions = func_str
        func_list = self.get_keylist(self.data.data['functions'])
        for y in range(len(functions)):                                                         #This code selects desired function value based on temperature.
            if temperature >= float(functions[y][0]) and temperature < float(functions[y + 1][0]):
                func_str = functions[y][1]
                
                
        while True:
            for x in range(len(func_list)):
                f = func_list[x]
                
              #  if f + '#' in func_str:                                 #This code detects fuction based on #-tag to the sub-function in function value.
              #      sub_f = '('+ self.func_chooser(f, temperature) + ')'
              #      func_str = func_str.replace(f + '#',sub_f)
                    
                if f in func_str:
                    print(f,func_str)
                    fx = func_detector(f, func_str, func_list)
                    if fx != None:                                 #This code detects fuction based on #-tag to the sub-function in function value.
                        sub_f = '('+ self.func_chooser(fx, temperature) + ')'
                        func_str = func_str.replace(f + '#',sub_f)
                    
                        
                        
            
            if any(func_l in func_str for func_l in func_list) == False:
                break
        return func_str                 #returns CP value of phase dependent on temperature.
    
    def __exs_params(self):
        p_n_x = []
        param_keys = [x for x in self.get_keylist(self.parameters) if x.startswith('L')]
        for p in param_keys:
            p_n_x.append(p.split(';')[0])
        self.exs_params = list(dict.fromkeys(p_n_x))
        
 
# =============================================================================
#      #//////////------gibbs energy calculations-----//////////
# =============================================================================
     
    #------gibbs reference----
    
    def gibbs_ref(self, temp):
        T = temp
        if T < 273 or T > 6000 :
            print('temperature is off limit:',T)
            return
        ref_g = 0.0
        
        for param in self.get_keylist(self.parameters):
            if param.startswith('G'):
                #print(param)
                con_el = []
                for phase_name in self.attachments:
                    if phase_name in param:
                        #print(phase_name)
                        con_el = param[param.index(phase_name) + len(phase_name) + 1: param.index(';')]
                        con_el = con_el.split(':')
                #print(con_el)
                el_fractions = 1.0
                for el in range(len(con_el)):
                    elements = con_el[el]
                    elements_in_lattice = elements.split(',')
                    for e in elements_in_lattice:
                        if e != 'VA':
                            el_frac = self.lattice_fraction(e, el)
                            #print(el_frac)
                            el_fractions *= el_frac
                
                func = self.func_processor(T, self.parameters[param])
                gibbs = el_fractions * eval(func)
                ref_g += gibbs
                
        return ref_g
    
# =============================================================================
#      #-----gibbs ideal--------
#      gibbs ideal depends on pressure, temperature and composition.
#      Gi =  RTΣ xi LN(xi) 
# =============================================================================
     
     
     
    def gibbs_ideal(self, temperature):
        ideal_g = 0.0
        for sub_lattice in range(len(self.selected_cons)):
            g_sub_l = 0.0
            
            for el in self.selected_cons[sub_lattice]:
                if el != 'VA':
                    el_fraction = self.lattice_fraction(el, sub_lattice)
                    g_sub_l += el_fraction * LN(el_fraction) 
            ideal_g +=  self.lattice_composition[sub_lattice] * g_sub_l
            
        return R * temperature  *ideal_g

# =============================================================================
#      #------gibbs excess-------  
# =============================================================================
     
    def gibbs_exs(self, temperature):
        T = temperature
        if T < 273 or T > 6000 :
            print('temperature is off limit:',T)
            return
        gibbs_ex = 0.0
        for p in self.exs_params:
            gibbs = 0.0
            x = 0                #final power value.N no.of parameters.
            while True:     #sum of all parameters.
                if p + ';' + str(x) + ')' in self.parameters:                
                    
                    l_param = self.func_processor(temperature, self.parameters[p + ';' + str(x) + ')'])      # all parameters will be added up.
                    #print(p + ';' + str(x) + ')', l_param)                 
                    gibbs += eval(l_param)
                    x += 1
                else:
                    break
            #print(gibbs,x)
            p = p[p.index(self.phase_name) + len(self.phase_name) + 1 : ]
            p = p.split(':')
            for sub in range(len(p)):
                if self.sub_totals[sub] != 0.0:
                    el_frac_sub = [self.lattice_fraction(e, sub) for e in p[sub].split(',')]
                    #print(el_frac_sub)
                    for el in el_frac_sub:
                        gibbs *= el      #gibbs multiplication individually with fractions in each lattice.
                    #print(gibbs)
                    #Redlich kister polynomial should be added.
                    #Use private variable 'x' as power factor.
                   
            gibbs_ex += gibbs
        return gibbs_ex
    
#--------------------------------------------------
#                Gibbs magnetic
#--------------------------------------------------
    def gibbs_mag(self, temperature):
        Tref = 1.0
        TC = 1.0
        funT = 1.0
        Bmag = 0.0
        p = 0.28                                 #-------------------need to be developed.
        for param in self.get_keylist(self.parameters):    #--------Tref
            if param.startswith('TC'):
                TC = float(self.parameters[param][0][1])
                Tref = temperature / TC
        a = (518/1125) + (11692/15975) * ((1/p)- 1)
        
        if Tref < 1:
            funT = 1 - (1/a)*(((79*Tref ** -1)/140 * p) + (474/497)*((1/p) - 1) * ((Tref**3/6) + (Tref**9/135) + (Tref**15/600)))
                              

        elif Tref >= 1:
            funT = (1/a)*((Tref**-5/10) + (Tref**-15/315) + (Tref**-25/600))
            
        for param in self.get_keylist(self.parameters):    #--------Tref
            if param.startswith('BMAGN'):
                Bmag = float(self.parameters[param][0][1])
        
        return funT  * R *temperature *ln(Bmag + 1)
    #----gibbs total--------
    
    def gibbs(self, temperature):
        return self.gibbs_ref(temperature)+ self.gibbs_ideal(temperature) +self.gibbs_exs(temperature) + self.gibbs_mag(temperature)
        


#----element selection--------
def select_element(data):
    elements_list = data.get_keylist(data.data['elements'])
    ref = data.data['reference_element']
    print('Avalable elements :')
    for ele in range(len(elements_list)):
        print(ele + 1,'. ',elements_list[ele] )
    elements = str(input('select elements :'))
    elements = elements.replace(' ', '')
    elements = elements.split(',')
    selected_elements = [elements_list[int(x) - 1] for x in elements]
    try:
        print('selected elements :', selected_elements)
        if ref == None or ref not in selected_elements:
            print('reference element not found.')
            ref = random.choice([x for x in selected_elements if x != 'VA'])
            print('setting', ref, 'as reference element.')
        else:
            print('setting', ref, 'as reference element.')   
    except IndexError:
        print('No selected elements found.')
        return
    comp = {}
    if 'VA' in selected_elements:
        comp['VA'] = 0.0
    for e in selected_elements:
        if e != ref and e != 'VA':
            comp[e] = float(input(e + ' :'))
    comp[ref] = 100 - sum([x for x in comp.values()])
    print(ref, ':', comp[ref],'  -reference element.')
    
    return selected_elements, comp


#------phase list eccording to constituents---------

def select_phases(phases, data):
    s_phases = []
    print('available phases:')
    for p in range(len(phases)):
        print(p + 1, '.', phases[p], data.data['phase_constituents'][phases[p]])
    s_phases = [phases[int(x)-1] for x in str(input('select phases :')).split(',')]
    print('selected phases :', s_phases)
    return s_phases


def grab_phases(elements_list, data):                   #-----for selecting phases.
    phases = []
    d = data.data
    for element in elements_list:
        constituent_phase = d['elements'][element]['constituents']
        
        for phase in constituent_phase:
            ele = d['phase_constituents'][phase].replace('%', '')
            ele = ele.replace('>', '')
            ele = ele.replace(" ","")
            ele = ele.split(':')
            del(ele[0])
            sublattice_len = len(ele)
            check = None
            for sub in range(sublattice_len):
                sub_l = ele[sub]
                if sub_l != '!':
                    if any(e in sub_l.split(',') for e in elements_list):
                        check = True
                         
                    else:
                        check = False
                        break
            
            if check:
                if phase not in phases:
                    phases.append(phase)
                        
    return phases

#------------------

def create_phases(phase_list, data, elements, comp):
    phase_attachments = {
        "BCC_B2" : ['BCC_A2'],
        "BCC_DISL" : ['BCC_A2']
        }
    ph = []
    moles = {}
    total_moles = 0.0
    for element in elements:
        if comp[element] > 0.0:
            moles_per_element = comp[element] / data.data['elements'][element]['mass [g/mol]']
            moles[element] = moles_per_element
            total_moles += moles_per_element
    
    
    
    
    
    
    for phase in phase_list:
        print('Creating',phase, 'phase.')
        existed_comp = {}
        
        #composition should be updated acc to existed elements in phase constituents.
        elements_in_constituents = data.data['phase_constituents'][phase]
        elements_in_constituents = elements_in_constituents.replace(':',',')
        elements_in_constituents = elements_in_constituents.replace('%', '')
        elements_in_constituents = elements_in_constituents.replace(' ', '')
        elements_in_constituents = elements_in_constituents.split(',')
        
        
        existed_elements = [x for x in elements if x in elements_in_constituents]
        print(existed_elements, 'are existed in',phase)
        existed_element_moles = sum([moles[x] for x in existed_elements if comp[x] > 0.0])
        for element in existed_elements:
            if comp[element] > 0.0:
                existed_comp[element] = moles[element] / existed_element_moles
                print(element, '-', existed_comp[element])
            else:
                print(element, '-', comp[element])
            
        
        if phase in phase_attachments:
            attachments = phase_attachments[phase]
            
            main_phase = CEF(phase, data, existed_elements, existed_comp , attachments)
            
            print(attachments, 'attached to', phase,'\n')
            
            for p in attachments:
                sub_phase = CEF(p, data, existed_elements, comp)
                main_phase.parameters.update(sub_phase.parameters)
                del(sub_phase)
            
            ph.append(main_phase)
            
            
            
        else:
            ph.append(CEF(phase, data, existed_elements, existed_comp))
            
    return ph

def print_params(phase_list):
    for i in phase_list:
        print('*'*5,i.phase_name,'*'*5)
        print(i.parameters)
   
def save_to_csv(data_list):
    
    for x in data_list:
        for data in data_list:
            save_data(data)
                
              

