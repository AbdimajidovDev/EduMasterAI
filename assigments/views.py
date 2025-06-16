# from rest_framework import viewsets, status
# from rest_framework.response import Response
# from rest_framework.views import APIView
#
# from assigments.models import Assignment, AssignmentFile
# from assigments.serializers import AssignmentSerializer, AssignmentFileSerializer
#
#
# class AssignmentViewSet(viewsets.ModelViewSet):
#     queryset = Assignment.objects.all()
#     serializer_class = AssignmentSerializer
#
#
# class AssignmentFileAPIView(APIView):
#     def post(self, request):
#         serializer = AssignmentFileSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def get(self, request):
#         assignment = AssignmentFile.objects.all()
#         serializer = AssignmentFileSerializer(assignment, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
