from functools import lru_cache
from ..utils import system


class Arguments:
    is_version  : bool = False
    is_global   : bool = False
    debug       : bool = False

    command     : str  = None
    # if command is not set in commands it means it's an executable
    exec        : str  = None

    action      : str  = None
    repo        : str
    init        : str

    src         : str
    compile_dir : str

    commands = [
        "info"    ,
        "clone"   ,
        "config"  ,
        "pull"    ,

        "trigger" , # triggers a hook
        "secret"  , # get secret 
        "compile" , # compile references and endpoints
        "init"    , # create the template for ymvas
    ]

    _config_args = [
        "global-compile-dir" , # where the compiles will be stored
        "global-commands"    , # where the global commands are stored
        "global-src"         , # where the user repo is stored

        # server settings
        'is-ymvas'           , # if it's server side or not [true or false]
        'ymvas-server-url'   , # url typically https://ymvas.com
        'ymvas-compile-url'  , # url typically https://docs.ymvas.com
        'ymvas-domain'       , # domain typically ymvas.com
        'ymvas-access'       , # access privileges
    ]


    def __init__( self , command:str,  *args , src = None ):
        _, self.is_version  = Arguments.flag(
            [command]+list(args),'-v','--version', False
        )

        setattr(
            self,
            'command' if command in self.commands else 'exec',
            command
        ) # first statement

        # flags [non required]
        args, self.debug       = Arguments.flag(args,'-d','--debug'  , False )
        args, self.is_global   = Arguments.flag(args,'-g','--global' , False )
        args, self.src         = Arguments.keyv(args,'-s','--src'    , src   )
        args, self.compile_dir = Arguments.keyv(args,'-c','--compile-dir'    )

        if self.src is None and self.is_global:
            cnf = system.get_global_config()
            self.src = cnf.get('global-src',None)

        self.args = args
        self._get_2nd_arg()

    def is_valid(self):
        pass

    def _get_2nd_arg(self):
        getters = {
            "clone"   : lambda a: a[0] if '/' in a[0] else f"{a[0]}/{a[0]}",
        }

        _2nd = getters.get( self.command, lambda a: a[0] )
        _2nd = None if len( self.args ) == 0 else _2nd(self.args)

        setters = {
            "clone"   : "repo",
            "init"    : "init",
            "config"  : "action",
            "trigger" : "action",
        }

        if self.command in setters and _2nd is not None:
            setattr( self, setters[self.command] , _2nd )
            self.args = self.args[1:]

    @staticmethod
    def flag(args,short_key,key,default=False):
        trash, value, found = [], default, False
        for i, c in enumerate( args ):
            if ( c == key or c == short_key ) and not found:
                value, found = True, True
            else:
                trash.append(c)
        return trash, value

    @staticmethod
    def keyv(args,short_key,key,default=None):
        trash, value, found = [], default, False
        for i, c in enumerate(args):
            if (c.startswith(key) or c.startswith(short_key)) and not found:
                found = True
                value = c.split('=')[0]
                value = c.replace(value + '=',"")
                if len(value) > 2 and value[0] == value[-1] and value[0] in ["'",'"']:
                    value = value.strip(value[0])
            else:
                trash.append(c)
        return trash, value

    @lru_cache(maxsize=None)
    def get_config_args(self):
        cnfs = {}
        for arg in self._config_args:
            self.args, value = Arguments.keyv(self.args,f'--{arg}',f'--{arg}')
            if value is None or value == '':
                continue
            cnfs[arg] = value
        return cnfs

    @lru_cache(maxsize=None)
    def get_config_flags(self):
        cnfs = []
        for arg in self._config_args:
            self.args, value = Arguments.flag(self.args,f'--{arg}',f'--{arg}')
            if value != True:
                continue
            cnfs.append(arg)
        return cnfs
