"""Test script to verify Supabase connection and user insertion"""
import sys
import os
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.db.supabase_client import get_supabase_service
from app.core.security import hash_password, verify_password
from app.models.enums import UserRole

def test_supabase_connection():
    """Test Supabase connection"""
    print("=" * 60)
    print("Testing Supabase Connection")
    print("=" * 60)
    
    try:
        supabase = get_supabase_service()
        print("[OK] Supabase service client initialized")
        
        # Test connection by querying a table
        result = supabase.table("users").select("id").limit(1).execute()
        print(f"[OK] Connection successful - can query users table")
        print(f"  Found {len(result.data)} existing users")
        
        return supabase
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return None

def test_password_hashing():
    """Test password hashing"""
    print("\n" + "=" * 60)
    print("Testing Password Hashing")
    print("=" * 60)
    
    test_password = "Test123!"
    print(f"Testing with password: {test_password} (length: {len(test_password)} chars, {len(test_password.encode('utf-8'))} bytes)")
    
    try:
        # Hash the password
        hashed = hash_password(test_password)
        print(f"[OK] Password hashed successfully")
        print(f"  Original: {test_password}")
        print(f"  Hash: {hashed[:30]}...")
        print(f"  Hash length: {len(hashed)} characters")
        print(f"  Hash format: {hashed[:4]} (should start with $2b$)")
        
        # Verify the password
        is_valid = verify_password(test_password, hashed)
        print(f"[OK] Password verification: {'PASSED' if is_valid else 'FAILED'}")
        
        # Test wrong password
        is_invalid = verify_password("WrongPassword", hashed)
        print(f"[OK] Wrong password test: {'PASSED' if not is_invalid else 'FAILED'}")
        
        return hashed
    except Exception as e:
        print(f"[ERROR] Password hashing failed: {e}")
        return None

def create_test_user(supabase, email, password, full_name, workspace_name):
    """Create a test user in Supabase"""
    print(f"\n" + "=" * 60)
    print(f"Creating Test User: {email}")
    print("=" * 60)
    
    try:
        # Check if user already exists
        existing = supabase.table("users").select("id, email").eq("email", email).execute()
        if existing.data:
            print(f"[WARN] User {email} already exists")
            user_id = existing.data[0]["id"]
            print(f"  User ID: {user_id}")
            return user_id
        
        # Hash the password
        hashed_password = hash_password(password)
        print(f"[OK] Password hashed")
        
        # Create user
        user_data = {
            "email": email,
            "password_hash": hashed_password,
            "full_name": full_name,
            "role": UserRole.OWNER.value,
            "is_active": True,
            "workspace_id": None,
        }
        
        print(f"  Inserting user data...")
        user_result = supabase.table("users").insert(user_data).execute()
        
        if not user_result.data:
            print(f"[ERROR] Failed to create user - no data returned")
            return None
        
        user_id = user_result.data[0]["id"]
        print(f"[OK] User created successfully")
        print(f"  User ID: {user_id}")
        print(f"  Email: {user_result.data[0]['email']}")
        print(f"  Full Name: {user_result.data[0]['full_name']}")
        print(f"  Role: {user_result.data[0]['role']}")
        
        # Create workspace
        workspace_data = {
            "name": workspace_name,
            "address": "",
            "contact_email": email,
            "status": "setup",
            "onboarding_step": "workspace_created",
            "owner_id": user_id,
        }
        
        print(f"\n  Creating workspace...")
        workspace_result = supabase.table("workspaces").insert(workspace_data).execute()
        
        if not workspace_result.data:
            print(f"[ERROR] Failed to create workspace")
            # Clean up user
            supabase.table("users").delete().eq("id", user_id).execute()
            return None
        
        workspace_id = workspace_result.data[0]["id"]
        print(f"[OK] Workspace created successfully")
        print(f"  Workspace ID: {workspace_id}")
        print(f"  Workspace Name: {workspace_result.data[0]['name']}")
        
        # Update user with workspace_id
        supabase.table("users").update({
            "workspace_id": workspace_id
        }).eq("id", user_id).execute()
        
        print(f"[OK] User updated with workspace_id")
        
        return user_id
        
    except Exception as e:
        print(f"[ERROR] Failed to create user: {e}")
        import traceback
        traceback.print_exc()
        return None

def verify_user_password(supabase, email, password):
    """Verify a user's password"""
    print(f"\n" + "=" * 60)
    print(f"Verifying Password for: {email}")
    print("=" * 60)
    
    try:
        # Get user
        user_result = supabase.table("users").select("*").eq("email", email).execute()
        
        if not user_result.data:
            print(f"[ERROR] User not found")
            return False
        
        user = user_result.data[0]
        stored_hash = user["password_hash"]
        
        print(f"[OK] User found")
        print(f"  User ID: {user['id']}")
        print(f"  Stored hash: {stored_hash[:30]}...")
        
        # Verify password
        is_valid = verify_password(password, stored_hash)
        
        if is_valid:
            print(f"[OK] Password verification: PASSED")
        else:
            print(f"[ERROR] Password verification: FAILED")
        
        return is_valid
        
    except Exception as e:
        print(f"[ERROR] Verification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def list_all_users(supabase):
    """List all users"""
    print(f"\n" + "=" * 60)
    print("All Users in Database")
    print("=" * 60)
    
    try:
        result = supabase.table("users").select("id, email, full_name, role, workspace_id, is_active").execute()
        
        if not result.data:
            print("No users found")
            return
        
        print(f"Found {len(result.data)} users:\n")
        for user in result.data:
            print(f"  ID: {user['id']}")
            print(f"  Email: {user['email']}")
            print(f"  Name: {user['full_name']}")
            print(f"  Role: {user['role']}")
            print(f"  Workspace ID: {user.get('workspace_id', 'None')}")
            print(f"  Active: {user['is_active']}")
            print()
            
    except Exception as e:
        print(f"[ERROR] Failed to list users: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function"""
    print("\n" + "=" * 60)
    print("Supabase Test Script")
    print("=" * 60 + "\n")
    
    # Test connection
    supabase = test_supabase_connection()
    if not supabase:
        print("\n[ERROR] Cannot proceed without Supabase connection")
        return
    
    # Test password hashing
    hashed = test_password_hashing()
    if not hashed:
        print("\n[ERROR] Cannot proceed without password hashing")
        return
    
    # Create test users
    test_users = [
        {
            "email": "test@example.com",
            "password": "Test123!",
            "full_name": "Test User",
            "workspace_name": "Test Workspace"
        },
        {
            "email": "admin@example.com",
            "password": "Admin123!",
            "full_name": "Admin User",
            "workspace_name": "Admin Workspace"
        }
    ]
    
    created_users = []
    for user_data in test_users:
        user_id = create_test_user(
            supabase,
            user_data["email"],
            user_data["password"],
            user_data["full_name"],
            user_data["workspace_name"]
        )
        if user_id:
            created_users.append((user_data["email"], user_data["password"]))
    
    # Verify passwords
    for email, password in created_users:
        verify_user_password(supabase, email, password)
    
    # List all users
    list_all_users(supabase)
    
    print("\n" + "=" * 60)
    print("Test Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
