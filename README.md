# PyFit
A Python app that displays your workout routine step by step.

It shows you the current exercise and set.

In the future, you'll be able to add new workout routines right inside the app.

# How to change the default exercise

Right now, there's only a default exercise that you can only change if you build the app yourself. You'll have to change the `exercise.json` file to add your own workout routine.

# Requirements to build
You need `py2app` to compile the app yourself.

Use `pip install py2app` to install it.

From the root of the project folder, run `python setup.py py2app -A` in the terminal to compile the app in Alias mode. The app is ready to open and test in the `dist` folder.

If everything works fine, and you want to create a stand-alone version, you have to remove the build and dist folder (`rm -rf build dist`). Then run `python setup.py py2app` to build the app. The stand-alone build is available in the `dist` folder.
