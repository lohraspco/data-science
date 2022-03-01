graph [
  directed 1
  node [
    id 0
    label "s"
      pos 0.0
      pos 0.0
  ]
  node [
    id 1
    label "1"
      pos 2.0
      pos -13.0
  ]
  node [
    id 2
    label "2"
      pos 3.0
      pos -6.0
  ]
  node [
    id 3
    label "3"
      pos 6.0
      pos 0.0
  ]
  node [
    id 4
    label "t"
      pos 8.0
      pos 2.0
  ]
  edge [
    source 0
    target 1
    capacity 3
    weight 1
  ]
  edge [
    source 0
    target 2
    capacity 2
    weight 1
  ]
  edge [
    source 0
    target 3
    capacity 1
    weight 1
  ]
  edge [
    source 1
    target 3
    capacity 3
    weight 1
  ]
  edge [
    source 2
    target 4
    capacity 2
    weight 2
  ]
  edge [
    source 2
    target 3
    capacity 2
    weight 2
  ]
  edge [
    source 3
    target 4
    capacity 5
    weight 1
  ]
]
