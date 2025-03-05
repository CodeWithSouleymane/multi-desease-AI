import os
import sys
from app import app, db, User, Disease
from utils.model_utils import initialize_models
from werkzeug.security import generate_password_hash

def init_database():
    """Initialize the database with sample data"""
    with app.app_context():
        # Create tables
        db.create_all()
        
        # Check if we already have data
        if User.query.first() is None:
            print("Creating admin user...")
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
            
            print("Adding diseases to database...")
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
        else:
            print('Database already contains data. Skipping initialization.')

def main():
    """Main initialization function"""
    print("Initializing Multi-Disease AI Early Warning System...")
    
    # Initialize models
    print("\nInitializing ML models...")
    models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
    initialize_models(models_dir)
    
    # Initialize database
    print("\nInitializing database...")
    init_database()
    
    print("\nInitialization complete! You can now run the application with 'python app.py'")

if __name__ == "__main__":
    main()
