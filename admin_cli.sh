#!/bin/bash

# The Direct Tree Admin CLI Tool
# Use this to manage your platform when web interface isn't accessible

API_URL="http://localhost:8001/api"
DB_NAME="test_direct_tree"

echo "🌴 THE DIRECT TREE - ADMIN CLI TOOL 🌴"
echo "========================================"

# Function to create admin user
create_admin() {
    echo "📧 Creating Admin User..."
    read -p "Enter admin email: " email
    read -s -p "Enter admin password: " password
    echo

    # Create user in database directly
    mongosh --quiet $DB_NAME --eval "
    db.users.insertOne({
        id: 'admin-' + Math.random().toString(36).substr(2, 9),
        email: '$email',
        password_hash: '\$2b\$12\$dummy_hash_for_now',
        first_name: 'Admin',
        last_name: 'User', 
        role: 'admin',
        is_verified: true,
        created_at: new Date(),
        updated_at: new Date()
    })
    "
    
    echo "✅ Admin user created: $email"
    echo "⚠️  Password needs to be set via login API"
}

# Function to list pending businesses
list_pending_businesses() {
    echo "🏢 PENDING BUSINESSES:"
    echo "====================="
    
    mongosh --quiet $DB_NAME --eval "
    db.businesses.find({status: 'pending'}).forEach(function(business) {
        print('');
        print('ID: ' + business.id);
        print('Name: ' + business.business_name);
        print('Email: ' + business.email);
        print('Category: ' + business.category);
        print('Island: ' + business.island);
        print('License: ' + business.license_number);
        print('Status: ' + business.status);
        print('---');
    })
    "
}

# Function to approve business
approve_business() {
    echo "✅ APPROVE BUSINESS:"
    echo "==================="
    read -p "Enter business ID to approve: " business_id
    
    if [ -z "$business_id" ]; then
        echo "❌ Business ID required"
        return
    fi
    
    mongosh --quiet $DB_NAME --eval "
    const result = db.businesses.updateOne(
        {id: '$business_id'}, 
        {\$set: {status: 'approved', updated_at: new Date()}}
    );
    if (result.matchedCount > 0) {
        print('✅ Business approved successfully!');
    } else {
        print('❌ Business not found');
    }
    "
}

# Function to reject business
reject_business() {
    echo "❌ REJECT BUSINESS:"
    echo "=================="
    read -p "Enter business ID to reject: " business_id
    
    if [ -z "$business_id" ]; then
        echo "❌ Business ID required"
        return
    fi
    
    mongosh --quiet $DB_NAME --eval "
    const result = db.businesses.updateOne(
        {id: '$business_id'}, 
        {\$set: {status: 'rejected', updated_at: new Date()}}
    );
    if (result.matchedCount > 0) {
        print('✅ Business rejected successfully!');
    } else {
        print('❌ Business not found');
    }
    "
}

# Function to show platform stats
show_stats() {
    echo "📊 PLATFORM STATISTICS:"
    echo "======================="
    
    mongosh --quiet $DB_NAME --eval "
    const totalUsers = db.users.countDocuments();
    const totalBusinesses = db.businesses.countDocuments();
    const pendingBusinesses = db.businesses.countDocuments({status: 'pending'});
    const approvedBusinesses = db.businesses.countDocuments({status: 'approved'});
    
    print('👥 Total Users: ' + totalUsers);
    print('🏢 Total Businesses: ' + totalBusinesses);
    print('⏳ Pending Businesses: ' + pendingBusinesses);
    print('✅ Approved Businesses: ' + approvedBusinesses);
    "
}

# Function to list all users
list_users() {
    echo "👥 ALL USERS:"
    echo "============="
    
    mongosh --quiet $DB_NAME --eval "
    db.users.find({}, {email: 1, role: 1, is_verified: 1}).forEach(function(user) {
        print('Email: ' + user.email + ' | Role: ' + user.role + ' | Verified: ' + user.is_verified);
    })
    "
}

# Main menu
while true; do
    echo ""
    echo "🎯 ADMIN MENU:"
    echo "1. Create Admin User"
    echo "2. List Pending Businesses"
    echo "3. Approve Business"
    echo "4. Reject Business"
    echo "5. Platform Statistics"
    echo "6. List All Users"
    echo "7. Exit"
    echo ""
    read -p "Choose option (1-7): " choice
    
    case $choice in
        1) create_admin ;;
        2) list_pending_businesses ;;
        3) approve_business ;;
        4) reject_business ;;
        5) show_stats ;;
        6) list_users ;;
        7) echo "👋 Goodbye!"; exit 0 ;;
        *) echo "❌ Invalid option" ;;
    esac
done