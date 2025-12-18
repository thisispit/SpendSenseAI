import requests
import os

API_URL = "http://localhost:8000/api"

def test_upload(filename):
    print(f"Testing upload for {filename}...")
    if not os.path.exists(filename):
        print(f"File {filename} not found!")
        return
    
    with open(filename, 'rb') as f:
        files = {'file': f}
        r = requests.post(f"{API_URL}/upload", files=files)
        print(f"Status: {r.status_code}")
        print(f"Response: {r.json()}")

def test_get():
    print("Fetching transactions...")
    r = requests.get(f"{API_URL}/transactions")
    data = r.json()
    print(f"Count: {len(data)}")
    if len(data) > 0:
        print("First transaction:", data[0])

if __name__ == "__main__":
    # Ensure PDF exists (run generation if needed, but assuming it was run)
    if not os.path.exists("sample_statement.pdf"):
        print("Run generate_pdf.py first")
        import generate_pdf
        generate_pdf.create_pdf("sample_statement.pdf")

    test_upload("sample_transactions.csv")
    test_upload("sample_statement.pdf")
    test_get()
