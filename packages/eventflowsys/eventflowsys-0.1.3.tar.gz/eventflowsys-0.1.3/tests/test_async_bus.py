import asyncio, pytest

from eventflowsys import AsyncServiceBus



@pytest.mark.asyncio
async def test_async_service_bus_basic():
    bus = AsyncServiceBus()
    received = []

    async def callback(msg_id, data):
        received.append((msg_id, data))

    await bus.subscribe("group1", "serviceA", callback)
    msg_id = await bus.publish("group1", "hello")
    await asyncio.sleep(0.1)
    assert received and received[0][1] == "hello"
    assert await bus.pending_count() == 0

@pytest.mark.asyncio
async def test_async_service_bus_unsubscribe():
    bus = AsyncServiceBus()
    received = []

    async def callback(msg_id, data):
        received.append(data)

    await bus.subscribe("group1", "serviceA", callback)
    await bus.unsubscribe("group1", "serviceA")
    await bus.publish("group1", "should not be received")
    await asyncio.sleep(0.1)
    assert not received

@pytest.mark.asyncio
async def test_async_service_bus_broadcast():
    bus = AsyncServiceBus()
    received = []

    async def cb1(msg_id, data):
        received.append(("cb1", data))

    async def cb2(msg_id, data):
        received.append(("cb2", data))

    await bus.subscribe("group1", "serviceA", cb1)
    await bus.subscribe("group2", "serviceB", cb2)
    await bus.publish("group1", "broadcasted", broadcast=True)
    await asyncio.sleep(0.1)
    assert ("cb1", "broadcasted") in received
    assert ("cb2", "broadcasted") in received

@pytest.mark.asyncio
async def test_async_service_bus_ttl_expiry():
    bus = AsyncServiceBus()
    received = []

    async def callback(msg_id, data):
        received.append(data)

    await bus.subscribe("group1", "serviceA", callback)
    await bus.publish("group1", "short-lived", ttl=0.01)
    await asyncio.sleep(0.05)
    assert bus.get_metrics()["expired"] >= 1

@pytest.mark.asyncio
async def test_async_service_bus_get_unread_services():
    bus = AsyncServiceBus()
    received = []

    async def callback(msg_id, data):
        received.append(data)

    await bus.subscribe("group1", "serviceA", callback)
    msg_id = await bus.publish("group1", "msg")
    await asyncio.sleep(0.1)
    assert await bus.get_unread_services(msg_id) == set() # pyright: ignore[reportArgumentType]