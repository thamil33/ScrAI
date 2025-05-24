# Simple test script
import logging

def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("SimpleTest")
    logger.info("Starting simple test...")
    
    try:
        from configurations.schemas.actor_schema import Actor, Goal, CognitiveCore
        logger.info("✅ Successfully imported real Pydantic schemas")
        
        # Test creating a model
        test_goal = Goal(description="Test goal", priority=1)
        logger.info(f"✅ Created Goal: {test_goal.description}")
        
        test_core = CognitiveCore(current_goals=[test_goal])
        logger.info(f"✅ Created CognitiveCore with {len(test_core.current_goals)} goals")
        
        test_actor = Actor(name="Test", description="Test actor", cognitive_core=test_core)
        logger.info(f"✅ Created Actor: {test_actor.name} (ID: {test_actor.id})")
        
        # Test serialization
        json_data = test_actor.model_dump_json()
        logger.info(f"✅ Serialized actor to JSON: {len(json_data)} characters")
        
        logger.info("🎉 All tests passed!")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
