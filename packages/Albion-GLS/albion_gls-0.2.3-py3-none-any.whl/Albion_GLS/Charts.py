import Albion_GLS.Albion_int as alb
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

def SaveTable(filename, df):
    #df = pd.DataFrame(data)
    
    df = df.reset_index()

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(8, 3))  # Set size to your needs

    # Hide the axes
    ax.xaxis.set_visible(False)
    ax.yaxis.set_visible(False)
    ax.set_frame_on(False)

    # Create the table
    table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
    
    
    # Adjust column widths if necessary
    for i, key in enumerate(table.get_celld().keys()):
        cell = table.get_celld()[key]
        if key[0] == 0:  # This checks if the cell is in the header row
            cell.set_text_props(fontsize=12, weight='bold')
        cell.set_fontsize(10)
        cell.set_edgecolor('black')
        
    # Adjust column widths
    table.auto_set_column_width([i for i in range(len(df.columns))])
    
    if os.path.exists(filename):
        os.remove(filename)
    
    # Save the table as a PNG
    plt.savefig(filename, bbox_inches='tight', dpi=300)

    # Show the plot (optional)
    #plt.show()

def Matplotlib_BoxAndWhisker(filename, df, fieldX, fieldY):

    # Handle missing values (drop rows with NaN in 'flow' column)
    df_clean = df.dropna(subset=[fieldY])

    # Group the data by 'system'
    grouped = df_clean.groupby(fieldX)[fieldY].apply(list)

    # Plotting
    fig, ax = plt.subplots(figsize=(10, 6))

    # Create a box plot
    #ax.boxplot(grouped, labels=grouped.index)
    sns.boxplot(data=df_clean, x=fieldX, y=fieldY)
    
    # Rotate x-axis labels
    plt.xticks(rotation=45)

    # Add labels and title
    ax.set_xlabel(fieldX)
    ax.set_ylabel(fieldY)
    ax.set_title('Box Plot of '+fieldY+' by '+fieldX)
    
    # Automatically adjust the layout to fit everything in the figure
    plt.tight_layout()

    # Display the plot
    #plt.show()
    if os.path.exists(filename):
        os.remove(filename)
    plt.savefig(filename)


def Seaborn_histplot(filename, df,fieldX, fieldHue):
    
    #df = pd.DataFrame({fieldX:dataX, fieldHue:dataHue})
    
    sns.set_theme(style="ticks")

    plt.figure(figsize=(10, 6))
    
    sns.histplot(data=df, x=fieldX, hue=fieldHue, multiple="stack")

    # Rotate x-axis labels
    plt.xticks(rotation=90)

    # Move the legend outside the plot
    plt.legend(title=fieldHue, bbox_to_anchor=(1.05, 1), loc='upper left')

    # Auto-adjust layout
    plt.tight_layout()
    
    if os.path.exists(filename):
        os.remove(filename)
        
    #fig = fig.get_figure()
    plt.savefig(filename) 
    
def Seaborn_cubehelix_palette(filename, fieldX, dataX, fieldY, dataY, fieldSize, dataSize, fieldHue, dataHue):
    sns.set_theme(style="whitegrid")

    df = pd.DataFrame({fieldX:dataX, fieldY:dataY, fieldSize:dataSize, fieldHue:dataHue})

    cmap = sns.cubehelix_palette(rot=-.2, as_cmap=True)
    g = sns.relplot(
        data=df,
        x=fieldX, y=fieldY,
        hue=fieldHue, size=fieldSize,
        palette=cmap, sizes=(10, 200),
    )
    
    g.set(xscale="linear", yscale="linear")
    g.ax.xaxis.grid(True, "minor", linewidth=.25)
    g.ax.yaxis.grid(True, "minor", linewidth=.25)
    g.despine(left=True, bottom=True)
    
    if os.path.exists(filename):
        os.remove(filename)
        
    fig = fig.get_figure()
    fig = fig.savefig(filename) 