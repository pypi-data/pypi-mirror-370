import os

#print("load " + '/'.join(__file__.split('/')[-2:]))

def Basedir(path:str) -> str:
    return os.path.dirname(path)

def Join(*path) -> str:
    return os.path.join(*path)

def Exists(path:str) -> bool:
    return os.path.exists(path)

def NotExists(path:str) -> bool:
    return not os.path.exists(path)

def SecureFilename(name:str) -> str:
    from werkzeug.utils import secure_filename
    return secure_filename(name)

def Uniquify(path:str) -> str:
    """
    If the file exists, add a number to the end of the file name until it doesn't exist
    
    :param path: The path to the file you want to uniquify
    :type path: str
    :return: The path of the file with a number appended to the end of the file name.
    """
    filename, extension = os.path.splitext(path)
    counter = 1

    while os.path.exists(path):
        path = filename + "." + str(counter) + extension
        counter += 1

    return path

def IsDir(path:str) -> bool:
    return os.path.isdir(path)

def Basename(path:str) -> str:
    return os.path.basename(path)

def Suffix(path:str) -> str:
    """
    Os.Path.Suffix("a.b") ==> ".b"
    Os.Path.Suffix("/c/d/a.b") ==> ".b"
    
    :param path: The path parameter is a string that represents the file path or file name for which we
    want to extract the file extension
    :type path: str
    :return: The function `Suffix` takes a string argument `path` and returns the file extension of the
    file specified in the path. It does this by using the `os.path.splitext()` function to split the
    path into the file name and extension, and then returning the extension. Therefore, the function
    returns a string that represents the file extension of the file specified in the path.
    """
    return os.path.splitext(path)[1]

class Path:
    Basedir
    Join
    Exists
    NotExists
    Uniquify
    IsDir
    Basename
    Suffix