from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json

app = Flask(__name__)
app.secret_key = '87weutgfr8iu7sedgrwfot9a8vghiwe8fy97833honv48y7bt9w8y4bf90w74b6tykizes7gtrk7itrbg'

# Load user accounts data from login.json file
with open('login.json', 'r') as file:
    user_accounts_list = json.load(file)

# Load user data from the login.json file
with open('login.json', 'r') as f:
    users = json.load(f)

# Load ticket data from the tickets.json file
with open('tickets.json', 'r') as f:
    tickets = json.load(f)

# Load completed ticket data from the completed_tickets.json file
with open('completed_tickets.json', 'r') as f:
    completed_tickets = json.load(f)


@app.route('/')
def login():
    if 'username' in session:
        return redirect(url_for('ticket'))
    return render_template('login.html')


@app.route('/authenticate', methods=['POST'])
def authenticate():
    username = request.form.get('username')
    password = request.form.get('password')

    # Check if user exists and password is correct
    if username in users and users[username]['password'] == password:
        session['username'] = username
        return redirect(url_for('ticket'))
    else:
        return render_template('login.html', message='Invalid username or password')


@app.route('/activetickets')
def active_tickets():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('activetickets.html', tickets=tickets)


@app.route('/assign_ticket', methods=['POST'])
def assign_ticket():
    if 'username' not in session:
        return jsonify({'message': 'Unauthorized'})

    data = request.get_json()
    ticket_id = data['ticketId']
    assigned_to = data['assignedTo']

    # Find the ticket by ID in the tickets list
    for ticket in tickets:
        if ticket['id'] == ticket_id:
            # Update the assigned_to field
            ticket['assigned_to'] = assigned_to
            break

    # Update the tickets.json file
    with open('tickets.json', 'w') as f:
        json.dump(tickets, f)

    return jsonify({'message': 'Ticket assigned successfully'})


@app.route('/update_status', methods=['POST'])
def update_status():
    if 'username' not in session:
        return jsonify({'message': 'Unauthorized'})

    data = request.get_json()
    ticket_id = int(data['ticketId'])
    status = data['status']

    # Find the ticket by ID in the tickets list
    for ticket in tickets:
        if ticket['id'] == ticket_id:
            # Update the status field
            ticket['status'] = status
            break

    # Update the tickets.json file
    with open('tickets.json', 'w') as f:
        json.dump(tickets, f)

    return jsonify({'message': 'Ticket status updated successfully'})


@app.route('/complete_ticket', methods=['POST'])
def complete_ticket():
    if 'username' not in session:
        return jsonify({'message': 'Unauthorized'})

    data = request.get_json()
    ticket_id = data['ticketId']

    # Find the ticket by ID in the tickets list
    for ticket in tickets:
        if ticket['id'] == ticket_id:
            # Move the ticket from tickets to completed_tickets
            completed_tickets.append(ticket)
            tickets.remove(ticket)
            break

    # Update the completed_tickets.json file
    with open('completed_tickets.json', 'w') as f:
        json.dump(completed_tickets, f)

    # Update the tickets.json file
    with open('tickets.json', 'w') as f:
        json.dump(tickets, f)

    return jsonify({'message': 'Ticket completed successfully'})


@app.route('/delete_ticket', methods=['POST'])
def delete_ticket():
    if 'username' not in session:
        return jsonify({'message': 'Unauthorized'})

    data = request.get_json()
    ticket_id = int(data['ticketId'])

    # Find the ticket by ID in the tickets list
    for ticket in tickets:
        if ticket['id'] == ticket_id:
            # Remove the ticket from the tickets list
            tickets.remove(ticket)
            # Add the ticket to the completed_tickets list
            completed_tickets.append(ticket)
            break

    # Update the tickets.json file
    with open('tickets.json', 'w') as f:
        json.dump(tickets, f)

    # Update the completed_tickets.json file
    with open('completed_tickets.json', 'w') as f:
        json.dump(completed_tickets, f)

    return jsonify({'message': 'Ticket deleted successfully'})



@app.route('/ticket')
def ticket():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('ticket.html', users=users, tickets=tickets)


@app.route('/submit_ticket', methods=['POST'])
def submit_ticket():
    if 'username' not in session:
        return jsonify({'message': 'Unauthorized'})

    # Get ticket data from the form
    title = request.form.get('title')
    description = request.form.get('description')
    assigned_to = request.form.get('assigned_to')

    # Create a new ticket
    ticket = {
        'id': len(tickets) + 1,
        'title': title,
        'description': description,
        'assigned_to': assigned_to,
        'status': 'pending',
        'admin_note': ''  # Add admin note field
    }

    # Add the ticket to the tickets list
    tickets.append(ticket)

    # Update the tickets.json file
    with open('tickets.json', 'w') as f:
        json.dump(tickets, f)

    return jsonify({'message': 'Ticket submitted successfully'})


@app.route('/update_note', methods=['POST'])
def update_note():
    if 'username' not in session:
        return jsonify({'message': 'Unauthorized'})

    data = request.get_json()
    ticket_id = int(data['ticketId'])  # Convert the ticketId to an integer
    note = data['note']

    # Find the ticket by ID in the tickets list
    for ticket in tickets:
        if ticket['id'] == ticket_id:
            # Update the admin_note field
            ticket['admin_note'] = note
            break

    # Update the tickets.json file
    with open('tickets.json', 'w') as f:
        json.dump(tickets, f)

    return jsonify({'message': 'Note updated successfully'})





@app.route('/logout', methods=['GET'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


# IT personnel routes

@app.route('/admin')
def admin():
    if 'username' not in session:
        return redirect(url_for('login'))

    username = session['username']
    if username in users and users[username]['role'] == 'admin':
        return render_template('admind.html')
    else:
        return redirect(url_for('ticket'))


@app.route('/useraccounts')
def user_accounts():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('useraccounts.html', user_accounts=user_accounts_list)


@app.route('/create_user', methods=['POST'])
def create_user():
    if request.method == 'POST':
        # Retrieve the username and password from the form data
        username = request.form.get('username')
        password = request.form.get('password')

        # Add code to create the user account and store it in the login.json file
        # For example, you can append a new user account to the user_accounts_list and save it back to the file
        user_accounts_list[username] = {
            'password': password,
            'role': 'employee'
        }

        # Update the login.json file with the modified user accounts
        with open('login.json', 'w') as file:
            json.dump(user_accounts_list, file)

        return redirect(url_for('user_accounts'))


@app.route('/edit_user', methods=['POST'])
def edit_user():
    if 'username' not in session:
        return jsonify({'message': 'Unauthorized'})

    username = request.form['username']
    new_password = request.form['password']

    # Check if the username exists in the user_accounts_list
    if username in user_accounts_list:
        # Update the password for the user
        user_accounts_list[username]['password'] = new_password

        # Update the login.json file with the modified user accounts
        with open('login.json', 'w') as file:
            json.dump(user_accounts_list, file)

        return redirect(url_for('user_accounts'))
    else:
        return jsonify({'message': 'User not found'})

@app.route('/oldtickets')
def old_tickets():
    return render_template('oldtickets.html')

if __name__ == '__main__':
    app.run()