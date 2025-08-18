
import os ,shutil
from os.path import dirname, join, exists

_dir = dirname(__file__)

class Creator:

    def __init__(self, argv):
        self.src    = join(_dir,argv.init)
        self.target = argv.src

        if not exists(self.src):
            print(f'Invalid init [{argv.init}]')
            return
    
    def commit(self):
        pass

    def run(self):
        for r,_,files in os.walk(self.src):

            for f in files:
                src = join(r,f)
                dst = src.replace(self.src,self.target)

                if exists(dst):
                    continue

                dic = dirname(dst)
                os.makedirs(dic,exist_ok=True)

                shutil.copyfile(src, dst)
