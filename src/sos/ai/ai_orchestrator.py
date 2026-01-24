#!/usr/bin/env python3
"""
AI Orchestrator Service (ai_orchestrator.py)
Runs in Alpine Linux chroot to manage AI-powered system operations

This service integrates Gemini and Claude CLI tools to provide AI-driven
automation, command interpretation, and system orchestration.
"""

import os
import sys
import json
import logging
import subprocess
import time
import re
from pathlib import Path
from typing import Dict, List, Optional
import http.client

# Configuration
LOG_FILE = "/var/log/ai_orchestrator.log"
CONFIG_FILE = "/etc/sos/ai_config.json"
API_GATEWAY_HOST = "127.0.0.1"
API_GATEWAY_PORT = 8888

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ai_orchestrator")


class AIConfig:
    """AI configuration management"""
    
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self):
        """Load AI configuration from file"""
        default_config = {
            "gemini": {
                "enabled": True,
                "model": "gemini-pro",
                "api_key_env": "GEMINI_API_KEY",
                "cli_path": "/usr/local/bin/gemini"
            },
            "claude": {
                "enabled": True,
                "model": "claude-3-sonnet",
                "api_key_env": "ANTHROPIC_API_KEY",
                "cli_path": "/usr/local/bin/claude"
            },
            "preferred_provider": "gemini",
            "max_retries": 3,
            "timeout": 30
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded = json.load(f)
                    default_config.update(loaded)
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        
        return default_config
    
    def save_config(self):
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")


class APIClient:
    """Client for internal API gateway"""
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
    
    def call_api(self, method, endpoint, data=None):
        """Make API call to gateway"""
        try:
            conn = http.client.HTTPConnection(self.host, self.port, timeout=10)
            
            headers = {'Content-Type': 'application/json'}
            body = json.dumps(data) if data else None
            
            conn.request(method, endpoint, body, headers)
            response = conn.getresponse()
            
            result = json.loads(response.read().decode('utf-8'))
            conn.close()
            
            return result
        except Exception as e:
            logger.error(f"API call failed: {e}")
            return {"status": "error", "message": str(e)}


class GeminiProvider:
    """Gemini AI provider integration"""
    
    def __init__(self, config):
        self.config = config
        self.cli_path = config.get("cli_path", "gemini")
        self.model = config.get("model", "gemini-pro")
    
    def is_available(self):
        """Check if Gemini CLI is available"""
        try:
            result = subprocess.run(
                [self.cli_path, "--version"],
                capture_output=True, timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def query(self, prompt, context=None):
        """Query Gemini with a prompt"""
        try:
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {json.dumps(context)}\n\nQuery: {prompt}"
            
            # Call Gemini CLI
            result = subprocess.run(
                [self.cli_path, "chat", "--prompt", full_prompt],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "provider": "gemini",
                    "response": result.stdout.strip()
                }
            else:
                return {
                    "status": "error",
                    "provider": "gemini",
                    "message": result.stderr
                }
        except Exception as e:
            logger.error(f"Gemini query failed: {e}")
            return {"status": "error", "message": str(e)}


class ClaudeProvider:
    """Claude AI provider integration"""
    
    def __init__(self, config):
        self.config = config
        self.cli_path = config.get("cli_path", "claude")
        self.model = config.get("model", "claude-3-sonnet")
    
    def is_available(self):
        """Check if Claude CLI is available"""
        try:
            result = subprocess.run(
                [self.cli_path, "--version"],
                capture_output=True, timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def query(self, prompt, context=None):
        """Query Claude with a prompt"""
        try:
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {json.dumps(context)}\n\nQuery: {prompt}"
            
            # Call Claude CLI
            result = subprocess.run(
                [self.cli_path, "chat", "--prompt", full_prompt],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "provider": "claude",
                    "response": result.stdout.strip()
                }
            else:
                return {
                    "status": "error",
                    "provider": "claude",
                    "message": result.stderr
                }
        except Exception as e:
            logger.error(f"Claude query failed: {e}")
            return {"status": "error", "message": str(e)}


class AIOrchestrator:
    """Main AI orchestration service"""
    
    def __init__(self):
        self.config = AIConfig(CONFIG_FILE)
        self.api_client = APIClient(API_GATEWAY_HOST, API_GATEWAY_PORT)
        
        # Initialize AI providers
        self.providers = {}
        if self.config.config.get("gemini", {}).get("enabled"):
            self.providers["gemini"] = GeminiProvider(self.config.config["gemini"])
        if self.config.config.get("claude", {}).get("enabled"):
            self.providers["claude"] = ClaudeProvider(self.config.config["claude"])
        
        self.preferred_provider = self.config.config.get("preferred_provider", "gemini")
        
        logger.info(f"AI Orchestrator initialized with providers: {list(self.providers.keys())}")
    
    def get_available_provider(self):
        """Get the first available AI provider"""
        # Try preferred provider first
        if self.preferred_provider in self.providers:
            if self.providers[self.preferred_provider].is_available():
                return self.providers[self.preferred_provider]
        
        # Fall back to any available provider
        for name, provider in self.providers.items():
            if provider.is_available():
                return provider
        
        return None
    
    def process_natural_language(self, query):
        """Process natural language query using AI"""
        logger.info(f"Processing query: {query}")
        
        provider = self.get_available_provider()
        if not provider:
            return {
                "status": "error",
                "message": "No AI provider available"
            }
        
        # Get system context
        context = self._get_system_context()
        
        # Construct prompt with system capabilities
        system_prompt = f"""You are an AI assistant controlling an Orbic Speed embedded device.
Available capabilities:
- WiFi scanning and status monitoring
- Cellular modem control
- Display management
- System monitoring
- Network operations

Available API endpoints:
- GET /api/wifi/status - Get WiFi interface status
- GET /api/wifi/scan - Scan for WiFi networks
- GET /api/cellular/status - Get cellular modem status
- GET /api/display/info - Get display information
- GET /api/system/info - Get system information
- POST /api/command - Execute custom command

Current system state: {json.dumps(context)}

User query: {query}

Provide a response that either:
1. Answers the question based on system state
2. Suggests which API to call to get required information
3. Proposes an action plan for complex tasks

Format your response as JSON with fields:
- action: "answer" | "api_call" | "action_plan"
- response: Your answer or explanation
- api_endpoint: (if action is api_call) endpoint to call
- steps: (if action is action_plan) list of steps
"""
        
        result = provider.query(system_prompt)
        return result
    
    def _get_system_context(self):
        """Get current system state for AI context"""
        try:
            system_info = self.api_client.call_api("GET", "/api/system/info")
            return {
                "system": system_info,
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error(f"Failed to get system context: {e}")
            return {}
    
    def execute_ai_action(self, action_spec):
        """Execute an action specified by AI"""
        action = action_spec.get("action")
        
        if action == "api_call":
            endpoint = action_spec.get("api_endpoint")
            method = action_spec.get("method", "GET")
            result = self.api_client.call_api(method, endpoint)
            return result
        elif action == "action_plan":
            steps = action_spec.get("steps", [])
            results = []
            for step in steps:
                logger.info(f"Executing step: {step}")
                # This would be implemented based on step type
                results.append({"step": step, "status": "pending"})
            return {"status": "success", "results": results}
        else:
            return action_spec  # Just return the answer
    
    def interactive_mode(self):
        """Run interactive AI mode"""
        logger.info("Starting interactive AI mode")
        print("AI Orchestrator - Interactive Mode")
        print("Type 'exit' to quit, 'help' for commands")
        print("-" * 50)
        
        while True:
            try:
                query = input("\n> ").strip()
                
                if not query:
                    continue
                
                if query.lower() == 'exit':
                    break
                
                if query.lower() == 'help':
                    print("""
Available commands:
  status - Show system status
  scan - Scan WiFi networks
  info - Show device information
  <natural language> - Ask AI anything
                    """)
                    continue
                
                # Process with AI
                result = self.process_natural_language(query)
                
                if result.get("status") == "success":
                    response = result.get("response", "")
                    print(f"\n{response}")
                    
                    # Try to parse and execute if it's JSON
                    try:
                        action = json.loads(response)
                        if isinstance(action, dict) and "action" in action:
                            exec_result = self.execute_ai_action(action)
                            print(f"\nResult: {json.dumps(exec_result, indent=2)}")
                    except:
                        pass  # Not JSON, just a text response
                else:
                    print(f"Error: {result.get('message', 'Unknown error')}")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                print(f"Error: {e}")


def main():
    """Main entry point"""
    logger.info("Starting AI Orchestrator")
    
    orchestrator = AIOrchestrator()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        orchestrator.interactive_mode()
    else:
        # Run as service
        logger.info("Running in service mode")
        print("AI Orchestrator running. Use --interactive for interactive mode.")


if __name__ == "__main__":
    main()
