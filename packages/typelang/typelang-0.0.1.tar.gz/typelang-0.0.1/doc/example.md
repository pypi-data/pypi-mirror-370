The `typelang` is a subset of typescript that are designed to provide. Its syntax as following.

```ts

type MyType0 = {
    value: string
}

type MyType<T> = {

    // PrimitiveType
    intValue: int
    floatValue: float
    strValue: string
    boolValue: bool
    listValue: list
    dictValue: dict
    anyValue: any

    //     ParameterizedType
    listValue: T[]
    dictValue: Dict<T, T>
    tupleValue: Tuple<T, T>
    unionValue: T | MyType0 // union type
    optionalValue?: T

    inlineType: {
        value: string
    }

    enumValue: 'enum' | 'is' | 'union' | 'type' | 'of' | 'literal' | 'types'
}

type NotInlineEnum = 'enum' | 'is' | 'union' | 'type' | 'of' | 'literal' | 'types'


```


