# assigning env variables from django project
import sys
import os

#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Setting up django configurations
import django

django.setup()

# python libraries for creating fake data
import random
from faker import Faker

# django app models for which data has to be populated
from django_shop.models import Product, ProductDetail, Key

# Initializing fake generator
fakegen = Faker()


def create_entities(N=50):

    products = Product.objects.all()
    # creating N entries
    for product in products:
        for i in range(N):
            f_key = fakegen.bothify(text='????-####-????-####')
            # creating data object and saving to DB
            key = Key.objects.create(
                key=f_key,
                product=product
            )
            key.save()
        f_price = fakegen.random_int(min=10, max=200)
        ProductDetail.objects.create(product=product,price=f_price)

    # finished
    print("Finished...{} entries populated.".format(N))


if __name__ == "__main__":

    # Verify the number of command line arguments
    print("Initializing... checking syntax...")

    try:
        if len(sys.argv) == 2:
            N = int(sys.argv[1])
            print("Found parameter N = {}".format(N))
            # calling method for data population
            create_entities(N)
        else:
            print("No additional parameter provided, populating default no. of entries.")
            create_entities()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print("Exception occurred at line : {}! {}".format(exc_tb.tb_lineno, e))
        sys.exit(1)