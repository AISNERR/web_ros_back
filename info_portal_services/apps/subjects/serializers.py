from rest_framework.serializers import ModelSerializer

from .models import Subjects


class SubjectsSerializer(ModelSerializer):
    
    class Meta:
        model = Subjects
        fields = [
            'id',
            'title'
        ]
