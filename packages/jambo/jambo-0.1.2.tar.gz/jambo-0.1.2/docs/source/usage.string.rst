String Type
=================

The String type has the following supported properties:

- maxLength: Maximum length of the string.
- minLength: Minimum length of the string.
- pattern: Regular expression pattern that the string must match.
- format: A string format that can be used to validate the string (e.g., "email", "uri").

And the additional generic properties:

- default: Default value for the string.
- description: Description of the string field.


Examples
-----------------

1. Basic String with maxLength and minLength:

.. code-block:: python

    from jambo import SchemaConverter


    schema = {
        "title": "StringExample",
        "type": "object",
        "properties": {
            "attr1": {
                "type": "string",
                "minLength": 5,
                "maxLength": 50,
            },
        },
        "required": ["attr1"],
    }

    Model = SchemaConverter.build(schema)

    obj = Model(attr1="this_is_a_valid_string")
    print(obj)
    # Output: StringExample(attr1='this_is_a_valid_string')

2. String with pattern and format:


Pattern example:

.. code-block:: python

    from jambo import SchemaConverter


    schema = {
        "title": "StringExample",
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "pattern": r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$",
            },
        },
        "required": ["email"],
    }

    Model = SchemaConverter.build(schema)

    obj = Model(email="test@email.com")
    print(obj)
    # Output: StringExample(email='test@email.com')

    try:
        Model(email="invalid-email")
    except ValueError as e:
        print("Validation Failed as Expected")  # Output: Validation Failed as Expected


Format example:

.. code-block:: python

    from jambo import SchemaConverter

    schema = {
        "title": "StringExample",
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "format": "email",
            },
        },
        "required": ["email"],
    }

    Model = SchemaConverter.build(schema)

    obj = Model(email="test@email.com")
    print(obj) 
    # Output: StringExample(email='test@email.com')

    try:
        Model(email="invalid-email")
    except ValueError as e:
        print("Validation Failed as Expected")  # Output: Validation Failed as Expected