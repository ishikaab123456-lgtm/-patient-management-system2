from flask import Flask, render_template_string, request, redirect
import csv, os

app = Flask(__name__)
DATA_FILE = "patients.csv"

# Queue (FIFO)
queue = []

# Create file if not exists
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID", "Name", "Age", "Gender", "Phone", "Disease"])

# HTML UI
HTML = '''
<!DOCTYPE html>
<html>
<head>
<title>Patient Management System</title>

<style>
body {
    font-family: Arial;
    background: #eef2f7;
    margin: 0;
}

h1 {
    background: #2c3e50;
    color: white;
    padding: 15px;
    text-align: center;
}

.container {
    width: 85%;
    margin: 20px auto;
}

.card {
    background: white;
    padding: 20px;
    margin-bottom: 20px;
    border-radius: 10px;
    box-shadow: 0px 3px 10px rgba(0,0,0,0.1);
}

input {
    padding: 10px;
    margin: 5px;
    border-radius: 5px;
    border: 1px solid #ccc;
}

button {
    padding: 10px 15px;
    border: none;
    border-radius: 5px;
    background: #27ae60;
    color: white;
    cursor: pointer;
}

button:hover {
    background: #219150;
}

.delete {
    background: #e74c3c;
}

.update {
    background: #2980b9;
}

.queue {
    background: #f39c12;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th {
    background: #34495e;
    color: white;
    padding: 10px;
}

td {
    padding: 10px;
    text-align: center;
    border-bottom: 1px solid #ddd;
}

h2 {
    margin-bottom: 10px;
}
</style>

</head>

<body>

<h1>Patient Management System</h1>

<div class="container">

<div class="card">
<h2>Register Patient</h2>
<form method="POST" action="/add">
<input name="id" placeholder="ID" required>
<input name="name" placeholder="Name" required>
<input name="age" placeholder="Age" required>
<input name="gender" placeholder="Gender" required>
<input name="phone" placeholder="Phone" required>
<input name="disease" placeholder="Disease" required>
<button>Add</button>
</form>
</div>

<div class="card">
<h2>Search Patient</h2>
<form method="POST" action="/search">
<input name="id" placeholder="Enter ID">
<button>Search</button>
</form>
</div>

<div class="card">
<h2>Delete Patient</h2>
<form method="POST" action="/delete">
<input name="id" placeholder="Enter ID">
<button class="delete">Delete</button>
</form>
</div>

<div class="card">
<h2>Update Patient</h2>
<form method="POST" action="/update">
<input name="id" placeholder="ID">
<input name="name" placeholder="New Name">
<input name="age" placeholder="New Age">
<input name="gender" placeholder="New Gender">
<input name="phone" placeholder="New Phone">
<input name="disease" placeholder="New Disease">
<button class="update">Update</button>
</form>
</div>

<div class="card">
<h2>Queue</h2>
<form method="POST" action="/enqueue">
<input name="name" placeholder="Name">
<input name="disease" placeholder="Disease">
<button class="queue">Add to Queue</button>
</form>

<form method="POST" action="/dequeue">
<button class="delete">Serve Patient</button>
</form>
</div>

<div class="card">
<h2>Patient Records</h2>
<table>
<tr>
<th>ID</th>
<th>Name</th>
<th>Age</th>
<th>Gender</th>
<th>Phone</th>
<th>Disease</th>
</tr>

{% for row in data %}
<tr>
{% for item in row %}
<td>{{ item }}</td>
{% endfor %}
</tr>
{% endfor %}

</table>
</div>

<div class="card">
<h2>Queue List</h2>
{% for q in queue %}
<p>{{ q[0] }} - {{ q[1] }}</p>
{% endfor %}
</div>

</div>

</body>
</html>
'''


# Load all data
def get_data():
    data = []
    with open(DATA_FILE) as f:
        reader = csv.reader(f)
        next(reader, None)  # skip header
        data = list(reader)
    return data

# Home
@app.route('/')
def index():
    return render_template_string(HTML, data=get_data(), result=None, queue=queue)

# Add Patient
@app.route('/add', methods=['POST'])
def add():
    row = [request.form[x] for x in ["id","name","age","gender","phone","disease"]]
    with open(DATA_FILE, "a", newline="") as f:
        csv.writer(f).writerow(row)
    return redirect('/')

# Search Patient
@app.route('/search', methods=['POST'])
def search():
    search_id = request.form['id']

    data = []
    found = []

    import csv
    with open("patients.csv", "r") as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)
            if row[0] == search_id:   # ID match
                found.append(row)

    # If found → show only that patient
    if found:
        return render_template("index.html", data=found, queue=queue)
    else:
        return render_template("index.html", data=data, queue=queue)
# Delete Patient
@app.route('/delete', methods=['POST'])
def delete():
    pid = request.form['id']
    rows = []

    with open(DATA_FILE) as f:
        rows = list(csv.reader(f))

    with open(DATA_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        for r in rows:
            if r[0] == "ID" or r[0] != pid:
                writer.writerow(r)

    return redirect('/')

# Update Patient
@app.route('/update', methods=['POST'])
def update():
    pid = request.form['id']
    rows = []

    with open(DATA_FILE) as f:
        rows = list(csv.reader(f))

    with open(DATA_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        for r in rows:
            if r[0] == pid:
                r = [
                    pid,
                    request.form['name'],
                    request.form['age'],
                    request.form['gender'],
                    request.form['phone'],
                    request.form['disease']
                ]
            writer.writerow(r)

    return redirect('/')

# Queue Add
@app.route('/enqueue', methods=['POST'])
def enqueue():
    name = request.form['name']
    disease = request.form['disease']
    if name and disease:
        queue.append([name, disease])
    return redirect('/')

# Queue Serve
@app.route('/dequeue', methods=['POST'])
def dequeue():
    if queue:
        queue.pop(0)
    return redirect('/')

# Run app
if __name__ == "__main__":
    app.run(debug=True)