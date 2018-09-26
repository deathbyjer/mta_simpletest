from crontab import CronTab

my_cron  = CronTab(user=True)
cron_id = "ping_web"

for job in my_cron.find_comment(cron_id):
    cron.remove(job)

job = my_cron.new(command="/bin/bash -l -c 'cd /code && python ping_web.py'", comment=cron_id)
job.minute.every(3)
my_cron.write()