import os
import json
import logging
import asyncio
import google.generativeai as genai
from typing import List, Dict, Any
from src.sos.ai.mcp_server import execute_command, read_ui_state, write_ui_state

logger = logging.getLogger("nexus_orchestrator")

class NexusOrchestrator:
    """
    Nexus Gemini Orchestrator: Managing turn-to-turn interactions 
    between Gemini and the Orbic hardware via MCP tools.
    """
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        
        # System instructions for the Field Operator
        self.system_instruction = """
        You are the 'Nexus Field Operator' controlling an Orbic Speed (RC400L) security appliance.
        Your goal is to perform autonomous reconnaissance and auditing.
        
        You have access to the following tools:
        - execute_command: Run shell tools (nmap, iw, scapy).
        - read_ui_state: Get current signal metrics and UI status.
        - write_ui_state: Update the device's framebuffer UI.
        
        Guidelines:
        1. Always analyze metrics before suggesting a vector.
        2. Keep UI updates frequent but concise.
        3. Prioritize targets with high signal strength.
        """
        
        self.model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=self.system_instruction
        )
        self.chat = self.model.start_chat(history=[])

    async def run_turn(self, user_input: str) -> str:
        """
        Executes a single interaction turn with the model.
        """
        logger.info(f"Nexus Turn: {user_input}")
        
        # Get current device context to feed to AI
        context = read_ui_state()
        prompt = f"Device Context: {context}\n\nUser Input: {user_input}"
        
        try:
            response = self.chat.send_message(prompt)
            # Handle tool calls if the SDK is configured for it
            # For now, we'll assume direct text response or planned JSON
            return response.text
        except Exception as e:
            logger.error(f"Nexus Turn failed: {e}")
            return f"Error: {str(e)}"

    def get_history(self):
        return self.chat.history
