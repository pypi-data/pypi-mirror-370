from os.path import join, exists, dirname, basename, isdir, relpath
from pathlib import Path
import os, json, shutil, yaml, subprocess
from os import walk, sep, remove

from functools import lru_cache
from ..settings import Settings
from .change import Change
from ics import Calendar

class Compiler:

    def __init__( self, settings:Settings , destination:str ):
        self.settings    = settings
        self.destination = destination
        
        self.modules = [
                m.alias for m in settings.get_modules().values() if not m.root
        ]

        self.config = {}
        
        self.file = join(destination,'config.json')
        if exists(self.file):
            with open(self.file) as f:
                self.config = json.loads(f.read())
        
        self.modules_changed = False

    @property
    @lru_cache(maxsize=None)
    def _git(self):
        return (
            f"git --git-dir='{self.settings.git}' "
            f" --work-tree='{self.settings.root}' "
        )
    
    @property
    @lru_cache(maxsize=None)
    def commit(self):
        return os.popen(
            f"{self._git} rev-parse HEAD"
        ).read().strip()
    
    @property
    @lru_cache(maxsize=None)
    def first_commit(self):
        return os.popen(
            f"{self._git} rev-list --max-parents=0 HEAD"  
        ).read().strip()
    
    @property
    @lru_cache(maxsize=None)
    def is_uncommited(self):
        return os.popen(f"{self._git} status -s").read().strip() != ""
    

    def __compiled_commit(self):
        comm = self.config.get('commit',self.first_commit)
        from ..__init__ import __version__

        if self.config.get('version','0') != __version__ \
           or self.is_uncommited:
            return self.first_commit
        
        return comm
        
    @property
    @lru_cache(maxsize=None)
    def compiled_commit(self):
        cm = self.__compiled_commit()
        return cm if self.is_forced else cm
        
    @property
    @lru_cache(maxsize=None)
    def is_forced(self):
        compiled_commit = self.__compiled_commit()
        if compiled_commit == self.first_commit:
            return True
        try:
            subprocess.run([
                "git", 
                f"--git-dir='{self.settings.git}'",
                'merge-base', 
                '--is-ancestor', 
                compiled_commit, 
                self.commit
               ],
               check=True,
               capture_output = True,
               text=True 
            )
            return False
        except subprocess.CalledProcessError as e:
            return True
    


    def __changes(self, track = [], include_directories = False):
        if len(track) == 0:
            return []

        tracked = " ".join(track) # create the traking files
        
        # command changes commited
        cmd = (
           f"{self._git} --no-pager diff --name-status "
           f"{self.compiled_commit} {self.commit} -- {tracked}"
        )
        com = os.popen( cmd ).read().strip()
        
        cmd = f"{self._git} --no-pager status -s {tracked}"
        mod = os.popen( cmd ).read().strip()
        
        # get all changes in one list
        data    = mod.split("\n") + com.split("\n")
        changes = []

        for f in data:
            f = f.strip().replace("\t"," ")
            file  = " ".join(f.split(' ')[1:])

            if '"' in f or "'" in f:
                continue # skip strange files
            
            # handle rename 
            if f.upper().startswith("R"):
                fxf  = file.split('->')
                file = fxf[-1].strip()

                changes.append(Change(
                    self.settings, fxf[-1].strip(), Change.DELETED 
                ))
                changes.append(Change(
                    self.settings, fxf[0].strip() , Change.UPDATED
                ))

                continue

            if f.upper().startswith("D"):
                changes.append(Change( 
                    self.settings, file , Change.DELETED 
                ))
                continue

            changes.append(Change( self.settings, file , Change.UPDATED ))
        
        
        nchanges = []
        for c in changes:
            if c.is_dir and not include_directories: 
                continue
            c.sync(self.destination,self.config)
            nchanges.append(c)

        return nchanges
    
            
    def get_end_conf(self):
        if not exists(self.settings.f_settings_endpoints):
            return {}
        with open(self.settings.f_settings_endpoints,'r') as f:
            data = yaml.safe_load(f.read())
            if isinstance(data,dict):
                return data
        return {}


  
    def get_settings_changes(self,conf_e,conf_o):
        files = conf_o.get("files",{})
        endpoints_p = self.settings.relpath(
            self.settings.d_endpoints
        )
        
        changes = []
        for e, cnf_e in conf_e.items():
            old = files.get(e,{})

            if json.dumps(cnf_e) == json.dumps(old):
                continue

            file = join( endpoints_p, e )
            changes.append(Change(self.settings, file ,Change.UPDATED))
         
        return changes


    def clean(self):
        self.config = {}

        if not exists(self.destination):
            return True

        if not self.settings.is_main:
            self.settings.log(f"deleted all previous data")
            shutil.rmtree(self.destination)
            return True

        def _loop():
            for r,_,files in walk( self.destination ):
                for f in files:
                    yield join(r,f)

        for f in _loop():
            rf = relpath(f, self.destination )
            dd = rf.split( sep )
            if dd[0] in self.modules:
                continue
            self.settings.log(f"removed {rf}")
            remove(f)


        return True
    

    def run( self ):
        from ..__init__ import __version__

        if self.config.get('version','0') != __version__:
            self.settings.log('mismatch of version... removing all files')
            self.clean()
        
        elif self.is_uncommited:
            self.settings.log(f"Looks like working on local... removing all files")
            self.clean()

        elif self.is_forced:
            self.settings.log("Looks like forced push... removing all files")
            self.clean()

        self.settings.log(
            f"Different commit? {self.commit != self.compiled_commit}"
            f" | {self.commit} == {self.compiled_commit}"
        )

        if self.commit == self.compiled_commit:
            self.settings.log(f"No changes detected!")
            return
        
        
        config = {
            "commit"  : self.commit,
            "version" : __version__ 
        }
        
        os.makedirs( self.destination , exist_ok = True )

        # store modules folders so we don't overwrite them
        if self.settings.is_main:
            config['modules'] = self.modules
            for k,m in self.settings.get_modules().items():
                if len(self.__changes([m.path], include_directories=True)) != 0:
                    self.modules_changed = True
        
        # end preparation 
        self.__compile_settings(  config )
        self.__compile_schedules( config )
        self.__compile_endpoints( config )
        # self.__compile_tasks( config ) 

        
        with open(join(self.file),'w') as f:
            f.write(json.dumps(config, indent = 4))

        # print complie data
        self.settings.log(f"Final config : {json.dumps(config,indent = 1)}")
        return config

    

    def __compile_settings(self, config ):
        if not self.settings.is_main:
            return

        avatars = self.__changes([
            join(self.settings.d_settings,'avatar.jpeg'),
            join(self.settings.d_settings,'avatar.png'),
            join(self.settings.d_settings,'avatar.jpg'),
        ])
        

        ovatar = self.config.get('avatar',None)

        if len(avatars) != 0:
            avatar = avatars[0]
            avatar.sync( self.destination , self.config )
        
            ovapat = join(self.destination,str(ovatar))
            if ovatar != None and exists(ovapath):
                remove(ovapat)

            avatar.create()
            ovatar = avatar.cnf_name

        config['avatar'] = ovatar


    def __compile_schedules( self , config ):
        stg = self.settings
        rcf = stg.get_ymvas_schedules_settings()
        
        cal_path = join( self.destination , 'calendar.ics' )
        
        schedules = []
        include = rcf.get('include')
        contacts = rcf.get('contacts','none')
        
        if include is not None and self.modules_changed and stg.is_main:
            modules = []
            if isinstance(include,list):
                modules = include
            elif isinstance(include,dict):
                modules = include.get("modules",[])
                if not isinstance(modules,list):
                    modules = []

                modules = [m for m in modules if isinstance(m,str)]                
            elif isinstance(include,str):
                if include == '*' or include == 'all':
                    modules = self.modules
            
            gmodules = stg.get_modules()
            for m in modules:
                if m not in self.modules: 
                    continue
                
                md = gmodules[m]
                if not md.active: 
                    continue
                                    
                schedules += list(md.settings.schedules())


        # schedules changes
        changes = self.__changes([ stg.d_schedules ])
        
        cal = self.config.get('calendar',None)
        if len(changes) == 0 and not self.modules_changed:
            self.settings.log(
                "no changes detected in "
                "modules or schedules directory"
            )

            if cal != None:
                config['calendar'] = cal
            return
        
        schedules += list(self.settings.schedules())
        if len(schedules) == 0:
            self.settings.log("no schedules detected")
            return

        calendar = Calendar()
        for s in schedules:
            
            if s.is_contact and contacts == 'all':
                self.settings.log(f"{s.name} contact was added as birhtday")
                s.validate()

            if not s.valid: 
                self.settings.log(f"schedule [{s.name}] is not valid!")
                continue

            self.settings.log(f"schedule [{s.name}] will be added!")
            calendar.events.add(s.event)

        with open(cal_path,'w') as f:
            config['calendar'] = 'calendar.ics'
            self.settings.log("calendar.ics generated")
            f.writelines(calendar)


    def __compile_endpoints( self , config ):        
        changes = self.__changes([
          self.settings.d_endpoints ,
          self.settings.f_settings_endpoints
        ])

        if len(changes) == 0:
            self.settings.log(f"No endpoints changes detected!")
            config['files'] = self.config.get('files',[])
            return
            
        # sync and rm outdated, and get endpoints settings
        nchanges = []
        end_conf = {}
        avatar = None
        
        for c in changes:
            self.settings.log(c.fullpath)

            if c.is_endpoints_setting:
                end_conf = self.get_end_conf()
            
            if c.is_outdated() and c.is_endpoint:
                c.rm()
                continue
            elif not c.is_endpoint:
                continue
            nchanges.append(c)
        
        # check if settings are modified if so recompile the files changed
        schanges = self.get_settings_changes(end_conf,self.config)
        for c in schanges:
            c.sync(
                self.destination,
                self.config
            )

            _cnf = end_conf.get(c.cnf_name,{})

            self.settings.log(
                f"settings changes = {c.cnf_name} => "
                f"{_cnf}"
            )

            c.format = _cnf.get("format" ,None)
            c.into   = _cnf.get("into"   ,None)

            _exists = False
            for i, gc in enumerate(nchanges):
                if c.cnf_name == gc.cnf_name:
                    _exists = True
                    nchanges[i] = c
                    break

            if _exists:
                continue

            nchanges.append(c)
        
        config['files'] = {}
        for c in nchanges:
            c.create()
            name, data = c.config()
            config['files'][name] = data
        
