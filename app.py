# compose_flask/app.py
import json

from flask import Flask
from redis import Redis

import lib.mta as Mta
from lib.line_status import LineStatus

app = Flask(__name__)

# We only use redis to monitor tasks and the current "live state"
redis = Redis(host='redis', port=6379)

#@app.route('/')
#def hello():
#    mta_reader = Mta.StatusReader()
#    mta_web = Mta.Web()
#    incidents = mta_reader.gather_incidents()
#    statuses = mta_web.from_planner()
    
#    for status in statuses:
#      line = LineStatus.loadLine(status["line"])
#      line.setStatus(status["status"])
#      line.save()
    
    #return json.dumps(incidents)
    #return json.dumps(statuses)
    #return statuses
    #return 'This Compose/Flask demo has been viewed %s time(s).' % redis.get('hits')


@app.route("/status/<line>")
def is_delayed(line):
  line = LineStatus.loadLine(line)
  return "Delayed" if line.is_delayed() else "Not Delayed"
    
@app.route("/percent_uptime/<line>")
def percent_uptime(line):
  line = LineStatus.loadLine(line)
  return str(line.uptime_percentage())
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)