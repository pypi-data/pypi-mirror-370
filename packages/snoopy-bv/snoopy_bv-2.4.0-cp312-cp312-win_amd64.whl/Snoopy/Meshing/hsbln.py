from Snoopy.Meshing.balance import hsbln
import sys
import os

if __name__ == "__main__":
   proj_name = None
   if len(sys.argv) < 2:
       sys.exit( "use: hsbln InputFile [ProjectName]")

   filename = sys.argv[1]
   if len(sys.argv)==3 : proj_name = sys.argv[2]

   if not os.path.exists(filename): #le fichier n'existe pas
      sys.exit( "Can not find the input file " + filename )

   hsbln( filename ) #, proj_name )
