from rest_framework import serializers
from home.models import User,AuditLog


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, write_only=True)  
    phone = serializers.CharField(max_length=15, required=False, allow_null=True, allow_blank=True)
    limit = serializers.CharField(required=False, allow_null=True)  
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'password', 'email', 'role', 'phone', 'limit','date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def validate(self, data):
        role = data.get('role', getattr(self.instance, 'role', 'guest'))
        limit = data.get('limit', getattr(self.instance, 'limit', None))

        if role == 'guest' and limit is None:
            raise serializers.ValidationError(
                {"limit": "Limit is required for guest users"}
            )

        if role != 'guest' and limit is not None:
            raise serializers.ValidationError(
                {"limit": "Limit is only allowed for guest users"}
            )
        return data

    def to_internal_value(self, data):
        data = data.copy()
        limit = data.get('limit')
        if limit in [None, '']:
            data['limit'] = None
        else:
            try:
                data['limit'] = int(limit)
            except (TypeError, ValueError):
                raise serializers.ValidationError(
                    {"limit": "Must be an integer"}
                )
        return super().to_internal_value(data)
    

    def create(self, validated_data):
        password = validated_data.pop('password')
        role = validated_data.get('role','guest')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=role,
            limit=validated_data.get('limit') if role=='guest' else None,
            password=password
        )
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)  
        new_role = validated_data.get('role', instance.role)
        
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.username = validated_data.get('username', instance.username)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.role = new_role
        
        if new_role == 'guest':
            instance.limit = validated_data.get('limit', instance.limit)
        else:
            instance.limit = None
        
        instance.save()
        
        if password:
            instance.set_password(password)
            instance.save()
        
        return instance
    
class AuditLogSerializer(serializers.ModelSerializer):
    actor=UserSerializer(read_only=True)
    target_user=UserSerializer(read_only=True)
    class Meta:
        model=AuditLog
        fields='__all__'
    
from .models import UsageLog

class UsageLogSerializer(serializers.ModelSerializer):
    # Optional: include nested user info if needed
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = UsageLog
        fields = [
            'id',
            'user',              # stores user ID
            'username',          # optional, read-only
            'email',             # optional, read-only
            'file_hash',
            'algorithm_name',
            'confidence_score',
            'usage_timestamp',
            'blockchain_hash',
            'transaction_hash',
        ]
        read_only_fields = ['usage_timestamp', 'blockchain_hash', 'transaction_hash']

