#!/usr/bin/env python3

"""Main file

Author: Dmytro Tarasiuk
URL: https://github.com/RoyBebru/addressbook
Email: RoyBebru@gmail.com
License: MIT
"""


import atexit
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
from pathlib import Path
import re
import subprocess
import sys
import types
from typing import Any
from urllib.parse import urlparse, parse_qs, unquote_plus
import webbrowser


from notabene.addressbook import AddressBook, AddressBookException
from notabene.birthday import BirthdayException
from notabene.phone import Phone, PhoneException
from notabene.record import Record, RecordException


"""CONSTANTS"""
ADDRESSBOOK_PATHFILE = Path.home() / ".notabene.abo"
HISTFILE = Path.home() / ".notabene.history"

HTTPD_PORT = 8888

def command_error_catcher(cmd_hundler):
    def decor(cmd_args, box):
        try:
            return cmd_hundler(cmd_args, box)
        except AddressBookException as e:
            return f"AddressBook Error: {e.args[0]}"
        except RecordException as e:
            return f"Record Error: {e.args[0]}"
        except PhoneException as e:
            return f"Phone Error: {e.args[0]}"
        except BirthdayException as e:
            return f"Birthday Error: {e.args[0]}"
    return decor


# @command_error_catcher
def cmd_help(*__):
    return ("Application uses MATCH-SET and MATCH-SUBSET. Command 'show' "
        + "produces MATCH-SET"
        + os.linesep + "Command 'search' produces MATCH-SUBSET from MATCH-SET."
        + "Commands 'add', 'change',"
        + os.linesep + "and 'delete' work with MATCH-SET. Commands have synonyms and "
        + "short forms including"
        + os.linesep + "ukrainian."
        + os.linesep + "Matches all records in address book: > all"
        + os.linesep + "Matches records with the relevant phone number: "
        + "> show 111-22-33"
        + os.linesep + "Matches records with the relevant person name: "
        + "> show Кас'ян Дем'янович Непийпиво-В'юнець"
        + os.linesep + "Show matching records: > show"
        + os.linesep + "Search in matching records by template with "
        + "metasymbols '*'/'?': > search #2"
        + os.linesep + "Delete searched record(s) or field: "
        + "> delete [<field_name>[<num>]]"
        + os.linesep + "Change name field in searched record: "
        + "> change name Лабуда Зоряна Акакіївна"
        + os.linesep + "Change 1st phone field in searched record: "
        + "> change phone +38 (033) 222-11-33"
        + os.linesep + "Change 2nd phone field in searched record: "
        + "> change phone2 333-33-333"
        + os.linesep + "Add new record. This record will be serched: "
        + "> add Голілиць Рада Варфоломіївна"
        + os.linesep + "Add new field to the last searched record: "
        + "> add phone +48 551-051-555"
    )


@command_error_catcher
def cmd_add(cmd_args: str, box):
    if cmd_args == "":
        return "Argument required, use help for more information"
    args = cmd_args.split(' ')
    title = args[0].capitalize()
    for field_title in Record.known_field_titles.keys():
        if title == field_title:
            args.pop(0)
            for name in box.ab_fit_to_fit:
                # Add new field
                box.ab[name].add( ((title, ' '.join(args)),) )
            break
    else:
        if title == "Name":
            args.pop(0) # omit option title "Name"
        # Create new record
        name = ' '.join(args)
        if box.ab.is_any_equal_by_combination(name):
            return f"Error: name '{' '.join(args)}' already exists"
        box.ab[name] = ()
        box.ab_fit += (name,)
        box.ab_fit_to_fit = (name,)
    box.ab.is_modified = True
    return None


# @command_error_catcher
def cmd_all(cmd_args: str, box):
    box.ab_fit = tuple(box.ab.keys())
    box.ab_fit_to_fit = box.ab_fit
    return None

@command_error_catcher
def cmd_change(cmd_args: str, box):
    args = cmd_args.split(' ') # [''] == ''.split(' ')
    title = args[0].capitalize()

    # Looking field index
    for ix in range(len(title)-1,-1,-1):
        if not title[ix].isdigit():
            if ix == len(title)-1:
                # No suffix number
                field_no = 1
            else:
                # File_no 0 is the same as 1
                field_no = int(title[ix+1:]) or 1
                title = title[:ix+1]
            break
    else:
        field_no = 1 # index is absent

    for field_title in Record.known_field_titles.keys():
        if title == field_title:
            # Field title is present: change field value
            args.pop(0)
            value = " ".join(args)
            for name in box.ab_fit_to_fit:
                box.ab[name].change(title, value, field_no)
            break # field is found and changed
    else:
        if title == "Name":
            args.pop(0)
        value = " ".join(args)
        if value != "":
            if len(box.ab_fit_to_fit) != 1:
                return "Change error: select only one record to rename"
            key = box.ab_fit_to_fit[0]
            value = box.ab.rename(key, value)
            # Delete old name from MATCH list
            box.ab_fit = tuple(filter(lambda e: e != key, box.ab_fit))
            # Add new name
            box.ab_fit += (value,)
            box.ab_fit_to_fit = (value,)
        else:
            return "Change error: name is required"
    box.ab.is_modified = True
    return


@command_error_catcher
def cmd_delete(cmd_args: str, box):
    args = cmd_args.split(' ') # [''] == ''.split(' ')
    title = args[0].capitalize()

    # Looking field index
    for ix in range(len(title)-1,-1,-1):
        if not title[ix].isdigit():
            if ix == len(title)-1:
                # No suffix number
                field_no = 1
            else:
                # File_no 0 is the same as 1
                field_no = int(title[ix+1:]) or 1
                title = title[:ix+1]
            break
    else:
        field_no = 1 # index is absent

    for field_title in Record.known_field_titles.keys():
        if title == field_title:
            # Field title is present: delete this field within record(s)
            args.pop(0)
            value = " ".join(args)
            for name in box.ab_fit_to_fit:
                box.ab[name].delete(title, value, field_no)
            break # field is found and deleted
    else:
        if title == "Name" or title == "":
            args.pop(0) # omit option title "Name"

        if len(args) == 0:
            # Delete all record(s) in ab_fit
            for name in box.ab_fit_to_fit:
                box.ab.pop(name, None)
            box.ab_fit = tuple(name for name in box.ab_fit
                            if name not in box.ab_fit_to_fit)
        else:
            value = " ".join(args)
            # Delete record(s) with Name similar to value
            box.ab_fit = tuple(name for name in box.ab_fit
                    if name not in box.ab_fit_to_fit or not AddressBook.is_similar(name, value))
            for name in box.ab_fit_to_fit:
                if AddressBook.is_similar(name, value):
                    box.ab.pop(name)
        box.ab_fit_to_fit = box.ab_fit
    box.ab.is_modified = True
    return


@command_error_catcher
def cmd_exit(*args):
    # dump_addressbook(args[1])
    return None


def report_fit_to_fit(box):
    report = ""
    report_lines = 0
    report_in_the_page_middle = False
    for name in box.ab_fit_to_fit:
        report_plus = box.ab.report(name, index=list(box.ab_fit).index(name)+1)
        report_plus_lines = report_plus.count(os.linesep) + 1
        # Empty line between records output
        report_plus_lines += int(report_in_the_page_middle)

        # Amount of terminal lines can be changed between iterations
        terminal_lines = os.get_terminal_size().lines - 2
        if not report_in_the_page_middle \
                or report_lines + report_plus_lines <= terminal_lines:
            # Add empty line between records output
            report_plus = os.linesep * (int(report_in_the_page_middle) * 2) \
                + report_plus
            report += report_plus
            report_lines += report_plus_lines
            report_in_the_page_middle = True
            continue

        yield report
        report = report_plus
        report_lines = report_plus_lines - int(report_in_the_page_middle) * 2
        report_in_the_page_middle = True

    if report_lines > 0:
        yield report

    return


@command_error_catcher
def cmd_search(cmd_args: str, box):
    box.ab_fit_to_fit = tuple(name for name in box.ab.iter_by_sample(
            cmd_args, names=box.ab_fit))
    return report_fit_to_fit(box)


@command_error_catcher
def cmd_show(cmd_args: str, box):
    if cmd_args == "":
        return report_fit_to_fit(box)
    try:
        box.ab_fit = ()
        ph = Phone(cmd_args)
        for name in box.ab.keys():
            for field in box.ab[name].fields:
                if isinstance(field, Phone) and field.is_similar(ph):
                    box.ab_fit += (name,)
                    break
    except PhoneException:
        # cmd_args is not Phone
        box.ab_fit = box.ab.get_similar(cmd_args)
    box.ab_fit_to_fit = box.ab_fit
    return box.ab.report(box.ab_fit)


def cmd_sort_files(*args):
    subprocess.run("fig")


def cmd_unknown(*args):
    return "Unknown command: use help command for more information"


def normalize(cmd: str) -> str:
    # Change many spaces with one and remove prefix/suffix space(s)
    return " ".join(cmd.split())


def parse(norm_cmd: str) -> tuple:
    i = norm_cmd.find(' ')
    if i == -1:
        return (norm_cmd, '')
    return (norm_cmd[:i], norm_cmd[i+1:])


HANDLERS = {
    cmd_add: re.compile(r"^(?:ad|add|"
                        r"дод|дода|додай|додат|додати)$",
                        re.IGNORECASE),
    cmd_all: re.compile(r"^(?:"+r"al|all|"
                        r"в|вс|вс[іе])$",
                        re.IGNORECASE),
    cmd_change: re.compile(r"^(?:c|ch|cha|chan|chang|change|"
                           r"зм|змі|змін|зміна|зміни|змінит|змінити)$",
                           re.IGNORECASE),
    cmd_delete: re.compile(r"^(?:d|de|del|dele|delet|delete|"
                           r"вид|вида|видал|видали|видалит|видалити)$",
                           re.IGNORECASE),
    cmd_exit: re.compile(r"^(?:\.|e|ex|exi|exit|"
                         r"q|qu|qui|quit|"
                         r"b|by|bye|"
                         r"вий|вий[тд]|вий[дт]и|вих|вихі|вихід)$",
                         re.IGNORECASE),
    cmd_sort_files: re.compile(r"^(?:\.|f|fi|fil|file.*|"
                               r"so|sor|sort*|"
                               r"ф|фа|фай|файл.*|"
                               r"к|ка|кат|ката|катало|каталог|"
                               r"с|со|сор|сорт|сорту|сорту*)$",
                         re.IGNORECASE),
    cmd_help: re.compile(r"^(?:\?|h|he|hel|help|"
                         r"доп|допо|допом|допомо|допомож|допоможи|допомог|допомога)$",
                         re.IGNORECASE),
    cmd_search: re.compile(r"^(?:se|se[ea]|sear|searc|search|"
                           r"зн|зна|знай|знай[тд]|знай[тд]и|"
                           r"пош|пошу|пошук|"
                           r"ш|шу|шук|шука|шукай|шукат|шукати)$",
                           re.IGNORECASE),
    cmd_show: re.compile(r"^(?:sh|sho|show|"
                         r"пок|пока|пока[зж]|покажи|показа|показат|показати|"
                         r"ди|див|диви|дивис|дивис[яь]|дивит|дивити|дивитис|дивитис[яь])$",
                         re.IGNORECASE),
}


def get_handler(cmd: str):
    for (func, regex) in HANDLERS.items():
        if regex.search(cmd):
            return func
    return cmd_unknown


def dump_addressbook(box):
    if not box.ab.is_modified:
        return
    try:
        with open(ADDRESSBOOK_PATHFILE, "w") as fh:
            fh.write(json.dumps(box.ab.JSON_helper(),
                                indent=2,
                                ensure_ascii=False))
    except PermissionError:
        return
    box.ab.is_modified = False
    return


def load_addressbook():
    try:
        with open(ADDRESSBOOK_PATHFILE, "r") as fh:
            ab = json.loads(fh.read())
    except (FileNotFoundError, PermissionError):
        return ()

    ab_as_tuple = ()
    for (name, record_list_of_list) in ab.items():
        ab_as_tuple += ( ((name,) + tuple((pair[0], pair[1])
                        for pair in record_list_of_list)), )
    return ab_as_tuple


def input_or_default(prompt="", default=""):
    try:
        return input(prompt)
    except (KeyboardInterrupt, EOFError):
        return default


def notabene_handler():
    print("nb_handler here!")
    return "nb_handler here!"

class PageEngine(BaseHTTPRequestHandler):
    c_keep_running = True
    c_box = None

    def do_GET(self):
        parsed = urlparse(self.path)

        # Get the query string
        # query_string = parsed.query

        # Get the request path, this new path does not have the query string
        path = parsed.path

        if path == '/':
            path = "/index.html"

        self.send_response(200)
        self.send_header("Content-Encoding", "gzip")
        # self.send_header("Content-Type", "text/html")
        self.end_headers()

        # Send the body of the response
        name = str(Path(__file__).parent / "web" / (path[1:] + ".gz"))
        try:
            with open(name, "rb") as fh:
                self.wfile.write(fh.read())
        except (FileNotFoundError, KeyError) as e:
            print(str(e))

    def do_POST(self):
        # Read the content-length header
        content_length = int(self.headers.get("Content-Length"))

        # Read that many bytes from the body of the request
        body = self.rfile.read(content_length)

        body = unquote_plus(body.decode("utf-8"))
        print(f"Post BODY: '{body}'")

        value = parse_qs(body)
        if "exit" in value.keys():
            print("Bye bye!")
            PageEngine.c_keep_running = False
        elif "firstly" in value.keys():
            body = "{" \
                        f"all:{len(PageEngine.c_box.ab)}," \
                        f"fit:{len(PageEngine.c_box.ab_fit)}," \
                        f"fit_to_fit:{len(PageEngine.c_box.ab_fit_to_fit)}" \
                    "}"
        else:
            # notabene_handler()
            print(f"command='{value['command'][0]}'")

        self.send_response(200)
        self.end_headers()

        # Send the body in the response
        self.wfile.write(bytes(body, "utf-8"))

    def log_message(self, format: str, *args: Any) -> None:
        """Do not print log"""
        return


def httpd_server(box):
    PageEngine.c_keep_running = True
    PageEngine.c_box = box
    try:
        httpd = HTTPServer(('localhost', HTTPD_PORT), PageEngine)

        webbrowser.open(f"http://localhost:{HTTPD_PORT}")
        while PageEngine.c_keep_running:
            httpd.handle_request()
    except (OSError, PermissionError, OverflowError, KeyboardInterrupt):
        pass

    return None


def main() -> None:
    # Function is used as convenient container for associated objects
    turn_on_edit_in_input()
    def box(): pass
    box.ab = AddressBook(load_addressbook())
    box.ab_fit = tuple(box.ab.keys())
    box.ab_fit_to_fit = box.ab_fit
    print("Use ? for more information")

    while True:

        for attempt in range(2):
            mflag = "C"
            if box.ab.is_modified:
                mflag = '@'
            cmd_raw = input_or_default(
                f"({len(box.ab)}" # total records
                f"({len(box.ab_fit)}" # records in MATCH SET
                f"({len(box.ab_fit_to_fit)}" # records in MATCH SUBSET
                f"(({mflag}> ", "Ctrl+C")
            if cmd_raw == "Ctrl+C":
                # Is pressed Ctrl+C or Ctrl+D
                if attempt == 0 and box.ab.is_modified:
                    print(os.linesep + "Addressbook was modified: use "
                          "'exit' or '.' to save changes and exit." +
                          os.linesep + "Or press Ctrl+C again to exit "
                          "without saving")
                    continue
                print("")
                return # exit without saving
            else:
                break

        cmd_raw = normalize(cmd_raw)
        if cmd_raw == "":
            # Empty string: nothing to do
            continue
        elif cmd_raw == "@":
            httpd_server(box)
            continue

        (cmd, cmd_args) = parse(cmd_raw)

        handler = get_handler(cmd)
        result = handler(cmd_args, box)

        if isinstance(result, types.GeneratorType):
            # Iterator for pagenation
            try:
                # Print and do not ask "Next?" on the last page
                prev_text = next(result)
                for text in result:
                    print(prev_text)
                    ans = input_or_default("Next? (Y|n) ", "ctrl+c").strip().lower()
                    if not(ans == "" or ans.startswith('y')):
                        if ans == "ctrl+c":
                            print("")
                        break
                    prev_text = text
                else:
                    print(prev_text)
            except StopIteration:
                # Nothing to print
                pass
        elif isinstance(result, str):
            if result != "":
                print(result)

        if handler is cmd_exit:
            if box.ab.is_modified:
                dump_addressbook(box)
            break


def turn_on_edit_in_input():
    try:
        import readline
        try:
            readline.read_history_file(HISTFILE)
        except FileNotFoundError:
            pass
        # Default history len is -1 (infinite), which may grow unruly
        readline.set_history_length(1000)
        atexit.register(readline.write_history_file, HISTFILE)
    except ModuleNotFoundError:
        pass


if __name__ == "__main__":
    main()
