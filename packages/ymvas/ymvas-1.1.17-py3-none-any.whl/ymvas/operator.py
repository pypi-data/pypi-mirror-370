import os

from os.path     import join, exists
from .compiler   import Ref, Compiler
from .settings   import Settings
from .templates  import Creator
from .gits       import Gits
from .utils      import system 

class Operator:
    _refs  :dict = {}
    _spaces:dict = {}

    def __init__(self, pwd , debug = False):
        self.settings       = Settings( pwd )
        self.settings.debug = True
        # self.git            = Gits(self.settings)

    def command(self,args):
        cmd = list(self.settings.get_commands(
            args.is_global,
            args.exec
        ))

        if len(cmd) == 0:
            print(f'Command [{args.exec}] is not setup for this repository!')
            print(self)
            return

        cmd = cmd[0]
        os.system(cmd['run'] + " " + cmd['path'])


    def clone(self,args):
        if args.repo is None:
            print('No repo specified!')
            return

        url = self.settings.ymvas_server_url.format(
            repo = args.repo
        )

        os.system(f"git clone {url}")

    def pull(self,argv):
        modules = self.settings.get_modules()
        modules = {k:v for k,v in modules.items() if not v.root and v.active}

        os.system(
            f"git --git-dir={self.settings.git} "
            f"--work-tree={self.settings.root} fetch"
        )

        # for k,v in modules.items():
        #     p = v[ 'path' ]
        #     u = v[ 'url'  ]
        #
        #     if not exists(p):
        #         os.system(
        #             f"cd {self.settings.root} && "
        #             f"git --git-dir={self.settings.git} "
        #             f"--work-tree={self.settings.root} "
        #             f"submodule add {u} {p}"
        #         )


    def push(self):
        if not self.settings.is_server:
            print('is not server', self.settings.hooks )


    def setup(self,argv):
        creator = Creator(argv)
        creator.run()

    def config(self,argv):
        if argv.is_global:
            stg = system.get_global_config()
            if argv.action == 'set':
                stg = stg | argv.get_config_args()
                self.settings.set_global_settings(stg)
            elif argv.action == "show":
                print(stg)
            elif argv.action == "get":
                for a in argv.get_config_flags():
                    v = stg.get(a,None)
                    print(v)
            return

    def secret(self,argv):
        pass

    def trigger(self,argv):
        hooks = self.settings.get_ymvas_hooks_settings()
        hook  = hooks.get( argv.action , None )
        if hook is None:
            return
        exec = hook.get("exec",None)
        file = hook.get('src',None)
        if not exec or not file:
            return
        file = join(self.settings.root,file)
        if not exist(file):
            return
        os.system(f'{exec} {file}')


    def compile(self,args):
        Compiler( 
            self.settings ,
            join( args.compile_dir, self.settings.d_compile_prefix )
        ).run()


    def __repr__( self ):
        data = [
            f"[{self.settings.alias}]",
            f" - is-repo  : {self.settings.is_repo}",
            f" - is-ymvas : {self.settings.is_ymvas}",
            f" - is-main  : {self.settings.is_main}",
            "",
            f"[global configuration]",
            f" - {system.global_config_file()}"
        ]

        cmds = [c['cmd'] for c in self.settings.get_commands()]
        if len(cmds) != 0:
            data += [
                "", f"[avaliable commands]",
                " - " +  "\n - ".join(cmds),
            ]

        return "\n".join(data) + "\n"










    #
