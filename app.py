from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.json
        aggregate = calculate_aggregate(data)
        return jsonify({'aggregate': f"{aggregate:.2f}%"})
    return render_template('index.html')

def calculate_aggregate(data):
    admission_test_marks = calculate_admission_test_marks(data['admissionTest'])
    
    intermediate_percentage = (data['intermediate']['obtained'] / data['intermediate']['total']) * 100
    matric_percentage = (data['matric']['obtained'] / data['matric']['total']) * 100

    admission_test_weightage = 0.50
    intermediate_weightage = 0.40
    matric_weightage = 0.10

    aggregate = (
        (admission_test_marks / 100) * admission_test_weightage * 100 +
        intermediate_percentage * intermediate_weightage +
        matric_percentage * matric_weightage
    )

    return aggregate

def calculate_admission_test_marks(admission_test_data):
    sections = ["English", "Analytical Skills & IQ", "Basic Math", "Adv. Math"]
    weightages = {"English": 0.33, "Analytical Skills & IQ": 1, "Basic Math": 1, "Adv. Math": 1}
    penalties = {"English": 0.13, "Analytical Skills & IQ": 0.25, "Basic Math": 0.25, "Adv. Math": 0.25}
    
    total_marks = 0
    
    for section in sections:
        section_data = admission_test_data[section]
        total_questions = section_data['total']
        attempted_questions = section_data['attempted']
        correct_answers = section_data['correct']
        
        wrong_answers = attempted_questions - correct_answers
        section_marks = correct_answers - (wrong_answers * penalties[section])
        
        weighted_marks = section_marks * weightages[section]
        
        total_marks += weighted_marks
    
    return total_marks

if __name__ == '__main__':
    if __name__ == '__main__':
        import os
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)