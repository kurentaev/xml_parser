from django.db import models


class Individuals(models.Model):
    dataid = models.CharField(max_length=255, primary_key=True)
    versionnum = models.CharField(max_length=255)
    name_original_script = models.CharField(max_length=255)
    first_name = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    second_name = models.CharField(max_length=255)
    third_name = models.CharField(max_length=255)
    un_list_type = models.CharField(max_length=255)
    reference_number = models.CharField(max_length=255)
    listed_on = models.CharField(max_length=255)
    comments1 = models.TextField()
    designation = models.TextField()
    nationality = models.CharField(max_length=255)
    list_type = models.CharField(max_length=255)
    last_day_updated = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state_province = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    from_year = models.CharField(max_length=255)
    to_year = models.CharField(max_length=255)

    class Meta:
        db_table = 'individuals'
