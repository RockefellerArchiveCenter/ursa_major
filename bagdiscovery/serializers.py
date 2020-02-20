from rest_framework import serializers

from .models import Accession, Bag


class AccessionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Accession
        fields = ('url', 'data', 'created', 'last_modified')


class AccessionListSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Accession
        fields = ('url', 'created', 'last_modified')


class BagSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Bag
        fields = ('url', 'bag_identifier', 'bag_path', 'accession', 'data', 'created', 'last_modified')


class BagListSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Bag
        fields = ('url', 'bag_identifier', 'accession', 'created', 'last_modified')
