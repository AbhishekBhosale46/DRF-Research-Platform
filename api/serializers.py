from rest_framework import serializers
from core.models import Opportunity, Opportunity_Type, Domain, Skill, User_Profile, Application


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


class OpportunityTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity_Type
        fields = ['id', 'name']


class OpportunitySerializer(serializers.ModelSerializer):
    domains = DomainSerializer(many=True)
    skills = SkillSerializer(many=True)
    # opportunity_type_id = serializers.IntegerField(write_only=True)
    created_by = serializers.SerializerMethodField('get_created_by', read_only=True)
    #opportunity_type = serializers.SerializerMethodField('get_opportunity_type', read_only=True)

    class Meta:
        model = Opportunity
        fields = ['id', 'title', 'description', 'start_date', 'end_date', 'duration','created_at', 'created_by','domains', 'skills']
        read_only_fields = ['id', 'created_by', 'duration']

    def get_created_by(self, opportunity_obj):
        return opportunity_obj.owner.name

    # def get_opportunity_type(self, opportunity_obj):
    #     return opportunity_obj.opportunity_type.name

    def create(self, validated_data):
        domains_data = validated_data.pop('domains')
        skills_data = validated_data.pop('skills')
        # opportunity_type_id = validated_data.pop('opportunity_type_id')

        # opportunity_type = Opportunity_Type.objects.get(id=opportunity_type_id)
        opportunity = Opportunity.objects.create(**validated_data)
        # opportunity.opportunity_type = opportunity_type

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
        # opportunity_type_id = validated_data.pop('opportunity_type_id', None)

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

        # if opportunity_type_id is not None:
        #     opportunity_type = Opportunity_Type.objects.get(id=opportunity_type_id)
        #     instance.opportunity_type = opportunity_type
        #     instance.save()

        return instance


class ApplicationSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField('get_status', read_only=True)
    opportunity_title = serializers.SerializerMethodField('get_opportunity_title', read_only=True)
    
    class Meta:
        model = Application
        fields = '__all__'

    def get_status(self, app_obj):
        return app_obj.get_status_display()

    def get_opportunity_title(self, app_obj):
        return app_obj.opportunity.title