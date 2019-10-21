import os
import json
import boto3


MTURK_SANDBOX = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
CONFIGURATION_FILE_PATH = 'input_files/mturk_configuration.json'
QUESTION_TEMPLATE = """<?xml version="1.0" encoding="UTF-8"?>
<ExternalQuestion xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2006-07-14/ExternalQuestion.xsd">
  <ExternalURL>{}</ExternalURL>
  <FrameHeight>0</FrameHeight>
</ExternalQuestion>
"""
HITS_LIST = {
    # TODO Change urls to prod before merge
    'register': 'https://labeling.umsi.io/mturk_register',
    'demographics': 'https://labeling.umsi.io/mturk_demographics',
    'label': 'https://labeling.umsi.io/mturk_label',
}


class MTurkConnection:
    def __init__(self):
        endpoint_url = MTURK_SANDBOX if not os.getenv('MTURK_ENDPOINT') else os.getenv('MTURK_ENDPOINT')
        self.client = boto3.client(
            'mturk',
            endpoint_url=endpoint_url,
            region_name=os.getenv('MTURK_REGION'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        )

    def _register_hit(self, hit_name, url):
        configuration = self.configuration[hit_name]['configuration']
        worker_configuration = self.configuration[hit_name]['worker_requirements']
        hit = self.client.create_hit(
            Title=configuration.get('Title'),
            Description=configuration.get('Description'),
            Keywords=configuration.get('Keywords'),
            Reward=configuration.get('Reward'),
            MaxAssignments=configuration.get('MaxAssignments'),
            LifetimeInSeconds=configuration.get('LifetimeInSeconds'),
            AssignmentDurationInSeconds=configuration.get('AssignmentDurationInSeconds'),
            AutoApprovalDelayInSeconds=configuration.get('AutoApprovalDelayInSeconds'),
            QualificationRequirements=worker_configuration,
            Question=QUESTION_TEMPLATE.format(url),
        )
        return hit

    def register_hits(self):
        self._load_configuration()
        return [self._register_hit(hit_name, url) for hit_name, url in HITS_LIST.items()]

    def _load_configuration(self):
        with open(CONFIGURATION_FILE_PATH, 'r') as f:
            self.configuration = json.loads(f.read())

    def accept_assignment(self, assignment_id, requester_feedback, override_rejection):
        return self.client.approve_assignment(
            AssignmentId=assignment_id,
            RequesterFeedback=requester_feedback,
            OverrideRejection=override_rejection,
        )
