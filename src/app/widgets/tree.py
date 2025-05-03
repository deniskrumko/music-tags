from pathlib import Path
from typing import Iterable

from rich.style import Style
from rich.text import Text
from textual.widgets._directory_tree import (
    DirectoryTree,
    DirEntry,
)
from textual.widgets._tree import (
    TOGGLE_STYLE,
    TreeNode,
)

from music import MusicFile


class MusicDirectoryTree(DirectoryTree):
    """A Tree widget that presents files and directories."""

    def render_label(self, node: TreeNode[DirEntry], base_style: Style, style: Style) -> Text:
        """Render a label for the given node.

        Args:
            node: A tree node.
            base_style: The base style of the widget.
            style: The additional style for the label.

        Returns:
            A Rich Text object containing the label.
        """
        node_label: Text = node._label.copy()
        node_label.stylize(style)
        filename = node_label.plain
        music_file = MusicFile.from_string(filename)

        # If the tree isn't mounted yet we can't use component classes to stylize
        # the label fully, so we return early.
        if not self.is_mounted:
            return node_label

        if node._allow_expand and not music_file.is_logicx:
            prefix = (
                "",
                base_style + TOGGLE_STYLE,
            )
            node_label.stylize_before(
                self.get_component_rich_style("directory-tree--folder", partial=True),
            )
        else:
            prefix = ("", base_style)
            # prefix = (f'{music_file.file_type.emoji}  ', base_style)
            node_label.stylize_before(
                self.get_component_rich_style("directory-tree--file", partial=True),
            )
            node_label.highlight_regex(
                r"\..+$",
                self.get_component_rich_style("directory-tree--extension", partial=True),
            )

        if filename.startswith("."):
            node_label.stylize_before(self.get_component_rich_style("directory-tree--hidden"))

        return Text.assemble(prefix, node_label)

    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        return [path for path in paths if not path.name.startswith(".")]
