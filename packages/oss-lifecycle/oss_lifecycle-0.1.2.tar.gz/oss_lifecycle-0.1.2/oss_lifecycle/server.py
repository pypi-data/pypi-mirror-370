from flask import Flask, request, jsonify, send_from_directory
import sys
import os
import subprocess
import json

app = Flask(__name__, static_folder='.')

@app.route('/run_github_gather', methods=['POST'])
def run_github_gather():
    try:
        # Get input from request
        data = request.get_json()
        owner = data.get('owner')
        repo = data.get('repo')

        if not owner or not repo:
            return jsonify({
                'success': False, 
                'error': 'Owner and repository name are required'
            })

        # Construct repo name and URL
        repo_name = f"{owner}/{repo}"
        
        # Run the github_gather script
        result = subprocess.run([
            sys.executable, 
            '-m', 'oss_lifecycle.github_gather',
            repo_name
        ], 
        capture_output=True, 
        text=True, 
        cwd=os.getcwd())

        # Check if the script ran successfully
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'output': result.stdout
            })
        else:
            return jsonify({
                'success': False,
                'error': result.stderr
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

# Serve static files
@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

@app.route('/run_bass_model', methods=['POST'])
def run_bass_model():
    try:
        # Get input from request
        data = request.get_json()
        owner = data.get('owner')
        repo = data.get('repo')

        if not owner or not repo:
            return jsonify({
                'success': False, 
                'error': 'Owner and repository name are required'
            })

        # Construct repo name
        repo_name = f"{owner}/{repo}"
        repo_string = f"{owner}-{repo}"
        
        # Run the Bass model fitting script
        result = subprocess.run([
            sys.executable, 
            '-m', 'oss_lifecycle.fit_bass',
            repo_name
        ], 
        capture_output=True, 
        text=True, 
        cwd=os.getcwd())

        # Check if the script ran successfully
        if result.returncode == 0:
            # Read the generated image files
            image_files = [
                f"images/{repo_string}_fit_contributors.png",
                f"images/{repo_string}_contributors_to_end.png"
            ]
            
            return jsonify({
                'success': True,
                'output': result.stdout,
                'images': image_files
            })
        else:
            return jsonify({
                'success': False,
                'error': result.stderr
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/run_innovation_model', methods=['POST'])
def run_innovation_model():
    try:
        # Get input from request
        data = request.get_json()
        owner = data.get('owner')
        repo = data.get('repo')

        if not owner or not repo:
            return jsonify({
                'success': False, 
                'error': 'Owner and repository name are required'
            })

        # Construct repo name
        repo_name = f"{owner}/{repo}"
        repo_string = f"{owner}-{repo}"
        
        # Run the innovation model fitting script
        result = subprocess.run([
            sys.executable, 
            '-m', 'oss_lifecycle.fit_innovation',
            repo_name
        ], 
        capture_output=True, 
        text=True, 
        cwd=os.getcwd())

        # Check if the script ran successfully
        if result.returncode == 0:
            # Read the generated image files
            image_files = [
                f"images/{repo_string}_innovation_fit.png",
                f"images/{repo_string}_polyfit_innovation.png",
                f"images/{repo_string}_forecasts.png"
            ]
            
            return jsonify({
                'success': True,
                'output': result.stdout,
                'images': image_files
            })
        else:
            return jsonify({
                'success': False,
                'error': result.stderr
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
