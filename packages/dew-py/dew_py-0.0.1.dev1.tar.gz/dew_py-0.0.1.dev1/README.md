# Dew

A simple parser for discord slash command-like text, written in pure python

```python
import dew

result = dew.parse('add rgb color name:"my color" r:100 g:150 b:200')

print(result)

# {
#     'command_name': 'add',
#     'sub_command_group_name': 'rgb',
#     'sub_command_name': 'color',
#     'kwargs': [
#         ('name', 'my color'),
#         ('r', '100'),
#         ('g', '150'),
#         ('b', '200')
#     ]
# }
```

### Links

[BNF grammar](grammar.bnf)
