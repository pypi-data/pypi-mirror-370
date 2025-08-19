from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
import os
import re
from pathlib import Path
from waitress import serve
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

# Global variable to store currently loaded data
ANTISMASH_DATA = None
CURRENT_FILE = None

def get_available_files():
    """Get list of available JSON files in the data directory."""
    data_dir = Path("data")
    if not data_dir.exists():
        return []
    
    json_files = []
    for file_path in data_dir.glob("*.json"):
        json_files.append(file_path.name)
    
    return sorted(json_files)

def load_antismash_data(filename=None):
    """Load AntiSMASH JSON data from file."""
    if filename is None:
        # Default to Y16952.json if no file specified
        filename = "Y16952.json"
    
    data_file = Path("data") / filename
    if data_file.exists():
        with open(data_file, 'r') as f:
            return json.load(f)
    return None

def set_current_file(filename):
    """Set the current file and load its data."""
    global ANTISMASH_DATA, CURRENT_FILE
    data = load_antismash_data(filename)
    if data is not None:
        ANTISMASH_DATA = data
        CURRENT_FILE = filename
        return True
    return False

# Load the default data at startup
# Try to load a default file if it exists, but don't fail if it doesn't
try:
    if not set_current_file("Y16952.json"):
        # Try to load any available JSON file from data directory
        available_files = get_available_files()
        if available_files:
            set_current_file(available_files[0])
        else:
            print("No JSON files found in data directory. Application will start without loaded data.")
except Exception as e:
    print(f"Warning: Could not load default data on startup: {e}")
    ANTISMASH_DATA = None
    CURRENT_FILE = None

@app.route('/')
def index():
    """Serve the SPA."""
    return app.send_static_file('dist/index.html')

@app.route('/<path:path>')
def spa_fallback(path):
    """Fallback for SPA routing - serve index.html for all non-API routes."""
    if path.startswith('api/'):
        # Let API routes be handled by their specific handlers
        return jsonify({"error": "Not found"}), 404
    return app.send_static_file('dist/index.html')

@app.route('/api/status')
def get_status():
    """API endpoint to get current file and data loading status."""
    return jsonify({
        "current_file": CURRENT_FILE if CURRENT_FILE else None,
        "has_loaded_data": ANTISMASH_DATA is not None,
        "data_directory_exists": Path("data").exists()
    })

@app.route('/api/browse')
def browse_filesystem():
    """API endpoint to browse the server's filesystem."""
    path = request.args.get('path', '.')
    
    try:
        # Resolve the path
        resolved_path = Path(path).resolve()
        
        if not resolved_path.exists():
            return jsonify({"error": "Path does not exist"}), 404
            
        if not resolved_path.is_dir():
            return jsonify({"error": "Path is not a directory"}), 400
        
        items = []
        
        # Add parent directory option (except for filesystem root)
        if resolved_path.parent != resolved_path:  # Not at filesystem root
            items.append({
                "name": "..",
                "type": "directory",
                "path": str(resolved_path.parent)
            })
        
        # List directory contents
        for item in sorted(resolved_path.iterdir()):
            try:
                if item.is_dir():
                    items.append({
                        "name": item.name,
                        "type": "directory", 
                        "path": str(item)
                    })
                elif item.suffix.lower() == '.json':
                    items.append({
                        "name": item.name,
                        "type": "file",
                        "path": str(item),
                        "size": item.stat().st_size
                    })
            except (OSError, PermissionError):
                # Skip items we can't access
                continue
        
        return jsonify({
            "current_path": str(resolved_path),
            "items": items
        })
        
    except PermissionError:
        return jsonify({"error": "Permission denied"}), 403
    except Exception as e:
        return jsonify({"error": f"Failed to browse directory: {str(e)}"}), 500

@app.route('/api/scan-folder', methods=['POST'])
def scan_folder_for_json():
    """API endpoint to scan a folder recursively for JSON files."""
    data = request.get_json()
    folder_path = data.get('path')
    
    if not folder_path:
        return jsonify({"error": "No folder path provided"}), 400
    
    try:
        # Resolve the path
        resolved_path = Path(folder_path).resolve()
        
        if not resolved_path.exists():
            return jsonify({"error": "Folder does not exist"}), 404
            
        if not resolved_path.is_dir():
            return jsonify({"error": "Path is not a directory"}), 400
        
        # Scan recursively for JSON files
        json_files = []
        try:
            # Use rglob to recursively find all JSON files
            for json_file in resolved_path.rglob('*.json'):
                try:
                    if json_file.is_file():
                        # Calculate relative path from the base folder for display
                        relative_path = json_file.relative_to(resolved_path)
                        json_files.append({
                            "name": json_file.name,
                            "path": str(json_file),
                            "relative_path": str(relative_path),
                            "size": json_file.stat().st_size,
                            "directory": str(json_file.parent.relative_to(resolved_path)) if json_file.parent != resolved_path else "."
                        })
                except (OSError, PermissionError):
                    # Skip files we can't access
                    continue
        except PermissionError:
            return jsonify({"error": "Permission denied to read folder"}), 403
        
        # Sort by relative path for better organization
        json_files.sort(key=lambda x: x['relative_path'])
        
        return jsonify({
            "folder_path": str(resolved_path),
            "json_files": json_files,
            "count": len(json_files),
            "scan_type": "recursive"
        })
        
    except PermissionError:
        return jsonify({"error": "Permission denied"}), 403
    except Exception as e:
        return jsonify({"error": f"Failed to scan folder: {str(e)}"}), 500

@app.route('/api/load-file', methods=['POST'])
def load_file_from_path():
    """API endpoint to load a JSON file from a specific path."""
    data = request.get_json()
    file_path = data.get('path')
    
    if not file_path:
        return jsonify({"error": "No file path provided"}), 400
    
    try:
        # Resolve the path
        resolved_path = Path(file_path).resolve()
        
        if not resolved_path.exists():
            return jsonify({"error": "File does not exist"}), 404
            
        if not resolved_path.is_file() or resolved_path.suffix.lower() != '.json':
            return jsonify({"error": "Not a JSON file"}), 400
        
        # Load the file
        global ANTISMASH_DATA, CURRENT_FILE
        with open(resolved_path, 'r') as f:
            data = json.load(f)
        
        ANTISMASH_DATA = data
        CURRENT_FILE = resolved_path.name
        
        return jsonify({
            "message": f"Successfully loaded {resolved_path.name}",
            "current_file": CURRENT_FILE,
            "file_path": str(resolved_path)
        })
        
    except PermissionError:
        return jsonify({"error": "Permission denied"}), 403
    except json.JSONDecodeError as e:
        return jsonify({"error": f"Invalid JSON file: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to load file: {str(e)}"}), 500

@app.route('/api/info')
def get_info():
    """API endpoint to get basic information about the dataset."""
    if not ANTISMASH_DATA:
        return jsonify({"error": "AntiSMASH data not found"}), 404
    
    return jsonify({
        "version": ANTISMASH_DATA.get("version"),
        "input_file": ANTISMASH_DATA.get("input_file"),
        "taxon": ANTISMASH_DATA.get("taxon"),
        "total_records": len(ANTISMASH_DATA.get("records", [])),
        "schema": ANTISMASH_DATA.get("schema"),
        "current_file": CURRENT_FILE
    })

@app.route('/api/records')
def get_records():
    """API endpoint to get list of all records (regions)."""
    if not ANTISMASH_DATA:
        return jsonify({"error": "AntiSMASH data not found"}), 404
    
    records = []
    for record in ANTISMASH_DATA.get("records", []):
        records.append({
            "id": record.get("id"),
            "description": record.get("description"),
            "gc_content": record.get("gc_content"),
            "feature_count": len(record.get("features", []))
        })
    
    return jsonify(records)

@app.route('/api/records/<record_id>')
def get_record(record_id):
    """API endpoint to get a specific record."""
    if not ANTISMASH_DATA:
        return jsonify({"error": "AntiSMASH data not found"}), 404
    
    record = next((r for r in ANTISMASH_DATA.get("records", []) if r.get("id") == record_id), None)
    if record:
        return jsonify(record)
    return jsonify({"error": "Record not found"}), 404

@app.route('/api/records/<record_id>/regions')
def get_record_regions(record_id):
    """API endpoint to get all regions for a specific record."""
    if not ANTISMASH_DATA:
        return jsonify({"error": "AntiSMASH data not found"}), 404
    
    record = next((r for r in ANTISMASH_DATA.get("records", []) if r.get("id") == record_id), None)
    if not record:
        return jsonify({"error": "Record not found"}), 404
    
    # Filter features to get only regions
    regions = []
    for feature in record.get("features", []):
        if feature.get("type") == "region":
            # Parse location to get start/end coordinates
            location_match = re.match(r'\[(\d+):(\d+)\]', feature.get("location", ""))
            start = int(location_match.group(1)) if location_match else 0
            end = int(location_match.group(2)) if location_match else 0
            
            region_info = {
                "id": f"region_{feature.get('qualifiers', {}).get('region_number', ['unknown'])[0]}",
                "region_number": feature.get('qualifiers', {}).get('region_number', ['unknown'])[0],
                "location": feature.get("location"),
                "start": start,
                "end": end,
                "product": feature.get('qualifiers', {}).get('product', ['unknown']),
                "rules": feature.get('qualifiers', {}).get('rules', [])
            }
            regions.append(region_info)
    
    return jsonify({
        "record_id": record_id,
        "regions": sorted(regions, key=lambda x: x['start'])
    })

@app.route('/api/records/<record_id>/regions/<region_id>/features')
def get_region_features(record_id, region_id):
    """API endpoint to get all features within a specific region."""
    if not ANTISMASH_DATA:
        return jsonify({"error": "AntiSMASH data not found"}), 404
    
    record = next((r for r in ANTISMASH_DATA.get("records", []) if r.get("id") == record_id), None)
    if not record:
        return jsonify({"error": "Record not found"}), 404
    
    # Find the region to get its boundaries
    region_feature = None
    for feature in record.get("features", []):
        if (feature.get("type") == "region" and 
            f"region_{feature.get('qualifiers', {}).get('region_number', [''])[0]}" == region_id):
            region_feature = feature
            break
    
    if not region_feature:
        return jsonify({"error": "Region not found"}), 404
    
    # Parse region boundaries
    region_location = region_feature.get("location", "")
    region_match = re.match(r'\[(\d+):(\d+)\]', region_location)
    if not region_match:
        return jsonify({"error": "Invalid region location format"}), 400
    
    region_start = int(region_match.group(1))
    region_end = int(region_match.group(2))
    
    # Get optional query parameters
    feature_type = request.args.get('type')
    
    # Filter features that fall within the region boundaries
    region_features = []
    for feature in record.get("features", []):
        # Skip the region feature itself
        if feature.get("type") == "region":
            continue
            
        # Parse feature location
        feature_location = feature.get("location", "")
        feature_match = re.match(r'\[(\d+):(\d+)\]', feature_location)
        if not feature_match:
            continue
            
        feature_start = int(feature_match.group(1))
        feature_end = int(feature_match.group(2))
        
        # Check if feature overlaps with region (allow partial overlaps)
        if not (feature_end < region_start or feature_start > region_end):
            # Apply type filter if specified
            if feature_type and feature.get("type") != feature_type:
                continue
            region_features.append(feature)
    
    return jsonify({
        "record_id": record_id,
        "region_id": region_id,
        "region_location": region_location,
        "region_boundaries": {"start": region_start, "end": region_end},
        "feature_type": feature_type or "all",
        "count": len(region_features),
        "features": region_features
    })

@app.route('/api/records/<record_id>/features')
def get_record_features(record_id):
    """API endpoint to get all features for a specific record."""
    if not ANTISMASH_DATA:
        return jsonify({"error": "AntiSMASH data not found"}), 404
    
    # Get optional query parameters
    feature_type = request.args.get('type')
    limit = request.args.get('limit', type=int)
    
    record = next((r for r in ANTISMASH_DATA.get("records", []) if r.get("id") == record_id), None)
    if not record:
        return jsonify({"error": "Record not found"}), 404
    
    features = record.get("features", [])
    
    # Filter by type if specified
    if feature_type:
        features = [f for f in features if f.get("type") == feature_type]
    
    # Limit results if specified
    if limit:
        features = features[:limit]
    
    return jsonify({
        "record_id": record_id,
        "feature_type": feature_type or "all",
        "count": len(features),
        "features": features
    })

@app.route('/api/feature-types')
def get_feature_types():
    """API endpoint to get all available feature types across all records."""
    if not ANTISMASH_DATA:
        return jsonify({"error": "AntiSMASH data not found"}), 404
    
    feature_types = set()
    for record in ANTISMASH_DATA.get("records", []):
        for feature in record.get("features", []):
            if "type" in feature:
                feature_types.add(feature["type"])
    
    return jsonify(sorted(list(feature_types)))

@app.route('/api/stats')
def get_stats():
    """API endpoint to get statistics about the dataset."""
    if not ANTISMASH_DATA:
        return jsonify({"error": "AntiSMASH data not found"}), 404
    
    # Calculate statistics
    records = ANTISMASH_DATA.get("records", [])
    total_features = sum(len(r.get("features", [])) for r in records)
    
    feature_type_counts = {}
    for record in records:
        for feature in record.get("features", []):
            ftype = feature.get("type", "unknown")
            feature_type_counts[ftype] = feature_type_counts.get(ftype, 0) + 1
    
    return jsonify({
        "total_records": len(records),
        "total_features": total_features,
        "feature_types": feature_type_counts,
        "version": ANTISMASH_DATA.get("version"),
        "schema": ANTISMASH_DATA.get("schema")
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "message": "Server is running"})

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500

def load_custom_data():
    """Load custom data from a file or database."""
    # This function is deprecated - now using ANTISMASH_DATA
    return load_antismash_data()

def main():
    """Main entry point for the application."""

    host = os.environ.get('BGCV_HOST', 'localhost')
    port = int(os.environ.get('BGCV_PORT', 5005))
    debug_mode = os.getenv('BGCV_DEBUG_MODE', 'False').lower() == 'true'

    if debug_mode:
        print(f"Running in debug mode on {host}:{port}")
        app.run(host=host, port=port, debug=True)
    else:
        print(f"Running server on {host}:{port}")
        serve(app, host=host, port=port, threads=4)

if __name__ == '__main__':
    main()
