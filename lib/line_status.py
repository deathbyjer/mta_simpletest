from redis import Redis
import json
import math
from datetime import datetime
import time

class LineStatus:
    prefix = "line:status:"
    redis = Redis(host='redis', port=6379)
    
    log_file = "log/line_status.log"
  
    @classmethod
    def loadLine(cls, line):
        data = { "line": line.upper(), "seconds_delayed": 0, "total_seconds": 0 }
        try:
            data = json.loads(cls.redis.get(cls.prefix + line))
        except:
            True
            
        return LineStatus(data)
            
    @classmethod
    def buildFromLog(cls, log):
        return True
  
    # Generate from Data
    def __init__(self, data):
        self.line = data["line"]
        self.status = data["status"] if "status" in data else None
        self.last_logged = data["last_logged"] if "last_logged" in data else 0
        self.seconds_delayed = data["seconds_delayed"] if "seconds_delayed" in data else 0
        self.total_seconds = data["total_seconds"] if "total_seconds" in data else 0
      
    def setStatus(self, status, t = "now"):
        self.new_status = status
        
        if isinstance(t, int):
            self.new_status_at = t
        else:
            d = datetime.utcnow()
            self.new_status_at = time.mktime(d.timetuple())
  
    def is_delayed(self):
        return self.status == "delays"
  
    def uptime_percentage(self):
        if self.seconds_delayed == 0:
            return 1
        
        return 1 - (self.seconds_delayed / self.total_seconds)
  
    def save(self):
        if not (self.new_status and self.new_status_at):
            return
            
        self.__saveToRedis()
        self.__writeLog()
        
        self.new_status = None
        self.new_status_at = None
        
    def __saveToRedis(self):
      self.__prepareForRedis()
      out = {
        "line": self.line,
        "status": self.status,
        "last_logged": self.last_logged,
        "seconds_delayed": self.seconds_delayed,
        "total_seconds": self.total_seconds
      }
      
      self.__class__.redis.set(self.__class__.prefix + self.line, json.dumps(out))
      
    def __writeLog(self):
        f=open(self.__class__.log_file, "a+")
        f.write(json.dumps({"line": self.line, "status": self.new_status, "at": self.new_status_at}) + "\n")
        f.close()
        
    def __prepareForRedis(self):
        new_seconds = self.new_status_at - self.last_logged if self.last_logged else 0
        self.last_logged = self.new_status_at
        self.total_seconds += new_seconds
        
        is_new_delayed = self.__class__.__is_status_delayed(self.new_status)
        is_old_delayed = self.__class__.__is_status_delayed(self.status)
        self.status = self.new_status
        
        if not (is_new_delayed or is_old_delayed):
            return
        
        if is_new_delayed == is_old_delayed:
            self.seconds_delayed += new_seconds
        else:
            self.seconds_delayed += (new_seconds / 2)
        
        
    @classmethod
    def __is_status_delayed(cls, status):
      is_a_delay = {
        "good": False,
        "planned_work": False,
        "delays": True
      }
      
      return is_a_delay[status] if status in is_a_delay else False