from django.contrib import admin
from .models import Claim, ClaimDetail, Flag, Note


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient_name', 'billed_amount', 'paid_amount', 'status', 'insurer_name', 'discharge_date']
    list_filter = ['status', 'insurer_name', 'discharge_date']
    search_fields = ['id', 'patient_name', 'insurer_name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-discharge_date']


@admin.register(ClaimDetail)
class ClaimDetailAdmin(admin.ModelAdmin):
    list_display = ['id', 'claim', 'cpt_codes', 'denial_reason']
    list_filter = ['claim__status']
    search_fields = ['claim__id', 'claim__patient_name', 'cpt_codes']
    readonly_fields = ['created_at']


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = ['claim', 'user', 'reason', 'is_resolved', 'created_at']
    list_filter = ['is_resolved', 'created_at']
    search_fields = ['claim__id', 'user__username', 'reason']
    readonly_fields = ['created_at']


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['claim', 'user', 'note_type', 'content_preview', 'created_at']
    list_filter = ['note_type', 'created_at']
    search_fields = ['claim__id', 'user__username', 'content']
    readonly_fields = ['created_at', 'updated_at']

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = "Content Preview"
