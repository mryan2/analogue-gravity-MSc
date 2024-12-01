# START OF CODE ---------------------------------------------------------------
# -----------------------------------------------------------------------------
# Library imports
# -----------------------------------------------------------------------------
# Python code reduces memory usage by only loading the minimum amount of
# components by default. Additional so-called Libraries/Packages must
# therefore be declared explicitly.

# This is done by the use of an import statement which
# - finds the module
# - loads the code
# - makes its functions & variables available.
#
# Imports are either from
# - the standard Python library or
# - from a third-party library.

# ------------------------
# Standard library imports
# ------------------------
from tkinter import (
    BOTH,
    Button,
    DoubleVar,
    Frame,
    IntVar,
    Label,
    LEFT,
    OptionMenu,
    Scale,
    StringVar,
    Tk,
    TOP,
    Toplevel,
    X
)
from datetime import datetime  # Get the current date and time
import time                    # Used for loop timing purposes
import math

# Import the necessary system information modules. These are for displaying
# information at the beginning of the run and (when needed) for testing.
from sys import (
    getwindowsversion,
    version             # Specify Python version
)

# Import threading components because the GUI cannot run in the same process
# as the main loop.
from threading import Thread, Event, Lock

# ----------------------------
# Third-party library imports
# ----------------------------
from pyautogui import size   # Used for obtaining screen resolution

# Import the "process and system utilities" library, here for obtaining CPU
# information.
from psutil import cpu_count, cpu_freq, cpu_percent

from matplotlib import colors as mcolors  # Use for converting string to RGB

import taichi as ti  # Use for enhancing rendering performance
ti.init(arch=ti.cpu,
        kernel_profiler=True)  # Force Taichi to use GPU (if available)

# -------------------------------------------------------------
# Construct the Tkinter GUI containing the sliders and buttons
# through which the user input controls the application.
# -------------------------------------------------------------
# Import essential components from the tkinter library for
# creating the GUI.
# These include widgets for
# - the layout (Frame, Label),
# - user interaction (Button, Slider), and
# - variable management (DoubleVar, IntVar, StringVar).

root = Tk()  # Create the main application window

root.config(bg="black")
root.attributes('-topmost', 1)  # Set GUI window to be on top of all others

# Set the GUI window to be non-resizable and disable its window dragging.
root.resizable(False, False)

# Create a frameless window (no title bar, no borders) for simplicity and
# aesthetics.
root.overrideredirect(True)

# Set the GUI screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
GUI_width = int(screen_width/5)
GUI_height = int(screen_height)
root.geometry(f"{GUI_width}x{GUI_height}+0+0")

# Get variables from the GUI, to be used for program control and the
# computations.
tkinter_outer_orbital_radius = DoubleVar()
tkinter_spheres_to_display = IntVar()
tkinter_inner_sphere_mass = IntVar()
tkinter_outer_sphere_mass = IntVar()
tkinter_vertical_scale = IntVar()
tkinter_smoothing_window_size = IntVar()
tkinter_horiz_angle_deg = DoubleVar()
tkinter_vert_angle_deg = DoubleVar()

tkinter_camera_zoom = DoubleVar()
tkinter_grid_chequer_size = IntVar()

# The size of the grid, representing a square 2D array, where the grid size
# corresponds to one side of the square. The grid size is hard coded here.
# Its optimal value must be empirically determined, however.
# Its value is already needed at this point in the code, for the slider
# definitions.
# Since we require one cell to represent the centre coordinates of the grid,
# the grid side lengths need to be an odd number.
grid_size = 500 + 1

# Scale grid element size (default 1 unit) to a real astronomical distance
# (in metres) by a factor of 10000.
astro_length_scaling = 1e3
formatted_astro_length_scaling = format(astro_length_scaling, ".0e")

# Define reusable variable structures for horizontal slider configuration.
horizontal_slider_arguments = {
    "bg": "light steel blue",
    "troughcolor": "steel blue",
    "orient": "horizontal"
}

# Create a slider widget to control the radius of the outer sphere's orbit.
# The relative masses of the two spheres, swapping if necessary, ensures
# that the outer sphere has the greater orbit of the two, so the slider's
# range goes from 0 to half the grid size.
slider_outer_orbital_radius = Scale(
    label=(
        "Outer Sphere Orbital Radius (m x "
        + formatted_astro_length_scaling
        + ")"
    ),
    variable=tkinter_outer_orbital_radius,
    from_=0,
    to=grid_size / 2,
    tickinterval=(grid_size / 2 - 10) / 4,
    **horizontal_slider_arguments
)

# Set padding for widget placement (horizontal and vertical) to 2 pixels.
padx, pady = 2, 2
slider_outer_orbital_radius.set(grid_size // 3)
slider_outer_orbital_radius.pack(
    side=TOP,
    padx=padx * 2,
    pady=(pady * 2, pady),
    fill=BOTH
)

# Define dictionaries for two packing options of the widgets.
pack_top = {
    "side": TOP,
    "padx": padx,
    "pady": pady,
    "fill": X
}
pack_left = {
    "side": LEFT,
    "padx": padx,
    "pady": pady,
    "fill": X,
    "expand": True
}

# -----------------------------------------------------------------------------
# Create a frame to hold the widgets for the parameters related to the spheres.
frame = Frame(root, bg="black")
frame.pack(**pack_top)

slider_spheres_to_display = Scale(
    frame,
    label="# Spheres",
    variable=tkinter_spheres_to_display,
    from_=0, to=2,
    tickinterval=1,
    **horizontal_slider_arguments
)
slider_spheres_to_display.pack(**pack_left)
slider_spheres_to_display.set(2)
slider_inner_sphere_mass = Scale(
    frame,
    label="Mass 1 [M⊙]",
    variable=tkinter_inner_sphere_mass,
    from_=1, to=50,
    tickinterval=25,
    **horizontal_slider_arguments
)
slider_inner_sphere_mass.pack(**pack_left)
slider_inner_sphere_mass.set(4)
slider_outer_sphere_mass = Scale(
    frame,
    label="Mass 2 [M⊙]",
    variable=tkinter_outer_sphere_mass,
    from_=1, to=50,
    tickinterval=25,
    **horizontal_slider_arguments
)
slider_outer_sphere_mass.pack(**pack_left)
slider_outer_sphere_mass.set(4)

# -----------------------------------------------------------------------------
# Define reusable variable structures for vertical slider configuration,
# including background color, trough color, orientation, and a length
# proportional to the GUI height.
# -----------------------------------------------------------------------------
vertical_slider = {
    "bg": "light steel blue",
    "troughcolor": "steel blue",
    "orient": "vertical",
    "length": GUI_height / 5
}

#------------------------------------------------------------------------------ 
# Create a frame for vertical scaling and smoothing. Adjusting the slider
# within this frame allows the user to set the sheet perturbations (waves)
# to different heights, offering better visibility, if needed.
# -----------------------------------------------------------------------------
frame = Frame(root, bg="black")
frame.pack(**pack_top)

# Add a vertical scale slider within this frame.
slider_vertical_scale = Scale(
    frame,
    label="Vertical Scale",
    variable=tkinter_vertical_scale,
    from_=20,
    to=0,
    **vertical_slider
)
slider_vertical_scale.pack(**pack_left)
slider_vertical_scale.set(10)
# Create a vertical slider within the frame to control the smoothing window
# size, which adjusts the level of smoothing applied to the sheet
# perturbations.
slider_smoothing_window_size = Scale(
    frame,
    label="Smoothing",
    variable=tkinter_smoothing_window_size,
    from_=25, to=0,
    resolution=2,
    **vertical_slider
)
slider_smoothing_window_size.pack(**pack_left)
slider_smoothing_window_size.set(11)

#------------------------------------------------------------------------------
# Create and configure sliders for controlling the camera's movement and
# viewpoint. These sliders allow the user to adjust the camera's position
# and orientation in 3D space, providing control over vertical and
# horizontal look direction and zooming.
# -----------------------------------------------------------------------------
frame = Frame(root, bg="black")
frame.pack(**pack_top)

# Camera left/right movement control slider
slider_horiz_angle_deg = Scale(
    frame,
    label="View L/R (degrees)",
    variable=tkinter_horiz_angle_deg,
    from_=-180.0, to=+180.0, resolution=0.01,
    tickinterval=60,
    **horizontal_slider_arguments
)
slider_horiz_angle_deg.pack(**pack_left)
slider_horiz_angle_deg.set(0)

frame = Frame(root, bg="black")
frame.pack(**pack_top)
# Camera look-up/down control slider
slider_vert_angle_deg = Scale(
    frame,
    label="View U/D (degrees)",
    variable=tkinter_vert_angle_deg,
    from_=-30.0, to=90.0, resolution=0.01,
    **vertical_slider
)
slider_vert_angle_deg.pack(**pack_left)   
slider_vert_angle_deg.set(45.0)

# Camera Zoom
slider_camera_zoom = Scale(
    frame,
    label="Zoom",
    variable=tkinter_camera_zoom, 
    from_=15.0, to=1.0, resolution=0.1,
    **vertical_slider
)
slider_camera_zoom.pack(**pack_left)   
slider_camera_zoom.set(2.0)

# -----------------------------------------------------------------------------
# Create a resizeable chequerboard/"table cloth" colour pattern
# -----------------------------------------------------------------------------
frame = Frame(root, bg="black")
frame.pack(**pack_top)
slider_grid_chequer_size = Scale(
    frame,
    label="Grid Chequer Size",
    variable=tkinter_grid_chequer_size,
    from_=0, to=100, resolution=1,
    **horizontal_slider_arguments
)
slider_grid_chequer_size.pack(**pack_left)
slider_grid_chequer_size.set(0.0)
frame = Frame(root, bg="black")
frame.pack(side=TOP, fill=X, padx=padx, pady=pady)

# Initialize a StringVar to hold the selected run option
run_option = StringVar()
run_option.set("Select a Run Option")  # Default prompt for selection

# List of available options for the run selection
options_list = ["Set outer sphere orbital radius",
                "Inspiralling",
                "Test 1 - two of four borders damped",
                "Test 2 - all four borders damped"]

# Create a run option selector (dropdown) for selecting a run option
# from the list.
run_option_dropdown = OptionMenu(frame,
                                 run_option,
                                 *options_list)
run_option_dropdown.config(bg="light steel blue")
run_option_dropdown.pack(**pack_left)

frame = Frame(root, bg="black")
frame.pack(**pack_top)

# -----------------------------------------------------------------------------
# Initialize the dictionary to hold shared data for the simulation.
# This includes flags, thread references, and various parameters related
# to the simulation's state and physics calculations.
# -----------------------------------------------------------------------------
shared_data = {
    'lock': Lock(),
    'running': False,
    'simulation_thread': None,
    'elapsed_time': 0.0,
    'fps': 0.0,
    'astro_orbital_separation': 0.0,
    'astro_outer_sphere_orbital_speed': 0.0,
    'astro_omega': 0.0,
    'model_omega': 0.0,
    'binary_energy_loss_rate': 0.0,
    'astro_orbital_decay_rate': 0.0
}

# -----------------------------------------------------------------------------
# These are declared in the "base" code block scope, because the mouse scroll
# function is required to be bound to the GUI tkinter root at the end 
# of the code.
# -----------------------------------------------------------------------------
camera_position_x = 0.0
camera_position_y = 0.0

# -----------------------------------------------------------------------------
# Function definitions for startup and main control
# -----------------------------------------------------------------------------
# Toggle the running of the simulation
def start_stop_simulation(shared_data):
    """
    Toggles the state of the simulation between running and stopped.

    When the simulation is not running, this function initiates the simulation
    by setting the 'running' flag to True, creating a new thread to execute 
    the main simulation code, and updating the button text to indicate the 
    simulation can be stopped. The info window is also scheduled to open in 
    the main thread.

    When the simulation is running, the function stops it by setting the 
    'running' flag to False, clearing the simulation thread, updating the 
    button text to indicate the simulation can be started, and scheduling 
    the info window to close.

    Shared Data Keys:
        - 'lock': A threading lock to ensure exclusive access to shared 
          resources.
        - 'running': Boolean flag to indicate the simulation's running state.
        - 'simulation_thread': The thread object for running the main 
          simulation code.

    Button Configurations:
        - Changes button text and background color based on simulation state.

    Returns:
        None
    """
    with shared_data['lock']:
        # Reset keys without replacing the entire dictionay.
        if not shared_data['running']:  # Start the simulation
            shared_data.update({
                'running': True,
                'simulation_thread': None,
                'elapsed_time': 0.0,
                'fps': 0.0,
                'astro_orbital_separation': 0.0,
                'astro_outer_sphere_orbital_speed': 0.0,
                'astro_omega': 0.0,
                'model_omega': 0.0,
                'binary_energy_loss_rate': 0.0,
                'astro_orbital_decay_rate': 0.0
            })
            shared_data['simulation_thread'] = Thread(
                target=mainline_code,
                args=(shared_data,)
            )
            shared_data['simulation_thread'].start()
            button_start_stop_simulation.config(
                text="STOP Simulation",
                bg="orange"
            )
            # Schedule the info window creation in the main thread
        else:  # Stop the simulation but keep the GUI displayed
            button_start_stop_simulation.config(
                text="START Simulation",
                bg="light green"
            )
            root.after(0, close_info_window)
            shared_data['simulation_thread'] = None
            shared_data['running'] = False
button_start_stop_simulation = Button(
    frame,
    width=25,
    text="START Simulation",
    command=lambda: start_stop_simulation(shared_data),
    bg="light green"
)
button_start_stop_simulation.pack(padx=padx, pady=pady)

# -----------------------------------------------------------------------------
# Respond to user input to pause the run
# -----------------------------------------------------------------------------
simulation_paused = Event()

def pause_the_simulation():
    """
    Toggles the simulation between paused and running states.

    When the simulation is running, this function pauses it by setting the 
    'simulation_paused' event and updating the button text and background 
    color to indicate that the simulation can be resumed.

    When the simulation is paused, this function resumes it by clearing the 
    'simulation_paused' event and restoring the button text and color to 
    indicate that the simulation can be paused again.

    During pausing, the vertical height and surface smoothing can still be
    adjusted.

    Button Configurations:
        - Updates button text and background color based on pause state.

    Returns:
        None
    """
    if simulation_paused.is_set():
        simulation_paused.clear()
        button_pause_the_simulation.config(text="PAUSE", bg="light yellow")
    else:
        simulation_paused.set()
        button_pause_the_simulation.config(
            text="resume after pause",
            bg="yellow"
        )
button_pause_the_simulation = Button(
    frame,
    width=25,
    text="PAUSE",
    bg="light yellow",
    command=pause_the_simulation
)
button_pause_the_simulation.pack(padx=padx, pady=pady)


def import_parameters_from_gui():
    """
    Retrieve user-defined simulation parameters from the graphical user 
    interface (GUI).

    This function collects various parameters inputted or adjusted by the user 
    through the GUI. These parameters control aspects of the simulation such 
    as the characteristics of the spheres, visual and smoothing settings, 
    and camera positioning. Parameters like vertical scaling and smoothing 
    can also be dynamically modified during the simulation.

    Parameters:
        None

    Returns:
        tuple: A collection of parameters retrieved from the GUI, including:
            - outer_orbital_radius (float): The orbital radius of the outer 
              sphere.
            - spheres_to_display (str): Specifies which spheres to display.
            - inner_sphere_mass (float): The mass of the inner sphere.
            - outer_sphere_mass (float): The mass of the outer sphere.
            - vertical_scale (float): The scale factor for vertical 
              adjustments.
            - smoothing_window_size (int): The size of the smoothing window.
            - horiz_angle_deg (float): Horizontal angle of the camera in 
              degrees.
            - vert_angle_deg (float): Vertical angle of the camera in degrees.
            - camera_zoom (float): The zoom level of the camera.
            - grid_chequer_size (int): Size of the chequer pattern on the grid.

    Notes:
        - The parameters are for initializing and dynamically updating the 
          simulation.
    """
    outer_orbital_radius = tkinter_outer_orbital_radius.get()
    spheres_to_display = tkinter_spheres_to_display.get()
    inner_sphere_mass = tkinter_inner_sphere_mass.get()
    outer_sphere_mass = tkinter_outer_sphere_mass.get()
    vertical_scale = tkinter_vertical_scale.get()
    smoothing_window_size = tkinter_smoothing_window_size.get()
    horiz_angle_deg = tkinter_horiz_angle_deg.get()
    vert_angle_deg = tkinter_vert_angle_deg.get()
    camera_zoom = tkinter_camera_zoom.get()
    grid_chequer_size = tkinter_grid_chequer_size.get()
    return (
        outer_orbital_radius,
        spheres_to_display,
        inner_sphere_mass,
        outer_sphere_mass,
        vertical_scale,
        smoothing_window_size,
        horiz_angle_deg,
        vert_angle_deg,
        camera_zoom,
        grid_chequer_size
    )


def show_system_information():
    print("==============================")
    print("      System Information      ")
    print("==============================")
    print("")
    print("Runtime")
    print("=======")
    now = datetime.now()
    formatted_time = now.strftime("%H:%M:%S")  # Format as HH:MM:SS
    print(formatted_time)
    print("")
    print("Windows Version")
    print("===============")
    print(getwindowsversion())
    print("")
    print("Version of the Python Interpreter")
    print("=================================")
    print(version)
    print("")
    print("Hardware, CPU Info")
    print("==================")
    print("Physical cores:", cpu_count(logical=False))
    print("Total cores:", cpu_count(logical=True))
    print("CPU Usage Per Core:")
    for current_core, percentage in enumerate(
            cpu_percent (percpu=True, 
                         interval=1)
        ):
        print(f"   Core {current_core + 1}: {percentage}%")
    print(f"Total CPU Usage: {cpu_percent()}%")
    cpufreq = cpu_freq()
    print(f"Max Frequency: {cpufreq.max:.2f} MHz")
    print(f"Min Frequency: {cpufreq.min:.2f} MHz")
    print(f"Current Frequency: {cpufreq.current:.2f} MHz")
    print("")
    print("Screen resolution")
    print("=================")
    print("width = " + str(screen_width) + ", "
          + "height = " + str(screen_height))
    print("")
    print("")
    return


def start_info_window(root, shared_data):
    """
    Creates a fixed-position, non-resizable information window at the 
    bottom-right corner of the screen, displaying real-time application
    metrics.

    The `Toplevel` window is styled with a black background and white text, 
    and remains on top of other windows. It includes labels for metrics such as 
    elapsed time, FPS, orbital parameters, and energy rates, which are updated 
    dynamically.

    Parameters:
        - root (Tk): Parent application window.
        - shared_data (dict): Shared data dictionary for thread-safe access to 
            real-time metrics, using a lock mechanism.

    Returns:
        - info_window (Toplevel): The created information window.
        - labels (dict): Dictionary of dynamically-updated labels, keyed by metric name.

    Notes:
        - The window is always on top and has a fixed size and position.
        - Label contents are initially empty and should be updated during the 
          application's main loop.
    """
    with shared_data['lock']:
        shared_data = {
            'elapsed_time': 0.0,
            'fps': 0.0,
            'astro_orbital_separation': 0.0,
            'astro_outer_sphere_orbital_speed': 0.0,
            'astro_omega': 0.0,
            'model_omega': 0.0,
            'binary_energy_loss_rate': 0.0,
            'astro_orbital_decay_rate': 0.0
        }
    info_window = Toplevel(root)
    info_window.attributes('-topmost', 1)
    info_window_width = screen_width // 5
    info_window_height = screen_height // 4
    info_x_pos = screen_width - info_window_width
    info_y_pos = screen_height - info_window_height
    info_window.geometry(
        f"{info_window_width}x{info_window_height}+{info_x_pos}+{info_y_pos}")
    info_window.overrideredirect(True)
    info_window.config(bg="black")

    def create_label(window, text="", fg="white", bg="black"):
        label = Label(window, text=text, fg=fg, bg=bg)
        label.pack()
        return label

    # Initialize labels
    labels = {  
        "": create_label(info_window), # Blank line label
        "elapsed_time_label": create_label(info_window),
        "fps_label": create_label(info_window),
        "astro_orbital_separation_label": create_label(info_window),
        "astro_outer_speed_label": create_label(info_window),
        "astro_omega_label": create_label(info_window),
        "model_omega_label": create_label(info_window),
        "binary_energy_loss_rate_label": create_label(info_window),
        "astro_orbital_decay_rate_label": create_label(info_window),
    }
    return info_window, labels


def update_info_window(
        run_option_value, 
        shared_data, 
        info_window, 
        labels
    ):
    """
    Update the information display in the Toplevel info window.
    
    This function updates various labels in the info window with real-time data 
    from the `shared_data` dictionary. It ensures that the window exists 
    before updating it and proceeds to update both general and specific labels
    based on the simulation's current state. 
    The function includes handling for elapsed time, frames per second (FPS), 
    and additional simulation parameters such as orbital separation, 
    orbital speed, angular velocities, energy loss rate, and 
    orbital decay rate.
    
    Parameters:
        - run_option_value (str): A string representing the current run option 
          selected by the user, influencing the type of simulation data 
          displayed.
        - shared_data (dict): A dictionary containing the shared data, 
          including real-time values like elapsed time, FPS, and simulation 
          parameters.
        - info_window (Toplevel): The Tkinter window where the information is 
          displayed.
        - labels (dict): A dictionary of Tkinter labels corresponding to the 
          various information fields, which will be updated with the new 
          values.
    
    Returns:
        None
    
    Notes:
        - The function ensures thread-safe access to shared data by using 
          the `shared_data['lock']`.
        - The labels are updated with formatted strings displaying values like 
          time, speed, and energy loss rate.
    """
    # Ensure the window exists before attempting to update it
    if not info_window.winfo_exists():
        return  # Exit if the window is closed or destroyed
    
    elapsed_time = shared_data['elapsed_time']
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    current_fps = shared_data['fps']
    
    with shared_data['lock']:
        # Update labels common to all cases
        labels["elapsed_time_label"].config(
            text = f"Elapsed Time: {int(hours):02}:"
                   f"{int(minutes):02}:{int(seconds):02}"
        )
        labels["fps_label"].config(text=f"FPS: {current_fps:.2f}")
        
        # Conditionally load data and update specific labels
        if run_option_value in ["Set outer sphere orbital radius", 
                                "Inspiralling"]:
            current_astro_orbital_separation = (
                shared_data['astro_orbital_separation']
            )
            current_outer_speed = (
                shared_data['astro_outer_sphere_orbital_speed']
            )
            current_astro_omega = shared_data['astro_omega']
            current_model_omega = shared_data['model_omega']
            energy_loss_rate = shared_data['binary_energy_loss_rate']
            orbital_decay_rate = shared_data['astro_orbital_decay_rate']
            labels["astro_orbital_separation_label"].config(
                text=f"Astro Orbital Separation:"
                     f" {current_astro_orbital_separation:.2e} m"
            )
            labels["astro_outer_speed_label"].config(
                text=f"Astro Outer Sphere Orbital Speed:"
                     f" {current_outer_speed:.2e} m/s"
            )
            labels["astro_omega_label"].config(
                text=f"Astro Ω: {current_astro_omega:.2e} rad/s"
            )
            labels["model_omega_label"].config(
                text=f"Model Ω: {current_model_omega:.2e} rad/s"
            )
            labels["binary_energy_loss_rate_label"].config(
                text=f"Astro Binary Energy Loss Rate: {energy_loss_rate:.2e} W"
            )
            labels["astro_orbital_decay_rate_label"].config(
                text=f"Astro Orbital Decay Rate: {orbital_decay_rate:.2e} m/s"
            )
            
    # Schedule the next update, 500 ms
    info_window.after(500,
                      update_info_window, 
                      run_option_value, 
                      shared_data, 
                      info_window, labels)
            

# Close the information display window at the end of a run.
def close_info_window():
    """
    Close all Toplevel windows associated with the main application.

    This function iterates through the application's child windows and 
    destroys any Toplevel windows, typically called at the end of a run.
    """
    for window in root.winfo_children():
        if isinstance(window, Toplevel):
            window.destroy()


@ti.kernel
def initialize_array_of_vectors(
        array_to_be_initialized: ti.template(),
        grid_size: ti.i32):
    """
    Initialize a 2D array of vectors with integer grid coordinates.

    This function iterates over a `grid_size x grid_size` array and sets each 
    vector within `array_to_be_initialized` to contain its grid coordinates 
    and a zero for the second array dimension representing the height.
    Specifically, each vector at position `(i, j)` is initialized as 
    `[i, 0.0, j]`.

    Parameters:
        - array_to_be_initialized (ti.template()): The 2D array of vectors to 
          initialize, typically a Taichi field with a shape of 
          `(grid_size, grid_size, 3)`.
        - grid_size (int): The size of the grid along each dimension, defining 
          the bounds of `i` and `j` (0 to `grid_size - 1`).
    """
    for i in range(grid_size):
        for j in range(grid_size):
            array_to_be_initialized[i, j][0] = i
            array_to_be_initialized[i, j][1] = 0.0
            array_to_be_initialized[i, j][2] = j


@ti.kernel
def increment_polar_angle(
        initial_outer_orbital_radius: ti.f64,
        outer_orbital_radius: ti.f64,
        previous_polar_angle: ti.f64,
        polar_angle_increment: ti.f64) -> ti.f64:
    """
    Increment the polar angle for an orbital simulation.

    This function computes the new polar angle based on the previous polar 
    angle, the angular step size, and the ratio of the current and initial 
    outer orbital radii. The calculation adjusts the step size based on the 
    orbital radius, following a formula commonly used in orbital dynamics 
    where the step size depends on the inverse of the radius raised to the 
    power of 3/2.

    Parameters:
        - initial_outer_orbital_radius (float): The initial orbital radius 
          used as a reference for scaling the angular step size.
        - outer_orbital_radius (float): The current orbital radius, which 
          affects the angular step size.
        - previous_polar_angle (float): The polar angle from the previous 
          iteration, used as the starting point for the new angle.
        - polar_angle_increment (float): The angular step size per iteration, 
          before adjusting for the orbital radius.

    Returns:
        float: The updated polar angle, wrapped to stay within the range 
        [0, 360) degrees.

    Notes:
        - The polar angle is incremented according to the inverse power law 
          relative to the orbital radius.
        - The result is wrapped using modulo 360 to ensure the angle stays 
          within the valid range for polar angles (0 to 360 degrees).
    """
    return ((previous_polar_angle
             + polar_angle_increment
             * (outer_orbital_radius / initial_outer_orbital_radius) ** -3/2)
            % 360)


@ti.kernel
def calculate_orbital_coords(
        grid_centre: ti.template(),
        sphere_orbital_radius: ti.f64,
        sphere_polar_angle: ti.f64,
        orbital_coords: ti.template()):
    """
    Calculate the Cartesian coordinates of a sphere on its orbital path.

    This function computes the (x, y, z) coordinates of a sphere based on 
    its orbital radius and polar angle relative to a grid center. The polar 
    angle is converted from degrees to radians before being used to compute 
    the offsets in the x and z dimensions, while the y-coordinate is fixed 
    to 0. The result is stored in the `orbital_coords` template.

    Parameters:
        - grid_centre (ti.template): The 3D coordinates of the grid center, 
          typically a vector, from which the orbital position is offset.
        - sphere_orbital_radius (ti.f64): The orbital radius of the sphere, 
          determining the distance from the grid center in the x-z plane.
        - sphere_polar_angle (ti.f64): The polar angle of the sphere's orbit 
          in degrees, used to calculate its position along the orbital path.
        - orbital_coords (ti.template): A template to store the calculated 
          sphere's coordinates (x, 0, z) based on the orbital parameters.

    Returns:
        None: The function does not return a value, but stores the calculated 
        coordinates in the `orbital_coords` template.

    Notes:
        - The y-coordinate of the sphere is fixed at 0 in this calculation.
        - The polar angle is assumed to be in degrees and is converted to 
          radians before calculating the offsets.
        - The function uses the grid center's x and z coordinates as the 
          reference point for the sphere's orbital position.

    Example:
        If the grid center is at (10, 0, 10), the orbital radius is 5, and the 
        polar angle is 30 degrees, the function will compute the sphere's 
        position relative to the grid center.
    """
    angle_rad = ti.math.radians(sphere_polar_angle)
    x_offset = sphere_orbital_radius * ti.cos(angle_rad)
    y_offset = sphere_orbital_radius * ti.sin(angle_rad)
    orbital_coords[None] = ti.Vector([grid_centre[None][0] + x_offset,
                                      0.0,
                                      grid_centre[None][2] + y_offset])

@ti.kernel
def calculate_model_omega(
        previous_polar_angle: ti.f64,
        current_polar_angle: ti.f64,
        loop_duration: ti.f64) -> ti.f64:
    """
    Calculate the angular velocity (ω) based on the change in polar angle.

    This function computes the angular velocity by calculating the rate of 
    change of the polar angle over a given time period (loop duration), 
    converting the result to radians per unit time. The change in polar 
    angle is determined by the difference between the current and previous 
    polar angles, and the result is scaled to radians per time unit.

    Parameters:
        - previous_polar_angle (ti.f64): The polar angle at the previous time 
          step, in degrees.
        - current_polar_angle (ti.f64): The polar angle at the current time 
          step, in degrees.
        - loop_duration (ti.f64): The time duration over which the change in 
          polar angle occurs, typically in seconds or another time unit.

    Returns:
        ti.f64: The angular velocity (ω) in radians per unit time, calculated 
            as the rate of change of the polar angle.

    Notes:
        - The polar angle is assumed to be in degrees and is converted to 
          radians by multiplying by π/180.
        - The angular velocity is expressed in radians per unit time, 
          computed as the difference in polar angles divided by the loop 
          duration.

    Example:
        If the previous polar angle is 45 degrees, the current polar angle is 
        90 degrees, and the loop duration is 1 second, the angular velocity 
        would be calculated as (90 - 45) * π/180 = 0.785 radians per second.
    """
    polar_angle_increment = current_polar_angle - previous_polar_angle
    return polar_angle_increment / loop_duration * ti.math.pi / 180


@ti.kernel
def compute_distance_between_points(
        first_coordinate_point: ti.template(),
        second_coordinate_point: ti.template()) -> ti.f64:
    """
    Computes the Euclidean distance (norm) between two coordinate points 
    in a 3D space.

    Parameters:
        - first_coordinate_point (ti.template): The first point in 3D space, 
          represented as a Taichi template variable.
        - second_coordinate_point (ti.template): The second point in 3D space, 
          represented as a Taichi template variable.

    Returns:
        ti.f64: The Euclidean distance between the two points.
    """
    return (first_coordinate_point[None] 
            - second_coordinate_point[None]).norm()


@ti.kernel
def model_to_astro_scale(
        model_distance: ti.f64,
        astro_length_scaling: ti.f64) -> ti.f64:
    """
    Converts a distance from the sheet's coordinate system to astronomical 
    distances by applying a scaling factor.

    Parameters:
        - model_distance (ti.f64): The distance in the model's coordinate 
          system.
        - astro_length_scaling (ti.f64): The scaling factor to convert the 
          model distance to the real astronomical scale in metres.

    Returns:
        ti.f64: The corresponding distance in metres.
    """
    return model_distance * astro_length_scaling


@ti.kernel
def calculate_astro_omega(
        astro_orbital_separation: ti.f64,
        newtons_const: ti.f64,
        astro_summed_masses: ti.f64) -> ti.f64:
    """
    Calculates the angular velocity (omega) of an astronomical system 
    based on orbital separation and total mass using Newton's law of 
    gravitation.

    Parameters:
        - astro_orbital_separation (ti.f64): The distance between the two 
          orbiting bodies in astronomical units.
        - newtons_const (ti.f64): Newton's gravitational constant.
        - astro_summed_masses (ti.f64): The sum of the masses of 
          the two bodies.

    Returns:
        ti.f64: The angular velocity (omega) in radians per unit time.
    """
    return ti.math.sqrt(
        newtons_const
        * astro_summed_masses
        / (astro_orbital_separation * astro_orbital_separation
           * astro_orbital_separation)
    )


@ti.kernel
def compute_binary_energy_loss(
        binary_energy_loss_rate_factor: ti.f64,
        astro_orbital_separation: ti.f64,
        astro_omega: ti.f64) -> ti.f64:
    """
    Computes the energy loss rate of a binary astronomical system due to 
    gravitational wave radiation.

    Parameters:
        - binary_energy_loss_rate_factor (ti.f64): A factor that encapsulates 
          the physical constants and parameters relevant to the system's 
          energy loss rate.
        - astro_orbital_separation (ti.f64): The separation distance between 
          the two orbiting bodies in astronomical units.
        - astro_omega (ti.f64): The angular velocity (omega) of the system 
          in radians per unit time.

    Returns:
        ti.f64: The energy loss rate of the binary system.
    """
    return (
        binary_energy_loss_rate_factor
        * astro_orbital_separation ** 4
        * astro_omega ** 6
    )


@ti.kernel
def astro_orbit_decay(
        astro_orbital_separation: ti.f64,
        outer_sphere_mass: ti.f64,
        inner_sphere_mass: ti.f64,
        orbital_decay_factor: ti.f64) -> ti.f64:
    """
    Calculate the rate of orbital decay for a binary system based on its 
    astronomical parameters, using the appropriate general relativistic
    equation.

    This function computes the decay rate of the orbit using the masses of  
    two real astronomical bodies and their actual separation distance, as 
    represented in the scaled-down simulation being rendered. The decay 
    rate accounts for gravitational radiation losses according to general 
    relativity.

    Parameters:
        - astro_orbital_separation (ti.f64): The actual separation distance 
          between the two astronomical bodies, given in units of metres.
        - outer_sphere_mass (ti.f64): The mass of the outer sphere in the 
          astronomical binary system, in units of kilogrammes.
        - inner_sphere_mass (ti.f64): The mass of the inner sphere in the 
          astronomical binary system.
        - orbital_decay_factor (ti.f64): A constant factor applied to scale 
          the orbital decay rate, based on Newton's constant, G, the speed of
          light, c, and the Solar mass.

    Returns:
        ti.f64: The rate of orbital decay for the system, accounting for 
        gravitational radiation losses.
    """
    astro_orbital_decay_rate = (orbital_decay_factor
                                * outer_sphere_mass
                                * inner_sphere_mass)
    astro_orbital_decay_rate *= (outer_sphere_mass + inner_sphere_mass
                                 )/(astro_orbital_separation ** 3)
    return astro_orbital_decay_rate


@ti.kernel
def create_gaussian_perturb_array(
        perturb_radius: ti.i32,
        perturb_max_depth: ti.f64,
        perturb_array: ti.template()):
    """
    Creates a 2D array of vertical positions relative to the unperturbed sheet 
    surface, forming an axially symmetric inverted Gaussian distribution. This 
    represents the gravitational well of each orbiting mass.

    The perturbation values are computed based on a Gaussian function that 
    decreases with distance from the center up to and including the value
    perturb_radius.

    Parameters:
        - perturb_radius (ti.i32): The radius of the (circular) perturbation 
          area in the 2D grid.
        - perturb_max_depth (ti.f64): The maximum depth of the perturbation at 
          the center of the distribution.
        - perturb_array (ti.template): A Taichi field (template) that stores 
          the perturbation values at each point in the 2D grid.

    Returns:
        None: This function updates the perturb_array field in place with the 
        computed perturbation values.
    """
    for index_x, index_y in ti.ndrange(
            (-perturb_radius, perturb_radius + 1),
            (-perturb_radius, perturb_radius + 1)
    ):
        distance_sq = index_x * index_x + index_y * index_y
        temp1 = index_x + perturb_radius
        temp2 = index_y + perturb_radius
        if distance_sq <= perturb_radius * perturb_radius:
            perturb_depth = -ti.exp(
                -((2 * index_x / perturb_radius) ** 2
                  + (2 * index_y / perturb_radius) ** 2)
            ) * perturb_max_depth
            perturb_array[temp1, temp2] = perturb_depth
        else:
            perturb_array[temp1, temp2] = 0.0


@ti.kernel
def overlay_perturb_shape_onto_grid(
        perturb_radius: ti.i32,
        perturb_array: ti.template(),
        orbital_coords: ti.template(),
        oscillator_positions: ti.template(),
        oscillator_velocities: ti.template()):
    """
    Overlay the perturbation shape onto the grid of oscillators (the sheet 
    surface).

    - This function applies the perturbation to the grid surface, centred 
      around the current orbital coordinates of each sphere.
    - The perturbation is applied within a circular radius and affects only 
      the vertical positions of oscillators that are at a higher elevation 
      than the perturbation depth at each point. 
    - Oscillators that are deeper remain unaffected, allowing them to relax
      naturally according to the successive steps of the numerical integration.

    Parameters:
        - perturb_radius (ti.i32): The radius of the perturbation in grid 
          units.
        - perturb_array (ti.template()): A 2D array representing the vertical 
          depth of the perturbation at each point within this radius.
        - orbital_coords (ti.template()): The current x and y coordinates on 
          the surface representing the sphere position, upon which the 
          perturbation shape is overlaid.
        - oscillator_positions (ti.template()): A 2D array containing the 
          vertical positions of all oscillators comprising the rendered 
          surface.
        - oscillator_velocities (ti.template()): A 2D array containing the
          vertical velocity (vector component) of all oscillators comprising
          the rendered surface.

    Note:
        - For oscillators whose positions are modified by the function, 
          the vertical velocity component is reset to zero.
    """
    for offset_x in range(-perturb_radius, perturb_radius + 1):
        for offset_y in range(-perturb_radius, perturb_radius + 1):
            absolute_coords_x = int(orbital_coords[None][0] + offset_x)
            absolute_coords_y = int(orbital_coords[None][2] + offset_y)

            # Compute the 2D matrix of offsets
            offset_vector = ti.Vector([offset_x, offset_y])

            # Calculate the norm (distance) from the center of the perturbation
            distance = offset_vector.norm()

            # Check if the current position is within the perturb radius
            if distance <= perturb_radius:
                # Ensure we are inside the perturbation plane radius.
                perturb_depth = perturb_array[perturb_radius + offset_x,
                                              perturb_radius + offset_y]
                oscillator_depth = oscillator_positions[absolute_coords_x,
                                                        absolute_coords_y][1]
                if perturb_depth < oscillator_depth:
                    oscillator_positions[absolute_coords_x,
                                         absolute_coords_y][1] = perturb_depth
                    oscillator_velocities[absolute_coords_x,
                                          absolute_coords_y][1] = 0.0


@ti.func
def oscillator_is_inside_perturb_zone(
    x: ti.i32,
    y: ti.i32,
    orbital_coords: ti.template(),
    perturb_radius: ti.f64) -> bool:
    """
    Parameters:
        - x (ti.i32): The x-coordinate of the oscillator.
        - y (ti.i32): The y-coordinate of the oscillator.
        - orbital_coords (ti.template): The 3D coordinates of the sphere 
          centre, expected to be a Taichi 3D vector.
        - perturb_radius (ti.f64): The radius of the perturbation zone.

    Returns:
        bool: True if inside the perturbation zone, False otherwise.
    """
    delta = ti.Vector([x - orbital_coords[None][0],
                       y - orbital_coords[None][2]])
    return delta.norm() < perturb_radius


@ti.kernel
def update_oscillator_positions_velocities_RK4(
        effective_grid_start: ti.i32,
        effective_grid_end: ti.i32,
        elastic_constant: ti.f64,
        initial_elastic_extension: ti.f64,
        oscillator_mass: ti.f64,
        adjacent_grid_elements: ti.template(),
        oscillator_positions: ti.template(),
        oscillator_velocities: ti.template(),
        oscillator_accelerations: ti.template(),
        timestep: ti.f64):
    """
    Update the positions and velocities of oscillators using the fourth-order 
    Runge-Kutta (RK4) method.

    This function updates the positions and velocities of oscillators in 
    a 2D grid based on the RK4 integration method. The update takes into 
    account the elastic properties of the sheet and masses of the oscillators.

    Parameters:
        - effective_grid_start (ti.i32): The starting index of the grid 
          to be updated (inclusive).
        - effective_grid_end (ti.i32): The ending index of the grid to be 
          updated (exclusive).
        - elastic_constant (ti.f64): The elastic constant for the oscillators' 
          restoring force.
        - initial_elastic_extension (ti.f64): The initial extension of 
          the oscillators from their equilibrium position.
        - oscillator_mass (ti.f64): The mass of the oscillators.
        - adjacent_grid_elements (ti.template()): Taichi Field containing 
          information about adjacent grid elements for calculating the
          interactions between the oscillators.
        - oscillator_positions (ti.template()): Taichi field holding current 
          positions of the oscillators.
        - oscillator_velocities (ti.template()): Taichi field holding current 
          velocities of the oscillators.
        - oscillator_accelerations (ti.template()): Taichi field holding  
          current accelerations of the oscillators.
        - timestep (ti.f64): The time step for each RK4 iteration.

    Returns:
        None: This function updates the fields, oscillator_positions and 
        oscillator_velocities in-place and does not return any value.
    """
    for i, j in ti.ndrange((effective_grid_start, effective_grid_end),
                           (effective_grid_start, effective_grid_end)):
        vel = oscillator_velocities[i, j]
        pos = oscillator_positions[i, j]
        k1 = timestep * vel
        l1 = timestep * update_oscillator_accelerations(
            i, j, adjacent_grid_elements, oscillator_positions, pos,
            elastic_constant, initial_elastic_extension, oscillator_mass
        )
        k2 = timestep * (vel + 0.5 * l1)
        l2 = timestep * update_oscillator_accelerations(
            i, j, adjacent_grid_elements, oscillator_positions, pos + 0.5 * k1,
            elastic_constant, initial_elastic_extension, oscillator_mass
        )
        k3 = timestep * (vel + 0.5 * l2)
        l3 = timestep * update_oscillator_accelerations(
            i, j, adjacent_grid_elements, oscillator_positions, pos + 0.5 * k2,
            elastic_constant, initial_elastic_extension, oscillator_mass
        )
        k4 = timestep * (vel + l3)
        l4 = timestep * update_oscillator_accelerations(
            i, j, adjacent_grid_elements, oscillator_positions, pos + k3,
            elastic_constant, initial_elastic_extension, oscillator_mass
        )
        # Update velocities first, then the position update.
        oscillator_velocities[i, j] += (l1 + 2 * l2 + 2 * l3 + l4) / 6.0
        oscillator_positions[i, j] += (k1 + 2 * k2 + 2 * k3 + k4) / 6.0


@ti.func
def update_oscillator_accelerations(
        i, j,
        adjacent_grid_elements,
        oscillator_positions,
        pos,
        elastic_constant,
        initial_elastic_extension,
        oscillator_mass):
    """
    Calculate the acceleration of an oscillator based on interactions with 
    adjacent grid elements.

    This function computes the accelerations of the oscillators. 
    This is done by considering the forces on each one exerted by the 
    adjacent oscillators. Hooke's law is then used to to compute the forces, 
    and the acceleration are updated using Newton's second law.

    Parameters:
        - i (int): The row index of the current oscillator in the grid.
        - j (int): The column index of the current oscillator in the grid.
        - adjacent_grid_elements (ti.template()): Taichi field containing 
          offsets of adjacent grid elements. Each entry specifies the relative
          position of a neighboring oscillator.
        - oscillator_positions (ti.template()): Taichi field containing 
          current positions of all oscillators in the grid.
        - pos (ti.Vector): Current position of the oscillator at index (i, j).
        - elastic_constant (ti.f64): The elastic constant that governs the 
          force exerted by the springs between oscillators. All springs 
          modelled have an identical value of this constant.
        - initial_elastic_extension (ti.f64): The initial extension of 
          the oscillators from their equilibrium positions.
        - oscillator_mass (ti.f64): The mass of the oscillator.

    Returns:
        ti.Vector: The computed acceleration of the oscillator at position 
        (i, j), given by Newton's second law, F = ma, where F is the net force
        and m is the mass of the oscillator. All oscillators have identical 
        masses.
    """
    force = ti.Vector.zero(ti.f64, 3)
    for count in range(adjacent_grid_elements.shape[0]):
        offset_i = adjacent_grid_elements[count, 0]
        offset_j = adjacent_grid_elements[count, 1]
        k, l = i + offset_i, j + offset_j
        displacement_vector = pos - oscillator_positions[k, l]
        euclidean_norm = displacement_vector.norm()
        unit_vector = displacement_vector.normalized()
        force -= (elastic_constant * (initial_elastic_extension + 1.0)
                  * euclidean_norm * unit_vector)
        force += elastic_constant * unit_vector
    return force / oscillator_mass  # Newton's second law: F = ma


@ti.kernel
def total_energy_of_sheet(
        grid_size: ti.i32,
        elastic_constant: ti.f64,
        oscillator_positions: ti.template(),
        oscillator_mass: ti.f64,
        oscillator_velocities: ti.template()) -> ti.f64:
    """
    Calculate the total energy of the grid: sum of potential and kinetic energy
    of all the oscillators.

    This function computes the total energy of a grid of oscillators by 
    summing up the potential and kinetic energy for each oscillator. 
    The potential energy is calculated based on the elastic constant and 
    the vertical displacement of each oscillator; the kinetic energy is 
    deterined based on the mass and velocity of each oscillator. The total 
    energy is then scaled down (arbitrarily) by a factor of 1e9.

    Parameters:
        - grid_size (ti.i32): The size of the grid.
        - elastic_constant (ti.f64): The elastic constant.
        - oscillator_positions (ti.template()): Taichi field containing 
          the positions of the oscillators, where the vertical component is 
          used for the potential energy calculation.
        - oscillator_mass (ti.f64): The mass of each oscillator, used to 
          calculate the kinetic energy.
        - oscillator_velocities (ti.template()): Taichi field containing the 
          velocities of the oscillators, where the vertical component is used 
          for kinetic energy calculation.

    Returns:
        ti.f64: The total energy of the grid, which is the sum of potential
        and kinetic energy, divided by 1e9.
    """
    total_potential_energy = 0.0
    total_kinetic_energy = 0.0
    for i, j in ti.ndrange(grid_size, grid_size):
        total_potential_energy += (0.5 * elastic_constant
                                   * oscillator_positions[i, j][1]
                                   * oscillator_positions[i, j][1])
        total_kinetic_energy += (0.5 * oscillator_mass
                                 * oscillator_velocities[i, j][1]
                                 * oscillator_velocities[i, j][1])
    return (total_potential_energy + total_kinetic_energy) / 1e9


@ti.kernel
def normalize_coords_for_rendering(
        rendering_rescale: ti.f64,
        orbital_coords: ti.template(),
        rendered_orbital_coords: ti.template()):
    """
    Rescale sphere coordinates to unit size for rendering.

    Parameters:
        - rendering_rescale (ti.f64): The scaling factor for rendering.
        - orbital_coords (ti.template()): Template for the original sphere 
          coordinates.
        - rendered_orbital_coords (ti.template()): Template for the rescaled 
        - sphere coordinates for rendering.
    """
    rendered_orbital_coords[0] = ti.Vector(
        [orbital_coords[None][0] * rendering_rescale,
         0.0,
         orbital_coords[None][2] * rendering_rescale]
    )


@ti.kernel
def damp_grid_boundary(
        number_of_damped_borders: ti.i32,
        effective_grid_start: ti.i32,
        effective_grid_end: ti.i32,
        damped_grid_boundary_depth: ti.i32,
        boundary_damping_factor: ti.f64,
        oscillator_velocities: ti.template(),
        oscillator_positions: ti.template()):
    """
    Apply damping to oscillator velocities and positions at and near the 
    grid boundaries.
    The damping effect reduces the velocities and positions of the oscillators 
    within the specified boundary regions, with the intensity of damping
    increasing stepwise as the boundary is approached. 

    Parameters:
        - number_of_damped_borders (ti.i32): The number of borders to apply 
          damping to. 
        - effective_grid_start (ti.i32): The starting index of the grid 
          to which damping should be applied (inclusive).
        - effective_grid_end (ti.i32): The ending index of the grid to which 
          damping should be applied (exclusive).
        - damped_grid_boundary_depth (ti.i32): The number of grid cells from 
          the boundary where damping should start.
        - boundary_damping_factor (ti.f64): The maximum damping factor applied 
          at the boundary. The damping decreases linearly from this factor 
          towards zero as it moves away from the boundary.
        - oscillator_velocities (ti.template()): Taichi field containing 
          the current velocities of the oscillators.
        - oscillator_positions (ti.template()): Taichi field containing 
          the current positions of the oscillators. The damping is applied 
          to the second (vertical) component of the positions.

    Returns:
        None: This function modifies the `oscillator_velocities` 
        and `oscillator_positions` fields in-place and does not return any 
        value.
    """
    lower_damping_end_pos = effective_grid_start + damped_grid_boundary_depth
    upper_damping_start_pos = effective_grid_end - damped_grid_boundary_depth

    if number_of_damped_borders == 4:
        for i in range(effective_grid_start, effective_grid_end):
            if i < lower_damping_end_pos:
                layer_damping_factor = (boundary_damping_factor
                                        * (lower_damping_end_pos - i)
                                        / damped_grid_boundary_depth)
                for j in range(effective_grid_start, effective_grid_end):
                    oscillator_velocities[i, j] *= (1 - layer_damping_factor)
                    oscillator_positions[i, j][1] *= (1 - layer_damping_factor)
            elif i >= upper_damping_start_pos:
                layer_damping_factor = (boundary_damping_factor
                                        * (i - upper_damping_start_pos)
                                        / damped_grid_boundary_depth)
                for j in range(effective_grid_start, effective_grid_end):
                    oscillator_velocities[i, j] *= (1 - layer_damping_factor)
                    oscillator_positions[i, j][1] *= (1 - layer_damping_factor)

    for i in range(lower_damping_end_pos, upper_damping_start_pos):
        for j in range(effective_grid_start, lower_damping_end_pos):
            layer_damping_factor = (boundary_damping_factor
                                    * (lower_damping_end_pos - j)
                                    / damped_grid_boundary_depth)
            oscillator_velocities[i, j] *= (1 - layer_damping_factor)
            oscillator_positions[i, j][1] *= (1 - layer_damping_factor)
        for j in range(upper_damping_start_pos, effective_grid_end):
            layer_damping_factor = (boundary_damping_factor
                                    * (j - upper_damping_start_pos)
                                    / damped_grid_boundary_depth)
            oscillator_velocities[i, j] *= (1 - layer_damping_factor)
            oscillator_positions[i, j][1] *= (1 - layer_damping_factor)


@ti.kernel
def rescale_oscillator_heights(
        grid_size: ti.i32,
        vertical_scale: ti.f64,
        oscillator_positions: ti.template(),
        height_rescaled_positions: ti.template()):
    """
    Rescale the vertical height component of oscillator positions.

    This function adjusts the vertical component (y-coordinate) of each 
    oscillator's position in the grid by applying a scaling factor. 
    The horizontal (x) and depth (z) components of the positions remain
    unchanged. The scaled positions are stored in a new Taichi field.

    Parameters:
        - grid_size (ti.i32): The size of the grid, assuming a square grid 
          of `grid_size` x `grid_size`.
        - vertical_scale (ti.f64): The scaling factor to apply to 
          the vertical (y) component of each oscillator's position.
        - oscillator_positions (ti.template()): Taichi field containing 
          the original positions of the oscillators.
        - height_rescaled_positions (ti.template()): Taichi field 
          where the height-rescaled positions will be stored.

    Returns:
        None: This function updates the `height_rescaled_positions` 
        field in-place and does not return any value.
    """
    for i in range(grid_size):
        for j in range(grid_size):
            height_rescaled_positions[i, j] = ti.Vector([
                oscillator_positions[i, j][0],
                oscillator_positions[i, j][1] * vertical_scale,
                oscillator_positions[i, j][2]
            ])


@ti.kernel
def smooth_the_surface(
        grid_size: ti.i32,
        smoothing_start_pos: ti.i32,
        smoothing_end_pos: ti.i32,
        smoothing_window_size: ti.i32,
        smoothed_cell_position: ti.template(),
        height_rescaled_positions: ti.template(),
        smoothed_oscillator_positions: ti.template()):
    """
    Smooth the vertical component of oscillator positions within a specified
    region of the grid.

    This function applies a smoothing operation to the vertical component
    (height) of the oscillator positions within a defined rectangular subregion
    of the grid. The smoothing is performed using a window-based approach, 
    where each position in the region is adjusted by averaging it with its 
    neighboring cells within the specified window size.

    Parameters:
        - grid_size (ti.i32): The size of the grid.
        - smoothing_start_pos (ti.i32): The starting index of the region to 
          apply smoothing (inclusive).
        - smoothing_end_pos (ti.i32): The ending index of the region to apply
          smoothing (inclusive).
        - smoothing_window_size (ti.i32): The size of the window used for
          smoothing. Determines the extent of neighboring positions 
          considered
          in the calculation.
        - smoothed_cell_position (ti.template()): Taichi field used to 
          temporarily store the current cell's position.
        - height_rescaled_positions (ti.template()): Taichi field containing
          the vertical component-rescaled positions of the oscillators.
        - smoothed_oscillator_positions (ti.template()): Taichi field storing
          the smoothed oscillator positions.

    Returns:
        None: This function updates the `smoothed_oscillator_positions` field
        in-place and does not return any value.

    Note:
        The smoothing is purely visual: the results of this computation are
        not fed back into the following iteration cycle.    
    """

    for i in range(grid_size):
        for j in range(grid_size):
            smoothed_oscillator_positions[i, j][0] = (
                height_rescaled_positions[i, j][0]
            )
            smoothed_oscillator_positions[i, j][2] = (
                height_rescaled_positions[i, j][2]
            )
            if (i >= smoothing_start_pos and
                i <= smoothing_end_pos and
                j >= smoothing_start_pos and
                    j <= smoothing_end_pos):
                smoothed_cell_position[None][0] = i
                smoothed_cell_position[None][1] = j
                smoothed_oscillator_positions[i, j][1] = smooth_each_cell(
                    smoothing_start_pos,
                    smoothing_end_pos,
                    smoothing_window_size,
                    smoothed_cell_position,
                    height_rescaled_positions)
            else:
                smoothed_oscillator_positions[i, j][1] = (
                    height_rescaled_positions[i, j][1]
                )


@ti.func
def smooth_each_cell(
        smoothing_start_pos,
        smoothing_end_pos,
        smoothing_window_size,
        smoothed_cell_position,
        height_rescaled_positions) -> ti.f64:
    """
    Calculate the smoothed vertical component for a single cell based on the 
    values of its neighbours.

    This function, operating with the kernel function smooth_the_surface, 
    computes the average vertical height of oscillators within a smoothing 
    window centered on the specified oscillator position. 
    The function returns the average vertical position of oscillators within 
    the window which is then used as the new vertical position of the
    specified oscillator.

    Parameters:
        - smoothing_start_pos (ti.i32): Starting index of the smoothing region
          (inclusive).
        - smoothing_end_pos (ti.i32): Ending index of the smoothing region
          (inclusive).
        - smoothing_window_size (ti.i32): Size of the window used for 
          smoothing. 
        - smoothed_cell_position (ti.template()): Taichi field containing 
          the position of the oscillator height being smoothed. 
        - height_rescaled_positions (ti.template()): Taichi field 
          containing the vertically rescaled positions of the oscillators.

    Returns:
        ti.f64: The average vertical height of oscillators within the smoothing
        window.
    """
    cumulative_sum = 0.0
    for i in range(
        ti.max(
            smoothed_cell_position[None][0] - smoothing_window_size // 2,
            smoothing_start_pos
        ),
        ti.min(
            smoothed_cell_position[None][0] + smoothing_window_size // 2 + 1,
            smoothing_end_pos
        )
    ):
        for j in range(
            ti.max(
                smoothed_cell_position[None][1] - smoothing_window_size // 2,
                smoothing_start_pos
            ),
            ti.min(
                smoothed_cell_position[None][1]
                + smoothing_window_size // 2 + 1,
                smoothing_end_pos
            )
        ):
            cumulative_sum += height_rescaled_positions[i, j][1]
    return cumulative_sum / (smoothing_window_size * smoothing_window_size)


@ti.kernel
def create_grid_surface(
        grid_size: ti.i32,
        smoothing_window_size: ti.i32,
        smoothed_oscillator_positions: ti.template(),
        height_rescaled_positions: ti.template(),
        grid_surface: ti.template()):
    """
    Create the surface to be rendered.

    This function generates a grid surface representation by selecting between 
    two types of oscillator positions:
    1. Smoothed positions, if the smoothing window size is greater than 2.
    2. Height-rescaled positions, if the smoothing window size is 2 or less.

    Parameters:
        - grid_size (ti.i32): The size of the grid.
        - smoothing_window_size (ti.i32): The size of the smoothing window. 
        - smoothed_oscillator_positions (ti.template()): Taichi array 
          representing the full set of smoothed positions of oscillators.
        - height_rescaled_positions (ti.template()): Taichi array 
          representing the full set of height-rescaled oscillator positions.
        - grid_surface (ti.template()): Taichi field to store the resulting 
          grid surface/elastic sheet array. The surface is then populated 
          with either smoothed or original non-smoothed oscillator positions, 
          depending on the user input in the GUI.

    Returns:
        None: This function updates the `grid_surface` field in-place 
        and does not return any value.
    """
    if smoothing_window_size > 2:
        for i in range(grid_size):
            for j in range(grid_size):
                grid_surface[i, j] = smoothed_oscillator_positions[i, j]
    else:
        for i in range(grid_size):
            for j in range(grid_size):
                grid_surface[i, j] = height_rescaled_positions[i, j]


@ti.kernel
def rescale_grid_for_rendering(
        grid_size: ti.i32,
        grid_rescale_for_rendering: ti.f64,
        grid_surface: ti.template(),
        grid_for_rendering: ti.template()):
    """
    The oscillator vectors representing the grid surface are rescaled for 
    rendering by Taichi. This rescaling is necessary because Taichi regards
    the 3D region it renders in the animation window as a 1 x 1 x 1 cube.
    """
    for i in range(grid_size):
        for j in range(grid_size):
            grid_for_rendering[i, j] = (grid_surface[i, j]
                                        * grid_rescale_for_rendering)


def color_longname_to_RGB(
        color_name,
        rgb_color,
        complementary_rgb_color):
    """
    The function determines the initial and complementary colors for 
    rendering the simulated surface by converting a human-readable color name 
    to its RGB representation and computing its complementary color by 
    subtracting each RGB component of the initial color from 1.0. 

    The two colors are used to render a chequerboard pattern unless the 
    user selects a maximal chequer size, in which case the entire surface 
    is treated as a single chequer of the initial color.

    Parameters:
        color_name (str): The name of the color to process, as recognized 
        by Matplotlib.

    Returns:
        tuple:
            - rgb_color (float): The normalized RGB values 
              of the primary color.
            - complementary_rgb_color (float): The normalized 
              RGB values of the complementary color.
    """
    rgb_color = mcolors.to_rgb(color_name)
    for i in range(3):
        complementary_rgb_color[i] = 1.0 - rgb_color[i]
    rgb_color = list(rgb_color)
    return rgb_color, complementary_rgb_color


@ti.kernel
def set_grid_colors(
        grid_size: ti.i32,
        grid_chequer_size: ti.i32,
        rgb_color: ti.template(),
        complementary_rgb_color: ti.template(),
        grid_colors: ti.template()):
    """
    Set colors for a grid with a chequered (chessboard-style) pattern. 
    The chequer size can be varied during runtime.

    Parameters:
        - grid_size (ti.i32): The size of the grid.
        - grid_chequer_size (ti.i32): The size of each chequer on the grid.
        - rgb_color (ti.template()): Template for the normalized 
          RGB color.
        - complementary_rgb_color (ti.template()): Template for the
          complementary normalized RGB color.
        - grid_colors (ti.template()): Template for the grid colors.
    """
    if grid_chequer_size == 0:
        for i, j in ti.ndrange(grid_size, grid_size):
            grid_colors[i * grid_size + j] = rgb_color
    else:
        for i, j in ti.ndrange(grid_size, grid_size):
            if (i // grid_chequer_size + j // grid_chequer_size) % 2 == 0:
                grid_colors[i * grid_size + j] = rgb_color
            else:
                grid_colors[i * grid_size + j] = complementary_rgb_color


@ti.kernel
def set_indices(
        grid_size: ti.i32,
        indices: ti.template()):
    """
    Set triangle indices for constructing the grid surface. This function is 
    executed at the beginning of the run, only once, because the indices do
    not change even when the form of the surface does.

    Parameters:
        - grid_size (ti.i32): The size of the grid.
        - indices (ti.template()): Template for the triangle indices.
    """
    for i, j in ti.ndrange(grid_size, grid_size):
        if i < grid_size - 1 and j < grid_size - 1:
            square_id = (i * (grid_size - 1)) + j
            # 1st triangle of the square
            indices[square_id * 6 + 0] = i * grid_size + j
            indices[square_id * 6 + 1] = (i + 1) * grid_size + j
            indices[square_id * 6 + 2] = i * grid_size + (j + 1)
            # 2nd triangle of the square
            indices[square_id * 6 +
                    3] = (i + 1) * grid_size + j + 1
            indices[square_id * 6 + 4] = i * grid_size + (j + 1)
            indices[square_id * 6 + 5] = (i + 1) * grid_size + j


@ti.kernel
def set_triangle_vertices(
        grid_size: ti.i32,
        grid_surface: ti.template(),
        vertices: ti.template()):
    """
    Set triangle vertices from oscillator positions. This is called for each
    frame of the simulation. The surface is rendered using a triangular mesh
    to approximate its shape.

    Parameters:
        - grid_size (ti.i32): The size of the grid.
          oscillator_positions (ti.template()): Template for the positions of 
          the oscillators.
        - triangle_vertices (ti.template()): Template for the 
          triangle vertices.
    """
    for i, j in ti.ndrange(grid_size, grid_size):
        vertices[i * grid_size + j] = grid_surface[i, j]


def update_camera_view_from_mouse(
    rendering_window,
    vert_angle_deg,
    horiz_angle_deg,
    prev_mouse_pos,
    LMB_already_active,
    slider_vert_angle_deg,
    slider_horiz_angle_deg
):
    """
    Updates the camera view angles based on mouse movement during a left 
    mouse button drag.

    This function adjusts the vertical and horizontal angles of the camera's 
    point of view (POV) according to mouse movements while the left mouse 
    button (LMB) is pressed. The updated angles are also reflected on GUI 
    sliders for visual feedback.

    Parameters:
        - rendering_window (ti.ui.Window): The application window where mouse 
          events are captured.
        - vert_angle_deg (float): The current vertical angle (in degrees) of 
          the camera POV.
        - horiz_angle_deg (float): The current horizontal angle (in degrees) of 
          the camera POV.
        - prev_mouse_pos (tuple): The last recorded mouse position (x, y). 
          Used to calculate the movement delta.
        - LMB_already_active (bool): Tracks whether the left mouse button was 
          already active to prevent reinitializing the drag state.
        - slider_vert_angle_deg (tk.Scale): GUI slider to display the vertical
          angle.
        - slider_horiz_angle_deg (tk.Scale): GUI slider to display the 
          horizontal angle.

    Returns:
        tuple:
            - vert_angle_deg (float): The updated vertical angle (in degrees).
            - horiz_angle_deg (float): The updated horizontal angle (in 
              degrees).
            - prev_mouse_pos (tuple): The updated mouse position as a tuple 
              (x, y).
            - LMB_already_active (bool): Updated state of the LMB activity.

    Notes:
        - Horizontal angle adjustments wrap within [-180, 180] degrees to 
          ensure continuity.
        - Vertical angle adjustments are "clamped" via GUI slider mechanisms, 
          ensuring they stay within valid limits defined externally.
        - Sensitivity factors (horizontal: 200.0, vertical: 100.0) scale the 
          impact of mouse movement on angle changes.
    """
    # Handle mouse drag for POV adjustments
    current_mouse_pos = rendering_window.get_cursor_pos()
    if LMB_already_active:
        if prev_mouse_pos is not None:
            mouse_shift_x = current_mouse_pos[0] - prev_mouse_pos[0]
            mouse_shift_y = current_mouse_pos[1] - prev_mouse_pos[1]

            # Update horiz_angle_deg (left-right rotation)
            horiz_angle_deg_sensitivity = 200.0
            horiz_angle_deg += mouse_shift_x * horiz_angle_deg_sensitivity
            horiz_angle_deg = (horiz_angle_deg + 180) % 360 - 180

            # Update vert_angle_deg (up-down rotation)
            vert_angle_deg_sensitivity = 200.0
            vert_angle_deg -= mouse_shift_y * vert_angle_deg_sensitivity

            slider_vert_angle_deg.set(vert_angle_deg)
            slider_horiz_angle_deg.set(horiz_angle_deg)
        prev_mouse_pos = current_mouse_pos
    else:
        LMB_already_active = True

    return vert_angle_deg, horiz_angle_deg, prev_mouse_pos, LMB_already_active


def update_zoom_from_mouse(
    rendering_window,
    camera_zoom,
    prev_zoom_mouse_pos,
    RMB_already_active,
    slider_camera_zoom
):
    """
    Adjusts the camera zoom level based on mouse movement while the right 
    mouse button (RMB) is pressed.

    This function modifies the `camera_zoom` value by interpreting vertical 
    mouse drag movements as zoom in/out commands. The zoom level is clamped 
    within the range of 1 to 15 for consistency. Updates are reflected in a 
    GUI slider for user feedback.

    Parameters:
        - rendering_window (ti.ui.Window): The application window capturing 
          mouse events.
        - camera_zoom (float): The current zoom level of the camera.
        - prev_zoom_mouse_pos (tuple): The previous mouse position (x, y), 
          used to calculate movement deltas.
        - RMB_already_active (bool): Tracks whether the RMB was already active 
          to manage drag state transitions.
        - slider_camera_zoom (tk.Scale): GUI slider to display and adjust 
          the camera zoom.

    Returns:
        tuple:
            - camera_zoom (float): The updated zoom level.
            - prev_zoom_mouse_pos (tuple): The updated mouse position as 
              (x, y).
            - RMB_already_active (bool): Updated state of the RMB activity.

    Notes:
        - Inverted Y-axis mouse movement (`mouse_shift_y`) is used for zoom 
          adjustments (upward movement zooms out; downward zooms in).
        - The zoom sensitivity is controlled by a scaling factor (10.0).
        - The function ensures thread safety and GUI consistency by "clamping" 
          the zoom level and updating the associated slider.
    """
    current_zoom_mouse_pos = rendering_window.get_cursor_pos()
    if RMB_already_active:
        if prev_zoom_mouse_pos is not None:
            # Inverted Y-axis
            mouse_shift_y = (
                - prev_zoom_mouse_pos[1] 
                + current_zoom_mouse_pos[1]
            )
            zoom_sensitivity = 10.0
            camera_zoom += mouse_shift_y * zoom_sensitivity
            
            # Clamp camera_zoom within the range 1 to 15
            camera_zoom = max(1, min(camera_zoom, 15))
            
            slider_camera_zoom.set(camera_zoom)
        prev_zoom_mouse_pos = current_zoom_mouse_pos
    else:
        RMB_already_active = True

    return camera_zoom, prev_zoom_mouse_pos, RMB_already_active


def mainline_code(shared_data):
    # -------------------------------------------------------------------------
    # Mainline code for simulating the dynamics and emitted gravitational
    # waves for two orbiting spheres in space.
    # -------------------------------------------------------------------------
    # The simulation includes the following steps:
    #
    # 1. Initialize simulation parameters and variables.
    # 2. While the window is open and simulation is running:
    #    a. Update parameters based on user input via the GUI.
    #    b. Simulate the orbital motion of the two spheres.
    #    c. Apply perturbations, which represent two gravitational wells,
    #       based on the sphere positions.
    #    d. Compute surface properties and boundary damping of the grid.
    #    e. Render the spheres and grid surface.
    #    f. Adjust camera viewpoint and lighting for visualization using the
    #       GUI sliders and/or the mouse. The mouse zoom is altered using 
    #       the right mouse button with mouse drag.
    #    g. Display the "scene" in the Taichi rendering window.
    #    h. Repeat steps a-g until simulation is paused or window is closed.
    # 3. If spheres have merged:
    #    a. Render the merged sphere with adjusted properties.
    # 4. Set grid colors and triangle vertices for rendering.
    # 5. Render the grid surface using triangles.
    # 6. Update camera position and orientation for the next frame, if these
    #       are changed by the user in the GUI during the run.
    # 7. Show the rendered scene in the window.
    # 8. Repeat steps 2-7 until simulation is stopped or the rendering window
    #    is closed.
    # -------------------------------------------------------------------------
    ti.init(arch=ti.cuda,
            kernel_profiler=True)  # Force Taichi to use GPU (if available)
    show_system_information()
    
    # -------------------------------------------------------------------------
    # Global Constants and Configuration Variables
    # -------------------------------------------------------------------------
    # Reset this value for each new run start.
    slider_outer_orbital_radius.set(grid_size // 3)

    (outer_orbital_radius,  # second radius will be computed from this,
                            # using the two relative masses.
     spheres_to_display,
     inner_sphere_mass,
     outer_sphere_mass,
     vertical_scale,
     smoothing_window_size,
     horiz_angle_deg,
     vert_angle_deg,
     camera_zoom,
     grid_chequer_size) = import_parameters_from_gui()

    initial_outer_orbital_radius = outer_orbital_radius
    # -------------------------------------------------------------------------
    # Initialisations of those variables that aren't set in the GUI
    # -------------------------------------------------------------------------
    vector_parameters = {
        "n": 3,
        "dtype": ti.f64,
        "shape": ()
    }
    outer_orbital_coords = ti.Vector.field(**vector_parameters)
    inner_orbital_coords = ti.Vector.field(**vector_parameters)

    # -------------------------------------------------------------------------
    # Grey out fields that cannot be updated by the user during the run
    # -------------------------------------------------------------------------
    greyed_out_slider = {
        "state": "disabled",
        "fg": "grey",
        "bg": "lightgrey",
        "troughcolor": "grey"
    }
    greyed_out_run_option_dropdown = {
        "state": "disabled",
        "fg": "grey",
        "bg": "lightgrey"
        # no troughcolor possible for dropdown widgets
    }
    # If the user hasn't selected an option, set a default value.
    if run_option.get() == "Select a Run Option":
        run_option.set("Set outer sphere orbital radius")   # For displaying 
    run_option_value = run_option.get()                     # For processing

    # In any case, grey out the dropdown options now, to show, and ensure,
    # that the selection cannot be changed during the run.
    run_option_dropdown.config(**greyed_out_run_option_dropdown)
    # -------------------------------------------------------------------------
    # Grid parameters
    # -------------------------------------------------------------------------
    grid_centre = ti.Vector.field(3, dtype=ti.f64, shape=())
    grid_centre[None] = ti.Vector([
        grid_size // 2,
        0.0,
        grid_size // 2
    ])
    number_of_damped_borders = 4
    depth_zeroised_grid_edges = grid_size // 100
    damped_grid_boundary_depth = grid_size // 20
    effective_grid_size = grid_size - 2 * depth_zeroised_grid_edges
    effective_grid_start = (grid_size - effective_grid_size)//2
    effective_grid_end = effective_grid_start + effective_grid_size
    array_arguments = {
        "n": 3,
        "dtype": ti.f64,
        "shape": (grid_size, grid_size)
    }
    grid_surface = ti.Vector.field(**array_arguments)
    initialize_array_of_vectors(
        grid_surface,
        grid_size
    )
    grid_for_rendering = ti.Vector.field(**array_arguments)
    initialize_array_of_vectors(
        grid_for_rendering,
        grid_size
    )
    if run_option_value in [
            "Test 1 - two of four borders damped",
            "Test 2 - all four borders damped"
        ]:
        color_name = "dodgerblue"  # Test surface is blue, reminiscent of
                                   # a liquid surface such as water.
        slider_outer_orbital_radius.config(**greyed_out_slider)
        tkinter_spheres_to_display.set(0)
        slider_spheres_to_display.config(**greyed_out_slider)
    else:
        color_name = "orange"  # Sheet surface is orange for normal runs,
                               # reminiscent of some physical models.

    # -------------------------------------------------------------------------
    # Sphere calculations and perturbation calculations
    # -------------------------------------------------------------------------
    # Set perturbation radial extension to be proportional to sphere mass.
    # The factor used here is arbitrary and is not based on the physics.
    inner_perturb_radius = int(inner_sphere_mass) * 2
    outer_perturb_radius = int(outer_sphere_mass) * 2

    # Arbitrarily define the sphere merged state as when the distance is less
    # than half the sum of the radii of perturbations.
    merging_distance = (outer_perturb_radius + inner_perturb_radius)/2

    # Allow sufficient space between perturbation extents and grid edge
    # so that everything is captured on the visible grid domain. This is also
    # designed to work for the spacing of the two test run perturbations which
    # remain at a fixed location.
    # Reset orbital radius on each restarted run.
    outer_orbital_radius = grid_size // 3
    max_initial_orbital_radius = (grid_size/2
                                  - depth_zeroised_grid_edges
                                  - damped_grid_boundary_depth
                                  - inner_perturb_radius)
    if outer_orbital_radius > max_initial_orbital_radius:
        outer_orbital_radius = max_initial_orbital_radius  # Keep within grid
        # extent.
        tkinter_outer_orbital_radius.set(outer_orbital_radius)

    previous_polar_angle = 0.0
    current_polar_angle = 0.0

    # If masses of spheres differ from one another, set inner sphere radius
    # to be the one of the more massive sphere.
    if inner_sphere_mass < outer_sphere_mass:
        inner_sphere_mass, outer_sphere_mass = (
            outer_sphere_mass, inner_sphere_mass
            )
    inner_sphere_radius = pow(inner_sphere_mass, 1/3)
    outer_sphere_radius = pow(outer_sphere_mass, 1/3)
    slider_inner_sphere_mass.config(**greyed_out_slider)
    slider_outer_sphere_mass.config(**greyed_out_slider)
    sphere_mass_ratio = outer_sphere_mass/inner_sphere_mass
    inner_orbital_radius = outer_orbital_radius * sphere_mass_ratio

    # Sphere perturbation calculations 
    outer_perturb_array = ti.field(
        dtype=ti.f64,
        shape=(outer_perturb_radius * 2 + 1,
               outer_perturb_radius * 2 + 1)
    )
    inner_perturb_array = ti.field(
        dtype=ti.f64,
        shape=(inner_perturb_radius * 2 + 1,
               inner_perturb_radius * 2 + 1)
    )
    outer_perturb_depth = outer_sphere_mass
    inner_perturb_depth = inner_sphere_mass
    create_gaussian_perturb_array(
        outer_perturb_radius,
        outer_perturb_depth,
        outer_perturb_array
    )
    create_gaussian_perturb_array(
        inner_perturb_radius,
        inner_perturb_depth,
        inner_perturb_array
    )

    # Merging parameters 
    merged_sphere_radius = pow(inner_sphere_mass + outer_sphere_mass, 1/3)
    merged_perturb_radius = int(merged_sphere_radius * 5)   # arbitrary
                                                            # augmentation.
    merged_perturb_array = ti.field(
        dtype=ti.f64,
        shape=(merged_perturb_radius * 2 + 1,
               merged_perturb_radius * 2 + 1)
    )
    merged_perturb_depth = inner_sphere_mass + outer_sphere_mass
    create_gaussian_perturb_array(
        merged_perturb_radius,
        merged_perturb_depth,
        merged_perturb_array
    )
    # -------------------------------------------------------------------------
    # Sheet surface computations
    # -------------------------------------------------------------------------
    adjacent_grid_elements = ti.field(dtype=ti.i32, shape=(4, 2))
    offsets = [[1, 0],
               [0, 1],
               [-1, 0],
               [0, -1]]
    for i in range(4):
        for j in range(2):
            adjacent_grid_elements[i, j] = offsets[i][j]
    oscillator_positions = ti.Vector.field(**array_arguments)
    initialize_array_of_vectors(oscillator_positions,
                                grid_size)
    height_rescaled_positions = ti.Vector.field(**array_arguments)
    initialize_array_of_vectors(height_rescaled_positions,
                                grid_size)
    effective_array_arguments = {
        "n": 3,
        "dtype": ti.f64,
        "shape": (effective_grid_size, effective_grid_size)
    }
    oscillator_velocities = ti.Vector.field(**effective_array_arguments)
    oscillator_accelerations = ti.Vector.field(**effective_array_arguments)
    
    # Smoothing
    smoothed_cell_position = ti.Vector.field(2, dtype=ti.i32, shape=())
    smoothing_start_pos = effective_grid_start + depth_zeroised_grid_edges
    smoothing_end_pos = effective_grid_end - depth_zeroised_grid_edges
    smoothed_oscillator_positions = ti.Vector.field(**array_arguments)
    initialize_array_of_vectors(
        smoothed_oscillator_positions,
        grid_size
    )
    
    # -------------------------------------------------------------------------
    # Model sheet parameters
    # -------------------------------------------------------------------------
    initial_elastic_extension = 100
    elastic_constant = 1e7
    timestep = 1e-5
    boundary_damping_factor = 0.06
    polar_angle_increment = 2.0
    oscillator_mass = 1.0
    model_omega = 0.0
    
    # -------------------------------------------------------------------------
    # Astrophysical parameters
    # -------------------------------------------------------------------------
    astro_omega = 0.0
    binary_energy_loss_rate = 0.0
    astro_orbital_separation = 0.0
    astro_outer_sphere_orbital_speed = 0.0
    astro_orbital_decay_rate = 0.0

    newtons_const = 6.67430e-11   # Newton's constant
    newtons_const_cubed = newtons_const * newtons_const * newtons_const
    newtons_const_to_fourth_power = newtons_const ** 4
    lightspeed = 3.0e8   # Speed of light in vacuum
    lightspeed_to_fifth_power = lightspeed ** 5
    m_sun = 1.989e30
    m_sun_squared = m_sun * m_sun
    m_sun_cubed = m_sun * m_sun * m_sun

    # The orbital decay factor is defined to have a positive value.
    orbital_decay_factor = (
        64/5 * newtons_const_cubed * m_sun_cubed
        / lightspeed_to_fifth_power
    )
    summed_masses = inner_sphere_mass + outer_sphere_mass
    astro_summed_masses = (inner_sphere_mass + outer_sphere_mass) * m_sun
    binary_energy_loss_rate_factor = 32/5 * newtons_const_to_fourth_power
    binary_energy_loss_rate_factor *= (
        m_sun_squared
        * (outer_sphere_mass * inner_sphere_mass) ** 2
        / (outer_sphere_mass + inner_sphere_mass) ** 2
    )
    binary_energy_loss_rate_factor /= lightspeed_to_fifth_power

    # -------------------------------------------------------------------------
    # Rendering vars 
    # -------------------------------------------------------------------------
    rendered_outer_orbital_coords = ti.Vector.field(3,
                                                    dtype=ti.f64,
                                                    shape=(1,))
    rendered_inner_orbital_coords = ti.Vector.field(3,
                                                    dtype=ti.f64,
                                                    shape=(1,))
    grid_rescale_for_rendering = 1 / grid_size
    rendered_outer_sphere_radius = (
        outer_sphere_radius
        * grid_rescale_for_rendering
    )
    rendered_inner_sphere_radius = (
        inner_sphere_radius
        * grid_rescale_for_rendering
    )
    # -------------------------------------------------------------------------
    # Colour the surface 
    # -------------------------------------------------------------------------
    rgb_color = [0, 0, 0]
    complementary_rgb_color = [0, 0, 0]
    rgb_color, complementary_rgb_color = color_longname_to_RGB(
        color_name,
        rgb_color,
        complementary_rgb_color
    )
    rgb_color = tuple(rgb_color)
    complementary_rgb_color = tuple(complementary_rgb_color)
    grid_colors = ti.Vector.field(
        n=3,
        dtype=ti.f64,
        shape=(grid_size * grid_size)
    )
    
    # -------------------------------------------------------------------------
    # Set up mesh data 
    # -------------------------------------------------------------------------
    num_triangles = (grid_size - 1) * (grid_size - 1) * 2
    indices = ti.field(int, num_triangles * 3)
    set_indices(grid_size,
                indices)
    vertices = ti.Vector.field(
        n=3,
        dtype=ti.f64,
        shape=(grid_size * grid_size)
    )
    rendering_window = ti.ui.Window(
        name="Surface",
        res=(int(screen_width * 0.8), screen_height),
        pos=(int(screen_width * 0.2), 0),
        show_window=True,
        vsync=True
    )
    canvas = rendering_window.get_canvas()
    
    scene = rendering_window.get_scene()
    simulation_frame_counter = 0
    start_time = time.time()
    loop_duration = 0.0
    fps = 0.0

    info_window, labels = start_info_window(root, shared_data)
    root.after(
        0, 
        update_info_window, 
        run_option_value, 
        shared_data, 
        info_window, 
        labels)
    
    merged_binary_system = False
    merge_only_once = True
    place_perturbation_only_once = True
    prev_mouse_pos = None  # To store the last mouse position
    prev_zoom_mouse_pos = None
    # Globals for camera state
    LMB_already_active = False
    RMB_already_active = False
    view_distance = 0.5  # Distance from the center of the surface
    camera_position_x = 0.0
    camera_position_y = 0.0
    horiz_angle_deg = 0.0    # Horizontal angle adjustable by the mouse
    vert_angle_deg = 0.0     # Vertical angle
    
    # -------------------------------------------------------------------------
    # This is the main loop 
    # -------------------------------------------------------------------------
    while (shared_data['running']):
        simulation_frame_counter += 1
        prev_time_stamp = time.time()
        previous_polar_angle = current_polar_angle

        # Get the user-adjustable parameters from the GUI. --------------------
        (outer_orbital_radius,  # second radius will be computed from this,
                                # using the two relative masses.
         spheres_to_display,
         inner_sphere_mass,
         outer_sphere_mass,
         vertical_scale,
         smoothing_window_size,
         horiz_angle_deg,
         vert_angle_deg,
         camera_zoom,
         grid_chequer_size) = import_parameters_from_gui()

        # If the simulation is paused, reset all dynamic properties.
        if simulation_paused.is_set():
            astro_outer_sphere_orbital_speed = 0.0
            astro_omega = 0.0
            model_omega = 0.0
            binary_energy_loss_rate = 0.0
            astro_orbital_decay_rate = 0.0
            fps = 0.0
            
        if not simulation_paused.is_set():   
            # Check to ensure that current run is not a test.  
            if run_option_value in [
            "Set outer sphere orbital radius",
            "Inspiralling"
            ]:
                if not merged_binary_system:        
                    current_polar_angle = increment_polar_angle(
                        initial_outer_orbital_radius,
                        outer_orbital_radius,
                        previous_polar_angle,
                        polar_angle_increment
                    )
                    calculate_orbital_coords(
                        grid_centre,
                        outer_orbital_radius,
                        current_polar_angle,
                        outer_orbital_coords
                    )
                    tkinter_outer_orbital_radius.set(outer_orbital_radius)
                    inner_orbital_radius = (outer_orbital_radius 
                                            * sphere_mass_ratio)
                    calculate_orbital_coords(
                        grid_centre,
                        inner_orbital_radius,
                        current_polar_angle + 180,
                        inner_orbital_coords
                    )
                    # Determine whether to merge the binary system.
                    model_orbital_separation = compute_distance_between_points(
                        outer_orbital_coords,
                        inner_orbital_coords
                    )
                    if model_orbital_separation <= merging_distance:   
                        merged_binary_system = True 
                        if merge_only_once: # merged_binary_system       
                            merge_only_once = False
                            # Merge binary system.        
                            # Reset the relevant model & astrophysical
                            # parameters to zero, ensuring that the 
                            # information window displays values of zero.
                            model_omega = 0.0
                            astro_omega = 0.0
                            binary_energy_loss_rate = 0.0
                            astro_orbital_separation = 0.0
                            model_orbital_separation = 0.0
                            astro_orbital_separation = 0.0
                            astro_outer_sphere_orbital_speed = 0.0
                            astro_orbital_decay_rate = 0.0
                            
                            spheres_to_display = 1
                            tkinter_spheres_to_display.set(1)
                            slider_spheres_to_display.config(
                                **greyed_out_slider
                            )
                            # This is now our merged sphere. 
                            # Arbitrary value for size.
                            outer_sphere_radius *= 2  
            
                            slider_outer_orbital_radius.config(**greyed_out_slider)
                            rendered_outer_sphere_radius = (
                                outer_sphere_radius * grid_rescale_for_rendering
                            )
                            overlay_perturb_shape_onto_grid(
                                merged_perturb_radius,
                                merged_perturb_array,
                                grid_centre,
                                oscillator_positions,
                                oscillator_velocities
                            )
                    else:
                        # Still not merged.
                        overlay_perturb_shape_onto_grid(
                            outer_perturb_radius,
                            outer_perturb_array,
                            outer_orbital_coords,
                            oscillator_positions,
                            oscillator_velocities
                        )
                        overlay_perturb_shape_onto_grid(
                            inner_perturb_radius,
                            inner_perturb_array,
                            inner_orbital_coords,
                            oscillator_positions,
                            oscillator_velocities
                        )
                        # Avoid the zerodivide condition for angular velocity 
                        # if the loop timing is zero.
                        if loop_duration != 0.0:
                            model_omega = calculate_model_omega(
                                previous_polar_angle,
                                current_polar_angle,
                                loop_duration
                            )
                        # Calculate display value of astrophysical 
                        # angular speed.
                        astro_orbital_separation = model_to_astro_scale(
                            model_orbital_separation,
                            astro_length_scaling
                        )
                        astro_omega = calculate_astro_omega(
                            astro_orbital_separation,
                            newtons_const,
                            astro_summed_masses
                        )
                        # Calculate display value of astrophysical 
                        # orbital speed.
                        astro_outer_orbital_radius = model_to_astro_scale(
                            outer_orbital_radius,
                            astro_length_scaling
                        )
                        astro_outer_sphere_orbital_speed = (
                            astro_omega
                            * astro_outer_orbital_radius
                        )
                        # Display the gravitational wave energy loss at the 
                        # current orbit even if the type of run is 
                        # non-inspiralling.
                        binary_energy_loss_rate = compute_binary_energy_loss(
                            binary_energy_loss_rate_factor,
                            astro_orbital_separation,
                            astro_omega
                        )
                        # Update orbits for inspiralling runs.
                        if run_option_value == "Inspiralling":
                            astro_orbital_decay_rate = astro_orbit_decay(
                                astro_orbital_separation,
                                outer_sphere_mass,
                                inner_sphere_mass,
                                orbital_decay_factor
                            )
                            model_orbital_decay = (
                                astro_orbital_decay_rate / astro_length_scaling
                                * model_omega / astro_omega
                            )
                            # If the orbital shrinkage exceeds the distance 
                            # between the binary  components, treat the system as
                            # now merged.
                            if model_orbital_decay >= (
                                    model_orbital_separation
                                    - merging_distance
                                ):
                                merged_binary_system = True
                            else:    
                                inner_orbital_radius -= (model_orbital_decay
                                                         * outer_sphere_mass 
                                                         / summed_masses)
                                outer_orbital_radius -= (model_orbital_decay
                                                         * inner_sphere_mass 
                                                         / summed_masses)
                                # Update this variable in the GUI.
                                tkinter_outer_orbital_radius.set(
                                    outer_orbital_radius
                                )
            else: # A test run
                if place_perturbation_only_once:
                    spheres_to_display = 0
                    tkinter_spheres_to_display.set(0)
                    slider_spheres_to_display.config(**greyed_out_slider)
                    outer_orbital_coords[None] = ti.Vector([
                    grid_centre[None][0] + outer_orbital_radius,
                    0.0,
                    grid_centre[None][2] # keep this axis zero, as the two test run 
                                         # perturbation positions have only the 
                                         # x-coord as non-zero value.
                    ])
                    inner_orbital_coords[None] = ti.Vector([
                        grid_centre[None][0] - outer_orbital_radius,
                        0.0,
                        grid_centre[None][2]
                    ])
                    place_perturbation_only_once
                    overlay_perturb_shape_onto_grid(
                        outer_perturb_radius,
                        outer_perturb_array,
                        outer_orbital_coords,
                        oscillator_positions,
                        oscillator_velocities
                    )
                    overlay_perturb_shape_onto_grid(
                        inner_perturb_radius,
                        inner_perturb_array,
                        inner_orbital_coords,
                        oscillator_positions,
                        oscillator_velocities
                    )
                    if run_option_value == "Test 1 - two of four borders damped":
                        number_of_damped_borders = 2
                    place_perturbation_only_once = False    
            # The damping of the grid boundary is done for both the simulation
            # proper, and test, cases.
            damp_grid_boundary(
                number_of_damped_borders,
                effective_grid_start,
                effective_grid_end,
                damped_grid_boundary_depth,
                boundary_damping_factor,
                oscillator_velocities,
                oscillator_positions
            )
            # -----------------------------------------------------------------
            # Determine the new oscillator positions using the Runge-Kutta 
            # 4th order numerical integration. This function is the core 
            # of the simulation.
            # -----------------------------------------------------------------
            update_oscillator_positions_velocities_RK4(
                effective_grid_start,
                effective_grid_end,
                elastic_constant,
                initial_elastic_extension,
                oscillator_mass,
                adjacent_grid_elements,
                oscillator_positions,
                oscillator_velocities,
                oscillator_accelerations,
                timestep
            )

        rescale_oscillator_heights(
            grid_size,
            vertical_scale,
            oscillator_positions,
            height_rescaled_positions
        )
        if smoothing_window_size > 2:
            smooth_the_surface(
                grid_size,
                smoothing_start_pos,
                smoothing_end_pos,
                smoothing_window_size,
                smoothed_cell_position,
                height_rescaled_positions,
                smoothed_oscillator_positions
            )
            rescale_grid_for_rendering(
                grid_size,
                grid_rescale_for_rendering,
                smoothed_oscillator_positions,
                grid_for_rendering
            )
        else:
            rescale_grid_for_rendering(
                grid_size,
                grid_rescale_for_rendering,
                height_rescaled_positions,
                grid_for_rendering
            )
        set_grid_colors(
            grid_size,
            grid_chequer_size,
            rgb_color,
            complementary_rgb_color,
            grid_colors
        )
        set_triangle_vertices(
            grid_size,
            grid_for_rendering,
            vertices
        )
        scene.mesh(
            vertices,
            indices=indices,
            per_vertex_color=(grid_colors),
            two_sided=True
        )
        
        # ---------------------------------------------------------------------
        # Render the spheres only for the non test run cases. For the test
        # runs, the number of spheres to display has been set to zero.
        # ---------------------------------------------------------------------
        if (spheres_to_display == 1 or
            spheres_to_display == 2):  # Render first sphere
            normalize_coords_for_rendering(
                grid_rescale_for_rendering,
                outer_orbital_coords,
                rendered_outer_orbital_coords
            )
            scene.particles(
                rendered_outer_orbital_coords,
                rendered_outer_sphere_radius,
                color=(0.9, 0.9, 0.9)
            )
        if spheres_to_display == 2:  # Render second sphere
            normalize_coords_for_rendering(
                grid_rescale_for_rendering,
                inner_orbital_coords,
                rendered_inner_orbital_coords
            )
            scene.particles(
                rendered_inner_orbital_coords,
                rendered_inner_sphere_radius,
                color=(0.7, 0.9, 50)
            )

        # Start the rendering 
        canvas.scene(scene)
        scene.ambient_light(color=(0.5, 0.5, 0.5))  # Ambient light
        scene.point_light(pos=(2, 4, 4), color=(1.0, 1.0, 1.0))
        rendering_window.show()
        camera = ti.ui.make_camera()
        scene.set_camera(camera)
        
        if rendering_window.is_pressed(ti.ui.LMB):
            (vert_angle_deg, 
             horiz_angle_deg, 
             prev_mouse_pos, 
             LMB_already_active) = (
                 update_camera_view_from_mouse(
                     rendering_window,
                     vert_angle_deg,
                     horiz_angle_deg,
                     prev_mouse_pos,
                     LMB_already_active,
                     slider_vert_angle_deg,
                     slider_horiz_angle_deg
                 )
             )
        else:
            LMB_already_active = False
            prev_mouse_pos = None
        
        if rendering_window.is_pressed(ti.ui.RMB):
            (camera_zoom, 
             prev_zoom_mouse_pos, 
             RMB_already_active) = (
                 update_zoom_from_mouse(
                     rendering_window,
                     camera_zoom,
                     prev_zoom_mouse_pos,
                     RMB_already_active,
                     slider_camera_zoom,
                 )
             )
        else:
            RMB_already_active = False
            prev_zoom_mouse_pos = None
            
        view_distance = 2.0
        view_distance /= camera_zoom
  
        # Adjust vertical angle for seamless behavior past 90 degrees
        if vert_angle_deg > 89.99:
            vert_angle_deg = 89.99  
            
        vert_angle_rad = math.radians(vert_angle_deg)
        horiz_angle_rad = math.radians(horiz_angle_deg)
        
        look_at_x = 0.5
        look_at_y = 0.0
        look_at_z = 0.5
        # Compute camera positions
        camera_position_x = (look_at_x 
                             + view_distance * math.cos(vert_angle_rad) 
                               * math.cos(horiz_angle_rad))
        camera_position_y = (look_at_z 
                             + view_distance * math.cos(vert_angle_rad) 
                               * math.sin(horiz_angle_rad))
        camera_height = (look_at_y 
                         + view_distance * math.sin(vert_angle_rad))

        # Set (point of) view using camera parameters -------------------------
        camera.position(
            camera_position_x,
            camera_height,
            camera_position_y
        )
        camera.lookat(look_at_x,
                      look_at_y,
                      look_at_z)

        scene.set_camera(camera)
        energy_of_sheet = 0.0
        energy_of_sheet = total_energy_of_sheet(
            grid_size,
            elastic_constant,
            oscillator_positions,
            oscillator_mass,
            oscillator_velocities
        )
        # Housekeeping of loop data -------------------------------------------
        loop_duration = time.time() - prev_time_stamp
        fps = 1/loop_duration
        
        if run_option_value in [
                "Test 1 - two of four borders damped",
                "Test 2 - all four borders damped"
            ]:
            print("Test, total surface energy of sheet")
            print("===================================")
            print("simulation_frame_counter", simulation_frame_counter)
            print("energy_of_sheet", energy_of_sheet)

        if simulation_frame_counter == 1:
            start_time = time.time()
        elapsed_time = time.time() - start_time  # This is our clock time. Runs
                                                 # even when loop is paused.
        with shared_data['lock']:
            shared_data['elapsed_time'] = elapsed_time
            shared_data['fps'] = fps
            shared_data['astro_orbital_separation'] = astro_orbital_separation
            shared_data[
                'astro_outer_sphere_orbital_speed'
            ] = astro_outer_sphere_orbital_speed
            shared_data['astro_omega'] = astro_omega
            shared_data['model_omega'] = model_omega
            shared_data['binary_energy_loss_rate'] = binary_energy_loss_rate
            shared_data['astro_orbital_decay_rate'] = astro_orbital_decay_rate

    # -------------------------------------------------------------------------
    # Drop out of the main loop.
    # -------------------------------------------------------------------------
    reactivate_slider = {
        "state": "normal",
        "fg": "black",
        "bg": "light steel blue",
        "troughcolor": "steel blue"
    }
    reactivate_dropdown = {
        "state": "normal",
        "fg": "black",
        "bg": "light steel blue",
    }
    slider_inner_sphere_mass.config(**reactivate_slider)
    slider_outer_sphere_mass.config(**reactivate_slider)
    slider_outer_orbital_radius.config(**reactivate_slider)
    slider_spheres_to_display.config(**reactivate_slider)
    slider_spheres_to_display.set(2)  # check this error
    run_option_dropdown.config(**reactivate_dropdown)

    # Initialize the dictionary to hold shared data for the simulation.
    # This includes flags, thread references, and various parameters related
    # to the simulation's state and physics calculations.
    with shared_data['lock']:
        shared_data = {
            'elapsed_time': 0.0,
            'fps': 0.0,
            'astro_orbital_separation': 0.0,
            'astro_outer_sphere_orbital_speed': 0.0,
            'astro_omega': 0.0,
            'model_omega': 0.0,
            'binary_energy_loss_rate': 0.0,
            'astro_orbital_decay_rate': 0.0
        }
        
    if run_option_value in [
            "Test 1 - two of four borders damped",
            "Test 2 - all four borders damped"
        ]:    
        # Provide print output showing relative percentages of CPU time
        # for each Taichi module (kernel).
        ti.sync()
        ti.profiler.print_kernel_profiler_info()
        
root.mainloop()
# END OF CODE -----------------------------------------------------------------