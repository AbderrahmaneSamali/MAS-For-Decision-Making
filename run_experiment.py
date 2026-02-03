"""
Direct 5-Group Experiment Runner
Simply run: python run_experiment.py
Then paste your scenario and get results!
"""

import os
import sys
import json
from datetime import datetime

# Setup path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load config first to set API key
from crisis_manager.config import OPENAI_API_KEY
from crisis_manager import ExperimentRunner

def main():
    print("\n" + "="*70)
    print("  5-GROUP A/B/C/D/E EXPERIMENT RUNNER")
    print("="*70)
    
    print("""
Groups:
  B - Agent Simple GPT (Neutral AI)
  C - Agent Féminin (Sarah persona)
  D - MAS sans KB (Multi-agent, no knowledge graph)
  E - MAS + Knowledge Graph (Full system)
  
Note: Group A (Human Expert) requires manual input.
""")
    
    # Select groups
    groups_input = input("Which groups to run? (e.g., 'BCDE' or 'E' for quick test): ").strip().upper()
    if not groups_input:
        groups_input = "E"  # Default to just MAS+KB
    
    groups = [g for g in groups_input if g in "BCDE"]
    if not groups:
        print("No valid groups selected. Defaulting to E.")
        groups = ["E"]
    
    print(f"\nRunning groups: {', '.join(groups)}")
    
    # Get scenario
    print("\n" + "-"*70)
    print("Paste your crisis scenario below.")
    print("When done, press Enter on an empty line to submit.")
    print("-"*70 + "\n")
    
    lines = []
    while True:
        try:
            line = input()
            if line == "":
                if lines:
                    break
            else:
                lines.append(line)
        except EOFError:
            break
    
    scenario = "\n".join(lines)
    
    if not scenario.strip():
        print("No scenario provided. Exiting.")
        return
    
    print(f"\n[Scenario received: {len(scenario)} characters]")
    print("\n" + "="*70)
    print("RUNNING EXPERIMENT...")
    print("="*70 + "\n")
    
    # Run experiment
    runner = ExperimentRunner(verbose=True)
    
    try:
        report = runner.run_full_experiment(
            scenario=scenario,
            groups=groups
        )
        
        # Display results
        print("\n" + "="*70)
        print("RESULTS - COMPARATIVE TABLE")
        print("="*70)
        print(report.to_table())
        
        # Detailed results
        print("\n" + "="*70)
        print("DETAILED RESULTS BY GROUP")
        print("="*70)
        
        for code, result in report.results.items():
            print(f"\n{'='*60}")
            print(f"[GROUP {code}] {result.group_name}")
            print(f"{'='*60}")
            print(f"Decision: {result.decision}")
            if result.legal_citations:
                print(f"Legal Citations: {', '.join(result.legal_citations)}")
            print(f"Risk Assessment: {result.risk_assessment}")
            print(f"Execution Time: {result.execution_time_seconds:.2f}s")
            print(f"\nFull Response:\n{'-'*40}")
            print(result.raw_output if result.raw_output else result.recommendation)
        
        # Save results
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"experiment_results_{timestamp}.json"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report.to_json())
        
        print(f"\n{'='*70}")
        print(f"Results saved to: {filename}")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"\n[ERROR] Experiment failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
