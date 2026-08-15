from django.db import models


class KnowledgeDocument(models.Model):
    """
    Tracks a company-knowledge source file (e.g. company_knowledge.md)
    that has been (or needs to be) processed into embeddings.
    """
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to="knowledge_files/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        status = "processed" if self.processed_at else "pending"
        return f"{self.title} ({status})"

    class Meta:
        ordering = ["-uploaded_at"]