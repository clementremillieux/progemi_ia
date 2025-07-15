"""All path related functions for proposal object."""


class ProposalObjectPaths:
    """Class to manage paths for proposal object files."""

    def __init__(self, file_name: str):
        """Initialize paths for proposal object files."""

        self.proposal_path = f"data/proposal_pdf/{file_name}.pdf"

        self.proposal_ocr_json_path = f"data/proposal_ocr_json/{file_name}.json"

        self.proposal_ocr_content_path = f"data/proposal_ocr_content/{file_name}.txt"

        self.proposal_json_path = f"data/proposal_json/{file_name}.json"

        self.proposal_text_path = f"data/proposal_text/{file_name}.txt"

        self.proposal_pdf_object_path = f"data/proposal_pdf_object/{file_name}.pdf"

        self.proposal_html_path = f"data/proposal_html/{file_name}.html"

        self.proposal_markdown_path = f"data/proposal_markdown/{file_name}.md"

        self.proposal_section_analysis_path = (
            f"data/proposal_section_analysis/{file_name}.json"
        )

        self.proposal_validation_path = f"data/proposal_validation/{file_name}.txt"

        self.proposal_object_known_path = f"data/proposal_object_know/{file_name}.json"

        self.proposal_object_line_path = f"data/proposal_object_line/{file_name}.txt"

        self.proposal_object_predicted_path = (
            f"data/proposal_object_predicted/{file_name}_predicted.json"
        )

        self.proposal_eval_path = f"data/proposal_eval/{file_name}.txt"
