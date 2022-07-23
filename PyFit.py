import json
import os
import shutil
import tkinter as tk
import urllib.request
from pathlib import Path
from tkinter import messagebox, filedialog

import customtkinter as ctk
import requests

if os.name == 'nt':
    path = os.path.join(os.getenv("APPDATA"), "PyFit", "workouts")
else:
    path = os.path.join(os.getenv("HOME"), "PyFit", "workouts")

# Global variables
version = "0.4.0"
exercise_index = 0
info_index = 0
exercise_list = []
info_list = []


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
                '{ "Push-ups": [ "10", "5", "" ], "Leg Raises": [ "30", "1", "" ], "Hip raises": [ "30", "1", "" ], "Toe touches": [ "30", "1", "" ], "Flutter kicks": [ "30", "1", "" ], "Sit-ups": [ "30", "1", "" ], "Pull-ups": [ "10", "1", "" ], "Chin-ups": [ "10", "1", "" ], "Biceps": [ "10", "1", "" ], "Forward fly": [ "10", "1", "" ], "Side fly": [ "10", "1", "" ], "Forearms": [ "50", "2", "" ] }')
            file.close()
    # Check if the user has updated from v0.2.0 to v0.3.0 or newer. If this is the case, the default exercise needs to be updated and all old exercises will be removed to prevent a startup crash.
    files = get_stored_workouts()
    filename = files[0] + ".json"
    default_file = open(os.path.join(path, filename))
    data = default_file.read()
    default_file.close()
    exercises = json.loads(data)
    if "exercises" in exercises:
        remove_files()
        check_files()


def create_new_workout_file():
    dialog = ctk.CTkInputDialog(master=None, text="Type in workout name:", title="New workout")
    filename = str(dialog.get_input()) + ".json"
    print("filename = " + filename)
    workout_file = Path(os.path.join(path, filename))
    workout_file.touch(exist_ok=True)
    workout_option_menu.configure(values=get_stored_workouts())
    workout_option_menu.set(filename.replace(".json", ""))


def get_stored_workouts():
    found_workouts = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    found_workouts_not_hidden = []
    for workout in found_workouts:
        if workout[0] != ".":
            found_workouts_not_hidden.append(workout.replace(".json", ""))
    print(found_workouts_not_hidden)
    return found_workouts_not_hidden


def get_stored_workout_names():
    file = open(os.path.join(path, workout_option_menu.get()) + ".json", "r")
    data = file.read()
    print(data)
    file.close()
    exercises = json.loads(data)
    keys = list(exercises)
    keys.insert(0, "Select workout step")
    return keys


def workout_option_menu_selection(choise):
    view_workout()


def stored_workout_menu_selection(choise):
    update_entries()


def update_entries():
    print("UPDATING ENTRIES")
    file = open(os.path.join(path, workout_option_menu.get()) + ".json", "r")
    data = file.read()
    file.close()
    exercises = json.loads(data)
    key = select_stored_workout_menu.get()
    if key == "Select workout step":
        return
    clear_edit_entries()
    edit_name_exercise_entry.insert(0, key)
    edit_reps_entry.insert(0, exercises[key][0])
    edit_sets_entry.insert(0, exercises[key][1])
    if exercises[key][2] != "":
        edit_weight_entry.insert(0, exercises[key][2])


def reset_workout_view():
    exercise_text["text"] = ""
    reps_text["text"] = ""
    sets_text["text"] = ""
    weight_text["text"] = ""


def view_workout():
    reset_workout_view()
    print("VIEW WORKOUT")
    file = open(os.path.join(path, workout_option_menu.get()) + ".json", "r")
    data = file.read()
    file.close()
    if data != '{}' and len(data) > 0:
        exercises = json.loads(data)
        keys = list(exercises)
        for key in keys:
            exercise_text["text"] = exercise_text.cget("text") + key + "\n"
            reps_text["text"] = reps_text.cget("text") + str(exercises[key][0]) + "\n"
            sets_text["text"] = sets_text.cget("text") + str(exercises[key][1]) + "\n"
            weight_text["text"] = weight_text.cget("text") + str(exercises[key][2]) + "\n"

    elif len(data) == 0:
        file = open(os.path.join(path, workout_option_menu.get() + ".json"), "w")
        file.write('{}')
        file.close()
        print("ADDED INITIAL JSON DATA TO FILE")
        exercise_text["text"] = "(empty)"
    else:
        exercise_text["text"] = "(empty)"


def add_workout_step():
    name = name_exercise_entry.get()
    reps = reps_entry.get()
    sets = sets_entry.get()
    weight = weight_entry.get()
    if name == "" or reps == "" or sets == "":
        messagebox.showerror("PyFit", "One or more of the fields haven't been filled in")
    elif not reps.isnumeric():
        messagebox.showerror("PyFit", "reps is not a number")
    elif not sets.isnumeric():
        messagebox.showerror("PyFit", "sets is not a number")
    else:
        file = open(os.path.join(path, workout_option_menu.get() + ".json"), "r")
        data = file.read()
        file.close()
        exercises = json.loads(data)
        keys = list(exercises)
        if name in keys:
            messagebox.showerror("PyFit", "Exercise already exists")
            return
        exercises[name] = [str(reps), str(sets), str(weight)]
        with open(os.path.join(path, workout_option_menu.get() + ".json"), "w") as outfile:
            json.dump(exercises, outfile)
        view_workout()
        clear_entries()
        select_stored_workout_menu.configure(values=get_stored_workout_names())


def remove_workout_step():
    name = select_stored_workout_menu.get()
    file = open(os.path.join(path, workout_option_menu.get() + ".json"), "r")
    data = file.read()
    file.close()
    exercises = json.loads(data)
    del exercises[name]
    with open(os.path.join(path, workout_option_menu.get() + ".json"), "w") as outfile:
        json.dump(exercises, outfile)
    view_workout()
    clear_edit_entries()
    select_stored_workout_menu.configure(values=get_stored_workout_names())
    select_stored_workout_menu.set(get_stored_workout_names()[0])


def edit_workout_step():
    name = edit_name_exercise_entry.get()
    reps = edit_reps_entry.get()
    sets = edit_sets_entry.get()
    weight = edit_weight_entry.get()
    if name == "" or reps == "" or sets == "":
        messagebox.showerror("PyFit", "One or more of the required fields are empty")
    elif not reps.isnumeric():
        messagebox.showerror("PyFit", "reps is not a number")
    elif not sets.isnumeric():
        messagebox.showerror("PyFit", "sets is not a number")
    elif weight != "" and not weight.isnumeric():
        messagebox.showerror("PyFit", "weight is not a number")
    else:
        file = open(os.path.join(path, workout_option_menu.get() + ".json"), "r")
        data = file.read()
        file.close()
        exercises = json.loads(data)
        keys = list(exercises)
        if name not in keys:
            messagebox.showerror("PyFit", "You can't change the exercise name")
            edit_name_exercise_entry.delete(0, 'end')
            edit_name_exercise_entry.insert(0, select_stored_workout_menu.get())
            return
        exercises[name] = [str(reps), str(sets), str(weight)]
        with open(os.path.join(path, workout_option_menu.get() + ".json"), "w") as outfile:
            json.dump(exercises, outfile)
        view_workout()
        clear_edit_entries()
        select_stored_workout_menu.configure(values=get_stored_workout_names())
        select_stored_workout_menu.set(get_stored_workout_names()[0])


def remove_workout():
    workouts = get_stored_workouts()
    if len(workouts) == 1:
        messagebox.showerror("PyFit", f'You must have at least 1 workout')
        return
    name = workout_option_menu.get()
    print(f"filename = {name}")
    os.remove(os.path.join(path, name + ".json"))
    workout_option_menu.configure(values=get_stored_workouts())
    workout_option_menu.set(get_stored_workouts()[0])
    app.update()
    messagebox.showinfo("PyFit", f'"{name}" has been removed')


def raise_main_frame():
    main_frame.pack(anchor="w", fill="both", expand=True)
    workout_frame.pack_forget()


def raise_workout_frame():
    workout_data = open(os.path.join(path, workout_option_menu.get() + ".json"), "r")
    data = workout_data.read()
    workout_data.close()
    if data != "{}":
        workout_frame.pack(anchor="w", fill="both", expand=True)
        main_frame.pack_forget()
        create_exercises_lists()
    else:
        messagebox.showerror("PyFit", "The selected workout doesn't contain any data.\nSelect another workout or edit the current one.")


def create_exercises_lists():
    global exercise_index
    global info_index
    global exercise_list
    global info_list
    exercise_index = 0
    info_index = 0
    exercise_list = []
    info_list = []
    next_step_button.set_text("Start")
    file = open(os.path.join(path, workout_option_menu.get() + ".json"), "r")
    data = file.read()
    exercises = json.loads(data)
    keys = list(exercises)
    for key in keys:
        for i in range(0, int(exercises[key][1])):
            if exercises[key][2] == "":
                exercise_list.append(f"{exercises[key][0]}x {key}")
            else:
                exercise_list.append(f"{exercises[key][0]}x {key} ({exercises[key][2]}kg)")
            info_list.append(f"Next up: {exercise_list[-1]}")
            info_list.append(f"Set {i + 1} of {exercises[key][1]}")
            exercise_list.append("Rest")
    info_list.append('Click "Finish" to go back to main menu')
    info_label["text"] = info_list[info_index]
    info_index += 1
    return exercise_list, info_list


def next_step():
    global exercise_index
    global info_index
    global exercise_list
    global info_list
    next_step_button.set_text("Next")
    if info_index == len(info_list):
        return_to_main()
        return
    select_workout_label["text"] = exercise_list[exercise_index]
    exercise_index += 1
    info_label["text"] = info_list[info_index]
    info_index += 1
    if info_index == len(info_list):
        next_step_button.set_text("Finish")


def check_for_updates():
    print("CHECKING FOR UPDATES")
    tag = requests.get("https://api.github.com/repos/MrBananaPants/PyFit/releases/latest").text
    tag = json.loads(tag)
    latest_version = int(str(tag["tag_name"]).lstrip('0').replace(".", ""))
    current_version = int(str(version).lstrip('0').replace(".", ""))
    print(f"latest: {latest_version}, installed: {current_version}")

    if latest_version > current_version:
        if messagebox.askyesno("PyFit", "An update is available. Do you want to download the latest version?"):
            save_path = filedialog.askdirectory(title="Select save location")
            if os.name == 'nt':
                urllib.request.urlretrieve(tag["assets"][0]["browser_download_url"], os.path.join(save_path, "PyFit.zip"))
            else:
                urllib.request.urlretrieve(tag["assets"][0]["browser_download_url"], os.path.join(save_path, "PyFit.exe"))
            messagebox.showinfo("PyFit", "The latest version has been downloaded")
    else:
        messagebox.showinfo("PyFit", "You already have the latest version installed")


def reset():
    clear_entries()
    clear_edit_entries()
    remove_files()
    check_files()
    workout_option_menu.configure(values=get_stored_workouts())
    workout_option_menu.set(get_stored_workouts()[0])
    select_stored_workout_menu.configure(values=get_stored_workout_names())
    select_stored_workout_menu.set(get_stored_workout_names()[0])
    app.update()
    messagebox.showinfo("PyFit", "Reset complete. Custom workouts have been removed.")


def remove_files():
    shutil.rmtree(path)


def showSettings():
    settings_window = ctk.CTkToplevel(bg="#333333")
    settings_window.title("Settings")
    settings_window.geometry("400x200")

    check_for_updates_button = ctk.CTkButton(master=settings_window, fg_color="#3C99DC", text="Check for updates", command=check_for_updates)
    check_for_updates_button.place(relx=0.5, rely=0.3, anchor=ctk.CENTER)
    check_for_updates_button = ctk.CTkButton(master=settings_window, fg_color="#3C99DC", text="Reset app", command=reset)
    check_for_updates_button.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    about_label = ctk.CTkLabel(master=settings_window, text_color="white", text=f"This app has been made by Joran Vancoillie\nPyFit v{version}")
    about_label.place(relx=0.5, rely=0.85, anchor=ctk.CENTER)


def clear_entries():
    name_exercise_entry.delete(0, 'end')
    reps_entry.delete(0, 'end')
    sets_entry.delete(0, 'end')


def clear_edit_entries():
    edit_name_exercise_entry.delete(0, 'end')
    edit_reps_entry.delete(0, 'end')
    edit_sets_entry.delete(0, 'end')
    edit_weight_entry.delete(0, 'end')


def return_to_main():
    raise_main_frame()
    select_workout_label["text"] = "Press START to begin"
    info_label["text"] = ""
    next_step_button.set_text("START")


def main():
    view_workout()
    app.mainloop()


check_files()

# App settings + layout
app = ctk.CTk()
app.geometry("1280x720")
app.title("PyFit")
app.configure(bg="#212121")

# mainFrame view
main_frame = ctk.CTkFrame(app, fg_color="#202020")
main_frame.pack(anchor="w", fill="both", expand=True)

action_frame = ctk.CTkFrame(master=main_frame, fg_color="#333333", corner_radius=10)
action_frame.pack(anchor="w", fill="both", expand=True, side="left", padx=20, pady=20)

viewer_frame = ctk.CTkFrame(master=main_frame, fg_color="#333333", corner_radius=10)
viewer_frame.pack(anchor="w", fill="both", expand=True, side="right", padx=20, pady=20)

select_workout_label = ctk.CTkLabel(master=action_frame, text_color="white", text="Select workout: ")
select_workout_label.place(relx=0, rely=0.035, anchor=ctk.W)
workout_option_menu = ctk.CTkOptionMenu(master=action_frame, dropdown_hover_color="#3f3f3f", dropdown_text_color="white", dropdown_color="#535353",
                                        fg_color="#3C99DC", dynamic_resizing=False, values=get_stored_workouts(),
                                        command=workout_option_menu_selection)
workout_option_menu.place(relx=0.15, rely=0.085, anchor=ctk.CENTER)
create_new_workout_button = ctk.CTkButton(master=action_frame, fg_color="#3C99DC", text="Create new workout", command=create_new_workout_file)
create_new_workout_button.place(relx=0.40, rely=0.085, anchor=ctk.CENTER)
remove_workout_button = ctk.CTkButton(master=action_frame, width=80, fg_color="#3C99DC", text="Remove", command=remove_workout)
remove_workout_button.place(relx=0.60, rely=0.085, anchor=ctk.CENTER)

# Add new step to workout
add_new_step_label = ctk.CTkLabel(master=action_frame, text_color="white", text="Add new step to workout: ")
add_new_step_label.place(relx=0.03, rely=0.16, anchor=ctk.W)
name_exercise_entry = ctk.CTkEntry(master=action_frame, border_color="#535353", placeholder_text_color="#afafaf", text_color="white", fg_color="#414141",
                                   width=292, placeholder_text="Exercise name")
name_exercise_entry.place(relx=0.03, rely=0.21, anchor=ctk.W)
reps_entry = ctk.CTkEntry(master=action_frame, border_color="#535353", placeholder_text_color="#afafaf", text_color="white", fg_color="#414141", width=292,
                          placeholder_text="Amount of reps")
reps_entry.place(relx=0.03, rely=0.26, anchor=ctk.W)
sets_entry = ctk.CTkEntry(master=action_frame, border_color="#535353", placeholder_text_color="#afafaf", text_color="white", fg_color="#414141", width=292,
                          placeholder_text="Amount of sets")
sets_entry.place(relx=0.03, rely=0.31, anchor=ctk.W)
weight_entry = ctk.CTkEntry(master=action_frame, border_color="#535353", placeholder_text_color="#afafaf", text_color="white", fg_color="#414141", width=292,
                            placeholder_text="Weight (leave blank for no weight)")
weight_entry.place(relx=0.03, rely=0.36, anchor=ctk.W)

add_step_button = ctk.CTkButton(master=action_frame, width=292, fg_color="#3C99DC", text="Add step", command=add_workout_step)
add_step_button.place(relx=0.03, rely=0.41, anchor=ctk.W)

# Edit or remove workout step
edit_remove_step_label = ctk.CTkLabel(master=action_frame, text_color="white", text="Edit or remove step: ")
edit_remove_step_label.place(relx=0.0275, rely=0.485, anchor=ctk.W)

select_stored_workout_menu = ctk.CTkOptionMenu(master=action_frame, width=292, dropdown_hover_color="#3f3f3f", dropdown_text_color="white",
                                               dropdown_color="#535353",
                                               fg_color="#3C99DC", dynamic_resizing=False, values=get_stored_workout_names(),
                                               command=stored_workout_menu_selection)
select_stored_workout_menu.place(relx=0.03, rely=0.535, anchor=ctk.W)

edit_name_exercise_entry = ctk.CTkEntry(master=action_frame, border_color="#535353", placeholder_text_color="#afafaf", text_color="white", fg_color="#414141",
                                        width=292, placeholder_text="Exercise name")
edit_name_exercise_entry.place(relx=0.03, rely=0.585, anchor=ctk.W)
edit_reps_entry = ctk.CTkEntry(master=action_frame, border_color="#535353", placeholder_text_color="#afafaf", text_color="white", fg_color="#414141", width=292,
                               placeholder_text="Amount of reps")
edit_reps_entry.place(relx=0.03, rely=0.635, anchor=ctk.W)
edit_sets_entry = ctk.CTkEntry(master=action_frame, border_color="#535353", placeholder_text_color="#afafaf", text_color="white", fg_color="#414141", width=292,
                               placeholder_text="Amount of sets")
edit_sets_entry.place(relx=0.03, rely=0.685, anchor=ctk.W)
edit_weight_entry = ctk.CTkEntry(master=action_frame, border_color="#535353", placeholder_text_color="#afafaf", text_color="white", fg_color="#414141",
                                 width=292, placeholder_text="Weight (no weight for selected step)")
edit_weight_entry.place(relx=0.03, rely=0.735, anchor=ctk.W)

edit_step_button = ctk.CTkButton(master=action_frame, fg_color="#3C99DC", text="Edit step", command=edit_workout_step)
edit_step_button.place(relx=0.03, rely=0.785, anchor=ctk.W)

remove_step_button = ctk.CTkButton(master=action_frame, fg_color="#3C99DC", text="Remove step", command=remove_workout_step)
remove_step_button.place(relx=0.2825, rely=0.785, anchor=ctk.W)

# remove_last_step_button = ctk.CTkButton(master=action_frame, fg_color="#3C99DC", text="Remove step", command=remove_workout_step)
# remove_last_step_button.place(relx=0.325, rely=0.47, anchor=ctk.W)

settings_button = ctk.CTkButton(master=action_frame, fg_color="#3C99DC", text="Settings", command=showSettings)
settings_button.place(relx=0.35, rely=0.925, anchor=ctk.CENTER)

start_workout_button = ctk.CTkButton(master=action_frame, fg_color="#3C99DC", text="Start workout", command=raise_workout_frame)
start_workout_button.place(relx=0.65, rely=0.925, anchor=ctk.CENTER)

select_workout_label = ctk.CTkLabel(master=viewer_frame, text="Exercise", text_color="white")
select_workout_label.place(relx=0.20, rely=0.0325, anchor=ctk.CENTER)

reps_label = ctk.CTkLabel(master=viewer_frame, text="Reps", text_color="white")
reps_label.place(relx=0.45, rely=0.0325, anchor=ctk.CENTER)

sets_label = ctk.CTkLabel(master=viewer_frame, text="Sets", text_color="white")
sets_label.place(relx=0.65, rely=0.0325, anchor=ctk.CENTER)

weight_label = ctk.CTkLabel(master=viewer_frame, text="Weight (kg)", text_color="white")
weight_label.place(relx=0.85, rely=0.0325, anchor=ctk.CENTER)

exercise_text = tk.Label(master=viewer_frame, text="", fg="white", bg="#333333", justify="left")
exercise_text.place(relx=0.15, rely=0.075, anchor=ctk.N)

reps_text = tk.Label(master=viewer_frame, text="", fg="white", bg="#333333", justify="center")
reps_text.place(relx=0.45, rely=0.075, anchor=tk.N)

sets_text = tk.Label(master=viewer_frame, text="", fg="white", bg="#333333", justify="center")
sets_text.place(relx=0.65, rely=0.075, anchor=ctk.N)

weight_text = tk.Label(master=viewer_frame, text="", fg="white", bg="#333333", justify="center")
weight_text.place(relx=0.85, rely=0.075, anchor=ctk.N)

# workoutFrame view
workout_frame = ctk.CTkFrame(app, fg_color="#202020")

select_workout_label = tk.Label(workout_frame, text="Press START to begin", fg="white", bg="#212121", font=('Segoe UI', 100))
select_workout_label.place(relx=0.50, rely=0.3, anchor=ctk.CENTER)
info_label = tk.Label(workout_frame, text="", fg="white", bg="#212121", font=('Segoe UI', 50))
info_label.place(relx=0.50, rely=0.5, anchor=ctk.CENTER)

next_step_button = ctk.CTkButton(master=workout_frame, fg_color="#3C99DC", width=300, height=125, text="START", text_font=('Segoe UI', 50), command=next_step)
next_step_button.place(relx=0.5, rely=0.85, anchor=ctk.CENTER)

return_button = ctk.CTkButton(master=workout_frame, fg_color="#3C99DC", width=50, height=25, text="Return", text_font=('Segoe UI', 18), command=return_to_main)
return_button.place(relx=0.05, rely=0.05, anchor=ctk.CENTER)

if __name__ == "__main__":
    main()
