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
from charmhelpers.core.hookenv import relation_get, related_units

class QuorumPeers(RelationBase):
    # Every unit connecting will get the same information
    scope = scopes.GLOBAL
    relation_name = 'zookeeper-quorum'

    @hook('{peers:zookeeper-quorum}-relation-{changed}')
    def changed(self):
        self.conversation().set_state('{relation_name}.increased')
        

    @hook('{peers:zookeeper-quorum}-relation-{departed}')
    def departed(self):
        self.conversation().set_state('{relation_name}.decreased')


    def get_nodes(self):
        self.conversation().remove_state('{relation_name}.increased')
        return related_units()


    def get_departed(self):
        self.conversation().remove_state('{relation_name}.decreased')
        return relation_get('private-address')
