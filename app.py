import os
from flask import Flask, render_template, abort, request
from dotenv import load_dotenv
from supabase import create_client, Client
import uuid

# --- Configuration ---
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Flask App
app = Flask(__name__,static_folder='static', template_folder='templates')

# Initialize Supabase Client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    print(f"Error initializing Supabase client: {e}")
    supabase = None

# --- Routes ---

@app.route('/verify/<uuid:certificate_id>')
def verify_certificate(certificate_id: uuid.UUID):
    """
    This page displays the verification card for a given certificate ID.
    The <uuid:certificate_id> part ensures that only valid UUIDs are accepted.
    """
    if not supabase:
        return "Error: Supabase client is not initialized.", 500

    # Convert UUID object to a string to query Supabase
    cert_id_str = str(certificate_id)
    
    try:
        # Fetch the record from Supabase that matches the certificate_id
        response = supabase.table("certificates").select("*").eq("certificate_id", cert_id_str).execute()
        
        # Check if any data was returned
        if response.data:
            certificate_data = response.data[0]
            # The URL to be shared on LinkedIn is the current page's URL
            share_url = request.url
            return render_template('certificate.html', cert=certificate_data, share_url=share_url)
        else:
            # If no data is found for that ID, show a 404 error page
            abort(404)
            
    except Exception as e:
        print(f"Error fetching data from Supabase: {e}")
        return "An error occurred while trying to verify the certificate.", 500


@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 error page."""
    return render_template('not_found.html'), 404


if __name__ == '__main__':
    # Runs the Flask app in debug mode for development
    app.run(debug=True)