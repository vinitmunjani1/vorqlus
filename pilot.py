"""
AI Role Player Chatbot
An interactive chatbot that allows users to select from various AI roles
and have conversations with them using Together AI API.
"""

import json
import sys
from together import Together

# Constants for configuration
EXIT_COMMANDS = ["exit", "quit", "q", "bye"]
MODEL_NAME = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
ROLES_JSON_FILE = "AI_Role_Player_System_Prompts_Formatted.json"

# Simple greetings that should get brief responses
SIMPLE_GREETINGS = ["hi", "hello", "hey", "hey there", "hi there", "greetings", "sup", "what's up"]


def load_ai_roles(json_file_path):
    """
    Load AI roles from JSON file.
    
    Args:
        json_file_path (str): Path to the JSON file containing AI role definitions
        
    Returns:
        list: List of role dictionaries containing role information
        
    Raises:
        FileNotFoundError: If the JSON file doesn't exist
        json.JSONDecodeError: If the JSON file is invalid
    """
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            roles = json.load(file)
        return roles
    except FileNotFoundError:
        print(f"Error: Could not find the roles file '{json_file_path}'")
        print("Please ensure the file exists in the current directory.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in '{json_file_path}': {e}")
        sys.exit(1)


def display_role_menu(roles):
    """
    Display a numbered menu of all available AI roles.
    
    Args:
        roles (list): List of role dictionaries to display
    """
    print("\n" + "=" * 70)
    print("AI ROLE PLAYER CHATBOT - Select an AI Role")
    print("=" * 70)
    print()
    
    for index, role in enumerate(roles, start=1):
        role_name = role.get('role', 'Unknown Role')
        short_desc = role.get('short_description', 'No description available')
        print(f"[{index}] {role_name} - {short_desc}")
    
    print()
    print("=" * 70)


def select_role(roles):
    """
    Prompt user to select a role from the menu and validate the selection.
    
    Args:
        roles (list): List of available role dictionaries
        
    Returns:
        dict: Selected role dictionary
        
    Raises:
        KeyboardInterrupt: If user interrupts with Ctrl+C
    """
    while True:
        try:
            user_input = input(f"\nEnter the number of the role you want to chat with (1-{len(roles)}): ").strip()
            
            # Check for exit commands even during role selection
            if user_input.lower() in EXIT_COMMANDS:
                print("\nExiting... Goodbye!")
                sys.exit(0)
            
            # Validate input is a number
            try:
                role_number = int(user_input)
            except ValueError:
                print(f"Error: Please enter a valid number between 1 and {len(roles)}")
                continue
            
            # Validate number is within range
            if 1 <= role_number <= len(roles):
                selected_role = roles[role_number - 1]
                print(f"\n✓ Selected: {selected_role.get('role', 'Unknown Role')}")
                print(f"  {selected_role.get('long_description', 'No description available')}")
                return selected_role
            else:
                print(f"Error: Please enter a number between 1 and {len(roles)}")
                
        except KeyboardInterrupt:
            print("\n\nExiting... Goodbye!")
            sys.exit(0)
        except EOFError:
            print("\n\nExiting... Goodbye!")
            sys.exit(0)


def initialize_chat(role):
    """
    Initialize the Together AI client and set up the conversation with system prompt.
    
    Args:
        role (dict): Selected role dictionary containing system_prompt
        
    Returns:
        tuple: (Together client, messages list with system prompt)
    """
    try:
        # Initialize Together AI client
        client = Together(api_key="tgp_v1_PGdcyLiSQQVcfUU0T4Acg0kKCcHXg0G6BaixywYYvIs")
        
        # Get the base system prompt from selected role
        base_system_prompt = role.get('system_prompt', '')
        
        # Add instruction to be concise and match user's message length/style
        # This ensures simple greetings get brief responses
        conciseness_instruction = (
            "\n\nIMPORTANT: Keep your responses concise and match the user's communication style. "
            "For simple greetings or short questions, provide brief, friendly responses. "
            "Only provide detailed explanations when the user asks complex questions or requests more information."
        )
        
        # Combine the base system prompt with the conciseness instruction
        enhanced_system_prompt = base_system_prompt + conciseness_instruction
        
        messages = [
            {
                "role": "system",
                "content": enhanced_system_prompt
            }
        ]
        
        return client, messages
        
    except Exception as e:
        print(f"Error initializing chat client: {e}")
        print("Please ensure you have the 'together' package installed and API key configured.")
        sys.exit(1)


def is_simple_greeting(message):
    """
    Check if the user message is a simple greeting that should get a brief response.
    
    Args:
        message (str): User's message
        
    Returns:
        bool: True if message is a simple greeting, False otherwise
    """
    message_lower = message.lower().strip()
    # Check if message is just a greeting (short and matches greeting patterns)
    if len(message_lower.split()) <= 3 and message_lower in SIMPLE_GREETINGS:
        return True
    # Also check if message starts with a greeting and is very short
    if len(message_lower.split()) <= 4:
        for greeting in SIMPLE_GREETINGS:
            if message_lower.startswith(greeting):
                return True
    return False


def run_conversation(client, messages, role_name):
    """
    Run the interactive conversation loop with the selected AI role.
    
    Args:
        client (Together): Together AI client instance
        messages (list): List of conversation messages (starts with system prompt)
        role_name (str): Name of the selected AI role for display purposes
        
    Raises:
        KeyboardInterrupt: If user interrupts with Ctrl+C
    """
    print("\n" + "=" * 70)
    print(f"Chatting with: {role_name}")
    print("Type 'exit', 'quit', 'q', or 'bye' to end the conversation")
    print("=" * 70)
    print()
    
    while True:
        try:
            # Get user input
            user_message = input("You: ").strip()
            
            # Check for exit commands
            if user_message.lower() in EXIT_COMMANDS:
                print(f"\nEnding conversation with {role_name}. Goodbye!")
                break
            
            # Skip empty messages
            if not user_message:
                continue
            
            # Prepare messages for API call
            # If it's a simple greeting, add a temporary instruction for brevity
            api_messages = messages.copy()
            if is_simple_greeting(user_message):
                # Add a temporary instruction before the user message for this specific call
                api_messages.append({
                    "role": "user",
                    "content": user_message + " (Please respond briefly and concisely.)"
                })
            else:
                # Add user message normally
                api_messages.append({
                    "role": "user",
                    "content": user_message
                })
            
            # Call Together AI API with current conversation history
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=api_messages
                )
                
                # Extract AI response
                ai_response = response.choices[0].message.content
                
                # Display AI response
                print(f"\n{role_name}: {ai_response}\n")
                
                # Add user message and AI response to conversation history for context
                # Use the original user message (without the temporary instruction)
                messages.append({
                    "role": "user",
                    "content": user_message
                })
                messages.append({
                    "role": "assistant",
                    "content": ai_response
                })
                
            except Exception as api_error:
                print(f"\nError calling AI API: {api_error}")
                print("Please check your API key and connection, then try again.")
                continue
                
        except KeyboardInterrupt:
            print(f"\n\nEnding conversation with {role_name}. Goodbye!")
            break
        except EOFError:
            print(f"\n\nEnding conversation with {role_name}. Goodbye!")
            break


def main():
    """
    Main function that orchestrates the complete chatbot flow:
    1. Load AI roles from JSON
    2. Display role menu
    3. Get user's role selection
    4. Initialize chat with selected role
    5. Run interactive conversation loop
    """
    try:
        # Load AI roles from JSON file
        roles = load_ai_roles(ROLES_JSON_FILE)
        
        if not roles:
            print("Error: No roles found in the JSON file.")
            sys.exit(1)
        
        # Display role menu
        display_role_menu(roles)
        
        # Get user's role selection
        selected_role = select_role(roles)
        
        # Initialize chat with selected role
        client, messages = initialize_chat(selected_role)
        
        # Run interactive conversation loop
        role_name = selected_role.get('role', 'AI Assistant')
        run_conversation(client, messages, role_name)
        
    except KeyboardInterrupt:
        print("\n\nExiting... Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

