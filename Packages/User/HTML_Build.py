import webbrowser
import sublime_plugin


class HtmlViewerCommand(sublime_plugin.WindowCommand):
    def run(self):
        view = self.window.active_view()
        if view.file_name():
            webbrowser.open_new_tab(view.file_name())
        else:
            self.window.status_message("Unsaved File!")
