import os
import yaml
import argparse
import asyncio
import uuid
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv(override=True)

from .base import BaseAgentRunner


class CLIAgent(BaseAgentRunner):
    """CLI Agent for xAgent."""
    
    def __init__(self, config_path: Optional[str] = None, toolkit_path: Optional[str] = None, verbose: bool = False):
        """
        Initialize CLIAgent.
        
        Args:
            config_path: Path to configuration file (if None, uses default configuration)
            toolkit_path: Path to toolkit directory (if None, no additional tools will be loaded)
            verbose: Enable verbose logging output
        """
        # Configure logging based on verbose setting
        self.verbose = verbose
        if not verbose:
            # Suppress most logging except critical errors
            logging.getLogger().setLevel(logging.CRITICAL)
            logging.getLogger("xagent").setLevel(logging.CRITICAL)
        else:
            # Enable verbose logging
            logging.getLogger().setLevel(logging.INFO)
            logging.getLogger("xagent").setLevel(logging.INFO)
        
        # Initialize the base agent runner
        super().__init__(config_path, toolkit_path)
        
        # Store config_path for CLI-specific functionality
        self.config_path = config_path if config_path and os.path.isfile(config_path) else None
        
    async def chat_interactive(self, user_id: str = None, session_id: str = None, stream: bool = None):
        """
        Start an interactive chat session.
        
        Args:
            user_id: User ID for the session
            session_id: Session ID for the chat
            stream: Enable streaming response (default: True, but False when verbose mode is enabled)
        """
        # If stream is not explicitly set, determine based on verbose mode
        if stream is None:
            # When verbose mode is enabled, default to non-streaming for better log readability
            stream = not (logging.getLogger().level <= logging.INFO)
        
        # Check if verbose mode is enabled by checking log level
        verbose_mode = logging.getLogger().level <= logging.INFO
        # Generate default IDs if not provided
        user_id = user_id or f"cli_user_{uuid.uuid4().hex[:8]}"
        session_id = session_id or f"cli_session_{uuid.uuid4().hex[:8]}"
        
        print(f"🤖 Welcome to xAgent CLI!")
        config_msg = f"Loading agent configuration from {self.config_path}" if self.config_path else "Using default configuration"
        print(config_msg)
        print(f"Agent: {self.agent.name}")
        print(f"Model: {self.agent.model}")
        print(f"Tools: {len(self.agent.tools)} loaded")
        print(f"Session: {session_id}")
        print(f"Verbose mode: {'Enabled' if verbose_mode else 'Disabled'}")
        print(f"Streaming: {'Enabled' if stream else 'Disabled'}")
        if verbose_mode and stream:
            print("ℹ️  Note: Verbose mode is enabled. Consider using 'stream off' for better log readability.")
        print("Type 'exit', 'quit', or 'bye' to end the session.")
        print("Type 'clear' to clear the session history.")
        print("Type 'stream on/off' to toggle streaming mode.")
        print("Type 'help' for available commands.")
        print("-" * 50)
        
        while True:
            try:
                # Get user input
                user_input = input("\n👤 You: ").strip()
                
                # Handle special commands
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'clear':
                    await self.message_storage.clear_history(user_id, session_id)
                    print("🧹 Session history cleared.")
                    continue
                elif user_input.lower().startswith('stream '):
                    # Handle stream toggle command
                    stream_cmd = user_input.lower().split()
                    if len(stream_cmd) == 2:
                        if stream_cmd[1] == 'on':
                            stream = True
                            print("🌊 Streaming mode enabled.")
                        elif stream_cmd[1] == 'off':
                            stream = False
                            print("📄 Streaming mode disabled.")
                        else:
                            print("⚠️  Usage: stream on/off")
                    else:
                        print("⚠️  Usage: stream on/off")
                    continue
                elif user_input.lower() == 'help':
                    self._show_help()
                    continue
                elif not user_input:
                    continue
                
                # Process the message
                if stream:
                    # Handle streaming response
                    response_generator = await self.agent(
                        user_message=user_input,
                        user_id=user_id,
                        session_id=session_id,
                        stream=True
                    )
                    
                    # Check if response is a generator (streaming) or a string
                    if hasattr(response_generator, '__aiter__'):
                        print("🤖 Agent: ", end="", flush=True)
                        async for chunk in response_generator:
                            if chunk:
                                print(chunk, end="", flush=True)
                        print()  # Add newline after streaming is complete
                    else:
                        # Fallback for non-streaming response
                        print("🤖 Agent: " + str(response_generator))
                else:
                    # Handle non-streaming response
                    response = await self.agent(
                        user_message=user_input,
                        user_id=user_id,
                        session_id=session_id,
                        stream=False
                    )
                    print("🤖 Agent: " + str(response))
                
            except KeyboardInterrupt:
                print("\n\n👋 Session interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
    
    async def chat_single(self, message: str, user_id: str = None, session_id: str = None):
        """
        Process a single message and return the response.
        
        Args:
            message: The message to process
            user_id: User ID for the session
            session_id: Session ID for the chat
            
        Returns:
            Agent response string
        """
        # Generate default IDs if not provided
        user_id = user_id or f"cli_user_{uuid.uuid4().hex[:8]}"
        session_id = session_id or f"cli_session_{uuid.uuid4().hex[:8]}"
        
        response = await self.agent(
            user_message=message,
            user_id=user_id,
            session_id=session_id,
            stream=False
        )
        
        return response
    
    def _show_help(self):
        """Show help information."""
        print("\n📋 Available commands:")
        print("  exit, quit, bye  - Exit the chat session")
        print("  clear           - Clear session history")
        print("  stream on/off   - Toggle streaming mode")
        print("  help            - Show this help message")
        print("\n🔧 Available tools:")
        for tool_name in self.agent.tools.keys():
            print(f"  - {tool_name}")
        if self.agent.mcp_tools:
            print("\n🌐 MCP tools:")
            for tool_name in self.agent.mcp_tools.keys():
                print(f"  - {tool_name}")
    
    def create_default_config(self, config_path: str = "config/agent.yaml"):
        """
        Create a default configuration file.
        
        Args:
            config_path: Path where to create the config file
        """
        # Create directory if it doesn't exist
        config_dir = os.path.dirname(config_path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        default_config = self._get_default_config()
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
        
        print(f"✅ Default configuration created at: {config_path}")
        print("You can edit this file to customize your agent settings.")


def create_default_config_file(config_path: str = "config/agent.yaml"):
    """
    Create a default configuration file.
    
    Args:
        config_path: Path where to create the config file
    """
    # Create directory if it doesn't exist
    config_dir = os.path.dirname(config_path)
    if config_dir and not os.path.exists(config_dir):
        os.makedirs(config_dir)
    
    # Use the default configuration from BaseAgentRunner
    dummy_runner = BaseAgentRunner()
    default_config = dummy_runner._get_default_config()
    
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)
    
    print(f"✅ Default configuration created at: {config_path}")
    print("You can edit this file to customize your agent settings.")


def main():
    """Main entry point for xagent-cli command."""
    parser = argparse.ArgumentParser(description="xAgent CLI - Interactive chat agent")
    
    # Main command arguments (no subcommands)
    parser.add_argument("--config", default=None, help="Config file path (if not specified, uses default configuration)")
    parser.add_argument("--toolkit_path", default=None, help="Toolkit directory path (if not specified, no additional tools will be loaded)")
    parser.add_argument("--user_id", help="User ID for the session")
    parser.add_argument("--session_id", help="Session ID for the chat")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--no-stream", action="store_true", help="Disable streaming response (default: streaming enabled)")
    
    # Special commands as optional arguments
    parser.add_argument("--ask", metavar="MESSAGE", help="Ask a single question instead of starting interactive chat")
    parser.add_argument("--init", action="store_true", help="Create default configuration file and exit")
    parser.add_argument("--init-config", default="config/agent.yaml", help="Config file path to create when using --init")
    
    # Parse arguments
    args = parser.parse_args()
    
    try:
        # Handle init command
        if args.init:
            create_default_config_file(args.init_config)
            return
        
        # Handle single question
        if args.ask:
            cli_agent = CLIAgent(
                config_path=args.config,
                toolkit_path=args.toolkit_path,
                verbose=args.verbose
            )
            response = asyncio.run(cli_agent.chat_single(
                message=args.ask,
                user_id=args.user_id,
                session_id=args.session_id
            ))
            print(response)
            return
        
        # Default behavior: start interactive chat
        cli_agent = CLIAgent(
            config_path=args.config,
            toolkit_path=args.toolkit_path,
            verbose=args.verbose
        )
        
        # Determine stream setting - if --no-stream is specified, use False
        # Otherwise, let chat_interactive decide based on verbose mode
        stream_setting = None if not args.no_stream else False
        asyncio.run(cli_agent.chat_interactive(
            user_id=args.user_id,
            session_id=args.session_id,
            stream=stream_setting
        ))
            
    except Exception as e:
        print(f"Failed to start CLI: {e}")
        raise


if __name__ == "__main__":
    main()
