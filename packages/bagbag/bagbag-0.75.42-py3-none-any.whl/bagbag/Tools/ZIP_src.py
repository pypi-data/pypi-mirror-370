import zipfile
import os
from collections import defaultdict
import typing

class ZIP():
    def __init__(self, zip_file_or_dir:str) -> None:
        self.path = zip_file_or_dir

        self.zipfr:zipfile.ZipFile = None

    def open_for_read(self):
        if self.zipfr == None:
            self.zipfr = zipfile.ZipFile(self.path, 'r')
    
    def Pack(self, out_zip_fpath:str):
        """
        将指定目录中的所有文件和子目录打包为一个zip文件

        :param input_dir: 要打包的目录路径
        :param output_zip_file: 输出的zip文件路径
        """
        with zipfile.ZipFile(out_zip_fpath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            self.zipfr = None 
            for root, dirs, files in os.walk(self.path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Arcname should be relative to the input_dir
                    arcname = os.path.relpath(file_path, start=self.path)
                    zipf.write(file_path, arcname)

    def Unpack(self, extract_to_dir:str):
        """
        The function `Unpack` extracts all files from a zip archive to a specified directory after
        ensuring the directory exists.
        
        :param extract_to_dir: The `extract_to_dir` parameter is a string that represents the directory
        path where you want to extract the contents of the zip file. This function will check if the
        directory exists, create it if it doesn't, and then extract all files from the zip file to that
        directory
        :type extract_to_dir: str
        """
        # 确保解压目录存在
        if not os.path.exists(extract_to_dir):
            os.makedirs(extract_to_dir)
        
        self.open_for_read()
        
        self.zipfr.extractall(extract_to_dir)

    def Read(self, fpath:str) -> str:
        """
        The function `Read` reads and returns the contents of a file within a zip archive specified by
        `fpath`.
        
        :param fpath: The `fpath` parameter in the `Read` method is a string that represents the file
        path within the zip archive from which you want to read the contents
        :type fpath: str
        :return: The `Read` method is returning the content of a file located at the specified `fpath`
        within a zip archive. The content is read as bytes and then decoded into a UTF-8 encoded string
        before being returned.
        """
        self.open_for_read()

        with self.zipfr.open(fpath) as file:
            return file.read().decode('utf-8')
    
    def ReadBytes(self, fpath:str) -> bytes:
        """
        The function `ReadBytes` reads and returns the contents of a file within a zip archive as bytes.
        
        :param fpath: The `fpath` parameter in the `ReadBytes` method is a string that represents the
        file path of the file you want to read from the zip archive. When calling the `ReadBytes`
        method, you should provide the specific file path within the zip archive that you want to read
        as a
        :type fpath: str
        :return: The `ReadBytes` method reads and returns the contents of a file located at the
        specified `fpath` within a zip archive. It returns the contents of the file as a bytes object.
        """
        self.open_for_read()

        with self.zipfr.open(fpath) as file:
            return file.read()
    
    def zip_os_walk(self):
        def split_path(path):
            """Split a path into its segments."""
            parts = []
            while path:
                path, tail = os.path.split(path)
                if tail:
                    parts.insert(0, tail)
                else:
                    if path:
                        parts.insert(0, path)
                    break
            return parts

        self.open_for_read()
        directories = defaultdict(lambda: {'dirs': [], 'files': []})

        # Collect directory and file information
        for zip_info in self.zipfr.infolist():
            parts = split_path(zip_info.filename)
            parent_dir = os.path.join(*parts[:-1]) if parts[:-1] else ''
            if zip_info.is_dir():
                directories[parent_dir]['dirs'].append(parts[-1])
            else:
                directories[parent_dir]['files'].append(parts[-1])

        # Yield directory content similar to os.walk
        for dirpath in directories:
            yield dirpath, directories[dirpath]['dirs'], directories[dirpath]['files']

    def Walk(self, type:str=None) -> typing.Iterable[typing.Tuple[str, str, str]]:
        for root, dirs, files in self.zip_os_walk():
            if type == None:
                for name in files:
                    yield os.path.join(root, name)
                for name in dirs:
                    yield os.path.join(root, name)
            elif type == "f":
                for name in files:
                    yield os.path.join(root, name)
            elif type == "d":
                for name in dirs:
                    yield os.path.join(root, name)
    
    def Close(self):
        if self.zipfr != None:
            self.zipfr.close()