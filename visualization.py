# visualization.py

import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
import matplotlib.patches as mpatches

# Google Calendar color mapping to actual colors
CALENDAR_COLOR_MAP = {
    'Professional Tasks': '#0f9d58',     # Basil (Green)
    'Meetings': '#4285f4',               # Blueberry (Blue) 
    'Social Connections': '#9c27b0',     # Grape (Purple)
    'Emotional Recharge': '#f9ab00',     # Banana (Yellow)
    'Self-Maintenance': '#673ab7',       # Lavender (Purple)
    'Life Admin': '#ff6d01',             # Tangerine (Orange)
    'Mental Struggles': '#5f6368',       # Graphite (Gray)
    'Romance': '#d93025'                 # Tomato (Red)
}

class CalendarVisualizer:
    """Class for creating visualizations of calendar data."""
    
    def __init__(self):
        """Initialize the visualizer with style settings."""
        plt.style.use('default')
        plt.rcParams['font.size'] = 10
        plt.rcParams['figure.facecolor'] = 'white'
    
    def create_pie_chart(self, category_time: Dict[str, float], title: str = "Time Distribution") -> None:
        """
        Create and display a pie chart of time distribution by category.
        
        Args:
            category_time: Dictionary mapping category names to hours spent
            title: Title for the chart
        """
        if not category_time:
            print("No data to visualize.")
            return
        
        # Filter out categories with 0 hours
        filtered_data = {k: v for k, v in category_time.items() if v > 0}
        
        if not filtered_data:
            print("No data to visualize (all categories have 0 hours).")
            return
        
        # Prepare data
        categories = list(filtered_data.keys())
        hours = list(filtered_data.values())
        total_hours = sum(hours)
        
        # Get colors for each category
        colors = [CALENDAR_COLOR_MAP.get(category, '#cccccc') for category in categories]
        
        # Create figure and axis
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            hours,
            labels=None,  # We'll create custom labels
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 9, 'weight': 'bold'},
            pctdistance=0.85
        )
        
        # Customize percentage text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_weight('bold')
        
        # Create custom legend
        legend_labels = []
        for category, hour in zip(categories, hours):
            percentage = (hour / total_hours * 100) if total_hours > 0 else 0
            legend_labels.append(f'{category}: {percentage:.1f}% ({hour:.1f}h)')
        
        ax.legend(
            wedges, 
            legend_labels,
            title="Categories",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
            fontsize=9
        )
        
        # Set title
        ax.set_title(title, fontsize=14, weight='bold', pad=20)
        
        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis('equal')
        
        # Adjust layout to prevent legend cutoff
        plt.tight_layout()
        
        # Show the plot
        plt.show()
    
    def save_pie_chart(self, category_time: Dict[str, float], filename: str, title: str = "Time Distribution") -> None:
        """
        Create and save a pie chart to file.
        
        Args:
            category_time: Dictionary mapping category names to hours spent
            filename: Filename to save the chart (should include .png extension)
            title: Title for the chart
        """
        # Create the chart (reuse the display logic)
        self.create_pie_chart(category_time, title)
        
        # Save the current figure
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"📊 Chart saved as: {filename}")
