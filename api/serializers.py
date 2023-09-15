from rest_framework import serializers
from core.models import Opportunity, Domain, Skill, User_Profile, Application, User


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

    class Meta:
        model = Opportunity
        fields = ['id', 'title', 'description', 'start_date', 'end_date', 'duration','created_at', 'created_by','domains', 'skills']
        read_only_fields = ['id', 'created_by', 'duration']

    def get_created_by(self, opportunity_obj):
        return opportunity_obj.owner.name

    def create(self, validated_data):
        domains_data = validated_data.pop('domains')
        skills_data = validated_data.pop('skills')

        opportunity = Opportunity.objects.create(**validated_data)

        for single_domain_data in domains_data:
            domain = Domain.objects.get_or_create(**single_domain_data)[0]
            opportunity.domains.add(domain)

        for single_skill_data in skills_data:
            skill = Skill.objects.get_or_create(**single_skill_data)[0]
            opportunity.skills.add(skill)

        opportunity.save()
    
        return opportunity

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