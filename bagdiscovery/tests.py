from django.test import TestCase
from .models import *
from .library import *
# Create your tests here.


class Data(object):

    data = dict( url='http://localhost:8000/api/accessions/8/', creators=[], external_identifiers=[], transfers=[],
               organization="Test Organization", rights_statements=[], language="und",
               title="Test Organization, Custard Pie Appreciation Consortium, Desperate Dan Appreciation Society grant records",
               accession_number='null', accession_date="2018-09-18T11:13:25.348653-04:00",
               start_date="1994-05-14T00:00:00-04:00", end_date="2005-06-22T00:00:00-04:00", extent_files=47,
               extent_size=18315519,
               description="Grant awarded to the Village Green Preservation Society for the purpose of \"preserving the old ways from being abused, protecting the new ways for me and for you\"",
               access_restrictions="Records embargoed for 10 years after date of creation. Records are open for research after expiration of embargo period.",
               use_restrictions="Records under copyright may not be republished without permission from the copyright holder. Work for hire, under copyright until 40 years after creation.",
               resource="http://example.org", acquisition_type="donation", appraisal_note="",
               created="2018-09-18T11:13:25.348762-04:00", last_modified="2018-09-18T11:13:25.567316-04:00",
               process_status=10)

class BagTestCase(TestCase):

        def test_isdatavalid(self):
            datatest = Data()
            self.assertTrue(isdatavalid(datatest.data))
