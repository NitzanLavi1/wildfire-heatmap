import time
import random
from state_engine import StateEngine, config
from simulation_scenarios import SCENARIOS

def populate_demo():
    print("--- STARTING DEMO POPULATION ---")
    engine = StateEngine()
    
    # Select 5 distinct scenarios
    target_districts = ["San Bernardino", "Riverside", "Alameda", "Monterey", "Shasta"]
    selected_scenarios = [s for s in SCENARIOS if s['district'] in target_districts]
    
    # If we don't have exactly these, just take first 5
    if len(selected_scenarios) < 5:
        selected_scenarios = SCENARIOS[:5]

    for i, scenario in enumerate(selected_scenarios):
        district = scenario['district']
        print(f"\n[{i+1}/5] Processing Demo Scenario: {district}")
        
        # signals
        signals = scenario['signals']
        
        # 1. Fetch Current State (should be None if board is clear)
        current_item = engine.fetch_current_state(district)
        
        # 2. Synthesize State (using new prompt without prefixes)
        new_state = engine.synthesize_state(district, current_item, signals)
        
        if new_state:
            # 3. Update Board
            engine.update_monday_board(district, new_state, item_id=current_item['id'] if current_item else None)
            
            # 4. Export Dashboard Data
            engine.export_dashboard_data(district, new_state)
            
        time.sleep(2) # Slight delay to be nice to API

    print("\n--- DEMO POPULATION COMPLETE ---")

if __name__ == "__main__":
    populate_demo()
