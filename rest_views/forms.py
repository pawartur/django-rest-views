from django import forms


class LoadMoreForm(forms.Form):
    exclude = forms.ModelMultipleChoiceField(queryset=None, required=False)

    def __init__(self, queryset, limit, *args, **kwargs):
        super(LoadMoreForm, self).__init__(*args, **kwargs)
        self.fields["exclude"].queryset = queryset
        self.limit = limit

    def get_qs_and_not_all_info(self):
        qs = self.fields["exclude"].queryset
        qs = qs.exclude(pk__in=map(lambda x: x.pk, self.cleaned_data["exclude"]))[:self.limit+1]
        not_all = qs.count() > self.limit
        # We make another query if not_all == True. This could be avoided by making a list out of
        # queryset, but I don't think it's a particularly good idea in our case.
        return not_all and qs[:self.limit] or qs, not_all