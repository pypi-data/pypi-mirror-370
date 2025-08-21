import os
import numpy as np
import re
from . import InputSyntaxError
re_num = re.compile(r"[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?")
mncn_matrix_keywords=['INERTIA_MATRIX','DAMPING_MATRIX',
                      'QDAMPING_MATRIX','STIFFNESS_MATRIX']


def isnumeric(input):
    """ Check if input string is a number """
    if re_num.match(input) is None:
        return False
    else:
        return True
def parse_header(input):
    """ Read the header, produce an object

    """
    input_ = list(input)
    name = None
    type = None
    body = None
    data = []
    current = None
    
    while len(input) > 0:
        tmp = input.pop(0)
        if not isnumeric(tmp):
            if name is None:
                name = tmp
                current = 'name'
            elif tmp == 'TYPE':
                current = 'type'
            elif tmp == 'BODY':
                body = []
                current = 'body'
            else:
                if str(current) == 'name':
                    data.append(tmp)
                else:
                    raise RuntimeError(f'Unexpected keyword: {tmp}')
        else:
            if current == 'name':
                if tmp.isdigit():
                    data.append(int(tmp))
                else:
                    data.append(float(tmp))
            elif current == 'type':
                type = int(tmp)
            elif current == 'body':
                body.append(int(tmp))
            else:
                raise RuntimeError(f'Unexpected reading state: {current}')
    if name in mncn_matrix_keywords:
        return InputMatrix(body=body,type=type,name=name)
    else:
        return (name,data)


class InputMatrix:
    def __init__(self,body=[],type=0,name='Unknown'):
        self.data = np.zeros((6,6),dtype='float64')
        self.name = name
        self.type   = type

        if body is None:
            self.body_i = 1
            self.body_j = 1
        elif len(body)==0:
            self.body_i = 1
            self.body_j = 1
        elif len(body)==1:
            self.body_i = body[0]
            self.body_j = body[0]
        elif len(body)==2:
            self.body_i = body[0]
            self.body_j = body[1]
        else:
            raise RuntimeError(f'Unexpected input for body: {body}')
        if type == 0:
            self.parse = self._parse_type0
        elif type == 1:
            self.parse = self._parse_type1
        elif type == 2:
            self.parse = self._parse_type1
        self._progess = 0

    def _parse_type0(self,splitted_line):
        self.data[self._progess,:] = np.array([float(item) for item in splitted_line])
        self._progess += 1
    def _parse_type1(self,splitted_line):
        ii  = int(splitted_line[0])-1
        jj  = int(splitted_line[1])-1
        val = float(splitted_line[2])
        self.data[ii,jj] = val
        self._progess +=1


def add_to_dict(dictIn,key,val):
    if key not in dictIn.keys():
        dictIn[key] = []
    dictIn[key].append(val)



def parse_input_mcn(inputfile):
    """ Final function: read inputfile and return dictionary
    """
    if not os.path.isfile(inputfile):
        raise FileNotFoundError(f"Can't find input file {inputfile}")
    output = {}

    # 1. Parse the inputfile
    with open(inputfile) as f:
        obj = None
        for iline, line in enumerate(f):
            line = line.strip()
            
            if (line.strip()=="") or (line.strip().startswith('#')):
                pass
            else:
                raw = line.split()
                if isnumeric(raw[0]):
                    assert obj is not None, \
                        f'Unexpected numerical value at line {iline}:{line}'
                    obj.parse(raw)
                else:
                    if obj is not None:
                        # Finish the previous object
                        obj_name = obj.name
                        if raw[0] != 'END'+obj_name:
                            raise InputSyntaxError(f'Entry {obj.name} is not ended correctly')
                            
                        add_to_dict(output,obj_name,obj)
                        obj = None
                    else:
                        # Start new object
                        obj = parse_header(raw)
                        # If the new object is a tuple, finish it,
                        # otherwise move on to the next line
                        if isinstance(obj,tuple):
                            add_to_dict(output,obj[0],obj[1])
                            obj = None

    # 2. get differents paremeters
    cog_point_raw       = output.get("COGPOINT_BODY", None)
    mass_raw            = output.get("MASS_BODY", None)
    gyration_radius_raw = output.get("GYRADIUS_BODY", None)
    mass_matrix_raw     = output.get("INERTIA_MATRIX", None)
    stiffness_matrix_raw= output.get("STIFFNESS_MATRIX", None)
    damping_matrix_raw  = output.get("DAMPING_MATRIX", None)
    qDamping_matrix_raw = output.get("QDAMPING_MATRIX", None)
    viscous_damping_raw = output.get("LINVISCOUSDAMPING", None)
    amplitude           = output.get("WAVEAMPLITUDE", 1.0)
    zero_encfreq_range  = output.get("WZEROENCFRQ", [[None]])[0][0]
    if zero_encfreq_range is None:
        zero_enc_freq_option_to_range = {
            0 : 0.0,
            1 : 0.1,
            2 : 0.2,
            3 : 0.5,
            4 : 1.0,    
            5 : 2.0   }
        zero_encfreq_option = output.get("ZEROENCFRQ", [[1]])[0][0]
        if zero_encfreq_option in zero_enc_freq_option_to_range.keys():
            zero_encfreq_range = zero_enc_freq_option_to_range[zero_encfreq_option]
        else:
            raise ValueError(f"Invalid ZEROENCFRQ option: {zero_encfreq_option}")

    # cog_point
    assert cog_point_raw is not None , 'Required information missing: COGPOINT'
    nb_body = len(cog_point_raw)
    cog_point = np.zeros((nb_body,3),dtype='float64')
    for item in cog_point_raw:
        cog_point[item[0]-1,:] = item[1:]

    # mass
    if mass_raw is not None:
        mass = np.zeros((nb_body,),dtype='float64')
        for item in mass_raw:
            mass[item[0]-1] = item[1]
    else:
        mass = None

    # gyration_radius
    if gyration_radius_raw is not None:
        gyration_radius =  np.zeros((nb_body,6),dtype='float64')
        for item in gyration_radius_raw:
            val = item[1:]
            if len(val)<6:
                val = np.pad(val,(0., 6-len(gyration_radius)))
            gyration_radius[item[0]-1,:] = val
    else:
        mass = None
        gyration_radius = None
    # mass matrix
    mass_matrix,_       = fill_matrix(mass_matrix_raw,nb_body,withcrossterm=False)

    stiffness_matrix,_  = fill_matrix(stiffness_matrix_raw,nb_body)
    qDamping_matrix,_   = fill_matrix(qDamping_matrix_raw,nb_body)
    damping_matrix_abs,damping_matrix_rel  = fill_matrix(damping_matrix_raw,nb_body)

    if viscous_damping_raw is not None:
        if damping_matrix_rel is None:
            damping_matrix_rel = np.zeros((nb_body,nb_body,6,6),dtype='float64')
        for item in viscous_damping_raw:
            if len(item) == 3:
                body_i = item[0]
                body_j = item[1]
                val   = item[2]
            elif len(item) == 2:
                body_i = body_j = item[0]
                val   = item[1]
            else:
                raise RuntimeError(f'Unexpect vicous damping entry:{viscous_damping_raw}')
            damping_matrix_rel[body_i-1,body_j-1,3,3] = val

    return dict( nb_body                 = nb_body,
                 cog                     = cog_point,
                 mass                    = mass,
                 gyration_radius         = gyration_radius,
                 mass_matrix             = mass_matrix,
                 user_stiffness_matrix   = stiffness_matrix,
                 user_damping_matrix_rel = damping_matrix_rel,
                 user_damping_matrix     = damping_matrix_abs,
                 user_quadratic_damping  = qDamping_matrix ,
                 amplitude               = amplitude,
                 wzeroencfrq             = zero_encfreq_range)



def fill_matrix(raw_data,nb_body,withcrossterm=True):
    if raw_data is None:
        return None,None
    if withcrossterm:
        return fill_matrix_withcrossterm(raw_data,nb_body)
    else:
        return fill_matrix_withoutcrossterm(raw_data,nb_body)

def fill_matrix_withoutcrossterm(raw_data,nb_body):
    matrix_out_1 = np.zeros((nb_body,6,6),dtype='float64')
    matrix_out_2 = np.zeros((nb_body,6,6),dtype='float64')

    for item in raw_data:
        if item.type < 2:
            matrix_out_1[item.body_i-1,:,:] = item.data
        else:
            matrix_out_2[item.body_i-1,:,:] = item.data

    return matrix_out_1,matrix_out_2

def fill_matrix_withcrossterm(raw_data,nb_body):
    matrix_out_1 = np.zeros((nb_body,nb_body,6,6),dtype='float64')
    matrix_out_2 = np.zeros((nb_body,nb_body,6,6),dtype='float64')

    for item in raw_data:
        if item.type < 2:
            matrix_out_1[item.body_i-1,item.body_j-1,:,:] = item.data
        else:
            matrix_out_2[item.body_i-1,item.body_j-1,:,:] = item.data

    return matrix_out_1,matrix_out_2




if __name__ == "__main__" :
    
    from io import StringIO
    test_file_1 = """#Diffraction results to use
FILENAME rd1

#Mass of the body (in kg)
MASS_BODY   1       1.92394E+08

#Center of gravity (in mesh reference)
COGPOINT_BODY  1     148.267     0.000    -4.343

#Rotational inertia
GYRADIUS_BODY  1      15.750    69.147    70.888     0.000     3.523     0.000

#Additional damping in roll
LINVISCOUSDAMPING   1   6.0

INFFREQ

ENDFILE
"""

    with open("test.mcn", "w") as f :  f.write(test_file_1)
    parse_input_mcn( "test.mcn" )
         
    
    
    