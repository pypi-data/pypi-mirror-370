import yaml, uuid
from functools import lru_cache
from croniter import croniter
from ics import Event
from os.path import basename
from datetime import datetime as dt
from ics.grammar.parse import ContentLine
from datetime import date, datetime as dt
from dateutil import parser 


class Schedule:

    def __init__(self,path):
        self.path = path 
        self.data = {}
        self._is_contact = False
    
    def transform_contact(self):
        self._load()
        cont = self.data
        birthday = cont.get("birthday")

        self.data = {
            "active" : True,
            'is-all-day' : 'true'
        }

        if birthday is not None:
            bdate = Schedule._date(birthday)
            self.data['cron'] = f"0 0 {bdate.day} {bdate.month} *"
            self.data['start'] = birthday
        else:
            self.data['active'] = False 

        self._is_contact = True
    
    @property
    def is_contact(self):
        return self._is_contact
    
    def validate(self):
        ics = self.data.get("ics",{})
        if str(ics.get('active','false')).lower() == 'false':
            return
        
        if 'ics' in self.data and isinstance(self.data['ics'],dict):
            self.data['ics']['active'] = 'true'
        elif 'ics' in self.data and not isinstance(self.data['ics'],dict):
            self.data['ics'] = {'active':'true'}
        elif 'ics' not in self.data:
            self.data['ics'] = {'active':'true'}


    @lru_cache
    def _load(self):
        try:
            with open(self.path,'r') as f:
                self.data = yaml.safe_load(f.read())
        except Exception:
            pass

    @property
    def name(self):
        bn = basename(self.path)
        bn = bn.split('.')[:-1]
        bn = ".".join(bn)
        return bn

    @property
    @lru_cache
    def active(self):
        self._load()
        return str(self.data.get('active',False)).lower() == 'true'
    
    @property
    @lru_cache
    def is_ics(self):
        ics = self.data.get('ics',{})
        ics_active = str(ics.get('active',"False")).lower()
        ics_active = ics_active == 'true' or ics_active == '1'
        return isinstance(ics,dict) and ics_active

    @property
    def cron_expr(self):
        return self.data.get('cron',None)

    @property
    @lru_cache
    def cron(self):
        if self.cron_expr is None:
            return

        if not croniter.is_valid(self.cron_expr):
            return

        return croniter(self.cron_expr,dt.now())
        
    def ics_days(self,days):
        _days = ['SU','MO','TU','WE','TH','FR','SA']
        return ','.join([_days[(int(d))] for d in days])

    @property
    @lru_cache
    def valid(self):
        return self.cron is not None \
                and self.is_ics \
                and self.cron_data is not None
    
    @property
    @lru_cache
    def cron_data(self):
        if self.cron is None:
            return None
    
        return croniter.expand(self.cron_expr)
    
    @staticmethod
    def _date(dx,default=date(1990,1,1)):
        if isinstance(dx,str):
            try:
                px = parser.parse(dx).date()
                if px is None:
                    return default
                return px
            except Exception:
                return default
        elif isinstance(dx,dict):
            y,m,d = dx.get('year'), dx.get("month"),dx.get("day")

            if y == None or \
               m == None or \
               d == None or \
               not str(y).isnumeric() or \
               not str(m).isnumeric() or \
               not str(d).isnumeric():
                return default
                
            return date(int(y),int(m),int(d))
        return default
    

    @property
    @lru_cache
    def start_date(self):
        data = self.data
        _date = data.get("start",data.get("start-date"))
        return Schedule._date(_date,date(1900,1,1))


    @property
    @lru_cache
    def end_date(self):
        data = self.data
        _date = data.get("end" ,data.get("end-date"))
        return Schedule._date(_date,date(3000,1,1))
       

    @property
    @lru_cache
    def urgency(self):
        u = self.data.get('urgency',0)
        if str(u).isnumeric():
            return u
        return 0

    @property
    def is_all_day(self):
        return str(self.data.get('is-all-day','false')).lower() == 'true'

    @property
    def event(self):
        e = Event()

        e.name        = self.name
        e.uid         = str(uuid.uuid4())
        e.description = self.data.get('description','undefined')
        e.priority    = self.urgency
        e.begin       = self.start_date

        parts         = self.cron_data[0]

        if self.is_all_day:
            e.make_all_day()

        yearly = self.data.get("yearly",None)
        if yearly is not None and str(yearly).isnumeric():
            days = ",".join(str(x) for x in parts[2])
            mont = ",".join(str(x) for x in parts[3])

            e.extra.append(ContentLine(
                name  = 'RRULE',
                value = f"FREQ=YEARLY;INTERVAL={yearly};BYMONTH={month};BYMONTHDAY={days}"
            ))

        elif parts[2] != ["*"] and parts[4] == ["*"]:
            rule = "FREQ=MONTHLY;BYMONTHDAY=" + ",".join(str(x) for x in parts[2])
            e.extra.append(ContentLine(name="RRULE", value=rule))
        elif parts[4] != '*':
            rule = "FREQ=WEEKLY;BYDAY=" + self.ics_days(parts[4])
            e.extra.append(ContentLine(name="RRULE", value=rule))
        else:
            rule = "FREQ=DAILY"
            e.extra.append(ContentLine(name="RRULE", value=rule))

        return e
