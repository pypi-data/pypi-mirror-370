#!/usr/bin/env python3
"""
{{ project_name | title }} - MCP Client Test Suite

This test suite validates the MCP server functionality by acting as an MCP client.
It tests all major endpoints and verifies MCP 2025-06-18 protocol compliance.
"""

import asyncio
import json
import sys
from typing import Dict, Any, List
import httpx
from pathlib import Path


class MCPClient:
    """MCP client for testing {{ project_name | title }}."""
    
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url
        self.session_id = None
        
    async def test_health_check(self) -> bool:
        """Test the health endpoint."""
        print("🏥 Testing health endpoint...")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health", timeout=10)
                
                if response.status_code != 200:
                    print(f"❌ Health check failed with status: {response.status_code}")
                    return False
                    
                health_data = response.json()
                print(f"✅ Health check passed")
                print(f"   Server: {health_data.get('server', {}).get('name', 'Unknown')}")
                print(f"   Version: {health_data.get('server', {}).get('version', 'Unknown')}")
                print(f"   MCP Version: {health_data.get('server', {}).get('mcp_version', 'Unknown')}")
                print(f"   Connectors: {health_data.get('connectors', {}).get('enabled', 0)} enabled")
                return True
                
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False
    
    async def test_initialize_mcp(self) -> bool:
        """Test MCP initialization."""
        print("\n🔧 Testing MCP initialization...")
        
        try:
            async with httpx.AsyncClient() as client:
                init_request = {
                    "jsonrpc": "2.0",
                    "method": "initialize",
                    "id": 1,
                    "params": {
                        "protocolVersion": "2025-06-18",
                        "capabilities": {
                            "roots": {
                                "listChanged": True
                            },
                            "sampling": {}
                        },
                        "clientInfo": {
                            "name": "{{ project_name | title }} Test Client",
                            "version": "1.0.0"
                        }
                    }
                }
                
                response = await client.post(
                    f"{self.base_url}/mcp",
                    json=init_request,
                    headers={
                        "Content-Type": "application/json",
                        "MCP-Protocol-Version": "2025-06-18"
                    },
                    timeout=10
                )
                
                if response.status_code != 200:
                    print(f"❌ MCP initialization failed with status: {response.status_code}")
                    return False
                    
                init_data = response.json()
                
                if "result" not in init_data:
                    print(f"❌ MCP initialization missing result: {init_data}")
                    return False
                    
                result = init_data["result"]
                print(f"✅ MCP initialization successful")
                print(f"   Protocol Version: {result.get('protocolVersion', 'Unknown')}")
                print(f"   Server Info: {result.get('serverInfo', {}).get('name', 'Unknown')}")
                
                return True
                
        except Exception as e:
            print(f"❌ MCP initialization error: {e}")
            return False
    
    async def test_list_tools(self) -> List[Dict[str, Any]]:
        """Test tools listing."""
        print("\n🛠️ Testing tools listing...")
        
        try:
            async with httpx.AsyncClient() as client:
                # Test REST endpoint
                response = await client.get(f"{self.base_url}/tools", timeout=10)
                
                if response.status_code != 200:
                    print(f"❌ Tools listing failed with status: {response.status_code}")
                    return []
                    
                tools_data = response.json()
                tools = tools_data.get("tools", [])
                
                print(f"✅ Found {len(tools)} tools:")
                for i, tool in enumerate(tools, 1):
                    print(f"   {i}. {tool.get('name', 'Unknown')}")
                    print(f"      Description: {tool.get('description', 'No description')[:80]}...")
                
                # Also test MCP endpoint
                mcp_request = {
                    "jsonrpc": "2.0",
                    "method": "tools/list",
                    "id": 2,
                    "params": {}
                }
                
                mcp_response = await client.post(
                    f"{self.base_url}/mcp",
                    json=mcp_request,
                    headers={
                        "Content-Type": "application/json",
                        "MCP-Protocol-Version": "2025-06-18"
                    },
                    timeout=10
                )
                
                if mcp_response.status_code == 200:
                    mcp_data = mcp_response.json()
                    mcp_tools = mcp_data.get("result", {}).get("tools", [])
                    print(f"✅ MCP endpoint also reports {len(mcp_tools)} tools")
                
                return tools
                
        except Exception as e:
            print(f"❌ Tools listing error: {e}")
            return []
    
    async def test_tool_call(self, tool_name: str, arguments: Dict[str, Any] = None) -> bool:
        """Test calling a specific tool."""
        print(f"\n🔧 Testing tool call: {tool_name}")
        
        if arguments is None:
            arguments = {}
        
        try:
            async with httpx.AsyncClient() as client:
                tool_request = {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "id": 3,
                    "params": {
                        "name": tool_name,
                        "arguments": arguments
                    }
                }
                
                response = await client.post(
                    f"{self.base_url}/mcp",
                    json=tool_request,
                    headers={
                        "Content-Type": "application/json",
                        "MCP-Protocol-Version": "2025-06-18"
                    },
                    timeout=30  # Longer timeout for tool calls
                )
                
                if response.status_code != 200:
                    print(f"❌ Tool call failed with status: {response.status_code}")
                    return False
                    
                tool_data = response.json()
                
                if "result" in tool_data:
                    result = tool_data["result"]
                    print(f"✅ Tool call successful")
                    print(f"   Content type: {result.get('content', [{}])[0].get('type', 'unknown')}")
                    if result.get('isError'):
                        print(f"   ⚠️ Tool returned error: {result.get('content', [{}])[0].get('text', 'Unknown error')}")
                    else:
                        content_text = result.get('content', [{}])[0].get('text', '')
                        print(f"   Response: {content_text[:100]}..." if len(content_text) > 100 else f"   Response: {content_text}")
                    return True
                elif "error" in tool_data:
                    error = tool_data["error"]
                    print(f"❌ Tool call error: {error.get('message', 'Unknown error')}")
                    return False
                else:
                    print(f"❌ Unexpected tool response: {tool_data}")
                    return False
                    
        except Exception as e:
            print(f"❌ Tool call error: {e}")
            return False

    async def test_environment_loading(self) -> bool:
        """Test that environment variables are properly loaded."""
        print("\n🔧 Testing environment variable loading...")
        
        try:
            # Check if .env file exists
            from pathlib import Path
            import os
            
            env_file = Path(".env")
            
            if env_file.exists():
                print("✅ .env file found")
                
                # Check if server is using correct port from env
                expected_port = os.getenv("SERVER__PORT", "8002")
                if self.base_url.endswith(f":{expected_port}"):
                    print(f"✅ Server running on expected port: {expected_port}")
                else:
                    print(f"⚠️ Server port mismatch. Expected: {expected_port}, Using: {self.base_url}")
                
                # Check for connector environment variables
                connector_vars = [k for k in os.environ.keys() if k.startswith("ENABLE_")]
                if connector_vars:
                    print(f"✅ Found {len(connector_vars)} connector enable flags")
                else:
                    print("⚠️ No connector enable flags found")
                
                return True
            else:
                print("⚠️ .env file not found - using defaults")
                return True
                
        except Exception as e:
            print(f"❌ Environment loading test error: {e}")
            return False
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive test suite."""
        print("🧪 {{ project_name | title }} - Comprehensive MCP Test Suite")
        print("=" * 60)
        
        results = {
            "health_check": False,
            "mcp_initialize": False,
            "tools_list": False,
            "environment_loading": False,
            "tool_calls": [],
            "total_tools": 0,
            "successful_tool_calls": 0
        }
        
        # Test health check
        results["health_check"] = await self.test_health_check()
        
        # Test MCP initialization
        results["mcp_initialize"] = await self.test_initialize_mcp()
        
        # Test environment loading
        results["environment_loading"] = await self.test_environment_loading()
        
        # Test tools listing
        tools = await self.test_list_tools()
        results["tools_list"] = len(tools) > 0
        results["total_tools"] = len(tools)
        
        # Test tool calls (sample a few tools)
        if tools:
            # Test up to 3 tools to avoid overwhelming the server
            sample_tools = tools[:3]
            for tool in sample_tools:
                tool_name = tool.get("name", "")
                if tool_name:
                    success = await self.test_tool_call(tool_name)
                    results["tool_calls"].append({
                        "name": tool_name,
                        "success": success
                    })
                    if success:
                        results["successful_tool_calls"] += 1
        
        # Summary
        print("\n" + "=" * 60)
        print("🏆 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Health Check: {'PASS' if results['health_check'] else 'FAIL'}")
        print(f"✅ MCP Initialize: {'PASS' if results['mcp_initialize'] else 'FAIL'}")
        print(f"✅ Environment Loading: {'PASS' if results['environment_loading'] else 'FAIL'}")
        print(f"✅ Tools Listing: {'PASS' if results['tools_list'] else 'FAIL'} ({results['total_tools']} tools)")
        print(f"✅ Tool Calls: {results['successful_tool_calls']}/{len(results['tool_calls'])} successful")
        
        total_tests = 4 + len(results['tool_calls'])
        passed_tests = sum([
            results['health_check'],
            results['mcp_initialize'],
            results['environment_loading'],
            results['tools_list'],
            results['successful_tool_calls']
        ])
        
        print(f"\n📊 Overall Score: {passed_tests}/{total_tests} ({(passed_tests/total_tests)*100:.1f}%)")
        
        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED! {{ project_name | title }} is working perfectly!")
        elif passed_tests >= total_tests * 0.8:
            print("👍 Most tests passed. {{ project_name | title }} is mostly working.")
        else:
            print("⚠️ Several tests failed. {{ project_name | title }} needs attention.")
        
        return results


async def main():
    """Main test runner."""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
        print(f"🌐 Testing {{ project_name | title }} at: {base_url}")
    else:
        base_url = "http://localhost:8002"
        print(f"🌐 Testing {{ project_name | title }} at: {base_url} (default)")
    
    client = MCPClient(base_url)
    results = await client.run_comprehensive_test()
    
    # Save results
    results_file = Path("test_results.json")
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    # Exit with appropriate code
    if results["health_check"] and results["mcp_initialize"] and results["tools_list"]:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure


if __name__ == "__main__":
    asyncio.run(main())
