from notionary.blocks.models import Block
from notionary.blocks.registry.block_registry import BlockRegistry
from notionary.page.reader.handler import (
    BlockRenderingContext,
    ColumnListRenderer,
    ColumnRenderer,
    LineRenderer,
    ToggleableHeadingRenderer,
    ToggleRenderer,
)
from notionary.util import LoggingMixin


class PageContentRetriever(LoggingMixin):
    """Retrieves Notion page content and converts it to Markdown using chain of responsibility."""

    def __init__(
        self,
        block_registry: BlockRegistry,
    ):
        self._block_registry = block_registry

        self._setup_handler_chain()

    async def convert_to_markdown(self, blocks: list[Block]) -> str:
        """
        Retrieve page content and convert it to Markdown.
        Uses the chain of responsibility pattern for scalable block processing.
        """
        return self._convert_blocks_to_markdown(blocks, indent_level=0)

    def _setup_handler_chain(self) -> None:
        """Setup the chain of handlers in priority order."""
        toggle_handler = ToggleRenderer()
        toggleable_heading_handler = ToggleableHeadingRenderer()
        column_list_handler = ColumnListRenderer()
        column_handler = ColumnRenderer()
        regular_handler = LineRenderer()

        # Chain handlers - most specific first
        toggle_handler.set_next(toggleable_heading_handler).set_next(
            column_list_handler
        ).set_next(column_handler).set_next(regular_handler)

        self._handler_chain = toggle_handler

    def _convert_blocks_to_markdown(
        self, blocks: list[Block], indent_level: int = 0
    ) -> str:
        """Convert blocks to Markdown using the handler chain."""
        if not blocks:
            return ""

        markdown_parts = []

        for block in blocks:
            context = BlockRenderingContext(
                block=block,
                indent_level=indent_level,
                block_registry=self._block_registry,
            )

            self._handler_chain.handle(context)

            if context.was_processed and context.markdown_result:
                markdown_parts.append(context.markdown_result)

        separator = "\n\n" if indent_level == 0 else "\n"
        return separator.join(markdown_parts)
