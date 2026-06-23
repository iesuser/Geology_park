from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, StringField, SubmitField, TextAreaField
from wtforms.validators import Length, NumberRange, Optional


class ArtifactForm(FlaskForm):
  specimen_id = IntegerField(
    "Specimen ID",
    validators=[Optional(), NumberRange(min=1, message="ID must be at least 1.")],
    description="Leave empty on create for auto ID, or set a specific number.",
  )
  title_en = StringField("Title (English)", validators=[Optional(), Length(max=200)])
  title_ka = StringField("Title (Georgian)", validators=[Optional(), Length(max=200)])
  elevation_m = IntegerField(
    "Elevation (meters above sea level)",
    validators=[Optional(), NumberRange(min=0, max=9000)],
  )
  description_en = TextAreaField(
    "Description (English)", validators=[Optional(), Length(max=5000)]
  )
  description_ka = TextAreaField(
    "Description (Georgian)", validators=[Optional(), Length(max=5000)]
  )
  is_active = BooleanField("Visible on home page", default=True)
  submit = SubmitField("Save")
