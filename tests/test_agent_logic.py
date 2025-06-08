import unittest
import os
from unittest.mock import patch, MagicMock
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice_agent_original import get_reply


class TestAgentLogic(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_prompt = "What is the weather like today?"
        self.test_user_id = "test_user_123"
        
    @patch('voice_agent_original.memg')
    @patch('voice_agent_original.Crew')
    def test_get_reply_success(self, mock_crew_class, mock_memg):
        """Test successful agent response generation."""
        # Mock memory search
        mock_memories = [
            {"memory": "User likes sunny weather"},
            {"memory": "User lives in New York"}
        ]
        mock_memg.search.return_value = mock_memories
        
        # Mock crew and task execution
        mock_result = MagicMock()
        mock_result.raw = "It's a beautiful sunny day today!"
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = mock_result
        mock_crew_class.return_value = mock_crew_instance
        
        # Mock memory addition
        mock_memg.add.return_value = True
        
        with patch('voice_agent_original.USER_ID', self.test_user_id):
            result = get_reply(self.test_prompt)
        
        # Verify result
        self.assertEqual(result, "It's a beautiful sunny day today!")
        
        # Verify memory search was called
        mock_memg.search.assert_called_once_with(self.test_prompt, user_id=self.test_user_id)
        
        # Verify crew was created and executed
        mock_crew_class.assert_called_once()
        mock_crew_instance.kickoff.assert_called_once()
        
        # Verify memory was added
        mock_memg.add.assert_called_once()
        add_call_args = mock_memg.add.call_args
        conversation = add_call_args[0][0]
        self.assertEqual(len(conversation), 2)
        self.assertEqual(conversation[0]["role"], "user")
        self.assertEqual(conversation[0]["content"], self.test_prompt)
        self.assertEqual(conversation[1]["role"], "assistant")
        self.assertEqual(conversation[1]["content"], "It's a beautiful sunny day today!")
    
    @patch('voice_agent_original.memg')
    @patch('voice_agent_original.Crew')
    def test_get_reply_with_relevant_memories(self, mock_crew_class, mock_memg):
        """Test that relevant memories are included in the prompt context."""
        # Mock memory search with multiple memories
        mock_memories = [
            {"memory": "User prefers short responses"},
            {"memory": "User is interested in technology"},
            {"memory": "User works as a developer"}
        ]
        mock_memg.search.return_value = mock_memories
        
        mock_result = MagicMock()
        mock_result.raw = "Here's a brief tech update."
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = mock_result
        mock_crew_class.return_value = mock_crew_instance
        
        with patch('voice_agent_original.USER_ID', self.test_user_id):
            get_reply("Tell me about recent tech news")
        
        # Verify crew was created with enhanced prompt containing memories
        crew_call_args = mock_crew_class.call_args[1]
        task = crew_call_args['tasks'][0]
        task_description = task.description
        
        # Should contain original prompt and memory context
        self.assertIn("Tell me about recent tech news", task_description)
        self.assertIn("Relevant memories:", task_description)
        self.assertIn("User prefers short responses", task_description)
        self.assertIn("User is interested in technology", task_description)
        self.assertIn("User works as a developer", task_description)
    
    @patch('voice_agent_original.memg')
    @patch('voice_agent_original.Crew')
    def test_get_reply_no_memories(self, mock_crew_class, mock_memg):
        """Test agent response when no relevant memories are found."""
        # Mock empty memory search
        mock_memg.search.return_value = []
        
        mock_result = MagicMock()
        mock_result.raw = "I can help you with that."
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = mock_result
        mock_crew_class.return_value = mock_crew_instance
        
        with patch('voice_agent_original.USER_ID', self.test_user_id):
            result = get_reply(self.test_prompt)
        
        # Should still work without memories
        self.assertEqual(result, "I can help you with that.")
        
        # Verify task description doesn't include memory context
        crew_call_args = mock_crew_class.call_args[1]
        task = crew_call_args['tasks'][0]
        task_description = task.description
        self.assertNotIn("Relevant memories:", task_description)
    
    @patch('voice_agent_original.memg')
    @patch('voice_agent_original.Crew')
    @patch('builtins.print')
    def test_get_reply_memory_search_error(self, mock_print, mock_crew_class, mock_memg):
        """Test handling of memory search errors."""
        # Mock memory search error
        mock_memg.search.side_effect = Exception("Memory search failed")
        
        mock_result = MagicMock()
        mock_result.raw = "Response without memory context"
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = mock_result
        mock_crew_class.return_value = mock_crew_instance
        
        with patch('voice_agent_original.USER_ID', self.test_user_id):
            result = get_reply(self.test_prompt)
        
        # Should still return result
        self.assertEqual(result, "Response without memory context")
        
        # Should print warning
        mock_print.assert_any_call("💭 Memory search warning: Memory search failed")
    
    @patch('voice_agent_original.memg')
    @patch('voice_agent_original.Crew')
    @patch('builtins.print')
    def test_get_reply_memory_addition_error(self, mock_print, mock_crew_class, mock_memg):
        """Test handling of memory addition errors."""
        mock_memg.search.return_value = []
        mock_memg.add.side_effect = Exception("Memory addition failed")
        
        mock_result = MagicMock()
        mock_result.raw = "Test response"
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = mock_result
        mock_crew_class.return_value = mock_crew_instance
        
        with patch('voice_agent_original.USER_ID', self.test_user_id):
            result = get_reply(self.test_prompt)
        
        # Should still return result
        self.assertEqual(result, "Test response")
        
        # Should print warning instead of success message
        mock_print.assert_any_call("💭 Memory addition warning: Memory addition failed")
    
    @patch('voice_agent_original.memg')
    @patch('voice_agent_original.Crew')
    def test_get_reply_crew_configuration(self, mock_crew_class, mock_memg):
        """Test that Crew is configured correctly."""
        mock_memg.search.return_value = []
        
        mock_result = MagicMock()
        mock_result.raw = "Test response"
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = mock_result
        mock_crew_class.return_value = mock_crew_instance
        
        with patch('voice_agent_original.USER_ID', self.test_user_id):
            get_reply(self.test_prompt)
        
        # Verify Crew configuration
        crew_call_args = mock_crew_class.call_args[1]
        
        # Check agents
        self.assertIn('agents', crew_call_args)
        self.assertEqual(len(crew_call_args['agents']), 1)
        
        # Check tasks
        self.assertIn('tasks', crew_call_args)
        self.assertEqual(len(crew_call_args['tasks']), 1)
        
        # Check process and settings
        self.assertEqual(crew_call_args['memory'], True)
        self.assertEqual(crew_call_args['verbose'], False)
    
    @patch('voice_agent_original.memg')
    @patch('voice_agent_original.Crew')
    def test_get_reply_task_configuration(self, mock_crew_class, mock_memg):
        """Test that Task is configured correctly."""
        mock_memg.search.return_value = []
        
        mock_result = MagicMock()
        mock_result.raw = "Test response"
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = mock_result
        mock_crew_class.return_value = mock_crew_instance
        
        with patch('voice_agent_original.USER_ID', self.test_user_id):
            get_reply(self.test_prompt)
        
        # Get the task from the crew call
        crew_call_args = mock_crew_class.call_args[1]
        task = crew_call_args['tasks'][0]
        
        # Verify task properties
        self.assertIn(self.test_prompt, task.description)
        self.assertEqual(task.expected_output, "A helpful and conversational response to the user's question")
    
    @patch('voice_agent_original.memg')
    @patch('voice_agent_original.Crew')
    def test_get_reply_result_handling(self, mock_crew_class, mock_memg):
        """Test handling of different result formats."""
        mock_memg.search.return_value = []
        
        # Test with result that has .raw attribute
        mock_result_with_raw = MagicMock()
        mock_result_with_raw.raw = "Response with raw attribute"
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = mock_result_with_raw
        mock_crew_class.return_value = mock_crew_instance
        
        with patch('voice_agent_original.USER_ID', self.test_user_id):
            result = get_reply(self.test_prompt)
        
        self.assertEqual(result, "Response with raw attribute")
    
    @patch('voice_agent_original.memg')
    @patch('voice_agent_original.Crew')
    def test_get_reply_result_without_raw(self, mock_crew_class, mock_memg):
        """Test handling of result without .raw attribute."""
        mock_memg.search.return_value = []
        
        # Test with result that doesn't have .raw attribute
        mock_result_without_raw = "Simple string result"
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = mock_result_without_raw
        mock_crew_class.return_value = mock_crew_instance
        
        with patch('voice_agent_original.USER_ID', self.test_user_id):
            result = get_reply(self.test_prompt)
        
        # Should convert to string
        self.assertEqual(result, "Simple string result")
    
    @patch('voice_agent_original.memg')
    @patch('voice_agent_original.Crew')
    def test_get_reply_memory_limit(self, mock_crew_class, mock_memg):
        """Test that only top 3 memories are included in context."""
        # Mock search with more than 3 memories
        mock_memories = [
            {"memory": "Memory 1"},
            {"memory": "Memory 2"},
            {"memory": "Memory 3"},
            {"memory": "Memory 4"},
            {"memory": "Memory 5"}
        ]
        mock_memg.search.return_value = mock_memories
        
        mock_result = MagicMock()
        mock_result.raw = "Response"
        mock_crew_instance = MagicMock()
        mock_crew_instance.kickoff.return_value = mock_result
        mock_crew_class.return_value = mock_crew_instance
        
        with patch('voice_agent_original.USER_ID', self.test_user_id):
            get_reply(self.test_prompt)
        
        # Verify only first 3 memories are included
        crew_call_args = mock_crew_class.call_args[1]
        task = crew_call_args['tasks'][0]
        task_description = task.description
        
        self.assertIn("Memory 1", task_description)
        self.assertIn("Memory 2", task_description)
        self.assertIn("Memory 3", task_description)
        self.assertNotIn("Memory 4", task_description)
        self.assertNotIn("Memory 5", task_description)


if __name__ == '__main__':
    unittest.main() 