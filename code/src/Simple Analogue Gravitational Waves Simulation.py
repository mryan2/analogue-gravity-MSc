# Start of Python script

# Library imports
# -----------------------------------------------------------------------------
# Python code reduces memory usage by only loading the minimum amount of
# components by default. Additional so-called Libraries/Packages must 
# therefore be declared explicitly. 
# This is done by the use of an import statement which 
# - finds the module
# - loads the code
# - makes its functions & variables available.
# Imports are either from 
# - the standard Python library or 
# - from a third-party library.

# Third-party library imports
from pyautogui import size   # Used for obtaining screen resolution

# Import the "process and system utilities" library, here for obtaining 
# (only) CPU information.
from psutil import cpu_count, cpu_freq, cpu_percent    

from matplotlib import colors as mcolors  # Use for converting string to RGB

# Standard library imports 
from datetime import datetime  # To get the current date and time
import time                    # Use for loop timing purposes

# Import the necessary system information modules. These are for displaying 
# information at the beginning of the run and (when needed) for testing.  
from sys import (
    getwindowsversion,
    version             # Specify Python version
)      

# from sys import exit  # For testing: prematurely finish the run 

# Import threading components because the GUI cannot run in the same process 
# as the main loop.
from threading import Thread, Event, Lock   

import taichi as ti  # Use for enhancing rendering performance 

# Construct the Tkinter GUI containing the sliders and buttons through
# which the user input controls the application. 
# -----------------------------------------------------------------------------
# Import essential components from the tkinter library for creating the GUI.
# They include widgets for 
# - the layout (Frame, Label), 
# - user interaction (Button, Slider), and
# - variable management (DoubleVar, IntVar, StringVar).
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

root = Tk()  # Create the main application window

root.config(bg="black")  
root.attributes('-topmost', 1)  # Set GUI window to be on top of all others 

# Set GUI window nonresizeable and disable window dragging.
root.resizable(False, False)

# Create frameless window (no title bar, no borders).
root.overrideredirect(True)

# Set the GUI screen width and height   
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
GUI_width = int(screen_width/5)
GUI_height = int(screen_height)
root.geometry(f"{GUI_width}x{GUI_height}+0+0") 

# Get variables from GUI, to be used for program control and the computations.
tkinter_outer_orbital_radius    = DoubleVar()
tkinter_spheres_to_display      = IntVar()
tkinter_inner_sphere_mass       = IntVar()
tkinter_outer_sphere_mass       = IntVar()
tkinter_vertical_rescale        = IntVar()
tkinter_smoothing_window_size   = IntVar()
tkinter_camera_look_up_down     = DoubleVar()
tkinter_camera_height           = DoubleVar()
tkinter_camera_left_right       = DoubleVar()
tkinter_camera_backward_forward = DoubleVar()
tkinter_grid_chequer_size       = IntVar()

padx, pady = 2, 2

# The size of the grid, representing a square 2D array, where the grid size
# corresponds to one side of the square. The grid size is hard coded here. 
# Its optimal value must be empirically determined. Its value is 
# already needed at this point in the code, for the slider definitions.  
# Since we require one cell to represent the centre coordinates of the grid, 
# the grid side lengths need to be an odd number.
grid_size = 600 + 1

# Scale up the grid element size (default 1 unit) to a real astronomical 
# distance (in metres). 
astro_length_scaling = 1e4
formatted_astro_length_scaling = format(astro_length_scaling, ".0e")

# Create these variable structures for reuseability.
horiz_slider_arguments = {
    "bg": "light steel blue",
    "troughcolor": "steel blue",
    "orient": "horizontal"
}
vert_slider = {
    "bg": "light steel blue",
    "troughcolor": "steel blue",
    "orient": "vertical",
    "length": GUI_height / 5
}
slider_outer_orbital_radius = Scale (
    label="Outer Sphere Orbital Radius (m x " 
        + formatted_astro_length_scaling + ")",
    variable=tkinter_outer_orbital_radius,
    from_=0, to=grid_size / 2,
    tickinterval=(grid_size / 2 - 10) / 4,
    **horiz_slider_arguments
)
slider_outer_orbital_radius.set(grid_size // 3)
slider_outer_orbital_radius.pack (
    side=TOP, 
    padx=padx * 2, 
    pady = (pady * 2, pady), 
    fill=BOTH
)

# Create a frame to hold the widgets for the sphere parameters
frame = Frame(root, bg="black")
                                                            
# Define dictionaries for the common packing options of the widgets
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
                                                           
frame.pack(**pack_top)  
slider_spheres_to_display = Scale (
    frame,
    label="# Spheres",
    variable=tkinter_spheres_to_display,
    from_=0, to=2,
    tickinterval=1,
    **horiz_slider_arguments
)
slider_spheres_to_display.pack(**pack_left)
slider_spheres_to_display.set(2)
slider_inner_sphere_mass = Scale (
    frame,
    label="Mass 1 [M⊙]",
    variable=tkinter_inner_sphere_mass,
    from_=1, to=50,
    tickinterval=25,
    **horiz_slider_arguments
)
slider_inner_sphere_mass.pack(**pack_left)
slider_inner_sphere_mass.set(4)

slider_outer_sphere_mass = Scale ( 
    frame,
    label="Mass 2 [M⊙]",
    variable=tkinter_outer_sphere_mass,
    from_=1, to=50,
    tickinterval=25,
    **horiz_slider_arguments
)
slider_outer_sphere_mass.pack(**pack_left)
slider_outer_sphere_mass.set(4)

# Create a frame for vertical scaling and smoothing
frame = Frame(root, bg="black")
frame.pack(**pack_top)   
slider_vertical_rescale = Scale ( 
    frame,
    label="Vertical Scale",
    variable=tkinter_vertical_rescale,
    from_=20, to=0,
    **vert_slider
)
slider_vertical_rescale.pack(**pack_left)
slider_vertical_rescale.set(10)
slider_smoothing_window_size = Scale (
    frame,
    label="Smoothing",
    variable=tkinter_smoothing_window_size,
    from_=25, to=0,
    resolution=2,
    **vert_slider
)  
slider_smoothing_window_size.pack(**pack_left)
slider_smoothing_window_size.set(11)

# Create a frame for vertical scaling and smoothing
frame = Frame(root, bg="black")
frame.pack(**pack_top)  
slider_camera_look_up_down = Scale ( 
    frame,
    label="Look u/d",
    variable=tkinter_camera_look_up_down,
    from_=2, to=-2, resolution=0.01,
    **vert_slider
)
slider_camera_look_up_down.pack(**pack_left)
slider_camera_look_up_down.set(0.0)
slider_camera_height = Scale (
    frame,
    label="Camera Height",
    variable=tkinter_camera_height,
    from_=2, to=-2, resolution=0.01,
    **vert_slider
)
slider_camera_height.pack(**pack_left)
slider_camera_height.set(1.0)

# Create a frame for the viewing position (camera point of view)
frame = Frame(root, bg="black")
frame.pack(**pack_top)  
slider_camera_left_right = Scale (
    frame,
    label="Camera L/R",
    variable=tkinter_camera_left_right,
    from_=1, to=-1, resolution=0.01,
    **horiz_slider_arguments
)
slider_camera_left_right.pack(**pack_left)
slider_camera_left_right.set(0)
slider_camera_forward_backward = Scale ( 
    frame,
    label="Camera B'wd/F'wd",
    variable=tkinter_camera_backward_forward,
    from_=-0.80, to=0.80, resolution=0.01,
    **horiz_slider_arguments
)
slider_camera_forward_backward.set(0.0)
slider_camera_forward_backward.pack(**pack_left)

# Create a resizeable chequerboard/"table cloth" colour pattern
frame = Frame(root, bg="black")
frame.pack(**pack_top)  
slider_grid_chequer_size = Scale ( 
    frame,
    label="Grid Chequer Size",
    variable=tkinter_grid_chequer_size,
    from_=0, to=100, resolution=1,
    **horiz_slider_arguments
)
slider_grid_chequer_size.pack(**pack_left)
slider_grid_chequer_size.set(0.0)
frame = Frame(root, bg="black")
frame.pack(side=TOP, fill=X, padx=padx, pady=pady) 

# Set the dropdown options for determining the type of run
run_option = StringVar()
run_option.set("Select an option")
options_list = ["Set outer sphere orbital radius",
                "Inspiralling",
                "Test run 1 - two of four borders damped",
                "Test run 2 - all four borders damped"]    
dropdown_run_option = OptionMenu(frame, 
                                 run_option, 
                                 *options_list)
dropdown_run_option.config(bg="light steel blue")
dropdown_run_option.pack(**pack_left)
frame = Frame(root, bg="black")
frame.pack(**pack_top)  

# Initialize the shared data (using a dictionary)
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
    'astro_binary_energy_loss_rate': 0.0,
    'astro_orbital_decay_rate': 0.0
} 

# Toggle the simulation thread 
def start_stop_simulation():
    with shared_data['lock']:
        if not shared_data['running']:  # Start the simulation
            shared_data['running'] = True  
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
            shared_data['running'] = False
            shared_data['simulation_thread'] = None
            root.after(0, close_info_window)
button_start_stop_simulation = Button(frame,
                                      width=25,
                                      text="START Simulation",
                                      command=start_stop_simulation,
                                      bg="light green")
button_start_stop_simulation.pack(padx=padx, pady=pady)  

# The command statement (pause_simulation) in the Button widget waits for user
# input (a clicking of the widget). During the pause, 

simulation_is_paused = Event()
def pause_simulation():
    if simulation_is_paused.is_set():
        simulation_is_paused.clear()
        button_pause_simulation.config(text="PAUSE", bg="light yellow")
    else:
        simulation_is_paused.set()
        button_pause_simulation.config(text="resume after pause", bg="yellow")
button_pause_simulation = Button(frame,
                                 width=25,
                                 text="PAUSE",
                                 bg="light yellow",
                                 command=pause_simulation)
button_pause_simulation.pack(padx=padx, pady=pady)    

def import_parameters_from_gui():
    """
    Retrieve parameters from the graphical user interface (GUI).

    This function retrieves various parameters from the graphical user 
    interface (GUI), including the grid size, the size of each chequer on the
    grid, the vertical rescaling factor, the number of spheres to display, 
    masses of the spheres, the orbital radius of the first sphere 
    (the orbital radius of the second one is computed based on this value), and
    camera positioning parameters. The returned values are assigned to the 
    respective variables in the order specified.

    Parameters:
    - outer_orbital_radius (float): The orbital radius of the first sphere.

    Returns (as a tuple):
        - outer_orbital_radius (float): Orbital radius of the first sphere 
              (the second one will be computed).
        - spheres_to_display (int): The number of spheres to display.
        - inner_sphere_mass (float): Mass of the first sphere.
        - outer_sphere_mass (float): Mass of the second sphere.
        - vertical_rescale (float): The vertical rescaling factor.
        - smoothing_window_size(int): The size for computing the average 
                                      position of a group of oscillators.
        - camera_look_up_down (float): Up-down position of the camera.
        - camera_height (float): Height of the camera.
        - camera_left_right (float): Left-right position of the camera.
        - camera_forward_backward (float): Forward-backward position of the 
              camera.
        - grid_chequer_size (int): The size of each chequer on the grid.
    """
    outer_orbital_radius   = tkinter_outer_orbital_radius.get()       
    spheres_to_display         = tkinter_spheres_to_display.get()
    inner_sphere_mass          = tkinter_inner_sphere_mass.get()
    outer_sphere_mass          = tkinter_outer_sphere_mass.get()
    vertical_rescale             = tkinter_vertical_rescale.get()
    smoothing_window_size        = tkinter_smoothing_window_size.get()
    camera_look_up_down          = tkinter_camera_look_up_down.get()
    camera_height                = tkinter_camera_height.get()
    camera_left_right            = tkinter_camera_left_right.get()
    camera_forward_backward      = tkinter_camera_backward_forward.get()
    grid_chequer_size            = tkinter_grid_chequer_size.get()
    return (outer_orbital_radius,
            spheres_to_display,
            inner_sphere_mass,
            outer_sphere_mass,
            vertical_rescale,
            smoothing_window_size,
            camera_look_up_down,
            camera_height,
            camera_left_right,
            camera_forward_backward,
            grid_chequer_size) 

# Function definitions for startup and main control ---------------------------

# Define and start the window for displaying the variables during the run.
def start_info_window(root, shared_data):
    info_window = Toplevel(root)
    info_window.attributes('-topmost', 1)
    info_window_width = screen_width // 5
    info_window_height = screen_height // 4
    info_window_x = screen_width - info_window_width
    info_window_y = screen_height - info_window_height
    info_window.geometry(
        f"{info_window_width}x{info_window_height}+{info_window_x}+{info_window_y}")
    info_window.resizable(False, False)
    info_window.overrideredirect(True)
    info_window.config(bg="black")
    
    # Define the window's labels without context, setting only the initial 
    # layout, without text or data. The latter will be added and updated 
    # during the mainloop run.
    
    # Function to create labels with common properties
    def create_label(window, text="", fg="white", bg="black"):
        label = Label(window, text=text, fg=fg, bg=bg)
        label.pack()
        return label
    blank_line_label = create_label(info_window, fg="black", bg="black")
    timer_label = create_label(info_window)
    fps_label = create_label(info_window)
    astro_orbital_separation_label = create_label(info_window)
    astro_outer_sphere_orbital_speed_label = create_label(info_window)
    astro_omega_label = create_label(info_window)
    model_omega_label = create_label(info_window)
    astro_binary_energy_loss_rate_label = create_label(info_window)
    astro_orbital_decay_rate_label = create_label(info_window)
    return (info_window, 
            blank_line_label,
            timer_label, 
            fps_label, 
            astro_orbital_separation_label,
            astro_outer_sphere_orbital_speed_label,
            astro_omega_label,
            model_omega_label,
            astro_binary_energy_loss_rate_label,
            astro_orbital_decay_rate_label)

# Update the info display window
def update_info_window(root, shared_data):
    if not shared_data['running']:
        return # Exit early if the simulation is not running
    
    # Update the information variables if the window is open and 
    # the main loop is running.
    (info_window,
     blank_line_label,
     timer_label, 
     fps_label, 
     astro_orbital_separation_label,
     astro_outer_sphere_orbital_speed_label,
     astro_omega_label,
     model_omega_label,
     astro_binary_energy_loss_rate_label,
     astro_orbital_decay_rate_label) = start_info_window(root, shared_data)
    
    with shared_data['lock']:
        # Refresh the variables using the shared data.
        elapsed_time = shared_data['elapsed_time'] 
        hours, remainder = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        current_fps = shared_data['fps']
        current_astro_orbital_separation = shared_data['astro_orbital_separation']
        current_astro_outer_sphere_orbital_speed = shared_data['astro_outer_sphere_orbital_speed']
        current_astro_omega = shared_data['astro_omega']
        current_model_omega = shared_data['model_omega']
        current_astro_binary_energy_loss_rate = shared_data['astro_binary_energy_loss_rate']
        current_astro_orbital_decay_rate = shared_data['astro_orbital_decay_rate']
  
    # Fill the window labels with their respective text and current data
    # values to be displayed. 
    timer_label.config(text=f"Elapsed Time: {int(hours):02}:{int(minutes):02}:{int(seconds):02}")
    fps_label.config(text=f"FPS: {current_fps:.2f}")
    if (run_option.get() == "Set outer sphere orbital radius" or
        run_option.get() == "Inspiralling"):
        astro_orbital_separation_label.config(
            text=f"Astro Orbital Separation: {current_astro_orbital_separation:.2e} m"
        )
        astro_outer_sphere_orbital_speed_label.config(
            text=f"Astro Outer Sphere Orbital Speed: {current_astro_outer_sphere_orbital_speed:.2e} m/s"
        )  
        astro_omega_label.config(text=f"Astro Ω: {current_astro_omega:.2e} rad/s")
        model_omega_label.config(text=f"Model Ω: {current_model_omega:.2e} rad/s")
        astro_binary_energy_loss_rate_label.config(
            text=f"Astro Binary Energy Loss Rate: {current_astro_binary_energy_loss_rate:.2e} W"
        )
        astro_orbital_decay_rate_label.config(
            text=f"Astro Orbital Decay: {current_astro_orbital_decay_rate:.2e} m/s"
        )
    else:    
        astro_orbital_separation_label.config(text = "", fg="black", bg="black") 
        astro_outer_sphere_orbital_speed_label.config(text = "", fg="black", bg="black")
        astro_omega_label.config(text = "", fg="black", bg="black")
        model_omega_label.config(text = "", fg="black", bg="black")
        astro_binary_energy_loss_rate_label.config(text = "", fg="black", bg="black")
        astro_orbital_decay_rate_label.config(text = "", fg="black", bg="black")          

    root.after(500, update_info_window, root, shared_data)    
   
# Close the information display window at the end of a run.
def close_info_window():
    for window in root.winfo_children():
        if isinstance(window, Toplevel):
            window.destroy()
 
def create_taichi_window(fullscreen_width,
                         fullscreen_height):
    window = ti.ui.Window(name="Surface",
                          res=(int(fullscreen_width * 0.8), fullscreen_height),
                          pos=(int(fullscreen_width * 0.2), 0),
                          show_window=True,
                          vsync=True)
    return window

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
    for current_core, percentage in enumerate(cpu_percent
                                              (percpu=True, interval=1)):
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

@ti.kernel
def initialise_vector_array(array_to_be_initialised: ti.template(),
                            grid_size: ti.i32): 
    """
    Initialize a 2D vector array generically with specified grid size.
    
    This function initializes each element of a 2D vector array with predefined values:
    - The first component (index 0) is set to the row index (i).
    - The second component (index 1) is set to 0.0.
    - The third component (index 2) is set to the column index (j).
    
    Args:
        array_to_be_initialised (ti.template()): A Taichi array structure
            that will be initialized. It is a 2D array where each element is a
            vector with three components.
        grid_size (ti.i32): The size of the grid (number of rows and columns) for the
            2D vector array.
    
    Returns:
        None: This function modifies the array in-place and does not return any value.
    """
    for i in range (grid_size):
        for j in range (grid_size):
            array_to_be_initialised[i, j][0] = i
            array_to_be_initialised[i, j][1] = 0.0
            array_to_be_initialised[i, j][2] = j   

@ti.kernel
def increment_polar_angle(initial_outer_orbital_radius: ti.f64,
                          outer_orbital_radius: ti.f64,
                          previous_polar_angle: ti.f64,
                          sphere_angular_stepsize: ti.f64) -> ti.f64:
    """
    Increments the polar angle for the first orbiting sphere. 
    
    Args:
        current_polar_angle (ti.f64): The current polar angle of the sphere's 
            orbit (in degrees).
        sphere_angular_stepsize (ti.f64): The step size, for incrementing the
            polar angle (in degrees).
        outer_orbital_radius (ti.f64): The current orbital radius of the 
            sphere.
        initial_outer_orbital_radius (ti.f64): The orbital radius of the 
            first sphere at the start of the simulation. 
    
    Returns:
        ti.f64: The updated polar angle after incrementing.
    """
    return ((previous_polar_angle 
             + sphere_angular_stepsize 
             * (outer_orbital_radius / initial_outer_orbital_radius) ** -3/2) 
            % 360)

@ti.kernel
def calculate_orbital_coords(grid_centre: ti.template(),
                             sphere_orbital_radius: ti.f64,
                             sphere_polar_angle: ti.f64,
                             orbital_coords: ti.template()):
    """
    Calculates the coordinates of a sphere on the surface based on its orbital
    parameters.
    
    Args:
        grid_centre (ti.template): The coordinates of the grid centre.
        sphere_orbital_radius (ti.f64): The orbital radius of the sphere.
        sphere_polar_angle (ti.f64): The polar angle of the sphere's orbit.
        orbital_coords (ti.template): Template for storing the calculated sphere coordinates.
    
    Returns:
        None: The calculated sphere coordinates are stored in the orbital_coords template.
    """
    angle_rad = ti.math.radians(sphere_polar_angle)
    x_offset = sphere_orbital_radius * ti.cos(angle_rad)
    z_offset = sphere_orbital_radius * ti.sin(angle_rad)
    orbital_coords[None] = ti.Vector([grid_centre[None][0] + x_offset, 
                                      0.0, 
                                      grid_centre[None][2] + z_offset])

@ti.kernel
def calculate_model_omega(previous_polar_angle: ti.f64,
                          current_polar_angle: ti.f64,
                          loop_duration: ti.f64) -> ti.f64:
    """
    Calculate the angular velocity (omega) based on current polar angle.
    
    This function computes the angular velocity by determining the change in 
    polar angle over a specified time duration and converting the result
    from degrees per unit time to radians per unit time.
    
    Args:
        current_polar_angle (ti.f64): The current polar angle in degrees.
        previous_polar_angle (ti.f64): The previous polar angle in degrees.
        loop_duration (ti.f64): The time duration over which the angle change occurred.
    
    Returns:
        ti.f64: The angular velocity in radians per unit time.
    """
    polar_angle_increment = current_polar_angle - previous_polar_angle   
    return polar_angle_increment/loop_duration * ti.math.pi/180 # convert to radians

@ti.kernel
def separation_distance(first_coordinate_point: ti.template(),
                        second_coordinate_point: ti.template()) -> ti.f64:
    return (first_coordinate_point[None] - second_coordinate_point[None]).norm() 

@ti.kernel
def convert_to_astro_distance(model_distance: ti.f64,
                              astro_length_scaling: ti.f64) -> ti.f64:
    return model_distance * astro_length_scaling 

@ti.kernel
def calculate_astro_omega(a: ti.f64,
                          G: ti.f64,
                          astro_summed_masses: ti.f64) -> ti.f64:
    return ti.math.sqrt (G * astro_summed_masses/(a * a * a))
   
@ti.kernel
def compute_binary_energy_loss_rate(binary_energy_loss_rate_factor: ti.f64,
                                    astro_orbital_separation: ti.f64,
                                    astro_omega: ti.f64) -> ti.f64:
    return (binary_energy_loss_rate_factor 
            * astro_orbital_separation ** 4 
            * astro_omega ** 6)   
   
@ti.kernel
def compute_astro_orbital_decay_rate(astro_orbital_separation: ti.f64,
                                     outer_sphere_mass: ti.f64,
                                     inner_sphere_mass: ti.f64,
                                     orbital_decay_factor: ti.f64) -> ti.f64: 
    """
    Calculate the rate of orbital decay for a system based on astro 
    parameters.
    
    This function computes the real physical rate of orbital decay using 
    the orbital separation on the grid and converts it to a real physical scale 
    based on a length scaling factor and the two sphere's physical masses. 
    The result is adjusted to reflect the orbital decay rate (shrinkage) 
    per unit time.
    
    Args:
        model_orbital_separation (ti.f64): The model orbital separation distance
            (in grid element units).
        astro_length_scaling (ti.f64): Scaling factor to convert 
            model units to physical units.
        outer_sphere_mass (ti.f64): Mass of the outer sphere (e.g., in solar masses).
        inner_sphere_mass (ti.f64): Mass of the inner sphere (e.g., in solar masses).
        orbital_decay_factor (ti.f64): A factor representing the strength of 
            orbital decay.
        loop_duration (ti.f64): Time duration over which the current decay is calculated.

    Returns:
        ti.f64: The rate of orbital decay per unit time, in physical units.
    """
    astro_orbital_decay_rate = (orbital_decay_factor 
                                * outer_sphere_mass
                                * inner_sphere_mass)
    astro_orbital_decay_rate *= (outer_sphere_mass + inner_sphere_mass
                                 )/(astro_orbital_separation ** 3)
    return astro_orbital_decay_rate  
 
@ti.kernel
def create_gaussian_perturb_array(perturb_radius: ti.i32, 
                                  perturb_max_depth: ti.f64,
                                  perturb_array: ti.template()):
    """
    Creates a 2D array containing the vertical positions of an axially symmetric,
    inverted Gaussian distribution.  
    
    Args:
        perturb_radius (ti.i32): The radius of the (circular) perturbation area.
        perturb_max_depth (ti.f64): The maximum depth of the perturbation (at
        the centre of the array).
        perturb_array (ti.template): Template for storing the perturbation array.
    
    Returns:
        None: The perturbation array is stored in the perturb_array template.
    """
    for index_x, index_y in ti.ndrange((-perturb_radius, perturb_radius + 1),
                                       (-perturb_radius, perturb_radius + 1)):
        distance_sq = index_x * index_x + index_y * index_y
        temp1 = index_x + perturb_radius
        temp2 = index_y + perturb_radius
        if distance_sq <= perturb_radius * perturb_radius:
            perturb_depth = -ti.exp(-((2 * index_x / perturb_radius) ** 2 
                                    + (2 * index_y / perturb_radius) ** 2)) * perturb_max_depth
            perturb_array[temp1, temp2] = perturb_depth
        else:
            perturb_array[temp1, temp2] = 0.0 
   
@ti.kernel
def overlay_perturb_shape_onto_grid(perturb_radius: ti.i32, 
                                    perturb_array: ti.template(), 
                                    orbital_coords: ti.template(),
                                    oscillator_positions: ti.template(),
                                    oscillator_velocities: ti.template()):
    for offset_x in range(-perturb_radius, perturb_radius + 1):
        for offset_y in range(-perturb_radius, perturb_radius + 1):
            absolute_coords_x = int(orbital_coords[None][0] + offset_x)
            absolute_coords_y = int(orbital_coords[None][2] + offset_y)
            # Compute model_orbital_separation from the center of the perturb
            distance_squared = (offset_x * offset_x + offset_y * offset_y) 
            # Check if the current position is within the perturb radius
            if (distance_squared <=
                perturb_radius * perturb_radius):
                # Ensure we are inside the perturbation horizontal radius.
                perturb_depth = perturb_array[perturb_radius + offset_x,
                                              perturb_radius + offset_y]
                oscillator_depth = oscillator_positions[absolute_coords_x, 
                                                        absolute_coords_y][1]
                # This important statement ensures that the oscillators at the
                # tail end of the perturbation are not "pulled up" but relax
                # according to the sheet iteration method.
                if perturb_depth < oscillator_depth:
                    oscillator_positions[absolute_coords_x, 
                                         absolute_coords_y][1] = perturb_depth
                    oscillator_velocities[absolute_coords_x, 
                                          absolute_coords_y][1] = 0.0
                          
@ti.func
def oscillator_is_inside_perturb_zone(i: ti.i32, 
                                      j: ti.i32,
                                      orbital_coords: ti.template(),
                                      perturb_radius: ti.f64) -> ti.i32:
    """
    Check if the oscillator at (i, j) is inside the perturbation zone.

    Args:
        i (ti.i32): The x-coordinate of the oscillator.
        j (ti.i32): The y-coordinate of the oscillator.
        orbital_coords (ti.template): The coordinates of the sphere centre, 
            expected to be a Taichi field with 3D coordinates.
        perturb_radius (ti.f64): The radius of the perturbation zone.

    Returns:
        bool: True if inside the perturbation zone, False otherwise.
    """
    delta = ti.Vector([i - orbital_coords[None][0],
                       j - orbital_coords[None][2]])
    return ti.cast(delta.norm_sqr() < perturb_radius * perturb_radius, ti.i32)

"""@ti.kernel
def set_perturb_oscillator_velocities_to_zero(perturb_radius: ti.i32,
                                              orbital_coords: ti.template(),
                                              oscillator_velocities: ti.template()):
     
    Set oscillator velocities to zero within the a perturb_radius around orbital_coords.

    Args:
        perturb_radius (ti.i32): The radius of the perturbation.
        orbital_coords (ti.template): Template for the coordinates of the sphere.
        oscillator_velocities (ti.template): Template for the velocities of oscillators.
    
    for offset_x, offset_y in ti.ndrange((-perturb_radius, perturb_radius + 1),
                                         (-perturb_radius, perturb_radius + 1)):
        absolute_coords_x = int(orbital_coords[None][0]) + offset_x
        absolute_coords_y = int(orbital_coords[None][2]) + offset_y
        if (0 <= absolute_coords_x < oscillator_velocities.shape[0] and 
            0 <= absolute_coords_y < oscillator_velocities.shape[1]):
            oscillator_velocities[absolute_coords_x, 
                                  absolute_coords_y] = ti.Vector.zero(ti.f64, 3)
"""
@ti.kernel
def update_oscillator_positions_velocities_RK4(effective_grid_start: ti.i32,
                                               effective_grid_end: ti.i32,
                                               elastic_constant: ti.f64,
                                               oscillator_initial_extension: ti.f64,
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
    a 2D grid based on the RK4 integration method. The update is performed over
    a specified grid range, taking into account the elastic properties of the sheet
    and masses of the oscillators.
    
    Args:
        effective_grid_start (ti.i32): The starting index of the grid 
            to be updated (inclusive).
        effective_grid_end (ti.i32): The ending index of the grid to be updated 
            (exclusive).
        elastic_constant (ti.f64): The elastic constant for the oscillators' 
            restoring force.
        oscillator_initial_extension (ti.f64): The initial extension of 
            the oscillators from their equilibrium position.
        oscillator_mass (ti.f64): The mass of the oscillators.
        adjacent_grid_elements (ti.template()): Taichi Field containing 
            information about adjacent grid elements for calculating the
            interactions between the oscillators.
        oscillator_positions (ti.template()): Taichi field holding current 
            positions of the oscillators.
        oscillator_velocities (ti.template()): Taichi field holding current 
            velocities of the oscillators.
        oscillator_accelerations (ti.template()): Taichi field holding  
            current accelerations of the oscillators.
        timestep (ti.f64): The time step for each RK4 iteration.
    
    Returns:
        None: This function updates the `oscillator_positions` and 
        `oscillator_velocities` fields in-place and does not return any value.
    """
    for i in range (effective_grid_start, effective_grid_end):
        for j in range (effective_grid_start, effective_grid_end):   
            vel = oscillator_velocities[i, j]
            pos = oscillator_positions[i, j]
            k1 = timestep * vel
            l1 = timestep * update_oscillator_accelerations(i, j,
                                                            adjacent_grid_elements,
                                                            oscillator_positions,
                                                            pos,
                                                            elastic_constant,
                                                            oscillator_initial_extension,
                                                            oscillator_mass)
            k2 = timestep * (vel + 0.5 * l1)
            l2 = timestep * update_oscillator_accelerations(i, j,
                                                            adjacent_grid_elements,
                                                            oscillator_positions,
                                                            pos + 0.5 * k1,
                                                            elastic_constant,
                                                            oscillator_initial_extension,
                                                            oscillator_mass)
            k3 = timestep * (vel + 0.5 * l2)
            l3 = timestep * update_oscillator_accelerations(i, j,
                                                            adjacent_grid_elements,
                                                            oscillator_positions,
                                                            pos + 0.5 * k2,
                                                            elastic_constant,
                                                            oscillator_initial_extension,
                                                            oscillator_mass)
            k4 = timestep * (vel + l3)
            l4 = timestep * update_oscillator_accelerations(i, j,
                                                            adjacent_grid_elements,
                                                            oscillator_positions,
                                                            pos + k3,
                                                            elastic_constant,
                                                            oscillator_initial_extension,
                                                            oscillator_mass)
            # Update velocities first, which then affects the position update.
            oscillator_velocities[i, j] += (l1 + 2 * l2 + 2 * l3 + l4) / 6.0 
            oscillator_positions[i, j] += (k1 + 2 * k2 + 2 * k3 + k4) / 6.0

@ti.func
def update_oscillator_accelerations(i, j,
                                    adjacent_grid_elements,
                                    oscillator_positions,
                                    pos,
                                    elastic_constant,
                                    oscillator_initial_extension,
                                    oscillator_mass):
    """
    Calculate the acceleration of an oscillator based on interactions with 
    adjacent grid elements.
    
    This function computes the accelerations of the oscillators. This is done by    
    considering the forces on each one exerted by its neighboring oscillators. 
    Hooke's law is used to to compute the forces and the acceleration are 
    updated using Newton's second law.
    
    Args:
        i (int): The row index of the current oscillator in the grid.
        j (int): The column index of the current oscillator in the grid.
        adjacent_grid_elements (ti.template()): Taichi field containing 
        offsets of adjacent grid elements. Each
            entry specifies the relative position of a neighboring oscillator.
        oscillator_positions (ti.template()): Taichi field containing 
            current positions of all oscillators in the grid.
        pos (ti.Vector): Current position of the oscillator at index `(i, j)`.
        elastic_constant (ti.f64): The elastic constant that governs the force 
            exerted by the springs between oscillators.
        oscillator_initial_extension (ti.f64): The initial extension of 
            the oscillators from their equilibrium positions.
        oscillator_mass (ti.f64): The mass of the oscillator.
    
    Returns:
        ti.Vector: The computed acceleration of the oscillator at position `(i, j)`,
        given by Newton's second law `F = ma`, where `F` is the net force
        and `m` is the mass of the oscillator. 
        All oscillators have identical masses.
    """
    force = ti.Vector.zero(ti.f64, 3)
    for count in range(adjacent_grid_elements.shape[0]):
        offset_i = adjacent_grid_elements[count, 0] 
        offset_j = adjacent_grid_elements[count, 1]
        k, l = i + offset_i, j + offset_j
        displacement_vector = pos - oscillator_positions[k, l]
        euclidean_norm = displacement_vector.norm()
        unit_vector = displacement_vector.normalized()
        force -= (elastic_constant * (oscillator_initial_extension + 1.0) 
                  * euclidean_norm * unit_vector)
        force += elastic_constant * unit_vector
    return force / oscillator_mass  # Newton's second law: F = ma

@ti.kernel
def total_energy_of_sheet(grid_size: ti.i32,
                      elastic_constant: ti.f64,
                      oscillator_positions: ti.template(),
                      oscillator_mass: ti.f64,
                      oscillator_velocities: ti.template()) -> ti.f64:
    """
    Calculate the total energy of the grid: potential and kinetic energy.
    
    This function computes the total energy of a grid of oscillators by 
    summing up the potential and kinetic energy for each oscillator. 
    The potential energy is calculated based on the elastic constant and 
    the vertical displacement of each oscillator; the kinetic energy is deterined 
    based on the mass and velocity of each oscillator. The total energy 
    is then scaled down (arbitrarily) by a factor of 10**9.
    
    Args:
        grid_size (ti.i32): The size of the grid.
        elastic_constant (ti.f64): The elastic constant.
        oscillator_positions (ti.template()): Taichi field containing 
            the positions of the oscillators, where the vertical component is used 
            for the potential energy calculation.
        oscillator_mass (ti.f64): The mass of each oscillator, used to 
            calculate the kinetic energy.
        oscillator_velocities (ti.template()): Taichi field containing the 
            velocities of the oscillators, where the vertical component 
            is used for kinetic energy calculation.
    
    Returns:
        ti.f64: The total energy of the grid, which is the sum of potential and kinetic energy, divided by 1e9.
    """
    total_potential_energy = 0.0
    total_kinetic_energy = 0.0
    for i, j in ti.ndrange(grid_size, grid_size):
        total_potential_energy += (0.5 * elastic_constant 
                                   * oscillator_positions [i,j][1]
                                   * oscillator_positions [i,j][1])        
        total_kinetic_energy += (0.5 * oscillator_mass 
                                 * oscillator_velocities [i,j][1]
                                 * oscillator_velocities [i,j][1])
    return (total_potential_energy + total_kinetic_energy) / 1e9

# Rescaling for rendering with Taichi
@ti.kernel
def rescale_rendered_orbital_coords(rendering_rescale: ti.f64,
                                    orbital_coords: ti.template(),
                                    rendered_orbital_coords: ti.template()):
    """
    Rescale sphere coordinates for rendering.

    Args:
        rendering_rescale (ti.f64): The scaling factor for rendering.
        orbital_coords (ti.template()): Template for the original sphere coordinates.
        rendered_orbital_coords (ti.template()): Template for the 
        rescaled sphere coordinates for rendering.
    """    
    rendered_orbital_coords[0] = ti.Vector([
                                    orbital_coords[None][0] * rendering_rescale,
                                    0.0,
                                    orbital_coords[None][2] * rendering_rescale
                                    ])
    
@ti.kernel
def damp_grid_boundary(number_of_damped_borders: ti.i32, 
                       effective_grid_start: ti.i32,
                       effective_grid_end: ti.i32,
                       damped_grid_boundary_depth: ti.i32,
                       boundary_damping_factor: ti.f64,
                       oscillator_velocities: ti.template(),
                       oscillator_positions: ti.template()):
    """
    Apply damping to oscillator velocities and positions near the boundaries of the grid.
    
    The damping effect reduces the velocities and positions of the oscillators 
    in the specified boundary regions, with the intensity of damping increasing 
    as the boundary is approached. 
    
    Args:
        number_of_damped_borders (ti.i32): The number of borders to apply damping to. 
        effective_grid_start (ti.i32): The starting index of the grid to which 
            damping should be applied (inclusive).
        effective_grid_end (ti.i32): The ending index of the grid to which 
            damping should be applied (exclusive).
        damped_grid_boundary_depth (ti.i32): The number of grid cells from 
            the boundary where damping should start.
        boundary_damping_factor (ti.f64): The maximum damping factor applied 
            at the boundary. The damping decreases linearly from this factor 
            towards zero as it moves away from the boundary.
        oscillator_velocities (ti.template()): Taichi field containing 
            the current velocities of the oscillators.
        oscillator_positions (ti.template()): Taichi field containing 
            the current positions of the oscillators. The damping is applied 
            to the second (vertical) component of the positions.
    
    Returns:
        None: This function modifies the `oscillator_velocities` 
        and `oscillator_positions` fields in-place and does not return any value.
        """

    lower_damping_end_pos   = effective_grid_start + damped_grid_boundary_depth
    upper_damping_start_pos = effective_grid_end   - damped_grid_boundary_depth
    
    if number_of_damped_borders == 4:
        for i in range (effective_grid_start, effective_grid_end): 
            if i < lower_damping_end_pos:
                damping_factor_for_this_layer = (boundary_damping_factor  
                                                 * (lower_damping_end_pos - i) 
                                                 / damped_grid_boundary_depth)
                for j in range (effective_grid_start, effective_grid_end):
                    oscillator_velocities[i, j] *= (1 - damping_factor_for_this_layer) 
                    oscillator_positions[i, j][1] *= (1 - damping_factor_for_this_layer) 
                        
            elif i >= upper_damping_start_pos:
                damping_factor_for_this_layer = (boundary_damping_factor 
                                                 * (i - upper_damping_start_pos) 
                                                 / damped_grid_boundary_depth)
                for j in range (effective_grid_start, effective_grid_end):
                    oscillator_velocities[i, j] *= (1 - damping_factor_for_this_layer)
                    oscillator_positions[i, j][1] *= (1 - damping_factor_for_this_layer)
                    
    for i in range (lower_damping_end_pos, upper_damping_start_pos): 
        for j in range (effective_grid_start, lower_damping_end_pos):
            damping_factor_for_this_layer = (boundary_damping_factor  
                                             * (lower_damping_end_pos - j) 
                                             / damped_grid_boundary_depth)
            oscillator_velocities[i, j] *= (1 - damping_factor_for_this_layer)
            oscillator_positions[i, j][1] *= (1 - damping_factor_for_this_layer)
            
        for j in range (upper_damping_start_pos, effective_grid_end):
            damping_factor_for_this_layer = (boundary_damping_factor  
                                             * (j - upper_damping_start_pos) 
                                             / damped_grid_boundary_depth)            
            oscillator_velocities[i, j] *= (1 - damping_factor_for_this_layer)
            oscillator_positions[i, j][1] *= (1 - damping_factor_for_this_layer)

@ti.kernel
def rescale_oscillator_heights(grid_size: ti.i32,
                               vertical_rescale: ti.f64,
                               oscillator_positions: ti.template(),
                               height_rescaled_oscillator_positions: ti.template()):
    """
    Rescale the vertical height component of oscillator positions.
    
    This function adjusts the vertical component (y-coordinate) of each 
    oscillator's position in the grid by applying a scaling factor. 
    The horizontal (x) and depth (z) components of the positions remain unchanged. 
    The scaled positions are stored in a new Taichi field.
    
    Args:
        grid_size (ti.i32): The size of the grid, assuming a square grid 
            of `grid_size` x `grid_size`.
        vertical_rescale (ti.f64): The scaling factor to apply to 
            the vertical (y) component of each oscillator's position.
        oscillator_positions (ti.template()): Taichi field containing 
            the original positions of the oscillators.
        height_rescaled_oscillator_positions (ti.template()): Taichi field 
            where the height-rescaled positions will be stored.
    
    Returns:
        None: This function updates the `height_rescaled_oscillator_positions` 
            field in-place and does not return any value.
    """
    for i in range (grid_size):
        for j in range (grid_size):
            height_rescaled_oscillator_positions[i, j] = ti.Vector([
                oscillator_positions[i, j][0],
                oscillator_positions[i, j][1] * vertical_rescale,
                oscillator_positions[i, j][2]
            ])

@ti.kernel
def smooth_the_surface(grid_size: ti.i32, 
                       smoothing_start_pos: ti.i32, 
                       smoothing_end_pos: ti.i32,
                       smoothing_window_size: ti.i32,
                       smoothed_cell_position: ti.template(), 
                       height_rescaled_oscillator_positions: ti.template(),
                       smoothed_oscillator_positions: ti.template()):
    
    """
    Smooth the vertical component of oscillator positions within a specified region of the grid.

    This function applies a smoothing operation to the vertical component (height) of
    the oscillator positions within a defined rectangular subregion of the grid. 
    The smoothing is performed using a window-based approach, where each position
    in the region is adjusted based by taking an average of it and its 
    neighboring cells within the specified window size. 

    Args:
        grid_size (ti.i32): The size of the grid.
        smoothing_start_pos (ti.i32): The starting index of the region to apply 
            smoothing (inclusive).
        smoothing_end_pos (ti.i32): The ending index of the region to apply 
            smoothing (inclusive).
        smoothing_window_size (ti.i32): The size of the window used for smoothing. 
            Determines the extent of neighboring positions considered in 
            the calculation.
        smoothed_cell_position (ti.template()): Taichi field used to 
            temporarily store the current cell's position.
        height_rescaled_oscillator_positions (ti.template()): Taichi field 
            containing the vertical component-rescaled positions of the oscillators. 
        smoothed_oscillator_positions (ti.template()): Taichi field storing  
            the smoothed oscillator positions. 

    Returns:
        None: This function updates the `smoothed_oscillator_positions` field in-place and does not return any value.
    """
    for i in range(grid_size):
        for j in range(grid_size):
            smoothed_oscillator_positions [i, j][0] = height_rescaled_oscillator_positions[i, j][0]
            smoothed_oscillator_positions [i, j][2] = height_rescaled_oscillator_positions[i, j][2]
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
                    height_rescaled_oscillator_positions)
            else:
                smoothed_oscillator_positions [i, j][1] = height_rescaled_oscillator_positions[i, j][1]

@ti.func
def smooth_each_cell(smoothing_start_pos, 
                     smoothing_end_pos,
                     smoothing_window_size,
                     smoothed_cell_position, 
                     height_rescaled_oscillator_positions) -> ti.f64:
    """
    Calculate the smoothed vertical component for a single cell based on the 
    values of its neighbours.

    This function, operating with the kernel function smooth_the_surface, 
    computes the average vertical height of oscillators within 
    a smoothing window centered on the specified oscillator position. 
    The window size is "clamped" between 3 and 15. 
    The function returns the average vertical position of oscillators within 
    the window which is then used as the new vertical position of the
    secified oscillator.

    Args:
        smoothing_start_pos (ti.i32): Starting index of the smoothing region (inclusive).
        smoothing_end_pos (ti.i32): Ending index of the smoothing region (inclusive).
        smoothing_window_size (ti.i32): Size of the window used for smoothing. 
        smoothed_cell_position (ti.template()): Taichi field containing 
            the position of the oscillator height being smoothed. 
        height_rescaled_oscillator_positions (ti.template()): Taichi field 
            containing the vertically rescaled positions of the oscillators.

    Returns:
        ti.f64: The average vertical height of oscillators within the smoothing window.
    """
            
    cumulative_sum = 0.0
    for i in range(ti.max(smoothed_cell_position[None][0] - smoothing_window_size//2, 
                          smoothing_start_pos), 
                   ti.min(smoothed_cell_position[None][0] + smoothing_window_size//2 + 1,
                          smoothing_end_pos)):
        for j in range(ti.max(smoothed_cell_position[None][1] - smoothing_window_size//2,
                              smoothing_start_pos),
                       ti.min(smoothed_cell_position[None][1] + smoothing_window_size//2 + 1,
                              smoothing_end_pos)):
            cumulative_sum += height_rescaled_oscillator_positions[i, j][1]       
    return cumulative_sum/(smoothing_window_size * smoothing_window_size)

@ti.kernel
def create_grid_surface(grid_size: ti.i32, 
                        smoothing_window_size: ti.i32,
                        smoothed_oscillator_positions: ti.template(),
                        height_rescaled_oscillator_positions: ti.template(),
                        grid_surface: ti.template()):
    """
    Create the surface to be rendered.

    This function generates a grid surface representation by selecting between two types of oscillator positions:
    1. Smoothed positions, if the smoothing window size is greater than 2.
    2. Height-rescaled positions, if the smoothing window size is 2 or less.

    Args:
        grid_size (ti.i32): The size of the grid.
        smoothing_window_size (ti.i32): The size of the smoothing window. 
        smoothed_oscillator_positions (ti.template()): Taichi field containing 
            the smoothed positions of oscillators.
        height_rescaled_oscillator_positions (ti.template()): Taichi field 
            containing the height-rescaled positions of oscillators.
        grid_surface (ti.template()): Taichi field to store the resulting grid surface
         The surface is then populated with either smoothed or original non-smoothed 
             oscillator positions, depending on the user unput in the GUI.
    
    Returns:
        None: This function updates the `grid_surface` field in-place and does not return any value.
    """   
    if smoothing_window_size > 2:
        for i in range (grid_size):
            for j in range (grid_size):
                grid_surface[i,j] = smoothed_oscillator_positions[i,j]
    else:  
        for i in range (grid_size):
            for j in range (grid_size):
                grid_surface[i,j] = height_rescaled_oscillator_positions[i,j]

@ti.kernel
def rescale_grid_for_rendering(grid_size: ti.i32, 
                               grid_rescale_for_rendering: ti.f64,
                               grid_surface: ti.template(),
                               grid_for_rendering: ti.template()):    
    """
    The vectors of the oscillators representing the grid surface are rescaled
    for rendering by Taichi. The rescaling is necessary because Taichi regards
    the 3D region it renders in the animation as a 1 x 1 x 1 cube.
    """
    for i in range (grid_size):
        for j in range (grid_size):
            grid_for_rendering[i,j] = grid_surface[i,j] * grid_rescale_for_rendering

def color_longname_to_RGB(color_name,
                          rgb_color_normalized,
                          complementary_rgb_color_normalized):
    """
    Convert a color name to its RGB representation and compute its 
    complementary color. This will be used for the colour(s) of the rendered
    surface.

    Given a color name, this function converts it to its RGB representation
    using the Matplotlib `to_rgb` function. It then calculates the complementary
    colour by subtracting each RGB component from 1.0. The RGB colour and its
    complementary colour are returned as tuples.

    Args:
        color_name (str): The name of the colour to convert.
        rgb_color_normalized (list): List to store the normalized RGB values of the color.
        complementary_rgb_color_normalized (list): List to store the normalized RGB values
            of the complementary color.

    Returns:
        tuple: A tuple containing two lists:
            - The RGB color represented as normalized values.
            - The complementary RGB color represented as normalized values.
    """    
    rgb_color_normalized = mcolors.to_rgb(color_name)
    for i in range(3):
        complementary_rgb_color_normalized[i] = 1.0 - rgb_color_normalized[i]
    rgb_color_normalized = list(rgb_color_normalized)
    return rgb_color_normalized, complementary_rgb_color_normalized

@ti.kernel
def set_grid_colors(grid_size: ti.i32,
                    grid_chequer_size: ti.i32,
                    rgb_color_normalized: ti.template(),
                    complementary_rgb_color_normalized: ti.template(),
                    grid_colors: ti.template()):
    """
    Set colors for a grid with a chequered (chessboard-style) pattern. This can
    also be done during the run, to give an aesthetically more pleasing
    visualisation.
    
    Args:
        grid_size (ti.i32): The size of the grid.
        grid_chequer_size (ti.i32): The size of each chequer on the grid.
        rgb_color_normalized (ti.template()): Template for the normalized RGB color.
        complementary_rgb_color_normalized (ti.template()): Template for the
            complementary normalized RGB color.
        grid_colors (ti.template()): Template for the grid colors.
    """
    if grid_chequer_size == 0:
        for i, j in ti.ndrange(grid_size, grid_size):
            grid_colors[i * grid_size + j] = rgb_color_normalized
    else: 
        for i, j in ti.ndrange(grid_size, grid_size):
            if (i // grid_chequer_size + j // grid_chequer_size) % 2 == 0:
                grid_colors[i * grid_size + j] = rgb_color_normalized
            else:
                grid_colors[i * grid_size + j] = complementary_rgb_color_normalized

@ti.kernel
def set_indices(grid_size: ti.i32,
                indices: ti.template()):
    """
    Set triangle indices for constructing the grid surface. This function is 
    executed at the beginning of the run, only once, because the indices do
    not change even when the form of the surface does.

    Args:
        grid_size (ti.i32): The size of the grid.
        indices (ti.template()): Template for the triangle indices.
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
def set_triangle_vertices(grid_size: ti.i32,
                          grid_surface: ti.template(),
                          vertices: ti.template()):
    """
    Set triangle vertices from oscillator positions. This is called for each
    frame of the simulation.

    Args:
        grid_size (ti.i32): The size of the grid.
        oscillator_positions (ti.template()): Template for the positions of the oscillators.
        triangle_vertices (ti.template()): Template for the triangle vertices.
    """
    for i, j in ti.ndrange(grid_size, grid_size):
            vertices[i * grid_size + j] = grid_surface[i, j]

def mainline_code(shared_data):
    #--------------------------------------------------------------------------
    # Mainline code for simulating the dynamics and emitted gravitational 
    #   waves for two orbiting spheres in space.
    #--------------------------------------------------------------------------
    # The simulation includes the following steps:
    #    
    # 1. Initialize simulation parameters and variables.
    # 2. While the window is open and simulation is running:
    #    a. Update parameters based on user input via the GUI.
    #    b. Simulate the orbital motion of the two spheres.
    #    c. Apply perturbations, which represent gravitational wells, 
    #       based on the sphere positions.
    #    d. Compute surface properties and boundary damping of the grid.
    #    e. Render the spheres and grid surface.
    #    f. Adjust camera viewpoint and lighting for visualization.
    #    g. Display the scene in the window.
    #    h. Repeat steps a-g until simulation is paused or window is closed.
    # 3. If spheres have merged:
    #    a. Render the merged sphere with adjusted properties.
    # 4. Set grid colors and triangle vertices for rendering.
    # 5. Render the grid surface using the triangles.
    # 6. Update camera position and orientation for the next frame, if these
    #       are changed by the user in the GUI during the run.
    # 7. Show the rendered scene in the window.
    # 8. Repeat steps 2-7 until simulation is stopped or window is closed.    
    #--------------------------------------------------------------------------

    ti.init(arch=ti.cuda, 
            kernel_profiler=True)  # Force Taichi to use GPU (if available)
    
    show_system_information()


    prev_time_stamp = time.time()
    # Global Constants and Configuration Variables
    
    (outer_orbital_radius, # second radius will be computed from this, using the two
                           # relative masses.
     spheres_to_display,
     inner_sphere_mass,
     outer_sphere_mass,
     vertical_rescale,
     smoothing_window_size,
     camera_look_up_down,
     camera_height,
     camera_left_right,
     camera_forward_backward,
     grid_chequer_size) = import_parameters_from_gui()

    initial_outer_orbital_radius = outer_orbital_radius
    ###########################################################################
    # Initialisations of those variables that aren't set in the GUI
    ###########################################################################
    vector_parameters = {
        "n": 3,
        "dtype": ti.f64,
        "shape": ()
    }
    outer_orbital_coords = ti.Vector.field(**vector_parameters)
    inner_orbital_coords = ti.Vector.field(**vector_parameters)
    

    
    ########################################################################### 
    # Grey out fields that cannot be updated by the user during the run -------
    ###########################################################################
    greyed_out_slider = {
        "state": "disabled",
        "fg": "grey",
        "bg": "lightgrey",
        "troughcolor": "grey"        
    }
    greyed_out_dropdown = {
        "state": "disabled",
        "fg": "grey",
        "bg": "lightgrey" 
        # no troughcolor possible for dropdown widgets
    }
    # If the user hasn't selected an option, set a default value. 
    if run_option.get() == "Select an option": 
        run_option.set("Set outer sphere orbital radius") 
    # In any case, grey out the dropdown options now, to show, and ensure, 
    # that the selection cannot be changed during the run.    
    dropdown_run_option.config(**greyed_out_dropdown)
  
    # Grid parameters ---------------------------------------------------------
    grid_centre = ti.Vector.field(3, dtype=ti.f64, shape=())
    grid_centre[None] = ti.Vector([
        grid_size // 2,
        0.0,
        grid_size // 2
    ])
    depth_zeroised_grid_edges = grid_size // 100
    damped_grid_boundary_depth = grid_size // 20
    effective_grid_size = grid_size - 2 * depth_zeroised_grid_edges
    effective_grid_start = (grid_size - effective_grid_size)//2
    effective_grid_end = effective_grid_start + effective_grid_size
    grid_size_array_parms = {
        "n": 3,
        "dtype": ti.f64,
        "shape": (grid_size, grid_size)
    }
    grid_surface = ti.Vector.field(**grid_size_array_parms)
    initialise_vector_array(grid_surface,
                            grid_size) 
    grid_for_rendering = ti.Vector.field(**grid_size_array_parms)
    initialise_vector_array(grid_for_rendering,
                            grid_size)
    if (run_option.get() == "Test run 1 - two of four borders damped" or 
        run_option.get() == "Test run 2 - all four borders damped"):
        color_name = "dodgerblue" # Test surface is blue, reminiscent of 
                                  # a liquid surface such as water.
        slider_outer_orbital_radius.config(**greyed_out_slider)   
        tkinter_spheres_to_display.set(0)   
        slider_spheres_to_display.config(**greyed_out_slider) 
                       
    else:    
        color_name = "orange" # Sheet surface is orange for normal runs,
                              # reminiscent of some physical models. 
    # Set perturbation size to be proportional to sphere mass.    
    inner_perturb_radius = int(inner_sphere_mass) * 2
    outer_perturb_radius = int(outer_sphere_mass) * 2
    # The arbitrary definition of when the two spheres have merged.
    merge_separation_distance = (outer_perturb_radius + inner_perturb_radius)/2 
    # Allow sufficient space between perturbation extents and grid edge
    # so that everything is captured on the visible grid domain.
    max_initial_orbital_radius = (grid_size/2 
                                  - depth_zeroised_grid_edges
                                  - damped_grid_boundary_depth
                                  - inner_perturb_radius) # the larger of the two. 
                                      # This allows sufficient spacing for the
                                      # test run perturbations.
    if outer_orbital_radius > max_initial_orbital_radius:
        outer_orbital_radius = max_initial_orbital_radius # Keep within grid extent.
        tkinter_outer_orbital_radius.set(outer_orbital_radius)

    # Sphere calculations and perturbation calculations -----------------------
    previous_polar_angle = 0.0
    current_polar_angle = 0.0
    # If masses of spheres differ from one another, set inner sphere radius 
    # to be the one of the more massive sphere.
    if inner_sphere_mass < outer_sphere_mass:
        inner_sphere_mass, outer_sphere_mass = outer_sphere_mass, inner_sphere_mass 
    inner_sphere_radius = pow(inner_sphere_mass, 1/3)
    outer_sphere_radius = pow(outer_sphere_mass, 1/3) 
    slider_inner_sphere_mass.config(**greyed_out_slider)
    slider_outer_sphere_mass.config(**greyed_out_slider)
    sphere_mass_ratio = outer_sphere_mass/inner_sphere_mass
    inner_orbital_radius = outer_orbital_radius * sphere_mass_ratio
    # Sphere perturbation calculations ----------------------------------------
    outer_perturb_array = ti.field(dtype=ti.f64, 
                                   shape=(outer_perturb_radius * 2 + 1, 
                                          outer_perturb_radius * 2 + 1))
    inner_perturb_array = ti.field(dtype=ti.f64, 
                                   shape=(inner_perturb_radius * 2 + 1, 
                                          inner_perturb_radius * 2 + 1))
    outer_perturb_depth = outer_sphere_mass 
    inner_perturb_depth = inner_sphere_mass
    create_gaussian_perturb_array(outer_perturb_radius,
                                  outer_perturb_depth,
                                  outer_perturb_array)
    create_gaussian_perturb_array(inner_perturb_radius,
                                  inner_perturb_depth,
                                  inner_perturb_array)
    set_perturbation_only_once = True
    # Merging -----------------------------------------------------------------
    merged_sphere_radius = pow(inner_sphere_mass + outer_sphere_mass, 1/3)
    merged_perturb_radius = int(merged_sphere_radius * 5) # arbitrary enhancement
    merged_perturb_array = ti.field(dtype=ti.f64, 
                                    shape=(merged_perturb_radius * 2 + 1, 
                                    merged_perturb_radius * 2 + 1))
    merged_perturb_depth = inner_sphere_mass + outer_sphere_mass
    create_gaussian_perturb_array(merged_perturb_radius,
                                  merged_perturb_depth,
                                  merged_perturb_array)
    # Sheet surface computations ----------------------------------------------------
    adjacent_grid_elements = ti.field(dtype=ti.i32, shape=(4, 2))
    offsets = [[ 1, 0],
               [ 0, 1],
               [-1, 0],
               [ 0,-1]]       
    for i in range(4):
        for j in range(2):
            adjacent_grid_elements[i, j] = offsets[i][j]
    oscillator_positions = ti.Vector.field(**grid_size_array_parms)
    initialise_vector_array(oscillator_positions,
                            grid_size)    
    height_rescaled_oscillator_positions = ti.Vector.field(**grid_size_array_parms)
    initialise_vector_array(height_rescaled_oscillator_positions,
                            grid_size)    
    effective_grid_size_array_parms = {
        "n": 3,
        "dtype": ti.f64,
        "shape": (effective_grid_size, effective_grid_size)
    }
    oscillator_velocities    = ti.Vector.field(**effective_grid_size_array_parms)
    oscillator_accelerations = ti.Vector.field(**effective_grid_size_array_parms)
    # Smoothing ---------------------------------------------------------------
    smoothed_cell_position = ti.Vector.field(2, dtype=ti.i32, shape=())
    smoothing_start_pos = effective_grid_start + depth_zeroised_grid_edges
    smoothing_end_pos = effective_grid_end - depth_zeroised_grid_edges
    smoothed_oscillator_positions = ti.Vector.field(**grid_size_array_parms)
    initialise_vector_array(smoothed_oscillator_positions,
                            grid_size)   
    # Physical parameters -----------------------------------------------------
    ###################################################
    oscillator_initial_extension = 10
    elastic_constant = 1e8
    timestep = 1e-5
    boundary_damping_factor = 0.05
    sphere_angular_stepsize = 1.0
    ###################################################
    oscillator_mass = 1.0
    model_orbital_separation = 0.0
    astro_orbital_separation = 0.0
    astro_outer_sphere_orbital_speed = 0.0
    model_omega = 0.0
    # astro parameters --------------------------------------------------------
    astro_orbital_decay_rate = 0.0
    astro_omega = 0.0
    astro_length_scaling = 1e2
    G = 6.67430e-11  # Newton's constant
    G_cubed = G * G * G
    G_to_fourth_power = G * G * G * G
    c = 3.0e8        # Speed of light in vacuum
    c_to_fifth_power = c * c * c * c * c
    m_sun = 1.989e30
    m_sun_squared = m_sun * m_sun
    m_sun_cubed = m_sun * m_sun * m_sun
    orbital_decay_factor = -64/5 * G_cubed * m_sun_cubed / c_to_fifth_power 
    summed_masses = inner_sphere_mass + outer_sphere_mass
    astro_summed_masses = (inner_sphere_mass + outer_sphere_mass) * m_sun
    binary_energy_loss_rate_factor = 32/5 * G_to_fourth_power 
    binary_energy_loss_rate_factor *= (m_sun_squared  
                                       * (outer_sphere_mass * inner_sphere_mass) ** 2
                                       / (outer_sphere_mass + inner_sphere_mass) ** 2)
    binary_energy_loss_rate_factor /= c_to_fifth_power
    astro_binary_energy_loss_rate = 0.0

    # Rendering vars ----------------------------------------------------------
    rendered_outer_orbital_coords = ti.Vector.field(3, 
                                                    dtype=ti.f64, 
                                                    shape=(1,))
    rendered_inner_orbital_coords = ti.Vector.field(3, 
                                                    dtype=ti.f64, 
                                                    shape=(1,))
    grid_rescale_for_rendering = 1 / grid_size
    rendered_outer_sphere_radius = outer_sphere_radius * grid_rescale_for_rendering
    rendered_inner_sphere_radius = inner_sphere_radius * grid_rescale_for_rendering
    # Colour the surface ------------------------------------------------------
    rgb_color_normalized = [0, 0, 0]
    complementary_rgb_color_normalized = [0, 0, 0]
    (rgb_color_normalized, 
     complementary_rgb_color_normalized) = color_longname_to_RGB(
                                               color_name,
                                               rgb_color_normalized,
                                               complementary_rgb_color_normalized)
    rgb_color_normalized = tuple(rgb_color_normalized)
    complementary_rgb_color_normalized = tuple(complementary_rgb_color_normalized)
    grid_colors = ti.Vector.field(n=3, 
                                  dtype=ti.f64, 
                                  shape=(grid_size * grid_size))
    # Set up mesh data --------------------------------------------------------
    num_triangles = (grid_size - 1) * (grid_size - 1) * 2
    indices = ti.field(int, num_triangles * 3)
    set_indices(grid_size,
                indices)
    vertices = ti.Vector.field(n=3,
                               dtype=ti.f64,
                               shape=(grid_size * grid_size))
    # Loop-related initialisations --------------------------------------------
    test_sheet_energy = False

    root.after(0, update_info_window, root, shared_data) 
    window = ti.ui.Window(name="Surface",
                          res=(int(screen_width * 0.8), screen_height),
                          pos=(int(screen_width * 0.2), 0),
                          show_window=True,
                          vsync=True)          
    canvas = window.get_canvas()
    scene = window.get_scene()
    
    simulation_frame_counter = 0
    spheres_have_merged = False
    elapsed_time = 0.0
            
    # This is the main simulation loop inside mainline_code     
    while (shared_data['running']):
        simulation_frame_counter += 1
        
        # Housekeeping of loop data -------------------------------------------
        loop_duration = time.time() - prev_time_stamp
        fps = 1/loop_duration
        prev_time_stamp = time.time()

        previous_polar_angle = current_polar_angle
        
        # Get the user-adjustable parameters from the GUI. --------------------        
        (outer_orbital_radius, # the second radius will be computed using this.
         spheres_to_display,
         inner_sphere_mass,
         outer_sphere_mass,
         vertical_rescale,
         smoothing_window_size,
         camera_look_up_down,
         camera_height,
         camera_left_right,
         camera_forward_backward,
         grid_chequer_size) = import_parameters_from_gui()
        
        if not simulation_is_paused.is_set():
            elapsed_time += loop_duration
        
        # If the simulation is paused, reset all dynamic properties to zero. --
        if simulation_is_paused.is_set():
            model_omega = 0.0 
            astro_omega = 0.0 
            astro_outer_sphere_orbital_speed = 0.0
            astro_binary_energy_loss_rate = 0.0  
            fps = 0.0
    
        # Check to ensure that current run is not a test. ---------------------    
        elif (run_option.get() == "Set outer sphere orbital radius" or
              run_option.get() == "Inspiralling"):                        
            current_polar_angle = increment_polar_angle(
                                      initial_outer_orbital_radius,
                                      outer_orbital_radius,
                                      previous_polar_angle,
                                      sphere_angular_stepsize)
            calculate_orbital_coords(grid_centre,
                                     outer_orbital_radius,
                                     current_polar_angle,
                                     outer_orbital_coords)
            tkinter_outer_orbital_radius.set(outer_orbital_radius) # check this
            inner_orbital_radius = outer_orbital_radius * sphere_mass_ratio
            calculate_orbital_coords(grid_centre,
                                     inner_orbital_radius,
                                     current_polar_angle + 180,
                                     inner_orbital_coords)
            model_orbital_separation = separation_distance(outer_orbital_coords,   
                                                           inner_orbital_coords)
            # Check to ensure that the two spheres have not (yet) merged. -----
            if model_orbital_separation > merge_separation_distance:
                model_omega = calculate_model_omega(previous_polar_angle,
                                                    current_polar_angle,                                                    
                                                    loop_duration)
                
                # Calculate display value of astrophysical angular speed. ----- 
                astro_orbital_separation = convert_to_astro_distance(
                                               model_orbital_separation,
                                               astro_length_scaling)
                astro_omega = calculate_astro_omega(
                                  astro_orbital_separation,
                                  G,
                                  astro_summed_masses) 
                
                # Calculate display value of astrophysical orbital speed. -----
                astro_outer_orbital_radius = convert_to_astro_distance(
                                                 outer_orbital_radius,
                                                 astro_length_scaling)
                astro_outer_sphere_orbital_speed = (astro_omega 
                                                    * astro_outer_orbital_radius)
                
                # Display the gravitational wave energy loss at the current 
                # orbit even if the type of run is not inspiralling. ---------- 
                astro_binary_energy_loss_rate = compute_binary_energy_loss_rate(
                                                    binary_energy_loss_rate_factor,
                                                    astro_orbital_separation,
                                                    astro_omega)
                overlay_perturb_shape_onto_grid(outer_perturb_radius,
                                                outer_perturb_array, 
                                                outer_orbital_coords,
                                                oscillator_positions,
                                                oscillator_velocities)
                overlay_perturb_shape_onto_grid(inner_perturb_radius,
                                                inner_perturb_array, 
                                                inner_orbital_coords,
                                                oscillator_positions,
                                                oscillator_velocities)
                # Calculate those values that need to be updated for the two 
                # shrinking orbits. -------------------------------------------
                if run_option.get() == "Inspiralling":
                    astro_orbital_decay_rate = compute_astro_orbital_decay_rate(
                                                   astro_orbital_separation,
                                                   outer_sphere_mass,
                                                   inner_sphere_mass,
                                                   orbital_decay_factor)
                    model_orbital_decay_rate = (
                        astro_orbital_decay_rate / astro_length_scaling
                        * model_omega / astro_omega)
                    model_orbital_decay_rate /= 10
                    print(model_orbital_decay_rate)
                    if model_orbital_decay_rate <= (model_orbital_separation 
                                                   - merge_separation_distance): 
                        inner_orbital_radius += (model_orbital_decay_rate 
                                                 * outer_sphere_mass / summed_masses)
                        outer_orbital_radius += (model_orbital_decay_rate 
                                                 * inner_sphere_mass / summed_masses) 
                        tkinter_outer_orbital_radius.set(outer_orbital_radius) # check this
                    else:
                        spheres_have_merged = True
            else:
                spheres_have_merged = True        
                
            if spheres_have_merged:
                if set_perturbation_only_once == True: 
                    set_perturbation_only_once = False 
                    spheres_to_display = 1
                    tkinter_spheres_to_display.set(1) 
                    outer_sphere_radius *= 2 # arbitrary value
                    rendered_outer_sphere_radius = (outer_sphere_radius 
                                                    * grid_rescale_for_rendering)
                    slider_spheres_to_display.config(**greyed_out_slider)
                    slider_outer_orbital_radius.config(**greyed_out_slider) 
                    overlay_perturb_shape_onto_grid(merged_perturb_radius,
                                                    merged_perturb_array, 
                                                    grid_centre,
                                                    oscillator_positions,
                                                    oscillator_velocities)
                    outer_orbital_coords = grid_centre # check this
                    inner_orbital_coords = grid_centre # check this
                    model_orbital_separation = 0.0 # check this
                    astro_orbital_separation = 0.0 # check this

        elif ((run_option.get() == "Test run 1 - two of four borders damped" or 
               run_option.get() == "Test run 2 - all four borders damped") and
               set_perturbation_only_once == True):
            # Place the two perturbations only once.         
            # Neither sphere is rendered. -------------------------------------
            set_perturbation_only_once = False
            outer_orbital_coords[None] = ti.Vector([
                grid_centre[None][0] + outer_orbital_radius,
                0.0,
                grid_centre[None][2]
            ])
            inner_orbital_coords[None] = ti.Vector([
                grid_centre[None][0] - outer_orbital_radius,
                0.0,
                grid_centre[None][2]
            ])            
            overlay_perturb_shape_onto_grid(outer_perturb_radius,
                                            outer_perturb_array, 
                                            outer_orbital_coords,
                                            oscillator_positions,
                                            oscillator_velocities)
            overlay_perturb_shape_onto_grid(inner_perturb_radius,
                                            inner_perturb_array, 
                                            inner_orbital_coords,
                                            oscillator_positions,
                                            oscillator_velocities)
        #else:
            # Place additional testing run options here if needed.

        # ---------------------------------------------------------------------
        if not simulation_is_paused.is_set():
            if run_option.get() == "Test run 1 - two of four borders damped":
                number_of_damped_borders = 2
            else:
                number_of_damped_borders = 4
            damp_grid_boundary(number_of_damped_borders,
                               effective_grid_start,
                               effective_grid_end,
                               damped_grid_boundary_depth,
                               boundary_damping_factor,
                               oscillator_velocities,
                               oscillator_positions)  
            # -----------------------------------------------------------------
            # The new oscillator positions are determined here using the 
            # Runge-Kutta 4th order numerical integration. --------------------
            update_oscillator_positions_velocities_RK4(effective_grid_start,
                                                       effective_grid_end,
                                                       elastic_constant,
                                                       oscillator_initial_extension,
                                                       oscillator_mass,
                                                       adjacent_grid_elements,
                                                       oscillator_positions,
                                                       oscillator_velocities,
                                                       oscillator_accelerations,
                                                       timestep) 
        # ---------------------------------------------------------------------
        rescale_oscillator_heights(grid_size,
                                   vertical_rescale,
                                   oscillator_positions,
                                   height_rescaled_oscillator_positions)
        
        if smoothing_window_size > 2:
            smooth_the_surface(grid_size, 
                               smoothing_start_pos, 
                               smoothing_end_pos,
                               smoothing_window_size,
                               smoothed_cell_position, 
                               height_rescaled_oscillator_positions,
                               smoothed_oscillator_positions)
            rescale_grid_for_rendering(grid_size, 
                                       grid_rescale_for_rendering,
                                       smoothed_oscillator_positions,
                                       grid_for_rendering)
        else:
            rescale_grid_for_rendering(grid_size, 
                                       grid_rescale_for_rendering,
                                       height_rescaled_oscillator_positions,
                                       grid_for_rendering)
        set_grid_colors(grid_size,
                        grid_chequer_size,
                        rgb_color_normalized,
                        complementary_rgb_color_normalized,
                        grid_colors)
        set_triangle_vertices(grid_size,
                              grid_for_rendering,
                              vertices)
        scene.mesh(vertices,
                   indices=indices,
                   per_vertex_color=(grid_colors),
                   two_sided=True)
        
        # Render the spheres. For the test run cases, do nothing. -------------
        if (spheres_to_display == 1 or
            spheres_to_display == 2): # Render first sphere 
            rescale_rendered_orbital_coords(grid_rescale_for_rendering,
                                            outer_orbital_coords,
                                            rendered_outer_orbital_coords)
            scene.particles(rendered_outer_orbital_coords,
                            rendered_outer_sphere_radius,  
                            color=(0.9, 0.9, 0.9))
        if spheres_to_display == 2: # Render second sphere
            rescale_rendered_orbital_coords(grid_rescale_for_rendering,
                                            inner_orbital_coords,
                                            rendered_inner_orbital_coords)
            scene.particles(rendered_inner_orbital_coords,
                            rendered_inner_sphere_radius,  
                            color=(0.7, 0.9, 50))

        canvas.scene(scene)
        scene.ambient_light(color=(0.5, 0.5, 0.5))  # Ambient light
        scene.point_light(pos=(2, 4, 4),
                          color=(1.0, 1.0, 1.0))
        window.show()
        camera = ti.ui.make_camera()
        scene.set_camera(camera)
        # Set point of view using camera parameters
        camera.position(camera_left_right + 0.5,
                        camera_height,
                        camera_forward_backward)
        camera.lookat(camera_left_right + 0.5,
                          camera_look_up_down,
                          camera_forward_backward + 0.5)
        scene.set_camera(camera)
        energy_of_sheet = 0.0
        energy_of_sheet = total_energy_of_sheet(grid_size,
                                        elastic_constant,
                                        oscillator_positions,
                                        oscillator_mass,
                                        oscillator_velocities)
        
        # ---------------------------------------------------------------------
        if test_sheet_energy is True:
            print ("Test, total surface energy of sheet")
            print ("===================================")
            print ("simulation_frame_counter", simulation_frame_counter)
            print ("energy_of_sheet", energy_of_sheet)

        with shared_data['lock']:
            shared_data['elapsed_time'] = elapsed_time 
            shared_data['fps'] = fps
            shared_data['astro_orbital_separation'] = astro_orbital_separation
            shared_data['astro_outer_sphere_orbital_speed'] = astro_outer_sphere_orbital_speed
            shared_data['astro_omega'] = astro_omega
            shared_data['model_omega'] = model_omega
            shared_data['astro_binary_energy_loss_rate'] = astro_binary_energy_loss_rate
            shared_data['astro_orbital_decay_rate'] = astro_orbital_decay_rate

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
    slider_spheres_to_display.set(2) # check this error
    dropdown_run_option.config(**reactivate_dropdown)
    # Set the dropdown options for determining the type of run
    options_list = ["Set outer sphere orbital radius",
                    "Inspiralling",
                    "Test run 1 - two of four borders damped",
                    "Test run 2 - all four borders damped"]    
    run_option.set("Select an option")
    
    
    ti.sync()
    ti.profiler.print_kernel_profiler_info()



root.mainloop()
# END OF CODE -----------------------------------------------------------------