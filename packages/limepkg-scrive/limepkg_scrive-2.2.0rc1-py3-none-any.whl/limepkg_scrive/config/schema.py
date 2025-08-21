from marshmallow import Schema, fields, validate


def create_schema(application):
    class ScriveConfigSchema(Schema):
        scriveHost = fields.URL(
            title="Scrive - Host",
            description="The host of this add-on. E.g. https://lime.scrive.com",
            default="https://lime.scrive.com",
            required=True)
        includePerson = fields.Boolean(
             title="Scrive - Include Person from Document",
             description="Activating this will import contact data from people linked to documents by default.",
             default=True,
             required=True)
        includeCoworker = fields.Boolean(
             title="Scrive - Include Coworker from Document",
             description="Activating this will import contact data from coworkers linked to documents by default.",
             default=True,
             required=True)
        cloneDocument = fields.Boolean(
             title="Scrive - Clone Document by default",
             description="Activating this will cause the 'Clone Document' option to be activated by default. This option only applies to 'main' documents, it does not apply to 'attachments'.",
             default=True,
             required=True)
        target = fields.String(
             title="Scrive - Target of integration window",
             description="This determines how the integration is opened in the brwoser. See https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/a#target for more information.",
             default="_blank",
             validate=validate.Regexp("_self|_blank|_parent|_top|_unfencedTop"),
             required=True)

        class Meta:
                ordered = True

    return ScriveConfigSchema()
