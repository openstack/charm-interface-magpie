# Overview

This interface layer handles the communication between the Flume Syslog and the rsyslog-forwarder service.


# Usage

## Provides

Charms providing this interface are able to recieve/consume system logs.

This interface layer will set the following states, as appropriate:

  * `{relation_name}.available`   The relation to a syslog producer has been established.
    If you are providing a service, you can use the following methods to pass the port of the service to the
    other end of the relation:
      * `send_port(port)`

For example, let's say that a charm recieves a connection from a syslog producer. 
The charm providing the log ingestion service should use this interface in the following way:

```python
@when('syslog.available')
@when_not('forwarding.ready')
def syslog_forward_connected(syslog):
    syslog.send_port(hookenv.config()['source_port'])
    set_state('forwarding.ready')
```


## Requires

This part of the relation has not been implemented yet.

# Contact Information

- <bigdata@lists.ubuntu.com>
