import subprocess
import threading

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

# Saved the command output as a dictionary.
cmd_output = {}


def run_command(command, cid):
    # Run the command, grab the results.
    process = subprocess.Popen(
        command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    stdout, stderr = process.communicate()
    # Combine regular and error messages.
    output = stdout + "\n" + (stderr if stderr else "")
    # Save everything in a dictionary.
    cmd_output[cid] = output


@app.route("/")
def index():
    # Render the homepage template.
    return render_template("index.html")


@app.route("/run_command", methods=["POST"])
def run_cmd():
    # Fetch the command from the form.
    command = request.form["command"]
    # Generate a unique command ID.
    cid = str(threading.get_ident())
    # Execute the command in a separate thread to avoid interrupting the main process.
    thread = threading.Thread(target=run_command, args=(command, cid))
    thread.start()
    # Redirect to the output page.
    return redirect(url_for("output", cid=cid))


@app.route("/output/<cid>")
def output(cid):
    # Wait for the command to finish and provide the result.
    while cid not in cmd_output:
        pass
    # Retrieve the command output and remove it from the dictionary.
    output = cmd_output.pop(cid, "No output available.")
    # Format and display the output using the designated template.
    return render_template("output.html", output=output)


if __name__ == "__main__":
    app.run(debug=True)
