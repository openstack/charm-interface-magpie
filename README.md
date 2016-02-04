# Overview

This interface layer handles the communication between the Apache Zookeeper unit members.


# Usage

## Peers

This interface allows the peers of the Zookeeper deployment to become aware of each other.
This interface layer will set the following states, as appropriate:

  * `{relation_name}.relate` A new member/unit in the Zookeeper service is present.
    The Zookeeper charm has to make a call to `get_nodes()` in order get the list of tuples with the unit ids and their IP.
    When a unit joins the set of peers, the interface makes sure that there is no `{relation_name}.departing` state set in the conversation. 
    
  * `{relation_name}.departing` A member/unit in the Zookeeper service has departed.
    The Zookeeper charm has to make a call to `get_nodes()` in order get the IP of the departing nodes.
    A call to `dismiss()` will clean the states in the conversation between the peers and dismiss the relation. 
    
    
For example, let's say that a new unit is added to the Zookeeper service deployment. 
The Zookeeper layer should handle the state of `{relation_name}.relate` like this:

```python
@when('zookeeper.installed', 'instance.related')
def quorum_incresed(instances):
    nodes = instances.get_nodes()
    zk = Zookeeper(dist_config())
    zk.increase_quorum(nodes)
```

In similar fashion, when a peer departs:
```
@when('zookeeper.installed', 'instance.departing')
def quorum_decreased(instances):
    nodes = instances.get_nodes()
    instances.dismiss()
    zk = Zookeeper(dist_config())
    zk.decrease_quorum(nodes)
```


# Contact Information

- <bigdata@lists.ubuntu.com>
