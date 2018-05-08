from rest_framework import serializers


class QuestionSerializer(serializers.Serializer):
    """
    Default Question serializer with all available fields
    """
    id = serializers.IntegerField()
    question_title = serializers.CharField(required=True, allow_blank=False,
                                           max_length=100)
    author = serializers.CharField(required=True, allow_blank=False,
                                   max_length=100)
    pub_date = serializers.DateTimeField(format="%x %X")
    question_tags = serializers.ManyRelatedField(child_relation=serializers.CharField())

    question_text = serializers.CharField(required=True, allow_blank=False,
                                          max_length=2000)

    number_of_answers = serializers.SerializerMethodField()
    rating = serializers.IntegerField()

    def create(self, validated_data):
        """
        No change with api available
        """
        pass

    def update(self, instance, validated_data):
        """
        No change with api available
        """
        pass

    def get_number_of_answers(self, obj):
        """
        :return: number of answers for number_of_answer field
        """
        return obj.answer_set.count()


class QuestionTrendingSerializer(QuestionSerializer):
    """
    Question serializer which returns only id, question_title and rating
    """
    question_text = None
    question_tags = None
    author = None
    number_of_answers = None
    pub_date = None


class QuestionBatchSerializer(QuestionSerializer):
    """
    Question serializer which returns all fields but question_text
    """
    question_text = None


class AnswerSerializer(serializers.Serializer):
    """
    Default Answer serializer with all available fields
    """

    author = serializers.CharField(required=True, allow_blank=False,
                                   max_length=100)
    right = serializers.BooleanField()
    rating = serializers.IntegerField()

    answer_text = serializers.CharField(required=True, allow_blank=False,
                                        max_length=2000)

    def create(self, validated_data):
        """
        No change with api available
        """
        pass

    def update(self, instance, validated_data):
        """
        No change with api available
        """
        pass
