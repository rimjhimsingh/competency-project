# Flask Application for Student Competency Tracking

## Overview
This Flask application is designed to manage and visualize student competency data across various semesters. It integrates with a MySQL database to fetch student scores and uses Plotly for dynamic data visualization. The application offers interactive web pages to view student progress and analyze deviations from target scores.

## Key Features

### Data Management
- **Database Connectivity**: Establishes connections to a MySQL database where student competencies are stored, ensuring data is up-to-date and accessible.
- **Data Retrieval**: Fetches specific student data based on semester and student ID, allowing for detailed analysis of student performance over time.

### Visualization
- **Plotly Integration**: Utilizes Plotly to create interactive graphs that display student scores against target scores across different semesters.
- **Dynamic Web Pages**: Provides web pages that dynamically render visualization graphs, enhancing user interaction and data accessibility.

### Web Routes
- **Home and Index Pages**: Displays the main page of the web application where users can view the default plot for a predefined student and semester.
- **About and Contact Pages**: Contains informational content about the application and contact details.
- **Progression View**: Shows a comprehensive plot for student progression in a particular competency over time, highlighting areas of improvement or concern.
- **Plot Generation**: Offers a route to generate plots dynamically based on the student ID and selected semester or competency.

## Application Structure

### Core Functions
- **`get_db_connection()`**: Manages database connections, facilitating secure and efficient database interactions.
- **`load_target_scores()`**: Loads target scores from a CSV file, which are used as benchmarks for evaluating student performance.
- **`fetch_student_data()`**: Retrieves specific data for a student for a given semester, aiding in detailed performance analysis.
- **`plot_student_competency_scores_plotly()`**: Generates a Plotly graph for a given student and semester, illustrating the deviation from target scores.
- **`plot_student_competency_scores_comprehensive()`**: Creates a line graph showing a student's performance across all semesters for a specified competency.

## Usage Instructions

### Accessing Different Sections
- Navigate to `/` or `/index` for the main dashboard.
- Visit `/about` for information about the application.
- Go to `/contact` for contact details and support.
- Access `/progression` to view the comprehensive performance plot of a predefined student.


## Summary
This Flask application serves as a powerful tool for educational institutions to monitor and assess student competencies dynamically. With integrated data visualization, the application helps educators and administrators make informed decisions based on comprehensive data analysis.
