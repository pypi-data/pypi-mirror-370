
from fastapi import FastAPI, HTTPException, Request
from loguru import logger

from agentlin.route.session_manager import SessionTaskManager
from agentlin.route.task_manager import _process_request
from dotenv import load_dotenv

load_dotenv()


app = FastAPI(
    title="Agent Server",
    description="A service for managing agent tasks and sessions",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Agent Server",
            "description": "Endpoints for managing agent tasks and sessions",
        }
    ],
)

session_task_manager = SessionTaskManager()

@app.post("/v1/agent")
async def agent(request: Request):
    """
    Endpoint to process session requests.
    """
    try:
        return await _process_request(session_task_manager, request)
    except Exception as e:
        logger.error(f"Error processing session request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/readiness")
def readiness():
    """
    Readiness endpoint to check if the service is ready.
    """
    return {"readiness": "ok"}


@app.get("/liveness")
def liveness():
    """
    Liveness endpoint to check if the service is alive.
    """
    return {"liveness": "ok"}


@app.get("/")
def root():
    """
    Root endpoint to check if the service is running.
    """
    return {"message": "Session Manager Service is running."}


@app.get("/health")
def health():
    """
    Health check endpoint to verify the service is operational.
    """
    return {"status": "healthy"}


@app.get("/version")
def version():
    """
    Version endpoint to return the service version.
    """
    return {
        "version": "1.0.0",
        "description": "Session Manager Service for Jupyter Kernels",
    }


if __name__ == "__main__":
    import argparse
    import uvicorn

    parser = argparse.ArgumentParser(description="Run the FastAPI app")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=9999, help="Port to bind")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--env-file", type=str, default=".env", help="Path to the .env file")
    args = parser.parse_args()

    logger.info(f"Starting Agent Server on {args.host}:{args.port}")
    if args.debug:
        logger.info("Debug mode is enabled.")
        app.debug = True
        app.logger.setLevel("DEBUG")

    if args.env_file:
        from dotenv import load_dotenv
        load_dotenv(args.env_file)
    logger.info(f"Loading environment variables from {args.env_file}")
    uvicorn.run(app, host=args.host, port=args.port)
