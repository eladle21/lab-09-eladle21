import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
import pandas as pd

def top_names_plot(df, year=2000, n=10, width=800, height=600, variable='count'):
    year_data = df[df['year'] == year].copy()
    year_data['overall_rank'] = year_data[variable].rank(method='min', ascending=False).astype(int)

    male_names = year_data[year_data['sex'] == 'M']
    top_male = male_names.sort_values(variable, ascending=False).head(n)
    top_male['sex_rank'] = range(1, n + 1)  # Rank within male names

    female_names = year_data[year_data['sex'] == 'F']
    top_female = female_names.sort_values(variable, ascending=False).head(n)
    top_female['sex_rank'] = range(1, n + 1)  # Rank within female names

    df = pd.concat([top_male, top_female])
    df.sort_values(variable, ascending=False, inplace=True)

    fig = px.bar(df, x='name', y=variable, color='sex',
                category_orders={"name": df['name'].tolist()},
                hover_data={'sex_rank': True, 'overall_rank': True, 'sex': False, 'name': False})  # Add custom hover data

    fig.update_layout(title=f'Top {n} by sex names in {year}',
                    width=width, height=height)  
    return fig  


def name_frequencies_plot(df, year=200, width=800, height=600):
    year_data = df[df['year'] == year].copy()
    name_counts = year_data.groupby(['name', 'sex'])['count'].sum().reset_index()
    color_map = {"M": "#636EFA", "F": "#EF553B"}

    fig = px.histogram(
        name_counts, 
        x='count', 
        color='sex',  
        nbins=30, 
        title=f"Distribution of Name Frequencies by Sex in {year}",
        facet_col='sex',
        category_orders={'sex': ['M', 'F']},
        color_discrete_map=color_map 
    )

    fig.update_yaxes(type="log", matches="y")
    fig.update_xaxes(title_text="Number of Occurrences of Each Name", matches="x")

    fig.update_layout(
        xaxis_title="Number of Occurrences of Each Name",
        yaxis_title="Frequency (Log Scale)",
        yaxis_type="log",  # Set y-axis to log scale
        width=width, height=height
    )
    return fig

def name_trend_plot(df, name='John', width=800, height=600):
    name_data = df[df['name'] == name].copy()
    color_map = {"M": "#636EFA", "F": "#EF553B"}

    if name_data.empty:
        print("Name not found in the dataset.")
    else:
        # Group by Year and Sex, and calculate total counts
        #sex_counts = name_data.groupby(['year', 'sex'])['count'].sum().reset_index()

        # Calculate total count per year and male-to-female ratio
        yearly_counts = name_data.groupby(['year', 'sex']).sum()['count'].unstack(fill_value=0)
        yearly_counts['Total'] = yearly_counts['M'] + yearly_counts['F']
        yearly_counts['Male_Ratio'] = yearly_counts['M'] / yearly_counts['Total']
        yearly_counts['Female_Ratio'] = yearly_counts['F'] / yearly_counts['Total']
        yearly_counts = yearly_counts.reset_index()

        # Create subplots with shared x-axis
        fig = make_subplots(
            rows=2, cols=1, shared_xaxes=True,
            subplot_titles=("Total Count Over Time", "Sex Balance Ratio Over Time")
        )

        # Add total count plot
        fig.add_trace(
            go.Scatter(x=yearly_counts['year'], y=yearly_counts['M'], mode='lines', name='Male', line=dict(color=color_map['M'])),
            row=1, col=1
        )

        fig.add_trace(
            go.Scatter(x=yearly_counts['year'], y=yearly_counts['F'], mode='lines', name='Female', line=dict(color=color_map['F'])),
            row=1, col=1
        )

        # Add male and female ratio plot
        fig.add_trace(
            go.Scatter(x=yearly_counts['year'], y=yearly_counts['Male_Ratio'], mode='lines', showlegend=False,  line=dict(color=color_map['M'])),
            row=2, col=1
        )
        fig.add_trace(
            go.Scatter(x=yearly_counts['year'], y=yearly_counts['Female_Ratio'], mode='lines', showlegend=False, line=dict(color=color_map['F'])),
            row=2, col=1
        )

        # Update layout
        fig.update_layout(
            title=f"Name Trend and Sex Distribution for '{name}'",
            xaxis_title="Year",
            yaxis_title="Total Count",
            yaxis2_title="Ratio",
            height=height,
            width=width
        )

        return fig

def name_sex_balance_plot(df, name='John'):
    name_data = df[df['name'] == name].copy()
    color_map = {"M": "#636EFA", "F": "#EF553B"}

    if name_data.empty:
        print("Name not found in the dataset.")
    else:
        sex_counts = name_data.groupby('sex').sum()['count']
        male_count = sex_counts.get('M', 0)
        female_count = sex_counts.get('F', 0)
        total_count = male_count + female_count
        if total_count > 0:
            male_ratio = male_count / total_count
            female_ratio = female_count / total_count

            fig, ax = plt.subplots(figsize=(10, 2))

            # Create a stacked bar representing male and female ratios
            ax.barh(0, male_ratio, color=color_map['M'], label='Male')
            ax.barh(0, female_ratio, left=male_ratio, color=color_map['F'], label='Female')

            # Customize the chart
            ax.set_xlim(0, 1)
            ax.set_xticks([0, 0.5, 1])
            ax.set_xticklabels(['0%', '50%', '100%'])
            ax.set_yticks([])  # Hide y-axis ticks

            # Add labels to display the ratios
            ax.text(male_ratio / 2, 0, f"{male_ratio * 100:.1f}%", va='center', 
                    ha='center', color='white', 
                    fontweight='bold',
                    fontsize=20)
            ax.text(male_ratio / 2, -.25, "male", va='center', 
                    ha='center', color='white', 
                    fontweight='bold',
                    fontsize=20)
            ax.text(male_ratio + female_ratio / 2, 0, f"{female_ratio * 100:.1f}%", va='center', 
                    ha='center', color='white', 
                    fontweight='bold',
                    fontsize=20)
            ax.text(male_ratio + female_ratio / 2, -.25, "female", va='center', 
                    ha='center', color='white', 
                    fontweight='bold',
                    fontsize=20)
            plt.title(f"Sex Balance of the '{name}'")
            return fig


        else:
            print("Insufficient data for gender dominance calculation.")

def unique_names_summary(df, year=1977):
    year_data = df[df['year'] == year].copy()
    total_names_per_sex = year_data.groupby('sex')['count'].sum()
    unique_names_per_sex = year_data.groupby('sex')['name'].nunique()
    percent_unique_names_per_sex = (unique_names_per_sex / total_names_per_sex) * 100

    output = pd.DataFrame({
        "Total Names": total_names_per_sex,
        "Unique Names": unique_names_per_sex,
        "Percent Unique": percent_unique_names_per_sex})
    
    return output


def one_hit_wonders(ohw_data, year=1977):
    ohw_year = ohw_data[ohw_data['year'] == year]

    if ohw_year.empty:
        print(f"No one-hit wonders found in {year}")
        return go.Figure()  # Return an empty figure if no data
    else:
        one_hit_wonder_counts = ohw_year['sex'].value_counts()
        common_one_hit_wonders = ohw_year.groupby(['name', 'sex'])['count'].sum().reset_index()

        # Create a Plotly bar chart
        fig = px.bar(
            common_one_hit_wonders,
            x='name',
            y='count',
            color='sex',
            title=f"One-Hit Wonders in {year}"
        )
        return fig
