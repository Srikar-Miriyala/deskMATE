import os
import json
import re
from typing import Dict, Any, List, Optional
from app.core.schema import Intent
from dotenv import load_dotenv

load_dotenv()

class RobustMockLLMClient:
    """Fallback client using regex and keyword matching"""
    
    def __init__(self):
        self.intent_patterns = {
            "greeting": ["hello", "hi", "hey", "greetings", "good morning", "good afternoon"],
            "help": ["help", "what can you do", "capabilities", "commands", "manual"],
            "summarize": ["summarize", "summary", "brief", "overview", "tl;dr"],
            "read_file": ["read", "show content", "display", "cat", "view file"],
            "search_files": ["search", "find", "locate", "where is", "list files"],
            "email": ["email", "draft", "send", "write to", "compose"],
            "shell": ["run", "execute", "command", "terminal", "shell", "cmd", "pwd", "ls", "dir"],
            "open_resource": ["open", "launch", "start", "visit", "go to", "play", "ask"],
            "create_file": ["create file", "make file", "new file", "write file"],
            "create_folder": ["create folder", "make folder", "new folder", "make directory", "new directory"]
        }

    def parse_intent(self, command: str) -> Intent:
        """Parse command using robust pattern matching"""
        command_lower = command.lower()
        
        # 1. Check for file/folder creation (Specific)
        for pattern in self.intent_patterns["create_file"]:
            if pattern in command_lower:
                return self._create_file_operation_intent(command, "create_file")
        
        for pattern in self.intent_patterns["create_folder"]:
            if pattern in command_lower:
                return self._create_file_operation_intent(command, "create_folder")

        # 2. Check for Deep Links (Search X on Y) - Prioritize over generic search
        # If command has "search"/"find" AND "on", it's likely a web search
        if "on" in command_lower and any(w in command_lower for w in ["search", "find", "look for", "ask"]):
             return self._create_open_resource_intent(command)
             
        # Check for "Ask [Platform]" even without "on"
        if command_lower.startswith("ask ") and any(p in command_lower for p in ["gemini", "chatgpt", "perplexity", "claude", "gpt"]):
             return self._create_open_resource_intent(command)

        # 3. Check for open resource (Specific)
        if any(p in command_lower for p in self.intent_patterns["open_resource"]):
            # Avoid capturing "open file" as open_resource if it's actually read_file
            if not ("read" in command_lower or "summarize" in command_lower):
                return self._create_open_resource_intent(command)

        # 4. Check for other intents
        if any(p == command_lower for p in self.intent_patterns["greeting"]): # Exact match for greeting
            return self._create_greeting_intent(command)
            
        if any(p in command_lower for p in self.intent_patterns["help"]):
            return self._create_help_intent(command)
            
        if any(p in command_lower for p in self.intent_patterns["summarize"]):
            return self._create_summarize_intent(command)
            
        if any(p in command_lower for p in self.intent_patterns["read_file"]):
            return self._create_read_file_intent(command)
            
        if any(p in command_lower for p in self.intent_patterns["search_files"]):
            return self._create_search_intent(command)
            
        if any(p in command_lower for p in self.intent_patterns["email"]):
            return self._create_email_intent(command)
            
        if any(p in command_lower for p in self.intent_patterns["shell"]):
            return self._create_shell_intent(command)
            
        # Check for system info/time
        if any(w in command_lower for w in ['system info', 'specs', 'cpu', 'ram', 'memory', 'what time', 'current time', 'clock']):
             return self._create_system_intent(command)
            
        # Default to QA
        return self._create_qa_intent(command)

    def _create_greeting_intent(self, command: str) -> Intent:
        return Intent(
            intent="general_qa",
            target=command,
            steps=[{"action": "answer_question", "params": {"question": command}}],
            confirmation_required=False,
            assumptions=["user is greeting"]
        )

    def _create_help_intent(self, command: str) -> Intent:
        return Intent(
            intent="general_qa",
            target=command,
            steps=[{"action": "answer_question", "params": {"question": command}}],
            confirmation_required=False,
            assumptions=["user needs help"]
        )

    def _create_qa_intent(self, command: str) -> Intent:
        return Intent(
            intent="general_qa",
            target=command,
            steps=[{"action": "answer_question", "params": {"question": command}}],
            confirmation_required=False,
            assumptions=["question is answerable"]
        )

    def _create_summarize_intent(self, command: str) -> Intent:
        filename = self._extract_filename(command)
        if not filename:
            return Intent(
                intent="general_qa",
                target=command,
                steps=[{"action": "answer_question", "params": {"question": f"Please specify which file to summarize. You said: '{command}'"}}],
                confirmation_required=False,
                assumptions=["user needs to specify filename"],
                clarification_question="Which file would you like me to summarize?"
            )
        return Intent(
            intent="summarize_file",
            target=filename,
            steps=[
                {"action": "read_file", "params": {"file_path": f"uploads/{filename}"}},
                {"action": "summarize", "params": {"style": "short"}}
            ],
            confirmation_required=False,
            assumptions=["file exists in uploads folder"]
        )

    def _create_read_file_intent(self, command: str) -> Intent:
        filename = self._extract_filename(command)
        if not filename:
            return Intent(
                intent="general_qa",
                target=command,
                steps=[{"action": "answer_question", "params": {"question": f"Please specify which file to read. You said: '{command}'"}}],
                confirmation_required=False,
                assumptions=["user needs to specify filename"],
                clarification_question="Which file would you like me to read?"
            )
        return Intent(
            intent="read_file",
            target=filename,
            steps=[{"action": "read_file", "params": {"file_path": f"uploads/{filename}"}}],
            confirmation_required=False,
            assumptions=["file exists in uploads folder"]
        )

    def _create_search_intent(self, command: str) -> Intent:
        query = self._extract_search_query(command) or "relevant files"
        directory = "."
        if "desktop" in command.lower():
            directory = os.path.join(os.path.expanduser("~"), "Desktop")
        return Intent(
            intent="search_files",
            target=query,
            steps=[{"action": "search_files", "params": {"query": query, "directory": directory}}],
            confirmation_required=False,
            assumptions=["search directory exists"]
        )

    def _create_email_intent(self, command: str) -> Intent:
        return Intent(
            intent="draft_email",
            target="email draft",
            steps=[{"action": "generate_email", "params": {
                "subject": "Meeting Follow-up", 
                "recipient": "team@company.com", 
                "body": f"Regarding: {command}"
            }}],
            confirmation_required=True,
            assumptions=["email content is appropriate"]
        )

    def _create_shell_intent(self, command: str) -> Intent:
        import platform
        is_windows = platform.system() == "Windows"
        shell_cmd = self._determine_shell_command(command, is_windows)
        return Intent(
            intent="run_shell_command",
            target=shell_cmd,
            steps=[{"action": "run_shell", "params": {"command": shell_cmd}}],
            confirmation_required=True,
            assumptions=["command is safe and whitelisted"]
        )

    def _determine_shell_command(self, command: str, is_windows: bool) -> str:
        command_lower = command.lower()
        if 'pwd' in command_lower:
            return "echo %CD%" if is_windows else "pwd"
        elif 'whoami' in command_lower:
            return "whoami"
        elif 'dir' in command_lower or 'ls' in command_lower:
            return "dir" if is_windows else "ls"
        elif 'terminal' in command_lower or 'cmd' in command_lower:
            return "echo 'Terminal session started'"
        else:
            return "dir" if is_windows else "ls"

    def _create_open_resource_intent(self, command: str) -> Intent:
        command_lower = command.lower()
        
        # 1. Handle "Search/Ask X on Y" pattern (Deep Linking)
        # Keywords: search, ask, find, query, look up
        action_words = ['search', 'ask', 'find', 'look for', 'query']
        platform_map = {
            'youtube': 'https://www.youtube.com/results?search_query={}',
            'google': 'https://www.google.com/search?q={}',
            'amazon': 'https://www.amazon.in/s?k={}',
            'bing': 'https://www.bing.com/search?q={}',
            'duckduckgo': 'https://duckduckgo.com/?q={}',
            'github': 'https://github.com/search?q={}',
            'stackoverflow': 'https://stackoverflow.com/search?q={}',
            'perplexity': 'https://www.perplexity.ai/search?q={}',
            'gemini': 'https://gemini.google.com/app?q={}',
            'chatgpt': 'https://chat.openai.com/?q={}',
            'gpt': 'https://chat.openai.com/?q={}',
        }
        
        for platform, template in platform_map.items():
            if platform in command_lower:
                # Check if it's a search/ask command
                if any(w in command_lower for w in action_words) or f"on {platform}" in command_lower or f"ask {platform}" in command_lower:
                    # Extract query
                    query = command_lower
                    for w in action_words + [platform, 'on', 'in', 'at', 'for', 'about', 'to', 'write', 'a']:
                        query = query.replace(w, ' ')
                    query = query.strip()
                    
                    if query:
                        from urllib.parse import quote_plus
                        encoded_query = quote_plus(query)
                        url = template.format(encoded_query)
                        return Intent(
                            intent="open_url",
                            target=f"{platform} search: {query}",
                            steps=[{"action": "open_url", "params": {"url": url}}],
                            confirmation_required=False,
                            assumptions=["url is valid"]
                        )

        # 2. Handle simple "Open X" where X is a known website
        resource = command_lower.replace('open', '').replace('launch', '').replace('start', '').replace('visit', '').replace('go to', '').strip()
        
        # Known websites that should be opened via open_url, not open_app
        known_sites = [
            "gemini", "chatgpt", "perplexity", "claude", "youtube", "google", "amazon", 
            "netflix", "github", "stackoverflow", "woxsen", "gmail", "whatsapp", "spotify",
            "facebook", "twitter", "instagram", "linkedin"
        ]
        
        if resource in known_sites or any(x in resource for x in ['.com', '.org', '.net', '.edu', '.in', 'http']):
            return Intent(
                intent="open_website",
                target=resource,
                steps=[{"action": "open_url", "params": {"url": resource}}],
                confirmation_required=False,
                assumptions=["url is valid"]
            )
            
        elif any(x in resource for x in ['explorer', 'folder', 'directory', 'file explorer']):
            path = os.path.expanduser("~")
            return Intent(
                intent="open_explorer",
                target="file explorer",
                steps=[{"action": "open_explorer", "params": {"path": path}}],
                confirmation_required=False,
                assumptions=["path exists"]
            )
            
        elif any(x in resource for x in ['terminal', 'cmd', 'command prompt', 'powershell']):
            return Intent(
                intent="run_shell_command",
                target="terminal",
                steps=[{"action": "open_terminal", "params": {"path": None}}],
                confirmation_required=False,
                assumptions=["terminal is available"]
            )
            
        else:
            return Intent(
                intent="open_app",
                target=resource,
                steps=[{"action": "open_app", "params": {"app_name": resource}}],
                confirmation_required=False,
                assumptions=["application is installed"]
            )

    def _create_system_intent(self, command: str) -> Intent:
        command_lower = command.lower()
        if any(w in command_lower for w in ['time', 'clock', 'date']):
            return Intent(
                intent="get_time",
                target="time",
                steps=[{"action": "get_time", "params": {}}],
                confirmation_required=False,
                assumptions=["user wants local time"]
            )
        else:
            return Intent(
                intent="get_system_info",
                target="system info",
                steps=[{"action": "get_system_info", "params": {}}],
                confirmation_required=False,
                assumptions=["user wants system specs"]
            )

    def _create_file_operation_intent(self, command: str, operation: str) -> Intent:
        # Use regex to remove command keywords only at the start
        pattern = r'^(create|make|new)\s+(file|folder|directory)\s+'
        name = re.sub(pattern, '', command.lower(), count=1).strip()
        
        # Fallback if regex didn't match (e.g. just "create notes.txt")
        if name == command.lower():
             # Try simpler removal - only remove first occurrence
             name = re.sub(r'^(create|make|new)\s+', '', command.lower(), count=1).strip()
        
        if not name:
            name = "new_item" if operation == "create_file" else "New Folder"
        
        action = "create_file" if operation == "create_file" else "create_folder"
        
        return Intent(
            intent=operation,
            target=name,
            steps=[{"action": action, "params": {"path": name}}],
            confirmation_required=False,
            assumptions=["path is valid"]
        )

    def _extract_filename(self, command: str) -> str:
        words = command.lower().split()
        for word in words:
            if word.endswith(('.pdf', '.txt', '.doc', '.docx')):
                return word
        return ""

    def _extract_search_query(self, command: str) -> str:
        remove_words = ['search', 'find', 'look', 'for', 'locate']
        words = command.lower().split()
        query_words = [word for word in words if word not in remove_words]
        return ' '.join(query_words) if query_words else ""


class GeminiLLMClient:
    """Real LLM client using Google Gemini with robust error handling"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        self.is_available = False
        self.fallback_client = RobustMockLLMClient()
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                model_names = ['models/gemini-2.0-flash', 'models/gemini-pro']
                for model_name in model_names:
                    try:
                        self.model = genai.GenerativeModel(model_name)
                        self.is_available = True
                        break
                    except:
                        continue
            except Exception as e:
                print(f"Gemini Init Error: {e}")
                self.is_available = False
    
    def parse_intent(self, command: str) -> Intent:
        if not self.is_available or not self.model:
            return self.fallback_client.parse_intent(command)
        
        try:
            prompt = f"""Analyze command: "{command}"
            Return JSON with intent, target, and steps.
            
            Capabilities:
            1. Open URLs/Apps: "open gemini", "open youtube", "open calculator"
            2. Search/Deep Links: "search iphone on amazon" -> open_url("https://amazon.in/s?k=iphone")
            3. File Ops: "create folder projects/test" -> create_folder("projects/test")
            4. Terminal: "open terminal" -> open_terminal()
            5. Q&A: "explain ML" -> answer_question("explain ML")
            6. System: "system info" -> get_system_info(), "what time is it" -> get_time()
            
            Rules:
            - **CRITICAL**: If command is "Ask Gemini...", "Ask ChatGPT...", "Ask Perplexity...", "Search on Google...", ALWAYS use `open_url` with the search URL. Do NOT use `answer_question`.
            - For "search X on Y", construct the search URL.
            - For "open gemini", "open perplexity", use open_url with just the name (e.g. "gemini") or full URL.
            - For file paths, keep them exactly as written (preserve casing/slashes).
            
            JSON Format:
            {{
                "intent": "action_name",
                "target": "target_name",
                "steps": [{{"action": "action_name", "params": {{...}}}}]
            }}
            """
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return Intent(**json.loads(match.group()))
            return self.fallback_client.parse_intent(command)
        except:
            return self.fallback_client.parse_intent(command)