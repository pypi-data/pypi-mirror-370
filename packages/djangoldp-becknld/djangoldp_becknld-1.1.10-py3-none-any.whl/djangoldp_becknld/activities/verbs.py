from djangoldp.activities import errors
from djangoldp.activities.objects import ALLOWED_TYPES, Object
from djangoldp.activities.verbs import Activity


class BecknLDActivity(Activity):
    # TODO: How to support both as:actor, as:Actor, actor, Actor? - Ignored for demo
    # TODO: How to support both as:object, as:Object, object, Object? - Ignored for demo
    attributes = Object.attributes + [
        "@type",
        "as:actor",
        "as:target",
        "as:object",
        "beckn:context",
    ]
    type = "BecknLDActivity"  # Placeholder type, should be overwritten
    required_attributes = {
        # TODO: Type check for as:actor (based on (Actor, str)):
        "as:actor": dict,
        # TODO: Stronger type check for object:
        "as:object": dict,
    }

    def validate(self):
        for attr in self.required_attributes.keys():
            if not isinstance(
                getattr(self, attr, None), self.required_attributes[attr]
            ):
                raise errors.ActivityStreamValidationError(
                    "required attribute "
                    + attr
                    + " of type "
                    + str(self.required_attributes[attr])
                )


class BecknLDSelect(BecknLDActivity):
    type = "select"


class BecknLDInit(BecknLDActivity):
    type = "init"


class BecknLDConfirm(BecknLDActivity):
    type = "confirm"


class BecknLDOnSelect(BecknLDActivity):
    type = "on_select"


class BecknLDOnInit(BecknLDActivity):
    type = "on_init"


class BecknLDOnConfirm(BecknLDActivity):
    type = "on_confirm"


ALLOWED_TYPES.update(
    {
        "select": BecknLDSelect,
        "init": BecknLDInit,
        "confirm": BecknLDConfirm,
        "on_select": BecknLDOnSelect,
        "on_init": BecknLDOnInit,
        "on_confirm": BecknLDOnConfirm,
    }
)
