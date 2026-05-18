"""Flask server for ArkTS knowledge graph visualization."""
import os
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS

from ark_analyzer_db import ArkAnalyzerDB
from ark_analyzer_runner import ArkAnalyzerRunner

app = Flask(__name__, static_folder='web', template_folder='web')
CORS(app)

# Configure paths
DB_PATH = "ark_graph.db"
PROJECT_PATH = "./complex_project"


@app.route('/')
def index():
    """Serve the visualization page."""
    return render_template('index.html')


@app.route('/api/graph')
def get_graph():
    """Get the knowledge graph data for visualization."""
    if not os.path.exists(DB_PATH):
        return jsonify({'error': 'Database not found'}), 404
    
    db = ArkAnalyzerDB(DB_PATH)
    db.initialize()
    
    try:
        cursor = db.conn.execute("SELECT id, name, path, analyzed_at FROM projects ORDER BY id DESC LIMIT 1")
        project = cursor.fetchone()
        
        if not project:
            return jsonify({'error': 'No project found'}), 404
        
        project_id = project[0]
        
        # Build nodes array
        nodes = []
        node_map = {}  # maps db id to node info
        
        # Add files
        cursor = db.conn.execute("SELECT id, path FROM files WHERE project_id = ?", (project_id,))
        for row in cursor.fetchall():
            file_id = f"file_{row[0]}"
            filename = os.path.basename(row[1])
            nodes.append({
                'id': file_id,
                'name': filename,
                'type': 'file',
                'file': row[1]
            })
            node_map[row[0]] = {'id': file_id, 'type': 'file', 'file': row[1]}
        
        # Add classes/structs
        cursor = db.conn.execute("""
            SELECT id, name, file_id, start_line, end_line 
            FROM classes WHERE project_id = ?
        """, (project_id,))
        for row in cursor.fetchall():
            class_id = f"class_{row[0]}"
            file_path = node_map.get(row[2], {}).get('file', '')
            nodes.append({
                'id': class_id,
                'name': row[1],
                'type': 'class',
                'file': file_path,
                'start_line': row[3],
                'end_line': row[4]
            })
            node_map[row[0]] = {'id': class_id, 'type': 'class', 'name': row[1], 'file': file_path}
        
        # Add methods
        cursor = db.conn.execute("""
            SELECT id, name, class_id, params, return_type, start_line, end_line
            FROM methods WHERE project_id = ?
        """, (project_id,))
        for row in cursor.fetchall():
            method_id = f"method_{row[0]}"
            class_id = row[2]
            file_path = ""
            
            if class_id and class_id in node_map:
                class_info = node_map[class_id]
                # Find the class's file
                file_path = next((n.get('file', '') for n in nodes 
                               if n['id'] == class_info['id']), '')
            
            nodes.append({
                'id': method_id,
                'name': row[1],
                'type': 'method',
                'class_id': class_id,
                'params': row[3],
                'return_type': row[4],
                'file': file_path,
                'start_line': row[5],
                'end_line': row[6]
            })
            node_map[row[0]] = {'id': method_id, 'type': 'method', 'name': row[1]}
        
        # Build links array
        links = []
        
        # Add member relationships (method -> class)
        cursor = db.conn.execute("""
            SELECT id, class_id FROM methods 
            WHERE project_id = ? AND class_id IS NOT NULL
        """, (project_id,))
        for row in cursor.fetchall():
            method_id = f"method_{row[0]}"
            class_id = f"class_{row[1]}"
            links.append({
                'source': method_id,
                'target': class_id,
                'type': 'member'
            })
        
        # Add call relationships
        cursor = db.conn.execute("""
            SELECT caller_method_id, callee_method_name, callee_method_id
            FROM calls WHERE project_id = ?
        """, (project_id,))
        for row in cursor.fetchall():
            caller_id = f"method_{row[0]}"
            callee_name = row[1]
            callee_method_id = row[2]
            
            if callee_method_id and callee_method_id in node_map:
                target_id = node_map[callee_method_id]['id']
                links.append({
                    'source': caller_id,
                    'target': target_id,
                    'type': 'call',
                    'callee_name': callee_name
                })
            else:
                # Can't resolve to a node, skip or add as external
                continue
        
        stats = db.get_project_stats(project_id)
        
        return jsonify({
            'nodes': nodes,
            'links': links,
            'stats': stats,
            'project': {
                'id': project[0],
                'name': project[1],
                'path': project[2],
                'analyzed_at': project[3]
            }
        })
        
    finally:
        db.close()


@app.route('/api/class/<class_name>')
def get_class(class_name):
    """Get detailed information about a class."""
    if not os.path.exists(DB_PATH):
        return jsonify({'error': 'Database not found'}), 404
    
    db = ArkAnalyzerDB(DB_PATH)
    db.initialize()
    
    try:
        cursor = db.conn.execute("SELECT id FROM projects ORDER BY id DESC LIMIT 1")
        project = cursor.fetchone()
        if not project:
            return jsonify({'error': 'No project found'}), 404
        
        result = db.query_class(project[0], class_name)
        if not result:
            return jsonify({'error': f'Class {class_name} not found'}), 404
        
        methods = db.query_methods_by_class(result['id'])
        
        # Get callers
        cursor = db.conn.execute("""
            SELECT m.id, m.name, c.name as class_name, f.path
            FROM calls call
            JOIN methods m ON call.caller_method_id = m.id
            LEFT JOIN classes c ON m.class_id = c.id
            LEFT JOIN files f ON c.file_id = f.id
            WHERE call.callee_method_id IN (SELECT id FROM methods WHERE class_id = ?)
        """, (result['id'],))
        callers = []
        for row in cursor.fetchall():
            callers.append({
                'method_id': row[0],
                'method_name': row[1],
                'class_name': row[2],
                'file': row[3]
            })
        
        return jsonify({
            'class': result,
            'methods': methods,
            'callers': callers
        })
        
    finally:
        db.close()


@app.route('/api/sync', methods=['POST'])
def sync_project():
    """Run analysis and update the database."""
    data = request.get_json() or {}
    project_path = data.get('project_path', PROJECT_PATH)
    project_name = data.get('project_name')
    
    if not os.path.exists(project_path):
        return jsonify({'error': f'Project path does not exist: {project_path}'}), 400
    
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    db = ArkAnalyzerDB(DB_PATH)
    db.initialize()
    
    try:
        runner = ArkAnalyzerRunner(os.path.dirname(os.path.abspath(__file__)), db)
        success = runner.analyze_project(project_path, project_name)
        
        if success:
            stats = db.get_project_stats(runner.project_id)
            return jsonify({'success': True, 'stats': stats})
        else:
            return jsonify({'error': 'Analysis failed'}), 500
            
    finally:
        db.close()


@app.route('/api/stats')
def get_stats():
    """Get project statistics."""
    if not os.path.exists(DB_PATH):
        return jsonify({'error': 'Database not found'}), 404
    
    db = ArkAnalyzerDB(DB_PATH)
    db.initialize()
    
    try:
        cursor = db.conn.execute("SELECT id FROM projects ORDER BY id DESC LIMIT 1")
        project = cursor.fetchone()
        if not project:
            return jsonify({'error': 'No project found'}), 404
        
        stats = db.get_project_stats(project[0])
        return jsonify(stats)
        
    finally:
        db.close()


def ensure_database():
    """Ensure the database exists and is populated."""
    if not os.path.exists(DB_PATH):
        print("Initial database not found. Running analysis...")
        db = ArkAnalyzerDB(DB_PATH)
        db.initialize()
        runner = ArkAnalyzerRunner(os.path.dirname(os.path.abspath(__file__)), db)
        runner.analyze_project(PROJECT_PATH)
        db.close()
        print("Analysis complete.")


if __name__ == '__main__':
    # Ensure database exists
    if not os.path.exists(DB_PATH):
        ensure_database()
    
    print("Starting ArkTS Knowledge Graph Server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
