from app import create_app

app = create_app()

# This line of code allows me to execute the code when the file runs as a script
# Debug is set to be True: this allows me to get a debugger when I run into errors, it also enables me to  see my changes on the
# browser without having to run the file again
if __name__ == '__main__':
    app.run(debug=True)
