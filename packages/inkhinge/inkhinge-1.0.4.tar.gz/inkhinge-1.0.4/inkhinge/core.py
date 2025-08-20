"""inkhinge包的核心功能模块"""
import os
import numpy as np
import pandas as pd
from ase.io import write
from ase.visualize import view
from scipy.spatial import cKDTree
from spectrochempy_omnic import OMNICReader as read
from decimal import Decimal, Context, ROUND_HALF_UP
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import find_peaks, savgol_filter
from PIL import Image
from collections import defaultdict
import datetime

"read_to_csv module:"
def read_to_csv(input_path, output_path=None, background_path=None, overwrite=False, recursive=False, precision=20, merge_output=None):
    """
    Read Omnic SPA files and convert to CSV format, with option to merge all converted CSV files

    Parameters:
        input_path (str): Path to input SPA file or directory containing files
        output_path (str): Path for output CSV file or directory
        background_path (str): Path to background BG.spa file
        overwrite (bool): Whether to overwrite existing files
        recursive (bool): Process subdirectories recursively (only effective for directories)
        precision (int): Decimal precision for output data
        merge_output (str): Output path for merged CSV file, None means no merging

    Returns:
        Processing result information (number of successfully converted files or output path)
    """
    def float_to_fixed_str(value, precision=20):
        """Convert float to fixed-point decimal string with specified precision"""
        if np.isnan(value):
            return 'nan'
        try:
            ctx = Context(prec=max(25, precision + 5), rounding=ROUND_HALF_UP)
            dec = ctx.create_decimal(str(value))
            return f"{dec:.{precision}f}"
        except:
            return str(value)

    def detect_data_type(reader):
        """Detect data type and return corresponding title and units"""
        data_type_mapping = {
            0: ("Absorbance", "AU"),
            1: ("Transmittance", "%"),
            2: ("Reflectance", "%"),
            3: ("Single Beam", ""),
            4: ("Kubelka-Munk", "KM units"),
        }

        if hasattr(reader, 'data_type') and reader.data_type in data_type_mapping:
            return data_type_mapping[reader.data_type]

        if hasattr(reader, 'title'):
            title = reader.title.lower()
            if "absorbance" in title:
                return "Absorbance", "AU"
            elif "transmittance" in title or "Transmittance" in title:  # Updated
                return "Transmittance", "%"
            elif "reflectance" in title:
                return "Reflectance", "%"
            elif "single beam" in title or "Single Beam" in title:  # Updated
                return "Single Beam", ""
            elif "kubelka-munk" in title or "km" in title:
                return "Kubelka-Munk", "KM units"

        y_title = reader.y_title or "Intensity"
        y_units = reader.y_units or ""

        if "kubelka" in y_title.lower() or "km" in y_title.lower():
            return "Kubelka-Munk", "KM units"

        return y_title, y_units

    def calculate_kubelka_munk(reflectance):
        """Calculate Kubelka-Munk values"""
        reflectance = np.clip(reflectance, 0.0001, 0.9999)
        return ((1 - reflectance) **2) / (2 * reflectance)

    def extract_spectral_data(reader):
        """Extract spectral data and corresponding X-axis data from reader"""
        data = reader.data
        x = reader.x

        x_units = reader.x_units or "cm^-1"
        x_title = reader.x_title or "Wavelength"

        if data.ndim == 1:
            spectral_data = data.reshape(1, -1)
        elif data.ndim >= 2:
            spectral_dim = None

            if data.shape[-1] == len(x):
                spectral_dim = -1
            elif data.shape[0] == len(x):
                spectral_dim = 0

            if spectral_dim is None:
                for i in range(data.ndim):
                    if data.shape[i] == len(x):
                        spectral_dim = i
                        break

            if spectral_dim is None:
                spectral_dim = np.argmin(np.abs(np.array(data.shape) - len(x)))
                print(f"Warning: Unable to determine spectral data dimension, assuming dimension {spectral_dim}")

            if spectral_dim != -1:
                axes = list(range(data.ndim))
                axes.remove(spectral_dim)
                axes.append(spectral_dim)
                data = data.transpose(axes)

            spectral_data = data.reshape(-1, len(x))
        else:
            raise ValueError(f"Unsupported data dimension: {data.ndim}")

        return spectral_data, x, x_title, x_units

    def apply_background_correction(sample_data, background_data, x_sample, x_bg):
        """Apply background correction"""
        if np.array_equal(x_sample, x_bg):
            corrected_data = sample_data / background_data
        else:
            corrected_data = np.zeros_like(sample_data)
            for i, spectrum in enumerate(sample_data):
                bg_interp = np.interp(x_sample, x_bg, background_data[0])
                corrected_data[i] = spectrum / bg_interp

        return corrected_data

    def convert_spa_to_csv(input_file, output_file=None, background_path=None, overwrite=False, precision=20):
        """Convert Omnic SPA file to CSV format"""
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")

        if not output_file:
            base_name, _ = os.path.splitext(input_file)
            output_file = f"{base_name}_converted.csv"

        if os.path.exists(output_file) and not overwrite:
            raise FileExistsError(f"Output file already exists: {output_file}")

        try:
            print(f"Reading sample file: {input_file}")
            sample_reader = read(input_file)

            sample_data, x_sample, x_title, x_units = extract_spectral_data(sample_reader)
            y_title, y_units = detect_data_type(sample_reader)

            if background_path:
                if not os.path.exists(background_path):
                    raise FileNotFoundError(f"Background file not found: {background_path}")

                print(f"Reading background file: {background_path}")
                bg_reader = read(background_path)
                bg_data, x_bg, _, _ = extract_spectral_data(bg_reader)

                if y_title == "Reflectance":
                    corrected_data = apply_background_correction(sample_data, bg_data, x_sample, x_bg)
                    y_title = "Corrected Reflectance"
                elif y_title == "Transmittance":
                    corrected_data = sample_data - bg_data
                    y_title = "Corrected Transmittance"
                else:
                    corrected_data = apply_background_correction(sample_data, bg_data, x_sample, x_bg)
                    y_title = f"Corrected {y_title}"

                spectral_data = corrected_data
            else:
                spectral_data = sample_data

            print(f"Data dimension: {spectral_data.shape}")
            print(f"X-axis: {x_title} ({x_units})")
            print(f"Data type: {y_title} ({y_units})")

            # Create DataFrame column data (resolve fragmentation)
            columns_data = {
                f"{x_title} ({x_units})": [float_to_fixed_str(val, precision) for val in x_sample]
            }

            if y_title == "Reflectance" or y_title == "Corrected Reflectance":
                km_data = calculate_kubelka_munk(spectral_data)
                km_title = "Kubelka-Munk"
                km_units = "KM units"

                if km_data.shape[0] == 1:
                    columns_data[f"{km_title} ({km_units})"] = [float_to_fixed_str(val, precision) for val in km_data[0]]
                else:
                    for i in range(km_data.shape[0]):
                        columns_data[f"{km_title}_{i} ({km_units})"] = [float_to_fixed_str(val, precision) for val in km_data[i]]

            if spectral_data.shape[0] == 1:
                columns_data[f"{y_title} ({y_units})"] = [float_to_fixed_str(val, precision) for val in spectral_data[0]]
            else:
                if hasattr(sample_reader, 'spectra_titles') and len(sample_reader.spectra_titles) == spectral_data.shape[0]:
                    for i, title in enumerate(sample_reader.spectra_titles):
                        clean_title = title.strip() or f"{y_title}_{i}"
                        columns_data[f"{clean_title} ({y_units})"] = [float_to_fixed_str(val, precision) for val in spectral_data[i]]
                else:
                    for i in range(spectral_data.shape[0]):
                        columns_data[f"{y_title}_{i} ({y_units})"] = [float_to_fixed_str(val, precision) for val in spectral_data[i]]

            df = pd.DataFrame(columns_data)
            df.to_csv(output_file, index=False, na_rep='nan')
            print(f"Successfully converted and saved to: {output_file}")
            return output_file

        except Exception as e:
            print(f"Conversion failed: {str(e)}")
            return None

    def batch_convert_spa_to_csv(input_dir, output_dir=None, background_path=None, overwrite=False, recursive=False,
                                 precision=20, merge_output=None):
        """Batch convert SPA files in directory to CSV format, with option to merge all CSV files"""
        if not os.path.exists(input_dir):
            raise FileNotFoundError(f"Input directory not found: {input_dir}")

        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        spa_files = []
        for root, _, files in os.walk(input_dir):
            for file in files:
                if file.lower().endswith('.spa'):
                    spa_files.append(os.path.join(root, file))

            if not recursive:
                break

        if not spa_files:
            print(f"No SPA files found in directory: {input_dir}")
            return []

        # Sort by filename
        spa_files.sort()
        output_files = []
        for spa_file in spa_files:
            try:
                if output_dir:
                    rel_path = os.path.relpath(spa_file, input_dir)
                    base_name, _ = os.path.splitext(rel_path)
                    output_file = os.path.join(output_dir, f"{base_name}.csv")
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)
                else:
                    output_file = None

                result = convert_spa_to_csv(spa_file, output_file, background_path, overwrite, precision)
                if result:
                    output_files.append(result)
            except Exception as e:
                print(f"Error processing file {spa_file}: {str(e)}")

        print(f"Batch conversion completed: {len(output_files)}/{len(spa_files)} successful")

        # Merge CSV files
        if merge_output and output_files:
            merge_csv_files(output_files, merge_output, overwrite, precision)

        return output_files

    def merge_csv_files(csv_files, output_path, overwrite=False, precision=20):
        """
        Merge multiple CSV files sequentially, resolve performance warnings and start column names from 0

        Parameters:
            csv_files (list): List of CSV file paths (in order)
            output_path (str): Output path for merged file
            overwrite (bool): Whether to overwrite existing file
            precision (int): Decimal precision for output data
        """
        if not csv_files:
            print("No CSV files to merge")
            return

        # Check if output file exists
        if os.path.exists(output_path) and not overwrite:
            raise FileExistsError(f"Merged output file already exists: {output_path}")

        print(f"Starting merge of {len(csv_files)} CSV files...")

        # Read all dataframes and prepare for merge
        data_frames = []
        x_column = None

        for i, csv_file in enumerate(csv_files):
            df = pd.read_csv(csv_file)

            # Validate X-axis column
            current_x_col = df.columns[0]
            if i == 0:
                x_column = current_x_col
                # Keep X-axis column of first file, rename data columns with suffix _0
                rename_map = {col: f"{col}_0" for col in df.columns[1:]}
                renamed_df = df.rename(columns=rename_map)
                data_frames.append(renamed_df)
            else:
                if current_x_col != x_column:
                    print(f"Warning: X-axis column name in file {csv_file} differs from first file: {current_x_col} vs {x_column}")
                    continue

                # Rename data columns of subsequent files, counting from 1
                file_suffix = f"_{i}"
                rename_map = {col: f"{col}{file_suffix}" for col in df.columns[1:]}
                renamed_df = df.rename(columns=rename_map)
                # Remove X-axis column from subsequent files
                data_frames.append(renamed_df.drop(columns=[current_x_col]))

            print(f"Prepared file {i+1}/{len(csv_files)}: {csv_file}")

        # Merge all dataframes at once (resolve performance warning)
        merged_df = pd.concat(data_frames, axis=1)

        # Save CSV with custom formatting function to ensure fixed decimal precision
        float_format = lambda x: float_to_fixed_str(x, precision)
        merged_df.to_csv(output_path, index=False, na_rep='nan', float_format=float_format)

        print(f"Successfully merged and saved to: {output_path}")
        return output_path

    # Determine if input is file or directory
    if os.path.isfile(input_path):
        # Ensure input is .spa file
        if not input_path.lower().endswith('.spa'):
            raise ValueError(f"Input file is not SPA file: {input_path}")
        # Process single file
        result = convert_spa_to_csv(input_path, output_path, background_path, overwrite, precision)
        if merge_output:
            return [result] if result else []
        return result
    elif os.path.isdir(input_path):
        # Process directory
        return batch_convert_spa_to_csv(input_path, output_path, background_path, overwrite, recursive, precision, merge_output)
    else:
        raise ValueError(f"Input path does not exist: {input_path}")

"curvefit_km_t module:"
def curvefit_km_t(file_path, target_row=1, txt_output_path="curvefit_km_t.txt", png_output_path="curvefit_km_t.png", show_plot=True):
    """
    Read CSV file, perform curve fitting on KM units data of specified row, and visualize results

    Parameters:
    file_path (str): CSV file path
    target_row (int, optional): Target row number (1-based), default is 1
    txt_output_path (str, optional): Output text file path for fitting results
    png_output_path (str, optional): Output PNG file path for fitting image
    show_plot (bool, optional): Whether to show plot, default True

    Returns:
    dict: Dictionary containing fitting parameters, evaluation metrics, and raw data
    """
    try:
        # Read CSV file
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"File read error: {e}")
        return None

    # Check data row count
    rows, columns = df.shape
    if rows < target_row:
        print(f'Data has {rows} rows, less than specified row {target_row}, unable to get corresponding row data')
        return None

    # Get specified row data
    row_data = df.iloc[target_row - 1]
    title = row_data[0]

    # Extract time and KM values
    time = np.array(range(1, len(row_data)))
    km_values = row_data[1:].values

    # Set image clarity and font
    plt.rcParams['figure.dpi'] = 150
    plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Heiti TC', 'sans-serif']

    # Define new fitting function: y = a * x^b * exp(-c * x)
    def new_fit_func(x, a, b, c):
        return a * np.power(x, b) * np.exp(-c * x)

    # Initial parameter guesses
    a_guess = max(km_values)
    b_guess = 0.5
    c_guess = 0.1
    p0 = [a_guess, b_guess, c_guess]

    try:
        # Perform curve fitting
        popt, pcov = curve_fit(new_fit_func, time, km_values, p0=p0, maxfev=5000)

        # Calculate fitted values and R²
        y_fit = new_fit_func(time, *popt)
        residuals = km_values - y_fit
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((km_values - np.mean(km_values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot)

        # Generate fitting function expression
        fit_expr = f"y = {popt[0]:.6f} * x^{popt[1]:.6f} * exp(-{popt[2]:.6f} * x)"

        # Write fitting results to text file
        with open(txt_output_path, "w") as f:
            f.write(f"Fitting Results - {title}\n\n")
            f.write("Fitting function expression:\n")
            f.write(f"{fit_expr}\n\n")
            f.write("Fitting parameters:\n")
            f.write(f"a = {popt[0]:.6f}\n")
            f.write(f"b = {popt[1]:.6f}\n")
            f.write(f"c = {popt[2]:.6f}\n\n")
            f.write(f"R² = {r_squared:.6f}\n")

        print(f"Fitting results successfully written to {txt_output_path}")

        # Create plot
        plt.figure(figsize=(7, 5))
        plt.scatter(time, km_values, marker='o', label='Raw data')
        plt.plot(time, y_fit, 'r-',
                 label=f'Fitted curve: {fit_expr}\nR² = {r_squared:.4f}')

        # Set plot properties
        plt.xlabel('T (s)')
        plt.ylabel('KM units')
        plt.title(title)
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()

        # Save image
        plt.savefig(png_output_path, dpi=300, bbox_inches='tight')
        print(f"Fitting image successfully saved to {png_output_path}")

        # Show plot if needed
        if show_plot:
            plt.show()

        # Return result dictionary
        return {
            'title': title,
            'time': time,
            'km_values': km_values,
            'parameters': {'a': popt[0], 'b': popt[1], 'c': popt[2]},
            'r_squared': r_squared,
            'fitted_values': y_fit,
            'fit_expression': fit_expr
        }

    except Exception as e:
        print(f"Fitting process error: {e}")
        return None

"curvefit_km_wavenumber module:"
def curvefit_km_wavenumber(file_path, time_column_index=1, txt_output_path="curvefit_km_wavenumber.txt",
                      png_output_path="curvefit_km_wavenumber.png"):
    """
    Fit KM values vs wavenumber using Gaussian-Lorentzian hybrid function at specific time

    Parameters:
        file_path: CSV file path, each row represents a wavenumber, each column represents KM values
        time_column_index: Time column index to fit (0-based), default is 1
        txt_output_path: Output text file path
        png_output_path: Output image file path

    Returns:
        Dictionary containing fitting results including parameters, R² value and function expression
    """

    # Gaussian-Lorentzian hybrid function (3 peaks)
    def gaussian_lorentzian(x, a1, x01, sigma1, eta1, a2, x02, sigma2, eta2, a3, x03, sigma3, eta3):
        g1 = a1 * np.exp(-(x - x01) ** 2 / (2 * sigma1 ** 2))
        l1 = a1 / (1 + ((x - x01) / sigma1) ** 2)
        g2 = a2 * np.exp(-(x - x02) ** 2 / (2 * sigma2 ** 2))
        l2 = a2 / (1 + ((x - x02) / sigma2) ** 2)
        g3 = a3 * np.exp(-(x - x03) ** 2 / (2 * sigma3 ** 2))
        l3 = a3 / (1 + ((x - x03) / sigma3) ** 2)
        return eta1 * l1 + (1 - eta1) * g1 + eta2 * l2 + (1 - eta2) * g2 + eta3 * l3 + (1 - eta3) * g3

    # Calculate R² value (goodness of fit)
    def calculate_r_squared(actual, predicted):
        ss_res = np.sum((actual - predicted) ** 2)
        ss_tot = np.sum((actual - np.mean(actual)) ** 2)
        return 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

    # 1. Data reading and preprocessing
    df = pd.read_csv(file_path)

    wavenumbers = df.iloc[:, 0].values  # Wavenumber column is index 0

    # Ensure wavenumbers are monotonically increasing
    is_increasing = np.all(np.diff(wavenumbers) >= 0)
    if not is_increasing:
        print("Detected non-monotonic wavenumbers, auto-correcting with sorting...")
        sorted_indices = np.argsort(wavenumbers)
        wavenumbers = wavenumbers[sorted_indices]
        df = df.iloc[sorted_indices]

    # Filter 1300-1320 cm⁻¹ range
    mask = (wavenumbers >= 1300) & (wavenumbers <= 1320)
    valid_wavenumbers = wavenumbers[mask]
    km_values = df.iloc[mask, time_column_index].values  # Get KM values for specified time column

    # 2. Three-peak fitting
    def fit_3peaks(x, y):
        x_min, x_max = x.min(), x.max()
        x_range = x_max - x_min
        y_max = y.max()

        # Enhanced peak detection
        peaks, _ = find_peaks(y, height=np.percentile(y, 70), distance=5)
        if len(peaks) < 3:
            peaks = [
                np.argmax(y),
                int(len(x) * 0.25),
                int(len(x) * 0.75)
            ]
        peaks = sorted(peaks)

        # Physically constrained initial values
        p0 = [
            y[peaks[0]] * 0.9, x[peaks[0]], max(x_range * 0.05, 0.05), 0.3,
            y[peaks[1]] * 0.6, x[peaks[1]], max(x_range * 0.08, 0.08), 0.5,
            y[peaks[2]] * 0.4, x[peaks[2]], max(x_range * 0.06, 0.06), 0.7
        ]

        # Reasonable constraints
        bounds = (
            [0, x_min, 0.01, 0.2, 0, x_min, 0.01, 0.2, 0, x_min, 0.01, 0.2],
            [np.inf, x_max, x_range, 0.8, np.inf, x_max, x_range, 0.8, np.inf, x_max, x_range, 0.8]
        )

        # Ensure initial values are within constraints
        for i in range(len(p0)):
            p0[i] = max(bounds[0][i], min(p0[i], bounds[1][i]))

        try:
            popt, pcov = curve_fit(
                gaussian_lorentzian, x, y, p0=p0, bounds=bounds,
                maxfev=100000, method='trf'
            )
            predicted = gaussian_lorentzian(x, *popt)
            r_squared = calculate_r_squared(y, predicted)
            return popt, r_squared
        except Exception as e:
            print(f"Three-peak fitting warning: {e}, enabling backup strategy")
            # Backup initial values
            simplified_popt = [
                y_max * 0.5, x.mean() - x_range * 0.2, x_range * 0.05, 0.4,
                y_max * 0.3, x.mean(), x_range * 0.07, 0.5,
                y_max * 0.2, x.mean() + x_range * 0.2, x_range * 0.06, 0.6
            ]
            # Ensure backup values are within constraints
            for i in range(len(simplified_popt)):
                simplified_popt[i] = max(bounds[0][i], min(simplified_popt[i], bounds[1][i]))
            popt, pcov = curve_fit(
                gaussian_lorentzian, x, y, p0=simplified_popt,
                bounds=bounds, maxfev=100000, method='trf'
            )
            predicted = gaussian_lorentzian(x, *popt)
            r_squared = calculate_r_squared(y, predicted)
            return popt, r_squared

    # Fit KM vs wavenumber relationship
    popt, r2 = fit_3peaks(valid_wavenumbers, km_values)

    # 3. Generate fitting function expression
    def format_gaussian_lorentzian(params):
        a1, x01, sigma1, eta1, a2, x02, sigma2, eta2, a3, x03, sigma3, eta3 = params
        expr = "KM(w) = "
        expr += f"{eta1:.6f} * ({a1:.6f} / (1 + ((w - {x01:.6f}) / {sigma1:.6f})^2)) + "
        expr += f"{1 - eta1:.6f} * ({a1:.6f} * exp(-(w - {x01:.6f})^2 / (2 * {sigma1:.6f}^2))) + "
        expr += f"{eta2:.6f} * ({a2:.6f} / (1 + ((w - {x02:.6f}) / {sigma2:.6f})^2)) + "
        expr += f"{1 - eta2:.6f} * ({a2:.6f} * exp(-(w - {x02:.6f})^2 / (2 * {sigma2:.6f}^2))) + "
        expr += f"{eta3:.6f} * ({a3:.6f} / (1 + ((w - {x03:.6f}) / {sigma3:.6f})^2)) + "
        expr += f"{1 - eta3:.6f} * ({a3:.6f} * exp(-(w - {x03:.6f})^2 / (2 * {sigma3:.6f}^2)))"
        return expr

    # Generate function expression
    km_expr = format_gaussian_lorentzian(popt)

    # Write to file
    with open(txt_output_path, "w") as f:
        f.write("===== Fitting Function Expression =====\n\n")
        f.write("Gaussian-Lorentzian hybrid function for KM vs wavenumber:\n")
        f.write(f"{km_expr}\n\n")
        f.write("===== Goodness of Fit =====\n")
        f.write(f"R² value: {r2:.6f}\n")

    print(f"Fitting function expression successfully written to {txt_output_path}")

    # 4. Visualize fitting results
    plt.rcParams["font.family"] = ["Arial Unicode MS", "Heiti TC", "sans-serif"]
    plt.rcParams["axes.unicode_minus"] = True

    plt.figure(figsize=(12, 6))
    plt.scatter(valid_wavenumbers, km_values, color='blue', label='Raw data')

    # Generate fitted curve
    x_fit = np.linspace(valid_wavenumbers.min(), valid_wavenumbers.max(), 1000)
    y_fit = gaussian_lorentzian(x_fit, *popt)
    plt.plot(x_fit, y_fit, 'r-', label=f'Fitted curve (R²={r2:.4f})')

    plt.title('Fitted Relationship between KM Values and Wavenumber')
    plt.xlabel('Wavenumber (cm⁻¹)')
    plt.ylabel('KM Value')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # Save image
    plt.savefig(png_output_path, dpi=300, bbox_inches='tight')
    print(f"Fitting result image successfully saved to {png_output_path}")

    # Show image (optional)
    plt.show()

    # Return key fitting results
    return {
        'popt': popt,
        'r2': r2,
        'km_expr': km_expr,
        'valid_wavenumbers': valid_wavenumbers,
        'km_values': km_values
    }

"curvefit_km_t_wavenumber module："
def curvefit_km_t_wavenumber(file_path, wavenumber_min=1300, wavenumber_max=1320,
                             output_txt_path="curvefit.txt", output_img_path="curvefit.png",
                             peak_num=3):
    """
    Perform 3D fitting on time-wavenumber-KM value data, return fitting results
    and generate visualizations and text reports.

    Parameters:
        file_path (str): Path to CSV data file
        wavenumber_min (float): Lower limit of wavenumber range, default 1300 cm⁻¹
        wavenumber_max (float): Upper limit of wavenumber range, default 1320 cm⁻¹
        output_txt_path (str): Output text report path, default "curvefit.txt"
        output_img_path (str): Output image path, default "curvefit.png"
        peak_num (int): Number of peaks to use in fitting, default 3
    """

    # Dynamically create Gaussian-Lorentzian mixture function (based on number of peaks)
    def create_gaussian_lorentzian(num_peaks):
        def func(x, *params):
            result = np.zeros_like(x)
            param_len = 4  # Each peak has 4 parameters: a, x0, sigma, eta
            for i in range(num_peaks):
                a = params[i * param_len]
                x0 = params[i * param_len + 1]
                sigma = params[i * param_len + 2]
                eta = params[i * param_len + 3]

                gaussian = a * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))
                lorentzian = a / (1 + ((x - x0) / sigma) ** 2)
                result += eta * lorentzian + (1 - eta) * gaussian
            return result

        return func

    # Power-exponential time function (for initial b value calculation)
    def power_exp_func_original(t, a, b, c):
        return a * t ** b * np.exp(-c * t)

    # Calculate R² (goodness of fit)
    def calculate_r_squared(actual, predicted):
        ss_res = np.sum((actual - predicted) ** 2)
        ss_tot = np.sum((actual - np.mean(actual)) ** 2)
        return 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

    # 1. Data reading and preprocessing
    df = pd.read_csv(file_path)
    wavenumbers = df.iloc[:, 0].values
    first_column_name = df.columns[0]
    print(f"Automatically using first column '{first_column_name}' as wavenumber data")

    # Ensure wavenumbers are monotonically increasing
    if not np.all(np.diff(wavenumbers) >= 0):
        print("Detected non-monotonic wavenumbers, auto-correcting...")
        sorted_indices = np.argsort(wavenumbers)
        wavenumbers = wavenumbers[sorted_indices]
        df = df.iloc[sorted_indices]

    # Filter specified wavenumber range
    mask = (wavenumbers >= wavenumber_min) & (wavenumbers <= wavenumber_max)
    valid_wavenumbers = wavenumbers[mask]
    time = np.arange(1, df.shape[1])

    print(f"Using wavenumber range: {wavenumber_min} - {wavenumber_max} cm⁻¹")
    print(f"Filtered to {len(valid_wavenumbers)} valid wavenumber data points")
    print(f"Using number of peaks: {peak_num}")

    # 2. Two-step fitting: First get b value to calculate constant k, then fix k to fit a(w) and c(w)
    a_temp, b_temp, c_temp = [], [], []
    for w in valid_wavenumbers:
        try:
            row_idx = np.where(wavenumbers == w)[0][0]
            km_values = df.iloc[row_idx, 1:].values
            km_values = savgol_filter(km_values, window_length=5, polyorder=2)

            # Initial value estimation
            early_mean = np.mean(km_values[:int(len(km_values) * 0.1)])
            late_mean = np.mean(km_values[-int(len(km_values) * 0.1):])
            a_guess = max(early_mean - late_mean, 0.1)
            b_guess = 0.5 if km_values[-1] > km_values[0] * 0.5 else 1.0
            c_guess = 0.05 if km_values[-1] > km_values[0] * 0.5 else 0.2

            # Constrained fitting
            popt, _ = curve_fit(
                power_exp_func_original, time, km_values, p0=[a_guess, b_guess, c_guess],
                maxfev=20000, bounds=([0, 0, 0], [np.inf, np.inf, np.inf])
            )
            a_temp.append(popt[0])
            b_temp.append(popt[1])
            c_temp.append(popt[2])
        except Exception as e:
            print(f"Wavenumber {w} initial fitting failed: {e}")
            a_temp.append(np.nan)
            b_temp.append(np.nan)
            c_temp.append(np.nan)

    # Calculate constant k
    k = np.nanmean(b_temp)
    print(f"Calculated constant k value: {k:.6f}")

    # Filter invalid data
    valid_mask = ~np.isnan(a_temp) & ~np.isnan(b_temp) & ~np.isnan(c_temp)
    valid_wavenumbers = valid_wavenumbers[valid_mask]
    a_temp = np.array(a_temp)[valid_mask]
    b_temp = np.array(b_temp)[valid_mask]
    c_temp = np.array(c_temp)[valid_mask]

    if len(valid_wavenumbers) < 12:
        raise ValueError("Insufficient valid data points (minimum 12 required)")

    # Second step: Fix k value and refit
    def power_exp_func_fixed_k(t, a, c):
        return a * t ** k * np.exp(-c * t)

    a_list, c_list = [], []
    a_r2_list, c_r2_list = [], []

    for i, w in enumerate(valid_wavenumbers):
        try:
            row_idx = np.where(wavenumbers == w)[0][0]
            km_values = df.iloc[row_idx, 1:].values
            a_guess = a_temp[i]
            c_guess = c_temp[i]

            popt, _ = curve_fit(
                power_exp_func_fixed_k, time, km_values, p0=[a_guess, c_guess],
                maxfev=20000, bounds=([0, 0], [np.inf, np.inf]))
            predicted = power_exp_func_fixed_k(time, *popt)
            r_squared = calculate_r_squared(km_values, predicted)

            a_list.append(popt[0])
            c_list.append(popt[1])
            a_r2_list.append(r_squared)
            c_r2_list.append(r_squared)
        except Exception as e:
            print(f"Wavenumber {w} secondary fitting failed: {e}")
            a_list.append(np.nan)
            c_list.append(np.nan)
            a_r2_list.append(np.nan)
            c_r2_list.append(np.nan)

    # Filter invalid data again
    valid_mask2 = ~np.isnan(a_list) & ~np.isnan(c_list)
    valid_wavenumbers = valid_wavenumbers[valid_mask2]
    a_vals = np.array(a_list)[valid_mask2]
    c_vals = np.array(c_list)[valid_mask2]
    a_r2 = np.array(a_r2_list)[valid_mask2]
    c_r2 = np.array(c_r2_list)[valid_mask2]

    if len(valid_wavenumbers) < 12:
        raise ValueError("Insufficient valid data points after secondary fitting (minimum 12 required)")

    # 3. Multi-peak fitting (based on peak_num parameter)
    def fit_peaks(x, y, num_peaks):
        # Create mixture function
        gl_func = create_gaussian_lorentzian(num_peaks)

        x_min, x_max = x.min(), x.max()
        x_range = x_max - x_min
        y_max = y.max()

        # Peak detection
        peaks, _ = find_peaks(y, height=np.percentile(y, 70), distance=5)
        if len(peaks) < num_peaks:
            peaks = list(peaks)
            # Supplement missing peaks
            while len(peaks) < num_peaks:
                candidate = int(len(x) * len(peaks) / (num_peaks + 1))
                peaks.append(candidate)
        peaks = sorted(peaks)[:num_peaks]  # Take only first num_peaks peaks

        # Initial values setup
        p0 = []
        bounds_lower = []
        bounds_upper = []
        for i in range(num_peaks):
            peak_idx = peaks[i] if i < len(peaks) else int(len(x) * (i + 1) / (num_peaks + 1))
            a_val = y[peak_idx] * (0.9 - i * 0.2)
            x0_val = x[peak_idx]
            sigma_val = max(x_range * 0.05, 0.05)
            eta_val = 0.3 + i * 0.1

            p0.extend([a_val, x0_val, sigma_val, eta_val])
            bounds_lower.extend([0, x_min, 0.01, 0.2])
            bounds_upper.extend([np.inf, x_max, x_range, 0.8])

        # Ensure initial values are within bounds
        for i in range(len(p0)):
            p0[i] = max(bounds_lower[i], min(p0[i], bounds_upper[i]))

        try:
            popt, _ = curve_fit(
                gl_func, x, y, p0=p0,
                bounds=(bounds_lower, bounds_upper),
                maxfev=500000, method='trf'
            )
            predicted = gl_func(x, *popt)
            r_squared = calculate_r_squared(y, predicted)
            return popt, r_squared
        except Exception as e:
            print(f"{num_peaks}-peak fitting failed: {e}")
            # Fallback strategy: Use simpler initial values
            simple_p0 = []
            for i in range(num_peaks):
                a_val = y_max * (0.5 - i * 0.1)
                x0_val = x_min + (i + 1) / (num_peaks + 1) * x_range
                sigma_val = x_range * 0.05
                eta_val = 0.5
                simple_p0.extend([a_val, x0_val, sigma_val, eta_val])

            popt, _ = curve_fit(
                gl_func, x, y, p0=simple_p0,
                bounds=(bounds_lower, bounds_upper),
                maxfev=500000, method='trf'
            )
            predicted = gl_func(x, *popt)
            r_squared = calculate_r_squared(y, predicted)
            return popt, r_squared

    # Fit spectral distributions for a and c
    popt_a, r2_a = fit_peaks(valid_wavenumbers, a_vals, peak_num)
    popt_c, r2_c = fit_peaks(valid_wavenumbers, c_vals, peak_num)

    # Get final mixture function
    gl_func = create_gaussian_lorentzian(peak_num)

    # 4. Construct 3D KM function
    def km_3d(t, w):
        a = gl_func(w, *popt_a)
        c = gl_func(w, *popt_c)
        return a * t ** k * np.exp(-c * t)

    # 5. Generate grid data
    t_grid = np.linspace(time[0], time[-1], 30)
    w_grid = valid_wavenumbers.reshape(-1, 1)

    km_grid = np.zeros((len(valid_wavenumbers), len(t_grid)))
    for i, w in enumerate(valid_wavenumbers):
        for j, t in enumerate(t_grid):
            km_grid[i, j] = km_3d(t, w)

    # Original data grid
    original_km_grid = np.zeros_like(km_grid)
    for i, w in enumerate(valid_wavenumbers):
        row_idx = np.where(wavenumbers == w)[0][0]
        km_values = df.iloc[row_idx, 1:].values
        original_km_grid[i, :] = np.interp(t_grid, time, km_values)

    # 6. Calculate overall R²
    actual_values = original_km_grid.flatten()
    predicted_values = km_grid.flatten()
    r2_overall = calculate_r_squared(actual_values, predicted_values)

    # 7. Format function expressions
    def format_gl_func(params, func_name, num_peaks):
        expr = f"{func_name}(w) = "
        for i in range(num_peaks):
            a = params[i * 4]
            x0 = params[i * 4 + 1]
            sigma = params[i * 4 + 2]
            eta = params[i * 4 + 3]

            expr += f"{eta:.6f} * ({a:.6f} / (1 + ((w - {x0:.6f}) / {sigma:.6f})^2)) + "
            expr += f"{1 - eta:.6f} * ({a:.6f} * exp(-(w - {x0:.6f})^2 / (2 * {sigma:.6f}^2)))"
            if i < num_peaks - 1:
                expr += " + "
        return expr

    # Generate function expressions
    a_expr = format_gl_func(popt_a, "a", peak_num)
    c_expr = format_gl_func(popt_c, "c", peak_num)
    km_3d_expr = f"km_3d(t, w) = a(w) * t^{k:.6f} * exp(-c(w))"

    # Ensure output directories exist
    os.makedirs(os.path.dirname(output_txt_path) or ".", exist_ok=True)
    os.makedirs(os.path.dirname(output_img_path) or ".", exist_ok=True)

    # Write to file
    with open(output_txt_path, "w") as f:
        f.write("===== Fitted Function Expressions =====\n\n")
        f.write(f"Number of peaks used: {peak_num}\n\n")
        f.write("1. Mixture function for parameter a:\n")
        f.write(f"{a_expr}\n\n")
        f.write("2. Mixture function for parameter c:\n")
        f.write(f"{c_expr}\n\n")
        f.write("3. 3D KM function:\n")
        f.write(f"{km_3d_expr}\n\n")
        f.write(f"Wavenumber range used: {wavenumber_min} - {wavenumber_max} cm⁻¹\n")
        f.write(f"CSV first column header: '{first_column_name}'\n\n")
        f.write("===== Goodness of Fit =====\n")
        f.write(f"R² for parameter a: {r2_a:.6f}\n")
        f.write(f"R² for parameter c: {r2_c:.6f}\n")
        f.write(f"Constant k value: {k:.6f}\n")
        f.write(f"Overall surface R²: {r2_overall:.6f}\n")
        f.write(f"Average R² for time function: {np.mean(a_r2):.6f}\n")

    print(f"Fitted function expressions successfully written to {output_txt_path}")

    # 8. Visualization comparison
    plt.rcParams["font.family"] = ["Arial", "DejaVu Sans", "Liberation Sans", "sans-serif"]
    plt.rcParams["axes.unicode_minus"] = False

    fig = plt.figure(figsize=(20, 8))

    # Original data surface
    ax1 = fig.add_subplot(121, projection='3d')
    surf1 = ax1.plot_surface(
        t_grid, w_grid, original_km_grid,
        cmap='viridis', alpha=0.9, edgecolor='none'
    )
    ax1.set_xlabel('Time t (s)')
    ax1.set_ylabel(f'Wavenumber ({wavenumber_min}-{wavenumber_max} cm⁻¹)')
    ax1.set_zlabel('KM Value')
    ax1.set_title('Original Data')

    # Fitted data surface
    ax2 = fig.add_subplot(122, projection='3d')
    surf2 = ax2.plot_surface(
        t_grid, w_grid, km_grid,
        cmap='plasma', alpha=0.9, edgecolor='none'
    )
    ax2.set_xlabel('Time t (s)')
    ax2.set_ylabel(f'Wavenumber ({wavenumber_min}-{wavenumber_max} cm⁻¹)')
    ax2.set_zlabel('KM Value')
    ax2.set_title(f'Fitted Surface (Overall R²: {r2_overall:.4f}, Peaks: {peak_num})')

    # Synchronize viewing angles
    ax2.view_init(elev=30, azim=45)
    ax1.view_init(elev=30, azim=45)

    # Fit evaluation information
    stats_text = (f"Fit Evaluation:\n"
                  f"• Number of peaks: {peak_num}\n"
                  f"• R² for parameter a: {r2_a:.4f}\n"
                  f"• R² for parameter c: {r2_c:.4f}\n"
                  f"• Constant k value: {k:.6f}\n"
                  f"• Average R² for time function: {np.mean(a_r2):.4f}\n"
                  f"• Overall surface R²: {r2_overall:.4f}\n"
                  f"• Wavenumber range: {wavenumber_min}-{wavenumber_max} cm⁻¹\n"
                  f"• CSV first column: '{first_column_name}'")
    fig.text(0.01, 0.01, stats_text, fontsize=9, bbox=dict(facecolor='white', alpha=0.8))

    # Colorbar
    cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])
    fig.colorbar(surf2, cax=cbar_ax)

    plt.tight_layout()

    # Save image
    plt.savefig(output_img_path, dpi=300, bbox_inches='tight')
    print(f"Visualization successfully saved to {output_img_path}")

    # Display image
    plt.show()

    # Output evaluation results
    print(f"===== Fit Evaluation Results =====")
    print(f"Number of peaks used: {peak_num}")
    print(f"CSV first column header: '{first_column_name}'")
    print(f"Wavenumber range used: {wavenumber_min} - {wavenumber_max} cm⁻¹")
    print(f"R² for parameter a: {r2_a:.4f}")
    print(f"R² for parameter c: {r2_c:.4f}")
    print(f"Constant k value: {k:.6f}")
    print(f"Average R² for time function: {np.mean(a_r2):.4f}")
    print(f"Overall surface R²: {r2_overall:.4f}")

    # Return fitting results
    return {
        'k': k,
        'popt_a': popt_a,
        'popt_c': popt_c,
        'r2_a': r2_a,
        'r2_c': r2_c,
        'r2_overall': r2_overall,
        'mean_time_r2': np.mean(a_r2),
        'km_3d_func': km_3d,
        'valid_wavenumbers': valid_wavenumbers,
        'time': time,
        'wavenumber_min': wavenumber_min,
        'wavenumber_max': wavenumber_max,
        'first_column_name': first_column_name,
        'peak_num': peak_num,
        'output_txt_path': output_txt_path,
        'output_img_path': output_img_path
    }


class GrayValueCalculation:
    @staticmethod
    def process_single_image(image_path,
                             red_range, green_range, blue_range,
                             max_valid_width, max_valid_height,
                             region_size,
                             output_dir="results"):
        """Process a single image and return the processing result"""
        # Check if the file exists
        if not os.path.exists(image_path):
            print(f"Error: File '{image_path}' does not exist")
            return None

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Generate result file name (based on original file name and timestamp)
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"{base_name}_results_{timestamp}.txt")

        # Store all output content for writing to file
        output_content = []
        # Store skipped content and valid content separately for separate display
        skipped_content = []
        valid_content = []

        def log(message, is_skipped=False):
            """Output to console and store in content list simultaneously"""
            print(message)
            output_content.append(message + "\n")
            if is_skipped:
                skipped_content.append(message + "\n")
            else:
                valid_content.append(message + "\n")

        # Record processing information
        log(f"===== Image processing started: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} =====")
        log(f"Processing image: {image_path}")
        log(f"RGB ranges - Red: {red_range}, Green: {green_range}, Blue: {blue_range}")
        log(f"Maximum valid region size: {max_valid_width}x{max_valid_height}")
        log(f"Base region size: {region_size}x{region_size}")
        log("----------------------------------------")

        # Open the image and convert to RGB format
        try:
            with Image.open(image_path) as img:
                # Convert to RGB mode to handle compatibility with different image modes
                image = img.convert('RGB')
            log(f"Image size: {image.size[0]}x{image.size[1]} pixels")
        except Exception as e:
            error_msg = f"Error opening image: {e}"
            log(error_msg)
            # Save error information to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.writelines(output_content)
            return None

        pixels = image.load()
        width, height = image.size

        # Parse parameters
        red_min, red_max = red_range
        green_min, green_max = green_range
        blue_min, blue_max = blue_range
        region_edge = region_size  # Side length of the region
        region_offset = region_edge - 1  # Offset for boundary calculation

        # Ensure the region size is valid
        if region_edge <= 0:
            error_msg = "Error: Region size must be a positive number"
            log(error_msg)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.writelines(output_content)
            return None

        # Ensure the image is large enough to contain at least one region
        if width < region_edge or height < region_edge:
            error_msg = f"Error: Image size ({width}x{height}) is smaller than the specified region size ({region_edge}x{region_edge})"
            log(error_msg)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.writelines(output_content)
            return None

        # Step 1: Collect all top-left coordinates (x, y) of qualified regions of specified size
        valid_regions = []
        # Ensure regions do not exceed image boundaries
        for y in range(0, height - region_offset):
            for x in range(0, width - region_offset):
                # Check if all pixels in the region meet RGB range requirements
                match = True
                for dy in range(region_edge):
                    if not match:
                        break
                    for dx in range(region_edge):
                        r, g, b = pixels[x + dx, y + dy]
                        if not (red_min <= r <= red_max and
                                green_min <= g <= green_max and
                                blue_min <= b <= blue_max):
                            match = False
                            break
                if match:
                    valid_regions.append((x, y))

        log(f"Number of qualified base regions found: {len(valid_regions)}")

        # Store average gray values of all valid regions
        all_region_averages = []

        # Step 2: Merge continuously adjacent regions and calculate overall average gray value
        if valid_regions:
            # Group by y-coordinate (regions in the same horizontal strip are grouped together)
            region_groups = defaultdict(list)
            for x, y in valid_regions:
                region_groups[y].append(x)

            log(f"Number of horizontal strips (grouped by y-coordinate): {len(region_groups)}")
            log("----------------------------------------")

            # Iterate through each y group and process regions with continuous x-coordinates
            for y0, x_list in region_groups.items():
                sorted_x = sorted(x_list)
                if not sorted_x:
                    continue

                # Divide continuous x-coordinates into groups
                continuous_groups = []
                current_start = sorted_x[0]
                current_end = sorted_x[0]
                for x in sorted_x[1:]:
                    if x == current_end + 1:
                        current_end = x
                    else:
                        continuous_groups.append((current_start, current_end))
                        current_start = x
                        current_end = x
                continuous_groups.append((current_start, current_end))

                # Calculate overall average gray value for each continuous group
                for start_x, end_x in continuous_groups:
                    # Calculate width and height of the merged region
                    region_width = end_x - start_x + region_edge
                    region_height = region_edge  # Height is fixed as region size

                    # Check if the region exceeds maximum limits
                    if region_width > max_valid_width or region_height > max_valid_height:
                        msg = f"Invalid region exceeding size limit - Top-left coordinate ({start_x}, {y0}), Bottom-right coordinate ({end_x + region_offset}, {y0 + region_offset}), " \
                              f"Size: {region_width}x{region_height}, skipped"
                        # log(msg, is_skipped=True)
                        continue

                    # Calculate average gray value of the region
                    total_gray = 0
                    total_pixels = 0
                    for y_pixel in range(y0, y0 + region_edge):
                        for x_pixel in range(start_x, end_x + region_edge):
                            r, g, b = pixels[x_pixel, y_pixel]
                            gray = int(0.2989 * r + 0.5870 * g + 0.1140 * b)
                            total_gray += gray
                            total_pixels += 1

                    # Output information of the merged region
                    if total_pixels > 0:
                        average_gray = total_gray / total_pixels
                        all_region_averages.append(average_gray)
                        msg = f"Qualified valid region - Top-left coordinate ({start_x}, {y0}), Bottom-right coordinate ({end_x + region_offset}, {y0 + region_offset}), " \
                              f"Size: {region_width}x{region_height}, Average gray value: {average_gray:.2f}"
                        log(msg)

        # Add separator to distinguish skipped content and valid content
        if skipped_content and valid_content:
            separator = "----------"
            print(separator)
            output_content.append(separator + "\n")

        # Calculate and output total average of all valid regions
        log("----------------------------------------")
        overall_average = None
        if all_region_averages:
            overall_average = sum(all_region_averages) / len(all_region_averages)
            msg = f"Average gray value of all qualified valid regions: {overall_average:.2f}"
            log(msg)
        else:
            log("No qualified valid regions found")

        # Record processing end information
        log(f"===== Image processing ended: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} =====")

        # Write results to file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.writelines(output_content)
            print(f"Results saved to: {output_file}\n")
        except Exception as e:
            print(f"Error saving result file: {e}\n")

        return {
            'image_path': image_path,
            'overall_average': overall_average,
            'result_file': output_file
        }

    @staticmethod
    def process_images(input_path,
                       red_range, green_range, blue_range,
                       max_valid_width, max_valid_height,
                       region_size,
                       output_dir="results"):
        """
        Process images, automatically identify whether the input is a single file or a directory

        Parameters:
            input_path: Path to a single image file or a directory containing images
            red_range: Red channel range, tuple (minimum, maximum)
            green_range: Green channel range, tuple (minimum, maximum)
            blue_range: Blue channel range, tuple (minimum, maximum)
            max_valid_width: Maximum valid region width
            max_valid_height: Maximum valid region height
            region_size: Size of the base region to calculate (e.g., 9 represents 9x9 region)
            output_dir: Directory to save result files, default is "results"
        """
        # Check if the input path exists
        if not os.path.exists(input_path):
            print(f"Error: Input path '{input_path}' does not exist")
            return []

        # If it's a single file
        if os.path.isfile(input_path):
            # Check if the file format is supported
            supported_formats = ('.png', '.jpg', '.jpeg', '.tif', '.tiff')
            file_ext = os.path.splitext(input_path)[1].lower()
            if file_ext in supported_formats:
                result = GrayValueCalculation.process_single_image(
                    image_path=input_path,
                    red_range=red_range,
                    green_range=green_range,
                    blue_range=blue_range,
                    max_valid_width=max_valid_width,
                    max_valid_height=max_valid_height,
                    region_size=region_size,
                    output_dir=output_dir
                )
                return [result] if result else []
            else:
                print(f"Error: Unsupported file format '{file_ext}', supported formats are: {supported_formats}")
                return []

        # If it's a directory, perform batch processing
        elif os.path.isdir(input_path):
            # Supported file formats
            supported_formats = ('.png', '.jpg', '.jpeg', '.tif', '.tiff')

            # Get all image files in the directory that meet the format requirements
            image_files = []
            for filename in os.listdir(input_path):
                file_path = os.path.join(input_path, filename)
                # Check if it's a file and the format meets the requirements
                if os.path.isfile(file_path):
                    file_ext = os.path.splitext(filename)[1].lower()
                    if file_ext in supported_formats:
                        image_files.append(file_path)

            if not image_files:
                print(f"No supported image files found in directory '{input_path}'")
                return []

            print(f"Found {len(image_files)} qualified image files, starting batch processing...\n")

            # Store summary information of all processing results
            batch_results = []

            # Process images one by one
            for i, image_path in enumerate(image_files, 1):
                print(f"----- Processing image {i}/{len(image_files)} -----")
                result = GrayValueCalculation.process_single_image(
                    image_path=image_path,
                    red_range=red_range,
                    green_range=green_range,
                    blue_range=blue_range,
                    max_valid_width=max_valid_width,
                    max_valid_height=max_valid_height,
                    region_size=region_size,
                    output_dir=output_dir
                )
                if result:
                    batch_results.append(result)

            # Generate batch processing summary report
            summary_file = os.path.join(output_dir,
                                        f"batch_summary_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
            try:
                with open(summary_file, 'w', encoding='utf-8') as f:
                    f.write(f"===== Batch processing summary report: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} =====\n")
                    f.write(f"Processing directory: {input_path}\n")
                    f.write(f"Total number of images processed: {len(image_files)}\n")
                    f.write(f"Successfully processed: {len(batch_results)}\n")
                    f.write("----------------------------------------\n")
                    f.write("Summary of average gray values for each image:\n")
                    for result in batch_results:
                        avg = result['overall_average'] if result['overall_average'] is not None else "No valid regions"
                        f.write(f"{os.path.basename(result['image_path'])}: {avg}\n")
                    f.write("----------------------------------------\n")
                    f.write(f"Result save directory: {output_dir}\n")

                print(f"Batch processing completed! Summary report saved to: {summary_file}")
            except Exception as e:
                print(f"Error generating summary report: {e}")

            return batch_results

        else:
            print(f"Error: Input path '{input_path}' is neither a file nor a directory")
            return []


class TifToPng:
    """TIF格式到PNG格式的转换工具类"""

    @staticmethod
    def convert_single(input_path, output_path=None):
        """
        将单个TIF文件转换为PNG格式

        参数:
            input_path: TIF文件的路径
            output_path: 输出PNG文件的路径，若为None则在原目录生成同名PNG文件

        返回:
            转换成功返回True，否则返回False
        """
        try:
            # 打开TIF文件
            with Image.open(input_path) as img:
                # 如果未指定输出路径，则在原目录生成同名PNG文件
                if output_path is None:
                    # 获取文件名和目录
                    file_dir, file_name = os.path.split(input_path)
                    # 替换扩展名
                    base_name = os.path.splitext(file_name)[0]
                    output_path = os.path.join(file_dir, f"{base_name}.png")

                # 创建输出目录（如果不存在）
                output_dir = os.path.dirname(output_path)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                # 保存为PNG格式
                img.save(output_path, "PNG")
                print(f"成功转换: {input_path} -> {output_path}")
                return True
        except Exception as e:
            print(f"转换失败 {input_path}: {str(e)}")
            return False

    @staticmethod
    def batch(input_dir, output_dir=None):
        """
        批量转换目录中的所有TIF文件为PNG格式

        参数:
            input_dir: 包含TIF文件的目录
            output_dir: 输出PNG文件的目录，若为None则使用输入目录
        """
        # 检查输入目录是否存在
        if not os.path.isdir(input_dir):
            print(f"错误: 目录 {input_dir} 不存在")
            return

        # 遍历目录中的所有文件
        for file_name in os.listdir(input_dir):
            # 检查文件是否为TIF格式
            if file_name.lower().endswith(('.tif', '.tiff')):
                input_path = os.path.join(input_dir, file_name)

                # 构建输出路径
                if output_dir:
                    base_name = os.path.splitext(file_name)[0]
                    output_path = os.path.join(output_dir, f"{base_name}.png")
                else:
                    output_path = None

                # 转换文件
                TifToPng.convert_single(input_path, output_path)

def Convert3D(file_path):
    """
    将CSV或XLSX文件数据转换为3D可视化图表

    参数:
    file_path (str): CSV或XLSX文件的路径
    """
    try:
        # 根据文件扩展名读取数据
        file_ext = os.path.splitext(file_path)[1].lower()
        if file_ext == '.csv':
            df = pd.read_csv(file_path)
        elif file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            raise ValueError("不支持的文件格式，请提供CSV或XLSX文件")

        # 检查数据是否为空
        if df.empty:
            raise ValueError("文件中没有数据")

        # 检查列数是否足够
        if df.shape[1] < 2:
            raise ValueError("文件至少需要包含两列数据")

        # 设置图片清晰度
        plt.rcParams['figure.dpi'] = 150

        # 设置 matplotlib 支持中文
        plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei', 'Heiti TC', 'SimHei']
        plt.rcParams['axes.unicode_minus'] = False

        # 创建三维图形对象
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        # 获取坐标轴标签（从列名获取）
        x_label = df.columns[0]
        z_label = '数据系列'  # 可以根据需要修改

        # 遍历从第二列开始的每一列
        for col_index in range(1, df.shape[1]):
            x = df.iloc[:, 0]
            z = [col_index - 1] * len(df)
            y = df.iloc[:, col_index]
            ax.plot(x, y, z, label=df.columns[col_index])

        # 设置坐标轴标签
        ax.set_xlabel(x_label)
        ax.set_zlabel(z_label)
        ax.set_ylabel('数值')  # 可以根据需要修改或从数据中获取

        # 添加图例
        ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')

        # 调整布局
        plt.tight_layout()

        # 显示图形
        plt.show()

    except FileNotFoundError:
        print(f"错误: 找不到文件 '{file_path}'")
    except Exception as e:
        print(f"发生错误: {str(e)}")


def insert_crystals(host_path, insert_path, center, radius, num, tolerance=0.9,
                    max_attempts=1000, output_path=None,view_crystals=True):
    """
    将晶体结构插入到主体结构中

    参数:
        host_path: 主体结构文件路径
        insert_path: 要插入的结构文件路径
        center: 插入区域中心坐标 (x, y, z)
        radius: 插入区域半径
        num: 要插入的数量
        tolerance: 碰撞容忍度 (0.0-1.0)
        max_attempts: 最大尝试次数
        output_path: 输出文件路径，若为None则不保存
        view_crystals:是否可视化生成的晶体结构（默认为TRUE）

    返回:
        插入后的结构对象
    """
    # 晶体半径字典，用于判断原子间距离是否合适
    CRYSTAL_RADII = {
        'Cu': 1.40, 'Fe': 1.40, 'Ni': 1.40,
        'Na+': 0.95, 'Cl-': 1.81, 'K+': 1.33,
        'H': 1.20, 'O': 1.52, 'C': 1.70,
        'default': 1.75
    }

    def get_minimal_displacement(pos1, pos2, cell, pbc):
        """计算考虑周期性边界条件的最小位移向量"""
        delta = pos1 - pos2
        scaled = np.linalg.solve(cell.T, delta.T).T

        for i in range(3):
            if pbc[i]:
                scaled[:, i] -= np.round(scaled[:, i])

        return np.dot(scaled, cell)

    def get_crystal_radius(atom):
        """获取原子的晶体半径"""
        symbol = atom.symbol
        return CRYSTAL_RADII.get(symbol, CRYSTAL_RADII['default'])

    def check_molecular_overlap(host, insert, tolerance):
        """检查分子与主体结构之间是否存在重叠"""
        host_pos = host.get_positions()
        insert_pos = insert.get_positions()

        # 计算分子质心和最大半径
        centroid = np.mean(insert_pos, axis=0)
        max_offset = max(np.linalg.norm(p - centroid) for p in insert_pos)
        mol_radius = max_offset + max(get_crystal_radius(a) for a in insert)

        # 使用KDTree快速查找潜在的碰撞原子
        host_tree = cKDTree(host_pos)
        neighbors = host_tree.query_ball_point(centroid, mol_radius)

        if not neighbors:
            return False

        host_radii = [get_crystal_radius(a) for a in host]
        insert_radii = [get_crystal_radius(a) for a in insert]

        # 详细检查潜在碰撞
        for h_idx in neighbors:
            h_pos = host_pos[h_idx]
            h_rad = host_radii[h_idx]
            for i_pos, i_rad in zip(insert_pos, insert_radii):
                delta = get_minimal_displacement(h_pos, i_pos, host.cell, host.pbc)
                distance = np.linalg.norm(delta)
                if distance < (h_rad + i_rad) * tolerance:
                    return True
        return False

    def check_ionic_overlap(host, insert, tolerance):
        """检查离子与主体结构之间是否存在重叠"""
        host_pos = host.get_positions()
        insert_pos = insert.get_positions()
        host_radii = [get_crystal_radius(a) for a in host]
        insert_radii = [get_crystal_radius(a) for a in insert]

        max_host_rad = max(host_radii)
        host_tree = cKDTree(host_pos)

        # 对每个插入原子检查是否与主体原子碰撞
        for i_pos, i_rad in zip(insert_pos, insert_radii):
            query_radius = (max_host_rad + i_rad) * tolerance
            neighbors = host_tree.query_ball_point(i_pos, query_radius)
            for h_idx in neighbors:
                h_rad = host_radii[h_idx]
                h_pos = host_pos[h_idx]
                delta = get_minimal_displacement(h_pos, i_pos, host.cell, host.pbc)
                distance = np.linalg.norm(delta)
                if distance < (h_rad + i_rad) * tolerance:
                    return True
        return False

    def random_in_sphere(center, radius):
        """在球内生成随机点"""
        theta = np.random.uniform(0, 2 * np.pi)
        phi = np.arccos(np.random.uniform(-1, 1))
        r = radius * np.random.uniform(0, 1) ** (1 / 3)

        return np.array([
            r * np.sin(phi) * np.cos(theta),
            r * np.sin(phi) * np.sin(theta),
            r * np.cos(phi)
        ]) + center

    def process_structure(struct):
        """处理结构，确定其类型并设置适当的晶胞"""
        if len(struct) == 0:
            struct.info['crystal_type'] = 'unknown'
            return struct

        pos = struct.positions
        min_dist = max_dist = avg_dist = 0
        if len(pos) > 1:
            dists = np.linalg.norm(pos[:, None] - pos, axis=2)
            np.fill_diagonal(dists, np.inf)
            min_dist = np.min(dists)
            max_dist = np.max(dists)
            avg_dist = np.mean(dists[dists < np.inf])

        has_ions = any(s in a.symbol for a in struct for s in ['+', '-'])

        # 确定晶体类型
        if len(struct) == 1:
            struct.info['crystal_type'] = 'atomic'
        elif min_dist < 1.5 and max_dist < 5.0 and not has_ions:
            struct.info['crystal_type'] = 'molecular'
        elif avg_dist > 2.0 and has_ions:
            struct.info['crystal_type'] = 'ionic'
        else:
            struct.info['crystal_type'] = 'atomic'

        # 设置适当的晶胞
        if not np.any(struct.cell):
            span = np.ptp(pos, axis=0)
            scale_factor = 4.0 if struct.info['crystal_type'] == 'molecular' else 3.0
            struct.cell = np.diag(span * scale_factor + 10.0)
            struct.center()
        return struct

    def safe_insert_cluster(host, cluster, check_overlap, tolerance):
        """安全地插入团簇，处理可能的错误"""
        original_host = host.copy()
        try:
            if not check_overlap(host, cluster, tolerance):
                host += cluster
                return True
            return False
        except Exception as e:
            # 出错时恢复原始状态
            host.positions = original_host.positions
            host.numbers = original_host.numbers
            host.cell = original_host.cell
            print(f"插入错误: {str(e)}")
            return False

    # 主逻辑实现
    # 读取并处理主体和插入结构
    host = process_structure(read(host_path))
    insert = process_structure(read(insert_path))
    original_insert = insert.copy()

    # 根据晶体类型选择合适的插入策略
    strategies = {
        'molecular': (check_molecular_overlap, 'rigid'),
        'ionic': (check_ionic_overlap, 'rigid'),
        'atomic': (check_ionic_overlap, 'single')
    }
    check_overlap, move_mode = strategies.get(
        insert.info['crystal_type'],
        (check_ionic_overlap, 'single')
    )

    success = 0
    attempts = 0

    # 尝试插入指定数量的结构
    while success < num and attempts < max_attempts:
        attempts += 1
        new_pos = random_in_sphere(center, radius)

        candidate = original_insert.copy()
        if move_mode == 'rigid':
            # 刚性移动整个分子/离子团
            original_centroid = np.mean(candidate.positions, axis=0)
            candidate.positions += new_pos - original_centroid

            # 调整到晶胞周期内
            current_centroid = np.mean(candidate.positions, axis=0)
            frac_centroid = np.linalg.solve(host.cell.T, current_centroid)
            for i in range(3):
                if host.pbc[i]:
                    frac_centroid[i] %= 1.0
            adjusted_centroid = np.dot(frac_centroid, host.cell)

            delta = adjusted_centroid - current_centroid
            candidate.positions += delta

            # 确保完全在主晶胞内
            frac_coords = np.linalg.solve(host.cell.T, candidate.positions.T).T
            min_floor = np.floor(frac_coords.min(axis=0))
            shift = np.dot(min_floor, host.cell)
            candidate.positions -= shift
        else:
            # 单个原子移动
            candidate.positions += new_pos

        # 检查并插入
        if safe_insert_cluster(host, candidate, check_overlap, tolerance):
            success += 1
            print(f"成功插入 {success}/{num}")

    print(f"插入完成: 尝试次数 {attempts}, 成功率 {success / (attempts + 1e-6):.1%}")

    # 保存结果（如果指定了输出路径）
    if output_path:
        write(output_path, host, wrap=False)
        print(f"最终结构已保存到 {output_path}，原子总数: {len(host)}")

    if view_crystals:
        atoms = read(output_path)
        view(atoms)

    return host