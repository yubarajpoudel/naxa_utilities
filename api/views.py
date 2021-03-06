import os

import random
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Max
from rest_framework.decorators import api_view
from uuid import uuid4

from api.permission import IsFrontendUser
from .serializers import MedicalFacilitySerializer, \
    MedicalFacilityCategorySerializer, MedicalFacilityTypeSerializer, \
    CaseSerializer, ProvinceSerializer, ProvinceDataSerializer, \
    DistrictSerializer, MunicipalitySerializer, UserRoleSerializer, \
    UserLocationSerializer, UserReportSerializer, AgeGroupDataSerializer, \
    SpaceSerializer, DistrictDataSerializer, MuncDataSerializer, \
    GlobalDataSerializer, MobileVersionSerializer, UserSerializer, \
    DeviceSerializer, SuspectSerializer, SmallUserReportSerializer, \
    NearUserSerializer, ApplicationDataSerializer, FAQSerializer, NewsSerializer
from .models import MedicalFacility, MedicalFacilityType, \
    MedicalFacilityCategory, CovidCases, Province, ProvinceData, Municipality, \
    District, UserLocation, UserReport, AgeGroupData, DistrictData, MuniData, \
    GlobalData, MobileVersion, Device, SuspectReport, CeleryTaskProgress, \
    ApplicationStat, FAQ, News
from .tasks import generate_user_report, generate_facility_report

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, pagination, views, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

import io
import json
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import GEOSGeometry, Point
from django.contrib.gis.measure import D
from django.core.serializers import serialize
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class BigResultsSetPagination(pagination.PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 1000


NationalHotine = settings.HOTLINE


# Create your views here.
class StatsAPI(viewsets.ModelViewSet):
    queryset = ProvinceData.objects.filter(active=True)
    serializer_class = ProvinceDataSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'province_id']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create' or self.action == 'destroy' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsFrontendUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def list(self, request):
        queryset = ProvinceData.objects.filter(active=True).annotate(
                facility_count=Count("province_id__medical_facility"))
        province = self.request.query_params.get('province')
        district = self.request.query_params.get('district')
        municipality = self.request.query_params.get('municipality')
        if province == "all":
            data = ProvinceDataSerializer(queryset, many=True).data
            return Response(data)

        elif province:
            queryset = queryset.filter(province_id=province).annotate(
                facility_count=Count("province_id__medical_facility"))
            data = ProvinceDataSerializer(queryset, many=True).data
            return Response(data)

        elif district == "all":
            queryset = DistrictData.objects.filter(active=True).annotate(
                facility_count=Count("district_id__medical_facility"))
            data = DistrictDataSerializer(queryset, many=True).data
            return Response(data)

        elif district:
            queryset = DistrictData.objects.filter(
                active=True, district_id=district).annotate(
                facility_count=Count("district_id__medical_facility"))
            data = DistrictDataSerializer(queryset, many=True).data
            return Response(data)
        elif municipality == "all":
            queryset = MuniData.objects.filter(active=True).annotate(
                facility_count=Count("municipality_id__medical_facility"))
            data = MuncDataSerializer(queryset, many=True).data
            return Response(data)

        elif municipality:
            queryset = MuniData.objects.filter(
                active=True, municipality_id=municipality).annotate(
                facility_count=Count("municipality_id__medical_facility"))
            data = MuncDataSerializer(queryset, many=True).data
            return Response(data)
        facility_count = MedicalFacility.objects.all().count()
        # tested = MedicalFacility.objects.aggregate(
        #     tested=Sum('total_tested'))
        data = queryset.aggregate(
            tested=Sum('total_tested'),
            total_samples_collected=Sum('total_samples_collected'),
            total_samples_pending=Sum('total_samples_pending'),
            total_negative=Sum('total_negative'),
            update_date=Max('update_date'),
            confirmed=Sum('total_positive'),
            isolation=Sum('total_in_isolation'),
            total_recovered=Sum('total_recovered'),
            death=Sum('total_death'),
            icu=Sum('num_of_icu_bed'),
            occupied_icu=Sum('occupied_icu_bed'),
            ventilator=Sum('num_of_ventilators'),
            occupied_ventilator=Sum('occupied_ventilators'),
            isolation_bed=Sum('num_of_isolation_bed'),
            occupied_isolation_bed=Sum('occupied_ventilators'),
        )
        # data.update(tested)
        data.update({'facility_count': facility_count})
        data.update({"hotline": NationalHotine})
        return Response(data)


class MedicalApi(viewsets.ModelViewSet):
    queryset = MedicalFacility.objects.all()
    serializer_class = MedicalFacilitySerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'type', 'municipality', 'district', 'province',
                        'category']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create' or self.action == 'destroy' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        return self.queryset.select_related('type', 'municipality',
                                            'district', 'province', 'category')


class MedicalApi2(viewsets.ModelViewSet):
    queryset = MedicalFacility.objects.all()
    serializer_class = MedicalFacilitySerializer
    pagination_class = StandardResultsSetPagination

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'type', 'municipality', 'province', 'district']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create' or self.action == 'destroy' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        action_type = self.request.query_params.get('action_type')
        if action_type == "generate":
            authenticated = bool(request.user and request.user.is_authenticated)
            if not authenticated:
                return Response({{'message': 'Permission denied'}},
                                status=status.HTTP_403_FORBIDDEN)
            frontend_group = request.user.roles.filter(
                group__name="FrontEnd").exists()
            if not frontend_group:
                return Response({{'message': 'Permission denied'}},
                         status=status.HTTP_403_FORBIDDEN)
            task_obj = CeleryTaskProgress.objects.create(
                user=self.request.user,
                content_object=self.request.user,
                task_type=1)
            if task_obj:
                task = generate_facility_report.apply_async(
                    (task_obj.id,), queue="default")

                task_obj.task_id = task.id
                task_obj.save()
                return Response({'message': 'File being updated'})
        return super(MedicalApi2, self).list(request, *args, **kwargs)

    
class MedicalCategoryApi(viewsets.ModelViewSet):
    queryset = MedicalFacilityCategory.objects.order_by('id')
    serializer_class = MedicalFacilityCategorySerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create' or self.action == 'destroy' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class MedicalTypeApi(viewsets.ModelViewSet):
    queryset = MedicalFacilityType.objects.order_by('id')
    serializer_class = MedicalFacilityTypeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'category']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create' or self.action == 'destroy' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class CaseApi(viewsets.ModelViewSet):
    queryset = CovidCases.objects.order_by('id')
    serializer_class = CaseSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create' or self.action == 'destroy' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class ProvinceApi(viewsets.ModelViewSet):
    queryset = Province.objects.order_by('id')
    serializer_class = ProvinceSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create' or self.action == 'destroy' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class MunicipalityApi(viewsets.ModelViewSet):
    queryset = Municipality.objects.order_by('id')
    serializer_class = MunicipalitySerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create' or self.action == 'destroy' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class DistrictApi(viewsets.ModelViewSet):
    queryset = District.objects.order_by('id')
    serializer_class = DistrictSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create' or self.action == 'destroy' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class ProvinceDataApi(viewsets.ModelViewSet):
    queryset = ProvinceData.objects.order_by('id')
    serializer_class = ProvinceDataSerializer
    permission_classes = [IsFrontendUser]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['province_id']

    def get_queryset(self):
        queryset = ProvinceData.objects.order_by('id')
        province_id = self.request.query_params.get("province_id")
        if province_id is not None:
            queryset = queryset.filter(province_id=province_id)
        return queryset


class DistrictDataApi(viewsets.ModelViewSet):
    queryset = DistrictData.objects.order_by('id')
    serializer_class = DistrictDataSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['province_id', 'district_id']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create' or self.action == 'destroy' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class MuncDataApi(viewsets.ModelViewSet):
    queryset = MuniData.objects.order_by('id')
    serializer_class = MuncDataSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['province_id', 'district_id', 'municipality_id']

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create' or self.action == 'destroy' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        roles = user.roles.all().select_related("group", "province", "facility")
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'roles': UserRoleSerializer(roles, many=True).data
        })

@api_view(['POST'])
def create_auth(request):
    serialized = UserSerializer(data=request.DATA)
    if serialized.is_valid():
        User.objects.create_user(
            serialized.init_data['username'],
            serialized.init_data['password']
        )
        return Response(serialized.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)


class UserLocationApi(viewsets.ModelViewSet):
    queryset = UserLocation.objects.all()
    serializer_class = UserLocationSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'destroy' or self.action == \
                'update' or self.action == 'partial_update' or self.action ==\
                'retrieve':
            permission_classes = [IsFrontendUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class UserReportApi(viewsets.ModelViewSet):
    queryset = UserReport.objects.all()
    serializer_class = UserReportSerializer
    small_serializer_class = SmallUserReportSerializer
    pagination_class = BigResultsSetPagination

    def get_serializer_class(self):
        data_type = self.request.query_params.get('data_type', "all")
        if data_type == "all":
            return super(UserReportApi, self).get_serializer_class()
        return self.small_serializer_class

    def list(self, request, *args, **kwargs):
        action_type = self.request.query_params.get('action_type')
        if action_type == "generate":
            authenticated = bool(request.user and request.user.is_authenticated)
            if not authenticated:
                return Response({{'message': 'Permission denied'}},
                                status=status.HTTP_403_FORBIDDEN)
            frontend_group = request.user.roles.filter(
                group__name="FrontEnd").exists()
            if not frontend_group:
                return Response({{'message': 'Permission denied'}},
                                status=status.HTTP_403_FORBIDDEN)
            task_obj = CeleryTaskProgress.objects.create(
                user=self.request.user,
                content_object=self.request.user,
                task_type=0)
            if task_obj:
                task = generate_user_report.apply_async((task_obj.pk,),
                                                        queue="default")

                task_obj.task_id = task.id
                task_obj.save()
                return Response({'message': 'File being updated'})

        data_type = self.request.query_params.get('data_type', "all")
        if data_type == "all":
            return super(UserReportApi, self).list(request, *args, **kwargs)
        queryset = self.filter_queryset(self.get_queryset().filter(
            result=data_type))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['destroy', 'update', 'partial_update', 'list',
                           'get', 'retrieve']:
            permission_classes = [IsFrontendUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        if self.request.user and not self.request.user.is_anonymous:
            serializer.save(user=self.request.user)
        else:
            serializer.save()

    def create(self, request, *args, **kwargs):
        if not request.data.get('lat'):
            request.data['lat'] = random.choice([27.61824026, 27.62824026,
                                                 27.63824026, 27.64824026])
            request.data['long'] = random.choice([85.46619027, 85.36619027,
                                                  85.26619027, 85.16619027,
                                                  85.56619027])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        temperature = serializer.data['temperature']
        travel_history = serializer.data['travel_history']
        try:
            data = json.loads(travel_history)
            if not isinstance(data, dict):
                print(data)
                raise ValueError(" failed to parse json")
        except Exception as e:
            print(e)
            data = {}
        has_travel_history = data.get('has_travel_history', False)
        has_convid_contact = data.get('has_convid_contact', False)
        has_covid_contact = data.get('has_covid_contact', False)
        if not has_covid_contact and has_convid_contact:
            has_covid_contact = has_convid_contact
        message = "प्रारम्भिक परिक्षणमा तपाईले बुझाउनु भएका शारीरिक लक्षण वा " \
                  "यात्रा विवरणका आधारमा तपाइँलाई कोभीड-१९ को संक्रमण हुने" \
                  " सम्भावन कम देखिन्छ। यद्यपि परिक्षणबिना संक्रमण भए नभएको " \
                  "थाहा नहुने हुनाले सकेसम्म हुलमुलमा नगई बाह्य सम्पर्क कम गरि " \
                  "संक्रमण फैलिन नदिन सहयोग गर्नुहोस्। तपाइलाई संका भएमा थप " \
                  "परिक्षण गर्नको निम्ति निम्न सम्पर्क नम्बर वा नजिकको कोभिड-१९ " \
                  "सम्बन्धि सेवाका लागी नेपाल सरकारद्वारा तोकिएको स्वास्थ्य संस्थामा सम्पर्क गर्नुहोस्।"
        result = "lesslikely"
        if temperature >= 102 and (has_travel_history or has_covid_contact):
            message = "प्रारम्भिक परिक्षणमा तपाईले बुझाउनु भएका लक्षण वा यात्रा विवरणका " \
                      "आधारमा तपाईँलाई कोभीड-१९ को संक्रमण भएको हुनसक्ने देखिन्छ। " \
                      "कृपया कोभिड-१९ को थप परिक्षण गर्नको निम्ति निम्न सम्पर्क नम्बर वा" \
                      " नजिकको कोभिड-१९ सम्बन्धि सेवाका लागी नेपाल सरकारद्वारा तोकिएको " \
                      "स्वास्थ्य संस्थामा सम्पर्क गर्नुहोस्। त्यतिन्जेल सेल्फ क्वारेन्टाइनमा बस्नुहोस् र" \
                      " अन्य व्यक्तिहरुसँग सम्पर्क नगरि कोरोना संक्रमण फैलन नदिन सहयोग गर्नुहोस्।"
            result = "morelikely"
        elif temperature >= 98 and (has_travel_history or has_covid_contact):
            message = "प्रारम्भिक परिक्षणमा तपाईले बुझाउनु भएका लक्षण वा यात्रा विवरणका " \
                      "आधारमा तपाईँलाई कोभीड-१९ को संक्रमण भएको हुनसक्ने देखिन्छ। " \
                      "कृपया कोभिड-१९ को थप परिक्षण गर्नको निम्ति निम्न सम्पर्क नम्बर वा" \
                      " नजिकको कोभिड-१९ सम्बन्धि सेवाका लागी नेपाल सरकारद्वारा तोकिएको " \
                      "स्वास्थ्य संस्थामा सम्पर्क गर्नुहोस्। त्यतिन्जेल सेल्फ क्वारेन्टाइनमा बस्नुहोस् र" \
                      " अन्य व्यक्तिहरुसँग सम्पर्क नगरि कोरोना संक्रमण फैलन नदिन सहयोग गर्नुहोस्।"
            result = "likely"

        headers = self.get_success_headers(serializer.data)
        return Response({"message": message, "result":result},
                        status=status.HTTP_201_CREATED,
                        headers=headers)


class AgeGroupDataApi(viewsets.ModelViewSet):
    queryset = AgeGroupData.objects.all()
    serializer_class = AgeGroupDataSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create' or self.action == 'destroy' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class DeviceApi(viewsets.ModelViewSet):
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # headers = self.get_success_headers(serializer.data)
        return Response({}, status=status.HTTP_201_CREATED)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        # if self.action == 'create' or self.action == 'destroy' or self.action == 'update' or self.action == 'partial_update':
        #     permission_classes = [IsAuthenticated]
        # else:
        permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class SuspectApi(viewsets.ModelViewSet):
    queryset = SuspectReport.objects.all()
    serializer_class = SuspectSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['destroy', 'update', 'partial_update', 'list',
                           'get', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class GlobalDataApi(viewsets.ModelViewSet):
    queryset = GlobalData.objects.all()
    serializer_class = GlobalDataSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create' or self.action == 'destroy' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsFrontendUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class ApplicationDataApi(viewsets.ModelViewSet):
    queryset = ApplicationStat.objects.all()
    serializer_class = ApplicationDataSerializer
    permission_classes = [IsFrontendUser]

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create' or self.action == 'destroy' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsFrontendUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class FAQApi(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    permission_classes = [IsFrontendUser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create' or self.action == 'destroy' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsFrontendUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class NewsApi(viewsets.ModelViewSet):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [IsFrontendUser]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create' or self.action == 'destroy' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsFrontendUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class VersionDataApi(viewsets.ModelViewSet):
    queryset = MobileVersion.objects.all()
    serializer_class = MobileVersionSerializer

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create' or self.action == 'destroy' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsFrontendUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]


class NearFacilityViewSet(views.APIView):
    permission_classes = [IsFrontendUser]

    def get(self, request):
        params = request.query_params
        longitude = params['long']
        latitude = params['lat']

        user_location = GEOSGeometry('POINT({} {})'.format(longitude, latitude), srid=4326)

        resource_queryset = MedicalFacility.objects.filter(
            location__distance_lte=(user_location, D(km=500))).annotate(
            distance=Distance(
                'location', user_location)).order_by('distance')[:10]
        resource_json = SpaceSerializer(resource_queryset, many=True)
        json_data = JSONRenderer().render(resource_json.data)
        stream = io.BytesIO(json_data)
        data = JSONParser().parse(stream)
        return Response(data)


class SpaceGeojsonViewSet(views.APIView):
    permission_classes = [IsFrontendUser]

    def get(self, request):
        serializers = serialize(
            'geojson', MedicalFacility.objects.all(),
            geometry_field='location', fields=('pk', 'name', 'location',
                                               'province', 'district', 
                                               'municipality', 'category', 
                                               'type', 'ownership', 
                                               'contact_person', 
                                               'contact_num', 
                                               'used_for_corona_response', 
                                               'num_of_bed', 
                                               'num_of_icu_bed', 
                                               'occupied_isolation_bed', 
                                               'occupied_ventilators', 
                                               'occupied_icu_bed',
                                               'num_of_isolation_bed',
                                               'num_of_ventilators',
                                               'total_in_isolation', 
                                               'total_death', 
                                               'total_positive','total_tested'))
        geojson = json.loads(serializers)
        return Response(geojson)


class NearUserReportViewSet(views.APIView):
    permission_classes = [IsFrontendUser]

    def get(self, request):
        params = request.query_params
        longitude = params['long']
        latitude = params['lat']
        result = params['result']
        km = params['km']

        user_location = GEOSGeometry(
            'POINT({} {})'.format(longitude, latitude), srid=4326)
        resource_queryset = UserReport.objects.filter(result=result).filter(
            location__distance_lte=(user_location, D(km=km))).annotate(
            distance=Distance(
                'location', user_location)).order_by('distance')[:25]
        resource_json = NearUserSerializer(resource_queryset, many=True)
        json_data = JSONRenderer().render(resource_json.data)
        stream = io.BytesIO(json_data)
        data = JSONParser().parse(stream)
        return Response(data)


class NearUserGeojsonViewSet(views.APIView):
    permission_classes = [IsFrontendUser]

    def get(self, request):
        serializers = serialize(
            'geojson', UserReport.objects.filter(result="morelikely"),
            geometry_field='location', fields=('pk', 'name', 'location'))
        geojson = json.loads(serializers)
        return Response(geojson)
