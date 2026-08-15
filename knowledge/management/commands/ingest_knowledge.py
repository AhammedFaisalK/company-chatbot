from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings

from knowledge.models import KnowledgeDocument
from knowledge.services.ingest import run_full_ingestion


class Command(BaseCommand):
    help = "Re-processes company_knowledge.md: chunk, embed, and rebuild the FAISS index."

    def handle(self, *args, **options):
        self.stdout.write("Starting knowledge base ingestion...")

        try:
            chunk_count = run_full_ingestion()
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ingestion failed: {e}"))
            return

        # Track this as a KnowledgeDocument record, creating one if
        # it doesn't exist yet, so its processed_at timestamp reflects reality.
        file_path = settings.KNOWLEDGE_BASE_DIR / "company_knowledge.md"
        doc, created = KnowledgeDocument.objects.get_or_create(
            title="company_knowledge.md",
            defaults={"file": "knowledge_files/company_knowledge.md"},
        )
        doc.processed_at = timezone.now()
        doc.save()

        status = "created" if created else "updated"
        self.stdout.write(
            self.style.SUCCESS(
                f"Ingestion complete: {chunk_count} chunks indexed. "
                f"KnowledgeDocument record {status}, processed_at={doc.processed_at}."
            )
        )