# Overview

This interface layer handles the communication among Apache Zookeeper peers.


# Usage

## Peers

This interface allows the peers of the Zookeeper deployment to be aware of
each other. This interface layer will set the following states, as appropriate:

  * `{relation_name}.joined` A new peer in the Zookeeper service has
  joined. The Zookeeper charm should call `get_nodes()` to get
  a list of tuples with unit ids and IP addresses for quorum members.

    * When a unit joins the set of peers, the interface ensures there
    is no `{relation_name}.departed` state set in the conversation.

    * A call to `dismiss_joined()` will remove the `joined` state in the
    peer conversation so this charm can react to subsequent peers joining.


  * `{relation_name}.departed` A peer in the Zookeeper service has
  departed. The Zookeeper charm should call `get_nodes()` to get
  a list of tuples with unit ids and IP addresses for remaining quorum members.

    * When a unit leaves the set of peers, the interface ensures there
    is no `{relation_name}.joined` state set in the conversation.

    * A call to `dismiss_departed()` will remove the `departed` state in the
    peer conversation so this charm can react to subsequent peers departing.


For example, let's say that a peer is added to the Zookeeper service
deployment. The Zookeeper charm should handle the new peer like this:

```python
@when('zookeeper.installed', 'zkpeer.joined')
def quorum_add(zkpeer):
    nodes = zkpeer.get_nodes()
    increase_quorum(nodes)
    zkpeer.dismiss_joined()
```

Similarly, when a peer departs:

```python
@when('zookeeper.installed', 'zkpeer.departed')
def quorum_remove(zkpeer):
    nodes = zkpeer.get_nodes()
    decrease_quorum(nodes)
    zkpeer.dismiss_departed()
```


# Contact Information

- <bigdata@lists.ubuntu.com>
