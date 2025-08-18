import time, pytest
from eventflowsys import ThreadedServiceBus

def test_threaded_service_bus_basic():
    bus = ThreadedServiceBus()
    received = []

    def callback(msg_id, data):
        received.append((msg_id, data))

    bus.subscribe("group1", "serviceA", callback)
    msg_id = bus.publish("group1", "hello")
    time.sleep(0.1)
    assert received and received[0][1] == "hello"
    assert bus.pending_count() == 0

def test_threaded_service_bus_unsubscribe():
    bus = ThreadedServiceBus()
    received = []

    def callback(msg_id, data):
        received.append(data)

    bus.subscribe("group1", "serviceA", callback)
    bus.unsubscribe("group1", "serviceA")
    bus.publish("group1", "should not be received")
    time.sleep(0.1)
    assert not received

def test_threaded_service_bus_broadcast():
    bus = ThreadedServiceBus()
    received = []

    def cb1(msg_id, data):
        received.append(("cb1", data))

    def cb2(msg_id, data):
        received.append(("cb2", data))

    bus.subscribe("group1", "serviceA", cb1)
    bus.subscribe("group2", "serviceB", cb2)
    bus.publish("group1", "broadcasted", broadcast=True)
    time.sleep(0.1)
    assert ("cb1", "broadcasted") in received
    assert ("cb2", "broadcasted") in received

def test_threaded_service_bus_ttl_expiry():
    bus = ThreadedServiceBus()
    received = []

    def callback(msg_id, data):
        received.append(data)

    bus.subscribe("group1", "serviceA", callback)
    bus.publish("group1", "short-lived", ttl=0.01)
    time.sleep(0.05)
    assert bus.get_metrics()["expired"] >= 1

def test_threaded_service_bus_get_unread_services():
    bus = ThreadedServiceBus()
    received = []

    def callback(msg_id, data):
        received.append(data)

    bus.subscribe("group1", "serviceA", callback)
    msg_id = bus.publish("group1", "msg")
    time.sleep(0.1)
    assert bus.get_unread_services(msg_id) == set() # pyright: ignore[reportArgumentType]