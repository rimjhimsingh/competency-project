# import pandas as pd

# # Load the CSV file
# path = 'C:/Users/rsingh16/Desktop/competency project/data/target-scores.csv'  # Update with your actual file path
# # df = pd.read_csv(path)

# # Ensure this path matches your file location
# target_scores_df = pd.read_csv(path)
# # target_scores_df.set_index('Semester', inplace=True)
# print(target_scores_df)


# # Print the column headers
# print(df.columns)


import pandas as pd


path = 'C:/Users/rsingh16/Desktop/competency project/data/target-scores.csv'
# Ensure this path matches your file location
# If your column headers start on the first row (usually row 0 in Python), and the 'Semesters' column is indeed labeled as such
target_scores_df = pd.read_csv(path)
# Set 'Semesters' as the index if that's the correct name in your CSV
target_scores_df.set_index('Semesters', inplace=True)
print(target_scores_df)
print(target_scores_df)
