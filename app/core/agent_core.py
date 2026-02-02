import uuid
from typing import Dict, Any
from app.core.schema import Intent, ActionStep, ExecutionResult
from app.core.llm_client import GeminiLLMClient
from app.core.executor import ActionExecutor

class DeskMateAgent:
    """Main AI agent that coordinates intent parsing and execution"""
    
    def __init__(self):
        try:
            self.llm_client = GeminiLLMClient()
            print("✅ Using Gemini LLM for intent parsing")
        except Exception as e:
            from app.core.llm_client import RobustMockLLMClient
            self.llm_client = RobustMockLLMClient()
            print(f"⚠️ Using Mock LLM (Gemini not available): {e}")
        
        self.executor = ActionExecutor()
    
    def process_command(self, command: str) -> Dict[str, Any]:
        """Process a natural language command and return results"""
        import time
        start_time = time.time()
        
        # Parse intent
        intent = self.llm_client.parse_intent(command)
        
        # Execute steps
        results = []
        overall_success = True
        friendly_responses = []
        
        for step_dict in intent.steps:
            step = ActionStep(**step_dict)
            result = self.executor.execute_step(step)
            results.append({
                "action": step.action,
                "params": step.params,
                "result": result.dict()
            })
            
            # Collect friendly messages
            if result.output and isinstance(result.output, dict):
                msg = result.output.get("friendly_message") or result.output.get("message")
                if msg:
                    friendly_responses.append(msg)
            
            if not result.success:
                overall_success = False
                break
        
        execution_time = round(time.time() - start_time, 2)
        
        # Construct final friendly response
        if friendly_responses:
            final_response = "\n".join(friendly_responses)
        elif overall_success:
            final_response = f"✅ Command executed successfully."
        else:
            final_response = "❌ Command failed to execute completely."
            
        final_response += f"\n\n(Executed in {execution_time}s)"
        
        return {
            "command": command,
            "intent": intent.dict(),
            "results": results,
            "success": overall_success,
            "requires_confirmation": intent.confirmation_required,
            "job_id": str(uuid.uuid4()),
            "friendly_response": final_response,
            "execution_time": execution_time
        }