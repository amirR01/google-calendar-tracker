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
    
    def create_pie_chart(self, category_time: Dict[str, float], top_titles: Dict[str, List[Tuple[str, float]]], title: str = "Time Distribution") -> None:
        """
        Create and display a pie chart of time distribution by category with top activities.
        
        Args:
            category_time: Dictionary mapping category names to hours spent
            top_titles: Dictionary mapping category names to list of top activities
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
        
        # Create figure with subplots - smaller pie chart on left, more space for details on right
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 12), gridspec_kw={'width_ratios': [1, 1.5]})
        
        # Create pie chart on the left (smaller)
        wedges, texts, autotexts = ax1.pie(
            hours,
            labels=None,  # We'll create custom labels
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 8, 'weight': 'bold'},
            pctdistance=0.85
        )
        
        # Customize percentage text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_weight('bold')
            autotext.set_fontsize(8)
        
        # Legend removed - colors are shown in the detailed breakdown
        
        # Set pie chart title
        # ax1.set_title("Time Distribution", fontsize=12, weight='bold', pad=20)  # Removed individual pie chart title
        ax1.axis('equal')
        
        # Create detailed breakdown on the right with optimized spacing
        ax2.axis('off')  # Turn off axes for text display
        
        # Create detailed text breakdown with smaller fonts and tighter spacing (moved further to the right)
        y_position = 0.98
        ax2.text(0.35, y_position, "Detailed Breakdown", fontsize=13, weight='bold', transform=ax2.transAxes)
        y_position -= 0.06
        
        # Sort categories by hours (same order as pie chart)
        sorted_categories = sorted(filtered_data.items(), key=lambda x: -x[1])
        
        for category, hour in sorted_categories:
            percentage = (hour / total_hours * 100) if total_hours > 0 else 0
            color = CALENDAR_COLOR_MAP.get(category, '#cccccc')
            
            # Category header with colored bullet (more compact, moved further right)
            ax2.text(0.35, y_position, f"●", fontsize=12, color=color, weight='bold', transform=ax2.transAxes)
            ax2.text(0.38, y_position, f"{category}: {percentage:.1f}% ({hour:.1f}h)", 
                    fontsize=10, weight='bold', transform=ax2.transAxes)
            y_position -= 0.035
            
            # Top activities for this category (more compact, moved further right)
            if category in top_titles and top_titles[category]:
                for activity_title, activity_hours in top_titles[category]:
                    # Truncate long activity names
                    display_title = activity_title[:35] + "..." if len(activity_title) > 35 else activity_title
                    ax2.text(0.40, y_position, f"• {display_title} ({activity_hours:.1f}h)", 
                            fontsize=8, color='#666666', transform=ax2.transAxes)
                    y_position -= 0.025
            else:
                ax2.text(0.40, y_position, "• No specific activities recorded", 
                        fontsize=8, color='#999999', style='italic', transform=ax2.transAxes)
                y_position -= 0.025
            
            y_position -= 0.015  # Smaller space between categories
            
            # Check if we're running out of space
            if y_position < 0.02:
                remaining_categories = len([cat for cat, _ in sorted_categories if sorted_categories.index((cat, _)) > sorted_categories.index((category, hour))])
                if remaining_categories > 0:
                    ax2.text(0.35, y_position, f"... and {remaining_categories} more categories (scroll up for details)", 
                            fontsize=8, color='#999999', style='italic', transform=ax2.transAxes)
                break
        
        # Set main title for the entire figure
        fig.suptitle(title, fontsize=16, weight='bold', y=0.95)
        
        # Adjust layout
        plt.tight_layout()
        plt.subplots_adjust(top=0.9)  # Make room for main title
        
        # Show the plot
        plt.show()
    
    def save_pie_chart(self, category_time: Dict[str, float], top_titles: Dict[str, List[Tuple[str, float]]], filename: str, title: str = "Time Distribution") -> None:
        """
        Create and save a pie chart with detailed breakdown to file.
        
        Args:
            category_time: Dictionary mapping category names to hours spent
            top_titles: Dictionary mapping category names to list of top activities
            filename: Filename to save the chart (should include .png extension)
            title: Title for the chart
        """
        # Create the chart (reuse the display logic)
        self.create_pie_chart(category_time, top_titles, title)
        
        # Save the current figure
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"📊 Chart saved as: {filename}")
