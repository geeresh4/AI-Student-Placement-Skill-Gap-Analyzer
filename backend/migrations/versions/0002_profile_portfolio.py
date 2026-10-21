from alembic import op
import sqlalchemy as sa
revision="0002_profile_portfolio"; down_revision="0001_initial"; branch_labels=None; depends_on=None
def upgrade():
    inspector=sa.inspect(op.get_bind()); existing={c['name'] for c in inspector.get_columns('student_profiles')}
    for name in ('projects_detail_json','internships_detail_json','certifications_json'):
        if name not in existing: op.add_column('student_profiles',sa.Column(name,sa.Text(),nullable=False,server_default='[]'))
def downgrade():
    inspector=sa.inspect(op.get_bind()); existing={c['name'] for c in inspector.get_columns('student_profiles')}
    for name in ('certifications_json','internships_detail_json','projects_detail_json'):
        if name in existing: op.drop_column('student_profiles',name)
