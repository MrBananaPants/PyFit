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
    # Check if the needed files exist. If not, create them
    workout_file = Path(os.path.join(path, "default.json"))
    workout_file.touch(exist_ok=True)
    if os.path.getsize(os.path.join(path, "default.json")) == 0:
        file = open(os.path.join(path, "default.json"), "a")
        file.write(
            '{ "Push-ups": [ 10, 5 ], "Leg Raises": [ 30, 1 ], "Hip raises": [ 30, 1 ], "Toe touches": [ 30, 1 ], "Flutter kicks": [ 30, 1 ], "Sit-ups": [ 30, 1 ], "Pull-ups": [ 10, 1 ], "Chin-ups": [ 10, 1 ], "Biceps": [ 10, 1 ], "Forward fly": [ 10, 1 ], "Side fly": [ 10, 1 ], "Forearms": [ 50, 2 ] }')
        file.close()


def createNewWorkoutFile():
    dialog = ctk.CTkInputDialog(master=None, text="Type in workout name:", title="New workout")
    filename = str(dialog.get_input()) + ".json"
    print("filename = " + filename)
    workout_file = Path(os.path.join(path, filename))
    workout_file.touch(exist_ok=True)
    workoutOptionMenu.configure(values=getStoredWorkouts())
    workoutOptionMenu.set(filename)


def getStoredWorkouts():
    foundWorkouts = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    print(foundWorkouts)
    foundWorkoutsNotHidden = []
    for workout in foundWorkouts:
        if workout[0] != ".":
            foundWorkoutsNotHidden.append(workout)
    print(foundWorkoutsNotHidden)
    return foundWorkoutsNotHidden


def comboboxSelection(choice):
    print("optionmenu dropdown clicked:", choice)
    viewWorkout()
    # workoutOptionMenu.set(choice)


def resetWorkoutView():
    exerciseText["text"] = ""
    repsText["text"] = ""
    setsText["text"] = ""


def viewWorkout():
    resetWorkoutView()
    print("VIEW WORKOUT")
    file = open(os.path.join(path, workoutOptionMenu.get()), "r")
    data = file.read()
    print(data)
    file.close()
    if data != '{}' and len(data) > 0:
        exercises = json.loads(data)
        keys = list(exercises)
        for key in keys:
            exerciseTextData = exerciseText.cget("text") + key + "\n"
            exerciseText["text"] = exerciseTextData
            repsTextData = repsText.cget("text") + str(exercises[key][0]) + "\n"
            repsText["text"] = repsTextData
            setsTextData = setsText.cget("text") + str(exercises[key][1]) + "\n"
            setsText["text"] = setsTextData
    elif len(data) == 0:
        file = open(os.path.join(path, workoutOptionMenu.get()), "w")
        file.write('{}')
        file.close()
        print("ADDED INITIAL JSON DATA TO FILE")
        exerciseText["text"] = "(empty)"
    else:
        exerciseText["text"] = "(empty)"


def addStepToWorkout():
    name = nameExerciseEntry.get()
    reps = repsEntry.get()
    sets = setsEntry.get()
    if name == "" or reps == "" or sets == "":
        create_toplevel("PyFit", "One or more of the fields haven't been filled in")
    elif not reps.isnumeric():
        create_toplevel("PyFit", "reps is not a number")
    elif not sets.isnumeric():
        create_toplevel("PyFit", "sets is not a number")
    else:
        file = open(os.path.join(path, workoutOptionMenu.get()), "r")
        data = file.read()
        file.close()
        exercises = json.loads(data)
        exercises[name] = [str(reps), str(sets)]
        with open(os.path.join(path, workoutOptionMenu.get()), "w") as outfile:
            json.dump(exercises, outfile)
    viewWorkout()


def removeLastStep():
    file = open(os.path.join(path, workoutOptionMenu.get()), "r")
    data = file.read()
    file.close()
    exercises = json.loads(data)
    if len(exercises) >= 1:
        del exercises[list(exercises)[-1]]
        with open(os.path.join(path, workoutOptionMenu.get()), "w") as outfile:
            json.dump(exercises, outfile)
    else:
        create_toplevel("PyFit", "Workout doesn't contain any steps")
    viewWorkout()


def create_toplevel(title, message):
    window = ctk.CTkToplevel()
    window.geometry("400x200")
    finishedwind = ctk.CTkLabel(window, text=message, text_font=('Segoe UI', 15))
    finishedwind.pack(side="top", fill="both", expand=True, padx=10, pady=10)
    window.title(title)


def raiseMainFrame():
    mainFrame.pack(anchor="w", fill="both", expand=True)
    workoutFrame.pack_forget()


def raiseWorkoutFrame():
    file = open(os.path.join(path, workoutOptionMenu.get()), "r")
    data = file.read()
    if len(data) != 0:
        workoutFrame.pack(anchor="w", fill="both", expand=True)
        mainFrame.pack_forget()
    else:
        create_toplevel("PyFit", "The selected workout doesn't contain any data.\nSelect another workout or edit the current one.")


exerciseStep = 0
exerciseSet = 0
totalRepCount = 0
showRestScreen = False


def nextStep():
    nextStepButton.set_text("Next step")
    global exerciseStep
    global exerciseSet
    global totalRepCount
    global showRestScreen
    file = open(os.path.join(path, workoutOptionMenu.get()), "r")
    data = file.read()
    exercises = json.loads(data)
    keys = list(exercises)

    if totalRepCount == 0:
        print("first exercise")
        currentStepLabel["text"] = f"{exercises[keys[exerciseStep]][0]}x {keys[exerciseStep]}"
        currentSetLabel["text"] = f"set {exerciseSet} of {exercises[keys[exerciseStep]][1]}"
    if showRestScreen:
        print("SHOW REST SCREEN")
        currentStepLabel["text"] = "Rest"
        if exerciseSet == int(exercises[keys[exerciseStep]][1]):
            if exerciseStep < len(exercises) - 1:
                currentSetLabel["text"] = f"Next up: {exercises[keys[exerciseStep + 1]][0]}x {keys[exerciseStep + 1]}"
            else:
                currentSetLabel["text"] = f'Click "Finish" to go back to main menu'
                nextStepButton.set_text("Finish")
        else:
            currentSetLabel["text"] = f"Next up: {exercises[keys[exerciseStep]][0]}x {keys[exerciseStep]}"
    elif exerciseSet == int(exercises[keys[exerciseStep]][1]):
        print("+1 exercise")
        exerciseStep += 1
        exerciseSet = 1
        if exerciseStep < len(exercises):
            currentStepLabel["text"] = f"{exercises[keys[exerciseStep]][0]}x {keys[exerciseStep]}"
            currentSetLabel["text"] = f"set {exerciseSet} of {exercises[keys[exerciseStep]][1]}"
        else:
            print("END OF EXERCISE")
            returnToMain()
    else:
        print("+1 set")
        exerciseSet += 1
        totalRepCount += int(exercises[keys[exerciseStep]][0])
        currentStepLabel["text"] = f"{exercises[keys[exerciseStep]][0]}x {keys[exerciseStep]}"
        currentSetLabel["text"] = f"set {exerciseSet} of {exercises[keys[exerciseStep]][1]}"
        print(f"exerciseStep = {exerciseStep}, exerciseSet = {exerciseSet}, exerciseRep = {totalRepCount}")
    showRestScreen = not showRestScreen


def checkForUpdates():
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
    shutil.rmtree(path)
    check_files()
    workoutOptionMenu.configure(values=getStoredWorkouts())
    workoutOptionMenu.set("default.json")
    messagebox.showinfo("PyFit", "Reset complete. Custom workouts have been removed.")


def showSettings():
    settingsWindow = ctk.CTkToplevel()
    settingsWindow.title("Settings")
    settingsWindow.geometry("400x200")
    checkForUpdatesButton = ctk.CTkButton(master=settingsWindow, text="Check for updates", command=checkForUpdates)
    checkForUpdatesButton.place(relx=0.5, rely=0.3, anchor=ctk.CENTER)

    checkForUpdatesButton = ctk.CTkButton(master=settingsWindow, text="Reset app", command=reset)
    checkForUpdatesButton.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    aboutLabel = ctk.CTkLabel(master=settingsWindow, text=f"This app has been made by Joran Vancoillie.\nPyFit v{version}")
    aboutLabel.place(relx=0.5, rely=0.85, anchor=ctk.CENTER)


def returnToMain():
    global exerciseStep
    global exerciseSet
    global totalRepCount
    global showRestScreen
    exerciseStep = 0
    exerciseSet = 0
    totalRepCount = 0
    showRestScreen = False
    raiseMainFrame()
    currentStepLabel["text"] = "Press START to begin"
    currentSetLabel["text"] = ""
    nextStepButton.set_text("START")


def main():
    viewWorkout()
    app.mainloop()


check_files()

# App settings + layout
app = ctk.CTk()
app.geometry("1100x650")
app.title("PyFit")
app.configure(bg="#212121")

# mainFrame view
mainFrame = ctk.CTkFrame(app, fg_color="#212121")
mainFrame.pack(anchor="w", fill="both", expand=True)

actionFrame = ctk.CTkFrame(master=mainFrame, fg_color="#E0E0E0", corner_radius=10)
actionFrame.pack(anchor="w", fill="both", expand=True, side="left", padx=20, pady=20)

viewerFrame = ctk.CTkFrame(master=mainFrame, fg_color="#757575", corner_radius=10)
viewerFrame.pack(anchor="w", fill="both", expand=True, side="right", padx=20, pady=20)

exerciseLabel = ctk.CTkLabel(master=actionFrame, text="Select workout: ")
exerciseLabel.place(relx=0.125, rely=0.055, anchor=ctk.CENTER)
workoutOptionMenu = ctk.CTkOptionMenu(master=actionFrame, values=getStoredWorkouts(), command=comboboxSelection)
workoutOptionMenu.place(relx=0.17, rely=0.105, anchor=ctk.CENTER)
createNewWorkoutButton = ctk.CTkButton(master=actionFrame, text="Create new workout", command=createNewWorkoutFile)
createNewWorkoutButton.place(relx=0.47, rely=0.105, anchor=ctk.CENTER)

settingsButton = ctk.CTkButton(master=actionFrame, width=80, text="Settings", command=showSettings)
settingsButton.place(relx=0.9, rely=0.035, anchor=ctk.CENTER)

exerciseLabel = ctk.CTkLabel(master=actionFrame, text="Edit selected workout: ")
exerciseLabel.place(relx=0.0125, rely=0.25, anchor=ctk.W)
nameExerciseEntry = ctk.CTkEntry(master=actionFrame, placeholder_text="Exercise name")
nameExerciseEntry.place(relx=0.03, rely=0.3, anchor=ctk.W)
repsEntry = ctk.CTkEntry(master=actionFrame, placeholder_text="Amount of reps")
repsEntry.place(relx=0.03, rely=0.36, anchor=ctk.W)
setsEntry = ctk.CTkEntry(master=actionFrame, placeholder_text="Amount of sets")
setsEntry.place(relx=0.03, rely=0.42, anchor=ctk.W)

addStepButton = ctk.CTkButton(master=actionFrame, text="Add step", command=addStepToWorkout)
addStepButton.place(relx=0.03, rely=0.48, anchor=ctk.W)

removeLastStepButton = ctk.CTkButton(master=actionFrame, text="Remove last step", command=removeLastStep)
removeLastStepButton.place(relx=0.325, rely=0.48, anchor=ctk.W)

startWorkoutButton = ctk.CTkButton(master=actionFrame, text="Start workout", command=raiseWorkoutFrame)
startWorkoutButton.place(relx=0.50, rely=0.925, anchor=ctk.CENTER)

exerciseLabel = ctk.CTkLabel(master=viewerFrame, text="Exercise", text_color="white")
exerciseLabel.place(relx=0.20, rely=0.025, anchor=ctk.CENTER)

repsLabel = ctk.CTkLabel(master=viewerFrame, text="Reps", text_color="white")
repsLabel.place(relx=0.50, rely=0.025, anchor=ctk.CENTER)

setsLabel = ctk.CTkLabel(master=viewerFrame, text="Sets", text_color="white")
setsLabel.place(relx=0.80, rely=0.025, anchor=ctk.CENTER)

exerciseText = tk.Label(master=viewerFrame, text="", fg="white", bg="#757575", justify="left")
exerciseText.place(relx=0.15, rely=0.075, anchor=ctk.N)

repsText = tk.Label(master=viewerFrame, text="", fg="white", bg="#757575", justify="left")
repsText.place(relx=0.50, rely=0.075, anchor=tk.N)

setsText = tk.Label(master=viewerFrame, text="", fg="white", bg="#757575", justify="left")
setsText.place(relx=0.80, rely=0.075, anchor=ctk.N)

# workoutFrame view
workoutFrame = ctk.CTkFrame(app, fg_color="#212121")

currentStepLabel = tk.Label(workoutFrame, text="Press START to begin", fg="white", bg="#212121", font=('Segoe UI', 100))
currentStepLabel.place(relx=0.50, rely=0.3, anchor=ctk.CENTER)
currentSetLabel = tk.Label(workoutFrame, text="", fg="white", bg="#212121", font=('Segoe UI', 50))
currentSetLabel.place(relx=0.50, rely=0.5, anchor=ctk.CENTER)

nextStepButton = ctk.CTkButton(master=workoutFrame, width=300, height=125, text="START", text_font=('Segoe UI', 50), command=nextStep)
nextStepButton.place(relx=0.5, rely=0.85, anchor=ctk.CENTER)

returnButton = ctk.CTkButton(master=workoutFrame, width=50, height=25, text="Return", text_font=('Segoe UI', 18), command=returnToMain)
returnButton.place(relx=0.05, rely=0.05, anchor=ctk.CENTER)

if __name__ == "__main__":
    main()
