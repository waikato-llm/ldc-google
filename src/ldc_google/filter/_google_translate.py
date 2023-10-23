import argparse
import copy
from google.cloud import translate
from typing import List

from ldc.core import LOGGING_WARN, DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION
from ldc.core import LOCATION_ANY, LOCATION_INSTRUCTION, LOCATION_INPUT, LOCATION_OUTPUT, LOCATION_CONTENT, \
    LOCATIONS, LOCATIONS_PAIRS, LOCATIONS_PRETRAIN
from ldc.filter import Filter
from ldc.pretrain import PretrainData
from ldc.supervised.pairs import PairData
from ldc.translation import TranslationData


class GoogleTranslate(Filter):
    """
    Translates text using Google's Translate API.

    https://cloud.google.com/translate/docs/reference/libraries/v3/python
    https://cloud.google.com/translate/docs/advanced/translating-text-v3#translating_text
    # use local dev credentials
    https://cloud.google.com/docs/authentication/provide-credentials-adc#local-dev
    # enable quota project
    https://cloud.google.com/docs/authentication/troubleshoot-adc#user-creds-client-based
    """

    def __init__(self, project_id: str = None, source_lang: str = None, target_lang: str = None,
                 location: str = LOCATION_ANY, logger_name: str = None, logging_level: str = LOGGING_WARN):
        """
        Initializes the filter. Either encoding or model need to be provided.

        :param project_id: the name/ID of the Google Cloud project
        :type project_id: str
        :param source_lang: the language of the text to be translated
        :type source_lang: str
        :param target_lang: the language to translate the text into
        :type target_lang: str
        :param location: which part of the data to count the tokens
        :type location: str
        :param logger_name: the name to use for the logger
        :type logger_name: str
        :param logging_level: the logging level to use
        :type logging_level: str
        """
        super().__init__(logger_name=logger_name, logging_level=logging_level)

        if location not in LOCATIONS:
            raise Exception("Invalid location: %s" % location)

        self.project_id = project_id
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.location = location
        self._client = None
        self._count = 0

    def name(self) -> str:
        """
        Returns the name of the handler, used as sub-command.

        :return: the name
        :rtype: str
        """
        return "google-translate"

    def description(self) -> str:
        """
        Returns a description of the reader.

        :return: the description
        :rtype: str
        """
        return "Translates text using Google's Translate API. The 'project_id' refers to your project ID in the "\
               "Google Cloud console (http://console.cloud.google.com/). "\
               "The Google Translate API must be enabled. "\
               "Requires local dev credentials: https://cloud.google.com/docs/authentication/provide-credentials-adc#local-dev"

    def domains(self) -> List[str]:
        """
        Returns the domains of the filter.

        :return: the domains
        :rtype: list
        """
        return [DOMAIN_PAIRS, DOMAIN_PRETRAIN, DOMAIN_TRANSLATION]

    def accepts(self) -> List:
        """
        Returns the list of classes that are accepted.

        :return: the list of classes
        :rtype: list
        """
        return [PairData, PretrainData, TranslationData]

    def generates(self) -> List:
        """
        Returns the list of classes that get produced.

        :return: the list of classes
        :rtype: list
        """
        return [PairData, PretrainData, TranslationData]

    def _create_argparser(self) -> argparse.ArgumentParser:
        """
        Creates an argument parser. Derived classes need to fill in the options.

        :return: the parser
        :rtype: argparse.ArgumentParser
        """
        parser = super()._create_argparser()
        parser.add_argument("-p", "--project_id", type=str, default=None, help="The name/ID of the Google Cloud project to use.", required=False)
        parser.add_argument("-s", "--source_lang", type=str, default=None, help="The language the incoming text is in.", required=False)
        parser.add_argument("-t", "--target_lang", type=str, default=None, help="The language to translate the text into.", required=False)
        parser.add_argument("-L", "--location", choices=LOCATIONS, default=LOCATION_ANY, help="Which data use for counting tokens; pairs: " + ",".join(LOCATIONS_PAIRS) + ", pretrain: " + ",".join(LOCATIONS_PRETRAIN) + ", translation: " + ",".join(LOCATIONS_PRETRAIN))
        return parser

    def _apply_args(self, ns: argparse.Namespace):
        """
        Initializes the object with the arguments of the parsed namespace.

        :param ns: the parsed arguments
        :type ns: argparse.Namespace
        """
        super()._apply_args(ns)
        self.project_id = ns.project_id
        self.source_lang = ns.source_lang
        self.target_lang = ns.target_lang
        self.location = ns.location

    def initialize(self):
        """
        Initializes the processing, e.g., for opening files or databases.
        """
        super().initialize()
        
        if self.project_id is None:
            raise Exception("No Google Cloud project ID provided!")

        if self.source_lang is None:
            raise Exception("Language for the incoming text not provided!")

        if self.target_lang is None:
            raise Exception("No language specified in which to translate!")

        self._client = translate.TranslationServiceClient()

    def _translate(self, s: str) -> str:
        """
        Translates the text.
        
        :param s: the text to translate
        :type s: str
        :return: the translated text
        :rtype: str
        """
        # skip empty text
        if len(s.strip()) == 0:
            return s

        self._count += len(s)
        location = "global"
        parent = f"projects/{self.project_id}/locations/{location}"
        response = self._client.translate_text(
            request={
                "parent": parent,
                "contents": [s],
                "mime_type": "text/plain",
                "source_language_code": self.source_lang,
                "target_language_code": self.target_lang,
            }
        )
        result = s
        for translation in response.translations:
            result = translation.translated_text
            break

        self.logger().debug("%s -> %s" % (s, result))

        return result

    def _do_process(self, data):
        """
        Processes the data record.

        :param data: the record to process
        :return: the potentially updated record or None if to drop
        """
        result = copy.deepcopy(data)

        if isinstance(result, PairData):
            if self.location in [LOCATION_INSTRUCTION, LOCATION_ANY]:
                result.instruction = self._translate(result.instruction)
            if self.location in [LOCATION_INPUT, LOCATION_ANY]:
                result.input = self._translate(result.input)
            if self.location in [LOCATION_OUTPUT, LOCATION_ANY]:
                result.output = self._translate(result.output)
        elif isinstance(result, PretrainData):
            if self.location in [LOCATION_CONTENT, LOCATION_ANY]:
                result.content = self._translate(result.content)
        elif isinstance(result, TranslationData):
            if self.source_lang in result.translations:
                result.translations[self.target_lang] = self._translate(result.translations[self.source_lang])
        else:
            raise Exception("Unhandled data type: %s" % str(type(result)))

        return result

    def finalize(self):
        """
        Finishes the processing, e.g., for closing files or databases.
        """
        super().finalize()
        self.logger().info("# characters: %d" % self._count)
