from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    path('posts/', views.posts, name='posts'),
    path('projects/', views.projects, name='projects'),
    path('projects/<int:projectid>', views.project_detail, name='project_detail'),

    path('experiments/', views.experiments, name='experiments'),
    path('experiments/<int:experimentid>', views.experiment_detail, name='experiment_detail'),
    path('projects/<int:projectid>/experiments/', views.project_experiments, name='project_experiments'),
    path('projects/<int:projectid>/experiments/<int:experimentid>', views.project_experiment_delete, name='project_experiment_delete'),

    path('types/', views.types, name='types'),
    path('types/<int:typeid>', views.type_detail, name='type_detail'),
    path('types/<int:typeid>/nodes/', views.nodes, name='nodes'),
    path('nodes/<int:nodeid>', views.node_detail, name='node_detail'),

    path('physics/', views.physics, name='physics'),
    path('unit_check/', views.unit_check, name='unit_check'),

    path('quantities/', views.quantities, name='quantities'),
    path('units/<int:unitid>', views.unit_detail, name='unit_detail'),
    path('properties/<int:propertyid>', views.property_detail, name='property_detail'),
    path('properties/<int:propertyid>/units', views.property_unit, name='property_unit'),

    path('figures/', views.figures, name='figures'),
    path('figures/<int:figureid>', views.figure_detail, name='figure_detail'),

    path('blueprints/', views.blueprint, name='blueprint'),
    path('blueprints/<int:blueprintid>', views.blueprint_detail, name='blueprint_detail'),
    path('blueprints/<int:blueprintid>/boxes/<str:boxid>', views.entity, name='entity'),

    path('templates/', views.templates, name='templates'),
    path('templates/<int:templateid>', views.template_detail, name='template_detail'),

    path('tags/', views.tags, name='tags'),
    path('tags/<int:tagid>', views.tag_detail, name='tag_detail'),
    path('experiments/<int:experimentid>/tags/<int:tagid>/pins/', views.pins, name='pins'),
    path('experiments/<int:experimentid>/pins/', views.experiment_pins, name='experiment_pins'),
    path('tags/<int:tagid>/pins/', views.tag_pins, name='tag_pins'),

    path('entities/<int:entityid>/data/', views.data, name='data'),

    path('items/', views.items, name='items'),
    path('items/<int:itemid>', views.item_detail, name='item_detail'),

    path('products/', views.products, name='products'),
    path('products/<int:productid>', views.product_detail, name='product_detail'),
    path('experiments/<int:experimentid>/products/', views.experiment_products, name='experiment_products'),
    path('entities/<int:entityid>/products/', views.selected_product, name='selected_product'),
    path('entities/<int:entityid>/products/<int:productid>', views.definitions, name='definitions'),

    path('images/', views.images, name='images'),
    path('images/<int:imageid>', views.image_detail, name='image_detail'),
    path('entities/<int:entityid>/images/', views.entity_images, name='entity_images'),


    path('entities/<int:entityid>/items/<int:itemid>/descriptions/', views.descriptions, name='descriptions'),
    path('entities/<int:entityid>/descriptions/', views.entity_descriptions, name='entity_descriptions'),
    path('items/<int:itemid>/descriptions/', views.item_descriptions, name='item_descriptions'),

    path('nodes/<int:nodeid>/items/<int:itemid>/defaults/', views.defaults, name='defaults'),
    path('nodes/<int:nodeid>/defaults/', views.node_defaults, name='node_defaults'),
    path('items/<int:itemid>/defaults/', views.item_defaults, name='item_defaults'),

    path('headlines/', views.headlines, name='headlines'),
    path('headlines/<int:headlineid>', views.headline_detail, name='headline_detail'),
    path('entities/<int:entityid>/headlines/<int:headlineid>/sentences/', views.sentences, name='sentences'),
    path('entities/<int:entityid>/sentences/', views.entity_sentences, name='entity_sentences'),
    path('headlines/<int:headlineid>/sentences/', views.headline_sentences, name='headline_sentences'),

    path('experiments/<int:experimentid>/getdata/', views.getdata, name='getdata'),
    path('experiments/<int:experimentid>/getsummarizeddata/', views.getsummarizeddata, name='getsummarizeddata'),

]
urlpatterns = format_suffix_patterns(urlpatterns)