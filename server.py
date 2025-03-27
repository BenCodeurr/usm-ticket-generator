from flask import Flask, request, jsonify
import csv

app = Flask(__name__)

# Function to mark beneficiary as served
def mark_as_served(ticket_code, distribution_data, csv_filename="beneficiaries.csv"):
    # Read the CSV file
    with open(csv_filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        fieldnames = reader.fieldnames

    # Find and update the beneficiary
    for row in rows:
        if row['Ticket Code'] == ticket_code:
            # Check if all fields are already "Oui"
            if (row['Jeton Distribué'] == 'Oui' and 
                row['NFI'] == 'Oui' and 
                row['Outils'] == 'Oui' and 
                row['Semence'] == 'Oui'):
                return False, "Le bénéficiaire est déjà servi à 100%."

            # Update the fields with new data
            row['Jeton Distribué'] = distribution_data.get('distribution_jeton', row['Jeton Distribué'])
            row['NFI'] = distribution_data.get('nfi', row['NFI'])
            row['Outils'] = distribution_data.get('outils', row['Outils'])
            row['Semence'] = distribution_data.get('semence', row['Semence'])

            # Save the updated CSV file
            with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            return True, "Données mises à jour avec succès."

    return False, "Code ticket non trouvé."

# Route to handle QR data from the mobile app/scanner
@app.route('/scan', methods=['POST'])
def scan_ticket():
    data = request.json
    ticket_code = data.get('ticket_code')
    distribution_data = {
        'distribution_jeton': data.get('distribution_jeton'),
        'nfi': data.get('nfi'),
        'outils': data.get('outils'),
        'semence': data.get('semence')
    }
    
    if not ticket_code:
        return jsonify({"status": "error", "message": "Code ticket requis"})
    
    success, message = mark_as_served(ticket_code, distribution_data)
    return jsonify({
        "status": "success" if success else "error",
        "message": message
    })

# Route to check ticket availability and return beneficiary info
@app.route('/check-ticket', methods=['POST'])
def check_ticket():
    ticket_code = request.json.get('ticket_code')
    
    if not ticket_code:
        return jsonify({"status": "error", "message": "Ticket code is required"})
    
    # Check if the ticket exists in the CSV file
    with open("beneficiaries.csv", newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['Ticket Code'] == ticket_code:
                # Determine what to return based on the requirements
                if row['Parténaire'] and row['Parténaire'].strip():
                    return jsonify({
                        "status": "success", 
                        "exists": True, 
                        "info": row['Parténaire'],
                        "info_type": "Parténaire"
                    })
                elif row['Carte'] and row['Carte'].strip():
                    return jsonify({
                        "status": "success", 
                        "exists": True, 
                        "info": row['Carte'],
                        "info_type": "Carte"
                    })
                else:
                    return jsonify({
                        "status": "success", 
                        "exists": True, 
                        "info": row['Age'],
                        "info_type": "Age"
                    })
        
        # If ticket not found
        return jsonify({"status": "error", "exists": False, "message": "Ticket code not found"})

if __name__ == '__main__':
    # Run the Flask app locally on your machine (localhost:5000)
    app.run(debug=True, host='0.0.0.0', port=8000)
