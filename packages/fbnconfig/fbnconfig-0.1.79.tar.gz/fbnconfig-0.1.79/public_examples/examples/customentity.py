from fbnconfig import Deployment, customentity

"""
An example configuration for a custom entity.
The script configures the following entities:
- Entity Type

More information can be found here:
https://support.lusid.com/knowledgebase/article/KA-01750/en-us
"""


def configure(env):
    ce = customentity.EntityTypeResource(
        id="ce1",
        entity_type_name="entity-type-name",
        display_name="Example Custom Entity",
        description="An example custom entity",
        field_schema=[
            customentity.FieldDefinition(
                name="Field1",
                lifetime=customentity.LifeTime.PERPETUAL,
                type=customentity.FieldType.STRING,
                collection_type=customentity.CollectionType.SINGLE,
                required=True,
            ),
            customentity.FieldDefinition(
                name="Field2",
                lifetime=customentity.LifeTime.TIMEVARIANT,
                type=customentity.FieldType.STRING,
                required=True,
            ),
        ],
    )
    return Deployment("custom_entity_example", [ce])
