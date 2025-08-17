#!/usr/bin/env python3
"""
Web Application Integration Example

This example demonstrates how to integrate the CSV Data Cleaner library
into web applications using Flask and Django.

Key concepts covered:
- Flask integration for file upload and cleaning
- Django integration with models and forms
- REST API endpoints for data cleaning
- Real-time progress tracking
- Error handling and user feedback
- File management and cleanup

Prerequisites:
- Flask: pip install flask
- Django: pip install django
- Additional dependencies as needed
"""

import os
import json
import tempfile
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np

from csv_cleaner.core.cleaner import CSVCleaner
from csv_cleaner.core.config import Config
from csv_cleaner.core.temp_file_manager import get_temp_file_manager


def create_sample_data():
    """Create sample data for web application testing."""
    np.random.seed(42)

    data = {
        'user_id': range(1, 101),
        'username': [f'user_{i}' for i in range(1, 101)],
        'email': [f'user{i}@example.com' for i in range(1, 101)],
        'age': np.random.randint(18, 80, 100),
        'score': np.random.randint(0, 100, 100),
        'status': np.random.choice(['active', 'inactive', 'pending'], 100),
        'created_at': pd.date_range('2023-01-01', periods=100, freq='D')
    }

    df = pd.DataFrame(data)

    # Add some data quality issues
    df.loc[10:15, 'age'] = np.nan
    df.loc[20:25, 'email'] = ''
    df = pd.concat([df, df.iloc[:5]])  # Add duplicates

    return df


# ============================================================================
# Flask Integration Example
# ============================================================================

def flask_integration_example():
    """Demonstrate Flask integration with CSV Data Cleaner."""
    print("\n" + "=" * 60)
    print("🌐 Flask Integration Example")
    print("=" * 60)

    try:
        from flask import Flask, request, jsonify, render_template_string, send_file
        from werkzeug.utils import secure_filename
        import io

        print("✅ Flask available - demonstrating integration")

        # Create Flask app
        app = Flask(__name__)
        app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

        # Initialize CSV Cleaner with temp file management
        config = Config(temp_file_cleanup_enabled=True, temp_file_auto_cleanup=True)
        cleaner = CSVCleaner(config)
        temp_manager = get_temp_file_manager(config)

        # In-memory storage for demo (use database in production)
        uploads = {}
        cleaning_jobs = {}

        # HTML template for the upload form
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>CSV Data Cleaner - Web Interface</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .form-group { margin-bottom: 20px; }
                label { display: block; margin-bottom: 5px; font-weight: bold; }
                input, select, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
                button { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; }
                button:hover { background: #0056b3; }
                .progress { width: 100%; height: 20px; background: #f0f0f0; border-radius: 10px; overflow: hidden; }
                .progress-bar { height: 100%; background: #007bff; transition: width 0.3s; }
                .result { margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 4px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🧹 CSV Data Cleaner</h1>
                <p>Upload a CSV file and clean it using our powerful data cleaning library.</p>

                <form method="POST" enctype="multipart/form-data" id="uploadForm">
                    <div class="form-group">
                        <label for="file">Select CSV File:</label>
                        <input type="file" id="file" name="file" accept=".csv" required>
                    </div>

                    <div class="form-group">
                        <label for="operations">Cleaning Operations:</label>
                        <select id="operations" name="operations" multiple>
                            <option value="remove_duplicates">Remove Duplicates</option>
                            <option value="fill_missing">Fill Missing Values</option>
                            <option value="clean_names">Clean Column Names</option>
                            <option value="clean_text">Clean Text Data</option>
                            <option value="convert_types">Convert Data Types</option>
                            <option value="fix_dates">Fix Date Formats</option>
                        </select>
                        <small>Hold Ctrl/Cmd to select multiple operations</small>
                    </div>

                    <div class="form-group">
                        <label for="ai_enabled">Enable AI Suggestions:</label>
                        <input type="checkbox" id="ai_enabled" name="ai_enabled">
                        <small>Use AI to suggest optimal cleaning strategies</small>
                    </div>

                    <button type="submit">Clean Data</button>
                </form>

                <div id="progress" style="display: none;">
                    <h3>Processing...</h3>
                    <div class="progress">
                        <div class="progress-bar" id="progressBar" style="width: 0%"></div>
                    </div>
                    <p id="progressText">Initializing...</p>
                </div>

                <div id="result" class="result" style="display: none;"></div>
            </div>

            <script>
                document.getElementById('uploadForm').onsubmit = function(e) {
                    e.preventDefault();

                    const formData = new FormData(this);
                    const progress = document.getElementById('progress');
                    const result = document.getElementById('result');

                    progress.style.display = 'block';
                    result.style.display = 'none';

                    fetch('/clean', {
                        method: 'POST',
                        body: formData
                    })
                    .then(response => response.json())
                    .then(data => {
                        progress.style.display = 'none';
                        result.style.display = 'block';

                        if (data.success) {
                            result.innerHTML = `
                                <h3>✅ Cleaning Completed!</h3>
                                <p><strong>Original rows:</strong> ${data.original_rows}</p>
                                <p><strong>Cleaned rows:</strong> ${data.cleaned_rows}</p>
                                <p><strong>Rows removed:</strong> ${data.rows_removed}</p>
                                <p><strong>Processing time:</strong> ${data.processing_time}s</p>
                                <a href="/download/${data.job_id}" class="button">Download Cleaned File</a>
                            `;
                        } else {
                            result.innerHTML = `<h3>❌ Error: ${data.error}</h3>`;
                        }
                    })
                    .catch(error => {
                        progress.style.display = 'none';
                        result.innerHTML = `<h3>❌ Error: ${error.message}</h3>`;
                    });
                };
            </script>
        </body>
        </html>
        """

        @app.route('/')
        def index():
            """Main page with upload form."""
            return render_template_string(html_template)

        @app.route('/clean', methods=['POST'])
        def clean_file():
            """Handle file upload and cleaning."""
            try:
                # Check if file was uploaded
                if 'file' not in request.files:
                    return jsonify({'success': False, 'error': 'No file uploaded'})

                file = request.files['file']
                if file.filename == '':
                    return jsonify({'success': False, 'error': 'No file selected'})

                # Get cleaning operations
                operations = request.form.getlist('operations')
                if not operations:
                    operations = ['remove_duplicates', 'fill_missing', 'clean_names']

                ai_enabled = 'ai_enabled' in request.form

                # Save uploaded file using temp file manager
                filename = secure_filename(file.filename)
                temp_file_path = temp_manager.create_temp_file(
                    suffix=Path(filename).suffix,
                    prefix="upload_",
                    tags=["upload", "web"],
                    metadata={"original_filename": filename}
                )
                file.save(temp_file_path)

                # Generate job ID
                job_id = f"job_{int(time.time())}"

                # Store job info
                cleaning_jobs[job_id] = {
                    'input_path': str(temp_file_path),
                    'operations': operations,
                    'ai_enabled': ai_enabled,
                    'status': 'processing'
                }

                # Perform cleaning in background thread
                def clean_in_background():
                    try:
                        # Configure cleaner based on AI setting
                        if ai_enabled:
                            config = Config(ai_enabled=True)
                            cleaner = CSVCleaner(config)
                        else:
                            cleaner = CSVCleaner()

                        # Clean the file using temp file manager
                        output_path = temp_manager.create_temp_file(
                            suffix="_cleaned.csv",
                            prefix="cleaned_",
                            tags=["cleaned", "web"],
                            metadata={"job_id": job_id, "operations": operations}
                        )
                        summary = cleaner.clean_file(input_path, str(output_path), operations)

                        # Update job status
                        cleaning_jobs[job_id].update({
                            'status': 'completed',
                            'output_path': output_path,
                            'summary': summary
                        })

                    except Exception as e:
                        cleaning_jobs[job_id].update({
                            'status': 'error',
                            'error': str(e)
                        })

                # Start background thread
                thread = threading.Thread(target=clean_in_background)
                thread.start()

                return jsonify({
                    'success': True,
                    'job_id': job_id,
                    'message': 'Cleaning started'
                })

            except Exception as e:
                return jsonify({'success': False, 'error': str(e)})

        @app.route('/status/<job_id>')
        def get_status(job_id):
            """Get cleaning job status."""
            if job_id not in cleaning_jobs:
                return jsonify({'error': 'Job not found'})

            job = cleaning_jobs[job_id]
            return jsonify({
                'status': job['status'],
                'summary': job.get('summary', {}),
                'error': job.get('error')
            })

        @app.route('/download/<job_id>')
        def download_file(job_id):
            """Download cleaned file."""
            if job_id not in cleaning_jobs:
                return jsonify({'error': 'Job not found'})

            job = cleaning_jobs[job_id]
            if job['status'] != 'completed':
                return jsonify({'error': 'Job not completed'})

            return send_file(
                job['output_path'],
                as_attachment=True,
                download_name=f"cleaned_{os.path.basename(job['input_path'])}"
            )

        @app.route('/api/clean', methods=['POST'])
        def api_clean():
            """REST API endpoint for cleaning."""
            try:
                data = request.get_json()

                if not data or 'file_path' not in data:
                    return jsonify({'error': 'file_path is required'}), 400

                file_path = data['file_path']
                operations = data.get('operations', ['remove_duplicates', 'fill_missing'])
                ai_enabled = data.get('ai_enabled', False)

                # Validate file exists
                if not os.path.exists(file_path):
                    return jsonify({'error': 'File not found'}), 404

                # Configure cleaner
                if ai_enabled:
                    config = Config(ai_enabled=True)
                    cleaner = CSVCleaner(config)
                else:
                    cleaner = CSVCleaner()

                # Create output path using temp file manager
                output_path = temp_manager.create_temp_file(
                    suffix="_cleaned.csv",
                    prefix="api_cleaned_",
                    tags=["api", "cleaned"],
                    metadata={"operations": operations, "ai_enabled": ai_enabled}
                )

                # Clean the file
                summary = cleaner.clean_file(file_path, str(output_path), operations)

                return jsonify({
                    'success': True,
                    'output_path': output_path,
                    'summary': summary
                })

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        print("🌐 Flask app created with endpoints:")
        print("   - GET  /              - Upload form")
        print("   - POST /clean         - Clean uploaded file")
        print("   - GET  /status/<id>   - Check job status")
        print("   - GET  /download/<id> - Download cleaned file")
        print("   - POST /api/clean     - REST API endpoint")

        # Create sample data for testing
        sample_df = create_sample_data()
        sample_file = "sample_web_data.csv"
        sample_df.to_csv(sample_file, index=False)
        print(f"\n📁 Sample data created: {sample_file}")

        print("\n🚀 To run the Flask app:")
        print("   app.run(debug=True, port=5000)")
        print("\n📝 Test with curl:")
        print(f"   curl -X POST http://localhost:5000/api/clean \\")
        print(f"        -H 'Content-Type: application/json' \\")
        print(f"        -d '{{\"file_path\": \"{sample_file}\", \"operations\": [\"remove_duplicates\", \"fill_missing\"]}}'")

        return app

    except ImportError:
        print("❌ Flask not available. Install with: pip install flask")
        return None


# ============================================================================
# Django Integration Example
# ============================================================================

def django_integration_example():
    """Demonstrate Django integration with CSV Data Cleaner."""
    print("\n" + "=" * 60)
    print("🐍 Django Integration Example")
    print("=" * 60)

    try:
        import django
        from django.conf import settings
        from django.http import JsonResponse
        from django.views.decorators.csrf import csrf_exempt
        from django.views.decorators.http import require_http_methods
        from django.core.files.storage import default_storage
        from django.core.files.base import ContentFile

        print("✅ Django available - demonstrating integration")

        # Django model example
        django_model_code = '''
from django.db import models
from django.contrib.auth.models import User
import uuid

class CleaningJob(models.Model):
    """Model for tracking CSV cleaning jobs."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    original_file = models.FileField(upload_to='uploads/')
    cleaned_file = models.FileField(upload_to='cleaned/', null=True, blank=True)
    operations = models.JSONField(default=list)
    ai_enabled = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    summary = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Cleaning Job {self.id} - {self.status}"
        '''

        # Django view example
        django_view_code = '''
import os
import tempfile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import CleaningJob
from csv_cleaner.core.cleaner import CSVCleaner
from csv_cleaner.core.config import Config

@csrf_exempt
@require_http_methods(["POST"])
def clean_csv_view(request):
    """Django view for cleaning CSV files."""
    try:
        # Get uploaded file
        if 'file' not in request.FILES:
            return JsonResponse({'error': 'No file uploaded'}, status=400)

        uploaded_file = request.FILES['file']

        # Get cleaning parameters
        operations = request.POST.getlist('operations', [])
        if not operations:
            operations = ['remove_duplicates', 'fill_missing', 'clean_names']

        ai_enabled = request.POST.get('ai_enabled', 'false').lower() == 'true'

        # Create cleaning job
        job = CleaningJob.objects.create(
            user=request.user,
            original_file=uploaded_file,
            operations=operations,
            ai_enabled=ai_enabled,
            status='pending'
        )

        # Start cleaning in background
        import threading
        thread = threading.Thread(target=process_cleaning_job, args=(job.id,))
        thread.start()

        return JsonResponse({
            'success': True,
            'job_id': str(job.id),
            'message': 'Cleaning job created'
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def process_cleaning_job(job_id):
    """Background task to process cleaning job."""
    try:
        job = CleaningJob.objects.get(id=job_id)
        job.status = 'processing'
        job.save()

        # Configure cleaner
        if job.ai_enabled:
            config = Config(ai_enabled=True)
            cleaner = CSVCleaner(config)
        else:
            cleaner = CSVCleaner()

        # Create temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_input:
            # Save uploaded file to temp
            for chunk in job.original_file.chunks():
                temp_input.write(chunk)
            temp_input_path = temp_input.name

        temp_output_path = temp_input_path.replace('.csv', '_cleaned.csv')

        # Clean the file
        summary = cleaner.clean_file(temp_input_path, temp_output_path, job.operations)

        # Save cleaned file
        with open(temp_output_path, 'rb') as f:
            cleaned_file = ContentFile(f.read())
            job.cleaned_file.save(f'cleaned_{job.original_file.name}', cleaned_file)

        # Update job status
        job.status = 'completed'
        job.summary = summary
        job.save()

        # Cleanup temp files
        os.unlink(temp_input_path)
        os.unlink(temp_output_path)

    except Exception as e:
        job = CleaningJob.objects.get(id=job_id)
        job.status = 'failed'
        job.error_message = str(e)
        job.save()

@require_http_methods(["GET"])
def job_status_view(request, job_id):
    """Get cleaning job status."""
    try:
        job = CleaningJob.objects.get(id=job_id)
        return JsonResponse({
            'job_id': str(job.id),
            'status': job.status,
            'summary': job.summary,
            'error_message': job.error_message,
            'created_at': job.created_at.isoformat(),
            'completed_at': job.completed_at.isoformat() if job.completed_at else None
        })
    except CleaningJob.DoesNotExist:
        return JsonResponse({'error': 'Job not found'}, status=404)

@require_http_methods(["GET"])
def download_cleaned_file(request, job_id):
    """Download cleaned file."""
    try:
        job = CleaningJob.objects.get(id=job_id)
        if job.status != 'completed' or not job.cleaned_file:
            return JsonResponse({'error': 'File not ready'}, status=400)

        response = HttpResponse(job.cleaned_file, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{job.cleaned_file.name}"'
        return response

    except CleaningJob.DoesNotExist:
        return JsonResponse({'error': 'Job not found'}, status=404)
        '''

        # Django URL configuration
        django_urls_code = '''
from django.urls import path
from . import views

urlpatterns = [
    path('clean/', views.clean_csv_view, name='clean_csv'),
    path('status/<uuid:job_id>/', views.job_status_view, name='job_status'),
    path('download/<uuid:job_id>/', views.download_cleaned_file, name='download_file'),
]
        '''

        print("🐍 Django integration components:")
        print("   📋 Model: CleaningJob for tracking jobs")
        print("   🔧 Views: clean_csv_view, job_status_view, download_cleaned_file")
        print("   🌐 URLs: RESTful endpoints for file cleaning")

        print("\n📁 Files to create:")
        print("   - models.py: CleaningJob model")
        print("   - views.py: Cleaning views")
        print("   - urls.py: URL routing")
        print("   - forms.py: File upload forms")
        print("   - templates/: HTML templates")

        print("\n🚀 Django integration features:")
        print("   - File upload handling")
        print("   - Background job processing")
        print("   - Job status tracking")
        print("   - File storage management")
        print("   - User authentication")
        print("   - Error handling")

        return True

    except ImportError:
        print("❌ Django not available. Install with: pip install django")
        return None


# ============================================================================
# REST API Example
# ============================================================================

def rest_api_example():
    """Demonstrate REST API integration."""
    print("\n" + "=" * 60)
    print("🔌 REST API Integration Example")
    print("=" * 60)

    # API client example
    api_client_code = '''
import requests
import json
import time

class CSVCleanerAPI:
    """Client for CSV Data Cleaner REST API."""

    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()

    def clean_file(self, file_path, operations=None, ai_enabled=False):
        """Clean a CSV file via API."""
        if operations is None:
            operations = ['remove_duplicates', 'fill_missing', 'clean_names']

        # Upload file
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'operations': operations,
                'ai_enabled': ai_enabled
            }

            response = self.session.post(f"{self.base_url}/clean", files=files, data=data)
            response.raise_for_status()

            result = response.json()
            return result['job_id']

    def get_status(self, job_id):
        """Get job status."""
        response = self.session.get(f"{self.base_url}/status/{job_id}")
        response.raise_for_status()
        return response.json()

    def download_file(self, job_id, output_path):
        """Download cleaned file."""
        response = self.session.get(f"{self.base_url}/download/{job_id}")
        response.raise_for_status()

        with open(output_path, 'wb') as f:
            f.write(response.content)

        return output_path

    def clean_and_wait(self, file_path, operations=None, ai_enabled=False, timeout=300):
        """Clean file and wait for completion."""
        job_id = self.clean_file(file_path, operations, ai_enabled)

        start_time = time.time()
        while time.time() - start_time < timeout:
            status = self.get_status(job_id)

            if status['status'] == 'completed':
                return status
            elif status['status'] == 'failed':
                raise Exception(f"Cleaning failed: {status.get('error_message', 'Unknown error')}")

            time.sleep(2)  # Poll every 2 seconds

        raise TimeoutError("Cleaning job timed out")

# Usage example
if __name__ == "__main__":
    api = CSVCleanerAPI()

    # Clean a file
    job_id = api.clean_file("data.csv", operations=["remove_duplicates", "fill_missing"])
    print(f"Job started: {job_id}")

    # Wait for completion
    result = api.clean_and_wait("data.csv")
    print(f"Cleaning completed: {result}")

    # Download result
    api.download_file(job_id, "cleaned_data.csv")
    print("File downloaded: cleaned_data.csv")
        '''

    print("🔌 REST API client example created")
    print("   📡 HTTP endpoints for file cleaning")
    print("   🔄 Asynchronous job processing")
    print("   📊 Status monitoring")
    print("   💾 File download")

    print("\n📝 API Usage:")
    print("   - POST /clean - Upload and clean file")
    print("   - GET  /status/<id> - Check job status")
    print("   - GET  /download/<id> - Download result")

    return api_client_code


def main():
    """Run all web integration examples."""
    print("🚀 Starting Web Application Integration Examples")
    print("=" * 70)

    # Flask integration
    flask_app = flask_integration_example()

    # Django integration
    django_integration_example()

    # REST API example
    rest_api_example()

    print("\n" + "=" * 70)
    print("✅ All web integration examples completed!")
    print("\n📚 Key Integration Patterns:")
    print("   - File upload and validation")
    print("   - Background job processing")
    print("   - Real-time status updates")
    print("   - Error handling and recovery")
    print("   - File storage management")
    print("   - User authentication and authorization")

    print("\n🔧 Next Steps:")
    print("   - Implement in your web framework of choice")
    print("   - Add user authentication and file permissions")
    print("   - Implement progress tracking and notifications")
    print("   - Add file validation and security measures")
    print("   - Consider using message queues for large files")

    if flask_app:
        print(f"\n🌐 Flask app ready to run!")
        print("   Uncomment the following line to start the server:")
        print("   flask_app.run(debug=True, port=5000)")


if __name__ == "__main__":
    main()
