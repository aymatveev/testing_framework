from typing import Iterable, Pattern, TextIO, Tuple
import pathlib
import re
import ast
import copy
import io
import sys
from contextlib import redirect_stdout
import time
import traceback
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import report
import ui

def get_test_files(src_dir_name: str) -> Iterable[pathlib.Path]:
    src_dir: pathlib.Path = pathlib.Path(src_dir_name)
    test_file_template: Pattern = re.compile(r".*_test\.py$", re.IGNORECASE)
    return (f for f in src_dir.iterdir() if test_file_template.match(f.name))

def append_call_to_ast_body(root: ast.AST, expr: ast.Expr) -> ast.AST:
    root.body.append(expr)
    ast.fix_missing_locations(root)
    return root

def exec_with_output_redirection(code) -> str:
    f = io.StringIO()
    with redirect_stdout(f):
        exec(code, globals())
    return f.getvalue()

def execute_test_functions(test_file_path: pathlib.Path) -> Iterable[Tuple[str, str]]:
    test_file: TextIO = open(test_file_path.absolute(), "r")
    test_file_content: str = test_file.read()
    test_file.close()
    parsed_ast: ast.AST = ast.parse(test_file_content)
    func_definitions: Iterable[ast.FunctionDef] = (node for node in parsed_ast.body if type(node) is ast.FunctionDef)
    test_func_name_template: Pattern = re.compile("test_.*", re.IGNORECASE)
    test_funcs_names: Iterable[str] = tuple(fdef.name for fdef in func_definitions if test_func_name_template.match(fdef.name))
    test_funcs_calls: Iterable[ast.Expr] = (ast.Expr(value=ast.Call(func=ast.Name(id=fn, ctx=ast.Load()), args=[], keywords=[])) for fn in test_funcs_names)
    test_funcs_calls_ast: Iterable[ast.AST] = (append_call_to_ast_body(copy.deepcopy(parsed_ast), tfc) for tfc in test_funcs_calls)
    test_funcs_calls_ast_code: Iterable = (compile(ast, test_file.name, "exec") for ast in test_funcs_calls_ast)
    test_funcs_results: Iterable[str] = (exec_with_output_redirection(code) for code in test_funcs_calls_ast_code)
    test_funcs_results_with_function_names: Iterable[Tuple[str, str]] = zip(test_funcs_names, test_funcs_results)
    return test_funcs_results_with_function_names

def flatten_results(results: Iterable[Tuple[str, str]]) -> Iterable[str]:
    for r in results:
        yield r[0]
        for r_ in r[1].split('\n'):
            yield r_

def build_reports(reporter, ui):
    test_files: Iterable[pathlib.Path] = get_test_files(".")

    for tf in test_files:
        results: Iterable[Tuple[str, str]] = execute_test_functions(tf)
        results_flat: Iterable[str] = flatten_results(results)
        r = reporter.report(results_flat)
        ui.generate_ui(r, pathlib.Path(f"../reports/{tf.name}.html"))
    
    print("Reporting: done")

def start_internal(reporter, ui):
    build_reports(reporter, ui)

    event_handler = MyHandler(reporter, ui)
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

def start():
    start_internal(report, ui)

class MyHandler(FileSystemEventHandler):
    def __init__(self, reporter, ui):
        self.reporter = reporter
        self.ui = ui

    def on_modified(self, event):
        print(f'event type: {event.event_type}  path : {event.src_path}')
        try:
            build_reports(self.reporter, self.ui)
        except Exception as e:
            print(e)
            traceback.print_exc(file=sys.stdout)