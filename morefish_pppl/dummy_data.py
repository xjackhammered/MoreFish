import os
import django

script_dir = os.path.dirname(__file__)
try:
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "morefish_pppl.settings"
    )
    django.setup() 
    from store.product.models import Product,ProductImage,ProductSpecifications
    from django.core.files import File
    from django.core.files.temp import NamedTemporaryFile
except ImportError as e:
    exit(1)
    
import random
from faker import Faker


fake = Faker()

# Generate dummy data for Product model
def generate_product_data():
    name = fake.word()
    description = fake.sentence()
    price = random.randint(10, 1000)
    return {
        'name': name,
        'description': description,
        'price': price
    }

# Generate dummy data for ProductImage model
def generate_product_image_data(product):
    image_path = os.path.join(script_dir, 'dummy_image.webp')
    product_image = ProductImage.objects.create(product=product, is_default=False)
    with open(image_path, 'rb') as img_file:
        product_image.image.save("dummy_image.webp", File(img_file), save=True)
        
# Generate dummy data for ProductSpecifications model
def generate_product_specifications_data(product):
    specification = fake.sentence()
    ProductSpecifications.objects.create(product=product, specification=specification)

# Generate dummy data for Products
def generate_products(num_products=10):
    for _ in range(num_products):
        product_data = generate_product_data()
        product = Product.objects.create(**product_data)
        generate_product_image_data(product)
        generate_product_specifications_data(product)

# Call the function to generate dummy data
generate_products()
