import yaml, json
from functools import cache
from .raw_tags import raw_tags

class Tag:
    _close_tag       = ''
    _link            = None
    _replace         = None

    def __init__(
        self              ,
        name       = ''   ,

        raw        = ''   ,
        contents   = None ,

        tabs       = ''   ,
        start      = 0    ,
        start_ends = None ,

        close      = None ,
        close_ends = None ,

        attrs      = {},
        slots      = [],
    ):

        self.name       = name
        self.tabs       = tabs

        self.start      = start
        self.start_ends = start_ends

        self.close      = close
        self.close_ends = close_ends

        self.raw        = raw
        self.contents   = contents

        self.attrs      = attrs
        self.slots      = slots

    def is_ref(self):
        return self.name == 'ref'
    def is_attr_true(self,attr):
        return self.attrs.get(attr,False) == True

    def outer_pos(self):
        if self.close_ends is None:
            return [self.start,self.start_ends]
        return [self.start,self.close_ends]

    def match(self,**kwargs):
        for k,v in kwargs.items():
            if getattr(self,k) != v:
                return False
        return True

    def get(self,attr,defaults_to=None):
        return self.attrs.get(attr,defaults_to)
    def __getitem__(self, item):
        return self.attrs.get(item,None)

    def get_paths(self):
        if self._link is not None:
            return self._link

        path = self.get('link')

        if path is None:
            return None
        path = path.split('/')
        self._link = {
            'name' : path[0],
            'path' : path[1:]
        }

        return self._link

    def ref(self):
        if self._link is None:
            self.get_paths()
        return self._link.get('name',None)

    def set_replace(self,v,lang=None):
        self._replace = v

        if lang == None:
            return

        try:
            if lang == 'yaml':
                v = yaml.safe_load( v )
            elif lang == 'json':
                v = json.load( v )
        except Exception:
            self._replace = v
            return

        path = self.get_paths()['path']

        for p in path:
            if str(p).isdigit() and isinstance(v,list):
                p = int(p)
            try:
                v = v[p]
            except Exception as e:
                px = self.get('link')
                v = f"{{key '{px}' is missing}}"
                break

        if isinstance(v, int):
            self._replace = str(v)
            return
        elif isinstance(v,str):
            self._replace = v
            return
        elif v is None:
            self._replace = ''
            return

        if self.is_attr_true('outer'):
            v = { path[-1] : v }

        if self.get('expose') != None \
           and self.get('expect') == None \
           and self.get('expose') in ['yaml','json']:
           lang = self.get('expose')

        if lang == 'yaml':
            v = yaml.dump(v,allow_unicode=True)
        elif lang == 'json':
            v = json.dumps(v)

        self._replace = v

    def __repr__(self):
        posi = [ self.start,self.start_ends,self.close,self.close_ends ]
        poss = ",".join([ str(x) for x in posi if x != None ])
        return f"<{self.name} {str(self.attrs)} pos='{poss}' />"

    def _render_counter(self):
        series = self.get( 'series' )
        if series is None:
            return str(self._replace)
        if str(series).isnumeric() and str(self._replace).isnumeric():
            s = int(series)
            n = int(self._replace)
            return str(int(n % s))
        return str(self._replace)

    def from_to(self,text,expect,expose):
        data = {}
        try:
            if expect == 'yaml':
                data = yaml.safe_load(text)
        except Exception as e:
            return text
        if expose == 'list':
            pass
        if expose == 'css':
            if not isinstance(data,dict):
                return text

            use_wpraps = [
                'px', '#', 'rgb', '-','.','rgb','var'
            ]

            def mk(dc,l=0):
                ls = []
                for k,v in dc.items():
                    if isinstance(v,dict):
                         v = mk(v,l+1)
                         ts = ('\t'*l)
                         ls.append( k + ("{\n" + ts ) + v + ts + '}' )
                         continue

                    _use = True
                    for u in use_wpraps:
                        if u in v:
                            _use = False
                            break
                    v = v.strip("\"'")

                    if _use:
                        v = f'"{v}"'

                    ls.append( k + ":" + v + ';' )
                return ('\n' + ('\t' * l)).join(ls)
            return mk(data)
        return text

    def render( self ):
        # print( f"     Has changes? [{self}] {self.has_changes()}" )

        if not self.has_changes():
            return self.raw

        elif self.name == 'counter':
            return self._render_counter()

        if self['expose'] != None and self['expect'] != None:
            self._replace = self.from_to(
                self._replace, self['expect'], self['expose']
            )

        if self.is_ref():
            if self['ignore-spaces'] == None:
                self._replace = f"\n{self.tabs}".join(
                    str( self._replace ).split('\n')
                )

        if len(self.slots) == 0 and self.close_ends is not None:
            s = Soup(str(self._replace))
            for t in s.tags:
                if t.name != 'slot': continue
                if t.get('name','main') != 'main': continue
                t._replace = self.contents
            return s.to_string()

        if len(self.slots) == 0:
            return str(self._replace)

        s = Soup(str(self._replace))
        rslots = {}
        for t in s.tags:
            if t.name != 'slot': continue
            name = t.get('name','main')
            rslots[name] = rslots.get(name,[])
            rslots[name].append(t)

        for l in self.slots:
            name = l['attrs'].get('name','main')
            if name not in rslots:
                continue
            for r in rslots[name]:
                r._replace = l['contents']

        for t in s.tags:
            if t.name == 'slot' and t.has_changes():
                continue
            if t.name == 'slot':
                t._replace = ''

        return s.to_string()

    def has_changes(self):
        return self._replace != None

class Soup:
    def __init__(self, value:str, logger = lambda *a,**ka: x):
        if value is None:
            self._val = ''
            self.tags = []
        self._val = value
        self._logger = logger
        self.tags = [Tag(**t) for t in raw_tags(value)]

    def apply(self,args:dict,cbfn):
        for t in self.tags:
            good = True
            for k,v in args.items():
                a = getattr(t,k,None)
                if v != a:
                    good = False
                    break
            if good:
                cbfn(t)
        return self

    def refs(self):
        return [t for t in self.tags if t.is_ref()]

    def cnfs(self):
        return [c for c in self.tags if t.name == 'cnf']

    def no_refs(self):
        for r in self.refs():
            r._replace = ""

    def find_by(self,**kwargs):
        arr = []

        attrs = {}
        if 'attrs' in kwargs:
            attrs = kwargs['attrs']
            del kwargs['attrs']

        has_attrs = len(list(attrs.keys())) != 0

        for t in self.tags:
            append = True

            for k,v in kwargs.items():
                a = getattr(t,k,None)
                if v != a:
                    append = False
                    break

            if has_attrs and append:
                links = t.attrs
                for a in attrs.keys():
                    if a not in links:
                        append = False
                        break
                    if attrs[a] != links[a]:
                        append = False
                        break

            if append:
                arr.append(t)

        return arr

    def to_string(self):
        nv,reach,_have_slots = '', 0, False

        for t in self.tags:
            if len(t.slots) == 0:
                continue
            xt,et = t.outer_pos()
            for st in self.tags:
                if not st.has_changes():
                    continue

                _added = False
                for l in t.slots:
                    if st.raw in l['contents']:
                        l['contents'] = l['contents'].replace( st.raw, st._replace )
                        _added = True

                if _added:
                    st._replace = None

        for t in self.tags:
            s,e = t.outer_pos()
            if not t.has_changes():
                continue
            if s < reach:
                continue
            nv += self._val[reach:s]
            nv += t.render()
            reach = e

        nv += self._val[reach:len(self._val)]

        # print(nv)
        # print('#' * 80)
        return nv
