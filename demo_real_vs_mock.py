# File: demo_real_vs_mock.py
# Demonstration script showing the transition from mock to real Pydantic models and LLM usage

import logging
from typing import Dict, Any

# Real imports
from configurations.schemas.actor_schema import Actor, Goal, CognitiveCore
from engine.llm_services.llm_interface import OpenRouterLLM
from engine.actors.basic_runtime import RuntimeActor

def setup_logging():
    """Sets up basic logging for the demo."""
    logging.basicConfig(level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

def demo_real_pydantic_models():
    """Demonstrates the usage of real Pydantic models."""
    logger = logging.getLogger("RealPydanticDemo")
    
    logger.info("=== REAL PYDANTIC MODEL DEMONSTRATION ===")
    
    # Create a real Pydantic model
    test_goal = Goal(
        description="Test understanding of Pydantic validation",
        priority=5
    )
    
    test_cognitive_core = CognitiveCore(
        current_goals=[test_goal],
        emotions={"curiosity": 0.8, "confidence": 0.6},
        llm_provider_settings={"model": "real_model", "temperature": 0.7}
    )
    
    test_actor = Actor(
        name="Test Actor",
        description="An actor for demonstrating real Pydantic usage",
        cognitive_core=test_cognitive_core,
        state={"status": "testing"}
    )
    
    # Show Pydantic features
    logger.info(f"✅ Actor created with ID: {test_actor.id}")
    logger.info(f"✅ Actor has model_dump method: {hasattr(test_actor, 'model_dump')}")
    logger.info(f"✅ Actor can be serialized: {len(test_actor.model_dump_json())} characters")
    
    # Show validation
    try:
        test_actor.name = 123  # This should trigger validation
    except Exception as e:
        logger.info(f"✅ Pydantic validation caught invalid data: {type(e).__name__}")
        test_actor.name = "Test Actor"  # Reset
    
    # Show field access
    logger.info(f"✅ Cognitive core emotions: {test_actor.cognitive_core.emotions}")
    logger.info(f"✅ Number of goals: {len(test_actor.cognitive_core.current_goals)}")
    
    return test_actor

def demo_llm_integration(test_actor):
    """Demonstrates real LLM integration."""
    logger = logging.getLogger("RealLLMDemo")
    
    logger.info("=== REAL LLM INTEGRATION DEMONSTRATION ===")
    
    try:
        # Initialize real LLM interface
        llm_interface = OpenRouterLLM()
        logger.info(f"✅ LLM Interface initialized: {llm_interface.provider}")
        
        # Create runtime actor
        runtime_actor = RuntimeActor(test_actor, llm_interface)
        logger.info(f"✅ RuntimeActor created for: {runtime_actor.pydantic_data.name}")
        
        # Test perception and action
        runtime_actor.perceive("This is a test perception for demonstrating real LLM usage.")
        
        logger.info("📡 Making real LLM API call...")
        action = runtime_actor.decide_and_act()
        
        if "error" not in action.get("action_name", "").lower():
            logger.info(f"✅ LLM successfully responded: {action}")
            return True
        else:
            logger.warning(f"⚠️ LLM error response: {action}")
            return False
            
    except Exception as e:
        logger.error(f"❌ LLM integration failed: {e}")
        return False

def main():
    """Main demonstration function."""
    try:
        setup_logging()
        logger = logging.getLogger("DemoMain")
        
        logger.info("🚀 Starting Real vs Mock Demonstration")
        
        # Demonstrate real Pydantic models
        test_actor = demo_real_pydantic_models()
        
        # Demonstrate real LLM integration
        llm_success = demo_llm_integration(test_actor)
        
        # Summary
        logger.info("=== DEMONSTRATION SUMMARY ===")
        logger.info("✅ Real Pydantic models: Working")
        logger.info(f"{'✅' if llm_success else '❌'} Real LLM integration: {'Working' if llm_success else 'Failed'}")
        
        if llm_success:
            logger.info("🎉 SUCCESS: ScrAI prototype has successfully transitioned from mock to real data!")
            logger.info("🔄 Next steps: Expand action repertoire, add persistence, integrate Agno framework")
        else:
            logger.info("📋 Note: LLM integration requires proper .env configuration")
            logger.info("📋 Check OPENROUTER_API_KEY and or_model settings")
            
    except Exception as e:
        print(f"ERROR in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
