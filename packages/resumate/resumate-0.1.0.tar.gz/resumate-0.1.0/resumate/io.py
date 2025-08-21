import yaml

def create_resume_template(yaml_file):
    """
    Create a template YAML file for a resume with structured sections.

    :param yaml_file: Path to the YAML file where the template will be saved.
    """
    resume_template = {
        'main_data': {
            'name': 'Your Name',
            'address': 'Your Address',
            'phone': 'Your Phone Number',
            'email': 'Your Email',
            'position': 'The position you\'re applying for',
            'links': [
                {
                    'type': 'GitHub',
                    'url': 'github.com/stuff',
                    'name': 'github',
                    'order':  2
              },{
                        'type': 'LinkedIn',
                    'url': 'linkedin.com/u/user',
                    'name': 'github',
                    'order': 1 ,
              
              }

            ],

            'picture': 'Path to your picture'
        },


        'experiences': [
            {
                'role': 'Your Role',
                'company': 'Company Name',
                'start': 'Start Date',
                'finished': 'End Date',
                'currently_working': False,
                'feature_comment': 'Key Achievement or Comment',
                'successes': [
                    'Success 1',
                    'Success 2'
                ],
                'skills_used': [
                    {
                        'category': 'Technical',
                        'skills': ['Skill 1', 'Skill 2']
                    }
                ]
            }
        ],
        'skills': [
            {
                'category': 'Technical',
                'skills_list': ['Skill 1', 'Skill 2']
            },
            {
                'category': 'Management',
                'skills_list': ['Skill 1', 'Skill 2']
            }
        ],
        'cover_page': True,
        'theme': {
            'color_scheme': {
                'background': 'Color Code',
                'foreground': 'Color Code'
            }
        }
    }

    with open(yaml_file, 'w') as file:
        yaml.safe_dump(resume_template, file, default_flow_style=False)

def load_resume_from_yaml(yaml_file):
    """
    Load resume data from a YAML file.

    :param yaml_file: Path to the YAML file containing resume data.
    :return: A dictionary containing the loaded resume data.
    """
    with open(yaml_file, 'r') as file:
        resume_data = yaml.safe_load(file)
    return resume_data

def save_resume_to_yaml(resume_data, yaml_file):
    """
    Save resume data to a YAML file.

    :param resume_data: A dictionary containing the resume data.
    :param yaml_file: Path to the YAML file where the data will be saved.
    """
    with open(yaml_file, 'w') as file:
        yaml.safe_dump(resume_data, file, default_flow_style=False)

