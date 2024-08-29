import sys
import subprocess

def main():
    print("Welcome to the Drone Routing System")
    
    # Step 1: No-Fly Zones
    create_zones = input("Would you like to create no-fly zones? (yes/no): ").strip().lower()
    if create_zones == 'yes':
        run_script("../scripts/generate_zones.py")
    
    # Step 2: Choose Algorithm
    print("\nSelect the Drone Routing Algorithm:")
    print("1. Simple Routing Algorithm")
    print("2. Advanced Routing Algorithm")
    
    choice = input("Please choose an algorithm (1/2): ").strip()
    
    if choice == '1':
        run_script("../scripts/generate_simple_route.py")
    elif choice == '2':
        run_script("../scripts/generate_advanced_route.py")
    else:
        print("Invalid choice. Exiting.")
        sys.exit(1)

def run_script(script_path):
    """Utility function to run a script."""
    result = subprocess.run(["python", script_path], text=True)
    if result.returncode != 0:
        print(f"Error running {script_path}")
        sys.exit(1)

if __name__ == "__main__":
    main()
