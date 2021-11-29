import sublime
import sublime_plugin
import subprocess
import threading
import os
import time
from .lib import Loger


def cache_path():
    cache = sublime.cache_path()
    this_cache = os.path.join(cache, __package__)
    os.makedirs(this_cache, exist_ok=True)
    return this_cache

def get_sample_output(test_cmd, sample_input_fd, shell):
    p = subprocess.Popen(test_cmd,
        shell=shell, stdin=sample_input_fd, stdout=subprocess.PIPE)
    p.wait()
    try:
        obytes = p.stdout.read()
        output = str(obytes, encoding='utf-8')
        return output
    except Exception as e:
        raise e


def run_sample_test(index, test_cmd, shell):
    dirname = '{}/patest/AdvancedLevel'.format(os.path.dirname(__file__))
    idir = "{}/{}/Sample Input".format(dirname, index)
    odir = "{}/{}/Sample Output".format(dirname, index)

    samples = sorted(os.listdir(idir))
    for sample in samples:
        sample_i = os.path.join(idir, sample)
        sample_o = os.path.join(odir, sample)

        with open(sample_i, 'r', encoding='utf-8') as sifd:
            output = get_sample_output(test_cmd, sifd, shell)

        with open(sample_o, 'r', encoding='utf-8') as sofd:
            result = sofd.read()

        output = output.strip('\r\n').replace('\r', '')

        if output != result:
            if len(samples) == 1:
                index = ''
            else:
                index = ' ' + os.path.splitext(sample)[0]
            message = (
                "Test Failed in Sample Input%s.\n"
                "*************Output************\n"
                "%s\n"
                "*************Result************\n"
                "%s\n" % (index, output, result))
            print(message)
            Loger.message_dialog(message)
            return

    Loger.message_dialog(
        "*****************All Test Right*****************\n"
        "Please go to the patest.cn site to do more tests.")


class PatBuildTestCommand(sublime_plugin.WindowCommand):
    def extract_variables(self, cmd, shell, variables):
        cmd = sublime.expand_variables(cmd, variables)
        if shell and type(cmd) is list:
            cmd = ' '.join(cmd)
        return cmd

    def run(self, compile_cmd=None, test_cmd=None, shell=True, kill=False):
        assert test_cmd is not None

        file = self.window.active_view().file_name()
        if not os.path.exists(file):
            sublime.message_dialog('File does not exist.')
            return

        variables = self.window.extract_variables()
        variables.update({"cache_path": cache_path()})

        def compile_code():
            nonlocal compile_cmd
            compile_cmd = self.extract_variables(
                compile_cmd, shell, variables)
            p = subprocess.Popen(compile_cmd, shell=shell)
            p.wait()
            # returncode = p.returncode
            # error = p.stderr.read()
            # if error:
            #     pass

        def run_pat_test():
            nonlocal test_cmd
            branch, leaf = os.path.split(file)
            index, ext = os.path.splitext(leaf)
            index = index[:4]
            test_cmd = self.extract_variables(test_cmd, shell, variables)
            run_sample_test(index, test_cmd, shell)

        def threading_run_pat_test():
            if compile_cmd:
                thread = Loger.Thread(compile_code,
                    "Compiling code",
                    "Successfully compiled code")
                thread.start()
                thread.join()
                time.sleep(2.0)

            Loger.threading(run_pat_test,
                "Running sample tests",
                "Successfully ran sample tests")

        thread = threading.Thread(target=threading_run_pat_test)
        thread.start()


class PatUpdateReadmeCommand(sublime_plugin.WindowCommand):
    pass


class PatOpenGitTerminalCommand(sublime_plugin.WindowCommand):
    pass


class PatShowCurrentProblemCommand(sublime_plugin.TextCommand):
    problem_dir = 'patest/AdvancedLevel/{index}/Problem'

    def run(self, edit):
        file_name = self.view.file_name()
        index = os.path.basename(file_name)[:4]
        package_dir = os.path.join(sublime.packages_path(), __package__)
        problem_dir = os.path.join(package_dir, self.problem_dir)
        problem_dir = problem_dir.format(index=index)
        problem_list = os.listdir(problem_dir)
        problem_path = os.path.join(problem_dir, problem_list[0])

        window = sublime.active_window()
        view = window.open_file(problem_path, sublime.ENCODED_POSITION)
        # problem = open(problem_path, encoding='utf-8').read()

        # view = sublime.active_window().new_file()
        # view.set_name("%s.md" % index)
        # view.assign_syntax("Markdown.sublime-syntax")
        # view.settings().set("font_face", "Lucida Console")
        # view.settings().set("word_wrap", True)
        # view.run_command("append", {"characters": problem})
        # view.set_scratch(True)
        view.set_read_only(True)



class FormatToMarkdownCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        sample = "Sample (Input|Output)( \\d)?"
        specification = "(Input|Output) Specification"
        english = "((%s)|(%s)):" % (sample, specification)
        chinese = "((输入|输出)(格式|样例( \\d)?))："
        pattern = "^((%s)|(%s))$\n" % (chinese, english)
        secondary = view.find_all(pattern)
        end_char = sublime.Region(view.size() - 1, view.size())
        if view.substr(end_char) != "\n":
            view.insert(edit, view.size(), "\n")

        secondary.reverse()
        view.insert(edit, view.size(), "```\n")
        for r in secondary[:-3]:
            view.insert(edit, r.end(), "```\n")
            view.insert(edit, r.begin(), "```\n\n## ")

        view.insert(edit, secondary[-3].end(), "```\n")
        view.insert(edit, secondary[-3].begin(), "## ")
        view.insert(edit, secondary[-2].begin(), "## ")
        view.insert(edit, secondary[-1].begin(), "## ")
        view.insert(edit, view.line(0).end(), "\n")
        view.insert(edit, 0, "# ")
