from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from .models import Room
from .serializers import RoomSerializer, CreateRoomSerializer, UpdateRoomSerializer


class RoomView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class CreateRoomView(APIView):
    # creates new room
    # called from CreateRoomPage.js component
    serializer_class = CreateRoomSerializer

    def post(self, request):
        # if there wasn't any session on device, create new session with it's key
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        serializer = self.serializer_class(data=request.data)

        # if serializer's validation went successfully, get data from it
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')

            # each host is identified by it's session key
            host = self.request.session.session_key
            queryset = Room.objects.filter(host=host)

            # existing of queryset means that user already has created a room once
            # and to create new room, we need to change 'guest_can_pause' and 'votes_to_skip' fields
            if queryset.exists():
                room = queryset[0]
                room.guest_can_pause = guest_can_pause
                room.votes_to_skip = votes_to_skip
                room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
                self.request.session['room_code'] = room.code
                return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)

            # otherwise we need to create a room from zero, and put a session key as a host value
            else:
                room = Room(host=host, guest_can_pause=guest_can_pause, votes_to_skip=votes_to_skip)
                room.save()
                self.request.session['room_code'] = room.code
                return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)

        return Response({'Bad Request': 'Invalid data...'}, status=status.HTTP_400_BAD_REQUEST)


class GetRoom(APIView):
    # gets information about room by it's code
    # called from Room.js component
    lookup_url_kwarg = 'code'

    def get(self, request):
        # find if there is a code in request
        code = request.GET.get(self.lookup_url_kwarg)
        if code is not None:
            # select room with given code
            room = Room.objects.filter(code=code)
            if room.exists():
                # get data dictionary of room
                data = RoomSerializer(room[0]).data
                # add new boolean field "is_host"
                data['is_host'] = self.request.session.session_key == room[0].host
                return Response(data, status=status.HTTP_200_OK)
            return Response({'Room Not Found': 'Invalid Room Code'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'Bad Request': 'Code parameter not found in request'}, status=status.HTTP_400_BAD_REQUEST)


class JoinRoom(APIView):
    # joins the room by given code
    # called from JoinRoomPage.js component
    lookup_url_kwarg = "code"

    def post(self, request):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        # find if there is a code in request
        code = request.data.get(self.lookup_url_kwarg)
        if code is not None:
            # select rooms with given code
            room_result = Room.objects.filter(code=code)
            if room_result.exists() > 0:
                # add 'room_code' value to session data
                self.request.session['room_code'] = code
                return Response({'message': 'Room Joined!'}, status=status.HTTP_200_OK)
            return Response({'Bad request': 'Invalid Room Code'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'Bad request': 'Invalid post data, code key not found'}, status=status.HTTP_400_BAD_REQUEST)


class UserInRoom(APIView):
    # checks if user is in room
    # called from HomePage.js component
    def get(self, request):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        # if user is not in the room, 'code' will be equal to None
        data = {
            'code': self.request.session.get('room_code'),
        }
        return JsonResponse(data, status=status.HTTP_200_OK)


class LeaveRoom(APIView):
    # leaves the room
    # called from Room.js component
    def post(self, request):
        if 'room_code' in self.request.session:
            # remove 'room_code' value from session data
            self.request.session.pop('room_code')
            # if host leaves the room, delete room from database
            host_id = self.request.session.session_key
            room_result = Room.objects.filter(host=host_id)
            if len(room_result) > 0:
                room = room_result[0]
                room.delete()
        return Response({'Message': 'Success'}, status=status.HTTP_200_OK)


class UpdateRoom(APIView):
    # updates room data
    # called from CreateRoomPage.js component
    serializer_class = UpdateRoomSerializer

    def patch(self, request):
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        # initialize serializer
        serializer = self.serializer_class(data=self.request.data)
        if serializer.is_valid():
            # getting data from serializer
            votes_to_skip = serializer.data.get('votes_to_skip')
            guest_can_pause = serializer.data.get('guest_can_pause')
            code = serializer.data.get('code')
            # checking if room exists
            queryset = Room.objects.filter(code=code)
            if not queryset.exists():
                return Response({'Message': 'Room not found'}, status=status.HTTP_404_NOT_FOUND)
            room = queryset[0]
            # only host can modify the room
            user_id = self.request.session.session_key
            if room.host != user_id:
                return Response({'Message': 'You are not a host'}, status=status.HTTP_403_FORBIDDEN)
            # changing and saving data
            room.guest_can_pause = guest_can_pause
            room.votes_to_skip = votes_to_skip
            room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
            return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
        return Response({'Bad Request': 'Invalid data...'}, status=status.HTTP_400_BAD_REQUEST)
