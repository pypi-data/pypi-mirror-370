#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#------------------------#
# Import project modules #
#------------------------#

from filewise.general.introspection_utils import get_caller_args
from pygenutils.arrays_and_lists.data_manipulation import flatten_list
from pygenutils.operative_systems.os_operations import run_system_command
from pygenutils.strings.string_handler import find_substring_index
from pygenutils.strings.text_formatters import print_format_string

#------------------#
# Define functions #
#------------------#

def get_googletrans_version() -> str:
    comm_conda_list_package = "conda list | grep googletrans"
    result = run_system_command(comm_conda_list_package, 
                                module="os", 
                                _class="popen", 
                                capture_output=True)
    str_conda_list_package = result["stdout"]
    
    googletrans_version = find_substring_index(str_conda_list_package,
                                               r"[0-9.]+",
                                               return_match_index=False,
                                               return_match_str=True,
                                               advanced_search=True)
    return googletrans_version
    

def translate_string(phrase_or_words: str | list[str], lang_origin: str, lang_translation: str = "en", 
                     procedure: str = "translate",
                     text_which_language_to_detect: str | None = None,
                     service_urls: str | list[str] | None = None,
                     user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                     proxies: dict | None = None,
                     timeout: int | float | None = None,
                     provider: str | None = None,
                     secret_access_key: str | None = None,
                     region: str | None = None,
                     print_attributes: bool = False):
    
    
    # Proper argument selection control #
    #-----------------------------------#
    
    param_keys = get_caller_args()
    meth_list_arg_pos = find_substring_index(param_keys, "action_list")
    
    if procedure not in ACTION_LIST:
        raise ValueError("Invalid processing procedure "
                         f"(argument '{param_keys[meth_list_arg_pos]}').\n"
                         f"Options are {ACTION_LIST}.")
    
    # Defensive programming: handle nested lists in phrase_or_words #
    #--------------------------------------------------------------#
    
    if isinstance(phrase_or_words, list):
        phrase_or_words = flatten_list(phrase_or_words)
        
    
    # Operation part #
    #----------------#
    
    """
    Translates phrases or words as strings from a language
    to another.    
    
    To accomplish this task, this function makes use of two powerful packages.
    
    1. By default, the first package used is 'googletrans'.
       According to the docs [https://py-googletrans.readthedocs.io/en/latest/]:
       
       A free and unlimited python library that implemented Google Translate API.
       This uses the Google Translate Ajax API to make calls to such procedures 
       as detect and translate, which implies that it requires a stable
       Internet connection.
       
       Features
       --------

       · Fast and reliable - it uses the same servers that translate.google.com uses
       · Auto language detection
       · Bulk translations
       · Customisable service URL
       · Connection pooling (the advantage of using requests.Session)
       · HTTP/2 support
                
       Note on library usage
       ---------------------

       · Maximum character limit on a single text: 15k.
       · Due to limitations of the web version of google translate,
         this API does not guarantee that the library would work properly at all times,
         so please use this library if you don't care about stability.
       
       · If you want to use a stable API, I highly recommend you to use 
         Google's official translate API.
       · If you get HTTP 5xx error or errors like #6, it's probably because Google 
         has banned your client IP address.

           - As an evidence to the latter, several tests that I've made with this module
             returned an exception as 'NoneType' object has no attribute 'group',
             because an internal module transaction, related to the translation,
             was banned by Google.
    
    
    2. In such case, this function is designed to automatically try the local 
       'translate' alternative package.
       According to the docs [https://translate-python.readthedocs.io/en/latest/]:
    
       A simple but powerful translation tool written in python with support for
       multiple translation providers.
       By now it is integrated with Microsoft Translation API and Translated MyMemory API.
       
       
    Parameters (based on built-in help)
    -----------------------------------
    
    General
    -#-#-#-    
    
    phrase_or_words : str | list[str]
        String as phrase or words, or list thereof, to be translated.
    lang_origin : str
        The original language or that where the phrase or words come from, 
        usually 2 or 3 characters long. 
    lang_translation : str
        Language of the text being translated, similar length as the original one.
        Defaults to 'en'.
    print_attributes : bool
        Determines whether to return the language translations or detections
        an a generator or return all attributes in a human-readable format.
   
    googletrans package
    -#-#-#-#-#-#-#-#-#-
    
    procedure : {'detect', 'translate'}
        Determines whether to detect the language that pertains a given string
        (or list of strings) or to perform translations.     
    text_which_language_to_detect : str
        String which language is going to be detected if chosen to.
    service_urls : str | list[str]
        Google translate url list. URLs will be used randomly.
        For example: ['translate.google.com', 'translate.google.co.kr']
    user_agent : str
        the User-Agent header to send when making requests.
    proxies : dict
        Proxies configuration. 
        Dictionary mapping protocol or protocol and host to the URL of the proxy 
        For example: {'http': 'foo.bar:3128', 'http://host.name': 'foo.bar:4012'}
    timeout : int | float
        Unit is seconds.
        
    alternative translate package
    -#-#-#-#-#-#-#-#-#-#-#-#-#-#-
    
    provider : {'MicrosoftProvider', 'MyMemory', 'LibreTranslate'}
        · MicrosoftProvider is a paid provider but it is possible you can create 
          a free account tends a quota of up to 2m of words per day.
        · MyMemory is a free provider but very complete.
        · LibreTranslate is a free and open source translation provider
        
    secret_access_key : str
        If provider is MicrosoftProvider the oAuth Access Token
        If it is LibreTranslate, the LibreTranslate API key.
        Not available for MyMemory
        
    region : str
        Region for which the available language variations are taken into account
        when making translations.
        Defaults to None for auto-detection (deduced from context).
    
    email : str
        Only for MyMemory provider.
        Valid email to increase your translations cote.
    
    Returns
    -------
    
    googletrans_package
    #-#-#-#-#-#-#-#-#-#
    
    googletrans_transl_generator : Translated object or list thereof
        Generator with the following attributes:
            - origin : str
                  Acronim of the language where the given string comes from.
            - text : str
                  The translated text
            - pronunciation : str
                  Standard pronunciation of the translated text (not
                  to be confused with phonetic translation).
                  
    googletrans_detect_spec_generator : Detected object or list thereof
        Generator with the following attributes:
            - lang : str
                  Acronim of the language in which the input string is written.
            - confidence : float
                  Probability for the language underlaying in 'lang' parameter 
                  being actual, lying in the interval [0,1].
                  
                  
    In both cases, the corresponding attibutes are printed in a 
    human-readable format if 'print_attributes' is True.
                  
    alternative translate package
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    
    alternative_transl_translation : str
        String translated to the desired language.
    """
    
    # 'googletrans' package with 'translate' procedure chosen #
    #---------------------------------------------------------#
    
    # Import the module only here #
    from googletrans import Translator as Translator_Google
    
    # Instantiate the Translator class (all critical arguments are default ones) #
    translator_instance_google = Translator_Google(service_urls=service_urls,
                                                   user_agent=user_agent,
                                                   proxies=proxies,
                                                   timeout=timeout)
    
    if procedure == "translate":    
        try:
            googletrans_transl_generator = \
            translator_instance_google.translate(phrase_or_words,
                                                 src=lang_origin, 
                                                 dest=lang_translation)
            
            googletrans_transl_attr_list = ["origin", "text", "pronunciation"]
            if isinstance(phrase_or_words, list):
                if print_attributes:
                    attribute_printer(googletrans_transl_generator, 
                                      LANG_DETECTION_CONF_INFO_TEMPLATE,
                                      googletrans_transl_attr_list)    
                else:
                    return googletrans_transl_generator
                
            else:
                if print_attributes: 
                    attribute_printer(googletrans_transl_generator, 
                                      LANG_DETECTION_CONF_INFO_TEMPLATE,
                                      googletrans_transl_attr_list)                    
                else:
                    return googletrans_transl_generator
                
    
        except AttributeError:
            
            # If an exception is raised, use the 'translate' alternative #
            #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-
            
            googletrans_version = get_googletrans_version()
            
            print("Google may have banned the methods for the 'googletrans' "
                  f"package's version {googletrans_version}. "
                  "Wait for a future update to check if the banning has been fixed."
                  "I will try with the local package 'translate' next.\n\n")
            
            # Import the module only here #
            from translate import Translator as Translator_Local
            
            # Instantiate the Translator class (all critical arguments are default ones) #
            translator_instance_local = Translator_Local(to_lang=lang_translation, 
                                                         from_lang=lang_origin,
                                                         provider=provider,
                                                         secret_access_key=secret_access_key,
                                                         region=region)
            
            
            # Catch invalid target languages
            """
            This function does not return any exception regarding this issue,
            but a string saying, depending whether the invalid shortand is that
            of the source or the target,
            "<invalid language shortand> IS AN INVALID TARGET/SOURCE LANGUAGE . \
            EXAMPLE: LANGPAIR=EN|IT USING 2 LETTER ISO OR RFC3066 LIKE ZH-CN. \
            ALMOST ALL LANGUAGES SUPPORTED BUT SOME MAY HAVE NO CONTENT".
            
            Then, one way to catch that exception is to detect whether the returned
            contains the part 'INVALID TARGET' or 'INVALID SOURCE', 
            and then throw a programmer-defined exception.
            """
            
            try:
                alternative_transl_translation = \
                translator_instance_local.translate(phrase_or_words)
            except SyntaxError:
                raise SyntaxError("Some argument is unquoted.")
            else:
                if TRANSLATE_ALTERNATIVE_ERROR_SOURCE_KWS in alternative_transl_translation:
                    raise ValueError("Invalid source language (argument no. 2)")
                
                elif TRANSLATE_ALTERNATIVE_ERROR_TARGET_KWS in alternative_transl_translation:
                    raise ValueError("Invalid target language (argument no. 3)")
                    
                else:
                    return alternative_transl_translation
                
                
    # 'googletrans' package with 'detect' procedure chosen #
    #------------------------------------------------------#
     
    elif procedure == "detect":
        try:
            googletrans_detect_spec_generator = \
            translator_instance_google.detect(text_which_language_to_detect)

            if print_attributes:
                googletrans_detect_attr_list = ["lang", "confidence"]
                attribute_printer(googletrans_detect_spec_generator, 
                                  LANG_DETECTION_CONF_INFO_TEMPLATE,
                                  googletrans_detect_attr_list)
            else:
                return googletrans_detect_spec_generator
                
                
        except AttributeError:
            print("Google may have banned the methods for the 'googletrans' "
                  f"package's version {googletrans_version}. "
                  "Wait for a future update to check if the banning has been fixed."
                  "The alternative package does not include language detection feature.")
            
            
def attribute_printer(generator: object | list[object], output_info_template: str, attr_list: list[str]) -> None:
    """
    Iterates over a generator or list of objects, retrieves specified attributes,
    and prints formatted output information using a provided format string.

    Parameters
    ----------
    generator: object | list[object]
        A single object or a list of objects from which attributes will be retrieved.

    output_info_template : str
        A format string specifying how to format and print the output information.

    attr_list : list of str
        A list of attribute names to retrieve from each object in the generator or list.

    Raises
    ------
    TypeError
        If the generator is not a list and is not an object.

    Notes
    -----
    - If `generator` is a list, iterates over each object `obj` in the list and retrieves
      the attributes specified in `attr_list`. Each attribute value is then formatted
      using `print_format_string` and printed according to `output_info_template`.

    - If `generator` is a single object, retrieves the attributes specified in `attr_list`
      from that object. Each attribute value is formatted using `print_format_string` and
      printed according to `output_info_template`.

    - Uses `getattr` to dynamically retrieve attributes from objects.

    - Uses `print_format_string` to format and print the output information.

    """
    # Defensive programming: handle nested lists in generator #
    #---------------------------------------------------------#
    
    if isinstance(generator, list):
        generator = flatten_list(generator)
        for obj in generator:            
            arg_list = [getattr(obj.attr)() for attr in attr_list]
            print_format_string(output_info_template, arg_list)
            
    else:
        arg_list = [getattr(generator.attr)() for attr in attr_list]
        print_format_string(output_info_template, arg_list)
                

#--------------------------#
# Parameters and constants #
#--------------------------#

# Google translator package #
STR_TRANSLATION_INFO_TEMPLATE = "{} --> {} (pronunciation: {})"
 
LANG_DETECTION_CONF_INFO_TEMPLATE = "Detected language: {}\nConfidence: {}"

# Alternative translator package #
TRANSLATE_ALTERNATIVE_ERROR_SOURCE_KWS = "INVALID SOURCE"
TRANSLATE_ALTERNATIVE_ERROR_TARGET_KWS = "INVALID TARGET"

# Processing procedure list #
ACTION_LIST = ["detect", "translate"]
