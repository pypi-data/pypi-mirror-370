
import yaml
from faker import Faker
import random

fake = Faker()

# Define a list of possible relationship types

def get_certificates(count):
    certs = []
    for _ in range(count):
        certificate = {
            'name': fake.catch_phrase() + " Course",
            'date': fake.date()
        }
        certs.append(certificate)
    return certs

# Function to generate a random relationship type
def get_relationship_type():
    relationship_types = [
        "Friend",
        "Coworker",
        "Parent",
        "Wife",
        "Husband",
        "Sibling",
        "Cousin",
        "Partner"
    ]
    return random.choice(relationship_types)

def generate_skills(category):
    skills = {
        'Technical': ['Python', 'Java', 'C++', 'JavaScript', 'SQL', 'AWS', 'Docker', 'Kubernetes', 'Machine Learning'],
        'Management': ['Project Management', 'Leadership', 'Budgeting', 'Strategic Planning', 'Agile Methodologies'],
        'Communication': ['Public Speaking', 'Negotiation', 'Persuasion', 'Interpersonal Communication', 'Writing'],
        'Analytical': ['Data Analysis', 'Critical Thinking', 'Problem Solving', 'Research', 'Statistics']
    }
    return {
        'category': category,
        'skills': random.sample(skills[category], k=random.randint(2, 5))
    }

def generate_position():
    positions = ['Software Engineer', 'Data Analyst', 'Project Manager', 'Marketing Specialist', 'Financial Analyst']
    return random.choice(positions)

def generate_experience():
    return {
        'role': fake.job(),
        'company': fake.company(),
        'start': fake.date_between(start_date='-10y', end_date='-2y').isoformat(),
        'end': fake.date_between(start_date='-2y', end_date='today').isoformat(),
        'currently_working': fake.boolean(chance_of_getting_true=25),
        'feature_comment': fake.paragraph(nb_sentences=2),
        'achievements': [fake.sentence() for _ in range(random.randint(2, 5))],
    }


def generate_resume_data(num_experiences,num_achievements=5,num_strengths=1,num_passions=2,certificate_count=2):
    return {
        'header': {
            'name': fake.name(),
            'address': fake.address(),
            'location': fake.city()+", "+fake.state(),
            'phone': fake.phone_number(),
            'email': fake.email(),
            'position':generate_position(),
            'github': 'github.com/in/' + fake.user_name(),
            'linkedin': 'linkedin.com/in/' + fake.user_name(),
            'picture': 'assets/avatar.png'
        },
        'summary': {'text':fake.paragraph(nb_sentences=5)},
        'cover_page': fake.paragraph(nb_sentences=15),
        'education': [{
           'school': fake.company() + " School",
           'course':  fake.catch_phrase() + " Course",
           'start':fake.date(),
           'end':fake.date(),
        }],

        'certificates': get_certificates(certificate_count),
        'screener': {
            'veteran': fake.boolean(),
            'disability': fake.boolean(),
            'us_citizen': fake.boolean(),
            'over_18': fake.boolean(),
            'willing_to_travel': fake.boolean(),
            'remote':fake.boolean(),
            'hybrid':fake.boolean(),
            'office':fake.boolean(),
            'start_date':fake.date(),

        },
        'references':[
            {
                'name':fake.name(),
                'relationship':  get_relationship_type(),
                'email': fake.email(),
                'phone': fake.phone_number(),
            },            {
                'name':fake.name(),
                'relationship':  get_relationship_type(),
                'email': fake.email(),
                'phone': fake.phone_number(),
            },            {
                'name':fake.name(),
                'relationship':  get_relationship_type(),
                'email': fake.email(),
                'phone': fake.phone_number(),
            },
        ],
        'strengths':  [fake.paragraph(nb_sentences=3) for _ in range(num_strengths)],
        'passions': [fake.paragraph(nb_sentences=3) for _ in range(num_passions)],
        'experiences': [generate_experience() for _ in range(num_experiences)],
        'achievements': [fake.paragraph(nb_sentences=3) for _ in range(num_achievements)],
        'skills': [generate_skills(category) for category in ['Technical', 'Management', 'Communication', 'Analytical']],
          'cover_page': fake.boolean()
    }
     

def generated_resume(filename, num_experiences):
    resume_data = generate_resume_data(num_experiences)
    with open(filename, 'w') as file:
        yaml.safe_dump(resume_data, file, default_flow_style=False)
    print(f"Generated resume data saved to '{filename}'.")

