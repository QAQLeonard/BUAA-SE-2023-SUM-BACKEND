from ProjectExecution.serializers import NodeSerializer


def build_tree(queryset):
    node_dict = {node.node_id: {"data": NodeSerializer(node).data, "children": []} for node in queryset}
    root_nodes = []

    for node in queryset:
        parent_id = node.parent_node.node_id if node.parent_node else None
        if parent_id:
            node_dict[parent_id]["children"].append(node_dict[node.node_id])
        else:
            root_nodes.append(node_dict[node.node_id])

    return root_nodes


def find_node_level(node):
    level = 1
    while node.parent_node is not None:
        level += 1
        node = node.parent_node
    return level
