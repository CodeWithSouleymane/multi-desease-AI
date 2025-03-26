import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI', 'sqlite:///disease_warning.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db = SQLAlchemy(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Define database models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='user')
    alerts = db.relationship('Alert', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Disease(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    symptoms = db.Column(db.Text)
    risk_factors = db.Column(db.Text)
    model_path = db.Column(db.String(200))
    predictions = db.relationship('Prediction', backref='disease', lazy='dynamic')

class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    disease_id = db.Column(db.Integer, db.ForeignKey('disease.id'), nullable=False)
    location = db.Column(db.String(100))
    risk_level = db.Column(db.Float)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    data_used = db.Column(db.Text)  # JSON string of data used for prediction

class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    disease_id = db.Column(db.Integer, db.ForeignKey('disease.id'), nullable=False)
    threshold = db.Column(db.Float, default=0.7)
    location = db.Column(db.String(100))
    active = db.Column(db.Boolean, default=True)
    disease = db.relationship('Disease')

class SystemLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Simplified prediction function (no ML model)
def simulate_prediction(disease_name, input_data):
    """
    Simulate a prediction without using ML models
    """
    # Simple rule-based risk calculation for demonstration
    risk_level = 0.5  # Default medium risk
    
    # Ensure all numeric values in input_data are properly converted to float
    for key in input_data:
        if isinstance(input_data[key], str) and input_data[key].replace('.', '', 1).isdigit():
            input_data[key] = float(input_data[key])
    
    if disease_name.lower() == 'covid-19':
        # Higher risk with: high population density, low vaccination, high mobility, low hospital beds
        if 'population_density' in input_data and float(input_data['population_density']) > 1000:
            risk_level += 0.2
        if 'vaccination_rate' in input_data and float(input_data['vaccination_rate']) < 50:
            risk_level += 0.2
        if 'mobility_index' in input_data and float(input_data['mobility_index']) > 70:
            risk_level += 0.1
        if 'hospital_beds' in input_data and float(input_data['hospital_beds']) < 3:
            risk_level += 0.1
            
    elif disease_name.lower() == 'influenza':
        # Higher risk with: low temperature, low humidity, low vaccination, high school density
        if 'temperature' in input_data and float(input_data['temperature']) < 10:
            risk_level += 0.2
        if 'humidity' in input_data and float(input_data['humidity']) < 40:
            risk_level += 0.1
        if 'flu_vaccination' in input_data and float(input_data['flu_vaccination']) < 40:
            risk_level += 0.2
        if 'school_density' in input_data and float(input_data['school_density']) > 5:
            risk_level += 0.1
            
    elif disease_name.lower() == 'dengue':
        # Higher risk with: high rainfall, high temperature, high humidity, high standing water
        if 'rainfall' in input_data and float(input_data['rainfall']) > 200:
            risk_level += 0.2
        if 'temperature_dengue' in input_data and float(input_data['temperature_dengue']) > 30:
            risk_level += 0.2
        if 'humidity_dengue' in input_data and float(input_data['humidity_dengue']) > 70:
            risk_level += 0.1
        if 'standing_water' in input_data and float(input_data['standing_water']) > 0.5:
            risk_level += 0.2
            
    elif disease_name.lower() == 'malaria':
        # Higher risk with: high rainfall, high temperature, high humidity, high mosquito density, low bednet usage
        if 'rainfall_malaria' in input_data and float(input_data['rainfall_malaria']) > 200:
            risk_level += 0.1
        if 'temperature_malaria' in input_data and float(input_data['temperature_malaria']) > 28:
            risk_level += 0.1
        if 'humidity_malaria' in input_data and float(input_data['humidity_malaria']) > 70:
            risk_level += 0.1
        if 'mosquito_density' in input_data and float(input_data['mosquito_density']) > 100:
            risk_level += 0.2
        if 'bednet_usage' in input_data and float(input_data['bednet_usage']) < 50:
            risk_level += 0.1
    
    # Cap risk level between 0 and 1
    return max(0, min(1, risk_level))

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    diseases = Disease.query.all()
    recent_predictions = Prediction.query.order_by(Prediction.timestamp.desc()).limit(10).all()
    return render_template('dashboard.html', diseases=diseases, predictions=recent_predictions)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        flash('Nom d\'utilisateur ou mot de passe invalide')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Ce nom d\'utilisateur existe déjà')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Cet email est déjà enregistré')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Inscription réussie! Vous pouvez maintenant vous connecter.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté avec succès', 'success')
    return redirect(url_for('index'))

@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict():
    diseases = Disease.query.all()
    if request.method == 'POST':
        disease_id = request.form.get('disease')
        location = request.form.get('location')
        
        # Get form data
        form_data = {key: float(value) if value.replace('.', '', 1).isdigit() else value 
                    for key, value in request.form.items() 
                    if key not in ['disease', 'location']}
        
        disease = Disease.query.get(disease_id)
        if not disease:
            flash('Maladie non trouvée')
            return redirect(url_for('predict'))
        
        # Use simplified prediction function
        risk_level = simulate_prediction(disease.name, form_data)
            
        # Save prediction to database
        prediction = Prediction(
            disease_id=disease.id,
            location=location,
            risk_level=risk_level,
            data_used=json.dumps(form_data)
        )
        db.session.add(prediction)
        db.session.commit()
        
        # Check for alerts
        if current_user.role == 'admin':
            alerts = Alert.query.filter_by(disease_id=disease.id, active=True).all()
            for alert in alerts:
                if alert.location == location and risk_level >= alert.threshold:
                    flash(f'Alerte : Le niveau de risque de {disease.name} à {location} est de {risk_level:.2f}')
        
        return render_template('prediction_result.html', 
                              disease=disease, 
                              location=location, 
                              risk_level=risk_level,
                              data=form_data)
    
    return render_template('predict.html', diseases=diseases)

@app.route('/disease/<int:disease_id>')
@login_required
def disease_detail(disease_id):
    disease = Disease.query.get_or_404(disease_id)
    predictions = Prediction.query.filter_by(disease_id=disease_id).order_by(Prediction.timestamp.desc()).limit(20).all()
    return render_template('disease_detail.html', disease=disease, predictions=predictions)

@app.route('/alerts', methods=['GET', 'POST'])
@login_required
def alerts():
    if request.method == 'POST':
        disease_id = request.form.get('disease')
        location = request.form.get('location')
        threshold = float(request.form.get('threshold'))
        
        alert = Alert(
            user_id=current_user.id,
            disease_id=disease_id,
            threshold=threshold,
            location=location
        )
        db.session.add(alert)
        db.session.commit()
        flash('Alert created successfully')
        return redirect(url_for('alerts'))
    
    user_alerts = Alert.query.filter_by(user_id=current_user.id).all()
    diseases = Disease.query.all()
    return render_template('alerts.html', alerts=user_alerts, diseases=diseases)

@app.route('/toggle_alert/<int:alert_id>', methods=['POST'])
@login_required
def toggle_alert(alert_id):
    alert = Alert.query.get_or_404(alert_id)
    
    # Ensure the alert belongs to the current user
    if alert.user_id != current_user.id:
        flash('Access denied: This alert does not belong to you')
        return redirect(url_for('alerts'))
    
    # Toggle the active status
    alert.active = not alert.active
    db.session.commit()
    
    status = "enabled" if alert.active else "disabled"
    flash(f'Alert for {alert.disease.name} in {alert.location} {status}')
    return redirect(url_for('alerts'))

@app.route('/delete_alert/<int:alert_id>', methods=['POST'])
@login_required
def delete_alert(alert_id):
    alert = Alert.query.get_or_404(alert_id)
    
    # Ensure the alert belongs to the current user
    if alert.user_id != current_user.id:
        flash('Access denied: This alert does not belong to you')
        return redirect(url_for('alerts'))
    
    disease_name = alert.disease.name
    location = alert.location
    
    db.session.delete(alert)
    db.session.commit()
    
    flash(f'Alert for {disease_name} in {location} deleted')
    return redirect(url_for('alerts'))

@app.route('/api/predictions/<disease_name>')
@login_required
def api_predictions(disease_name):
    disease = Disease.query.filter_by(name=disease_name).first_or_404()
    predictions = Prediction.query.filter_by(disease_id=disease.id).order_by(Prediction.timestamp.desc()).limit(100).all()
    
    data = [{
        'location': p.location,
        'risk_level': p.risk_level,
        'timestamp': p.timestamp.isoformat(),
        'data': json.loads(p.data_used) if p.data_used else {}
    } for p in predictions]
    
    return jsonify(data)

@app.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash('Access denied: Admin privileges required')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    diseases = Disease.query.all()
    predictions = Prediction.query.order_by(Prediction.timestamp.desc()).limit(50).all()
    return render_template('admin.html', users=users, diseases=diseases, predictions=predictions)

@app.route('/admin/add_disease', methods=['GET', 'POST'])
@login_required
def add_disease():
    if current_user.role != 'admin':
        flash('Access denied: Admin privileges required')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        symptoms = request.form.get('symptoms')
        risk_factors = request.form.get('risk_factors')
        
        disease = Disease(
            name=name,
            description=description,
            symptoms=symptoms,
            risk_factors=risk_factors,
            model_path=f"models/{name.lower().replace(' ', '_')}_model.pkl"
        )
        db.session.add(disease)
        db.session.commit()
        flash(f'Disease {name} added successfully')
        return redirect(url_for('admin'))
    
    return render_template('add_disease.html')

def simulate_outbreak_prediction(disease_name, region, timeframe, confidence, include_environmental, include_social):
    """
    Simule une prédiction d'épidémie alimentée par l'IA basée sur les paramètres fournis.
    Dans un système réel, cela utiliserait des modèles d'apprentissage automatique.
    """
    # Simulate processing time to make it feel like AI computation
    import time
    time.sleep(1)
    
    # Generate realistic-looking prediction results
    findings = [
        f"Épidémie potentielle de {disease_name} détectée en {region.replace('_', ' ').title()} dans les {timeframe} prochains mois",
        f"Niveau de confiance : {confidence}% basé sur les tendances historiques",
        f"Principaux points chauds identifiés dans les centres urbains avec une densité de population >5000/km²",
        f"Les facteurs environnementaux suggèrent un risque de transmission accru de {random.randint(10, 30)}%",
        f"Couverture vaccinale actuelle estimée à {random.randint(40, 80)}% dans les zones à haut risque"
    ]
    
    actions = [
        f"Augmenter la surveillance dans les régions à risque identifiées",
        f"Préparer les établissements de santé à une augmentation potentielle de {random.randint(15, 50)}% des cas",
        f"Mettre en œuvre des campagnes de vaccination ciblées dans les communautés à haut risque",
        f"Renforcer la sensibilisation du public aux mesures de prévention de {disease_name}",
        f"Coordonner avec les régions voisines pour une surveillance transfrontalière"
    ]
    
    # Generate map data (simplified for demonstration)
    map_data = [{
        'type': 'choropleth',
        'locations': ['USA', 'CAN', 'MEX', 'BRA', 'ARG', 'COL', 'PER', 'CHL'] if region == 'north_america' or region == 'south_america' else
                   ['FRA', 'DEU', 'GBR', 'ITA', 'ESP', 'POL', 'UKR', 'RUS'] if region == 'europe' else
                   ['CHN', 'IND', 'JPN', 'KOR', 'IDN', 'THA', 'VNM', 'MYS'] if region == 'asia' else
                   ['ZAF', 'EGY', 'NGA', 'KEN', 'ETH', 'DZA', 'MAR', 'GHA'] if region == 'africa' else
                   ['AUS', 'NZL', 'PNG', 'FJI'],
        'z': [random.uniform(0.1, 0.9) for _ in range(8)],
        'text': ['Risque Élevé', 'Risque Moyen', 'Risque Faible', 'Risque Moyen', 'Risque Élevé', 'Risque Faible', 'Risque Moyen', 'Risque Faible'],
        'colorscale': 'Reds',
        'showscale': True,
        'colorbar': {'title': 'Niveau de Risque'}
    }]
    
    # Generate timeline data
    timeline_data = [{
        'x': list(range(timeframe + 1)),
        'y': [0.1] + [min(0.1 + i * random.uniform(0.05, 0.15), 0.95) for i in range(timeframe)],
        'type': 'scatter',
        'mode': 'lines+markers',
        'name': 'Risque Prédit',
        'line': {'color': 'rgb(219, 64, 82)', 'width': 3}
    }]
    
    # Add another line for comparison if including environmental factors
    if include_environmental:
        timeline_data.append({
            'x': list(range(timeframe + 1)),
            'y': [0.05] + [min(0.05 + i * random.uniform(0.03, 0.12), 0.9) for i in range(timeframe)],
            'type': 'scatter',
            'mode': 'lines',
            'name': 'Risque de Base',
            'line': {'color': 'rgba(50, 171, 96, 0.7)', 'width': 2, 'dash': 'dot'}
        })
    
    return {
        'disease': disease_name,
        'region': region,
        'timeframe': timeframe,
        'findings': findings,
        'actions': actions,
        'map_data': map_data,
        'timeline_data': timeline_data,
        'region': region
    }

@app.route('/outbreak-prediction', methods=['GET', 'POST'])
@login_required
def outbreak_prediction():
    diseases = Disease.query.all()
    prediction_results = None
    
    if request.method == 'POST':
        disease_id = request.form.get('disease')
        region = request.form.get('region')
        timeframe = int(request.form.get('timeframe'))
        confidence = int(request.form.get('confidence'))
        include_environmental = 'includeEnvironmental' in request.form
        include_social = 'includeSocial' in request.form
        
        # Get the disease
        disease = Disease.query.get(disease_id)
        
        # Simulate AI prediction results
        prediction_results = simulate_outbreak_prediction(
            disease.name, 
            region, 
            timeframe, 
            confidence, 
            include_environmental,
            include_social
        )
        
        # Log the prediction request
        log_entry = SystemLog(
            user_id=current_user.id,
            action=f"Prédiction d'épidémie générée pour {disease.name} en {region}",
            timestamp=datetime.now()
        )
        db.session.add(log_entry)
        db.session.commit()
        
    return render_template('outbreak_prediction.html', diseases=diseases, prediction_results=prediction_results)

# Initialize database with some sample data
def init_db():
    db.create_all()
    
    # Check if we already have data
    if User.query.first() is None:
        # Create admin user
        admin = User(username='admin', email='admin@example.com', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Create regular user
        user = User(username='user', email='user@example.com', role='user')
        user.set_password('user123')
        db.session.add(user)
        
        # Create sample diseases
        diseases = [
            {
                'name': 'COVID-19',
                'description': 'Coronavirus disease (COVID-19) is an infectious disease caused by the SARS-CoV-2 virus.',
                'symptoms': 'Fever, cough, tiredness, loss of taste or smell',
                'risk_factors': 'Age, underlying medical conditions, close contact with infected individuals'
            },
            {
                'name': 'Influenza',
                'description': 'Influenza is a viral infection that attacks your respiratory system.',
                'symptoms': 'Fever, chills, muscle aches, cough, congestion',
                'risk_factors': 'Age, weakened immune system, chronic illnesses, pregnancy'
            },
            {
                'name': 'Dengue',
                'description': 'Dengue is a mosquito-borne viral disease that has rapidly spread in all regions in recent years.',
                'symptoms': 'High fever, headache, vomiting, muscle and joint pains, skin rash',
                'risk_factors': 'Living in tropical areas, prior infection with dengue virus'
            },
            {
                'name': 'Malaria',
                'description': 'Malaria is a life-threatening disease caused by parasites that are transmitted to people through the bites of infected female Anopheles mosquitoes.',
                'symptoms': 'Fever, chills, headache, nausea and vomiting',
                'risk_factors': 'Travel to areas where malaria is common, not taking preventive drugs'
            }
        ]
        
        for d in diseases:
            disease = Disease(
                name=d['name'],
                description=d['description'],
                symptoms=d['symptoms'],
                risk_factors=d['risk_factors'],
                model_path=f"models/{d['name'].lower().replace(' ', '_')}_model.pkl"
            )
            db.session.add(disease)
        
        db.session.commit()
        print('Database initialized with sample data.')

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
