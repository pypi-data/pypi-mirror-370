#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
**Goal**
Make audio transcriptions using preferently free software
Easiest way is using IBM Watson Cloud services (IBM Watsonx),
available through Anaconda.
The service or resource to accomplish the task is 'Speech To Text'
"""

#----------------#
# Import modules # 
#----------------#

from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

#------------------------#
# Import project modules # 
#------------------------#

from filewise.file_operations.path_utils import find_files
from pygenutils.strings.string_handler import append_ext, modify_obj_specs
from pygenutils.strings.text_formatters import print_format_string

#------------------#
# Define functions # 
#------------------#

def save_transcription_in_file(transcript: str, relative_path_noext: str, ext: str = "txt") -> None:
    
    # Add the extension to the input file #
    relative_path = append_ext(relative_path_noext, ext)
    
    # Create the file object #
    file_object = open(relative_path, "w")
    
    # Write the transcription to the file #
    print_format_string(SAVING_TRANSCRIPTION_STR, relative_path)
    
    file_object.write(transcript)
    file_object.close()
    
    # If the execution has reached the end with no errors, print a confirmation message #
    print("Transcription successfully writt.")
    

#--------------------------#
# Parameters and constants #
#--------------------------#

# File extensions #
FILE2TRANSCRIPT_EXT = "wav"

# Relative paths #
FILES2TRANSCRIBE_PATH = "/home/jonander/Documents/04-Ikasketak/04-Ikastaroak/"\
                        "Deusto_Formacion/Curso_superior_Python/teoria/moduluak/Tema_5/"

files2transcribe_list = find_files(FILE2TRANSCRIPT_EXT,
                                   FILES2TRANSCRIBE_PATH, 
                                   match_type="ext",
                                   top_path_only=True)

# Output informartion strings #
TRANSCRIPTION_RESULT_STR = """File : {}
Transcription:
    
{}"""

SAVING_TRANSCRIPTION_STR = "Saving transcription to file {}"

# Transcription controls #
PRINT_TRANSCRIPTION = False
SAVE_TRANSCRIPTION = False

# IBM Watson Cloud's Speech To Text service's keys #
"""
Steps to get the API Key and 'Speech To Text' service ID
--------------------------------------------------------
1. Open Anaconda Navigator and select IBM Watsonx and log in
2. At the top-left corner, click into the four horizontal parallel lines.
    2.1 Unfold the 'Administration' menu and click the 'Access (IAM)' option.
        Another tab will be opened, redirecting to IBM Cloud
    2.2 At IBM Cloud, check whether the mentioned resource -Speech To Text'-
        is activated, at the resources list.
        2.2.1 In the leftmost shrinked panel, click into the bulletpoint icon 
              (third one, starting from the upmost four horizontal parallel
                lines icon). The resources list will show.
        2.2.2 The section that this service belongs to is 'AI / Machine Learning'
              If the service does not appear, search through the catalog
              (upmost main bar, at the right of the search bar) and create it.
    2.3 When checked or created, at the resource list, click on the service
    2.4 The API Key and service ID are contained in the 'Credentials' tag;
        the service ID is contained in the URL, after the last forward slash.
"""

# Define both the API_KEY and SERVICE_ID here
API_KEY=""
SERVICE_ID=""
    
#----------------#
# Operation part # 
#----------------#

# Set up authentication #
#-----------------------#

url = f"https://api.eu-de.speech-to-text.watson.cloud.ibm.com/instances/{SERVICE_ID}"

authenticator = IAMAuthenticator(API_KEY)
speech_to_text = SpeechToTextV1(authenticator=authenticator)
speech_to_text.set_service_url(url)

# Loop through the file list #
#----------------------------#

for audio_file in files2transcribe_list:    
    with open(audio_file, "rb") as audio:
        
        # Transcribe the audio file #
        response = speech_to_text.recognise(audio=audio,
                                            content_type=f"audio/{FILE2TRANSCRIPT_EXT}")
        
    # Save or print transcription as chosen #
    #-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#
    
    transcript = response.result['results'][0]['alternatives'][0]['transcript']
    format_args = [audio_file, transcript]
    
    transcript_file_name = modify_obj_specs(audio_file, 
                                            "name_noext",
                                            str2add="_transcription")
    
    if PRINT_TRANSCRIPTION: 
        print_format_string(TRANSCRIPTION_RESULT_STR, format_args)
    
    if SAVE_TRANSCRIPTION:
        save_transcription_in_file(transcript, transcript_file_name)
        
    if (not PRINT_TRANSCRIPTION and not SAVE_TRANSCRIPTION):
        print("No transcription printing nor saving chosen")
