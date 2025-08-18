import sys, os
from os.path import join, exists, dirname
from .operator import Operator
from ymvas.models.arguments import Arguments


_defined_config   = ['set','get','show']
_defined_inits    = ['account','default']

red    = lambda x: f"\033[31m{x}\033[0m"
green  = lambda x: f"\033[32m{x}\033[0m"
yellow = lambda x: f"\033[33m{x}\033[0m"
blue   = lambda x: f"\033[34m{x}\033[0m"


def _default_info():
    print(f"{green('YMVAS')} - handle your life like a developer!")
    print(f"Usage : "                                 )

    print(f"    {green('ym')} {{command}}   |  {yellow(', '.join(Arguments.commands))} ")
    print(f"    {green('ym')} --version   |  {green('Is allowed!')}              ")
    print( ""                                         )

    print( "File based commands:"                     )
    print( "    {repo}/.ymvas/commands/install.bash"  )
    print( "    {repo}/.ymvas/commands/install.py "   )
    print( "    {repo}/.ymvas/commands/install.sh "   )
    print( ""                                         )

    print(f"Can be easly executed like this: "        )
    print(f"    {green('ym')} install        "        )
    print( ""                                         )
    print(f"Flags:                           "        )
    print(f"    [ {yellow('--debug')}  ] or [{yellow('-d')}]" )
    print(f"    [ {yellow('--global')} ] or [{yellow('-g')}]" )

def _compile_info():
    print(f"Usage : ")
    print(f"    {green('ym')} compile -c=\"~/destination/folder\"")
    print(f"    {green('ym')} compile --compile-dir=\"~/destination/folder\"")
    print(f"")
    print(yellow(f"You can also setup default compile directory with: "))
    print(yellow(f"    ym config set --global-compile-dir=\"~/your/path\""))

def _compile_no_repo():
    print(red(f"[{os.getcwd()}]: is not a valid repository!"))
    print("")

def _config_info():
    print(f"Usage : ")
    print(f"    {green('ym')} config     | {yellow(', '.join(_defined_config))} ")
    print(f"    {green('ym')} config -g  | For global configuration ")
    print(f"")
    print(f"Example : ")
    print(f"    {green('ym')} config set -g  | For global configuration ")

def _init_info():
    print(f"Usage : ")
    print(f"    {green('ym')} init     | {yellow(', '.join(_defined_inits))} ")
    print(f"")
    print(f"Example : ")
    print(f"    {green('ym')} init account ")



def run():
    args = sys.argv[1:]

    # no arguments passed
    if len(args) == 0:
        _default_info()
        sys.exit(1)

    argv = Arguments(args[0], *args[1:], src = os.getcwd())

    if argv.is_version: # print version
        from .__init__ import __version__
        print( __version__ )
        sys.exit(0)

    # extract src
    cli = Operator( argv.src , debug = argv.debug )

    if argv.command == 'info':
        print( cli )
        return

    if argv.command == "clone":
        cli.clone( argv )
        return

    if argv.command == "init":
        if argv.init is None:
            _init_info()
            return
        cli.setup( argv )
        return

    if argv.command == 'config':
        if argv.action not in _defined_config:
            _config_info()
            return
        cli.config(argv)
        return

    if argv.exec is not None:
        cli.command(argv)
        return


    # found repo
    if not cli.settings.is_repo:
        _compile_no_repo()
        print(cli)
        return

    if argv.command == 'compile':
        if cli.settings.d_default_compiles is None and argv.compile_dir is None:
            _compile_info()
            return

        cli.compile( argv )
        return

    if argv.command == 'trigger':
        cli.trigger(argv)
        return

    if argv.command == 'secret':
        cli.secret(argv)

    if argv.command == 'pull':
        cli.pull(argv)
        return


if __name__ == '__main__':
    run()
