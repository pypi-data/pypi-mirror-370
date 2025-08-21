import os
import argparse
from .io import load_resume_from_yaml, save_resume_to_yaml, create_resume_template
from .pdf import generate_pdf
from .generator import generated_resume
from .template import template
from .template_loader import template_loader

def main():
    parser = argparse.ArgumentParser(
        description="Resumate - Professional Resume Management System",
        epilog="Examples:\n"
               "  %(prog)s template my_resume.yaml              # Create new resume template\n"
               "  %(prog)s generate_pdf resume.yaml             # Generate PDF with default template\n"
               "  %(prog)s generate_pdf resume.yaml -t modern   # Generate PDF with 'modern' template\n"
               "  %(prog)s list_templates                       # Show all available templates\n",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'action', 
        choices=['template', 'load', 'save', 'generate_pdf', 'generate_fake', 'extract', 'new_style', 'list_templates'],
        help="Operation to perform on resume files",
        metavar='ACTION'
    )
    
    action_help = {
        'template': 'Create a new blank resume template YAML file with all standard sections',
        'load': 'Load and display resume data from a YAML file (validation check)',
        'save': 'Re-save resume data to YAML file (normalizes formatting)',
        'generate_pdf': 'Generate a PDF document from resume YAML data using specified template',
        'generate_fake': 'Generate sample resume data with Lorem Ipsum content for testing',
        'extract': 'Extract resume data from an existing PDF file (experimental)',
        'new_style': 'Create a new PDF styling template for custom resume layouts',
        'list_templates': 'Display all available built-in PDF templates with descriptions'
    }
    
    parser.add_argument(
        'file', 
        nargs='?', 
        help="Path to the resume YAML file (e.g., resume.yaml, /path/to/cv.yaml). Not required for 'list_templates' action",
        metavar='FILE_PATH'
    )
    
    parser.add_argument(
        'dir', 
        nargs='?', 
        default=None, 
        help="Output directory for generated files (PDFs, templates). Defaults to same directory as input file",
        metavar='OUTPUT_DIR'
    )
    
    parser.add_argument(
        '--template', '-t', 
        default=None, 
        help="PDF template to use for generation. Can be: "
             "1) Built-in template name (e.g., 'modern', 'classic', 'resume-1'), "
             "2) Path to custom template file (e.g., './my_template.yaml'). "
             "Default: 'resume-1' or 'resume-with-qr' if available",
        metavar='TEMPLATE_NAME_OR_PATH'
    )

    args = parser.parse_args()

    # Handle list_templates which doesn't need a file
    if args.action == 'list_templates':
        templates = template_loader.list_templates()
        print("\n" + "="*60)
        print("AVAILABLE PDF TEMPLATES")
        print("="*60)
        for tmpl in templates:
            print(f"\n📄 {tmpl['name']} (version {tmpl.get('version', '1.0')})")
            if tmpl.get('description'):
                print(f"   Description: {tmpl['description']}")
        print("\n" + "-"*60)
        print("Usage: resumate generate_pdf <file> --template <name>")
        print("Example: resumate generate_pdf resume.yaml -t modern")
        print("="*60 + "\n")
        return

    # All other actions need a file
    if not args.file:
        print(f"\n❌ ERROR: Action '{args.action}' requires a file path")
        print(f"   Description: {action_help.get(args.action, 'Unknown action')}")
        print(f"\n   Usage: {parser.prog} {args.action} <file_path>")
        print(f"   Example: {parser.prog} {args.action} resume.yaml\n")
        parser.error(f"'{args.action}' requires a file argument")

    if args.dir == None:
        args.dir = os.path.dirname(args.file)

    if not os.path.exists(args.dir):
        print(f"📁 Creating output directory: {args.dir}")
        os.makedirs(args.dir)
        
    if args.action == 'new_style':
        print(f"\n🎨 Creating new PDF styling template...")
        t = template(args.file)
        t.build()
        t.save()
        print(f"✅ Successfully created new template style: {args.file}")
        print(f"   You can now use this template with: --template {args.file}\n")
        
    elif args.action == 'template':
        print(f"\n📝 Creating new resume template...")
        create_resume_template(args.file)
        print(f"✅ Successfully created resume template: {args.file}")
        print(f"   Next steps:")
        print(f"   1. Edit {args.file} with your information")
        print(f"   2. Generate PDF: {parser.prog} generate_pdf {args.file}\n")
        
    elif args.action == 'load':
        print(f"\n📖 Loading resume data from: {args.file}")
        print("-" * 60)
        data = load_resume_from_yaml(args.file)
        print(f"✅ Successfully loaded resume data:")
        print("-" * 60)
        print(f"{data}")
        print("-" * 60)
        print(f"Resume sections found: {', '.join(data.keys())}\n")
        
    elif args.action == 'save':
        print(f"\n💾 Re-saving resume data...")
        data = load_resume_from_yaml(args.file)
        save_resume_to_yaml(data, args.file)
        print(f"✅ Successfully normalized and saved: {args.file}")
        print(f"   This action reformats the YAML for consistency\n")
        
    elif args.action == 'generate_fake':
        print(f"\n🎲 Generating sample resume data...")
        generated_resume(args.file, 10)  # Generate fake resume data with 10 experiences
        print(f"✅ Successfully generated fake resume: {args.file}")
        print(f"   Contains: 10 work experiences with Lorem Ipsum content")
        print(f"   Use this for testing PDF templates and layouts\n")
        
    elif args.action == 'generate_pdf':
        print(f"\n📄 Generating PDF from resume data...")
        print(f"   Source: {args.file}")
        
        data = load_resume_from_yaml(args.file)
        pdf_file = args.file.replace('.yaml', '.pdf')
        
        # Determine which template to use
        if args.template:
            print(f"   Template requested: {args.template}")
            # Resolve template name to file path
            try:
                template_file = template_loader.resolve_template_path(args.template)
                print(f"   Resolved to built-in: {template_file}")
            except:
                template_file = args.template
                print(f"   Using custom template: {template_file}")
        else:
            print(f"   No template specified, checking for defaults...")
            # Try QR template first, fall back to original
            qr_template = "template/resume-with-qr.yaml"
            default_template = "template/resume-1.yaml"
            
            # Also check for built-in default
            try:
                template_file = template_loader.resolve_template_path('resume-1')
                print(f"   Using built-in default: resume-1")
            except:
                template_file = qr_template if os.path.exists(qr_template) else default_template
                template_name = "resume-with-qr" if os.path.exists(qr_template) else "resume-1"
                print(f"   Using local default: {template_name}")
        
        if not os.path.exists(template_file):
            print(f"\n❌ ERROR: Template file not found: {template_file}")
            print(f"   Try one of these:")
            print(f"   • Run: {parser.prog} list_templates")
            print(f"   • Create custom: {parser.prog} new_style my_template.yaml")
            return
        
        print(f"\n⚙️  Processing with template: {template_file}")
        generate_pdf(data, pdf_file, template_file)
        print(f"\n✅ PDF successfully generated!")
        print(f"   Output file: {pdf_file}")
        print(f"   Template used: {template_file}")
        print(f"\n   View your resume: open {pdf_file}\n")
    else:
        print("\n" + "="*60)
        print("ACTION DESCRIPTIONS")
        print("="*60)
        for action, description in action_help.items():
            print(f"\n{action:15} - {description}")
        print("\n" + "="*60 + "\n")
        parser.print_help()


if __name__ == '__main__':
    main()