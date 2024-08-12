from flask import render_template, request, redirect, url_for, jsonify, send_file
from . import metadata_extractor
from .forms import LoginForm, ProgramSelectionForm, MetadataSelectionForm, ToolRequestForm
from .utils import get_dhis2_data, get_all_programs, get_program_attributes, get_program_stages, get_program_stage_data_elements, get_program_indicators, get_option_sets, save_data_to_excel, log_extraction, get_usage_statistics
import pandas as pd
from io import BytesIO
from flask_mail import Message

@metadata_extractor.route('/')
def welcome():
    """
    Render the welcome page.
    """
    return render_template('welcome.html')

@metadata_extractor.route('/tools')
def tools():
    """
    Render the tools page where users can access different tools.
    """
    return render_template('tools.html')

@metadata_extractor.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle login form submission to get available programs from DHIS2.
    """
    form = LoginForm()
    if form.validate_on_submit():
        url = form.url.data
        username = form.username.data
        password = form.password.data
        
        try:
            programs = get_all_programs(url, username, password)
            return jsonify(programs)
        except Exception as e:
            return jsonify({'error': str(e)})
    
    return render_template('login.html', form=form)

@metadata_extractor.route('/programs', methods=['POST'])
def programs():
    """
    Handle program selection and display stages for the selected program.
    """
    form = ProgramSelectionForm()
    if form.validate_on_submit():
        url = request.form['url']
        username = request.form['username']
        password = request.form['password']
        program_id = form.program.data
        
        try:
            stages = get_program_stages(url, username, password, program_id)
            return jsonify(stages)
        except Exception as e:
            return jsonify({'error': str(e)})

    return render_template('program_selection.html', form=form)

@metadata_extractor.route('/metadata_extractor', methods=['GET'])
def metadata_extractor_view():
    """
    Render the metadata extractor page.
    """
    form = MetadataSelectionForm()
    return render_template('extract.html', form=form)

@metadata_extractor.route('/extract', methods=['POST'])
def extract():
    """
    Handle metadata extraction and return the Excel file with the extracted data.
    """
    form = MetadataSelectionForm()
    if form.validate_on_submit():
        url = request.form['url']
        username = request.form['username']
        password = request.form['password']
        program_id = request.form['program_id']
        selected_metadata = form.metadata_types.data
        stage_ids = form.stages.data

        try:
            attributes = pd.DataFrame()
            stages_data = {}
            indicators = pd.DataFrame()
            option_sets = pd.DataFrame()

            if 'attributes' in selected_metadata:
                attributes = get_program_attributes(url, username, password, program_id)
            
            if 'data-elements' in selected_metadata:
                stages = get_program_stages(url, username, password, program_id)
                for stage_id in stage_ids:
                    stage_data_elements = get_program_stage_data_elements(url, username, password, stage_id)
                    stage_name = [name for name, id in stages.items() if id == stage_id][0]
                    stages_data[stage_name] = stage_data_elements
            
            if 'program-indicators' in selected_metadata:
                indicators = get_program_indicators(url, username, password, program_id)
            
            if 'option-sets' in selected_metadata:
                option_sets = get_option_sets(url, username, password)

            # Log the extraction
            log_extraction('DHIS2 Metadata Extractor')

            output = save_data_to_excel(attributes, stages_data, indicators, option_sets)
            return send_file(
                output,
                as_attachment=True,
                download_name="metadata.xlsx",
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            return jsonify({'error': str(e)})

    return render_template('extract.html', form=form)

@metadata_extractor.route('/request_tool', methods=['POST'])
def request_tool():
    """
    Handle the submission of a tool request.
    """
    form = ToolRequestForm()
    if form.validate_on_submit():
        request_text = form.request_text.data
        msg = Message('Tool Request Submission', sender='noreply@example.com', recipients=['kk426st@gmail.com'])
        msg.body = request_text
        
        try:
            mail.send(msg)
            return jsonify({'status': 'success'})
        except Exception as e:
            return jsonify({'error': str(e)})

    return render_template('request_tool.html', form=form)

@metadata_extractor.route('/statistics', methods=['GET'])
def statistics():
    """
    Retrieve and return usage statistics for the 'DHIS2 Metadata Extractor' tool.
    """
    try:
        stats = get_usage_statistics('DHIS2 Metadata Extractor')
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)})
