from django_cron import  CronJobBase, Schedule
from .library import *
from .models import *

class bagStore(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins = RUN_EVERY_MINS)

    code = 'bagdiscovery.bagcron'

    def do(self):
        bag = Bag.objects.all()

        for i in bag:
            name = i.bag_identifier + ".tar.gz"
            print(name)
            if (checkforbag(name)) == 'true':
                # if true move to storage directory
                movebag(name)
                # Then store name, accession data, and path in database.
                # storebag(request, name)

