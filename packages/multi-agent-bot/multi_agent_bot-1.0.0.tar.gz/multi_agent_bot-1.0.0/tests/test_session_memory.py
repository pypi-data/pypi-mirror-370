"""
Test session memory functionality for bots.

This module tests that bots can maintain conversation context 
across multiple queries within a user session.
"""

import pytest

from main.sales_bot import SalesBot
from utils.session_manager import session_manager


class TestSessionMemory:
    """Test session memory functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Clear any existing sessions before each test
        session_manager.sessions.clear()
        session_manager.user_sessions.clear()
    
    def test_session_creation(self):
        """Test that sessions are created correctly"""
        user_id = "test_user_creation"
        
        # Create session
        session_id = session_manager.get_or_create_session(user_id)
        
        # Verify session was created
        assert session_id is not None
        assert len(session_id) > 0
        
        # Check stats
        stats = session_manager.get_stats()
        assert stats['active_sessions'] == 1
        assert stats['unique_users'] == 1
        assert stats['total_queries'] == 0
        assert stats['total_agent_memories'] == 0
    
    def test_session_reuse(self):
        """Test that same user gets same session"""
        user_id = "test_user_reuse"
        
        # Create session twice
        session_id1 = session_manager.get_or_create_session(user_id)
        session_id2 = session_manager.get_or_create_session(user_id)
        
        # Should be the same session
        assert session_id1 == session_id2
        
        # Should still be only one session
        stats = session_manager.get_stats()
        assert stats['active_sessions'] == 1
        assert stats['unique_users'] == 1
    
    def test_interaction_recording(self):
        """Test that interactions are recorded correctly"""
        user_id = "test_user_interaction"
        agent_name = "TestAgent"
        
        # Create session and record interaction
        session_id = session_manager.get_or_create_session(user_id)
        session_manager.record_interaction(
            session_id, 
            "Dame ventas de 2024", 
            "Las ventas de 2024 fueron...", 
            agent_name
        )
        
        # Check stats updated
        stats = session_manager.get_stats()
        assert stats['total_queries'] == 1
        assert stats['total_agent_memories'] == 1
        
        # Check context is available
        context = session_manager.get_context_for_agent(session_id, agent_name)
        assert "Dame ventas de 2024" in context
        assert "Las ventas de 2024 fueron..." in context
    
    def test_context_accumulation(self):
        """Test that context accumulates across interactions"""
        user_id = "test_user_context"
        agent_name = "TestAgent"
        
        session_id = session_manager.get_or_create_session(user_id)
        
        # First interaction
        session_manager.record_interaction(
            session_id, 
            "Dame ventas de 2024", 
            "Las ventas de 2024 fueron 21M USD", 
            agent_name
        )
        
        # Second interaction
        session_manager.record_interaction(
            session_id,
            "Y de 2023?",
            "Las ventas de 2023 fueron 19M USD",
            agent_name
        )
        
        # Check final context contains both
        context = session_manager.get_context_for_agent(session_id, agent_name)
        assert "Dame ventas de 2024" in context
        assert "Y de 2023?" in context
        
        # Check stats
        stats = session_manager.get_stats()
        assert stats['total_queries'] == 2
        assert stats['total_agent_memories'] == 2
    
    def test_sales_bot_session_memory_comprehensive(self):
        """Test that SalesBot uses session memory correctly like in the API"""
        user_id = "api_user_123"
        
        # Initialize bot (like sales_engine does)
        bot = SalesBot()
        
        # Test 1: First query - should create a session
        print(f"\nTest 1: First query with user_id: {user_id}")
        result1 = bot.process_query("Dame ventas de 2024", user_name=user_id)
        
        # Verify the query was processed successfully
        assert result1 is not None
        assert 'error' not in result1
        assert 'messages' in result1
        
        # Check session was created and interaction recorded
        stats1 = session_manager.get_stats()
        print(f"Stats after first query: {stats1}")
        
        assert stats1['active_sessions'] == 1
        assert stats1['unique_users'] == 1
        assert stats1['total_queries'] == 1
        assert stats1['total_agent_memories'] == 1
        
        # Verify session exists for this user
        assert user_id in session_manager.user_sessions
        session_id = session_manager.user_sessions[user_id]
        session = session_manager.get_session(session_id)
        assert session is not None
        assert len(session.recent_queries) == 1
        assert "2024" in session.recent_queries[0]['query']
        
        # Test 2: Second query from same user - should reuse session and have context
        print(f"\nTest 2: Second query with same user_id: {user_id}")
        result2 = bot.process_query("Y de 2023?", user_name=user_id)
        
        # Verify the second query was processed successfully
        assert result2 is not None
        assert 'error' not in result2
        assert 'messages' in result2
        
        # Check session accumulated interactions
        stats2 = session_manager.get_stats()
        print(f"Stats after second query: {stats2}")
        
        assert stats2['active_sessions'] == 1  # Still 1 session
        assert stats2['unique_users'] == 1  # Still 1 user
        assert stats2['total_queries'] == 2
        assert stats2['total_agent_memories'] == 2
        
        # Verify session has both queries
        session = session_manager.get_session(session_id)
        assert len(session.recent_queries) == 2
        assert "2024" in session.recent_queries[0]['query']
        assert "2023" in session.recent_queries[1]['query']
        
        # Test 3: Third query from different user - should create new session
        print(f"\nTest 3: Query from different user")
        user_id_2 = "api_user_456"
        result3 = bot.process_query("Dame ventas totales por producto", user_name=user_id_2)
        
        # Verify the query was processed successfully
        assert result3 is not None
        assert 'error' not in result3
        
        # Check we now have 2 sessions
        stats3 = session_manager.get_stats()
        print(f"Stats after third query (different user): {stats3}")
        
        assert stats3['active_sessions'] == 2  # Now 2 sessions
        assert stats3['unique_users'] == 2  # Now 2 users
        assert stats3['total_queries'] == 3
        assert stats3['total_agent_memories'] == 3
        
        # Test 4: Fourth query from first user again - should reuse original session
        print(f"\nTest 4: Query from first user again: {user_id}")
        result4 = bot.process_query("Compara esos años", user_name=user_id)
        
        # Verify the query was processed successfully
        assert result4 is not None
        assert 'error' not in result4
        
        # Check sessions and interactions
        stats4 = session_manager.get_stats()
        print(f"Stats after fourth query (original user): {stats4}")
        
        assert stats4['active_sessions'] == 2  # Still 2 sessions
        assert stats4['unique_users'] == 2  # Still 2 users
        assert stats4['total_queries'] == 4
        assert stats4['total_agent_memories'] == 4
        
        # Verify the first user's session now has 3 queries
        session = session_manager.get_session(session_id)
        assert len(session.recent_queries) == 3
        assert "compara" in session.recent_queries[2]['query'].lower() or "años" in session.recent_queries[2]['query'].lower()
        
        print("\nAll session memory tests passed!")
    
    def test_different_users_different_sessions(self):
        """Test that different users get different sessions"""
        user1 = "user_one" 
        user2 = "user_two"
        
        # Create sessions for different users
        session1 = session_manager.get_or_create_session(user1)
        session2 = session_manager.get_or_create_session(user2)
        
        # Should be different sessions
        assert session1 != session2
        
        # Should have 2 sessions, 2 users
        stats = session_manager.get_stats()
        assert stats['active_sessions'] == 2
        assert stats['unique_users'] == 2
    
    def test_topic_extraction(self):
        """Test that topics are extracted from queries"""
        user_id = "test_topics"
        agent_name = "TestAgent"
        
        session_id = session_manager.get_or_create_session(user_id)
        
        # Record interaction with topic keywords
        session_manager.record_interaction(
            session_id,
            "Dame las ventas de CompanyName por producto",
            "Las ventas por producto son...",
            agent_name
        )
        
        # Get session and check topics were extracted
        session = session_manager.get_session(session_id)
        assert session is not None
        
        # Should have extracted 'ventas' and 'deliproduct' topics
        assert 'ventas' in session.key_topics
        assert 'deliproduct' in session.key_topics or 'deliproducta' in session.key_topics


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
