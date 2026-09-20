# Training examples

Two records from the CV online-training split. The code below is excerpted from the original prompts; labels and line intervals are unchanged. Full prompts are in [online_cv_samples.jsonl](online_cv_samples.jsonl).

## Competition: arithmetic expressions

```text
   1 | import sys
   2 | stdin = sys.stdin
   3 | def na(): return map(int, stdin.readline().split())
   4 | def ns(): return stdin.readline().strip()
   5 | def main():
   6 |     a,op,b = stdin.readline().split()
   7 |     if op == '+':
   8 |         print(a+b)
   9 |     else:
  10 |         print(a-b)
  11 |     pass
  12 | if __name__ == '__main__':
  13 |     main()
```

```json
{
  "verdict_gt": "WA",
  "actual_changed_line_ranges": [
    [
      6,
      6
    ],
    [
      8,
      8
    ],
    [
      10,
      10
    ]
  ]
}
```

## Repository: a setter with a shadowed parameter

```text
1 | #include "util/fixed_point.h"
2 | #include "heuristic.h"
3 | Heuristic::Heuristic(const SearchDomain *d) : domain(d), weight(fp_one) {}
4 | Heuristic::~Heuristic() {}
5 | void Heuristic::set_weight(float weight)
6 | {
7 | 	weight = fp_one * weight;
8 | }
9 | fp_type Heuristic::get_weight(void) const
10 | {
11 | 	return weight;
12 | }
```

```json
{
  "verdict_gt": "FAIL",
  "actual_changed_line_ranges": [
    [
      5,
      5
    ],
    [
      7,
      7
    ]
  ]
}
```
