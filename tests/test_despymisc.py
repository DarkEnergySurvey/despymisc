#!/usr/bin/env python2
import unittest
from contextlib import contextmanager
import sys
from StringIO import StringIO
from mock import patch, mock_open, MagicMock
from despymisc.xmlslurp import Xmlslurper

@contextmanager
def capture_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err

class TestXmlslurper(unittest.TestCase):
    tablelist = ("Astrometric_Instruments",
                 "FGroups",
                 "Fields",
                 "Photometric_Instruments",
                 "PSF_Extensions",
                 "PSF_Fields",
                 "Warnings")
    xmldata = """<main><TABLE name="FGroups">
<FIELD name="Field1" datatype="float"/>
<field name="Field2" datatype="int"/>
<field name="Field3" datatype="str"/>
<field name="Field4" datatype="int" arraysize="5"/>
<field name="Field5" datatype="char" arraysize="2"/>
<field name="field6" datatype="float" arraysize="2"/>
<field name="field7" datatype="bool" arraysize="3"/>
<TR>
 <TD>12345.6</TD><td>25</td><td>Blah</td><td>2 4 6 8 10</td><td>first second</td><td>2.5 6.7</td><td>1 0 1</td>
</TR>
<hi/>
</TABLE>
<table name="bad_table">
<field name="f1" datatype="int"/>
<tr><td>5</td></tr>
</table>
</main>
"""
    def test_all(self):
        with patch('despymisc.xmlslurp.open', mock_open(read_data=self.xmldata)) as mo:
            data = Xmlslurper('filename', self.tablelist)
            self.assertTrue('FGroups' in data.gettables().keys())
            self.assertTrue(len(data.gettables().keys()), 1)
            self.assertEqual(len(data.keys()), 1)
            tab = data.gettables()
            self.assertEqual(tab['FGroups'][0]['field1'], 12345.6)

if __name__ == '__main__':
    unittest.main()
