from django_cron import CronJobBase, Schedule
from .library import *
from .models import *


class bagStore(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)

    code = 'bagdiscovery.bagcron'

    def do(self):
        bags = Bag.objects.all()

        for bag in bags:
            # name = bag.bag_identifier + ".tar.gz"
            # # print(name)
            try:
                process_bag(bag)
            except Exception as e:
                print('No bags are present')
