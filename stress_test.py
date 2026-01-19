import asyncio
import httpx
import time

# Configuration
URL = "http://127.0.0.1:8000/orders/"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImtpcmFuIiwiZXhwIjoxNzY4ODQ3MTMwfQ.GYFqiLUqw8e7UXflmX0XLJXKjXUWbrVwgMVOvAoOnG8" # Copy this from your /login response
PRODUCT_ID = 8 # Make sure this product has exactly 10 in stock
QUANTITY = 1
CONCURRENT_REQUESTS = 15 # We try to buy 15 items when only 10 exist

headers = {"Authorization": f"Bearer {TOKEN}"}
order_data = {"product_id": PRODUCT_ID, "quantity": QUANTITY}

async def place_order(client, task_id):
    try:
        response = await client.post(URL, json=order_data, headers=headers)
        print(f"Task {task_id}: Status {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Task {task_id} failed: {e}")

async def run_test():
    async with httpx.AsyncClient() as client:
        tasks = [place_order(client, i) for i in range(CONCURRENT_REQUESTS)]
        print(f"🚀 Firing {CONCURRENT_REQUESTS} orders simultaneously...")
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(run_test())
    print(f"--- Finished in {time.time() - start_time:.2f} seconds ---")