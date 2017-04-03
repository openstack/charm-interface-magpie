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

from charms.reactive import RelationBase, hook, scopes
from charmhelpers.core import hookenv

class MagpiePeers(RelationBase):
    scope = scopes.UNIT

    @hook('{peers:magpie}-relation-joined')
    def joined(self):
        conv = self.conversation()
        conv.remove_state('{relation_name}.departed')
        conv.set_state('{relation_name}.joined')

    @hook('{peers:magpie}-relation-departed')
    def departed(self):
        conv = self.conversation()
        conv.remove_state('{relation_name}.joined')
        conv.set_state('{relation_name}.departed')

    def dismiss_departed(self):
        for conv in self.conversations():
            conv.remove_state('{relation_name}.departed')

    def dismiss_joined(self):
        for conv in self.conversations():
            conv.remove_state('{relation_name}.joined')

    def get_nodes(self):
        nodes = []
        for conv in self.conversations():
            nodes.append((conv.scope, conv.get_remote('private-address')))
        return nodes

#    def initialise_iperf(self):
#        '''
#        First use juju leadership to pick client, then handle in code
#        '''
#        for conv in self.conversations():
#            conv.set_remote('iperf.initialised')
#
#    def iperf_initialised(self):
#        '''
#        Check if initialised
#        '''
#        for conv in self.conversations():
#            if conv.get_remote('iperf.initialised'):
#                return True
#
    def set_iperf_client(self):
        '''
        The unit which is currently allowed to test (all) other units
        '''
        for conv in self.conversations():
            conv.set_remote('is_iperf_client', True)

    def get_iperf_client(self):
        '''
        Checks which unit should currently be performing iperf checks
        '''
        for conv in self.conversations():
            if conv.get_remote('is_iperf_client'):
                return conv.get_remote('private_address')

    def set_iperf_server_ready(self):
        for conv in self.conversations():
            conv.set_state('iperf.server.ready')

    def set_iperf_server_checked(self):
        for conv in self.conversations():
            conv.set_state('iperf.server.checked')

    def check_ready_iperf_servers(self):
        nodes_ready = []
        for conv in self.conversations():
            hookenv.log(" CHECKING CONVERSAITIOSN ------------------------------------------------------", 'INFO')
            if conv.get_remote('iperf.server.ready'):
                hookenv.log(" YEP I FOUND ONE HERE ------------------------------------------------------", 'INFO')
                nodes_ready.append((conv.scope, conv.get_remote('private-address')))
        return nodes_ready

