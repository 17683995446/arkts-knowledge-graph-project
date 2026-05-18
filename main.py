"""Main orchestration and CLI interface for the code knowledge graph."""

import sys
import argparse
import time
import signal
from pathlib import Path
from typing import Optional

from database import Database
from parser import ArkTSParser
from watcher import FileWatcher, ChangeType
from updater import UpdateEngine
from query import QueryAPI, format_json


class KnowledgeGraphService:
    """Main service orchestrating the knowledge graph."""
    
    def __init__(self, project_path: str, db_path: str = "code_graph.db"):
        self.project_path = Path(project_path).resolve()
        self.db_path = db_path
        self.db: Optional[Database] = None
        self.parser: Optional[ArkTSParser] = None
        self.updater: Optional[UpdateEngine] = None
        self.query_api: Optional[QueryAPI] = None
        self.watcher: Optional[FileWatcher] = None
        self._running = False
    
    def initialize(self):
        """Initialize all components."""
        print(f"Initializing knowledge graph for: {self.project_path}")
        
        self.db = Database(self.db_path)
        self.db.initialize()
        
        self.parser = ArkTSParser()
        self.updater = UpdateEngine(self.db, self.parser)
        self.query_api = QueryAPI(self.db)
        
        self.watcher = FileWatcher(str(self.project_path), debounce_seconds=1.0)
        
        print("✓ All components initialized")
    
    def full_sync(self):
        """Perform a full project synchronization."""
        print("\n" + "=" * 60)
        print("Starting full synchronization...")
        print("=" * 60 + "\n")
        
        start_time = time.time()
        file_count, elapsed = self.updater.full_sync(str(self.project_path))
        
        print(f"\n{'=' * 60}")
        print(f"✓ Full sync complete: {file_count} files in {elapsed:.2f}s")
        print(f"{'=' * 60}\n")
        
        stats = self.query_api.get_stats()
        print("Database statistics:")
        print(f"  Files:      {stats['files']}")
        print(f"  Classes:    {stats['classes']}")
        print(f"  Methods:    {stats['methods']}")
        print(f"  Calls:      {stats['calls']}")
        print(f"  Components: {stats['components']}")
    
    def start_watching(self):
        """Start the file watcher for real-time updates."""
        print("\nStarting file watcher (Ctrl+C to stop)...")
        print("-" * 60)
        
        self.watcher.start()
        self._running = True
        
        def signal_handler(sig, frame):
            print("\n\nStopping watcher...")
            self._running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            while self._running:
                changes = self.watcher.get_and_wait_for_changes(timeout=1.0)
                
                if changes:
                    for change in changes:
                        self.updater.update_file(change)
                        
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
    
    def query(self, query_type: str, args: dict) -> str:
        """Execute a query and return formatted result."""
        if query_type == "class":
            result = self.query_api.query_class(args.get("name", ""))
            if result:
                return format_json(result)
            return f"Class '{args.get('name')}' not found"
        
        elif query_type == "file":
            result = self.query_api.query_file(args.get("path", ""))
            if result:
                return format_json(result)
            return f"File '{args.get('path')}' not found"
        
        elif query_type == "callers":
            result = self.query_api.query_callers(args.get("method", ""))
            return format_json(result)
        
        elif query_type == "callees":
            result = self.query_api.query_callees(
                args.get("method", ""),
                args.get("class")
            )
            return format_json(result)
        
        elif query_type == "components":
            result = self.query_api.query_components(args.get("class", ""))
            return format_json(result)
        
        elif query_type == "search-classes":
            result = self.query_api.search_classes(args.get("pattern", ""))
            return format_json(result)
        
        elif query_type == "search-methods":
            result = self.query_api.search_methods(args.get("pattern", ""))
            return format_json(result)
        
        elif query_type == "stats":
            result = self.query_api.get_stats()
            return format_json(result)
        
        elif query_type == "export":
            result = self.query_api.export_graph()
            return format_json(result)
        
        elif query_type == "files":
            result = self.query_api.get_all_files()
            return format_json(result)
        
        return "Unknown query type"
    
    def stop(self):
        """Stop the service and cleanup."""
        print("Stopping service...")
        if self.watcher:
            self.watcher.stop()
        if self.db:
            self.db.close()
        print("Service stopped.")


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="ArkTS Code Knowledge Graph - Dynamic Update Edition",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize and perform full sync
  python main.py --project /path/to/project sync
  
  # Start watching for changes
  python main.py --project /path/to/project watch
  
  # Query a class
  python main.py --project /path/to/project query class --name MyClass
  
  # Search for classes
  python main.py --project /path/to/project search-classes --pattern Component
  
  # Get statistics
  python main.py --project /path/to/project stats
        """
    )
    
    parser.add_argument(
        "--project", "-p",
        required=True,
        help="Path to the project directory"
    )
    
    parser.add_argument(
        "--db",
        default="code_graph.db",
        help="Path to SQLite database file (default: code_graph.db)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    sync_parser = subparsers.add_parser("sync", help="Perform full synchronization")
    
    watch_parser = subparsers.add_parser("watch", help="Start file watcher for real-time updates")
    
    query_parser = subparsers.add_parser("query", help="Query the knowledge graph")
    query_parser.add_argument("query_type", choices=["class", "file", "callers", "callees", "components"])
    query_parser.add_argument("--name", help="Class or component name")
    query_parser.add_argument("--path", help="File path")
    query_parser.add_argument("--method", help="Method name")
    query_parser.add_argument("--class", dest="class_name", help="Class name")
    
    search_parser = subparsers.add_parser("search-classes", help="Search for classes")
    search_parser.add_argument("--pattern", required=True, help="Search pattern")
    
    search_parser = subparsers.add_parser("search-methods", help="Search for methods")
    search_parser.add_argument("--pattern", required=True, help="Search pattern")
    
    subparsers.add_parser("stats", help="Get database statistics")
    
    subparsers.add_parser("export", help="Export entire knowledge graph as JSON")
    
    subparsers.add_parser("files", help="List all files in the knowledge graph")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    service = KnowledgeGraphService(args.project, args.db)
    
    try:
        service.initialize()
        
        if args.command == "sync":
            service.full_sync()
        
        elif args.command == "watch":
            service.full_sync()
            service.start_watching()
        
        elif args.command == "query":
            result = service.query(args.query_type, {
                "name": args.name,
                "path": args.path,
                "method": args.method,
                "class": args.class_name
            })
            print(result)
        
        elif args.command in ("search-classes", "search-methods"):
            if args.command == "search-classes":
                result = service.query_api.search_classes(args.pattern)
            else:
                result = service.query_api.search_methods(args.pattern)
            print(format_json(result))
        
        elif args.command == "stats":
            print(service.query("stats", {}))
        
        elif args.command == "export":
            print(service.query("export", {}))
        
        elif args.command == "files":
            print(service.query("files", {}))
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        service.stop()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
