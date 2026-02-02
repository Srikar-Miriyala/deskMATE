import unittest
import os
import sys

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.core.llm_client import MockLLMClient
from app.core.agent_core import DeskMateAgent
from app.plugins.file_reader import FileReaderPlugin
from app.plugins.shell_runner import ShellRunnerPlugin

class TestDeskMateAgent(unittest.TestCase):
    
    def setUp(self):
        self.llm_client = MockLLMClient()
        self.agent = DeskMateAgent()
        self.file_reader = FileReaderPlugin()
        self.shell_runner = ShellRunnerPlugin()
    
    def test_intent_parsing(self):
        """Test that commands are correctly parsed into intents"""
        
        # Test summarize intent
        intent = self.llm_client.parse_intent("summarize my document")
        self.assertEqual(intent.intent, "summarize_file")
        
        # Test read file intent
        intent = self.llm_client.parse_intent("read the file notes.txt")
        self.assertEqual(intent.intent, "read_file")
        
        # Test email intent
        intent = self.llm_client.parse_intent("draft an email to john")
        self.assertEqual(intent.intent, "draft_email")
        self.assertTrue(intent.confirmation_required)
        
        # Test shell command intent
        intent = self.llm_client.parse_intent("run ls command")
        self.assertEqual(intent.intent, "run_shell_command")
        self.assertTrue(intent.confirmation_required)
    
    def test_shell_command_safety(self):
        """Test that only whitelisted commands are allowed"""
        
        # Test safe commands
        self.assertTrue(self.shell_runner.is_command_safe("ls"))
        self.assertTrue(self.shell_runner.is_command_safe("pwd"))
        self.assertTrue(self.shell_runner.is_command_safe("whoami"))
        
        # Test unsafe commands
        self.assertFalse(self.shell_runner.is_command_safe("rm -rf /"))
        self.assertFalse(self.shell_runner.is_command_safe("sudo"))
        self.assertFalse(self.shell_runner.is_command_safe("curl"))
    
    def test_agent_processing(self):
        """Test end-to-end agent processing"""
        result = self.agent.process_command("what can you do?")
        
        self.assertIn('command', result)
        self.assertIn('intent', result)
        self.assertIn('results', result)
        self.assertIn('success', result)

if __name__ == '__main__':
    unittest.main()