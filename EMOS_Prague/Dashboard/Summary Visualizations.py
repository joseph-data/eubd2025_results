# Create summary visualizations
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import datetime
from pathlib import Path

# Define the custom colormap for consistency
water_colors = [(0.9, 0.9, 1), (0, 0.3, 0.8), (0, 0, 0.6)]
blue_cmap = LinearSegmentedColormap.from_list('water_blues', water_colors, N=256)

# Create a grid view of all Norway images
print("Creating Norway grid visualization...")
n_cols = min(4, len(norway_data)) 
n_rows = int(np.ceil(len(norway_data) / n_cols))

fig_grid = plt.figure(figsize=(16, 4 * n_rows))

for idx, data in enumerate(norway_data):
    if idx >= len(slots):
        break
        
    # Get time slot
    time_slot = slots[idx]
    start_date = time_slot[0]
    end_date = time_slot[1]
    
    # Create subplot
    ax = fig_grid.add_subplot(n_rows, n_cols, idx + 1)
    
    # Extract and plot data
    sar_data = data[..., 0]
    mask = data[..., 1] if data.shape[-1] > 1 else np.ones_like(sar_data)
    masked_data = np.ma.masked_where(mask == 0, sar_data)
    
    im = ax.imshow(masked_data, cmap=blue_cmap, vmin=0, vmax=1)
    ax.set_title(f"{start_date} to {end_date}")
    ax.axis('off')

# Add colorbar
fig_grid.subplots_adjust(right=0.9)
cbar_ax = fig_grid.add_axes([0.92, 0.15, 0.02, 0.7])
cbar = fig_grid.colorbar(im, cax=cbar_ax)
cbar.set_label('SAR backscatter (dB scaled)')

# Add legend
handles = [
    mpatches.Patch(color=water_colors[0], label='Low backscatter (smooth water)'),
    mpatches.Patch(color=water_colors[1], label='Medium backscatter'),
    mpatches.Patch(color=water_colors[2], label='High backscatter (rough water)')
]
fig_grid.legend(handles=handles, loc='lower center', ncol=3)

# Add overall title
plt.suptitle("Norway Fjord SAR Data Grid", fontsize=18, y=0.98)

# Save the grid
grid_path = results_dir / "norway_sar_grid.png"
plt.savefig(grid_path, dpi=300, bbox_inches='tight')
plt.close(fig_grid)

print(f"  Saved grid visualization: {grid_path}")

# Create a grid view of all Finland images
print("Creating Finland grid visualization...")
n_cols = min(4, len(finland_data)) 
n_rows = int(np.ceil(len(finland_data) / n_cols))

fig_grid = plt.figure(figsize=(16, 4 * n_rows))

for idx, data in enumerate(finland_data):
    if idx >= len(slots):
        break
        
    # Get time slot
    time_slot = slots[idx]
    start_date = time_slot[0]
    end_date = time_slot[1]
    
    # Create subplot
    ax = fig_grid.add_subplot(n_rows, n_cols, idx + 1)
    
    # Extract and plot data
    sar_data = data[..., 0]
    mask = data[..., 1] if data.shape[-1] > 1 else np.ones_like(sar_data)
    masked_data = np.ma.masked_where(mask == 0, sar_data)
    
    im = ax.imshow(masked_data, cmap=blue_cmap, vmin=0, vmax=1)
    ax.set_title(f"{start_date} to {end_date}")
    ax.axis('off')

# Add colorbar
fig_grid.subplots_adjust(right=0.9)
cbar_ax = fig_grid.add_axes([0.92, 0.15, 0.02, 0.7])
cbar = fig_grid.colorbar(im, cax=cbar_ax)
cbar.set_label('SAR backscatter (dB scaled)')

# Add legend
handles = [
    mpatches.Patch(color=water_colors[0], label='Low backscatter (smooth water)'),
    mpatches.Patch(color=water_colors[1], label='Medium backscatter'),
    mpatches.Patch(color=water_colors[2], label='High backscatter (rough water)')
]
fig_grid.legend(handles=handles, loc='lower center', ncol=3)

# Add overall title
plt.suptitle("Finland Lake SAR Data Grid", fontsize=18, y=0.98)

# Save the grid
grid_path = results_dir / "finland_sar_grid.png"
plt.savefig(grid_path, dpi=300, bbox_inches='tight')
plt.close(fig_grid)

print(f"  Saved grid visualization: {grid_path}")

# Create time series plots for Norway
print("Creating Norway time series analysis...")
if len(norway_data) > 1:
    fig_ts, ax_ts = plt.subplots(figsize=(14, 7))
    
    # Extract average backscatter for each time slot
    mean_values = [np.ma.mean(np.ma.masked_where(data[..., 1] == 0, data[..., 0])) for data in norway_data]
    std_values = [np.ma.std(np.ma.masked_where(data[..., 1] == 0, data[..., 0])) for data in norway_data]
    
    # Convert dates to datetime objects for better plotting
    dates = [datetime.datetime.strptime(slot[0], "%Y-%m-%d") for slot in slots[:len(norway_data)]]
    
    # Plot the time series
    ax_ts.errorbar(dates, mean_values, yerr=std_values, marker='o', linestyle='-', capsize=5, 
                  color='navy', linewidth=2, markersize=8)
    ax_ts.set_title("Norway Fjord: Average SAR Backscatter Over Time", fontsize=16)
    ax_ts.set_xlabel("Date", fontsize=14)
    ax_ts.set_ylabel("Average Backscatter (scaled)", fontsize=14)
    ax_ts.grid(True, alpha=0.3)
    ax_ts.tick_params(axis='both', which='major', labelsize=12)
    
    fig_ts.autofmt_xdate() 
    plt.tight_layout()
    
    # Save the figure
    ts_path = results_dir / "norway_sar_timeseries.png"
    plt.savefig(ts_path, dpi=300)
    plt.close(fig_ts)
    
    print(f"  Saved time series plot: {ts_path}")

# Create time series plots for Finland
print("Creating Finland time series analysis...")
if len(finland_data) > 1:
    fig_ts, ax_ts = plt.subplots(figsize=(14, 7))
    
    # Extract average backscatter for each time slot
    mean_values = [np.ma.mean(np.ma.masked_where(data[..., 1] == 0, data[..., 0])) for data in finland_data]
    std_values = [np.ma.std(np.ma.masked_where(data[..., 1] == 0, data[..., 0])) for data in finland_data]
    
    # Convert dates to datetime objects for better plotting
    dates = [datetime.datetime.strptime(slot[0], "%Y-%m-%d") for slot in slots[:len(finland_data)]]
    
    # Plot the time series
    ax_ts.errorbar(dates, mean_values, yerr=std_values, marker='o', linestyle='-', capsize=5, 
                  color='royalblue', linewidth=2, markersize=8)
    ax_ts.set_title("Finland Lake: Average SAR Backscatter Over Time", fontsize=16)
    ax_ts.set_xlabel("Date", fontsize=14)
    ax_ts.set_ylabel("Average Backscatter (scaled)", fontsize=14)
    ax_ts.grid(True, alpha=0.3)
    ax_ts.tick_params(axis='both', which='major', labelsize=12)
    
    fig_ts.autofmt_xdate() 
    plt.tight_layout()
    
    # Save the figure
    ts_path = results_dir / "finland_sar_timeseries.png"
    plt.savefig(ts_path, dpi=300)
    plt.close(fig_ts)
    
    print(f"  Saved time series plot: {ts_path}")

# Create combined time series for comparison
print("Creating combined time series analysis...")
if len(norway_data) > 1 and len(finland_data) > 1:
    fig_ts, ax_ts = plt.subplots(figsize=(14, 7))
    
    # Extract average backscatter for each time slot
    norway_means = [np.ma.mean(np.ma.masked_where(data[..., 1] == 0, data[..., 0])) for data in norway_data]
    finland_means = [np.ma.mean(np.ma.masked_where(data[..., 1] == 0, data[..., 0])) for data in finland_data]
    
    # Convert dates to datetime objects for better plotting
    dates = [datetime.datetime.strptime(slot[0], "%Y-%m-%d") for slot in slots[:min(len(norway_data), len(finland_data))]]
    
    # Plot both time series
    ax_ts.plot(dates, norway_means[:len(dates)], marker='o', linestyle='-', 
              color='navy', linewidth=2, markersize=8, label='Norway Fjord')
    ax_ts.plot(dates, finland_means[:len(dates)], marker='s', linestyle='--', 
              color='royalblue', linewidth=2, markersize=8, label='Finland Lake')
    
    ax_ts.set_title("Comparative SAR Backscatter: Norway Fjord vs Finland Lake", fontsize=16)
    ax_ts.set_xlabel("Date", fontsize=14)
    ax_ts.set_ylabel("Average Backscatter (scaled)", fontsize=14)
    ax_ts.grid(True, alpha=0.3)
    ax_ts.tick_params(axis='both', which='major', labelsize=12)
    ax_ts.legend(fontsize=14)
    
    fig_ts.autofmt_xdate()  
    plt.tight_layout()
    
    # Save the figure
    ts_path = results_dir / "combined_sar_timeseries.png"
    plt.savefig(ts_path, dpi=300)
    plt.close(fig_ts)
    
    print(f"  Saved combined time series plot: {ts_path}")

# Create statistical comparison
print("Creating statistical comparison...")
if len(norway_data) > 0 and len(finland_data) > 0:
    fig_comp, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
    
    # Use the first time slot for comparison
    norway_first = norway_data[0][..., 0].flatten()
    finland_first = finland_data[0][..., 0].flatten()
    
    # Remove masked values (zeros)
    norway_first = norway_first[norway_first > 0]
    finland_first = finland_first[finland_first > 0]
    
    # Plot histograms
    ax1.hist(norway_first, bins=50, alpha=0.7, color='navy', label='Norway Fjord')
    ax1.hist(finland_first, bins=50, alpha=0.7, color='royalblue', label='Finland Lake')
    ax1.set_title("Histogram of SAR Backscatter Values", fontsize=16)
    ax1.set_xlabel("Backscatter (scaled)", fontsize=14)
    ax1.set_ylabel("Frequency", fontsize=14)
    ax1.legend(fontsize=14)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='both', which='major', labelsize=12)
    
    # Plot cumulative distributions
    ax2.hist(norway_first, bins=50, alpha=0.7, color='navy', label='Norway Fjord', 
             cumulative=True, density=True)
    ax2.hist(finland_first, bins=50, alpha=0.7, color='royalblue', label='Finland Lake', 
             cumulative=True, density=True)
    ax2.set_title("Cumulative Distribution of SAR Backscatter", fontsize=16)
    ax2.set_xlabel("Backscatter (scaled)", fontsize=14)
    ax2.set_ylabel("Cumulative Probability", fontsize=14)
    ax2.legend(fontsize=14)
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='both', which='major', labelsize=12)
    
    plt.suptitle("Statistical Comparison of SAR Backscatter: Norway Fjord vs Finland Lake", fontsize=18)
    plt.tight_layout()
    
    # Save the figure
    comp_path = results_dir / "statistical_comparison.png"
    plt.savefig(comp_path, dpi=300)
    plt.close(fig_comp)
    
    print(f"  Saved statistical comparison: {comp_path}")

print("All summary visualizations complete!")
