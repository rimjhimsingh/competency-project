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
    xaxis=dict(
        zeroline=True,  # Show the zeroline
        zerolinecolor='#7CF3A0',  # Set the color of the zeroline
        zerolinewidth=6  # Set the width of the zeroline
    ),

    yaxis_title="Competency",
    plot_bgcolor='#fefae0',
    paper_bgcolor='#faedcd',
    height=1000,   
    width=1000    
)
    return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')
#functions for comprehensive
# Function to fetch student competency data for a specific column (competency)
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
    target_scores_df = load_target_scores()  # Assuming this loads the target scores from a CSV file
    return target_scores_df[competency_column]
def plot_student_competency_scores_comprehensive(student_id, competency_column, target_scores_df):
    """
    Plots a line graph using Plotly showing the scores of a specific student and the target scores for a specific competency.
    This function handles all semesters for the student.
    """
    # Define the order of semesters you want to display in the plot
    semester_order = ['Fall 2024', 'Spring 2025', 'Summer 2025', 'Fall 2025',
                      'Spring 2026', 'Summer 2026', 'Fall 2026', 'Spring 2027', 'Summer 2027']

    # Define the y-axis order for scores and map scores to their respective indices
    score_order = ['NA', 'NR', 'B', 'E', 'P', 'C']
    score_mapping = {score: idx for idx, score in enumerate(score_order)}

    # Fetch the student's score for the competency across all semesters
    student_data = fetch_student_competency_data(student_id, competency_column)
    print(f"student_data: {student_data}")
    
    competency_name = competency_column  # Using competency_column as the name

    semesters = []
    student_scores = []
    target_scores = []

    # Collect semesters, student scores, and target scores
    for student in student_data:
        semester = student[0]  # First element is the semester_id
        mapped_semester = semester_mapping[semester]  # Map to generic semester names for target scores
        
        student_score = student[1]  # Student score for this semester
        target_score = target_scores_df.loc[mapped_semester, competency_column]  # Get the target score
        
        # Skip if student score or target score is 'NA'
        if student_score == 'NA':
            continue


        # Map the scores to their numeric indices
        student_score_mapped = score_mapping.get(student_score, 0)  # Map letter grade to index
        target_score_mapped = score_mapping.get(target_score, 0)  # Map target score to index
        
        # Debug: Check collected data
        print(f"Semester: {semester}, Student Score: {student_score}, Target Score: {target_score}")

        semesters.append(semester)
        student_scores.append(student_score_mapped)
        target_scores.append(target_score_mapped)

    # Sort the data based on the predefined semester order
    sorted_data = sorted(zip(semesters, student_scores, target_scores), key=lambda x: semester_order.index(x[0]))

    # Unzip the sorted data
    semesters, student_scores, target_scores = zip(*sorted_data)

    # Create the Plotly figure
    fig = go.Figure()    

    # Plot student's scores
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

    # Plot target scores
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
    x=[None], y=[None],  # No actual data points
    mode='markers',
    marker=dict(color='blue', size=5),
    name="NR: Needs Redirection"
))

    fig.add_trace(go.Scatter(
        x=[None], y=[None],  # No actual data points
        mode='markers',
        marker=dict(color='blue', size=5),
        name="B: Beginning"
    ))

    fig.add_trace(go.Scatter(
        x=[None], y=[None],  # No actual data points
        mode='markers',
        marker=dict(color='blue', size=5),
        name="E: Emerging"
    ))

    fig.add_trace(go.Scatter(
        x=[None], y=[None],  # No actual data points
        mode='markers',
        marker=dict(color='blue', size=5),
        name="P: Progressing"
    ))

    fig.add_trace(go.Scatter(
        x=[None], y=[None],  # No actual data points
        mode='markers',
        marker=dict(color='blue', size=5),
        name="C: Capable"
    ))

    # Update the layout of the plot with a manual y-axis category order
    fig.update_layout(
        title=f"Performance: {competency_name} - {student_id} vs Target",
        xaxis_title="Semesters",
        yaxis_title="Scores",
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(len(score_order))),  # Numeric values for the y-axis
            ticktext=score_order  # Corresponding labels for the y-axis
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
    plot_html = plot_student_competency_scores_plotly(student_id, semester, target_scores_df)
    return render_template('/index.html', plot_html=plot_html)


@app.route('/about')
def about():
    return render_template('About.html')

@app.route('/contact')
def contact():
    return render_template('Contact.html')

@app.route('/progression')
@app.route('/progression')
def progression():
    student_id = 'B00768785'  # Replace with actual student ID
    # competency_column = '1.1 mid'  # Specify the competency column
    competency_column = 'competency_1_1_mid'  # Specify the competency column
    

    # Load the target scores
    target_scores_df = load_target_scores()

    # Generate the comprehensive plot
    plot_html = plot_student_competency_scores_comprehensive(student_id, competency_column, target_scores_df)

    # Render the 'progression.html' template, passing the plot HTML
    return render_template('progression.html', plot_html=plot_html)

@app.route('/plot/<student_id>')
def plot_png(student_id):
    plot_type = request.args.get('type', 'plotly')
    semester = "Fall 2024"  # This might be dynamically determined or passed as an argument
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
