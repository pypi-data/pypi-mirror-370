from flask import Flask, render_template, request, redirect, url_for, make_response
import os
import platform
import shutil
import re
import json
from difflib import SequenceMatcher
from natsort import natsorted
from datetime import date, datetime
import sqlite3

from reportlab.lib.pagesizes import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, Frame, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT

from chemical_safety.chemical import chemical

# Define the paths
package_config_path = os.path.join(os.path.dirname(__file__), 'config.json')
user_config_dir = os.path.expanduser('~/.chemical_safety')
user_config_path = os.path.join(user_config_dir, 'config.json')

# Ensure the user config directory exists
os.makedirs(user_config_dir, exist_ok=True)

# Copy default config to user directory if it doesn't exist
if not os.path.exists(user_config_path):
    shutil.copyfile(package_config_path, user_config_path)

# Load configuration
with open(user_config_path) as config_file:
    CONFIG = json.load(config_file)

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def home():
        inventory_dir = CONFIG['inventory_dir']
        if os.path.exists(os.path.expanduser(inventory_dir)):
            inventory_info=True
        else:
            inventory_info=False

        course_dir = CONFIG['user_courses_dir']
        if os.path.exists(os.path.expanduser(course_dir)):
            course_info=True
        else:
            course_info=False

        return render_template('index.html', course_info=course_info, inventory_info=inventory_info)

    @app.route('/chemical_lookup')
    def chemical_lookup():
        return render_template('search_form.html', lookup_type='Chemical', page_title='Chemical Lookup')

    @app.route('/multi_chemical_lookup')
    def multi_chemical_lookup():
        return render_template('search_form.html', lookup_type='multi chemical', page_title='Multiple Chemical Lookup')

    @app.route('/experiment_lookup')
    def experiment_lookup():
        return render_template('search_form.html', lookup_type='experiment', page_title='Experiment Lookup')

    @app.route('/room_lookup', methods=['GET', 'POST'])
    def room_lookup():
        # Connect to the database
        inventory_dir = CONFIG['inventory_dir']
        if os.path.exists(os.path.expanduser(inventory_dir)):
            conn = sqlite3.connect(inventory_dir)
            cursor = conn.cursor()

            # Fetch all unique room numbers for the dropdown
            cursor.execute("SELECT DISTINCT Area FROM inventory ORDER BY Area")
            rooms = cursor.fetchall()

            selected_room = None
            room_data = []

            if request.method == 'POST':
                # Get the selected room from the form
                selected_room = request.form.get('room')

                # Query to get data for the selected room
                if selected_room:
                    cursor.execute("""
                        SELECT ID, name, Amount, [Additional Location Details], phs
                        FROM inventory
                        WHERE Area = ?
                        ORDER BY name
                    """, (selected_room,))
                    room_data = cursor.fetchall()

            conn.close()

            # Pass data to the template
            return render_template('room_lookup.html', rooms=rooms, room_data=room_data, selected_room=selected_room)
        else:
            return render_template('lookup_fail.html',msg='No chemical inventory found')

    @app.route('/course_lookup', methods=['GET', 'POST'])
    def course_lookup():
        # Path to the courses directory
        courses_dir = CONFIG['user_courses_dir']
        if os.path.exists(os.path.expanduser(courses_dir)):
            # List all available courses
            courses = [f for f in os.listdir(courses_dir) if os.path.isdir(os.path.join(courses_dir, f))]

            if request.method == 'POST':
                selected_course = request.form.get('course')
                if selected_course:
                    course_data, course_title = build_course_summary(selected_course)
                    return render_template('course_lookup.html', lookup_type="course", course_data=course_data, course_title = course_title)

            return render_template('course_dropdown.html', courses=courses, page_title='Course Lookup')
        else:
            return render_template('lookup_fail.html',msg='No course directory found')


    @app.route('/first_aid')
    def first_aid():
        return render_template('search_form.html', lookup_type='first_aid', page_title='Chemical Lookup — First Aid')

    @app.route('/secondary_label')
    def secondary_label():
        return render_template('search_form.html', lookup_type='secondary', page_title='Secondary Container Builder')

    @app.route('/phs_list', methods=['GET', 'POST'])
    def phs_list():
        inventory_dir = CONFIG['inventory_dir']
        if os.path.exists(os.path.expanduser(inventory_dir)):
            # Connect to the database
            conn = sqlite3.connect(CONFIG['inventory_dir'])
            cursor = conn.cursor()

            # Fetch unique values for Area and Contact for the dropdowns
            cursor.execute("SELECT DISTINCT Area FROM inventory WHERE phs = TRUE ORDER BY Area")
            areas = cursor.fetchall()

            cursor.execute("SELECT DISTINCT Contact FROM inventory WHERE phs = TRUE ORDER BY Contact")
            contacts = cursor.fetchall()

            # Default query to fetch all PHS data
            query = """
                SELECT ID, name, Area, Amount, [Additional Location Details], Contact, carcinogen, acute_toxin, reproductive_toxin
                FROM inventory
                WHERE phs = TRUE
            """
            filters = []
            params = []

            # Handle filtering if form is submitted
            if request.method == 'POST':
                selected_area = request.form.get('area')
                selected_contact = request.form.get('contact')

                # Add conditions to the query based on selected filters
                if selected_area and selected_area != 'any':
                    filters.append("Area = ?")
                    params.append(selected_area)

                if selected_contact and selected_contact != 'any':
                    filters.append("Contact = ?")
                    params.append(selected_contact)

                if filters:
                    query += " AND " + " AND ".join(filters)

            query += " ORDER BY Area, name"
            cursor.execute(query, params)
            phs_data = cursor.fetchall()

            conn.close()

            # Pass data to the template
            return render_template('phs_list.html', phs_data=phs_data, areas=areas, contacts=contacts)
        else: 
            return render_template('lookup_fail.html',msg='No chemical inventory found')

    @app.route('/lookup', methods=['GET', 'POST'])
    def lookup():
        if request.method == 'POST':
            search_term = request.form['search_term']
            lookup_type = request.form.get('lookup_type', 'chemical')
            # Redirect to the appropriate lookup route with the search term as a query parameter
            if lookup_type == 'Chemical':
                result = chemical(search_term)
                return render_template('chemical_lookup.html', lookup_type=lookup_type, result=result)
            elif lookup_type == 'multi chemical':
                result = [chemical(c) for c in search_term.split(', ')]
                return render_template('multi_chemical_lookup.html', lookup_type=lookup_type, result=result, experiment_name = "Custom Chemical List")
            elif lookup_type == 'experiment':
                chemlist,experiment_name = get_experiment_chem_list(search_term)
                result = [chemical(c) for c in chemlist]
                return render_template('experiment_lookup.html', lookup_type=lookup_type, result=result, experiment_name = experiment_name)
            elif lookup_type == 'first_aid':
                c = chemical(search_term)
                result = get_first_aid_info(c)
                return render_template('first_aid_info.html', name=c.full_name, result=result)
            elif lookup_type == 'secondary':
                if len(search_term) == 0:
                    return render_template('custom_secondary_label_builder.html')
                result = [chemical(c) for c in search_term.split(', ')]
                return render_template('secondary_label_builder.html', lookup_type=lookup_type, result=result)
            else:
                return "Lookup type not supported", 400
        else:
            # Render the search form with a default lookup type context
            return render_template('search_form.html', lookup_type='Chemical', page_title='Chemical Lookup')
        
    @app.route('/generate_label', methods=['POST'])
    def generate_label():    
        container_name = request.form.get('container_name')
        generator_name = request.form.get('generator_name')
        signal_word = request.form.get('signal_word')
        chemical_cids = request.form.get('chemical_cids').split(',')
        disposal_info_list = list(set(request.form.getlist('disposal[]')))
        haz_waste_list = request.form.getlist('hazwaste[]')
        PHS_list = request.form.getlist('PHS[]')
        PHS_type = request.form.getlist('phs_type[]')

        haz_set = set()
        for hw in haz_waste_list:
            hw_designations = hw.split(', ')
            for hwd in hw_designations:
                haz_set.add(hwd)
        haz_list = list(haz_set)
        if len(haz_list) > 0:
            hazwaste_info_string = ', '.join(haz_list)
        else:
            hazwaste_info_string = None

        disposal_info_string = ', '.join(disposal_info_list) if disposal_info_list else None

        PHS = any(PHS_list)
        PHS_type = list(set(PHS_type)) if PHS_type else []

        all_selected_pictograms = set()
        all_selected_statements = set()

        for cid in chemical_cids:
            selected_pictograms = request.form.getlist(f'pictograms_{cid}')
            selected_statements = request.form.getlist(f'hazard_statements_{cid}')
            all_selected_pictograms.update(selected_pictograms)
            all_selected_statements.update(selected_statements)

        danger_statements = [s.replace("Danger:", "<strong>Danger:</strong>").split('(')[0] for s in all_selected_statements if "Danger:" in s]
        warning_statements = [s.replace("Warning:", "<strong>Warning:</strong>").split('(')[0] for s in all_selected_statements if "Warning:" in s]
        hazard_statements = danger_statements + warning_statements

        label_dict = {
            'container_name': container_name,
            'signal_word': signal_word,
            'generator': generator_name,
            'pictograms': list(all_selected_pictograms),
            'hazard_statements': hazard_statements,
            'date': date.today().strftime("%B %d, %Y")
            #'disposal': disposal_info_string,
            #'hazwaste': hazwaste_info_string,
            #'PHS': PHS,
            #'PHS_types': PHS_type
        }
        
        # Determine the action based on which button was pressed
        if 'print' in request.form:
            try:
                
                pdf_path = os.path.join(user_config_dir, 'label.pdf')
                base_dir = os.path.dirname(os.path.abspath(__file__))
                pictogram_paths = [os.path.join(base_dir, 'static', 'img', f"{p}.png") for p in all_selected_pictograms]

                create_label_pdf(container_name, signal_word, pictogram_paths, hazard_statements, generator_name, pdf_path)

                #Determine OS and execute the respective print command
                current_os = platform.system()
                if current_os == "Windows":
                    os.startfile(pdf_path, "print")
                elif current_os == "Linux" or current_os == "Darwin":
                    os.system(f'lp {pdf_path}')
                else:
                    raise Exception(f"Unsupported operating system: {current_os}")

                return 'Label has been printed.<br><a href="/" title="Go to Home Page">Home</a>'
            except Exception as e:
                print(f'Did not successfully print: {e}')
                return render_template('lookup_fail.html',msg=f"Did not successfully print: {e}")

        # If 'preview' button was clicked, just render the template
        return render_template('secondary_label.html', data=label_dict)

    return app

def enumerate(sequence, start=0):
    return zip(range(start, len(sequence) + start), sequence)

def build_course_summary(search_term):

    user_static_dir = CONFIG.get('user_courses_dir', 'None')

    # Check if user has set a valid directory
    if user_static_dir == "None" or not os.path.exists(os.path.expanduser(user_static_dir)):
       return [], "Did not find directory with course information."
    else:
        directory_path = user_static_dir
    

    course_list = get_course_list(directory_path)
    custom_matched = custom_match(search_term,course_list)
    best_course = ''
    if custom_matched:
        best_course, _ = custom_matched[0]
    directory_path = os.path.join(directory_path, best_course.replace(' ', ''))
    exp_names = [f for f in list_experiments(best_course)]

    exp_summary = []

    for file in exp_names:
        with open(os.path.join(directory_path, file+'.txt'), 'r') as f:
            experiment_chemical_data = [chemical(line.strip()) for line in f.readlines()]

        disposal = set()
        phs = False
        ppe = False

        for chem in experiment_chemical_data:
            if chem.WSU_particularly_hazardous:
                phs=True
                ppe = True
            if 'P262' in chem.p_codes:
                ppe = True
            if chem.disposal_info:
                for di in chem.disposal_info:
                    disposal.add(di)
            if chem.hazardous_waste:
                disposal.add(chem.hazardous_waste_info) 
        exp_summary.append({'name' : file, 'PHS' : phs, 'disposal' : list(disposal), 'PPE' : ppe, 'chem_data': experiment_chemical_data})

    return exp_summary, best_course
        
def get_course_list(directory_path):


    course_list = []

    pattern = re.compile(r'^([A-Z]{4})(\d{4})$')

    if os.path.exists(directory_path):
        for entry in os.listdir(directory_path):
            if os.path.isdir(os.path.join(directory_path, entry)):
                match = pattern.match(entry)
                if match:
                    course_name = f"{match.group(1)} {match.group(2)}"
                    course_list.append(course_name)
    else:
        print(f"Directory not found: {directory_path}")

    return natsorted(course_list)

def list_experiments(course):
    
    course = course.replace(' ', '')

    user_static_dir = CONFIG.get('user_courses_dir', 'None')

    # Check if user has set a valid directory
    if user_static_dir == "None" or not os.path.exists(os.path.expanduser(user_static_dir)):
        directory_path = os.path.join('static/courses', course)
    else:
        directory_path = os.path.join(os.path.expanduser(user_static_dir), course)
    
    txt_files = []
    if os.path.exists(directory_path):
        for filename in os.listdir(directory_path):
            if filename.endswith('.txt'):
                txt_files.append(os.path.splitext(filename)[0])
    else:
        print(f"Directory not found: {directory_path}")
    return natsorted(txt_files)

def get_experiment_chem_list(search_term):

    user_static_dir = CONFIG.get('user_courses_dir', 'None')
    if user_static_dir == "None" or not os.path.exists(os.path.expanduser(user_static_dir)):
        directory_path = 'static/courses'
    else:
        directory_path = user_static_dir

    course_list = get_course_list(directory_path)
    best_course = None
    best_distance = float('inf')  # Use infinity as initial comparison value
    
    pattern = re.compile(r'([A-Z]{4})\s*(\d{4})')
    match = pattern.search(search_term)

    if match:
        best_course, _ = custom_match(f"{match.group(0)} {match.group(1)}", course_list)[0]
        search_term = search_term.replace(match.group(0), '')

    user_static_dir = CONFIG.get('user_courses_dir', 'None')

    # Check if user has set a valid directory
    if user_static_dir == "None" or not os.path.exists(os.path.expanduser(user_static_dir)):
        return [], "Did not find directory with course information."
    else:
        directory_path = os.path.expanduser(user_static_dir)
    
    if best_course:
        directory_path = os.path.join(directory_path, best_course.replace(' ', ''))
        txt_files = [os.path.splitext(f)[0] for f in os.listdir(directory_path) if f.endswith('.txt')]
    else:
        txt_files_dict = {}
        for course in course_list:
            course_directory_path = os.path.join(directory_path, course.replace(' ', ''))
            for f in os.listdir(course_directory_path): 
                if f.endswith('.txt'):
                    f_name = os.path.splitext(f)[0]
                    txt_files_dict[f_name] = course_directory_path
        txt_files = txt_files_dict.keys()

    best_experiment, _ = custom_match(search_term, txt_files)[0]

    if best_course is None:
        directory_path = txt_files_dict[best_experiment]
        with open(os.path.join(directory_path, best_experiment+".txt"), 'r') as f:
            experiment_data = [line.strip() for line in f.readlines()]
        return natsorted(experiment_data), best_experiment
    return [], f"No valid match for {search_term}"    # Return an empty list if no match is found
    

def custom_match(search_str, choices, weight_number=0.7, weight_text=0.3):
    """
    Custom matching function that places more weight on numerical parts of the strings.
    
    :param search_str: The string to search for.
    :param choices: A list of strings to search against.
    :param weight_number: The weight to place on matching numbers. Default is 0.7.
    :param weight_text: The weight to place on the rest of the text. Default is 0.3.
    :return: A list of tuples with the match and its score, sorted by score.
    """
    search_numbers = [int(num) for num in re.findall(r'\d+', search_str)]
    results = []

    for choice in choices:
        choice_numbers = [int(num) for num in re.findall(r'\d+', choice)]
        number_score = 1 if search_numbers == choice_numbers else 0
        text_score = SequenceMatcher(None, search_str, choice).ratio() 

        # Calculate final score with weighted sum of number and text similarities
        final_score = (weight_number * number_score) + (weight_text * text_score)
        results.append((choice, final_score))

    # Sort the results based on the score in descending order
    return sorted(results, key=lambda x: x[1], reverse=True)

def get_first_aid_info(c):
    data = c.full_json()

    results = []

    SafetyInfo = next((item for item in data['Record']['Section'] if item['TOCHeading'] == 'Safety and Hazards'), None)
    if SafetyInfo:
        First_Aid_Info = next((item for item in SafetyInfo['Section'] if item['TOCHeading'] == 'First Aid Measures'), None)
        if First_Aid_Info:
            for e in First_Aid_Info["Information"]:
                results.append(e)
        First_Aid_Second = next((item for item in First_Aid_Info['Section'] if item['TOCHeading'] == 'First Aid'), None)
        if First_Aid_Second:
            for e in First_Aid_Second["Information"]:
                results.append(e)
    
    results_dict = {}

    named_results = [r for r in results if 'Name' in r.keys()]
    #print(f'{len(named_results)} out of {len(results)} results had names')
    for nr in named_results:
        results_dict[nr['Name']] = [s['String'] for s in nr['Value']['StringWithMarkup']] 
    
    return results_dict


def create_label_pdf(container_name, signal_word, pictogram_paths, hazard_statements, generator, pdf_path):

    # Set up the document
    doc = SimpleDocTemplate(pdf_path, pagesize=(4 * inch, 2 * inch), topMargin=0, bottomMargin=0, leftMargin=0.05 * inch, rightMargin=0.05 * inch)

    # Container for elements
    elements = []

    # Create custom styles
    title_style = ParagraphStyle(
        name='TitleStyle',
        fontName='Helvetica-Bold',
        fontSize=14,  # Title font size
        alignment=TA_LEFT,  # Left alignment for title
        spaceAfter=8  # Space after the title
    )

    signal_word_style = ParagraphStyle(
        name='SignalWordStyle',
        fontName='Helvetica-Bold',
        fontSize=11,
        alignment=TA_LEFT,
        spaceAfter=2,
        spaceBefore=0
    )

    normal_text_style = ParagraphStyle(
        name='NormalTextStyle',
        fontName='Helvetica',
        fontSize=9,  # Normal text font size
        alignment=TA_LEFT,  # Left alignment
        spaceAfter=0,
        leading=9.5
    )

    small_text_style = ParagraphStyle(
        name='NormalTextStyle',
        fontName='Helvetica',
        fontSize=7,  # Normal text font size
        alignment=TA_LEFT,  # Left alignment
        spaceAfter=0,
        leading=7.5
    )

    # Add the title
    title = Paragraph(f"<b>{container_name}</b>", title_style)
    elements.append(title)

    # Content for the left column
    left_elements = []
    signal_word = Paragraph(f"<b>{signal_word}</b>", signal_word_style)
    left_elements.append(signal_word)

    # Load and place pictograms in left column

    num_pictograms = len(pictogram_paths)

    # Case structure for different numbers of pictograms
    pictogram_table_data=[]
    if num_pictograms == 1:
        # One pictogram - use a large size
        img_size = 0.8 * inch
        pictogram_table_data = [[Image(pictogram_paths[0], img_size, img_size)]]

    elif num_pictograms == 2:
        # Two pictograms - stack them vertically
        img_size = 0.6 * inch
        pictogram_table_data = [
            [Image(pictogram_paths[0], img_size, img_size)],  # First image in the first row
            [Image(pictogram_paths[1], img_size, img_size)]   # Second image in the second row
        ]


    elif num_pictograms == 3:
        # Three pictograms - put two on the first row, one centered on the second row
        img_size = 0.5 * inch
        pictogram_table_data = [
            [Image(pictogram_paths[0], img_size, img_size), Image(pictogram_paths[1], img_size, img_size)],
            [Image(pictogram_paths[2], img_size, img_size), '']  # Second row has one pictogram, other cell is empty
        ]

    elif num_pictograms == 4:
        # Four pictograms - two per row
        img_size = 0.5 * inch
        pictogram_table_data = [
            [Image(pictogram_paths[0], img_size, img_size), Image(pictogram_paths[1], img_size, img_size)],
            [Image(pictogram_paths[2], img_size, img_size), Image(pictogram_paths[3], img_size, img_size)]
        ]

    elif num_pictograms > 4:
        # More than four pictograms - dynamically handle with smaller sizes
        img_size = 0.4 * inch
        pictogram_images = [Image(pictogram, img_size, img_size) for pictogram in pictogram_paths]
        pictogram_table_data = [pictogram_images[i:i+2] for i in range(0, len(pictogram_images), 2)]  # Two per row

    if len(pictogram_table_data) > 0:
        pictogram_table = Table(pictogram_table_data)

        pictogram_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Align images vertically
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),   # Align images horizontally
            ('LEFTPADDING', (0, 0), (-1, -1), 0),    # Remove left padding
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),   # Remove right padding
            ('TOPPADDING', (0, 0), (-1, -1), 0),     # Remove top padding
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),  # Remove bottom padding
            ('GRID', (0, 0), (-1, -1), 0, colors.white)  # Optional: Remove grid borders
        ]))


        left_elements.append(pictogram_table)

    # Content for the right column
    right_elements = []

    for statement in hazard_statements:
        right_elements.append(Paragraph(statement, normal_text_style))

    table_data = [[left_elements, right_elements]]

    table = Table(table_data, colWidths=[1 * inch, 2.8 * inch])

    # Style the table (optional)
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Align content to the top of each cell
        ('LEFTPADDING', (0, 0), (-1, -1), 0),    # Remove left padding
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),   # Remove right padding
        ('TOPPADDING', (0, 0), (-1, -1), 0),     # Remove top padding
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),  # Remove bottom padding
        ('GRID', (0, 0), (-1, -1), 0, colors.white)  # Optional: Remove grid borders
    ]))

    # Add the table (2-column layout) to elements
    elements.append(table)

    # Add a footer
    now = datetime.now()
    formatted_date = now.strftime("%b %d, %Y")
    generator = Paragraph(f"{generator} — {formatted_date}", small_text_style)
    elements.append(generator)

    # Build the PDF with elements
    doc.build(elements)
    return 0
    

def dashboard():
    app = create_app()
    app.run(debug=True)

if __name__ == '__main__':
    dashboard()