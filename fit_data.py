import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

def celsius_to_fahrenheit(T):
    """Convert celsius to fahrenheit."""
    return T * 9/5 + 32

def get_user_input():
    """
    Prompt the user for input of:
    1) Data source file relative path
    2) Regression fit option, linear or quadratic
    """
    # Ask for the file name of the data
    file_path = input("\nEnter the file relative path (with .xlsx): ")

    # Ask for the fit option
    while True:
        fit_option = input("Choose the fit option (linear or quadratic): ").lower()
        if fit_option in ["linear", "quadratic"]:
            break
        else:
            print(f"Invalid option: '{fit_option}'. Please choose 'linear' or 'quadratic'.")
    
    return file_path, fit_option

def read_data(file_path):
    """Read the excel data. Clean NaN and unused cells."""
    data = pd.read_excel(file_path, header=None, names=['Time-Stamp', 'Temperature/°C', 'Temperature/°F'])

    data = data.dropna(how='any', axis=0, ignore_index=True) # Remove NaN due to empty cells
    data = data[pd.to_numeric(data['Temperature/°C'], errors='coerce').notnull()] # Remove non-numeric rows

    data['Time-Stamp'] = pd.to_datetime(data['Time-Stamp'])
    data['Temperature/°C'] = data['Temperature/°C'].astype('float64')

    print('\nData extracted:')
    print(data)
    return data

def fit_data(data, fit_option):
    """
    Fit regression model to the data.
    """
    x = data['Time-Stamp'].values
    y = data['Temperature/°C'].values
    x_num = mdates.date2num(x)

    # Compute fitted parameters
    if fit_option == "linear":
        params = np.polyfit(x_num, y, 1)
        params_labels = ['a', 'b']
        print(f"\nLinear fit parameters: ax + b")
    elif fit_option == "quadratic":
        params = np.polyfit(x_num, y, 2)
        params_labels = ['a', 'b', 'c']
        print(f"\nQuadratic fit parameters: ax^2 + bx + c")
    else:
        raise NotImplementedError
    
    # Make predictions
    data["Prediction/°C"] = np.polyval(params, x_num)
    data["Prediction/°F"] = celsius_to_fahrenheit(data["Prediction/°C"])

    params = pd.DataFrame([params], columns=params_labels)

    return data, params

def save_fit_params(params, fit_option, data_folder_path):
    """Save fitted parameters to .csv file."""
    save_path = os.path.join(data_folder_path, f"{fit_option}_fit_parameters.csv")
    params.to_csv(save_path, index=False)
    print(params.to_string(index=False))

def save_predictions(data, fit_option, data_folder_path):
    """Save predictions to .csv file."""
    save_path = os.path.join(data_folder_path, f"{fit_option}_predictions.csv")
    data.to_csv(save_path, index=False)
    print("\nPredictions:")
    print(data)

def plot_data(data, fit_option, data_folder_path):
    """Plot data and the fitted curve, and save to .png file."""
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.plot_date(data["Time-Stamp"], data["Temperature/°C"], 'bo', label='Original Data')
    ax.plot_date(data["Time-Stamp"], data["Prediction/°C"], 'r-', label='Fitted Line')

    # Format the date on the x-axis
    ax.xaxis.set_minor_locator(mdates.HourLocator(interval=1))   # every 1 hour
    ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M:%S'))  # hours, minutes and seconds
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))    # every day
    ax.xaxis.set_major_formatter(mdates.DateFormatter('\n%d-%m-%Y')) 

    ax.set_xlabel('Time Stamp')
    ax.set_ylabel('Temperature ($^\circ$C)')
    ax.set_title(f'{fit_option.capitalize()} Fit')
    ax.legend()

    fig.tight_layout()
    save_path = os.path.join(data_folder_path, f"{fit_option}_fit.png")
    plt.savefig(save_path, bbox_inches="tight", dpi=200)

def main():
    data_file_path, fit_option = get_user_input()

    data_folder_path = os.path.dirname(data_file_path)
    data = read_data(data_file_path)

    data, params = fit_data(data, fit_option)

    save_fit_params(params, fit_option, data_folder_path)
    save_predictions(data, fit_option, data_folder_path)
    plot_data(data, fit_option, data_folder_path)

if __name__ == "__main__":
    main()
