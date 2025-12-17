# tests/test_routes.py
import unittest
from datetime import date
from app import create_app, db
from app.models import User, Listing

class RouteTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test app and client"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['WTF_CSRF_ENABLED'] = False
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        """Clean up after tests"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def create_user(self, username='testuser', email='test@sjsu.edu', password='password'):
        user = User(username=username, email=email, full_name='Test User')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
    
    def login(self, username, password):
        return self.client.post('/auth/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)
    
    def logout(self):
        return self.client.get('/auth/logout', follow_redirects=True)
    
    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SJSU Housing', response.data)
    
    def test_register_page_loads(self):
        response = self.client.get('/auth/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)
    
    def test_user_registration(self):
        response = self.client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@sjsu.edu',
            'full_name': 'New User',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        user = User.query.filter_by(username='newuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'newuser@sjsu.edu')
    
    def test_login_logout(self):
        user = self.create_user()
        response = self.login('testuser', 'password')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)  # assuming redirect after login
        
        response = self.logout()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SJSU Housing', response.data)  # homepage after logout
    
    def test_listings_page_loads(self):
        response = self.client.get('/listings')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Available Listings', response.data)
    
    def test_create_listing_requires_login(self):
        response = self.client.get('/listing/create')
        self.assertEqual(response.status_code, 302)  # redirect to login
    
    def test_create_listing_authenticated(self):
        user = self.create_user()
        self.login('testuser', 'password')
        
        response = self.client.post('/listing/create', data={
            'title': 'Test Listing',
            'description': 'Description for test',
            'address': '123 Main St',
            'city': 'San Jose',
            'state': 'CA',
            'zip_code': '95112',
            'price_per_month': 1200,
            'bedrooms': 2,
            'bathrooms': 1,
            'square_feet': 800,
            'available_from': '2025-01-01',
            'available_to': '2025-12-31',
            'amenities': 'WiFi, Parking'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        listing = Listing.query.filter_by(title='Test Listing').first()
        self.assertIsNotNone(listing)
        self.assertEqual(listing.owner_id, user.id)
    
    def test_listing_detail_page(self):
        user = self.create_user()
        listing = Listing(
            title='Test Listing',
            description='Test description',
            address='123 Main St',
            city='San Jose',
            state='CA',
            zip_code='95112',
            price_per_month=1200.00,
            bedrooms=2,
            bathrooms=1,
            available_from=date.today(),
            available_to=date(2025, 12, 31),
            owner_id=user.id
        )
        db.session.add(listing)
        db.session.commit()
        
        response = self.client.get(f'/listing/{listing.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Listing', response.data)
        self.assertIn(b'Test description', response.data)
        self.assertIn(b'$1200.00', response.data)

if __name__ == '__main__':
    unittest.main()
