from django_cron import CronJobBase, Schedule
import logging
from structlog import wrap_logger
from uuid import uuid4
from .library import BagDiscovery
from .models import Bag

logger = wrap_logger(logger=logging.getLogger(__name__))


class BagStore(CronJobBase):
    RUN_EVERY_MINS = 0
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)

    code = 'bagdiscovery.bagcron'

    def do(self):
        self.log = logger.new(transaction_id=str(uuid4()))
        try:
            BagDiscovery().run()
        except Exception as e:
            self.log.error(e)
            print(e)
