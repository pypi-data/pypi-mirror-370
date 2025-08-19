"""
OACP Web Dashboard and API
Provides REST API and WebSocket endpoints for monitoring OACP runs.
"""

import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

try:
    from fastapi import FastAPI, WebSocket, HTTPException, Query, Depends
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.websockets import WebSocketDisconnect
    import uvicorn
    WEB_AVAILABLE = True
except ImportError:
    WEB_AVAILABLE = False

from .context import get_config
from .storage import create_storage
from .trace import TraceReader
from .events import EventBase


class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Connection might be closed
                pass


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("🌐 OACP Web Dashboard starting...")
    yield
    # Shutdown
    print("🌐 OACP Web Dashboard shutting down...")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    if not WEB_AVAILABLE:
        raise ImportError("FastAPI and uvicorn required for web interface. Install with: pip install 'oacp[web]'")
    
    app = FastAPI(
        title="OACP Dashboard",
        description="Open Agent Compliance Protocol - Web Dashboard and API",
        version="0.1.5",
        lifespan=lifespan
    )
    
    # Add routes
    app.include_router(create_api_router(), prefix="/api/v1", tags=["api"])
    
    # Serve static files (dashboard frontend)
    static_path = Path(__file__).parent / "static"
    if static_path.exists():
        app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    
    # Dashboard home page
    @app.get("/", response_class=HTMLResponse)
    async def dashboard():
        """Serve the main dashboard page."""
        return get_dashboard_html()
    
    # Health check
    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    
    # WebSocket for real-time updates
    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """WebSocket endpoint for real-time log streaming."""
        await manager.connect(websocket)
        try:
            while True:
                # Keep connection alive and handle incoming messages
                data = await websocket.receive_text()
                
                # Handle different message types
                message = json.loads(data)
                if message.get("type") == "subscribe_run":
                    run_id = message.get("run_id")
                    if run_id:
                        # Start streaming logs for this run
                        await stream_run_logs(websocket, run_id)
                
        except WebSocketDisconnect:
            manager.disconnect(websocket)
    
    return app


def create_api_router():
    """Create API router with all endpoints."""
    from fastapi import APIRouter
    
    router = APIRouter()
    
    @router.get("/runs")
    async def list_runs(
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        status: Optional[str] = Query(None)
    ):
        """List recent OACP runs with pagination."""
        try:
            config = get_config()
            storage = create_storage(config["storage_uri"])
            
            # For file storage, scan directory
            if config["storage_uri"].startswith("file://"):
                runs = await get_file_runs(storage, limit, offset, status)
            else:
                runs = await get_db_runs(storage, limit, offset, status)
            
            return {
                "runs": runs,
                "total": len(runs),
                "limit": limit,
                "offset": offset
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/runs/{run_id}")
    async def get_run_details(run_id: str):
        """Get detailed information about a specific run."""
        try:
            config = get_config()
            storage = create_storage(config["storage_uri"])
            reader = TraceReader(storage)
            
            events = list(reader.read_run(run_id))
            if not events:
                raise HTTPException(status_code=404, detail="Run not found")
            
            # Calculate run statistics
            stats = calculate_run_stats(events)
            
            # Get recent events (last 50)
            recent_events = events[-50:] if len(events) > 50 else events
            
            return {
                "run_id": run_id,
                "stats": stats,
                "events": [event.model_dump() for event in recent_events],
                "total_events": len(events)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/runs/{run_id}/events")
    async def get_run_events(
        run_id: str,
        limit: int = Query(50, ge=1, le=500),
        offset: int = Query(0, ge=0),
        event_type: Optional[str] = Query(None)
    ):
        """Get events for a specific run with pagination and filtering."""
        try:
            config = get_config()
            storage = create_storage(config["storage_uri"])
            reader = TraceReader(storage)
            
            events = list(reader.read_run(run_id))
            if not events:
                raise HTTPException(status_code=404, detail="Run not found")
            
            # Filter by event type if specified
            if event_type:
                events = [e for e in events if e.event_type == event_type]
            
            # Apply pagination
            paginated_events = events[offset:offset + limit]
            
            return {
                "run_id": run_id,
                "events": [event.model_dump() for event in paginated_events],
                "total": len(events),
                "limit": limit,
                "offset": offset,
                "filter": {"event_type": event_type} if event_type else None
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/stats")
    async def get_global_stats(days: int = Query(7, ge=1, le=365)):
        """Get global statistics across all runs."""
        try:
            config = get_config()
            storage = create_storage(config["storage_uri"])
            
            # Calculate date range
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            if config["storage_uri"].startswith("file://"):
                stats = await get_file_global_stats(storage, start_date, end_date)
            else:
                stats = await get_db_global_stats(storage, start_date, end_date)
            
            return {
                "period": {
                    "days": days,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "stats": stats
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @router.get("/config")
    async def get_configuration():
        """Get current OACP configuration (sensitive values redacted)."""
        try:
            config = get_config()
            
            # Redact sensitive values
            safe_config = {}
            for key, value in config.items():
                if any(sensitive in key.lower() for sensitive in ['key', 'password', 'token', 'secret']):
                    safe_config[key] = "*" * 8 if value else None
                else:
                    safe_config[key] = value
            
            return {"config": safe_config}
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return router


async def get_file_runs(storage, limit: int, offset: int, status: Optional[str]) -> List[Dict]:
    """Get runs from file storage."""
    config = get_config()
    path = Path(config["storage_uri"][7:])  # Remove 'file://' prefix
    
    if not path.exists():
        return []
    
    log_files = list(path.glob("*.jsonl"))
    log_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    
    runs = []
    for log_file in log_files[offset:offset + limit]:
        run_id = log_file.stem
        stat = log_file.stat()
        
        # Analyze run
        run_status, event_count, node_count = analyze_run_file(log_file)
        
        # Filter by status if specified
        if status and run_status != status:
            continue
        
        runs.append({
            "run_id": run_id,
            "status": run_status,
            "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "size_bytes": stat.st_size,
            "event_count": event_count,
            "node_count": node_count
        })
    
    return runs


async def get_db_runs(storage, limit: int, offset: int, status: Optional[str]) -> List[Dict]:
    """Get runs from database storage."""
    # TODO: Implement database run querying
    return []


async def get_file_global_stats(storage, start_date: datetime, end_date: datetime) -> Dict:
    """Get global statistics from file storage."""
    config = get_config()
    path = Path(config["storage_uri"][7:])
    
    if not path.exists():
        return {}
    
    total_runs = 0
    total_events = 0
    total_nodes = 0
    status_counts = {"completed": 0, "failed": 0, "running": 0, "cancelled": 0}
    
    for log_file in path.glob("*.jsonl"):
        stat = log_file.stat()
        file_date = datetime.fromtimestamp(stat.st_mtime)
        
        # Skip files outside date range
        if not (start_date <= file_date <= end_date):
            continue
        
        total_runs += 1
        run_status, event_count, node_count = analyze_run_file(log_file)
        
        total_events += event_count
        total_nodes += node_count
        status_counts[run_status] = status_counts.get(run_status, 0) + 1
    
    return {
        "total_runs": total_runs,
        "total_events": total_events,
        "unique_nodes": total_nodes,  # This is approximate
        "status_breakdown": status_counts,
        "avg_events_per_run": total_events / max(total_runs, 1)
    }


async def get_db_global_stats(storage, start_date: datetime, end_date: datetime) -> Dict:
    """Get global statistics from database storage."""
    # TODO: Implement database stats querying
    return {}


def analyze_run_file(log_file: Path) -> tuple[str, int, int]:
    """Analyze a run log file and return status, event count, and node count."""
    event_count = 0
    nodes = set()
    run_status = "running"  # Default
    
    try:
        with open(log_file, 'r') as f:
            for line in f:
                if line.strip():
                    event_count += 1
                    try:
                        event_data = json.loads(line)
                        # Track unique nodes
                        if 'node_id' in event_data:
                            nodes.add(event_data['node_id'])
                        
                        # Check for run summary to get final status
                        if event_data.get('event_type') == 'RunSummary':
                            run_status = event_data.get('status', 'completed')
                    except json.JSONDecodeError:
                        continue
    except Exception:
        pass
    
    return run_status, event_count, len(nodes)


def calculate_run_stats(events: List[EventBase]) -> Dict:
    """Calculate statistics for a run."""
    stats = {
        'total_events': len(events),
        'unique_nodes': len(set(getattr(e, 'node_id', None) for e in events if hasattr(e, 'node_id'))),
        'total_votes': len([e for e in events if e.event_type == 'VoteCast']),
        'consensus_reached': len([e for e in events if e.event_type == 'DecisionFinalized' and getattr(e, 'approved', False)]),
        'conflicts_raised': len([e for e in events if e.event_type == 'ConflictRaised']),
        'retries': len([e for e in events if e.event_type == 'RetryScheduled']),
        'event_types': {},
        'duration_ms': None,
    }
    
    # Count event types
    for event in events:
        event_type = event.event_type
        stats['event_types'][event_type] = stats['event_types'].get(event_type, 0) + 1
    
    # Calculate duration if we have start and end
    if events:
        start_time = min(e.timestamp for e in events)
        end_time = max(e.timestamp for e in events)
        stats['duration_ms'] = int((end_time - start_time).total_seconds() * 1000)
    
    return stats


async def stream_run_logs(websocket: WebSocket, run_id: str):
    """Stream real-time logs for a specific run."""
    try:
        config = get_config()
        storage = create_storage(config["storage_uri"])
        reader = TraceReader(storage)
        
        # Send initial events
        events = list(reader.read_run(run_id))
        for event in events[-10:]:  # Send last 10 events
            await websocket.send_text(json.dumps({
                "type": "event",
                "run_id": run_id,
                "event": event.model_dump()
            }))
        
        # TODO: Implement real-time streaming
        # For now, just send a status message
        await websocket.send_text(json.dumps({
            "type": "status",
            "message": f"Streaming logs for run {run_id}"
        }))
        
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": str(e)
        }))


def get_dashboard_html() -> str:
    """Generate the dashboard HTML page."""
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OACP Dashboard</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 300;
        }
        .header p {
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
            font-size: 1.1rem;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        .card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            border: 1px solid #e1e5e9;
        }
        .card h3 {
            margin: 0 0 1rem 0;
            color: #2d3748;
            font-size: 1.25rem;
        }
        .stats {
            display: flex;
            justify-content: space-between;
            margin-bottom: 1rem;
        }
        .stat {
            text-align: center;
        }
        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: #667eea;
        }
        .stat-label {
            font-size: 0.875rem;
            color: #718096;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .status {
            padding: 0.25rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.875rem;
            font-weight: 500;
        }
        .status.completed { background-color: #c6f6d5; color: #22543d; }
        .status.running { background-color: #bee3f8; color: #2a69ac; }
        .status.failed { background-color: #fed7d7; color: #c53030; }
        .runs-list {
            max-height: 400px;
            overflow-y: auto;
        }
        .run-item {
            padding: 1rem;
            border-bottom: 1px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .run-item:last-child {
            border-bottom: none;
        }
        .run-id {
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 0.875rem;
            color: #4a5568;
        }
        .api-links {
            margin-top: 1rem;
        }
        .api-links a {
            color: #667eea;
            text-decoration: none;
            margin-right: 1rem;
            font-size: 0.875rem;
        }
        .api-links a:hover {
            text-decoration: underline;
        }
        .loading {
            text-align: center;
            color: #718096;
            padding: 2rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 OACP Dashboard</h1>
            <p>Open Agent Compliance Protocol - Real-time Monitoring</p>
        </div>

        <div class="grid">
            <div class="card">
                <h3>📊 Global Statistics</h3>
                <div class="stats" id="global-stats">
                    <div class="loading">Loading stats...</div>
                </div>
            </div>

            <div class="card">
                <h3>🔧 Configuration</h3>
                <div id="config-info">
                    <div class="loading">Loading config...</div>
                </div>
            </div>
        </div>

        <div class="card">
            <h3>📋 Recent Runs</h3>
            <div class="runs-list" id="runs-list">
                <div class="loading">Loading runs...</div>
            </div>
            <div class="api-links">
                <a href="/api/v1/runs" target="_blank">📡 API: Runs</a>
                <a href="/api/v1/stats" target="_blank">📊 API: Stats</a>
                <a href="/api/v1/config" target="_blank">⚙️ API: Config</a>
                <a href="/docs" target="_blank">📚 API Docs</a>
            </div>
        </div>
    </div>

    <script>
        // Load global statistics
        async function loadGlobalStats() {
            try {
                const response = await fetch('/api/v1/stats');
                const data = await response.json();
                
                const statsHtml = `
                    <div class="stat">
                        <div class="stat-value">${data.stats.total_runs || 0}</div>
                        <div class="stat-label">Total Runs</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">${data.stats.total_events || 0}</div>
                        <div class="stat-label">Total Events</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">${data.stats.unique_nodes || 0}</div>
                        <div class="stat-label">Unique Nodes</div>
                    </div>
                `;
                
                document.getElementById('global-stats').innerHTML = statsHtml;
            } catch (error) {
                document.getElementById('global-stats').innerHTML = '<div class="loading">Error loading stats</div>';
            }
        }

        // Load configuration
        async function loadConfig() {
            try {
                const response = await fetch('/api/v1/config');
                const data = await response.json();
                
                const configHtml = Object.entries(data.config)
                    .map(([key, value]) => `<div><strong>${key}:</strong> ${value}</div>`)
                    .join('');
                
                document.getElementById('config-info').innerHTML = configHtml;
            } catch (error) {
                document.getElementById('config-info').innerHTML = '<div class="loading">Error loading config</div>';
            }
        }

        // Load recent runs
        async function loadRuns() {
            try {
                const response = await fetch('/api/v1/runs?limit=10');
                const data = await response.json();
                
                if (data.runs.length === 0) {
                    document.getElementById('runs-list').innerHTML = '<div class="loading">No runs found</div>';
                    return;
                }
                
                const runsHtml = data.runs.map(run => `
                    <div class="run-item">
                        <div>
                            <div class="run-id">${run.run_id}</div>
                            <div style="font-size: 0.875rem; color: #718096; margin-top: 0.25rem;">
                                ${run.event_count} events • ${run.node_count} nodes
                            </div>
                        </div>
                        <div>
                            <span class="status ${run.status}">${run.status}</span>
                        </div>
                    </div>
                `).join('');
                
                document.getElementById('runs-list').innerHTML = runsHtml;
            } catch (error) {
                document.getElementById('runs-list').innerHTML = '<div class="loading">Error loading runs</div>';
            }
        }

        // Load all data
        loadGlobalStats();
        loadConfig();
        loadRuns();

        // Refresh data every 30 seconds
        setInterval(() => {
            loadGlobalStats();
            loadRuns();
        }, 30000);
    </script>
</body>
</html>
    """


def serve(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """Start the OACP web server."""
    if not WEB_AVAILABLE:
        raise ImportError("FastAPI and uvicorn required for web interface. Install with: pip install 'oacp[web]'")
    
    app = create_app()
    
    print(f"🌐 Starting OACP Dashboard at http://{host}:{port}")
    print(f"📊 Dashboard: http://{host}:{port}")
    print(f"📡 API Docs: http://{host}:{port}/docs")
    print(f"🔌 WebSocket: ws://{host}:{port}/ws")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
