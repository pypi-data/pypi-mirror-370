from django.views.generic import TemplateView
import json
import seaborn
from matplotlib.colors import to_hex

DEFAULT_COSMOGRAPH_PARAMS = {
    "renderLinks": True,
    "backgroundColor": "transparent",
    "linkArrows": False,
    "scaleNodesOnZoom": False,
    "simulationGravity": 1.0,
    "simulationRepulsion": 0.1,
    "simulationRepulsionTheta": 1.7,
    "simulationLinkSpring": 1.0,
    "simulationLinkDistance": 2,
    "simulationFriction": 0.85,
    "simulationCenter": 1.0,
    "simulationDecay": 1000,
    "simulationRepulsionFromMouse": 2.0,
}


class CosmographView(TemplateView):
    template_name = "django_cosmograph/cosmograph.html"

    def get_nodes_links(self):
        # Expect JSON strings in GET params
        nodes_json = self.request.GET.get("nodes", "[]")
        links_json = self.request.GET.get("links", "[]")
        try:
            nodes = json.loads(nodes_json)
            links = json.loads(links_json)
        except json.JSONDecodeError:
            nodes, links = [], []

        return nodes, links

    def get_params(self, *args, **kwargs):
        """
        override this method to return a dictionary of parameters
        for cosmograph simulation.
        Reference: https://cosmograph.app/docs/cosmograph/Cosmograph%20JavaScript/Cosmograph/#simulation-settings
        """
        return DEFAULT_COSMOGRAPH_PARAMS

    def get_legend(self, nodes, *args, **kwargs):
        """
        creates a qualitative colour map for the graph
        based on "group" attribute of nodes.
        Override this method to customize the legend.
        """
        if nodes:
            groups = set(node.get("group", "default") for node in nodes)
            colours = seaborn.color_palette("deep", n_colors=len(groups))
            legend = [
                {"group": group, "colour": to_hex(colour), "selected": True}
                for group, colour in zip(groups, colours)
            ]
            legend.sort(key=lambda x: x["group"])
            return legend
        return []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nodes, links = self.get_nodes_links()
        context["nodes_json"] = json.dumps(nodes)
        context["links_json"] = json.dumps(links)
        context["params_json"] = json.dumps(self.get_params())
        context["legend_json"] = json.dumps(self.get_legend(nodes))
        return context
