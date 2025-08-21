import magic 
import os 

#print("load " + __file__.split('/')[-1])

def FileType(file:str) -> str:
    """
    It takes a file path or file content and returns the file type
    
    :param file: The file to check
    :type file: str
    :return: The content type of the file. Ex: PDF document, version 1.2
    """
    if os.path.exists(file) and os.path.isfile(file):
        contenttype = magic.from_file(file)
    else:
        contenttype = magic.from_buffer(file)

    return contenttype



if __name__ == "__main__":
    print(FileType("FileType.py"))