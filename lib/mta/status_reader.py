import math
import http.client
import xml.dom.minidom

# This is an instantiated class because originally, it was going to read the live data, which needs a dev key.
#
# Later on, I found this library. I did this because I don't trust screen scrapers - but I implemented that anyway
# because it's the only thing that would solve the stated assignment.
class StatusReader:
    status_host = "web.mta.info"
    status_path = "/status/ServiceStatusSubway.xml"
    
    def gather_incidents(self):
        data = self.__lookup_incidents()
        dom = xml.dom.minidom.parseString(data)
        dom_incidents = dom.getElementsByTagName("PtSituationElement")
        return list(map(self.__class__.__translate_situation, dom_incidents))   
    
    def __lookup_incidents(self):
        conn = http.client.HTTPConnection(self.__class__.status_host)
        conn.request("GET", self.__class__.status_path)
        res = conn.getresponse()
        if not math.floor(res.status / 100) <= 3:
            raise Exception("could not reach service")
        
        data = res.read()
        conn.close()
        return data
        
    @classmethod  
    def __translate_situation(cls, situation):
        # We are going to parse the routes into both route and lines
        routes = list(map(lambda s: { "line": cls.__readSingleChild(s, "LineRef"), "direction": cls.__readSingleChild(s, "DirectionRef")}, situation.getElementsByTagName("AffectedVehicleJourney")))
        routes = list(filter(lambda s: s["line"] and s["direction"], routes))
        for route in routes:
          route["line"] = route["line"].upper().replace("MTA NYCT_", "")
        
        # And we just care about the condition, not the severity
        conditions = map(lambda s: cls.__readSingleChild(s, "Condition"), situation.getElementsByTagName("Consequence"))
        
        # We can lookup some other conditions, start times and end times and stuff like that... but not for now
        return {
          "routes": routes,
          "lines": list(set(list(map(lambda r: r["line"], routes)))),
          "conditions": conditions
        }   
       
    @classmethod    
    def __readSingleChild(cls, node, child):
        return cls.__getText(node.getElementsByTagName(child)[0])
        
    @classmethod   
    def __getText(cls, nodelist):
        rc = []
        for node in nodelist.childNodes:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc).strip()
    