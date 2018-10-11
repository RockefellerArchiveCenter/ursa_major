from django_cron import  CronJobBase, Schedule
from .library import *

class bagStore(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins = RUN_EVERY_MINS)

    code = 'bagdiscovery.bagcron'

    def do(self):
        print("Test that cron works")
