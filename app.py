from flask import Flask, render_template, request, jsonify, send_file
from flask_mail import Mail, Message
import requests
import pandas as pd
from io import BytesIO
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.example.com'  # Replace with your SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your-email@example.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'your-email-password'  # Replace with your email password
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

def get_dhis2_data(url, username, password, endpoint, params=None):
    response = requests.get(f"{url}/api/{endpoint}", auth=(username, password), params=params)
    response.raise_for_status()
    return response.json()

def get_all_programs(url, username, password):
    endpoint = "programs.json?fields=id,name&paging=false"
    programs_data = get_dhis2_data(url, username, password, endpoint)
    return {program['name']: program['id'] for program in programs_data['programs']}

def get_program_attributes(url, username, password, program_id):
    endpoint = f"programs/{program_id}.json?fields=programTrackedEntityAttributes[trackedEntityAttribute[name,id]]"
    program_data = get_dhis2_data(url, username, password, endpoint)
    attributes = program_data['programTrackedEntityAttributes']
    
    attributes_list = []
    for attribute in attributes:
        attribute_info = {
            "Name": attribute['trackedEntityAttribute']['name'],
            "ID": attribute['trackedEntityAttribute']['id']
        }
        attributes_list.append(attribute_info)
    
    return pd.DataFrame(attributes_list)

def get_program_stages(url, username, password, program_id):
    endpoint = f"programs/{program_id}.json?fields=programStages[id,name]"
    program_data = get_dhis2_data(url, username, password, endpoint)
    return {stage['name']: stage['id'] for stage in program_data['programStages']}

def get_program_stage_data_elements(url, username, password, program_stage_id):
    endpoint = f"programStages/{program_stage_id}.json?fields=programStageDataElements[dataElement[name,id]]"
    stage_data = get_dhis2_data(url, username, password, endpoint)
    data_elements = stage_data['programStageDataElements']
    
    data_elements_list = []
    for de in data_elements:
        de_info = {
            "Name": de['dataElement']['name'],
            "ID": de['dataElement']['id']
        }
        data_elements_list.append(de_info)
    
    return pd.DataFrame(data_elements_list)

def get_program_indicators(url, username, password, program_id):
    endpoint = f"programs/{program_id}.json?fields=programIndicators[id,name]"
    program_data = get_dhis2_data(url, username, password, endpoint)
    indicators = program_data['programIndicators']
    
    indicators_list = []
    for indicator in indicators:
        indicator_info = {
            "Name": indicator['name'],
            "ID": indicator['id']
        }
        indicators_list.append(indicator_info)
    
    return pd.DataFrame(indicators_list)

def get_option_sets(url, username, password):
    endpoint = "optionSets.json?fields=id,name&paging=false"
    option_sets_data = get_dhis2_data(url, username, password, endpoint)
    return pd.DataFrame(option_sets_data['optionSets'], columns=['id', 'name'])

def save_data_to_excel(attributes, stages_data, indicators, option_sets):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if not attributes.empty:
            attributes.to_excel(writer, sheet_name='Attributes', index=False)
        
        for stage_name, stage_data_elements in stages_data.items():
            sheet_name = stage_name[:31]  # Excel sheet name limit
            stage_data_elements.to_excel(writer, sheet_name=sheet_name, index=False)
        
        if not indicators.empty:
            indicators.to_excel(writer, sheet_name='Indicators', index=False)
        
        if not option_sets.empty:
            option_sets.to_excel(writer, sheet_name='OptionSets', index=False)
    
    output.seek(0)
    return output

# Database operations
def log_extraction(tool_name):
    conn = sqlite3.connect('usage_stats.db')
    c = conn.cursor()
    c.execute("INSERT INTO extractions (tool_name, extraction_date) VALUES (?, ?)",
              (tool_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_usage_statistics(tool_name):
    conn = sqlite3.connect('usage_stats.db')
    c = conn.cursor()
    
    # Get total extractions
    c.execute("SELECT COUNT(*) FROM extractions WHERE tool_name = ?", (tool_name,))
    total_extractions = c.fetchone()[0]
    
    # Get last extraction date
    c.execute("SELECT extraction_date FROM extractions WHERE tool_name = ? ORDER BY extraction_date DESC LIMIT 1", (tool_name,))
    last_extraction = c.fetchone()
    last_extraction_date = last_extraction[0] if last_extraction else 'N/A'
    
    # Get extractions in the current period (e.g., last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    c.execute("SELECT COUNT(*) FROM extractions WHERE tool_name = ? AND extraction_date >= ?", (tool_name, thirty_days_ago.isoformat()))
    period_extractions = c.fetchone()[0]
    
    conn.close()
    return {
        'total_count': total_extractions,
        'last_date': last_extraction_date,
        'period_count': period_extractions
    }

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/tools')
def tools():
    return render_template('tools.html')

@app.route('/login', methods=['POST'])
def login():
    url = request.form['url']
    username = request.form['username']
    password = request.form['password']
    
    try:
        programs = get_all_programs(url, username, password)
        return jsonify(programs)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/stages', methods=['POST'])
def stages():
    url = request.form['url']
    username = request.form['username']
    password = request.form['password']
    program_id = request.form['program_id']
    
    try:
        stages = get_program_stages(url, username, password, program_id)
        return jsonify(stages)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/metadata_extractor', methods=['GET'])
def metadata_extractor():
    return render_template('extract.html')

@app.route('/extract', methods=['POST'])
def extract():
    url = request.form['url']
    username = request.form['username']
    password = request.form['password']
    program_id = request.form['program_id']
    selected_metadata = request.form.getlist('metadata[]')
    stage_ids = request.form.getlist('stage_ids[]')

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

@app.route('/request_tool', methods=['POST'])
def request_tool():
    msg = Message('Tool Request Submission', sender='noreply@example.com', recipients=['kk426st@gmail.com'])
    msg.body = request.form['request_text']
    
    try:
        mail.send(msg)
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/statistics', methods=['GET'])
def statistics():
    try:
        stats = get_usage_statistics('DHIS2 Metadata Extractor')
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
