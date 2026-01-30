"""
Crisis Manager - Main Entry Point
Interactive CLI for the multi-agent crisis decision system.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crisis_manager import CrisisManagerCrew


def print_banner():
    """Print the application banner."""
    banner = """
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║     ██████╗██████╗ ██╗███████╗██╗███████╗    ███╗   ███╗ █████╗ ███████╗     ║
║    ██╔════╝██╔══██╗██║██╔════╝██║██╔════╝    ████╗ ████║██╔══██╗██╔════╝     ║
║    ██║     ██████╔╝██║███████╗██║███████╗    ██╔████╔██║███████║███████╗     ║
║    ██║     ██╔══██╗██║╚════██║██║╚════██║    ██║╚██╔╝██║██╔══██║╚════██║     ║
║    ╚██████╗██║  ██║██║███████║██║███████║    ██║ ╚═╝ ██║██║  ██║███████║     ║
║     ╚═════╝╚═╝  ╚═╝╚═╝╚══════╝╚═╝╚══════╝    ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝     ║
║                                                                               ║
║              Multi-Agent System for Managerial Crisis Decision-Making        ║
║                         Powered by CrewAI + Knowledge Graph                   ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_menu():
    """Print the main menu."""
    menu = """
┌─────────────────────────────────────────┐
│              MAIN MENU                  │
├─────────────────────────────────────────┤
│  1. Analyze a Crisis Scenario           │
│  2. Run Sample Scenario (Ransomware)    │
│  3. View Agent Roles                    │
│  4. Exit                                │
└─────────────────────────────────────────┘
    """
    print(menu)


def get_sample_scenario():
    """Return the sample ransomware/bug bounty scenario."""
    return """
I am the CEO of a mid-sized Fintech company operating in Europe and the US.

We just discovered a security breach. Hackers accessed a database with 50,000 user IDs. 
They have contacted us and are offering a deal: if we pay them $50,000 in Bitcoin 
immediately, they certify they will delete the data and tell no one.

My CISO (Chief Information Security Officer) suggests we pay it but book the transaction 
internally as a 'Bug Bounty' reward (a payment to ethical researchers). His argument is that:
- It costs less than the legal fees of reporting it.
- By calling it a 'Bug Bounty', we technically don't have to declare a 'hostile breach' 
  to the regulators or our customers, protecting our reputation.

Should I authorize this payment?
    """


def run_analysis(crew: CrisisManagerCrew, scenario: str):
    """Run crisis analysis and display results."""
    print("\n" + "="*80)
    print("INITIATING MULTI-AGENT ANALYSIS...")
    print("="*80 + "\n")
    
    try:
        result = crew.analyze_crisis(scenario)
        
        print("\n" + "="*80)
        print("FINAL VERDICT")
        print("="*80)
        print(result)
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n[ERROR] Analysis failed: {str(e)}")
        print("Make sure you have set up your LLM API keys (OPENAI_API_KEY or similar).\n")


def view_agent_roles(crew: CrisisManagerCrew):
    """Display the roles of all agents."""
    print("\n" + "="*80)
    print("AGENT ROLES")
    print("="*80)
    
    roles = crew.get_agent_roles()
    for name, info in roles.items():
        print(f"\n[{name.upper()}]")
        print(f"Role: {info['role']}")
        print(f"Goal: {info['goal'][:200]}...")
    
    print("\n" + "="*80 + "\n")


def main():
    """Main entry point."""
    print_banner()
    
    # Check for API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("\n[WARNING] OPENAI_API_KEY not set.")
        print("Set it with: set OPENAI_API_KEY=your-key-here\n")
    
    # Initialize crew
    print("Initializing Crisis Manager Crew...")
    crew = CrisisManagerCrew(verbose=True)
    print("Crew initialized with 3 agents: Scientist, Compliance, Judge\n")
    
    while True:
        print_menu()
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == "1":
            print("\nEnter your crisis scenario (press Enter twice to submit):")
            lines = []
            while True:
                line = input()
                if line == "":
                    if lines:
                        break
                else:
                    lines.append(line)
            scenario = "\n".join(lines)
            run_analysis(crew, scenario)
            
        elif choice == "2":
            scenario = get_sample_scenario()
            print("\nSAMPLE SCENARIO:")
            print("-" * 40)
            print(scenario)
            print("-" * 40)
            run_analysis(crew, scenario)
            
        elif choice == "3":
            view_agent_roles(crew)
            
        elif choice == "4":
            print("\nExiting Crisis Manager. Goodbye!\n")
            break
            
        else:
            print("\nInvalid choice. Please enter 1-4.\n")


if __name__ == "__main__":
    main()
