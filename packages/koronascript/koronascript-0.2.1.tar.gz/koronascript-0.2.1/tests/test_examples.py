import os
import examples.channelRemoval as CR

TESTDATA = 'test_data/EK60'

def test_get_data():
    if not os.path.exists(TESTDATA):
        # Get test data from pyEchoLab examples:
        os.system('mkdir -p test_data && cd test_data && wget --recursive --no-parent -nH --cut-dirs=6 ftp://ftp.ngdc.noaa.gov/pub/outgoing/mgg/wcd/pyEcholab_data/examples/EK60')

def test_channelRemoval():
    """This fails to fail if no data is present"""
    CR.ks.run('test_data/EK60', 'test_out/cr_out')


