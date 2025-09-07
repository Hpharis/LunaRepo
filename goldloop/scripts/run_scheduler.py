import subprocess
import schedule
import time

def job():
    print("📝 Running Goldloop Writer...")
    try:
        # Run Node generator
        result = subprocess.run(
            ["node", "scripts/generate-post.js"],
            check=True,
            text=True,
            capture_output=True
        )
        print(result.stdout)  # show slug + title
    except subprocess.CalledProcessError as e:
        print("❌ Error while running generate-post.js")
        print(e.stderr)

# Run once now (for testing)
job()

# Schedule daily at 9 AM
schedule.every().day.at("09:00").do(job)

print("📅 Scheduler started. Will run daily at 09:00 AM.")
while True:
    schedule.run_pending()
    time.sleep(60)
