import json
import os
import shutil
import tkinter as tk
import urllib.request
from pathlib import Path
from tkinter import messagebox, filedialog

import customtkinter as ctk

path = os.path.join(os.getenv("HOME"), "PyFit", "workouts")
version = "0.3.0"


def check_files():
    # Check whether the specified path exists or not
    if not os.path.exists(path):
        os.makedirs(path)
        print("DIRECTORY CREATED")
    # Check if at least one workout file exists. If not, create a default workout.
    if len(get_stored_workouts()) == 0:
        workout_file = Path(os.path.join(path, "default.json"))
        workout_file.touch(exist_ok=True)
        if os.path.getsize(os.path.join(path, "default.json")) == 0:
            file = open(os.path.join(path, "default.json"), "a")
            file.write(
                '{ "Push-ups": [ 10, 5 ], "Leg Raises": [ 30, 1 ], "Hip raises": [ 30, 1 ], "Toe touches": [ 30, 1 ], "Flutter kicks": [ 30, 1 ], "Sit-ups": [ 30, 1 ], "Pull-ups": [ 10, 1 ], "Chin-ups": [ 10, 1 ], "Biceps": [ 10, 1 ], "Forward fly": [ 10, 1 ], "Side fly": [ 10, 1 ], "Forearms": [ 50, 2 ] }')
            file.close()
    # Check if the user has updated from v0.2.0 to v0.3.0 or newer. If this is the case, the default exercise needs to be updated and all old exercises will be removed to prevent a startup crash.
    files = get_stored_workouts()
    filename = files[0]
    default_file = open(os.path.join(path, filename))
    data = default_file.read()
    default_file.close()
    exercises = json.loads(data)
    if list(exercises)[0] == "exercises":
        remove_files()
        check_files()


def create_new_workout_file():
    dialog = ctk.CTkInputDialog(master=None, text="Type in workout name:", title="New workout")
    filename = str(dialog.get_input()) + ".json"
    print("filename = " + filename)
    workout_file = Path(os.path.join(path, filename))
    workout_file.touch(exist_ok=True)
    workout_option_menu.configure(values=get_stored_workouts())
    workout_option_menu.set(filename)


def get_stored_workouts():
    found_workouts = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    found_workouts_not_hidden = []
    for workout in found_workouts:
        if workout[0] != ".":
            found_workouts_not_hidden.append(workout)
    print(found_workouts_not_hidden)
    return found_workouts_not_hidden


def combobox_selection(choice):
    view_workout()
    # workoutOptionMenu.set(choice)


def reset_workout_view():
    exercise_text["text"] = ""
    reps_text["text"] = ""
    sets_text["text"] = ""


def view_workout():
    reset_workout_view()
    print("VIEW WORKOUT")
    file = open(os.path.join(path, workout_option_menu.get()), "r")
    data = file.read()
    print(data)
    file.close()
    if data != '{}' and len(data) > 0:
        exercises = json.loads(data)
        keys = list(exercises)
        for key in keys:
            exercise_text_data = exercise_text.cget("text") + key + "\n"
            exercise_text["text"] = exercise_text_data
            reps_text_data = reps_text.cget("text") + str(exercises[key][0]) + "\n"
            reps_text["text"] = reps_text_data
            sets_text_data = sets_text.cget("text") + str(exercises[key][1]) + "\n"
            sets_text["text"] = sets_text_data
    elif len(data) == 0:
        file = open(os.path.join(path, workout_option_menu.get()), "w")
        file.write('{}')
        file.close()
        print("ADDED INITIAL JSON DATA TO FILE")
        exercise_text["text"] = "(empty)"
    else:
        exercise_text["text"] = "(empty)"


def add_edit_workout_step():
    name = name_exercise_entry.get()
    reps = reps_entry.get()
    sets = sets_entry.get()
    if name == "" or reps == "" or sets == "":
        messagebox.showerror("PyFit", "One or more of the fields haven't been filled in")
    elif not reps.isnumeric():
        messagebox.showerror("PyFit", "reps is not a number")
    elif not sets.isnumeric():
        messagebox.showerror("PyFit", "sets is not a number")
    else:
        file = open(os.path.join(path, workout_option_menu.get()), "r")
        data = file.read()
        file.close()
        exercises = json.loads(data)
        exercises[name] = [str(reps), str(sets)]
        with open(os.path.join(path, workout_option_menu.get()), "w") as outfile:
            json.dump(exercises, outfile)
    view_workout()
    clear_entries()


def remove_workout_step():
    name = name_exercise_entry.get()
    file = open(os.path.join(path, workout_option_menu.get()), "r")
    data = file.read()
    file.close()
    exercises = json.loads(data)
    if name == "":
        messagebox.showerror("PyFit", "Name field is empty. Please enter step name you want to remove.")
        return
    if name in exercises:
        del exercises[name]
        with open(os.path.join(path, workout_option_menu.get()), "w") as outfile:
            json.dump(exercises, outfile)
    else:
        messagebox.showerror("PyFit", f'Workout doesn\'t contain "{name}" step.')
    view_workout()
    clear_entries()


def remove_workout():
    workouts = get_stored_workouts()
    if len(workouts) == 1:
        messagebox.showerror("PyFit", f'You must have at least 1 workout')
        return
    name = workout_option_menu.get()
    print(f"filename = {name}")
    os.remove(os.path.join(path, name))
    workout_option_menu.configure(values=get_stored_workouts())
    workout_option_menu.set("default.json")
    app.update()
    messagebox.showinfo("PyFit", f'{name} has been removed')


def raise_main_frame():
    main_frame.pack(anchor="w", fill="both", expand=True)
    workout_frame.pack_forget()


def raise_workout_frame():
    file = open(os.path.join(path, workout_option_menu.get()), "r")
    data = file.read()
    if len(data) != 0:
        workout_frame.pack(anchor="w", fill="both", expand=True)
        main_frame.pack_forget()
    else:
        messagebox.showerror("PyFit", "The selected workout doesn't contain any data.\nSelect another workout or edit the current one")


exercise_step = 0
exercise_set = 0
total_rep_count = 0
show_rest_screen = False


def next_step():
    next_step_button.set_text("Next step")
    global exercise_step
    global exercise_set
    global total_rep_count
    global show_rest_screen
    file = open(os.path.join(path, workout_option_menu.get()), "r")
    data = file.read()
    exercises = json.loads(data)
    keys = list(exercises)

    if total_rep_count == 0:
        print("first exercise")
        current_step_label["text"] = f"{exercises[keys[exercise_step]][0]}x {keys[exercise_step]}"
        current_set_label["text"] = f"set {exercise_set} of {exercises[keys[exercise_step]][1]}"
    if show_rest_screen:
        print("SHOW REST SCREEN")
        current_step_label["text"] = "Rest"
        if exercise_set == int(exercises[keys[exercise_step]][1]):
            if exercise_step < len(exercises) - 1:
                current_set_label["text"] = f"Next up: {exercises[keys[exercise_step + 1]][0]}x {keys[exercise_step + 1]}"
            else:
                current_set_label["text"] = f'Click "Finish" to go back to main menu'
                next_step_button.set_text("Finish")
        else:
            current_set_label["text"] = f"Next up: {exercises[keys[exercise_step]][0]}x {keys[exercise_step]}"
    elif exercise_set == int(exercises[keys[exercise_step]][1]):
        print("+1 exercise")
        exercise_step += 1
        exercise_set = 1
        if exercise_step < len(exercises):
            current_step_label["text"] = f"{exercises[keys[exercise_step]][0]}x {keys[exercise_step]}"
            current_set_label["text"] = f"set {exercise_set} of {exercises[keys[exercise_step]][1]}"
        else:
            print("END OF EXERCISE")
            return_to_main()
    else:
        print("+1 set")
        exercise_set += 1
        total_rep_count += int(exercises[keys[exercise_step]][0])
        current_step_label["text"] = f"{exercises[keys[exercise_step]][0]}x {keys[exercise_step]}"
        current_set_label["text"] = f"set {exercise_set} of {exercises[keys[exercise_step]][1]}"
        print(f"exerciseStep = {exercise_step}, exerciseSet = {exercise_set}, exerciseRep = {total_rep_count}")
    show_rest_screen = not show_rest_screen


def check_for_updates():
    print("CHECKING FOR UPDATES")
    tag = os.popen('curl -sL https://api.github.com/repos/MrBananaPants/PyFit/releases/latest').read()
    tag = json.loads(tag)
    latest_version = int(str(tag["tag_name"]).lstrip('0').replace(".", ""))
    current_version = int(str(version).lstrip('0').replace(".", ""))
    print(f"latest: {latest_version}, installed: {current_version}")

    if latest_version > current_version:
        if messagebox.askyesno("PyFit", "An update is available. Do you want to download the latest version?"):
            save_path = filedialog.askdirectory(title="Select save location")
            # todo: Change "PyFit.zip" to "PyFit.dmg" after release of version 0.3.0
            urllib.request.urlretrieve(tag["assets"][0]["browser_download_url"], os.path.join(save_path, "PyFit.zip"))
            messagebox.showinfo("PyFit", "The latest version has been downloaded")
    else:
        messagebox.showinfo("PyFit", "You already have the latest version installed")


def reset():
    clear_entries()
    remove_files()
    check_files()
    workout_option_menu.configure(values=get_stored_workouts())
    workout_option_menu.set("default.json")
    messagebox.showinfo("PyFit", "Reset complete. Custom workouts have been removed.")


def remove_files():
    shutil.rmtree(path)


def showSettings():
    settings_window = ctk.CTkToplevel()
    settings_window.title("Settings")
    settings_window.geometry("400x200")
    check_for_updates_button = ctk.CTkButton(master=settings_window, fg_color="#3C99DC", text="Check for updates", command=check_for_updates)
    check_for_updates_button.place(relx=0.5, rely=0.3, anchor=ctk.CENTER)
    check_for_updates_button = ctk.CTkButton(master=settings_window, fg_color="#3C99DC", text="Reset app", command=reset)
    check_for_updates_button.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    about_label = ctk.CTkLabel(master=settings_window, text=f"This app has been made by Joran Vancoillie.\nPyFit v{version}")
    about_label.place(relx=0.5, rely=0.85, anchor=ctk.CENTER)


def clear_entries():
    name_exercise_entry.delete(0, 'end')
    reps_entry.delete(0, 'end')
    sets_entry.delete(0, 'end')


def return_to_main():
    global exercise_step
    global exercise_set
    global total_rep_count
    global show_rest_screen
    exercise_step = 0
    exercise_set = 0
    total_rep_count = 0
    show_rest_screen = False
    raise_main_frame()
    current_step_label["text"] = "Press START to begin"
    current_set_label["text"] = ""
    next_step_button.set_text("START")


def main():
    view_workout()
    app.mainloop()


check_files()

# App settings + layout
app = ctk.CTk()
app.geometry("1100x650")
app.title("PyFit")
app.configure(bg="#212121")

# mainFrame view
main_frame = ctk.CTkFrame(app, fg_color="#212121")
main_frame.pack(anchor="w", fill="both", expand=True)

action_frame = ctk.CTkFrame(master=main_frame, fg_color="#E0E0E0", corner_radius=10)
action_frame.pack(anchor="w", fill="both", expand=True, side="left", padx=20, pady=20)

viewer_frame = ctk.CTkFrame(master=main_frame, fg_color="#757575", corner_radius=10)
viewer_frame.pack(anchor="w", fill="both", expand=True, side="right", padx=20, pady=20)

exercise_label = ctk.CTkLabel(master=action_frame, text="Select workout: ")
exercise_label.place(relx=0.125, rely=0.055, anchor=ctk.CENTER)
workout_option_menu = ctk.CTkOptionMenu(master=action_frame, fg_color="#3C99DC", values=get_stored_workouts(), command=combobox_selection)
workout_option_menu.place(relx=0.17, rely=0.105, anchor=ctk.CENTER)
create_new_workout_button = ctk.CTkButton(master=action_frame, fg_color="#3C99DC", text="Create new workout", command=create_new_workout_file)
create_new_workout_button.place(relx=0.47, rely=0.105, anchor=ctk.CENTER)
remove_workout_button = ctk.CTkButton(master=action_frame, width=80, fg_color="#3C99DC", text="Remove", command=remove_workout)
remove_workout_button.place(relx=0.71, rely=0.105, anchor=ctk.CENTER)

settings_button = ctk.CTkButton(master=action_frame, fg_color="#3C99DC", width=80, text="Settings", command=showSettings)
settings_button.place(relx=0.9, rely=0.035, anchor=ctk.CENTER)

exercise_label = ctk.CTkLabel(master=action_frame, text="Edit selected workout: ")
exercise_label.place(relx=0.0125, rely=0.25, anchor=ctk.W)
name_exercise_entry = ctk.CTkEntry(master=action_frame, placeholder_text="Exercise name")
name_exercise_entry.place(relx=0.03, rely=0.3, anchor=ctk.W)
reps_entry = ctk.CTkEntry(master=action_frame, placeholder_text="Amount of reps")
reps_entry.place(relx=0.03, rely=0.36, anchor=ctk.W)
sets_entry = ctk.CTkEntry(master=action_frame, placeholder_text="Amount of sets")
sets_entry.place(relx=0.03, rely=0.42, anchor=ctk.W)

add_step_button = ctk.CTkButton(master=action_frame, fg_color="#3C99DC", text="Edit/Add step", command=add_edit_workout_step)
add_step_button.place(relx=0.03, rely=0.48, anchor=ctk.W)

remove_last_step_button = ctk.CTkButton(master=action_frame, fg_color="#3C99DC", text="Remove step", command=remove_workout_step)
remove_last_step_button.place(relx=0.325, rely=0.48, anchor=ctk.W)

start_workout_button = ctk.CTkButton(master=action_frame, fg_color="#3C99DC", text="Start workout", command=raise_workout_frame)
start_workout_button.place(relx=0.50, rely=0.925, anchor=ctk.CENTER)

exercise_label = ctk.CTkLabel(master=viewer_frame, text="Exercise", text_color="white")
exercise_label.place(relx=0.20, rely=0.025, anchor=ctk.CENTER)

reps_label = ctk.CTkLabel(master=viewer_frame, text="Reps", text_color="white")
reps_label.place(relx=0.50, rely=0.025, anchor=ctk.CENTER)

sets_label = ctk.CTkLabel(master=viewer_frame, text="Sets", text_color="white")
sets_label.place(relx=0.80, rely=0.025, anchor=ctk.CENTER)

exercise_text = tk.Label(master=viewer_frame, text="", fg="white", bg="#757575", justify="left")
exercise_text.place(relx=0.15, rely=0.075, anchor=ctk.N)

reps_text = tk.Label(master=viewer_frame, text="", fg="white", bg="#757575", justify="left")
reps_text.place(relx=0.50, rely=0.075, anchor=tk.N)

sets_text = tk.Label(master=viewer_frame, text="", fg="white", bg="#757575", justify="left")
sets_text.place(relx=0.80, rely=0.075, anchor=ctk.N)

# workoutFrame view
workout_frame = ctk.CTkFrame(app, fg_color="#212121")

current_step_label = tk.Label(workout_frame, text="Press START to begin", fg="white", bg="#212121", font=('Segoe UI', 100))
current_step_label.place(relx=0.50, rely=0.3, anchor=ctk.CENTER)
current_set_label = tk.Label(workout_frame, text="", fg="white", bg="#212121", font=('Segoe UI', 50))
current_set_label.place(relx=0.50, rely=0.5, anchor=ctk.CENTER)

next_step_button = ctk.CTkButton(master=workout_frame, fg_color="#3C99DC", width=300, height=125, text="START", text_font=('Segoe UI', 50), command=next_step)
next_step_button.place(relx=0.5, rely=0.85, anchor=ctk.CENTER)

return_button = ctk.CTkButton(master=workout_frame, fg_color="#3C99DC", width=50, height=25, text="Return", text_font=('Segoe UI', 18), command=return_to_main)
return_button.place(relx=0.05, rely=0.05, anchor=ctk.CENTER)

if __name__ == "__main__":
    main()
