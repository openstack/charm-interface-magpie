# Copyright 2020 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import importlib
import unittest
import mock


with mock.patch('charmhelpers.core.hookenv.metadata') as _meta:
    _meta.return_Value = 'ss'
    import peers


_hook_args = {}

TO_PATCH = [
    'RelationBase',
    'hook',
]


def mock_hook(*args, **kwargs):

    def inner(f):
        # remember what we were passed.  Note that we can't actually determine
        # the class we're attached to, as the decorator only gets the function.
        _hook_args[f.__name__] = dict(args=args, kwargs=kwargs)
        return f
    return inner


class _unit_mock:
    def __init__(self, unit_name, received=None):
        self.unit_name = unit_name
        self.received = received or {}


class _relation_mock:
    def __init__(self, application_name=None, units=None):
        self.to_publish_raw = {}
        self.application_name = application_name
        self.units = units


class TestMagpiePeers(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._patched_hook = mock.patch('charms.reactive.hook', mock_hook)
        cls._patched_hook_started = cls._patched_hook.start()
        # force peers to rerun the mock_hook decorator:
        importlib.reload(peers)

    @classmethod
    def tearDownClass(cls):
        cls._patched_hook.stop()
        cls._patched_hook_started = None
        cls._patched_hook = None
        # and fix any breakage we did to the module
        importlib.reload(peers)

    def patch(self, method):
        _m = mock.patch.object(self.obj, method)
        _mock = _m.start()
        self.addCleanup(_m.stop)
        return _mock

    def get_fake_remote_data(self, conv_name):
        def _get_fake_remote_data(key, default=None):
            return self._remote_data[conv_name].get(key) or default
        return _get_fake_remote_data

    def get_fake_local_data(self, key, default=None):
        return self._local_data.get(key) or default

    def patch_mpeer(self, attr, return_value=None):
        mocked = mock.patch.object(self.mpeer, attr)
        self._patches[attr] = mocked
        started = mocked.start()
        started.return_value = return_value
        self._patches_start[attr] = started
        setattr(self, attr, started)

    def setUp(self):
        self._patches = {}
        self._patches_start = {}
        self.obj = peers
        for method in TO_PATCH:
            setattr(self, method, self.patch(method))
        self._rel_ids = ["magpie:3"]
        self._remote_data = {}
        self._local_data = {}

        conversations = []

        def _init_conversation(conv_name, unit_name):
            _conv = mock.MagicMock()
            _conv.relation_ids = self._rel_ids
            _conv.scope = unit_name
            _conv.get_remote.side_effect = self.get_fake_remote_data(conv_name)
            _conv.get_local.side_effect = self.get_fake_local_data
            conversations.append(_conv)
            self._remote_data[conv_name] = {}
            return _conv

        self._conversation1 = _init_conversation('conv1', 'magpie/1')
        self._conversation2 = _init_conversation('conv2', 'magpie/2')

        # The Relation object
        self.mpeer = peers.MagpiePeers('magpie-relation', conversations)
        self.patch_mpeer('conversations', conversations)
        self.patch_mpeer('conversation', conversations[0])

    def tearDown(self):
        self.ncr = None
        for k, v in self._patches.items():
            v.stop()
            setattr(self, k, None)
        self._patches = None
        self._patches_start = None

    def test_registered_hooks(self):
        # test that the decorators actually registered the relation
        # expressions that are meaningful for this interface: this is to
        # handle regressions.
        # The keys are the function names that the hook attaches to.
        hook_patterns = {
            'joined': ('{peers:magpie}-relation-joined', ),
            'departed': ('{peers:magpie}-relation-departed', ),
        }
        for k, v in _hook_args.items():
            self.assertEqual(hook_patterns[k], v['args'])

    def test_joined(self):
        self.mpeer.joined()
        self._conversation1.remove_state.assert_called_once_with(
            '{relation_name}.departed')
        self._conversation1.set_state.assert_called_once_with(
            '{relation_name}.joined')

    def test_departed(self):
        self.mpeer.departed()
        self._conversation1.remove_state.assert_called_once_with(
            '{relation_name}.joined')
        self._conversation1.set_state.assert_called_once_with(
            '{relation_name}.departed')

    def test_dismiess_departed(self):
        self.mpeer.dismiss_departed()
        self._conversation1.remove_state.assert_called_once_with(
            '{relation_name}.departed')

    def test_dismiess_joined(self):
        self.mpeer.dismiss_joined()
        self._conversation1.remove_state.assert_called_once_with(
            '{relation_name}.joined')

    def test_get_nodes(self):
        self._remote_data['conv1'] = {'private-address': '10.0.0.10'}
        self._remote_data['conv2'] = {'private-address': '10.0.0.11'}
        self.assertEqual(
            self.mpeer.get_nodes(),
            [('magpie/1', '10.0.0.10'), ('magpie/2', '10.0.0.11')])

    def test_set_iperf_checked(self):
        self._remote_data['conv1'] = {'iperf.checked': 'True'}
        self._remote_data['conv2'] = {'iperf.checked': 'True'}
        self.mpeer.set_iperf_checked()
        self._conversation1.set_remote.assert_called_once_with(
            'iperf.checked', ['True magpie/1', 'True magpie/2'])
        self._conversation2.set_remote.assert_called_once_with(
            'iperf.checked', ['True magpie/1', 'True magpie/2'])

    def test_get_iperf_checked(self):
        self._remote_data['conv1'] = {'iperf.checked': 'True'}
        self._remote_data['conv2'] = {'iperf.checked': 'True'}
        self.assertEqual(
            self.mpeer.get_iperf_checked(),
            ['True', 'True'])

    def test_set_iperf_server_ready(self):
        self.mpeer.set_iperf_server_ready()
        self._conversation1.set_remote.assert_called_once_with(
            'iperf.server', True)
        self._conversation2.set_remote.assert_called_once_with(
            'iperf.server', True)

    def test_set_iperf_server_checked(self):
        self.mpeer.set_iperf_server_checked()
        self._conversation1.set_remote.assert_called_once_with(
            'iperf.server.checked')
        self._conversation2.set_remote.assert_called_once_with(
            'iperf.server.checked')

    def test_check_ready_iperf_servers(self):
        self._remote_data['conv1'] = {
            'private-address': '10.0.0.10',
            'iperf.server': True}
        self._remote_data['conv2'] = {'private-address': '10.0.0.11'}
        self.assertEqual(
            self.mpeer.check_ready_iperf_servers(),
            [('magpie/1', '10.0.0.10')])
