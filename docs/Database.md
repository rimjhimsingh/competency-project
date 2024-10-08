# Database Structure Documentation

## Database Overview
The `competencydata` database is designed to store and manage detailed student competency data across multiple semesters. It provides comprehensive tracking of student progress in various academic competencies, enabling faculty and administrators to analyze performance trends and offer targeted educational interventions.

## Primary Table: `StudentCompetencies`
This table is the central repository for all data related to student assessments regarding their competencies throughout their academic tenure.

### Fields Description

#### 1. `student_id`
- **Type**: VARCHAR
- **Purpose**: Serves as a unique identifier for each student, facilitating individual tracking and record management. It may act as a primary key or part of a composite key within the database.
- **Usage**: Essential for linking student-specific data across various semesters and competency evaluations.

#### 2. `student_name`
- **Type**: VARCHAR
- **Purpose**: Records the full legal name of the student for identification and administrative purposes.
- **Usage**: Utilized in reporting and personalized communications.

#### 3. `cohort`
- **Type**: VARCHAR
- **Purpose**: Identifies the cohort or batch of the student, typically indicating the year of entry or program enrollment.
- **Usage**: Key for cohort-specific analyses and historical data tracking.

#### 4. `semester_id`
- **Type**: VARCHAR
- **Purpose**: Indicates the specific semester and year relevant to the recorded data.
- **Usage**: Critical for temporal analysis and understanding the progression of student competencies over time.

#### 5. Competency Scores (Various Fields)
- **Type**: DECIMAL or FLOAT
- **Purpose**: These fields store numerical scores reflecting student performance in specific competencies assessed mid-semester and at the end.
- **Examples**:
  - `competency_1_1_mid`
  - `competency_1_1_end`
  - and so forth for each assessed competency.
- **Usage**: Fundamental for detailed performance tracking and evaluation of educational outcomes.

#### 6. Feedback Fields (Various Fields)
- **Type**: TEXT
- **Purpose**: To store textual feedback associated with each competency group, providing qualitative insights into student performance.
- **Examples**:
  - `feedback_1`
  - `feedback_2`
- **Usage**: Enhances quantitative data with qualitative analysis, supporting comprehensive performance reviews.

## Functional Capabilities
- **Data Insertion**: Supports the insertion of new student competency records for each semester, ensuring that all student evaluations are recorded systematically.
- **Data Update**: Facilitates the updating of existing records to reflect the latest evaluations and corrections, ensuring data accuracy and relevance.
- **Data Retrieval**: Includes functionalities such as:
  - `get_student_competency_data(student_id, competency_id)`: Retrieves a student's scores across all semesters for a specified competency.
  - `get_student_scores_for_semester(student_id, semester_id)`: Fetches a complete set of competency scores and feedback for a specified semester.

## Schema Implications
- **Normalization**: The design exhibits a high degree of normalization to avoid data redundancy, ensuring that each piece of information is stored only once and referenced elsewhere as needed.
- **Scalability**: Capable of scaling to accommodate an increased number of students, semesters, and new competencies without performance degradation.
- **Flexibility**: The schema's flexible design allows for easy modifications to adapt to evolving educational assessment needs, such as adding new competencies or adjusting feedback mechanisms.

## Conclusion
The `competencydata` database is a robust solution for educational institutions requiring detailed tracking and analysis of student competencies. Its design supports effective data management practices, facilitating advanced analytics capabilities that can inform strategic educational decisions and interventions.
