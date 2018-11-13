from django.db import models
from django.contrib.auth.models import User
from django.db.models import Max
# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    description = models.CharField(max_length=420, blank=True, default="Hi~")
    age = models.CharField(max_length=3, blank=True)
    location = models.CharField(max_length=40, blank=True, null=True)
    picture = models.ImageField(upload_to="user-photos", blank=True,
                                default="user-photos/hdfj3498whf23jdnfsjk382r.png")
    header_photo = models.ImageField(upload_to="header-photos", blank=True,
                                     default="header-photos/hfjq74yr7HBKYG78hg7bFFY213.jpg")
    jumbotron_title = models.CharField(max_length=40, blank=True, default="Welcome")
    jumbotron_content = models.CharField(max_length=200, blank=True, default="Enjoy yourself!~")
    friends = models.ManyToManyField("self", symmetrical=False, blank=True)
    token_reg = models.CharField(max_length=400, blank=True)

    def save(self):
        try:
            this = UserProfile.objects.get(id=self.id)
            if this.picture != self.picture and this.picture.name != 'user-photos/hdfj3498whf23jdnfsjk382r.png':
                this.picture.delete()
            if this.header_photo != self.header_photo and this.header_photo != 'header-photos/hfjq74yr7HBKYG78hg7bFFY213.jpg':
                this.header_photo.delete()
        except: pass
        super(UserProfile, self).save()

    def __str__(self):
        return self.user.username


class Message(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    content = models.CharField(max_length=42)
    time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content

    @staticmethod
    def get_changes(time="1970-01-01T00:00+00:00"):
        return Message.objects.filter(time__gt=time)

    @staticmethod
    def get_max_time():
        return Message.objects.all().aggregate(Max('time'))['time__max'] or "1970-01-01T00:00+00:00"


class Favorite(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    content = models.CharField(max_length=42)
    poster = models.CharField(max_length=200)
    message_id = models.CharField(max_length=40)
    time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content


class Comment(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    content = models.CharField(max_length=42)
    time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content
