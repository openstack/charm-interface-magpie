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


class QuorumPeers(RelationBase):
    # Every unit connecting will get the same information
    scope = scopes.UNIT
    relation_name = 'zookeeper-quorum'

    @hook('{peers:zookeeper-quorum}-relation-{joined}')
    def changed(self):
        conv = self.conversation()
        conv.set_state('{relation_name}.relating')
        conv.remove_state('{relation_name}.departing')

    @hook('{peers:zookeeper-quorum}-relation-{departed}')
    def departed(self):
        conv = self.conversation()
        conv.remove_state('{relation_name}.relating')
        conv.set_state('{relation_name}.departing')

    def dismiss_departing(self):
        for conv in self.conversations():
            conv.remove_state('{relation_name}.departing')

    def dismiss_relating(self):
        for conv in self.conversations():
            conv.remove_state('{relation_name}.relating')

    def get_nodes(self):
        nodes = []
        for conv in self.conversations():
            nodes.append((conv.scope, conv.get_remote('private-address')))

        return nodes
