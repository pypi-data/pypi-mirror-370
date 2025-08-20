from bx_py_utils.test_utils.unittest_utils import BaseDocTests

import ha_services


class DocTests(BaseDocTests):
    def test_doctests(self):
        self.run_doctests(
            modules=(ha_services,),
        )
