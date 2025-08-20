"""
This module constains the flask server for viewing the documentation and for live editing.
The server is lunched with `gitbuilding serve` or `gitbuilding webapp` and runs on port 6178.
"""

import logging
from uuid import uuid4
import socket
import json
from copy import deepcopy
import posixpath
import requests
import flask
from flask import request, jsonify
import waitress
from gitbuilding.live_editor import LiveEditor, DevLiveEditor
from gitbuilding.example import output_example_project
from gitbuilding.utilities import get_project_title, supported_licenses
from gitbuilding.native_file_operations import (GBPATH,
                                                DATADIR,
                                                as_native_path,
                                                is_local_file,
                                                read_local_file,
                                                list_dirs_and_files,
                                                is_valid_directory_name,
                                                make_dir_if_needed,
                                                exists_on_disk,
                                                make_local_dir,
                                                write_local_file)
_LOGGER = logging.getLogger('BuildUp.GitBuilding')




class GBServer(flask.Flask):
    """
    GBServer is the GitBuilding server it is a child class of flask.Flask. It is pretty lightweight.
    All functionality to manage live editors is handled by the LiveEditorManager. All dunctionality to
    preview and edit documentation is handled by live_editor.LiveEditor
    """

    def __init__(self, handler, working_dir, editor_only=False, dev=False):

        super().__init__(__name__)
        self._working_dir = working_dir
        self._dev = dev
        self._editor_only = editor_only
        self.editor_manager = LiveEditorManager(self, handler, single_editor=editor_only, dev=dev)
        if editor_only:
            self.editor_manager.create_editor(working_dir)
        else:
            self.add_url_rule('/', "server_home", self._home)
            self.add_url_rule('/-/list-files',
                              "list-local-files",
                              self._list_local_files,
                              methods=["POST"])
            self.add_url_rule('/-/list-licenses', "list-licenses", self._list_licenses)
        self.editor_manager.create_url_rules()
        if dev: # pragma: no cover
            self._add_dev_url_rules(editor_only)

    def _add_dev_url_rules(self, editor_only): # pragma: no cover
        self.add_url_rule("/static/webapp/<path:subpath>",
                          "dev_editor_static",
                          self._dev_editor_static)

        self.add_url_rule("/static/<path:subpath>",
                          "dev_other_static",
                          self._dev_other_static)
        if not editor_only:
            self.add_url_rule("/live/<string:editorname>/static/webapp/<path:subpath>",
                              "dev_editor_static",
                              self._dev_editor_static)
            self.add_url_rule("/live/<string:editorname>/static/<path:subpath>",
                              "dev_other_static",
                              self._dev_other_static)

        self.add_url_rule("/sockjs-node/<path:subpath>",
                          "dev_editor_sockjs",
                          self._dev_sockjs)

        self.add_url_rule("/__webpack_dev_server__/<path:subpath>",
                          "dev_editor_webpack",
                          self._dev_webpack)

    @property
    def working_dir(self):
        return self._working_dir

    def run(self, host="localhost", port=6178, use_waitress=False): # pylint: disable=arguments-differ
        """
        Starts the flask server
        """
        try:
            # Check the server isn't already running (only needed on Windows)
            sock = socket.create_connection((host, port), timeout=0.5)
            sock.close()
            # If we have made it past this, there is a server running - so we
            # should fail
            raise ServerAlreadyRunningError(f'A server is already running on "{host}"'
                                            f' port {port}.')
        except socket.timeout:
            pass  # If we couldn't connect, ignore the error
        except ConnectionError:
            pass # If we couldn't connect, ignore the error

        if use_waitress:
            print('GitBuilding server running on http://localhost:6178/ (Press CTRL+C to quit)')
            waitress.serve(self, host=host, port=port)
        else:
            super().run(host, port)

    def _home(self):
        #add-dev-option
        if self._dev:
            return self._dev_home()
        page = "static/webapp/project-selector.html"
        return flask.send_from_directory(GBPATH, page)

    def _list_local_files(self):
        content = request.get_json()
        if "path" in content:
            path = content["path"]
            path = posixpath.normpath(path)
            if path == '.':
                path = ''
            if path.startswith('..'):
                error_msg = "For security the web app will not navigate out of the server directory"
                return jsonify({'completed': False, 'msg': error_msg})
            try:
                dirs_and_files = list_dirs_and_files(path, self._working_dir)
            except ValueError:
                error_msg = "Problem opening this directory. Is it an absolute path?"
                return jsonify({'completed': False, 'msg': error_msg})
            except FileNotFoundError:
                error_msg = f'Cannot find directory "{path}". Are you sure it exists?'
                return jsonify({'completed': False, 'msg': error_msg})
            response = {'completed': True, 'normpath': path}
            directorylist = [item.name for item in dirs_and_files if item.is_dir()]
            filelist = [item.name for item in dirs_and_files if item.is_file()]
            response['directoryList'] = sorted(directorylist, key=str.casefold)
            response['fileList'] = sorted(filelist, key=str.casefold)
            return jsonify(response)
        return jsonify({'completed': False, 'msg': "Path not specified"})

    def _list_licenses(self):
        return jsonify({'licenses': supported_licenses()})

    def _dev_home(self):
        url = "http://localhost:8080/static/webapp/project-selector.html"
        try:
            req = requests.request(flask.request.method, url, timeout=5)
        except requests.exceptions.RequestException:
            msg = (f"ERROR: Could not connect to webapp dev server for '{url}',"
                   " did you forget to start it?")
            return flask.abort(flask.Response(msg, status=500))
        return req.text

    def _dev_editor_static(self, subpath, editorname=None):# pylint: disable=unused-argument
        url = "http://localhost:8080/static/webapp/" + subpath
        try:
            req = requests.request(flask.request.method, url, timeout=5)
        except requests.exceptions.RequestException:
            msg = (f"ERROR: Could not connect to webapp dev server for '{url}',"
                   " did you forget to start it?")
            return flask.abort(flask.Response(msg, status=500))
        if subpath.endswith('.svg'):

            return flask.Response(req.text, mimetype='image/svg+xml')
        return req.text

    def _dev_other_static(self, subpath, editorname=None):# pylint: disable=unused-argument
        return flask.send_from_directory("static", subpath)

    def _dev_sockjs(self, subpath):
        url = ("http://localhost:8080/sockjs-node/"
               + subpath
               + flask.request.query_string.decode())
        try:
            req = requests.request(flask.request.method, url, timeout=5)
        except requests.exceptions.RequestException:
            msg = (f"ERROR: Could not connect to webapp dev server for '{url}',"
                   " did you forget to start it?")
            return flask.abort(flask.Response(msg, status=500))
        return req.text

    def _dev_webpack(self, subpath):
        url = ("http://localhost:8080/__webpack_dev_server__/"
               + subpath
               + flask.request.query_string.decode())
        try:
            req = requests.request(flask.request.method, url, timeout=5)
        except requests.exceptions.RequestException:
            msg = (f"ERROR: Could not connect to webapp dev server for '{url}',"
                   " did you forget to start it?")
            return flask.abort(flask.Response(msg, status=500))
        return req.text


CLOSED = 0
LAUNCHING = 1
RUNNING = 2

class LiveEditorManager:
    """
    This handles all url rule creation for managing live editors and handles passing
    requests onto the correct live editor.
    """

    def __init__(self, server, handler, single_editor=True, dev=False):
        self.server = server
        self._handler = handler
        self._dev = dev
        self.editors = {}
        self._editor_counter = 0
        self._closed_editors = []
        self._single_editor = single_editor
        self._projects = []
        file_errors = False
        if is_local_file("projects.json", DATADIR):
            projects_from_file = json.loads(read_local_file("projects.json", DATADIR))
            for project in projects_from_file:
                if "name" in project and "working_dir" in project:
                    project["editorName"] = ""
                    project["uuid"] = str(uuid4())
                    project["editorStatus"] = CLOSED
                    self._projects.append(project)
                else:
                    file_errors = True
                    _LOGGER.warning('Corrupted project %s being removed', str(project))
            if file_errors:
                self._update_projects_file()

    def _update_projects_file(self):
        projects_dict = deepcopy(self._projects)
        for project in projects_dict:
            del project["editorName"]
            del project["uuid"]
            del project["editorStatus"]
        make_dir_if_needed("projects.json", DATADIR, isfile=True)
        write_local_file("projects.json", DATADIR, json.dumps(projects_dict))

    def create_editor(self, working_dir, name=None):
        """
        Starts a new live editor. Nothing is returned
        """
        if name is None:
            name = "only"
            url_prefix = ""
        else:
            url_prefix = f"/live/{name}"
        if self._dev:
            self.editors[name] = DevLiveEditor(working_dir, url_prefix, self._handler)
        else:
            self.editors[name] = LiveEditor(working_dir, url_prefix, self._handler)

    def add_url_rule(self, *args, **kwargs):
        """
        A small helper function to reduce characters when running create url rule
        """
        self.server.add_url_rule(*args, **kwargs)

    def _add_editor_url_rule(self, sub_rule, endpoint, func, **kwargs):
        """
        Add a url rule to the editor. This rule needs to be added twice.
        """
        prefix = self.editor_prefix
        self.add_url_rule(prefix+"/-/editor/"+sub_rule, endpoint, func, **kwargs)
        self.add_url_rule(prefix+"/<path:rawsubpath>/-/editor/"+sub_rule, endpoint, func, **kwargs)

    @property
    def editor_prefix(self):
        """
        the prefix for a rule to be sent to a live editor
        """
        if self._single_editor:
            prefix = ''
        else:
            prefix = '/live/<string:editorname>'
        return prefix


    def create_url_rules(self):
        """
        Create all of the URL rules for the managing live editors and all the url rules
        for communitcating with live editors
        """

        # Disabling long lines here as honestly I belive that a long line of these rules is
        # clearer than breaking up the url rules onto many lines.
        # pylint: disable=line-too-long

        prefix = self.editor_prefix
        if not self._single_editor:
            self.add_url_rule('/launcher/data', "launcher_data", self._launcher_data)
            self.add_url_rule('/launcher/launch', "_launch_editor", self._launch_editor, methods=["POST"])
            self.add_url_rule('/launcher/remove', "_remove_project", self._remove_project, methods=["POST"])
            self.add_url_rule('/launcher/open-project', "_open_project", self._open_project, methods=["POST"])
            self.add_url_rule('/launcher/new-project', "_new_project", self._new_project, methods=["POST"])

            self.add_url_rule(prefix+"/static/<path:static_file>", "editor-static", self._editor_static)

        self.add_url_rule(prefix+"/", "render", self._render_page)

        self.add_url_rule(prefix+"/<path:rawsubpath>", "render", self._render_page)
        self.add_url_rule(prefix+"/-/<path:rawsubpath>", "undef_special", self._undefined_special_page)
        self.add_url_rule(prefix+"/assets/<path:rawsubpath>", "assets", self._return_assets)
        self.add_url_rule(prefix+"/-/new-page/", "new_page", self._new_page)
        self.add_url_rule(prefix+"/-/new-page/list-files", "new_page_file_list", self._new_page_file_list, methods=["POST"])
        self.add_url_rule(prefix+"/-/new-page/create-from-template", "create_from_template", self._create_from_template, methods=["POST"])
        self.add_url_rule(prefix+"/-/warnings", "warning_page", self._warning_page)
        self.add_url_rule(prefix+"/-/create-homepage/", "create_homepage", self._create_homepage)

        self.add_url_rule(prefix+"/-/contents-page/", "contents_page", self._contents_page)
        self.add_url_rule(prefix+"/-/contents-page/list-output-files", "contents_page-output-file-list", self._contents_page_output_file_list, methods=["POST"])
        self.add_url_rule(prefix+"/-/contents-page/list-source-files", "contents_page-source-file-list", self._contents_page_source_file_list, methods=["POST"])
        self.add_url_rule(prefix+"/-/contents-page/file-info", "contents_page-file-info", self._contents_page_file_info, methods=["POST"])
        self.add_url_rule(prefix+"/-/contents-page/rename-file", "contents_page-rename-file", self._contents_page_rename_file, methods=["POST"])


        self._add_editor_url_rule("", "editor", self._edit_page)
        self._add_editor_url_rule("save", "save", self._save_edit, methods=["POST"])
        self._add_editor_url_rule("raw", "raw", self._raw_md)
        self._add_editor_url_rule("render_markdown", "live_render", self._live_render, methods=["POST"])
        self._add_editor_url_rule("dropped-file", "droppedfile", self._dropped_file, methods=["POST"])
        self._add_editor_url_rule("partlist", "part_list", self._part_list)

        self.add_url_rule("/search_index.json", "search_index", self._serve_search_index)

        self.add_url_rule(prefix+"/-/navbar-buttons.js", "nav_buttons", self._nav_buttons)

        self.add_url_rule(prefix+"/-/conf-editor/", "conf_editor", self._conf_edit)
        self.add_url_rule(prefix+"/-/conf-editor/raw", "raw_config", self._raw_config)
        self.add_url_rule(prefix+"/-/conf-editor/save", "save_config", self._save_config, methods=["POST"])

        self.add_url_rule(prefix+"/-/pdf/", "pdf", self._pdf)
        self.add_url_rule(prefix+"/-/pdf/status", "pdf_status", self._pdf_status)
        self.add_url_rule(prefix+"/-/pdf/fetch/<int:pdf_id>", "pdf_fetch", self._pdf_fetch)
        self.add_url_rule(prefix+"/-/pdf/generate", "pdf_generate", self._pdf_generate, methods=["POST"])

    def _launcher_data(self):
        return jsonify({"projects": self._projects})

    def _open_project(self):
        content = request.get_json()
        if "path" in content:
            path = content['path']
            working_dir = as_native_path(path, self.server.working_dir)
            name = get_project_title(working_dir)
            self._projects.append({'name': name,
                                   'working_dir': working_dir,
                                   'editorName': "",
                                   'uuid': str(uuid4()),
                                   'editorStatus': CLOSED})
            self._update_projects_file()
            return jsonify({"completed": True})
        return flask.abort(405)

    def _new_project(self):
        content = request.get_json()
        for key in ['projectConfig', 'Path', 'newDir']:
            if key not in content:
                return flask.abort(405)

        config = content['projectConfig']
        title = config['Title']
        del config['Title']
        #Remove any empty keys
        for key in list(config.keys()):
            if len(config[key]) == 0:
                del config[key]

        newdir = content['newDir']
        parent_dir = as_native_path(content['Path'], self.server.working_dir)
        if not is_valid_directory_name(newdir):
            msg = "Directory name invalid"
            return jsonify({"completed": False, "msg": msg})
        if exists_on_disk(newdir, parent_dir):
            msg = f"Cannot create directory '{newdir}', as it already exists"
            return jsonify({"completed": False, "msg": msg})
        try:
            make_local_dir(newdir, parent_dir)
        except (PermissionError, FileNotFoundError):
            msg = f"Failed to create directory '{newdir}' do you have the correct permissions?"
            return jsonify({"completed": False, "msg": msg})

        fullpath = as_native_path(newdir, parent_dir)

        completed = output_example_project(fullpath,
                                           interactive=False,
                                           title=title,
                                           config=config)
        if not completed:
            msg = "Unknown error ouputting files."
            return jsonify({"completed": False, "msg": msg})

        self._projects.append({'name': title,
                               'working_dir': fullpath,
                               'editorName': "",
                               'uuid': str(uuid4()),
                               'editorStatus': CLOSED})
        self._update_projects_file()
        return jsonify({"completed": True})

    def _get_project_index_from_uuid(self, uuid):
        uuids = [proj["uuid"] for proj in self._projects]
        if uuid in uuids:
            return uuids.index(uuid)
        return None

    def _remove_project(self):
        content = request.get_json()
        if "uuid" in content:
            index = self._get_project_index_from_uuid(content["uuid"])
            if index is None:
                msg = "Cannot find the requested editor"
                return jsonify({"completed": False, "msg": msg})

            removed_project = self._projects.pop(index)
            self._update_projects_file()

            name = removed_project['editorName']
            if name in self.editors:
                del self.editors[name]
                self._closed_editors.append(name)

            return jsonify({"completed": True})
        return flask.abort(405)

    def _launch_editor(self):
        content = request.get_json()
        if "uuid" in content:
            index = self._get_project_index_from_uuid(content["uuid"])
            if index is None:
                msg = "Cannot find the requested editor"
                return jsonify({"completed": False, "msg": msg})

            self._editor_counter+=1
            name = f"editor{self._editor_counter}"
            project = self._projects[index]
            self.create_editor(project["working_dir"], name=name)
            project["editorName"] = name
            project["editorStatus"] = RUNNING
            return jsonify({"launched": True, "editorName": name})
        return flask.abort(405)

    def _get_editor(self, editorname=None, dev_static=False):
        if editorname is None and self._single_editor:
            if "only" in self.editors:
                return self.editors["only"]
            raise RuntimeError("Editor hasn't been started.")
        if editorname is not None and not self._single_editor:
            if editorname in self.editors:
                return self.editors[editorname]
            if editorname in self._closed_editors:
                return ClosedEditor()
            return UnknownEditor()
        if dev_static:
            # in the the case of the dev server static files, the editor name
            # isn't provided. Using any editor should be fine
            return next(iter(self.editors.values()))
        raise RuntimeError("Unknown problem trying to find editor")

    def _editor_static(self, static_file, editorname=None): # pylint: disable=unused-argument
        return flask.send_from_directory('static', static_file)

    def _nav_buttons(self, editorname=None):
        editor = self._get_editor(editorname)
        return editor.nav_buttons()

    def _conf_edit(self, editorname=None):
        editor = self._get_editor(editorname)
        return editor.conf_edit()

    def _contents_page(self, editorname=None):
        editor = self._get_editor(editorname)
        return editor.contents_page()

    def _contents_page_output_file_list(self, editorname=None):
        editor = self._get_editor(editorname)
        return editor.contents_page_output_file_list()

    def _contents_page_source_file_list(self, editorname=None):
        editor = self._get_editor(editorname)
        return editor.contents_page_source_file_list()

    def _contents_page_file_info(self, editorname=None):
        editor = self._get_editor(editorname)
        return editor.contents_page_file_info()

    def _contents_page_rename_file(self, editorname=None):
        editor = self._get_editor(editorname)
        return editor.contents_page_rename_file()

    def _create_from_template(self, editorname=None):
        editor = self._get_editor(editorname)
        return editor.create_from_template()

    def _create_homepage(self, editorname=None):
        editor = self._get_editor(editorname)
        return editor.create_homepage()

    def _dropped_file(self, rawsubpath=None, editorname=None):
        editor = self._get_editor(editorname)
        return editor.dropped_file(rawsubpath=rawsubpath)

    def _edit_page(self, rawsubpath=None, editorname=None):
        editor = self._get_editor(editorname)
        return editor.edit_page(rawsubpath=rawsubpath)

    def _live_render(self, rawsubpath=None, editorname=None): # pylint: disable=unused-argument
        editor = self._get_editor(editorname)
        return editor.live_render()

    def _new_page(self, editorname=None):
        editor = self._get_editor(editorname)
        return editor.new_page()

    def _new_page_file_list(self, editorname=None):
        editor = self._get_editor(editorname)
        return editor.new_page_file_list()

    def _part_list(self, rawsubpath=None, editorname=None):
        editor = self._get_editor(editorname)
        return editor.part_list(rawsubpath=rawsubpath)

    def _raw_config(self, editorname=None):
        editor = self._get_editor(editorname)
        return editor.raw_config()

    def _raw_md(self, rawsubpath=None, editorname=None):
        editor = self._get_editor(editorname)
        return editor.raw_md(rawsubpath=rawsubpath)

    def _render_page(self, rawsubpath=None, editorname=None):
        editor = self._get_editor(editorname)
        return editor.render_page(rawsubpath=rawsubpath)

    def _return_assets(self, rawsubpath, editorname=None):
        editor = self._get_editor(editorname)
        return editor.return_assets(rawsubpath=rawsubpath)

    def _save_config(self, editorname=None):
        editor = self._get_editor(editorname)
        return editor.save_config()

    def _save_edit(self, rawsubpath=None, editorname=None):
        editor = self._get_editor(editorname)
        return editor.save_edit(rawsubpath=rawsubpath)

    def _undefined_special_page(self, rawsubpath=None, editorname=None):
        editor = self._get_editor(editorname)
        return editor.undefined_special_page(rawsubpath=rawsubpath)

    def _warning_page(self, editorname=None):
        editor = self._get_editor(editorname)
        return editor.warning_page()

    def _serve_search_index(self, editorname=None):
        editor = self._get_editor(editorname)
        return editor.serve_search_index()

    def _pdf(self, editorname=None):
        editor = self._get_editor(editorname)
        return editor.pdf()

    def _pdf_status(self, editorname=None):
        editor = self._get_editor(editorname)
        return editor.pdf_status()

    def _pdf_fetch(self, pdf_id, editorname=None):
        editor = self._get_editor(editorname)
        return editor.pdf_fetch(pdf_id)

    def _pdf_generate(self, editorname=None):
        editor = self._get_editor(editorname)
        return editor.pdf_generate()

class DummyEditor:
    """
    A dummy editor, there is no running editor for the LiveEditorManager to pass
    requests onto they are passed onto a dummy editor to provide default response
    with some more information.
    This class should be sub-classed.
    """

    # pylint: disable=unused-argument
    # pylint: disable=missing-function-docstring

    def __init__(self):
        self.return_html = r"<h1>Dummy Editor</h1>"
        self.return_message = "Dummy Editor"

    def editor_static(self, static_file):
        return self.return_html

    def conf_edit(self):
        return self.return_html

    def contents_page(self):
        return self.return_html

    def contents_page_output_file_list(self):
        return self.return_html

    def contents_page_source_file_list(self):
        return self.return_html

    def contents_page_file_info(self):
        return self.return_html

    def contents_page_rename_file(self):
        return self.return_html

    def create_from_template(self):
        return self.return_html

    def create_homepage(self):
        return self.return_html

    def dropped_file(self, rawsubpath=None):
        return flask.abort(405)

    def edit_page(self, rawsubpath=None):
        return self.return_html

    def live_render(self, rawsubpath=None):
        return flask.abort(405)

    def new_page(self):
        return self.return_html

    def new_page_file_list(self):
        return self.return_html

    def part_list(self, rawsubpath=None):
        return self.return_message

    def raw_config(self):
        return flask.abort(405)

    def raw_md(self, rawsubpath=None):
        return self.return_message

    def render_page(self, rawsubpath=None):
        return self.return_html

    def return_assets(self, rawsubpath):
        return self.return_html

    def save_config(self):
        return flask.abort(405)

    def save_edit(self, rawsubpath=None):
        return flask.abort(405)

    def undefined_special_page(self, rawsubpath=None):
        return self.return_html

    def warning_page(self):
        return self.return_html

    def pdf(self):
        return self.return_html

    def pdf_status(self):
        return self.return_message

    def pdf_fetch(self, pdf_id):
        return flask.abort(405)

    def pdf_generate(self):
        return flask.abort(405)

class ClosedEditor(DummyEditor):
    """
    A dummy editor class to return message that the editor requested is now closed.
    See also UnknownEditor
    """

    def __init__(self):
        super().__init__()
        self.return_html = r"<h1>This editor has been closed</h1>"
        self.return_message = "This editor has been closed<"

class UnknownEditor(DummyEditor):
    """
    A dummy editor class to return message that the editor requested is unknown.
    See also Closed Editor
    """

    def __init__(self):
        super().__init__()
        self.return_html = r"<h1>Cannot find this editor</h1>"
        self.return_message = "Cannot find this editor"

class ServerAlreadyRunningError(Exception):
    """
    Custom exception for if the GitBuilding server is already running.
    """
