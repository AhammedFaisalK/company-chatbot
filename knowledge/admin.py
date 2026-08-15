from django.contrib import admin
from django.core.management import call_command
from .models import KnowledgeDocument


@admin.register(KnowledgeDocument)
class KnowledgeDocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "uploaded_at", "processed_at")
    actions = ["reprocess_knowledge_base"]

    @admin.action(description="Re-process knowledge base (rebuild embeddings)")
    def reprocess_knowledge_base(self, request, queryset):
        try:
            call_command("ingest_knowledge")
            self.message_user(request, "Knowledge base re-processed successfully.")
        except Exception as e:
            self.message_user(request, f"Re-processing failed: {e}", level="error")