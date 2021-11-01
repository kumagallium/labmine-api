from django.shortcuts import render
from rest_framework import status
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from rest_framework.pagination import PageNumberPagination

from django.db.models import ProtectedError
from rest_framework.validators import ValidationError

from .serializer import ProjectSerializer,ExperimentSerializer,TypeSerializer, NodeSerializer, PropertySerializer, UnitSerializer, FigureSerializer,BlueprintSerializer, TemplateSerializer, TagSerializer, DatumSerializer, ItemSerializer, HeadlineSerializer, ImageSerializer, ProductSerializer
from account.models import User
from .models import Post, Project, Library, Experiment, Type, Node, Datum, Property, Unit, Quantity, Figure, Metakey, Metadata, Blueprint,Entity, Template, Tag, Pin, Product, Definition, Item, Description, Default, Headline, Sentence, Image, Explanation
import json
import datetime
import pandas as pd
import numpy as np 

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def posts(request):
    posts = Post.objects.filter(
        published_at__isnull=False).order_by('-published_at')
    post_list = serializers.serialize('json', posts)
    return HttpResponse(post_list, content_type="text/json-comment-filtered")

######################################
############## Project ###############
######################################
@api_view(['GET','POST'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def projects(request):
    context = {
        "request": request,
    }
    if request.method == 'GET':
        projects = Project.objects.prefetch_related("editor")
        project_list = serializers.serialize('json', projects)
        response = []
        for project in json.loads(project_list):
            editor_id = project["fields"]["editor"]
            editor = User.objects.get(id=int(editor_id)).username
            project["fields"]["editor"] = editor
            response.append(project)

        return Response(response)
    elif request.method == 'POST':
        serializer = ProjectSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','PUT','DELETE'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def project_detail(request,projectid):
    try:
        project = Project.objects.get(pk=projectid)
    except Project.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProjectSerializer(project)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ProjectSerializer(project, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


######################################
############# Expriments #############
######################################
@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def experiments(request):
    if request.method == 'GET':
        experiments = Experiment.objects.prefetch_related("editor")
        experiment_list = serializers.serialize('json', experiments)
        response = []
        for experiment in json.loads(experiment_list):
            editor_id = experiment["fields"]["editor"]
            editor = User.objects.get(id=int(editor_id)).username
            experiment["fields"]["editor"] = editor
            response.append(experiment)

        return Response(response)

@api_view(['GET','PUT'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def experiment_detail(request,experimentid):
    try:
        experiment = Experiment.objects.get(pk=experimentid)
    except Experiment.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        experiments = Experiment.objects.filter(pk=experimentid).prefetch_related("editor")
        response = json.loads(serializers.serialize('json', experiments))[0]
        editor_id = response["fields"]["editor"]
        editor = User.objects.get(id=int(editor_id)).username
        response["fields"]["editor"] = editor
        return Response(response)
    elif request.method == 'PUT':
        serializer = ExperimentSerializer(experiment, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','POST'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def project_experiments(request,projectid):
    context = {
        "request": request,
    }
    if request.method == 'GET':
        keywords = request.GET.get(key="keywords", default="")
        tags_tmp = request.GET.get(key="tags", default="")
        startdate = request.GET.get(key="startdate", default="")
        enddate = request.GET.get(key="enddate", default="")
        itemsperpage = int(request.GET.get(key="itemsperpage", default=10))

        library = list(Library.objects.filter(project=projectid).values_list('experiment',flat=True))
        
        expriments = Experiment.objects.filter(id__in=library).prefetch_related("editor")
        if keywords != "":
            keyworkdlist = keywords.split(" ")
            for keyword in keyworkdlist:
                expriments = expriments.filter(title__icontains=keyword)
        
        if startdate != "":
            startdate = datetime.datetime.strptime(startdate, "%Y-%m-%d")
            if enddate != "":
                enddate = datetime.datetime.strptime(enddate, "%Y-%m-%d")
                expriments = expriments.filter(created_at__range=[startdate,enddate+datetime.timedelta(days=1)])
            else:
                expriments = expriments.filter(created_at__date=startdate)

        experiment_list = serializers.serialize('json', expriments.order_by('-created_at'))
        response = []
        for experiment in json.loads(experiment_list):
            editor_id = experiment["fields"]["editor"]
            editor = User.objects.get(id=int(editor_id)).username
            experiment["fields"]["editor"] = editor
            experimentid = int(experiment["pk"])
            taglist = []
            for tagid in Pin.objects.filter(experiment_id=experimentid).values_list("tag",flat=True):
                taglist.append(Tag.objects.get(id=tagid).tag_name)
            experiment["fields"]["tags"] = taglist

            if tags_tmp != "":
                tags = tags_tmp.split(" ")
                cnt = 0
                for tag in tags:
                    if tag in " ".join(taglist):
                        cnt += 1
                if cnt > 0:
                    response.append(experiment)
            else:
                response.append(experiment)

        if itemsperpage>0:
            paginator = StandardResultsSetPagination()
            paginator.page_size = itemsperpage
            response = paginator.paginate_queryset(response, request)
            return paginator.get_paginated_response(response)
        else:
            return Response(response)
    elif request.method == 'POST':
        try:
            project = Project.objects.get(pk=projectid)
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = ExperimentSerializer(data=request.data, context=context)
        if serializer.is_valid():
            experiment = serializer.save()

            if len(Library.objects.filter(project=project,experiment=experiment)) <= 0:
                Library.objects.create(project=project,experiment=experiment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def project_experiment_delete(request,projectid, experimentid):
    try:
        project = Project.objects.get(pk=projectid)
        experiment = Experiment.objects.get(pk=experimentid)
        library = Library.objects.get(project=project,experiment=experiment)
    except Library.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        experiment.delete()
        library.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

######################################
################ Type ################
######################################
@api_view(['GET','POST'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def types(request):
    context = {
        "request": request,
    }
    if request.method == 'GET':
        concept = request.GET.get(key="concept", default=2)
        types = Type.objects.filter(concept=concept).prefetch_related("editor")
        types_list = serializers.serialize('json', types)
        response = []
        for tl in json.loads(types_list):
            editor_id = tl["fields"]["editor"]
            editor = User.objects.get(id=int(editor_id)).username
            tl["fields"]["editor"] = editor
            response.append(tl)

        return Response(response)
    elif request.method == 'POST':
        serializer = TypeSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','PUT','DELETE'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def type_detail(request,typeid):
    try:
        types = Type.objects.get(pk=typeid)
    except Type.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TypeSerializer(types)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = TypeSerializer(types, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            types.delete()
        except ProtectedError:
            raise ValidationError({
                'error': [
                    'This category cannot be deleted because one or more nodes are already registered.'
                ]
            })
        return Response(status=status.HTTP_204_NO_CONTENT)


######################################
############## Node ###############
######################################
@api_view(['GET','POST'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def nodes(request,typeid):
    context = {
        "request": request,
        "typeid":typeid
    }
    if request.method == 'GET':
        nodes = Node.objects.filter(typeid=typeid).prefetch_related("editor")
        node_list = serializers.serialize('json', nodes)
        response = []
        for node in json.loads(node_list):
            editor_id = node["fields"]["editor"]
            editor = User.objects.get(id=int(editor_id)).username
            node["fields"]["editor"] = editor
            response.append(node)

        return Response(response)
    elif request.method == 'POST':
        serializer = NodeSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','PUT','DELETE'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def node_detail(request,nodeid):
    try:
        node = Node.objects.get(pk=nodeid)
    except Node.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        response = Node.objects.filter(id=nodeid).values()[0]
        figures = Figure.objects.filter(node_id=nodeid).values()
        for fig in figures:
            if fig["property_x_id"]: property_x = Property.objects.filter(id=fig["property_x_id"]).values()[0]
            else: property_x = ""
            if fig["property_y_id"]: property_y = Property.objects.filter(id=fig["property_y_id"]).values()[0]
            else: property_y = ""
            if fig["property_z_id"]: property_z = Property.objects.filter(id=fig["property_z_id"]).values()[0]
            else: property_z = ""
            datatype = fig["datatype"]
            fig["property_x"]=property_x
            fig["property_y"]=property_y
            fig["property_z"]=property_z
            fig["datatype"]=datatype
            fig.pop("node_id")
        if len(figures)>0:
            response["figures"]=figures
        else:
            response["figures"]=[]#[{"figure_name": "","property_x": {"property_name":""},"property_y":  {"property_name":""},"property_z":  {"property_name":""},"datatype":0,"cluster":1},\
                                #{"figure_name": "","property_x": {"property_name":""},"property_y":  {"property_name":""},"property_z":  {"property_name":""},"datatype":0,"cluster":2}]
 
        return Response(response)
    elif request.method == 'PUT':
        serializer = NodeSerializer(node, data=request.data)
        if serializer.is_valid():
            #nodename = str(node.node_name)
            serializer.save()

            nodeid = serializer.data["id"]
            new_nodename = str(serializer.data["node_name"])
            blueprintidlist = list(set(Entity.objects.filter(node_id=nodeid).values_list('blueprint_id',flat=True)))
            for blueprintid in blueprintidlist:
                blueprint = Blueprint.objects.get(pk=blueprintid)
                
                #newflowdata = json.dumps(blueprint.flowdata).replace('"text": "'+nodename,'"text": "'+new_nodename)
                newflowdata = list(blueprint.flowdata)
                for flow in newflowdata:
                    if "nodeid" in flow["userData"]:
                        if flow["userData"]["nodeid"] == nodeid:
                            flow["labels"][0]["text"] = new_nodename
                blueprint.flowdata = json.loads(json.dumps(newflowdata))
                blueprint.save()

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            node.delete()
        except ProtectedError:
            raise ValidationError({
                'error': [
                    'This node cannot be deleted because one or more workflow are already registered.'
                ]
            })
        return Response(status=status.HTTP_204_NO_CONTENT)

######################################
############## Physics ###############
######################################
import pint
import scipy.constants as cnst

u = pint.UnitRegistry()
Q = u.Quantity
u.define('fraction = [] = frac')
u.define('percent = 1e-2 frac = pct')
u.define('ppm = 1e-6 fraction')

##コンパクトな基本単位
unitlist = list(dir(u))
siconvertlist = []
for unt in unitlist:
    try:
        siconvertlist.append({"unit":unt,"si_value":Q(1,unt).to_base_units().magnitude,"si_unit":str(Q(1,unt).to_base_units().units)})
    except:
        pass
df_unit = pd.DataFrame(siconvertlist)
siuniqlist = df_unit[df_unit["si_value"]==1].si_unit.unique()
sisymbol_dict = {}
for siunit in siuniqlist:
    symboltmp = "a"*100
    for symbol in df_unit[df_unit["si_value"]==1][df_unit["si_unit"]==siunit]["unit"]:
        if len(symboltmp)>=len(symbol):
            symboltmp = symbol
    sisymbol_dict.setdefault(siunit,"")
    sisymbol_dict[siunit] = symboltmp
sisymbol_dict.update({"kilogram * meter ** 2 / kelvin / second ** 2":"J/K"})
sisymbol_dict.update({"ampere * meter * second":"C m"})
sisymbol_dict.update({"pixel / meter":"pixel / meter"})
sisymbol_dict.update({"meter / kilogram":"m / kg"})
sisymbol_dict.update({"kilogram ** 0.5 * meter ** 1.5 / second":"(kg**0.5 m**1.5)/s"})#これは要検討
sisymbol_dict.update({"kilogram ** 0.5 / meter ** 0.5 / second":"kg**0.5/m**0.5/s"})#これは要検討
sisymbol_dict.update({"meter / second ** 2":"m/s**2"})
sisymbol_dict.update({"kilogram / meter ** 3":"kg/m**3"})
sisymbol_dict.update({"ampere * second ** 2 / kilogram / meter ** 2":"Hz/V"})
sisymbol_dict.update({"dimensionless":"dimensionless"})
sisymbol_dict.update({"kilogram / second ** 2":"kg/s**2"})
sisymbol_dict.update({"mole / meter ** 3":"mole/m**3"})
sisymbol_dict.update({"1 / mole":"1/mole"})
sisymbol_dict.update({"kilogram / meter / second":"Pa s"})
sisymbol_dict.update({"kilogram * meter ** 2 / kelvin / mole / second ** 2":"J/(K mol)"})
sisymbol_dict.update({"1 / meter":"1/m"})
sisymbol_dict.update({"meter ** 2 / second":"m**2/s"})
sisymbol_dict.update({"kilogram / meter":"kg/m"})
sisymbol_dict.update({"kilogram * meter ** 2 / second":"J s"})
sisymbol_dict.update({"kilogram * meter / ampere / second ** 3":"N/C"})
sisymbol_dict.update({"kilogram / second ** 3":"kg/s**3"})
sisymbol_dict.update({"meter ** 2":"m**2"})
sisymbol_dict.update({"ampere * meter ** 2":"J/T"})
sisymbol_dict.update({"ampere * meter ** 2 * second":"(J s)/T"})
sisymbol_dict.update({"kilogram * meter ** 4 / second ** 3":"W m**2"})
sisymbol_dict.update({"kelvin * meter":"m K"})
sisymbol_dict.update({"kilogram * meter ** 3 / ampere ** 2 / second ** 4":"N m**2/C**2"})
sisymbol_dict.update({"ampere ** 2 * second ** 4 / kilogram / meter ** 3":"F/m"})
sisymbol_dict.update({"ampere * second / mole":"C/mol"})
sisymbol_dict.update({"meter ** 3 / kilogram / second ** 2":"m**3/kg/s**2"})
sisymbol_dict.update({"kilogram * meter / ampere ** 2 / second ** 2":"N/A**2"})
sisymbol_dict.update({"radian / second":"rad/s"})
sisymbol_dict.update({"meter * second / kilogram":"(m s)/kg"})
sisymbol_dict.update({"ampere * second / kilogram":"(A s)/kg"})
sisymbol_dict.update({"kilogram / kelvin ** 4 / second ** 3":"W/(m**2 K**4)"})
sisymbol_dict.update({"kilogram ** 0.5 * meter ** 1.5 / second ** 2":"(kg**0.5 m**1.5)/s**2"})
sisymbol_dict.update({"second ** 2 / meter":"s**2/m"})
sisymbol_dict.update({"kilogram ** 0.5 / meter ** 1.5":"kg**0.5/m**1.5"})
sisymbol_dict.update({"kilogram ** 0.5 * meter ** 0.5 / second":"(kg**0.5 m**0.5)/s"})
sisymbol_dict.update({"kilogram ** 0.5 * meter ** 0.5":"kg**0.5 m**0.5"})
sisymbol_dict.update({"second / meter":"s/m"})
sisymbol_dict.update({"1 / kelvin / second":"Hz/K"})
sisymbol_dict.update({"meter ** 3":"m**3"})
sisymbol_dict.update({"kilogram":"kg"})

def getsisymbol(unit):
    return sisymbol_dict[unit]

def ucheck(unit):
    value = 1
    try:
        if unit == "":
            response = {"flag":False, "error":"Invalid Unit"}
        elif unit == "-":
            response = {"flag":True,"si":True,"si_value":1,"si_unit":"-"}
        else:
            mag = Q(value,unit).to_base_units().magnitude
            siunit = str(Q(value,unit).to_base_units().units)
            si = False
            if mag == value:
                si = True
            response = {"flag":True,"si":si,"si_value":mag,"si_unit":siunit}
    except:
        response = {"flag":False, "error":"Invalid Unit"}
    return response

def convert2si(value,unit):
    result = ucheck(unit)
    mgnitude = Q(value,unit).to_base_units().magnitude
    if result["si"]:
        siunit = unit
    else:
        try:
            siunit = getsisymbol(result["si_unit"])
        except:
            siunit = str((Q(value,unit)/(Q(value,unit).to_base_units().magnitude)).to_compact().units)
    return mgnitude,siunit

@api_view(['GET'])
def physics(request):
    # 基本単位リスト
    unitlist = list(dir(u))
    unittable = []
    error = []
    for unit in unitlist:
        try:
            unittable.append({"symbol":unit,"name":str(u[unit].units)})
        except:
            error.append(unit)
    unittable.append({"symbol":"-","name":"dimensionless quantity"})

    # 基本定数リスト
    cnsttable = []
    for k,v in cnst.physical_constants.items():
        cnsttable.append({"name":k,"unit":v[1],"value":v[0],"uncertainty":v[2]})
    
    # Prefix
    prefixtable=[{"name":"yocto","value":1e-24,"symbol":"y"},
                {"name":"zepto","value":1e-21,"symbol":"z"},
                {"name":"atto","value": 1e-18,"symbol":"a"},
                {"name":"femto","value":1e-15,"symbol":"f"},
                {"name":"pico","value": 1e-12,"symbol":"p"},
                {"name":"nano","value": 1e-9 ,"symbol":"n"},
                {"name":"micro","value":1e-6 ,"symbol":"u"},
                {"name":"milli","value":1e-3 ,"symbol":"m"},
                {"name":"centi","value":1e-2 ,"symbol":"c"},
                {"name":"deci","value": 1e-1 ,"symbol":"d"},
                {"name":"deca","value": 1e+1 ,"symbol":"d"},
                {"name":"hecto","value":1e2  ,"symbol":"h"},
                {"name":"kilo","value": 1e3  ,"symbol":"k"},
                {"name":"mega","value": 1e6  ,"symbol":"M"},
                {"name":"giga","value": 1e9  ,"symbol":"G"},
                {"name":"tera","value": 1e12 ,"symbol":"T"},
                {"name":"peta","value": 1e15 ,"symbol":"P"},
                {"name":"exa","value":  1e18 ,"symbol":"E"},
                {"name":"zetta","value":1e21 ,"symbol":"Z"},
                {"name":"yotta","value":1e24 ,"symbol":"Y"},
                {"name":"kibi","value":2**10,"symbol":"Ki"},
                {"name":"mebi","value":2**20,"symbol":"Mi"},
                {"name":"gibi","value":2**30,"symbol":"Gi"},
                {"name":"tebi","value":2**40,"symbol":"Ti"},
                {"name":"pebi","value":2**50,"symbol":"Pi"},
                {"name":"exbi","value":2**60,"symbol":"Ei"},
                {"name":"zebi","value":2**70,"symbol":"Zi"},
                {"name":"yobi","value":2**80,"symbol":"Yi"}]

    response = {"units":unittable,"constants":cnsttable,"prefix":prefixtable}
    
    return Response(response)

@api_view(['GET'])
def unit_check(request):
    value = 1
    unit = str(request.GET.get(key="unit", default=""))
    response = ucheck(unit)

    return Response(response)

######################################
############## Quantity ###############
######################################
def getDiffinitions(properties,units):
    property_list = json.loads(serializers.serialize('json', properties))
    unitdict = {}
    for unit in units:
        unitdict[unit["id"]]= unit["symbol"]#+" (Base unit)" if unit["base"] else unit["symbol"]

    response = []
    index = 1
    for prop in property_list:
        prop["id"]=index
        property_id = prop["pk"]
        prop_unit = list(Quantity.objects.filter(property_id=property_id).values_list('unit',flat=True))
        children = []
        for unit in prop_unit:
            index += 1
            children.append({ "id": index, "pk":unit, "name": unitdict[unit]})
        prop["name"] = prop["fields"]["property_name"]
        prop["children"] = children
        prop.pop("model")
        prop.pop("fields")
        response.append(prop)
        index += 1
    return response

@api_view(['GET','POST'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def quantities(request):
    context = {
        "request": request
    }
    if request.method == 'GET':
        properties = Property.objects.all()
        allunits = Unit.objects.all().values()
        response = getDiffinitions(properties,allunits)
        
        return Response(response)

    elif request.method == 'POST':
        prop_serializer = PropertySerializer(data=request.data, context=context)
        unit_serializer = UnitSerializer(data=request.data, context=context)
        if prop_serializer.is_valid():
            if unit_serializer.is_valid():
                prop = prop_serializer.save()
                unit = unit_serializer.save()
                editor = prop.editor
                if len(Quantity.objects.filter(property=prop,unit=unit)) <= 0:
                    Quantity.objects.create(property=prop,unit=unit,editor=editor)

                qobjects = Quantity.objects.filter(property=prop).values()
                baseflag = 0
                for qo in qobjects:
                    unitid = qo["unit_id"]
                    base = Unit.objects.filter(id=unitid).values()[0]["base"]
                    if base:
                        baseflag = 1
                
                if baseflag == 0:
                    mag, baseunit = convert2si(1,unit.symbol)
                    baseunit = Unit.objects.create(symbol=baseunit, base=True, editor=editor)
                    Quantity.objects.create(property=prop,unit=baseunit,editor=editor)

                response = qobjects

                return Response(response)
            else:
                return Response(unit_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(prop_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['GET','PUT','DELETE'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def property_detail(request,propertyid):
    try:
        prop = Property.objects.get(pk=propertyid)
    except Property.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PropertySerializer(prop)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = PropertySerializer(prop, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            prop.delete()
        except ProtectedError:
            raise ValidationError({
                'protect_error': [
                    'This property cannot be deleted because one or more units are already registered.'
                ]
            })
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def property_unit(request,propertyid):
    try:
        prop = Property.objects.get(pk=propertyid)
    except Property.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        unitids = Quantity.objects.filter(property_id=propertyid).values('unit')
        units = [Unit.objects.filter(pk=uid['unit']).values('id','symbol','created_at','updated_at')[0] for uid in unitids]
    
        return Response(units)

@api_view(['GET','PUT','DELETE'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def unit_detail(request,unitid):
    try:
        unit = Unit.objects.get(pk=unitid)
    except Unit.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UnitSerializer(unit)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = UnitSerializer(unit, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            unit.delete()
        except ProtectedError:
            raise ValidationError({
                'protect_error': [
                    'This unit cannot be deleted because one or more data are already registered.'
                ]
            })
        return Response(status=status.HTTP_204_NO_CONTENT)

######################################
############### Figure ###############
######################################
@api_view(['POST'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def figures(request):
    context = {
        "request": request
    }
    if request.method == 'POST':
        serializer = FigureSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','PUT','DELETE'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def figure_detail(request,figureid):
    try:
        figure = Figure.objects.get(pk=figureid)
    except Figure.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = FigureSerializer(figure)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = FigureSerializer(figure, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            figure.delete()
        except ProtectedError:
            raise ValidationError({
                'protect_error': [
                    'This figure cannot be deleted because one or more data are already registered.'
                ]
            })
        return Response(status=status.HTTP_204_NO_CONTENT)

######################################
############### Blueprint ###############
######################################
def filterjson(jsontext):
    jsontextafter = jsontext
    if len(jsontext) > 0:
        jsondict = eval(str(jsontext).replace("true","True").replace("false","False").replace("null","None"))
        df_json = pd.DataFrame(jsondict)
        df_json_fig = df_json[(df_json["type"]=="CustomFigure")|(df_json["type"]=="MaterialFigure")|(df_json["type"]=="ToolFigure")|(df_json["type"]=="PlanFigure")].dropna(axis=1).copy()
        filtercols = ['x', 'y', 'id', 'type', 'ports', 'labels', 'bgColor', 'cssClass', 'userData', 'draggable', 'selectable']
        df_json_fig = df_json_fig[filtercols]
        dictfig = df_json_fig.to_dict(orient='records')

        df_json_con = df_json[df_json["type"]=="draw2d.Connection"].dropna(axis=1).copy()
        if len(df_json_con) > 0:
            filtercols = ['id', 'type', 'alpha', 'color', 'cssClass','userData', 'draggable', 'selectable', 'policy', 'router', 'source','target','vertex','routingMetaData']
            df_json_con = df_json_con[filtercols]
            dictcon = df_json_con.to_dict(orient='records')
            dictfig.extend(dictcon)
        jsontextafter = dictfig

    return jsontextafter

@api_view(['POST','GET'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def blueprint(request):
    context = {
        "request": request
    }
    if request.method == 'GET':
        blueprints = Blueprint.objects.prefetch_related("editor")
        blueprint_list = serializers.serialize('json', blueprints)
        response = []
        for blueprint in json.loads(blueprint_list):
            editor_id = blueprint["fields"]["editor"]
            editor = User.objects.get(id=int(editor_id)).username
            blueprint["fields"]["editor"] = editor
            blueprint["fields"].pop("flowdata")
            response.append(blueprint)

        return Response(response)
    elif request.method == 'POST':
        #nodeids = list(set(request.POST.getlist("nodeids")))
        request.data['flowdata'] = filterjson(request.data['flowdata'])
        serializer = BlueprintSerializer(data=request.data, context=context)
        if serializer.is_valid():
            blueprint=serializer.save()
            figures = [fd for fd in serializer.data["flowdata"] if (fd["type"] == "CustomFigure")or(fd["type"] == "MaterialFigure")or(fd["type"] == "ToolFigure")]
            for fig in figures:
                nodeid = fig["userData"]["nodeid"]
                boxid = fig["id"]
                node = Node.objects.get(pk=nodeid)
                Entity.objects.create(node=node,blueprint=blueprint,boxid=boxid)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','PUT','DELETE'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def blueprint_detail(request,blueprintid):
    try:
        blueprint = Blueprint.objects.get(pk=blueprintid)
    except Blueprint.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = BlueprintSerializer(blueprint)
        #flowdata_tmp = serializer.data["flowdata"]
        return Response(serializer.data)
    elif request.method == 'PUT':
        request.data['flowdata'] = filterjson(request.data['flowdata'])
        serializer = BlueprintSerializer(blueprint, data=request.data)
        if serializer.is_valid():
            serializer.save()
            figures = [fd for fd in serializer.data["flowdata"] if (fd["type"] == "CustomFigure")or(fd["type"] == "MaterialFigure")or(fd["type"] == "ToolFigure")]
            for fig in figures:
                nodeid = fig["userData"]["nodeid"]
                boxid = fig["id"]
                node = Node.objects.get(pk=nodeid)
                if len(Entity.objects.filter(node=node,blueprint=blueprint,boxid=boxid))<=0:
                    Entity.objects.create(node=node,blueprint=blueprint,boxid=boxid)

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            blueprint.delete()
        except ProtectedError:
            raise ValidationError({
                'protect_error': [
                    'This blueprint cannot be deleted because one or more data are already registered.'
                ]
            })
        return Response(status=status.HTTP_204_NO_CONTENT)


######################################
############### Entity ###############
######################################
@api_view(['GET','POST','DELETE'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def entity(request,blueprintid, boxid):

    if request.method == 'GET':
        entity = Entity.objects.filter(blueprint_id=blueprintid, boxid=boxid)
        response = serializers.serialize('json', entity)

        return Response(json.loads(response))
    elif request.method == 'POST':
        entity_tmp = Entity.objects.filter(blueprint_id=blueprintid, boxid=boxid)
        if len(entity_tmp)==0:
            Entity.objects.create(blueprint_id=blueprintid, boxid=boxid)

        return Response(status=status.HTTP_201_CREATED)

    elif request.method == 'DELETE':
        entity = Entity.objects.filter(blueprint_id=blueprintid, boxid=boxid)
        if len(entity) > 0:
            if request.method == 'DELETE':
                entity.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response([])

######################################
############## Template ###############
######################################
@api_view(['POST','GET'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def templates(request):
    context = {
        "request": request
    }
    if request.method == 'GET':
        templates = Template.objects.prefetch_related("editor")
        template_list = serializers.serialize('json', templates)
        response = []
        for template in json.loads(template_list):
            editor_id = template["fields"]["editor"]
            editor = User.objects.get(id=int(editor_id)).username
            template["fields"]["editor"] = editor
            response.append(template)

        return Response(response)
    elif request.method == 'POST':
        serializer = TemplateSerializer(data=request.data, context=context)
        if serializer.is_valid():
            template=serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','PUT','DELETE'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def template_detail(request,templateid):
    try:
        template = Template.objects.get(pk=templateid)
    except Template.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TemplateSerializer(template)
        return Response(serializer.data)
        #response = Template.objects.filter(pk=templateid).values()[0]
        #return Response(response)
        
    elif request.method == 'PUT':
        serializer = TemplateSerializer(template, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        try:
            template.delete()
        except ProtectedError:
            raise ValidationError({
                'protect_error': [
                    'This template cannot be deleted because one or more data are already registered.'
                ]
            })
        return Response(status=status.HTTP_204_NO_CONTENT)


######################################
################ Tag #################
######################################
@api_view(['POST','GET'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def tags(request):
    context = {
        "request": request
    }
    if request.method == 'GET':
        tags = Tag.objects.prefetch_related("editor")
        tag_list = serializers.serialize('json', tags)
        response = []
        for tag in json.loads(tag_list):
            editor_id = tag["fields"]["editor"]
            editor = User.objects.get(id=int(editor_id)).username
            tag["fields"]["editor"] = editor
            response.append(tag)

        return Response(response)
    elif request.method == 'POST':
        serializer = TagSerializer(data=request.data, context=context)
        if serializer.is_valid():
            tag=serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','PUT','DELETE'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def tag_detail(request,tagid):
    try:
        tag = Tag.objects.get(pk=tagid)
    except Tag.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TagSerializer(tag)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = TagSerializer(tag, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        checkpin = Pin.objects.filter(tag_id=tagid)
        if len(checkpin) <1:
            tag.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


######################################
################ Pin #################
######################################
@api_view(['POST','DELETE'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def pins(request,experimentid,tagid):
    if request.method == 'POST':
        experiment = Experiment.objects.get(pk=experimentid)
        tag = Tag.objects.get(pk=tagid)
        if len(Pin.objects.filter(tag=tag,experiment=experiment)) <= 0:
            Pin.objects.create(tag=tag,experiment=experiment)
        return Response(status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        experiment = Experiment.objects.get(pk=experimentid)
        tag = Tag.objects.get(pk=tagid)
        if len(Pin.objects.filter(tag=tag,experiment=experiment)) > 0:
            Pin.objects.filter(tag=tag,experiment=experiment).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def experiment_pins(request,experimentid):
    if request.method == 'GET':
        experiment = Experiment.objects.get(pk=experimentid)
        pins = Pin.objects.filter(experiment=experiment)
        pins_list = serializers.serialize('json', pins)
        response = []
        for pin in json.loads(pins_list):
            tag_name = Tag.objects.get(id=pin["fields"]["tag"]).tag_name
            pin["fields"]["tag_name"] = tag_name
            response.append(pin)
    return Response(response)

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def tag_pins(request,tagid):
    if request.method == 'GET':
        tag = Tag.objects.get(pk=tagid)
        pins = Pin.objects.filter(tag=tag)
        response = json.loads(serializers.serialize('json', pins))
    return Response(response)

######################################
############### Data ###############
######################################
@api_view(['GET','POST'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def data(request,entityid):
    context = {
        "request": request,
        "entityid":entityid
    }
    if request.method == 'GET':
        data_tmp = Datum.objects.filter(entity_id=entityid,is_deleted=False).prefetch_related("editor")
        data_list = serializers.serialize('json', data_tmp)
        response = []
        for data in json.loads(data_list):
            editor_id = data["fields"]["editor"]
            editor = User.objects.get(id=int(editor_id)).username
            data["fields"]["editor"] = editor
            unit_x_name = ""
            unit_y_name = ""
            unit_z_name = ""
            if data["fields"]["unit_x"]:unit_x_name = Unit.objects.get(id=int(data["fields"]["unit_x"])).symbol
            if data["fields"]["unit_y"]:unit_y_name = Unit.objects.get(id=int(data["fields"]["unit_y"])).symbol
            if data["fields"]["unit_z"]:unit_z_name = Unit.objects.get(id=int(data["fields"]["unit_z"])).symbol
            data["fields"]["unit_x_name"] = unit_x_name
            data["fields"]["unit_y_name"] = unit_y_name
            data["fields"]["unit_z_name"] = unit_z_name
            if type(data["fields"]["data"]) == list:
                data["fields"]["data"] = data["fields"]["data"][0]

            response.append(data)

        return Response(response)
    elif request.method == 'POST':
        data_tmp = request.data
        rawdata  = data_tmp["data"]["rawdata"]
        datasize = len(rawdata)
        unit_x_id  = data_tmp["unit_x"]
        unit_y_id  = data_tmp["unit_y"]
        unit_z_id  = data_tmp["unit_z"]


        ## Preparation of data converted in SI units.
        basedata = []
        if datasize > 0:
            xunit_symbol = Unit.objects.filter(id=unit_x_id).values_list("symbol", flat=True)[0]
            xdata = [Q(xd,xunit_symbol).to_base_units().magnitude for xd in rawdata[0]]
            basedata.append(xdata)
        if datasize > 1:
            yunit_symbol = Unit.objects.filter(id=unit_y_id).values_list("symbol", flat=True)[0]
            ydata = [Q(yd,yunit_symbol).to_base_units().magnitude for yd in rawdata[1]]
            basedata.append(ydata)
        if datasize > 2:
            zunit_symbol = Unit.objects.filter(id=unit_z_id).values_list("symbol", flat=True)[0]
            zdata = [Q(zd,zunit_symbol).to_base_units().magnitude for zd in rawdata[2]]
            basedata.append(zdata)
        
        context["basedata"] = basedata

        serializer = DatumSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


######################################
############## Products ##############
######################################
@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def products(request):
    if request.method == 'GET':
        products = Product.objects.prefetch_related("editor")
        product_list = serializers.serialize('json', products)
        response = []
        for product in json.loads(product_list):
            editor_id = product["fields"]["editor"]
            editor = User.objects.get(id=int(editor_id)).username
            product["fields"]["editor"] = editor
            response.append(product)

        return Response(response)

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def product_detail(request,productid):
    if request.method == 'GET':
        products = Product.objects.filter(pk=productid).prefetch_related("editor")
        response = json.loads(serializers.serialize('json', products))[0]
        editor_id = response["fields"]["editor"]
        editor = User.objects.get(id=int(editor_id)).username
        response["fields"]["editor"] = editor
        return Response(response)

@api_view(['GET','POST'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def experiment_products(request,experimentid):
    context = {
        "request": request,
        "experimentid":experimentid
    }
    if request.method == 'GET':
        products = Product.objects.filter(experiment=experimentid).prefetch_related("editor")
        product_list = serializers.serialize('json', products)
        response = []
        for product in json.loads(product_list):
            editor_id = product["fields"]["editor"]
            editor = User.objects.get(id=int(editor_id)).username
            product["fields"]["editor"] = editor
            response.append(product)
        return Response(response)
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data, context=context)
        if serializer.is_valid():
            product=serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

######################################
############### Definition ###############
######################################
@api_view(['GET','PUT','POST','DELETE'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def definitions(request,entityid, productid):
    if request.method == 'GET':
        definition = Definition.objects.filter(entity_id=entityid, productid=productid)
        response = serializers.serialize('json', definition)

        return Response(json.loads(response))

    elif request.method == 'PUT':
        newname = request.data['product_name']
        products = Product.objects.filter(pk=productid)
        experimentid = products[0].experiment_id
        product_names = list(Product.objects.filter(experiment_id=experimentid).values_list("product_name", flat=True))
        if newname not in product_names:
            products.update(product_name=newname)
            return Response(status=status.HTTP_201_CREATED)
        else:
            newproduct = Product.objects.get(experiment_id=experimentid,product_name=newname)
            Definition.objects.filter(entity_id=entityid, product_id=productid).delete()
            entity = Entity.objects.get(pk=entityid)
            Definition.objects.create(product=newproduct,entity=entity)
            return Response(status=status.HTTP_201_CREATED)

    elif request.method == 'POST':
        entity = Entity.objects.get(pk=entityid)
        product = Product.objects.get(pk=productid)
        if len(Definition.objects.filter(product=product,entity=entity)) <= 0:
            Definition.objects.create(product=product,entity=entity)
        return Response(status=status.HTTP_201_CREATED)

    elif request.method == 'DELETE':
        definition = Definition.objects.filter(entity_id=entityid, product_id=productid)
        if len(definition) > 0:
            if request.method == 'DELETE':
                definition.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response([])

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def selected_product(request,entityid):
    if request.method == 'GET':
        definition = Definition.objects.filter(entity_id=entityid)

        response = json.loads(serializers.serialize('json', definition))
        if len(response) > 0:
            response = response[0]
            product_id = response["fields"]["product"]
            product_name = Product.objects.get(id=int(product_id)).product_name
            response["fields"]["product_name"] = product_name

        return Response(response)

######################################
############## Images ##############
######################################
@api_view(['POST','GET'])
def images(request):
    context = {
        "request": request,
    }
    if request.method == 'GET':
        images = Image.objects.prefetch_related("editor")
        image_list = serializers.serialize('json', images)
        response = []
        for image in json.loads(image_list):
            editor_id = image["fields"]["editor"]
            editor = User.objects.get(id=int(editor_id)).username
            image["fields"]["editor"] = editor
            response.append(image)

        return Response(response)
    elif request.method == 'POST':
        serializer = ImageSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','PUT','DELETE'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def image_detail(request,imageid):
    try:
        image = Image.objects.get(pk=imageid)
    except Image.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        response = json.loads(serializers.serialize('json', image))[0]
        return Response(response)
    elif request.method == 'PUT':
        serializer = ImageSerializer(image, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
    elif request.method == 'DELETE':
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def entity_images(request,entityid):
    if request.method == 'GET':
        images = Image.objects.filter(entity=entityid).prefetch_related("editor")
        image_list = serializers.serialize('json', images)
        response = []
        for image in json.loads(image_list):
            editor_id = image["fields"]["editor"]
            editor = User.objects.get(id=int(editor_id)).username
            image["fields"]["editor"] = editor
            response.append(image)
        return Response(response)


######################################
############### Item #################
######################################
@api_view(['POST','GET'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def items(request):
    context = {
        "request": request
    }
    if request.method == 'GET':
        items = Item.objects.prefetch_related("editor")
        item_list = serializers.serialize('json', items)
        response = []
        for item in json.loads(item_list):
            editor_id = item["fields"]["editor"]
            editor = User.objects.get(id=int(editor_id)).username
            item["fields"]["editor"] = editor
            response.append(item)

        return Response(response)
    elif request.method == 'POST':
        serializer = ItemSerializer(data=request.data, context=context)
        if serializer.is_valid():
            item=serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','PUT','DELETE'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def item_detail(request,itemid):
    try:
        item = Item.objects.get(pk=itemid)
    except Item.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ItemSerializer(item)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        checkdescription = len(Description.objects.filter(item_id=itemid))
        checkdefault = len(Default.objects.filter(item_id=itemid))
        if checkdescription + checkdefault <1:
            item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


######################################
############ Description #############
######################################
@api_view(['POST','DELETE'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def descriptions(request,entityid,itemid):
    if request.method == 'POST':
        entity = Entity.objects.get(pk=entityid)
        item = Item.objects.get(pk=itemid)

        if "values" in request.data.keys():
            values = request.data['values']
        else:
            values = []
        if "cluster" in request.data.keys():
            cluster = request.data['cluster']
        else:
            cluster = 2
        if len(Description.objects.filter(item=item,entity=entity,cluster=cluster)) <= 0:
            Description.objects.create(item=item,entity=entity,values=values,cluster=cluster)
        else:
            Description.objects.filter(item=item,entity=entity,cluster=cluster).update(values=values)
        return Response(status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        entity = Entity.objects.get(pk=entityid)
        item = Item.objects.get(pk=itemid)
        if "cluster" in request.data:
            cluster = request.data['cluster']
            if len(Description.objects.filter(item=item,entity=entity,cluster=cluster)) > 0:
                Description.objects.filter(item=item,entity=entity,cluster=cluster).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def entity_descriptions(request,entityid):
    if request.method == 'GET':
        entity = Entity.objects.get(pk=entityid)
        
        if "cluster" in request.GET.keys():
            cluster = request.GET['cluster']
            descriptions = Description.objects.filter(entity=entity,cluster=cluster)
        else:
            descriptions = Description.objects.filter(entity=entity)
        
        descriptions_list = serializers.serialize('json', descriptions)
        response = []
        for description in json.loads(descriptions_list):
            item_name = Item.objects.get(id=description["fields"]["item"]).item_name
            description["fields"]["item_name"] = item_name
            response.append(description)
    return Response(response)

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def item_descriptions(request,itemid):
    if request.method == 'GET':
        item = Item.objects.get(pk=itemid)
        descriptions = Description.objects.filter(item=item)
        response = json.loads(serializers.serialize('json', descriptions))
    return Response(response)


######################################
############## Default ###############
######################################
@api_view(['POST','DELETE'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def defaults(request,nodeid,itemid):
    if request.method == 'POST':
        node = Node.objects.get(pk=nodeid)
        item = Item.objects.get(pk=itemid)
        if "cluster" in request.data:
            cluster = request.data['cluster']
        else:
            cluster = False
        if len(Default.objects.filter(item=item,node=node,cluster=cluster)) <= 0:
            Default.objects.create(item=item,node=node,cluster=cluster)
        return Response(status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        node = Node.objects.get(pk=nodeid)
        item = Item.objects.get(pk=itemid)
        if "cluster" in request.data.keys():
            cluster = request.data['cluster']
            if len(Default.objects.filter(item=item,node=node,cluster=cluster)) > 0:
                Default.objects.filter(item=item,node=node,cluster=cluster).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def node_defaults(request,nodeid):
    if request.method == 'GET':
        node = Node.objects.get(pk=nodeid)
        if "cluster" in request.GET.keys():
            cluster = request.GET['cluster']
            defaults = Default.objects.filter(node=node,cluster=cluster)
        else:
            defaults = Default.objects.filter(node=node)
        defaults_list = serializers.serialize('json', defaults)
        response = []
        for default in json.loads(defaults_list):
            item_name = Item.objects.get(id=default["fields"]["item"]).item_name
            default["fields"]["item_name"] = item_name
            response.append(default)
    return Response(response)

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def item_defaults(request,itemid):
    if request.method == 'GET':
        item = Item.objects.get(pk=itemid)
        defaults = Default.objects.filter(item=item)
        response = json.loads(serializers.serialize('json', defaults))
    return Response(response)

def str2bool( value ):
    if isinstance( value, str ) and value.lower() == "false":
        return False
    return bool( value )



######################################
############### Headline #################
######################################
@api_view(['POST','GET'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def headlines(request):
    context = {
        "request": request
    }
    if request.method == 'GET':
        headlines = Headline.objects.prefetch_related("editor")
        headline_list = serializers.serialize('json', headlines)
        response = []
        for headline in json.loads(headline_list):
            editor_id = headline["fields"]["editor"]
            editor = User.objects.get(id=int(editor_id)).username
            headline["fields"]["editor"] = editor
            response.append(headline)

        return Response(response)
    elif request.method == 'POST':
        serializer = HeadlineSerializer(data=request.data, context=context)
        if serializer.is_valid():
            headline=serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET','PUT','DELETE'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def headline_detail(request,headlineid):
    try:
        headline = Headline.objects.get(pk=headlineid)
    except Headline.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = HeadlineSerializer(headline)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = HeadlineSerializer(headline, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        checksentence = len(Sentence.objects.filter(headline_id=headlineid))
        if checksentence < 1:
            headline.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


######################################
############ Sentence #############
######################################
@api_view(['POST','DELETE'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def sentences(request,entityid,headlineid):
    if request.method == 'POST':
        entity = Entity.objects.get(pk=entityid)
        headline = Headline.objects.get(pk=headlineid)

        if "value" in request.data.keys():
            value = request.data['value']
        else:
            value = ""
        cluster = request.data['cluster']
        if len(Sentence.objects.filter(headline=headline,entity=entity,cluster=cluster)) <= 0:
            Sentence.objects.create(headline=headline,entity=entity,value=value,cluster=cluster)
        else:
            Sentence.objects.filter(headline=headline,entity=entity,cluster=cluster).update(value=value)
        return Response(status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        entity = Entity.objects.get(pk=entityid)
        headline = Headline.objects.get(pk=headlineid)
        if "cluster" in request.data:
            cluster = request.data['cluster']
            if len(Sentence.objects.filter(headline=headline,entity=entity,cluster=cluster)) > 0:
                Sentence.objects.filter(headline=headline,entity=entity,cluster=cluster).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def entity_sentences(request,entityid):
    if request.method == 'GET':
        entity = Entity.objects.get(pk=entityid)
        
        sentences = Sentence.objects.filter(entity=entity)
        sentences_list = serializers.serialize('json', sentences)
        response = []
        for sentence in json.loads(sentences_list):
            headline_name = Headline.objects.get(id=sentence["fields"]["headline"]).headline_name
            sentence["fields"]["headline_name"] = headline_name
            response.append(sentence)
    return Response(response)

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def headline_sentences(request,headlineid):
    if request.method == 'GET':
        headline = Headline.objects.get(pk=headlineid)
        sentences = Sentence.objects.filter(headline=headline)
        response = json.loads(serializers.serialize('json', sentences))
    return Response(response)


######################################
############ getdata #############
######################################
def setnodeid(userdata):
    nodeid = ""
    if "nodeid" in userdata.keys():
        nodeid = userdata["nodeid"]
    return nodeid

def setisdone(ports):
    is_done = 0
    for port in ports:
        if port["type"] == "draw2d.OutputPort":
            if "is_done" in port["userData"].keys():
                is_done = port["userData"]["is_done"]
    return is_done

def setisdata(ports):
    is_data = 0
    for port in ports:
        if port["type"] == "draw2d.OutputPort":
            if "is_data" in port["userData"].keys():
                is_data = port["userData"]["is_data"]
    return is_data

def setsourcetarget(st):
    return st["node"]

def setproperty(property):
    return {"propertyid":property["id"],"property_name":property["property_name"]}

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def getdata(request,experimentid):
    if request.method == 'GET':
        clusterdict = {0:"Plan",1:"Methods",2:"Results"}
        experiment = Experiment.objects.filter(pk=experimentid).values()[0]
        
        #Experiment
        tmpjson = {"experiment":{
            "experiment_id":experimentid,
            "title":experiment["title"]
        }}
        blueprintid = experiment["blueprint_id"]

        #Project
        library =Library.objects.filter(experiment_id=experimentid).values()[0]
        projectid = library["project_id"]
        project = Project.objects.filter(pk=projectid).values()[0]
        tmpjson["project"]={
            "project_id":projectid,
            "project_name":project["project_name"]
        }

        #Tag
        pins = list(Pin.objects.filter(experiment_id=experimentid).values_list('tag_id', flat=True))
        tags = Tag.objects.filter(pk__in=pins).values_list('tag_name', flat=True)
        tmpjson["experiment"]["tags"]=tags

        #Blueprint
        blueprint = Blueprint.objects.filter(pk=blueprintid).values()[0]
        blueprintid = blueprint["id"]
        flowdata = blueprint["flowdata"]
        dictnode = []
        dictcon = []
        if len(flowdata) > 0:
            jsondict = eval(str(flowdata).replace("true","True").replace("false","False").replace("null","None"))
            df_json = pd.DataFrame(jsondict)
            df_json_node = df_json[(df_json["type"]=="CustomFigure")|(df_json["type"]=="MaterialFigure")|(df_json["type"]=="ToolFigure")].dropna(axis=1).copy()
            df_json_node["nodeid"]=df_json_node["userData"].apply(setnodeid)
            df_json_node["is_done"]=df_json_node["ports"].apply(setisdone)
            df_json_node["blockid"]=df_json_node["id"]
            #df_json_node["is_data"]=df_json_node["ports"].apply(setisdata)
            filtercols = ['x', 'y', 'blockid','nodeid','is_done']#,'is_data']
            df_json_node = df_json_node[filtercols]
            dictnode = df_json_node.to_dict(orient='records')

            df_json_con = df_json[df_json["type"]=="draw2d.Connection"].dropna(axis=1).copy()
            if len(df_json_con) > 0:
                df_json_con["source"]=df_json_con["source"].apply(setsourcetarget)
                df_json_con["target"]=df_json_con["target"].apply(setsourcetarget)
                filtercols = ['id','source','target']
                df_json_con = df_json_con[filtercols]
                dictcon = df_json_con.to_dict(orient='records')
        tmpjson["connections"] = dictcon

        #Node
        for idx, node in enumerate(dictnode):
            nodeid = node["nodeid"]
            nodes = Node.objects.filter(pk=nodeid).values()[0]
            node["node_name"] = nodes["node_name"]
            typeid = nodes["typeid_id"]
            node["typeid"] = typeid

            #Type
            typename = Type.objects.filter(pk=typeid).values_list("type_name")[0][0]
            node["type_name"] = typename

            #Entity
            entityid = Entity.objects.filter(blueprint_id=blueprintid,node_id=nodeid,boxid=node["blockid"]).values()[0]["id"]

            #Figure
            figures = Figure.objects.filter(node_id=nodeid).values()
            for fig in figures:
                if fig["property_x_id"]: property_x = Property.objects.filter(id=fig["property_x_id"]).values()[0]
                else: property_x = ""
                if fig["property_y_id"]: property_y = Property.objects.filter(id=fig["property_y_id"]).values()[0]
                else: property_y = ""
                if fig["property_z_id"]: property_z = Property.objects.filter(id=fig["property_z_id"]).values()[0]
                else: property_z = ""
                datatype = fig["datatype"]
                fig["property"]=[]
                if property_x: fig["property"].append(setproperty(property_x))
                if property_y: fig["property"].append(setproperty(property_y))
                if property_z: fig["property"].append(setproperty(property_z))
                fig["datatype"]=datatype
                fig["clusterid"] = fig["cluster"]
                fig["cluster"] = clusterdict[fig["cluster"]]
                fig["figureid"] = fig["id"]
                fig.pop("id")
                fig.pop("node_id")
                fig.pop("property_x_id")
                fig.pop("property_y_id")
                fig.pop("property_z_id")
                fig.pop("is_condition")
                fig.pop("created_at")
                fig.pop("updated_at")
                fig.pop("editor_id")
                figureid = fig["figureid"]

                #Data
                data = Datum.objects.filter(is_deleted=0).filter(entity_id=entityid,figure_id=figureid).values("data","unit_x_id","unit_y_id","unit_z_id")
                if len(data)>0:
                    data = data[0]
                    if type(data["data"]) == list:
                        data["data"] = data["data"][0]
                    units = []
                    if data["unit_x_id"]:
                        unitname = Unit.objects.filter(id=data["unit_x_id"]).values()[0]["symbol"]
                        units.append({"unitid":data["unit_x_id"],"unit_name":unitname})
                    if data["unit_y_id"]:
                        unitname = Unit.objects.filter(id=data["unit_y_id"]).values()[0]["symbol"]
                        units.append({"unitid":data["unit_y_id"],"unit_name":unitname})
                    if data["unit_z_id"]:
                        unitname = Unit.objects.filter(id=data["unit_z_id"]).values()[0]["symbol"]
                        units.append({"unitid":data["unit_z_id"],"unit_name":unitname})
                    fig["rawdata"] = {
                        "values":data["data"]["rawdata"],
                        "units":units
                    }
                else:
                    fig["rawdata"] = []

                #Metadata
                metadata = Metadata.objects.filter(figure_id=figureid).values()
                metadtmp = []
                if len(metadata) > 0:
                    for metad in metadata:
                        itemid = metad["item_id"]
                        itemname = Item.objects.filter(pk=itemid).values()[0]["item_name"]
                        metadata = {
                            "metadataid":metad["id"],
                            "values":metad["values"],
                            "itemid":itemid,
                            "item_name":itemname
                        }
                        metadtmp.append(metadata)
                fig["metadata"] = metadtmp
            
                #Explanation
                explanations = Explanation.objects.filter(figure_id=figureid).values()
                exptmp = []
                if len(explanations) > 0:
                    for exp in explanations:
                        headlineid = exp["headline_id"]
                        headlinename = Headline.objects.filter(pk=headlineid).values()[0]["headline_name"]
                        explanation = {
                            "explanationid":exp["id"],
                            "value":exp["value"],
                            "headlineid":headlineid,
                            "headline_name":headlinename
                        }
                        exptmp.append(explanation)
                fig["explanation"] = exptmp

            if len(figures)>0:
                node["figures"]=figures
            else:
                node["figures"]=[]

            #Description
            descriptions = Description.objects.filter(entity_id=entityid).values()
            desctmp = []
            if len(descriptions) > 0:
                for desc in descriptions:
                    itemid = desc["item_id"]
                    itemname = Item.objects.filter(pk=itemid).values()[0]["item_name"]
                    description = {
                        "descriptionid":desc["id"],
                        "values":desc["values"],
                        "clusterid":desc["cluster"],
                        "cluster":clusterdict[desc["cluster"]],
                        "itemid":itemid,
                        "item_name":itemname
                    }
                    desctmp.append(description)
            node["descriptions"] = desctmp
        
            #Sentence
            sentences = Sentence.objects.filter(entity_id=entityid).values()
            senttmp = []
            if len(sentences) > 0:
                for sent in sentences:
                    headlineid = sent["headline_id"]
                    headlinename = Headline.objects.filter(pk=headlineid).values()[0]["headline_name"]
                    sentence = {
                        "sentenceid":sent["id"],
                        "value":sent["value"],
                        "clusterid":sent["cluster"],
                        "cluster":clusterdict[sent["cluster"]],
                        "headlineid":headlineid,
                        "headline_name":headlinename
                    }
                    senttmp.append(sentence)
            node["sentence"] = senttmp

            #Image
            images = Image.objects.filter(entity_id=entityid).values()
            imgtmp = []
            if len(images) > 0:
                for img in images:
                    image = {
                        "imageid":img["id"],
                        "image_name":img["image_name"],
                        "clusterid":img["cluster"],
                        "cluster":clusterdict[img["cluster"]],
                        "image":img["image"],
                    }
                    imgtmp.append(image)
            node["image"] = imgtmp

        tmpjson["blocks"] = dictnode

        response = tmpjson

        return Response(response)

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
@authentication_classes((JWTTokenUserAuthentication,))
def getsummarizeddata(request,experimentid):
    if request.method == 'GET':
        clusterdict = {0:"plan",1:"methods",2:"results"}
        experiment = Experiment.objects.filter(pk=experimentid).values()[0]
        
        #Experiment
        tmpjson = {"experiment":{
            "experiment_id":experimentid,
            "title":experiment["title"]
        }}
        blueprintid = experiment["blueprint_id"]

        #Project
        library =Library.objects.filter(experiment_id=experimentid).values()[0]
        projectid = library["project_id"]
        project = Project.objects.filter(pk=projectid).values()[0]
        tmpjson["project"]={
            "project_id":projectid,
            "project_name":project["project_name"]
        }

        #Tag
        pins = list(Pin.objects.filter(experiment_id=experimentid).values_list('tag_id', flat=True))
        tags = Tag.objects.filter(pk__in=pins).values_list('tag_name', flat=True)
        tmpjson["experiment"]["tags"]=tags

        #Blueprint
        blueprint = Blueprint.objects.filter(pk=blueprintid).values()[0]
        flowdata = blueprint["flowdata"]
        dictnode = []
        if len(flowdata) > 0:
            jsondict = eval(str(flowdata).replace("true","True").replace("false","False").replace("null","None"))
            df_json = pd.DataFrame(jsondict)
            df_json_node = df_json[(df_json["type"]=="CustomFigure")|(df_json["type"]=="MaterialFigure")|(df_json["type"]=="ToolFigure")|(df_json["type"]=="PlanFigure")].dropna(axis=1).copy()
            df_json_node["nodeid"]=df_json_node["userData"].apply(setnodeid)
            df_json_node["blockid"]=df_json_node["id"]
            filtercols = ['nodeid','blockid']
            df_json_node = df_json_node[filtercols]
            dictnode = df_json_node.to_dict(orient='records')

        summarizebase = {
            "plan":{
                "figures":[],
                "images":[],
                "products":[],
                "descriptions":[],
                "sentences":[]
		    },
            "methods":{
                "figures":[],
                "images":[],
                "products":[],
                "descriptions":[],
                "sentences":[]
		    },
            "results":{
                "figures":[],
                "images":[],
                "products":[],
                "descriptions":[],
                "sentences":[]
		    },
        }

        #Node
        for idx, node in enumerate(dictnode):
            nodeid = node["nodeid"]
            node["node_name"] = "Plan"
            typeid = ""
            if nodeid != "":
                nodes = Node.objects.filter(pk=nodeid).values()[0]
                node["node_name"] = nodes["node_name"]
                typeid = nodes["typeid_id"]
            node["typeid"] = typeid

            #Type
            node["type_name"] = "Plan"
            node["concept"] = 2
            if typeid != "":
                type_tmp = Type.objects.filter(pk=typeid).values_list("type_name","concept")[0]
                typename = type_tmp[0]
                concept = type_tmp[1]
                node["type_name"] = typename
                node["concept"] = concept

            #Entity
            entityid = Entity.objects.filter(blueprint_id=blueprintid,boxid=node["blockid"]).values()[0]["id"]

            #Production
            definition = Definition.objects.filter(entity_id=entityid)
            if len(definition) > 0:
                productid = definition[0].product_id
                production = Product.objects.filter(pk=productid).values()
                productname = production[0]["product_name"]
            else:
                productid = ""
                if node["concept"] == 2:
                    productname = "entity-"+str(entityid)
                else:
                    productname = node["node_name"]

            #Figure
            if nodeid != "":
                figures = Figure.objects.filter(node_id=nodeid).values()
                for fig in figures:
                    samefigcheck = 0
                    for i, fg in enumerate(summarizebase[clusterdict[fig["cluster"]]]["figures"]):
                        if fg["figure_id"] == fig["id"]:
                            samefigcheck = 1
                            samefigidx = i
                    if samefigcheck == 0:
                        if fig["property_x_id"]: property_x = Property.objects.filter(id=fig["property_x_id"]).values()[0]
                        else: property_x = ""
                        if fig["property_y_id"]: property_y = Property.objects.filter(id=fig["property_y_id"]).values()[0]
                        else: property_y = ""
                        if fig["property_z_id"]: property_z = Property.objects.filter(id=fig["property_z_id"]).values()[0]
                        else: property_z = ""
                        datatype = fig["datatype"]
                        fig["property"]=[]
                        if property_x: fig["property"].append(setproperty(property_x))
                        if property_y: fig["property"].append(setproperty(property_y))
                        if property_z: fig["property"].append(setproperty(property_z))
                        fig["datatype"]=datatype
                        fig["figure_id"] = fig["id"]
                        fig["node_id"] = nodeid
                        fig["node_name"] = node["node_name"]
                        fig["concept"] = node["concept"]
                        fig["type_id"] = typeid
                        fig["type_name"] = node["type_name"]
                        fig.pop("id")
                        fig.pop("node_id")
                        fig.pop("property_x_id")
                        fig.pop("property_y_id")
                        fig.pop("property_z_id")
                        fig.pop("is_condition")
                        fig.pop("created_at")
                        fig.pop("updated_at")
                        fig.pop("editor_id")
                        figureid = fig["figure_id"]

                        #Data
                        data = Datum.objects.filter(is_deleted=0).filter(entity_id=entityid,figure_id=figureid).values("data","unit_x_id","unit_y_id","unit_z_id")
                        if len(data)>0:
                            data = data[0]
                            if type(data["data"]) == list:
                                data["data"] = data["data"][0]
                            units = []
                            if data["unit_x_id"]:
                                xprop_id = Quantity.objects.filter(unit_id=data["unit_x_id"]).values_list("property_id", flat=True)[0]
                                xunit_ids = Quantity.objects.filter(property_id=xprop_id).values_list("unit_id", flat=True)
                                xunits = Unit.objects.filter(id__in=xunit_ids).values("id","symbol","base")

                                xsiunit_id = [xu["id"] for xu in xunits if xu["base"]]
                                if len(xsiunit_id)>0:
                                    xsiunit_id = xsiunit_id[0]
                                    xsiunit = [xu["symbol"] for xu in xunits if xu["base"]][0]
                                else:
                                    xsiunit_id = ""
                                    xsymbol = Unit.objects.filter(id=data["unit_x_id"]).values_list("symbol", flat=True)[0]
                                    _, xsiunit = convert2si(1,xsymbol)

                                units.append({"unitid":xsiunit_id,"unit_name":xsiunit})

                            if data["unit_y_id"]:
                                yprop_id = Quantity.objects.filter(unit_id=data["unit_y_id"]).values_list("property_id", flat=True)[0]
                                yunit_ids = Quantity.objects.filter(property_id=yprop_id).values_list("unit_id", flat=True)
                                yunits = Unit.objects.filter(id__in=yunit_ids).values("id","symbol","base")

                                ysiunit_id = [yu["id"] for yu in yunits if yu["base"]]
                                if len(ysiunit_id)>0:
                                    ysiunit_id = ysiunit_id[0]
                                    ysiunit = [yu["symbol"] for yu in yunits if yu["base"]][0]
                                else:
                                    ysiunit_id = ""
                                    ysymbol = Unit.objects.filter(id=data["unit_y_id"]).values_list("symbol", flat=True)[0]
                                    _, ysiunit = convert2si(1,ysymbol)

                                units.append({"unitid":ysiunit_id,"unit_name":ysiunit})

                            if data["unit_z_id"]:
                                zprop_id = Quantity.objects.filter(unit_id=data["unit_z_id"]).values_list("property_id", flat=True)[0]
                                zunit_ids = Quantity.objects.filter(property_id=zprop_id).values_list("unit_id", flat=True)
                                zunits = Unit.objects.filter(id__in=zunit_ids).values("id","symbol","base")
                               
                                zsiunit_id = [zu["id"] for zu in zunits if zu["base"]]
                                if len(zsiunit_id)>0:
                                    zsiunit_id = zsiunit_id[0]
                                    zsiunit = [zu["symbol"] for zu in zunits if zu["base"]][0]
                                else:
                                    zsiunit_id = ""
                                    zsymbol = Unit.objects.filter(id=data["unit_z_id"]).values_list("symbol", flat=True)[0]
                                    _, zsiunit = convert2si(1,zsymbol)

                                units.append({"unitid":zsiunit_id,"unit_name":zsiunit})
                            fig["rawdata"] = [{
                                "product_id":productid,
                                "product_name":productname,
                                "values":data["data"]["basedata"] if "basedata" in data["data"] else np.zeros_like(data["data"]["rawdata"]),
                                "units":units
                            }]    
                        else:
                            fig["rawdata"] = []

                        #Metadata
                        metadata = Metadata.objects.filter(figure_id=figureid).values()
                        metadtmp = []
                        if len(metadata) > 0:
                            for metad in metadata:
                                itemid = metad["item_id"]
                                itemname = Item.objects.filter(pk=itemid).values()[0]["item_name"]
                                metadata = {
                                    "product_id":productid,
                                    "product_name":productname,
                                    "metadataid":metad["id"],
                                    "values":metad["values"],
                                    "itemid":itemid,
                                    "item_name":itemname
                                }
                                metadtmp.append(metadata)
                        fig["metadata"] = metadtmp
                    
                        #Explanation
                        explanations = Explanation.objects.filter(figure_id=figureid).values()
                        exptmp = []
                        if len(explanations) > 0:
                            for exp in explanations:
                                headlineid = exp["headline_id"]
                                headlinename = Headline.objects.filter(pk=headlineid).values()[0]["headline_name"]
                                explanation = {
                                    "product_id":productid,
                                    "product_name":productname,
                                    "explanationid":exp["id"],
                                    "value":exp["value"],
                                    "headlineid":headlineid,
                                    "headline_name":headlinename
                                }
                                exptmp.append(explanation)
                        fig["explanation"] = exptmp

                        summarizebase[clusterdict[fig["cluster"]]]["figures"].append(fig)
                    else:
                        #Data
                        figureid = fig["id"]
                        data = Datum.objects.filter(is_deleted=0).filter(entity_id=entityid,figure_id=figureid).values("data","unit_x_id","unit_y_id","unit_z_id")
                        if len(data)>0:
                            data = data[0]
                            if type(data["data"]) == list:
                                data["data"] = data["data"][0]
                            units = []
                            if data["unit_x_id"]:
                                xprop_id = Quantity.objects.filter(unit_id=data["unit_x_id"]).values_list("property_id", flat=True)[0]
                                xunit_ids = Quantity.objects.filter(property_id=xprop_id).values_list("unit_id", flat=True)
                                xunits = Unit.objects.filter(id__in=xunit_ids).values("id","symbol","base")

                                xsiunit_id = [xu["id"] for xu in xunits if xu["base"]]
                                if len(xsiunit_id)>0:
                                    xsiunit_id = xsiunit_id[0]
                                    xsiunit = [xu["symbol"] for xu in xunits if xu["base"]][0]
                                else:
                                    xsiunit_id = ""
                                    xsymbol = Unit.objects.filter(id=data["unit_x_id"]).values_list("symbol", flat=True)[0]
                                    _, xsiunit = convert2si(1,xsymbol)
                                units.append({"unitid":xsiunit_id,"unit_name":xsiunit})

                            if data["unit_y_id"]:
                                yprop_id = Quantity.objects.filter(unit_id=data["unit_y_id"]).values_list("property_id", flat=True)[0]
                                yunit_ids = Quantity.objects.filter(property_id=yprop_id).values_list("unit_id", flat=True)
                                yunits = Unit.objects.filter(id__in=yunit_ids).values("id","symbol","base")

                                ysiunit_id = [yu["id"] for yu in yunits if yu["base"]]
                                if len(ysiunit_id)>0:
                                    ysiunit_id = ysiunit_id[0]
                                    ysiunit = [yu["symbol"] for yu in yunits if yu["base"]][0]
                                else:
                                    ysiunit_id = ""
                                    ysymbol = Unit.objects.filter(id=data["unit_y_id"]).values_list("symbol", flat=True)[0]
                                    _, ysiunit = convert2si(1,ysymbol)
                                units.append({"unitid":ysiunit_id,"unit_name":ysiunit})

                            if data["unit_z_id"]:
                                zprop_id = Quantity.objects.filter(unit_id=data["unit_z_id"]).values_list("property_id", flat=True)[0]
                                zunit_ids = Quantity.objects.filter(property_id=zprop_id).values_list("unit_id", flat=True)
                                zunits = Unit.objects.filter(id__in=zunit_ids).values("id","symbol","base")

                                zsiunit_id = [zu["id"] for zu in zunits if zu["base"]]
                                if len(zsiunit_id)>0:
                                    zsiunit_id = zsiunit_id[0]
                                    zsiunit = [zu["symbol"] for zu in zunits if zu["base"]][0]
                                else:
                                    zsiunit_id = ""
                                    zsymbol = Unit.objects.filter(id=data["unit_z_id"]).values_list("symbol", flat=True)[0]
                                    _, zsiunit = convert2si(1,zsymbol)
                                units.append({"unitid":zsiunit_id,"unit_name":zsiunit})

                            datatmp = {
                                "product_id":productid,
                                "product_name":productname,
                                "values":data["data"]["basedata"] if "basedata" in data["data"] else np.zeros_like(data["data"]["rawdata"]),
                                "units":units
                            }
                            summarizebase[clusterdict[fig["cluster"]]]["figures"][samefigidx]["rawdata"].append(datatmp)

                        #Metadata
                        metadata = Metadata.objects.filter(figure_id=figureid).values()
                        metadtmp = []
                        if len(metadata) > 0:
                            for metad in metadata:
                                itemid = metad["item_id"]
                                itemname = Item.objects.filter(pk=itemid).values()[0]["item_name"]
                                metadata = {
                                    "product_id":productid,
                                    "product_name":productname,
                                    "metadataid":metad["id"],
                                    "values":metad["values"],
                                    "itemid":itemid,
                                    "item_name":itemname
                                }
                                metadtmp.append(metadata)
                        summarizebase[clusterdict[fig["cluster"]]]["figures"][samefigidx]["metadata"].extend(metadtmp)
                    
                        #Explanation
                        explanations = Explanation.objects.filter(figure_id=figureid).values()
                        exptmp = []
                        if len(explanations) > 0:
                            for exp in explanations:
                                headlineid = exp["headline_id"]
                                headlinename = Headline.objects.filter(pk=headlineid).values()[0]["headline_name"]
                                explanation = {
                                    "product_id":productid,
                                    "product_name":productname,
                                    "explanationid":exp["id"],
                                    "value":exp["value"],
                                    "headlineid":headlineid,
                                    "headline_name":headlinename
                                }
                                exptmp.append(explanation)
                        summarizebase[clusterdict[fig["cluster"]]]["figures"][samefigidx]["explanation"].extend(exptmp)

            #Description
            descriptions = Description.objects.filter(entity_id=entityid).values()
            if len(descriptions) > 0:
                for desc in descriptions:
                    itemid = desc["item_id"]
                    itemname = Item.objects.filter(pk=itemid).values()[0]["item_name"]
                    description = {
                        "product_id":productid,
                        "product_name":productname,
                        "descriptionid":desc["id"],
                        "values":desc["values"],
                        "itemid":itemid,
                        "item_name":itemname
                    }
                    summarizebase[clusterdict[desc["cluster"]]]["descriptions"].append(description)
        
            #Sentence
            sentences = Sentence.objects.filter(entity_id=entityid).values()
            if len(sentences) > 0:
                for sent in sentences:
                    headlineid = sent["headline_id"]
                    headlinename = Headline.objects.filter(pk=headlineid).values()[0]["headline_name"]
                    sentence = {
                        "product_id":productid,
                        "product_name":productname,
                        "sentenceid":sent["id"],
                        "value":sent["value"],
                        "headlineid":headlineid,
                        "headline_name":headlinename
                    }
                    summarizebase[clusterdict[sent["cluster"]]]["sentences"].append(sentence)

            #Image
            images = Image.objects.filter(entity_id=entityid).values()
            if len(images) > 0:
                for img in images:
                    image = {
                        "product_id":productid,
                        "product_name":productname,
                        "imageid":img["id"],
                        "image_name":img["image_name"],
                        "image":img["image"],
                    }
                    summarizebase[clusterdict[img["cluster"]]]["images"].append(image)

        tmpjson.update(summarizebase)

        response = tmpjson

        return Response(response)