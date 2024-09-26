from flask import Flask, render_template, request, send_file
import plotly.graph_objects as go
import io
import plotly.io as pio
import mysql.connector
import pandas as pd


app = Flask(__name__)

# Database configuration
db_config = {
    'user': 'rimjhim',  # Update with your username
    'password': 'DeckerCompetency2024',  # Update with your password
    'host': 'localhost',  # Update with your database host
    'database': 'competencydata',  # Update with your database name
    'raise_on_warnings': True
}


# Semester mapping from specific to generic
semester_mapping = {
    'Fall 2024': 'Fall Year 1',
    'Spring 2025': 'Spring Year 1',
    'Summer 2025': 'Summer Year 1',
    'Fall 2025': 'Fall Year 2',
    'Spring 2026': 'Spring Year 2',
    'Summer 2026': 'Summer Year 2',
    'Fall 2026': 'Fall Year 3',
    'Spring 2027': 'Spring Year 3',
    'Summer 2027': 'Summer Year 3'
}

# Establish a database connection
def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

# Load the target scores from Excel
def load_target_scores():
    path = 'C:/Users/rsingh16/Desktop/competency project/data/target-scores.csv'
    target_scores_df = pd.read_csv(path)
    target_scores_df.set_index('Semesters', inplace=True)
    
    return target_scores_df

def fetch_student_data(student_id, semester):
    """Fetches student scores from the database for a specific semester using the mapping."""
    connection = get_db_connection()
    cursor = connection.cursor()

    # Adjust the SQL query based on your specific database schema
    query = "SELECT * FROM studentcompetencies WHERE student_id = %s AND semester_id = %s"
    cursor.execute(query, (student_id, semester))
    student_data = cursor.fetchall()

    cursor.close()
    connection.close()
    return student_data

grade_mapping = {
    'NR': 0,
    'B': 1,
    'E': 2,
    'P': 3,
    'C': 4,
    'NA': 0  # Not assessed yet
}

def plot_student_competency_scores_plotly(student_id, semester, target_scores_df):
    mapped_semester = semester_mapping[semester]
    student_data = fetch_student_data(student_id, semester)

    fig = go.Figure()
    valid_scores = {'B', 'E', 'P', 'C', 'NR', 'NA'}  # Set of valid scores

    for student in student_data:
        print(student)
        # Loop over each competency in the DataFrame
        score_index = 4  # Starting index of scores in the student tuple
        for comp in target_scores_df.columns:
            # Skip if the score is not valid or is feedback
            if student[score_index] not in valid_scores:
                score_index += 1
                continue  # Skip this loop iteration if the score is invalid

            student_score = grade_mapping[student[score_index]]  # Convert letter grade to number
            print(student[score_index])   
            print ("===")
            print(student_score)
            print ("\n")
           
           

            competency_name = comp
            target_score = grade_mapping[target_scores_df.loc[mapped_semester, comp]]  # Convert target score to number

            deviation = student_score - target_score
            message = "Right on track!" if deviation == 0 else "Great work, slow down!" if deviation > 0 else "Keep working hard!"

            # Plot each point with the appropriate deviation and message
            fig.add_trace(go.Scatter(
                x=[0, deviation],
                y=[competency_name, competency_name],
                mode='lines+markers',
                name=competency_name,
                text=f"Student: {student[score_index]}, Target: {target_scores_df.loc[mapped_semester, comp]}, {message}",
                hoverinfo='text',
                marker=dict(size=[12, 16 if deviation == 0 else 12], color='#887BB0' if deviation > 0 else ('#FB6090' if deviation < 0 else 'yellow')),
                line=dict(width=1.5, dash='solid' if deviation != 0 else 'solid')
            ))

            score_index += 1  # Move to the next score in the tuple

    fig.update_layout(
    title=f"Difference graph for {student_id} in {mapped_semester}",
    xaxis_title="Deviation from Target",
    yaxis_title="Competency",
    plot_bgcolor='#fefae0',
    paper_bgcolor='#faedcd',
    height=1000,   
    width=1000    
)
    return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')


@app.route('/')
@app.route('/index')
def index():
    student_id = 'B00768785'
    semester = 'Fall 2024' 
    target_scores_df = load_target_scores()
    plot_html = plot_student_competency_scores_plotly(student_id, semester, target_scores_df)
    return render_template('/index.html', plot_html=plot_html)


@app.route('/about')
def about():
    return render_template('About.html')

@app.route('/contact')
def contact():
    return render_template('Contact.html')
@app.route('/deviation')
def deviation():
    student_id = 'student 1 BD'

    return render_template('deviation.html')

@app.route('/plot/<student_id>')
def plot_png(student_id):
    plot_type = request.args.get('type', 'plotly')
    semester = "Fall 2024"  # This might be dynamically determined or passed as an argument
    target_scores_df = load_target_scores()
    html_content = plot_student_competency_scores_plotly(student_id, semester, target_scores_df)

    return html_content


if __name__ == '__main__':
    app.run(debug=True)
