import http.client as httplib
import json
import os
import shutil
import urllib.request
import webbrowser
from datetime import datetime
from pathlib import Path
from subprocess import call
from tkinter import messagebox, filedialog

import matplotlib
from PIL.ImageTk import PhotoImage
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

matplotlib.use("TkAgg")
import matplotlib.dates as mdates

import customtkinter as ctk
import requests
from PIL import Image

if os.name == 'nt':
    path = os.path.join(os.getenv("APPDATA"), "PyFit", "workouts")
    main_path = os.path.join(os.getenv("APPDATA"), "PyFit")

else:
    path = os.path.join(os.getenv("HOME"), "PyFit", "workouts")
    main_path = os.path.join(os.getenv("HOME"), "PyFit")

# Global variables
version = "0.6.2"
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
            with open(os.path.join(path, "default.json"), "a") as file:
                file.write(
                    '{ "Push-ups": [ "10", "5", "" ], "Leg Raises": [ "30", "1", "" ], "Hip raises": [ "30", "1", "" ], "Toe touches": [ "30", "1", "" ], "Flutter kicks": [ "30", "1", "" ], "Sit-ups": [ "30", "1", "" ], "Pull-ups": [ "10", "1", "" ], "Chin-ups": [ "10", "1", "" ], "Biceps": [ "10", "1", "" ], "Forward fly": [ "10", "1", "" ], "Side fly": [ "10", "1", "" ], "Forearms": [ "50", "2", "" ] }')
    # Check if the user has updated from v0.2.0 to v0.3.0 or newer. If this is the case, the default exercise needs to be updated and all old exercises will be removed to prevent a startup crash.
    files = get_stored_workouts()
    filename = files[0]
    exercises = get_workout_data(os.path.join(path, filename + ".json"))
    if "exercises" in exercises:
        remove_files()
        check_files()
    # Check if the settings file exists. Create one if it doesn't.
    settings_path = Path(os.path.join(main_path, "settings.json"))
    settings_path.touch(exist_ok=True)
    if os.path.getsize(os.path.join(main_path, "settings.json")) == 0:
        print("CREATING SETTINGS FILE")
        with open(os.path.join(main_path, "settings.json"), "w") as file:
            settings = {
                "theme": "Dark"
            }
            json.dump(settings, file)
    # Check if the personal records file exists. Create one if it doesn't.
    pr_path = Path(os.path.join(main_path, "personal_records.json"))
    pr_path.touch(exist_ok=True)
    if os.path.getsize(os.path.join(main_path, "personal_records.json")) == 0:
        print("CREATING PERSONAL_RECORDS FILE")
        with open(os.path.join(main_path, "personal_records.json"), "w") as file:
            settings = {}
            json.dump(settings, file)


def export_workouts():
    save_path = filedialog.askdirectory(title="Choose export location")
    if save_path:
        shutil.make_archive(os.path.join(save_path, "PyFit_export"), "zip", path)
        messagebox.showinfo("PyFit", "Export complete")


def import_workouts():
    zip_file = filedialog.askopenfilename()
    filename, extension = os.path.splitext(zip_file)
    if zip_file:
        if extension != ".zip":
            messagebox.showerror("PyFit", "Selected file is not a .zip file")
        else:
            shutil.unpack_archive(zip_file, path, "zip")
            messagebox.showinfo("PyFit", "Import complete")
        workout_option_menu.configure(values=get_stored_workouts())


def create_new_workout_file():
    dialog = ctk.CTkInputDialog(text="Type in workout name:", title="New workout")
    dialog_input = dialog.get_input()
    if dialog_input is None or dialog_input == "":
        return
    if len(dialog_input) > 100:
        messagebox.showerror("PyFit", "Workout name too long")
        return
    if str(dialog_input).lower() in get_stored_workouts():
        messagebox.showerror("PyFit", "Workout with this name already exists")
        return
    filename = str(dialog_input + ".json")
    print("filename = " + filename)
    workout_file = Path(os.path.join(path, filename))
    workout_file.touch(exist_ok=True)
    workout_option_menu.configure(values=get_stored_workouts())
    workout_option_menu.set(filename.replace(".json", ""))
    view_workout()


def get_stored_workouts():
    found_workouts = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    found_workouts_not_hidden = []
    for workout in found_workouts:
        if workout[0] != "." and workout != "settings.json":
            found_workouts_not_hidden.append(workout.replace(".json", ""))
    print(f"found workouts: {found_workouts_not_hidden}")
    return found_workouts_not_hidden


def get_workout_steps_names():
    exercises = get_workout_data(os.path.join(path, workout_option_menu.get()) + ".json")
    print(str(exercises))
    keys = list(exercises)
    return keys


def get_pr_names():
    with open(os.path.join(main_path, "personal_records.json"), "r") as file:
        data = file.read()
    exercises = json.loads(data)
    print(str(exercises))
    keys = list(exercises)
    return keys


def get_workout_data(filename):
    with open(filename, "r") as file:
        return json.load(file)


def workout_option_menu_selection(choice):
    view_workout()


def stored_workout_menu_selection(choice):
    update_entries()


def pr_menu_selection(choice):
    update_pr_entries()


def theme_option_selection(choice):
    print(f"Selected theme {choice}")
    change_theme(choice)


def change_theme(theme):
    print(f"CHANGING THEME TO {theme}")
    with open(os.path.join(main_path, "settings.json"), "r") as file:
        settings = json.load(file)
    settings["theme"] = str(theme)
    with open(os.path.join(main_path, "settings.json"), "w") as outfile:
        json.dump(settings, outfile)
    ctk.set_appearance_mode(str(theme).lower())
    generate_graph()


def update_entries():
    print("UPDATING ENTRIES")
    exercises = get_workout_data(os.path.join(path, workout_option_menu.get()) + ".json")
    key = select_workout_step_menu.get()
    if key == "Select workout step":
        return
    clear_edit_entries()
    edit_name_exercise_entry.insert(0, key)
    edit_reps_entry.insert(0, exercises[key][0])
    edit_sets_entry.insert(0, exercises[key][1])
    if exercises[key][2] != "":
        edit_weight_entry.insert(0, exercises[key][2])


def update_pr_entries():
    print("UPDATING PR ENTRIES")
    with open(os.path.join(main_path, "personal_records.json"), "r") as file:
        data = file.read()
    exercises = json.loads(data)
    print(str(exercises))
    key = select_pr_menu.get()
    if key == "Select personal record":
        return
    clear_pr_entries()
    pr_edit_name_entry.insert(0, key)
    pr_edit_weight_entry.insert(0, exercises[key][1][-1])


def reset_workout_view():
    exercise_text.configure(text="")
    reps_text.configure(text="")
    sets_text.configure(text="")
    weight_text.configure(text="")


def reset_pr_view():
    pr_exercise_text.configure(text="")
    pr_weight_text.configure(text="")
    pr_date_text.configure(text="")


def view_workout():
    reset_workout_view()
    print("VIEW WORKOUT")
    with open(os.path.join(path, workout_option_menu.get()) + ".json", "r") as file:
        data = file.read()
    if data != '{}' and len(data) > 0:
        exercises = json.loads(data)
        keys = list(exercises)
        exercise = ""
        reps = ""
        sets = ""
        weight = ""
        for key in keys:
            exercise += key + "\n"
            reps += str(exercises[key][0]) + "\n"
            sets += str(exercises[key][1]) + "\n"
            weight += str(exercises[key][2]) + "\n"
        exercise_text.configure(text=exercise)
        reps_text.configure(text=reps)
        sets_text.configure(text=sets)
        weight_text.configure(text=weight)
    elif len(data) == 0:
        with open(os.path.join(path, workout_option_menu.get() + ".json"), "w") as file:
            file.write('{}')
        print("ADDED INITIAL JSON DATA TO FILE")
        exercise_text.configure(text="(empty)")

    else:
        exercise_text.configure(text="(empty)")
    clear_edit_entries()
    select_workout_step_menu.configure(values=get_workout_steps_names())
    select_workout_step_menu.set("Select workout step")


def view_pr():
    reset_pr_view()
    print("VIEW PR")
    with open(os.path.join(main_path, "personal_records.json"), "r") as file:
        data = file.read()
    if data != '{}' and len(data) > 0:
        exercises = json.loads(data)
        keys = list(exercises)
        exercise = ""
        weight = ""
        date = ""
        for key in keys:
            exercise += key + "\n"
            weight += str(list(list(exercises[key])[1])[-1]) + "\n"
            date += str(list(list(exercises[key])[0])[-1]) + "\n"
        pr_exercise_text.configure(text=exercise)
        pr_weight_text.configure(text=weight)
        pr_date_text.configure(text=date)
    else:
        pr_exercise_text.configure(text="(no records)")
    clear_pr_entries()
    select_workout_step_menu.configure(values=get_pr_names())
    select_pr_menu.set("Select personal record")
    select_graph_menu.set("Select personal record")


def add_workout_step():
    name = name_exercise_entry.get()
    reps = reps_entry.get()
    sets = sets_entry.get()
    weight = weight_entry.get()
    if name == "" or reps == "" or sets == "":
        messagebox.showerror("PyFit", "One or more of the required fields are empty")
    elif not reps.isnumeric():
        messagebox.showerror("PyFit", "reps is not a number")
    elif not sets.isnumeric():
        messagebox.showerror("PyFit", "sets is not a number")
    else:
        exercises = get_workout_data(os.path.join(path, workout_option_menu.get() + ".json"))
        keys = list(exercises)
        if name in keys:
            messagebox.showerror("PyFit", "Exercise already exists")
            return
        exercises[name] = [str(reps), str(sets), str(weight)]
        with open(os.path.join(path, workout_option_menu.get() + ".json"), "w") as outfile:
            json.dump(exercises, outfile)
        view_workout()
        clear_entries()
        select_workout_step_menu.configure(values=get_workout_steps_names())


def remove_workout_step():
    name = select_workout_step_menu.get()
    exercises = get_workout_data(os.path.join(path, workout_option_menu.get() + ".json"))
    if name == "Select workout step":
        messagebox.showerror("PyFit", "No workout step selected")
        return
    del exercises[name]
    with open(os.path.join(path, workout_option_menu.get() + ".json"), "w") as outfile:
        json.dump(exercises, outfile)
    view_workout()
    clear_edit_entries()
    select_workout_step_menu.configure(values=get_workout_steps_names())
    select_workout_step_menu.set("Select workout step")


def edit_workout_step():
    name = edit_name_exercise_entry.get()
    reps = edit_reps_entry.get()
    sets = edit_sets_entry.get()
    weight = edit_weight_entry.get()
    if name == "":
        messagebox.showerror("PyFit", "No workout step selected")
    elif reps == "" or sets == "":
        messagebox.showerror("PyFit", "One or more of the required fields are empty")
    elif not reps.isnumeric():
        messagebox.showerror("PyFit", "reps is not a number")
    elif not sets.isnumeric():
        messagebox.showerror("PyFit", "sets is not a number")
    elif weight != "" and not weight.isnumeric():
        messagebox.showerror("PyFit", "weight is not a number")
    else:
        exercises = get_workout_data(os.path.join(path, workout_option_menu.get() + ".json"))
        keys = list(exercises)
        if name not in keys:
            messagebox.showerror("PyFit", "You can't change the exercise name")
            edit_name_exercise_entry.delete(0, 'end')
            edit_name_exercise_entry.insert(0, select_workout_step_menu.get())
            return
        exercises[name] = [str(reps), str(sets), str(weight)]
        with open(os.path.join(path, workout_option_menu.get() + ".json"), "w") as outfile:
            json.dump(exercises, outfile)
        view_workout()
        clear_edit_entries()
        select_workout_step_menu.configure(values=get_workout_steps_names())
        select_workout_step_menu.set("Select workout step")


def add_pr():
    name = pr_add_name_entry.get()
    weight = pr_add_weight_entry.get()
    if name == "" or weight == "":
        messagebox.showerror("PyFit", "One or more of the required fields are empty")
    elif not weight.isnumeric():
        messagebox.showerror("PyFit", "weight is not a number")
    else:
        with open(os.path.join(main_path, "personal_records.json"), "r") as file:
            data = file.read()
        exercises = json.loads(data)
        keys = list(exercises)
        if name in keys:
            messagebox.showerror("PyFit", "Personal record already exists")
            return
        exercises[name] = [[datetime.today().strftime('%d-%m-%Y')], [str(weight)]]
        with open(os.path.join(main_path, "personal_records.json"), "w") as outfile:
            json.dump(exercises, outfile)
        view_pr()
        clear_pr_entries()
        select_pr_menu.configure(values=get_pr_names())
        select_graph_menu.configure(values=get_pr_names())


def edit_pr():
    name = pr_edit_name_entry.get()
    weight = pr_edit_weight_entry.get()
    if name == "" or weight == "":
        messagebox.showerror("PyFit", "One or more of the required fields are empty")
    elif not weight.isnumeric():
        messagebox.showerror("PyFit", "weight is not a number")
    else:
        with open(os.path.join(main_path, "personal_records.json"), "r") as file:
            data = file.read()
        exercises = json.loads(data)
        keys = list(exercises)
        if name not in keys:
            messagebox.showerror("PyFit", "You can't change the record's name")
            pr_add_name_entry.delete(0, 'end')
            pr_add_name_entry.insert(0, select_pr_menu.get())
            return
        # "benchpress" : [[date, date, date], [weight weight weight]]

        record_dates = exercises[name][0]
        if datetime.today().strftime('%d-%m-%Y') in record_dates:
            print("Record for today already exists, replacing old record...")
            record_weights = exercises[name][1]
            record_weights[-1] = str(weight)
        else:
            record_dates.append(datetime.today().strftime('%d-%m-%Y'))
            record_weights = exercises[name][1]
            record_weights.append(str(weight))

        print(f"--------------NEW PR VALUE: {str([record_dates, record_weights])}")
        exercises[name] = [record_dates, record_weights]
        with open(os.path.join(main_path, "personal_records.json"), "w") as outfile:
            json.dump(exercises, outfile)
        view_pr()
        clear_pr_entries()
        select_pr_menu.configure(values=get_pr_names())
        select_graph_menu.configure(values=get_pr_names())


def remove_pr():
    name = select_pr_menu.get()
    if name == "Select personal record":
        messagebox.showerror("PyFit", "No record selected")
        return
    with open(os.path.join(main_path, "personal_records.json"), "r") as file:
        data = file.read()
    exercises = json.loads(data)
    del exercises[name]
    with open(os.path.join(main_path, "personal_records.json"), "w") as outfile:
        json.dump(exercises, outfile)
    clear_pr_entries()
    view_pr()
    select_pr_menu.configure(values=get_pr_names())
    select_graph_menu.configure(values=get_pr_names())
    messagebox.showinfo("PyFit", f'"{name}" record has been removed')


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
    view_workout()


def create_exercises_lists():
    global exercise_index
    global info_index
    global exercise_list
    global info_list
    total_reps = 0
    total_volume = 0
    exercise_index = 0
    info_index = 0
    exercise_list = []
    info_list = []
    next_step_button.configure(text="START")
    exercises = get_workout_data(os.path.join(path, workout_option_menu.get() + ".json"))
    keys = list(exercises)
    for key in keys:
        for i in range(0, int(exercises[key][1])):
            if exercises[key][2] == "":
                exercise_list.append(f"{exercises[key][0]}x {key}")
            else:
                exercise_list.append(f"{exercises[key][0]}x {key} ({exercises[key][2]}kg)")
                total_volume += int(exercises[key][0]) * int(exercises[key][2])
            total_reps += int(exercises[key][0])
            info_list.append(f"Next up: {exercise_list[-1]}")
            info_list.append(f"Set {i + 1} of {exercises[key][1]}")
            exercise_list.append("Rest")
    exercise_list[-1] = "Workout finished!"
    if total_volume > 0:
        info_list.append(f"You've done {total_reps} reps\nYour total volume is {total_volume}kg")
    else:
        info_list.append(f"You've done {total_reps} reps")
    info_label.configure(text=info_list[info_index])
    info_index += 1
    print(f"total reps = {total_reps}, total volume = {total_volume}")


def next_step():
    global exercise_index
    global info_index
    global exercise_list
    global info_list
    progressbar.configure(width=app.winfo_width())
    progressbar.set(info_index / len(exercise_list))
    next_step_button.configure(text="Next step")
    if info_index == len(info_list):
        raise_main_frame()
        return
    if int(len(exercise_list[exercise_index])) > 25:
        current_workout_step_label.cget("font").configure(size=50)
    else:
        current_workout_step_label.cget("font").configure(size=100)
    current_workout_step_label.configure(text=exercise_list[exercise_index])
    exercise_index += 1
    info_label.configure(text=info_list[info_index])
    info_index += 1
    if info_index == len(info_list):
        next_step_button.configure(text="Finish")


def generate_graph():
    for widget in graph_frame.winfo_children():
        widget.destroy()

    with open(os.path.join(main_path, "settings.json")) as settings_file_graph:
        settings_data_graph = json.load(settings_file_graph)

    if str(settings_data_graph["theme"]).lower() == "light":
        background_color = "#e2e2e2"
        graph_color = "black"
    else:
        background_color = "#333333"
        graph_color = "white"

    dates = []
    records = []

    with open(os.path.join(main_path, "personal_records.json"), "r") as file:
        data = file.read()
    if data != '{}' and len(data) > 0 and select_graph_menu.get() != "Select personal record":
        exercises = json.loads(data)
    else:
        messagebox.showerror("PyFit", "No personal record selected. Select a record or add a new one.")
        return

    dates_list_string = exercises[select_graph_menu.get()][0]
    for date in dates_list_string:
        dates.append(datetime.strptime(date, '%d-%m-%Y'))

    records_list_string = exercises[select_graph_menu.get()][1]
    for record in records_list_string:
        records.append(int(record))

    f, a = plt.subplots(figsize=(6, 5), dpi=100)
    a.plot(dates, records, linestyle="solid", color="#3C99DC")

    plt.xlabel('Date')
    plt.ylabel('Weight (kg)')

    date_format = mdates.DateFormatter('%b-%y')
    a.xaxis.set_major_formatter(date_format)
    a.xaxis.set_major_locator(mdates.MonthLocator(interval=1))

    a.set_facecolor(background_color)
    f.patch.set_facecolor(background_color)
    a.spines['top'].set_color(background_color)
    a.spines['right'].set_color(background_color)
    a.spines['bottom'].set_color(graph_color)
    a.spines['left'].set_color(graph_color)
    a.xaxis.label.set_color(graph_color)
    a.yaxis.label.set_color(graph_color)
    a.tick_params(axis='x', colors=graph_color)
    a.tick_params(axis='y', colors=graph_color)

    canvas = FigureCanvasTkAgg(f, graph_frame)

    canvas.get_tk_widget().pack(side=ctk.TOP, fill=ctk.BOTH, expand=False)
    img = PhotoImage(file='media/icon.ico')
    app.tk.call('wm', 'iconphoto', app._w, img)


def check_connection():
    connection = httplib.HTTPConnection("www.github.com", timeout=5)
    try:
        # only header requested for fast operation
        connection.request("HEAD", "/")
        connection.close()
        print("Internet On")
        return True
    except Exception as exep:
        print(exep)
        return False


def check_for_updates(alert_when_no_update=False):
    print("CHECKING FOR UPDATES")
    if not check_connection():
        if alert_when_no_update:
            messagebox.showerror("PyFit", "Unable to check for updates: no internet connection")
        return
    tag = requests.get("https://api.github.com/repos/MrBananaPants/PyFit/releases/latest").text
    tag = json.loads(tag)
    print(str(tag))
    if list(tag)[0] != "url":
        if alert_when_no_update:
            messagebox.showerror("PyFit", "API rate limit exceeded, press OK to manually download the newest version")
            webbrowser.open('https://github.com/MrBananaPants/PyFit/releases/latest', new=2)
        return None
    latest_version = int(str(tag["tag_name"]).lstrip('0').replace(".", ""))
    current_version = int(str(version).lstrip('0').replace(".", ""))
    latest_version_formatted = str(tag["tag_name"])
    print(f"latest: {latest_version}, installed: {current_version}")

    if latest_version > current_version:
        if messagebox.askyesno("PyFit", f"An update is available (v{latest_version_formatted}). Do you want to download this update?"):
            save_path = filedialog.askdirectory(title="Select save location")
            try:
                if os.name == 'nt':
                    urllib.request.urlretrieve(f"https://github.com/MrBananaPants/PyFit/releases/download/{latest_version_formatted}/PyFit.exe",
                                               os.path.join(save_path, "PyFit.exe"))
                    messagebox.showinfo("PyFit", "The latest version has been downloaded")
                    os.startfile(save_path)
                else:
                    urllib.request.urlretrieve(f"https://github.com/MrBananaPants/PyFit/releases/download/{latest_version_formatted}/PyFit.dmg",
                                               os.path.join(save_path, "PyFit.dmg"))
                    messagebox.showinfo("PyFit", "The latest version has been downloaded")
                    call(["open", "-R", os.path.join(save_path, "PyFit.dmg")])

            except urllib.error.HTTPError:
                messagebox.showerror("PyFit", "Cannot download latest version. Press OK to manually download the newest version")
                webbrowser.open('https://github.com/MrBananaPants/PyFit/releases/latest', new=2)

    elif alert_when_no_update:
        messagebox.showinfo("PyFit", "You already have the latest version installed")


def reset():
    if messagebox.askyesno("PyFit",
                           f"Are you sure you want to continue? This will remove all custom workouts, personal records and reset all settings to their default value."):
        clear_entries()
        clear_edit_entries()
        remove_files()
        check_files()
        workout_option_menu.configure(values=get_stored_workouts())
        workout_option_menu.set(get_stored_workouts()[0])
        select_workout_step_menu.configure(values=get_workout_steps_names())
        select_workout_step_menu.set(get_workout_steps_names()[0])
        tabview.set("Home")
        ctk.set_appearance_mode("dark")
        theme_selection.set("Dark")
        app.update()
        view_workout()
        view_pr()
        for widget in graph_frame.winfo_children():
            widget.destroy()
        messagebox.showinfo("PyFit", "Reset complete")


def remove_files():
    shutil.rmtree(main_path)


def clear_entries():
    name_exercise_entry.delete(0, 'end')
    reps_entry.delete(0, 'end')
    sets_entry.delete(0, 'end')
    weight_entry.delete(0, 'end')


def clear_pr_entries():
    pr_add_name_entry.delete(0, 'end')
    pr_add_weight_entry.delete(0, 'end')
    pr_edit_weight_entry.delete(0, 'end')
    pr_edit_name_entry.delete(0, 'end')


def clear_edit_entries():
    edit_name_exercise_entry.delete(0, 'end')
    edit_reps_entry.delete(0, 'end')
    edit_sets_entry.delete(0, 'end')
    edit_weight_entry.delete(0, 'end')


def raise_main_frame():
    main_frame.pack(anchor="w", fill="both", expand=True)
    workout_frame.pack_forget()


def raise_workout_frame():
    data = get_workout_data(os.path.join(path, workout_option_menu.get() + ".json"))
    if str(data) != "{}":
        progressbar.set(0)
        current_workout_step_label.configure(text="Press START to begin")
        info_label.configure(text="")
        next_step_button.configure(text="START")
        workout_frame.pack(anchor="w", fill="both", expand=True)
        main_frame.pack_forget()
        create_exercises_lists()
    else:
        messagebox.showerror("PyFit", "The selected workout doesn't contain any data.\nSelect another workout or edit the current one.")


def quit_me():
    print('quit')
    app.quit()
    app.destroy()


def main():
    check_for_updates(False)
    view_workout()
    view_pr()
    app.mainloop()


check_files()

# App settings + layout
app = ctk.CTk()

width = 1280
height = 720

width_screen = app.winfo_screenwidth()
height_screen = app.winfo_screenheight()

spawn_x = int((width_screen / 2) - (width / 2))
spawn_y = int((height_screen / 2) - (height / 2))

app.geometry(f"{width}x{height}+{spawn_x}+{spawn_y}")
app.title("PyFit")

with open(os.path.join(main_path, "settings.json")) as settings_file:
    settings_data = json.load(settings_file)

print(f'setting theme to {str(settings_data["theme"]).lower()}')
ctk.set_appearance_mode(str(settings_data["theme"]).lower())

app.configure(bg=("#f2f2f2", "#202020"))
app.resizable(False, False)

app.protocol("WM_DELETE_WINDOW", quit_me)

img = PhotoImage(file='media/icon.ico')
app.tk.call('wm', 'iconphoto', app._w, img)

# Initialize fonts
pyfit_label_font = ctk.CTkFont(family="Segoe UI", size=40)
current_workout_step_label_font = ctk.CTkFont(family="Segoe UI", size=100)
info_label_font = ctk.CTkFont(family="Segoe UI", size=50)
return_button_font = ctk.CTkFont(family="Segoe UI", size=18)

# Initialize icons
settings_icon = ctk.CTkImage(light_image=Image.open("media/icons/settings_black.png"),
                             dark_image=Image.open("media/icons/settings_white.png"),
                             size=(19, 19))

dumbbell_icon = ctk.CTkImage(light_image=Image.open("media/icons/dumbbell_black.png"),
                             dark_image=Image.open("media/icons/dumbbell_white.png"),
                             size=(19, 19))

edit_icon = ctk.CTkImage(light_image=Image.open("media/icons/edit_black.png"),
                         dark_image=Image.open("media/icons/edit_white.png"),
                         size=(19, 19))

export_icon = ctk.CTkImage(light_image=Image.open("media/icons/export_black.png"),
                           dark_image=Image.open("media/icons/export_white.png"),
                           size=(19, 19))

import_icon = ctk.CTkImage(light_image=Image.open("media/icons/import_black.png"),
                           dark_image=Image.open("media/icons/import_white.png"),
                           size=(19, 19))

delete_icon = ctk.CTkImage(light_image=Image.open("media/icons/delete_black.png"),
                           dark_image=Image.open("media/icons/delete_white.png"),
                           size=(19, 19))

update_icon = ctk.CTkImage(light_image=Image.open("media/icons/update_black.png"),
                           dark_image=Image.open("media/icons/update_white.png"),
                           size=(19, 19))

reset_icon = ctk.CTkImage(light_image=Image.open("media/icons/reset_black.png"),
                          dark_image=Image.open("media/icons/reset_white.png"),
                          size=(19, 19))

add_icon = ctk.CTkImage(light_image=Image.open("media/icons/add_black.png"),
                        dark_image=Image.open("media/icons/add_white.png"),
                        size=(19, 19))

back_icon = ctk.CTkImage(light_image=Image.open("media/icons/back_black.png"),
                         dark_image=Image.open("media/icons/back_white.png"),
                         size=(19, 19))

# mainFrame view
main_frame = ctk.CTkFrame(app, fg_color=("#f2f2f2", "#202020"))
main_frame.pack(anchor="w", fill="both", expand=True)

# Tabview

tabview = ctk.CTkTabview(master=main_frame, fg_color=("#e2e2e2", "#333333"), segmented_button_selected_color="#3C99DC", text_color=("black", "white"),
                         corner_radius=10, width=600)
tabview.pack(anchor="w", fill="y", expand=True, side="left", padx=20, pady=(2, 20))

tabview.add("Home")
tabview.add("Personal records")
tabview.add("Records history")
tabview.add("Settings")
tabview.set("Home")

viewer_frame = ctk.CTkFrame(master=main_frame, fg_color=("#e2e2e2", "#333333"), corner_radius=10, width=600)
viewer_frame.pack(anchor="w", fill="y", expand=True, side="right", padx=20, pady=20)

pyfit_label = ctk.CTkLabel(master=tabview.tab("Home"), text=f"PyFit", font=pyfit_label_font)
pyfit_label.place(relx=0.5, rely=0.04, anchor=ctk.CENTER)

select_workout_label = ctk.CTkLabel(master=tabview.tab("Home"), text_color=("black", "white"), text="Select workout: ")
select_workout_label.place(relx=0.03, rely=0.095, anchor=ctk.W)

workout_option_menu = ctk.CTkOptionMenu(master=tabview.tab("Home"), fg_color="#3C99DC", text_color=("black", "white"), dynamic_resizing=False,
                                        values=get_stored_workouts(),
                                        command=workout_option_menu_selection)
workout_option_menu.place(relx=0.03, rely=0.145, anchor=ctk.W)

create_new_workout_button = ctk.CTkButton(master=tabview.tab("Home"), fg_color="#3C99DC", image=add_icon, compound="left", text_color=("black", "white"),
                                          text="Create new workout",
                                          command=create_new_workout_file)
create_new_workout_button.place(relx=0.425, rely=0.145, anchor=ctk.CENTER)

remove_workout_button = ctk.CTkButton(master=tabview.tab("Home"), width=80, fg_color="#3C99DC", image=delete_icon, compound="left",
                                      text_color=("black", "white"),
                                      text="Remove",
                                      command=remove_workout)
remove_workout_button.place(relx=0.66, rely=0.145, anchor=ctk.CENTER)

# Add new step to workout
add_new_step_label = ctk.CTkLabel(master=tabview.tab("Home"), text="Add new step to workout: ")
add_new_step_label.place(relx=0.03, rely=0.22, anchor=ctk.W)
name_exercise_entry = ctk.CTkEntry(master=tabview.tab("Home"), border_color=("#b2b2b2", "#535353"), placeholder_text_color=("#858585", "#afafaf"),
                                   text_color=("black", "white"), fg_color=("white", "#414141"), width=292, placeholder_text="Exercise name")
name_exercise_entry.place(relx=0.03, rely=0.27, anchor=ctk.W)
reps_entry = ctk.CTkEntry(master=tabview.tab("Home"), border_color=("#b2b2b2", "#535353"), placeholder_text_color=("#858585", "#afafaf"),
                          text_color=("black", "white"), fg_color=("white", "#414141"), width=292, placeholder_text="Amount of reps")
reps_entry.place(relx=0.03, rely=0.32, anchor=ctk.W)
sets_entry = ctk.CTkEntry(master=tabview.tab("Home"), border_color=("#b2b2b2", "#535353"), placeholder_text_color=("#858585", "#afafaf"),
                          text_color=("black", "white"),
                          fg_color=("white", "#414141"), width=292, placeholder_text="Amount of sets")
sets_entry.place(relx=0.03, rely=0.37, anchor=ctk.W)
weight_entry = ctk.CTkEntry(master=tabview.tab("Home"), border_color=("#b2b2b2", "#535353"), placeholder_text_color=("#858585", "#afafaf"),
                            text_color=("black", "white"),
                            fg_color=("white", "#414141"), width=292, placeholder_text="Weight (leave blank for no weight)")
weight_entry.place(relx=0.03, rely=0.42, anchor=ctk.W)

add_step_button = ctk.CTkButton(master=tabview.tab("Home"), width=292, fg_color="#3C99DC", image=add_icon, compound="left", text_color=("black", "white"),
                                text="Add step",
                                command=add_workout_step)
add_step_button.place(relx=0.03, rely=0.47, anchor=ctk.W)

# Edit or remove workout step
edit_remove_step_label = ctk.CTkLabel(master=tabview.tab("Home"), text="Edit or remove step: ")
edit_remove_step_label.place(relx=0.03, rely=0.545, anchor=ctk.W)

select_workout_step_menu = ctk.CTkOptionMenu(master=tabview.tab("Home"), width=292, fg_color="#3C99DC", text_color=("black", "white"), dynamic_resizing=False,
                                             values=get_workout_steps_names(),
                                             command=stored_workout_menu_selection)
select_workout_step_menu.place(relx=0.03, rely=0.595, anchor=ctk.W)

edit_name_exercise_entry = ctk.CTkEntry(master=tabview.tab("Home"), border_color=("#b2b2b2", "#535353"), placeholder_text_color=("#858585", "#afafaf"),
                                        text_color=("black", "white"),
                                        fg_color=("white", "#414141"), width=292, placeholder_text="Exercise name")
edit_name_exercise_entry.place(relx=0.03, rely=0.645, anchor=ctk.W)
edit_reps_entry = ctk.CTkEntry(master=tabview.tab("Home"), border_color=("#b2b2b2", "#535353"), placeholder_text_color=("#858585", "#afafaf"),
                               text_color=("black", "white"),
                               fg_color=("white", "#414141"), width=292,
                               placeholder_text="Amount of reps")
edit_reps_entry.place(relx=0.03, rely=0.695, anchor=ctk.W)
edit_sets_entry = ctk.CTkEntry(master=tabview.tab("Home"), border_color=("#b2b2b2", "#535353"), placeholder_text_color=("#858585", "#afafaf"),
                               text_color=("black", "white"),
                               fg_color=("white", "#414141"), width=292,
                               placeholder_text="Amount of sets")
edit_sets_entry.place(relx=0.03, rely=0.745, anchor=ctk.W)
edit_weight_entry = ctk.CTkEntry(master=tabview.tab("Home"), border_color=("#b2b2b2", "#535353"), placeholder_text_color=("#858585", "#afafaf"),
                                 text_color=("black", "white"),
                                 fg_color=("white", "#414141"),
                                 width=292, placeholder_text="Weight (no weight for selected step)")
edit_weight_entry.place(relx=0.03, rely=0.795, anchor=ctk.W)

edit_step_button = ctk.CTkButton(master=tabview.tab("Home"), fg_color="#3C99DC", image=edit_icon, compound="left", text_color=("black", "white"),
                                 text="Edit step",
                                 command=edit_workout_step)
edit_step_button.place(relx=0.03, rely=0.845, anchor=ctk.W)

remove_step_button = ctk.CTkButton(master=tabview.tab("Home"), fg_color="#3C99DC", image=delete_icon, compound="left", text_color=("black", "white"),
                                   text="Remove step",
                                   command=remove_workout_step)
remove_step_button.place(relx=0.29, rely=0.845, anchor=ctk.W)

start_workout_button = ctk.CTkButton(master=tabview.tab("Home"), fg_color="#3C99DC", image=dumbbell_icon, compound="left", text_color=("black", "white"),
                                     text="Start workout",
                                     command=raise_workout_frame)
start_workout_button.place(relx=0.5, rely=0.935, anchor=ctk.CENTER)

workout_label = ctk.CTkLabel(master=viewer_frame, text="Exercise")
workout_label.place(relx=0.20, rely=0.0325, anchor=ctk.CENTER)

reps_label = ctk.CTkLabel(master=viewer_frame, text="Reps")
reps_label.place(relx=0.45, rely=0.0325, anchor=ctk.CENTER)

sets_label = ctk.CTkLabel(master=viewer_frame, text="Sets")
sets_label.place(relx=0.65, rely=0.0325, anchor=ctk.CENTER)

weight_label = ctk.CTkLabel(master=viewer_frame, text="Weight (kg)")
weight_label.place(relx=0.85, rely=0.0325, anchor=ctk.CENTER)

exercise_text = ctk.CTkLabel(master=viewer_frame, width=150, height=200, text="", bg_color=("#e2e2e2", "#333333"), justify="left", anchor="nw")
exercise_text.place(relx=0.25, rely=0.075, anchor=ctk.N)

reps_text = ctk.CTkLabel(master=viewer_frame, width=80, text="", bg_color=("#e2e2e2", "#333333"), justify="center")
reps_text.place(relx=0.45, rely=0.075, anchor=ctk.N)

sets_text = ctk.CTkLabel(master=viewer_frame, text="", bg_color=("#e2e2e2", "#333333"), justify="center")
sets_text.place(relx=0.65, rely=0.075, anchor=ctk.N)

weight_text = ctk.CTkLabel(master=viewer_frame, text="", bg_color=("#e2e2e2", "#333333"), justify="center")
weight_text.place(relx=0.85, rely=0.075, anchor=ctk.N)

# workoutFrame view
workout_frame = ctk.CTkFrame(app, fg_color=("#f2f2f2", "#202020"))

progressbar = ctk.CTkProgressBar(master=workout_frame, fg_color=("#e2e2e2", "#333333"), progress_color="#3C99DC", height=15, width=app.winfo_width())
progressbar.place(relx=0.5, rely=0, anchor=ctk.N)

current_workout_step_label = ctk.CTkLabel(workout_frame, text="Press START to begin", font=current_workout_step_label_font)
current_workout_step_label.place(relx=0.50, rely=0.3, anchor=ctk.CENTER)
info_label = ctk.CTkLabel(workout_frame, text="", font=info_label_font)
info_label.place(relx=0.50, rely=0.5, anchor=ctk.CENTER)

next_step_button = ctk.CTkButton(master=workout_frame, fg_color="#3C99DC", width=300, height=125, text_color=("black", "white"), text="START",
                                 font=info_label_font, command=next_step)
next_step_button.place(relx=0.5, rely=0.85, anchor=ctk.CENTER)

return_button = ctk.CTkButton(master=workout_frame, fg_color="#3C99DC", width=50, height=25, text_color=("black", "white"), text="Return",
                              font=return_button_font,
                              command=raise_main_frame)
return_button.place(relx=0.0375, rely=0.055, anchor=ctk.CENTER)

# SettingsFrame view
settings_frame = ctk.CTkFrame(master=main_frame, fg_color=("#e2e2e2", "#333333"), corner_radius=10)

settings_label = ctk.CTkLabel(master=tabview.tab("Settings"), text=f"Settings", font=pyfit_label_font)
settings_label.place(relx=0.5, rely=0.04, anchor=ctk.CENTER)

theme_selection_default = str(settings_data["theme"])

select_theme_label = ctk.CTkLabel(master=tabview.tab("Settings"), text_color=("black", "white"), text="Choose theme: ")
select_theme_label.place(relx=0.03, rely=0.095, anchor=ctk.W)

theme_selection = ctk.CTkOptionMenu(master=tabview.tab("Settings"), fg_color="#3C99DC", text_color=("black", "white"), dynamic_resizing=False,
                                    values=["Light", "Dark", "System"],
                                    command=theme_option_selection)
theme_selection.place(relx=0.03, rely=0.145, anchor=ctk.W)
theme_selection.set(theme_selection_default)

check_for_updates_label = ctk.CTkLabel(master=tabview.tab("Settings"), text_color=("black", "white"), text="Check for updates:")
check_for_updates_label.place(relx=0.03, rely=0.22, anchor=ctk.W)

check_for_updates_button = ctk.CTkButton(master=tabview.tab("Settings"), fg_color="#3C99DC", image=update_icon, compound="left", text_color=("black", "white"),
                                         text="Check for updates",
                                         command=lambda: check_for_updates(True))
check_for_updates_button.place(relx=0.03, rely=0.27, anchor=ctk.W)

reset_app_label = ctk.CTkLabel(master=tabview.tab("Settings"), text_color=("black", "white"), text="Reset to factory settings:")
reset_app_label.place(relx=0.03, rely=0.345, anchor=ctk.W)

reset_app_button = ctk.CTkButton(master=tabview.tab("Settings"), fg_color="#3C99DC", image=reset_icon, compound="left", text_color=("black", "white"),
                                 text="Reset app",
                                 command=reset)
reset_app_button.place(relx=0.03, rely=0.395, anchor=ctk.W)

import_export_label = ctk.CTkLabel(master=tabview.tab("Settings"), text_color=("black", "white"), text="Import or export workouts:")
import_export_label.place(relx=0.03, rely=0.47, anchor=ctk.W)

import_exercises_button = ctk.CTkButton(master=tabview.tab("Settings"), fg_color="#3C99DC", image=import_icon, compound="left", text_color=("black", "white"),
                                        text="Import workouts",
                                        command=import_workouts)
import_exercises_button.place(relx=0.03, rely=0.52, anchor=ctk.W)

export_exercises_button = ctk.CTkButton(master=tabview.tab("Settings"), fg_color="#3C99DC", image=export_icon, compound="left", text_color=("black", "white"),
                                        text="Export workouts",
                                        command=export_workouts)
export_exercises_button.place(relx=0.415, rely=0.52, anchor=ctk.CENTER)

about_label = ctk.CTkLabel(master=tabview.tab("Settings"), text=f"This app has been made by Joran Vancoillie\nPyFit v{version}")
about_label.place(relx=0.5, rely=0.96, anchor=ctk.CENTER)

# Personal records view
personal_records_label = ctk.CTkLabel(master=tabview.tab("Personal records"), text=f"Personal records", font=pyfit_label_font)
personal_records_label.place(relx=0.5, rely=0.04, anchor=ctk.CENTER)

pr_exercise_label = ctk.CTkLabel(master=tabview.tab("Personal records"), text="Exercise")
pr_exercise_label.place(relx=0.1, rely=0.125, anchor=ctk.W)

pr_weight_label = ctk.CTkLabel(master=tabview.tab("Personal records"), text="Weight (kg)")
pr_weight_label.place(relx=0.5, rely=0.125, anchor=ctk.CENTER)

pr_date_label = ctk.CTkLabel(master=tabview.tab("Personal records"), text="Date")
pr_date_label.place(relx=0.8, rely=0.125, anchor=ctk.CENTER)

pr_exercise_text = ctk.CTkLabel(master=tabview.tab("Personal records"), width=225, height=200, text="", bg_color=("#e2e2e2", "#333333"), justify="left",
                                anchor="nw")
pr_exercise_text.place(relx=0.225, rely=0.175, anchor=ctk.N)

pr_weight_text = ctk.CTkLabel(master=tabview.tab("Personal records"), width=80, text="", bg_color=("#e2e2e2", "#333333"), justify="center")
pr_weight_text.place(relx=0.50, rely=0.175, anchor=ctk.N)

pr_date_text = ctk.CTkLabel(master=tabview.tab("Personal records"), width=80, text="", bg_color=("#e2e2e2", "#333333"), justify="center")
pr_date_text.place(relx=0.8, rely=0.175, anchor=ctk.N)

# Add new record
pr_add_label = ctk.CTkLabel(master=tabview.tab("Personal records"), text_color=("black", "white"), text="Add new record:")
pr_add_label.place(relx=0.03, rely=0.500, anchor=ctk.W)

pr_add_name_entry = ctk.CTkEntry(master=tabview.tab("Personal records"), border_color=("#b2b2b2", "#535353"), placeholder_text_color=("#858585", "#afafaf"),
                                 text_color=("black", "white"),
                                 fg_color=("white", "#414141"), width=292, placeholder_text="Record name")
pr_add_name_entry.place(relx=0.03, rely=0.550, anchor=ctk.W)
pr_add_weight_entry = ctk.CTkEntry(master=tabview.tab("Personal records"), border_color=("#b2b2b2", "#535353"), placeholder_text_color=("#858585", "#afafaf"),
                                   text_color=("black", "white"),
                                   fg_color=("white", "#414141"), width=292,
                                   placeholder_text="Record weight")
pr_add_weight_entry.place(relx=0.03, rely=0.600, anchor=ctk.W)

pr_add_record_button = ctk.CTkButton(master=tabview.tab("Personal records"), fg_color="#3C99DC", width=292, image=add_icon, compound="left",
                                     text_color=("black", "white"), text="Add record",
                                     command=add_pr)
pr_add_record_button.place(relx=0.03, rely=0.650, anchor=ctk.W)

# Edit or remove record
pr_edit_label = ctk.CTkLabel(master=tabview.tab("Personal records"), text_color=("black", "white"), text="Update or remove record:")
pr_edit_label.place(relx=0.03, rely=0.725, anchor=ctk.W)

select_pr_menu = ctk.CTkOptionMenu(master=tabview.tab("Personal records"), width=292, fg_color="#3C99DC", text_color=("black", "white"), dynamic_resizing=False,
                                   values=get_pr_names(),
                                   command=pr_menu_selection)
select_pr_menu.place(relx=0.03, rely=0.775, anchor=ctk.W)

pr_edit_name_entry = ctk.CTkEntry(master=tabview.tab("Personal records"), border_color=("#b2b2b2", "#535353"), placeholder_text_color=("#858585", "#afafaf"),
                                  text_color=("black", "white"),
                                  fg_color=("white", "#414141"), width=292, placeholder_text="Record name")
pr_edit_name_entry.place(relx=0.03, rely=0.825, anchor=ctk.W)
pr_edit_weight_entry = ctk.CTkEntry(master=tabview.tab("Personal records"), border_color=("#b2b2b2", "#535353"), placeholder_text_color=("#858585", "#afafaf"),
                                    text_color=("black", "white"),
                                    fg_color=("white", "#414141"), width=292,
                                    placeholder_text="Record weight")
pr_edit_weight_entry.place(relx=0.03, rely=0.875, anchor=ctk.W)

pr_edit_record_button = ctk.CTkButton(master=tabview.tab("Personal records"), fg_color="#3C99DC", image=edit_icon, compound="left",
                                      text_color=("black", "white"), text="Update record",
                                      command=edit_pr)
pr_edit_record_button.place(relx=0.03, rely=0.925, anchor=ctk.W)

pr_remove_record_button = ctk.CTkButton(master=tabview.tab("Personal records"), fg_color="#3C99DC", image=delete_icon, compound="left",
                                        text_color=("black", "white"),
                                        text="Remove record",
                                        command=remove_pr)
pr_remove_record_button.place(relx=0.29, rely=0.925, anchor=ctk.W)

# Records history view
history_label = ctk.CTkLabel(master=tabview.tab("Records history"), text=f"Records history", font=pyfit_label_font)
history_label.place(relx=0.5, rely=0.04, anchor=ctk.CENTER)

select_graph_menu = ctk.CTkOptionMenu(master=tabview.tab("Records history"), width=200, fg_color="#3C99DC", text_color=("black", "white"),
                                      dynamic_resizing=False,
                                      values=get_pr_names(), command=print("generate graph"))
select_graph_menu.place(relx=0.03, rely=0.125, anchor=ctk.W)

generate_graph_button = ctk.CTkButton(master=tabview.tab("Records history"), fg_color="#3C99DC", image=update_icon, compound="left",
                                      text_color=("black", "white"), text="Generate graph", command=generate_graph)
generate_graph_button.place(relx=0.39, rely=0.125, anchor=ctk.W)

graph_frame = ctk.CTkFrame(master=tabview.tab("Records history"), fg_color=("#e2e2e2", "#333333"), height=525, width=300)
graph_frame.place(relx=0.5, rely=0.975, anchor=ctk.S)
# generate_graph

if __name__ == "__main__":
    main()
