import os
import shutil
import pytest

def test_package():

    import bin

    bin.cat('/etc/hosts').grep('[0-9]*')
    bin.curl('-s icanhazip.com')

    if shutil.which('cowsay'):
        bin.cowsay('omfg')
        # the one true test
        s1 = os.popen("cowsay omfg | sed 's/(oo)/(👀)/g'").read()
        s2 = bin.cowsay("omfg").sed("s/(oo)/(👀)/g")
        assert s1 == s2
