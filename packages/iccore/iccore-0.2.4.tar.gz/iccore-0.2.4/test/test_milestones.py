import json
from datetime import datetime

from iccore.project import Milestone


def test_milestone():

    milestone = Milestone(
        title="My Milestone",
        description="My Milestone description",
        start_date=datetime.fromisoformat("2024-10-07"),
        due_date=datetime.fromisoformat("2024-10-15"),
    )

    milestone_serialized = milestone.model_dump_json()
    milestone_json = json.loads(milestone_serialized)

    milestone_cpy = Milestone(**milestone_json)

    assert milestone_cpy.title == milestone.title
    assert milestone_cpy.start_date == milestone.start_date
