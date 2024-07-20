from flask import Flask, render_template, request, jsonify
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

df_2024 = pd.read_csv('data/predictions_2024.csv')

def calculate_probabilities(student_merit, predicted_merits):
    probabilities = {}
    for _, row in predicted_merits.iterrows():
        discipline = row['Discipline']
        campus = row['Campus']
        closing_merit = row['Merit']
        
        if campus not in probabilities:
            probabilities[campus] = {}
        
        if pd.notna(closing_merit) and closing_merit != 0:
            if student_merit >= closing_merit:
                probabilities[campus][discipline] = 1.0
            else:
                probabilities[campus][discipline] = student_merit / closing_merit
        else:
            probabilities[campus][discipline] = 'N/A'
    
    return probabilities

def generate_probability_chart(probabilities):
    fig, ax = plt.subplots(figsize=(12, 8)) 
    
    campuses = list(probabilities.keys())
    campus_colors = {campus: plt.cm.tab10(i) for i, campus in enumerate(campuses)}
    
    y_offset = 0  # Offset to separate disciplines of different campuses
    bar_height = 0.4
    discipline_labels = []
    discipline_positions = []
    
    for campus in campuses:
        disciplines = list(probabilities[campus].keys())
        values = [probabilities[campus][d] * 100 for d in disciplines if probabilities[campus][d] != 'N/A']
        
        for i, (discipline, value) in enumerate(zip(disciplines, values)):
            bar_position = y_offset + i * (bar_height + 0.2)
            ax.barh(bar_position, value, height=bar_height, color=campus_colors[campus], label=campus if i == 0 else "")
            
            if value > 10:  # Threshold for inside vs. outside
                ax.text(value - 5, bar_position, f"{value:.1f}%", va='center', color='black', fontweight='bold')
            else:
                ax.text(value + 1, bar_position, f"{value:.1f}%", va='center', color='black', fontweight='bold')
            
            discipline_labels.append(discipline)
            discipline_positions.append(bar_position)
        
        y_offset += len(disciplines) * (bar_height + 0.2) + 1 
    
    ax.set_xlabel('Probability (%)')
    ax.set_title('Admission Probabilities')
    ax.set_yticks(discipline_positions)
    ax.set_yticklabels(discipline_labels)
    
    ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1))
    
    plt.tight_layout() 
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart = base64.b64encode(buf.getvalue()).decode('utf-8')
    return chart

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

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.json
        aggregate = calculate_aggregate(data)
        return jsonify({'aggregate': f"{aggregate:.2f}%"})
    return render_template('index.html')

@app.route('/probability')
def probability():
    return render_template('probability.html')

@app.route('/calculate_probability', methods=['POST'])
def calculate_probability():
    data = request.json
    student_merit = data['merit']
    probabilities = calculate_probabilities(student_merit, df_2024)
    chart = generate_probability_chart(probabilities)
    return jsonify({'chart': chart})

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)