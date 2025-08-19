import os
import re
import json
import gazu
import time

from kabaret import flow
from libreflow.flows.default.flow.film import Film
from libreflow.baseflow.file import (
    GenericRunAction,
    TrackedFile,
    FileRevisionNameChoiceValue,
    UploadPNGToKitsu,
    PublishAndRenderPlayblast,
    PublishFileAction,
    UploadAfterPublishValue,
    CreateWorkingCopyAction,
)
from psd_tools import PSDImage
from psd_tools.psd import PSD

from libreflow.baseflow.task import Task
from libreflow.baseflow.task_manager import CreateTaskDefaultFiles
from libreflow.baseflow.users import PresetValue, PresetSessionValue, PresetChoiceValue


class ExportPSDLayers(flow.Action):
    ICON = ("icons.flow", "photoshop")

    _file = flow.Parent()
    _files = flow.Parent(2)
    _task = flow.Parent(3)
    _shot = flow.Parent(5)
    _sequence = flow.Parent(7)

    revision = flow.Param(None, FileRevisionNameChoiceValue)

    def allow_context(self, context):
        return (
            context
            and self._file.format.get() in ["psd", "psb"]
            and len(
                self._file.get_revision_names(
                    sync_status="Available", published_only=True
                )
            ) > 0
        )

    def needs_dialog(self):
        msg = ""
        if self._task.name() == "bg_layout":
            msg = "<b>Layout : Photoshop Project layers will be exported separately</b>"
        elif self._task.name() == "bg_color":
            msg = "<b>BG Color : Photoshop Project will be exported as a single image</b>"
        
        self.message.set(msg)
        return True

    def get_buttons(self):
        self.revision.revert_to_default()
        return ["Export", "Cancel"]

    def ensure_render_folder(self):
        folder_name = self._file.complete_name.get()
        folder_name += "_render"

        if not self._files.has_folder(folder_name):
            self._files.create_folder_action.folder_name.set(folder_name)
            self._files.create_folder_action.category.set("Outputs")
            self._files.create_folder_action.tracked.set(True)
            self._files.create_folder_action.run(None)

        return self._files[folder_name]

    def ensure_render_folder_revision(self):
        folder = self.ensure_render_folder()
        revision_name = self.revision.get()
        source_revision = self._file.get_revision(self.revision.get())

        if not folder.has_revision(revision_name):
            revision = folder.add_revision(revision_name)
            folder.set_current_user_on_revision(revision_name)
        else:
            revision = folder.get_revision(revision_name)

        revision.comment.set(source_revision.comment.get())

        folder.ensure_last_revision_oid()

        self._files.touch()

        return revision
    
    def get_default_file(self):
        mng = self.root().project().get_task_manager()
        default_files = mng.default_files.get()
        for file_name, task_names in default_files.items():
            if 'bg_color.png' in file_name:
                task = default_files[file_name][0]
                file_mapped_name = file_name.replace(".", '_')
                break

        dft_task = mng.default_tasks[task]
        if not dft_task.files.has_mapped_name(file_mapped_name): # check default file
            # print(f'Scene Builder - default task {task_name} has no default file {filename} -> use default template')
            return None

        dft_file = dft_task.files[file_mapped_name]
        return dft_file
    
    def _ensure_file(self, name, format, path_format, source_revision):
        mapped_name = "%s_%s" % (name, format)

        file = None
        
        if not self._files.has_mapped_name(mapped_name):
            if format:
                file = self._files.add_file(
                name=name,
                extension=format,
                tracked=True,
                default_path_format=path_format,
            )
            else:
                file = self._files.add_folder(name, tracked=True)
        else:
            file = self._files[mapped_name]

        revision_name = self.revision.get()

        if not file.has_revision(revision_name):
            r = file.add_revision(revision_name)
            file.set_current_user_on_revision(revision_name)
        else:
            r = file.get_revision(revision_name)

        r.comment.set(source_revision.comment.get())
        
        file.ensure_last_revision_oid()

        r.set_sync_status("Available")

        img_path = r.get_path().replace("\\", "/")

        if not os.path.exists(img_path):
            os.makedirs(os.path.dirname(img_path), exist_ok=True)
        else:
            os.remove(img_path)

        self._files.touch()
        
        return r

    def run(self, button):
        if button == "Cancel":
            return
        
        session = self.root().session()
        log_format = "[EXPORT LAYERS] {message}"

        # Start log message
        session.log_info(
            log_format.format(
                message=f"Export started - {self._sequence.name()} {self._shot.name()} {self._file.name()} {self.revision.get()}"
            )
        )

        # Get revisions
        source_revision = self._file.get_revision(self.revision.get())

        # Open photoshop file
        psb = PSDImage.open(source_revision.get_path())


        ############# BG LAYOUT PROCESS #############

        if self._task.name() == "bg_layout" :

            render_revision = self.ensure_render_folder_revision()
            # JSON structure for layers order
            layers_data = {
                "from": os.path.basename(source_revision.get_path()),
                "layers": [],
                "hidden_layers": []
            }

            # Export image layers
            if os.path.exists(render_revision.get_path()) is False:
                os.makedirs(render_revision.get_path())
            
            folder_name = os.path.basename(render_revision.get_path())

            # frame_bbox = (0, 0, 0, 0)

            # frame_layer = psb.find("white")

            # if frame_layer is None:
            #     raise Exception("FRAME LAYER NOT FOUND")
            # else:
            #     frame_bbox = frame_layer.bbox

            #     if frame_bbox == (0, 0, 0, 0):
            #         raise Exception("Frame Layer has no bounding box")

            #     # Substract by 10pixels (width and height) in order to remove border margin
            #     # frame_bbox = (
            #     #     frame_bbox[0] + 5,
            #     #     frame_bbox[1] + 5,
            #     #     frame_bbox[2] - 5,
            #     #     frame_bbox[3] - 5,
            #     # )
            
            # print(frame_bbox)

            for layer in reversed(psb):
                # Remove invalid characters
                layer_name = layer.name.replace(' ','-')
                match_invalid = re.search(r"[~\"#%&*:<>?/\\{|}]+", layer.name)
                if match_invalid:
                    layer_name = layer_name.replace(match_invalid.group(0), '')

                output_path = os.path.join(
                    render_revision.get_path(),
                    "{folder}-{layer}.png".format(folder=folder_name, layer=layer_name),
                )

                session.log_info(log_format.format(message=f'Exporting layer {layer_name}'))

                if not layer.visible:
                    layer.visible = True
                    # psb.save(source_revision.get_path())

                # Push layer in correct JSON data
                layers_data["layers" if layer.visible else "hidden_layers"].append(
                    layer_name
                )

                image = layer.composite(viewport=psb.viewbox)
                image.save(output_path)

            
            # Export JSON data
            json_object = json.dumps(layers_data)
            json_path = os.path.join(render_revision.get_path(), "layers.json")
            
            session.log_info(log_format.format(message='Saving layers.json'))
            with open(json_path, "w") as outfile:
                outfile.write(json_object)
            
            session.log_info(log_format.format(message='Export complete'))
        
        ############# BG COLOR PROCESS #############
    
        if self._task.name() == "bg_color" :

            default_file = self.get_default_file()

            if default_file is not None:
                                    
                render_revision = self._ensure_file(
                        name="bg_color",
                        format="png",
                        path_format=default_file.path_format.get(),
                        source_revision=source_revision
                    )

                output_path = render_revision.get_path()

                info_layer = psb.find("INFO")
                if info_layer : info_layer.visible = False 

                LO_layer = psb.find("REF_LAYOUT")
                if LO_layer : LO_layer.visible = False 

                DES_layer = psb.find("REF_DESIGN")
                if DES_layer : DES_layer.visible = False

                chara_layer = psb.find("character")
                if chara_layer : chara_layer.visible = False 

                utils_layer = psb.find("_utils")
                if utils_layer : utils_layer.visible = False 

                image = psb.composite(viewport=psb.viewbox,force=True)
                image.save(output_path)

                session.log_info(log_format.format(message='Export complete'))

            else:
                self.root().session().log_error("[Export PSD] BG Color Image default file do not exist")

        return self.get_result(close=True)


class SequencesSelectAll(flow.values.SessionValue):
    DEFAULT_EDITOR = "bool"

    _action = flow.Parent()

    def _fill_ui(self, ui):
        super(SequencesSelectAll, self)._fill_ui(ui)
        if self._action.sequences.choices() == []:
            ui["hidden"] = True


class SequencesMultiChoiceValue(flow.values.SessionValue):
    DEFAULT_EDITOR = "multichoice"

    _action = flow.Parent()

    def choices(self):
        return self._action._film.sequences.mapped_names()

    def revert_to_default(self):
        self.choices()
        self.set([])


class TaskChoiceValue(flow.values.SessionValue):
    DEFAULT_EDITOR = "choice"

    _action = flow.Parent()

    def choices(self):
        return ['Any', 'BG_Layout', 'BG_Color']


class ExportPSDLayersBatch(flow.Action):
    ICON = ("icons.flow", "photoshop")

    select_all = (
        flow.SessionParam(False, SequencesSelectAll).ui(editor="bool").watched()
    )
    sequences = flow.SessionParam([], SequencesMultiChoiceValue)
    task_target = flow.SessionParam("Any", TaskChoiceValue)

    _film = flow.Parent()

    def allow_context(self, context):
        user = self.root().project().get_user()
        return user.status.get() == "Admin"

    def get_buttons(self):
        return ["Export", "Close"]

    def needs_dialog(self):
        self.message.set("<h2>Batch Export Layers</h2>")
        return True

    def child_value_changed(self, child_value):
        if child_value is self.select_all:
            if child_value.get():
                self.sequences.set(self.sequences.choices())
            else:
                self.sequences.revert_to_default()

    def run(self, button):
        if button == "Close":
            return
        
        session = self.root().session()
        log_format = "[BATCH EXPORT LAYERS] {status} - {sequence} {shot} {file} {revision}"

        for seq_name in self.sequences.get():
            seq = self._film.sequences[seq_name]
            for shot in seq.shots.mapped_items():
                for task in shot.tasks.mapped_items():
                    # Ignore if specific task parameter is used
                    if (
                        self.task_target.get() != "Any"
                        and task.name() != self.task_target.get().lower()
                    ):
                        continue
                    for f in task.files.mapped_items():
                        # Get only photoshop files
                        if (
                            f.format.get() in ["psd", "psb"]
                            and len(
                                f.get_revision_names(
                                    sync_status="Available", published_only=True
                                )
                            ) > 0
                        ):
                            # Check if revision is already exported
                            if task.files.has_folder(f'{task.name()}_render'):
                                render_folder = task.files[f'{task.name()}_render']
                                render_revision = render_folder.get_head_revision(sync_status="Available")
                                if render_revision and os.path.exists(render_revision.get_path()):
                                    session.log_warning(
                                        log_format.format(
                                            status="Already exported",
                                            sequence=seq.name(),
                                            shot=shot.name(),
                                            file=f.display_name.get(),
                                            revision=render_revision.name()
                                        )
                                    )
                                    continue
                            
                            # Start export base action
                            f.export_layers.revision.revert_to_default()
                            f.export_layers.run("Export")

                            # Wait for base action to finish
                            for sp in (
                                self.root()
                                .session()
                                .cmds.SubprocessManager.list_runner_infos()
                            ):
                                if sp["is_running"] and sp["label"] == "Export Layers":
                                    while sp["is_running"]:
                                        time.sleep(1)
                                        sp = (
                                            self.root()
                                            .session()
                                            .cmds.SubprocessManager.get_runner_info(
                                                sp["id"]
                                            )
                                        )
                                    break
                                    
                            # Upload render to exchange
                            render_folder = f.export_layers.ensure_render_folder()
                            render_revision = render_folder.get_head_revision(sync_status="Available")

                            if render_revision:
                                render_revision.upload.run('Upload')
        
        session.log_info('[BATCH EXPORT LAYERS] Batch complete')


class PublishandExportPSD(PublishAndRenderPlayblast):
    ICON = ('icons.libreflow', 'publish')

    _shot = flow.Parent(5)
    _sequence = flow.Parent(7)
    _film = flow.Parent(9)

    def allow_context(self, context):
        return (
            context
            and super(PublishandExportPSD, self).allow_context(context)
            and self._file.format.get() in ["psd", "psb"]
        )

    def get_bg_layout(self):
        source_file = None
        shot_entity = (
            self.root()
            .project()
            .films[self._film.name()]
            .sequences[self._sequence.name()]
            .shots[self._shot.name()]
        )

        bg_layout_task = shot_entity.tasks["bg_layout"]
        if bg_layout_task.files.has_file("bg_layout", "psb"):
            # Get the file path as parent
            source_file = bg_layout_task.files["bg_layout_psb"].get_head_revision()

        return source_file

    def get_buttons(self):
        msg = "<h2>Publish and Export Preview</h2>"

        if "bg_color" in self._file.name():
            bg_layout_file = self.get_bg_layout()
            bg_layout_psb = PSDImage.open(bg_layout_file.get_path())
            working_copy_path = self._file.get_working_copy().get_path()
            psb = PSDImage.open(working_copy_path)

            if psb.size != bg_layout_psb.size:
                msg += (f"""<h3><font color=#D66500>
                    Does not conform to the size of bg_layout.
                    </font></h3>
                    <h4><font color=#D66500>
                    BG_layout size = {bg_layout_psb.size}
                    </font></h4>
                    """)

            if psb.depth != 16:
                msg += (
                    "<h3><font color=#D66500>"
                    "This file is not in 16-bit format."
                    "</font></h3>"
                    "<h4><font color=#D66500>"
                    "To convert to 16 Bits/Channel, choose `Image  > Mode > 16 Bits/Channel`."
                    "</font></h4>"
                )

                self.message.set(msg)
                return ["Cancel"]

        self.message.set(msg)

        return ["Publish and Export Preview", "Cancel"]

    def _configure_and_render(self, revision_name, upload_after_publish):
        export_preview = self._file.export_preview
        export_preview.revision.set(revision_name)
        export_preview.upload_to_kitsu.set(upload_after_publish)

        return export_preview.run("Export")

    def run(self, button):
        if button == "Cancel":
            return

        project_settings = self.root().project().settings()
        if (
            self.comment.get() == ""
            and not project_settings.optional_publish_comment.get()
        ):
            self.message.set(
                "<h2>Publish</h2>Please enter a comment to describe your changes."
            )
            return self.get_result(close=False)

        # Update parameter presets
        self.update_presets()

        # Publish
        publish_action = self._file.publish_action
        publish_action.publish_file(
            self._file,
            comment=self.comment.get(),
            keep_editing=self.keep_editing.get(),
            upload_after_publish=False,
        )

        # Playblast
        ret = self._configure_and_render(
            self._file.get_head_revision().name(), self.upload_after_publish.get()
        )

        return ret


class ExportPSDPreview(flow.Action):
    ICON = ("icons.flow", "photoshop")

    revision = flow.Param(None, FileRevisionNameChoiceValue)
    upload_to_kitsu = flow.BoolParam(False)

    _file = flow.Parent()
    _shot = flow.Parent(5)
    _sequence = flow.Parent(7)

    def allow_context(self, context):
        return (
            context
            and self._file.format.get() in ["psd", "psb"]
            and len(
                self._file.get_revision_names(
                    sync_status="Available", published_only=True
                )
            ) > 0
        )

    def needs_dialog(self):
        self.revision.revert_to_default()
        return True

    def get_buttons(self):
        return ["Export", "Cancel"]

    def get_target_path(self):
        rev = self._file.get_revision(self.revision.get())
        return rev.get_path()

    def export_full(self, psb, file_path):
        self.root().session().log_info("Exporting full project")

        output_path = f"{os.path.splitext(file_path)[0]}.png"

        image = psb.composite(viewport=psb.viewbox)
        image.save(output_path)

        return output_path

    def export_no_chara(self, psb, file_path):
        self.root().session().log_info("Exporting project without characters")

        output_path = f"{os.path.splitext(file_path)[0]}_no_chara.png"

        info_layer = psb.find("INFO")
        if info_layer : info_layer.visible = False 

        LO_layer = psb.find("REF_LAYOUT")
        if LO_layer : LO_layer.visible = False 

        DES_layer = psb.find("REF_DESIGN")
        if DES_layer : DES_layer.visible = False

        chara_layer = psb.find("character")
        if chara_layer : chara_layer.visible = False 

        utils_layer = psb.find("_utils")
        if utils_layer : utils_layer.visible = False 

        image = psb.composite(viewport=psb.viewbox,force=True)

        image.save(output_path)

        return output_path

    def export_cropped(self, psb, file_path):
        self.root().session().log_info("Exporting project in film format")

        output_path = f"{os.path.splitext(file_path)[0]}_no_safety.png"

        frame_bbox = (0, 0, 0, 0)

        frame_layer = psb.find("FRAME 4096x1716")

        if frame_layer is None:
            raise Exception("FRAME LAYER NOT FOUND")
        else:
            frame_bbox = frame_layer.bbox

            if frame_bbox == (0, 0, 0, 0):
                raise Exception("Frame Layer has no bounding box")

            # Substract by 10pixels (width and height) in order to remove border margin
            frame_bbox = (
                frame_bbox[0] + 5,
                frame_bbox[1] + 5,
                frame_bbox[2] - 5,
                frame_bbox[3] - 5,
            )

        image = psb.composite(viewport=psb.viewbox)
        image = image.crop(frame_bbox)
        image.save(output_path)

        return output_path

    def run(self, button):
        if button == "Cancel":
            return

        path = self.get_target_path()
        psb = PSDImage.open(path)

        full_img_path = self.export_full(psb, path)
        no_chara_img_path = self.export_no_chara(psb, path)
        cropped_img_path = self.export_cropped(psb, path)

        if self.upload_to_kitsu.get():
            self._file.upload_preview.full_img_path.set(full_img_path)
            self._file.upload_preview.no_chara_img_path.set(no_chara_img_path)
            self._file.upload_preview.cropped_img_path.set(cropped_img_path)
            self._file.upload_preview.revision_name.set(self.revision.get())
            return self.get_result(next_action=self._file.upload_preview.oid())


class UploadPSDPreview(UploadPNGToKitsu):
    _file = flow.Parent()

    full_img_path = flow.Param("").ui(hidden=True)
    no_chara_img_path = flow.Param("").ui(hidden=True)
    cropped_img_path = flow.Param("").ui(hidden=True)

    def allow_context(self, context):
        return context and context.endswith(".details")

    def upload_preview(
        self,
        kitsu_entity,
        task_type_name,
        task_status_name,
        path_list,
        comment="",
        user_name=None,
    ):
        kitsu_api = self.root().project().kitsu_api()

        # Get user
        user = kitsu_api.get_user(user_name)

        # Get task
        task = kitsu_api.get_task(kitsu_entity, task_type_name)

        if task is None or user is None:
            return False

        # Add comment with preview

        # Check if preview file exists
        for file_path in path_list:
            if not os.path.exists(file_path):
                self.root().session().log_error(
                    f"Preview file '{file_path}' does not exists."
                )
                return False

        task_status = gazu.task.get_task_status_by_name(task_status_name)

        # Check if status is valid
        if task_status is None:
            task_statuses = gazu.task.all_task_statuses()
            names = [ts["name"] for ts in task_statuses]
            self.root().session().log_error(
                (
                    f"Invalid task status '{task_status_name}'."
                    "Should be one of " + str(names) + "."
                )
            )
            return False

        comment = gazu.task.add_comment(task, task_status, comment=comment)

        for file_path in path_list:
            try:
                gazu.task.add_preview(task, comment, file_path)
            except json.decoder.JSONDecodeError:
                self.root().session().log_warning(
                    f"Invalid response from Gazu while uploading preview {file_path}"
                )

        return True

    def run(self, button):
        if button == "Cancel":
            return

        self.update_presets()

        if not self._check_kitsu_params():
            self.root().session().log_error("KITSU PARAM ERROR")
            return self.get_result(close=False)

        kitsu_api = self.root().project().kitsu_api()
        kitsu_entity = self._ensure_kitsu_entity()

        if kitsu_entity is None:
            self.root().session().log_error(
                "No Kitsu entity for file " + self._file.oid()
            )
            return self.get_result(close=False)

        task_status_data = kitsu_api.get_task_status(
            short_name=self.target_task_status.names_dict[self.target_task_status.get()]
        )

        success = self.upload_preview(
            kitsu_entity=kitsu_entity,
            task_type_name=self.target_task_type.get(),
            task_status_name=task_status_data["name"],
            path_list=[
                self.full_img_path.get(),
                self.no_chara_img_path.get(),
                self.cropped_img_path.get(),
            ],
            comment=self.comment.get(),
        )

        if not success:
            self.message.set(
                (
                    "<h2>Upload playblast to Kitsu</h2>"
                    "<font color=#FF584D>An error occured "
                    "while uploading the preview.</font>"
                )
            )
            return self.get_result(close=False)

        rev = self._file.get_revision(self.revision_name.get())
        rev.set_status("on_kitsu")


class PublishPSDFile(PublishFileAction):

    _task = flow.Parent(3)
    _shot = flow.Parent(5)
    _sequence = flow.Parent(7)
    _film = flow.Parent(9)

    def __init__(self, name, parent):
        super(PublishPSDFile, self).__init__(parent, name)

    def get_bg_layout(self):
        source_file = None
        shot_entity = (
            self.root()
            .project()
            .films[self._film.name()]
            .sequences[self._sequence.name()]
            .shots[self._shot.name()]
        )

        bg_layout_task = shot_entity.tasks["bg_layout"]
        if bg_layout_task.files.has_file("bg_layout", "psb"):
            # Get the file path as parent
            source_file = bg_layout_task.files["bg_layout_psb"].get_head_revision()

        return source_file

    def get_buttons(self):
        self.check_default_values()

        msg = "<h2>Publish</h2>"

        working_copies = self._file.get_working_copies()
        if working_copies:
            user_names = [wc.user.get() for wc in working_copies]
            user_names = ["<b>" + n + "</b>" for n in user_names]
            msg += (
                "<h3><font color=#D66500><br>"
                "This file is currently being edited by one or more users ({})."
                "</font></h3>".format(", ".join(user_names))
            )

        if "bg_color" in self._file.name():
            bg_layout_file = self.get_bg_layout()
            bg_layout_psb = PSDImage.open(bg_layout_file.get_path())
            working_copy_path = self._file.get_working_copy().get_path()
            psb = PSDImage.open(working_copy_path)

            if psb.size != bg_layout_psb.size:
                msg += f"""<h3><font color=#D66500>
                    Does not conform to the size of bg_layout.
                    </font></h3>
                    <h4><font color=#D66500>
                    BG_layout size = {bg_layout_psb.size}
                    </font></h4>
                    """

            if psb.depth != 16:
                msg += (
                    "<h3><font color=#D66500>"
                    "This file is not in 16-bit format."
                    "</font></h3>"
                    "<h4><font color=#D66500>"
                    "To convert to 16 Bits/Channel, choose `Image  > Mode > 16 Bits/Channel`."
                    "</font></h4>"
                )

                self.message.set(msg)
                return ["Cancel"]

        self.message.set(msg)

        return ["Publish", "Cancel"]

class CreateWorkingCopy(CreateWorkingCopyAction):
    def __init__(self, parent, name):
        super(CreateWorkingCopy, self).__init__(parent, name)

    def get_buttons(self):
        msg = "<h3>Create a working copy</h3>"

        if "bg_color" in self._task.name() and "psb" in self._file.name():
            msg += """<h3>
                Remember to change the colour depth to <u>16 bits</u> in Photoshop.
                </h3>
                <h4>
                To convert to 16 Bits/Channel, choose <u>`Image  > Mode > 16 Bits/Channel`</u>.
                </h4>"""

        # Buttons for Use Base File mode
        if self.use_base_file:
            msg += f"<font color=#FFA34D>WARNING: You should start working on this file \
                    from the latest version of {self.base_file_name} in {self.from_task} task.</font>"
            self.message.set(msg)
            return ["Create from base file", "Create from scratch", "Cancel"]

        if self._file.has_working_copy(from_current_user=True):
            msg += "<font color=#FFA34D>WARNING: You already have a working copy to your name. \
                    Choosing to create a new one will overwrite your changes.</font>"

        self.message.set(msg)

        self.from_revision.revert_to_default()

        return ["Create", "Create from scratch", "Cancel"]


def publish_psd_file(parent):
    if isinstance(parent, TrackedFile) and "psb" in parent.name():
        r = flow.Child(PublishPSDFile).ui(label="Publish")
        r.name = "publish_action"
        r.index = 25
        return r


def create_working_copy(parent):
    if isinstance(parent, TrackedFile) and "psb" in parent.name():
        r = flow.Child(CreateWorkingCopy).ui(label="Create working copy")
        r.name = "create_working_copy_action"
        r.index = 25
        return r


def publish_and_export_preview(parent):
    if isinstance(parent, TrackedFile):
        r = flow.Child(PublishandExportPSD)
        r.name = "publish_and_export_preview"
        r.index = 26
        return r


def upload_preview(parent):
    if isinstance(parent, TrackedFile):
        r = flow.Child(UploadPSDPreview)
        r.name = "upload_preview"
        return r


def export_psd_layers(parent):
    if isinstance(parent, TrackedFile):
        r = flow.Child(ExportPSDLayers)
        r.name = "export_layers"
        r.ui(label="Export")
        r.index = 50
        return r

    if isinstance(parent, Film):
        r = flow.Child(ExportPSDLayersBatch).ui(
            label="Batch Export Layers", dialog_size=(750, 800)
        )
        r.name = "export_layers_batch"
        r.index = None
        return r


def export_psd_preview(parent):
    if isinstance(parent, TrackedFile):
        r = flow.Child(ExportPSDPreview)
        r.name = "export_preview"
        r.index = 49
        return r


def install_extensions(session):
    return {
        "export_psd_layers": [
            export_psd_layers,
            export_psd_preview,
            upload_preview,
            publish_and_export_preview,
            publish_psd_file,
            create_working_copy,
        ]
    }
