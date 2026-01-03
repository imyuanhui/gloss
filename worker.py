from workers import WorkerEntrypoint
import asgi

# Import your FastAPI app
from backend.main import app


class Entrypoint(WorkerEntrypoint):
    async def fetch(self, request):
        return await asgi.fetch(app, request)
