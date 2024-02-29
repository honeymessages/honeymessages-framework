import json
from json import JSONDecodeError

from rest_framework.renderers import BrowsableAPIRenderer, TemplateHTMLRenderer


def get_nested_json_content(renderer, data, accepted_media_type, renderer_context):
    """
    Get the content as if it had been rendered by the default
    non-documenting renderer.
    """
    if not renderer:
        return "[No renderers were found]"

    renderer_context["indent"] = 4
    # content = renderer.render(data, accepted_media_type, renderer_context)

    data_dict: dict = dict(data.items())
    for k in data_dict.keys():
        try:
            data_dict[k] = json.loads(data_dict[k], strict=False)
        except (JSONDecodeError, TypeError):
            pass

    content = json.dumps(data_dict, indent=4, sort_keys=True).encode(encoding="utf-8")

    render_style = getattr(renderer, "render_style", "text")
    assert render_style in ["text", "binary"], (
        'Expected .render_style "text" or "binary", but got "%s"' % render_style
    )
    if render_style == "binary":
        return "[%d bytes of binary content]" % len(content)

    return content


class SmartBrowsableAPIRenderer(BrowsableAPIRenderer):
    @property
    def template(self):
        view = self.renderer_context.get("view", {})
        table = "table" in view.request.query_params
        if view and hasattr(view, "detail") and view.detail and table:
            return "apps/tabular_api.html"
        else:
            return "rest_framework/api.html"

    def get_default_renderer(self, view):
        table = "table" in view.request.query_params
        if hasattr(view, "detail") and view.detail and table:
            return AccessLogHtmlRenderer()

        return super().get_default_renderer(view)

    def get_content(self, renderer, data, accepted_media_type, renderer_context):
        """
        Extends BrowsableAPIRenderer.get_content.
        """
        view = self.renderer_context.get("view", {})
        table = "table" in view.request.query_params
        if view and hasattr(view, "detail") and not table:
            # when in detail view and table is not requested, use the nested JSON renderer
            return get_nested_json_content(
                renderer, data, accepted_media_type, renderer_context
            )
        else:
            # use default
            return super().get_content(
                renderer, data, accepted_media_type, renderer_context
            )


class AccessLogHtmlRenderer(TemplateHTMLRenderer):
    media_type = "text/html"
    format = "api"
    template_name = "apps/table_content.html"

    def get_template_context(self, data, renderer_context):
        for key in data.keys():
            try:
                data[key] = json.dumps(json.loads(data[key]), indent=4)
            except (JSONDecodeError, TypeError):
                pass

        context = {"data": data}

        response = renderer_context["response"]
        if response.exception:
            context["status_code"] = response.status_code

        return context
