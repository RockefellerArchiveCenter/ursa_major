from django_cron import CronJobBase, Schedule
from .library import BagDiscovery
from .models import Bag


class BagStore(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)

    code = 'bagdiscovery.bagcron'

    def do(self):
            try:
                BagDiscovery().run()
            except Exception as e:
                print(e)
