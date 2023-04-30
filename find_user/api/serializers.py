from rest_framework import serializers
from auction.models import Auction
from auction.models import Category, Rating, Transaction


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['title',]


class RatingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rating
        fields = ['star']


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = ['count']


class AuctionSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name')
    company_id = serializers.CharField(source='company.id')
    categories = CategorySerializer(many=True, read_only=True)
    ratings = RatingsSerializer(read_only=True, many=True)
    transaction = TransactionSerializer()
    status = serializers.CharField(source='status.id')

    class Meta:
        model = Auction
        fields = ['id', 'product',
                  'company_name', 'company_id',
                  'categories', 'ratings', 'transaction', 'status']
