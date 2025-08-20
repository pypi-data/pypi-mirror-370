from ..Tools.print_format import write_matrix
from .mass_distribution import MassObject,MassElementABC,\
            MassElementTriLinCont,CollectMassElement, \
            MassElementPonctual, MassElementTriLin,\
            MassElementPlan,legacy_format
import numpy as np
import os
import re
from Snoopy import logger

#---------------------------------------------------------------------------#
#                       UTILITY FUNCTIONS                                   #
#---------------------------------------------------------------------------#
def _compare_message(check_level,elim_logic,message,isequal):
    """Utility function, useful when there are a list of things to check, 
    only 1 fail will cause the whole check fail
    Parameters
    ----------
    check_level : int
        choice of behavior: depend on check_level, the routine will either:
        - check_level = 0: only return True or False
        - check_level = 1: beside return True or False, print an message to 
                            indicate why the logic fail
        - check_level = 2: stop raise an assert error if elim_logic is False
    elim_logic : bool
        Results of check
    message : str
        message to be display
    isequal : bool
        final total check 
    Returns
    -------
    bool
        final total check 
    """
    if check_level == 1:
        if not elim_logic:
            print('Warning:'+message)
    else:
        assert elim_logic,message
    return elim_logic and isequal



#---------------------------------------------------------------------------#
#                               Section object                              #
#---------------------------------------------------------------------------#
class Section(MassObject):
    """ The mass section of a ship at a given point

    It's a MassObject but with some more property and a write_don method
    """

    def __init__(self,ID,section_point,global_CoG,element_CoG,inertia_matrix,
                VIS44PC = 0.):
        """Initialisation
        
        Parameters
        ----------
        ID : float
            ID of the object, correspond to SECTION N° in _wld.don file
        section_point : ndarray(3,)
            Reference point of the section 
        global_CoG : ndarray(3,)
            all the element of type ShipCut will have refpoint at Global CoG
        element_CoG : ndarray(3,)
            CoG of the section
        inertia_matrix: ndarray(6,6)
            Inertia matrix given at Global CoG
        VIS44PC : float
            % of additional viscous roll 
        """
        super().__init__(inertia_matrix = inertia_matrix,
                         CoG            = element_CoG,
                         ref_point      = global_CoG )
        self.ID = ID
        self.section_point = np.asarray(section_point)
        self.VIS44PC = VIS44PC

    def write_don(self):
        """Return the string block for _wld.don format."""

        return f"""
SECTION_No  {self.ID}
REFPOINT   {self.section_point[0]} {self.section_point[1]} {self.section_point[2]}
COGFROMAP  {self._CoG[0]} {self._CoG[1]} {self._CoG[2]}
VIS44PC    {self.VIS44PC:}
INERTMATRIX
{write_matrix(self._inertia_matrix_at_ref_point)}ENDSECTION 
""" 



    def _compare_section(self,other_section,
                    check_level = 0):
        """Compare Section, used mainly for pytest (or elsewhere need comparison)

        It do the same thing as __eq__ but with less strict comparing policy
        Mainly due to the writing format of fortran have less significant decimal
        Parameters
        ----------
        other : Section
            another section to be compared with self
        check_level : int
            Choise of behavior, optional, by default 0
            0: return False if non equal, True otherwise
            1: write an additional warning where the different is if non equal
            2: assert equal            
        """
        def _is_points_close(p1,p2,tol = 1e-3 ):
            diff =  p1 - p2
            distance = np.sqrt(np.dot(diff,diff))
            return distance <tol
        isEqual = True
        me1 = self
        me2 = other_section
        #isEqual = _compare_message(check_level,self.id ==other.id,
        #        f"2 section doesn't have same ID",isEqual) 

        isEqual = _compare_message(check_level,_is_points_close(me1._ref_point, me2._ref_point),
                f"Section {me1.ID} doesn't have same refpoint",isEqual)                 

        isEqual = _compare_message(check_level,_is_points_close(me1._CoG,me2._CoG),
                f"Section {me1.ID} doesn't have same CoG!",isEqual)    

        #isEqual = _compare_message(check_level,self.VIS44PC == other.VIS44PC,
        #        f"Section {self.id} doesn't have same VIS44PC",isEqual) 
        diffMat = (me1._inertia_matrix_at_ref_point - me2._inertia_matrix_at_ref_point).flat
        refMat = np.asarray(me1._inertia_matrix_at_ref_point.flat)
        refVal = np.sqrt(np.dot(refMat,refMat))
        if refVal < 1:
            diff = np.sqrt(np.dot(diffMat,diffMat))
        else:
            diff = np.sqrt(np.dot(diffMat,diffMat)) /refVal

        isEqual = _compare_message(check_level,diff<1e-5,
                f"Section {me1.ID} doesn't have same inertia matrix, relative error = {diff}",isEqual)    

        return isEqual


#---------------------------------------------------------------------------#
#                       Collection of sections object                       #
#---------------------------------------------------------------------------#
class AllSections:
    """This object correspond to a whole ship, but compare to WLDFile, 
    it contain only sections, and intended to be use as a parser
    It can be intialized as the result of reading _wld.don
    It might contain a attribute of class WLDFile
    """
    def __init__(self):

        self.sectionlist     = []

        #------------------#
        self.mass       = None
        self.CoG        = None
        self.gyration   = None
        
        
    def get_mcn_input( self ) :
        """Return global mass properties
        
        Returns
        -------
        xarray.Dataset
            The global mass properties

        """
        from .hydro_coef import McnInput
        CoG = np.array([self.CoG])    
        obj = McnInput.Build(  nb_body = 1,
                                cog     = CoG,
                                mass    = np.array([self.mass]),
                                gyration_radius  = np.array([self.gyration]),
                                ref_point = CoG )
        return obj

    def set_ref_point(self, new_ref_point):
        logger.debug(f"Set ref_point to {new_ref_point}.")
        for section in self.sectionlist:
            section.set_ref_point(new_ref_point)
        self._ref_point = new_ref_point
    

    @property
    def ref_point(self):
        if hasattr(self,"_ref_point"):
            return self._ref_point
        else:
            return self.CoG


    
    #-------------------------------------------> Lire wld.don
    @staticmethod
    def read_don(filename):
        """Parse the _wld.don file
        
        Parameters
        ----------
        filename : str
            path to _wld.don file

        Returns
        -------
        AllSections
            List of section object, with some all bodies infos
        """
        obj = AllSections()
        
        with open(filename,'r') as f:
            buf = f.read()
            content = "\n".join( [ s.strip() for s in buf.splitlines() if not s.startswith("#")] )


        for match in re.finditer(r"^MASS_BODY(.*?)\n", content, re.MULTILINE | re.DOTALL):
            raw = (match.group().split())
            body_id         = int(raw[1])
            if body_id != 1:
                raise ValueError("We accept only 1 body")
            obj.mass   = float(raw[2])
        
        for match in re.finditer(r"^COGPOINT_BODY(.*?)\n", content,re.MULTILINE | re.DOTALL):
            raw = (match.group().split())
            body_id         = int(raw[1])
            if body_id != 1:
                raise ValueError("We accept only 1 body")            
            obj.CoG   = global_CoG = np.asarray([float(item) for item in raw[2:]])

        for match in re.finditer(r"^GYRADIUS_BODY(.*?)\n", content, re.MULTILINE | re.DOTALL):
            raw = (match.group().split())
            body_id         = int(raw[1])
            if body_id != 1:
                raise ValueError("We accept only 1 body")
            obj.gyration = np.asarray([float(item) for item in raw[2:]])


        def parse_data(line,dataname,expected_format):
            if not line.startswith(dataname):
                raise ValueError(f"Error in format: expect {dataname} at line:{line}")
            line_splitted = line.split()
            return [str_format(str_val) \
                    for str_val,str_format in zip(line_splitted[1:],expected_format)]


        
        for ii,item in enumerate(\
                re.finditer(r"^SECTION_No(.*?)ENDSECTION\n", content,re.MULTILINE | re.DOTALL)):
            lines = item.group().splitlines()

            ID = parse_data(lines[0],"SECTION_No",[int])[0]

            # ATTENTION! REFPOINT dans fichier WLD.don is where section were defined!
            # It's not the point where inertia matrix is computed!!
            section_point   = np.asarray(parse_data(lines[1],"REFPOINT",[float]*3))
            cog_point       = np.asarray(parse_data(lines[2],"COGFROMAP",[float]*3))
            VIS44PC         = parse_data(lines[3],"VIS44PC",[float])[0]
            _inertia_matrix_at_ref_point =  np.zeros((6,6),dtype=float)
            if not lines[4].startswith("INERTMATRIX"):
                raise  ValueError(f"Expect INERTMATRIX at 5th line! Received: {lines[4]}")
            iline_start_matrix = 5 #We know that the matrix data start at line n°6
            for iline in range(6):
                data_raw = lines[iline + iline_start_matrix].split()
                _inertia_matrix_at_ref_point[iline] = np.asarray([float(item) for item in data_raw])

            obj.sectionlist.append(Section(  ID = ID,
                            section_point   = section_point,
                            global_CoG      = global_CoG,
                            element_CoG     = cog_point,
                            inertia_matrix  = _inertia_matrix_at_ref_point,
                            VIS44PC         = VIS44PC))
        return obj


        

    #-------------------------------------------> Read .wld
    @staticmethod
    def from_wld(filename, dispatch_load = None, use_upstream = True ):
        """Import wld file and compute section mass matrix

        Parameters
        ----------
        filename : str
            path to .wld file

        use_upstream : bool
            use mass distribution before the cut

        Returns
        -------
        AllSections
            built object
        """

        if not callable( dispatch_load ):
            if dispatch_load is None:
                def dispatch_load(*args):
                    return 0.0
            else:
                min_, max_ = dispatch_load
                def dispatch_load(x,y,z):
                    return np.clip((x - min_) / (max_ - min_) , 0.0 , 1.0)


        all_sections_obj = AllSections()

        #----------------> Parse wld file : start parsing
        if not os.path.isfile(filename):
            raise FileNotFoundError(f"Input file {filename} not found!!")

        with open(filename,"r") as f:
            buf = f.read()
            content = "\n".join( [ s.strip() for s in buf.splitlines() if not s.startswith("#")] )

        for matches in re.finditer(r"^ZFSURFACE(.*?)\n", content, re.DOTALL):
            zfsurface_str = matches.group().split()
            zfsurface = float(zfsurface_str[1])

        #-----------------------> Parse wld file : parse section
        cut_list = {}
        for matches in re.finditer(r"^SECTION(.*?)ENDSECTION\n", content, re.MULTILINE | re.DOTALL):
            lines = matches.group().splitlines()
            for line in lines[1:-1]:
                line_splitted = line.split()
                if (len(line_splitted) != 4):
                    raise ValueError(f"Expect 4 numbers: ID x y z, received {line_splitted} instead")
                id = int(line_splitted[0])
                cut_point = np.array([float(item) for item in line_splitted[1:]])
                if zfsurface != 0:
                    cut_point[2] -= zfsurface
                cut_list[id]  = cut_point


        #-----------------------> Parse wld file : parse mass element and construct object
        collect_element = CollectMassElement.from_wld( filename )

        #-----------------------> Compute section:
        for elem in collect_element._mass_element_list:
            elem.solve()
            
        all_sections_obj.CoG        = global_CoG = collect_element.CoG
        all_sections_obj.mass       = collect_element.mass
        all_sections_obj.gyration   = collect_element.gyration

        for isection,section_point in cut_list.items():
            amont = CollectMassElement()
            aval  = CollectMassElement()
            for elem in collect_element._mass_element_list:
                elem1, elem2 = elem.cutX(section_point[0])
                amont.add_element(elem1)
                aval.add_element(elem2)
            #---------------------------------#
            if use_upstream:
                all_sections_obj.sectionlist.append(
                    Section(isection,section_point,global_CoG,
                            element_CoG = amont.CoG,
                            inertia_matrix = amont.get_inertia_matrix_at(global_CoG),
                            VIS44PC  = dispatch_load( *section_point) ) )
            else:
                all_sections_obj.sectionlist.append(  
                    Section(isection,section_point,global_CoG,
                            element_CoG = aval.CoG,
                            inertia_matrix = aval.get_inertia_matrix_at(global_CoG),
                            VIS44PC  = 1-dispatch_load( *section_point) ))

        return all_sections_obj



    #-------------------------------------------> Ecrire wld.don
    def write_don(self,filename):
        """Write content of target to don file.
        
        Parameters
        ----------
        filename : str
            target file to write to

        
        distributionVIS44PC: function to determine VIS44PC
            the VIS44PC will be result of evaluation of 
            distributionVIS44PC at section point

        Returns
        -------
        str
            filename automatically generated
        """

        with open(filename,"w") as f:
            f.write(f"""
MASS_BODY   1        {self.mass}

COGPOINT_BODY   1      {self.CoG[0]}     {self.CoG[1]}    {self.CoG[2]}

GYRADIUS_BODY   1       {self.gyration[0]}     {self.gyration[1]}    {self.gyration[2]}     {self.gyration[3]}     {self.gyration[4]}    {self.gyration[5]}
    """)
            for section in self.sectionlist:
                f.write(section.write_don())
            f.write("\nENDFILE")
        return filename


    #-------------------------------------------> Debug: compare with another one
    def _compare(self,other,check_level=0):
        """Compare with another object


        It do the same thing as __eq__ but with less strict comparing policy
        Mainly due to the writing format of fortran have less significant decimal
        Parameters
        ----------
        other : WLDFile
            Object to be compare
        check_level : int
            Choise of behavior, optional, by default 0
            0: return False if non equal, True otherwise
            1: write an additional warning where the different is if non equal
            2: assert equal 

        """
        isEqual = True
        isEqual = _compare_message(check_level,isinstance(other,self.__class__),            
                f"Can't compare object WLDFile with object type {other.__class__}",isEqual)


        diffmass = abs(self.mass - other.mass )
        reldiff = diffmass/abs(self.mass )
        isEqual = _compare_message(check_level,reldiff<1e-5,            
            f"""Different in mass {self.mass } vs {other.mass }:
    relative different = {reldiff*100}%
    absolute different = {diffmass}""",isEqual)

        diffCoG =  self.CoG - other.CoG
        distanceCoG = np.sqrt(np.dot(diffCoG,diffCoG))
        isEqual = _compare_message(check_level,distanceCoG<1e-3,            
            f"Different in CoG, distance = {distanceCoG} ",isEqual)

        diff_gyration = self.gyration - other.gyration
        distance_gyration = np.sqrt(np.dot(diff_gyration,diff_gyration))
        isEqual = _compare_message(check_level,distance_gyration<1e-3,            
            f"Different in GYRADIUS, L2 difference: {distance_gyration}!",isEqual)


        isEqual = _compare_message(check_level,len(self.sectionlist) == len(other.sectionlist),\
                f"2 object doesn't have same ID of bodies",isEqual)                
        for section1,section2 in zip(self.sectionlist,other.sectionlist):
            isEqual = section1._compare_section(section2,check_level)
        return isEqual
