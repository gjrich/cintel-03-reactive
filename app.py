# Additional Python Notes
# ------------------------

# Capitalization matters in Python. Python is case-sensitive: min and Min are different.
# Spelling matters in Python. You must match the spelling of functions and variables exactly.
# Indentation matters in Python. Indentation is used to define code blocks and must be consistent.


# For example:
#    The function filtered_data() takes no arguments.
#    The function between(min, max) takes two arguments, a minimum and maximum value.
#    Arguments can be positional or keyword arguments, labeled with a parameter name.

# The function body is indented (consistently!) after the colon. 
# Use the return keyword to return a value from a function.
    
# Decorators
# ----------
# Use the @ symbol to decorate a function with a decorator.
# Decorators a concise way of calling a function on a function.
# We don't typically write decorators, but we often use them.


import plotly.express as px
from shiny.express import input, ui, output, render
from shinywidgets import render_plotly, render_widget
from shiny import reactive
import palmerpenguins  # This package provides the Palmer Penguins dataset
import seaborn as sns
import matplotlib.pyplot as plt


# Use the built-in function to load the Palmer Penguins dataset
# Columns include:
# - species: chinstrap, adelie, and gentoo
# - island: island name: Dream, torgensen, or Biscoe - islands in the Palmer Archipelago
# - bill_length_mm: length of bill in mm
# - bill_depth_mm: depth of bill in mm
# - flipper_length_mm: flipper length in mm
# - body_mass_g: body mass in grams
# - sex: male or female

# it is then loaded into a pandas dataframe
penguin_df = palmerpenguins.load_penguins()

with ui.layout_columns():
    # Data Table
    with ui.card():
        "Penguin Data Table"
        @render.data_frame
        def penguintable():
            return render.DataTable(penguin_df, filters=False)

    # Data Grid
    with ui.card():
        "Penguin Data Grid"
        @render.data_frame
        def penguingrid():
            return render.DataGrid(penguin_df, filters=False)


# Add a Shiny UI sidebar for user interaction
# Use the ui.sidebar() function to create a sidebar
# Set the open parameter to "open" to make the sidebar open by default
# Use a with block to add content to the sidebar
with ui.sidebar(open="open"):
    
    # Use the ui.h2() function to add a 2nd level header to the sidebar
    #   pass in a string argument (in quotes) to set the header text to "Sidebar"
    ui.h2("Sidebar")


    # Use ui.input_selectize() to create a dropdown input to choose a column
    #   pass in three arguments:
    #   the name of the input (in quotes), e.g., "selected_attribute"
    #   the label for the input (in quotes)
    #   a list of options for the input (in square brackets) 
    #   e.g. ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
    ui.input_selectize(
        "selected_attribute", "Select Attribute", ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
    )

    # Use ui.input_numeric() to create a numeric input for the number of Plotly histogram bins
    #   pass in two arguments:
    #   the name of the input (in quotes), e.g. "plotly_bin_count"
    #   the label for the input (in quotes)
    ui.input_numeric("plotly_bin_count", label="Plotly hist bin count", value=20)


    # Use ui.input_slider() to create a slider input for the number of Seaborn bins
    #   pass in four arguments:
    #   the name of the input (in quotes), e.g. "seaborn_bin_count"
    #   the label for the input (in quotes)
    #   the minimum value for the input (as an integer)
    #   the maximum value for the input (as an integer)
    #   the default value for the input (as an integer)
    ui.input_slider("seaborn_bin_count", label="Seaborn hist bin count", min=2, max=20, value=10) 

    
    # Use ui.input_checkbox_group() to create a checkbox group input to filter the species
    #   pass in five arguments:
    #   the name of the input (in quotes), e.g.  "selected_species_list"
    #   the label for the input (in quotes)
    #   a list of options for the input (in square brackets) as ["Adelie", "Gentoo", "Chinstrap"]
    #   a keyword argument selected= a list of selected options for the input (in square brackets)
    #   a keyword argument inline= a Boolean value (True or False) as you like
    ui.input_checkbox_group("selected_species_list", label="Species", choices=["Adelie", "Chinstrap","Gentoo"], selected=["Adelie"],inline=False)

    # Use ui.hr() to add a horizontal rule to the sidebar
    ui.hr()

    # Use ui.a() to add a hyperlink to the sidebar
    #   pass in two arguments:
    #   the text for the hyperlink (in quotes), e.g. "GitHub"
    #   a keyword argument href= the URL for the hyperlink (in quotes), e.g. your GitHub repo URL
    #   a keyword argument target= "_blank" to open the link in a new tab
    ui.a("gjrich - github", href="https://github.com/gjrich/cintel-02-data/")

# When passing in multiple arguments to a function, separate them with commas.



# Build the UI
ui.page_opts(title="gjrich's penguin review", fillable=True)
with ui.layout_columns():

    with ui.card():
        ui.card_header("Plotly Histogram")
        @render_widget
        def plot1():
            scattery = px.histogram(
                data_frame=penguin_df,
                x=input.selected_attribute(),
                nbins=input.plotly_bin_count()
            ).update_layout(title={"text": "Penguins", "x": 0.5}, yaxis_title="count",xaxis_title=input.selected_attribute())
            return scattery


    
    with ui.card():
        ui.card_header("Seaborn Histogram")
        @render.plot
        def plot2():
            ax=sns.histplot(data=penguin_df, x=input.selected_attribute(), bins=input.seaborn_bin_count())
            ax.set_title("Penguins")
            ax.set_xlabel(input.selected_attribute())
            ax.set_ylabel("Count")
            return ax

    with ui.card():
        ui.card_header("Plotly Scatterplot: Species")
        @render_plotly
        def plotly_scatterplot():
            # Filter penguin_df based on selected species
            selected_species = input.selected_species_list()  # Get the selected species from the checkbox group
            filtered_df = penguin_df[penguin_df["species"].isin(selected_species)]
                        
            return px.scatter(
                data_frame=filtered_df,
                x="bill_length_mm",
                y="bill_depth_mm",
                color="island",
                symbol="species",
                labels={"bill_depth_mm": "Bill Depth (mm)",
                       "bill_length_mm": "Bill Length (mm)",
                       "species": "Species of Penguin",
                       "island": "Island of origin"},
            )
    
    # --------------------------------------------------------
    # Reactive calculations and effects
    # --------------------------------------------------------

    # Add a reactive calculation to filter the data
    # By decorating the function with @reactive, we can use the function to filter the data
    # The function will be called whenever an input functions used to generate that output changes.
    # Any output that depends on the reactive function (e.g., filtered_data()) will be updated when the data changes.

    with ui.card():
        ui.card_header("Reactive Calc")
        @reactive.calc
        def filtered_data():
            return penguin_df

        @render.plot(alt="A Seaborn histogram on penguin body mass in grams.")
        def seaborn_histogram():
                    histplot = sns.histplot(data=filtered_data(), x="body_mass_g", bins=input.seaborn_bin_count() )
                    histplot.set_title("Palmer Penguins")
                    histplot.set_xlabel("Mass (g)")
                    histplot.set_ylabel("Count")
                    return histplot
                
                

