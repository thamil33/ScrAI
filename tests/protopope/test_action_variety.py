#!/usr/bin/env python3
"""
Test script to demonstrate the variety of actions in the ActionManager system
by running multiple action cycles with real LLM calls.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("ActionVarietyTest")

# Load environment variables
load_dotenv()

# Import necessary modules
from configurations.scenarios.pope_vision_scenario import get_pope_leo_xiii_vision_scenario
from engine.llm_services.llm_provider import LLmClientInterface
from engine.actors.basic_runtime import ScrAIActor

def main():
    """
    Test the ActionManager with multiple action cycles to demonstrate variety.
    """
    logger.info("Starting Action Variety Test...")
    
    # Initialize LLM interface
    llm_provider = LLmClientInterface()
    logger.info(f"LLM Interface: {llm_provider.provider}, Model: {llm_provider.OPENROUTER_MODEL}")
    
    # Load scenario
    scenario = get_pope_leo_xiii_vision_scenario()
    pope_actor_data = scenario.initial_actors[0]
    
    # Create runtime actor
    pope_runtime = ScrAIActor(pope_actor_data, llm_provider)
    logger.info(f"Created ScrAIActor: {pope_runtime.pydantic_data.name}")
    logger.info(f"Available actions: {len(pope_runtime.get_available_actions())}")
    
    # Test multiple perception-action cycles
    perceptions = [
        "You hear a menacing voice: 'I can destroy your Church in 75 years!'",
        "A divine presence responds with calm authority: 'You may try, but my Church will endure.'",
        "The vision expands to show scenes of future trials and triumphs.",
        "You feel an overwhelming sense of divine mission and responsibility.",
        "The chapel around you seems to glow with supernatural light."
    ]
    
    for i, perception in enumerate(perceptions, 1):
        logger.info(f"\n=== Action Cycle {i} ===")
        
        # Show current status
        status = pope_runtime.get_current_status()
        logger.info(f"Current spiritual state: {status['current_state'].get('spiritual_state', 'unknown')}")
        logger.info(f"Current emotions: {status['emotions']}")
        logger.info(f"Recent memory: {status['recent_memory']}")
        
        # Perception
        logger.info(f"Perception: {perception}")
        pope_runtime.perceive(perception)
        
        # Action
        logger.info("Deciding and executing action...")
        result = pope_runtime.decide_and_act()
        
        action = result['action']
        outcome = result['outcome']
        
        logger.info(f"Action taken: {action['action_name']}")
        logger.info(f"Action parameters: {action.get('parameters', {})}")
        logger.info(f"Outcome: {outcome.result.value} - {outcome.message}")
        
        if outcome.state_changes:
            logger.info(f"State changes applied: {list(outcome.state_changes.keys())}")
        
        # Brief pause between cycles
        import time
        time.sleep(1)
    
    # Final status summary
    logger.info(f"\n=== Final Status Summary ===")
    final_status = pope_runtime.get_current_status()
    logger.info(f"Final spiritual state: {final_status['current_state'].get('spiritual_state', 'unknown')}")
    logger.info(f"Final emotions: {final_status['emotions']}")
    logger.info(f"Final memory: {final_status['recent_memory']}")
    logger.info(f"Additional state: {[(k,v) for k,v in final_status['current_state'].items() if k != 'spiritual_state']}")
    
    logger.info("Action Variety Test Complete!")

if __name__ == "__main__":
    main()
