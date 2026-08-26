
import os
import warnings
import logging
import textwrap

# 1. Silence all standard Python warnings
warnings.filterwarnings("ignore")

# 2. Aggressively mute Google SDK and ChromaDB background logs
logging.getLogger("google").setLevel(logging.ERROR)
logging.getLogger("chromadb").setLevel(logging.ERROR)
logging.getLogger("httpx").setLevel(logging.ERROR)

from src.agent import run_chat_turn

def print_agent_box(text):
    """Prints the agent's response inside a neat visual terminal box."""
    lines = []
    # Break the text into lines and wrap long paragraphs so they fit on screen
    for line in text.split('\n'):
        if line.strip() == "":
            lines.append("")
        else:
            lines.extend(textwrap.wrap(line, width=75, replace_whitespace=False))
    
    # Calculate the width of the box based on the longest line
    max_width = max((len(line) for line in lines), default=20)
    max_width = max(max_width, 20) # Ensure a minimum width
    
    # Draw the box using Unicode characters
    print("\n╭" + "─" * (max_width + 2) + "╮")
    print("│ " + "🤖 Aster Row Agent".ljust(max_width) + " │")
    print("├" + "─" * (max_width + 2) + "┤")
    
    for line in lines:
        print("│ " + line.ljust(max_width) + " │")
        
    print("╰" + "─" * (max_width + 2) + "╯")

def main():
    print("🤖 Aster Row Support Agent Initiated")
    print("Type 'exit' or 'quit' to stop.\n")
    
    # Store just the pure conversational history to save context tokens
    conversation_history = []
    
    while True:
        try:
            user_input = input("\nYou: ")
            
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
                
            if not user_input.strip():
                continue

            # Run the agent turn
            response = run_chat_turn(user_input, conversation_history)
            
            # Print the response using our new box function instead of a standard print
            print_agent_box(response)
            
            # Save raw input and output to history for multi-turn memory
            conversation_history.append({"role": "user", "content": user_input})
            conversation_history.append({"role": "assistant", "content": response})

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"\n[!] Error: {e}")

if __name__ == "__main__":
    main()