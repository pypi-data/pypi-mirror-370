Numeric Types
=================


The Numeric Types (integer, number) have the following supported properties:

- minimum: Minimum value for the number.
- maximum: Maximum value for the number.
- exclusiveMinimum: If true, the value must be greater than the minimum.
- exclusiveMaximum: If true, the value must be less than the maximum.
- multipleOf: The value must be a multiple of this number.

And the additional generic properties:

- default: Default value for the string.
- description: Description of the string field.


Examples
-----------------


1. Basic Integer with minimum and maximum:

.. code-block:: python

    from jambo import SchemaConverter

    schema = {
        "title": "IntegerExample",
        "type": "object",
        "properties": {
            "age": {
                "type": "integer",
                "minimum": 0,
                "maximum": 120,
            },
        },
        "required": ["age"],
    }

    Model = SchemaConverter.build(schema)

    obj = Model(age=30)
    print(obj) # Output: IntegerExample(age=30)

    try:
        obj = Model(age=-5)  # This will raise a validation error
    except ValueError as e:
        print("Validation fails as expected:", e) # Output: Validation fails as expected: 1 validation error for IntegerExample


2. Number with exclusiveMinimum and exclusiveMaximum:

.. code-block:: python

    from jambo import SchemaConverter

    schema = {
        "title": "NumberExample",
        "type": "object",
        "properties": {
            "price": {
                "type": "number",
                "exclusiveMinimum": 0,
                "exclusiveMaximum": 1000,
            },
        },
        "required": ["price"],
    }

    Model = SchemaConverter.build(schema)

    obj = Model(price=1)
    print(obj) # Output: NumberExample(price=1)

    try:
        obj = Model(price=0)  # This will raise a validation error
    except ValueError as e:
        print("Validation fails as expected:", e) # Output: Validation fails as expected: 1 validation error for NumberExample


    obj = Model(price=999)
    print(obj) # Output: NumberExample(price=999)

    try:
        obj = Model(price=1000)  # This will raise a validation error
    except ValueError as e:
        print("Validation fails as expected:", e) # Output: Validation fails as expected: 1 validation error for NumberExample


3. Number with multipleOf:

.. code-block:: python

    from jambo import SchemaConverter

    schema = {
        "title": "MultipleOfExample",
        "type": "object",
        "properties": {
            "quantity": {
                "type": "number",
                "multipleOf": 0.5,
            },
        },
        "required": ["quantity"],
    }

    Model = SchemaConverter.build(schema)

    obj = Model(quantity=2.5)
    print(obj) # Output: MultipleOfExample(quantity=2.5)

    try:
        obj = Model(quantity=2.3)  # This will raise a validation error
    except ValueError as e:
        print("Validation fails as expected:", e) # Output: Validation fails as expected: 1 validation error for MultipleOfExample
