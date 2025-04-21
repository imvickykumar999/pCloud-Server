from flask import Flask, request, jsonify, render_template_string
import os

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>File Processor</title>
    <style>
        body {
            font-family: 'Roboto', sans-serif;
            background-color: #e9ecef;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background-color: #ffffff;
            width: 90%;
            max-width: 500px;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        h1 {
            text-align: center;
            color: #495057;
            margin-bottom: 20px;
        }
        form {
            display: flex;
            flex-direction: column;
        }
        label {
            font-weight: bold;
            margin-top: 10px;
            color: #343a40;
        }
        input, select, button {
            width: 100%;
            padding: 12px;
            margin-top: 5px;
            margin-bottom: 15px;
            border: 1px solid #ced4da;
            border-radius: 5px;
            box-sizing: border-box;
            font-size: 1rem;
        }
        button {
            background-color: #007bff;
            color: #fff;
            font-weight: bold;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        button:hover {
            background-color: #0056b3;
        }
        .optional-section {
            display: none;
            margin-top: 10px;
        }
        .optional-section input {
            margin-bottom: 10px;
        }
        #loader {
            display: none;
            text-align: center;
        }
        #loader img {
            width: 50px;
            height: 50px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>File Processor</h1>
        <form action="/" method="post" id="fileForm">
            <label for="database_name">Database Name:</label>
            <input type="text" id="database_name" name="database_name" placeholder="Enter Database Name" required>

            <label for="command">Command:</label>
            <select id="command" name="command" required>
                <option value="">-- Select Your Choice --</option>
                <option value="zip">Zip Password</option>
                <option value="list">Link Password</option>
                <option value="merge">Merge CSV Files</option>
            </select>

            <div id="zip-options" class="optional-section">
                <label for="folder_path">Folder Path:</label>
                <input type="text" id="folder_path" name="folder_path" placeholder="Enter Folder Path">
            </div>

            <div id="list-options" class="optional-section">
                <label for="folder_id">Folder ID:</label>
                <input type="text" id="folder_id" name="folder_id" placeholder="Enter Folder ID">

                <label for="access_token">Access Token:</label>
                <input type="text" id="access_token" name="access_token" placeholder="Enter Access Token">
            </div>

            <button type="submit">Execute</button>
        </form>
        <div id="loader">
            <p>Processing...</p>
            <img src="https://i.gifer.com/ZKZg.gif" alt="Loading...">
        </div>
    </div>

    <script>
        const commandSelect = document.getElementById("command");
        const zipOptions = document.getElementById("zip-options");
        const listOptions = document.getElementById("list-options");
        const form = document.getElementById("fileForm");
        const loader = document.getElementById("loader");

        commandSelect.addEventListener("change", function () {
            zipOptions.style.display = "none";
            listOptions.style.display = "none";

            if (this.value === "zip") {
                zipOptions.style.display = "block";
            } else if (this.value === "list") {
                listOptions.style.display = "block";
            }
        });

        form.addEventListener("submit", function () {
            loader.style.display = "block";
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/', methods=['POST'])
def execute():
    try:
        database_name = request.form.get('database_name')
        command = request.form.get('command')
        folder_path = request.form.get('folder_path')
        folder_id = request.form.get('folder_id')
        access_token = request.form.get('access_token')

        base_command = f"python3 file_processor.py \"{database_name}\" {command}"
        
        if command == "zip" and folder_path:
            os.system(f"{base_command} --folder_path \"{folder_path}\"")
        elif command == "list" and folder_id and access_token:
            os.system(f"{base_command} --folder_id \"{folder_id}\" --access_token \"{access_token}\"")
        elif command == "merge":
            os.system(base_command)
        else:
            return jsonify({"status": "error", "message": "Invalid command or missing arguments."})

        return render_template_string(HTML_TEMPLATE)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    app.run(debug=True)

