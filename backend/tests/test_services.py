from backend.app.services import coverage,match_score
from backend.app.models import StudentProfile
def test_coverage_transparent():
    r=coverage([{'name':'python','level':2}],[{'skill':'python','level':2},{'skill':'sql','level':2}]); assert r['score']==50 and r['gaps'][0]['status']=='missing'
def test_match_bounded():
    p=StudentProfile(student_id='x',skills_json='[{"name":"python","level":1}]',cgpa=8); r=match_score(p,[{'skill':'python','level':2}]); assert 0<=r['score']<=100 and r['eligible']
