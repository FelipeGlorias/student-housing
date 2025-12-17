# tests/test_models.py
import unittest
from datetime import date
from app import create_app, db
from app.models import User, Listing, Booking, Review

class ModelTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test app and database"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
    def tearDown(self):
        """Clean up after tests"""
        db.session.rollback()
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_user_creation(self):
        """Test creating a user"""
        user = User(username='testuser', email='test@sjsu.edu', full_name='Test User')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@sjsu.edu')
        self.assertTrue(user.check_password('password123'))
        self.assertFalse(user.check_password('wrongpassword'))
    
    def test_listing_creation(self):
        """Test creating a listing"""
        user = User(username='owner', email='owner@sjsu.edu', full_name='Owner')
        user.set_password('password')
        db.session.add(user)
        db.session.commit()
        
        listing = Listing(
            title='Cozy Apartment',
            description='Great place near campus',
            address='123 Main St',
            city='San Jose',
            state='CA',
            zip_code='95112',
            price_per_month=1200.00,
            bedrooms=2,
            bathrooms=1.0,
            square_feet=800,
            available_from=date.today(),
            available_to=date(2025, 12, 31),
            amenities='WiFi, Parking',
            owner_id=user.id
        )
        db.session.add(listing)
        db.session.commit()
        
        self.assertEqual(listing.title, 'Cozy Apartment')
        self.assertEqual(listing.owner_id, user.id)
        self.assertEqual(listing.bedrooms, 2)
        self.assertEqual(listing.bathrooms, 1.0)
        self.assertEqual(listing.amenities, 'WiFi, Parking')
        self.assertTrue(listing.is_active)
    
    def test_booking_creation(self):
        """Test creating a booking"""
        # Create owner and tenant
        owner = User(username='owner', email='owner@sjsu.edu', full_name='Owner')
        owner.set_password('password')
        tenant = User(username='tenant', email='tenant@sjsu.edu', full_name='Tenant')
        tenant.set_password('password')
        db.session.add_all([owner, tenant])
        db.session.commit()
        
        # Create listing
        listing = Listing(
            title='Test Listing',
            description='Description',
            address='123 Test St',
            city='San Jose',
            state='CA',
            zip_code='95112',
            price_per_month=1000.00,
            bedrooms=1,
            bathrooms=1.0,
            available_from=date.today(),
            available_to=date(2025, 12, 31),
            owner_id=owner.id
        )
        db.session.add(listing)
        db.session.commit()
        
        # Create booking
        booking = Booking(
            listing_id=listing.id,
            tenant_id=tenant.id,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 1),
            total_price=5000.00
        )
        db.session.add(booking)
        db.session.commit()
        
        self.assertEqual(booking.status, 'pending')
        self.assertEqual(booking.tenant_id, tenant.id)
        self.assertEqual(booking.listing_id, listing.id)
        self.assertEqual(booking.total_price, 5000.00)
    
    def test_review_creation(self):
        """Test creating a review"""
        owner = User(username='owner', email='owner@sjsu.edu', full_name='Owner')
        owner.set_password('password')
        reviewer = User(username='reviewer', email='reviewer@sjsu.edu', full_name='Reviewer')
        reviewer.set_password('password')
        db.session.add_all([owner, reviewer])
        db.session.commit()
        
        listing = Listing(
            title='Test Listing',
            description='Description',
            address='123 Test St',
            city='San Jose',
            state='CA',
            zip_code='95112',
            price_per_month=1000.00,
            bedrooms=1,
            bathrooms=1.0,
            available_from=date.today(),
            available_to=date(2025, 12, 31),
            owner_id=owner.id
        )
        db.session.add(listing)
        db.session.commit()
        
        review = Review(
            listing_id=listing.id,
            reviewer_id=reviewer.id,
            rating=5,
            comment='Great place!',
            review_type='listing'
        )
        db.session.add(review)
        db.session.commit()
        
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Great place!')
        self.assertEqual(review.reviewer_id, reviewer.id)
        self.assertEqual(review.listing_id, listing.id)
        self.assertEqual(review.review_type, 'listing')

if __name__ == '__main__':
    unittest.main()
