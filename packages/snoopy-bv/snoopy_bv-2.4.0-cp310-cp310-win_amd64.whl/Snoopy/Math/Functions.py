'''
Created on 24 mars 2020

@author: cbrun
'''

import inspect
import re
import sys
import numpy

from _Math import _Functions
try:
    from Opera import Math
except ImportError:
    from Snoopy import Math


SEPARATORS = ('; ', ';', ' ;', ' ; ')
SEPARATOR = SEPARATORS[0]


class FunctionsException(Exception):
    """Function exception"""

def getTuple(function):
    d = function.getSerializable()
    # case function of type RiToRj
    if d['type'][2:5] == "ToR":
        type_str = (d['type'][6:],)
    # case wrapped cpp function
    else:
        type_str = (d['type'],)
    args = tuple(d['arguments'])
    return type_str + args

def getFunctionTypeDimensions(t, NoTest=False):
    """t: type of the Value"""
    if not NoTest:
        if not IsFunctionType(t):
            return 0, 0
    typeName = t.__name__
    rex = re.compile("^R.ToR.")
    s = rex.match(typeName)[0]
    return (int(s[1]), int(s[5]))

def IsFunctionType(t):
    """t: type of the Value"""
    try:
        typeName = t.__name__
        rex = re.compile("^R.ToR.")
        return bool(rex.match(typeName))
    except:
        return False


def AsFunction(vals, N=None, M=None):
    if not (N and M):
        if IsFunctionType(type(vals)):
            return vals
        elif type(vals) is dict:
            return getattr(Math.Functions, vals['type'])(vals)
        else:
            raise ValueError(f'AsFunction : cannot guess function dimensions from {type(vals)}')

    if isinstance(vals, getattr(Math.Functions, "_R{}ToR{}ABC".format(N, M))):
        return vals
    if type(vals) in (float, int, numpy.float64):
        return getattr(Math.Functions, 'R{}ToR{}Uniform'.format(N, M))(vals)
    if type(vals) is dict:
        try:
            return getattr(Math.Functions, vals['type'])(vals)
        except AttributeError:
            from Opera import SlenderBodies
            return getattr(SlenderBodies, vals['type'])(vals)
    fctName = "R{}ToR{}Uniform".format(N, M)  # Default function
    if type(vals) is str:
        # FIXME this is a small hack for specific functions saved as strings
        # Try to split it
        tmp = vals.split(";")
        vals = [tmp[0],]
        if len(tmp) > 1:
            vals.extend(list(map(float, tmp[1:])))
    if type(vals[0]) is str:
        if hasattr(Math.Functions, vals[0]):
            fctName = vals[0]
            vals = vals[1:]
        else:
            fctName = "R{}ToR{}{}".format(N, M, vals[0])
            if hasattr(Math.Functions, fctName):
                vals = vals[1:]
    else:
        try:
            return getattr(Math.Functions, vals[0][0])(*tuple(vals[0][1]), **vals[1])
        except Exception:
            pass
    try:
        return getattr(Math.Functions, fctName)(*tuple(vals))
    except SyntaxError:
        pass
    raise FunctionsException('Wrong Function format')

def listDepth(L):
    if type(L) is not list:
        return 0
    else:
        if not L:
            return 1
        return 1 + listDepth(L[0])

def polyCoefsToExpression(coefs, variable='X'):
    expression = ''
    for deg, coef in enumerate(coefs):
        if coef == 0.0:
            continue
        if deg == 0:
            expression+=f'{coef} + '
        elif deg == 1:
            expression+=f'{coef}*{variable} + '
        else:
            expression+=f'{coef}*{variable}**{deg} + '
    if not expression:
        expression = '0.0'
    else:
        expression = expression[:-3]
    return expression

def polynomialToAnalytical(func):
    #===============================================================================================
    # Note : polynomial functions only existe for R1ToRn dimensions
    #===============================================================================================
    if type(func) is tuple:
        t = func
    elif IsFunctionType(type(func)):
        t = getTuple(func)
    coefs = t[-1]
    depth = listDepth(coefs)
    dim1, dim2 = getFunctionTypeDimensions(type(func))
    if depth == 1:
        expression = polyCoefsToExpression(coefs)
        return eval("Math.Functions.R1ToR1Analytical(expression, 'X')")
    elif depth == 2:
        expressionsList = []
        for coefList in coefs:
            expressionsList.append(polyCoefsToExpression(coefList))
        retFuncCls = eval(f'R{dim1}ToR{dim2}Analytical')
        return retFuncCls(expressionsList, 'X')
    else:
        raise ValueError(f'Coefficient must have a list depth of either 1 or 2')

def _AdaptArguments(args, isAnalytical=False):
    adaptedArguments = []
    constructionArgs = []
    execCode = []
    for arg in args:
        if type(arg) is dict:
            # Adaptation requested !
            # args come from serialization
            try:
                adaptedArguments.append(
                    eval("Math.Functions.{}(*tuple(arg['arguments']))".format(
                        arg['type'], arg)))
            except AttributeError:
                from Opera import SlenderBodies
                adaptedArguments.append(
                    eval("SlenderBodies.{}(*tuple(arg['arguments']))".format(
                        arg['type'], arg)))
            constructionArgs.append(arg)
        elif type(arg) in (list, tuple):
            try:
                t = numpy.asarray(arg, dtype=float)
                if isAnalytical:
                    # Analytical functions expect fixed size arrays
                    # so we can't provide numpy arrays but lists or tuples
                    adaptedArguments.append(arg)
                else:
                    adaptedArguments.append(t)
                constructionArgs.append(arg)
            except:
                a, c, e = _AdaptArguments(arg)
                adaptedArguments.append(a)
                constructionArgs.append(c)
                execCode.extend(e)
        elif callable(arg):
            adaptedArguments.append(arg)
            if type(arg).__name__ in dir(_Functions):
                constructionArgs.append(arg.getSerializable())
            else:
                try:
                    codeStr = ''.join(inspect.getsourcelines(arg)[0])
                    whiteSpaces = codeStr.split('def')[0]
                    if whiteSpaces:
                        codeStr = codeStr.replace('\n'+whiteSpaces, '\n')[len(whiteSpaces):]
                    name = codeStr.split('(')[0].replace('def ', '')
                    constructionArgs.append(name)
                    execCode.append(codeStr)
                except TypeError:
                    constructionArgs.append(arg)
        else:
            adaptedArguments.append(arg)
            for attr in ('tolist', 'getSerializable'):
                if hasattr(arg, attr):
                    constructionArgs.append(getattr(arg, attr)())
                    break
            else:
                constructionArgs.append(arg)
    return adaptedArguments, constructionArgs, execCode


class _DecoratorFunction:

    def __init__(self, *args):
        self._functors = []
        functors = []
        if len(args) == 1:
            arg, = args
            if type(arg) is dict:
                # from serialization
                if arg['type'] != self.__class__.__name__:
                    raise FunctionsException(
                        'Wrong function type {} {}'.format(
                            arg['type'],
                            self.__class__.__name__))
                execCode = arg['execCode']
                functors = arg['functors']
                if execCode:
                    for eXcode in execCode:
                        exec(eXcode, globals())
                    self._constructionArgs = arg['arguments']
                    self._execCode = execCode
                    eval('super(_DecoratorFunction, self).__init__({})'.format(
                              ', '.join(self._constructionArgs)))
                    for functor in functors:
                        N = int(functor['type'][1])
                        M = int(functor['type'][5])
                        self.addFunctor(functor['name'], AsFunction(functor, N, M))
                    return
                args = arg['arguments']
        isAnalytical = "Analytical" in str(self.__class__)
        adaptedArguments, c, e = _AdaptArguments(args, isAnalytical)
        self._constructionArgs = c
        self._execCode = e
        super(_DecoratorFunction, self).__init__(*adaptedArguments)
        for functor in functors:
            N = int(functor['type'][1])
            M = int(functor['type'][5])
            self.addFunctor(functor['name'], AsFunction(functor, N, M))

    def addFunctor(self, name, functor):
        if hasattr(functor, 'getSerializable'):
            d = functor.getSerializable()
            d['name'] = name
            self._functors.append(d)
            adaptedFunctor = functor
        else:
            raise FunctionsException('Only a Functions submodule can be added')
        super(_DecoratorFunction, self).addFunctor(name, adaptedFunctor)

    def getSerializable(self):
        return {'type': self.__class__.__name__,
                'arguments': self._constructionArgs,
                'execCode': self._execCode,
                'functors': self._functors}

    def __repr__(self):
        if self.__class__.__name__[2:5] == "ToR":
            return self.__class__.__name__[6:] + ', ' + ', '.join(map(str, self._constructionArgs))
        return self.__class__.__name__ + ', ' + ', '.join(map(str, self._constructionArgs))

    def __eq__(self, other):
        if type(other) == type(self) and other.getSerializable() == self.getSerializable():
            return True
        return False

    def _strSeparatedPart(self, name=""):
        ret = name
        if self._constructionArgs:
            lastPart = SEPARATOR.join(map(str, self._constructionArgs))
            if ret:
                ret = ret + SEPARATOR + lastPart
            else:
                ret = lastPart
        return ret

    def __str__(self):
        if self.__class__.__name__[2:5] == "ToR":
            name = self.__class__.__name__[6:]
            if name != 'Uniform':
                return self._strSeparatedPart(name)
            else:
                return self._strSeparatedPart()
        return self._strSeparatedPart(self.__class__.__name__)


for attr in [a for a in dir(_Functions) if a.startswith('R')]:
    globals()[attr] = type(attr, (_DecoratorFunction,
                                  getattr(_Functions, attr)), {})

for attr in [a for a in dir(_Functions) if a.startswith('_R')]:
    globals()[attr] = getattr(_Functions, attr)

try:
    from Opera import SlenderBodies
    for attr in [a for a in dir(SlenderBodies) if (a.endswith('Function') or
                                                   a.endswith('FunctionNoAngles'))]:
        mod = type(attr, (_DecoratorFunction,
                          getattr(SlenderBodies, attr)), {})
        sys.modules['Opera.SlenderBodies.'+attr] = mod
        setattr(sys.modules[SlenderBodies.__name__], attr, mod)
except ImportError:
    pass