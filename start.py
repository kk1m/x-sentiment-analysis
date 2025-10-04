"""
Start Script
Starts the API server and scheduler together
"""
import asyncio
import uvicorn
from multiprocessing import Process
from backend.src.jobs.scheduler import start_scheduler


def run_api_server():
    """Run the FastAPI server"""
    uvicorn.run(
        "backend.src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )


async def run_scheduler_async():
    """Run the job scheduler"""
    from backend.src.jobs.scheduler import run_scheduler
    await run_scheduler()


def main():
    """Start both API server and scheduler"""
    print("🚀 Starting X Sentiment Analysis System...")
    print("")
    print("📡 API Server: http://localhost:8000")
    print("📊 API Docs: http://localhost:8000/docs")
    print("📅 Scheduler: Daily batch at 23:59")
    print("")
    print("Press Ctrl+C to stop")
    print("")
    
    # Start API server in separate process
    api_process = Process(target=run_api_server)
    api_process.start()
    
    # Start scheduler in main process
    try:
        asyncio.run(run_scheduler_async())
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        api_process.terminate()
        api_process.join()
        print("✓ Shutdown complete")


if __name__ == "__main__":
    main()
