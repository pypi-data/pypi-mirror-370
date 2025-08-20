# Concept.identify_by

We want to support reference schemes in the query builder directly, we do this by speficying a set of relationships that act as identifying information for a concept.

## constructor variant

```python
SSN = Concept("SSN", extends=[String])
person = Concept("Person", identify_by={
    "ssn": SSN # can be a Concept, in which case we create a relationship {Person} has {ssn:SSN} behind the scenes
})

EmployeeNumber = Concept("EmployeeNumber", extends=[String])
employee = Concept("Employee", extends=[Person], identify_by={
    "employee_number": Relation("{Employee} is identified by {EmployeeNumber}"),
})
```

## function variant

```python
Person = Concept("Person")
Person.ssn = Relation("{Person} has {SSN}")
Person.identify_by(Person.ssn)
```

## How this impacts `Concept.new`

Once a concept has identifying relationships, values for them must always be provided when calling Concept.new. So given our definitions of Person above:

```python
Person.new() # raises an error, ssn is required
Person.new(name="foo") # raises an error, ssn is required
Person.new(ssn="123-45-6789") # works
Person.new(ssn="123-45-6789", name="foo") # works
```

References schemes are inherited from parent concepts, so because Employee extends Person, we must provide both ssn and employee_number when creating an Employee:

```python
Employee.new(employee_number="123456") # raises an error, ssn is required
Employee.new(ssn="123-45-6789") # raises an error, employee_number is required
Employee.new(ssn="123-45-6789", employee_number="123456") # works
```
Internally, when calling Concept.new with a reference scheme, we must not only fill the values of the provided relationships, but also add this new identity to the population of the concept and if there are inherited reference schemes, we create the internal mappings from the child identity to the parent one.

NOTE: the primary identity is always the highest ancestor in the hierarchy with a reference scheme. This means that while we hash employee_number to create a lookup to person, the identity of the employee will always be the hash of ssn. The QB deals with this mapping under the hood.

```python
Employee.new(ssn="123-45-6789", employee_number="123456")

# during compilation will turn into the equivalent of:

define(
    p := construct(Person, ssn="123-45-6789"),
    Person(p)
    person_ssn(p, "123-45-6789"),
    Employee(p),
    employee_number(p, "123456"),
    e := construct(Employee, employee_number="123456"),
    employee_to_person(e, p),
)
```
## How this impacts `Concept.new_identity`

There are times where we might be working with an external source that only has a child identifier and not the parent one. While we require the parent identifier to be provided to add to the population, if we've already done that elsewhere, it's reasonable to get a reference to the parent identity from the child one. To do that we can use `Concept.new_identity`:

```python
define(
    e := Employee.new_identity(employee_number="123456") # works assuming something has previousl added this employee_number to the population
    e.salary(1000)
)

# during compilation will turn into the equivalent of:
define(
    e := construct(Employee, employee_number="123456"),
    employee_to_person(e, p),
    employee_salary(p, 1000)
)
```

As stated previously, all references must map back to the parent identity and this employee id is just used to lookup the person id.

## Implied constraints

Any relationship that is used to identify a concept is mandatory (which is enforced directly by `.new()`) and also implies that the combination of identifying relationships must be unique. We can create those constraints like so when defining the reference scheme:

```python
# after adding the relationships to the concept
rels = [getattr(self, rel) for rel in identify_by.keys()]
self.require(*rels) # make the relationships mandatory
self.require(distinct(*rels)) # ensure the relationships are unique (needs to be implemented)
```

If you were to write that by hand, it'd look something like this for Employee:

```python
Employee.require(Employee.ssn, Employee.employee_number)
Employee.require(distinct(Employee.ssn, Employee.employee_number))
```

## Implementation notes

We want to store the reference schemes on the concept itself and during the QB -> IR compilation, take them into account when we encounter either a `ConceptNew` (for the `.new(..)` case) or a `ConceptConstruct` (for the `.new_identity(..)` case). At that point in the compiler, we'd add the necessary mappings and handle parent reference schemes.

Since we allow for multiple inheritance, the "primary" reference scheme is determined by doing depth first search on the parent types and taking the first ancestor with a reference scheme that we encounter. This means a user can control this by ordering their parents in `extends=[..]`.