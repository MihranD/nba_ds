import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns
import numpy as np

def show_preprocessing_page():
  st.write("## Pre-processing and feature engineering")
  
  # Read the dataset into a DataFrame
  df = read_df()

  # Presentation of data
  st.write("Display the first few rows of the dataset:")
  st.dataframe(df.head(10))
  st.write("Size of the dataset (number of rows and columns):")
  st.write(df.shape)
  st.write("---")
  
  if st.checkbox("Show the structure of the dataset"):
    st.dataframe(df.describe())
  st.write("---")
  
  st.markdown("If there are missing values, options are: include imputation, deletion, or using default values depending on the context.")
  if st.checkbox("Show missing values"):
    st.dataframe(df.isnull().sum())
    st.write("We don't have any missing values.")
  st.write("---")

  st.markdown("If there are duplicated values, we can remove it.")
  if st.checkbox("Show duplicates"):
    num_duplicates = df.duplicated().sum()
    st.write(f"Number of duplicate rows: {num_duplicates}")
    st.write("We don't have any duplicated values.")
  st.write("---")

  if st.checkbox("Show the big picture of the data to see what kind of dataset we have."):
    show_df_big_picture(df)

  # Distributions of variables
  if st.checkbox("Show distributions of variables"):
    df['Game Date'] = pd.to_datetime(df['Game Date'], format='%Y%m%d')
    min_date = df['Game Date'].min()
    max_date = df['Game Date'].max()
    st.write(f"Our data looks at the time period from {min_date.year} to {max_date.year}")
  st.write("---")

  # Balanced/imbalanced Dataset
  st.write("### Balanced/imbalanced Dataset")
  st.markdown('''
To check if the dataset is balanced in terms of shot made and shot missed instances, we can calculate the proportion of shots made (positive class) versus shots missed (negative class) in the dataset. Let's perform this analysis:
              ''')
  if st.checkbox("Proportion of shots made and shots missed") :
    # Compute and retrieve the cached value counts
    st.dataframe(compute_proportion_of_shots(df))
  st.markdown('''
The dataset displays a proportion of shots made at around 0.45 and shots missed at 0.55, suggesting a slight imbalance in class distribution. However, with a difference of only 0.1 between the two proportions, some may not consider it significantly imbalanced. In instances where the split between classes is close to 50/50, explicit balancing techniques like oversampling or undersampling may not be necessary. Given these considerations, we can interpret the dataset as balanced and proceed accordingly.
              ''')

  # Outliers
  st.write("### Outliers")
  st.markdown('''
Identify if there are any outliers in the dataset, especially in numerical features like shot distance, X and Y locations. Outliers might affect the model's performance and need to be handled appropriately, for example, by removing them or transforming them using some techniques.
              ''')
  if st.checkbox("Show outliers using IQR method"):
    c = st.container()
    show_outlier_plots(df)
    show_outlier_texts(df)
    st.markdown("")
    styled_text = "<span style='font-size:14px'>It seems that the outliers identified statistically may not necessarily reflect true anomalies in the data, as certain locations and distances are indeed realistic in the context of basketball shots. While shots taken from distances greater than 50 feet may be statistically considered outliers due to their low frequency, they actually indicate a scarcity of attempts from such distances. Similarly, Y location values exceeding 350 feet may appear as statistical outliers, but they represent realistic shooting positions. As for the X location, although there are fewer data points observed on both sides (left and right) beyond +/-220 feet, these values are genuine and should be taken into account when building models.</span>"
    st.markdown(styled_text, unsafe_allow_html=True)
    st.write("---")

  st.markdown('''
Let's explore shot distance accuracy through visualization.
              ''')
  shot_distance_accuracy(df)
  st.markdown('''
The graph above shows something interesting about how accurate NBA players are with their shots. Usually, we expect accuracy to drop as the shot gets farther from the basket. But between 5 to 25 feet away, accuracy stays about the same. There could be a few reasons. Players practice free throws a lot, which are taken from 15 feet away, so they're pretty good at shots from nearby distances. Also, defenders guard differently depending on how close the shooter is to the basket, which might make closer shots harder. But between 5 to 25 feet, these factors seem to balance out. So, even though we might think farther shots are always harder, this graph shows that's not always the case. It gives us a new perspective on how distance affects shooting accuracy.

In terms of outliers, the extreme value observed at the far right end of the graph, with an accuracy of approximately 0.18 points, could be considered an outlier. This is likely a scenario where a player hastily attempts a long-range shot as time expires, resulting in a low success rate. While these shots occasionally find success, they occur infrequently.
              ''')

  # Normalization and Standardization
  st.write("### Normalization and Standardization")
  st.markdown('''
During the data exploration phase, we are primarily focused on understanding the data distribution, identifying outliers, and gaining insights into feature relationships. We will not perform normalization and standardization during this phase as they can alter the data distribution and make it harder to interpret visualizations. Therefore, we will skip normalization and standardization during data exploration and apply them later during preprocessing, just before training the model.
              ''')

# Define a cached function to compute and cache the value counts
@st.cache_data
def compute_proportion_of_shots(df):
  return df['Shot Made Flag'].value_counts(normalize=True).head()

@st.cache_data
def read_df():
  df = pd.read_csv('NBA Shot Locations 1997 - 2020.csv')
  return df

# Define the numerical features for outlier detection
numerical_features = ['Shot Distance', 'X Location', 'Y Location']

@st.cache_data
def show_outlier_texts(df):
  # Detect outliers
  outliers_list = detect_outliers_iqr(df, numerical_features)

  shot_distance = str(len(outliers_list[0])) + ' outliers'
  x_location = str(len(outliers_list[1])) + ' outliers'
  y_location = str(len(outliers_list[2])) + ' outliers'
  col1, col2, col3 = st.columns(3)
  col1.write(f"<div style='text-align: center;'>{shot_distance}</div>", unsafe_allow_html=True)
  col2.write(f"<div style='text-align: center;'>{x_location}</div>", unsafe_allow_html=True)
  col3.write(f"<div style='text-align: center;'>{y_location}</div>", unsafe_allow_html=True)
  
# Function to detect outliers using IQR method
@st.cache_data
def detect_outliers_iqr(df, features):
  outliers = []
  for feature in features:
    Q1 = df[feature].quantile(0.25)
    Q3 = df[feature].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    feature_outliers = df[(df[feature] < lower_bound) | (df[feature] > upper_bound)]
    outliers.append(feature_outliers)
  return outliers

@st.cache_data
def show_outlier_plots(df):
  # Create box plots for numerical features
  fig = plt.figure(figsize = (12, 6))
  for i, feature in enumerate(numerical_features):
    plt.subplot(1, len(numerical_features), i + 1)
    sns.boxplot(y = df[feature])
    plt.title(f'Boxplot of {feature}')
  plt.tight_layout()
  st.pyplot(fig)

@st.cache_data
def shot_distance_accuracy(df):
  shot_count_by_distance = df.groupby('Shot Distance')['Shot Made Flag'].agg(['sum', 'count'])

  # Calculate accuracy for each shot distance
  shot_accuracy_by_distance = shot_count_by_distance['sum'] / shot_count_by_distance['count']

  fig = plt.figure(figsize = (10, 6))

  # Plotting accuracy
  plt.scatter(x = shot_accuracy_by_distance.index, 
              y = shot_accuracy_by_distance.values, 
              color = 'blue', alpha = 0.5)
  plt.title('Shot Accuracy by Distance')
  plt.xlabel('Shot Distance (feet)')
  plt.ylabel('Accuracy')
  plt.tight_layout()
  plt.grid(True)
  st.pyplot(fig)

@st.cache_data
def show_df_big_picture(df):
  # Create column name as index and data type column
  data_audit = pd.DataFrame(df.dtypes, columns = ['data_type'])
  # Create target column, if 0, row is not a target if 1, row is a target
  data_audit['target'] = 0 
  data_audit.loc[data_audit.index == 'Shot Made Flag', 'target'] = 1
  descriptions = [
  'Unique id assigned to every game',
  'Unique id assigned to every event within a game',
  'Unique id assigned to each player',
  'Shooting Players full name',
  'Unique id assigned to each team',
  'The team of the player taking the shot',
  'The period of the game (out of four); each period is 12 minutes',
  'Minutes remaining in period (out of 12)',
  'Seconds remaining in period-minute combination (out of 60)',
  'Type of shot (ex. Jump Shot, Layup, Hookshot, Dunk, etc)',
  'Either 2pt or 3pt shot',
  'General location of shot (ex. Left Corner 3, Mid-range, etc)',
  'Area/Direction of shot (ex. Center, Left Side, etc)',
  'Grouping of shots based on range (ex. 8-16ft, 16-24ft, etc)',
  'Exact distance of shot in feet',
  'Location of shot as X coordinate',
  'Location of shot as Y coordinate',
  '1 (made shot) or 0 (missed shot)',
  'Date of game',
  'Team name of the home team',
  'Team name of the away team',
  'Regular Season or Playoffs'
  ]
  # Create a data description column
  data_audit['description'] = descriptions
  # Create a column with missing data in %
  data_audit['missing_data'] = np.round((df.isna().sum() / len(df)) * 100,2)
  # Create a type data classifying data into date, categorical or quantitative
  data_audit.loc[data_audit['data_type'] == 'int64', 'type'] = 'quantitative'
  data_audit.loc[data_audit['data_type'] == 'object', 'type'] = 'categorical'
  data_audit.loc[data_audit.index == 'Game Date', 'type'] = 'date'
  # Create a column which describe categories 
  periods = f'{sorted(df["Period"].unique())}'
  shot_types = f'{df["Shot Type"].unique()}'
  shot_zone_basics = f'{df["Shot Zone Basic"].unique()}'
  shot_zone_areas = f'{df["Shot Zone Area"].unique()}'
  shot_zone_ranges = f'{df["Shot Zone Range"].unique()}'
  season_types = f'{df["Season Type"].unique()}'
  data_audit.loc[data_audit.index == 'Team Name', 'category'] = "37 teams (ex. Washington Wizards, etc)"
  data_audit.loc[data_audit.index == 'Period', 'category'] = periods
  data_audit.loc[data_audit.index == 'Period', 'category'] = periods
  data_audit.loc[data_audit.index == 'Action Type', 'category'] = "70 types (ex. Jump Shot, Layup, Hookshot, Dunk, etc)"
  data_audit.loc[data_audit.index == 'Shot Type', 'category'] = shot_types
  data_audit.loc[data_audit.index == 'Shot Zone Basic', 'category'] = shot_zone_basics
  data_audit.loc[data_audit.index == 'Shot Zone Area', 'category'] = shot_zone_areas
  data_audit.loc[data_audit.index == 'Shot Zone Range', 'category'] = shot_zone_ranges
  data_audit.loc[data_audit.index == 'Home Team', 'category'] = "37 teams (ex. LAL, ATL, etc)"
  data_audit.loc[data_audit.index == 'Away Team', 'category'] = "37 teams (ex. LAL, ATL, etc)"
  data_audit.loc[data_audit.index == 'Season Type', 'category'] = season_types
  data_audit.loc[data_audit.index == 'Shot Made Flag', 'category'] = "[1, 0]"
  # Create comment column 
  data_audit.loc[data_audit.index == 'Game Date', 'comment'] = "Should be datetime"
  # Display data_audit and descriptive statistics 
  st.write(data_audit)