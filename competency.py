from flask import Flask, render_template, request, send_file
import plotly.graph_objects as go
import io
import plotly.io as pio
import mysql.connector
import pandas as pd


app = Flask(__name__)

# Database configuration
db_config = {
    'user': 'rimjhim',  
    'password': 'DeckerCompetency2024',  
    'host': 'localhost',   
    'database': 'competencydata',  
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
#Feedback function

def fetch_student_feedback(student_id, semester):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Adjust the query to fetch the feedback columns for the student
    query = """
    SELECT feedback_1, feedback_2, feedback_3, feedback_4, feedback_5
    FROM StudentCompetencies
    WHERE student_id = %s AND semester_id = %s;
    """
    cursor.execute(query, (student_id, semester))
    feedback_data = cursor.fetchone()

    cursor.close()
    connection.close()

    return feedback_data


def plot_student_competency_scores_plotly(student_id, semester, target_scores_df):
    mapped_semester = semester_mapping[semester]
    student_data = fetch_student_data(student_id, semester)

    fig = go.Figure()
    valid_scores = {'B', 'E', 'P', 'C', 'NR', 'NA'}  # Set of valid scores
    def shorten_competency_name(competency_name):
        parts = competency_name.replace('competency_', '').split('_')
        return f"{parts[0]}.{parts[1]} {parts[2]}"
    
    shortened_labels = [shorten_competency_name(comp) for comp in target_scores_df.columns]
    print("helloo")

    for student in student_data:
        
        score_index = 4  
        zip_res = zip(target_scores_df.columns, shortened_labels)
        zip_list = list(zip_res)
        
        for comp, short_label in zip(target_scores_df.columns, shortened_labels):
            
            # Skip if the score is not valid or is feedback
            if student[score_index] not in valid_scores:
                score_index += 1

            student_score = grade_mapping[student[score_index]]  # Convert letter grade to number
            competency_name = short_label 
            target_score = grade_mapping[target_scores_df.loc[mapped_semester, comp]]  # Convert target score to number

            deviation = student_score - target_score
            message = "Right on track!" if deviation == 0 else "Great work, slow down!" if deviation > 0 else "Keep working hard!"

            # Plot each point with the appropriate deviation and message
            fig.add_trace(go.Scatter(
                x=[0, deviation],
                y=[short_label, short_label],
                mode='lines+markers',
                showlegend=False,
                name=competency_name,
                text=f"Student: {student[score_index]}, Target: {target_scores_df.loc[mapped_semester, comp]}, {message}",
                hoverinfo='text',
                marker=dict(size=[12, 16 if deviation == 0 else 12], color='#887BB0' if deviation > 0 else ('#FB6090' if deviation < 0 else '#7CF3A0')),
                line=dict(width=1.5, dash='solid' if deviation != 0 else 'solid')
            ))

            score_index += 1 
            
    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=12, color='yellow'),
        showlegend=True,
        name='Right on track'  
    ))

    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=12, color='#FB6090'),
        showlegend=True,
        name='Needs more work' 
    ))

    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=12, color='#887BB0'),
        showlegend=True,
        name='Slow down!'
    ))
    fig.update_layout(
    title=f"Comprehensive graph sample student",
    xaxis_title="Deviation from Target",
    xaxis=dict(
        zeroline=True, 
        zerolinecolor='#fdff6b', 
        zerolinewidth=40 
        
    ),

    yaxis_title="Competency",
    plot_bgcolor='#fefae0',
    paper_bgcolor='#faedcd',
    height=1000,   
    width=1000    
)
    return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

def fetch_student_competency_data(student_id, competency_column):
    connection = get_db_connection()
    cursor = connection.cursor()

    query = f"""
    SELECT semester_id, {competency_column} 
    FROM studentcompetencies 
    WHERE student_id = %s
    """
    cursor.execute(query, (student_id,))
    student_data = cursor.fetchall()

    cursor.close()
    connection.close()
    return student_data

# Function to fetch target scores (assuming you have target scores in your CSV or database)
def fetch_target_competency_scores(competency_column):
    target_scores_df = load_target_scores()  
    return target_scores_df[competency_column]

def plot_student_competency_scores_comprehensive(student_id, competency_column, target_scores_df):
    """
    Plots a line graph using Plotly showing the scores of a specific student and the target scores for a specific competency.
    This function handles all semesters for the student.
    """
    semester_order = ['Fall 2024', 'Spring 2025', 'Summer 2025', 'Fall 2025',
                      'Spring 2026', 'Summer 2026', 'Fall 2026', 'Spring 2027', 'Summer 2027']

    score_order = ['NA', 'NR', 'B', 'E', 'P', 'C']
    score_mapping = {score: idx for idx, score in enumerate(score_order)}

    student_data = fetch_student_competency_data(student_id, competency_column)
    print(f"student_data: {student_data}")
    
    competency_name = competency_column  

    semesters = []
    student_scores = []
    target_scores = []

    for student in student_data:
        semester = student[0]  
        mapped_semester = semester_mapping[semester]  
        
        student_score = student[1]  
        target_score = target_scores_df.loc[mapped_semester, competency_column]  
        
        if student_score == 'NA':
            continue

        student_score_mapped = score_mapping.get(student_score, 0) 
        target_score_mapped = score_mapping.get(target_score, 0)  
        
        print(f"Semester: {semester}, Student Score: {student_score}, Target Score: {target_score}")

        semesters.append(semester)
        student_scores.append(student_score_mapped)
        target_scores.append(target_score_mapped)

    sorted_data = sorted(zip(semesters, student_scores, target_scores), key=lambda x: semester_order.index(x[0]))

    semesters, student_scores, target_scores = zip(*sorted_data)

    fig = go.Figure()    

    fig.add_trace(go.Scatter(
        x=semesters,
        y=student_scores,
        mode='lines+markers',
        name='Student Score',
        text=[f"Your Score: {s}" for s in student_scores],
        hoverinfo='text',
        marker=dict(color='Green', size=15),
        line=dict(color='Green', width=2)
    ))

    fig.add_trace(go.Scatter(
        x=semesters,
        y=target_scores,
        mode='lines+markers',
        name='Target Score',
        text=[f"Target: {t}" for t in target_scores],
        hoverinfo='text',
        marker=dict(color='Red', size=8),
        line=dict(color='Red', width=2)
    ))
    fig.add_trace(go.Scatter(
    x=[None], y=[None],  
    mode='markers',
    marker=dict(color='blue', size=5),
    name="NR: Needs Redirection"
))

    fig.add_trace(go.Scatter(
        x=[None], y=[None],  
        mode='markers',
        marker=dict(color='blue', size=5),
        name="B: Beginning"
    ))

    fig.add_trace(go.Scatter(
        x=[None], y=[None],  
        mode='markers',
        marker=dict(color='blue', size=5),
        name="E: Emerging"
    ))

    fig.add_trace(go.Scatter(
        x=[None], y=[None],  
        mode='markers',
        marker=dict(color='blue', size=5),
        name="P: Progressing"
    ))

    fig.add_trace(go.Scatter(
        x=[None], y=[None], 
        mode='markers',
        marker=dict(color='blue', size=5),
        name="C: Capable"
    ))

    fig.update_layout(
        title=f"Progression graph sample student",
        xaxis_title="Semesters",
        yaxis_title="Scores",
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(len(score_order))),  
            ticktext=score_order  
        ),
        plot_bgcolor='#fefae0',
        paper_bgcolor='#faedcd'
        #height=600,
        #width=600
    )

    return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')
@app.route('/')
@app.route('/index')
def index():
    student_id = 'B00768785'
    semester = 'Fall 2024' 
    target_scores_df = load_target_scores()
    feedback_data = fetch_student_feedback(student_id, semester) #call feedback function
    plot_html = plot_student_competency_scores_plotly(student_id, semester, target_scores_df)
    return render_template('/index.html', plot_html=plot_html, feedback_data=feedback_data)


@app.route('/about')
def about():
    return render_template('About.html')

@app.route('/contact')
def contact():
    return render_template('Contact.html')

@app.route('/progression')
@app.route('/progression')
def progression():
    student_id = 'B00768785'  
    competency_column = 'competency_1_1_mid'  

    target_scores_df = load_target_scores()

    plot_html = plot_student_competency_scores_comprehensive(student_id, competency_column, target_scores_df)

    return render_template('progression.html', plot_html=plot_html)

@app.route('/plot/<student_id>')
def plot_png(student_id):
    plot_type = request.args.get('type', 'plotly')
    semester = "Fall 2024" 
    target_scores_df = load_target_scores()
    html_content = plot_student_competency_scores_plotly(student_id, semester, target_scores_df)

    return html_content

# Route for the comprehensive plot
@app.route('/comprehensive_plot/<student_id>/<competency_index>')
def comprehensive_plot(student_id, competency_index):
    plot_html = plot_student_competency_scores_comprehensive(student_id, int(competency_index))
    return render_template('comprehensive_plot.html', plot_html=plot_html)


if __name__ == '__main__':
    app.run(debug=True)
