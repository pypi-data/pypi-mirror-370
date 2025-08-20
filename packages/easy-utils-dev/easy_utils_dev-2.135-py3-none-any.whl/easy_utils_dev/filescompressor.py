import pyzipper , os
from easy_utils_dev import utils


DEFAULT_PASSWORD = 'EASY_UTILS_DEV_COM_FILE_CLASS@123'

class FileCompressor :
    def __init__(self , output_dir , filename , password=None, default_file_format='zip') :
        self.password = None
        self.output_dir = output_dir
        self.filename = filename
        self.files= []
        self.default_file_format = default_file_format
        self.absolute_path = os.path.join( output_dir , f'{filename}.{default_file_format}')
        self.zip = pyzipper.AESZipFile(
            self.absolute_path, 
            'w', 
            compression=pyzipper.ZIP_LZMA, 
            encryption=pyzipper.WZ_AES
        )
        if not password :
            self.password = DEFAULT_PASSWORD
        else :
            self.password = password
        self.zip.setpassword(self.password.encode())

    def change_password(self, password) :
        self.password = password
        self.zip.setpassword(password.encode())

    def get_password(self) :
        return self.password

    def add_directory(self, directory: str):
        # Recursively add files from the directory to the zip file
        for root, dirs, files in os.walk(directory):
            for file in files:
                # Add each file in the directory (relative to the directory structure)
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=directory)  # Relative path to preserve structure
                self.zip.write(file_path, arcname)
        return self.files
        
    def generate_password( self ) :
        return utils.getRandomKeysAndStr()

    def add_file(self, file: str):
        if os.path.isdir(file):
            # If it's a directory, recursively add its contents
            self.add_directory(file)
        else:
            # If it's a file, add the file
            self.files.append(file)
            self.zip.write(file, os.path.basename(file))  # Write file with base name (no path)
        return self.files
    
    def add_files( self , files : list) :
        for file in files :
            self.add_file(file)
        return self.files

    def close(self) :
        self.zip.close()    

    def get_output_path(self) :
        return self.absolute_path

    def extract_files(self , input_dir , output_dir) :
        with pyzipper.AESZipFile(input_dir, 'r') as zf:
            zf.setpassword(self.password.encode())
            zf.extractall(output_dir)
        return output_dir
# Example usage

if __name__ == "__main__" :
    # cfile = FileCompressor(
    #     './',
    #     'test',
    # )
    # cfile.add_file('setup.py')
    # cfile.add_file('license.dat')
    # cfile.close()
    # cfile.extract_files(cfile.get_output_path() , './ahmed/')
    pass