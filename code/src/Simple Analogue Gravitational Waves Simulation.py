# =============================================================================
# Import Libraries
# =============================================================================
# The following imports are necessary for the program to function.
# Standard Python libraries and third-party packages are loaded here.
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
    exit,
    getwindowsversion,
    version  # Specify Python version
)

# Import threading components because the GUI cannot run in the same process
# as the main loop.
from threading import Thread, Event, Lock

# ----------------------------
# Third-party library imports
# ----------------------------
from pyautogui import size  # Used for obtaining screen resolution

# Import the "psutil" (process and system utilities) library, here for 
# obtaining CPU information.
from psutil import cpu_count, cpu_freq, cpu_percent

from matplotlib import colors as mcolors  # Used for converting string to RGB

import taichi as ti  # Use for enhancing rendering performance
ti.init(arch=ti.cpu,
        default_fp=ti.f64,
        kernel_profiler=True)

# =============================================================================
# Construct the Tkinter GUI containing the sliders and buttons
# through which the user input controls the application.
# =============================================================================
# Import essential components from the tkinter library for creating the GUI.
# These include widgets for
# - the layout (Frame, Label),
# - user interaction (Button, Slider), and
# - variable management (DoubleVar, IntVar, StringVar).

root = Tk()  # Create the main application GUI window

root.config(bg="black")
root.attributes('-topmost', 1)  # Set GUI window to be on top of all others
root.resizable(False, False)    # and to be non-resizable and non-draggable.

# Make this window frameless (no title bar, no borders) as not required.
root.overrideredirect(True)

# Set the GUI screen width and height.
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
GUI_width = int(screen_width/5)
GUI_height = int(screen_height)
root.geometry(f"{GUI_width}x{GUI_height}+0+0")

# Initialize variables to bind GUI elements for program control. These 
# represent user-adjustable parameters in the GUI.
tkinter_first_orbital_radius  = DoubleVar()
tkinter_number_of_spheres     = IntVar()
tkinter_first_sphere_mass     = IntVar()
tkinter_second_sphere_mass    = IntVar()
tkinter_vertical_scale        = IntVar()
tkinter_smoothing_window_size = IntVar()
tkinter_horiz_angle_deg       = DoubleVar()
tkinter_vert_angle_deg        = DoubleVar()
tkinter_camera_zoom           = DoubleVar()
tkinter_grid_chequer_size     = IntVar()
# -----------------------------------------------------------------------------
# The parameter grid_size represents the length of one side of a square 2D 
# array. Its value is needed at this point in the code due to several
# dependencies.
# Since, for symmetry purposes, a single cell represents the centre of the 
# grid, the grid side lengths need to be incremented by one so that they are
# odd-numbered. The grid size can be increased for running on high end 
# spec machines.
# -----------------------------------------------------------------------------
grid_size = 300 + 1

# Scale grid element size (default 1 unit = 1 pixel) to a real 
# astronomical distance (in metres) by a realistic factor.
astro_length_scaling = 1e3
formatted_astro_length_scaling = format(astro_length_scaling, ".0e")

# -----------------------------------------------------------------------------
# Define the GUI user input widgets, which allow user control of the run.
# -----------------------------------------------------------------------------
# Define a reusable generic structure for horizontal slider configuration.
horizontal_slider_arguments = {
    "bg": "light steel blue",
    "troughcolor": "steel blue",
    "orient": "horizontal"
}

# Set padding for widget placement (horizontal and vertical) to 2 pixels.
padx, pady = 2, 2

# Define two generic packing options for the widgets.
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

# Create a frame to hold the widgets for the parameters related to the spheres.
frame = Frame(root, bg="black")
frame.pack(**pack_top)

# Create a slider widget to control the radius of the first sphere's orbit.
# If the masses of the spheres differ, this orbit is always set to be the 
# larger of the two. The slider values are therefore swapped before the run,
# if necessary.
slider_first_orbital_radius = Scale(
    frame,
    label=(
        "First Sphere Orbital Radius (m x "
        + formatted_astro_length_scaling
        + ")"
    ),
    variable=tkinter_first_orbital_radius,
    from_=0,
    to=grid_size / 3,
    tickinterval=(grid_size / 2 - 10) / 4,
    **horizontal_slider_arguments
)    
slider_first_orbital_radius.pack(
    side=TOP,
    padx=padx * 2,
    pady=(pady * 2, pady),
    fill=BOTH
)

frame = Frame(root, bg="black")
frame.pack(**pack_top)

slider_number_of_spheres = Scale(
    frame,
    label="# Spheres",
    variable=tkinter_number_of_spheres,
    from_=0, to=2,
    tickinterval=1,
    **horizontal_slider_arguments
)
slider_number_of_spheres.pack(**pack_left)

slider_first_sphere_mass = Scale(
    frame,
    label="Mass 1 [M⊙]",
    variable=tkinter_first_sphere_mass,
    from_=0, to=20,
    tickinterval=20,
    **horizontal_slider_arguments
)
slider_first_sphere_mass.pack(**pack_left)

slider_second_sphere_mass = Scale(
    frame,
    label="Mass 2 [M⊙]",
    variable=tkinter_second_sphere_mass,
    from_=0, to=20,
    tickinterval=20,
    **horizontal_slider_arguments
)
slider_second_sphere_mass.pack(**pack_left)

# Define a generic structure for configuratio of vertical sliders.
vertical_slider_arguments = {
    "bg": "light steel blue",
    "troughcolor": "steel blue",
    "orient": "vertical",
    "length": GUI_height / 5
}

# Create a frame for vertical scaling and smoothing. Adjusting the slider
# within this frame allows the user to set the sheet perturbations (waves)
# to different heights, offering better visibility, if needed.
frame = Frame(root, bg="black")
frame.pack(**pack_top)

# Add a vertical scale slider within this frame.
slider_vertical_scale = Scale(
    frame,
    label="Vertical Scale",
    variable=tkinter_vertical_scale,
    from_=20,
    to=0,
    **vertical_slider_arguments
)
slider_vertical_scale.pack(**pack_left)

# Create a vertical slider within the frame to control the smoothing window
# size, which adjusts the level of smoothing applied to the grid. 
# The smoothing is purely visual and does not form part of the numerical 
# integration, i.e. it does not feed back into the rendering loop computations.
slider_smoothing_window_size = Scale(
    frame,
    label="Smoothing",
    variable=tkinter_smoothing_window_size,
    from_=25, to=0,
    resolution=2,
    **vertical_slider_arguments
)
slider_smoothing_window_size.pack(**pack_left)

# Create and configure sliders for controlling the camera's movement and
# viewpoint. These sliders allow the user to adjust the camera's position
# and orientation in 3D space, providing control over vertical and
# horizontal look direction, and zooming.
frame = Frame(root, bg="black")
frame.pack(**pack_top)

# Camera left/right movement control slider (azimuth, or yaw)
slider_horiz_angle_deg = Scale(
    frame,
    label="View L/R (degrees)",
    variable=tkinter_horiz_angle_deg,
    from_=-180.0, to=+180.0, resolution=0.01,
    tickinterval=60,
    **horizontal_slider_arguments
)
slider_horiz_angle_deg.pack(**pack_left)

frame = Frame(root, bg="black")
frame.pack(**pack_top)

# Camera look-up/down control slider (altitude, or pitch)
slider_vert_angle_deg = Scale(
    frame,
    label="View U/D (degrees)",
    variable=tkinter_vert_angle_deg,
    from_=-45.0, to=90.0, resolution=0.01,
    **vertical_slider_arguments
)
slider_vert_angle_deg.pack(**pack_left)   

slider_camera_zoom = Scale(
    frame,
    label="Zoom",
    variable=tkinter_camera_zoom, 
    from_=15.0, to=1.0, resolution=0.1,
    **vertical_slider_arguments
)
slider_camera_zoom.pack(**pack_left)   

# Create a resizeable chequerboard/"table cloth" style color pattern.
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

frame = Frame(root, bg="black")
frame.pack(side=TOP, fill=X, padx=padx, pady=pady)

run_option = StringVar()
run_option.set("Select a Run Option")  # Default prompt for selection

# Create a run option selector (dropdown) for choosing a run option
# from the list.
options_list = ["Set first sphere orbital radius",
                "Inspiralling",
                "Test 1 - two of four borders damped",
                "Test 2 - all four borders damped"]
run_option_dropdown = OptionMenu(frame,
                                 run_option,
                                 *options_list)
run_option_dropdown.config(bg="light steel blue")
run_option_dropdown.pack(**pack_left)
frame = Frame(root, bg="black")
frame.pack(**pack_top)

# -----------------------------------------------------------------------------
# Define the GUI slider widget values, which can be adjusted to alter the 
# type/style of the run (including a "testing mode").
# -----------------------------------------------------------------------------
# Define and initialize a data dictionary to hold shared data. This is used to 
# allow values of the GUI widgets (in the tkinter GUI thread) to be passed 
# to the processing/rendering thread in a thread-safe way.
shared_slider_data = { 
    'lock': Lock(),
    'running': False,
    'first_orbital_radius':  0.0,
    'number_of_spheres':     0,
    'first_sphere_mass':     0,
    'second_sphere_mass':    0,
    'vertical_scale':        0.0,
    'smoothing_window_size': 0.0,
    'horiz_angle_deg':       0.0,
    'vert_angle_deg':        0.0,
    'camera_zoom':           0.0,
    'grid_chequer_size':     0
} 

# -----------------------------------------------------------------------------
def update_gui_sliders_with_defaults():
    slider_first_orbital_radius.set(grid_size / 4)
    slider_number_of_spheres.set(2)
    slider_first_sphere_mass.set(grid_size // 100)
    slider_second_sphere_mass.set(grid_size // 100)
    slider_vertical_scale.set(10.0)
    slider_smoothing_window_size.set(5.0)
    slider_horiz_angle_deg.set(0.0)
    slider_vert_angle_deg.set(45.0)
    slider_camera_zoom.set(2.0)
    slider_grid_chequer_size.set(0.0)

# This function places the GUI current slider values into the previously 
# defined shared data dictionary, ready for use across threads. 
def shared_slider_data_from_gui(shared_slider_data):
    with shared_slider_data['lock']:
        shared_slider_data.update({
            'first_orbital_radius':  slider_first_orbital_radius.get(),
            'number_of_spheres':     slider_number_of_spheres.get(),
            'first_sphere_mass':     slider_first_sphere_mass.get(),
            'second_sphere_mass':    slider_second_sphere_mass.get(),
            'vertical_scale':        slider_vertical_scale.get(),
            'smoothing_window_size': slider_smoothing_window_size.get(),
            'horiz_angle_deg':       slider_horiz_angle_deg.get(),
            'vert_angle_deg':        slider_vert_angle_deg.get(),
            'camera_zoom':           slider_camera_zoom.get(),
            'grid_chequer_size':     slider_grid_chequer_size.get()
        })

with shared_slider_data['lock']:
    first_orbital_radius  = shared_slider_data['first_orbital_radius']
    number_of_spheres     = shared_slider_data['number_of_spheres']
    first_sphere_mass     = shared_slider_data['first_sphere_mass']
    second_sphere_mass    = shared_slider_data['second_sphere_mass']
    vertical_scale        = shared_slider_data['vertical_scale']
    smoothing_window_size = shared_slider_data['smoothing_window_size']
    horiz_angle_deg       = shared_slider_data['horiz_angle_deg']
    vert_angle_deg        = shared_slider_data['vert_angle_deg']
    camera_zoom           = shared_slider_data['camera_zoom']
    grid_chequer_size     = shared_slider_data['grid_chequer_size']
root.after(0, update_gui_sliders_with_defaults)

shared_slider_data_from_gui(shared_slider_data)

greyed_out_slider = {
    "state": "disabled",
    "fg": "grey",
    "bg": "lightgrey",
    "troughcolor": "grey"
}
def set_and_grey_out_two_sliders():
    slider_number_of_spheres.set(2)
    slider_first_orbital_radius.set(0.0)
    slider_number_of_spheres.config(**greyed_out_slider)
    slider_first_orbital_radius.config(**greyed_out_slider)

def set_and_grey_out_number_of_spheres():
    tkinter_number_of_spheres.set(0)
    slider_number_of_spheres.config(**greyed_out_slider)
    
# -----------------------------------------------------------------------------
# Initialize a second, separate, dictionary to hold shared data. This 
# information, generated during each iteration of the main loop, is displayed
# in a separate window at the right of the screen.
# -----------------------------------------------------------------------------
shared_display_data = {
    'lock': Lock(),
    'running': False,
    'simulation_thread': None,
    'elapsed_time': 0.0,
    'fps': 0.0,
    'astro_binary_separation': 0.0,
    'astro_first_sphere_orbital_speed': 0.0,
    'astro_omega': 0.0,
    'model_omega': 0.0,
    'binary_energy_loss': 0.0,
    'astro_orbital_decay': 0.0
}  

def reset_shared_display_data(shared_display_data):
    shared_display_data.update({
        'running': False,
        'simulation_thread': None,
        'elapsed_time': 0.0,
        'fps': 0.0,
        'astro_binary_separation': 0.0,
        'astro_first_sphere_orbital_speed': 0.0,
        'astro_omega': 0.0,
        'model_omega': 0.0,
        'binary_energy_loss': 0.0,
        'astro_orbital_decay': 0.0
    })

# =============================================================================
# Function definitions for startup and main control
# =============================================================================
# -----------------------------------------------------------------------------
# Toggle the running of the simulation: stop/start.
# -----------------------------------------------------------------------------
def start_stop_simulation(shared_display_data):
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
    with shared_display_data['lock']:
        if not shared_display_data['running']:  # Start the simulation.
            button_start_stop_simulation.config(
                text="STOP Simulation",
                bg="orange"
            )
            # Set both running flags to True
            shared_slider_data['running'] = True
            shared_display_data['running'] = True
            shared_display_data['simulation_thread'] = Thread(
                target=mainline_code,
                args=(shared_slider_data, 
                      shared_display_data)  # Pass both shared
                                            # dictionaries to 
                                            # the main function.
            )
            shared_display_data['simulation_thread'].start()
        else:  # Stop the simulation but keep the GUI displayed.
            run_option.set("Select a Run Option")  # Default prompt for 
                                                   # selection
            button_start_stop_simulation.config(
                text="START Simulation",
                bg="light green"
            )
            # Set the running flags of the two data dictionaries to False.
            shared_slider_data['running'] = False
            shared_display_data['running'] = False
            root.after(0, close_info_window)

button_start_stop_simulation = Button(
    frame,
    width=25,
    text="START Simulation",
    command=lambda: start_stop_simulation(shared_display_data),
    bg="light green"
)
button_start_stop_simulation.pack(padx=padx, pady=pady)

# -----------------------------------------------------------------------------
# Respond to user input to pause the run.
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


def start_info_window(
        root, 
        run_option_value, 
        shared_display_data
    ):
    """
    Creates a fixed-position, non-resizable information window at the 
    bottom-right corner of the screen, displaying real-time metrics.

    The 'Toplevel' window is styled with a black background and white text, 
    and remains on top of other windows. It includes labels for items such as 
    elapsed time, FPS, orbital parameters, and energy rates, which are updated 
    dynamically.

    Parameters:
        - root (Tk): Parent application window.
        - shared_display_data (dict): Shared data dictionary for thread-safe 
          access to real-time data, using a lock mechanism.

    Returns:
        - info_window (Toplevel): The created information window.
        - labels (dict): Dictionary of dynamically-updated labels.

    Notes:
        - The window is always on top and has a fixed size and position.
        - Label contents are initially empty and should be updated during the 
          application's main loop.
    """
    info_window = Toplevel(root)
    info_window.attributes('-topmost', 1)
    info_window_width = screen_width // 5
    
    # Query this parameter to set the size of the window appropriately, 
    # according to how many fields/labels are required to be displayed.
    if run_option_value in ["Set first sphere orbital radius", 
                            "Inspiralling"]:
        info_window_height = int(screen_height * 0.21)
    else:
        info_window_height = int(screen_height * 0.05)
     
    info_x_pos = screen_width - info_window_width
    info_y_pos = 0
    info_window.geometry(
        f"{info_window_width}x{info_window_height}+{info_x_pos}+{info_y_pos}")
    info_window.config(bg="black")

    def create_label(window, text="", fg="white", bg="black"):
        label = Label(window, text=text, fg=fg, bg=bg)
        label.pack()
        return label

    # Initialize labels related to display fields
    labels = {  
        "elapsed_time_label":            create_label(info_window),
        "fps_label":                     create_label(info_window),
        "astro_binary_separation_label": create_label(info_window),
        "astro_first_speed_label":       create_label(info_window),
        "astro_omega_label":             create_label(info_window),
        "model_omega_label":             create_label(info_window),
        "binary_energy_loss_label":      create_label(info_window),
        "astro_orbital_decay_label":     create_label(info_window),
    }
    # This must be done after all other specifications for the window:
    # Create a frameless window (no title bar, no borders, as not needed).
    info_window.overrideredirect(True)
    return info_window, labels


def update_info_window(
        run_option_value, 
        shared_display_data, 
        info_window, 
        labels
    ):
    """
    Update the information display in the info window.
    
    This function updates various labels in the info window with real-time
    data from the 'shared_display_data' dictionary. 
    It updates labels based on the simulation's current state.
     
    The function includes handling for elapsed time, frames per second (FPS), 
    and additional simulation parameters.
    
    Parameters:
        - run_option_value (str): A string representing the current run option 
          selected by the user, influencing the type of simulation data 
          displayed.
        - shared_display_data (dict): A dictionary containing the shared data, 
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
          the 'shared_display_data['lock']'.
        - The labels are updated with formatted strings. 
    """
    elapsed_time = shared_display_data['elapsed_time']
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    current_fps = shared_display_data['fps']
    
    with shared_display_data['lock']:
        # Update labels common to all run cases
        labels["elapsed_time_label"].config(
            text = f"Elapsed Time: {int(hours):02}:"
                   f"{int(minutes):02}:{int(seconds):02}"
        )
        labels["fps_label"].config(text=f"FPS: {current_fps:.2f}")
        
        #  Set remaining labels
        if run_option_value in ["Set first sphere orbital radius", 
                                "Inspiralling"]:
            astro_binary_separation = (
                shared_display_data['astro_binary_separation']
            )
            current_first_speed = (
                shared_display_data['astro_first_sphere_orbital_speed']
            )
            current_astro_omega = shared_display_data['astro_omega']
            current_model_omega = shared_display_data['model_omega']
            energy_loss_rate = shared_display_data['binary_energy_loss']
            astro_orbital_decay = shared_display_data['astro_orbital_decay']
            
            labels["astro_binary_separation_label"].config(
                text=f"Astro Binary Separation:"
                     f" {astro_binary_separation:.2e} m"
            )
            labels["astro_first_speed_label"].config(
                text=f"Astro First Sphere Orbital Speed:"
                     f" {current_first_speed:.2e} m/s"
            )
            labels["astro_omega_label"].config(
                text=f"Astro Ω: {current_astro_omega:.2e} rad/s"
            )
            labels["model_omega_label"].config(
                text=f"Model Ω: {current_model_omega:.2e} rad/s"
            )
            labels["binary_energy_loss_label"].config(
                text=f"Astro Binary Energy Loss Rate: {energy_loss_rate:.2e} W"
            )
            labels["astro_orbital_decay_label"].config(
                text=f"Astro Orbital Decay Rate: {astro_orbital_decay:.2e} m/s"
            )
    # Schedule the next update (in milliseconds)
    info_window.after(500,
                      update_info_window, 
                      run_option_value, 
                      shared_display_data, 
                      info_window, 
                      labels)


# Close the information display window at the end of a run.
def close_info_window():
    """
    Close all "Toplevel" windows associated with the main application.

    This function iterates through the application's child windows and 
    destroys any windows at the top of the hierarchy at the end of a run.
    """
    for window in root.winfo_children():
        if isinstance(window, Toplevel):
            window.destroy()


@ti.kernel
def initialize_array_of_vectors(
        array_to_be_initialized: ti.template(),
        array_size: ti.i32
        ):
    """
    Initialize a 2D array of vectors with integer grid coordinates.

    This function iterates over a 'array_size x array_size' array and sets each 
    vector within 'array_to_be_initialized' to contain its grid coordinates 
    and a zero for the second array dimension representing the height.
    Specifically, each vector at position '(i, j)' is initialized as 
    '[i, 0.0, j]'.

    Parameters:
        - array_to_be_initialized (ti.template()): The 2D array of vectors to 
          initialize, with a shape of '(array_size, array_size, 3)'.
        - array_size (int): The size of the grid along each dimension, defining 
          the bounds of 'i' and 'j' (0 to 'array_size - 1').
    """
    for i in range(array_size):
        for j in range(array_size):
            array_to_be_initialized[i, j][0] = i
            array_to_be_initialized[i, j][1] = 0.0
            array_to_be_initialized[i, j][2] = j


@ti.kernel
def compute_polar_angle_increase(
        default_first_orbital_radius: ti.f64,
        first_orbital_radius: ti.f64,
        default_polar_angle_step: ti.f64
    ) -> ti.f64:
    """
    Increment the polar angle for the binary system.

    This function computes the new polar angle based on the previous polar 
    angle, the angular step size, and the ratio of the current and initial 
    first orbital radii. 
    
    The calculation adjusts the effective step size based on the 
    orbital radius, where the step size depends on the inverse of the radius
    raised to the power of 3/2.

    Parameters:
        - default_first_orbital_radius (float): The initial orbital radius 
          used as a reference for scaling the angular step size.
        - first_orbital_radius (float): The current orbital radius, which 
          affects the angular step size.
        - previous_polar_angle (float): The polar angle from the previous 
          iteration, used as the starting point for the new angle.
        - default_polar_angle_step (float): The angular step size 
          per iteration, before adjusting for the orbital radius.

    Returns:
        float: The updated polar angle, wrapped to stay within the range 
        [0, 360) degrees.

    Notes:
        - The polar angle is incremented according to the inverse power law 
          relative to the orbital radius.
        - Its previous value (wrapped using modulo 360 to ensure it falls 
          within 0 - 360 degrees) is then increased by a factor that accounts
          for Keplerian orbital dynamics. The result for the polar angle 
          increment is, however, not wrapped, as the angular velocity 
          calculated from it needs to reflect values over 360 degrees (should
          they occur).
    """
    return (default_polar_angle_step
             * (first_orbital_radius / default_first_orbital_radius) ** -3/2)


@ti.kernel
def calculate_model_omega(
        delta_polar_angle: ti.f64,
        loop_duration: ti.f64
    ) -> ti.f64:
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
          polar angle occurs.

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
    return delta_polar_angle / loop_duration * ti.math.pi / 180


@ti.kernel
def calculate_orbital_coords(
        grid_centre: ti.template(),
        sphere_orbital_radius: ti.f64,
        sphere_polar_angle: ti.f64,
        orbital_coords: ti.template()
    ):
    """
    Calculate the Cartesian coordinates of a sphere, or its perturbation,
    on its orbital path.

    This function computes the (x, y, z) coordinates of a sphere based on 
    its orbital radius and polar angle relative to a grid centre. The polar 
    angle is converted from degrees to radians before being used to compute 
    the offsets in the x and z dimensions, while the y-coordinate is fixed 
    to 0. The result is stored in the 'orbital_coords' template.

    Parameters:
        - grid_centre (ti.template): The 3D coordinates of the grid centre, 
          typically a vector, from which the orbital position is offset.
        - sphere_orbital_radius (ti.f64): The orbital radius of the sphere, 
          determining the distance from the grid centre in the x-z plane.
        - sphere_polar_angle (ti.f64): The polar angle of the sphere's orbit 
          in degrees, used to calculate its position along the orbital path.
        - orbital_coords (ti.template): A template to store the calculated 
          sphere's coordinates (x, 0, z) based on the orbital parameters.

    Returns:
        None: The function does not return a value, but stores the calculated 
        coordinates in the 'orbital_coords' template.

    Notes:
        - The y-coordinate of the sphere is fixed at 0 in this calculation.
        - The polar angle is assumed to be in degrees and is converted to 
          radians before calculating the offsets.
        - The function uses the grid centre's x and z coordinates as the 
          reference point for the sphere's orbital position.

    Example:
        If the grid centre is at (10, 0, 10), the orbital radius is 5, and the 
        polar angle is 30 degrees, the function will compute the sphere's 
        position relative to the grid centre.
    """
    angle_rad = ti.math.radians(sphere_polar_angle)
    x_offset = sphere_orbital_radius * ti.cos(angle_rad)
    y_offset = sphere_orbital_radius * ti.sin(angle_rad)
    orbital_coords[None] = ti.Vector([grid_centre[None][0] + x_offset,
                                      0.0,
                                      grid_centre[None][2] + y_offset])


@ti.kernel
def model_to_astro_scale(
        model_distance: ti.f64,
        astro_length_scaling: ti.f64
    ) -> ti.f64:
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
        astro_binary_separation: ti.f64,
        newtons_const: ti.f64,
        astro_summed_masses: ti.f64
    ) -> ti.f64:
    """
    Calculates the angular velocity (omega) of an astronomical system 
    based on orbital separation and total mass using Newton's law of 
    gravitation.

    Parameters:
        - astro_binary_separation (ti.f64): The distance between the two 
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
        / (astro_binary_separation * astro_binary_separation
           * astro_binary_separation)
    )


@ti.kernel
def compute_binary_energy_loss(
        binary_energy_loss_factor: ti.f64,
        astro_binary_separation: ti.f64,
        astro_omega: ti.f64
    ) -> ti.f64:
    """
    Computes the energy loss rate of a binary astronomical system due to 
    gravitational wave radiation.

    Parameters:
        - binary_energy_loss_factor (ti.f64): A factor that encapsulates 
          the physical constants and parameters relevant to the system's 
          energy loss rate.
        - astro_binary_separation (ti.f64): The separation distance between 
          the two orbiting bodies in astronomical units.
        - astro_omega (ti.f64): The angular velocity (omega) of the system 
          in radians per unit time.

    Returns:
        ti.f64: The energy loss rate of the binary system.
    """
    return (
        binary_energy_loss_factor
        * astro_binary_separation ** 4
        * astro_omega ** 6
    )


@ti.kernel
def calc_astro_orbital_decay(
        astro_binary_separation: ti.f64,
        first_sphere_mass: ti.i32,
        second_sphere_mass: ti.i32,
        orbital_decay_factor: ti.f64
    ) -> ti.f64:
    """
    Calculate the rate of orbital decay for a binary system based on its 
    astronomical parameters, using the appropriate general relativistic
    equation.

    This function computes the decay rate of the orbit using the masses of  
    two real astronomical bodies and their separation distance (upscaled from 
    the model). 
    The decay is due to the energy lost due to gravitational radiation.

    Parameters:
        - astro_binary_separation (ti.f64): The actual separation distance 
          between the two astronomical bodies, given in units of metres.
        - first_sphere_mass (ti.i32): The mass of the first sphere in the 
          astronomical binary system, in units of Solar masses.
        - second_sphere_mass (ti.i32): The mass of the second sphere in the 
          astronomical binary system, in units of Solar masses.
        - orbital_decay_factor (ti.f64): A constant factor applied to scale 
          the orbital decay rate, based on Newton's constant, G, the speed of
          light, c, and the Solar mass.

    Returns:
        ti.f64: The rate of orbital decay for the system, im m/s.
    """
    astro_orbital_decay = (
        orbital_decay_factor 
        * first_sphere_mass 
        * second_sphere_mass
        )
    astro_orbital_decay *= (
        (first_sphere_mass + second_sphere_mass)
        /(astro_binary_separation ** 3)
        )
    return astro_orbital_decay


@ti.kernel
def create_gaussian_perturb_array(
        perturb_radius: ti.i32,
        perturb_max_depth: ti.f64,
        perturb_array: ti.template()
    ):
    """
    Creates a 2D array of vertical positions relative to the unperturbed sheet 
    surface, forming an axially symmetric inverted Gaussian distribution. This 
    represents the 'gravitational well' of each orbiting mass.

    The perturbation values are computed based on a Gaussian function that 
    decreases with distance from the centre up to and including the value
    perturb_radius.

    Parameters:
        - perturb_radius (ti.i32): The radius of the (circular) perturbation 
          area in the 2D grid.
        - perturb_max_depth (ti.f64): The maximum depth of the perturbation at 
          the centre of the distribution.
        - perturb_array (ti.template): A Taichi field (template) that stores 
          the perturbation values at each point in the 2D grid.

    Returns:
        None: This function updates the perturb_array field in place with the 
        computed perturbation values.
    """
    for offset_x, offset_y in ti.ndrange(
        (-perturb_radius, perturb_radius + 1),
        (-perturb_radius, perturb_radius + 1)
    ):
        distance_squared = offset_x * offset_x + offset_y * offset_y
        if distance_squared <= perturb_radius * perturb_radius:
            perturb_depth = (
                perturb_max_depth
                * -ti.exp(
                    -(abs(offset_x) / abs(perturb_radius)) ** 2
                    -(abs(offset_y) / abs(perturb_radius)) ** 2)
            )
            perturb_array[
                perturb_radius + offset_x, 
                perturb_radius + offset_y
            ] = perturb_depth


@ti.kernel
def overlay_perturb_shape_onto_grid(
        perturb_radius: ti.i32,
        perturb_array: ti.template(),
        first_orbital_coords: ti.template(),
        perturb_centre_grid_coords: ti.template(),
        oscillator_positions: ti.template(),
        oscillator_velocities: ti.template()
    ):
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
        - perturb_array perturb_centre_grid_coords: A 2D array representing 
          the vertical depth of the perturbation at each point within this 
          radius.
        - orbital_coords (ti.template()): The current x and y coordinates on 
          the surface representing the sphere position, floating point, 
          upon which the perturbation shape is overlaid.
        - perturb_centre_grid_coords (ti.template()): The actual discrete 
          grid positions (in the array) of the elements of the perturbation
          structure shape. The shape is aligned with the floating point
          value for the central position.
        - oscillator_positions (ti.template()): A 2D array containing the 
          three vector components of each oscillator comprising the rendered 
          surface.
        - oscillator_velocities (ti.template()): A 2D array containing the
          three vector components of each oscillator comprising the rendered 
          surface.

    Note:
        - For those oscillators whose positions are modified by the function, 
          the velocity is reset to zero.
    """
    grid_coords_x = int(ti.round(first_orbital_coords[None][0]))
    grid_coords_y = int(ti.round(first_orbital_coords[None][2]))

    for offset_x, offset_y in ti.ndrange(
            (-perturb_radius, perturb_radius + 1), 
            (-perturb_radius, perturb_radius + 1)
        ):
        if perturb_array[
            perturb_radius + offset_x, 
            perturb_radius + offset_y
        ] < oscillator_positions[
            grid_coords_x + offset_x,
            grid_coords_y + offset_y
        ][1]:
            oscillator_positions[
                    grid_coords_x + offset_x, 
                    grid_coords_y + offset_y
                
            ][1] = perturb_array[
                perturb_radius + offset_x, 
                perturb_radius + offset_y
            ]    
            
        oscillator_velocities[
            grid_coords_x,
            grid_coords_y
        ] = 0.0

   
def perform_rendering_of_spheres(
        model_binary_separation,
        number_of_spheres,
        rendered_first_orbital_coords,
        rendered_first_sphere_radius,
        rendered_second_orbital_coords,
        rendered_second_sphere_radius,
        rendered_merged_sphere_coords,
        rendered_merged_sphere_radius,
        scene
    ):  
    """
    Render spheres in a Taichi 3D scene based on the orbital positions.

    Each sphere is rendered with its specified radius, position, and color.

    Parameters:
        - model_binary_separation: The distance between the binary components. 
          A value of 0.0 indicates that the spheres are merged.
        - number_of_spheres: The number of spheres to render (1 or 2).
        - rendered_first_orbital_coords: Coordinates for the first sphere.
        - rendered_first_sphere_radius: Radius of the first sphere.
        - rendered_second_orbital_coords: Coordinates for the second sphere.
        - rendered_second_sphere_radius: Radius of the second sphere.
        - rendered_merged_sphere_coords: Coordinates for the merged sphere.
        - rendered_merged_sphere_radius: Radius of the merged sphere.
        - scene: The Taichi scene object used for rendering.

    Behaviour:
        - If 'model_binary_separation' is 0.0:
            - A merged sphere is rendered at 'rendered_merged_sphere_coords' 
              with a radius of 'rendered_merged_sphere_radius' and color 
              light gray (0.9, 0.9, 0.9).
        - If 'model_binary_separation' is non-zero:
            - If 'number_of_spheres' is 1 or 2:
                - The first sphere is rendered at 
                  'rendered_first_orbital_coords' with a radius of 
                  'rendered_first_sphere_radius' and color 
                  light gray (0.9, 0.9, 0.9).
            - If 'number_of_spheres' is 2:
                - The second sphere is rendered at 
                  'rendered_second_orbital_coords' with a radius of 
                  'rendered_second_sphere_radius' and color 
                   yellow-green (0.7, 0.9, 50).

    Returns:
        None
        
    Note:
        It is not possible to encapsulate this function in a Taichi kernel
        because the processing of the particles is done, implicitly, by a 
        kernel call. In Taichi, kernels cannot call kernels.
    """
    if model_binary_separation == 0.0: # merged
        scene.particles(
            rendered_merged_sphere_coords,
            rendered_merged_sphere_radius,
            color=(0.9, 0.9, 0.9)
        )   
    else:
        if (number_of_spheres == 1 or
            number_of_spheres == 2):  # Render the first sphere
            scene.particles(
                rendered_first_orbital_coords,
                rendered_first_sphere_radius,
                color=(0.9, 0.9, 0.9)
            )
        if number_of_spheres == 2:    # Render the second sphere
            scene.particles(
                rendered_second_orbital_coords,
                rendered_second_sphere_radius,
                color=(0.7, 0.9, 50)
            )   


@ti.kernel
def update_oscillator_positions_velocities_RK4(
        reduced_grid_start: ti.i32,
        reduced_grid_end: ti.i32,
        elastic_constant: ti.f64,
        adjacent_grid_elements: ti.template(),
        oscillator_velocities: ti.template(),
        oscillator_positions: ti.template(),
        oscillator_accelerations: ti.template(),
        oscillator_mass:ti.f64,
        timestep: ti.f64
    ):
    """
    Update the positions and velocities of oscillators using the fourth-order 
    Runge-Kutta (RK4) method.

    This function updates the positions and velocities of oscillators in 
    a 2D grid based on the RK4 integration method. The update takes into 
    account the elastic properties of the sheet and masses of the oscillators.

    Parameters:
        - reduced_grid_start (ti.i32): The starting index of the grid 
          to be updated (inclusive).
        - reduced_grid_end ti(.i32): The ending index of the grid to be 
          updated (exclusive).
        - elastic_constant (ti.f64: The elastic constant for the oscillators' 
          restoring force.
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
        oscillator_velocities in-place and has no return value.
    """
    for i, j in ti.ndrange((reduced_grid_start, reduced_grid_end),
                           (reduced_grid_start, reduced_grid_end)):

        vel = oscillator_velocities[i, j] 
        pos = oscillator_positions[i, j]

        k1 = timestep * vel
        l1 = timestep * update_oscillator_accelerations(
            i, j, adjacent_grid_elements, oscillator_positions, pos,
            elastic_constant, oscillator_mass
        )
        k2 = timestep * (vel + 0.5 * l1)
        l2 = timestep * update_oscillator_accelerations(
            i, j, adjacent_grid_elements, oscillator_positions, pos + 0.5 * k1,
            elastic_constant, oscillator_mass
        )
        k3 = timestep * (vel + 0.5 * l2)
        l3 = timestep * update_oscillator_accelerations(
            i, j, adjacent_grid_elements, oscillator_positions, pos + 0.5 * k2,
            elastic_constant, oscillator_mass
        )
        k4 = timestep * (vel + l3)
        l4 = timestep * update_oscillator_accelerations(
            i, j, adjacent_grid_elements, oscillator_positions, pos + k3,
            elastic_constant, oscillator_mass
        )
        oscillator_velocities[i, j] += (l1 + 2 * l2 + 2 * l3 + l4) / 6.0
        oscillator_positions[i, j] += (k1 + 2 * k2 + 2 * k3 + k4) / 6.0

@ti.func
def update_oscillator_accelerations(
        i, j,
        adjacent_grid_elements,
        oscillator_positions,
        pos,
        elastic_constant,
        oscillator_mass
    ):
    """
    Calculate the acceleration of an oscillator based on interactions with 
    adjacent grid elements.

    This function computes the accelerations of the oscillators. 
    This is done by considering the forces on each one exerted by the 
    adjacent oscillators. Hooke's law is then used to to compute the forces, 
    and the acceleration are updated using Newton's second law.

    Parameters:
        - grid_pos_x (int): Row index of the current oscillator in the grid.
        - grid_pos_y (int): Column index of the current oscillator in the grid.
        - adjacent_grid_elements (ti.template()): Taichi field containing 
          offsets of adjacent grid elements. Each entry specifies the relative
          position of a neighboring oscillator.
        - oscillator_positions (ti.template()): Taichi field containing 
          current positions of all oscillators in the grid.
        - pos (ti.Vector): Current position of the oscillator. 
        - elastic_constant (ti.f64): The elastic constant that governs the 
          force exerted by the springs between oscillators. All springs 
          modelled have an identical value of this constant.

    Returns:
        ti.Vector: The computed acceleration of the oscillator at position 
        (i, j), given by Newton's second law, F = ma, where F is the net force
        and m is the mass of the oscillator. All oscillators have identical 
        masses.
    """
    force = ti.Vector.zero(ti.f64, 3)
    for count in range(adjacent_grid_elements.shape[0]):
        x_offset = adjacent_grid_elements[count, 0]
        y_offset = adjacent_grid_elements[count, 1]
        force_matrix_x = i + x_offset
        force_matrix_y = j + y_offset
        displacement_vector = pos - oscillator_positions[
            force_matrix_x,
            force_matrix_y
        ]
        force -= elastic_constant * displacement_vector
    return force / oscillator_mass  # Newton's second law: F = ma


@ti.kernel
def rescale_orbital_coords_for_rendering(
        rendering_rescale: ti.f64,
        orbital_coords: ti.template(),
        rendered_orbital_coords: ti.template()
    ):
    """
    Rescale sphere coordinates to unit size for rendering.

    Parameters:
        - rendering_rescale (ti.f64): The scaling factor for rendering.
        - orbital_coords (ti.template()): Template for the original sphere 
          coordinates.
        - rendered_orbital_coords (ti.template()): Template for the rescaled 
        - sphere coordinates for rendering.
    """
    rendered_orbital_coords[0] = ( 
        [orbital_coords[None][0] * rendering_rescale,
         0.0,
         orbital_coords[None][2] * rendering_rescale]
        )


@ti.kernel
def damp_grid_boundary(
        number_of_damped_borders: ti.i32,
        reduced_grid_start: ti.i32,
        reduced_grid_end: ti.i32,
        damping_layer_depth: ti.i32,
        max_damping_factor: ti.f64,
        oscillator_velocities: ti.template(),
        oscillator_positions: ti.template()
    ):
    """
    Apply damping to oscillator velocities and positions at and near the 
    grid boundaries.
    The damping effect reduces the velocities and positions of the oscillators 
    within the specified boundary regions, with the intensity of damping
    increasing stepwise as the boundary is approached. 

    Parameters:
        - number_of_damped_borders (ti.i32): The number of borders to apply 
          damping to. 
        - reduced_grid_start (ti.i32): The starting index of the grid 
          to which damping should be applied (inclusive).
        - reduced_grid_end (ti.i32): The ending index of the grid to which 
          damping should be applied (exclusive).
        - damping_layer_depth (ti.i32): The number of grid cells from 
          the boundary where damping should start.
        - max_damping_factor (ti.f64): The maximum damping factor applied 
          at the boundary. The damping decreases linearly from this factor 
          towards zero as it moves away from the boundary.
        - oscillator_velocities (ti.template()): Taichi field containing 
          the current velocities of the oscillators.
        - oscillator_positions (ti.template()): Taichi field containing 
          the current positions of the oscillators. The damping is applied 
          to the second (vertical) component of the positions.

    Returns:
        None: This function modifies the 'oscillator_velocities' 
        and 'oscillator_positions' fields in-place and does not return any 
        value.
    """
    lower_damping_end_pos = reduced_grid_start + damping_layer_depth
    upper_damping_start_pos = reduced_grid_end - damping_layer_depth
    
    if number_of_damped_borders == 4:
        # Lower damping region
        for i in ti.ndrange(
                (reduced_grid_start, 
                 lower_damping_end_pos)
        ):
            damping_coefficient = (max_damping_factor
                                   * (lower_damping_end_pos - i)
                                   / damping_layer_depth)
            for j in ti.ndrange(
                    (reduced_grid_start, 
                     reduced_grid_end)
                ):
                oscillator_velocities[i, j]   *= (1 - damping_coefficient)
                oscillator_positions[i, j][1] *= (1 - damping_coefficient)
         
        # Upper damping region
        for i in ti.ndrange(
            (upper_damping_start_pos, 
             reduced_grid_end)
        ):
            damping_coefficient = (max_damping_factor
                                   * (i - upper_damping_start_pos)
                                   / damping_layer_depth)
            for j in ti.ndrange(
                    (reduced_grid_start, 
                     reduced_grid_end)
                ):
                oscillator_velocities[i, j]   *= (1 - damping_coefficient)
                oscillator_positions[i, j][1] *= (1 - damping_coefficient)
                
    # Left damping region (left boundary). Avoid the "corners" in order 
    # not to damp cells twice (which would not be desired).
    for j in ti.ndrange((reduced_grid_start, lower_damping_end_pos)):  
        damping_coefficient = (max_damping_factor
                               * (lower_damping_end_pos - j)
                               / damping_layer_depth)
        for i in ti.ndrange((reduced_grid_start + damping_layer_depth, 
                             reduced_grid_end - damping_layer_depth)):  
            oscillator_velocities[i, j] *= (1 - damping_coefficient)
            oscillator_positions[i, j][1] *= (1 - damping_coefficient)

    # Right damping region (right boundary). Avoid the "corners" in order 
    # not to damp cells twice (which would not be desired).
    for j in ti.ndrange((upper_damping_start_pos, reduced_grid_end)):  
        damping_coefficient = (max_damping_factor
                               * (j - upper_damping_start_pos)
                               / damping_layer_depth)
        for i in ti.ndrange((reduced_grid_start + damping_layer_depth, 
                             reduced_grid_end - damping_layer_depth)):  
            oscillator_velocities[i, j] *= (1 - damping_coefficient)
            oscillator_positions[i, j][1] *= (1 - damping_coefficient)          


@ti.kernel
def rescale_oscillator_heights(
        grid_size: ti.i32,
        vertical_scale: ti.f64,
        oscillator_positions: ti.template(),
        height_rescaled_positions: ti.template()
    ):
    """
    Rescale the vertical height component of oscillator positions.

    This function adjusts the vertical component (y-coordinate) of each 
    oscillator's position in the grid by applying a scaling factor. 
    The horizontal (x) and depth (z) components of the positions remain
    unchanged. The scaled positions are stored in a new Taichi field.

    Parameters:
        - grid_size (ti.i32): The size of the grid, assuming a square grid 
          of 'grid_size' x 'grid_size'.
        - vertical_scale (ti.f64): The scaling factor to apply to 
          the vertical (y) component of each oscillator's position.
        - oscillator_positions (ti.template()): Taichi field containing 
          the original positions of the oscillators.
        - height_rescaled_positions (ti.template()): Taichi field 
          where the height-rescaled positions will be stored.

    Returns:
        None: This function updates the 'height_rescaled_positions' 
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
        smoothed_oscillator_positions: ti.template()
    ):
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
        None: This function updates the 'smoothed_oscillator_positions' field
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
        height_rescaled_positions
    ) -> ti.f64:
    """
    Calculate the smoothed vertical component for a single cell based on the 
    values of its neighbours.

    This function, operating with the kernel function smooth_the_surface, 
    computes the average vertical height of oscillators within a smoothing 
    window centreed on the specified oscillator position. 
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
        grid_surface: ti.template()
    ):
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
        None: This function updates the 'grid_surface' field in-place 
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
def rescale_surface_for_rendering(
        grid_size: ti.i32,
        rendering_rescale: ti.f64,
        grid_surface: ti.template(),
        surface_for_rendering: ti.template()
    ):
    """
    The oscillator vectors representing the grid surface are rescaled for 
    rendering by Taichi. This rescaling is necessary because Taichi regards
    the 3D region it renders in the animation window as a 1 x 1 x 1 cube.
    """
    for i in range(grid_size):
        for j in range(grid_size):
            surface_for_rendering[i, j] = (grid_surface[i, j]
                                          * rendering_rescale)

@ti.kernel
def total_energy_of_sheet(
        grid_size: ti.i32,
        elastic_constant: ti.f64,
        oscillator_positions: ti.template(),
        oscillator_mass: ti.i32,
        oscillator_velocities: ti.template()
    ) -> ti.f64:
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
        - oscillator_mass (ti.i32): The mass of each oscillator, used to 
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


def color_longname_to_RGB(
        color_name,
        rgb_color,
        complementary_rgb_color
    ):
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
        grid_colors: ti.template()
    ):
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
        indices: ti.template()
    ):
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
        vertices: ti.template()
    ):
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
    # Handle mouse drag for popint of view (POV) adjustments
    current_mouse_pos = rendering_window.get_cursor_pos()
    if LMB_already_active:
        if prev_mouse_pos is not None:
            mouse_shift_x = current_mouse_pos[0] - prev_mouse_pos[0]
            mouse_shift_y = current_mouse_pos[1] - prev_mouse_pos[1]

            # Update horiz_angle_deg (left-right rotation, or yaw)
            horiz_angle_deg_sensitivity = 200.0
            horiz_angle_deg += mouse_shift_x * horiz_angle_deg_sensitivity
            horiz_angle_deg = (horiz_angle_deg + 180) % 360 - 180

            # Update vert_angle_deg (up-down rotation, or pitch)
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

    This function modifies the 'camera_zoom' value by interpreting vertical 
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
        - Inverted Y-axis mouse movement ('mouse_shift_y') is used for zoom 
          adjustments (upward movement zooms out; downward zooms in).
        - The zoom sensitivity is controlled by a scaling factor (10.0).
        - The function ensures thread safety and GUI consistency by "clamping" 
          the zoom level and updating the associated slider.
    """
    current_zoom_mouse_pos = rendering_window.get_cursor_pos()
    if RMB_already_active:
        if prev_zoom_mouse_pos is not None:
            # Inverted y-axis
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


def mainline_code(
        shared_slider_data,
        shared_display_data
    ):
    # =========================================================================
    # Mainline code for simulating the dynamics and emitted gravitational
    # waves for two orbiting spheres in space.
    # =========================================================================
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
    # =========================================================================
    ti.init(arch=ti.cpu,
        default_fp=ti.f64,
        kernel_profiler=True)
    show_system_information()
    
    # -------------------------------------------------------------------------
    # Global Constants and Configuration Variables
    # -------------------------------------------------------------------------
    # Extract the GUI values and place in the shared_slider_data dictionary. 
    # The use of the shared data dictionary independent of these processing
    # variables ensures thread safety.
    # We need to update the shared GUI data dictionary immediately because
    # several variables are needed in the following initialisation logic,
    # before commencing the main loop run.
    
    # Extract the GUI values and place in the shared_slider_data dictionary. 
    shared_slider_data_from_gui(shared_slider_data)
    # The use of the shared data dictionary independent of these processing
    # variables ensures thread safety.
    with shared_slider_data['lock']:
        first_orbital_radius  = shared_slider_data['first_orbital_radius']
        number_of_spheres     = shared_slider_data['number_of_spheres']
        first_sphere_mass     = shared_slider_data['first_sphere_mass']
        second_sphere_mass    = shared_slider_data['second_sphere_mass']
        vertical_scale        = shared_slider_data['vertical_scale']
        smoothing_window_size = shared_slider_data['smoothing_window_size']
        horiz_angle_deg       = shared_slider_data['horiz_angle_deg']
        vert_angle_deg        = shared_slider_data['vert_angle_deg']
        camera_zoom           = shared_slider_data['camera_zoom']
        grid_chequer_size     = shared_slider_data['grid_chequer_size']

    if first_sphere_mass == 0:
        first_sphere_mass = 1
    if second_sphere_mass == 0:
        second_sphere_mass = 1
    # If masses of spheres differ from one another, swap the sphere
    # masses. 
    if first_sphere_mass > second_sphere_mass:
        second_sphere_mass, first_sphere_mass = (
            first_sphere_mass, second_sphere_mass
            )
    with shared_slider_data['lock']: 
        shared_slider_data['first_sphere_mass'] = first_sphere_mass
        shared_slider_data['second_sphere_mass'] = second_sphere_mass
        slider_first_sphere_mass.set(shared_slider_data['first_sphere_mass'])
        slider_second_sphere_mass.set(shared_slider_data['second_sphere_mass'])
        
    # Disable the sliders for the masses during the run.  
    greyed_out_slider = {
        "state": "disabled",
        "fg": "grey",
        "bg": "lightgrey",
        "troughcolor": "grey"
    }
    root.after(0, lambda: slider_first_sphere_mass.config(**greyed_out_slider))
    root.after(0, lambda: slider_second_sphere_mass.config(**greyed_out_slider))
   
    # -------------------------------------------------------------------------
    # Grid parameters
    # -------------------------------------------------------------------------
    grid_centre = ti.Vector.field(3, dtype=ti.i32, shape=())
    grid_centre[None][0] = int((grid_size - 1) / 2)
    grid_centre[None][2] = int((grid_size - 1) / 2)
    
    # -------------------------------------------------------------------------
    # Initialisations of those variables that aren't set in the GUI
    # -------------------------------------------------------------------------
    vector_parameters = {
        "n": 3,
        "dtype": ti.f64,
        "shape": ()
    }
    first_orbital_coords = ti.Vector.field(**vector_parameters)
    second_orbital_coords = ti.Vector.field(**vector_parameters)

    # -------------------------------------------------------------------------
    # Grey out fields that cannot be updated by the user during the run.
    # -------------------------------------------------------------------------
    greyed_out_run_option_dropdown = {
        "state": "disabled",
        "fg": "grey",
        "bg": "lightgrey"
        # no troughcolor possible for dropdown widgets
    }

    # If the user hasn't selected an option, set a default value.
    if run_option.get() == "Select a Run Option":
        run_option.set("Set first sphere orbital radius")   # For displaying 
    run_option_value = run_option.get()                     # For processing

    # In any case, grey out the dropdown options now, to show, and ensure,
    # that the selection cannot be changed during the run.
    root.after(0, 
               lambda: 
               run_option_dropdown.config(**greyed_out_run_option_dropdown))

    # -------------------------------------------------------------------------
    #  Main run options vs. testing run options
    # -------------------------------------------------------------------------
    if "test" in run_option_value.lower(): 
        # Don't alter the value but grey out.
        slider_first_orbital_radius.config(**greyed_out_slider)
        root.after(0, 
                   lambda: 
                   slider_first_orbital_radius.config(**greyed_out_slider)
        )
        number_of_spheres = 0   
        root.after(0, 
                   set_and_grey_out_number_of_spheres)

        astro_omega = 0.0
        model_omega = 0.0
        astro_first_sphere_orbital_speed = 0.0
        binary_energy_loss = 0.0
        astro_orbital_decay = 0.0  
            
    # Compute the sphere and perturbation radii from the respective masses.
    first_sphere_radius  = pow(first_sphere_mass, 1/3) 
    second_sphere_radius = pow(second_sphere_mass, 1/3)
   
    # Compute the second orbital radius based on the mass ratio and 
    # the first orbital radius. 
    sphere_mass_ratio = first_sphere_mass / second_sphere_mass
    second_orbital_radius = first_orbital_radius * sphere_mass_ratio
            
    # Initialize the orbits by using the polar angle to compute the two initial 
    # orbital positions for the system.
    previous_polar_angle = 0.0
    current_polar_angle  = 0.0    
    calculate_orbital_coords(
        grid_centre,
        first_orbital_radius,
        current_polar_angle,
        first_orbital_coords
    )    
    calculate_orbital_coords(
        grid_centre,
        second_orbital_radius,
        current_polar_angle + 180,
        second_orbital_coords
    )
        
    # Allow sufficient space between perturbation extents and grid edge
    # so that everything is captured on the visible grid domain. This is also
    # designed to work for the spacing of the two test run perturbations (which
    # remain immovable).
    # Reset orbital radius on each restarted run.
    default_first_orbital_radius = ti.Vector.field(**vector_parameters)
    default_first_orbital_radius = grid_size / 4
    rendered_merged_sphere_coords = ti.Vector.field(3, 
                                                    dtype=ti.f64, 
                                                    shape=(1,))
    
    # -------------------------------------------------------------------------
    # Damping parameters
    # -------------------------------------------------------------------------
    number_of_damped_borders = 4
    depth_zeroised_grid_edges = 1
    damping_layer_depth = grid_size // 20  
    
    # Calculate 'effective' grid dimensions: exclude zeroized layers at the 
    # edges. Only the positions and velocities within this smaller grid 
    # need be updated by the application.
    # Like grid_size, reduced_grid_size is, consequently, an odd integer.
    reduced_grid_start = depth_zeroised_grid_edges
    reduced_grid_end = grid_size - depth_zeroised_grid_edges

    grid_size_args = {
        "n": 3,
        "dtype": ti.f64,
        "shape": (grid_size, grid_size)
    }
    grid_surface = ti.Vector.field(**grid_size_args)
    initialize_array_of_vectors(
        grid_surface,
        grid_size
    )
    surface_for_rendering = ti.Vector.field(**grid_size_args)
    initialize_array_of_vectors(
        surface_for_rendering,
        grid_size
    )
    
    # -------------------------------------------------------------------------
    # Perturbation parameters
    # -------------------------------------------------------------------------
    # Because the sphere radii will be used for the array creation for 
    # perturbation form/shape, both the masses and the radius augmentation
    # need to be integers.
    radius_augmentation_factor = 1
     
    # Set perturbation radial extension to be proportional to sphere mass.
    first_perturb_radius = first_sphere_mass * radius_augmentation_factor
    second_perturb_radius = second_sphere_mass * radius_augmentation_factor
    merged_perturb_radius = first_sphere_mass + second_sphere_mass 
    merged_perturb_radius *= radius_augmentation_factor

    first_perturb_max_depth = first_sphere_mass  
    second_perturb_max_depth = second_sphere_mass   
    merged_perturb_max_depth = first_sphere_mass + second_sphere_mass
    
    # Define the system separation distance for merging.
    merging_distance = first_perturb_radius + second_perturb_radius

    # Rendered sphere size can be exaggerated by an arbitrary value, as 
    # required for vizualisation. 
    sphere_augmentation_factor = 1.0
    merged_sphere_radius = pow(
        second_sphere_mass + first_sphere_mass, 1/3
        ) * sphere_augmentation_factor 
    
    first_perturb_grid_coords = ti.Vector.field(3, dtype=ti.i32, shape=())
    second_perturb_grid_coords = ti.Vector.field(3, dtype=ti.i32, shape=())
    
    # Sphere perturbation calculations 
    first_perturb_array = ti.field(
        dtype=ti.f64,
        shape=(first_perturb_radius * 2 + 1,
               first_perturb_radius * 2 + 1)
    )
    create_gaussian_perturb_array(
        first_perturb_radius,
        first_perturb_max_depth,
        first_perturb_array
    )
    
    second_perturb_array = ti.field(
        dtype=ti.f64,
        shape=(second_perturb_radius * 2 + 1,
               second_perturb_radius * 2 + 1)
    )
    create_gaussian_perturb_array(
        second_perturb_radius,
        second_perturb_max_depth,
        second_perturb_array
    )
    
    merged_perturb_array = ti.field(
        dtype=ti.f64,
        shape=(merged_perturb_radius * 2 + 1,
               merged_perturb_radius * 2 + 1)
    )
    create_gaussian_perturb_array(
        merged_perturb_radius,
        merged_perturb_max_depth,
        merged_perturb_array
    )

    # -------------------------------------------------------------------------
    # Sheet surface computations
    # -------------------------------------------------------------------------
    # Define a field to store the offsets for four adjacent grid elements 
    # (North, East, South, West) that form a square surrounding the central 
    # element. These are used to calculate the forces acting on each 
    # oscillator. 
    adjacent_grid_elements = ti.field(dtype=ti.i32, shape=(4, 2))
    offsets = [
        [ 0, 1],  # North: directly above
        [ 1, 0],  # East: directly to the right
        [ 0,-1],  # South: directly below
        [-1, 0]   # West: directly to the left
        ]

    # Populate the adjacent grid elements field with these offset values. 
    for i in range(4):
        for j in range(2):
            adjacent_grid_elements[i, j] = offsets[i][j]

    oscillator_positions = ti.Vector.field(**grid_size_args)
    initialize_array_of_vectors(oscillator_positions,
                                grid_size)
    
    height_rescaled_positions = ti.Vector.field(**grid_size_args)
    initialize_array_of_vectors(height_rescaled_positions,
                                grid_size)

    oscillator_velocities = ti.Vector.field(**grid_size_args)
    oscillator_accelerations = ti.Vector.field(**grid_size_args)
    
    # Sheet Surface Smoothing -------------------------------------------------
    smoothed_cell_position = ti.Vector.field(2, dtype=ti.i32, shape=())
    smoothing_start_pos = reduced_grid_start + depth_zeroised_grid_edges
    smoothing_end_pos = reduced_grid_end - depth_zeroised_grid_edges
    smoothed_oscillator_positions = ti.Vector.field(**grid_size_args)
    initialize_array_of_vectors(
        smoothed_oscillator_positions,
        grid_size
    )
    # -------------------------------------------------------------------------
    # Model sheet parameters
    # -------------------------------------------------------------------------
    elastic_constant = 1e11
    timestep = 1e-7
    oscillator_mass = 1.0
    
    max_damping_factor = 0.03
    # Common values range between 0.05 and 0.2.
    
    default_polar_angle_step = 1.0
    model_omega = 0.0
    
    # -------------------------------------------------------------------------
    # Astrophysical parameters
    # -------------------------------------------------------------------------
    astro_omega = 0.0
    binary_energy_loss = 0.0
    astro_binary_separation = 0.0
    astro_first_sphere_orbital_speed = 0.0
    astro_orbital_decay = 0.0
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
    astro_summed_masses = (second_sphere_mass + first_sphere_mass) * m_sun
    binary_energy_loss_factor = 32/5 * newtons_const_to_fourth_power
    binary_energy_loss_factor *= (
        m_sun_squared
        * (first_sphere_mass * second_sphere_mass) ** 2
        / (first_sphere_mass + second_sphere_mass) ** 2
    )
    binary_energy_loss_factor /= lightspeed_to_fifth_power
    
    # -------------------------------------------------------------------------
    # Rendering vars 
    # -------------------------------------------------------------------------
    rendered_first_orbital_coords = ti.Vector.field(
        3,
        dtype=ti.f64,
        shape=(1,)
    )
    rendered_second_orbital_coords = ti.Vector.field(
        3,
        dtype=ti.f64,
        shape=(1,)
    )
    rendering_rescale = 1 / grid_size
    
    rendered_first_sphere_radius = (
        first_sphere_radius
        * rendering_rescale
    )
    rendered_second_sphere_radius = (
        second_sphere_radius
        * rendering_rescale
    )
    rendered_merged_sphere_radius = (
        merged_sphere_radius
        * rendering_rescale
    )
    rescale_orbital_coords_for_rendering(
        rendering_rescale,
        grid_centre,
        rendered_merged_sphere_coords
    )
    # -------------------------------------------------------------------------
    # Set surface colors depending on run type
    # -------------------------------------------------------------------------
    if "test" in run_option_value.lower():         
        color_name = "dodgerblue"  # Test surface is blue, reminiscent of
                                   # a liquid surface such as water.
    else:
        color_name = "orange"  # Sheet surface is orange for normal runs,
                               # reminiscent of some physical models.
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
    
    # -------------------------------------------------------------------------
    # Set up rendering data 
    # -------------------------------------------------------------------------
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

    info_window, labels = start_info_window(
        root, 
        run_option_value, 
        shared_display_data
    )
    root.after(
        0, 
        update_info_window, 
        run_option_value, 
        shared_display_data, 
        info_window, 
        labels
    )
    
    first_iteration_merge_binary = True
    first_iteration_test_run = True
    
    # -------------------------------------------------------------------------
    # Mouse and camera setup 
    # -------------------------------------------------------------------------
    prev_mouse_pos = None  # To store the last mouse position
    prev_zoom_mouse_pos = None
    LMB_already_active = False
    RMB_already_active = False
    view_distance = 0.5  # Distance from the centre of the surface
    camera_position_x = 0.0
    camera_position_y = 0.0
    horiz_angle_deg = 0.0  # Horizontal angle 
    vert_angle_deg = 0.0   # Vertical angle
    
    print("Key Variables")
    print("=============")
    print("Surface grid_size:        ", grid_size, "x", grid_size)
    print(f"elastic_constant:          {elastic_constant:.2e}")
    print("first perturbation size:  ", first_perturb_radius * 2, "x", 
                                        first_perturb_radius * 2)
    print("second perturbation size: ", second_perturb_radius * 2, "x", 
                                        second_perturb_radius * 2)
    print("default_polar_angle_step: ", default_polar_angle_step)  
    print("timestep:                 ", timestep)
    print("merging_distance:         ", merging_distance) 
    print("max_damping_factor:       ", max_damping_factor) 

    # =========================================================================
    # This is the main loop 
    # =========================================================================
    while (
        shared_slider_data['running'] and
        shared_display_data['running']
    ):
        simulation_frame_counter += 1
        prev_time_stamp = time.time()
        
        # Extract the GUI values and place in the shared_slider_data 
        # data dictionary. 
        shared_slider_data_from_gui(shared_slider_data)
        # Initialize processing variables using values from the shared
        # data dictionary. This decoupling ensures thread safety by 
        # isolating shared data from processing logic.
        with shared_slider_data['lock']:
            first_orbital_radius  = shared_slider_data['first_orbital_radius']
            number_of_spheres     = shared_slider_data['number_of_spheres']
            first_sphere_mass     = shared_slider_data['first_sphere_mass']
            second_sphere_mass    = shared_slider_data['second_sphere_mass']
            vertical_scale        = shared_slider_data['vertical_scale']
            smoothing_window_size = shared_slider_data['smoothing_window_size']
            horiz_angle_deg       = shared_slider_data['horiz_angle_deg']
            vert_angle_deg        = shared_slider_data['vert_angle_deg']
            camera_zoom           = shared_slider_data['camera_zoom']
            grid_chequer_size     = shared_slider_data['grid_chequer_size']

        if not simulation_paused.is_set():
            if run_option_value in [
                "Set first sphere orbital radius",
                "Inspiralling"
            ]: 
                second_orbital_radius = (first_orbital_radius 
                                         * sphere_mass_ratio)   
                model_binary_separation = (first_orbital_radius 
                                           + second_orbital_radius)
                previous_polar_angle = current_polar_angle
                
                # Check the orbital radius value read from the GUI. 
                # The user may have manually adjusted this value during the 
                # run. Adjust the second radius accordingly.
                if model_binary_separation >= merging_distance:
                    # ---------------------------------------------------------
                    # Compute the astrophysical separation distance using that
                    # of the model. This is needed: 
                    # - as information for the display window, and
                    # - for the case of merging, the astro orbital decay value.
                    # ---------------------------------------------------------
                    astro_binary_separation = model_to_astro_scale(
                        model_binary_separation,
                        astro_length_scaling
                    )
                                        
                    # The omega value for the model is simply the value in the
                    # simulation, "as seen in realtime" (wall clock time) 
                    # during the run. 
                    if loop_duration != 0.0: # Avoid the zerodivide condition 
                                             # by setting the value of omega 
                                             # to zero if the loop duration 
                                             # is zero.  
                        delta_polar_angle = compute_polar_angle_increase(
                            default_first_orbital_radius,
                            first_orbital_radius,
                            default_polar_angle_step
                        )
                        model_omega = calculate_model_omega(
                            delta_polar_angle,
                            loop_duration
                        )
                        current_polar_angle = (
                            previous_polar_angle + delta_polar_angle
                            )
                    else:
                        model_omega == 0.0   
   
                    # ---------------------------------------------------------
                    # Compute the astrophysical angular velocity (astro_omega)
                    # based on the astrophysical orbital separation, 
                    # gravitational constant, and the sum of the masses of 
                    # the objects in the system.
                    # ---------------------------------------------------------
                    astro_omega = calculate_astro_omega(
                        astro_binary_separation,
                        newtons_const,
                        astro_summed_masses
                    )     
               
                    # --------------------------------------------------------- 
                    # Adjust orbits if selected run type is inspiralling.
                    # ---------------------------------------------------------
                    if run_option_value == "Inspiralling":
                        astro_orbital_decay = calc_astro_orbital_decay(
                            astro_binary_separation,
                            first_sphere_mass,
                            second_sphere_mass,
                            orbital_decay_factor
                        )
                        model_orbital_decay = (
                            astro_orbital_decay / astro_length_scaling
                            * model_omega / astro_omega
                        )
                        # If the orbital shrinkage exceeds the remaining 
                        # distance between the binary components, 
                        # treat the system as now merged.
                        if model_orbital_decay >= (
                                model_binary_separation
                                - merging_distance
                            ):
                            first_orbital_radius = 0.0
                            second_orbital_radius = 0.0
                            model_binary_separation = 0.0
                        else:
                            # Reduce the size of the orbits for the system.
                            first_orbital_radius -= (
                                first_orbital_radius 
                                * model_orbital_decay 
                                / model_binary_separation)
                            second_orbital_radius = (first_orbital_radius 
                                                     * sphere_mass_ratio) 
                            model_binary_separation = (first_orbital_radius 
                                                       + second_orbital_radius)    
                        root.after(
                            0, 
                            slider_first_orbital_radius.set, 
                            first_orbital_radius
                        )
                else:    
                    model_binary_separation = 0.0
                    root.after(
                        0, 
                        slider_first_orbital_radius.set, 
                        0.0
                    )
                    
                if model_binary_separation != 0.0:        
                    # The second orbital radius is calculated using the 
                    # first one and the sphere mass ratio.
                    second_orbital_radius = (first_orbital_radius 
                                             * sphere_mass_ratio)   
                    model_binary_separation = (first_orbital_radius 
                                               + second_orbital_radius)
                    # ---------------------------------------------------------
                    # We compute these again because the binary orbit
                    # sizes may have been reduced by the inspiral effect.
                    # ---------------------------------------------------------
                    astro_binary_separation = model_to_astro_scale(
                        model_binary_separation,
                        astro_length_scaling
                    )
                    astro_omega = calculate_astro_omega(
                        astro_binary_separation,
                        newtons_const,
                        astro_summed_masses
                    )
                    if loop_duration != 0.0:
                        model_omega = calculate_model_omega(
                            delta_polar_angle,
                            loop_duration
                        )
                        current_polar_angle %= 360
                    else:
                        model_omega == 0.0  

                    astro_first_orbital_radius = model_to_astro_scale(
                        first_orbital_radius,
                        astro_length_scaling
                    )
                    # Calculate the orbital speed of the first sphere.
                    astro_first_sphere_orbital_speed = (
                        astro_omega * astro_first_orbital_radius
                    )
                    # Display the gravitational wave energy loss at the current 
                    # orbit (even for the run type of non-inspiralling).
                    binary_energy_loss = compute_binary_energy_loss(
                        binary_energy_loss_factor,
                        astro_binary_separation,
                        astro_omega
                    )
                    # Use the polar angle to compute the two orbital positions 
                    # for the system.
                    calculate_orbital_coords(
                        grid_centre,
                        first_orbital_radius,
                        current_polar_angle,
                        first_orbital_coords
                    )
                    calculate_orbital_coords(
                        grid_centre,
                        second_orbital_radius,
                        current_polar_angle + 180,
                        second_orbital_coords
                    )
                    overlay_perturb_shape_onto_grid(
                        first_perturb_radius,
                        first_perturb_array,
                        first_orbital_coords,
                        first_perturb_grid_coords,
                        oscillator_positions,
                        oscillator_velocities
                    )
                    overlay_perturb_shape_onto_grid(
                        second_perturb_radius,
                        second_perturb_array,
                        second_orbital_coords,
                        second_perturb_grid_coords,
                        oscillator_positions,
                        oscillator_velocities
                    )
                    rescale_orbital_coords_for_rendering(
                        rendering_rescale,
                        first_orbital_coords,
                        rendered_first_orbital_coords
                    )            
                    rescale_orbital_coords_for_rendering(
                        rendering_rescale,
                        second_orbital_coords,
                        rendered_second_orbital_coords
                    )                    
                    # If merging has not taken place, place either one or both
                    # orbiting spheres at the correct coordinates. If merging
                    # has taken place, place a larger sphere in the centre 
                    # of the rendered surface to represent the final, merged,
                    # object.
                    perform_rendering_of_spheres(
                        model_binary_separation,
                        number_of_spheres,
                        rendered_first_orbital_coords,
                        rendered_first_sphere_radius,
                        rendered_second_orbital_coords,
                        rendered_second_sphere_radius,
                        rendered_merged_sphere_coords,
                        rendered_merged_sphere_radius,
                        scene
                    ) 
                else:
                    # model_binary_separation is zero 
                    if first_iteration_merge_binary:
                        # Reset these parameters because the binaries 
                        # are merged. Execute this code block only once.
                        first_iteration_merge_binary = False
                        first_orbital_radius = 0.0
                        second_orbital_radius = 0.0
                        astro_binary_separation = 0.0
                        astro_first_sphere_orbital_speed = 0.0
                        model_omega = 0.0
                        astro_omega = 0.0
                        binary_energy_loss = 0.0
                        astro_orbital_decay = 0.0
                       
                        # Grey out the options, in the GUI, for 
                        # - choosing the number of spheres to display.
                        # - setting the orbital radius.
                        root.after(0, set_and_grey_out_two_sliders)

                        # Place the perturbation associated with the central 
                        # sphere once only since a stationary mass produces
                        # no gravitational waves.
                        calculate_orbital_coords(
                            grid_centre,
                            first_orbital_radius,
                            current_polar_angle,
                            first_orbital_coords
                        )
                        overlay_perturb_shape_onto_grid(
                            merged_perturb_radius,
                            merged_perturb_array,
                            first_orbital_coords,
                            first_perturb_grid_coords,
                            oscillator_positions,
                            oscillator_velocities
                        )
                    # Set a single sphere, the merged sphere, in the rendered 
                    # surface centre. This needs to be rendered for every 
                    # frame, although its position remains fixed.
                    perform_rendering_of_spheres(
                        model_binary_separation,
                        number_of_spheres,
                        rendered_first_orbital_coords,
                        rendered_first_sphere_radius,
                        rendered_second_orbital_coords,
                        rendered_second_sphere_radius,
                        rendered_merged_sphere_coords,
                        rendered_merged_sphere_radius,
                        scene
                    ) 
                    
            if "test" in run_option_value.lower():
                # Test run cases ----------------------------------------------
                # For simplicity, the test runs do not feature rendered 
                # spheres. This allows for future development using the wave
                # features only.
                # -------------------------------------------------------------
                if first_iteration_test_run:
                     # Execute this code block only once.
                     first_iteration_test_run = False
                     
                     first_orbital_coords[None] = ti.Vector([
                     grid_centre[None][0] + first_orbital_radius,
                     0.0,
                     grid_centre[None][2] # keep this axis zero, as the two 
                                          # test run perturbation positions
                                          # have only the x-coord non-zero.
                     ])
                     second_orbital_coords[None] = ti.Vector([
                         grid_centre[None][0] - first_orbital_radius,
                         0.0,
                         grid_centre[None][2]
                     ])
                     
                     # Overlay each perturbation (only once).
                     overlay_perturb_shape_onto_grid(
                         first_perturb_radius,
                         first_perturb_array,
                         first_orbital_coords,
                         first_perturb_grid_coords,
                         oscillator_positions,
                         oscillator_velocities
                     )
                     overlay_perturb_shape_onto_grid(
                         second_perturb_radius,
                         second_perturb_array,
                         second_orbital_coords,
                         second_perturb_grid_coords,
                         oscillator_positions,
                         oscillator_velocities
                     )
                     
                # Having two opposite borders damped with the other two 
                # undamped allows a visual comparison to be made, in order to 
                # further adjust parameters, should this be needed in future.
                if run_option_value == "Test 1 - two of four borders damped":
                    number_of_damped_borders = 2

            # The damping of all four grid boundary layers is done for both 
            # the simulation proper, and one test case.
            damp_grid_boundary(
                number_of_damped_borders,
                reduced_grid_start,
                reduced_grid_end,
                damping_layer_depth,
                max_damping_factor,
                oscillator_velocities,
                oscillator_positions
            )

            # -----------------------------------------------------------------
            # Determine the new oscillator positions using the Runge-Kutta 
            # 4th order numerical integration. This function is the core 
            # of the whole simulation.
            # -----------------------------------------------------------------
            update_oscillator_positions_velocities_RK4(
                reduced_grid_start,
                reduced_grid_end,
                elastic_constant,
                adjacent_grid_elements,
                oscillator_velocities,
                oscillator_positions,
                oscillator_accelerations,
                oscillator_mass,
                timestep
            )

        if simulation_paused.is_set():
            # Spheres must be continually rendered (in every paused frame)
            # because Taichi rendered "particles" need to be updated and 
            # replaced.
            if run_option_value in [
                "Set first sphere orbital radius",
                "Inspiralling"
                ]:
                model_binary_separation = (first_orbital_radius 
                                           + second_orbital_radius)
                perform_rendering_of_spheres(
                    model_binary_separation,
                    number_of_spheres,
                    rendered_first_orbital_coords,
                    rendered_first_sphere_radius,
                    rendered_second_orbital_coords,
                    rendered_second_sphere_radius,
                    rendered_merged_sphere_coords,
                    rendered_merged_sphere_radius,
                    scene
                )      
                # If the simulation is paused, reset all dynamic properties
                # so that the display window correctly represents the variables 
                # during the pause.
                astro_first_sphere_orbital_speed = 0.0
                astro_omega = 0.0
                model_omega = 0.0
                binary_energy_loss = 0.0
                astro_orbital_decay = 0.0
   
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
            rescale_surface_for_rendering(
                grid_size,
                rendering_rescale,
                smoothed_oscillator_positions,
                surface_for_rendering
            )
        else:
            rescale_surface_for_rendering(
                grid_size,
                rendering_rescale,
                height_rescaled_positions,
                surface_for_rendering
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
            surface_for_rendering,
            vertices
        )
        # Add objects to the rendering scene
        scene.mesh(
            vertices,
            indices=indices,
            per_vertex_color=(grid_colors),
            two_sided=True
        )
        # Start the rendering proper
        canvas.scene(scene)
        scene.ambient_light(color=(0.5, 0.5, 0.5))  # Ambient light
        scene.point_light(pos=(2, 4, 4), color=(1.0, 1.0, 1.0))
        rendering_window.show()
        camera = ti.ui.make_camera()
        scene.set_camera(camera)
        
        # Adjust the (point of) view based on mouse movement with left mouse
        # click (LMB, left mouse button).
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
        
        # Adjust the zoom based on mouse movement with right mouse button (RMB) 
        # depressed.
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
        
        # Prevent the vertical angle from reaching exactly 90 degrees (since 
        # the surface cannot be unambiguously rendered at exactly this angle).
        if vert_angle_deg > 89.99:
            vert_angle_deg = 89.99  

        vert_angle_rad = math.radians(vert_angle_deg)
        horiz_angle_rad = math.radians(horiz_angle_deg)
        
        # Define the fixed point in space that the camera will always be
        # oriented at.
        look_at_x = 0.5
        look_at_y = 0.0
        look_at_z = 0.5
        camera_position_x = (look_at_x 
                             + view_distance * math.cos(vert_angle_rad) 
                               * math.cos(horiz_angle_rad))
        camera_position_y = (look_at_z 
                             + view_distance * math.cos(vert_angle_rad) 
                               * math.sin(horiz_angle_rad))
        camera_height = (look_at_y 
                         + view_distance * math.sin(vert_angle_rad))

        # Set (point of) view using camera parameters
        camera.position(
            camera_position_x,
            camera_height,
            camera_position_y
        )
        camera.lookat(look_at_x,
                      look_at_y,
                      look_at_z)
        scene.set_camera(camera)
        
        # Test showing total energy of surface.
        """if "test" in run_option_value.lower():
            oscillator_mass = 1
            energy_of_sheet = total_energy_of_sheet(
                grid_size,
                elastic_constant,
                oscillator_positions,
                oscillator_mass,
                oscillator_velocities
            )
            print("Test, total surface energy of sheet")
            print("===================================")
            print("simulation_frame_counter", simulation_frame_counter)
            print("energy_of_sheet", energy_of_sheet)"""
        
        # Housekeeping of loop data -------------------------------------------
        loop_duration = time.time() - prev_time_stamp
        fps = 1/loop_duration
        if simulation_frame_counter == 1:
            start_time = time.time()
        elapsed_time = time.time() - start_time  # This is our wall clock time. 
                                                 # Runs even when loop paused.
        with shared_display_data['lock']:
            shared_display_data['elapsed_time'] = elapsed_time
            shared_display_data['fps'] = fps
            shared_display_data[
                'astro_binary_separation'
                ] = astro_binary_separation
            shared_display_data[
                'astro_first_sphere_orbital_speed'
                ] = astro_first_sphere_orbital_speed
            shared_display_data['astro_omega'] = astro_omega
            shared_display_data['model_omega'] = model_omega
            shared_display_data['binary_energy_loss'] = binary_energy_loss
            shared_display_data['astro_orbital_decay'] = astro_orbital_decay

    # -------------------------------------------------------------------------
    # Drop out of the main loop.
    # -------------------------------------------------------------------------
    # This section of the code reactivates those widgets that have been  
    # disabled, so that their default values can be set in readiness for the
    # next program run.
    reactivate_slider = {
        "state": "normal",
        "fg": "black",
        "bg": "light steel blue",
        "troughcolor": "steel blue"
    }
    slider_first_orbital_radius.config (**reactivate_slider)
    slider_first_sphere_mass.config    (**reactivate_slider)
    slider_second_sphere_mass.config   (**reactivate_slider)
    slider_number_of_spheres.config    (**reactivate_slider)
    root.after(0, update_gui_sliders_with_defaults)
    shared_slider_data_from_gui(shared_slider_data)
    reset_shared_display_data(shared_display_data)

    reactivate_dropdown = {
        "state": "normal",
        "fg": "black",
        "bg": "light steel blue",
    }
    run_option_dropdown.config (**reactivate_dropdown)
    run_option.set("Select a Run Option")  # Default prompt for selection

    # At the end of the run, this option shows the CPU usage for each 
    # Taichi kernel function.
    if "test" in run_option_value.lower(): 
        ti.sync()
        ti.profiler.print_kernel_profiler_info()
        
root.mainloop()