import os
from flask import Flask, render_template, abort, request
from supabase import create_client, Client
import uuid


SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

# --- Explicitly Define Paths for Vercel ---
# This guarantees that Flask knows where to find the 'static' and 'templates' folders.
base_dir = os.path.abspath(os.path.dirname(__file__))
app = Flask(
    __name__,
    static_folder=os.path.join(base_dir, 'static'),
    template_folder=os.path.join(base_dir, 'templates')
)

# --- Supabase Client Initialization ---
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Error initializing Supabase client: {e}")
else:
    print("Supabase URL and Key are not configured in environment variables.")

# The rest of your routes and functions go here...
# For example:
@app.route('/verify/<uuid:certificate_id>')
def verify_certificate(certificate_id: uuid.UUID):
    if not supabase:
        return "Error: Supabase client is not initialized or configured.", 500

    cert_id_str = str(certificate_id)
    try:
        response = supabase.table("certificates").select("*").eq("certificate_id", cert_id_str).execute()
        if response.data:
            return render_template('certificate.html', cert=response.data[0], request=request)
        else:
            abort(404)
    except Exception as e:
        print(f"Error fetching data from Supabase: {e}")
        return "An error occurred while trying to verify the certificate.", 500

@app.errorhandler(404)
def page_not_found(e):
    return render_template('not_found.html'), 404

