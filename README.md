# Overview

This interface layer handles the communication among Magpie peers.


# Usage

## Peers

This interface allows the peers of the Magpie deployment to be aware of
each other. This interface layer will set the following states, as appropriate:

  * `{relation_name}.joined` A new peer in the Magpie service has
  joined. The Magpie charm should call `get_nodes()` to get
  a list of tuples with unit ids and IP addresses for peer members.

    * When a unit joins the set of peers, the interface ensures there
    is no `{relation_name}.departed` state set in the conversation.

    * A call to `dismiss_joined()` will remove the `joined` state in the
    peer conversation so this charm can react to subsequent peers joining.


  * `{relation_name}.departed` A peer in the Magpie service has
  departed. The Magpie charm should call `get_nodes()` to get
  a list of tuples with unit ids and IP addresses for remaining peer members.

    * When a unit leaves the set of peers, the interface ensures there
    is no `{relation_name}.joined` state set in the conversation.

    * A call to `dismiss_departed()` will remove the `departed` state in the
    peer conversation so this charm can react to subsequent peers departing.


For example, let's say that a peer is added to the Magpie service
deployment. The Magpie charm should handle the new peer like this:

```python
@when('magpie.joined')
def check_peers(magpie):
    nodes = magpie.get_nodes()
    # do stuff with nodes
```

# Contact Information

