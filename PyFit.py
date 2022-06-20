import json
import os
import tkinter as tk
from pathlib import Path

import customtkinter as ctk

path = os.path.join(os.getenv("HOME"), "PyFit/workouts")


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
            '{ "exercises": [ { "name": "Push-ups", "reps": 10, "sets": 5 }, { "name": "Leg raises", "reps": 30, "sets": 1 }, { "name": "Hip raises", "reps": 30, "sets": 1 }, { "name": "Toe touches", "reps": 30, "sets": 1 }, { "name": "Flutter kicks", "reps": 30, "sets": 1 }, { "name": "Sit-ups", "reps": 30, "sets": 1 }, { "name": "Pull-ups", "reps": 10, "sets": 1 }, { "name": "Chin-ups", "reps": 10, "sets": 1 }, { "name": "Biceps", "reps": 10, "sets": 1 }, { "name": "Forward fly", "reps": 10, "sets": 1 }, { "name": "Side fly", "reps": 10, "sets": 1 }, { "name": "Forearms", "reps": 50, "sets": 2 } ] }')
        file.close()


def createNewWorkoutFile():
    dialog = ctk.CTkInputDialog(master=None, text="Type in workout name:", title="New workout")
    filename = str(dialog.get_input()) + ".json"
    print("filename = " + filename)
    workout_file = Path(os.path.join(path, filename))
    workout_file.touch(exist_ok=True)
    workoutOptionMenu.configure(values=getStoredWorkouts())


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
    if data != '{"exercises": []}' and len(data) > 0:
        source = json.loads(data)
        exercises = source["exercises"]
        for exercise in exercises:
            exerciseTextData = exerciseText.cget("text") + exercise["name"] + "\n"
            exerciseText["text"] = exerciseTextData
            repsTextData = repsText.cget("text") + str(exercise["reps"]) + "\n"
            repsText["text"] = repsTextData
            setsTextData = setsText.cget("text") + str(exercise["sets"]) + "\n"
            setsText["text"] = setsTextData
    elif len(data) == 0:
        file = open(os.path.join(path, workoutOptionMenu.get()), "w")
        file.write('{"exercises": []}')
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
    else:
        file = open(os.path.join(path, workoutOptionMenu.get()), "r")
        data = file.read()
        file.close()
        source = json.loads(data)
        exercises = source["exercises"]
        exercise = '{"name": "' + str(name) + '", "reps": "' + str(reps) + '", "sets": "' + str(sets) + '"}'
        exercises.append(exercise)
        file = open(os.path.join(path, workoutOptionMenu.get()), "w")
        file.write('{"exercises": [')
        for index, item in enumerate(exercises):
            file.write(str(item).replace("'", '"'))
            if index + 1 < len(exercises):
                file.write(",")
        file.write(']}')
        file.close()
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
    file = open(os.path.join(path, "default.json"), "r")
    data = file.read()
    source = json.loads(data)
    exercises = source["exercises"]

    if totalRepCount == 0:
        print("first exercise")
        currentStepLabel["text"] = f"{exercises[exerciseStep]['reps']}x {exercises[exerciseStep]['name']}"
        currentSetLabel["text"] = f"set {exerciseSet} of {exercises[exerciseStep]['sets']}"
    if showRestScreen:
        print("SHOW REST SCREEN")
        currentStepLabel["text"] = "Rest"
        if exerciseSet == exercises[exerciseStep]["sets"]:
            if exerciseStep < len(exercises) - 1:
                currentSetLabel["text"] = f"Next up: {exercises[exerciseStep + 1]['reps']}x {exercises[exerciseStep + 1]['name']}"
            else:
                currentSetLabel["text"] = f'Click "Finish" to go back to main menu'
                nextStepButton.set_text("Finish")
        else:
            currentSetLabel["text"] = f"Next up: {exercises[exerciseStep]['reps']}x {exercises[exerciseStep]['name']}"
    elif exerciseSet == exercises[exerciseStep]["sets"]:
        print("+1 exercise")
        exerciseStep += 1
        exerciseSet = 1
        if exerciseStep < len(exercises):
            currentStepLabel["text"] = f"{exercises[exerciseStep]['reps']}x {exercises[exerciseStep]['name']}"
            currentSetLabel["text"] = f"set {exerciseSet} of {exercises[exerciseStep]['sets']}"
        else:
            print("END OF EXERCISE")
            returnToMain()
    else:
        print("+1 set")
        exerciseSet += 1
        totalRepCount += exercises[exerciseStep]["reps"]
        currentStepLabel["text"] = f"{exercises[exerciseStep]['reps']}x {exercises[exerciseStep]['name']}"
        currentSetLabel["text"] = f"set {exerciseSet} of {exercises[exerciseStep]['sets']}"
        print(f"exerciseStep = {exerciseStep}, exerciseSet = {exerciseSet}, exerciseRep = {totalRepCount}")
    showRestScreen = not showRestScreen


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
    check_files()
    viewWorkout()
    app.mainloop()


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
workoutOptionMenu.place(relx=0.375, rely=0.055, anchor=ctk.CENTER)
createNewWorkoutButton = ctk.CTkButton(master=actionFrame, text="Create new workout", command=createNewWorkoutFile)
createNewWorkoutButton.place(relx=0.675, rely=0.055, anchor=ctk.CENTER)

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

removeLastStepButton = ctk.CTkButton(master=actionFrame, text="Remove last step", command=viewWorkout)
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
