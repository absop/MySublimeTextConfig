import re

import sublime
import sublime_plugin


# def merge_selections(sel):
#     new_selections = []
#     selection_regions = []
#     for selection in sel:
#         selection = selection.cover(view.line(selection.end()))
#         if selection_regions:
#             last = selection_regions[-1]
#             if last.contains(selection):
#                 continue
#             if last.intersects(selection):
#                 selection_regions[-1] = last.cover(selection)
#         else:
#             new_selections.append(selection)
#             selection_regions.append(sel)


def join_lines(edit, view):
    new_selections = []
    replacements = []
    num_removed_chars = 0
    for selection in view.sel():
        if replacements and replacements[-1][0].contains(selection):
            pattern = r'\n[ \t]*'
            new_selections.pop()
        else:
            pattern = r'[ \t]*\n[ \t]*'
        curr_line = view.line(selection.end())
        next_line_indent = view.find(pattern, curr_line.begin())
        space = ' '
        if view.substr(next_line_indent.end()) == '\n':
            space = ''

        if selection.empty():
            cursor_point = next_line_indent.a - num_removed_chars
            if space:
                cursor_point += 1
            new_selections.append(cursor_point)
        else:
            spaces = view.find(r'[ \t]*', selection.end())
            selection = selection.cover(spaces)
            original = view.substr(selection)
            one_line = re.sub(r'\s*\n\s*', ' ', original)
            a = selection.a - num_removed_chars
            if one_line != original:
                replacements.append((selection, one_line))
                num_removed_chars += len(original) - len(one_line)
            b = selection.b - num_removed_chars - original[-1].isspace()
            new_selections.append(sublime.Region(a, b))

        replacements.append((next_line_indent, space))
        num_removed_chars += next_line_indent.size() - len(space)

    for region, content in reversed(replacements):
        view.replace(edit, region, content)

    view.sel().clear()
    view.sel().add_all(new_selections)


class ReJoinLinesCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        join_lines(edit, self.view)
