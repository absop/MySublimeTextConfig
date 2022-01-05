import sublime
import sublime_plugin


class AddLineFeedsCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        if not (self.view.sel() and self.view.sel()[0]):
            return
        lines = self.view.lines(self.view.sel()[0])
        maxlen = max([len(line) for line in lines])
        maxlen = maxlen + (4 - maxlen % 4)

        lines.reverse()
        for line in lines:
            content = self.view.substr(line)
            space = ' ' * (maxlen - len(line))
            text = content + space + "\\"
            self.view.replace(edit, line, text)
