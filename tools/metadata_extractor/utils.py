import requests
import pandas as pd
import os
from io import BytesIO

def get_dhis2_data(url, username, password):
    """
    Generic function to make a request to the DHIS2 API.
    """
    response = requests.get(url, auth=(username, password))
    response.raise_for_status()
    return response.json()

def get_all_programs(url, username, password):
    """
    Get all DHIS2 programs.
    """
    programs_url = f"{url}/api/programs?fields=id,name"
    data = get_dhis2_data(programs_url, username, password)
    return {program['name']: program['id'] for program in data['programs']}

def get_program_attributes(url, username, password, program_id):
    """
    Get program attributes for a given program.
    """
    attributes_url = f"{url}/api/programs/{program_id}?fields=programTrackedEntityAttributes[trackedEntityAttribute[id,name]]"
    data = get_dhis2_data(attributes_url, username, password)
    attributes = pd.DataFrame(data['programTrackedEntityAttributes'])
    return attributes

def get_program_stages(url, username, password, program_id):
    """
    Get stages for a given program.
    """
    stages_url = f"{url}/api/programs/{program_id}?fields=programStages[id,name]"
    data = get_dhis2_data(stages_url, username, password)
    return {stage['name']: stage['id'] for stage in data['programStages']}

def get_program_stage_data_elements(url, username, password, stage_id):
    """
    Get data elements for a given program stage.
    """
    data_elements_url = f"{url}/api/programStages/{stage_id}?fields=programStageDataElements[dataElement[id,name]]"
    data = get_dhis2_data(data_elements_url, username, password)
    data_elements = pd.DataFrame(data['programStageDataElements'])
    return data_elements

def get_program_indicators(url, username, password, program_id):
    """
    Get program indicators for a given program.
    """
    indicators_url = f"{url}/api/programs/{program_id}?fields=programIndicators[id,name]"
    data = get_dhis2_data(indicators_url, username, password)
    indicators = pd.DataFrame(data['programIndicators'])
    return indicators

def get_option_sets(url, username, password):
    """
    Get option sets from DHIS2.
    """
    option_sets_url = f"{url}/api/optionSets?fields=id,name,options[id,name]"
    data = get_dhis2_data(option_sets_url, username, password)
    option_sets = pd.DataFrame(data['optionSets'])
    return option_sets

def save_data_to_excel(attributes, stages_data, indicators, option_sets):
    """
    Save the extracted data to an Excel file.
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        if not attributes.empty:
            attributes.to_excel(writer, sheet_name='Attributes', index=False)
        for stage, data_elements in stages_data.items():
            data_elements.to_excel(writer, sheet_name=stage, index=False)
        if not indicators.empty:
            indicators.to_excel(writer, sheet_name='Indicators', index=False)
        if not option_sets.empty:
            option_sets.to_excel(writer, sheet_name='Option Sets', index=False)

    output.seek(0)
    return output

def log_extraction(tool_name):
    """
    Log the extraction event.
    """
    # Assuming you have a logging mechanism in place
    # You can implement your logging logic here
    pass

def get_usage_statistics(tool_name):
    """
    Retrieve usage statistics for the given tool.
    """
    # Assuming you have a statistics tracking mechanism in place
    # You can implement your statistics retrieval logic here
    return {
        "total_extractions": 100,
        "last_extraction_date": "2024-08-12",
        "extractions_this_period": 5
    }
