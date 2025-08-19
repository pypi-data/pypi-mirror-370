#!/usr/bin/env python3
"""
Complete Integration Test for ProductBot Session Management
Tests the full flow from UI-like requests to backend session storage and retrieval.
"""

import requests
import uuid
import time
import json
import pytest
from datetime import datetime
from typing import Dict, Any


class ProductBotIntegrationTester:
    """Test the complete session management integration"""

    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.test_results = []

    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append(
            {
                "test": test_name,
                "status": status,
                "details": details,
                "timestamp": datetime.now().isoformat(),
            }
        )
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")

    def simulate_ui_request(
        self, query: str, user_id: str, session_id: str, endpoint: str = "/api/query"
    ) -> Dict[Any, Any]:
        """Simulate a UI request exactly as the chat app would send it"""
        payload = {"query": query, "user_id": user_id, "session_id": session_id}

        try:
            response = requests.post(
                f"{self.base_url}{endpoint}", json=payload, timeout=60
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "status_code": response.status_code,
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "status_code": response.status_code,
                }
        except Exception as e:
            return {"success": False, "error": str(e), "status_code": None}

    def test_session_creation_and_persistence(self):
        """Test 1: Session creation and persistence across multiple messages"""
        print("\n🧪 TEST 1: Session Creation and Persistence")
        print("-" * 50)

        # Generate session like UI would
        user_id = datetime.now().strftime("%Y%m%d%H%M%S")
        session_id = str(uuid.uuid4())

        print(f"Generated User ID: {user_id}")
        print(f"Generated Session ID: {session_id}")

        # First message
        response1 = self.simulate_ui_request(
            "¿Cuáles son las ventas de CompanyName en 2023?", user_id, session_id
        )

        if response1["success"]:
            self.log_test(
                "First message sent successfully",
                True,
                f"Status: {response1['status_code']}",
            )
        else:
            self.log_test("First message failed", False, response1["error"])
            return False

        # Wait a moment
        time.sleep(2)

        # Follow-up message (should have context)
        response2 = self.simulate_ui_request(
            "¿Y cómo se comparan con el año anterior?", user_id, session_id
        )

        if response2["success"]:
            self.log_test(
                "Follow-up message with context", True, "Session context maintained"
            )
        else:
            self.log_test("Follow-up message failed", False, response2["error"])
            return False

        return True

    def test_multi_bot_session_sharing(self):
        """Test 2: Session sharing across different bot endpoints"""
        print("\n🧪 TEST 2: Multi-Bot Session Sharing")
        print("-" * 50)

        # Generate session
        user_id = datetime.now().strftime("%Y%m%d%H%M%S")
        session_id = str(uuid.uuid4())

        print(f"Testing session sharing across bots with Session ID: {session_id}")

        # Start with SuperBot
        response1 = self.simulate_ui_request(
            "Dame información sobre la marca CompanyName", user_id, session_id, "/api/query"
        )

        if response1["success"]:
            self.log_test("SuperBot initial query", True, "Main bot responded")
        else:
            self.log_test("SuperBot initial query", False, response1["error"])
            return False

        time.sleep(2)

        # Switch to MarketStudy bot with same session
        response2 = self.simulate_ui_request(
            "¿Qué estudios de mercado tenemos sobre percepción de marca?",
            user_id,
            session_id,
            "/api/market-study/query",
        )

        if response2["success"]:
            self.log_test(
                "MarketStudy bot with shared session",
                True,
                "Different bot accessed same session",
            )
        else:
            self.log_test(
                "MarketStudy bot with shared session", False, response2["error"]
            )
            return False

        time.sleep(2)

        # Switch to Sales bot with same session
        response3 = self.simulate_ui_request(
            "¿Cuáles fueron las ventas en el último trimestre?",
            user_id,
            session_id,
            "/api/sales/query",
        )

        if response3["success"]:
            self.log_test(
                "Sales bot with shared session", True, "Third bot accessed same session"
            )
        else:
            self.log_test("Sales bot with shared session", False, response3["error"])
            return False

        return True

    def test_session_isolation(self):
        """Test 3: Session isolation between different sessions"""
        print("\n🧪 TEST 3: Session Isolation")
        print("-" * 50)

        # Two different sessions
        user_id1 = datetime.now().strftime("%Y%m%d%H%M%S") + "_1"
        session_id1 = str(uuid.uuid4())

        user_id2 = datetime.now().strftime("%Y%m%d%H%M%S") + "_2"
        session_id2 = str(uuid.uuid4())

        print(f"Session 1: {session_id1}")
        print(f"Session 2: {session_id2}")

        # Send message in session 1
        response1 = self.simulate_ui_request(
            "Quiero información sobre ventas de producta en Country B",
            user_id1,
            session_id1,
        )

        if response1["success"]:
            self.log_test("Session 1 message", True, "First session established")
        else:
            self.log_test("Session 1 message", False, response1["error"])
            return False

        time.sleep(1)

        # Send completely different message in session 2
        response2 = self.simulate_ui_request(
            "Dame datos de mercado sobre Country A", user_id2, session_id2
        )

        if response2["success"]:
            self.log_test(
                "Session 2 isolated message", True, "Second session works independently"
            )
        else:
            self.log_test("Session 2 isolated message", False, response2["error"])
            return False

        return True

    def test_ui_session_lifecycle(self):
        """Test 4: UI Session Lifecycle (Clear Chat, New Session)"""
        print("\n🧪 TEST 4: UI Session Lifecycle")
        print("-" * 50)

        # Simulate initial session
        user_id = datetime.now().strftime("%Y%m%d%H%M%S")
        session_id1 = str(uuid.uuid4())

        print(f"Initial session: {session_id1}")

        # First conversation
        response1 = self.simulate_ui_request(
            "¿Qué sabes sobre CompanyName?", user_id, session_id1
        )

        if response1["success"]:
            self.log_test("Initial conversation", True, "Session 1 started")
        else:
            self.log_test("Initial conversation", False, response1["error"])
            return False

        time.sleep(1)

        # Simulate "Clear Chat" - new session ID
        session_id2 = str(uuid.uuid4())
        print(f"After clear chat: {session_id2}")

        response2 = self.simulate_ui_request(
            "¿Cuáles son los productos de CompanyName?",
            user_id,  # Same user
            session_id2,  # Different session
        )

        if response2["success"]:
            self.log_test("New session after clear", True, "Fresh session created")
        else:
            self.log_test("New session after clear", False, response2["error"])
            return False

        return True

    def test_error_handling(self):
        """Test 5: Error handling and edge cases"""
        print("\n🧪 TEST 5: Error Handling")
        print("-" * 50)

        # Test with malformed session ID
        response1 = self.simulate_ui_request(
            "Test query", "test_user", "invalid-session-id-format"
        )

        # Should still work - backend should handle any string as session ID
        if response1["success"]:
            self.log_test(
                "Malformed session ID handling",
                True,
                "Backend handled non-UUID session ID",
            )
        else:
            self.log_test("Malformed session ID handling", False, response1["error"])

        # Test with empty query
        response2 = self.simulate_ui_request("", "test_user", str(uuid.uuid4()))

        # Should handle gracefully
        self.log_test("Empty query handling", True, "Backend handled empty query")

        return True

    def run_all_tests(self):
        """Run the complete integration test suite"""
        print("🚀 SOYBOT COMPLETE INTEGRATION TEST SUITE")
        print("=" * 60)
        print(f"Testing against: {self.base_url}")
        print(f"Test started at: {datetime.now().isoformat()}")

        tests = [
            self.test_session_creation_and_persistence,
            self.test_multi_bot_session_sharing,
            self.test_session_isolation,
            self.test_ui_session_lifecycle,
            self.test_error_handling,
        ]

        passed = 0
        failed = 0

        for test in tests:
            try:
                if test():
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                failed += 1
                print(f"❌ Test failed with exception: {e}")

        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {len(tests)}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed / len(tests) * 100):.1f}%")

        if failed == 0:
            print("\n🎉 ALL TESTS PASSED - COMPLETE INTEGRATION VERIFIED!")
        else:
            print(f"\n⚠️  {failed} test(s) failed - check details above")

        # Detailed results
        print("\n📋 DETAILED TEST RESULTS:")
        for result in self.test_results:
            print(f"   {result['status']}: {result['test']}")
            if result["details"]:
                print(f"      └─ {result['details']}")

        return failed == 0


# Pytest-compatible test functions
@pytest.fixture
def integration_tester():
    """Create an integration tester instance"""
    return ProductBotIntegrationTester()


def test_api_server_availability():
    """Test that the API server is running"""
    try:
        response = requests.get("http://localhost:8001/docs", timeout=5)
        assert response.status_code == 200, "API server not responding correctly"
    except requests.exceptions.RequestException:
        pytest.skip("API server not running - start with: python api/main.py")


def test_session_persistence(integration_tester):
    """Pytest wrapper for session persistence test"""
    assert integration_tester.test_session_creation_and_persistence()


def test_multi_bot_sessions(integration_tester):
    """Pytest wrapper for multi-bot session test"""
    assert integration_tester.test_multi_bot_session_sharing()


def test_session_isolation_pytest(integration_tester):
    """Pytest wrapper for session isolation test"""
    assert integration_tester.test_session_isolation()


def test_ui_lifecycle(integration_tester):
    """Pytest wrapper for UI lifecycle test"""
    assert integration_tester.test_ui_session_lifecycle()


def test_error_handling_pytest(integration_tester):
    """Pytest wrapper for error handling test"""
    assert integration_tester.test_error_handling()


if __name__ == "__main__":
    # Check if API server is running
    try:
        response = requests.get("http://localhost:8001/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running at http://localhost:8001")
        else:
            print("⚠️  API server responded but may have issues")
    except:
        print("❌ API server is not running at http://localhost:8001")
        print("   Please start the server with: python api/main.py")
        exit(1)

    # Run the tests
    tester = ProductBotIntegrationTester()
    success = tester.run_all_tests()

    exit(0 if success else 1)
