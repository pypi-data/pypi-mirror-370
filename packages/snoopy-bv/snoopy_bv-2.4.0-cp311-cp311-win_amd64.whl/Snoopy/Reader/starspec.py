"""
   Translate from StarSpec input file to Snoopy scripts
"""
import re
import os
import numpy as np
from io import StringIO
from Snoopy import Spectral as sp
from Snoopy import logger



class StarspecParser(object):
    """
    Parse Snoopy input file

    .get provide prepared data (Snoopy object when relevant)
    """


    def __str__(self) :

        t = 'scatter' if self._scatter else f'list of len(self.)'
        return f"""nrao = {len(self._raoList):}
Seastate input as {t:}
"""



    def __init__(self, filename):

        self._filename = filename

        self.ssList = []

        self._dir = os.path.dirname(filename)

        with open(filename, "r") as f :
            self.content = "".join( [line for line in f.readlines() if not line.startswith("#") ] )

        self._parse_RAO_PATH()

        self._parse_RAO_FILE()

        #------- Read azimuth
        self.azim, self.azimProb = self.getDirProb(keyword = "AZIMUTH")

        #------- Interpolation options
        step = re.search(r'\n\s*STEP\s*(.*)', self.content)
        if step :
            self.step = float(step.group(1))
        else :
            self.step = 0.001

        nb_hstep = re.search(r'\n\s*NB_HSTEP\s*(.*)', self.content)
        if nb_hstep :
            self.nb_hstep = int(nb_hstep.group(1))
        else :
            self.nb_hstep = 72

        #------- Parse spectrum type
        self._specType =  re.search(r'SPECTRE_TYPE.*\n.*?ENDSPECTRE_TYPE', self.content, re.DOTALL).group().splitlines()[1:-1]

        #-------Scatter diagram, seastate list or list_generic ?
        self._list_seastates = re.search(r'LIST_SEASTATE.*\n.*?ENDLIST_SEASTATE', self.content, re.DOTALL)
        if self._list_seastates is not None :
            self._list_seastates = self._list_seastates.group().splitlines()[1:-1]

        self._scatter = re.search(r'SCATTER.*\n.*?ENDSCATTER', self.content, re.DOTALL)

        self._list_generic = re.search(r'LIST_GENERIC.*\n.*?ENDLIST_GENERIC', self.content, re.DOTALL)

        self.nbmode = re.search( r'.*LIST_SEASTATE.*NBMODE\s*(\d+)\s*\n', self.content)
        if self.nbmode is not None :
            self.nbmode = int(self.nbmode.group(1))
        elif self._list_generic is not None:
            self.nbmode = 1

        #------- Read specrum info
        if self._scatter :
            self._parse_scatter()



    def getDirProb(self, keyword = "WAVEDIR_PROB"):
        iso = re.search( keyword + r'.*ISO\s*(\d+)\s*\n', self.content)
        if iso is not None :
            iso = int(iso.group(1))
            return np.linspace(0, 360, iso, endpoint=False) , iso*[1/iso]
        wavedir, wavedirProb = re.search( keyword + r'((.*\n){3})', self.content).group().splitlines()[1:]
        return [float(i) for i in wavedir.split()] ,  [float(i) for i in wavedirProb.split()]


    def _parse_RAO_FILE(self):
        self._raoList = re.search(r'RAO_FILE.*\n.*?ENDRAO_FILE', self.content, re.DOTALL).group().splitlines()[1:-1]


    def _parse_RAO_PATH(self):
        self._raopList = re.search(r'RAO_PATH.*\n.*?ENDRAO_PATH', self.content, re.DOTALL).group().splitlines()[1:-1]


    def _parse_scatter(self) :
        #---------- read scatter diagram data
        if "NB_TZ" in self._scatter.group().splitlines()[0] :
            self.tz = True
        elif "NB_TP" in self._scatter.group().splitlines()[0] :
            self.tz = False
        else :
            raise(Exception("Incorrect syntax in StarSpec file"))

        #read scatter table
        scatter_ = self._scatter.group().splitlines()[1:-1]
        self.SD_period = [float(i) for i in scatter_[0].split()]
        tab = np.loadtxt( StringIO( "\n".join(scatter_[1:]) ) )
        self.SD_hs = tab[:,0]
        self.SD_data = tab[:,1:]

        #Read wave direction
        self.SD_wavedir, self.SD_wavedirProb =  self.getDirProb("WAVEDIR_PROB")

        #Read spectrum type
        if "JONSWAP" == self._specType[0].split()[0] :
            self.specType = sp.Jonswap
            self.SD_gamma = float(self._specType[0].split()[1])

        if len( self._specType ) > 1 :
            if "SPREADING" == self._specType[1].split()[0] :
                if self._specType[1].split()[1]  == "COSN" :
                    self._spreadingType = sp.SpreadingType.Cosn
                self._spreadingValue = float(self._specType[1].split()[2] )
        else:
            self._spreadingType = sp.SpreadingType.No
            self._spreadingValue = -1.0


    def getSpreadingTypesAndValues(self):
        sline = [l for l in self._specType if "SPREADING" in l]
        if len(sline) == 1:
            types_ = [ sp.SpreadingType.__members__[ i.capitalize() ] for i in sline[0].split()[1::2] ]
            values_ = [ float(v) for v in sline[0].split()[2::2] ]
            return types_ , values_
        elif len(sline) == 0:
            return [ sp.SpreadingType.No ] * self.nbmode , [-1] * self.nbmode

        else :
            raise(Exception)

    def getListSeaStates(self):
        """

        Returns
        -------
        ssList : List of sp.SeaState
        """

        ssList = []
        if self._scatter is not None :
            self.SD_data /= np.sum(self.SD_data)

            for ihs, hs in enumerate(self.SD_hs) :
                for it, t in enumerate(self.SD_period) :
                    if self.tz :
                        tp = sp.Jonswap.tz2tp( t, self.SD_gamma )
                    else :
                        tp = t

                    for wdir, pwdir in zip(self.SD_wavedir , self.SD_wavedirProb) :
                        for azim, pazim in zip(self.azim , self.azimProb) :
                            prob = self.SD_data[ ihs, it ] * pwdir * pazim
                            relHeading = -wdir + azim + 180

                            ssList.append(  sp.SeaState( self.specType( hs = hs , tp = tp , gamma = self.SD_gamma,
                                                         heading = np.deg2rad(relHeading)  ,
                                                         spreading_type = self._spreadingType,
                                                         spreading_value = self._spreadingValue,
                                                        ),
                                                         probability = prob ) )
        elif self._list_seastates is not None :

            spreadTypes_, spreadValues_ = self.getSpreadingTypesAndValues()

            for ssParamS in self._list_seastates :
                specList = []
                ssParam = [float(i) for i in ssParamS.split()]
                for ispec in range( self.nbmode ) :
                    specList.append( sp.Jonswap( hs = ssParam[1] , tp = ssParam[2] , gamma = 1.0 ,
                                                heading = np.deg2rad(ssParam[0])  ,
                                                spreading_type = spreadTypes_[ispec] ,
                                                spreading_value = spreadValues_[ispec] ,
                                                )
                                    )

                ssList.append( sp.SeaState( specList ) )

        return ssList


    def getRaos(self) :
        """Return List of Snoopy.Rao, with appropriate processing

        Returns
        -------
        l : list
            List of Snoopy RAOs
        """
        l = []
        for path_ in self._raopList :
            for raol in self._raoList:
                raol = raol.strip().split()[0]
                rao = sp.Rao( os.path.join( self._dir, path_ ,  raol  ))
                #Apply options
                #TODO
                l.append( rao )
        return l
