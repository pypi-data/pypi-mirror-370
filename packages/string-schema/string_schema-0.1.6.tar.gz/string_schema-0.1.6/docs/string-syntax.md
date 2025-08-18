# String Syntax Guide

String Schema's string syntax provides an intuitive way to define schemas using human-readable text. This syntax is particularly effective for LLM-based data extraction.

## Basic Syntax

### Field Definitions

```
field_name:type
```

Examples:

```
name:string
age:int
price:number
active:bool
```

### Optional Fields

Add `?` to make fields optional:

```
name:string
email:string?
phone:string?
```

### Field Constraints

Add constraints in parentheses:

```
name:string(min=1,max=100)
age:int(0,120)
price:number(min=0)
description:text(max=500)
```

## Type System

### Basic Types

| Type      | Aliases            | Description       |
| --------- | ------------------ | ----------------- |
| `string`  | `str`, `text`      | Text data         |
| `integer` | `int`              | Whole numbers     |
| `number`  | `float`, `decimal` | Decimal numbers   |
| `boolean` | `bool`             | True/false values |

### Special Types

Special types provide format hints for better validation and LLM guidance:

| Type       | Description      | JSON Schema Format |
| ---------- | ---------------- | ------------------ |
| `email`    | Email addresses  | `email`            |
| `url`      | Web URLs         | `uri`              |
| `uri`      | Generic URIs     | `uri`              |
| `datetime` | Date and time    | `date-time`        |
| `date`     | Date only        | `date`             |
| `uuid`     | UUID identifiers | `uuid`             |
| `phone`    | Phone numbers    | _(custom)_         |

Examples:

```
email:email
website:url
created:datetime
birthday:date
id:uuid
contact:phone
```

## Arrays

### Simple Arrays

Arrays of basic types:

```
[string]        # Array of strings
[int]           # Array of integers
[email]         # Array of email addresses
[url]           # Array of URLs
```

### Array Constraints

Control array size:

```
[string](max=5)              # Maximum 5 items
[email](min=1,max=3)         # 1-3 email addresses required
[int](min=0)                 # At least 0 items (no maximum)
```

### Object Arrays

Arrays of structured objects:

```
[{name:string, email:email}]                    # Array of user objects
[{title:string, price:number}](min=1,max=10)    # 1-10 product objects
```

### Alternative Array Syntax

Alternative syntax for arrays:

```
tags:array(string,max=5)         # Array of strings, max 5
contacts:list(email,min=1)       # List of emails, min 1
```

## Objects

### Simple Objects

```
{name:string, age:int}
```

### Nested Objects

```
{
    user:{
        name:string,
        contact:{
            email:email,
            phone:phone?
        }
    },
    metadata:{
        created:datetime,
        tags:[string]?
    }
}
```

### Object with Mixed Fields

```
{
    id:uuid,
    profile:{
        name:string(min=1,max=100),
        bio:text(max=500)?,
        social:[url]?
    },
    settings:{
        theme:enum(light,dark),
        notifications:bool
    }
}
```

## Enums

Define specific allowed values:

### Basic Enums

```
status:enum(active,inactive,pending)
priority:choice(low,medium,high,urgent)
category:select(tech,business,personal)
```

### Enum Aliases

- `enum()` - Standard enum syntax
- `choice()` - Alternative syntax
- `select()` - Alternative syntax

All three work identically.

## Union Types

Allow multiple types for flexible data:

### Basic Unions

```
id:string|int               # String or integer
value:string|number         # String or number
response:string|null        # String or null
```

### Complex Unions

```
identifier:string|uuid|int
data:string|number|bool
content:string|object|null
```

## Constraints

### String Constraints

```
name:string(min=1,max=100)      # Length between 1-100 characters
title:text(max=200)             # Maximum 200 characters
code:string(min=3)              # Minimum 3 characters
```

### Numeric Constraints

```
age:int(0,120)                  # Integer between 0-120
price:number(min=0)             # Non-negative number
rating:float(1.0,5.0)           # Float between 1.0-5.0
```

### Constraint Syntax Variations

```
# Using min/max keywords
age:int(min=0,max=120)

# Using positional values
age:int(0,120)

# Single constraint
price:number(min=0)
title:string(max=100)
```

## Practical Examples

### Product Schema

```
{
    id:uuid,
    name:string,
    price:number(min=0),
    category:enum(electronics,clothing,books),
    in_stock:bool,
    tags:[string]?
}
```

### User Profile

```
{
    id:uuid,
    profile:{
        name:string,
        email:email,
        phone:phone?
    },
    account:{
        status:enum(active,inactive),
        role:enum(admin,user)
    }
}
```

### API Response

```
{
    success:bool,
    data:object|null,
    message:string?,
    timestamp:datetime
}
```

## Best Practices

### 1. Use Descriptive Field Names

```
# Good
user_email:email
created_at:datetime
max_attendees:int

# Avoid
e:email
dt:datetime
max:int
```

### 2. Add Appropriate Constraints

```
# Good - provides clear guidance
name:string(min=1,max=100)
age:int(0,120)
tags:[string](max=10)

# Less helpful - no constraints
name:string
age:int
tags:[string]
```

### 3. Use Special Types

```
# Good - provides format hints
email:email
website:url
created:datetime

# Less specific
email:string
website:string
created:string
```

### 4. Mark Optional Fields

```
# Clear about what's required
name:string
email:email
phone:phone?
bio:text?
```

### 5. Group Related Fields

```
{
    user:{
        name:string,
        email:email
    },
    preferences:{
        theme:enum(light,dark),
        notifications:bool
    }
}
```

## Syntax Reference

### Field Definition Patterns

| Pattern                  | Description       | Example                        |
| ------------------------ | ----------------- | ------------------------------ |
| `name:type`              | Basic field       | `name:string`                  |
| `name:type?`             | Optional field    | `email:string?`                |
| `name:type(constraints)` | Constrained field | `age:int(0,120)`               |
| `name:enum(values)`      | Enum field        | `status:enum(active,inactive)` |
| `name:type1\|type2`      | Union field       | `id:string\|int`               |

### Array Patterns

| Pattern                        | Description        | Example                    |
| ------------------------------ | ------------------ | -------------------------- |
| `[type]`                       | Simple array       | `[string]`                 |
| `[type](constraints)`          | Constrained array  | `[string](max=5)`          |
| `[{fields}]`                   | Object array       | `[{name:string}]`          |
| `name:array(type,constraints)` | Alternative syntax | `tags:array(string,max=5)` |

### Object Patterns

| Pattern          | Description            | Example                  |
| ---------------- | ---------------------- | ------------------------ |
| `{fields}`       | Simple object          | `{name:string, age:int}` |
| `name:{fields}`  | Nested object          | `user:{name:string}`     |
| `name:{fields}?` | Optional nested object | `profile:{bio:string}?`  |

This syntax provides a powerful yet intuitive way to define schemas that work well with both traditional validation and LLM-based data extraction.
