import json
import lib.mta as Mta

from redis import Redis
from lib.line_status import LineStatus

mta_web = Mta.Web()
statuses = mta_web.from_planner()

for ping in statuses:
  current = LineStatus.loadLine(ping["line"])
  current.setStatus(ping["status"])
  current.save()