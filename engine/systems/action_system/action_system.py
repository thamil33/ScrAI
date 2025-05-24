# File: scrai/engine/systems/action_system.py

"""
Basic Action System for ScrAI Prototype

This module provides:
1. ActionManager - Validates and executes actions chosen by actors
2. Action validation logic
3. Action effects on actor state and environment
4. Extensible action registry system
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
from enum import Enum

# Import Pydantic schemas
from configurations.schemas.actor_schema import Actor as ActorData
from configurations.schemas.event_schema import Event

class ActionResult(Enum):
    """Outcome of action execution"""
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"
    INVALID = "invalid"

@dataclass
class ActionOutcome:
    """Result of executing an action"""
    result: ActionResult
    message: str
    state_changes: Dict[str, Any] = None
    events_generated: List[Event] = None
    
    def __post_init__(self):
        if self.state_changes is None:
            self.state_changes = {}
        if self.events_generated is None:
            self.events_generated = []

class ActionManager:
    """
    Manages the validation and execution of actor actions.
    
    This is a basic implementation that will be expanded as the system grows.
    Future versions will integrate with WorldStateManager, EventSystem, etc.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._action_handlers: Dict[str, Callable] = {}
        self._register_default_actions()
    
    def _register_default_actions(self):
        """Register the default set of actions that actors can perform"""
        self._action_handlers.update({
            # Spiritual/Religious Actions
            "pray": self._handle_pray,
            "compose_prayer": self._handle_compose_prayer,
            "record_vision": self._handle_record_vision,
            "bless": self._handle_bless,
            "contemplate": self._handle_contemplate,
            
            # Communication Actions
            "speak": self._handle_speak,
            "whisper": self._handle_whisper,
            "shout": self._handle_shout,
            "write": self._handle_write,
            
            # Observation/Perception Actions
            "observe_surroundings": self._handle_observe_surroundings,
            "listen_carefully": self._handle_listen_carefully,
            "examine": self._handle_examine,
            "search": self._handle_search,
            
            # Emotional Actions
            "show_emotion_fear": self._handle_show_emotion,
            "show_emotion_awe": self._handle_show_emotion,
            "show_emotion_determination": self._handle_show_emotion,
            "show_emotion_sadness": self._handle_show_emotion,
            "show_emotion_joy": self._handle_show_emotion,
            "show_emotion_anger": self._handle_show_emotion,
            
            # Movement Actions
            "move_to": self._handle_move_to,
            "stand": self._handle_stand,
            "sit": self._handle_sit,
            "kneel": self._handle_kneel,
            "lie_down": self._handle_lie_down,
            
            # Interaction Actions
            "use_item": self._handle_use_item,
            "take": self._handle_take,
            "give": self._handle_give,
            "touch": self._handle_touch,
            
            # Planning/Mental Actions
            "think": self._handle_think,
            "decide": self._handle_decide,
            "plan": self._handle_plan,
            "remember": self._handle_remember,
            
            # System Actions
            "wait": self._handle_wait,
            "rest": self._handle_rest,
        })
    
    def register_action(self, action_name: str, handler: Callable):
        """Register a custom action handler"""
        self._action_handlers[action_name] = handler
        self.logger.info(f"Registered custom action: {action_name}")
    
    def get_available_actions(self) -> List[str]:
        """Return list of all available action names"""
        return list(self._action_handlers.keys())
    
    def validate_action(self, action: Dict[str, Any], actor: ActorData) -> bool:
        """
        Validate if an action can be performed by the given actor.
        
        Args:
            action: The action dictionary from LLM (action_name, parameters)
            actor: The actor attempting the action
            
        Returns:
            True if action is valid, False otherwise
        """
        action_name = action.get("action_name", "").lower()
        
        # Check if action exists
        if action_name not in self._action_handlers:
            self.logger.warning(f"Unknown action: {action_name}")
            return False
        
        # Basic validation - can be expanded with more sophisticated rules
        parameters = action.get("parameters", {})
        
        # Validate action-specific requirements
        if action_name in ["move_to"] and "location" not in parameters:
            self.logger.warning(f"Action {action_name} requires 'location' parameter")
            return False
        
        if action_name in ["speak", "whisper", "shout"] and "message" not in parameters:
            self.logger.warning(f"Action {action_name} requires 'message' parameter")
            return False
        
        if action_name in ["examine", "use_item", "take", "give", "touch"] and "target" not in parameters:
            self.logger.warning(f"Action {action_name} requires 'target' parameter")
            return False
        
        return True
    
    def execute_action(self, action: Dict[str, Any], actor: ActorData) -> ActionOutcome:
        """
        Execute the given action for the specified actor.
        
        Args:
            action: The action dictionary from LLM
            actor: The actor performing the action
            
        Returns:
            ActionOutcome with results and any state changes
        """
        self.logger.info(f"Executing action for {actor.name}: {action}")
        
        action_name = action.get("action_name", "").lower()
        parameters = action.get("parameters", {})
        
        # Validate action first
        if not self.validate_action(action, actor):
            return ActionOutcome(
                result=ActionResult.INVALID,
                message=f"Action '{action_name}' is invalid or missing required parameters"
            )
        
        # Execute the action
        try:
            handler = self._action_handlers[action_name]
            return handler(actor, parameters)
        except Exception as e:
            self.logger.error(f"Error executing action {action_name}: {e}")
            return ActionOutcome(
                result=ActionResult.FAILED,
                message=f"Action failed due to error: {str(e)}"
            )
    
    # Action Handler Methods
    # These methods define the actual effects of each action
    
    def _handle_pray(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        """Handle prayer action - increases spiritual state and may reduce fear"""
        intensity = params.get("intensity", "medium")
        duration = params.get("duration", "short")
        
        state_changes = {}
        
        # Affect spiritual state
        current_spiritual = actor.state.get("spiritual_state", "neutral")
        if current_spiritual == "in_vision":
            state_changes["spiritual_state"] = "praying_during_vision"
        else:
            state_changes["spiritual_state"] = "praying"
        
        # Emotional effects
        emotion_changes = {}
        if "fear" in actor.cognitive_core.emotions:
            reduction = 0.1 if intensity == "low" else 0.2 if intensity == "medium" else 0.3
            emotion_changes["fear"] = max(0, actor.cognitive_core.emotions["fear"] - reduction)
        
        if "determination" in actor.cognitive_core.emotions:
            increase = 0.1 if intensity == "low" else 0.15 if intensity == "medium" else 0.2
            emotion_changes["determination"] = min(1.0, actor.cognitive_core.emotions["determination"] + increase)
        
        state_changes["emotion_changes"] = emotion_changes
        
        # Add to memory
        memory_entry = f"Prayed with {intensity} intensity for {duration} duration"
        if hasattr(actor.cognitive_core, 'short_term_memory'):
            actor.cognitive_core.short_term_memory.append(memory_entry)
        
        return ActionOutcome(
            result=ActionResult.SUCCESS,
            message=f"{actor.name} prays with {intensity} intensity",
            state_changes=state_changes
        )
    
    def _handle_compose_prayer(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        """Handle composing a prayer"""
        topic = params.get("topic", "general guidance")
        style = params.get("style", "formal")
        
        memory_entry = f"Composed a {style} prayer about {topic}"
        if hasattr(actor.cognitive_core, 'short_term_memory'):
            actor.cognitive_core.short_term_memory.append(memory_entry)
        
        return ActionOutcome(
            result=ActionResult.SUCCESS,
            message=f"{actor.name} composes a {style} prayer about {topic}",
            state_changes={"last_prayer_topic": topic}
        )
    def _handle_record_vision(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        """Handle recording details of a vision"""
        detail = params.get("detail", "general impression")
        method = params.get("method", "mental note")
        
        memory_entry = f"Recorded vision detail: {detail} (via {method})"
        if hasattr(actor.cognitive_core, 'short_term_memory'):
            actor.cognitive_core.short_term_memory.append(memory_entry)
        
        # Initialize state_changes properly
        state_changes = {}
        if "vision_records" not in actor.state:
            state_changes["vision_records"] = [detail]
        else:
            existing_records = actor.state.get("vision_records", [])
            state_changes["vision_records"] = existing_records + [detail]
        
        return ActionOutcome(
            result=ActionResult.SUCCESS,
            message=f"{actor.name} records vision detail: {detail}",
            state_changes=state_changes
        )
    
    def _handle_speak(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        """Handle speaking action"""
        message = params.get("message", "...")
        tone = params.get("tone", "normal")
        target = params.get("target", "general")
        
        memory_entry = f"Spoke with {tone} tone: '{message}'"
        if hasattr(actor.cognitive_core, 'short_term_memory'):
            actor.cognitive_core.short_term_memory.append(memory_entry)
        
        return ActionOutcome(
            result=ActionResult.SUCCESS,
            message=f"{actor.name} speaks ({tone}): '{message}'",
            state_changes={"last_spoken": message}
        )
    
    def _handle_observe_surroundings(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        """Handle observing surroundings"""
        focus = params.get("focus", "general")
        detail_level = params.get("detail_level", "normal")
        
        # This would normally interact with the environment system
        # For now, we'll simulate based on current state
        observations = []
        current_location = actor.state.get("current_location_id", "unknown")
        
        if "chapel" in str(current_location).lower():
            observations = [
                "Dim candlelight flickers on stone walls",
                "Religious iconography adorns the walls", 
                "A sense of ancient sanctity pervades the space",
                "Shadows dance in the corners"
            ]
        else:
            observations = [
                "The immediate surroundings are unclear",
                "The environment seems spiritually charged"
            ]
        
        if focus != "general":
            observations.append(f"Focusing particularly on: {focus}")
        
        memory_entry = f"Observed surroundings with {detail_level} attention"
        if hasattr(actor.cognitive_core, 'short_term_memory'):
            actor.cognitive_core.short_term_memory.append(memory_entry)
            actor.cognitive_core.short_term_memory.extend(observations[:2])  # Add some observations to memory
        
        return ActionOutcome(
            result=ActionResult.SUCCESS,
            message=f"{actor.name} observes surroundings. Sees: {'; '.join(observations[:2])}",
            state_changes={"recent_observations": observations}
        )
    
    def _handle_show_emotion(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        """Handle displaying emotions"""
        action_name = params.get("original_action", "show_emotion")
        emotion_type = action_name.replace("show_emotion_", "") if "show_emotion_" in action_name else "neutral"
        intensity = params.get("intensity", "medium")
        
        # Update emotional state
        emotion_changes = {}
        intensity_value = 0.3 if intensity == "low" else 0.5 if intensity == "medium" else 0.8
        
        if emotion_type in actor.cognitive_core.emotions:
            emotion_changes[emotion_type] = min(1.0, actor.cognitive_core.emotions[emotion_type] + 0.1)
        else:
            emotion_changes[emotion_type] = intensity_value
        
        memory_entry = f"Expressed {emotion_type} with {intensity} intensity"
        if hasattr(actor.cognitive_core, 'short_term_memory'):
            actor.cognitive_core.short_term_memory.append(memory_entry)
        
        return ActionOutcome(
            result=ActionResult.SUCCESS,
            message=f"{actor.name} shows {emotion_type} ({intensity} intensity)",
            state_changes={"emotion_changes": emotion_changes}
        )
    
    def _handle_think(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        """Handle thinking/contemplation action"""
        topic = params.get("topic", "current situation")
        depth = params.get("depth", "surface")
        
        memory_entry = f"Contemplated {topic} with {depth} depth"
        if hasattr(actor.cognitive_core, 'short_term_memory'):
            actor.cognitive_core.short_term_memory.append(memory_entry)
        
        return ActionOutcome(
            result=ActionResult.SUCCESS,
            message=f"{actor.name} thinks deeply about {topic}",
            state_changes={"last_thought_topic": topic}
        )
    
    def _handle_wait(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        """Handle waiting/resting action"""
        duration = params.get("duration", "moment")
        reason = params.get("reason", "to gather thoughts")
        
        memory_entry = f"Waited for a {duration} {reason}"
        if hasattr(actor.cognitive_core, 'short_term_memory'):
            actor.cognitive_core.short_term_memory.append(memory_entry)
        
        return ActionOutcome(
            result=ActionResult.SUCCESS,
            message=f"{actor.name} waits for a {duration} {reason}",
            state_changes={}
        )
    
    # Placeholder implementations for other actions
    def _handle_bless(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        target = params.get("target", "general")
        return ActionOutcome(ActionResult.SUCCESS, f"{actor.name} offers a blessing to {target}")
    
    def _handle_contemplate(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        subject = params.get("subject", "divine mysteries")
        return ActionOutcome(ActionResult.SUCCESS, f"{actor.name} contemplates {subject}")
    
    def _handle_whisper(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        message = params.get("message", "...")
        return ActionOutcome(ActionResult.SUCCESS, f"{actor.name} whispers: '{message}'")
    
    def _handle_shout(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        message = params.get("message", "...")
        return ActionOutcome(ActionResult.SUCCESS, f"{actor.name} shouts: '{message}'")
    
    def _handle_write(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        content = params.get("content", "notes")
        return ActionOutcome(ActionResult.SUCCESS, f"{actor.name} writes: {content}")
    
    def _handle_listen_carefully(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        return ActionOutcome(ActionResult.SUCCESS, f"{actor.name} listens intently")
    
    def _handle_examine(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        target = params.get("target", "unknown")
        return ActionOutcome(ActionResult.SUCCESS, f"{actor.name} examines {target}")
    
    def _handle_search(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        target = params.get("target", "something")
        return ActionOutcome(ActionResult.SUCCESS, f"{actor.name} searches for {target}")
    
    def _handle_move_to(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        location = params.get("location", "unknown")
        return ActionOutcome(ActionResult.SUCCESS, f"{actor.name} moves to {location}")
    
    def _handle_stand(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        return ActionOutcome(ActionResult.SUCCESS, f"{actor.name} stands up", {"posture": "standing"})
    
    def _handle_sit(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        return ActionOutcome(ActionResult.SUCCESS, f"{actor.name} sits down", {"posture": "sitting"})
    
    def _handle_kneel(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        return ActionOutcome(ActionResult.SUCCESS, f"{actor.name} kneels", {"posture": "kneeling"})
    
    def _handle_lie_down(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        return ActionOutcome(ActionResult.SUCCESS, f"{actor.name} lies down", {"posture": "lying"})
    
    def _handle_use_item(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        target = params.get("target", "unknown item")
        return ActionOutcome(ActionResult.SUCCESS, f"{actor.name} uses {target}")
    
    def _handle_take(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        target = params.get("target", "unknown item")
        return ActionOutcome(ActionResult.SUCCESS, f"{actor.name} takes {target}")
    
    def _handle_give(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        target = params.get("target", "someone")
        item = params.get("item", "something")
        return ActionOutcome(ActionResult.SUCCESS, f"{actor.name} gives {item} to {target}")
    
    def _handle_touch(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        target = params.get("target", "unknown")
        return ActionOutcome(ActionResult.SUCCESS, f"{actor.name} touches {target}")
    
    def _handle_decide(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        decision = params.get("decision", "course of action")
        return ActionOutcome(ActionResult.SUCCESS, f"{actor.name} decides on {decision}")
    
    def _handle_plan(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        plan = params.get("plan", "future actions")
        return ActionOutcome(ActionResult.SUCCESS, f"{actor.name} plans {plan}")
    
    def _handle_remember(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        memory = params.get("memory", "past events")
        return ActionOutcome(ActionResult.SUCCESS, f"{actor.name} remembers {memory}")
    
    def _handle_rest(self, actor: ActorData, params: Dict[str, Any]) -> ActionOutcome:
        return ActionOutcome(ActionResult.SUCCESS, f"{actor.name} rests", {"energy": "restored"})


# Example usage and testing
if __name__ == "__main__":
    # This would be used by the simulation engine
    action_manager = ActionManager()
    
    print(f"Available actions: {len(action_manager.get_available_actions())}")
    print("Sample actions:", action_manager.get_available_actions()[:10])
