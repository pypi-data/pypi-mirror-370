from functools   import lru_cache
from os.path import join, relpath, isdir, basename, dirname
from os import remove, makedirs, sep

import shutil
from .modifiers  import make
from .references import Ref


class Change:
    
    DELETED = 'D'
    UPDATED = 'U'

    def __init__(self,settings, file,action):
        self.origin = file
        self.action = action
        self.settings = settings
        
        # populated on sync old
        self._prev_compiled = None
        self._destination = None

        self.format = None
        self.into = None
    
    @property
    @lru_cache(maxsize=None)
    def fullpath(self):
        return join(self.settings.root, self.origin)

    @property
    @lru_cache(maxsize=None)
    def is_endpoint(self):
        endpoints_path = self.settings.relpath( self.settings.d_endpoints )
        return self.origin.startswith( endpoints_path )
    
    @property
    @lru_cache(maxsize=None)
    def is_setting(self):
        settings_path = self.settings.relpath( self.settings.d_settings )
        return self.origin.startswith( settings_path )
    
    @property
    @lru_cache(maxsize=None)
    def is_endpoints_setting(self):
        file = self.settings.relpath(self.settings.f_settings_endpoints)
        return self.origin == file
    
    
    @property
    @lru_cache(maxsize=None)
    def cnf_name(self):
        if self.is_setting:
            return relpath(self.fullpath,self.settings.d_settings)
        return relpath(self.fullpath, self.settings.d_endpoints )
 
    @property
    @lru_cache(maxsize=None)
    def cnf_end(self):
        name = self.cnf_name
        if not self.into:
            return name
        
        base = basename(name)
        frgm = name.strip(base)
        fnam = [base] if not '.' in base else base.split('.')[:-1]
        fnam = ".".join(fnam)
        fnam+= "." + self.into

        return frgm + fnam

    @property
    def end_basename(self):
        return basename(self.cnf_end)
    
    @property
    def cnf_dir(self):
        dd = dirname(self.cnf_name)
        if dd is None:
            return self._destination
        return join(self._destination,dd)

    @property
    def is_dir(self):
        return isdir(self.fullpath)
    
    def sync(self,destination, conf):
        self._destination = destination

        if not self.is_endpoint:
            return
        
        files    = conf.get('files',{})
        current  = files.get(self.cnf_name,{})
        compiled = current.get('compiled',None)

        if compiled is not None:
            self._prev_compiled = join(destination,compiled)
        
        cnf_e = current.get('conf',{})
        self.format = cnf_e.get('format',None)
        self.into   = cnf_e.get('into',None)

    def rm(self):
        if self._prev_compiled:
            remove(self._prev_compiled)
            self.settings.log(f"Deleted {self._prev_compiled}")
        
    def is_outdated(self):
        return self.action == Change.DELETED
    
                
    def create(self):
        e = Ref( self.fullpath , self.settings )
        makedirs( self.cnf_dir , exist_ok = True )
        
        destination = join(self.cnf_dir, self.end_basename )
        
        if e.just_copy:
           shutil.copy2( self.fullpath , destination )
           self.settings.log(f"file {self.origin} was copied")
           return
            
        with open(destination, 'wb') as f:
            cnf = {}
            if self.format and self.into:
                cnf['format'] = self.format
                cnf['into']   = self.into
            
            success = make(
               self.format,
               self.into,
               f,
               e.content,
            )

            if not success:
                f.write(e.content.encode('utf-8'))

    
    def config(self):
        cnf = {}
        if self.format and self.into:
            cnf['format'] = self.format
            cnf['into'] = self.into


        return (
            self.cnf_name,
            {
                "origin" : self.origin,
                "compiled" : self.cnf_end,
                "conf" : cnf
            }
        )
