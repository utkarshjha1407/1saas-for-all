# CareOps Testing Guide

## 🚀 Quick Start

### 1. Seed Test Data
```bash
# Windows
seed-test-data.bat

# Mac/Linux
cd Backend
source venv/bin/activate
python seed_test_data.py
```

This creates:
- ✅ 2 workspaces (Wellness Clinic, Therapy Center)
- ✅ 5 users (2 owners, 3 staff)
- ✅ 8 contacts
- ✅ 3 booking types
- ✅ 5 bookings (today, tomorrow, past)
- ✅ 8 inventory items (some low stock)
- ✅ 3 form templates
- ✅ 2 integrations

### 2. Start Application
```bash
# Terminal 1: Backend
cd Backend
venv\Scripts\activate
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 3. Login Credentials

**Wellness Clinic:**
- Owner: `alice@wellnessclinic.com` / `password123`
- Staff: `bob@wellnessclinic.com` / `password123`
- Staff: `carol@wellnessclinic.com` / `password123`

**Therapy Center:**
- Owner: `david@therapycenter.com` / `password123`
- Staff: `emma@therapycenter.com` / `password123`

---

## 📋 Test Scenarios

### Scenario 1: Owner Login & Dashboard
**Goal:** Verify owner can see workspace data

1. Login as `alice@wellnessclinic.com`
2. Should see Dashboard with:
   - Today's bookings (2)
   - Total contacts (5)
   - Active alerts
   - Forms status
3. ✅ Pass if dashboard shows real data

### Scenario 2: View & Manage Contacts
**Goal:** Test contact CRUD operations

1. Click "Contacts" in sidebar
2. Should see 5 contacts
3. Click "Add Contact"
4. Fill form:
   - Name: "Test Contact"
   - Email: "test@example.com"
   - Phone: "+1-555-9999"
5. Click "Create Contact"
6. ✅ Pass if contact appears in list
7. Search for "Test"
8. ✅ Pass if search works
9. Delete "Test Contact"
10. ✅ Pass if contact removed

### Scenario 3: View & Manage Inventory
**Goal:** Test inventory CRUD operations

1. Click "Inventory" in sidebar
2. Should see 5 items for Wellness Clinic
3. Note: Some items should show "Low" or "Critical" status
4. Click "Add Item"
5. Fill form:
   - Name: "Test Item"
   - Quantity: 10
   - Threshold: 5
   - Unit: "units"
6. Click "Create Item"
7. ✅ Pass if item appears with "OK" status
8. Click edit icon on "Test Item"
9. Change quantity to 2
10. Click "Update Item"
11. ✅ Pass if status changes to "Critical"
12. Delete "Test Item"
13. ✅ Pass if item removed

### Scenario 4: View Bookings
**Goal:** Verify booking display

1. Click "Bookings" in sidebar
2. Should see 5 bookings
3. Filter by "Upcoming"
4. ✅ Pass if shows only future bookings
5. Filter by "Past"
6. ✅ Pass if shows only past bookings
7. Click on a booking
8. ✅ Pass if details shown

### Scenario 5: View Forms
**Goal:** Verify form submissions display

1. Click "Forms" in sidebar
2. Should see form submissions (if any)
3. Check summary stats
4. ✅ Pass if stats match submissions

### Scenario 6: Staff Login (Limited Access)
**Goal:** Verify staff has limited permissions

1. Logout
2. Login as `bob@wellnessclinic.com`
3. Should see same workspace data
4. Try to access Settings (if available)
5. ✅ Pass if staff cannot access owner-only features

### Scenario 7: Switch Workspaces
**Goal:** Test multi-workspace isolation

1. Logout
2. Login as `david@therapycenter.com`
3. Should see Therapy Center data
4. Click "Contacts"
5. ✅ Pass if shows only 3 contacts (Therapy Center)
6. Click "Inventory"
7. ✅ Pass if shows only 3 items (Therapy Center)

### Scenario 8: Public Contact Form
**Goal:** Test public form submission

1. Open new browser tab (incognito)
2. Go to: `http://localhost:8080/public/wellness-clinic/contact`
3. Should see public contact form
4. Fill form:
   - Name: "Public Test"
   - Email: "public@test.com"
   - Phone: "+1-555-8888"
5. Submit form
6. ✅ Pass if success message shown
7. Login as Alice
8. Go to Contacts
9. ✅ Pass if "Public Test" appears with source "contact_form"

### Scenario 9: Public Booking Page
**Goal:** Test public booking

1. Open new browser tab (incognito)
2. Go to: `http://localhost:8080/public/wellness-clinic/book`
3. Should see booking types
4. Select "Initial Consultation"
5. Choose available date/time
6. Fill contact info
7. Submit booking
8. ✅ Pass if confirmation shown
9. Login as Alice
10. Go to Bookings
11. ✅ Pass if new booking appears

---

## 🐛 Known Issues & Fixes

### Issue 1: Inventory Not Saving
**Symptom:** Click "Create Item" but nothing happens

**Fix Applied:** ✅ Fixed mutation handling in Inventory.tsx

**Test:**
1. Add new inventory item
2. Should see success toast
3. Item should appear in list immediately

### Issue 2: Forms Page Empty
**Symptom:** Forms page shows "No submissions"

**Why:** Form submissions are created automatically when bookings are made

**Test:**
1. Create a booking (via public page or admin)
2. Forms should be sent automatically
3. Check Forms page for submissions

### Issue 3: Search Not Working
**Symptom:** Search box doesn't filter results

**Fix Applied:** ✅ Added search functionality to Contacts

**Test:**
1. Go to Contacts
2. Type in search box
3. Results should filter in real-time

---

## 🔍 API Testing

### Test Backend Directly

**Get Contacts:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/contacts
```

**Create Contact:**
```bash
curl -X POST http://localhost:8000/api/v1/contacts \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"API Test","email":"api@test.com"}'
```

**Get Inventory:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/v1/inventory
```

**Public Workspace Lookup:**
```bash
curl http://localhost:8000/api/v1/public/wellness-clinic
```

---

## 📊 Expected Results

### Dashboard Stats (Wellness Clinic)
- Total Bookings: 4
- Total Contacts: 5
- Today's Bookings: 2
- Pending Bookings: 1
- Low Stock Items: 2-3

### Inventory Status
- Cleaning Supplies: Critical (3/5)
- PPE Kits: Low (7/10)
- Hand Sanitizer: OK (15/10)
- Tissue Boxes: Critical (2/6)
- Welcome Packages: OK (25/5)

### Bookings Timeline
- Today: 2 bookings (confirmed)
- Tomorrow: 2 bookings (1 pending, 1 confirmed)
- Yesterday: 1 booking (completed)

---

## 🚨 Troubleshooting

### Backend Not Starting
```bash
cd Backend
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Not Starting
```bash
cd frontend
npm install
npm run dev
```

### Database Connection Error
1. Check `.env` file in Backend folder
2. Verify `SUPABASE_URL` and `SUPABASE_KEY`
3. Test connection: `python Backend/test_supabase.py`

### Seeding Fails
1. Check Supabase connection
2. Verify `SUPABASE_SERVICE_KEY` in `.env`
3. Check console for specific error
4. Try clearing data manually in Supabase dashboard

### Login Fails
1. Verify user was created (check Supabase dashboard)
2. Check password is exactly `password123`
3. Check backend logs for errors
4. Try re-seeding data

### No Data Showing
1. Verify you're logged in
2. Check browser console for errors
3. Check Network tab for failed API calls
4. Verify backend is running
5. Check workspace_id matches

---

## ✅ Success Criteria

### Minimum Viable Test
- ✅ Can login as owner
- ✅ Dashboard shows data
- ✅ Can view contacts
- ✅ Can add contact
- ✅ Can view inventory
- ✅ Can add inventory item
- ✅ Can view bookings
- ✅ Can view forms

### Full Feature Test
- ✅ All CRUD operations work
- ✅ Search/filter works
- ✅ Staff login works
- ✅ Multi-workspace isolation works
- ✅ Public forms work
- ✅ Public booking works
- ✅ Automation triggers (check backend logs)

---

## 📝 Test Checklist

### Pre-Test Setup
- [ ] Backend running on port 8000
- [ ] Frontend running on port 8080
- [ ] Test data seeded
- [ ] Browser console open (F12)
- [ ] Backend logs visible

### Core Features
- [ ] Login/Logout
- [ ] Dashboard displays
- [ ] Contacts CRUD
- [ ] Inventory CRUD
- [ ] Bookings view
- [ ] Forms view
- [ ] Search functionality
- [ ] Filter functionality

### Advanced Features
- [ ] Staff permissions
- [ ] Multi-workspace
- [ ] Public contact form
- [ ] Public booking page
- [ ] Form submissions
- [ ] Low stock alerts
- [ ] Booking status updates

### Edge Cases
- [ ] Empty states
- [ ] Error handling
- [ ] Loading states
- [ ] Invalid input
- [ ] Network errors
- [ ] Token expiration

---

## 🎯 Next Steps After Testing

1. **Document Issues:** Note any bugs or unexpected behavior
2. **Check Logs:** Review backend logs for errors
3. **Verify Data:** Check Supabase dashboard for data integrity
4. **Test Automation:** Verify background tasks are running
5. **Performance:** Check page load times
6. **Mobile:** Test on mobile devices
7. **Browsers:** Test on Chrome, Firefox, Safari

---

## 📞 Support

If you encounter issues:
1. Check this guide first
2. Review error messages in console
3. Check backend logs
4. Verify environment variables
5. Try re-seeding data
6. Check Supabase dashboard

---

## 🎉 Success!

If all tests pass, you have:
- ✅ Working authentication
- ✅ Functional CRUD operations
- ✅ Real-time data updates
- ✅ Multi-workspace support
- ✅ Public pages working
- ✅ Staff permissions
- ✅ Inventory tracking
- ✅ Booking management
- ✅ Form submissions

**You're ready to demo!** 🚀
