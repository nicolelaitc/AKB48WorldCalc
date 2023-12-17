from flask_wtf.form import _Auto
from wtforms import (
    validators,
    TextAreaField,
    StringField,
    SelectField,
    IntegerField,
    FloatField,
)
from flask_wtf import FlaskForm


class InputForm(FlaskForm):
    theme = SelectField(
        "theme", validators=[validators.input_required()], validate_choice=False
    )
    theme_other = TextAreaField("theme_other", default="(Other theme)")
    team = SelectField(
        "team", validators=[validators.input_required()], validate_choice=False
    )
    member = SelectField(
        "member", validators=[validators.input_required()], validate_choice=False
    )
    member_other = TextAreaField("member_other", default="(Other member)")
    singing = IntegerField("singing", validators=[validators.number_range(min=0)])
    dancing = IntegerField("dancing", validators=[validators.number_range(min=0)])
    variety = IntegerField("vaiety", validators=[validators.number_range(min=0)])
    style = IntegerField("style", validators=[validators.number_range(min=0)])
    total = IntegerField("total", validators=[validators.input_required()])
    skill_type = StringField("skill_type", validators=[validators.input_required()])
    skill_target = StringField("skill_target", validators=[validators.input_required()])
    skill_rate = FloatField(
        "skill_rate", validators=[validators.number_range(min=1, max=99)]
    )
    cheer = SelectField(
        "cheer", validators=[validators.input_required()], validate_choice=False
    )
    cheer_skill = StringField("cheer_skill", validators=[validators.input_required()])
    cheer_rate = FloatField(
        "cheer_rate", validators=[validators.number_range(min=1, max=99)]
    )

    def validate_total(form, field):
        if (
            form.singing.data + form.dancing.data + form.style.data + form.variety.data
        ) != field.data:
            raise validators.ValidationError("Total is not correct.")

    def validate_cheer(form, field):
        if field.data == form.member.data:
            raise validators.ValidationError(
                "Cheer member and card member cannot be the same."
            )


class editForm(FlaskForm):
    id = IntegerField("id", validators=[validators.input_required()])


class loginForm(FlaskForm):
    username = StringField("username", validators=[validators.input_required()])
    password = StringField("password", validators=[validators.input_required()])


class registerForm(FlaskForm):
    username = StringField("username", validators=[validators.input_required()])
    password = StringField("password", validators=[validators.input_required()])
    confirmPassword = StringField(
        "confirmPassword",
        validators=[validators.input_required(), validators.equal_to("password")],
    )


class calculatorForm(FlaskForm):
    production = IntegerField(
        "production", validators=[validators.input_required()], default=0
    )
    today_target_team = SelectField(
        "today_target_team",
        validate_choice=False,
    )
    today_skill = SelectField("today_skill", validate_choice=False)
    bonus_rate = IntegerField(
        "bonus_rate", validators=[validators.number_range(min=0, max=99)]
    )
    singing = IntegerField(
        "singing", validators=[validators.number_range(min=-300, max=500)], default=0
    )
    dancing = IntegerField(
        "dancing", validators=[validators.number_range(min=-300, max=500)], default=0
    )
    variety = IntegerField(
        "vaiety", validators=[validators.number_range(min=-300, max=500)], default=0
    )
    style = IntegerField(
        "style", validators=[validators.number_range(min=-300, max=500)], default=0
    )
    target = IntegerField(
        "target",
        validators=[validators.input_required()],
    )
    stage = SelectField("stage", validate_choice=False)
    opponent = SelectField("opponent", validate_choice=False)


class memberListForm(FlaskForm):
    item_type = SelectField(
        "item_type",
        validators=[validators.input_required()],
        validate_choice=True,
        choices=["member", "theme"],
    )
    var = IntegerField("var", validators=[validators.input_required()])


def savedDataToInputForm(card) -> InputForm:
    form = InputForm()
    form.theme.data = card["theme"]
    form.team.data = card["team"]
    form.member.data = card["member"]
    form.singing.data = card["singing"]
    form.dancing.data = card["dancing"]
    form.variety.data = card["variety"]
    form.style.data = card["style"]
    form.total.data = card["total"]
    form.skill_type.data = card["skill_type"]
    form.skill_target.data = card["skill_target"]
    form.skill_rate.data = card["skill_rate"]
    form.cheer.data = card["cheer"]
    form.cheer_skill.data = card["cheer_skill"]
    form.cheer_rate.data = card["cheer_rate"]

    return form
