from rest_framework import serializers
from core.models import Opportunity, Domain, Skill, User_Profile, Application, User, Feedback


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name']
        read_only_fields = ['id', 'email', 'name']


class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ['id', 'name']
        read_only_fields = ['id']


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name']
        read_only_fields = ['id']


class OpportunitySerializer(serializers.ModelSerializer):
    domains = DomainSerializer(many=True)
    skills = SkillSerializer(many=True)
    created_by = serializers.SerializerMethodField('get_created_by', read_only=True)
    created_by_id = serializers.SerializerMethodField('get_created_by_id', read_only=True)

    class Meta:
        model = Opportunity
        fields = ['id', 'title', 'description', 'start_date', 'end_date', 'duration','created_at', 'created_by', 'created_by_id','domains', 'skills']
        read_only_fields = ['id', 'created_by', 'created_by_id', 'duration']

    def get_created_by(self, opportunity_obj):
        return opportunity_obj.owner.name

    def get_created_by_id(self, opportunity_obj):
        return opportunity_obj.owner.id

    def create(self, validated_data):
        domains_data = validated_data.pop('domains')
        skills_data = validated_data.pop('skills')
        start_date = validated_data.pop('start_date')
        end_date = validated_data.pop('end_date')

        user = self.context['request'].user
        exisitng_profile = User_Profile.objects.filter(user=user)

        if exisitng_profile:

            if end_date>start_date:
                opportunity = Opportunity.objects.create(**validated_data, start_date=start_date, end_date=end_date)

                for single_domain_data in domains_data:
                    domain = Domain.objects.get_or_create(**single_domain_data)[0]
                    opportunity.domains.add(domain)

                for single_skill_data in skills_data:
                    skill = Skill.objects.get_or_create(**single_skill_data)[0]
                    opportunity.skills.add(skill)

                opportunity.save()
                return opportunity
            else:
                raise serializers.ValidationError({"detail": "End date must be greater than start date"})
        else:
            raise serializers.ValidationError({"detail": "User profile not created"})

    def update(self, instance, validated_data):
        domains_data = validated_data.pop('domains', None)
        skills_data = validated_data.pop('skills', None)
        start_date = validated_data.pop('start_date', None)
        end_date = validated_data.pop('end_date', None)

        if start_date:
            old_end_date = instance.end_date
            if start_date < old_end_date:
                validated_data['start_date'] = start_date
                instance = super().update(instance, validated_data)
            else:
                raise serializers.ValidationError({"detail": "Start date is greater than old end date"})
        elif end_date:
            old_start_date = instance.start_date
            if end_date>old_start_date:
                validated_data['end_date'] = end_date
                instance = super().update(instance, validated_data)
            else:
                raise serializers.ValidationError({"detail": "End date must be greater than old start date"})
        elif start_date and end_date:
            if end_date>start_date:
                validated_data['start_date'] = start_date
                validated_data['end_date'] = end_date
                instance = super().update(instance, validated_data)
            else:
                raise serializers.ValidationError({"detail": "End date must be greater than start date"})
        else:
            instance = super().update(instance, validated_data)

        if domains_data is not None:
            instance.domains.clear()
            for single_domain_data in domains_data:
                domain = Domain.objects.get_or_create(**single_domain_data)[0]
                instance.domains.add(domain)

        if skills_data is not None:
            instance.skills.clear()
            for single_skill_data in skills_data:
                skill = Skill.objects.get_or_create(**single_skill_data)[0]
                instance.skills.add(skill)

        return instance

class ApplicationSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField('get_status', read_only=True)
    opportunity_title = serializers.SerializerMethodField('get_opportunity_title', read_only=True)
    applicant = UserSerializer()

    class Meta:
        model = Application
        fields = '__all__'

    def get_status(self, app_obj):
        return app_obj.get_status_display()

    def get_opportunity_title(self, app_obj):
        return app_obj.opportunity.title


class UserProfileSerializer(serializers.ModelSerializer):
    domains = DomainSerializer(many=True)
    skills = SkillSerializer(many=True)
    # role_type = serializers.SerializerMethodField('get_role_type')
    user_name = serializers.SerializerMethodField('get_user_name')

    class Meta:
        model = User_Profile
        fields = ['id', 'user_name','role','about', 'contact_no', 'contact_email', 'domains', 'skills']
        read_only_fields = ['id', 'user_name']

    def get_role_type(self, obj):
        return obj.get_role_display()

    def get_user_name(self, obj):
        return obj.user.name

    def create(self, validated_data):
        domains_data = validated_data.pop('domains')
        skills_data = validated_data.pop('skills')
        
        user = self.context['request'].user
        exisitng_profile = User_Profile.objects.filter(user=user)  

        if exisitng_profile:
            raise serializers.ValidationError({"detail":"Profile for user already exists"})
        else:
            user_profile = User_Profile.objects.create(**validated_data)

            for single_domain_data in domains_data:
                domain = Domain.objects.get_or_create(**single_domain_data)[0]
                user_profile.domains.add(domain)

            for single_skill_data in skills_data:
                skill = Skill.objects.get_or_create(**single_skill_data)[0]
                user_profile.skills.add(skill)

            user_profile.save()
        
            return user_profile

    def update(self, instance, validated_data):
        domains_data = validated_data.pop('domains', None)
        skills_data = validated_data.pop('skills', None)

        instance = super().update(instance, validated_data)

        if domains_data is not None:
            instance.domains.clear()
            for single_domain_data in domains_data:
                domain = Domain.objects.get_or_create(**single_domain_data)[0]
                instance.domains.add(domain)

        if skills_data is not None:
            instance.skills.clear()
            for single_skill_data in skills_data:
                skill = Skill.objects.get_or_create(**single_skill_data)[0]
                instance.skills.add(skill)

        return instance


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'