from django.db import models
from django.contrib.auth.models import (
	AbstractBaseUser, PermissionsMixin, BaseUserManager
)
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.mail import send_mail

from django.urls import reverse
from django.utils.text import slugify

import uuid
from django.dispatch import receiver
from django.db.models.signals import post_save

from django.core.exceptions import ValidationError

from django.db import IntegrityError
from django.db import transaction


class ActiveManager(models.Manager):
	def get_queryset(self):
		return super(ActiveManager, self).get_queryset()\
											.filter(is_active=True)
class VerifiedManager(models.Manager):
	def get_queryset(self):
		return super(VerifiedManager, self).get_queryset()\
											.filter(is_verified=True)

class UserManager(BaseUserManager):
	"""
	Custom user model manager where email is the unique identifiers
	for authentication instead of usernames.
	"""

	use_in_migrations = True

	def create_user(self, email, password, **extra_fields):
		"""
		Create and save a User with the given email and password.
		"""
		if not email:
			raise ValueError(_('The Email must be set'))
		email = self.normalize_email(email)
		user = self.model(email=email, **extra_fields)
		user.set_password(password)
		user.save()
		return user
	
	def create_superuser(self, email, password, **extra_fields):
		"""
		Create and save a SuperUser with the given email and password.
		"""
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)
		extra_fields.setdefault('is_active', True)

		if extra_fields.get('is_staff') is not True:
			raise ValueError(_('Superuser must have is_staff=True.'))
		if extra_fields.get('is_superuser') is not True:
			raise ValueError(_('Superuser must have is_superuser=True.'))
		return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
	"""
	An abstract base class implementing a fully featured User model with
	admin-compliant permissions.

	"""

	uuid = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
	email = models.EmailField(max_length=128, unique=True)
	username = models.CharField(max_length=128, unique=True, blank=True)
	fullname = models.CharField(max_length=128, blank=True)
	is_staff = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	image = models.ImageField(upload_to='profile/',blank=True, null=True)
	date_joined = models.DateTimeField(default=timezone.now)
	last_login = models.DateTimeField(null=True)

	objects = UserManager()

	active_now = ActiveManager() # Our custom manager

	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []

	class Meta:
		verbose_name = _('user')
		verbose_name_plural = _('users')

	def __str__(self):
		return self.email

	def email_user(self, subject, message, from_email=None, **kwargs):
		'''
		Sends an email to this User.
		'''
		send_mail(subject, message, from_email, [self.email], **kwargs)

	def save(self, *args, **kwargs):
		# The if not here is to ensure the account is just created
		if not self.username:
			username = self.email.split('@')[0].lower()
			username = ''.join(e for e in username if e.isalnum())
			try:
				User.objects.get(username = username)
				self.username = username.lower() +'_'+str(uuid.uuid4())[:6]
			except:
				self.username = username
		super().save(*args, **kwargs)


class Company(models.Model):
	"""
	An abstract base class implementing a fully featured User model with
	admin-compliant permissions.

	"""

	uuid = models.UUIDField(default=uuid.uuid4, editable=False, db_index=True)
	email = models.EmailField(max_length=128, unique=True)
	name = models.CharField(max_length=128)
	username = models.CharField(max_length=128, unique=True, blank=True)
	url = models.URLField(blank=False)
	is_verified = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	image = models.ImageField(upload_to='company/',blank=True, null=True)
	date_joined = models.DateTimeField(auto_now_add=True)
	# last_login = models.DateTimeField(null=True)

	active_now = ActiveManager()
	verified_now = VerifiedManager()

	class Meta:
		verbose_name = _('company')
		verbose_name_plural = _('companies')

	def __str__(self):
		return self.username

	def save(self, *args, **kwargs):
		# The if not here is to ensure the account is just created
		if not self.username:
			username = ''.join(e for e in self.name.lower() if e.isalnum())
			try:
				Company.objects.get(username = username)
				self.username = username.lower() +'_'+str(uuid.uuid4())[:6]
			except:
				self.username = username
		super().save(*args, **kwargs)