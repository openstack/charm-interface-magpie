# Overview

This interface layer handles the communication between the Apache Zookeeper unit members.


# Usage

## Peers

This interface allows the peers of the Zookeeper deployment to become aware of each other.
This interface layer will set the following states, as appropriate:

  * `{relation_name}.increased` A new member/unit in the Zookeeper deployment/service is present.
    The Zookeeper charm has to make a call to `get_nodes()` in order get the list of the available nodes.
    `get_nodes()` will remove the `{relation_name}.increased` so that the Zookeeper layer keeps monitoring that state for future notifications. 
    
  * `{relation_name}.decreased` A member/unit in the Zookeeper deployment/service has departed.
    The Zookeeper charm has to make a call to `get_departed()` in order get the IP of the departed node.
    `get_departed()` will remove the `{relation_name}.decreased` so that the Zookeeper layer keeps monitoring that state for future notifications. 
    
    
For example, let's say that a new unit is added to the Zookeeper service deployment. 
The Zookeeper layer should handle the state of `{relation_name}.increased` like this:

```python
@when('zookeeper.installed', 'quorum.increased')
def quorum_incresed(quorum):
    nodes = quorum.get_nodes()
    ...
```


# Contact Information

- <bigdata@lists.ubuntu.com>
