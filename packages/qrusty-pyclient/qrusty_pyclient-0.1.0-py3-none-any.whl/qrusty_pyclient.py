import requests


class QrustyClient:
    """
    Python client for the qrusty priority queue API.

    Example usage:
        client = QrustyClient(base_url="http://localhost:3000")
        client.publish(queue="orders", priority=100, payload={"order_id": 123})
        message = client.consume(queue="orders", consumer_id="worker-1")
        client.ack(queue="orders", message_id=message["id"], consumer_id="worker-1")
    """

    def __init__(self, base_url: str):
        """
        Initialize the client with the base URL of the qrusty API server.
        :param base_url: Base URL of the qrusty server (e.g., http://localhost:3000)
        """
        self.base_url = base_url.rstrip("/")

    def publish(
        self, queue: str, priority: int, payload: dict, max_retries: int = 3
    ) -> dict:
        """
        Publish a message to a queue.
        :param queue: Queue name
        :param priority: Message priority
        :param payload: Message payload (dict)
        :param max_retries: Maximum retry count
        :return: Response JSON from server
        """
        data = {
            "queue": queue,
            "priority": priority,
            "payload": payload,
            "max_retries": max_retries,
        }
        resp = requests.post(f"{self.base_url}/publish", json=data, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def consume(self, queue: str, consumer_id: str, timeout_seconds: int = 30) -> dict:
        """
        Consume a message from a queue.
        :param queue: Queue name
        :param consumer_id: Consumer identifier
        :param timeout_seconds: Lock timeout in seconds
        :return: Message JSON from server
        """
        data = {"consumer_id": consumer_id, "timeout_seconds": timeout_seconds}
        resp = requests.post(f"{self.base_url}/consume/{queue}", json=data, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def ack(self, queue: str, message_id: str, consumer_id: str) -> dict:
        """
        Acknowledge a message as processed.
        :param queue: Queue name
        :param message_id: Message ID
        :param consumer_id: Consumer identifier
        :return: Response JSON from server
        """
        data = {"message_id": message_id, "consumer_id": consumer_id}
        resp = requests.post(f"{self.base_url}/ack/{queue}", json=data, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def purge(self, queue: str) -> dict:
        """
        Purge all messages from a queue.
        :param queue: Queue name
        :return: Response JSON from server
        """
        resp = requests.post(f"{self.base_url}/purge-queue/{queue}", timeout=10)
        resp.raise_for_status()
        return resp.json()

    def stats(self) -> dict:
        """
        Get statistics for all queues.
        :return: Stats JSON from server
        """
        resp = requests.get(f"{self.base_url}/stats", timeout=10)
        resp.raise_for_status()
        return resp.json()

    def list_queues(self) -> dict:
        """
        List all active queue names.
        :return: List of queue names
        """
        resp = requests.get(f"{self.base_url}/queues", timeout=10)
        resp.raise_for_status()
        return resp.json()
