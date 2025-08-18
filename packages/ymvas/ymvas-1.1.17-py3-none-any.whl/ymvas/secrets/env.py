from ymvas.compiler.references import Ref
from ymvas.settings import Settings
from os.path import exists, dirname, isdir, join, basename
import inspect, os, json, yaml, io
from dotenv.main import DotEnv


class Environ:

    def __init__(self, src = None, settings = None):
        self.src = src

        if src is None:
            caller   = inspect.stack()[1]
            self.src = dirname(caller.filename)

        self.settings = settings
        if settings is None:
            self.settings = self.__get_settings()
        
        self.__is_env = False
        self.file = self.__find__file()
        self.ref = None

        if not (self.file is None):
            self.ref = Ref(self.file,self.settings)

    def __get_settings(self):
        return Settings(self.src)

    def __find__file(self):

        if exists(self.src) and not isdir(self.src):
            dna = basename(self.src)
            self.__is_env = (dna == '.env')
            return self.src

        posible = [
            ['.env'     , True],
            [".env.json", False],
            [".env.yaml", False],
            [".env.yml" , False],
        ]

        for f,is_env in posible:
            ff = join(self.src,f)
            if not exists(ff) or isdir(ff):
                continue
            self.__is_env = is_env
            return ff

        for f,is_env in posible:
            ff = join(self.settings.root,f)
            if not exists(ff) or isdir(ff):
                continue
            self.__is_env = is_env
            return ff
            
    def __load_env(self):
        e = DotEnv(
            None,
            stream = io.StringIO(self.ref.content)
        )
        return e.dict()

    def __parse(self):
        if self.ref is None:
            return {}

        cnt = self.ref.content

        if self.__is_env:
            return self.__load_env()
        elif self.ref.lang == 'json':
            return json.loads(cnt)
        elif self.ref.lang == 'yaml':
            return yaml.safe_load(cnt)
        elif self.ref.lang == 'yml':
            return yaml.safe_load(cnt)
        
        return {}

    def load(self):
        data = self._parse()
        if not isinstance(data,dict):
            return
        for k, v in data.items():
            os.environ[k] = str(v)

    def __get__(self,key):
        return os.environ.get(key)

    def get(self,key,default=None):
        return os.environ.get(key,default)
