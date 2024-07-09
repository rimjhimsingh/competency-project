from flask import Flask, send_file, render_template, request
import plotly.graph_objects as go
import pandas as pd
import io

app = Flask(__name__)

# Assuming your data is loaded here globally
path = 'data/simple-data.csv'  # Update this path
data = pd.read_csv(path, header=None)

def plot_student_competency_scores_plotly(data, student_id, competency_index):
    # Similar function as you provided, returning the figure instead of showing it
    # Add your function here
     # Filter rows that contain the word 'Competency' in the first column to identify competency names
    competency_names = data[0].str.extract(r'(Competency \d+\.\d+)')[0].dropna().unique()

    # Filter data for the specific student
    student_data = data[data[0].str.contains(student_id, na=False)]

    # Get target scores for each competency
    targets = data[data[0].str.strip().str.lower() == 'target']

    fig = go.Figure()

    for i in range(len(student_data)):
        student_score = student_data.iloc[i, 3]  # stores the current score of the student
        competency = competency_names[i]  # correct
        target_score = targets.iloc[i, 3]
        deviation = int(student_score) - int(target_score)

        if deviation == 0:
            message = "Right on track!"  # Changed message for deviation 0
        elif deviation > 0:
            message = "Great work, slow down!"
        else:
            message = "Keep working hard!"

        fig.add_trace(go.Scatter(
            x=[0, deviation],
            y=[competency, competency],
            mode='lines+markers',
            name=competency,
            text=[f"Student: {student_score}, Target: {target_score}, {message}", f"Student: {student_score}, Target: {target_score}, {message}"],
            hoverinfo='text',
            marker=dict( size=[12, 16 if deviation == 0 else 12], color='#887BB0' if deviation > 0 else ('#FB6090' if deviation < 0 else 'yellow')),

            line=dict(width=1.5, dash='solid' if deviation != 0 else 'solid')
        ))

    fig.update_layout(
        title=f"Difference graph for Spring 1 {student_id}",
        xaxis_title="Deviation from Target",
        yaxis_title="Competency",
        xaxis=dict(
            zeroline=True,
            zerolinewidth=3,
            zerolinecolor='#7CF3A0',
            gridcolor='#D3D3D3',
            range=[-4, 4],
            tickvals=[-4, -3, -2, -1, 0, 1, 2, 3, 4],
            ticktext=['-4', '-3', '-2', '-1', 'Right on track!', '1', '2', '3', '4'],
            tickfont=dict(color='black', size=12),
            linecolor='black',
            #
            mirror=True
        ),
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(len(competency_names))),
            ticktext=competency_names,
            gridcolor='#D3D3D3',
            tickfont=dict(color='black', size=15)
        ),
        legend=dict(title="Competencies", font=dict(color='black')),
        width=1000,
        height=600,
        plot_bgcolor='#fefae0',
        paper_bgcolor='#faedcd'

    )
    
    return fig

@app.route('/')
def index():
     return render_template('index.html')

@app.route('/plot/<student_id>/<int:competency_index>')
def plot_png(student_id, competency_index):
    fig = plot_student_competency_scores_plotly(data, student_id, competency_index)
    img_bytes = io.BytesIO()
    fig.write_image(img_bytes, format='png')
    img_bytes.seek(0)
    return send_file(img_bytes, mimetype='image/png')
plot_png('student 1 BD', data)


if __name__ == '__main__':
    app.run(debug=True)