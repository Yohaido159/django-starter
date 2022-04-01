import re
from django.core.management import BaseCommand
from pprint import pprint


def join_new_line(list_string):
    return "\n".join(list_string)


def flatten_list(list):
    return [item for sublist in list for item in sublist]


def snack_case(string):
    return '_'.join(
        re.sub('([A-Z][a-z]+)', r' \1',
               re.sub('([A-Z]+)', r' \1',
                      string.replace('-', ' '))).split()).lower()


def open_file(type, name_app, model_name, fields):

    if type == "models":
        check_string = f"class {model_name}(models.Model)"
        list_string = [
            [f"class {model_name}(models.Model):"],
            [f"\t{field} = models.CharField(max_length=225, blank=True, null=True)" for field in fields],
            [f"\tdef __str__(self):"],
            [f"\t\treturn self.name"],
            [f"\tdef __repr__(self):"],
            [f"\t\treturn f\"<{model_name} name={{self.name}}/>\""],
        ]

        string = join_new_line(flatten_list(list_string))
        file_path = f"{name_app}/models.py"

    elif type == "serializers_write":
        check_string = f"class {model_name}Serializer(serializers.ModelSerializer)"

        list_string = [
            [f"class {model_name}Serializer(serializers.ModelSerializer):"],
            ["\tclass Meta:"],
            [f"\t\tmodel = {model_name}"],
            ["\t\tfields = '__all__'\n"],
        ]
        string = join_new_line(flatten_list(list_string))
        file_path = f"{name_app}/serializers/write_serializers.py"

    elif type == "serializers_read":
        check_string = f"class {model_name}ReadSerializer(serpy.Serializer)"
        list_string = [
            [f"class {model_name}ReadSerializer(serpy.Serializer):"],
            ["\tid= serpy.Field()"],
            [f"\t{field} = serpy.Field()" for field in fields],

        ]
        string = join_new_line(flatten_list(list_string))
        file_path = f"{name_app}/serializers/read_serializers.py"

    elif type == "views":
        check_string = f"class {model_name}ViewSet(viewsets.ModelViewSet)"
        list_string = [
            [f"class {model_name}Viewset(AutoPrefetchViewSetMixin , viewsets.ModelViewSet):"],
            [f"\tqueryset = {model_name}.objects.all()"],
            [f"\tserializer_class = {model_name}Serializer"],
            [f"\tfilter_backends = (RQLFilterBackend,)"],
            [f"\trql_filter_class = {model_name}FilterClass\n"],
            [f"\tdef list(self, request, *args, **kwargs):"],
            [f"\t\tqueryset = self.filter_queryset(self.get_queryset())"],
            [f"\t\tserializer = {model_name}ReadSerializer(queryset, many=True)"],
            [f"\t\treturn Response(data=serializer.data)\n"],
            [f"\tdef retrieve(self, request, *args, **kwargs):"],
            [f"\t\tqueryset = self.filter_queryset(self.get_queryset())"],
            [f"\t\tserializer = {model_name}ReadSerializer(queryset, many=True)"],
            [f"\t\treturn Response(data=serializer.data)\n"],
            [f"\tdef get_queryset(self):"],
            [f"\t\tqs = super().get_queryset()"],
            [f"\t\treturn qs"],

        ]
        string = join_new_line(flatten_list(list_string))
        file_path = f"{name_app}/views/write_views.py"

    elif type == "urls":
        check_string = f"router.register('{snack_case(model_name)}', {model_name}Viewset, basename='{snack_case(model_name)}')"
        list_string = [
            [f"router.register('{snack_case(model_name)}', {model_name}Viewset, basename='{snack_case(model_name)}')"],
        ]
        string = join_new_line(flatten_list(list_string))
        file_path = f"{name_app}/urls.py"

    elif type == "filters":
        check_string = f"class {model_name}FilterClass(RQLFilterClass)"
        list_string = [
            [f"class {model_name}FilterClass(RQLFilterClass):"],
            [f"\tMODEL = {model_name}"],
            [f"\tFILTERS = {fields}"],

        ]
        string = join_new_line(flatten_list(list_string))
        file_path = f"{name_app}/filters.py"

    elif type == "admin":
        check_string = f"class {model_name}Admin(admin.ModelAdmin)"
        list_string = [
            [f"class {model_name}Admin(admin.ModelAdmin):"],
            [f"\tpass"],
            [f"admin.site.register({model_name}, {model_name}Admin)"],
        ]
        string = join_new_line(flatten_list(list_string))

    with open(file_path, "r+") as open_file:
        file = open_file.read()
        if check_string in file:
            return False
        else:
            return open_file.write(f"\n\n{string}")


def create_mode(name_app, model_name, fields=[]):
    modules = ["models", "serializers_write",
               "serializers_read", "views", "urls", "filters"]
    for module in modules:
        open_file(module, name_app, model_name, fields)


class Command(BaseCommand):

    def handle(self, **options):
        argv = options.get('argv')
        app_name = argv[0]
        model_name = argv[1]
        fields = argv[2:]

        print(f'Creating model {options}')
        create_mode(app_name, model_name, fields)

    def add_arguments(self, parser):
        parser.add_argument(
            "argv",
            nargs="+",
            type=str,
        )
