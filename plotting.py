import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from PyQt5.QtWidgets import QFileDialog
import matplotlib.image as mpimg
from matplotlib.collections import LineCollection
from utils import get_user_inputs

def update_plot(window):
    try:
        # Clear plot if no file is selected
        if not window.file_path:
            window.figure.clear()
            window.canvas.draw()
            return

        encodings_to_try = ['utf-8', 'latin1', 'ISO-8859-1']
        for encoding in encodings_to_try:
            try:
                window.data = pd.read_csv(window.file_path, encoding=encoding, on_bad_lines='skip')
                break
            except UnicodeDecodeError:
                continue

        if window.second_file_path:
            for encoding in encodings_to_try:
                try:
                    window.second_data = pd.read_csv(window.second_file_path, encoding=encoding, on_bad_lines='skip')
                    break
                except UnicodeDecodeError:
                    continue
        else:
            window.second_data = None

        if not window.data.empty:
            window.figure.clear()
            columns = get_columns_based_on_mode(window)
            selected_columns = window.get_selected_columns()
            columns = [col for col in columns if col in selected_columns]
            num_plots = len(columns)

            if columns:
                data_limit_slider_value = window.data_limit_slider.value()
                data_limit = int(data_limit_slider_value / 100 * len(window.data))

                range_slider_value = window.data_range_slider.value()
                data_range_start = int((100 - range_slider_value) / 100 * len(window.data))

                for i, column in enumerate(columns):
                    if column in window.data.columns:
                        ax = window.figure.add_subplot(num_plots, 1, i + 1)
                        plot_height = 0.9 / num_plots
                        plot_bottom = 0.05 + (num_plots - i - 1) * plot_height
                        ax.set_position([0.1, plot_bottom, 0.8, plot_height])

                        column_data = pd.to_numeric(window.data[column], errors='coerce').dropna()
                        column_data = column_data.iloc[data_range_start:data_range_start + data_limit]

                        if column_data.empty:
                            continue

                        # Gunakan batas yang didefinisikan oleh pengguna jika ada
                        if column in window.bounds:
                            upper_bound = window.bounds[column][0]
                            lower_bound = window.bounds[column][1]
                        else:
                            upper_bound = column_data.max()
                            lower_bound = column_data.min()

                        ax.axhline(upper_bound, color='black', linestyle='--', linewidth=1, label='Upper Bound')
                        ax.axhline(lower_bound, color='black', linestyle='--', linewidth=1, label='Lower Bound')

                        color_normal = 'blue'
                        color_above = 'red'
                        color_below = 'orange'

                        x_values = column_data.index
                        y_values = column_data

                        segments = []
                        colors = []

                        for j in range(len(y_values) - 1):
                            x0, x1 = x_values[j], x_values[j + 1]
                            y0, y1 = y_values.iloc[j], y_values.iloc[j + 1]

                            if y0 > upper_bound and y1 > upper_bound:
                                segments.append([(x0, y0), (x1, y1)])
                                colors.append(color_above)
                            elif y0 < lower_bound and y1 < lower_bound:
                                segments.append([(x0, y0), (x1, y1)])
                                colors.append(color_below)
                            else:
                                if y0 > upper_bound:
                                    x_cross = x0 + (x1 - x0) * (upper_bound - y0) / (y1 - y0)
                                    segments.append([(x0, y0), (x_cross, upper_bound)])
                                    colors.append(color_above)
                                    if y1 < lower_bound:
                                        x_cross_lower = x_cross + (x1 - x_cross) * (lower_bound - upper_bound) / (y1 - upper_bound)
                                        segments.append([(x_cross, upper_bound), (x_cross_lower, lower_bound)])
                                        colors.append(color_normal)
                                        segments.append([(x_cross_lower, lower_bound), (x1, y1)])
                                        colors.append(color_below)
                                    else:
                                        segments.append([(x_cross, upper_bound), (x1, y1)])
                                        colors.append(color_normal)
                                elif y1 > upper_bound:
                                    if y0 < lower_bound:
                                        x_cross_lower = x0 + (x1 - x0) * (lower_bound - y0) / (y1 - y0)
                                        segments.append([(x0, y0), (x_cross_lower, lower_bound)])
                                        colors.append(color_below)
                                        x_cross = x_cross_lower + (x1 - x_cross_lower) * (upper_bound - lower_bound) / (y1 - lower_bound)
                                        segments.append([(x_cross_lower, lower_bound), (x_cross, upper_bound)])
                                        colors.append(color_normal)
                                        segments.append([(x_cross, upper_bound), (x1, y1)])
                                        colors.append(color_above)
                                    else:
                                        x_cross = x0 + (x1 - x0) * (upper_bound - y0) / (y1 - y0)
                                        segments.append([(x0, y0), (x_cross, upper_bound)])
                                        colors.append(color_normal)
                                        segments.append([(x_cross, upper_bound), (x1, y1)])
                                        colors.append(color_above)
                                elif y0 < lower_bound:
                                    x_cross = x0 + (x1 - x0) * (lower_bound - y0) / (y1 - y0)
                                    segments.append([(x0, y0), (x_cross, lower_bound)])
                                    colors.append(color_below)
                                    if y1 > upper_bound:
                                        x_cross_upper = x_cross + (x1 - x_cross) * (upper_bound - lower_bound) / (y1 - lower_bound)
                                        segments.append([(x_cross, lower_bound), (x_cross_upper, upper_bound)])
                                        colors.append(color_normal)
                                        segments.append([(x_cross_upper, upper_bound), (x1, y1)])
                                        colors.append(color_above)
                                    else:
                                        segments.append([(x_cross, lower_bound), (x1, y1)])
                                        colors.append(color_normal)
                                elif y1 < lower_bound:
                                    x_cross = x0 + (x1 - x0) * (lower_bound - y0) / (y1 - y0)
                                    segments.append([(x0, y0), (x_cross, lower_bound)])
                                    colors.append(color_normal)
                                    segments.append([(x_cross, lower_bound), (x1, y1)])
                                    colors.append(color_below)
                                else:
                                    segments.append([(x0, y0), (x1, y1)])
                                    colors.append(color_normal)

                        lc = LineCollection(segments, colors=colors, linewidths=2)
                        ax.add_collection(lc)
                        ax.autoscale()

                        if window.second_data is not None and column in window.second_data.columns:
                            second_column_data = pd.to_numeric(window.second_data[column], errors='coerce').dropna()
                            second_column_data = second_column_data.iloc[data_range_start:data_range_start + data_limit]

                            x_values_2 = second_column_data.index
                            y_values_2 = second_column_data

                            segments_2 = [[(x_values_2[j], y_values_2.iloc[j]), (x_values_2[j + 1], y_values_2.iloc[j + 1])] for j in range(len(y_values_2) - 1)]
                            colors_2 = ['green'] * (len(y_values_2) - 1)

                            lc_2 = LineCollection(segments_2, colors=colors_2, linewidths=2)
                            ax.add_collection(lc_2)
                            ax.autoscale()

                        ax.grid(True)
                        ax.set_xlabel('Time', fontsize=9)
                        ax.set_ylabel(column, fontsize=9)
                        ax.tick_params(axis='both', which='major', labelsize=8)

                        y_min, y_max = column_data.min(), column_data.max()
                        y_margin = 20
                        ax.set_ylim(min(y_min, lower_bound) - y_margin, max(y_max, upper_bound) + y_margin)

                        last_value = column_data.iloc[-1]
                        ax.text(1.01, 0.5, f'Latest: {last_value:.2f}', transform=ax.transAxes, verticalalignment='center', fontsize=8)

                window.canvas.draw()
    except Exception as e:
        print(f"Error updating plot: {e}")

def get_columns_based_on_mode(self):
    columns = {
        'VOR': ['LEVEL[dBm]', 'BEARING(from)[°]', 'FM-DEV.[Hz]', 'FM-INDEX'],
        'LLZ': ['LEVEL[dBm]', 'AM-MOD./90Hz[%]', 'AM-MOD./150Hz[%]', 'DDM(90-150)[uA]', 'SDM[%]'],
        'GP': ['LEVEL[dBm]', 'AM-MOD./90Hz[%]', 'AM-MOD./150Hz[%]', 'DDM(90-150)[uA]', 'SDM[%]'],
    }
    return columns.get(self.mode, [])

def clear_plot(self):
    self.figure.clear()
    self.canvas.draw()

def save_plot(self):
    if self.file_path and not self.data.empty:
        pdf_path, _ = QFileDialog.getSaveFileName(self, "Save PDF File", "", "PDF Files (*.pdf);;All Files (*)")
        if pdf_path:
            columns = get_columns_based_on_mode(self)
            num_plots = len(columns)
            plots_per_page = 2
            num_pages = (num_plots + plots_per_page - 1) // plots_per_page

            user_inputs = get_user_inputs()
            if user_inputs is None:
                return
            
            bandara, alat, pengujian = user_inputs

            columns = get_columns_based_on_mode(self)
            num_plots = len(columns)

            with PdfPages(pdf_path) as pdf:
                for page in range(num_pages):
                    fig = plt.figure(figsize=(11.69, 8.27))
                    fig.subplots_adjust(top=0.8, bottom=0.1, left=0.1, right=0.9, hspace=0.4)

                    logo_ax = fig.add_axes([0.02, 0.9, 0.3, 0.05])
                    logo_ax.axis('off')
                    image_path = 'rsxbeta.png'
                    if os.path.exists(image_path):
                        img = mpimg.imread(image_path)
                        logo_ax.imshow(img, aspect='auto')

                    header_ax = fig.add_axes([0.35, 0.88, 0.4, 0.07])
                    header_ax.axis('off')

                    header_text = (
                        f'MODE: {self.mode}\n'
                        f'DATE: {pd.Timestamp.now().strftime("%Y-%m-%d")}\n'
                        f'TIME: {pd.Timestamp.now().strftime("%H:%M:%S")}\n'
                    )
                    header_ax.text(0.0, 0.35, header_text, fontsize=12, ha='left', va='center', wrap=True)

                    header_ax2 = fig.add_axes([0.53, 0.88, 0.4, 0.07])
                    header_ax2.axis('off')
                    header_text_right = (
                        f'Airport: {bandara}\n'
                        f'Transmitter: {alat}\n'
                        f'Attempt: {pengujian}'
                    )
                    header_ax2.text(0.0, 1.0, header_text_right, fontsize=12, ha='left', va='top')

                    start_index = page * plots_per_page
                    end_index = min(start_index + plots_per_page, num_plots)
                    columns_for_page = columns[start_index:end_index]

                    plot_height = 0.6 if num_plots == 1 else 0.35
                    plot_spacing = 0.05
                    start_height = 0.20 if num_plots == 1 else 0.51

                    for i, column in enumerate(columns_for_page):
                        if column in self.data.columns:
                            plot_bottom = start_height - (i * (plot_height + plot_spacing))
                            ax = fig.add_axes([0.1, plot_bottom, 0.8, plot_height])
                            column_data = self.data[column].dropna()

                            if column_data.empty:
                                continue

                            # Gunakan batas yang didefinisikan oleh pengguna jika ada
                            if column in self.bounds:
                                upper_bound = self.bounds[column][0]
                                lower_bound = self.bounds[column][1]
                            else:
                                upper_bound = column_data.max()
                                lower_bound = column_data.min()

                            ax.axhline(upper_bound, color='black', linestyle='--', linewidth=1, label='Upper Bound')
                            ax.axhline(lower_bound, color='black', linestyle='--', linewidth=1, label='Lower Bound')

                            color_normal = 'blue'
                            color_above = 'red'
                            color_below = 'orange'

                            x_values = column_data.index
                            y_values = column_data

                            segments = []
                            colors = []

                            for j in range(len(y_values) - 1):
                                x0, x1 = x_values[j], x_values[j + 1]
                                y0, y1 = y_values.iloc[j], y_values.iloc[j + 1]

                                if y0 > upper_bound and y1 > upper_bound:
                                    segments.append([(x0, y0), (x1, y1)])
                                    colors.append(color_above)
                                elif y0 < lower_bound and y1 < lower_bound:
                                    segments.append([(x0, y0), (x1, y1)])
                                    colors.append(color_below)
                                else:
                                    if y0 > upper_bound:
                                        x_cross = x0 + (x1 - x0) * (upper_bound - y0) / (y1 - y0)
                                        segments.append([(x0, y0), (x_cross, upper_bound)])
                                        colors.append(color_above)
                                        segments.append([(x_cross, upper_bound), (x1, y1)])
                                        colors.append(color_normal if y1 < upper_bound else color_below)
                                    elif y1 > upper_bound:
                                        x_cross = x0 + (x1 - x0) * (upper_bound - y0) / (y1 - y0)
                                        segments.append([(x0, y0), (x_cross, upper_bound)])
                                        colors.append(color_normal)
                                        segments.append([(x_cross, upper_bound), (x1, y1)])
                                        colors.append(color_above)
                                    elif y0 < lower_bound:
                                        x_cross = x0 + (x1 - x0) * (lower_bound - y0) / (y1 - y0)
                                        segments.append([(x0, y0), (x_cross, lower_bound)])
                                        colors.append(color_below)
                                        segments.append([(x_cross, lower_bound), (x1, y1)])
                                        colors.append(color_normal if y1 > lower_bound else color_above)
                                    elif y1 < lower_bound:
                                        x_cross = x0 + (x1 - x0) * (lower_bound - y0) / (y1 - y0)
                                        segments.append([(x0, y0), (x_cross, lower_bound)])
                                        colors.append(color_normal)
                                        segments.append([(x_cross, lower_bound), (x1, y1)])
                                        colors.append(color_below)
                                    else:
                                        segments.append([(x0, y0), (x1, y1)])
                                        colors.append(color_normal)

                            lc = LineCollection(segments, colors=colors, linewidths=2)
                            ax.add_collection(lc)
                            ax.autoscale()

                            ax.grid(True)
                            ax.set_xlabel('Time', fontsize=9)
                            ax.set_ylabel(column, fontsize=7)
                            ax.tick_params(axis='both', which='major', labelsize=8)

                            y_min, y_max = column_data.min(), column_data.max()
                            y_margin = 4.0
                            ax.set_ylim(min(y_min, lower_bound) - y_margin, max(y_max, upper_bound) + y_margin)

                    fig.text(0.55, 0.04, "-- : Upper and Lower", fontsize=10, ha='right', va='top', color='red')
                    fig.text(0.69, 0.04, "blue : Normal Range", fontsize=10, ha='right', va='top', color='blue')
                    fig.text(0.83, 0.04, "Red : Above Upper", fontsize=10, ha='right', va='top', color='red')
                    fig.text(0.98, 0.04, "Orange : Below Lower", fontsize=10, ha='right', va='top', color='orange')

                    pdf.savefig(fig)
                    plt.close(fig)
