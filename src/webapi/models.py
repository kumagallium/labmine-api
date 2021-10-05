from django.db import models
from django.utils import timezone
from account.models import User
from django_mysql.models import JSONField, Model

class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank = True, null = True)

    def publish(self):
        self.published_at = timezone.now()
        self.save()

    def __str__(self):
        return self.title

class Project(models.Model):
    project_name = models.CharField(max_length=255, unique=True)
    editor = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.project_name

class Blueprint(models.Model):
    flowdata = JSONField()
    editor = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Template(models.Model):
    template_name = models.CharField(max_length=255, unique=True)
    blueprint = models.ForeignKey(Blueprint, on_delete=models.PROTECT)
    editor = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Experiment(models.Model):
    title = models.CharField(max_length=255, unique=True)
    blueprint = models.ForeignKey(Blueprint, on_delete=models.PROTECT)
    editor = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Library(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Tag(models.Model):
    tag_name = models.CharField(max_length=255, unique=True)
    editor = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.tag_name

class Pin(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Type(models.Model):
    type_name = models.CharField(max_length=255, unique=True)
    concept = models.IntegerField(default=2)
    editor = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.type_name

class Node(models.Model):
    node_name = models.CharField(max_length=255)
    typeid = models.ForeignKey(Type, on_delete=models.PROTECT)
    editor = models.ForeignKey(User, on_delete=models.PROTECT)
    node_image = models.ImageField(upload_to='images/',default='images/node_default.png')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.node_name

class Entity(models.Model):
    node = models.ForeignKey(Node, on_delete=models.PROTECT,null=True,blank=True)
    boxid = models.CharField(max_length=255)
    blueprint = models.ForeignKey(Blueprint, on_delete=models.PROTECT)
    is_finished = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    finished_at = models.DateTimeField(blank = True, null = True)

    def finished(self):
        self.finished_at = timezone.now()
        self.save()

class Property(models.Model):
    property_name = models.CharField(max_length=255, default="")
    official = models.BooleanField(default=False)
    editor = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.property_name

class Unit(models.Model):
    symbol = models.CharField(max_length=255, default="")
    base = models.BooleanField(default=False)
    editor = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.symbol

class Quantity(models.Model):
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.PROTECT)
    editor = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Figure(models.Model):
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    figure_name = models.CharField(max_length=255)
    property_x = models.ForeignKey(Property, on_delete=models.PROTECT, related_name="property_x", blank = True, null = True)
    property_y = models.ForeignKey(Property, on_delete=models.PROTECT, related_name="property_y", blank = True, null = True)
    property_z = models.ForeignKey(Property, on_delete=models.PROTECT, related_name="property_z", blank = True, null = True)
    datatype = models.IntegerField(default=0)
    is_condition = models.BooleanField(default=False)#将来的に廃止予定
    cluster = models.IntegerField(default=2)
    editor = models.ForeignKey(User, on_delete=models.PROTECT,blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.figure_name

class Datum(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.PROTECT)
    unit_x = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name="unit_x", blank = True, null = True)
    unit_y = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name="unit_y", blank = True, null = True)
    unit_z = models.ForeignKey(Unit, on_delete=models.PROTECT, related_name="unit_z", blank = True, null = True)
    figure = models.ForeignKey(Figure, on_delete=models.PROTECT)
    data = JSONField()
    editor = models.ForeignKey(User, on_delete=models.PROTECT, related_name="editor")
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Metakey(models.Model):
    key_name = models.CharField(max_length=255)
    editor = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key_name

class Product(models.Model):
    product_name = models.CharField(max_length=255)
    experiment = models.ForeignKey(Experiment, on_delete=models.PROTECT)
    editor = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product_name

class Definition(models.Model):
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    entity = models.ForeignKey(Entity, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Image(models.Model):
    image_name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='images/')
    cluster = models.IntegerField(default=2)
    entity = models.ForeignKey(Entity, on_delete=models.PROTECT)
    editor = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.image_name

class Video(models.Model):
    video_name = models.CharField(max_length=255)
    video_url = models.TextField()
    cluster = models.IntegerField(default=2)
    entity = models.ForeignKey(Entity, on_delete=models.PROTECT)
    editor = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.video_name

class Item(models.Model):
    item_name = models.CharField(max_length=255, unique=True)
    editor = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.item_name

class Metadata(models.Model):
    figure = models.ForeignKey(Node, on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.PROTECT)
    values = JSONField()
    editor = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.value

class Detail(models.Model):
    detail_name = models.CharField(max_length=255, unique=True)
    editor = models.ForeignKey(User, on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.detail_name

class Description(models.Model):
    values = JSONField()
    is_condition = models.BooleanField(default=False)#将来的に廃止予定
    cluster = models.IntegerField(default=2)
    entity = models.ForeignKey(Entity, on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Default(models.Model):
    node = models.ForeignKey(Node, on_delete=models.PROTECT)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    is_condition = models.BooleanField(default=False)#将来的に廃止予定
    cluster = models.IntegerField(default=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Headline(models.Model):
    headline_name = models.CharField(max_length=255, unique=True)
    editor = models.ForeignKey(User, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.headline_name

class Sentence(models.Model):
    value = models.TextField()
    headline = models.ForeignKey(Headline, on_delete=models.PROTECT)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    cluster = models.IntegerField(default=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Explanation(models.Model):
    value = models.TextField()
    headline = models.ForeignKey(Headline, on_delete=models.PROTECT)
    figure = models.ForeignKey(Figure, on_delete=models.PROTECT)
    cluster = models.IntegerField(default=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
