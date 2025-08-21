# jsw-nx
> Next toolkit for python.

## installation
```shell
pip install jsw-nx -U
```

## usage
```python
import jsw_nx as nx

## common methods
nx.includes([1,2,3], 2) # => True
nx.includes([1,2,3], 5) # => False
```

## next core methods
- base/every
- base/filter
- base/find
- base/find_index
- base/flatten
- base/foreach
- base/forin
- base/get
- base/includes
- base/index
- base/map
- base/reduce
- base/set
- base/some
- base/type

## ruby style
- rubify/times
- rubify/to_a
- rubify/to_b
- rubify/to_f
- rubify/to_i
- rubify/to_n
- rubify/to_s

## next packages
- days
- deep_each
- env_select
- filesize
- get_domain
- getenv
- html2text
- is_process_alive
- md5
- param
- parse_cookie
- qs
- replace_dict_all
- sample
- [tmpl](https://js.work/posts/34ef06b7870ec)
- uniq
- urljoin

## next classes
+ configuration
  - set
  - get 
  - sets
  - gets
  - save
  - update
+ date
  - format 
  - now 
  - create
+ fileutils
  - mkdir_p
  - cd
  - pwd
  - ls
  - mv
  - rmdir
  - touch
  - cp_r
  - isfile
  - isdir
  - rm
  - exists
  - gbk_to_utf8
  - read_file_content
+ tar
  - gz
  - xz
+ [JSON](https://js.work/posts/3dc24683e53c4)
  - parse
  - stringify