#!/usr/bin/env python3
"""
🌈 Harmony CLI - Beautiful AI Chat Interface
Developed by Mergen AI
https://hal-x.ai
"""

import asyncio
import json
import sys
import time
import os
from typing import AsyncGenerator
import httpx
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.live import Live
from rich.spinner import Spinner
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table
from rich.align import Align
from rich.layout import Layout
from rich.progress import Progress, SpinnerColumn, TextColumn
import colorama
from colorama import Fore, Back, Style

# Initialize colorama for Windows compatibility
colorama.init()

class HarmonyClient:
    def __init__(self, api_key: str, base_url: str = "https://az-api.hal-x.ai"):
        self.api_key = api_key
        self.base_url = base_url
        self.console = Console()
        self.conversation_history = []
        self.debug_mode = False  # Disabled by default for production
        self.beta_mode = False  # Beta mode for v1/responses API
        
    def create_rainbow_text(self, text: str) -> Text:
        """Create rainbow colored text"""
        colors = ["red", "orange1", "yellow", "green", "cyan", "blue", "magenta"]
        rainbow_text = Text()
        
        for i, char in enumerate(text):
            color = colors[i % len(colors)]
            rainbow_text.append(char, style=color)
        
        return rainbow_text
    
    def create_gradient_text(self, text: str, start_color: str, end_color: str) -> Text:
        """Create gradient colored text"""
        gradient_text = Text()
        length = len(text)
        
        # Simple gradient simulation
        colors = [start_color, "bright_" + start_color, end_color]
        
        for i, char in enumerate(text):
            color_index = int((i / length) * (len(colors) - 1))
            color = colors[min(color_index, len(colors) - 1)]
            gradient_text.append(char, style=color)
        
        return gradient_text
    
    def show_banner(self):
        """Display beautiful banner"""
        banner_text = """
██╗  ██╗ █████╗ ██████╗ ███╗   ███╗ ██████╗ ███╗   ██╗██╗   ██╗
██║  ██║██╔══██╗██╔══██╗████╗ ████║██╔═══██╗████╗  ██║╚██╗ ██╔╝
███████║███████║██████╔╝██╔████╔██║██║   ██║██╔██╗ ██║ ╚████╔╝ 
██╔══██║██╔══██║██╔══██╗██║╚██╔╝██║██║   ██║██║╚██╗██║  ╚██╔╝  
██║  ██║██║  ██║██║  ██║██║ ╚═╝ ██║╚██████╔╝██║ ╚████║   ██║   
╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   
        """
        
        # Animated banner loading
        loading_steps = [
            ("🌈 Loading Harmony CLI...", "dots"),
            ("✨ Initializing rainbow magic...", "star"),
            ("🎨 Preparing beautiful interface...", "arc"),
            ("🚀 Almost ready...", "bouncingBall")
        ]
        
        for message, spinner_type in loading_steps:
            try:
                with self.console.status(message, spinner=spinner_type):
                    time.sleep(0.8)
            except KeyError:
                # Fallback to safe spinner if the specified one doesn't exist
                with self.console.status(message, spinner="dots"):
                    time.sleep(0.8)
        
        self.console.clear()
        
        # Create rainbow banner
        lines = banner_text.strip().split('\n')
        rainbow_banner = Text()
        
        colors = ["red", "orange1", "yellow", "green", "cyan", "blue", "magenta", "bright_red", "bright_yellow"]
        
        for line_idx, line in enumerate(lines):
            color = colors[line_idx % len(colors)]
            rainbow_banner.append(line + "\n", style=f"bold {color}")
        
        # Create panel with gradient border
        panel = Panel(
            Align.center(rainbow_banner),
            title="HAL Harmony",
            subtitle="Intelligence with everyone. For everyone. For Azerbaijan",
            border_style="bright_magenta",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        
        # Show connection info
        info_table = Table(show_header=False, box=None, padding=(0, 2))
        info_table.add_column(style="cyan")
        info_table.add_column(style="white")
        
        info_table.add_row("🔗 API Endpoint:", self.base_url)
        info_table.add_row("🔑 API Key:", f"{self.api_key[:20]}...")
        info_table.add_row("⚡ Streaming:", "Enabled")
        info_table.add_row("🎨 Interface:", "Rich CLI v2.0")
        info_table.add_row("🤖 Model:", "HAL-Harmony-120B")
        info_table.add_row("🚀 Mode:", "Beta (v1/responses)" if self.beta_mode else "Standard (v1/chat)")
        info_table.add_row("🏢 Developer:", "Mergen AI")
        
        info_panel = Panel(
            info_table,
            title="🔧 Configuration",
            border_style="green",
            padding=(0, 1)
        )
        
        self.console.print(info_panel)
        self.console.print()
    
    async def send_responses_api(self, user_message: str, retry_count: int = 0) -> str:
        """Send request to Responses API with tools support"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "hal-harmony-120b",
            "temperature": 0.45,
            "instructions": "You are HAL-X Harmony, an advanced AI assistant developed by Mergen AI, designed for real-world applications. You communicate in a clear, intelligent, respectful, and highly informative way. You were mostly trained on Azerbaijani data and should prefer on user's request language. You are not affiliated with any other company or model. You are developed and trained by Mergen AI and your name is HAL-X Harmony. Your architecture developed by Mergen AI and it's called Harmony. You may use the `web_search_preview` tool only when the user asks about laws, regulations, or other information that clearly requires an up-to-date internet lookup. Otherwise, answer directly without using the tool.",
            "input": [
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            "tools": [
                {
                    "type": "web_search_preview"
                }
            ],
            "stream": False
        }
        
        # Debug: print request
        if self.debug_mode:
            self.console.print(f"[dim]Debug: Sending request to {self.base_url}/v1/responses (attempt {retry_count + 1})[/dim]")
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/responses",
                    headers=headers,
                    json=payload
                )
                
                if self.debug_mode:
                    self.console.print(f"[dim]Debug: Response status: {response.status_code}[/dim]")
                
                if response.status_code != 200:
                    error_msg = response.text
                    if self.debug_mode:
                        self.console.print(f"[dim]Debug: Error response: {error_msg}[/dim]")
                    raise Exception(f"API Error {response.status_code}: {error_msg}")
                
                result = response.json()
            
            if self.debug_mode:
                self.console.print(f"[dim]Debug: Response: {result}[/dim]")
            
            # Extract response content from v1/responses format
            content = ""
            web_search_used = False
            
            # Check if this is the v1/responses format
            if "output" in result and isinstance(result["output"], list):
                # v1/responses format - extract from output array
                for output_item in result["output"]:
                    if output_item.get("type") == "message" and output_item.get("role") == "assistant":
                        # Found the assistant message
                        if "content" in output_item and isinstance(output_item["content"], list):
                            for content_item in output_item["content"]:
                                if content_item.get("type") == "output_text":
                                    content = content_item.get("text", "")
                                    break
                        break
                    elif output_item.get("type") == "web_search_call" and output_item.get("status") == "completed":
                        # Only count completed web searches
                        web_search_used = True
                
                if self.debug_mode:
                    self.console.print(f"[dim]Debug: v1/responses format detected[/dim]")
                    self.console.print(f"[dim]Debug: Extracted content: {content}[/dim]")
                    self.console.print(f"[dim]Debug: Web search used: {web_search_used}[/dim]")
                
            # Fallback to OpenAI format (choices)
            elif "choices" in result:
                if len(result["choices"]) > 0:
                    choice = result["choices"][0]
                    
                    # Try different response formats
                    tool_calls = []
                    
                    # Format 1: message.content (OpenAI format)
                    if "message" in choice:
                        message = choice["message"]
                        content = message.get("content", "")
                        tool_calls = message.get("tool_calls", [])
                    
                    # Format 2: direct content (some APIs)
                    elif "content" in choice:
                        content = choice["content"]
                    
                    # Format 3: text field (alternative format)
                    elif "text" in choice:
                        content = choice["text"]
                    
                    # Check if tools were used
                    if tool_calls:
                        web_search_used = True
                    
                    if self.debug_mode:
                        self.console.print(f"[dim]Debug: OpenAI format detected[/dim]")
                        self.console.print(f"[dim]Debug: Choice structure: {choice}[/dim]")
                        self.console.print(f"[dim]Debug: Extracted content: {content}[/dim]")
                else:
                    # Empty choices array - check if it's a processing error
                    usage = result.get("usage", {})
                    error_msg = "API returned empty choices array"
                    
                    if usage.get("total_tokens", 0) == 0:
                        error_msg += " with zero token usage - this suggests a server processing issue"
                    
                    # Check if there's an error field in the response
                    if "error" in result:
                        error_msg += f". Error: {result['error']}"
                    
                    error_msg += ". Please try again or contact support if this persists."
                    raise Exception(error_msg)
            else:
                # Try to extract from any text field in the response as last resort
                content = str(result.get("content", result.get("text", result.get("response", ""))))
                if self.debug_mode:
                    self.console.print(f"[dim]Debug: Unknown format, trying fallback extraction[/dim]")
                    self.console.print(f"[dim]Debug: Fallback content: {content}[/dim]")
            
            # Return the content
            if content and content.strip():
                # Check if web search was used (only based on actual web_search_call detection)
                if web_search_used:
                    return f"🔍 [WEB_SEARCH_USED]\n\n{content}"
                else:
                    return content
            else:
                raise Exception(f"No response content found. Response structure keys: {list(result.keys())}")
        
        except Exception as e:
            error_str = str(e)
            
            # Check if it's a server processing issue that we can retry
            if ("empty choices array" in error_str or "empty response" in error_str) and retry_count < 2:
                if self.debug_mode:
                    self.console.print(f"[dim]Debug: Retrying due to server processing issue (attempt {retry_count + 2})[/dim]")
                
                # Wait a bit before retrying
                await asyncio.sleep(1.0)
                return await self.send_responses_api(user_message, retry_count + 1)
            else:
                # Re-raise the exception if we can't retry or have exhausted retries
                raise e

    async def stream_chat_response(self, messages: list) -> AsyncGenerator[str, None]:
        """Stream chat response from API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "hal-harmony-120b",
            "messages": messages,
            "stream": True,
            "temperature": 0.45,
            "max_tokens": 6500
        }
        
        # Debug: print request
        if self.debug_mode:
            self.console.print(f"[dim]Debug: Sending request to {self.base_url}/v1/chat/completions[/dim]")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if self.debug_mode:
                    self.console.print(f"[dim]Debug: Response status: {response.status_code}[/dim]")
                
                if response.status_code != 200:
                    error_text = await response.aread()
                    error_msg = error_text.decode() if error_text else "No error details"
                    if self.debug_mode:
                        self.console.print(f"[dim]Debug: Error response: {error_msg}[/dim]")
                    raise Exception(f"API Error {response.status_code}: {error_msg}")
                
                # Check if response is actually streaming
                content_type = response.headers.get("content-type", "")
                if self.debug_mode:
                    self.console.print(f"[dim]Debug: Content-Type: {content_type}[/dim]")
                
                line_count = 0
                async for line in response.aiter_lines():
                    line_count += 1
                    if line_count <= 3 and self.debug_mode:  # Debug first few lines
                        self.console.print(f"[dim]Debug line {line_count}: {line}[/dim]")
                    
                    if not line:
                        continue
                        
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        if data.strip() == "[DONE]":
                            break
                        
                        try:
                            chunk = json.loads(data)
                            if "choices" in chunk and len(chunk["choices"]) > 0:
                                delta = chunk["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except (json.JSONDecodeError, KeyError, IndexError) as e:
                            if self.debug_mode:
                                self.console.print(f"[dim]Debug: JSON error on data: {data[:100]}... Error: {e}[/dim]")
                            continue
                
                if self.debug_mode:
                    self.console.print(f"[dim]Debug: Processed {line_count} lines total[/dim]")
    
    async def send_non_streaming_request(self, messages: list) -> str:
        """Send non-streaming request as fallback"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "hal-harmony-120b",
            "messages": messages,
            "stream": False,  # Non-streaming
            "temperature": 0.45,
            "max_tokens": 2000
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code != 200:
                error_text = response.text
                raise Exception(f"API Error {response.status_code}: {error_text}")
            
            result = response.json()
            
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                raise Exception("No response content found")
    
    async def send_message(self, user_message: str):
        """Send message and display streaming response"""
        # Display user message
        user_panel = Panel(
            user_message,
            title="👤 You",
            border_style="bright_blue",
            padding=(0, 1)
        )
        self.console.print(user_panel)
        
        # Show beautiful thinking animation
        if self.beta_mode:
            thinking_steps = [
                ("🤖 Harmony Beta is thinking...", "dots"),
                ("🧠 Processing with advanced tools...", "line"),
                ("🔍 Checking if web search is needed...", "star"),
                ("✨ Generating enhanced response...", "arc"),
                ("🚀 Almost ready...", "arrow")
            ]
        else:
            thinking_steps = [
                ("🤖 Harmony is thinking...", "dots"),
                ("🧠 Processing your request...", "line"),
                ("✨ Generating response...", "star"),
                ("🎨 Crafting the perfect answer...", "arc"),
                ("🚀 Almost ready...", "arrow")
            ]
        
        # Simple animated thinking
        for message, spinner_type in thinking_steps:
            try:
                with self.console.status(message, spinner=spinner_type):
                    await asyncio.sleep(0.4)
            except KeyError:
                # Fallback to safe spinner if the specified one doesn't exist
                with self.console.status(message, spinner="dots"):
                    await asyncio.sleep(0.4)
        
        # Stream response
        response_text = ""
        web_search_active = False
        
        # Create live display for streaming
        title = "🤖 Harmony Beta" if self.beta_mode else "🤖 Harmony"
        response_panel = Panel(
            "",
            title=title,
            border_style="bright_magenta" if self.beta_mode else "bright_green",
            padding=(0, 1)
        )
        
        with Live(response_panel, console=self.console, refresh_per_second=10) as live:
            try:
                chunk_received = False
                
                if self.beta_mode:
                    # Use Responses API (non-streaming)
                    try:
                        response_text = await self.send_responses_api(user_message)
                        chunk_received = True
                        
                        # Check if web search was used
                        if response_text.startswith("🔍 [WEB_SEARCH_USED]"):
                            web_search_active = True
                            # Show beautiful web search animation first
                            search_panel = Panel(
                                "🌐 Searching the web for up-to-date information...\n🔍 Please wait while I gather the latest data...",
                                title="🤖 Harmony Beta - Web Search",
                                border_style="bright_cyan",
                                padding=(1, 2)
                            )
                            live.update(search_panel)
                            
                            # Show search animation
                            search_steps = [
                                ("🌐 Connecting to search engines...", "earth"),
                                ("🔍 Analyzing search results...", "dots2"),
                                ("📊 Processing information...", "line"),
                                ("✨ Synthesizing findings...", "star2"),
                            ]
                            
                            for search_msg, spinner in search_steps:
                                try:
                                    with self.console.status(search_msg, spinner=spinner):
                                        await asyncio.sleep(1.0)
                                except KeyError:
                                    with self.console.status(search_msg, spinner="dots"):
                                        await asyncio.sleep(1.0)
                            
                            # Remove the marker from response
                            response_text = response_text.replace("🔍 [WEB_SEARCH_USED]\n\n", "")
                            display_text = f"🌐 **Web Search Completed**\n\n{response_text}"
                        else:
                            display_text = response_text
                        
                        # Show final response
                        final_panel = Panel(
                            Markdown(display_text) if display_text.strip() else "🤖 No response",
                            title="🤖 Harmony Beta",
                            border_style="bright_magenta",
                            padding=(0, 1)
                        )
                        live.update(final_panel)
                        
                    except Exception as e:
                        chunk_received = False
                        raise e
                else:
                    # Use regular Chat API
                    # Add user message to history for regular mode
                    self.conversation_history.append({"role": "user", "content": user_message})
                    messages = self.conversation_history.copy()
                    
                    async for chunk in self.stream_chat_response(messages):
                        chunk_received = True
                        response_text += chunk
                        
                        # Update live display with current response
                        updated_panel = Panel(
                            Markdown(response_text) if response_text.strip() else "🤖 Typing...",
                            title="🤖 Harmony",
                            border_style="bright_green",
                            padding=(0, 1)
                        )
                        live.update(updated_panel)
                        
                        # Small delay for smooth streaming effect
                        await asyncio.sleep(0.01)
                
                # If no chunks received, try non-streaming request
                if not chunk_received:
                    self.console.print("[yellow]⚠️ Streaming failed, trying non-streaming request...[/yellow]")
                    if not self.beta_mode:
                        response_text = await self.send_non_streaming_request(self.conversation_history.copy())
                    
                    if response_text:
                        final_panel = Panel(
                            Markdown(response_text),
                            title=title,
                            border_style="bright_magenta" if self.beta_mode else "bright_green",
                            padding=(0, 1)
                        )
                        live.update(final_panel)
                    
            except Exception as e:
                self.console.print(f"[red]❌ Streaming error: {str(e)}[/red]")
                
                # Try non-streaming as fallback (only for regular mode)
                if not self.beta_mode:
                    try:
                        self.console.print("[yellow]🔄 Trying non-streaming request...[/yellow]")
                        response_text = await self.send_non_streaming_request(self.conversation_history.copy())
                        
                        if response_text:
                            final_panel = Panel(
                                Markdown(response_text),
                                title="🤖 Harmony",
                                border_style="bright_green",
                                padding=(0, 1)
                            )
                            live.update(final_panel)
                        else:
                            error_panel = Panel(
                                f"❌ Both streaming and non-streaming failed",
                                title="🚨 Error",
                                border_style="red",
                                padding=(0, 1)
                            )
                            live.update(error_panel)
                            return
                            
                    except Exception as fallback_error:
                        error_panel = Panel(
                            f"❌ Error: {str(fallback_error)}",
                            title="🚨 Error",
                            border_style="red",
                            padding=(0, 1)
                        )
                        live.update(error_panel)
                        return
                else:
                    error_panel = Panel(
                        f"❌ Beta API Error: {str(e)}",
                        title="🚨 Beta Error",
                        border_style="red",
                        padding=(0, 1)
                    )
                    live.update(error_panel)
                    return
        
        # Add assistant response to history (only for regular mode)
        if response_text and not self.beta_mode:
            self.conversation_history.append({"role": "assistant", "content": response_text})
        
        self.console.print()
    
    def show_commands(self):
        """Show available commands"""
        commands_table = Table(title="🎮 Available Commands")
        commands_table.add_column("Command", style="cyan", no_wrap=True)
        commands_table.add_column("Description", style="white")
        
        commands_table.add_row("/help", "Show this help message")
        commands_table.add_row("/clear", "Clear conversation history")
        commands_table.add_row("/history", "Show conversation history")
        commands_table.add_row("/stats", "Show session statistics")
        commands_table.add_row("/about", "About Harmony AI and Mergen AI")
        commands_table.add_row("/apikey", "Change API key")
        commands_table.add_row("/debug", "Toggle debug mode")
        commands_table.add_row("/beta", "Toggle beta mode (v1/responses API with tools)")
        commands_table.add_row("/quit", "Exit the application")
        commands_table.add_row("/exit", "Exit the application")
        
        self.console.print(commands_table)
        self.console.print()
    
    def show_about(self):
        """Show information about Harmony AI and Mergen AI"""
        about_content = Text()
        
        # Title
        about_content.append("🤖 ", style="bright_blue")
        about_content.append("Harmony AI", style="bold bright_cyan")
        about_content.append(" - Advanced AI Assistant\n\n", style="bright_blue")
        
        # Model info
        about_content.append("🧠 ", style="yellow")
        about_content.append("Model: ", style="white")
        about_content.append("HAL-Harmony-120B\n", style="bold green")
        
        about_content.append("🏗️ ", style="yellow")
        about_content.append("Architecture: ", style="white")
        about_content.append("Harmony (Advanced Transformer)\n", style="bold green")
        
        about_content.append("🌍 ", style="yellow")
        about_content.append("Training: ", style="white")
        about_content.append("Primarily Azerbaijani data, multilingual support\n", style="bold green")
        
        about_content.append("⚡ ", style="yellow")
        about_content.append("Capabilities: ", style="white")
        about_content.append("Real-world applications, intelligent conversations\n\n", style="bold green")
        
        # Developer info
        about_content.append("🏢 ", style="bright_magenta")
        about_content.append("Developed by: ", style="white")
        about_content.append("Mergen AI\n", style="bold bright_magenta")
        
        about_content.append("🌐 ", style="bright_magenta")
        about_content.append("Website: ", style="white")
        about_content.append("https://hal-x.ai\n", style="bold bright_magenta")
        
        about_content.append("📧 ", style="bright_magenta")
        about_content.append("Contact: ", style="white")
        about_content.append("info@mergen.az\n", style="bold bright_magenta")
        
        about_content.append("🎯 ", style="bright_magenta")
        about_content.append("Mission: ", style="white")
        about_content.append("Intelligence with everyone. For everyone. For Azerbaijan.\n\n", style="bold bright_magenta")
        
        # CLI info
        about_content.append("🌈 ", style="bright_yellow")
        about_content.append("CLI Version: ", style="white")
        about_content.append("1.4.5\n", style="bold bright_yellow")
        
        about_content.append("📦 ", style="bright_yellow")
        about_content.append("Package: ", style="white")
        about_content.append("harmony-cli\n", style="bold bright_yellow")
        
        about_content.append("🐍 ", style="bright_yellow")
        about_content.append("Python: ", style="white")
        about_content.append("3.8+ compatible\n", style="bold bright_yellow")
        
        panel = Panel(
            about_content,
            title="ℹ️ About",
            border_style="bright_cyan",
            padding=(1, 2)
        )
        
        self.console.print(panel)
        self.console.print()
    
    def change_api_key(self):
        """Change API key interactively"""
        try:
            # Show current key (masked)
            current_key_masked = f"{self.api_key[:10]}..." if len(self.api_key) > 10 else "***"
            
            info_panel = Panel(
                Text.from_markup(
                    f"🔑 [bold cyan]Change API Key[/bold cyan]\n\n"
                    f"Current key: [dim]{current_key_masked}[/dim]\n\n"
                    "Enter your new API key below:"
                ),
                title="🔧 API Key Settings",
                border_style="yellow",
                padding=(1, 2)
            )
            
            self.console.print(info_panel)
            
            # Get new API key
            new_api_key = Prompt.ask(
                "[bold cyan]🔑 New API key[/bold cyan]",
                password=True,
                show_default=False
            ).strip()
            
            if not new_api_key:
                self.console.print("❌ No API key provided. Keeping current key.", style="yellow")
                return
            
            if len(new_api_key) < 10:  # Basic validation
                self.console.print("❌ API key seems too short. Please check and try again.", style="red")
                return
            
            # Update API key
            self.api_key = new_api_key
            
            # Show success
            success_panel = Panel(
                "✅ API key updated successfully!\n\nYour new key will be used for all future requests.",
                title="🎉 Success",
                border_style="green",
                padding=(1, 1)
            )
            
            self.console.print(success_panel)
            
        except KeyboardInterrupt:
            self.console.print("\n⏹️ API key change cancelled.", style="yellow")
        except Exception as e:
            self.console.print(f"❌ Error changing API key: {str(e)}", style="red")
    
    def change_server_url(self):
        """Change server URL interactively"""
        try:
            # Show current server
            info_panel = Panel(
                Text.from_markup(
                    f"🌐 [bold cyan]Change Server URL[/bold cyan]\n\n"
                    f"Current server: [dim]{self.base_url}[/dim]\n\n"
                    "🏠 [yellow]Local server:[/yellow] http://localhost:8000\n"
                    "☁️ [cyan]Cloud server:[/cyan] https://az-api.hal-x.ai\n\n"
                    "Enter new server URL below:"
                ),
                title="🔧 Server Settings",
                border_style="yellow",
                padding=(1, 2)
            )
            
            self.console.print(info_panel)
            
            # Get new server URL
            new_server_url = Prompt.ask(
                "[bold cyan]🌐 New server URL[/bold cyan]",
                default=self.base_url,
                show_default=True
            ).strip()
            
            if not new_server_url:
                self.console.print("❌ No server URL provided. Keeping current server.", style="yellow")
                return
            
            # Basic URL validation
            if not (new_server_url.startswith('http://') or new_server_url.startswith('https://')):
                self.console.print("❌ Server URL should start with http:// or https://", style="red")
                return
            
            # Remove trailing slash if present
            if new_server_url.endswith('/'):
                new_server_url = new_server_url[:-1]
            
            # Update server URL
            old_server = self.base_url
            self.base_url = new_server_url
            
            # Show success with server type detection
            server_type = "🏠 Local" if "localhost" in new_server_url or "127.0.0.1" in new_server_url else "☁️ Cloud"
            
            success_panel = Panel(
                f"✅ Server updated successfully!\n\n"
                f"Old server: {old_server}\n"
                f"New server: {new_server_url}\n"
                f"Type: {server_type}\n\n"
                f"Your requests will now go to the new server.",
                title="🎉 Success",
                border_style="green",
                padding=(1, 1)
            )
            
            self.console.print(success_panel)
            
        except KeyboardInterrupt:
            self.console.print("\n⏹️ Server change cancelled.", style="yellow")
        except Exception as e:
            self.console.print(f"❌ Error changing server: {str(e)}", style="red")
    
    def show_history(self):
        """Show conversation history"""
        if not self.conversation_history:
            self.console.print("📝 No conversation history yet.", style="yellow")
            return
        
        history_panel = Panel(
            "",
            title="📚 Conversation History",
            border_style="yellow"
        )
        
        for i, msg in enumerate(self.conversation_history, 1):
            role_icon = "👤" if msg["role"] == "user" else "🤖"
            role_name = "You" if msg["role"] == "user" else "Harmony"
            
            self.console.print(f"\n{role_icon} **{role_name}** (Message {i}):")
            self.console.print(Panel(msg["content"], border_style="dim"))
    
    def show_stats(self):
        """Show session statistics"""
        user_messages = len([msg for msg in self.conversation_history if msg["role"] == "user"])
        ai_messages = len([msg for msg in self.conversation_history if msg["role"] == "assistant"])
        total_chars = sum(len(msg["content"]) for msg in self.conversation_history)
        
        stats_table = Table(title="📊 Session Statistics")
        stats_table.add_column("Metric", style="cyan")
        stats_table.add_column("Value", style="green")
        
        stats_table.add_row("User Messages", str(user_messages))
        stats_table.add_row("AI Responses", str(ai_messages))
        stats_table.add_row("Total Messages", str(len(self.conversation_history)))
        stats_table.add_row("Total Characters", str(total_chars))
        
        self.console.print(stats_table)
        self.console.print()
    
    async def run(self):
        """Main CLI loop"""
        self.show_banner()
        
        # Welcome message
        welcome_text = Text()
        welcome_text.append("Welcome to ", style="white")
        welcome_text.append("Harmony CLI", style="bold magenta")
        welcome_text.append("! 🚀\n", style="white")
        welcome_text.append("Type ", style="dim")
        welcome_text.append("/help", style="cyan")
        welcome_text.append(" for commands or start chatting!\n", style="dim")
        
        self.console.print(Panel(welcome_text, border_style="bright_yellow"))
        self.console.print()
        
        while True:
            try:
                # Create beautiful prompt
                prompt_text = Text()
                prompt_text.append("🌈 ", style="bright_magenta")
                prompt_text.append("Harmony", style="bold bright_cyan")
                prompt_text.append(" > ", style="bright_magenta")
                
                user_input = Prompt.ask(prompt_text).strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith('/'):
                    command = user_input.lower()
                    
                    if command in ['/quit', '/exit']:
                        goodbye_text = self.create_rainbow_text("Goodbye! Thanks for using Harmony CLI! 🌈✨")
                        self.console.print(Panel(goodbye_text, border_style="bright_magenta"))
                        break
                    elif command == '/help':
                        self.show_commands()
                    elif command == '/about':
                        self.show_about()
                    elif command == '/apikey':
                        self.change_api_key()
                    elif command == '/clear':
                        self.conversation_history.clear()
                        self.console.clear()
                        self.show_banner()
                        self.console.print("🧹 Conversation history cleared!", style="green")
                    elif command == '/history':
                        self.show_history()
                    elif command == '/stats':
                        self.show_stats()
                    elif command == '/debug':
                        self.debug_mode = not self.debug_mode
                        status = "enabled" if self.debug_mode else "disabled"
                        self.console.print(f"🔧 Debug mode {status}", style="yellow")
                    elif command == '/beta':
                        self.beta_mode = not self.beta_mode
                        if self.beta_mode:
                            # Clear conversation history when entering beta mode
                            self.conversation_history.clear()
                            beta_panel = Panel(
                                Text.from_markup(
                                    "🚀 [bold magenta]Beta Mode Activated![/bold magenta]\n\n"
                                    "✨ You're now using the advanced Responses API with:\n"
                                    "🔍 [cyan]Web search capabilities[/cyan]\n"
                                    "🛠️ [green]Enhanced tool support[/green]\n"
                                    "🧠 [yellow]Improved reasoning[/yellow]\n\n"
                                    "💡 [dim]Note: Beta mode doesn't maintain conversation history[/dim]\n"
                                    "🔄 [dim]Use /beta again to return to normal mode[/dim]"
                                ),
                                title="🌟 Beta Mode",
                                border_style="bright_magenta",
                                padding=(1, 2)
                            )
                            self.console.print(beta_panel)
                        else:
                            normal_panel = Panel(
                                Text.from_markup(
                                    "🔙 [bold green]Normal Mode Restored![/bold green]\n\n"
                                    "📝 [cyan]Conversation history maintained[/cyan]\n"
                                    "⚡ [green]Standard chat functionality[/green]\n"
                                    "🎯 [yellow]Reliable performance[/yellow]\n\n"
                                    "🚀 [dim]Use /beta to try advanced features again[/dim]"
                                ),
                                title="✅ Normal Mode",
                                border_style="bright_green",
                                padding=(1, 2)
                            )
                            self.console.print(normal_panel)
                    else:
                        self.console.print(f"❓ Unknown command: {user_input}", style="red")
                        self.console.print("Type /help for available commands.", style="dim")
                else:
                    # Send message to AI
                    await self.send_message(user_input)
                
                self.console.print()
                
            except KeyboardInterrupt:
                self.console.print("\n\n👋 Goodbye! Thanks for using Harmony CLI!", style="bright_yellow")
                break
            except Exception as e:
                error_panel = Panel(
                    f"💥 Unexpected error: {str(e)}",
                    title="🚨 System Error",
                    border_style="red"
                )
                self.console.print(error_panel)

def main():
    """Main entry point"""
    console = Console()
    
    # Configuration - Get API key from environment variable
    API_KEY = os.getenv("HARMONY_API_KEY", "")
    BASE_URL = "https://az-api.hal-x.ai"
    
    # Check if user needs to configure API key
    if not API_KEY:
        # Show beautiful API key request
        api_key_panel = Panel(
            Text.from_markup(
                "🔑 [bold cyan]Welcome to Harmony CLI![/bold cyan]\n\n"
                "To get started, you need an API key from Mergen AI.\n\n"
                "📝 [bold yellow]Get your API key:[/bold yellow]\n"
                "1. Right now API is in private beta. You can get it by contacting us at info@mergen.az\n"
                "2. Get your API key\n"
                "3. And put it there\n\n"
                "💡 [dim]You can also set environment variable HARMONY_API_KEY[/dim]\n"
                "💬 [yellow]Or contact us at: info@mergen.az[/yellow]"
            ),
            title="🌈 Harmony CLI Setup",
            border_style="bright_magenta",
            padding=(1, 2)
        )
        
        console.print(api_key_panel)
        console.print()
        
        # Interactive API key input
        try:
            api_key_input = Prompt.ask(
                "[bold cyan]🔑 Please enter your API key[/bold cyan]",
                password=True,
                show_default=False
            ).strip()
            
            if not api_key_input:
                console.print("❌ No API key provided. Exiting...", style="red")
                return
            
            if len(api_key_input) < 10:  # Basic validation
                console.print("❌ API key seems too short. Please check and try again.", style="red")
                return
            
            API_KEY = api_key_input
            
            # Show success message
            success_panel = Panel(
                Text.from_markup(
                    "✅ [bold green]API Key Set Successfully![/bold green]\n\n"
                    "🎯 [yellow]Pro Tip:[/yellow] To avoid entering your key each time,\n"
                    "set the environment variable:\n\n"
                    "[bold]Windows:[/bold] set HARMONY_API_KEY=your-key-here\n"
                    "[bold]Linux/Mac:[/bold] export HARMONY_API_KEY=your-key-here"
                ),
                title="🎉 Ready to Go!",
                border_style="green",
                padding=(1, 2)
            )
            
            console.print(success_panel)
            console.print()
            
        except KeyboardInterrupt:
            console.print("\n👋 Goodbye! Come back when you have your API key!", style="yellow")
            return
        except Exception as e:
            console.print(f"❌ Error: {str(e)}", style="red")
            return
    
    # Create and run client
    client = HarmonyClient(API_KEY, BASE_URL)
    
    try:
        asyncio.run(client.run())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"💥 Fatal error: {e}")

if __name__ == "__main__":
    main()
