import argparse

def main():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description="Process some input.")
    
    # Add an argument for the input
    parser.add_argument('input_text', type=str, help='The text to be printed')
    
    # Parse the arguments
    args = parser.parse_args()
    
    # Print the input
    print(f"You entered: {args.input_text}")

if __name__ == "__main__":
    main()
