# vim: set fileencoding=UTF-8:

import os
import sys
from collections import OrderedDict

from epicsdbbuilder import *


def test_output(tmp_path):
    ResetRecords()

    InitialiseDbd(
        os.environ.get("EPICS_BASE", None), os.environ.get("EPICS_HOST_ARCH", None)
    )

    tmpl_names = TemplateRecordNames()
    dls_names = SimpleRecordNames("XX-YY-ZZ-01", ":")

    SetRecordNames(dls_names)

    P = Parameter("P", "A parameter")
    assert repr(P) == "Parameter(P)"
    Q = Parameter("Q", "A number")

    r = ImportRecord("SR-DI-DCCT-01:SIGNAL")

    records.bi(
        "TRIG",
        FLNK=create_fanout(
            "FAN", records.longin("A", DESC="blah"), records.ai("B", INP=r)
        ),
        SCAN="1 second",
    )

    s = ImportRecord(RecordName("TRIG"))

    PushPrefix("ABC")

    r = records.ai("TEST")
    r.add_comment("comment 1")
    r.add_metadata("metadata")
    r.add_comment("comment 2")

    assert PopPrefix() == "ABC"

    SetRecordNames(tmpl_names)

    t = records.ai("TEST", INP="@%s" % P, VAL=Q, SCAN="1 second")
    records.bi("BOO", INP=s)

    # Test link options
    records.ai("OPTIONS:CA", INP=CA(t))
    records.ai("OPTIONS:CP", INP=CP(t))
    records.ai("OPTIONS:CPP", INP=CPP(t))
    records.ai("OPTIONS:NP", INP=NP(t))
    records.ai("OPTIONS:MSS", INP=MSS(t))
    records.ai("OPTIONS:MSI", INP=MSI(t))
    records.ai("OPTIONS:NMS", INP=NMS(t))

    # Test multiple link options
    records.ai("OPTIONS:PP:MS", INP=PP(MS(t)))

    # Test const array with QSRV infos
    w = records.waveform("FIELD:WITH_CONST_ARRAY", INP=ConstArray(["A", "B", "C"]))
    # Ordereddict for python2.7 compat
    td = OrderedDict(
        [
            ("+id", "epics:nt/NTTable:1.0"),
            ("labels", OrderedDict([("+type", "plain"), ("+channel", "VAL")])),
        ]
    )
    w.add_info("Q:group", {"MYTABLE": td})
    # And json links with readbacks
    a = records.ai("FIELD:WITH_JSON_LINK", INP={"const": 3.14159265358979})
    a.add_info("asyn:READBACK", 1)
    a.add_info("autosaveFields", "PREC EGU DESC")

    # A string constant with some evil character values
    records.stringin("STRING", VAL='"\n\\\x01€')

    fname = str(tmp_path / "test_output.db")
    expected_open_args = {}
    if sys.version_info > (3,):
        # Specify encoding so it works on windows
        expected_open_args["encoding"] = "utf8"

    def lines(fname, **open_args):
        return [x.rstrip() for x in open(fname, **open_args).readlines()[1:]]

    WriteRecords(fname, alphabetical=False)
    expected = os.path.join(os.path.dirname(__file__), "expected_output.db")
    assert lines(fname) == lines(expected, **expected_open_args)

    WriteRecords(fname)
    expected = os.path.join(
        os.path.dirname(__file__), "expected_output_alphabetical.db"
    )
    assert lines(fname) == lines(expected, **expected_open_args)
