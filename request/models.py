from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.utils import timezone
from account.models import Company

User = get_user_model()

# Create your models here.
class Request(models.Model):
	INACTIVE = 0
	IN_PROGRESS = 1
	RELEASED = 2

	ACTIVITY_TYPE = (
		(INACTIVE, 'inactive'),
		(IN_PROGRESS, 'in_progress'),
		(RELEASED, 'released'),
	)

	uuid = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
	request = models.CharField(max_length=256)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	company = models.ForeignKey(Company, on_delete=models.CASCADE)
	date_created = models.DateTimeField(auto_now_add=True)
	activity = models.IntegerField(default=0, choices=ACTIVITY_TYPE)
	is_active = models.BooleanField(default=True)


	def get_total_likes(self):
		return self.likes.users.count()

	def get_total_dislikes(self):
		return self.dislikes.users.count()

	def __str__(self):
		return str(self.request)[:30]


class Like(models.Model):
	''' like  comment '''

	request = models.OneToOneField(Request, related_name="likes", on_delete=models.CASCADE)
	users = models.ManyToManyField(User, related_name='requirement_request_likes')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return str(self.request.request)[:30]


class DisLike(models.Model):
	''' Dislike  comment '''

	request = models.OneToOneField(Request, related_name="dislikes", on_delete=models.CASCADE)
	users = models.ManyToManyField(User, related_name='requirement_request_dislikes')
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return str(self.request.request)[:30]