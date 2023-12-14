import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# open the data
pisa_Mean_scores = pd.read_csv("archive/Pisa mean performance scores 2013 - 2015 Data.csv")

# create interface
st.set_page_config(layout="wide")
st.sidebar.title("Filters")

# select the visualization
vis = st.sidebar.radio("Select Your Question:",
                     options=["Question 1",
                              "Question 2",
                              "Question 3"])
pisa_Mean_scores = pisa_Mean_scores.drop(['2013 [YR2013]', '2014 [YR2014]', 'Country Code', 'Series Code'], axis=1)

# Question 1: Which gender performed better in different subjects in 2015?
if vis=="Question 1":
    #Create interface for Q1
    # Create title
    st.title("Question 1: Which gender performed better in different subjects in 2015?")

    # Filter the DataFrame to keep only male and female scores in 2015
    series_gender_scale = ["PISA: Mean performance on the mathematics scale. Female",
                            "PISA: Mean performance on the mathematics scale. Male",
                            "PISA: Mean performance on the reading scale. Female",
                            "PISA: Mean performance on the reading scale. Male",
                            "PISA: Mean performance on the science scale. Female",
                            "PISA: Mean performance on the science scale. Male"]
    filtered_data = pisa_Mean_scores[pisa_Mean_scores['Series Name'].isin(series_gender_scale)]
    #filtered_data = pisa_Mean_scores[(pisa_Mean_scores['Series Name'].str.contains('Male') | pisa_Mean_scores[
        #'Series Name'].str.contains('Female')) & (pisa_Mean_scores['2015 [YR2015]'].notnull())]

    # Extract subject information from "Series Name" and create a new "Subject" column，首先splitPISA: Mean Performance on the"，然后取分割后的第一个部分，再以"scale"为分割符，最后取分割后的第一个部分。
    filtered_data['Subject'] = \
        filtered_data['Series Name'].str.split('PISA: Mean performance on the ').str[1].str.split(' scale').str[0]
    # 另一种表达，用正则表达式：filtered_data['Subject'] = filtered_data['Series Name'].str.extract(r'PISA: Mean performance on the (\w+) scale')

    # Create a new "Gender" column based on the information in "Series Name"
    #filtered_data['Gender'] = \
        #filtered_data['Series Name'].apply(lambda x: 'Female' if 'Female' in x else 'Male')
    #filtered_data['Gender'] = 'Male'
    #filtered_data.loc[filtered_data['Series Name'].str.contains('Female'), 'Gender'] = 'Female'
    filtered_data['Gender'] = np.where(filtered_data['Series Name'].str.contains('Female'), 'Female', 'Male')

    # Drop the "Series Name" column
    filtered_data = filtered_data.drop(columns=['Series Name','Country Name'])

    # Replace ".." with NaN in the "2015 [YR2015]" column
    filtered_data['2015 [YR2015]'] = filtered_data['2015 [YR2015]'].replace('..', np.nan)

    # Drop rows where "2015 [YR2015]" is N/A
    filtered_data = filtered_data.dropna(subset=['2015 [YR2015]'])

    # Convert the "2015 [YR2015]" column to numeric
    filtered_data['2015 [YR2015]'] = pd.to_numeric(filtered_data['2015 [YR2015]'], errors='coerce')

    # Group by "Subject" and "Gender" and calculate the mean
    average_scores = filtered_data.groupby(['Subject', 'Gender'])['2015 [YR2015]'].mean().reset_index()

    # Rename the "2015 [YR2015]" column to "Average Score"
    average_scores = average_scores.rename(columns={'2015 [YR2015]': 'Average Score'})

    # Checkbox for selecting subjects
    st.sidebar.markdown("Please select the subjects:")
    selected_math = st.sidebar.checkbox("Mathematics")
    selected_reading = st.sidebar.checkbox("Reading")
    selected_science = st.sidebar.checkbox("Science")

    # Create a list of selected subjects
    selected_subjects = []
    if selected_math:
        selected_subjects.append("mathematics")
    if selected_reading:
        selected_subjects.append("reading")
    if selected_science:
        selected_subjects.append("science")

    # Check if no subjects are selected
    if not selected_subjects:
        st.warning("Please select the subject first.")
    else:
        # Filter the DataFrame based on selected subjects
        filtered_scores = average_scores[average_scores['Subject'].isin(selected_subjects)]

        # Bar chart using Plotly Express
        fig = px.bar(filtered_scores, x='Gender', y='Average Score', color='Subject', barmode='group',
                     labels={'Average Score': 'Average Score'})

        #Set y-axis minimum value
        fig.update_yaxes(range=[430, filtered_scores['Average Score'].max()])

        # Display the chart
        st.plotly_chart(fig)

# Question 2: Which countries have the best/worst student performances in different subjects in 2015?
if vis == "Question 2":
    # Create interface for Q1
    # Create title
    st.title("Question 2: Which countries had the best/worst student performances in different subjects in 2015?")

    # Filter the DataFrame to keep only the desired Series Name
    series_scale = ["PISA: Mean performance on the mathematics scale",
                            "PISA: Mean performance on the reading scale",
                            "PISA: Mean performance on the science scale"]
    filtered_data = pisa_Mean_scores[pisa_Mean_scores['Series Name'].isin(series_scale)]

    # Extract subject information from "Series Name" and create a new "Subject" column
    filtered_data['Subject'] = \
    filtered_data['Series Name'].str.split('PISA: Mean performance on the ').str[1].str.split(' scale').str[0]

    # Drop the "Series Name" column
    filtered_data = filtered_data.drop(columns=['Series Name'])

    # Replace ".." with NaN in the "2015 [YR2015]" column
    filtered_data['2015 [YR2015]'] = filtered_data['2015 [YR2015]'].replace('..', np.nan)

    # Drop rows where "2015 [YR2015]" is N/A
    filtered_data = filtered_data.dropna(subset=['2015 [YR2015]'])

    # Group by 'Country Name' and calculate the sum of scores for all subjects
    filtered_data['2015 [YR2015]'] = filtered_data['2015 [YR2015]'].astype(
        float)  # Convert the '2015 [YR2015]' column to float type

    # 按国家分组，并计算每个国家在所有科目上的平均分
    country_averages = filtered_data.groupby('Country Name')['2015 [YR2015]'].mean().reset_index()
    country_averages['Subject'] = 'combined subjects'

    # 将平均分作为新行添加到原始数据集
    combined_data = pd.concat([filtered_data, country_averages], ignore_index=True)

    # 重命名列
    combined_data = combined_data.rename(columns={'2015 [YR2015]': 'Average Score'})

    # Add a multiselect to the sidebar for year selection
    selected_countries = st.sidebar.multiselect('Select the Country',options=combined_data['Country Name'].unique(),)

    # 在侧边栏添加复选框以筛选科目
    st.sidebar.markdown("Please select the subjects:")
    subjects = combined_data['Subject'].unique()
    selected_subjects = []
    for subject in subjects:
        if st.sidebar.checkbox(f'{subject}', value=True):  # 默认所有科目选中
            selected_subjects.append(subject)
    if not selected_subjects:
        st.warning("Please select the subjects first.")
    else:
        # Filter the DataFrame based on the selected country and subject
        filtered_df = combined_data[(combined_data['Country Name'].isin(selected_countries)) &
                                    (combined_data['Subject'].isin(selected_subjects))]

        # 在侧边栏添加单选按钮以选择排序方式
        sort_order = st.sidebar.radio("Sort Order",('Descending','Ascending'))

        # 根据用户选择的排序方式对数据进行排序
        if sort_order == 'Ascending':
            filtered_df = filtered_df.sort_values(by='Average Score', ascending=True)
        else:
            filtered_df = filtered_df.sort_values(by='Average Score', ascending=False)

        if not selected_countries:
            # 如果没有选择任何国家，则显示包含所有国家的柱状图
            if sort_order == 'Ascending':
                combined_data = combined_data.sort_values(by='Average Score', ascending=True)
            else:
                combined_data = combined_data.sort_values(by='Average Score', ascending=False)
            for subject in selected_subjects:
                subject_df = combined_data[combined_data['Subject'] == subject]

                fig = px.bar(subject_df,
                             x='Country Name',
                             y='Average Score',
                             title=f'Average Scores in {subject}')
                fig.update_yaxes(range=[300, subject_df['Average Score'].max()])
                st.plotly_chart(fig)
        else:
            # 为每个学科创建并显示一个柱状图
            for subject in selected_subjects:
                # 筛选特定学科和国家的数据
                subject_df = filtered_df[filtered_df['Subject'] == subject]

                # 创建柱状图
                fig = px.bar(subject_df,
                             x='Country Name',
                             y='Average Score',
                             title=f'Average Scores in {subject}')

                # Set y-axis minimum value
                fig.update_yaxes(range=[300, filtered_df['Average Score'].max()])
                st.plotly_chart(fig)
    # 在 Streamlit 应用中显示数据
        #st.write(filtered_df)

# Question 3: Which countries have the largest/smallest score differences between Male and Female Students
if vis=="Question 3":
    #Create interface for Q1
    # Create title
    st.title("Question 3: Which countries had the largest/smallest score differences between Male and Female Students?")

    # Filter the DataFrame to keep only male and female scores in 2015
    series_gender_scale = ["PISA: Mean performance on the mathematics scale. Female",
                            "PISA: Mean performance on the mathematics scale. Male",
                            "PISA: Mean performance on the reading scale. Female",
                            "PISA: Mean performance on the reading scale. Male",
                            "PISA: Mean performance on the science scale. Female",
                            "PISA: Mean performance on the science scale. Male"]
    filtered_data = pisa_Mean_scores[pisa_Mean_scores['Series Name'].isin(series_gender_scale)]

    # Extract学科信息，首先splitPISA: Mean Performance on the"，然后取分割后的第一个部分，再以"scale"为分割符，最后取分割后的第一个部分。
    filtered_data['Subject'] = \
        filtered_data['Series Name'].str.split('PISA: Mean performance on the ').str[1].str.split(' scale').str[0]
    # 提取出性别，用np.where在Series Name中查找包含female和male的值，然后提取出来放到新的一列
    filtered_data['Gender'] = np.where(filtered_data['Series Name'].str.contains('Female'), 'Female', 'Male')

    # Drop the "Series Name" column
    filtered_data = filtered_data.drop(columns=['Series Name'])

    # Replace ".." with NaN in the "2015 [YR2015]" column
    filtered_data['2015 [YR2015]'] = filtered_data['2015 [YR2015]'].replace('..', np.nan)

    # Drop rows where "2015 [YR2015]" is N/A
    filtered_data = filtered_data.dropna(subset=['2015 [YR2015]'])

    # Convert the "2015 [YR2015]" column to 变成 float形式
    filtered_data['2015 [YR2015]'] = filtered_data['2015 [YR2015]'].astype(float)  # Convert the '2015 [YR2015]' column to float type

    # 初始化用于存储差值的列表
    differences = []

    # 计算每个国家在每个科目的男女分数差值
    for subject in ['mathematics', 'reading', 'science']:
        # 筛选特定科目的数据
        subject_data = filtered_data[filtered_data['Subject'] == subject]

        # 分别获取男女学生的数据
        females = subject_data[subject_data['Gender'] == 'Female']
        males = subject_data[subject_data['Gender'] == 'Male']

        # 对每个国家计算分数差
        for country in females['Country Name'].unique():
            female_score = females[females['Country Name'] == country]['2015 [YR2015]'].values[0]
            male_score = males[males['Country Name'] == country]['2015 [YR2015]'].values[0]
            score_diff = female_score - male_score

            # 将差值信息添加到列表中
            differences.append({'Country Name': country, 'Subject': subject, '2015 [YR2015]': score_diff})

    # 使用列表创建一个新的 DataFrame
    differences_df = pd.DataFrame(differences)

    # 将 differences_df 添加到原始数据集中
    combined_data = pd.concat([filtered_data, differences_df], ignore_index=True)

    # 仅保留 Gender 列为 NaN 的行
    combined_data = combined_data[combined_data['Gender'].isna()]

    # 从 combined_data 中删除 Gender 列
    combined_data = combined_data.drop(columns=['Gender'])

    # 计算每个国家的所有学科的平均分差之和
    country_sum_diff = combined_data.groupby('Country Name')['2015 [YR2015]'].sum().reset_index()

    # 创建一个新的 DataFrame 用于存储每个国家的总分差
    total_differences = pd.DataFrame({
        'Country Name': country_sum_diff['Country Name'],
        'Subject': 'Combined subjects',
        '2015 [YR2015]': country_sum_diff['2015 [YR2015]']
    })

    # 将 total_differences 添加到 combined_data 中
    combined_data_with_total = pd.concat([combined_data, total_differences], ignore_index=True)

    # 将 '2015 [YR2015]' 列的数据转换为绝对值
    combined_data_with_total['2015 [YR2015]'] = combined_data_with_total['2015 [YR2015]'].abs()

    # 将 '2015 [YR2015]' 列重命名为 'Score Difference'
    combined_data_with_total = combined_data_with_total.rename(columns={'2015 [YR2015]': 'Score Difference'})

    # 筛选出 Subject 为 "Combined subjects" 的数据
    combined_subjects_data = combined_data_with_total[combined_data_with_total['Subject'] == 'Combined subjects']

    # Add a multiselect to the sidebar for country selection
    selected_countries = st.sidebar.multiselect('Select the Country', options=combined_subjects_data['Country Name'].unique())

    # 在侧边栏添加单选按钮以选择排序方式
    sort_order = st.sidebar.radio("Select Sort Order", ['Descending', 'Ascending'])

    # 检查是否有选中的国家
    if selected_countries:
        # 根据选中的国家过滤数据
        filtered_data_by_country = combined_subjects_data[
            combined_subjects_data['Country Name'].isin(selected_countries)]
    else:
        # 如果没有国家被选中，显示所有数据
        filtered_data_by_country = combined_subjects_data

    # 根据用户选择的排序方式对数据进行排序
    if sort_order == 'Ascending':
        filtered_data_by_country = filtered_data_by_country.sort_values(by='Score Difference', ascending=True)
    else:
        filtered_data_by_country = filtered_data_by_country.sort_values(by='Score Difference', ascending=False)

    # 创建一个柱状图以展示选中国家的分数差异
    fig = px.bar(filtered_data_by_country,
                 x='Country Name',
                 y='Score Difference',
                 title="Score Differences in Combined Subjects")

    # 展示柱状图
    st.plotly_chart(fig)

    # 显示筛选后的数据
    #st.write(filtered_data_by_country)










    #fig = px.bar(filtered_df,
    #             x='Country Name',
    #             y='Average Score',
    #            color='Subject',
    #            barmode='group',
    #            title='Average Scores by Country and Subject')



    #Filter the DataFrame based on selected subjects
        #filtered_scores = average_scores[average_scores['Subject'].isin(selected_subjects)]
        # Display separate bar charts for each selected subject
        #for subject in selected_subjects:
            #subject_data = filtered_scores[filtered_scores['Subject'] == subject]

            # Add title
            #st.subheader(f"The performance of Male and Female in {subject}" )

            # Bar chart using Plotly Express
            #fig = px.bar(subject_data, x='Gender', y='Average Score', text="Average Score", hover_name="Average Score",
                         #labels={'Average Score': 'Average Score'})

            # Set y-axis minimum value
            #fig.update_yaxes(range=[430, subject_data['Average Score'].max()])

            # Display the chart
            #st.plotly_chart(fig)











