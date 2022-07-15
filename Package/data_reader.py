import json
import os


class data_reader():
    def __init__(self):
        self.data = None
        self.file = None
        

    def save_data(self, name):                      #Use save_data function with dict object followed by name.
        with open(name+'.json', 'w') as f: 
            json.dump(self.data, f)
        return print('data saved succesfully in '+name +'.json')

    def __stripper(self, x,*argv):
        for arg in argv:
            x = x.replace(arg, " ")
        return x

    def __splitter(self, x, *argv):   #---do not add " " in the arguement
        for arg in argv:
            x = x.split(arg)
            x = " ".join(x)
        return x.split()
    
    def get_keylist(self, x):
        l = []
        for el in x.keys():
            l.append(el)
        return l
    
    def get_valuelist(self, x):
        l = []
        for el in x.values():
            l.append(el)
        return l
        
    def chooser(self, path = '.'):                        #use chooser function incase scan files in directory.
        if path.endswith('.tdb') or path.endswith('.TDB'):
            self.file = path
        else :
            temp_files = os.listdir(path)
            files = list(filter(lambda x: x.endswith('.tdb') or x.endswith('.TDB'), temp_files))
            if len(files) == 0:
                print('No tdb file found.')
            else:
                for i in range(len(files)):
                    print(i + 1 ,'. '+ files[i])
                selected_file = int(input('choose the file: ')) - 1
                print(files[selected_file])
                self.file = files[selected_file]
        
            
       

    def scan_data(self, path = '.' , file_name ="" ):    #------use data_reader function with file name in order to read data-------#
        
        if file_name != "":
            self.file = file_name
        
        else:
            self.chooser(path)
            print('file name: ', self.file)
        try:
            with open(path + '\\'+self.file) as f:
                data = f.read()
        
            dt = data.split('\n')
            j_data = {}
            elements_data = {}
            functions_data = {}                                 
            parameters_data = {}
            phase_data = {}
            phase_constituent = {}
            phase_comp = {}
            ref = None
            for i in range(len(dt)):
                try:
                    if dt[i].strip():
                        temp = dt[i].split()
                        if temp[0].startswith('$') == False:
                            if temp[0] == 'ELEMENT':                     #-----------data extractor of pure elements--------#
                                elements_data[temp[1]] = {
                                    "standard state" : temp[2],
                                    "mass [g/mol]" : float(temp[3]),
                                    "entalpy_298" : float(temp[4]),
                                    "entropy_298": float(temp[5].strip('!')),
                                    "constituents":[]
                                    }  
                            elif temp[0] == 'FUNCTION':                  #------------data extractor of gibbs functions---------#
                                func = []
                                x = 0
                                while True:
                                    
                                    if dt[i + x].split()[-1] != '!':
                                        func += dt[i + x].split()
                                    elif dt[i + x].split()[-2] == 'N' and dt[i + x].split()[-1] == '!':
                                        func += dt[i + x].split()
                                        break
                                    else:
                                        break
                                    x += 1
                                
                                del(func[:2])
                                func = " ".join(func)
                                func = func.split(";")
                                equations = []
                                for k in range(len(func)):
                                    eq = func[k].replace("Y", "")
                                    #eq = eq.replace("#", "")        #-----change to include or exclude Hashtags to functions.
                                    eq = eq.split()
                                    eq[1] = "".join(eq[1:])
                                    del(eq[2:])
                                    equations.append(eq)
                                    
                                functions_data[temp[1]] = equations
                                    
                                
                                #Functions to be extracted according to data
                            elif temp[0].startswith('PARA'):                #------------data extractor of parameters-----------#
                                parameter_name = temp[1]
                                x = 1
                                while True:
                                    
                                    if temp[-1] == 'N' or temp[-1] == '!':
                                        break
                                    temp += dt[i + x].split()
                                    x += 1
                                    
                                
                                del(temp[0:2])        
                                temp = " ".join(temp)
                                temp = temp.strip('!')
                                temp = temp.strip('Y')
                                temp = temp.split(";")
                                
                                params = []
                                for parameter in range(len(temp)):
                                    eq = temp[parameter].split()
                                    equation = []
                                    equation.append(eq[0])
                                    x = "".join(eq[1:])
                                    equation.append(x.strip('Y'))
                                    params.append(equation)
                                            
                                parameters_data[parameter_name] = params
                                
                            elif temp[0].startswith('CONST'):
                                phase = temp[1]
                                x = 1
                                while True:
                                    if temp[-1].endswith('!'):
                                        break
                                    temp += dt[i + x].split()
                                    x += 1
                                del(temp[:2])
                                constituents = " ".join(temp)
                               # print(constituents)
                                phase_constituent[phase] = constituents
                                constituents = self.__stripper(constituents, ':', '!', '%', '>', '1', '2', '3', '4')
                                #-----phase data with constituents, sublattices seperated by space.   
                                constituents = self.__splitter(constituents, ',')
                                phase_data[phase] = constituents
                               # print(constituents, phase)
                                for ele in constituents:
                                    if phase not in elements_data[ele]["constituents"]:
                                        elements_data[ele]["constituents"].append(phase)
                                
                                
                               #________paste here________
                            elif temp[0].startswith('PHASE'):
                                comp = ''
                                x = 0
                                ref = '!'
                                while True:
                                    comp += dt[i + x]
                                    if '>' in comp:
                                        ref = '>'
                                        break
                                    if '!' in comp:
                                        ref = '!'
                                        break
                                    
                                    x += 1
                                phase = comp.split()[1]
                                #print(comp, phase)
                                comp = comp[comp.index('%') + 2 : comp.index(ref)]
                                
                                comp = comp.split()[1:]
                                phase_comp[phase] = comp
                                
                            if temp[0].startswith('REFERENCE'):
                                ref_el = temp[1]
                                
                            else:
                                ref_el = None
                                 
                except ValueError:
                    print('ValueError')
                    print(dt[i])
            j_data['elements'] = elements_data
            j_data['functions'] = functions_data
            j_data['parameters'] = parameters_data
            j_data['phases'] = phase_data
            j_data['phase_constituents'] = phase_constituent
            j_data['phase_compositions'] = phase_comp
            j_data['reference_element'] = ref_el
            self.data = j_data
            
        except OSError:
                print('File not found', self.file)     
                print('please check the file and run chooser function again.')
            


