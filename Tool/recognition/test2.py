import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        session_id = sys.argv[1]
        print(f"Received session ID: {session_id}")
    else:
        print("No session ID provided")
