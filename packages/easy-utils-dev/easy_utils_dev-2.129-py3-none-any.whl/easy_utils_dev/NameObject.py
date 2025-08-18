from argparse import Namespace 

class NameObject : 
    def __init__(self , *args, **kwargs) -> None:
          for key, value in kwargs.items():
                self.update(key, value)

    def update(self, key , value ) :
            setattr(self, key, value)