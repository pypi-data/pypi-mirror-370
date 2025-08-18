import re
from mkdocs.plugins import BasePlugin

class PlatformContentPlugin(BasePlugin):
    def on_page_markdown(self, markdown, page, config, files):
        # Remove GitHub-only content
        pattern_github = r'<!-- github-only-start -->.*?<!-- github-only-end -->'
        markdown = re.sub(pattern_github, '', markdown, flags=re.DOTALL)

        # Uncomment MkDocs-only content
        pattern_mkdocs = r'<!-- mkdocs-only-start\n(.*?)\nmkdocs-only-end -->'
        markdown = re.sub(pattern_mkdocs, r'\1', markdown, flags=re.DOTALL)

        # Clean up excessive newlines
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)

        return markdown