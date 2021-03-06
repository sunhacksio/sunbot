from peewee import *
from models import db, Hacker

class Registration(db.Model):
    id = CharField(verbose_name = "Typeform ID", primary_key=True)
    first_name = TextField(verbose_name = "First Name")
    last_name = TextField(verbose_name = "Last Name")
    pronouns_he = BooleanField(default = False, verbose_name = "Pronouns He/Him/His")
    pronouns_she = BooleanField(default = False, verbose_name = "Pronouns She/Her/Hers")
    pronouns_them = BooleanField(default = False, verbose_name = "Pronouns They/Them/Theirs")
    pronouns_other = TextField(null = True, verbose_name = "Pronouns Other")
    first_hack = BooleanField(verbose_name = "First Hackathon")
    phone_number = TextField(verbose_name = "Phone Number")
    email = TextField(verbose_name = "Email Address")
    school = TextField(verbose_name = "School")
    school_other = TextField(null = True, verbose_name="School (Other)")
    level_of_study = TextField(verbose_name = "Level of Study")
    level_of_study_other = TextField(null = True, verbose_name = "Level of Study (Other)")
    undergrad = TextField(null = True, verbose_name = "Undergrad Year")
    undergrad_other = TextField(null = True, verbose_name = "Undergrad Year (Other)")
    grad_year = TextField(null = True, verbose_name = "Graduation Year")
    major = TextField(null = True, verbose_name = "Major")
    major_other = TextField(null = True, verbose_name = "Major (Other)")
    sponsor = BooleanField(default = False, verbose_name = "Send Sponsor?")
    resume_link = TextField(null = True, verbose_name = "Resume Link")
    github_link = TextField(null = True, verbose_name = "GitHub Link")
    linkedin_link = TextField(null = True, verbose_name = "LinkedIn Link")
    devpost_link = TextField(null = True, verbose_name = "Devpost Link")
    personal_link = TextField(null = True, verbose_name = "Personal Link")
    gender = TextField(null = True, verbose_name = "Gender")
    gender_other = TextField(null = True, verbose_name = "Other")
    background_indian = BooleanField(default = False, verbose_name = "Background American Indian or Alaska Native")
    background_asian = BooleanField(default = False, verbose_name = "Background Asian / Pacific Islander")
    background_black = BooleanField(default = False, verbose_name = "Background Black or African American")
    background_hispanic = BooleanField(default = False, verbose_name = "Background Hispanic or Latinx")
    background_middle_east = BooleanField(default = False, verbose_name = "Background Middle Eastern or North African")
    background_hawaii = BooleanField(default = False, verbose_name = "Background Native Hawaiian or Other Pacific Islander")
    background_white = BooleanField(default = False, verbose_name = "Background White / Caucasian")
    background_none = BooleanField(default = False, verbose_name = "Background Prefer Not to Answer")
    background_other = TextField(null = True, verbose_name = "Background Other")
    country = TextField(null = True, verbose_name = "Country of Origin")
    state = TextField(null = True, verbose_name = "State of Origin")
    swag = BooleanField(default = False, verbose_name = "Send Swag?")
    ship_street = TextField(null = True, verbose_name = "Shipping Address")
    ship_etc = TextField(null = True, verbose_name = "Shipping Etc")
    ship_city = TextField(null = True, verbose_name = "Shipping City")
    ship_state = TextField(null = True, verbose_name = "Shipping State")
    ship_postal = TextField(null = True, verbose_name = "Shipping Postal Code")
    ship_country = TextField(null = True, verbose_name = "Shipping Country")
    shirt = TextField(null = True, verbose_name = "Shirt Size")
    code_of_conduct = BooleanField(default = False, verbose_name = "MLH Code of Conduct")
    terms_and_conditions = BooleanField(default = False, verbose_name = "MLH Terms and Conditions")
    start_time = DateTimeField(verbose_name = "Typeform Start Time")
    submit_time = DateTimeField(verbose_name = "Typeform Submission Time")
    network_id = CharField(verbose_name = "Typeform Network ID", null = True)
    hacker_discord = ForeignKeyField(Hacker, backref="responses", null = True)

    class Meta:
        table_name = "responses"
