from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from account.serializer import UserSerializer
from .models import Post, Project, Library, Experiment, Type, Node, Datum, Property, Unit, Figure, Metakey, Metadata, Blueprint, Template, Tag, Quantity, Entity, Product, Definition, Item, Description, Headline, Image
#from rest_framework.fields import CurrentUserDefault
import pint
u = pint.UnitRegistry()
Q = u.Quantity

class ProjectSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    project_name = serializers.CharField(max_length=255, validators=[UniqueValidator(queryset=Project.objects.all())])

    def create(self, validated_data):
        project_tmp = Project.objects.filter(project_name=validated_data['project_name'])
        if len(project_tmp)>0:
            project = Project.objects.get(project_name=validated_data['project_name'])
            project.project_name = validated_data['project_name']
            project.save()
        else:
            project = Project.objects.create(
                project_name=validated_data['project_name'],
                editor_id=self.context['request'].user.id)
        return project

    def update(self, instance, validated_data):
        instance.project_name = validated_data.get('project_name', instance.project_name)
        instance.save()
        return instance


class BlueprintSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    flowdata = serializers.JSONField()

    def create(self, validated_data):
        blueprint = Blueprint.objects.create(
            flowdata=self.context['flowdata'],
            editor_id=self.context['request'].user.id)
        return blueprint

    def update(self, instance, validated_data):
        instance.flowdata = validated_data.get('flowdata', instance.flowdata)
        instance.save()
        return instance

class TemplateSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    template_name = serializers.CharField(max_length=255, validators=[UniqueValidator(queryset=Template.objects.all())])
    blueprint =  BlueprintSerializer(read_only=True)#serializers.CharField(max_length=255)
    blueprint_id = serializers.CharField(max_length=255,write_only=True)

    def create(self, validated_data):
        blueprint = Blueprint.objects.get(id=validated_data['blueprint_id'])
        template = Template.objects.create(
            template_name=validated_data['template_name'],
            blueprint = blueprint,
            editor_id=self.context['request'].user.id)
        return template

    def update(self, instance, validated_data):
        instance.template_name = validated_data.get('template_name', instance.template_name)
        instance.save()
        return instance

class ExperimentSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=255, validators=[UniqueValidator(queryset=Experiment.objects.all())])
    blueprint =  serializers.CharField(max_length=255)
    blueprint_id = serializers.CharField(source='blueprint.pk', read_only=True)

    def create(self, validated_data):
        blueprint = Blueprint.objects.get(id=validated_data['blueprint'])
        experiment_tmp = Experiment.objects.filter(title=validated_data['title'])
        if len(experiment_tmp)>0:
            experiment = Experiment.objects.get(title=validated_data['title'])
            experiment.title = validated_data['title']
            experiment.save()
        else:
            experiment = Experiment.objects.create(
                title=validated_data['title'],
                blueprint = blueprint,
                editor_id=self.context['request'].user.id)
        return experiment

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.save()
        return instance

class TagSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    tag_name = serializers.CharField(max_length=255)

    def create(self, validated_data):
        tag_tmp = Tag.objects.filter(tag_name=validated_data['tag_name'])
        if len(tag_tmp)>0:
            tags = Tag.objects.get(tag_name=validated_data['tag_name'])
            tags.tag_name = validated_data['tag_name']
            tags.save()
        else:
            tags = Tag.objects.create(
                tag_name=validated_data['tag_name'],
                editor_id=self.context['request'].user.id)

        return tags

    def update(self, instance, validated_data):
        instance.tag_name = validated_data.get('tag_name', instance.tag_name)
        instance.save()
        return instance

class TypeSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    type_name = serializers.CharField(max_length=255, validators=[UniqueValidator(queryset=Type.objects.all())])
    concept = serializers.IntegerField(default=2)

    def create(self, validated_data):
        types = Type.objects.create(
            type_name=validated_data['type_name'],
            concept=validated_data['concept'],
            editor_id=self.context['request'].user.id)
        return types

    def update(self, instance, validated_data):
        instance.type_name = validated_data.get('type_name', instance.type_name)
        instance.save()
        return instance

class NodeSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    node_name = serializers.CharField(max_length=255)
    node_image = serializers.ImageField(max_length=None,use_url=True,default='images/node_default.png')
    is_newimage = serializers.BooleanField(default=False)

    def create(self, validated_data):
        typeid = self.context['typeid']
        type_tmp = Type.objects.get(pk=typeid)
        node_tmp = Node.objects.filter(node_name=validated_data['node_name'],typeid=type_tmp)
        if len(node_tmp)>0:
            node = Node.objects.get(node_name=validated_data['node_name'],typeid=type_tmp)
            node.node_name = validated_data['node_name']
            node.node_image = validated_data['node_image']
            node.save()
        else:
            node = Node.objects.create(
                node_name=validated_data['node_name'],
                node_image=validated_data['node_image'],
                typeid=type_tmp,
                editor_id=self.context['request'].user.id)
        return node

    def update(self, instance, validated_data):
        instance.node_name =  validated_data.get('node_name', instance.node_name)
        if validated_data['is_newimage']:
            instance.node_image =  validated_data.get('node_image', instance.node_image)
        instance.save()
        return instance

class PropertySerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    property_name = serializers.CharField(max_length=255)
    official = serializers.BooleanField(default=False)

    def create(self, validated_data):
        properties_tmp = Property.objects.filter(property_name=validated_data['property_name'])
        if len(properties_tmp)>0:
            properties = Property.objects.get(property_name=validated_data['property_name'])
            properties.property_name = validated_data['property_name']
            properties.save()
        else:
            properties = Property.objects.create(
                property_name=validated_data['property_name'],
                editor_id=self.context['request'].user.id)
        return properties

    def update(self, instance, validated_data):
        properties_tmp = Property.objects.filter(property_name=validated_data['property_name'])
        if len(properties_tmp)<=0:
            instance.property_name = validated_data.get('property_name', instance.property_name)
            instance.save()
        return instance

class UnitSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    symbol = serializers.CharField(max_length=255)
    base = serializers.BooleanField(default=False)

    def create(self, validated_data):
        units_tmp = Unit.objects.filter(symbol=validated_data['symbol'])
        if len(units_tmp)>0:
            units = Unit.objects.get(symbol=validated_data['symbol'])
            units.symbol = validated_data['symbol']
            units.base = validated_data['base']
            units.save()
        else:
            units = Unit.objects.create(
                symbol=validated_data['symbol'],
                base=validated_data['base'],
                editor_id=self.context['request'].user.id)
        return units

    def update(self, instance, validated_data):
        units_tmp = Unit.objects.filter(symbol=validated_data['symbol'])

        if Q(1,instance.symbol).to(validated_data['symbol']).magnitude == 1:
            if len(units_tmp)<=0:
                instance.symbol = validated_data.get('symbol', instance.symbol)
                instance.save()
        return instance

class FigureSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    figure_name = serializers.CharField(max_length=255)
    #↓CharよりIntの方が良い？また確認する
    node = serializers.CharField(max_length=255)
    property_x = PropertySerializer(read_only=True)#serializers.CharField(max_length=255, allow_blank=True)
    property_y = PropertySerializer(read_only=True)#serializers.CharField(max_length=255, allow_blank=True)
    property_z = PropertySerializer(read_only=True)#serializers.CharField(max_length=255, allow_blank=True)
    property_x_id = serializers.CharField(max_length=255, allow_blank=True, write_only=True)
    property_y_id = serializers.CharField(max_length=255, allow_blank=True, write_only=True)
    property_z_id = serializers.CharField(max_length=255, allow_blank=True, write_only=True)

    datatype = serializers.IntegerField()
    is_condition = serializers.BooleanField(default=False)
    cluster = serializers.IntegerField(default=2)

    def create(self, validated_data):
        node = Node.objects.get(id=str(validated_data['node']))
        if validated_data['property_x_id']!='':  property_x = Property.objects.get(id=validated_data['property_x_id'])
        else: property_x = None
        if validated_data['property_y_id']!='': property_y = Property.objects.get(id=validated_data['property_y_id'])
        else: property_y = None
        if validated_data['property_z_id']!='':  property_z = Property.objects.get(id=validated_data['property_z_id'])
        else: property_z = None
        datatype = validated_data['datatype']
        is_condition = validated_data['is_condition']
        cluster = validated_data['cluster']

        figures_tmp = Figure.objects.filter(figure_name=validated_data['figure_name'],
                                            node=node,
                                            property_x=property_x,
                                            property_y=property_y,
                                            property_z=property_z,
                                            is_condition=is_condition,
                                            cluster=cluster)
        if len(figures_tmp)>0:
            figures = Figure.objects.get(figure_name=validated_data['figure_name'],
                                            node=node,
                                            property_x=property_x,
                                            property_y=property_y,
                                            property_z=property_z,
                                            is_condition=is_condition,
                                            cluster=cluster)
            figures.figure_name=validated_data['figure_name']
            figures.node=node
            figures.property_x=property_x
            figures.property_y=property_y
            figures.property_z=property_z
            figures.save()
        else:
            figures = Figure.objects.create(figure_name=validated_data['figure_name'],
                                            node=node,
                                            property_x=property_x,
                                            property_y=property_y,
                                            property_z=property_z,
                                            datatype=datatype,
                                            is_condition=is_condition,
                                            cluster=cluster,
                                            editor_id=self.context['request'].user.id)
        return figures

    def update(self, instance, validated_data):
        if validated_data['property_x_id']!='':  property_x = Property.objects.get(id=validated_data['property_x_id'])
        else: property_x = None
        if validated_data['property_y_id']!='': property_y = Property.objects.get(id=validated_data['property_y_id'])
        else: property_y = None
        if validated_data['property_z_id']!='':  property_z = Property.objects.get(id=validated_data['property_z_id'])
        else: property_z = None
        instance.figure_name = validated_data.get('figure_name', instance.figure_name)
        instance.property_x = property_x
        instance.property_y = property_y
        instance.property_z = property_z
        instance.is_condition = validated_data.get('is_condition', instance.is_condition)
        instance.cluster = validated_data.get('cluster', instance.cluster)
        instance.datatype = validated_data.get('datatype', instance.datatype)
        instance.save()
        return instance

class DatumSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    unit_x = serializers.CharField(max_length=255, allow_blank=True)
    unit_y = serializers.CharField(max_length=255, allow_blank=True)
    unit_z = serializers.CharField(max_length=255, allow_blank=True)
    figure = serializers.CharField(max_length=255)
    data = serializers.JSONField()

    def create(self, validated_data):
        entity = Entity.objects.get(id=self.context['entityid'])

        figure = Figure.objects.get(id=validated_data['figure'])
        if validated_data['unit_x']!='':  unit_x = Unit.objects.get(id=validated_data['unit_x'])
        else: unit_x = None
        if validated_data['unit_y']!='': unit_y = Unit.objects.get(id=validated_data['unit_y'])
        else: unit_y = None
        if validated_data['unit_z']!='':  unit_z = Unit.objects.get(id=validated_data['unit_z'])
        else: unit_z = None

        data = validated_data['data']
        data["basedata"] = self.context['basedata']
        
        data_tmp = Datum.objects.filter(entity=entity, figure=figure)
        if len(data_tmp)>0:
            data_tmp = Datum.objects.filter(entity=entity, figure=figure)
            for dt in data_tmp:
                dt.is_deleted = True
                dt.save()
            data_tmp = Datum.objects.create(entity=entity,
                        unit_x=unit_x,
                        unit_y=unit_y,
                        unit_z=unit_z,
                        figure=figure,
                        data=data,
                        is_deleted=False,
                        editor_id=self.context['request'].user.id)

        else:
            data_tmp = Datum.objects.create(entity=entity,
                        unit_x=unit_x,
                        unit_y=unit_y,
                        unit_z=unit_z,
                        figure=figure,
                        data=data,
                        is_deleted=False,
                        editor_id=self.context['request'].user.id)
        return data_tmp

class ItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    item_name = serializers.CharField(max_length=255)

    def create(self, validated_data):
        item_tmp = Item.objects.filter(item_name=validated_data['item_name'])
        if len(item_tmp)>0:
            items = Item.objects.get(item_name=validated_data['item_name'])
            items.item_name = validated_data['item_name']
            items.save()
        else:
            items = Item.objects.create(
                item_name=validated_data['item_name'],
                editor_id=self.context['request'].user.id)

        return items

    def update(self, instance, validated_data):
        instance.item_name = validated_data.get('item_name', instance.item_name)
        instance.save()
        return instance


class ImageSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    image_name = serializers.CharField(max_length=255)
    image = serializers.ImageField(max_length=None,use_url=True)
    cluster = serializers.IntegerField(default=2)
    entity = serializers.CharField(max_length=255)

    def create(self, validated_data):
        entityid = validated_data['entity']
        entity = Entity.objects.get(id=entityid)
        images = Image.objects.create(
            image_name=validated_data['image_name'],
            cluster=validated_data['cluster'],
            image=validated_data['image'],
            entity=entity,
            editor_id=self.context['request'].user.id)

        return images

class HeadlineSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    headline_name = serializers.CharField(max_length=255)

    def create(self, validated_data):
        headline_tmp = Headline.objects.filter(headline_name=validated_data['headline_name'])
        if len(headline_tmp)>0:
            headlines = Headline.objects.get(headline_name=validated_data['headline_name'])
            headlines.headline_name = validated_data['headline_name']
            headlines.save()
        else:
            headlines = Headline.objects.create(
                headline_name=validated_data['headline_name'],
                editor_id=self.context['request'].user.id)

        return headlines

    def update(self, instance, validated_data):
        instance.headline_name = validated_data.get('headline_name', instance.headline_name)
        instance.save()
        return instance


class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    product_name = serializers.CharField(max_length=255)

    def create(self, validated_data):
        experiment = Experiment.objects.get(id=self.context['experimentid'])
        product_tmp = Product.objects.filter(experiment=experiment,product_name=validated_data['product_name'])
        if len(product_tmp)>0:
            products = Product.objects.get(experiment=experiment,product_name=validated_data['product_name'])
            products.product_name = validated_data['product_name']
            products.save()
        else:
            products = Product.objects.create(
                experiment=experiment,
                product_name=validated_data['product_name'],
                editor_id=self.context['request'].user.id)

        return products