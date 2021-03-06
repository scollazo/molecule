#  Copyright (c) 2015-2016 Cisco Systems, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.

import pytest

from molecule.verifier import testinfra


@pytest.fixture()
def testinfra_instance(molecule_instance):
    return testinfra.Testinfra(molecule_instance)


@pytest.fixture
def patched_code_verifier(mocker):
    return mocker.patch('molecule.verifier.testinfra.Testinfra._flake8')


@pytest.fixture
def patched_test_verifier(mocker):
    return mocker.patch('molecule.verifier.testinfra.Testinfra._testinfra')


@pytest.fixture
def patched_get_tests(mocker):
    return mocker.patch('molecule.verifier.testinfra.Testinfra._get_tests')


@pytest.fixture
def patched_ansible(mocker):
    return mocker.patch('molecule.ansible_playbook.AnsiblePlaybook')


def test_execute(mocker, patched_code_verifier, patched_test_verifier,
                 patched_get_tests, patched_ansible, testinfra_instance):
    patched_get_tests.return_value = ['/test/1', '/test/2']
    patched_ansible.return_value = mocker.Mock(env={})
    testinfra_instance._molecule.args = {'debug': True, 'sudo': True}
    testinfra_instance.execute()

    patched_code_verifier.assert_called_once_with(['/test/1', '/test/2'])
    patched_test_verifier.assert_called_once_with(
        ['/test/1', '/test/2'],
        ansible_inventory='test/inventory_file',
        ansible_env={},
        connection='ansible',
        debug=True,
        sudo=True)


def test_execute_no_tests(patched_code_verifier, patched_test_verifier,
                          patched_get_tests, testinfra_instance):
    patched_get_tests.return_value = []
    testinfra_instance.execute()

    assert not patched_code_verifier.called
    assert not patched_test_verifier.called


def test_testinfra(mocker, patched_get_tests, testinfra_instance):
    patched_testinfra = mocker.patch('sh.testinfra')
    args = ['/tmp/ansible-inventory']
    kwargs = {'debug': True, 'out': None, 'err': None}
    testinfra_instance._testinfra(*args, **kwargs)

    patched_testinfra.assert_called_once_with(
        '/tmp/ansible-inventory', _env={}, _err=None, _out=None, debug=True)


def test_flake8(mocker, testinfra_instance):
    patched_flake8 = mocker.patch('sh.flake8')
    args = ['test1.py', 'test2.py']
    testinfra_instance._flake8(args)

    patched_flake8.assert_called_once_with(args)


def test_get_tests(testinfra_instance):
    assert [] == testinfra_instance._get_tests()
