"""
Seed test data for CareOps
Creates test users, workspaces, contacts, bookings, inventory, etc.
"""
import asyncio
from datetime import datetime, timedelta
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from app.core.security import get_password_hash

load_dotenv()

# Initialize Supabase
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

async def clear_existing_data():
    """Clear existing test data"""
    print("🗑️  Clearing existing data...")
    
    # Delete in reverse order of dependencies
    tables = [
        "inventory_usage",
        "form_submissions",
        "messages",
        "conversations",
        "bookings",
        "availability_slots",
        "booking_types",
        "form_templates",
        "inventory_items",
        "alerts",
        "integrations",
        "contacts",
        "users",
        "workspaces",
    ]
    
    for table in tables:
        try:
            supabase.table(table).delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
            print(f"  ✓ Cleared {table}")
        except Exception as e:
            print(f"  ⚠️  Could not clear {table}: {e}")

async def seed_workspaces_and_users():
    """Create test workspaces and users"""
    print("\n👥 Creating workspaces and users...")
    
    workspaces_data = []
    users_data = []
    
    # Workspace 1: Wellness Clinic (Owner: Alice)
    workspace1 = {
        "name": "Wellness Clinic",
        "address": "123 Health St, San Francisco, CA 94102",
        "timezone": "America/Los_Angeles",
        "contact_email": "contact@wellnessclinic.com",
        "status": "active",
        "onboarding_step": "activated",
        "slug": "wellness-clinic",
        "primary_color": "#3b82f6",
        "secondary_color": "#8b5cf6",
        "is_onboarding_complete": True,
    }
    
    # Create workspace first (without owner_id)
    ws1_response = supabase.table("workspaces").insert({
        **workspace1,
        "owner_id": "00000000-0000-0000-0000-000000000000"  # Temporary
    }).execute()
    ws1_id = ws1_response.data[0]["id"]
    
    # Owner: Alice (Wellness Clinic)
    alice = {
        "email": "alice@wellnessclinic.com",
        "password_hash": get_password_hash("password123"),
        "full_name": "Alice Johnson",
        "role": "owner",
        "workspace_id": ws1_id,
        "is_active": True,
    }
    alice_response = supabase.table("users").insert(alice).execute()
    alice_id = alice_response.data[0]["id"]
    
    # Update workspace with correct owner_id
    supabase.table("workspaces").update({"owner_id": alice_id}).eq("id", ws1_id).execute()
    
    # Staff: Bob (Wellness Clinic)
    bob = {
        "email": "bob@wellnessclinic.com",
        "password_hash": get_password_hash("password123"),
        "full_name": "Bob Smith",
        "role": "staff",
        "workspace_id": ws1_id,
        "is_active": True,
    }
    supabase.table("users").insert(bob).execute()
    
    # Staff: Carol (Wellness Clinic)
    carol = {
        "email": "carol@wellnessclinic.com",
        "password_hash": get_password_hash("password123"),
        "full_name": "Carol Williams",
        "role": "staff",
        "workspace_id": ws1_id,
        "is_active": True,
    }
    supabase.table("users").insert(carol).execute()
    
    # Workspace 2: Therapy Center (Owner: David)
    workspace2 = {
        "name": "Therapy Center",
        "address": "456 Care Ave, Los Angeles, CA 90001",
        "timezone": "America/Los_Angeles",
        "contact_email": "info@therapycenter.com",
        "status": "active",
        "onboarding_step": "activated",
        "slug": "therapy-center",
        "primary_color": "#10b981",
        "secondary_color": "#3b82f6",
        "is_onboarding_complete": True,
    }
    
    ws2_response = supabase.table("workspaces").insert({
        **workspace2,
        "owner_id": "00000000-0000-0000-0000-000000000000"
    }).execute()
    ws2_id = ws2_response.data[0]["id"]
    
    # Owner: David (Therapy Center)
    david = {
        "email": "david@therapycenter.com",
        "password_hash": get_password_hash("password123"),
        "full_name": "David Brown",
        "role": "owner",
        "workspace_id": ws2_id,
        "is_active": True,
    }
    david_response = supabase.table("users").insert(david).execute()
    david_id = david_response.data[0]["id"]
    
    supabase.table("workspaces").update({"owner_id": david_id}).eq("id", ws2_id).execute()
    
    # Staff: Emma (Therapy Center)
    emma = {
        "email": "emma@therapycenter.com",
        "password_hash": get_password_hash("password123"),
        "full_name": "Emma Davis",
        "role": "staff",
        "workspace_id": ws2_id,
        "is_active": True,
    }
    supabase.table("users").insert(emma).execute()
    
    print(f"  ✓ Created 2 workspaces")
    print(f"  ✓ Created 5 users (2 owners, 3 staff)")
    print(f"\n📧 Login Credentials:")
    print(f"  Owner 1: alice@wellnessclinic.com / password123")
    print(f"  Staff 1: bob@wellnessclinic.com / password123")
    print(f"  Staff 2: carol@wellnessclinic.com / password123")
    print(f"  Owner 2: david@therapycenter.com / password123")
    print(f"  Staff 3: emma@therapycenter.com / password123")
    
    return ws1_id, ws2_id

async def seed_contacts(ws1_id, ws2_id):
    """Create test contacts"""
    print("\n📇 Creating contacts...")
    
    contacts = [
        # Wellness Clinic contacts
        {"workspace_id": ws1_id, "name": "Sarah Mitchell", "email": "sarah@email.com", "phone": "+1-555-0101", "source": "contact_form"},
        {"workspace_id": ws1_id, "name": "James Kerr", "email": "james.k@email.com", "phone": "+1-555-0102", "source": "booking_page"},
        {"workspace_id": ws1_id, "name": "Emily Chen", "email": "emily.c@email.com", "phone": "+1-555-0103", "source": "contact_form"},
        {"workspace_id": ws1_id, "name": "Robert Davis", "email": "r.davis@email.com", "phone": "+1-555-0104", "source": "manual"},
        {"workspace_id": ws1_id, "name": "Lisa Wang", "email": "lisa.w@email.com", "phone": "+1-555-0105", "source": "booking_page"},
        
        # Therapy Center contacts
        {"workspace_id": ws2_id, "name": "Michael Brown", "email": "m.brown@email.com", "phone": "+1-555-0201", "source": "contact_form"},
        {"workspace_id": ws2_id, "name": "Jennifer Lee", "email": "j.lee@email.com", "phone": "+1-555-0202", "source": "booking_page"},
        {"workspace_id": ws2_id, "name": "Thomas Wilson", "email": "t.wilson@email.com", "phone": "+1-555-0203", "source": "manual"},
    ]
    
    response = supabase.table("contacts").insert(contacts).execute()
    print(f"  ✓ Created {len(contacts)} contacts")
    return response.data

async def seed_booking_types_and_availability(ws1_id, ws2_id):
    """Create booking types and availability"""
    print("\n📅 Creating booking types and availability...")
    
    # Wellness Clinic booking types
    bt1 = supabase.table("booking_types").insert({
        "workspace_id": ws1_id,
        "name": "Initial Consultation",
        "description": "First-time consultation session",
        "duration_minutes": 60,
        "location": "123 Health St, Room 101",
        "is_active": True,
    }).execute()
    bt1_id = bt1.data[0]["id"]
    
    bt2 = supabase.table("booking_types").insert({
        "workspace_id": ws1_id,
        "name": "Follow-up Session",
        "description": "Follow-up appointment",
        "duration_minutes": 30,
        "location": "123 Health St, Room 102",
        "is_active": True,
    }).execute()
    bt2_id = bt2.data[0]["id"]
    
    # Therapy Center booking types
    bt3 = supabase.table("booking_types").insert({
        "workspace_id": ws2_id,
        "name": "Therapy Session",
        "description": "Individual therapy session",
        "duration_minutes": 50,
        "location": "456 Care Ave, Suite 200",
        "is_active": True,
    }).execute()
    bt3_id = bt3.data[0]["id"]
    
    # Add availability slots (Mon-Fri, 9 AM - 5 PM)
    availability = []
    for day in range(5):  # Monday to Friday
        for bt_id in [bt1_id, bt2_id, bt3_id]:
            availability.append({
                "workspace_id": ws1_id if bt_id in [bt1_id, bt2_id] else ws2_id,
                "booking_type_id": bt_id,
                "day_of_week": day,
                "start_time": "09:00:00",
                "end_time": "17:00:00",
            })
    
    supabase.table("availability_slots").insert(availability).execute()
    
    print(f"  ✓ Created 3 booking types")
    print(f"  ✓ Created {len(availability)} availability slots")
    
    return [bt1_id, bt2_id, bt3_id]

async def seed_bookings(ws1_id, ws2_id, contacts, booking_type_ids):
    """Create test bookings"""
    print("\n📆 Creating bookings...")
    
    # Get contacts for each workspace
    ws1_contacts = [c for c in contacts if c["workspace_id"] == ws1_id]
    ws2_contacts = [c for c in contacts if c["workspace_id"] == ws2_id]
    
    bookings = []
    
    # Today's bookings
    today = datetime.now()
    bookings.append({
        "workspace_id": ws1_id,
        "booking_type_id": booking_type_ids[0],
        "contact_id": ws1_contacts[0]["id"],
        "scheduled_at": (today + timedelta(hours=2)).isoformat(),
        "status": "confirmed",
        "notes": "First consultation",
    })
    
    bookings.append({
        "workspace_id": ws1_id,
        "booking_type_id": booking_type_ids[1],
        "contact_id": ws1_contacts[1]["id"],
        "scheduled_at": (today + timedelta(hours=4)).isoformat(),
        "status": "confirmed",
        "notes": "Follow-up session",
    })
    
    # Tomorrow's bookings
    tomorrow = today + timedelta(days=1)
    bookings.append({
        "workspace_id": ws1_id,
        "booking_type_id": booking_type_ids[0],
        "contact_id": ws1_contacts[2]["id"],
        "scheduled_at": (tomorrow + timedelta(hours=10)).isoformat(),
        "status": "pending",
        "notes": "New patient consultation",
    })
    
    bookings.append({
        "workspace_id": ws2_id,
        "booking_type_id": booking_type_ids[2],
        "contact_id": ws2_contacts[0]["id"],
        "scheduled_at": (tomorrow + timedelta(hours=14)).isoformat(),
        "status": "confirmed",
        "notes": "Therapy session",
    })
    
    # Past bookings
    yesterday = today - timedelta(days=1)
    bookings.append({
        "workspace_id": ws1_id,
        "booking_type_id": booking_type_ids[1],
        "contact_id": ws1_contacts[3]["id"],
        "scheduled_at": yesterday.isoformat(),
        "status": "completed",
        "notes": "Completed session",
    })
    
    response = supabase.table("bookings").insert(bookings).execute()
    print(f"  ✓ Created {len(bookings)} bookings")
    return response.data

async def seed_inventory(ws1_id, ws2_id):
    """Create inventory items"""
    print("\n📦 Creating inventory items...")
    
    items = [
        # Wellness Clinic inventory
        {"workspace_id": ws1_id, "name": "Cleaning Supplies", "description": "Disinfectant and sanitizer", "quantity": 3, "low_stock_threshold": 5, "unit": "bottles"},
        {"workspace_id": ws1_id, "name": "PPE Kits", "description": "Personal protective equipment", "quantity": 7, "low_stock_threshold": 10, "unit": "kits"},
        {"workspace_id": ws1_id, "name": "Hand Sanitizer", "description": "70% alcohol sanitizer", "quantity": 15, "low_stock_threshold": 10, "unit": "bottles"},
        {"workspace_id": ws1_id, "name": "Tissue Boxes", "description": "Facial tissues", "quantity": 2, "low_stock_threshold": 6, "unit": "boxes"},
        {"workspace_id": ws1_id, "name": "Welcome Packages", "description": "New client welcome materials", "quantity": 25, "low_stock_threshold": 5, "unit": "packages"},
        
        # Therapy Center inventory
        {"workspace_id": ws2_id, "name": "Office Supplies", "description": "Pens, paper, folders", "quantity": 50, "low_stock_threshold": 20, "unit": "items"},
        {"workspace_id": ws2_id, "name": "Water Bottles", "description": "Bottled water for clients", "quantity": 12, "low_stock_threshold": 15, "unit": "bottles"},
        {"workspace_id": ws2_id, "name": "Tissues", "description": "Box tissues", "quantity": 8, "low_stock_threshold": 10, "unit": "boxes"},
    ]
    
    response = supabase.table("inventory_items").insert(items).execute()
    print(f"  ✓ Created {len(items)} inventory items")
    print(f"  ✓ {len([i for i in items if i['quantity'] <= i['low_stock_threshold']])} items are low stock")

async def seed_form_templates(ws1_id, ws2_id):
    """Create form templates"""
    print("\n📋 Creating form templates...")
    
    templates = [
        {
            "workspace_id": ws1_id,
            "name": "Intake Form",
            "description": "New patient intake form",
            "fields": [
                {"name": "medical_history", "type": "textarea", "label": "Medical History", "required": True},
                {"name": "allergies", "type": "text", "label": "Allergies", "required": False},
                {"name": "emergency_contact", "type": "text", "label": "Emergency Contact", "required": True},
            ],
            "booking_type_ids": [],
        },
        {
            "workspace_id": ws1_id,
            "name": "Service Agreement",
            "description": "Terms of service agreement",
            "fields": [
                {"name": "agree_terms", "type": "checkbox", "label": "I agree to the terms", "required": True},
                {"name": "signature", "type": "text", "label": "Signature", "required": True},
            ],
            "booking_type_ids": [],
        },
        {
            "workspace_id": ws2_id,
            "name": "Therapy Intake",
            "description": "Initial therapy assessment",
            "fields": [
                {"name": "reason", "type": "textarea", "label": "Reason for seeking therapy", "required": True},
                {"name": "goals", "type": "textarea", "label": "Therapy goals", "required": False},
            ],
            "booking_type_ids": [],
        },
    ]
    
    response = supabase.table("form_templates").insert(templates).execute()
    print(f"  ✓ Created {len(templates)} form templates")

async def seed_integrations(ws1_id, ws2_id):
    """Create integration configurations"""
    print("\n🔌 Creating integrations...")
    
    integrations = [
        {
            "workspace_id": ws1_id,
            "provider": "sendgrid",
            "config": {"api_key": "test_key", "from_email": "noreply@wellnessclinic.com"},
            "status": "active",
        },
        {
            "workspace_id": ws2_id,
            "provider": "sendgrid",
            "config": {"api_key": "test_key", "from_email": "noreply@therapycenter.com"},
            "status": "active",
        },
    ]
    
    supabase.table("integrations").insert(integrations).execute()
    print(f"  ✓ Created {len(integrations)} integrations")

async def main():
    """Main seeding function"""
    print("🌱 Seeding CareOps Test Data\n")
    print("=" * 50)
    
    # Clear existing data
    await clear_existing_data()
    
    # Seed data
    ws1_id, ws2_id = await seed_workspaces_and_users()
    contacts = await seed_contacts(ws1_id, ws2_id)
    booking_type_ids = await seed_booking_types_and_availability(ws1_id, ws2_id)
    await seed_bookings(ws1_id, ws2_id, contacts, booking_type_ids)
    await seed_inventory(ws1_id, ws2_id)
    await seed_form_templates(ws1_id, ws2_id)
    await seed_integrations(ws1_id, ws2_id)
    
    print("\n" + "=" * 50)
    print("✅ Seeding complete!\n")
    print("🚀 You can now login with:")
    print("   • alice@wellnessclinic.com / password123 (Owner)")
    print("   • bob@wellnessclinic.com / password123 (Staff)")
    print("   • david@therapycenter.com / password123 (Owner)")
    print("\n🌐 Public URLs:")
    print("   • http://localhost:8080/public/wellness-clinic/contact")
    print("   • http://localhost:8080/public/wellness-clinic/book")
    print("   • http://localhost:8080/public/therapy-center/contact")
    print("   • http://localhost:8080/public/therapy-center/book")

if __name__ == "__main__":
    asyncio.run(main())
