import http.client as httplib
import json
import os
import shutil
import urllib.request
import webbrowser
from pathlib import Path
from subprocess import call
from tkinter import messagebox, filedialog

import PIL.Image
import customtkinter as ctk
import requests
from PIL import Image, ImageTk

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
    dialog = ctk.CTkInputDialog(master=None, text="Type in workout name:", title="New workout")
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


def get_workout_data(filename):
    with open(filename, "r") as file:
        return json.load(file)


def workout_option_menu_selection(choice):
    view_workout()


def stored_workout_menu_selection(choice):
    update_entries()


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
    update_button_icons(str(theme).lower())
    ctk.set_appearance_mode(str(theme).lower())


def update_button_icons(theme):
    if theme == "dark":
        button_theme = "white"
    else:
        button_theme = "black"

    if settings_button.image != button_theme:
        if settings_button.image == "white":
            settings_button.configure(image=settings_icon_black)
            start_workout_button.configure(image=dumbbell_icon_black)
            edit_step_button.configure(image=edit_icon_black)
            import_exercises_button.configure(image=import_icon_black)
            export_exercises_button.configure(image=export_icon_black)
            remove_step_button.configure(image=delete_icon_black)
            remove_workout_button.configure(image=delete_icon_black)
            check_for_updates_button.configure(image=update_icon_black)
            reset_app_button.configure(image=reset_icon_black)
            create_new_workout_button.configure(image=add_icon_black)
            add_step_button.configure(image=add_icon_black)
            return_to_main_button.configure(image=back_icon_black)
            settings_button.image = "black"

        else:
            settings_button.configure(image=settings_icon_white)
            start_workout_button.configure(image=dumbbell_icon_white)
            edit_step_button.configure(image=edit_icon_white)
            import_exercises_button.configure(image=import_icon_white)
            export_exercises_button.configure(image=export_icon_white)
            remove_step_button.configure(image=delete_icon_white)
            remove_workout_button.configure(image=delete_icon_white)
            check_for_updates_button.configure(image=update_icon_white)
            reset_app_button.configure(image=reset_icon_white)
            create_new_workout_button.configure(image=add_icon_white)
            add_step_button.configure(image=add_icon_white)
            return_to_main_button.configure(image=back_icon_white)
            settings_button.image = "white"


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


def reset_workout_view():
    exercise_text.configure(text="")
    reps_text.configure(text="")
    sets_text.configure(text="")
    weight_text.configure(text="")


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
    next_step_button.set_text("START")
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
    next_step_button.set_text("Next step")
    if info_index == len(info_list):
        raise_main_frame()
        return
    if int(len(exercise_list[exercise_index])) > 25:
        current_workout_step_label.configure(text_font=('Segoe UI', 50))
    else:
        current_workout_step_label.configure(text_font=('Segoe UI', 100))
    current_workout_step_label.configure(text=exercise_list[exercise_index])
    exercise_index += 1
    info_label.configure(text=info_list[info_index])
    info_index += 1
    if info_index == len(info_list):
        next_step_button.set_text("Finish")


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
    if messagebox.askyesno("PyFit", f"Are you sure you want to continue? This will remove all custom workout files and reset all settings."):
        clear_entries()
        clear_edit_entries()
        remove_files()
        check_files()
        workout_option_menu.configure(values=get_stored_workouts())
        workout_option_menu.set(get_stored_workouts()[0])
        select_workout_step_menu.configure(values=get_workout_steps_names())
        select_workout_step_menu.set(get_workout_steps_names()[0])
        return_to_main_from_settings()
        ctk.set_appearance_mode("dark")
        update_button_icons("dark")
        theme_selection.set("Dark")
        app.update()
        view_workout()
        messagebox.showinfo("PyFit", "Reset complete")


def remove_files():
    shutil.rmtree(main_path)


def clear_entries():
    name_exercise_entry.delete(0, 'end')
    reps_entry.delete(0, 'end')
    sets_entry.delete(0, 'end')
    weight_entry.delete(0, 'end')


def clear_edit_entries():
    edit_name_exercise_entry.delete(0, 'end')
    edit_reps_entry.delete(0, 'end')
    edit_sets_entry.delete(0, 'end')
    edit_weight_entry.delete(0, 'end')


def raise_main_frame():
    main_frame.pack(anchor="w", fill="both", expand=True)
    workout_frame.pack_forget()


def return_to_main_from_settings():
    action_frame.pack(anchor="w", fill="both", expand=True, side="left", padx=20, pady=20)
    settings_frame.pack_forget()


def raise_workout_frame():
    data = get_workout_data(os.path.join(path, workout_option_menu.get() + ".json"))
    if str(data) != "{}":
        progressbar.set(0)
        current_workout_step_label.configure(text="Press START to begin")
        info_label.configure(text="")
        next_step_button.set_text("START")
        workout_frame.pack(anchor="w", fill="both", expand=True)
        main_frame.pack_forget()
        create_exercises_lists()
    else:
        messagebox.showerror("PyFit", "The selected workout doesn't contain any data.\nSelect another workout or edit the current one.")


def raise_settings_frame():
    settings_frame.pack(anchor="w", fill="both", expand=True, side="left", padx=20, pady=20)
    action_frame.pack_forget()


def main():
    check_for_updates(False)
    view_workout()
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

if str(settings_data["theme"].lower()) == "dark":
    icon_theme = "white"
else:
    icon_theme = "black"

app.configure(bg=("#f2f2f2", "#202020"))

# Initialize icons
settings_icon_initial = ImageTk.PhotoImage(Image.open(f"media/icons/settings_{icon_theme}.png").resize((20, 20), resample=PIL.Image.Resampling(1)))
settings_icon_white = ImageTk.PhotoImage(Image.open(f"media/icons/settings_white.png").resize((20, 20), resample=PIL.Image.Resampling(1)))
settings_icon_black = ImageTk.PhotoImage(Image.open(f"media/icons/settings_black.png").resize((20, 20), resample=PIL.Image.Resampling(1)))

dumbbell_icon_initial = ImageTk.PhotoImage(Image.open(f"media/icons/dumbbell_{icon_theme}.png").resize((20, 20), resample=PIL.Image.Resampling(1)))
dumbbell_icon_white = ImageTk.PhotoImage(Image.open(f"media/icons/dumbbell_white.png").resize((20, 20), resample=PIL.Image.Resampling(1)))
dumbbell_icon_black = ImageTk.PhotoImage(Image.open(f"media/icons/dumbbell_black.png").resize((20, 20), resample=PIL.Image.Resampling(1)))

edit_icon_initial = ImageTk.PhotoImage(Image.open(f"media/icons/edit_{icon_theme}.png").resize((20, 20), resample=PIL.Image.Resampling(1)))
edit_icon_white = ImageTk.PhotoImage(Image.open(f"media/icons/edit_white.png").resize((20, 20), resample=PIL.Image.Resampling(1)))
edit_icon_black = ImageTk.PhotoImage(Image.open(f"media/icons/edit_black.png").resize((20, 20), resample=PIL.Image.Resampling(1)))

export_icon_initial = ImageTk.PhotoImage(Image.open(f"media/icons/export_{icon_theme}.png").resize((20, 20), resample=PIL.Image.Resampling(1)))
export_icon_white = ImageTk.PhotoImage(Image.open(f"media/icons/export_white.png").resize((20, 20), resample=PIL.Image.Resampling(1)))
export_icon_black = ImageTk.PhotoImage(Image.open(f"media/icons/export_black.png").resize((20, 20), resample=PIL.Image.Resampling(1)))

import_icon_initial = ImageTk.PhotoImage(Image.open(f"media/icons/import_{icon_theme}.png").resize((20, 20), resample=PIL.Image.Resampling(1)))
import_icon_white = ImageTk.PhotoImage(Image.open(f"media/icons/import_white.png").resize((20, 20), resample=PIL.Image.Resampling(1)))
import_icon_black = ImageTk.PhotoImage(Image.open(f"media/icons/import_black.png").resize((20, 20), resample=PIL.Image.Resampling(1)))

delete_icon_initial = ImageTk.PhotoImage(Image.open(f"media/icons/delete_{icon_theme}.png").resize((20, 20), resample=PIL.Image.Resampling(1)))
delete_icon_white = ImageTk.PhotoImage(Image.open(f"media/icons/delete_white.png").resize((20, 20), resample=PIL.Image.Resampling(1)))
delete_icon_black = ImageTk.PhotoImage(Image.open(f"media/icons/delete_black.png").resize((20, 20), resample=PIL.Image.Resampling(1)))

update_icon_initial = ImageTk.PhotoImage(Image.open(f"media/icons/update_{icon_theme}.png").resize((20, 20), resample=PIL.Image.Resampling(1)))
update_icon_white = ImageTk.PhotoImage(Image.open(f"media/icons/update_white.png").resize((20, 20), resample=PIL.Image.Resampling(1)))
update_icon_black = ImageTk.PhotoImage(Image.open(f"media/icons/update_black.png").resize((20, 20), resample=PIL.Image.Resampling(1)))

reset_icon_initial = ImageTk.PhotoImage(Image.open(f"media/icons/reset_{icon_theme}.png").resize((20, 20), resample=PIL.Image.Resampling(1)))
reset_icon_white = ImageTk.PhotoImage(Image.open(f"media/icons/reset_white.png").resize((20, 20), resample=PIL.Image.Resampling(1)))
reset_icon_black = ImageTk.PhotoImage(Image.open(f"media/icons/reset_black.png").resize((20, 20), resample=PIL.Image.Resampling(1)))

add_icon_initial = ImageTk.PhotoImage(Image.open(f"media/icons/add_{icon_theme}.png").resize((20, 20), resample=PIL.Image.Resampling(1)))
add_icon_white = ImageTk.PhotoImage(Image.open(f"media/icons/add_white.png").resize((20, 20), resample=PIL.Image.Resampling(1)))
add_icon_black = ImageTk.PhotoImage(Image.open(f"media/icons/add_black.png").resize((20, 20), resample=PIL.Image.Resampling(1)))

back_icon_initial = ImageTk.PhotoImage(Image.open(f"media/icons/back_{icon_theme}.png").resize((20, 20), resample=PIL.Image.Resampling(1)))
back_icon_white = ImageTk.PhotoImage(Image.open(f"media/icons/back_white.png").resize((20, 20), resample=PIL.Image.Resampling(1)))
back_icon_black = ImageTk.PhotoImage(Image.open(f"media/icons/back_black.png").resize((20, 20), resample=PIL.Image.Resampling(1)))

# mainFrame view
main_frame = ctk.CTkFrame(app, fg_color=("#f2f2f2", "#202020"))
main_frame.pack(anchor="w", fill="both", expand=True)

action_frame = ctk.CTkFrame(master=main_frame, fg_color=("#e2e2e2", "#333333"), corner_radius=10)
action_frame.pack(anchor="w", fill="both", expand=True, side="left", padx=20, pady=20)

viewer_frame = ctk.CTkFrame(master=main_frame, fg_color=("#e2e2e2", "#333333"), corner_radius=10)
viewer_frame.pack(anchor="w", fill="both", expand=True, side="right", padx=20, pady=20)

pyfit_label = ctk.CTkLabel(master=action_frame, text=f"PyFit", text_font=('Segoe UI', 40))
pyfit_label.place(relx=0.5, rely=0.04, anchor=ctk.CENTER)

select_workout_label = ctk.CTkLabel(master=action_frame, text_color=("black", "white"), text="Select workout: ")
select_workout_label.place(relx=0, rely=0.095, anchor=ctk.W)

workout_option_menu = ctk.CTkOptionMenu(master=action_frame, fg_color="#3C99DC", dynamic_resizing=False, values=get_stored_workouts(),
                                        command=workout_option_menu_selection)
workout_option_menu.place(relx=0.15, rely=0.145, anchor=ctk.CENTER)

create_new_workout_button = ctk.CTkButton(master=action_frame, fg_color="#3C99DC", image=add_icon_initial, compound="left", text="Create new workout",
                                          command=create_new_workout_file)
create_new_workout_button.place(relx=0.425, rely=0.145, anchor=ctk.CENTER)

remove_workout_button = ctk.CTkButton(master=action_frame, width=80, fg_color="#3C99DC", image=delete_icon_initial, compound="left", text="Remove",
                                      command=remove_workout)
remove_workout_button.place(relx=0.66, rely=0.145, anchor=ctk.CENTER)

# Add new step to workout
add_new_step_label = ctk.CTkLabel(master=action_frame, text="Add new step to workout: ")
add_new_step_label.place(relx=0.03, rely=0.22, anchor=ctk.W)
name_exercise_entry = ctk.CTkEntry(master=action_frame, border_color=("#b2b2b2", "#535353"), placeholder_text_color=("#858585", "#afafaf"),
                                   text_color=("black", "white"), fg_color=("white", "#414141"), width=292, placeholder_text="Exercise name")
name_exercise_entry.place(relx=0.03, rely=0.27, anchor=ctk.W)
reps_entry = ctk.CTkEntry(master=action_frame, border_color=("#b2b2b2", "#535353"), placeholder_text_color=("#858585", "#afafaf"),
                          text_color=("black", "white"), fg_color=("white", "#414141"), width=292, placeholder_text="Amount of reps")
reps_entry.place(relx=0.03, rely=0.32, anchor=ctk.W)
sets_entry = ctk.CTkEntry(master=action_frame, border_color=("#b2b2b2", "#535353"), placeholder_text_color=("#858585", "#afafaf"),
                          text_color=("black", "white"),
                          fg_color=("white", "#414141"), width=292, placeholder_text="Amount of sets")
sets_entry.place(relx=0.03, rely=0.37, anchor=ctk.W)
weight_entry = ctk.CTkEntry(master=action_frame, border_color=("#b2b2b2", "#535353"), placeholder_text_color=("#858585", "#afafaf"),
                            text_color=("black", "white"),
                            fg_color=("white", "#414141"), width=292, placeholder_text="Weight (leave blank for no weight)")
weight_entry.place(relx=0.03, rely=0.42, anchor=ctk.W)

add_step_button = ctk.CTkButton(master=action_frame, width=292, fg_color="#3C99DC", image=add_icon_initial, compound="left", text="Add step",
                                command=add_workout_step)
add_step_button.place(relx=0.03, rely=0.47, anchor=ctk.W)

# Edit or remove workout step
edit_remove_step_label = ctk.CTkLabel(master=action_frame, text="Edit or remove step: ")
edit_remove_step_label.place(relx=0.0175, rely=0.545, anchor=ctk.W)

select_workout_step_menu = ctk.CTkOptionMenu(master=action_frame, width=292, fg_color="#3C99DC", dynamic_resizing=False, values=get_workout_steps_names(),
                                             command=stored_workout_menu_selection)
select_workout_step_menu.place(relx=0.03, rely=0.595, anchor=ctk.W)

edit_name_exercise_entry = ctk.CTkEntry(master=action_frame, border_color=("#b2b2b2", "#535353"), placeholder_text_color=("#858585", "#afafaf"),
                                        text_color=("black", "white"),
                                        fg_color=("white", "#414141"), width=292, placeholder_text="Exercise name")
edit_name_exercise_entry.place(relx=0.03, rely=0.645, anchor=ctk.W)
edit_reps_entry = ctk.CTkEntry(master=action_frame, border_color=("#b2b2b2", "#535353"), placeholder_text_color=("#858585", "#afafaf"),
                               text_color=("black", "white"),
                               fg_color=("white", "#414141"), width=292,
                               placeholder_text="Amount of reps")
edit_reps_entry.place(relx=0.03, rely=0.695, anchor=ctk.W)
edit_sets_entry = ctk.CTkEntry(master=action_frame, border_color=("#b2b2b2", "#535353"), placeholder_text_color=("#858585", "#afafaf"),
                               text_color=("black", "white"),
                               fg_color=("white", "#414141"), width=292,
                               placeholder_text="Amount of sets")
edit_sets_entry.place(relx=0.03, rely=0.745, anchor=ctk.W)
edit_weight_entry = ctk.CTkEntry(master=action_frame, border_color=("#b2b2b2", "#535353"), placeholder_text_color=("#858585", "#afafaf"),
                                 text_color=("black", "white"),
                                 fg_color=("white", "#414141"),
                                 width=292, placeholder_text="Weight (no weight for selected step)")
edit_weight_entry.place(relx=0.03, rely=0.795, anchor=ctk.W)

edit_step_button = ctk.CTkButton(master=action_frame, fg_color="#3C99DC", image=edit_icon_initial, compound="left", text="Edit step", command=edit_workout_step)
edit_step_button.place(relx=0.03, rely=0.845, anchor=ctk.W)

remove_step_button = ctk.CTkButton(master=action_frame, fg_color="#3C99DC", image=delete_icon_initial, compound="left", text="Remove step",
                                   command=remove_workout_step)
remove_step_button.place(relx=0.2825, rely=0.845, anchor=ctk.W)

settings_button = ctk.CTkButton(master=action_frame, fg_color="#3C99DC", width=100, image=settings_icon_initial, compound="left", text="Settings",
                                command=raise_settings_frame)
settings_button.place(relx=0.9, rely=0.035, anchor=ctk.CENTER)
settings_button.image = icon_theme

start_workout_button = ctk.CTkButton(master=action_frame, fg_color="#3C99DC", image=dumbbell_icon_initial, compound="left", text="Start workout",
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

current_workout_step_label = ctk.CTkLabel(workout_frame, text="Press START to begin", text_font=('Segoe UI', 100))
current_workout_step_label.place(relx=0.50, rely=0.3, anchor=ctk.CENTER)
info_label = ctk.CTkLabel(workout_frame, text="", text_font=('Segoe UI', 50))
info_label.place(relx=0.50, rely=0.5, anchor=ctk.CENTER)

next_step_button = ctk.CTkButton(master=workout_frame, fg_color="#3C99DC", width=300, height=125, text="START", text_font=('Segoe UI', 50), command=next_step)
next_step_button.place(relx=0.5, rely=0.85, anchor=ctk.CENTER)

return_button = ctk.CTkButton(master=workout_frame, fg_color="#3C99DC", width=50, height=25, text="Return", text_font=('Segoe UI', 18),
                              command=raise_main_frame)
return_button.place(relx=0.0375, rely=0.055, anchor=ctk.CENTER)

# SettingsFrame view
settings_frame = ctk.CTkFrame(master=main_frame, fg_color=("#e2e2e2", "#333333"), corner_radius=10)

settings_label = ctk.CTkLabel(master=settings_frame, text=f"Settings", text_font=('Segoe UI', 40))
settings_label.place(relx=0.5, rely=0.04, anchor=ctk.CENTER)

theme_selection_default = str(settings_data["theme"])

select_theme_label = ctk.CTkLabel(master=settings_frame, text_color=("black", "white"), text="Choose theme: ")
select_theme_label.place(relx=0, rely=0.095, anchor=ctk.W)

theme_selection = ctk.CTkOptionMenu(master=settings_frame, fg_color="#3C99DC", dynamic_resizing=False, values=["Light", "Dark", "System"],
                                    command=theme_option_selection)
theme_selection.place(relx=0.15, rely=0.145, anchor=ctk.CENTER)
theme_selection.set(theme_selection_default)

check_for_updates_label = ctk.CTkLabel(master=settings_frame, text_color=("black", "white"), text="Check for updates:")
check_for_updates_label.place(relx=0.015, rely=0.22, anchor=ctk.W)

check_for_updates_button = ctk.CTkButton(master=settings_frame, fg_color="#3C99DC", image=update_icon_initial, compound="left", text="Check for updates",
                                         command=lambda: check_for_updates(True))
check_for_updates_button.place(relx=0.165, rely=0.27, anchor=ctk.CENTER)

reset_app_label = ctk.CTkLabel(master=settings_frame, text_color=("black", "white"), text="Reset to factory settings:")
reset_app_label.place(relx=0.0325, rely=0.345, anchor=ctk.W)

reset_app_button = ctk.CTkButton(master=settings_frame, fg_color="#3C99DC", image=reset_icon_initial, compound="left", text="Reset app", command=reset)
reset_app_button.place(relx=0.15, rely=0.395, anchor=ctk.CENTER)

import_export_label = ctk.CTkLabel(master=settings_frame, text_color=("black", "white"), text="Import or export workouts:")
import_export_label.place(relx=0.0325, rely=0.47, anchor=ctk.W)

import_exercises_button = ctk.CTkButton(master=settings_frame, fg_color="#3C99DC", image=import_icon_initial, compound="left", text="Import workouts",
                                        command=import_workouts)
import_exercises_button.place(relx=0.1525, rely=0.52, anchor=ctk.CENTER)
# relx=0,03
export_exercises_button = ctk.CTkButton(master=settings_frame, fg_color="#3C99DC", image=export_icon_initial, compound="left", text="Export workouts",
                                        command=export_workouts)
export_exercises_button.place(relx=0.415, rely=0.52, anchor=ctk.CENTER)

about_label = ctk.CTkLabel(master=settings_frame, text=f"This app has been made by Joran Vancoillie\nPyFit v{version}")
about_label.place(relx=0.5, rely=0.96, anchor=ctk.CENTER)

return_to_main_button = ctk.CTkButton(master=settings_frame, width=75, fg_color="#3C99DC", image=back_icon_initial, compound="left", text="Return",
                                      command=return_to_main_from_settings)
return_to_main_button.place(relx=0.09, rely=0.035, anchor=ctk.CENTER)

if __name__ == "__main__":
    main()
