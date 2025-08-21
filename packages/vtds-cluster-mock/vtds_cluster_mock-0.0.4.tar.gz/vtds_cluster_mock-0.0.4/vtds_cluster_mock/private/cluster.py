#
# MIT License
#
# (C) Copyright 2024-2025 Hewlett Packard Enterprise Development LP
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
"""Private layer implementation module for the kvm cluster.

"""
from random import randint
from ipaddress import IPv4Network
from vtds_base import (
    ContextualError,
    info_msg,
    expand_inheritance
)
from vtds_base.layers.cluster import (
    ClusterAPI
)

from .common import Common
from .api_objects import (
    VirtualNodes,
    VirtualNetworks
)


class Cluster(ClusterAPI):
    """Cluster class, implements the kvm cluster layer
    accessed through the python Cluster API.

    """
    def __init__(self, stack, config, build_dir):
        """Constructor, stash the root of the platfform tree and the
        digested and finalized cluster configuration provided by the
        caller that will drive all activities at all layers.

        """
        self.__doc__ = ClusterAPI.__doc__
        self.config = config.get('cluster', None)
        if self.config is None:
            raise ContextualError(
                "no cluster configuration found in top level configuration"
            )
        self.provider_api = None
        self.stack = stack
        self.build_dir = build_dir
        self.common = Common(self.config, self.stack, self.build_dir)
        self.prepared = False

    def __add_endpoint_ips(self, network):
        """Go through the list of connected blade classes for a
        network and use the list of endpoint IPs represented by all of
        the blades in each of those classes to compose a comprehensive
        list of endpoint IPs for the overlay network we are going to
        build for the network. Add that list under the 'endpoint_ips'
        key in the network and return the modified network to the
        caller.

        """
        virtual_blades = self.provider_api.get_virtual_blades()
        try:
            interconnect = network['blade_interconnect']
        except KeyError as err:
            raise ContextualError(
                "network configuration '%s' does not specify "
                "'blade_interconnect'" % str(network)
            ) from err
        blade_classes = network.get('connected_blade_classes', None)
        blade_classes = (
            virtual_blades.blade_classes()
            if blade_classes is None
            else blade_classes
        )
        network['endpoint_ips'] = [
            virtual_blades.blade_ip(blade_class, instance, interconnect)
            for blade_class in blade_classes
            for instance in range(0, virtual_blades.blade_count(blade_class))
        ] if interconnect is not None else []
        return network

    @staticmethod
    def __clean_deleted_interfaces(node_class_config):
        """Go through the network interfaces in a node class
        configuration and remove any that have the 'deleted' flag
        set. Return the resulting config.

        """
        net_interfaces = {
            key: interface
            for key, interface in node_class_config.get(
                    'network_interfaces', {}
            ).items()
            if not interface.get('delete', False)
        }
        node_class_config['network_interfaces'] = net_interfaces
        return node_class_config

    @staticmethod
    def __clean_deleted_partitions(disk):
        """Go through any partitions that might be defined on a disk
        and remove any that have been deleted.

        """
        partitions = {
            key: partition
            for key, partition in disk.get('partitions', {}).items()
            if not partition.get('delete', False)
        }
        disk['partitions'] = partitions
        return disk

    def __clean_deleted_disks(self, node_class_config):
        """Go through the additional disks in a node class
        configuration and remove any that have the 'deleted' flag
        set. Return the resulting config.

        """
        virtual_machine = node_class_config.get('virtual_machine', {})
        additional_disks = {
            key: self.__clean_deleted_partitions(disk)
            for key, disk in virtual_machine.get(
                    'additional_disks', {}
            ).items()
            if not disk.get('delete', False)
        }
        virtual_machine['additional_disks'] = additional_disks
        node_class_config['virtual_machine'] = virtual_machine
        return node_class_config

    @staticmethod
    def __get_node_classes(config):
        """Extract the node classes section from a cluster config and
        return it.

        """
        node_classes = (
            config.get('node_classes', None)
        )
        if node_classes is None:
            raise ContextualError(
                "configuration error - cluster configuration has no "
                "'node_classes' defined: %s" % (str(config))
            )
        return node_classes

    @staticmethod
    def __net_name(network):
        """Return the network name of a network and error if there is
        none.

        """
        netname = network.get('network_name', None)
        if netname is None:
            raise ContextualError(
                "configuration error: network has no network name: %s" %
                str(network)
            )
        return netname

    def __get_addr_family(self, network, family):
        """Look up the address family configuration for the specified
        address family in the specified network.

        """
        addr_families = network.get('address_families', None)
        if addr_families is None:
            raise ContextualError(
                "configuration error: network '%s' has no "
                "'address_families' section" % self.__net_name(network)
            )
        candidates = [
            addr_family
            for _, addr_family in addr_families.items()
            if addr_family.get('family', None) == family
        ]
        if not candidates:
            raise ContextualError(
                "configuration error: network '%s' has no "
                "%s address family" % (self.__net_name(network), family)
            )
        if len(candidates) > 1:
            raise ContextualError(
                "configuration error: network '%s' has more than one "
                "%s address family" % (self.__net_name(network), family)
            )
        return candidates[0]

    def __get_ipv4_cidr(self, network):
        """Return the IPv4 CIDR for the specified network.  Error if
        there is none.

        """
        addr_family = self.__get_addr_family(network, 'AF_INET')
        cidr = addr_family.get('cidr', None)
        if cidr is None:
            raise ContextualError(
                "configuration error: AF_INET address family for "
                "network '%s' has no 'cidr' specified" %
                self.__net_name(network)
            )
        return cidr

    def __cluster_node_count(self):
        """Return the total number of Virtual Nodes in the cluster

        """
        node_classes = self.__get_node_classes(self.config)
        counts = [
            int(node_class.get('node_count', 0))
            for _, node_class in node_classes.items()
        ]
        return sum(counts)

    def __add_host_blade_net(self):
        """Merge the blade host networks into the config making sure
        every Virtual Node instance is connected to a blade host
        network and has a static IP address, and making sure that each
        Virtual Blade is connected to its blade host network and has
        an IP address.

        """
        virtual_blades = self.provider_api.get_virtual_blades()
        node_classes = self.config.get('node_classes', {})
        networks = self.config.get('networks', {})
        host_blade_network = self.config.get('host_blade_network', None)
        netname = self.__net_name(host_blade_network)
        hosts = [
            *IPv4Network(self.__get_ipv4_cidr(host_blade_network)).hosts()
        ][:self.__cluster_node_count() + 1]
        hosts.reverse()  # We are going to pop from this list, so reverse it
        # The blade IP for every conencted blade on the host blade
        # network is the same. It is the '.1' IP in the CIDR block for
        # that network.
        blade_ip = str(hosts.pop())
        if host_blade_network is None:
            raise ContextualError(
                "configuration error: no 'host_blade_network' defined in "
                "the cluster configuration"
            )
        # Connect the host_blade_network to all blades of all classes.
        blade_classes = virtual_blades.blade_classes()
        addr_family = self.__get_addr_family(host_blade_network, 'AF_INET')
        addr_family['connected_blades'] = [
            {
                'blade_class': blade_class,
                'blade_instances': [
                    *range(0, virtual_blades.blade_count(blade_class))
                ],
                # All blade IPs are the '.1' address of the
                # network. We need one copy of that value per blade
                # instance.
                'blade_ips': [blade_ip] * virtual_blades.blade_count(
                    blade_class
                ),
                'dhcp_server_instance': None,
            }
            for blade_class in blade_classes
        ]
        # Add the host blade network to the set of Virtual Networks so
        # it will be used.
        networks[netname] = host_blade_network
        # Connect all the Virtual Node classes of all classes to the
        # host_blade_network
        for _, node_class in node_classes.items():
            host_blade_interface = {
                'delete': False,
                'cluster_network': netname,
                'addr_info': {
                    'ipv4': {
                        'family': 'AF_INET',
                        'mode': 'static',
                        'addresses': [
                            str(hosts.pop())
                            for i in range(
                                0, int(node_class.get('node_count', 0))
                            )
                        ],
                        'hostname_suffix': '-host-blade'
                    }
                }
            }
            node_class['network_interfaces'][netname] = host_blade_interface
        self.config['networks'] = networks
        self.config['node_classes'] = node_classes

    def __expand_node_classes(self, blade_config):
        """Expand the node class inheritance tree found in the
        provided blade_config data and replace the node classes found
        there with their expanded versions.

        """
        node_classes = self.__get_node_classes(blade_config)
        for key, node_class in node_classes.items():
            # Expand the inheritance tree for Virtual Node classes and put
            # the expanded result back into the configuration. That way,
            # when we write out the configuration we have the full
            # expansion there.
            if node_class.get('pure_base_class', False):
                # Skip inheritance and installation for pure base
                # classes since they have no parents, and they aren't
                # used for deployment.
                continue
            expanded_config = expand_inheritance(node_classes, key)
            expanded_config = self.__clean_deleted_interfaces(expanded_config)
            expanded_config = self.__clean_deleted_disks(expanded_config)
            node_classes[key] = expanded_config

    @staticmethod
    def __random_mac(prefix="52:54:00"):
        """Generate a MAC address using a specified prefix specified
        as a string containing colon separated hexadecimal octet
        values for the length of the desired prefix. By default use
        the KVM reserved prefix '52:54:00'.

        """
        try:
            prefix_octets = [
                int(octet, base=16) for octet in prefix.split(':')
            ]
        except Exception as err:
            raise ContextualError(
                "internal error: parsing MAC prefix '%s' failed - %s" % (
                    prefix, str(err)
                )
            ) from err
        if len(prefix_octets) > 6:
            raise ContextualError(
                "internal error: MAC address prefix '%s' has too "
                "many octets" % prefix
            )
        mac_binary = prefix_octets + [
            randint(0x00, 0xff) for i in range(0, 6 - len(prefix_octets))
        ]
        return ":".join(["%2.2x" % octet for octet in mac_binary])

    def __add_mac_addresses(self, node_class):
        """Compute MAC address for every Virtual Node interface and
        overlay an 'addr_info.layer_2' that has AF_PACKET as its
        address family, and a list of MAC addresses in it. If that
        block already exists, then just make sure there are enough MAC
        addresses in it, and supplement as needed.

        """
        node_count = int(node_class.get('node_count', 0))
        interfaces = node_class.get('network_interfaces', {})
        for key, interface in interfaces.items():
            layer_2 = interface.get(
                "layer_2",
                {
                    'family': 'AF_PACKET',
                    'addresses': [],
                }
            )
            existing_macs = layer_2.get('addresses', [])[0:node_count]
            existing_count = len(existing_macs)
            layer_2['addresses'] = existing_macs + [
                self.__random_mac()
                for i in range(0, node_count - existing_count)
            ]
            interface['addr_info'] = (
                interface['addr_info'] if 'addr_info' in interface else
                {}
            )
            interface['addr_info']['layer_2'] = layer_2
            interfaces[key] = interface

    def __set_node_mac_addresses(self, blade_config):
        """Compute and inject MAC addresses for every Virtual Node
        interface in all of the node classes.

        """
        node_classes = self.__get_node_classes(blade_config)
        for _, node_class in node_classes.items():
            self.__add_mac_addresses(node_class)

    def consolidate(self):
        return

    def prepare(self):
        self.provider_api = self.stack.get_provider_api()
        self.__add_host_blade_net()
        blade_config = self.config
        self.__expand_node_classes(blade_config)
        self.__set_node_mac_addresses(blade_config)
        networks = self.config.get('networks', {})
        blade_config['networks'] = {
            key: self.__add_endpoint_ips(network)
            for key, network in networks.items()
            if not network.get('delete', False)
        }
        self.prepared = True

    def validate(self):
        if not self.prepared:
            raise ContextualError(
                "cannot validate an unprepared cluster, call prepare() first"
            )
        info_msg("Validating vtds-cluster-mock")

    def deploy(self):
        if not self.prepared:
            raise ContextualError(
                "cannot deploy an unprepared cluster, call prepare() first"
            )
        info_msg("deploying vtds-cluster-mock")

    def remove(self):
        if not self.prepared:
            raise ContextualError(
                "cannot remove an unprepared cluster, call prepare() first"
            )
        info_msg("removing vtds-cluster-mock")

    def get_virtual_nodes(self):
        return VirtualNodes(self.common)

    def get_virtual_networks(self):
        return VirtualNetworks(self.common)
