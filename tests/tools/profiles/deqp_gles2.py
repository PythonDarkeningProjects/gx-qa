# Copyright 2014, 2015 Intel Corporation
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Piglit integrations for dEQP GLES2 tests."""

import xml.etree.cElementTree as ET

from framework.test import deqp

__all__ = ['profile']

# Path to the deqp-glES2 executable.
_DEQP_GLES2_EXE = deqp.get_option('PIGLIT_DEQP_GLES2_EXE',
                                  ('deqp-gles2', 'exe'))

# Path to the xml file which contained the case list of the subset of dEQP
# and marked as must pass in CTS.
_DEQP_MUSTPASS = deqp.get_option('PIGLIT_DEQP_MUSTPASS',
                                 ('deqp-gles2', 'mustpasslist'))

_EXTRA_ARGS = deqp.get_option('PIGLIT_DEQP_GLES2_EXTRA_ARGS',
                              ('deqp-gles2', 'extra_args'),
                              default='').split()


def _get_test_case(root, root_group, outputfile):
    """Parser the test case list of Google Android CTS,
    and store the test case list to dEQP-GLES2-cases.txt
    """
    for child in root:
        root_group.append(child.get('name'))
        if child.tag == "Test":
            outputfile.write('TEST: {}\n'.format('.'.join(root_group)))
            del root_group[-1]
        else:
            _get_test_case(child, root_group, outputfile)
            del root_group[-1]


def _load_test_hierarchy(mustpass, case_list):
    """Google have added a subset of dEQP to CTS test, the case list is stored
    at some xml files. Such as: com.drawelements.deqp.glES2.xml This function
    is used to parser the file, and generate a new dEQP-GLES2-cases.txt which
    only contain the subset of dEQP.
    """
    tree = ET.parse(mustpass)
    root = tree.getroot()
    root_group = []
    with open(case_list, 'w') as f:
        _get_test_case(root, root_group, f)


def filter_mustpass(caselist_path):
    """Filter tests that are not in the DEQP_MUSTPASS profile."""
    if _DEQP_MUSTPASS is not None:
        _load_test_hierarchy(_DEQP_MUSTPASS, caselist_path)

    return caselist_path


class DEQPGLES2Test(deqp.DEQPBaseTest):
    deqp_bin = _DEQP_GLES2_EXE
    extra_args = [x for x in _EXTRA_ARGS if not x.startswith('--deqp-case')]


    def __init__(self, *args, **kwargs):
        super(DEQPGLES2Test, self).__init__(*args, **kwargs)


profile = deqp.make_profile(  # pylint: disable=invalid-name
    deqp.iter_deqp_test_cases(filter_mustpass(
        deqp.gen_caselist_txt(_DEQP_GLES2_EXE, 'dEQP-GLES2-cases.txt',
                              _EXTRA_ARGS))),
    DEQPGLES2Test)
