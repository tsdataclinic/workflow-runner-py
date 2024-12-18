# Using Workflow Runner

## Concepts

- A **workflow** is a series of validations run on a CSV file. A workflow consists of **fieldset schemas**
- An **operation**, which is a single validation step in a workflow
- A **fieldset schema**, is a set of validations which runs on a _fieldset_, or set of columns, in a CSV file.
- A **parameter** is a user-supplied value which affects the behaviour of a workflow in some way.

## Creating a Workflow

Each workflow should be modeled in a JSON file. Over the next few sections, you'll see how to set up this JSON file for a simple workflow in which school testing data is validated. Our CSV file has the following headers:

```csv
studentName,subject,grade
```

### Configure Fieldset Schemas

First, we'll configure two fieldsets: one for student information, and one for class and grade-related information.

The student information fieldset validates the following details:

- The `studentName` columns is not blank

The class and grade-related fieldset validates the following details:

- The `subject` is one of `Math`, `English` or `Philosophy`
- That `score` is `A`, `B`, `C`, `D` or `F`.

These fieldsets are configured by adding the following to the workflow JSON:

```json
{
  // inside workflow json
  "fieldsetSchemas": [
    {
      "name": "validate_student_data",
      "orderMatters": false, // whether columns need to appear in the csv in this order
      "allowExtraColumns": "anywhere",
      "fields": [
        {
          "name": "studentName", // name of the column in the CSV file
          "caseSensitive": false, // whether the name of the column is case sensitive
          "required": true, // whether the column must exist
          "allowEmptyValues": false, // no empty values,
          "allowedValues": null, // any value is ok,
          "dataTypeValidation": {
            "dataType": "string"
          }
        }
      ]
    },
    {
      "name": "validate_subject_and_grade",
      "orderMatters": false,
      "allowExtraColumns": "anywhere",
      "fields": [
        {
          "name": "subject",
          "caseSensitive": false,
          "required": true,
          "allowEmptyValues": false,
          "allowedValues": ["Math", "History", "Science"], // only these values are allowed
          "dataTypeValidation": {
            "dataType": "string"
          }
        },
        {
          "name": "grade",
          "caseSensitive": false,
          "required": true,
          "allowEmptyValues": false,
          "allowedValues": ["A", "B", "C", "D", "F"],
          "dataTypeValidation": {
            "dataType": "string"
          }
        }
      ]
    }
  ]
}
```

### Configure Workflow Operations

Now that we have some fieldsets to validate, we can use them as workflow operations, or steps in our workflow. We'll validate the following things:

- That the file is a csv file
- The the file has at least 10 rows
- That the student data in the file passes the validations in the `validate_student_fields` fieldset defined above
- That the class and grade data in the file passes the validations in the `validate_subject_and_grade` fieldset defined above

```json
{
  // rest of json
  "operations": [
    {
      "type": "fileTypeValidation",
      "id": "op_1",
      "expectedFileType": "csv",
      "title": "Validate file type",
      "description": "Validate that the file type is CSV"
    },
    {
      "type": "rowCountValidation",
      "minRowCount": 10,
      "maxRowCount": null,
      "id": "op_2",
      "title": "Validate row count",
      "description": "There should be at least 10 rows"
    },
    {
      "type": "fieldsetSchemaValidation",
      "fieldsetSchema": "validate_student_data", // should match fieldset name above
      "title": "Validate student data",
      "description": "Validate student data"
    },
    {
      "type": "fieldsetSchemaValidation",
      "fieldsetSchema": "validate_subject_and_grade",
      "title": "Validate subject and grade",
      "description": "Validate subject and grade"
    }
  ]
}
```

### Configure Workflow Parameters

Thus far, the workflow we've defined is totally static, meaning that it applies exactly the same validations to every file it runs on. However, depending on which files we need to validate, our validation needs might change slightly: for example, different files may allow for different class names.

We can introduce this ability by adding a _parameter_ to the workflow schema, and updating our allowed values for `subject` to point at the parameter:

```json
{
    "operations": [/*same as above*/],
    "fieldsetSchemas": {
        // student data fieldset remains the same
        {
        // most fields remain the same
        "fields": [
            {
                "id": "2",
                "name": "subject",
                "caseSensitive": false,
                "required": true,
                "allowEmptyValues": false,
                "allowedValues": {
                    "paramId": "allowed_subjects" // should match the parameter ID below
                }
            },
            // same allowed grades
        ]
        }
    },
    "params": [
        {
            "name": "allowed_subjects",
            "displayName": "Allowed Subjects",
            "description": "Allowed Subjects",
            "required": "true"
        }
    ]
}
```

Note that the values in the `params` above are not the _values_ of the allowed subjects, but rather how those values will be formatted. The values are provided when the workflow is run, as shown below.

## Running a workflow

Using the python library, you can load the workflow schema and run it as follows:

```python
from workflow_runner_py import load_workflow_schema, process_workflow

schema = load_workflow_schema("my_schema.json")
validation_results = process_workflow(
    "file_to_validate.csv",
    param_values={
        "allowed_subjects": ["Math", "History", "Science"],
    },
    schema=schema
)

print(validation_results)
```

The `process_workflow` function returns a list of `ValidationFailure`s, which have the following fields:

- A `message` summarizing the issue
- A `rowNumber` indicating which row of the CSV the error was found on. If there is no
  row associated with this failure, this field is `None`.

## Appendices

### Full Workflow Schema

This schema can also be found in `tests/sample_schema/workflow_schema.json` in this repository. `tests/data` also contains two csv files the workflow can be tested on.

```json
{
  "fieldSetSchemas": [
    {
      "id": "fs_1",
      "name": "validate_student_data",
      "orderMatters": false,
      "allowExtraColumns": "anywhere",
      "fields": [
        {
          "id": "1",
          "name": "studentFirstName",
          "caseSensitive": false,
          "required": true,
          "allowEmptyValues": false,
          "allowedValues": null,
          "dataTypeValidation": {
            "dataType": "string"
          }
        }
      ]
    },
    {
      "id": "fs_2",
      "name": "validate_subject_and_grade",
      "orderMatters": "false",
      "allowExtraColumns": "anywhere",
      "fields": [
        {
          "id": "2",
          "name": "subject",
          "caseSensitive": false,
          "required": true,
          "allowEmptyValues": false,
          "allowedValues": {
            "paramId": "allowed_subjects"
          }
        },
        {
          "id": "3",
          "name": "grade",
          "caseSensitive": false,
          "required": true,
          "allowEmptyValues": false,
          "allowedValues": ["A", "B", "C", "D", "F"]
        }
      ]
    }
  ],
  "operations": [
    {
      "type": "fileTypeValidation",
      "id": "op_1",
      "expectedFileType": "csv",
      "title": "Validate file type",
      "description": "Validate that the file type is CSV"
    },
    {
      "type": "rowCountValidation",
      "minRowCount": 10,
      "maxRowCount": null,
      "id": "op_2",
      "title": "Validate row count",
      "description": "There should be at least 10 rows"
    },
    {
      "type": "fieldsetSchemaValidation",
      "id": "validateStudentData",
      "fieldsetSchema": "validate_student_data"
    }
  ],
  "params": [
    {
      "id": "allowed_subjects",
      "name": "allowed_subjects",
      "displayName": "Allowed Subjects",
      "description": "Allowed Subjects",
      "required": "true"
    }
  ]
}
```

## Supplying fieldset schemas as parameters

Listing a fieldset schema in the `fieldsetSchemas` field in a workflow JSON schema _does not_ automatically run that fieldset's validations until the fieldset validation is also listed as an operation in the `operations` field. This allows you to dynamically configure _which_ fieldsets are run on a file by passing them in as a parameter:

```json
{
    "fieldsetSchemas": {
        {
            "name": "fieldset_1",
            // etc
        },
        {
            "name": "fieldset_2",
            // etc
        },
    },
    "operations": [
        {
            "type": "fieldsetSchemaValidation",
            "fieldsetSchema": {
                "paramId": "fieldset_for_file"
            },
            "title": "Fieldset for file",
            "description": "Which fieldset to run for this file (fieldset_1 or fieldset_2)"
        }
    ]
}
```

```python
from workflow_runner_py import load_workflow_schema, process_workflow

schema = load_workflow_schema("my_schema.json")

# Validate 2 files, each of which uses a different fieldset

validation_results_for_file_1 = process_workflow(
    "file_1.csv",
    param_values={
        "fieldset_for_file": "fieldset_1",
    },
    schema=schema
)

validation_results_for_file_1 = process_workflow(
    "file_2.csv",
    param_values={
        "fieldset_for_file": "fieldset_2",
    },
    schema=schema
)

print(validation_results)
```
