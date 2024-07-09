from flask import Flask, send_file, render_template, request
import plotly.graph_objects as go
import pandas as pd
import io
import plotly.io as pio

app = Flask(__name__)

path = 'data/simple-data.csv'
data = pd.read_csv(path, header=None)

def plot_student_competency_scores_plotly(data, student_id):
    
    competency_names = data[0].str.extract(r'(Competency \d+\.\d+)')[0].dropna().unique()

    
    student_data = data[data[0].str.contains(student_id, na=False)]

    
    targets = data[data[0].str.strip().str.lower() == 'target']

    fig = go.Figure()

    for i in range(len(student_data)):
        student_score = student_data.iloc[i, 3]
        competency = competency_names[i]
        target_score = targets.iloc[i, 3]
        deviation = int(student_score) - int(target_score)

        message = "Right on track!" if deviation == 0 else "Great work, slow down!" if deviation > 0 else "Keep working hard!"

        fig.add_trace(go.Scatter(
            x=[0, deviation],
            y=[competency, competency],
            mode='lines+markers',
            name=competency,
            text=f"Student: {student_score}, Target: {target_score}, {message}",
            hoverinfo='text',
            marker=dict(size=[12, 16 if deviation == 0 else 12], color='#887BB0' if deviation > 0 else ('#FB6090' if deviation < 0 else 'yellow')),
            line=dict(width=1.5, dash='solid' if deviation != 0 else 'solid')
        ))

    fig.update_layout(
        title=f"Difference graph for {student_id}",
        xaxis_title="Deviation from Target",
        yaxis_title="Competency",
        xaxis=dict(
            zeroline=True, zerolinewidth=3, zerolinecolor='#7CF3A0',
            gridcolor='#D3D3D3', range=[-4, 4],
            tickvals=[-4, -3, -2, -1, 0, 1, 2, 3, 4],
            ticktext=['-4', '-3', '-2', '-1', 'Right on track!', '1', '2', '3', '4'],
            tickfont=dict(color='black', size=12),
            linecolor='black', mirror=True
        ),
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(len(competency_names))),
            ticktext=competency_names,
            gridcolor='#D3D3D3',
            tickfont=dict(color='black', size=15)
        ),
        legend=dict(title="Competencies"),
        #width=800, height=600, # removing the height component here
        plot_bgcolor='#fefae0', paper_bgcolor='#faedcd'
    )

    return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')
def plot_student_competency_scores_comprehensive(data, student_name, competency_index):
    """
    Plots a line graph using Plotly showing the scores of a specific student and the target scores for a specific competency.
    Adds customized hover text to indicate performance status.

    Parameters:
    - data: pandas.DataFrame containing the data
    - student_name: str, the name of the student
    - competency_index: int, the index of the competency (0-indexed)
    """

    # this is hardcoded for rows and columns need to be made general
    # Assuming each competency block spans 7 rows including the title row

    start_row = competency_index * 7 + 1  
    end_row = start_row + 6  

   
    df = data.iloc[start_row:end_row, :]
    competency_name = data.iloc[start_row - 1, 0]  

    columns = df.columns[1:]  
    student_scores = df[df.iloc[:, 0].str.contains(student_name)].iloc[:, 1:].astype(float).squeeze()
    target_scores = df[df.iloc[:, 0].str.contains('target', case=False)].iloc[:, 1:].astype(float).squeeze()

    
    hover_texts = [f"Score: {s} (On track!)" if s == t else (f"Score: {s} (Good job!)" if s > t else f"Score: {s} (Keep working!)")
                   for s, t in zip(student_scores, target_scores)]

    
    fig = go.Figure()

    
    fig.add_trace(go.Scatter(
        x=columns,
        y=student_scores,
        mode='lines+markers',  
        name='Student Scores',
        text=hover_texts,
        hoverinfo='text',
        marker=dict(color='Green', size=15),
        line=dict(color='Green', width=2)  
    ))

    fig.add_trace(go.Scatter(
        x=columns,
        y=target_scores,
        mode='lines+markers',
        name='Target Scores',
        text=[f"Target: {t}" for t in target_scores],
        hoverinfo='text',
        marker=dict(color='Red', size=8),
        line=dict(color='Red', width=2)
    ))

    fig.update_layout(
        title=f'Performance: {competency_name} - {student_name} vs Target',
        xaxis_title='Semesters',
        yaxis_title='Scores',
        legend_title='Legend',
        hovermode='closest',
        # width=1000,
        # height=600, # removing the size here
        plot_bgcolor='#fefae0',
        paper_bgcolor='#faedcd'
    )

    return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

@app.route('/')
@app.route('/index')
def index():
    student_id= 'student 1 BD'
    plot_html = plot_student_competency_scores_plotly(data, student_id)
    return render_template('index.html', plot_html=plot_html)

@app.route('/about')
def about():
    return render_template('About.html')

@app.route('/contact')
def contact():
    return render_template('Contact.html')
@app.route('/deviation')
def deviation():
    student_id = 'student 1 BD'
    plot_html = plot_student_competency_scores_comprehensive(data, student_id, 0)
    return render_template('deviation.html', plot_html=plot_html)
    

@app.route('/plot/<student_id>')
def plot_png(student_id):
    plot_type = request.args.get('type', 'plotly')  
    if plot_type == 'comprehensive':
        fig = plot_student_competency_scores_comprehensive(data, student_id, 0)
    else:
        fig = plot_student_competency_scores_plotly(data, student_id)

    img_bytes = io.BytesIO()
    fig.write_image(img_bytes, format='png')
    img_bytes.seek(0)
    return send_file(img_bytes, mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=True)