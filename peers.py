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

import json
import netaddr
import netifaces

from charms.reactive import RelationBase, hook, scopes


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

    def get_nodes(self, cidr=None):
        nodes = []
        if cidr:
            network = netaddr.IPNetwork(cidr)
        for conv in self.conversations():
            iperf_addresses = conv.get_remote('iperf_addresses')
            ip = None
            if cidr and iperf_addresses:
                for addr in json.loads(iperf_addresses):
                    if netaddr.IPNetwork(addr) in network:
                        ip = addr
                        break
            if not ip:
                ip = conv.get_remote('private-address')
            nodes.append((conv.scope, ip))
        return nodes

    def set_iperf_checked(self):
        postnode = []
        for conv in self.conversations():
            prenode = conv.get_remote('iperf.checked')
            postnode.append(str(prenode) + " " + conv.scope)
            conv.set_remote('iperf.checked', postnode)

    def get_iperf_checked(self):
        nodes = []
        for conv in self.conversations():
            nodes.append(conv.get_remote('iperf.checked'))
        return nodes

    def set_iperf_server_ready(self):
        for conv in self.conversations():
            conv.set_remote('iperf.server', True)

    def set_iperf_server_checked(self):
        for conv in self.conversations():
            conv.set_remote('iperf.server.checked')

    def check_ready_iperf_servers(self):
        nodes_ready = []
        for conv in self.conversations():
            if conv.get_remote('iperf.server'):
                nodes_ready.append((conv.scope,
                                    conv.get_remote('private-address')))
        return nodes_ready

    def advertise_addresses(self):
        addrs = []
        for iface in netifaces.interfaces():
            for addr in netifaces.ifaddresses(iface).get(
                    netifaces.AF_INET, []):
                addrs.append(addr['addr'])
        for conv in self.conversations():
            conv.set_remote('iperf_addresses', json.dumps(sorted(addrs)))
