import os
import time
from io import BytesIO
from pathlib import Path
from typing import Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from app.schemas.letter import LetterRequest
from app.core import get_logger

logger = get_logger(__name__)

# Singleton font configuration - reused across all PDF generations
_font_config = FontConfiguration()

class PDFGenerator:
    def __init__(self, templates_dir: str = "app/templates", output_dir: str = "output"):
        self.base_dir = Path(os.getcwd())
        self.templates_dir = self.base_dir / templates_dir
        self.output_dir = self.base_dir / output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Jinja2 environment with auto-caching
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            auto_reload=False  # Disable reload checks for production speed
        )

    def generate(self, request: LetterRequest, custom_filename: Optional[str] = None) -> str:
        """
        Generates a PDF based on the letter request.
        Returns the path to the generated PDF.
        """
        start_time = time.time()

        template_name = f"letters/{request.template_type}.html"
        try:
            template = self.env.get_template(template_name)
        except Exception as e:
            raise ValueError(f"Template '{template_name}' not found. Error: {e}")

        # Prepare context
        context = request.model_dump()

        # Flatten content dict to top level for easier access in templates
        # (while keeping 'content' key for backward compatibility)
        if 'content' in context and isinstance(context['content'], dict):
            context.update(context['content'])

        # Render HTML
        html_string = template.render(**context)

        # Determine filename
        if custom_filename:
            filename = custom_filename
            if not filename.endswith(".pdf"):
                filename += ".pdf"
        else:
            filename = f"{request.template_type}_{request.nomor_surat.replace('/', '-')}.pdf"

        output_path = self.output_dir / filename

        # Generate PDF with cached font configuration
        html_doc = HTML(string=html_string, base_url=str(self.templates_dir))
        html_doc.write_pdf(str(output_path), font_config=_font_config)

        # Log timing
        elapsed = time.time() - start_time
        logger.info(f"PDF generated in {elapsed:.2f}s: {filename}")

        return str(output_path)

    def generate_bytes(self, request: LetterRequest) -> BytesIO:
        """
        Generate PDF and return as BytesIO for streaming response.
        Faster for direct downloads without file I/O.
        """
        template_name = f"letters/{request.template_type}.html"
        try:
            template = self.env.get_template(template_name)
        except Exception as e:
            raise ValueError(f"Template '{template_name}' not found. Error: {e}")

        context = request.model_dump()
        html_string = template.render(**context)

        html_doc = HTML(string=html_string, base_url=str(self.templates_dir))
        pdf_bytes = html_doc.write_pdf(font_config=_font_config)

        return BytesIO(pdf_bytes)
