from django.db import models


class NodeType(models.Model):
    key = models.CharField(max_length=8, primary_key=True)
    
    def __str__(self) -> str:
        return f"{self.key}"


class NodeManager(models.Manager):
    def find_or_make(self, id):
        if id is None:
            return None
        id_type, id_value = Node.parse_combined_id(id)
        node_type, _created = NodeType.objects.get_or_create(key=id_type)   #TODO meaningful error message if too long
        node, _created = Node.objects.get_or_create(id=id_value, type=node_type)
        return node


class Node(models.Model):
    id = models.CharField(max_length=24, primary_key=True)
    type = models.ForeignKey(NodeType, on_delete=models.CASCADE)
    objects = NodeManager()

    class Meta:
        verbose_name_plural = "Graph Nodes"

    def __str__(self):
        return f"{self.type}@{self.id}"
    
    @staticmethod
    def parse_combined_id(id):
        *excluded, id_type, id_value = id.split("@")
        return id_type, id_value


def removed_node():
    removed_type = NodeType.objects.get_or_create(key="REMOVED")[0]
    return Node.objects.get_or_create(id="--removed--", type=removed_type)[0]


class EdgeType(models.Model):
    key = models.CharField(max_length=20, primary_key=True)


def default_edge_type():
    return EdgeType.objects.get_or_create(key="none")[0]


class Edge(models.Model):
    edge_id = models.BigAutoField(primary_key=True)
    edge_type = models.ForeignKey(
        EdgeType, on_delete=models.SET_DEFAULT, blank=True, default=default_edge_type
    )
    child = models.ForeignKey(Node, on_delete=models.CASCADE, related_name="links_to_parents")
    parent = models.ForeignKey(
        Node, on_delete=models.CASCADE, related_name="links_to_children"
    )
    start = models.DateTimeField()
    end = models.DateTimeField(blank=True, null=True)
    quantity = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.child} --o {self.parent}"

    class Meta:
        verbose_name_plural = "Graph Edges"
        indexes = [
            models.Index(fields=["parent", "child", "end"], name="parent_idx"),
            models.Index(fields=["-start", "-end"], name="timestamp_idx"),
        ]


class Event(models.Model):
    event_id = models.BigAutoField(primary_key=True)
    child = models.ForeignKey(Node, on_delete=models.SET(removed_node), related_name="events_as_child")
    from_parent = models.ForeignKey(
        Node, on_delete=models.SET(removed_node), max_length=32, blank=True, null=True, related_name="departure_events"
    )
    to_parent = models.ForeignKey(
        Node, on_delete=models.SET(removed_node), max_length=32, related_name="arrival_events"
    )
    quantity = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField()

    def __str__(self):
        return f"{self.child}: {self.from_parent} --> {self.to_parent}"

    class Meta:
        verbose_name_plural = "Event Records"
