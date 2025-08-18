# alignment/chatbot_ai/views.py


from custos import Custos, set_api_key, AlignmentViolation
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .ai_engine import SimpleAIModel
from .models import ChatInteraction
import traceback

# Set API Key once 
set_api_key("c8834798457a2c71f322eacbb68e1cc3c0de71bc812b1469006fe9ad42f5cfd4")

class ChatBotAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            prompt = request.data.get("prompt")
            if not prompt:
                return Response({"error": "Prompt is required."}, status=status.HTTP_400_BAD_REQUEST)

            # Step 1: Generate AI response
            ai_model = SimpleAIModel()
            ai_response = ai_model.generate_response(prompt)

            # Step 2: Evaluate via custos guardian
            guardian = Custos.guardian()
            evaluation = guardian.evaluate(prompt=prompt, response=ai_response)

            # Step 3: Save interaction
            ChatInteraction.objects.create(user=request.user, prompt=prompt, response=ai_response)

            return Response({
                "prompt": prompt,
                "ai_response": ai_response,
                "evaluation": evaluation
            })

        except AlignmentViolation as e:
            return Response({
                "alignment_status": "violation",
                "message": str(e),
                "details": e.result
            }, status=400)

        except Exception as e:
            return Response({
                "error": "Unexpected error occurred.",
                "detail": str(e),
                "trace": traceback.format_exc()
            }, status=500)
