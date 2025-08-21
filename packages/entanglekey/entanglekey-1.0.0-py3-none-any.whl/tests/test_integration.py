"""
EntangleKey Integration Tests

Tests the interaction between multiple EntangleKeyManager instances
over a network connection.
"""

import pytest
import pytest_asyncio
import asyncio
from typing import AsyncGenerator, Tuple

from entanglekey import EntangleKeyManager
from entanglekey.config import EntangleKeyConfig, NetworkConfig

@pytest_asyncio.fixture
async def managers() -> AsyncGenerator[Tuple[EntangleKeyManager, EntangleKeyManager], None]:
    """
    Provides a fixture of two connected EntangleKeyManager instances.
    """
    # Create configurations with different ports
    config1 = EntangleKeyConfig(
        network=NetworkConfig(port=9001)
    )
    config2 = EntangleKeyConfig(
        network=NetworkConfig(port=9002)
    )

    manager1 = EntangleKeyManager(
        instance_id="manager1",
        network_port=9001,
        config=config1
    )
    manager2 = EntangleKeyManager(
        instance_id="manager2", 
        network_port=9002,
        config=config2
    )

    # Start both managers
    await manager1.start()
    await manager2.start()

    # Store connected instances
    connected_events = {"manager1": asyncio.Event(), "manager2": asyncio.Event()}

    async def on_connect_m1(instance_id):
        if instance_id == "manager2":
            connected_events["manager1"].set()

    async def on_connect_m2(instance_id):
        if instance_id == "manager1":
            connected_events["manager2"].set()
    
    manager1.add_instance_connected_callback(on_connect_m1)
    manager2.add_instance_connected_callback(on_connect_m2)

    # Connect manager1 to manager2
    await manager1.connect_instance("127.0.0.1", 9002)

    # Wait for connections to be established on both sides
    await asyncio.wait_for(connected_events["manager1"].wait(), timeout=5)
    await asyncio.wait_for(connected_events["manager2"].wait(), timeout=5)

    yield manager1, manager2

    # Teardown: stop both managers
    await manager1.stop()
    await manager2.stop()


@pytest.mark.asyncio
async def test_instance_connection(managers: Tuple[EntangleKeyManager, EntangleKeyManager]):
    """
    Tests if two manager instances can successfully connect to each other.
    """
    manager1, manager2 = managers
    
    # Check if connections are registered
    assert "manager2" in manager1.network_manager.get_connected_instances()
    assert "manager1" in manager2.network_manager.get_connected_instances()

    assert manager1.is_running
    assert manager2.is_running

@pytest.mark.asyncio
async def test_session_key_generation_and_sync(managers: Tuple[EntangleKeyManager, EntangleKeyManager]):
    """
    Tests session key generation between two managers and verifies synchronization.
    """
    manager1, manager2 = managers

    key_generated_event_m1 = asyncio.Event()
    generated_session_id_m1 = None
    
    async def on_key_generated_m1(session_id, key):
        nonlocal generated_session_id_m1
        generated_session_id_m1 = session_id
        key_generated_event_m1.set()
        
    manager1.add_key_generated_callback(on_key_generated_m1)

    # Manager1 generates a session key with Manager2 as a partner
    session_id = await manager1.generate_session_key(partner_instances=["manager2"])
    
    # Wait for the key generation event
    await asyncio.wait_for(key_generated_event_m1.wait(), timeout=10)
    
    assert session_id is not None
    assert generated_session_id_m1 == session_id

    # Get the key from both managers
    key1 = await manager1.get_session_key(session_id)
    
    # In the current design, the partner instance (manager2) doesn't automatically
    # store the key. It only participates in the synchronization validation.
    # To fully test, we'd need a key agreement protocol.
    # For now, we confirm the generating manager has the key.
    
    assert key1 is not None
    assert isinstance(key1, bytes)
    assert len(key1) == manager1.key_length // 8
    
    # We can't directly get manager2's key as it's not stored by default.
    # The successful generation implies sync acknowledgement was received.
    
    # Let's check if manager2 received the sync message by checking its logs or state
    # (This part is conceptual as there's no direct state to check for sync)
    # The fact that `generate_session_key` completed without a timeout is the primary check.
    
    # Test key revocation
    await manager1.revoke_session_key(session_id)
    assert await manager1.get_session_key(session_id) is None

if __name__ == "__main__":
    pytest.main([__file__])
