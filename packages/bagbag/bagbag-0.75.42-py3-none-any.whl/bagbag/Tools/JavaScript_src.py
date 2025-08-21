import js2py

#print("load " + '/'.join(__file__.split('/')[-2:]))

class JavaScript():
    def __init__(self) -> None:
        pass

    def Eval(self, code:str):
        """
        Just like javascript eval. Translates javascript to python, executes and returns python object. js is javascript source code

        EXAMPLE:

        >>> Tools.JavaScript.Eval('console.log( "Hello World!" )')
        'Hello World!'
        >>> add = Tools.JavaScript.Eval('function add(a, b) {return a + b}')
        >>> add(1, 2) + 3
        6
        >>> add('1', 2, 3)
        u'12'
        >>> add.constructor
        function Function() { [python code] }
        
        NOTE: For Js Number, String, Boolean and other base types returns appropriate python BUILTIN type. For Js functions and objects, returns Python wrapper - basically behaves like normal python object. If you really want to convert object to python dict you can use to_dict method.
        
        :param code: The code to be evaluated
        :type code: str
        :return: The result of the code being evaluated.
        """
        return js2py.eval_js(code)
    
    def Eval6(self, code:str):
        """
        Just like Eval() but with experimental support for js6 via babel.
        
        :param code: The code to be executed
        :type code: str
        :return: The return value is the result of the last statement executed.
        """
        return js2py.eval_js6(code)