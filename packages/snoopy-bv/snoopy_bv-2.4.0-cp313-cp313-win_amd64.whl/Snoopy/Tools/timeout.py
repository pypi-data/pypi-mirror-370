"""
   Decorator to time out a function
"""
import threading
import functools
import logging

def timeout(duration, default=None):
    """Decarator to timeout a function.
    
    Example
    -------
    >>> @timeout(1)
    ... def timeOutSleep(i):
    ...      sleep(i)
    ...      return True
    >>> print (timeOutSleep(0.5))
    True
    >>> print (timeOutSleep(2.0))
    WARNING:root:timeout in function <function timeOutSleep at 0x000001F35DE71300>: args: (2,), kwargs: {}
    None
    """

    def decorator(func):
        class InterruptableThread(threading.Thread):
            def __init__(self, args, kwargs):
                threading.Thread.__init__(self)
                self.args = args
                self.kwargs = kwargs
                self.result = default
                self.daemon = True

            def run(self):
                try:
                    self.result = func(*self.args, **self.kwargs)
                except Exception:
                    pass

        @functools.wraps(func)
        def wrap(*args, **kwargs):
            it = InterruptableThread(args, kwargs)
            it.start()
            it.join(duration)
            if it.is_alive():
                logging.warning('timeout in function {0}: args: {1}, kwargs: {2}'.format(func, args, kwargs))
            return it.result
        return wrap
    return decorator

if __name__ == "__main__" :

   print ('Run')
   from time import sleep

   @timeout(1)
   def timeOutSleep(i):
      sleep(i)
      return True

   print (timeOutSleep(0.5))
   print (timeOutSleep(2))

   print (timeout(0.5)(sleep)(1))
   print (timeout(2.0)(sleep)(1))



