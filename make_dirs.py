import os
from ursa_major import settings

for dir in [settings.LANDING_DIR, settings.STORAGE_DIR]:
    if not os.path.isdir(dir):
        os.makedirs(dir)
