# -*- coding: utf-8 -*-
import re
from typing import Optional, Union

from rich.progress import Progress

from .csl import GetCSLJsonHook, add_get_csl_json_hook, CSLJson
from .error import AddHyperlinkError, HookNotRegisteredError, ParamsError
from .hook import ExtensionHookBase, HOOKTYPE, HookBase
from .utils import logger, find_urls, parse_color
from .word import Word
from .zotero import zotero_check_initialized, zotero_query_pages


def _find_words(text: str, words_list: list[str]):
    pattern = r"\b(?:" + "|".join(re.escape(word) for word in words_list) + r")\b"
    return re.findall(pattern, text)


def _check_extension_hook_registered(hook_name: str, hook: Union[HookBase, ExtensionHookBase]):
    if not hook.is_registered():
        logger.error(f"Hook '{hook_name}' requires `{type(hook)}` to be registered.")
        raise HookNotRegisteredError(f"Hook '{hook_name}' requires `{type(hook)}` to be registered.")


def italicize_container_publisher(paragraph_range, container_title="", publisher=""):
    """
    Italicize the container title and publisher name in bibliography text.

    :param paragraph_range: Range object of the bibliography.
    :type paragraph_range:
    :param container_title: Container title.
    :type container_title: str
    :param publisher: Publisher name.
    :type publisher: str
    :return:
    :rtype:
    """
    bib_text = paragraph_range.Text
    if container_title != "":
        split_paragraph = bib_text.split(container_title)
        pre_paragraph, post_paragraph = split_paragraph[0], split_paragraph[1]
        paragraph_range.MoveStart(Unit=1, Count=len(pre_paragraph))
        paragraph_range.MoveEnd(Unit=1, Count=-len(post_paragraph))
        paragraph_range.Font.Italic = True
        paragraph_range.MoveStart(Unit=1, Count=-len(pre_paragraph))
        paragraph_range.MoveEnd(Unit=1, Count=len(post_paragraph))

    if publisher != "":
        split_paragraph = bib_text.split(publisher)
        pre_paragraph, post_paragraph = split_paragraph[0], split_paragraph[1]
        paragraph_range.MoveStart(Unit=1, Count=len(pre_paragraph))
        paragraph_range.MoveEnd(Unit=1, Count=-len(post_paragraph))
        paragraph_range.Font.Italic = True
        paragraph_range.MoveStart(Unit=1, Count=-len(pre_paragraph))
        paragraph_range.MoveEnd(Unit=1, Count=len(post_paragraph))


class BibLoopHook(HookBase):
    """
    This hook loops each paragraph in bibliography, and calls extension hook in each iteration.
    Extension hook is a type of hook to process paragraphs in bibliography.
    See ``noterools.hook.ExtensionHookBase``.
    """

    def __init__(self):
        if self._hook_initialized:
            return

        super().__init__(name="BibLoopHook")
        self._hook_dict: dict[str, ExtensionHookBase] = {}
        self._low_priority_hook_dict: dict[str, ExtensionHookBase] = {}
        self._fields_list = []

    def set_hook(self, hook: ExtensionHookBase, low_priority=False):
        """
        Set extension hook.
        Only accept HOOKTYPE.IN_ITERATE type.

        :param hook: ExtensionHookBase type hook.
        :type hook: ExtensionHookBase
        :param low_priority: If True, call this hook after other hooks.
        :type low_priority: bool
        :return:
        :rtype:
        """
        if hook.is_registered():
            return

        if low_priority:
            if hook.name in self._low_priority_hook_dict:
                logger.warning(f"Hook {hook.name} won't be added because a hook with same name exists.")
                return
            self._low_priority_hook_dict.update({hook.name: hook})

        else:
            if hook.name in self._hook_dict:
                logger.warning(f"Hook {hook.name} won't be added because a hook with same name exists.")
                return
            self._hook_dict.update({hook.name: hook})

        hook.finish_register()

    def update_hook(self, hook: ExtensionHookBase):
        """
        Update specific child hook.
        Only accept HOOKTYPE.IN_ITERATE type.

        :param hook: ExtensionHookBase type hook.
        :type hook: ExtensionHookBase
        :return:
        :rtype:
        """
        if hook.is_registered():
            return

        if hook.name in self._hook_dict:
            self._hook_dict.update({hook.name: hook})

        elif hook.name in self._low_priority_hook_dict:
            self._low_priority_hook_dict.update({hook.name: hook})

        else:
            logger.warning(f"Hook {hook.name} doesn't exist.")
            return

        hook.finish_register()

    def remove_hook(self, name: str):
        """
        Remove a hook.

        :param name: Hook's name.
        :type name: str
        :return:
        :rtype:
        """
        if name in self._hook_dict:
            self._hook_dict.pop(name)

        if name in self._low_priority_hook_dict:
            self._low_priority_hook_dict.pop(name)

    def on_iterate(self, word, field):
        if "ADDIN ZOTERO_BIBL" in field.Code.Text:
            self._fields_list.append(field)

    def after_iterate(self, word: Word):
        if len(self._fields_list) == 0:
            logger.warning(f"Zotero's bibliography not found in your file. Generate bibliography in your file, and DO NOT unlink it.")
            return

        elif len(self._fields_list) > 1:
            logger.warning(f"Found multiple bibliography in your file, this is weird.")

        for field in self._fields_list:

            # find ZOTERO field.
            if "ADDIN ZOTERO_BIBL" not in field.Code.Text:
                logger.debug(f"Exclude field that is not Zotero bibliography: {field.Code.Text}")
                continue

            field_res_range = field.Result

            # used for numbered citation
            total = len(list(field_res_range.Paragraphs))

            with Progress() as progress:
                pid = progress.add_task(f"[red]Processing your bibliography..[red]", total=total)

                for _paragraph in field_res_range.Paragraphs:
                    progress.advance(pid, advance=1)

                    for _hook_name in self._hook_dict:
                        logger.debug(f"Call hook: {_hook_name}")
                        self._hook_dict[_hook_name].on_iterate(word, _paragraph.Range)

                    for _hook_name in self._low_priority_hook_dict:
                        logger.debug(f"Call hook: {_hook_name}")
                        self._low_priority_hook_dict[_hook_name].on_iterate(word, _paragraph.Range)


def add_bib_loop_hook(word: Word) -> BibLoopHook:
    """
    Register ``BibLoopHook``.

    :param word: ``noterools.word.Word`` object.
    :type word: Word
    :return: ``BibLoopHook`` instance.
    :rtype: BibLoopHook
    """
    bib_loop_hook = BibLoopHook()
    word.set_hook(bib_loop_hook, HOOKTYPE.IN_ITERATE)
    word.set_hook(bib_loop_hook, HOOKTYPE.AFTER_ITERATE)

    return bib_loop_hook


class BibPairCitationBibHook(ExtensionHookBase):
    def __init__(self):
        """
        This extension hook trys to pair bibliography and CSL JSON, so other extension hooks can get corresponding article information of bibliography.
        """
        super().__init__(name="BibPairCitationBibHook")
        self._get_cls_json_hook = GetCSLJsonHook()
        self._paired_dict: dict[str, CSLJson] = {}
        self.hyphen = "-"
        self.en_dash = "–"

        _check_extension_hook_registered(self.name, self._get_cls_json_hook)

    def get_csl_json(self, bib_text: str) -> Optional[CSLJson]:
        """
        Get the corresponding CSLJson object of the bibliography.

        :param bib_text: Bibliography text.
        :type bib_text: str
        :return: CSLJson object.
        :rtype: CSLJson
        """
        # replace all en-dashes to hyphen to make sure we can find the CSLJson even after update dash symbols.
        bib_text_new = bib_text.replace(self.en_dash, self.hyphen)

        if bib_text_new in self._paired_dict:
            return self._paired_dict[bib_text_new]

        for _item_id, _csl_json in self._get_cls_json_hook.csl_json_dict.items():
            _title = _csl_json.get_title()
            _container_title = _csl_json.get_container_title()
            _language = _csl_json.get_language(defaults="cn")
            _author = _csl_json.get_author_names(_language)[0]
            _publisher = _csl_json.get_publisher()

            # we have to check following things to make sure this is the article we find for bibliography
            # 1. bib text contains article's title.
            # 2. bib text contains article's container title (container title will be `""` if your Zotero doesn't have information about it).
            # 3. bib text contains the first author's name.
            # 4. article's title must match the title in bib text perfectly.
            if _title in bib_text and _container_title in bib_text and _author in bib_text and f"{_title} " not in bib_text:
                self._paired_dict[bib_text_new] = _csl_json
                self._get_cls_json_hook.csl_json_dict.pop(_item_id)
                return _csl_json

        logger.warning(f"Can't find the corresponding citation of bib: {bib_text}, do you really cite it?")

        return None

    def on_iterate(self, word, word_range):
        bib_text = word_range.Text
        _ = self.get_csl_json(bib_text)


def add_bib_pair_citation_bib_hook(word: Word) -> BibPairCitationBibHook:
    """
    Register ``BibPairCitationBibHook``.

    :param word: ``noterools.word.Word`` object.
    :type word: Word
    :return: ``BibPairCitationBibHook`` instance.
    :rtype: BibPairCitationBibHook
    """
    add_get_csl_json_hook(word)
    bib_pair_citation_bib_hook = BibPairCitationBibHook()
    bib_loop_hook = add_bib_loop_hook(word)
    bib_loop_hook.set_hook(bib_pair_citation_bib_hook)

    return bib_pair_citation_bib_hook


class BibBookmarkHook(ExtensionHookBase):
    def __init__(self, is_numbered=False, set_container_title_italic=True):
        """
        This extension hook can add bookmark to your bibliography so you can create hyperlinks from citations to bibliography.

        :param is_numbered: If your citation is numbered. Defaults to False.
        :type is_numbered: bool
        :param set_container_title_italic: If italicize the container title and publisher name in bibliography. Defaults to True.
        :type set_container_title_italic: bool
        """
        super().__init__(name="BibBookmarkHook")
        self.is_numbered = is_numbered
        self.set_container_title_italic = set_container_title_italic
        self._fields_list = []
        self._get_cls_json_hook = GetCSLJsonHook()
        # self._bib_pair_citation_bib_hook = BibPairCitationBibHook()

        _check_extension_hook_registered(self.name, self._get_cls_json_hook)

        # used to generate bookmark for numbered citation
        self._number_count = 1

        # used to match the citation with bibliography.
        self._item_info_list: Optional[list[tuple[str, str, str, str, str, str]]] = None
        
    def _get_bookmark_id_and_item_info(self, bib_text: str) -> tuple[str, tuple[str, str, str, str]]:
        """
        Get bookmark id and information about the article.

        :param bib_text: Text of the bibliography.
        :type bib_text: str
        :return: (bookmark_id, (title, container_title, publisher, language))
        :rtype: tuple
        """
        if self._item_info_list is None:
            csl_json_dict = self._get_cls_json_hook.get_csl_jsons()
            # [("title", "container title", "first author name", "publisher", "language", "item id"), ...]
            self._item_info_list = [
                (
                    csl_json.get_title(), csl_json.get_container_title(), csl_json.get_author_names(language=csl_json.get_language(defaults="cn"))[0],
                    csl_json.get_publisher(), csl_json.get_language(defaults="cn"), item_id
                ) for item_id, csl_json in csl_json_dict.items()
            ]

        bib_title = ""
        bib_container_title = ""
        bib_publisher = ""
        bib_language = ""
        bib_item_id = ""

        for index, _tuple in enumerate(self._item_info_list):
            _title, _container_title, _author, _publisher, _language, _item_id = _tuple

            # we have to check following things to make sure this is the article we find for bibliography
            # 1. bib text contains article's title.
            # 2. bib text contains article's container title (container title will be `""` if your Zotero doesn't have information about it).
            # 3. bib text contains the first author's name.
            # 4. article's title must match the title in bib text perfectly.
            if _title in bib_text and _container_title in bib_text and _author in bib_text and f"{_title} " not in bib_text:
                bib_title = _title
                bib_container_title = _container_title
                bib_publisher = _publisher
                bib_language = _language
                bib_item_id = _item_id
                self._item_info_list.pop(index)
                break

        article_info = (bib_title, bib_container_title, bib_publisher, bib_language)

        if self.is_numbered:
            bookmark_id = f"Ref_{self._number_count}"
            self._number_count += 1

        else:
            # item id is unique in Zotero
            bookmark_id = f"Ref_{bib_item_id}"

        return bookmark_id, article_info

    def on_iterate(self, word: Word, word_range):
        bib_text = word_range.Text
        bookmark_id, (bib_title, bib_container_title, bib_publisher, bib_language) = self._get_bookmark_id_and_item_info(bib_text)

        if not self.is_numbered and bib_title == "":
            logger.warning(f"Can't find the corresponding citation of bib: {bib_text}, do you really cite it?")
            return

        # csl_json = self._bib_pair_citation_bib_hook.get_csl_json(bib_text)

        # if csl_json is None:
        #     # no csl json found, skip
        #     return
        
        # bib_item_id = csl_json.item_id
        # bib_container_title = csl_json.get_container_title()
        # bib_publisher = csl_json.get_publisher()
        # bib_language = csl_json.get_language(defaults="cn")
        
        # if self.is_numbered:
        #     bookmark_id = f"Ref_{self._number_count}"
        #     self._number_count += 1
        #
        # else:
        #     # item id is unique in Zotero
        #     bookmark_id = f"Ref_{bib_item_id}"

        # set italic for Chinese container title
        if self.set_container_title_italic and "cn" in bib_language:
            italicize_container_publisher(word_range, bib_container_title, bib_publisher)

        word_range.MoveEnd(1, -1)
        word.add_bookmark(bookmark_id, word_range)


def add_bib_bookmark_hook(word: Word, is_numbered=False, set_container_title_italic=True) -> BibBookmarkHook:
    """
    Register ``BibBookmarkHook``.

    :param word: ``noterools.word.Word`` object.
    :type word: Word
    :param is_numbered: If your citation is numbered. Defaults to False.
    :type is_numbered: bool
    :param set_container_title_italic: If italicize the container title and publisher name in bibliography. Defaults to True.
    :type set_container_title_italic: bool
    :return: ``BibBookmarkHook`` instance.
    :rtype: BibBookmarkHook
    """
    # add_bib_pair_citation_bib_hook(word)
    add_get_csl_json_hook(word)
    bib_bookmark_hook = BibBookmarkHook(is_numbered, set_container_title_italic)
    bib_loop_hook = add_bib_loop_hook(word)
    bib_loop_hook.set_hook(bib_bookmark_hook)

    return bib_bookmark_hook


class BibUpdateDashSymbolHook(ExtensionHookBase):
    def __init__(self, font_family="Times New Roman"):
        """
        This hook will replace the dash symbol between page numbers in your bibliography with the right one.

        The default dash symbol between page numbers in the bibliography generated by Zotero is ``-`` (which Unicode is ``002D`` in Times New Roman).
        This hook will replace the dash symbol with ``–``, which Unicode is ``2013``.

        :param font_family: The font you use. Defaults to ``Times New Roman``.
        :type font_family: 
        """
        super().__init__("BibUpdateDashSymbolHook")
        zotero_check_initialized("BibUpdateDashSymbolHook")

        self.font_family = font_family
        self._fields_list = []
        self._get_cls_json_hook = GetCSLJsonHook()
        # self._bib_pair_citation_bib_hook = BibPairCitationBibHook()
        self.hyphen = "-"
        self.en_dash = "–"

        # we need ``GetCSLJsonHook`` to be registered.
        _check_extension_hook_registered(self.name, self._get_cls_json_hook)

        # used to match the citation with bibliography.
        self._item_info_list: Optional[list[tuple[str, str, str, str, str, str]]] = None

    def _get_item_id(self, bib_text: str) -> str:
        """
        Get item id of the article.

        :param bib_text: Text of the bibliography.
        :type bib_text: str
        :return: Item ID.
        :rtype: str
        """
        if self._item_info_list is None:
            csl_json_dict = self._get_cls_json_hook.get_csl_jsons()
            # [("title", "container title", "first author name", "publisher", "language", "item id"), ...]
            self._item_info_list = [
                (
                    csl_json.get_title(), csl_json.get_container_title(), csl_json.get_author_names(language=csl_json.get_language(defaults="cn"))[0],
                    csl_json.get_publisher(), csl_json.get_language(defaults="cn"), item_id
                ) for item_id, csl_json in csl_json_dict.items()
            ]

        item_id = ""

        for index, _tuple in enumerate(self._item_info_list):
            _title, _container_title, _author, _publisher, _language, _item_id = _tuple

            # we have to check following things to make sure this is the article we find for bibliography
            # 1. bib text contains article's title.
            # 2. bib text contains article's container title (container title will be `""` if your Zotero doesn't have information about it).
            # 3. bib text contains the first author's name.
            # 4. article's title must match the title in bib text perfectly.
            if _title in bib_text and _container_title in bib_text and _author in bib_text and f"{_title} " not in bib_text:
                item_id = _item_id
                self._item_info_list.pop(index)
                break

        return item_id

    def on_iterate(self, word: Word, word_range):
        _bib_text: str = word_range.Text
        item_id = self._get_item_id(_bib_text)
        page_num_section_text = zotero_query_pages(item_id)

        # csl_json = self._bib_pair_citation_bib_hook.get_csl_json(_bib_text)
        #
        # if csl_json is None:
        #     return
        #
        # item_id = csl_json.item_id
        # page_num_section_text = zotero_query_pages(item_id)

        if page_num_section_text == "":
            return

        if self.hyphen not in page_num_section_text and page_num_section_text in _bib_text:
            return

        # need extra check, sometimes we got en_dash from Zotero but hyphen in bib text.
        if self.en_dash in page_num_section_text:
            page_num_section_text = page_num_section_text.replace(self.en_dash, self.hyphen)

        if page_num_section_text not in _bib_text:
            return

        logger.debug(f"Page num is: '{page_num_section_text}'")

        _bib_text_list = _bib_text.split(page_num_section_text)

        if len(_bib_text_list) != 2:
            logger.warning(f"Bibliography should have only one page number section, something is wrong, skip the paragraph: {_bib_text}")
            return

        pre_paragraph, post_paragraph = _bib_text_list

        word_range.MoveStart(Unit=1, Count=len(pre_paragraph))
        word_range.MoveEnd(Unit=1, Count=-len(post_paragraph))
        word_range.Text = page_num_section_text.replace("-", "–")
        word_range.Font.Name = self.font_family


def add_update_dash_symbol_hook(word: Word, font_family="Times New Roman") -> BibUpdateDashSymbolHook:
    """
    Register ``BibUpdateDashSymbolHook``.

    :param word: ``noterools.word.Word`` object.
    :type word: Word
    :param font_family: The font family you use. Default is "Times New Roman".
    :type font_family: str
    :return: ``BibUpdateDashSymbolHook`` instance.
    :rtype: BibUpdateDashSymbolHook
    """
    # add_bib_pair_citation_bib_hook(word)
    add_get_csl_json_hook(word)
    bib_update_dash_symbol_hook = BibUpdateDashSymbolHook(font_family)
    bib_loop_hook = add_bib_loop_hook(word)
    bib_loop_hook.set_hook(bib_update_dash_symbol_hook, low_priority=True)

    return bib_update_dash_symbol_hook


class BibFormatTitleHook(ExtensionHookBase):
    def __init__(self, upper_first_char=False, upper_all_words=False, lower_all_words=False, word_list: list[str] = None):
        """
        This hook will format the article title with three rules: upper_all, upper_first_character, and lower_all.

        :param upper_first_char: Upper the first character of each word. Defaults to False.
        :type upper_first_char: bool
        :param upper_all_words: Upper all words. Defaults to False.
        :type upper_all_words: bool
        :param lower_all_words: Lower characters except the first in all words. Words or phrases in ``word_dict`` will not be changed. Defaults to False.
        :type lower_all_words: bool
        :param word_list: A list contains words or phrases which format will not be changed.
        :type word_list: list
        """
        super().__init__("BibFormatTitleHook")
        self._get_cls_json_hook = GetCSLJsonHook()
        # self._bib_pair_citation_bib_hook = BibPairCitationBibHook()

        # we need ``GetCSLJsonHook`` to be registered.
        _check_extension_hook_registered(self.name, self._get_cls_json_hook)

        # used to match the citation with bibliography.
        self._item_info_list: Optional[list[tuple[str, str, str, str, str, str]]] = None
        
        if upper_all_words + upper_first_char + lower_all_words >= 2:
            logger.error(f"You must chose only one format rule for article's title.")
            raise ParamsError(f"You must chose only one format rule for article's title.")

        if lower_all_words and word_list is None:
            logger.error("To prevent proper noun to be lower, you must give your word dictionary contains roper noun.")
            raise ParamsError("To prevent proper noun to be lower, you must give your word dictionary contains roper noun.")

        self.upper_first_char = upper_first_char
        self.upper_all_words = upper_all_words
        self.lower_all_words = lower_all_words

        # remove empty strings
        word_list = [x for x in word_list if x != ""]
        self.word_list = word_list

        logger.warning("Change the capitalization of article title is an experimental feature and may make mistakes.")
        logger.warning("Use it carefully.")
        
    def _get_title(self, bib_text: str) -> tuple[str, str]:
        """
        Get the title and language of a bibliography.

        :param bib_text: Text of the bibliography.
        :type bib_text: str
        :return: (title, language)
        :rtype: tuple
        """
        if self._item_info_list is None:
            csl_json_dict = self._get_cls_json_hook.get_csl_jsons()
            # [("title", "container title", "first author name", "publisher", "language", "item id"), ...]
            self._item_info_list = [
                (
                    csl_json.get_title(), csl_json.get_container_title(), csl_json.get_author_names(language=csl_json.get_language(defaults="cn"))[0],
                    csl_json.get_publisher(), csl_json.get_language(defaults="cn"), item_id
                ) for item_id, csl_json in csl_json_dict.items()
            ]

        bib_title = ""
        bib_language = ""

        for index, _tuple in enumerate(self._item_info_list):
            _title, _container_title, _author, _publisher, _language, _item_id = _tuple

            # we have to check following things to make sure this is the article we find for bibliography
            # 1. bib text contains article's title.
            # 2. bib text contains article's container title (container title will be `""` if your Zotero doesn't have information about it).
            # 3. bib text contains the first author's name.
            # 4. article's title must match the title in bib text perfectly.
            if _title in bib_text and _container_title in bib_text and _author in bib_text and f"{_title} " not in bib_text:
                bib_title = _title
                bib_language = _language
                self._item_info_list.pop(index)
                break

        return bib_title, bib_language

    def on_iterate(self, word: Word, word_range):
        bib_text = word_range.Text
        bib_title, bib_language = self._get_title(bib_text)

        # csl_json = self._bib_pair_citation_bib_hook.get_csl_json(bib_text)
        #
        # if csl_json is None:
        #     return
        #
        # bib_language = csl_json.get_language(defaults="cn")
        # bib_title = csl_json.get_title()

        if bib_title != "" and bib_language == "en":
            if self.upper_all_words:
                split_paragraph = bib_text.split(bib_title)
                new_bib_title = bib_title.upper()

                pre_paragraph, post_paragraph = split_paragraph[0], split_paragraph[1]
                word_range.MoveStart(Unit=1, Count=len(pre_paragraph))
                word_range.MoveEnd(Unit=1, Count=-len(post_paragraph))
                word_range.Text = new_bib_title
                word_range.MoveStart(Unit=1, Count=-len(pre_paragraph))
                word_range.MoveEnd(Unit=1, Count=len(post_paragraph))

            elif self.upper_first_char:
                split_paragraph = bib_text.split(bib_title)
                new_bib_title = bib_title.split(" ")
                for index, _word in enumerate(new_bib_title):
                    _word = f"{_word[0].upper()}{_word[1:]}"
                    new_bib_title[index] = _word
                new_bib_title = " ".join(new_bib_title)

                pre_paragraph, post_paragraph = split_paragraph[0], split_paragraph[1]
                word_range.MoveStart(Unit=1, Count=len(pre_paragraph))
                word_range.MoveEnd(Unit=1, Count=-len(post_paragraph))
                word_range.Text = new_bib_title
                word_range.MoveStart(Unit=1, Count=-len(pre_paragraph))
                word_range.MoveEnd(Unit=1, Count=len(post_paragraph))

            elif self.lower_all_words:
                res = _find_words(bib_text, self.word_list)
                res = [x for x in res if x != ""]

                if len(res) == 0:
                    new_bib_title = bib_title.split(" ")
                    for index, _word in enumerate(new_bib_title):
                        if index == 0:
                            _word = f"{_word[0].upper()}{_word[1:].lower()}"
                            new_bib_title[index] = _word
                        else:
                            if new_bib_title[index - 1].startswith((":", ".", "?")):
                                _word = f"{_word[0].upper()}{_word[1:].lower()}"
                                new_bib_title[index] = _word
                            else:
                                new_bib_title[index] = _word.lower()

                    new_bib_title = " ".join(new_bib_title)

                else:
                    logger.debug(f"Find proper nouns in title: {res}")
                    new_bib_title = bib_title.split(" ")
                    for index, _word in enumerate(new_bib_title):
                        if index == 0:
                            _word = f"{_word[0].upper()}{_word[1:].lower()}"
                            new_bib_title[index] = _word
                        else:
                            if new_bib_title[index - 1].endswith((":", ".", "?")):
                                _word = f"{_word[0].upper()}{_word[1:].lower()}"
                                new_bib_title[index] = _word
                            else:
                                new_bib_title[index] = _word.lower()

                    new_bib_title = " ".join(new_bib_title)

                    for proper_noun in res:
                        if proper_noun.lower() in new_bib_title:
                            logger.debug(f"Find proper noun {proper_noun} in title: {new_bib_title}")
                            new_bib_title = new_bib_title.replace(proper_noun.lower(), proper_noun)

                        else:
                            proper_noun_lower = proper_noun.lower()
                            proper_noun_lower = f"{proper_noun_lower[0].upper()}{proper_noun_lower[1:]}"

                            if proper_noun_lower in new_bib_title:
                                logger.debug(f"Find proper noun {proper_noun} in title: {new_bib_title}")
                                new_bib_title = new_bib_title.replace(proper_noun_lower, proper_noun)

                            else:
                                logger.warning(f"Can't find proper noun '{proper_noun}' in title: {new_bib_title}")

                split_paragraph = bib_text.split(bib_title)
                logger.debug(f"Update title '{bib_title}' to '{new_bib_title}'")
                pre_paragraph, post_paragraph = split_paragraph[0], split_paragraph[1]
                word_range.MoveStart(Unit=1, Count=len(pre_paragraph))
                word_range.MoveEnd(Unit=1, Count=-len(post_paragraph))
                word_range.Text = new_bib_title
                word_range.MoveStart(Unit=1, Count=-len(pre_paragraph))
                word_range.MoveEnd(Unit=1, Count=len(post_paragraph))


def add_format_title_hook(word: Word, upper_first_char=False, upper_all_words=False, lower_all_words=False, word_list: list[str] = None) -> BibFormatTitleHook:
    """
    Register ``BibFormatTitleHook``.

    :param word: ``noterools.word.Word`` object.
    :type word: Word
    :param upper_first_char: Upper the first character of each word. Defaults to False.
    :type upper_first_char: bool
    :param upper_all_words: Upper all words. Defaults to False.
    :type upper_all_words: bool
    :param lower_all_words: Lower characters except the first in all words. Words or phrases in ``word_dict`` will not be changed. Defaults to False.
    :type lower_all_words: bool
    :param word_list: A list contains words or phrases which format will not be changed.
    :type word_list: list
    :return: ``BibFormatTitleHook`` instance.
    :rtype: BibFormatTitleHook
    """
    # add_bib_pair_citation_bib_hook(word)
    add_get_csl_json_hook(word)
    bib_format_title_hook = BibFormatTitleHook(upper_first_char, upper_all_words, lower_all_words, word_list)
    bib_loop_hook = add_bib_loop_hook(word)
    bib_loop_hook.set_hook(bib_format_title_hook, low_priority=True)

    return bib_format_title_hook


class BibURLHyperlinkHook(ExtensionHookBase):
    """
    This extension hook adds hyperlinks to URLs in your bibliography.
    """
    
    def __init__(self, color=None, no_under_line=False):
        """
        Initialize the URL hyperlink hook.

        :param color: Set font color for URLs. Accepts integer decimal value (e.g., 16711680 for blue), 
                     RGB string (e.g., "255, 0, 0" for red), or "word_auto" for automatic color.
                     Defaults to None (keep original color).
        :type color: Union[int, str, None]
        :param no_under_line: If remove the underline of hyperlinks. Defaults to False.
        :type no_under_line: bool
        """
        super().__init__(name="BibURLHyperlinkHook")
        self.color = parse_color(color)  # Use parse_color
        self.no_under_line = no_under_line

    def on_iterate(self, word: Word, word_range):
        """
        Process each bibliography entry to find and hyperlink URLs.

        :param word: Word object.
        :type word: Word
        :param word_range: Range object of the bibliography entry.
        :type word_range: object
        """
        bib_text = word_range.Text      # type: ignore
        
        # Find URLs in the bibliography text
        url_positions = find_urls(bib_text)
        
        if not url_positions:
            return
            
        logger.debug(f"Found {len(url_positions)} URLs in bibliography entry")
        
        # Process URLs in reverse order to maintain position integrity
        for start_pos, end_pos, url in reversed(url_positions):
            # Create a duplicate range for the URL
            url_range = word_range.Duplicate    # type: ignore
            
            # Move start and end positions to isolate just the URL text
            url_range.MoveStart(Unit=1, Count=start_pos)
            url_range.MoveEnd(Unit=1, Count=-(len(bib_text) - end_pos))
            
            try:
                # Add hyperlink to the URL
                word.add_hyperlink(url, url_range, no_under_line=self.no_under_line)
                
                # Set color if specified (after adding hyperlink)
                if self.color is not None:
                    url_range.Font.Color = self.color
                    
                logger.debug(f"Added hyperlink for URL: {url}")
                
            except AddHyperlinkError:
                logger.warning(f"Failed to add hyperlink for URL: {url}")


def add_url_hyperlink_hook(word: Word, color=None, no_under_line=False) -> BibURLHyperlinkHook:
    """
    Register ``BibURLHyperlinkHook`` to add hyperlinks to URLs in bibliography.

    :param word: ``noterools.word.Word`` object.
    :type word: Word
    :param color: Set font color for URLs. Accepts integer decimal value (e.g., 16711680 for blue), 
                 RGB string (e.g., "255, 0, 0" for red), or "word_auto" for automatic color.
                 Defaults to None (keep original color).
    :type color: Union[int, str, None]
    :param no_under_line: If remove the underline of hyperlinks. Defaults to False.
    :type no_under_line: bool
    :return: ``BibURLHyperlinkHook`` instance.
    :rtype: BibURLHyperlinkHook
    """
    add_get_csl_json_hook(word)
    url_hyperlink_hook = BibURLHyperlinkHook(color, no_under_line)
    bib_loop_hook = add_bib_loop_hook(word)
    bib_loop_hook.set_hook(url_hyperlink_hook)
    
    return url_hyperlink_hook


__all__ = ["BibLoopHook", "BibBookmarkHook", "BibUpdateDashSymbolHook", "BibFormatTitleHook", 
           "BibURLHyperlinkHook", "add_bib_loop_hook", "add_bib_bookmark_hook", 
           "add_update_dash_symbol_hook", "add_format_title_hook", "add_url_hyperlink_hook"]
