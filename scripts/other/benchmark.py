import plotly.express as px
from cobra import io, Model, Reaction, Metabolite
from cobra.manipulation.validate import check_mass_balance
import os, sys

# Benchmark metabolites per compartment
def pie_chart(m: Model, name: str, save_path: str):

    # Total number of reactions in model
    rxn_count = len(m.reactions)
    # Number of reactions in each subgroup
    metabolite_groups = {}
    for met in m.metabolites:
        group = met.compartment if met.compartment else "Uncategorized"
        if group not in metabolite_groups:
            metabolite_groups[group] = 0
        metabolite_groups[group] += 1

    # Create pie chart using plotly express with vibrant colors
    fig = px.pie(
        values=list(metabolite_groups.values()),
        names=list(map(lambda x: m.compartments[x], metabolite_groups.keys())),
        title=f"Distribution of Metabolites by Compartment ({name})",
        color_discrete_sequence=px.colors.qualitative.Vivid  # More vibrant colors
    )
    
    # Customize the appearance with large pie and side legend
    fig.update_traces(
        textposition='inside',  # Show percentages inside the pie slices
        texttemplate='%{percent}<br>(%{value})',  # Custom format: percentage on one line, (value) on next line
        textfont_size=14,
        textfont_color="white",
        marker_line_color="white",  # White borders around slices
        marker_line_width=2
    )
    
    fig.update_layout(
        # Enable legend on the right side
        showlegend=True,
        legend=dict(
            orientation="v",  # Vertical legend
            yanchor="middle",
            y=0.5,
            xanchor="left",
            x=1.02,  # Position legend to the right of the chart
            font=dict(size=12)
        ),
        # Make the pie chart large and centered
        font=dict(size=16, color="black"),
        title_font_size=20,
        title_x=0.4,  # Center title over pie chart area (not including legend)
        margin=dict(t=80, b=50, l=50, r=250),  # Extra right margin for legend
        paper_bgcolor="white",
        plot_bgcolor="white",
        width=1400,  # Wider to accommodate legend
        height=800
    )
    
    # Save as PNG image with layout similar to the example
    fig.write_image(os.path.join(save_path, f"{name}_met_chart.png"), width=1400, height=800, scale=2)
    print(f"Pie chart saved as '{name}_met_chart.png'")

    return fig

# Benchmark important subsystems and their completeness
def pathway_reaction_comparison(models: list, model_names: list, save_path: str):
    """
    Compare the number of reactions in Sterol Biosynthesis and Pyruvate Metabolism 
    pathways across multiple models using a bar chart.
    
    Args:
        models: List of COBRApy Model objects
        model_names: List of string names for each model
    """
    # Data for the bar chart
    pathway_data = []


    for model, name in zip(models, model_names):

        # Get mass-unbalanced reactions
        mass_unbalanced_reactions = [r.id for r in list(check_mass_balance(model=model).keys())]

        sterol_count = { 'balanced': 0, 'unbalanced': 0 }
        pyruvate_count = { 'balanced': 0, 'unbalanced': 0 }
        carotenoid_count = { 'balanced': 0, 'unbalanced': 0 }
        
        # Count reactions in each pathway
        for reaction in model.reactions:
            # Check if reaction belongs to sterol biosynthesis
            if hasattr(reaction, 'subsystem') and reaction.subsystem:
                subsystem = reaction.subsystem
                balance = 'balanced' if reaction.id not in mass_unbalanced_reactions else 'unbalanced'
                if ('Biosynthesis of steroids' in subsystem):
                    sterol_count[balance] += 1
                elif ('Pyruvate metabolism' in subsystem):
                    pyruvate_count[balance] += 1
                elif ('Carotenoid biosynthesis' in subsystem):
                    carotenoid_count[balance] += 1

        # Add data for this model - separate balanced and unbalanced (unbalanced first for bottom layer)
        pathway_data.extend([
            # Sterol Biosynthesis - unbalanced first (bottom), balanced second (top)
            {"Model": name, "Pathway": "Sterol Biosynthesis", "Balance": "Mass-Unbalanced", "Reaction Count": sterol_count['unbalanced']},
            {"Model": name, "Pathway": "Sterol Biosynthesis", "Balance": "Mass-Balanced", "Reaction Count": sterol_count['balanced']},
            # Pyruvate Metabolism - unbalanced first (bottom), balanced second (top)
            {"Model": name, "Pathway": "Pyruvate Metabolism", "Balance": "Mass-Unbalanced", "Reaction Count": pyruvate_count['unbalanced']},
            {"Model": name, "Pathway": "Pyruvate Metabolism", "Balance": "Mass-Balanced", "Reaction Count": pyruvate_count['balanced']},
            # Carotenoid Biosynthesis - unbalanced first (bottom), balanced second (top)
            {"Model": name, "Pathway": "Carotenoid Biosynthesis", "Balance": "Mass-Unbalanced", "Reaction Count": carotenoid_count['unbalanced']},
            {"Model": name, "Pathway": "Carotenoid Biosynthesis", "Balance": "Mass-Balanced", "Reaction Count": carotenoid_count['balanced']}
        ])
    
    # Create stacked bar chart
    fig = px.bar(
        pathway_data,
        x="Model",
        y="Reaction Count", 
        color="Balance",
        facet_col="Pathway",  # Separate column for each pathway
        title="Mass Balance Analysis: Reactions by Pathway",
        color_discrete_map={
            "Mass-Balanced": "#2E8B57",      # Sea green for balanced
            "Mass-Unbalanced": "#FF6347"     # Tomato red for unbalanced
        },
        barmode="stack"  # Stack bars on top of each other
    )
    
    # Customize appearance
    fig.update_layout(
        font=dict(size=12),
        title_font_size=16,
        title_x=0.5,
        yaxis_title="Number of Reactions",
        legend_title="Mass Balance Status",
        paper_bgcolor="white",
        plot_bgcolor="white",
        showlegend=True,
        bargap=0.5,  # Increase gap around bar groups to make bars appear narrower
        bargroupgap=0.1  # Keep same gap between bars within each group
    )
    
    # Move pathway labels from top to bottom and clean up layout
    pathway_names = []
    fig.for_each_annotation(lambda a: pathway_names.append(a.text.replace("Pathway=", "")))
    fig.update_annotations(text="")  # Remove top subplot titles
    
    # Set pathway names as x-axis titles (bottom labels)
    for i, pathway_name in enumerate(pathway_names):
        fig.layout[f'xaxis{i+1 if i > 0 else ""}'].title.text = pathway_name
    
    # Add value labels on bars (only show non-zero values)
    fig.update_traces(
        texttemplate='%{y}', 
        textposition='inside',
        textfont_color="white",
        textfont_size=10
    )
    
    # Save as PNG
    fig.write_image(os.path.join(save_path, "pathway_comparison.png"), width=1000, height=600, scale=2)
    print("Pathway comparison chart saved as 'pathway_comparison.png'")
    
    return fig

if __name__ == "__main__":
    
    # Load models
    # iRC1080, e = io.validate_sbml_model('./data/raw/iRC1080.xml')
    iBD1106, e = io.validate_sbml_model('./data/raw/iBD1106.xml')
    iCre1355, e = io.validate_sbml_model('./data/raw/iCre1355/iCre1355_auto.xml')

    save_path = './results/bench'
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # # Generate pie charts
    pie_chart(iBD1106, "iBD1106", save_path)
    pie_chart(iCre1355, "iCre1355", save_path)
    
    # Generate pathway comparison bar chart
    models = [iBD1106, iCre1355]
    model_names = ["iBD1106", "iCre1355"]
    pathway_reaction_comparison(models, model_names, save_path)
