from os.path import (
    exists,
    join,
    dirname,
    basename,
    splitext,
    expanduser,
    relpath,
    isdir
)
from .compiler import Ref, Schedule
from os import environ, walk
import configparser, json, os, yaml
import logging
from functools import lru_cache
from pathlib import Path
from .gits.module import GitModule
from .utils import system


class Settings:
    # dev utils
    debug = False

    # if path provided leads to a repo upstream
    is_repo      : bool = False
    is_module    : bool = False
    is_ymvas     : bool = False # if repos if fetched from ymvas
    is_main      : bool = False # if repo is main git@ymvas.com/vas/vas.git

    # paths
    root         : str  = None # /root             -> folder of the repo
    git          : str  = None # /root/.git        -> folder , if module -> /root/../../.git
    hooks        : str  = None # /root/.git/hooks  -> folder , if module -> /root/../../.git/hooks
    ymvas        : str  = None # /root/.ymvas      -> folder

    # repo info
    url          : str  = None # example  -> git@ymvas.com/vas/ymvas.git
    name         : str  = None # from url -> ymvas
    user         : str  = None # from url -> vas
    alias        : str  = None # from url -> vas/ymvas

    # ymvas important folders
    d_references : str = None
    d_commands   : str = None
    d_settings   : str = None
    d_tasks      : str = None
    d_schedules  : str = None
    d_secrets    : str = None
    d_finance    : str = None
    d_hooks      : str = None
    d_endpoints  : str = None
    d_documents  : str = None
    d_contacts   : str = None
    d_spaces     : str = None

    # where are we going to complie the endpointss
    d_compile_prefix : str = None

    # submodules asociated
    modules: dict = {}

    # ymvas important files
    f_settings            : str = None
    f_settings_endpoints  : str = None
    f_settings_references : str = None
    f_settings_secrets    : str = None
    f_settings_tasks      : str = None
    f_settings_finance    : str = None
    f_settings_hooks      : str = None

    d_default_compiles    : str = None


    # private
    __git_modules = []
    __references  = {}

    def __init__( self , pwd ):
        root, is_repo = Settings._find_repo_root(pwd)
        self.__logger = logging.getLogger(__name__)

        self.root = root
        if is_repo:
            self._setup_repo_paths()

        self.is_repo = is_repo

        data = system.get_global_config()
        if "version" not in data:
            os.makedirs(
                dirname( system.global_config_dir() ),
                exist_ok = True
            )

            with open(system.global_config_file(),'w') as fs:
                from .__init__ import __version__

                data = {
                    "version" : __version__ ,
                }

                if self.is_main:
                    data['global-src']      = self.root
                    data['global-commands'] = self.d_commands

                fs.write(json.dumps(data, indent= 10))
        else:
            data = system.get_global_config()
            self.d_default_compiles = data.get('global-compile-dir',None)

    def log(self,*args,color=None,**kwargs):

        if self.debug:
            if color != None:
                painter = {
                    "red"    : lambda x: f"\033[31m{x}\033[0m",
                    "green"  : lambda x: f"\033[32m{x}\033[0m",
                    "yellow" : lambda x: f"\033[33m{x}\033[0m",
                    "blue"   : lambda x: f"\033[34m{x}\033[0m",
                }.get(color, lambda x: x)
                args = [painter(a) for a in args]

            print(*args)
            return

        self.__logger.info(*args,**kwargs)

    @property
    @lru_cache(maxsize=None)
    def ymvas_server_url(self):
        stg = system.get_global_config()
        return str(stg.get(
            'ymvas-server-url',
            'ssh://git@'+self.ymvas_domain+'/{repo}.git'
        ))

    @property
    @lru_cache(maxsize=None)
    def is_server(self):
        return system.get_global_config().get( 'is-ymvas', False )

    @property
    @lru_cache(maxsize=None)
    def ymvas_domain( self ):
        stg = system.get_global_config()
        return str(stg.get(
            'ymvas-domain' ,
            'ymvas.com'
        ))

    @staticmethod
    def _find_repo_root(pwd):
        _pwd_b = pwd

        ymf = join(pwd , '.ymvas' )
        ymp = join(pwd , '.ymvas' )
        git = join(pwd , '.git'   )

        _is_repo = True
        _search  = {}

        while not exists(ymf):
            _pwd_b = dirname(_pwd_b)

            _search[_pwd_b] = _search.get(_pwd_b,0) + 1
            ymf = join(_pwd_b,'.ymvas')

            if _search[_pwd_b] > 10 or exists(git):
                ymf = ymp
                _is_repo = False
                break

            git = join( _pwd_b , '.git'   )
            ymp = join( _pwd_b , '.ymvas' )

        return dirname(ymf), _is_repo

    def _setup_repo_paths( self ):
        _git      = join( self.root , '.git' )
        is_module = not isdir( _git )

        if not exists(_git):
            return

        if is_module:
            with open( _git ,'r' ) as f:
                _git = Path(f.read().split("gitdir:")[1].strip())
                _git = str( Path(self.root) / _git )

        self.git       = _git
        self.hooks     = join(_git,'hooks')
        self.is_module = is_module

        ######### config #########
        cnf = configparser.ConfigParser()
        cnf.read(join( _git , 'config' ))

        _url = None
        for section in cnf.sections():
            if 'origin' in section and 'remote':
                _url = cnf[section].get('url',None)
                break


        user, name, is_ymvas = self._parse_url(_url)

        self.is_ymvas = is_ymvas
        self.user     = user
        self.name     = name
        self.url      = _url

        self.is_main = user == name
        self.alias   = f'{name}'
        if user is not None:
            self.alias = f'{user}/{name}'

        # /repo/.ymvas folders
        self.ymvas = join(self.root, '.ymvas' )

        self.d_references = join( self.ymvas, 'references' )
        self.d_commands   = join( self.ymvas, 'commands'   )
        self.d_settings   = join( self.ymvas, 'settings'   )
        self.d_tasks      = join( self.ymvas, 'tasks'      )
        self.d_schedules  = join( self.ymvas, 'schedules'  )
        self.d_secrets    = join( self.ymvas, 'secrets'    )
        self.d_finance    = join( self.ymvas, 'finance'    )
        self.d_hooks      = join( self.ymvas, 'hooks'      )
        self.d_endpoints  = join( self.ymvas, 'endpoints'  )

        # /repo folders if account
        if self.is_main:
            self.d_endpoints = join(self.root, 'endpoints' )
            self.d_documents = join(self.root, 'documents' )
            self.d_contacts  = join(self.root, 'contacts'  )
            self.d_finance   = join(self.root, 'finance'   )
            self.d_spaces    = join(self.root, 'spaces'    )

        # ymvas endpoints paths
        self.d_compile_prefix = self.alias
        if self.is_main:
            self.d_compile_prefix = user

        self.modules   = self.get_modules()

        # sttings files
        self.f_settings            = join(self.d_settings, 'settings.yaml'   )
        self.f_settings_endpoints  = join(self.d_settings, 'endpoints.yaml'  )
        self.f_settings_references = join(self.d_settings, 'references.yaml' )
        self.f_settings_secrets    = join(self.d_settings, 'secrets.yaml'    )
        self.f_settings_tasks      = join(self.d_settings, 'tasks.yaml'      )
        self.f_settings_finance    = join(self.d_settings, 'finance.yaml'    )
        self.f_settings_hooks      = join(self.d_settings, 'hooks.yaml'      )
        self.f_settings_schedules  = join(self.d_settings, 'schedules.yaml'  )

    @lru_cache(maxsize=None)
    def relpath(self,path):
        return relpath(path,self.root)

    def refs(self, src = None):
        _dir = self.d_references

        if src is not None:
            _dir = join(self.d_references,src)

        for r,_,_files in walk(_dir):
            for f in files:
                yield Ref(join(ff), self)

    def get_ref(self,space:str,fragment:str) -> Ref:
        _exists = self.__references.get(space,{}).get(fragment,None)

        if _exists:
            return _exists

        # get refs only for active or in scope of user
        module = self.get_modules().get(space,{})
        m_path = join(module.path , '.ymvas', 'references' )

        if not module.path or not module.active:
            return

        if not exists(m_path):
            return

        for r,_,files in walk( m_path ):
            for f in files:
                ff = join(r,f)
                if not Ref.match(ff,fragment):
                    continue

                r = Ref( ff , self )
                # store for later use
                if space not in self.__references:
                    self.__references[space] = {fragment:r}
                else:
                    self.__references[space][fragment] = r
                return r

        pass

    
    def schedules(self):
        for r,_,files in walk( self.d_schedules ):
            for f in files:
                schedule = Schedule(join(r,f))
                if not schedule.active:
                    continue
                yield schedule

        if self.is_main:
            for r,_,files in walk( self.d_contacts ):
                for f in files:
                    schedule = Schedule(join(r,f))
                    schedule.transform_contact()

                    if not schedule.active:
                        continue

                    yield schedule

    @lru_cache(maxsize=None)
    def get_modules(self):
        file = join(self.root,'.gitmodules')

        if self.is_module:
            modules = join(".git","modules")
            fragment = modules + self.git.split(modules)[-1]
            main_path = self.git.replace(fragment,"")
            main_settings = Settings(main_path)
            return main_settings.get_modules()

        m = GitModule()
        m.root = True
        m.active = True
        m.path = self.root
        m.url  = self.url
        m.name = self.name
        m.user = self.user

        modules = { self.alias : m }

        if not exists(file):
            return modules

        cnf = configparser.ConfigParser()
        cnf.read( file )

        for s in cnf.sections():
            p = cnf[s].get('path'   , None )
            u = cnf[s].get('url'    , None )
            a = cnf[s].get('active' , 'True' ).lower().strip() == 'true'

            if not 'submodule' in s or p is None or u is None:
                continue

            user, name, is_ymvas = self._parse_url(u)
            if name is None:
                continue

            m = GitModule()
            m.root = False
            m.active = a
            m.path = join( self.root , p )
            m.url = u
            m.name = name
            m.user = user

            modules[f"{user}/{name}"] = m

        return modules

    @lru_cache(maxsize=None)
    def get_commands(self, is_global = False, filter = None):
        dr = self.d_commands
        if is_global or not self.is_repo:
            dr = system.get_global_config().get( 'global-commands',None )

        if dr is None: return

        # widnows git bash fixes
        dr = Path(dr)
        if str(dr).startswith("/c/") or str(dr).startswith("\\c\\"):
            dr = Path("C:" + str(dr)[2:])

        if not dr.exists():
            return

        valid = [
            {"ext" : 'py'   , "run" : "python3" },
            {"ext" : 'bash' , "run" : "bash"    },
            {"ext" : 'sh'   , "run" : "sh"      }
        ]

        vdict = {x['ext']:x['run'] for x in valid}

        if filter is None:
            for r,_,files in os.walk(dr):
                if len(files) == 0:
                    continue
                for f in files:
                    ab = join(r,f)
                    fl = str(Path( ab ).relative_to( dr ))
                    st = splitext(fl)
                    rn = vdict.get(st[1].strip('.'),None)

                    if rn is None:
                        continue

                    yield {
                        "cmd"  : st[0],
                        "run"  : rn,
                        "path" : ab
                    }
            return

        for t in valid:
            file = join(dr,f"{filter}." + t['ext'])
            if exists(file):
                yield {
                    "cmd"  : filter,
                    "run"  : t['run'],
                    "path" : file
                }
                break

 
    @lru_cache(maxsize=None)
    def get_ymvas_settings(self):
        return self.__json_file(self.f_settings)

    @lru_cache(maxsize=None)
    def get_ymvas_hooks_settings(self):
        return self.__yaml_file(self.f_settings_hooks)

    @lru_cache(maxsize=None)
    def get_ymvas_schedules_settings(self):
        return self.__yaml_file(self.f_settings_schedules)

    def __json_file(self,file, types = dict):
        if not exists(file):
            return {}
        try:
            with open(file,'r') as f:
                data = json.loads(f.read())
                if not isinstance(data,types):
                    return {}
                return data
        except Exception:
            return {}
        return {}

    def __yaml_file(self,file, types = dict):
        if not exists(file):
            return {}
        try:
            with open(file,'r') as f:
                data = yaml.safe_load(f.read())
                if not isinstance(data,types):
                    return {}
                return data
        except Exception as e:
            return {}
        return {}

    def set_global_settings(self,stg):
        with open(system.global_config_file(),'w') as fs:
            fs.write(json.dumps(stg))

    def _parse_url(self, url ):
        if url is None:
            return None, None, None

        is_ymvas = f"@{self.ymvas_domain}" in url
        name = basename(url).replace('.git','')

        # get repo user
        user1 = url.split('@')[-1]
        user  = user1.replace(basename(url),'')
        user  = basename(user.strip('/'))
        user  = user.split(':')[-1]
        user  = user.strip('/')
        user  = user if '/' not in user else None

        if user is not None:
            user  = None if user1.startswith( user ) else user

        return user, name, is_ymvas
