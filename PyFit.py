import json
import os
import tkinter as tk

import customtkinter as ctk

path = os.path.join(os.getenv("HOME"), "PyFit/workouts")


def check_files():
    # Check whether the specified path exists or not
    if not os.path.exists(path):
        os.makedirs(path)
        print("DIRECTORY CREATED")
    # Check if the needed files exist. If not, create them
    # workout_file = Path(os.path.join(path, "exercise.json"))
    # workout_file.touch(exist_ok=True)


def viewWorkoutButtonEvent():
    print("VIEW WORKOUT")
    # file = open(os.path.join(path, "exercise.json"), "r")
    file = open("exercise.json", "r")
    data = file.read()
    source = json.loads(data)
    exercises = source["exercises"]
    for exercise in exercises:
        exerciseTextData = exerciseText.cget("text") + exercise["name"] + "\n"
        exerciseText["text"] = exerciseTextData
        repsTextData = repsText.cget("text") + str(exercise["reps"]) + "\n"
        repsText["text"] = repsTextData
        setsTextData = setsText.cget("text") + str(exercise["sets"]) + "\n"
        setsText["text"] = setsTextData
        # print(f'name: {exercise["name"]}, reps: {exercise["reps"]}, sets: {exercise["sets"]}')


def raiseMainFrame():
    mainFrame.pack(anchor="w", fill="both", expand=True)
    workoutFrame.pack_forget()


def raiseWorkoutFrame():
    workoutFrame.pack(anchor="w", fill="both", expand=True)
    mainFrame.pack_forget()


exerciseStep = 0
exerciseSet = 0
totalRepCount = 0


def nextStep():
    nextStepButton.set_text("Next step")
    global exerciseStep
    global exerciseSet
    global totalRepCount
    file = open("exercise.json", "r")
    data = file.read()
    source = json.loads(data)
    exercises = source["exercises"]
    if totalRepCount == 0:
        print("first exercise")
        currentStepLabel["text"] = f"{exercises[exerciseStep]['reps']}x {exercises[exerciseStep]['name']}"
        currentSetLabel["text"] = f"set {exerciseSet} of {exercises[exerciseStep]['sets']}"
    if exerciseSet == exercises[exerciseStep]["sets"]:
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
        currentSetLabel["text"] = f"set {exerciseSet} of {exercises[exerciseStep]['sets']}"
        print(f"exerciseStep = {exerciseStep}, exerciseSet = {exerciseSet}, exerciseRep = {totalRepCount}")


def returnToMain():
    global exerciseStep
    global exerciseSet
    global totalRepCount
    exerciseStep = 0
    exerciseSet = 0
    totalRepCount = 0
    raiseMainFrame()
    currentStepLabel["text"] = "Press START to begin"
    currentSetLabel["text"] = ""
    nextStepButton.set_text("START")


def main():
    check_files()
    viewWorkoutButtonEvent()
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

startWorkoutButton = ctk.CTkButton(master=actionFrame, text="Start workout", command=raiseWorkoutFrame)
startWorkoutButton.place(relx=0.33, rely=0.9, anchor=ctk.CENTER)

viewWorkoutButton = ctk.CTkButton(master=actionFrame, text="View workout", command=viewWorkoutButtonEvent)
viewWorkoutButton.place(relx=0.66, rely=0.9, anchor=ctk.CENTER)

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
