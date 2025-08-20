#!/usr/bin/env upython3.sh
import os, sys, mmap
import glob
import numpy as np
import ctypes
import struct
from collections import OrderedDict
from copy import deepcopy
import pandas as pd
import logging
logger = logging.getLogger("Snoopy")
int32 = ctypes.c_int32
int64 = ctypes.c_int64
float64 = ctypes.c_double

class DynProbeReader(object):

    fieldsName = [ "time", "p", "Ux" , "Uy", "Uz", "vof", "ip", "iUx", "iUy", "iUz", "iVof", "iUNormal" ]

    def __init__(self, fileName):
        """Creates a DynProbe object from a data file

        fileName : str
            File to be read

        Parameters
        ----------
        fileName : str
            The name of the data file, e.g. postProcessing/dynamicProbes/0/p000_ceiling.dat
        """

        self.fileName = fileName
        self.header = OrderedDict()
        self._readHeader()


    def header_as_df(self) :
        """Return header as dataframe

        Returns
        -------
        pd.DataFrame
            Header data, as dataframe
        """

        return pd.DataFrame( data = self.header ).transpose().astype( {"pMax" : float , "cellNumber" : int, "nImpact" : int} )


    def cellData_as_df(self, cellNum = None, index = None) :
        """Read cell data and return results as dataframe

        Parameters
        ----------
        cellNum : int or None, optional
            Cell ID. The default is None.
        index  : int or None
            Cell position. The default is None.

        Returns
        -------
        pd.DataFrame
            Cell time series
        """

        info, data = self.readDataInCell( cellNum=cellNum, index=index)
        l = pd.concat( [ pd.DataFrame( data = d_ , columns=self.fieldsName ) for d_ in data ] ).set_index("time")
        l.attrs = info
        return l



    def _readHeader(self):
        logger.info(f"Read header from file: {self.fileName:}")
        fSize = os.path.getsize(self.fileName)
        fid = open(self.fileName, 'rb')
        # read <binSize><tailSize>_END
        fid.seek(-20,2)
        s = struct.Struct('q q 4s')
        ch = fid.read(s.size)
        (binSize,tailSize,sig) = s.unpack(ch)
        binOffset = fSize - binSize - tailSize
        if (sig != b'_END'):
            logger.info("warning: file corrupted, _END not found")
            fid.close()
            self.rebuildHeader()
            return
        if (binSize == 0):
            # sose: tailSize is never zero because it includes the signatures TAIL, _END and everything else inbetween
            logger.warning("warning: file empty")
            return
        # read TAIL <nCells>
        fid.seek(-tailSize,2)
        s = struct.Struct('4s i')
        ch = fid.read(s.size)
        (sig,nCells) = s.unpack(ch)
        if (sig != b'TAIL'):
            logger.info("warning: file corrupted, TAIL not found")
            fid.close()
            self.rebuildHeader()
            return
        # read byteSize <data> ...
        s = struct.Struct('q i i d 3d d 3d') # byteSize, cellNum, nImpact, pMax, UMax, ipMax, iUMax, array_of_offsets
        for i in range(nCells):
            ch = fid.read(s.size)
            (byteSize, cellNumber, nImpact, pMax, UMax0, UMax1, UMax2, ipMax, iUMax0, iUMax1, iUMax2) = s.unpack(ch)
            oSize = byteSize-72 # byteSize of array_of_offsets
            ch = fid.read(oSize)
            if (len(ch) != oSize):
                logger.waring(f"warning: file corrupted, cannot read offset(s) for cell {cellNumber:}")
                fid.close()
                self.rebuildHeader()
                return
            dat = {}
            dat['cellNumber'] = cellNumber
            dat['nImpact'] = nImpact
            dat['pMax'] = pMax
            dat['UMax'] = np.array([UMax0,UMax1,UMax2], dtype=float64)
            dat['ipMax'] = ipMax
            dat['iUMax'] = np.array([iUMax0,iUMax1,iUMax2], dtype=float64)
            dat['nOffset'] = int(oSize/8)
            dat['offset'] = np.frombuffer(ch,dtype=np.int64) + binOffset
            self.header[cellNumber] = deepcopy(dat)
        # read impact 0 on each cell
        # (byteSize, cellNumber, impactNumber, faceIdx, iCell, faceArea, initialFaceNormal, initialFaceCenter, initialCellCenter)
        s = struct.Struct('q i i i i d 3d 3d 3d')
        for key in self.header:
            p = self.header[key]
            offset = p['offset'][0]
            fid.seek(offset)
            ch = fid.read(s.size)
            (byteSize, cellNumber, impactNumber, faceIdx, iCell, magSf, nf0,nf1,nf2, fc0,fc1,fc2, cc0,cc1,cc2) = s.unpack(ch)
            if (impactNumber != 0):
                logger.warning(f'Cell: {key:}, expected nImpact == 0, found: {impactNumber:} at offset: {offset:}')
                continue
            p['faceIndex'] = faceIdx
            p['iCellNumber'] = iCell
            p['faceArea'] = magSf
            p['initialNormal'] = [nf0, nf1, nf2]
            p['initialFaceCenter'] = [fc0, fc1, fc2]
            p['initialCellCenter'] = [cc0, cc1, cc2]
            p['offset'][0] += s.size
        # done
        fid.close()
        pass

    def rebuildHeader(self):
        ''' if the simulation did not end properly (e.g. due to a crash) the data file will not have TAIL signature,
            so we attempt to rebuild it by read the file contents from A to Z
        '''
        def abort_on_error(msg):
            raise Exception(msg)
            pass
        logger.info("Rebuild header ...")
        # search for BIN_
        fSize = os.path.getsize(self.fileName)
        fid = open(self.fileName, 'rb')
        mm = mmap.mmap(fid.fileno(),0, access=mmap.ACCESS_READ)
        binSig = mm.find(b'\nBIN_')
        if (binSig == -1): abort_on_error('cannot find BIN_')
        mm.seek(binSig+5)
        # temporary storage
        header = OrderedDict()
        # read <byte> <data> ...
        sbyte = struct.Struct('q')          # <byteSize>
        shead = struct.Struct('i i')        # <cellNumber, nImpact>
        s0 = struct.Struct('i i d 3d 3d 3d')  # <faceIndex(global), iCellNumber, faceArea, initialFaceNormal, initialFaceCenter, initialCellCenter>
        while (mm.tell() < fSize):
            offset = mm.tell()
            ch = mm.read(sbyte.size)
            (bsize,) = sbyte.unpack(ch)
            ch = mm.read(bsize)
            if (len(ch) != bsize):
                mm.seek(mm.tell()-len(ch)) # rewind
                break
            # read <cellNum, nImpact>
            (cellNumber, nImpact) = shead.unpack(ch[:8])
            keyExist = (cellNumber in header)
            if (not keyExist):
                dat = {}
                dat['cellNumber'] = cellNumber
                dat['nImpact'] = nImpact
                dat['pMax'] = 0.0
                dat['UMax'] = [0.0,0.0,0.0]
                dat['ipMax'] = 0.0
                dat['iUMax'] = np.array([0.0,0.0,0.0], dtype=float64)
                dat['nOffset'] = 0
                dat['offset'] = np.array([], dtype=np.int64)
                dat['faceIndex'] = -1
                dat['iCellNumber'] = -1
                dat['initialNormal'] = [0.0, 0.0, 0.0]
                dat['faceArea'] = 0.0
                header[cellNumber] = deepcopy(dat)
                # end if
            dat = header[cellNumber]
            if ((nImpact > 0) and (not keyExist)):
                logger.info("warning: ImpactN==0 are defined for cellNumber " + str(cellNumber))
            if (nImpact == 0):
                if keyExist:
                    logger.info("warning: ImpactN==0 are defined twice for cellNumber " + str(cellNumber))
                (faceIdx, iCell, magSf, nf0,nf1,nf2, fc0,fc1,fc2, cc0,cc1,cc2) = s0.unpack(ch[8:])
                dat['faceIndex'] = faceIdx
                dat['iCellNumber'] = iCell
                dat['faceArea'] = magSf
                dat['initialNormal'] = [nf0, nf1, nf2]
                dat['initialFaceCenter'] = [fc0, fc1, fc2]
                dat['initialCellCenter'] = [cc0, cc1, cc2]
                # impact 1 must follows immediately after, so we update offset and ch
                offset = mm.tell()
                ch = mm.read(sbyte.size)
                (bsize,) = sbyte.unpack(ch)
                ch = mm.read(bsize)
                if (len(ch) != bsize):
                    mm.seek(mm.tell()-len(ch)) # rewind
                    break
                (chkCellNum, nImpact) = shead.unpack(ch[:8])
                if (cellNumber != chkCellNum) or (nImpact != 1):
                    del header[cellNumber]
                    break
                # end if
            # update and append new offset
            dat['nImpact'] = max(dat['nImpact'], nImpact)
            dat['nOffset'] += 1
            dat['offset'] = np.append(header[cellNumber]['offset'],[offset])
            # read <t,p,U,vof,...>, we need only the header
            # note: max. values are not "simple max."
            nRows = int((bsize-8)/(12*8))
            tmpArray = np.frombuffer(ch[8:], dtype=np.float64).reshape((nRows,12));
            # p
            tmp = np.fabs(tmpArray[:,1])
            abs_pMax = np.amax(tmp)
            idx_pMax = np.where(tmp == abs_pMax)
            if (abs(dat['pMax']) < abs_pMax): dat['pMax'] = tmpArray[idx_pMax][0,1]
            # U
            tmp = np.linalg.norm(tmpArray[:,2:5], axis=1)
            abs_UMax = np.amax(tmp)
            idx_UMax = np.where(tmp == abs_UMax)
            if (np.linalg.norm(dat['UMax']) < abs_UMax): dat['UMax'] = tmpArray[idx_UMax][0,2:5]
            # ip
            tmp = np.fabs(tmpArray[:,6]) # ip
            abs_ipMax = np.amax(tmp)
            idx_ipMax = np.where(tmp == abs_ipMax)
            if (abs(dat['ipMax']) < abs_ipMax): dat['ipMax'] = tmpArray[idx_ipMax][0,6]
            # iU
            tmp = np.linalg.norm(tmpArray[:,7:10], axis=1)
            abs_iUMax = np.amax(tmp)
            idx_iUMax = np.where(tmp == abs_iUMax)
            if (np.linalg.norm(dat['iUMax']) < abs_iUMax): dat['iUMax'] = tmpArray[idx_iUMax][0,7:10]
            # end while
        #
        self.header = deepcopy(header)
        mm.close()
        fid.close()
    def getCellList(self):
        return list(self.header.keys())

    def readDataInCell(self, cellNum=None, index=None):
        """Read cell data

        Parameters
        ----------
        cellNum : int, optional
            ID of the cell. The default is None.
        index : int, optional
            Position of the cell. The default is None.

        Returns
        -------
        res : tuple ( infoDict , ListOfArray )
            Each array corresponds to one impact, and has the following channels :
                t, p, U(3), vof, ip, iU(3), iVof, iUNormal.
        """
        if (cellNum is None):
            if (index is None):
                raise(Exception("Error: cellNum nor index are defined"))
            cellNum = self.getCellList()[index]
        if (cellNum not in self.header):
            raise(Exception("Error: cellNumber " + str(cellNum) + " not found"))
        p = self.header[cellNum]
        listOfData = []
        for i in range(0,p['nImpact']):
            listOfData.append([])
        s = struct.Struct('q i i') # byteSize CellNum n
        fid = open(self.fileName, 'rb')
        for offset in p['offset']:
            fid.seek(offset)
            ch = fid.read(s.size)
            (byteSize, chkCell, ImpactNum) = s.unpack(ch)
            if (cellNum != chkCell):
                raise(Exception("Error: expect cellNum: ", cellNum, ", found: ", chkCell, ", at offset: ", offset))
            n = ImpactNum-1
            byteSize -= 8
            nRows = int(byteSize/(12*8))
            ch = fid.read(byteSize)
            listOfData[n].append(np.frombuffer(ch, dtype=np.float64).reshape((nRows,12)))
        for i in range(0,p['nImpact']): listOfData[i] = np.vstack(listOfData[i])
        # DEBUG
        #np.set_printoptions(threshold=sys.maxsize)
        #print(listOfData[0][:,0])
        return (p,listOfData)

if __name__ == "__main__":
    import sys
    np.set_printoptions(threshold=sys.maxsize)
    dp = DynProbeReader(fileName="p005_transBulkheadFore.dat")
    (p,data) = dp.readDataInCell(index=0)

    # DEBUG: show time axis of each impact
    for n in range(0,len(data)):
        print("time for impact", (n+1), "of cell",p['cellNumber'],":", data[n][:,0])
    # DEBUG: testing rebuildHeader()
    dp_broken = DynProbeReader(fileName="p005_transBulkheadFore.dat_broken")
    (p1,data1) = dp_broken.readDataInCell(index=0)
    print(p)
    print(p1)


