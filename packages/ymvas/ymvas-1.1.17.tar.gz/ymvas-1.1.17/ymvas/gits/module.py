from functools import lru_cache


class GitModule:
    root   : bool = False
    active : bool = False
    path   : str  = None
    url    : str  = None
    name   : str  = None
    user   : str  = None

    @property
    def alias(self):
        return f"{self.user}/{self.name}"
    
    @property
    @lru_cache(maxsize=True)
    def settings(self):
        from .. import Settings 
        return Settings(self.path)

