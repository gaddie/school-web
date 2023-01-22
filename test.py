from wtforms import Form, SelectField

class MyForm(Form):
    choices = [('option1', 'Option 1'), ('option2', 'Option 2'), ('option3', 'Option 3')]
    select = SelectField('Select an option:', choices=choices)