import dateutil.parser
import base64
import hmac
import os
import hashlib

def parse_short_text(field,res):
    return res["text"]

def parse_multiple_choice(field,res):
    labels = [i["label"] for i in field["choices"]]
    other_flag = "allow_other_choice" in field
    if "allow_multiple_selections" in field:
        if other_flag:
            other = res["choices"]["other"] if "other" in res["choices"] else ""
        checked = [False for i in labels]
        if res["choices"]["labels"] == None:
            return checked + ([other] if other_flag else [])
        for choice in res["choices"]["labels"]:
            i = labels.index(choice)
            checked[i] = True
        return checked + ([other] if other_flag else [])
    else:
        if other_flag:
            if "label" in res["choice"]:
                return [res["choice"]["label"],""]
            else:
                return ["",res["choice"]["other"]]
        else:
            return res["choice"]["label"]

def parse_phone_number(field,res):
    return res["phone_number"]

def parse_email(field,res):
    return res["email"]

def parse_yes_no(field,res):
    return res["boolean"]

def parse_dropdown(field,res):
    return res["choice"]["label"]

def parse_file_upload(field,res):
    return res["file_url"]

def parse_website(field,res):
    return res["url"]

def parse_legal(field,res):
    return res["boolean"]

parse_types = { "short_text" : parse_short_text, "multiple_choice" : parse_multiple_choice, "phone_number" : parse_phone_number, "email" : parse_email, "yes_no" : parse_yes_no, "dropdown" : parse_dropdown, "file_upload" : parse_file_upload, "website" : parse_website, "legal" : parse_legal }

FIELDS = ["first_name", "last_name", "pronouns_he", "pronouns_she", "pronouns_them", "pronouns_other", "first_hack", "phone_number", "email", "school", "school_other", "level_of_study", "level_of_study_other", "undergrad", "undergrad_other", "grad_year", "major", "major_other", "sponsor", "resume_link", "github_link", "linkedin_link", "devpost_link", "personal_link", "gender", "gender_other", "background_indian", "background_asian", "background_black", "background_hispanic", "background_middle_east", "background_hawaii", "background_white", "background_none", "background_other", "country", "state", "swag", "ship_street", "ship_etc", "ship_city", "ship_state", "ship_postal", "ship_country", "shirt", "code_of_conduct", "terms_and_conditions"]


TYPEFORM_FIELDS = {
    '9TQX4bMyZjPb' : ['first_name'],
    'rl3Wev9Xvjea' : ['last_name'],
    'se8FtJiLgUTz' : ['pronouns_he', 'pronouns_she', 'pronouns_them','pronouns_other'],
    'rhQFIuEukIqw' : ['first_hack'],
    'hwBya5o5jO3c' : ['phone_number'],
    'yZLjWLUW0YoQ' : ['email'],
    'icgw1L5XkJYg' : ['school'],
    '4ufLPmVyeNNI' : ['school_other'],
    'JMJo5tsnaR6c' : ['level_of_study','level_of_study_other'],
    '5CQ7uLxBak7z' : ['undergrad', 'undergrad_other'],
    'pomyvT86USol' : ['grad_year'],
    'i4Naogjh487w' : ['major'],
    'lxLED0iLAZZB' : ['major_other'],
    'v0CCbyxOWvDX' : ['sponsor'],
    'hGt6dL0WfElp' : ['resume_link'],
    'yZUdXhebuwa4' : ['github_link'],
    'ZaoruXmjfMyS' : ['linkedin_link'],
    'anjySNASmA8Z' : ['devpost_link'],
    'FRjbyIjfjQ5l' : ['personal_link'],
    'Qe4Vprh1TfQS' : ['gender','gender_other'],
    'cJ5ldwv0xt8M' : ['background_indian', 'background_asian', 'background_black', 'background_hispanic', 'background_middle_east', 'background_hawaii', 'background_white', 'background_none', 'background_other'],
    '68nWVlMdiFPq' : ['country'],
    'regccqjLbMTy' : ['state'],
    'tBU55m95fJa5' : ['swag'],
    '0hGnDOX8X0qm' : ['ship_street'],
    'KdDAQiy98XIt' : ['ship_ect'],
    'ylC1N7eozKxT' : ['ship_city'],
    'Qorr1f4J80Jx' : ['ship_state'],
    'U6VdOqQDQeWk' : ['ship_postal'],
    '4w8Z7micuDVT' : ['ship_country'],
    '72NwO25sqhzI' : ['shirt'],
    'ziVbGM8AlHPn' : ['code_of_conduct'],
    'b6ms8QC2jcrW' : ['terms_and_conditions']
}

def parse_response(field,res):
    assert field["id"] == res["field"]["id"]
    if field["type"] in parse_types:
        return parse_types[field["type"]](field,res)
    else:
        raise NotImplementedError()

def parse_responses(event):
    form_res = event["form_response"]
    answers = []
    fields = []
    for i, ans in enumerate(form_res["answers"]):
        field_def = form_res["definition"]["fields"][i]
        vals = parse_response(field_def, ans)
        fields = fields + TYPEFORM_FIELDS[field_def["id"]]
        if type(vals) == list:
            answers.extend(vals)
        else:
            answers.append(vals)
    entry = {}
    for i, field in enumerate(fields):
        entry[field] = answers[i]
    entry["id"] = event["event_id"]
    entry["start_time"] = dateutil.parser.parse(form_res["landed_at"])
    entry["submit_time"] = dateutil.parser.parse(form_res["submitted_at"])
    return entry


def authorize(sig, body):
    # body = body.encode('utf-8')
    sha_name, signature = sig.split('=', 1)
    mac = hmac.new(os.getenv("TYPEFORM_SECRET").encode('utf-8'), msg = body, digestmod = hashlib.sha256)
    return  hmac.compare_digest(base64.b64encode(mac.digest()).decode().encode('utf-8'), signature.encode('utf-8'))
