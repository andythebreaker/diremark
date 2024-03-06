import subprocess
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy, QVBoxLayout, QWidget, QPushButton,QSystemTrayIcon, QMenu
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QIcon

import os
import tkinter as tk
from tkinter import ttk, filedialog
from datetime import datetime
import hashlib
import json
import base64

from bs4 import BeautifulSoup

def open_file_with_default_program(file_path):
        try:
            # Use the 'start' command to open the file with the default program
            subprocess.run(['start', '', file_path], check=True, shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")

def add_table_row(old_html, col1, col2, col3, col4,classType):
    soup = BeautifulSoup(old_html, 'html.parser')
    table_body = soup.find('tbody', {'id': 'file_table'})
    new_row = soup.new_tag('tr')
    cell = soup.new_tag('td')
    cell.string = col1
    cell['id'] = col3
    cell['onclick'] = "winOpen(this)"
    new_row.append(cell)
    cell=soup.new_tag('td')
    cell.string=classType
    cell['id']=col2#dummy
    cell['class'] = "b64"
    cell['onclick']="editClassType(this)"
    new_row.append(cell)
    cell = soup.new_tag('td')
    cell.string = col4
    cell['onclick'] = "editRemark(this)"
    cell['class'] = "b64"
    new_row.append(cell)
    table_body.append(new_row)
    new_html_string = str(soup)

    return new_html_string

def create_or_update_diremark_file(dir_path, sha_string, remark_string):
    remark_file_path = os.path.join(dir_path, ".diremark")
    # Check if ".diremark" file exists
    if not os.path.exists(remark_file_path):
        # If not, create the file
        with open(remark_file_path, 'w') as remark_file:
            json.dump([], remark_file)  # Initialize with an empty list
    # Read existing content from the file
    with open(remark_file_path, 'r') as remark_file:
        data = json.load(remark_file)
    # Check if sha is not in the file, add json object {sha_string, remark_string}
    if sha_string not in [entry.get("sha") for entry in data]:
        new_entry = {"sha": sha_string, "remark": remark_string}
        data.append(new_entry)
        try:
            # Write the updated content back to the file
            with open(remark_file_path, 'w') as remark_file:
                json.dump(data, remark_file, indent=2)  # You can adjust the indent as needed
                return remark_string
        except Exception as e:
            return f"Error updating file: {str(e)}"
    else:
        for entry in data:
            if entry.get("sha") == sha_string:
                #if remark_string is empty
                if remark_string == "":
                    return entry.get("remark")
                else:
                    #update file
                    entry["remark"] = remark_string
                    try:
                        # Write the updated content back to the file
                        with open(remark_file_path, 'w') as remark_file:
                            json.dump(data, remark_file, indent=2)  # You can adjust the indent as needed
                            return remark_string
                    except Exception as e:
                        return f"Error updating file: {str(e)}"

        return "EOF ERROR"



class BrowserApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.dirname=None

        self.browser = QWebEngineView()
        self.browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.central_widget = QWidget()
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.addWidget(self.browser)

        #add a button
        self.button = QPushButton("Sel Dir")
        self.button.clicked.connect(self.Sel_Dir)
        self.layout.addWidget(self.button)

        self.setCentralWidget(self.central_widget)

        self.html_string = """<!DOCTYPE html>
<html lang="zh-tw">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>0</title>
    <style>
        table {
            border-collapse: collapse;
            width: 100%;
        }

        th, td {
            border: 1px solid black;
            padding: 8px;
            text-align: left;
        }

        .hidden {
            display: none;
        }
    </style>
</head>
<body>
    <table>
        <thead>
            <tr>
                <th>File Name</th>
                <th>classType</th>
                <!--th>Date Created</th>
                <th>SHA256</th-->
                <th>Remark</th>
            </tr>
        </thead>
        <tbody id="file_table">
        </tbody>
    </table>
    <script>
        function editRemark(cell) {
            // Get the current remark text
            var currentRemark = cell.innerText;
            // Create an input element
            var input = document.createElement("input");
            input.type = "text";
            input.value = currentRemark;
            // Replace the cell's text with the input element
            cell.innerText = "";
            cell.appendChild(input);
            input.focus();
            // Add an event listener to the input element
            input.addEventListener("blur", function() {
                // When the input element loses focus, save the new remark
                var newRemark = input.value;
                cell.removeChild(input);
                cell.innerText = newRemark;
                // Update the remark in the .diremark file
                var shaString = cell.parentElement.children[0].id;
                var classType_value = cell.parentElement.children[1].innerText;
var rmk=JSON.stringify({classType:window.btoa(encodeURIComponent( escape( classType_value ))),content:window.btoa(encodeURIComponent( escape( newRemark )))});

                document.title = JSON.stringify({PYfucn:'create_or_update_diremark_file',sha: shaString, remark: btoa(rmk)});
            });
        }

function editClassType(cell) {
    // Get the current class type text
    var currentClassType = cell.innerText;
    
    // Create an input element
    var input = document.createElement("input");
    input.type = "text";
    input.value = currentClassType;
    
    // Replace the cell's text with the input element
    cell.innerText = "";
    cell.appendChild(input);
    input.focus();
    
    // Add an event listener to the input element
    input.addEventListener("blur", function() {
        // When the input element loses focus, save the new class type
        var newClassType = input.value;
        
        // Remove the input element and set the cell's text to the new class type
        cell.removeChild(input);
        cell.innerText = newClassType;
        
        // Update the class type in the .diremark file
        var shaString = cell.parentElement.children[0].id;
        var remarkValue = cell.parentElement.children[2].innerText; // Assuming the remark is the third child
        var rmk = JSON.stringify({
            classType: window.btoa(encodeURIComponent(escape(newClassType))),
            content: window.btoa(encodeURIComponent(escape(remarkValue)))
        });

        document.title = JSON.stringify({
            PYfucn: 'create_or_update_diremark_file',
            sha: shaString,
            remark: btoa(rmk)
        });
    });
}


        function winOpen(cell) {
            var filename = cell.parentElement.children[0].innerText;
            document.title = JSON.stringify({PYfucn:'open_file_with_default_program',filename:filename});
                }
        document.addEventListener('DOMContentLoaded', function () {
  // Select all elements with class "b64"
  var elements = document.querySelectorAll('.b64');

  // Loop through each element and decode its content
  elements.forEach(function (element) {
    // Get the base64-encoded content
    var base64Content = element.textContent.trim();

    // Decode the base64 content using atob
    var decodedContent = unescape(decodeURIComponent(window.atob( base64Content )));

    // Update the element's content with the decoded value
    element.textContent = decodedContent;
  });
});
    </script>
</body>
</html>

        """
        self.browser.setHtml(self.html_string)

        # Connect to the titleChanged signal
        self.browser.titleChanged.connect(self.handleTitleChanged)

    def Sel_Dir(self):
        directory_path = filedialog.askdirectory(title="Select Directory")
        if directory_path:
            print(directory_path)
            self.dirname=directory_path
            self.display_files(directory_path)

    def display_files(self, directory_path):
        # Get list of files in the selected directory
        file_list = os.listdir(directory_path)

        for file_name in file_list:
            file_path = os.path.join(directory_path, file_name)
            # Check if the item is a file (not a subdirectory)
            if os.path.isfile(file_path):
                # Get file creation date
                date_created = datetime.fromtimestamp(os.path.getctime(file_path)).strftime("%Y-%m-%d %H:%M:%S")
                # Calculate SHA256 hash
                sha256_hash = self.calculate_sha256(file_path)
                # Insert data into the table
                remarktext = create_or_update_diremark_file(directory_path,sha256_hash,"")
                #remarktext b64 to str
                # Decode Base64 to bytes
                decoded_bytes = base64.b64decode(remarktext)
                # Convert bytes to string
                decoded_string = decoded_bytes.decode('utf-8')
                #JSON phrase decoded_string
                
                try:
                    decoded_json = json.loads(decoded_string)
                    class_type_value = decoded_json.get("classType")
                    remarktext_value = decoded_json.get("content")
                    self.html_string = add_table_row(self.html_string, file_name, date_created, sha256_hash, remarktext_value, class_type_value)
                    self.browser.setHtml(self.html_string)
                except json.JSONDecodeError as e:
                    print("JSON load fail:", str(e))
                    self.html_string = add_table_row(self.html_string, file_name, date_created, sha256_hash, "", "")
                    self.browser.setHtml(self.html_string)

    def calculate_sha256(self, file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read and update hash string value in blocks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def handleTitleChanged(self, title):
        print(f"Title changed: {title}")
        #try-catch JSON.parse(title)
        try:
            data = json.loads(title)
            print(data)
            if data.get("PYfucn") == "create_or_update_diremark_file":
                sha_string = data.get("sha")
                remark_string = data.get("remark")
                create_or_update_diremark_file(self.dirname, sha_string, remark_string)
            elif data.get("PYfucn") == "open_file_with_default_program":
                filename = data.get("filename")
                open_file_with_default_program(os.path.join(self.dirname, filename))
        except Exception as e:
            print(f"Error parsing JSON: {str(e)}")

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = BrowserApp()
    # Set window title
    window.setWindowTitle("diremark")

    # Set window icon
    icon = QIcon("icon.png")
    window.setWindowIcon(icon)

    # Set system tray icon
    tray_icon = QSystemTrayIcon(icon, parent=app)
    tray_menu = QMenu()
    show_action = tray_menu.addAction("Show")
    exit_action = tray_menu.addAction("Exit")

    tray_icon.setContextMenu(tray_menu)

    show_action.triggered.connect(window.show)
    exit_action.triggered.connect(app.quit)

    tray_icon.show()
    window.setWindowIcon(icon)
    window.setGeometry(100, 100, 800, 600)
    window.show()
    sys.exit(app.exec_())
