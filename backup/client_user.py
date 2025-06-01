import socket

def main():
    print("🔐 Permission Request Client (Press Ctrl+C to exit)\n")
    requester = input("Enter your username: ")

    try:
        while True:
            print("\nEnter your GRANT query:")
            grant_query = input("Query: ").strip()

            if not grant_query.lower().startswith("grant"):
                print("⚠️ Only GRANT queries are allowed.")
                continue

            data = f"{requester}||{grant_query}"

            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect(('localhost', 5000))  # Replace with server IP if needed
                    s.sendall(data.encode())

                    response = s.recv(1024).decode()
                    print(f"\n🛡️ Admin Response: {response}")

            except ConnectionRefusedError:
                print("❌ Could not connect to admin server. Make sure it is running.")
            except Exception as e:
                print(f"⚠️ Error: {e}")

    except KeyboardInterrupt:
        print("\n👋 Exiting client... Goodbye!")

if __name__ == "__main__":
    main()
