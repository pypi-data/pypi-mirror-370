import logging
from os import makedirs
from os.path import basename, dirname, exists
from shutil import move
from typing import Union, Optional

from rich.progress import Progress
from win32com.client import CDispatch, Dispatch, GetObject

import pywintypes
from .error import AddBookmarkError, AddHyperlinkError, ContextError, HookTypeError
from .hook import HOOKTYPE, HookBase
from .utils import logger


def _add_log_file(log_path: str):
    file_handler = logging.FileHandler(log_path, "w", encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s :: %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


class Word:
    """
    Wrapped Word instance.

    """

    def __init__(self, word_file_path: str, save_path: str = None, log_path: Optional[str] = None):
        if log_path is not None:
            if not exists(dirname(log_path)):
                makedirs(dirname(log_path))
            _add_log_file(log_path)

        if not exists(word_file_path):
            logger.error(f"File not found: {word_file_path}")
            raise FileNotFoundError(f"File not found: {word_file_path}")

        self.word_file_path = word_file_path
        self.save_path = save_path
        self.word = None
        self.docx = None

        self._context = False

        self._hook_before_dict: dict[str, HookBase] = {}
        self._hook_in_dict: dict[str, HookBase] = {}
        self._hook_after_dict: dict[str, HookBase] = {}
        self._hook_res_dict = {}
        self._lazy_hook_dict = []

    @property
    def fields(self):
        """
        A wrapper for docx.Fields.

        :return:
        :rtype:
        """
        self._check_context()

        return self.docx.Fields

    def __enter__(self):
        try:
            # attach to existed Word progress
            self.word = GetObject(Class="Word.Application")
            self._attached_existed_progress = True

        except pywintypes.com_error:
            self.word = Dispatch("Word.Application")
            self.word.Visible = False
            self._attached_existed_progress = False

        if self._attached_existed_progress:
            logger.warning(f"Open word file in visible mode, DO NOT CLOSE the word window!")

        self.docx = self.word.Documents.Open(self.word_file_path)

        self._context = True

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self._close_word()
            raise exc_type(exc_val)

        else:
            self._perform()

            self._context = False

            self.to_word()
            self._close_word()
            
    def _close_word(self):
        if not self._attached_existed_progress:
            self.docx.Close(False)
            self.word.Quit()
        else:
            self.docx.Close(False)

    def _check_context(self):
        if not self._context or self.word is None or self.docx is None:
            raise ContextError(f"You must enter Noterools context to do following operations")

    def add_bookmark(self, bookmark_id: str, text_range: CDispatch):
        """
        Add a bookmark to Word.

        :param bookmark_id: Unique ID of the bookmark.
        :type bookmark_id: str
        :param text_range: Text range of Word.
        :type text_range:
        :return:
        :rtype:
        """
        self._check_context()

        try:
            self.docx.Bookmarks.Add(Name=bookmark_id, Range=text_range)
        except pywintypes.com_error as error:
            logger.error(f"Cannot add bookmarks: {bookmark_id}. Error is: {error}")
            raise AddBookmarkError(f"Cannot add bookmarks: {bookmark_id}. Error is: {error}")

    def add_hyperlink(self, link_address: Union[str, CDispatch], text_range: CDispatch, tips="", text_to_display="", no_under_line=True):
        """
        Add a hyperlink to Word.

        :param link_address: Internet url or a bookmark, named range, slide number.
        :type link_address:
        :param text_range: Text range of Word.
        :type text_range: CDispatch
        :param tips: Tips to be displayed.
        :type tips: str
        :param text_to_display: If ``text_to_display!=""``, its text will replace that of ``text_range``.
        :type text_to_display: str
        :param no_under_line: If removes the underline style.
        :type no_under_line: bool
        :return:
        :rtype:
        """
        self._check_context()

        kwargs = {
            "Anchor": text_range,
            "Address": "",
            "SubAddress": "",
            "ScreenTip": tips,
            "TextToDisplay": text_to_display,
        }

        if isinstance(link_address, str) and link_address.startswith("http"):
            kwargs["Address"] = link_address

        else:
            kwargs["SubAddress"] = link_address

        try:
            self.docx.Hyperlinks.Add(**kwargs)
        except pywintypes.com_error as error:
            logger.error(f"Cannot add hyperlinks: {link_address}. Error is: {error}")
            raise AddHyperlinkError(f"Cannot add hyperlinks: {link_address}. Error is: {error}")

        if no_under_line:
            text_range.Font.Underline = 0

    def set_save_path(self, save_path: str):
        """
        Set the path the Word will be saved to.

        :param save_path:
        :type save_path:
        :return:
        :rtype:
        """
        self.save_path = save_path

    def to_word(self, new_file_path: str = None):
        """
        Save the Word to a new file.

        :param new_file_path: Absolute path of the new Word document. Existed file will be renamed.
        :type new_file_path: str
        :return:
        :rtype:
        """
        if new_file_path is None:
            if self.save_path is None:
                return
            else:
                new_file_path = self.save_path

        # check the file
        if exists(new_file_path):
            file_basename = basename(new_file_path)
            dir_path = dirname(new_file_path)
            backup_file_name = file_basename.strip(".docx") + "_bak.docx"
            logger.warning(rf"Found existed output file, backup to {dir_path}\{backup_file_name}")

            try:
                move(new_file_path, rf"{dir_path}\{backup_file_name}")
                is_clear = True

            except PermissionError:
                logger.error(f"Can't rename existed file, skip saving")
                is_clear = False

        else:
            is_clear = True

        if is_clear:
            self.docx.SaveAs(new_file_path)

    def _set_hook(self, hook: HookBase, hook_type: Union[int, HOOKTYPE]):
        """
        Set function hook for Word field.

        :param hook: Hook object.
        :type hook:
        :param hook_type: Integer flag. Check ``HOOKTYPE``.
        :type hook_type: int
        :return:
        :rtype:
        """
        if hook_type == HOOKTYPE.BEFORE_ITERATE:
            self._hook_before_dict.update({hook.name: hook})
        elif hook_type == HOOKTYPE.IN_ITERATE:
            self._hook_in_dict.update({hook.name: hook})
        elif hook_type == HOOKTYPE.AFTER_ITERATE:
            self._hook_after_dict.update({hook.name: hook})
        else:
            raise HookTypeError(f"Unknown hook type: {hook_type}.")

        hook.finish_register(hook_type)

    def set_hook(self, hook: HookBase, hook_type: Union[int, HOOKTYPE] = HOOKTYPE.IN_ITERATE):
        """
        Set function hook for Word field.

        :param hook: Callback function which first parameter should accept the Word field object.
        :type hook:
        :param hook_type: Integer flag. Check ``HOOKTYPE``.
        :type hook_type: int
        :return:
        :rtype:
        """
        if hook_type == HOOKTYPE.BEFORE_ITERATE:
            _hook_dict = self._hook_before_dict

        elif hook_type == HOOKTYPE.IN_ITERATE:
            _hook_dict = self._hook_in_dict

        elif hook_type == HOOKTYPE.AFTER_ITERATE:
            _hook_dict = self._hook_after_dict

        else:
            raise HookTypeError(f"Unknown hook type: {hook_type}.")

        if hook.is_registered(hook_type):
            return

        if hook.name in _hook_dict:
            logger.warning(f"Hook {hook.name} won't be added because a hook with same name exists.")
            return

        logger.debug(f"Hook '{hook.name}' is registered for hook type '{hook_type}'.")

        self._set_hook(hook, hook_type)

    def update_hook(self, hook: HookBase, hook_type: Union[int, HOOKTYPE] = HOOKTYPE.IN_ITERATE):
        """
        Update function hook for Word field.

        :param hook: Callback function which first parameter should accept the Word field object.
        :type hook:
        :param hook_type: Integer flag. Check ``HOOKTYPE``.
        :type hook_type: int
        :return:
        :rtype:
        """
        if hook_type == HOOKTYPE.BEFORE_ITERATE:
            _hook_dict = self._hook_before_dict

        elif hook_type == HOOKTYPE.IN_ITERATE:
            _hook_dict = self._hook_in_dict

        elif hook_type == HOOKTYPE.AFTER_ITERATE:
            _hook_dict = self._hook_after_dict

        else:
            raise HookTypeError(f"Unknown hook type: {hook_type}.")

        if hook.is_registered(hook_type):
            logger.debug(f"Hook '{hook.name}' is registered for hook type '{hook_type}'.")
            return

        if hook.name not in _hook_dict:
            logger.warning(f"Hook {hook.name} doesn't exist.")
            return

        self._set_hook(hook, hook_type)

    def remove_hook(self, name: str, hook_type: Union[int, HOOKTYPE]):
        """
        Remove a hook.

        :param name: A unique name for hook.
        :type name: str
        :param hook_type: Integer flag. Check ``HOOKTYPE``.
        :type hook_type: int
        :return:
        :rtype:
        """
        if hook_type == HOOKTYPE.BEFORE_ITERATE and name in self._hook_before_dict:
            _ = self._hook_before_dict.pop(name)
        elif hook_type == HOOKTYPE.IN_ITERATE and name in self._hook_in_dict:
            _ = self._hook_in_dict.pop(name)
        elif hook_type == HOOKTYPE.AFTER_ITERATE and name in self._hook_after_dict:
            _ = self._hook_after_dict.pop(name)
        else:
            raise HookTypeError(f"Unknown hook type: {hook_type}.")

    def _before_perform(self):
        """
        Call hooks before iterations.

        :return:
        :rtype:
        """
        for name in self._hook_before_dict:
            self._hook_before_dict[name].before_iterate(self)

    def _after_perform(self):
        """
        Call hooks after iterations.

        :return:
        :rtype:
        """
        for name in self._hook_after_dict:
            self._hook_after_dict[name].after_iterate(self)

    def _perform(self):
        """
        Perform iterations.

        :return:
        :rtype:
        """
        self._before_perform()

        total = len(list(self.docx.Fields))
        with Progress() as progress:
            pid = progress.add_task(f"[red]Processing your Word...[red]", total=total)

            for field in self.docx.Fields:
                progress.advance(pid)

                for name in self._hook_in_dict:
                    self._hook_in_dict[name].on_iterate(self, field)

        self._after_perform()


__all__ = ["Word"]
