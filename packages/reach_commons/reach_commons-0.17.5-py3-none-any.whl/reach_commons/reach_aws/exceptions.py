class KMSClientException(Exception):
    pass


class KinesisClientException(Exception):
    pass


class SNSClientException(Exception):
    pass


class HubspotBusinessNotFoundException(Exception):
    def __init__(self, business_id, message="Business not found"):
        self.business_id = business_id
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}. Business ID: {self.business_id}"


class HubspotUserNotFoundException(Exception):
    def __init__(self, user_id, message="User not found"):
        self.user_id = user_id
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}. User ID: {self.user_id}"


class SQSClientTopicNotFound(SNSClientException):
    pass


class SQSClientPublishError(SNSClientException):
    pass
