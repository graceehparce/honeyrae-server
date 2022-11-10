from django.http import HttpResponseServerError
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from repairsapi.models import ServiceTicket, service_ticket
from repairsapi.models import employee
from repairsapi.models.employee import Employee
from repairsapi.models.customer import Customer


class ServiceTicketView(ViewSet):

    def destroy(self, request, pk=None):
        service_ticket = ServiceTicket.objects.get(pk=pk)
        service_ticket.delete()
        return Response(None, status=status.HTTP_204_NO_CONTENT)

    def create(self, request):
        new_ticket = ServiceTicket()
        new_ticket.customer = Customer.objects.get(user=request.auth.user)
        new_ticket.description = request.data['description']
        new_ticket.emergency = request.data['emergency']
        new_ticket.save()

        serialized = TicketSerializer(new_ticket, many=False)

        return Response(serialized.data, status=status.HTTP_201_CREATED)

    def list(self, request):

        service_tickets = []

        if "status" in request.query_params:
            if request.query_params['status'] == "done":
                service_tickets = ServiceTicket.objects.filter(
                    date_completed__isnull=False)

            if request.query_params['status'] == "all":
                service_tickets = ServiceTicket.objects.all()

        else:
            service_tickets = ServiceTicket.objects.all()

        serialized = TicketSerializer(service_tickets, many=True)
        return Response(serialized.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):

        ticket = ServiceTicket.objects.get(pk=pk)
        serialized = TicketSerializer(ticket, context={'request': request})
        return Response(serialized.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):

        ticket = ServiceTicket.objects.get(pk=pk)
        employee_id = request.data['employee']['id']
        assigned_employee = Employee.objects.get(pk=employee_id)
        ticket.employee = assigned_employee
        ticket.date_completed = request.data['date_completed']
        ticket.save()
        return Response(None, status=status.HTTP_204_NO_CONTENT)


class TicketCustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ('id', 'address', 'full_name')


class TicketEmployeeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employee
        fields = ('id', 'specialty', 'full_name')


class TicketSerializer(serializers.ModelSerializer):

    employee = TicketEmployeeSerializer(many=False)

    customer = TicketCustomerSerializer(many=False)

    class Meta:
        model = ServiceTicket
        fields = ('id', 'customer', 'employee', 'description',
                  'emergency', 'date_completed')
        depth = 1
