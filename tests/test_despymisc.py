#!/usr/bin/env python2
import unittest
from contextlib import contextmanager
import sys
import time
import errno
import signal
import psutil

from StringIO import StringIO
from mock import patch, mock_open
from despymisc.xmlslurp import Xmlslurper
import despymisc.subprocess4 as sub4

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

class TestSubprocess4(unittest.TestCase):
    class TestError(OSError):
        def __init__(self, text=''):
            OSError.__init__(self, text)
            self.errno = errno.ECHILD

    def test_init(self):
        _ = sub4.Popen(['ls','-1'])

    def test_wait(self):
        start = time.time()
        po = sub4.Popen(['sleep', '10'])
        po.wait4()
        self.assertTrue(time.time() - start >= 10.)

    def test_waitError(self):
        with patch('despymisc.subprocess4.os.wait4', side_effect=self.TestError()):
            start = time.time()
            po = sub4.Popen(['sleep', '10'])
            self.assertTrue(po.wait4() == 0)
            self.assertTrue(time.time() - start < 10.)
        with patch('despymisc.subprocess4.os.wait4', side_effect=OSError()):
            with self.assertRaises(OSError):
                po = sub4.Popen(['sleep', '10'])
                po.wait4()

    def test_fastReturn(self):
        po = sub4.Popen(['ls','-1'])
        time.sleep(3)
        po.returncode = 0
        self.assertIsNotNone(po.returncode)
        self.assertIsNotNone(po.wait4())

    def test_segfault(self):
        with capture_output() as (out, err):
            po = sub4.Popen(['ls','-1'])
            po.returncode = -signal.SIGSEGV
            self.assertTrue(-signal.SIGSEGV == po.wait4())
            output = out.getvalue().strip()
            self.assertTrue('SEGMENTATION' in output)

    def test_mismatchPID(self):
        with patch('despymisc.subprocess4.os.wait4', return_value=(0,1,{})) as osw:
            po = sub4.Popen(['ls'])
            pu = psutil.Process(po.pid)
            pu.terminate()
            pu.wait()
            self.assertEqual(po.wait4(), 1)

if __name__ == '__main__':
    unittest.main()
