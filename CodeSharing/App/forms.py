from django import forms


class SearchForm(forms.Form):
    search_input = forms.CharField(
        max_length=255,
        required=True,
        label="",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "search",
                "dir": "auto",
                "spellcheck": "false",
            }
        ),
    )
    page_size = forms.ChoiceField(
        choices=[
            (5, "5"),
            (10, "10"),
            (15, "15"),
            (20, "20"),
            (25, "25"),
            (50, "50"),
            (75, "75"),
            (100, "100"),
        ],
        required=False,
        label="number of results to show",
        initial=10,
        widget=forms.Select(
            attrs={"class": "form-control page-size-select", "dir": "ltr"}
        ),
    )
