from __future__ import print_function

class CallCounter(object):
   """Decorator to determine number of calls for a method"""
   def __init__(self,method):
      self.method=method
      self.counter=0
   def __call__(self,*args,**kwargs):
      self.counter+=1
      return self.method(*args,**kwargs)

if __name__ == "__main__" :

   @CallCounter
   def myFunc():
      print ("truc")

   for i in range(10) :
      myFunc()
   print (myFunc.counter)