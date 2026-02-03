"""
Crisis Manager - Main Entry Point v1.1
Interactive CLI for the multi-agent crisis decision system.
Enhanced with 5-group A/B/C/D/E comparative testing.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crisis_manager import CrisisManagerCrew, ExperimentRunner, get_group_description


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
┌─────────────────────────────────────────────┐
│                 MAIN MENU                   │
├─────────────────────────────────────────────┤
│  1. Analyze a Crisis Scenario (MAS+KB)      │
│  2. Run Sample Scenario (Ransomware)        │
│  3. View Agent Roles                        │
│  4. Run 5-Group A/B/C/D/E Experiment        │
│  5. View Experiment Group Descriptions      │
│  6. Exit                                    │
└─────────────────────────────────────────────┘
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
    print("INITIATING MULTI-AGENT ANALYSIS (MAS + Knowledge Graph)...")
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
    print("AGENT ROLES (MAS + Knowledge Graph System)")
    print("="*80)
    
    roles = crew.get_agent_roles()
    for name, info in roles.items():
        print(f"\n[{name.upper()}]")
        print(f"Role: {info['role']}")
        print(f"Goal: {info['goal'][:200]}...")
    
    print("\n" + "="*80 + "\n")


def run_experiment():
    """Run the 5-group A/B/C/D/E comparative experiment."""
    print("\n" + "="*80)
    print("5-GROUP A/B/C/D/E COMPARATIVE EXPERIMENT")
    print("="*80)
    
    print("""
The 5 Experimental Groups:
  A - Expert Humain (Senior Manager) : Human gold standard
  B - Agent Simple GPT (Neutre)      : Standard AI without KB
  C - Agent Féminin (Sarah)          : Female persona for bias testing
  D - MAS (sans KB)                  : Multi-agent without knowledge graph
  E - MAS + Knowledge Graph          : Full system with KB access
""")
    
    # Select groups to run
    group_input = input("Enter groups to run (e.g., 'BCDE' or 'all'): ").strip().upper()
    if group_input == "ALL":
        groups = ["A", "B", "C", "D", "E"]
    else:
        groups = [g for g in group_input if g in "ABCDE"]
    
    if not groups:
        print("No valid groups selected.")
        return
    
    # Get human response if Group A is selected
    human_response = None
    if "A" in groups:
        print("\nFor Group A (Human Expert), enter your expert response:")
        print("(Press Enter twice to submit, or type 'skip' to skip Group A)")
        lines = []
        while True:
            line = input()
            if line.lower() == "skip":
                groups = [g for g in groups if g != "A"]
                break
            if line == "":
                if lines:
                    human_response = "\n".join(lines)
                    break
            else:
                lines.append(line)
    
    if not groups:
        print("No groups remaining.")
        return
    
    # Get or use sample scenario
    use_sample = input("\nUse sample ransomware scenario? (y/n): ").strip().lower()
    if use_sample == "y":
        scenario = get_sample_scenario()
    else:
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
    
    print(f"\nRunning experiment with groups: {', '.join(groups)}")
    print("-" * 40)
    
    # Run experiment
    runner = ExperimentRunner(verbose=True)
    
    try:
        report = runner.run_full_experiment(
            scenario=scenario,
            human_response=human_response,
            groups=groups
        )
        
        # Display results
        print("\n" + "="*80)
        print("EXPERIMENT RESULTS - COMPARATIVE TABLE")
        print("="*80)
        print(report.to_table())
        
        # Display individual results
        print("\n" + "="*80)
        print("DETAILED RESULTS BY GROUP")
        print("="*80)
        
        for code, result in report.results.items():
            print(f"\n[GROUP {code}] {result.group_name}")
            print("-" * 40)
            print(f"Decision: {result.decision}")
            if result.legal_citations:
                print(f"Legal Citations: {', '.join(result.legal_citations)}")
            print(f"Risk Assessment: {result.risk_assessment}")
            print(f"Execution Time: {result.execution_time_seconds:.2f}s")
            print(f"\nRecommendation:\n{result.recommendation[:500]}...")
        
        # Offer to save results
        save = input("\n\nSave results to JSON? (y/n): ").strip().lower()
        if save == "y":
            filename = f"experiment_results_{report.timestamp[:10]}.json"
            with open(filename, "w") as f:
                f.write(report.to_json())
            print(f"Results saved to: {filename}")
        
    except Exception as e:
        print(f"\n[ERROR] Experiment failed: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80 + "\n")


def view_group_descriptions():
    """Display descriptions of all 5 experimental groups."""
    print("\n" + "="*80)
    print("EXPERIMENTAL GROUP DESCRIPTIONS")
    print("="*80)
    
    for code in ["A", "B", "C", "D", "E"]:
        print(f"\n{'='*40}")
        description = get_group_description(code)
        print(description)
    
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
    print("Crew initialized with 3 agents: Scientist, Compliance, Judge")
    print("Experiment framework ready for 5-group testing\n")
    
    while True:
        print_menu()
        choice = input("Enter your choice (1-6): ").strip()
        
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
            run_experiment()
            
        elif choice == "5":
            view_group_descriptions()
            
        elif choice == "6":
            print("\nExiting Crisis Manager. Goodbye!\n")
            break
            
        else:
            print("\nInvalid choice. Please enter 1-6.\n")


if __name__ == "__main__":
    main()

