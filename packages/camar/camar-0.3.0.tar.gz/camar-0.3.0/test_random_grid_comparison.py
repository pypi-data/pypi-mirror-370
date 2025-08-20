#!/usr/bin/env python3
"""
Test script to compare the original random_grid with the improved random_grid2.
"""

import jax
import jax.numpy as jnp
from src.camar.maps.random_grid import random_grid
from src.camar.maps.random_grid2 import random_grid2


def test_basic_functionality():
    """Test basic functionality of both implementations."""
    key = jax.random.key(42)

    # Test original implementation
    print("Testing original random_grid...")
    original_map = random_grid(
        num_rows=10,
        num_cols=10,
        num_agents=5,
        obstacle_density=0.1
    )

    key, landmarks, agents, goals, sizes = original_map.reset(key)
    print(f"Original - Agents: {agents.shape}, Goals: {goals.shape}, Landmarks: {landmarks.shape}")
    print(f"Original - Homogeneous agents: {original_map.homogeneous_agents}")
    print(f"Original - Homogeneous goals: {original_map.homogeneous_goals}")

    # Test improved implementation
    print("\nTesting improved random_grid2...")
    improved_map = random_grid2(
        num_rows=10,
        num_cols=10,
        num_agents=5,
        obstacle_density=0.1
    )

    key, landmarks, agents, goals, sizes = improved_map.reset(key)
    print(f"Improved - Agents: {agents.shape}, Goals: {goals.shape}, Landmarks: {landmarks.shape}")
    print(f"Improved - Homogeneous agents: {improved_map.homogeneous_agents}")
    print(f"Improved - Homogeneous goals: {improved_map.homogeneous_goals}")


def test_heterogeneous_configurations():
    """Test heterogeneous configurations."""
    key = jax.random.key(123)

    print("\n" + "="*50)
    print("Testing heterogeneous configurations...")

    # Test with heterogeneous agents
    map_hetero_agents = random_grid2(
        num_rows=8,
        num_cols=8,
        num_agents=3,
        agent_rad_range=(0.1, 0.3)
    )

    key, landmarks, agents, goals, sizes = map_hetero_agents.reset(key)
    print(f"Heterogeneous agents - Agent radii shape: {sizes.agent_rad.shape if hasattr(sizes, 'agent_rad') else 'None'}")
    print(f"Heterogeneous agents - Goal radii shape: {sizes.goal_rad.shape if hasattr(sizes, 'goal_rad') else 'None'}")

    # Test with proportional goals
    map_proportional = random_grid2(
        num_rows=8,
        num_cols=8,
        num_agents=3,
        agent_rad_range=(0.1, 0.3),
        goal_rad_range=None  # This triggers proportional goals
    )

    key, landmarks, agents, goals, sizes = map_proportional.reset(key)
    print(f"Proportional goals - Agent radii shape: {sizes.agent_rad.shape if hasattr(sizes, 'agent_rad') else 'None'}")
    print(f"Proportional goals - Goal radii shape: {sizes.goal_rad.shape if hasattr(sizes, 'goal_rad') else 'None'}")


def test_radius_configuration():
    """Test the radius configuration logic."""
    print("\n" + "="*50)
    print("Testing radius configuration logic...")

    # Test different configurations
    configs = [
        ("Default (homogeneous)", {}),
        ("Heterogeneous agents", {"agent_rad_range": (0.1, 0.3)}),
        ("Heterogeneous goals", {"goal_rad_range": (0.05, 0.15)}),
        ("Both heterogeneous", {"agent_rad_range": (0.1, 0.3), "goal_rad_range": (0.05, 0.15)}),
        ("Proportional goals", {"agent_rad_range": (0.1, 0.3), "goal_rad_range": None}),
    ]

    for name, config in configs:
        map_instance = random_grid2(num_rows=5, num_cols=5, num_agents=2, **config)
        print(f"{name}:")
        print(f"  - Agent type: {map_instance._radius_config.agent_type}")
        print(f"  - Goal type: {map_instance._radius_config.goal_type}")
        print(f"  - Homogeneous agents: {map_instance.homogeneous_agents}")
        print(f"  - Homogeneous goals: {map_instance.homogeneous_goals}")
        print(f"  - Proportional goals: {map_instance.proportional_goal_rad}")
        print()


if __name__ == "__main__":
    test_basic_functionality()
    test_heterogeneous_configurations()
    test_radius_configuration()