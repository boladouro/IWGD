from haystack import indexes
from main.models import Thread, Post, User


# https://stackoverflow.com/questions/13959525/which-fields-of-the-model-in-the-django-haystack-tutorial-get-indexed
class ThreadIndex(indexes.SearchIndex, indexes.Indexable):
  text = indexes.CharField(document=True, use_template=True)
  title_ind = indexes.CharField(model_attr='title')
  date_ind = indexes.DateTimeField(model_attr='date_created')
  user_ind = indexes.CharField(model_attr='user')
  topico_ind = indexes.CharField(model_attr='topico')

  def get_model(self):
    return Thread

  def index_queryset(self, using=None):
    """Used when the entire index for model is updated."""
    return self.get_model().objects.all()


class PostIndex(indexes.SearchIndex, indexes.Indexable):
  text = indexes.CharField(document=True, use_template=True)
  date_ind = indexes.DateTimeField(model_attr='date_created')
  user_ind = indexes.CharField(model_attr='user')
  thread_ind = indexes.CharField(model_attr='thread')

  def get_model(self):
    return Post

  def index_queryset(self, using=None):
    """Used when the entire index for model is updated."""
    return self.get_model().objects.all()

class UserIndex(indexes.SearchIndex, indexes.Indexable):
  text = indexes.CharField(document=True, use_template=True)
  username_ind = indexes.CharField(model_attr='username')

  def get_model(self):
    return User

  def index_queryset(self, using=None):
    """Used when the entire index for model is updated."""
    return self.get_model().objects.all()