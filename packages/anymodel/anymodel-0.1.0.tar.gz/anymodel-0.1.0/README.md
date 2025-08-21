# AnyModel – Data Mapper for Python

`anymodel` is a data mapper for python built on top pydantic providing a flexible storage layer.

Write Plain Old Pydantic Objects, describe how the data are mapped to which storage (or storage combination) and let
`anymodel` do the rest.

Migrations are automatic. Patch your models and we'll diff your storage to apply the schema changes.
This is a dangerous operation that we may disable as a default in the future, but for now, we move fast and break 
things.

THIS SOFTWARE IS STILL IN DEVELOPMENT, EXPECT BREAKING CHANGES AND BUGS. IT MAY BREAK YOUR DATA COMPLETELY, SO DON'T USE
IT UNLESS YOU KNOW WHAT YOU ARE DOING.

## Reqs

We want to work with "popo" entities (here, plain old pydantic objects). We should be able to sync them back and forth
with nunderlying storages, but the storage implementation should not be tied to business objects.

Migrations should be automatic, yet not dangerous. Removed fields / tables should require an explicit confirmation from
the user, yet adding a field should be transparent.

We should be able to work with multiple storages at the same time, and even have a single entity mapped to multiple
storages, with a main/secondary logic (for example, an sql storage may be responsible for the key management, and store
the name, and a lucene index may store other things).

We should be able to manage lazy relations, and even lazy fields from secondary storages.

