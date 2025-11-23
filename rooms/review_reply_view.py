
class ReviewReply(APIView):
    """Handle adding replies to reviews."""
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [NoCSRFSessionAuthentication, TokenAuthentication, JWTAuthentication]
    
    def get_review(self, room_pk, review_pk):
        try:
            from reviews.models import Review
            return Review.objects.get(pk=review_pk, room_id=room_pk)
        except Review.DoesNotExist:
            raise NotFound("Review not found")
    
    def put(self, request, pk, review_pk):
        """Add or update a reply to a review."""
        review = self.get_review(pk, review_pk)
        reply_text = request.data.get("reply")
        
        if not reply_text:
            raise ParseError("Reply text is required")
        
        # Update the review with reply information
        from django.utils import timezone
        review.reply = reply_text
        review.reply_user = request.user
        review.reply_created_at = timezone.now()
        review.save()
        
        # Return the updated review
        serializer = ReviewSerializer(review)
        return Response(serializer.data)
