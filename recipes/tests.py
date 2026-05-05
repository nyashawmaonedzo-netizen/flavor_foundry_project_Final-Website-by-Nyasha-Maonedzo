from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from .models import Category, Product, Order, OrderItem, Review, Wishlist


class CategoryModelTest(TestCase):
    """Test Category model"""
    
    def setUp(self):
        self.category = Category.objects.create(name="Pasta", description="Italian pasta dishes")
    
    def test_category_str(self):
        self.assertEqual(str(self.category), "Pasta")
    
    def test_category_unique_name(self):
        with self.assertRaises(Exception):
            Category.objects.create(name="Pasta")


class ProductModelTest(TestCase):
    """Test Product model"""
    
    def setUp(self):
        self.category = Category.objects.create(name="Pasta")
        self.product = Product.objects.create(
            name="Spaghetti",
            description="Italian pasta",
            price=Decimal("10.99"),
            category=self.category,
            stock=10,
            available=True
        )
    
    def test_product_str(self):
        self.assertEqual(str(self.product), "Spaghetti")
    
    def test_is_in_stock(self):
        self.assertTrue(self.product.is_in_stock())
        self.product.available = False
        self.assertFalse(self.product.is_in_stock())
    
    def test_get_average_rating_no_reviews(self):
        self.assertEqual(self.product.get_average_rating(), 0)
    
    def test_get_average_rating_with_reviews(self):
        user = User.objects.create_user(username="reviewer", password="test123")
        Review.objects.create(product=self.product, user=user, rating=4)
        Review.objects.create(product=self.product, user=User.objects.create_user(username="reviewer2", password="test123"), rating=5)
        self.assertEqual(self.product.get_average_rating(), 4.5)


class ReviewModelTest(TestCase):
    """Test Review model"""
    
    def setUp(self):
        self.user = User.objects.create_user(username="reviewer", password="test123")
        self.category = Category.objects.create(name="Pasta")
        self.product = Product.objects.create(
            name="Spaghetti",
            description="Italian pasta",
            price=Decimal("10.99"),
            category=self.category
        )
    
    def test_review_creation(self):
        review = Review.objects.create(
            product=self.product,
            user=self.user,
            rating=5,
            comment="Excellent product!"
        )
        self.assertEqual(str(review), "reviewer - Spaghetti (5★)")
    
    def test_unique_review_per_user_product(self):
        Review.objects.create(product=self.product, user=self.user, rating=5)
        with self.assertRaises(Exception):
            Review.objects.create(product=self.product, user=self.user, rating=3)


class WishlistModelTest(TestCase):
    """Test Wishlist model"""
    
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="test123")
        self.category = Category.objects.create(name="Pasta")
        self.product = Product.objects.create(
            name="Spaghetti",
            description="Italian pasta",
            price=Decimal("10.99"),
            category=self.category
        )
    
    def test_wishlist_creation(self):
        wishlist = Wishlist.objects.create(user=self.user)
        self.assertEqual(str(wishlist), "testuser's Wishlist")
    
    def test_add_to_wishlist(self):
        wishlist = Wishlist.objects.create(user=self.user)
        wishlist.products.add(self.product)
        self.assertIn(self.product, wishlist.products.all())


class HomeViewTest(TestCase):
    """Test Home/Product listing view"""
    
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Pasta")
        self.product = Product.objects.create(
            name="Spaghetti",
            description="Italian pasta",
            price=Decimal("10.99"),
            category=self.category,
            stock=10
        )
    
    def test_home_page_loads(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')
    
    def test_products_displayed(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, "Spaghetti")
    
    def test_search_functionality(self):
        response = self.client.get(reverse('home') + '?search=Spaghetti')
        self.assertContains(response, "Spaghetti")
    
    def test_category_filter(self):
        response = self.client.get(reverse('home') + f'?category={self.category.id}')
        self.assertContains(response, "Spaghetti")


class ProductDetailViewTest(TestCase):
    """Test Product detail view"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="test123")
        self.category = Category.objects.create(name="Pasta")
        self.product = Product.objects.create(
            name="Spaghetti",
            description="Italian pasta",
            price=Decimal("10.99"),
            category=self.category,
            stock=10
        )
    
    def test_product_detail_page_loads(self):
        response = self.client.get(reverse('product_detail', args=[self.product.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Spaghetti")
    
    def test_product_not_found(self):
        response = self.client.get(reverse('product_detail', args=[999]))
        self.assertEqual(response.status_code, 404)
    
    def test_review_form_visible_for_authenticated_user(self):
        self.client.login(username="testuser", password="test123")
        response = self.client.get(reverse('product_detail', args=[self.product.id]))
        self.assertContains(response, "Leave a Review")


class CartViewTest(TestCase):
    """Test Cart functionality"""
    
    def setUp(self):
        self.client = Client()
        self.category = Category.objects.create(name="Pasta")
        self.product = Product.objects.create(
            name="Spaghetti",
            price=Decimal("10.99"),
            category=self.category,
            stock=10,
            available=True
        )
    
    def test_add_to_cart(self):
        response = self.client.post(reverse('add_to_cart', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(self.product.id), self.client.session.get('cart', {}))
    
    def test_cart_detail_page(self):
        self.client.post(reverse('add_to_cart', args=[self.product.id]))
        response = self.client.get(reverse('cart_detail'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Spaghetti")
    
    def test_remove_from_cart(self):
        self.client.post(reverse('add_to_cart', args=[self.product.id]))
        response = self.client.post(reverse('remove_from_cart', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(str(self.product.id), self.client.session.get('cart', {}))
    
    def test_cannot_add_unavailable_product(self):
        self.product.available = False
        self.product.save()
        response = self.client.post(reverse('add_to_cart', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn(str(self.product.id), self.client.session.get('cart', {}))


class CheckoutViewTest(TestCase):
    """Test Checkout functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="test123", email="test@example.com")
        self.category = Category.objects.create(name="Pasta")
        self.product = Product.objects.create(
            name="Spaghetti",
            price=Decimal("10.99"),
            category=self.category,
            stock=10
        )
    
    def test_checkout_requires_login(self):
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_checkout_with_empty_cart(self):
        self.client.login(username="testuser", password="test123")
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith('/') or 'home' in response.url)
    
    def test_checkout_page_loads_with_items(self):
        self.client.login(username="testuser", password="test123")
        self.client.post(reverse('add_to_cart', args=[self.product.id]))
        response = self.client.get(reverse('checkout'))
        self.assertEqual(response.status_code, 200)
    
    def test_checkout_creates_order(self):
        self.client.login(username="testuser", password="test123")
        self.client.post(reverse('add_to_cart', args=[self.product.id]))
        response = self.client.post(reverse('checkout'), {
            'full_name': 'John Doe',
            'email': 'john@example.com',
            'shipping_address': '123 Main St',
            'city': 'New York',
            'postal_code': '10001'
        })
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(response.status_code, 302)


class AuthenticationViewTest(TestCase):
    """Test Authentication views"""
    
    def setUp(self):
        self.client = Client()
    
    def test_register_page_loads(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
    
    def test_user_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!'
        })
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(Wishlist.objects.filter(user__username='newuser').exists())
    
    def test_login_page_loads(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
    
    def test_user_login(self):
        User.objects.create_user(username="testuser", password="test123")
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'test123'
        })
        self.assertEqual(response.status_code, 302)
    
    def test_user_logout(self):
        user = User.objects.create_user(username="testuser", password="test123")
        self.client.login(username="testuser", password="test123")
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)


class WishlistViewTest(TestCase):
    """Test Wishlist views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="test123")
        self.wishlist = Wishlist.objects.create(user=self.user)
        self.category = Category.objects.create(name="Pasta")
        self.product = Product.objects.create(
            name="Spaghetti",
            price=Decimal("10.99"),
            category=self.category,
            stock=10
        )
    
    def test_wishlist_requires_login(self):
        response = self.client.get(reverse('wishlist'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
    
    def test_wishlist_page_loads(self):
        self.client.login(username="testuser", password="test123")
        response = self.client.get(reverse('wishlist'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'wishlist.html')
    
    def test_add_to_wishlist(self):
        self.client.login(username="testuser", password="test123")
        response = self.client.post(reverse('add_to_wishlist', args=[self.product.id]))
        self.assertTrue(self.wishlist.products.filter(id=self.product.id).exists())
    
    def test_remove_from_wishlist(self):
        self.wishlist.products.add(self.product)
        self.client.login(username="testuser", password="test123")
        response = self.client.post(reverse('remove_from_wishlist', args=[self.product.id]))
        self.assertFalse(self.wishlist.products.filter(id=self.product.id).exists())


class ProductManagementTest(TestCase):
    """Test Product CRUD for staff users"""
    
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(username="staff", password="test123", is_staff=True)
        self.regular_user = User.objects.create_user(username="user", password="test123")
        self.category = Category.objects.create(name="Pasta")
        self.product = Product.objects.create(
            name="Spaghetti",
            price=Decimal("10.99"),
            category=self.category,
            stock=10
        )
    
    def test_add_product_requires_staff(self):
        response = self.client.get(reverse('add_product'))
        self.assertEqual(response.status_code, 302)
    
    def test_staff_can_add_product(self):
        self.client.login(username="staff", password="test123")
        response = self.client.post(reverse('add_product'), {
            'name': 'Penne',
            'description': 'Italian pasta',
            'price': '12.99',
            'category': self.category.id,
            'available': True,
            'stock': 20
        })
        self.assertEqual(Product.objects.filter(name='Penne').count(), 1)
    
    def test_staff_can_edit_product(self):
        self.client.login(username="staff", password="test123")
        response = self.client.post(reverse('edit_product', args=[self.product.id]), {
            'name': 'Spaghetti Updated',
            'description': 'Italian pasta',
            'price': '11.99',
            'category': self.category.id,
            'available': True,
            'stock': 15
        })
        self.product.refresh_from_db()
        self.assertEqual(self.product.name, 'Spaghetti Updated')
    
    def test_staff_can_delete_product(self):
        self.client.login(username="staff", password="test123")
        product_id = self.product.id
        response = self.client.post(reverse('delete_product', args=[product_id]))
        self.assertFalse(Product.objects.filter(id=product_id).exists())
    
    def test_regular_user_cannot_manage_products(self):
        self.client.login(username="user", password="test123")
        response = self.client.get(reverse('add_product'))
        self.assertEqual(response.status_code, 302)


class ReviewCreationTest(TestCase):
    """Test Review functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="reviewer", password="test123")
        self.category = Category.objects.create(name="Pasta")
        self.product = Product.objects.create(
            name="Spaghetti",
            price=Decimal("10.99"),
            category=self.category,
            stock=10
        )
    
    def test_authenticated_user_can_review(self):
        self.client.login(username="reviewer", password="test123")
        response = self.client.post(reverse('product_detail', args=[self.product.id]), {
            'rating': 5,
            'comment': 'Great product!'
        })
        self.assertEqual(Review.objects.count(), 1)
    
    def test_unauthenticated_user_cannot_review(self):
        response = self.client.post(reverse('product_detail', args=[self.product.id]), {
            'rating': 5,
            'comment': 'Great product!'
        })
        self.assertEqual(Review.objects.count(), 0)
