from django.db import models


# Create your models here.
class BaseModel(models.Model):
    name = models.CharField(max_length=200, null=False)
    url = models.CharField(max_length=200, null=False)

    class Meta:
        abstract = True


class Fiction(BaseModel):
    fiction_id = models.CharField(max_length=200, null=False)

    def __str__(self):
        return "fiction name:{0},fiction url:{1}".format(self.name,self.url)



class Content(BaseModel):
    fiction_id = models.CharField(max_length=200, null=False)
    chapter_id = models.CharField(max_length=100, null=False)
    content = models.TextField()
    def __str__(self):
        return "chapter name:{0},chapter url:{1}".format(self.name,self.url)
