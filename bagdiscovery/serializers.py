from rest_framework import serializers
from .models import Accession, Bag


class AccessionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Accession
        fields = ('url', 'archivesspace_identifier', 'data', 'created', 'last_modified')


class AccessionListSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Accession
        fields = ('url', 'archivesspace_identifier', 'created', 'last_modified')


class BagSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Bag
        fields = ('url', 'bag_identifier', 'archivesspace_identifier', 'archivesspace_parent_identifier', 'accession', 'data', 'created', 'last_modified')


class BagListSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Bag
        fields = ('url', 'bag_identifier', 'archivesspace_identifier', 'archivesspace_parent_identifier', 'accession', 'created', 'last_modified')
