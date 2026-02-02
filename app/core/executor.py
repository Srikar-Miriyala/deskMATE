from typing import Dict, Any, List
from app.core.schema import ActionStep, ExecutionResult
from app.plugins.file_reader import FileReaderPlugin
from app.plugins.email_generator import EmailGeneratorPlugin
from app.plugins.shell_runner import ShellRunnerPlugin
from app.plugins.system_control import SystemControlPlugin

class ActionExecutor:
    """Executes action steps from the plan"""
    
    def __init__(self):
        self.file_reader = FileReaderPlugin()
        self.email_generator = EmailGeneratorPlugin()
        self.shell_runner = ShellRunnerPlugin()
        self.system_control = SystemControlPlugin()
    
    def execute_step(self, step: ActionStep) -> ExecutionResult:
        """Execute a single action step"""
        action = step.action
        params = step.params
        
        try:
            # Map AI-generated actions to our existing actions
            if action in ["respond_to_greeting", "greet_user", "answer_greeting"]:
                result = self._answer_question(params.get("question", "hello"))
            elif action == "read_file":
                result = self.file_reader.read_file(params.get("file_path", ""))
            elif action == "summarize":
                text = params.get("text", "")
                style = params.get("style", "short")
                result = self.file_reader.summarize_text(text, style)
            elif action == "generate_email":
                result = self.email_generator.generate_email(
                    params.get("subject", ""),
                    params.get("recipient", ""),
                    params.get("body", "")
                )
            elif action == "run_shell":
                result = self.shell_runner.run_shell_command(params.get("command", ""))
            elif action == "answer_question":
                result = self._answer_question(params.get("question", ""))
            elif action == "search_files":
                result = self._search_files(params.get("query", ""), params.get("directory", "."))
            elif action == "open_url":
                result = self._open_url(params.get("url", ""))
            elif action == "open_app":
                result = self._open_app(params.get("app_name", ""))
            elif action == "open_explorer":
                result = self._open_explorer(params.get("path", "."))
            elif action == "create_file":
                result = self._create_file(params.get("path", ""), params.get("content", ""))
            elif action == "create_folder":
                result = self._create_folder(params.get("path", ""))
            elif action == "open_terminal":
                result = self._open_terminal(params.get("path", None))
            elif action == "get_system_info":
                result = self._get_system_info()
            elif action == "get_time":
                result = self._get_time()
            else:
                # If we get an unknown action, treat it as a question
                print(f"⚠️ Unknown action '{action}', treating as question")
                question = params.get("question", f"Action: {action}")
                result = self._answer_question(question)
            
            return ExecutionResult(
                success=result.get("success", False),
                output=result,
                error=result.get("error")
            )
            
        except Exception as e:
            return ExecutionResult(
                success=False,
                output=None,
                error=f"Error executing {action}: {str(e)}"
            )
    
    def _open_url(self, url: str) -> dict:
        """Open a URL using SystemControlPlugin"""
        result = self.system_control.open_url(url)
        
        # Add friendly message
        if result["success"]:
            domain = url.replace('https://', '').replace('http://', '').split('/')[0]
            friendly_name = domain.replace('www.', '').split('.')[0].title()
            result["message"] = f"🌐 {friendly_name} is now opened in your browser!"
            result["friendly_message"] = f"✅ {friendly_name} is now opened!"
            result["action"] = "opened_browser"
        else:
            result["friendly_message"] = f"❌ Sorry, I couldn't open {url}"
            
        return result
    
    def _open_app(self, app_name: str) -> dict:
        """Open an application using SystemControlPlugin"""
        result = self.system_control.open_application(app_name)
        
        if result["success"]:
            result["message"] = f"🚀 {app_name} is now launched!"
            result["friendly_message"] = f"✅ {app_name} is now opened!"
            result["action"] = "launched_app"
        else:
            result["friendly_message"] = f"❌ Could not open {app_name}"
            
        return result
    
    def _open_explorer(self, path: str) -> dict:
        """Open file explorer using SystemControlPlugin"""
        result = self.system_control.open_file_explorer(path)
        
        if result["success"]:
            import os
            folder_name = os.path.basename(os.path.abspath(path)) if path else "Home"
            result["message"] = f"📁 File Explorer opened at: {folder_name}"
            result["friendly_message"] = f"✅ File Explorer is now opened at {folder_name}!"
            result["action"] = "opened_explorer"
        else:
            result["friendly_message"] = f"❌ Sorry, I couldn't open File Explorer"
            
        return result

    def _create_file(self, path: str, content: str) -> dict:
        """Create a file using SystemControlPlugin"""
        result = self.system_control.create_file(path, content)
        if result["success"]:
            import os
            filename = os.path.basename(path) if path else "file"
            result["friendly_message"] = f"✅ File created: {filename}"
        else:
            result["friendly_message"] = f"❌ Failed to create file"
        return result

    def _create_folder(self, path: str) -> dict:
        """Create a folder using SystemControlPlugin"""
        result = self.system_control.create_folder(path)
        if result["success"]:
            import os
            foldername = os.path.basename(path) if path else "folder"
            result["friendly_message"] = f"✅ Folder created: {foldername}"
        else:
            result["friendly_message"] = f"❌ Failed to create folder"
        return result

    def _open_terminal(self, path: str) -> dict:
        """Open terminal using SystemControlPlugin"""
        result = self.system_control.open_terminal(path)
        if result["success"]:
            result["friendly_message"] = "✅ Terminal opened"
        else:
            result["friendly_message"] = "❌ Failed to open terminal"
        return result

    def _get_system_info(self) -> dict:
        """Get system info"""
        result = self.system_control.get_system_info()
        if result["success"]:
            info = result["output"]
            formatted = f"💻 System: {info['system']} ({info['architecture']})\n⚙️ Processor: {info['machine']}\n🐍 Python: {info['python_version']}"
            result["friendly_message"] = formatted
        else:
            result["friendly_message"] = "❌ Failed to get system info"
        return result

    def _get_time(self) -> dict:
        """Get current time"""
        result = self.system_control.get_time()
        if result["success"]:
            result["friendly_message"] = f"🕒 Current Time: {result['output']}"
        else:
            result["friendly_message"] = "❌ Failed to get time"
        return result
    
    def _answer_question(self, question: str) -> dict:
        """Use Gemini AI to generate dynamic, conversational responses"""
        try:
            # Try to use Gemini for real AI responses
            return self._generate_ai_response(question)
        except Exception as e:
            print(f"AI response generation failed: {e}, using fallback")
            return self._fallback_response(question)
    
    def _generate_ai_response(self, question: str) -> dict:
        """Generate real AI responses using Gemini - NO EVASIVE ANSWERS"""
        import google.generativeai as genai
        import os
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return self._fallback_response(question)
        
        try:
            genai.configure(api_key=api_key)
            
            model_names = [
                'models/gemini-2.0-flash-lite',
                'models/gemini-2.0-flash',
                'models/gemini-pro-latest'
            ]
            
            model = None
            for model_name in model_names:
                try:
                    model = genai.GenerativeModel(model_name)
                    break
                except:
                    continue
            
            if not model:
                return self._fallback_response(question)
            
            # DIRECT PROMPT - NO EVASIVENESS
            prompt = f"""You are DeskMate AI assistant. Answer the user's question directly and helpfully.

User: {question}

IMPORTANT: 
- Answer directly without saying "I don't have real-time data" or similar disclaimers
- Provide the best answer you can with available knowledge
- If comparing products, give educated comparisons based on public information
- Be helpful and informative, not evasive
- For technical questions, provide detailed technical answers

Answer:"""
            
            response = model.generate_content(prompt)
            ai_response = response.text.strip()
            
            return {
                "success": True,
                "answer": ai_response,
                "question": question,
                "answer_type": "ai_generated",
                "is_conversational": True
            }
            
        except Exception as e:
            return self._fallback_response(question)
    
    def _fallback_response(self, question: str) -> dict:
        """Enhanced fallback responses when AI is unavailable"""
        question_lower = question.lower()
        
        # Enhanced conversational fallbacks - DIRECT ANSWERS
        fallback_responses = {
            "hello": "👋 Hello! I'm DeskMate. How can I help you?",
            "hi": "👋 Hi! What can I do for you?",
        }
        
        # Find matching response
        for key, response in fallback_responses.items():
            if key in question_lower:
                return {
                    "success": True,
                    "answer": response,
                    "question": question,
                    "answer_type": "fallback",
                    "is_conversational": True
                }
        
        # Smart default - DIRECT answers only
        if any(word in question_lower for word in ['joke', 'funny', 'laugh', 'humor']):
            response = "Here's a joke: Why don't eggs tell jokes? They'd crack each other up!"
        elif any(word in question_lower for word in ['time', 'clock', 'current time', 'what time']):
            response = "I can't access real-time information. I can open a time website if you'd like."
        elif any(word in question_lower for word in ['weather', 'temperature']):
            response = "I don't have weather access. I can open a weather website for you."
        elif any(word in question_lower for word in ['model', 'version', 'what are you']):
            response = "I'm DeskMate using Google Gemini AI. I help with files, emails, commands, and opening apps/websites."
        else:
            response = f"I can help you with that. I can assist with files, emails, commands, opening websites/apps, and more."

        return {
            "success": True,
            "answer": response,
            "question": question,
            "answer_type": "fallback",
            "is_conversational": True
        }
    
    def _search_files(self, query: str, directory: str = ".") -> dict:
        """Enhanced file search function"""
        import os
        from datetime import datetime
        
        try:
            results = []
            if os.path.exists(directory):
                for item in os.listdir(directory):
                    item_path = os.path.join(directory, item)
                    if query.lower() in item.lower():
                        stat = os.stat(item_path)
                        results.append({
                            "name": item,
                            "path": item_path,
                            "type": "directory" if os.path.isdir(item_path) else "file",
                            "size": stat.st_size,
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
                        })
            
            return {
                "success": True,
                "query": query,
                "directory": directory,
                "results": results[:10],  # Limit results
                "result_count": len(results),
                "message": f"Found {len(results)} items matching '{query}'"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Search error: {str(e)}",
                "results": []
            }