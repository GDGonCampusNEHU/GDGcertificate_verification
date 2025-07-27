import os
import uuid
import qrcode
from dotenv import load_dotenv
from supabase import create_client, Client

# --- Configuration ---

# Load environment variables from .env file
load_dotenv()

# Get Supabase credentials from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# !! IMPORTANT !!
# This is the base URL for your future verification web page.
# The QR code will point here. You will need to build a simple web app
# at this address that can read the 'id' and verify it against Supabase.
VERIFICATION_BASE_URL = "https://gdgcertificate-verification.vercel.app/verify"

# Create a directory to store the generated QR codes
OUTPUT_QR_DIR = "qr_codes"
os.makedirs(OUTPUT_QR_DIR, exist_ok=True)

# --- GDG on Campus NEHU Core Team 2024-25 Data ---
# Team members list updated from the official GDG community page.
team_members = [
    {"name": "Abhishek Kumar Rai", "team": "Organizer","id":"7783750a-72ec-429e-9b78-25aca4d24f38"},
    {"name": "Aradhya Jha", "team": "Co-organizer","id":"3e20a361-df55-417c-8039-b8f7c49a8baa"},
    {"name": "Devanshi Sanganeria", "team": "Head, Event Management Team","id":"da281c8c-2c27-4e1c-a7c1-dde7ced5d7a4"},
    {"name": "Anirudh Gupta", "team": "Head, Event Management Team","id":"253b82fe-bfed-405a-a817-e120b53582a7"},
    {"name": "Dibakar Patar", "team": "Head, Event Management Team","id":"ac44a028-6c87-4008-b3d1-997f30f5c8e4"},
    {"name": "Chandrasmita Gayan", "team": "Head, Event Management Team","id":"80e8a816-eae3-4106-a1cc-945139a726fa"},
    {"name": "Sazeed Taj", "team": "Head, Media & Communication Team","id":"08063948-1f3f-4b75-ab4e-694481611661"},
    {"name": "Bandeep Bhatta", "team": "Head, Outreach & Partnership Team","id":"eb573c62-0315-4502-bbcd-4568c43ce25d"},
    {"name": "Rideep Kumar Kakati", "team": "Head, Creative & Content Team","id":"8dee7d5d-4586-4061-8691-d8b0d2548821"},
    {"name": "SOUMOJIT BHUIN", "team": "Head, Creative & Content Team","id":"7b8e0d82-131d-4b91-a439-d7ffe5818583"},
    {"name": "Shiva Sai Naluvala", "team": "Head, Creative & Content Team","id":"10e3ff4b-6c92-4925-8761-500828e37093"},
    {"name": "Shekhar Pachlore", "team": "Head, Technical & Academics Team","id":"87b98cd4-1d6c-4be2-a30e-7631663ba898"}
]


def main():
    """
    Main function to generate certificate data, create QR codes,
    and upload the information to Supabase.
    """
    print("Starting certificate generation process...")

    # Initialize Supabase client
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Successfully connected to Supabase.")
    except Exception as e:
        print(f"Error connecting to Supabase: {e}")
        return

    # Process each team member
    for member in team_members:
        member_name = member["name"]
        member_team = member["team"]
        id=member["id"]
        print(f"\nProcessing member: {member_name} ({member_team})")

        # 1. Generate a unique certificate ID
        certificate_id = str(uuid.uuid4())
        print(f"  - Generated Certificate ID: {certificate_id}")

        # 2. Create the full verification URL
        verification_url = f"{VERIFICATION_BASE_URL}/{id}"
        print(f"  - Verification URL: {verification_url}")

        # 3. Generate the QR Code
        qr_image_path = os.path.join("qr_codes", f"{member_name.replace(' ', '_').lower()}_qr.png")
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(verification_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(qr_image_path)
            print(f"  - QR Code saved to: {qr_image_path}")
        except Exception as e:
            print(f"  - Error generating QR code: {e}")
            continue # Skip to the next member

        # 4. Prepare data for Supabase
        # For now, we use a placeholder URL for the certificate image.
        # You will update this in Supabase later.
        demo_cert_image_url = f"https://example.com/certs/{member_name.replace(' ', '_').lower()}.pdf"
        
        data_to_insert = {
            "member_name": member_name,
            "member_team": member_team,
            "certificate_id": certificate_id,
            "certificate_image_url": demo_cert_image_url,
            "verification_url": verification_url
        }

        # 5. Insert the data into the Supabase 'certificates' table
        try:
            data, count = supabase.table("certificates").insert(data_to_insert).execute()
            # The response format for execute() is a tuple (data, count)
            if data[1]: # Check if the list inside the data tuple is not empty
                print(f"  - Successfully inserted data for {member_name} into Supabase.")
            else:
                print(f"  - Failed to insert data for {member_name} into Supabase.")
        except Exception as e:
            print(f"  - Error inserting data into Supabase: {e}")

    print("\nCertificate generation process finished!")


if __name__ == "__main__":
    main()